---
title: "RDS for MySQL 8.0 → 8.4 を標準サポート終了当日に Blue/Green で移行した記録 — 実測値と落とし穴18個"
date: 2026-08-03
lastmod: 2026-08-03
slug: "rds-mysql-84-blue-green-migration"
draft: false
description: "RDS の書き込み停止1秒に対して、アプリから見た停止は24秒。原因は DNS 伝播でした。本番 MySQL 8.0.41 を標準サポート終了日当日に 8.4.10 へ Blue/Green 移行した実録と、落とし穴18個を実測値付きでまとめます。"
categories: ["クラウド/インフラ"]
tags: ["aws", "rds", "mysql", "terraform", "blue-green-deployment"]
---

本番 RDS（MySQL 8.0.41）を、標準サポート終了日である 2026-07-31 当日に 8.4.10 へ移行しました。
Extended Support 課金の開始（8/1）に1日だけ間に合わせた形です。

事前検証・リハーサル2回・stage 先行移行・本番2インスタンスの切替までを2日で通しており、
その過程で**事前資料や AWS ドキュメントだけでは分からなかった落とし穴が18個**出てきました。
同じ移行を控えている人向けに、実測値と一緒に残します。

Blue/Green デプロイの仕組み自体を先に押さえたい方は「前提」から、
実務的な落とし穴だけ読みたい方は「tips」から読んでください。

> インスタンス名・テーブル名・AWS リソース ID は匿名化しています。実測値は実際の数値で、
> 時刻はすべて JST、リクエスト数のみ概算です。

---

## TL;DR

| 対象 | 方式 | 実施 | RDS の書き込み停止 | アプリから見た停止 |
|---|---|---|---|---|
| stage | in-place | 2026-07-30 12:04 | — | **約5分** |
| prod-sub（20GB / Multi-AZ） | Blue/Green | 2026-07-31 11:03 | **約1秒** | **18秒**（完全停止15秒 + 部分障害3秒） |
| prod-main（200GB / db.m6g.2xlarge） | Blue/Green | 2026-07-31 12:07 | **約1秒** | **24秒**（完全停止15秒 + 部分障害9秒） |

- **ALB での流入遮断はしない**方が正解だった（遮断すると16秒の障害を回避するために4分の全断を作ることになる）
- **Blue/Green 切替は Terraform state を壊す**（`DbiResourceId` が変わる）。`state rm` + `import` が必須
- 切替時にアプリが返すエラーは「接続不能」ではなく **`1290 read-only`**。原因は **DNS 伝播の遅れ**
- Extended Support 課金は **$0**（下限見積り約 $1,022/月 を回避）

---

## 1. 前提：AWS RDS の Blue/Green デプロイとは

以降の話がすべてこの仕組みに乗っているので、先に3分で押さえます。

**Amazon RDS Blue/Green Deployments** は、本番と同じ構成の複製環境を作って
そちらでバージョンアップやスキーマ変更を済ませ、**準備が整ってから一瞬で入れ替える**
マネージド機能です。

![RDS Blue/Green デプロイの4段階を示した図。BG デプロイ作成で blue から green へ binlog レプリケーションが張られ、green だけを MySQL 8.4 へアップグレードし、switchover でエンドポイント名を入れ替え、最後に旧 blue を old1 として削除する流れ](/blogs/images/rds-mysql-84-blue-green-flow.png)

### 4つのポイント

1. **green は blue の「リードレプリカ」** — MySQL なら binlog レプリケーションで
   blue の更新が継続的に green へ流れます（方向は blue → green の一方向のみ）。
   だから **green の作成に1時間かかっても、その間の本番更新は失われません**。
2. **green は本番トラフィックを受けない** — なのでメジャーバージョンアップに
   何分かかっても、失敗して再試行しても、**ユーザー影響はゼロ**です。
   ここが in-place アップグレードとの決定的な違いです。
3. **切替はエンドポイント名の入れ替え** — アプリの接続文字列を変更する必要がありません。
   ただし**名前解決の結果が切り替わるまでのラグ**が残ります（本記事の tip 9 の核心）。
4. **旧 blue は消えず `-old1` として残る** — read-only 化されて残るので、
   直後であれば「戻る」判断の材料になります（ただし後述のとおり実質的な制約あり）。

### 切替（switchover）の内部シーケンス

RDS が実際にやっていることは7段階です。

1. **ガードレールチェック**
2. **両環境**のプライマリで新規書き込みを停止
3. **両環境の接続を切断し、新規接続も受け付けない**
4. green のレプリケーション追いつきを待つ
5. **エンドポイント名を入れ替え**（green → 本番名、blue → `-old1`）
6. 接続を再許可
7. 新本番で書き込みを再許可

> **書き込みはキューイングされません。接続エラーになります。**
> コミット済みは失われませんが（手順4）、未コミットは接続切断でロールバックされます。

**ガードレール**は「満たさなければ切替しない」条件です。

| 対象 | チェック内容 |
|---|---|
| green | レプリケーションの健全性 / 遅延が許容範囲内 / 書き込みが無いこと |
| blue | **長時間実行中の書き込みが無いこと** / **長時間 DDL が無いこと** |

タイムアウト（既定300秒、`--switchover-timeout` で 30〜3,600秒に変更可）を超えると **全ロールバック**され、
**両環境に変更が入りません**。つまり**切替の失敗は安全側に倒れます**。

### in-place アップグレードとの比較

| 観点 | in-place | **Blue/Green** |
|---|---|---|
| ダウンタイム | 200GB なら数十分 | **書き込み停止 約1秒**（本記事の実測） |
| 事前検証 | 本番でしか試せない | **本番データのコピーで事前検証できる** |
| 切替失敗時 | スナップショットからリストア | **自動ロールバックで blue 無変更** |
| 追加コスト | なし | **並走期間は green の分だけ二重課金** |
| 前提条件 | なし | **自動バックアップ（binlog）有効が必須**（`binlog_format=ROW` 等） |
| 制約 | なし | **カスタム Option Group だとメジャーバージョン指定不可** 等（tip 2） |

今回は **stage は in-place（約5分の停止を許容）**、**prod は Blue/Green** で実施しました。

### この記事で使う用語

| 用語 | 意味 |
|---|---|
| **blue** | 現行本番。切替まで一切変更されない |
| **green** | 複製環境。ここをアップグレードする |
| **切替（switchover）** | エンドポイント名の入れ替え。以降は「切替」と書きます |
| **BG** | Blue/Green デプロイの略 |
| **`-old1`** | 切替後の旧 blue に自動で付くサフィックス |
| **ガードレール** | 切替の実行可否を RDS が判定する条件 |
| **provisioning** | green を作成してレプリケーションを開始するまでの期間。**ユーザー影響なし** |
| **prod-main / prod-sub** | 本番の2インスタンス。Terraform 上のリソース名はそれぞれ `rds` / `sub`、<br>インスタンス識別子は `myproj-prod-db-instance` / `myproj-prod-sub-db-instance` |

---

## 2. 背景：なぜ「当日」というスケジュールになったのか

AWS Health から通知が来ていた内容はこうです。

| 項目 | 日付 |
|---|---|
| RDS 標準サポート終了（MySQL 8.0） | **2026-07-31** |
| Extended Support 年1-2 料金開始 | 2026-08-01 |
| Extended Support 年3 料金開始（倍額） | 2028-08-01 |
| Extended Support 終了 | 2029-07-31 |

### 課金インパクト

Extended Support は **vCPU 時間課金**で、しかも **Multi-AZ のスタンバイも課金対象**です。

| インスタンス | クラス | 課金 vCPU |
|---|---|---|
| prod-main | db.m6g.2xlarge | 8 |
| prod-sub | db.m6g.large（Multi-AZ） | **4**（スタンバイ含む） |
| stage | db.m6g.large | 2 |
| 計 | | **14** |

14 vCPU × 730h = 10,220 vCPU-h/月。**us-east-1 の公表単価** $0.100/vCPU-h を当てると
**約 $1,022/月**（年 $12,000 超）。

> ⚠️ Tokyo リージョンの Extended Support 単価は Pricing API / 公式料金ページから取得できませんでした。
> 上記は us-east-1 の単価による**下限の見積り**です（単価はリージョンと暦年に依存します）。

### 逃げ道がなかった理由（tip #0）

**`EngineLifecycleSupport` は既存インスタンスでは変更できません**（作成時 / リストア時のみ指定可能）。
つまり「Extended Support をオプトアウトして課金を止める」という選択肢は、
すでに動いているインスタンスには存在しません。**間に合わせるか、払うかの二択**です。

さらに悪い話として、現行の **8.0.41 はすでに deprecated**（マイナー標準サポート終了 2026-05-31）で、
`describe-db-engine-versions` も `Status=deprecated` を返します。Extended Support で
CVE パッチが提供されるのは 8.0.46 系のみ。

> **放置すると「Extended Support 料金を払うのにセキュリティパッチは来ない」状態になります。**

---

## 3. Terraform 側の設計：family 差し替えではなく「併設」

最初に検討したのは、既存の Parameter Group / Option Group の `family` を
`mysql8.0` → `mysql8.4` に差し替える方式です。これはダメでした。

**PG/OG が prod の2インスタンス（main と sub）で共有されている**ため、
family を差し替えると**2台が同時に切り替わり、段階移行ができません**。

そこで 8.4 用の PG/OG を**併設**し、インスタンス単位で選択できるようにしました。

```hcl
# modules/rds/mysql84.tf
locals {
  # rds = prod-main / sub = prod-sub
  rds_engine_versions = {
    rds = try(var.rds_params.rds.engine_version, var.engine_version)
    sub = try(var.rds_params.sub.engine_version, var.engine_version)
  }

  # 8.4 系のインスタンスは family mysql8.4 の PG/OG を使う
  rds_is_mysql84 = {
    for k, v in local.rds_engine_versions : k => startswith(v, "8.4")
  }

  rds_parameter_group_names = {
    for k, v in local.rds_is_mysql84 :
    k => v ? aws_db_parameter_group.mysql84.name : aws_db_parameter_group.rds.name
  }
  # option_group も同様
}
```

利用側は `engine_version` を書くだけで PG/OG まで一緒に切り替わります。

```hcl
# terraform/prod/variables.tf
rds_params = {
  rds = { engine_version = "8.4.10" }   # ← PG/OG も自動で -84 に
  sub = { engine_version = "8.4.10" }
}
```

移行後に `terraform plan` を打って **`engine_version` / PG / OG / `identifier` の差分がすべて消える**
ことが、この設計が正しく効いている証拠になります。

設定中の8パラメータ（`general_log` / `slow_query_log` / `long_query_time` / `log_output` /
`time_zone` / `binlog_format` / `binlog_checksum` / `binlog_row_image`）は
`describe-engine-default-parameters --db-parameter-group-family mysql8.4` で
**すべて mysql8.4 family に存在する**ことを事前確認しました。
`binlog_format` は 8.0.34 で非推奨になり（8.4 でも非推奨のまま、将来のバージョンで削除予定）ですが、
`ROW` は引き続き有効です。

---

## 4. tips：事前資料に書いていなかった落とし穴

ここが本題です。ほぼすべて**実機で踏んで**から分かったものです。
⭐ は**特に影響が大きく、他の環境でも再現しやすい**ものです。

| # | 一言 | フェーズ |
|---|---|---|
| [1](#tip-1) | MEMCACHED は事前アンインストールが必要（独立した1段目） | 事前準備 |
| [2](#tip-2) ⭐ | カスタム OG だと BG 作成時にメジャーバージョンを指定できない | 事前準備 |
| [3](#tip-3) ⭐ | クロスバージョンレプリケーションが動くから migration を流せない | 並走期間 |
| [4](#tip-4) | 夜間無人の並走監視は CloudWatch アラームだけでは足りない | 並走期間 |
| [5](#tip-5) ⭐ | Blue/Green 切替は Terraform state を壊す | 後片付け |
| [6](#tip-6) | old1 は `deletion_protection` を継承する（インスタンスごとに違う） | 後片付け |
| [7](#tip-7) ⭐ | ALB で流入を止めるのは逆効果だった | 切替設計 |
| [8](#tip-8) | 止めるべきは web ではなく job/celery | 切替設計 |
| [9](#tip-9) ⭐ | アプリが返すエラーは「接続不能」ではなく `1290 read-only` | 切替中 |
| [10](#tip-10) | 「復旧」をポーリングだけで判定すると短く見積もる | 切替中 |
| [11](#tip-11) | ヘルスチェックの「余裕」の計算式を間違えていた | 切替設計 |
| [12](#tip-12) | AWS CLI のオプションは create と describe で対称ではない | 切替中 |
| [13](#tip-13) | Performance Insights の SQL は途中で切られる → EXPLAIN に流せない | 検証 |
| [14](#tip-14) | 8.4 で実際に変わった変数と、無停止で戻せるかどうか | 検証 |
| [15](#tip-15) | 切替後の PI 比較は「時間帯の交絡」で簡単に嘘になる | 検証 |
| [16](#tip-16) | リハーサルの provisioning 時間は本番に当てはまらない | 事前準備 |
| [17](#tip-17) | 前提条件を満たしていれば BG はソースを再起動しない | 事前準備 |
| [18](#tip-18) | 心配していたが問題にならなかったこと | 補足 |

### tip 1. MEMCACHED は「8.4 に無い」だけでなく「事前アンインストールが必要」 {#tip-1}

`describe-option-group-options --engine-name mysql --major-engine-version 8.4` の結果は `MARIADB_AUDIT_PLUGIN` のみで、
**MEMCACHED は 8.4 では提供されません**。ここまでは事前に分かります。

問題は、「同じ `modify-db-instance` で 8.4 用 OG に差し替えればよい」では**通らない**ことです。
stage で1段方式を試したところ、プリチェックでロールバックされました。

```text
Database instance is in a state that cannot be upgraded: PreUpgrade checks failed:
RDS detected incompatibilities when upgrading to MySQL 8.4.10.

12) memcached plugin needs to be uninstalled before upgrade
    daemon_memcached - Remove the MySQL memcached support option from your DB instance
    and then retry the upgrade.
```

→ **「アタッチ中の 8.0 用 OG から MEMCACHED を削除する」独立した1段目が必要**です。

これはオンライン適用で**再起動不要・約1分**。本番でも適用窓 17:25:26〜17:26:43（77秒）の間、
**全リクエスト HTTP 200 / DB エラー0件**で完了しました。

prod の 8.0 用 OG は main と sub で共有しているので、**1回の apply で両インスタンスの前提条件が揃う**
のが唯一の救いでした。

> なお 11211 は prod/stage の RDS セキュリティグループで許可されておらず（3306 のみ）、
> MEMCACHED は完全に未使用でした。使っていたら移行そのものの設計が変わります。**先に確認してください。**

### tip 2. ⭐ カスタム OG を使っていると BG 作成時にメジャーバージョンを指定できない {#tip-2}

これが最大の落とし穴でした。AWS ドキュメントの MySQL 固有制限にこう書いてあります。

> If the source database is associated with a custom option group, you can't specify
> a major version upgrade when you create the blue/green deployment.

prod はカスタム OG を使っているため、当初手順に書いていた

```bash
aws rds create-blue-green-deployment ... --target-engine-version 8.4.10   # ← prod では失敗する
```

は通りません。**MEMCACHED を外して OG を空にしても「カスタム OG に関連付けられている」ことは変わらない**
ので、この制限は回避できません。実際に試すとこうなります。

```text
InvalidParameterCombination: RDS Blue/Green Deployments only support default option groups
for major version upgrades. Don't specify a major version upgrade when you create the
blue/green deployment. After you create the blue/green deployment, you can upgrade the
database in the green environment.
```

**エラーメッセージ自身が回避策を書いてくれている**のが親切ですが、本番当日に見たい文字列ではありません。

#### さらに厄介だったこと：リハーサルが「偶然」成功していた

1回目のリハーサルは、prod スナップショットから復元したクローンに `default:mysql-8-0` を
指定していました。そのため**この制限を偶然すり抜けて成功していた**のです。

> **教訓: リハーサル環境の構成が本番と1箇所でも違うと、その1箇所の検証が丸ごと抜けます。**
> 「本番のスナップショットから復元した」だけでは同一条件になりません。OG/PG/Multi-AZ まで揃えてください。

そこで**カスタムの空 8.0 OG を付けたクローン**で2回目のリハーサルを実施し、
2段構えの手順を検証し直しました。

```bash
# 【1】BG を 8.0 のまま作成（--target-engine-version を指定しない）
aws rds create-blue-green-deployment \
  --blue-green-deployment-name myproj-prod-84 \
  --source <source-db-arn>

# 【2】green を単体で 8.4.10 へアップグレード
GREEN=$(aws rds describe-blue-green-deployments \
  --filters Name=blue-green-deployment-name,Values=myproj-prod-84 \
  --query 'BlueGreenDeployments[0].Target' --output text | awk -F: '{print $NF}')
[ -z "$GREEN" ] && { echo "green 識別子が取れていません"; exit 1; }

aws rds modify-db-instance --db-instance-identifier "$GREEN" \
  --engine-version 8.4.10 --allow-major-version-upgrade \
  --db-parameter-group-name myproj-prod-parameter-group-84 \
  --option-group-name myproj-prod-option-group-84 \
  --apply-immediately
```

**green はトラフィックを受けていないので、この in-place アップグレードのダウンタイムは無害**です。

副次的な利点もありました。`create-blue-green-deployment` には `--target-option-group-name` が
**存在しない**ので、1段方式だと green は `default:mysql-8-4` になってしまいます。
2段構えなら `modify-db-instance --option-group-name` で**カスタム 8.4 OG に載せられます**。

### tip 3. ⭐ blue(8.0) → green(8.4) のクロスバージョンレプリケーションは動く。だから migration を流せない {#tip-3}

green は blue の**リードレプリカ**で、binlog により blue の更新が継続的に green に流れます。
方向は blue → green の一方向のみ。**8.0 → 8.4 のクロスバージョンでもちゃんと動きます**
（本番で約16.5時間並走し、遅延は最大 1.0s、60秒を超えたデータポイントは0件）。

green のメジャーアップグレード中も、再起動でレプリケーションが**1分だけ**止まって復帰しました。

しかし「動く」ことが逆にリスクになります。

> **blue で実行した DDL も binlog 経由で green（8.4）に適用されます。**
> 8.0 では通るが 8.4 では拒否される文があると、**green 側でレプリケーションが壊れて切替不可**になります。

今回まさに該当するものがプリチェックで出ていました（テーブル名は匿名化）。

```text
appdb.child_parent_id_xxxxxxxx_fk_parent_id
  - 'child(parent_id)' references a non unique key
appdb.grandchild_parent_id_yyyyyyyy_fk_parent_id
  - 'grandchild(parent_id)' references a non unique key
appdb.detail_parent_id_zzzzzzzz_fk_parent_id
  - 'detail(parent_id)' references a non unique key
```

**一意インデックスを参照していない（または部分キーを参照する）外部キーは、MySQL 8.4.0 以降
デフォルトで新規作成が拒否されます**。8.4 で追加された `restrict_fk_on_non_standard_key`（既定 `ON`）
による挙動で、**既存 FK は動作し続け、アップグレード自体も止まりません**。
BG 並走中にこの FK を再作成する migration が流れていたら、切替不能に陥っていました。

> アプリが実行時に FK を作る場合は、**8.4 のパラメータグループで
> `restrict_fk_on_non_standard_key = OFF`** にする回避策があります（AWS も公式ブログで案内しています）。
> 今回は migration を止める方針にしましたが、止められない環境ではこちらが現実的です。

→ **BG 作成から切替完了までは migration を流さない**、を関係チームに事前周知。
今回の禁止期間は **7/30 19:49 〜 7/31 12:30 の約16.7時間**でした。

夜間の one-off タスクは ECS Task State Change → CloudWatch Logs の記録で全数確認し、
`migrate` は BG 作成前の 19:39 の1件のみ、異常終了0件であることを裏取りしました。
日次バッチスクリプトの中身も1本ずつ読んで `migrate` を含まないことを確認しています。

> **tip: この確認は「BG を作る前」ではなく「作った後・切替前の朝」にやる必要があります。**
> 深夜に何が走ったかを後追いできる仕組み（イベント記録）が無いと、この確認自体ができません。

### tip 4. 夜間無人の並走を監視する（CloudWatch アラームだけでは足りない） {#tip-4}

BG が約16.5時間存在し、うち深夜は無人。手動チェックポイントだけでは間が空白になります。

そこで EventBridge Scheduler + Lambda で 10分毎の監視を組みました。
**CloudWatch アラームでは代替できません**：

- **BG デプロイの `Status` はメトリクスではないのでアラームで監視できない**
- **`ReplicaLag` はレプリケーション破断時に `-1` を返して「遅延なし」に見えることがある**

そして**誤報抑制の設計が本質でした**。実装時に本番で誤報を出しかけて気付いた点：

| 抑制 | 理由 |
|---|---|
| `PROVISIONING` / `DELETING` 中は green と `ReplicaLag` を検査しない | 200GB の BG 作成は1時間以上かかる。この間 green は未作成なので、検査すると**必ず誤報** |
| green が遷移中（`modifying` / `upgrading` / `rebooting` 等）は `ReplicaLag` の異常値を無視 | green のアップグレード中は再起動で `ReplicaLag = -1` になる |
| `SWITCHOVER_COMPLETED` 後はレプリケーション停止が正常 | 切替後に「壊れた」と誤報しない |
| BG が存在しない場合は `SKIP` | BG 作成前に apply しておいても誤報しない |

結果、**160回実行してアラート0件 / SNS 通知0件**。
green アップグレード中に出た `ReplicaLag = -1.0s` も誤報になりませんでした。

> **誤報を出す監視は、無いのと同じか、それより悪い**（深夜に10分毎に鳴り続けます）。
> 「正常な遷移状態」を列挙してから書き始めるのが正解でした。

### tip 5. ⭐ Blue/Green 切替は Terraform state を壊す {#tip-5}

これは全 Terraform ユーザーに刺さります。

**Terraform は `aws_db_instance` を `DbiResourceId` で管理しています。**
Blue/Green 切替では**識別子（名前）は引き継がれますが `DbiResourceId` は変わります**。

| インスタンス | DbiResourceId |
|---|---|
| `...-db-instance`（新本番 = 旧 green） | `db-XXXXXXXXXXXXXXXXXXXXXXXXXX`（**新規**） |
| `...-db-instance-old1`（旧 blue） | `db-YYYYYYYYYYYYYYYYYYYYYYYYYY` ← **state が指し続ける** |

切替直後の `plan` は実際にこう出ました。

```text
module.rds.aws_db_instance.sub[0]: Refreshing state... [id=db-YYYYYYYYYYYYYYYYYYYYYYYYYY]

  # module.rds.aws_db_instance.sub[0] will be updated in-place
      ~ identifier = "myproj-prod-sub-db-instance-old1" -> "myproj-prod-sub-db-instance"
```

**旧 blue を本番名にリネームしようとします。**

- 気づかず apply すれば**名前衝突**
- **old1 を先に削除していれば「DB インスタンスを新規作成」** になります

対策（**old1 削除より前に必須**）:

```bash
terraform -chdir=terraform/prod state pull > backup.json     # 保険
terraform -chdir=terraform/prod state rm 'module.rds.aws_db_instance.rds[0]'
terraform -chdir=terraform/prod import 'module.rds.aws_db_instance.rds[0]' myproj-prod-db-instance
```

修正後は `identifier` のリネーム差分が消え **`0 to destroy`**。
残る `allow_major_version_upgrade` / `apply_immediately` の差分は
**import では読めない TF 側属性**なので正常です。

> **手順の順序が重要:** 切替 → **state 張り替え** → plan で `0 to destroy` 確認 → old1 削除。
> この順序を守らないと、本番 DB を新規作成する plan を持ったまま作業を続けることになります。

なお、これは **AWS CLI / コンソールから手動で BG を回した場合**の話です。
Terraform の `aws_db_instance` には `blue_green_update { enabled = true }`（low-downtime updates）があり、
**Terraform 主導で BG を回せば state の張り替えは不要**になります。
ただしリードレプリカを持つインスタンスでは使えないなどの制約があるため、今回は手動 BG を選びました。
どちらを採るかは**着手前に決めておく**べきポイントです。

### tip 6. old1 は deletion_protection を継承する（インスタンスによって違う） {#tip-6}

後片付けで `Cannot delete protected DB Instance` に当たりました。しかも**インスタンスによって違いました**。

| | `deletion_protection` | 削除前の対応 |
|---|---|---|
| prod-main green | **`true`** | `--no-deletion-protection` が**必要** |
| prod-sub green | `false` | 不要 |

sub で成功した手順をそのまま main に流すと止まります。**2台あるなら2台とも確認**。

### tip 7. ⭐ ALB で流入を止めるのは逆効果だった {#tip-7}

当初の手順は「ALB リスナールールの優先度1に `fixed-response 503` を挿して全断 → 切替 → 削除」でした。
CloudFront ではなく ALB を選ぶ判断自体は正しいのですが（反映が数秒 / CloudFront はエラーをエッジで
キャッシュして復帰後も 503 が残る）、**そもそも遮断が不要**でした。

stage でバージョン変更なしの BG を作り、1秒間隔の HTTP ポーリングで切替を計測した結果：

```text
17:00:49  200          ← 正常
17:00:50  500          ← 障害開始
17:00:51  000 (timeout)
17:00:56  000 (timeout)
17:01:01  000 (timeout)
17:01:06  200          ← 復旧
17:01:18  SWITCHOVER_COMPLETED   ← API は12秒遅れて完了報告
```

| 方式 | ユーザー体験 |
|---|---|
| **遮断なし** | **約16秒**、一部リクエストが 500 |
| ALB 遮断あり | **約4分**、その間ずっと 503（遮断・切替・確認・解除の直列） |

> **16秒を避けるために4分の全断を宣言するのは本末転倒**です。遮断しない方針に変更しました。

副産物として **アプリは切替 API の完了報告より12秒早く復旧する**ことも分かりました。
`SWITCHOVER_COMPLETED` を待ってから復帰作業を始めると、その分だけ停止を長く見せます。

なお `--switchover-timeout` で DB 側所要時間の上限を指定でき、超えたら**自動ロールバックして
blue が稼働継続**します。180秒に設定すれば影響時間の上限を自分で決められます（本番でも 180 を指定）。

### tip 8. 止めるべきは web ではなく job/celery {#tip-8}

ECS のスケールダウン/アップは往復10分前後かかるので、**web を落とすとその分が停止時間に加算**されます。
実測1秒（DB 側）に対して割に合いません。

一方 **job/celery の停止は必須**です。帳票生成や請求書 PDF 生成のような長時間トランザクションが
残っていると、**Blue/Green のガードレールが切替そのものを拒否**します。これは実測1秒とは無関係に残るリスク。

順序の罠もありました。

> **Auto Scaling の `min_capacity` を先に下げないと、`desired_count=0` にしても戻されます。**
> （web min=3 / job min=2 → 復帰時に必ず元の値へ戻す）

そして復帰順の最適化：

1. web の疎通を内部から確認（最後のゲート）
2. ALB / 流入を戻す ← **ここでユーザーから見た停止は終了**
3. job を復帰 + Auto Scaling の min を戻す（以降ユーザー影響なし）

**流入復帰を job 復帰より先に**します。job が落ちている間の celery タスクは Redis に enqueue され、
worker 起動後に処理されるので失われません（数分の遅延のみ）。

### tip 9. ⭐ アプリが返すエラーは「接続不能」ではなく `1290 read-only` {#tip-9}

事前の想定は「接続切断 → DNS 再解決 → 再接続」でした。実際のアプリログはこれでした。

```text
MySQLdb.OperationalError:
  (1290, 'The MySQL server is running with the --read-only option so it cannot execute this statement')
```

**接続には成功するが書き込みが拒否される**形です。これは接続エラーより厄介です。

> 接続エラーなら再接続してリトライする実装は多いですが、**read-only はクエリレベルのエラー**なので
> 「正常応答した DB が拒否した」形になり、フレームワークの自動リトライが働かないことがあります。

CloudWatch Logs のエラーを Issue に自動起票する仕組みが切替直後に反応することも織り込み済みとし、
実際にコメントが1件追加されました。
**切替中に監視を無効化しなかったので、監視が生きていることの確認も同時にできました。**

#### そしてこの機構の説明は間違っていた（訂正）

当初は「切替中 green はレプリカとして read-only のままだから」と説明していました。**これは成立しません。**

RDS イベントによれば green は **12:07:23.234 に読み書き受付を開始**しており、
1290 エラーが出た 12:07:46 は**その23秒後**です。

アクセスログ末尾の所要時間（マイクロ秒）からリクエスト開始時刻を逆算しました。
**通常のヘルスチェック `GET /` は 10〜35ms** ですが、500 を返したものは：

| 500 応答時刻 | 所要 | 逆算した開始時刻 |
|---|---|---|
| 12:07:37.911 | 7,232.6 ms | 12:07:30.7 |
| 12:07:40.318 | 7,275.5 ms | **12:07:33.0** |
| 12:07:46.169 | 15,882.3 ms | **12:07:30.3** |
| 12:07:46.226 | 15,939.5 ms | **12:07:30.3** |

切替は 12:07:20.264 開始 → **12:07:28.109 にリネーム完了**。
つまり **12:07:30.3 / 12:07:33.0 に開始したリクエストは、リネーム完了後に始まっているのに
read-only に当たっています**。

このアプリは `CONN_MAX_AGE = 0`（永続接続なし・毎リクエストで新規接続）なので、
**その時点で DNS を解決した結果が旧インスタンスを指していた**ことになります。

RDS のイベントメッセージ自身がこう警告していました。

```text
The write downtime during the switchover lasted approximately 1 seconds.
DNS propagation might take additional time to complete.
```

> **`CONN_MAX_AGE` を変えても対策になりません**（すでに 0）。
> DNS 伝播はアプリ側の接続設定では制御できないので、対策は RDS Proxy か、
> 切替後に ECS タスクをローリング再起動して名前解決を強制的にやり直させることになります。

### tip 10. 「復旧」をポーリングだけで判定すると短く見積もる {#tip-10}

prod-sub でも prod-main でも、**ポーラーが 200 を観測した後にアプリログの 1290 が残っていました**。

| 実施 | 完全停止 | 部分障害 | 合計 | 切替 API |
|---|---|---|---|---|
| stage リハーサル | 約16秒 | 未計測 | — | 34秒 |
| prod-sub | 約15秒 | 約3秒 | **18秒** | 35秒 |
| **prod-main** | **15秒** | **9秒** | **約24秒** | 35秒 |

prod-main では**完全停止15秒 + 部分障害9秒 = 約24秒**（12:07:22 の最初の失敗から 12:07:46 のエラー停止まで）。部分障害期間は約26リクエスト中6件が 500 で、
残りは成功していました（秒単位の内訳は後述の「切替の瞬間」の図を参照）。

> **復旧時刻は「アプリログのエラーが止まった時刻」で判定すべき**です。
> 単一のポーリングだけだと、prod-main では9秒短く報告することになっていました。

### tip 11. ヘルスチェックの「余裕」の計算式を間違えていた {#tip-11}

当初の見積りはこうでした。

> `interval 30s × unhealthy_threshold 2` = **猶予60秒**なので、16秒の障害では閾値に届かない。

**間違いです。** 正しくは **各ターゲットが失敗しうる回数 = 障害窓 ÷ interval** です。

| 要素 | 値 |
|---|---|
| prod-main の障害窓 | **約24秒** |
| `interval` | 30秒 |
| → 各ターゲットの失敗回数 | **最大1回** |
| `unhealthy_threshold` | **2** |

**24秒 < 30秒だったから閾値に届かなかっただけ**です。
**30秒を超えれば3本すべてが unhealthy 判定**され、全断 + ECS タスク入れ替え（起動に数分）に
発展する可能性がありました。実測約24秒なので**残り約6秒**しかありませんでした。

CloudWatch では `UnHealthyHostCount = 0` / `HealthyHostCount = 3` を全期間で維持していましたが、
**それは余裕があったからではありません。**

根っこの問題は、ヘルスチェックパスが `/` で、かつ Django 側が
`SESSION_ENGINE = db` + `SESSION_SAVE_EVERY_REQUEST = True` のため
**参照のみのリクエストでも DB 書き込みが発生する**ことでした。
「ヘルスチェックが DB 書き込みに依存している」ので、DB が書き込み不可になると即 500 です。

> **tip: ヘルスチェックエンドポイントが DB 書き込みを伴っていないか、移行前に確認してください。**
> これは移行に限らず、フェイルオーバー・再起動・パッチ適用のすべてで効いてきます。

### tip 12. AWS CLI のオプションは create と describe で対称ではない {#tip-12}

本番実施中にこれで失敗しました。

```text
aws: [ERROR]: Unknown options: --blue-green-deployment-name, myproj-prod-84
```

**`--blue-green-deployment-name` は `create-blue-green-deployment` にはあるが
`describe-blue-green-deployments` には存在しません。** describe 側は

```bash
--filters Name=blue-green-deployment-name,Values=myproj-prod-84
```

が正しい形です。

このとき `$GREEN` が空文字になり、後続の `modify-db-instance` が
`DBInstanceIdentifier must not be blank` で弾かれたため**実害はありませんでした**。
運が良かっただけなので、手順に `-z` チェックを追加しました。

> **本番手順のシェル変数には必ず空チェックを入れる。** 空文字が別のリソースに当たる形の
> コマンドだったら、本番を壊していました。

### tip 13. Performance Insights の SQL は途中で切られる → EXPLAIN に流せない {#tip-13}

切替前に blue(8.0) と green(8.4) へ同一クエリを投げて `EXPLAIN FORMAT=JSON` を比較したかったのですが、
**PI の Top SQL 表と `DescribeDimensionKeys` は500バイトで切られます**（SQL text セクションや `GetDimensionKeyDetails` なら MySQL は最大 4,096 バイトまで取れます）。Django が生成する
`SELECT <約100カラム> ... WHERE ...` は**WHERE 句が切り落ちる**ので、本番の文をそのまま流せません。

やったこと：

- 完全な形が判明している上位2件は **verbatim** で実行（合計 DB Load の 30.9%）
- 残りは **Django ORM で同一の文を生成**して blue / green の両方に投げる

実行は **job コンテナ内から `aws ecs execute-command`** で行いました。VPC 内から、コンテナの環境変数にある認証情報を
使うので、**DB 認証情報を手元で扱わずに済みます**（green は blue と同一 SG / 同一サブネットグループ
なので到達可能）。

結果は **`access_type` / `key` / `used_key_parts` / `rows_examined_per_scan` / `filtered` が全ケース同一**。
差分は `prefix_cost`（オプティマイザ内部のコスト単位で、実行時間ではない）のみでした。

> **残るリスク:** cost モデルが変わったことは事実なので、**複数プランの cost が拮抗しているクエリでは
> 選択が反転する可能性があります**。これは EXPLAIN の事前比較では網羅できず、切替後に PI で観測するしかありません。

### tip 14. 8.4 で実際に変わった変数と、戻せるかどうか {#tip-14}

事前の警告リストに載っていないものがありました。

| 変数 | 8.0.41 | 8.4.10 | `ApplyType` | revert |
|---|---|---|---|---|
| `innodb_adaptive_hash_index` | `1` | **`0`** | dynamic | **無停止で戻せる** |
| `innodb_io_capacity` | `200` | **`10000`** | dynamic | 無停止 |
| `innodb_change_buffering` | `all` | **`none`** | dynamic | 無停止 |
| **`innodb_buffer_pool_instances`** | **`8`** | **`2`** | **static** | **再起動が必要** |

**`innodb_buffer_pool_instances` の 8 → 2 は事前の警告リストに挙がっていませんでした。**
db.m6g.2xlarge（8 vCPU）でバッファプールを2分割にするとプール mutex の競合が増えうるため
重点監視項目に追加しました（結果的に競合は観測されませんでした）。
8.4 では固定値ではなく論理 CPU 数 ÷ 4 から算出されるため、8 vCPU で 2 は仕様どおりです。

> **tip: `describe-engine-default-parameters --db-parameter-group-family mysql8.4` を叩いて、
> 変わった変数の `ApplyType` を移行前に確認しておく。**
> 「問題が起きたとき無停止で戻せるのはどれか」を事前に知っていると、判断が速くなります。

### tip 15. 切替後の PI 比較は「時間帯の交絡」で簡単に嘘になる {#tip-15}

切替1時間後に PI を比較したところ、負荷が劇的に下がっていました。

| 指標 | 8.0.41（11:07–12:07） | 8.4.10（12:10–13:04） |
|---|---|---|
| 平均 DB Load | 0.434 AAS | 0.128 AAS |
| `Innodb_buffer_pool_read_requests` | 251,804/s | 73,536/s |

**8.4 の改善効果ではありません。12:10–13:04 が昼休みだからです**
（12時台は 10,502 req/h、09時台のピークは 36,046 req/h）。

逆方向の交絡もありました。

| 指標 | 8.0.41（長期稼働） | 8.4.10（稼働約1時間） |
|---|---|---|
| ディスク物理読み取り | 0.2/s | **15.9/s（約80倍）** |
| バッファプールヒット率 | 99.9999% | 99.9783% |

新しく `wait/io/file/innodb/innodb_data_file` が 12.0% で出現しましたが、これも
**8.4 による劣化ではなくバッファプールが冷えているだけ**です（絶対値としてヒット率 99.98% は健全）。

一方で予想が当たった点：`innodb_adaptive_hash_index` ON→OFF により
**`wait/synch/sxlock/innodb/btr_search_latch` が消滅**しました。
ただし 8.0 でも 0.6% しかなかったので、失った利得も限定的です。

> **tip: 移行前に PI のベースラインを別ファイルに記録しておく。**
> **PI の履歴は切替でリセットされます**（新インスタンスになるため）。
> 旧 blue が `-old1` として残っている間だけ、同日・直前の窓と突合できます。

そして**そのベースライン記録自体が別の発見を生みました**。
社内 Issue で「主役」とされていたテーブルが**現在の Top 12 に現れず**、
別のテーブルが 25.3%（ピーク窓では 42.9%）を占めていました。
さらに副産物として、**インデックス欠落による全表スキャン2件（DB 負荷の約31%）** を発見し、
移行とは別の Issue に分離しました。

> **移行前のベースライン取得は「比較のため」だけでなく、それ自体が現状把握の機会になります。**

### tip 16. リハーサルの provisioning 時間は本番に当てはまらない {#tip-16}

1回目のリハーサルでは Blue/Green の provisioning に **約65分**（うち green の
`storage-initialization` が約58分）かかりました。

原因は、**ソースがスナップショットから復元したばかりのクローンでストレージが遅延ロード中**だったこと。
本番はストレージが温まっているので短くなります（実測：200GB の prod-main は
19:49 開始で翌朝までに完了、20GB のクローンは約12分）。

> ただし**1時間以上かかる前提で計画**してください。**この間 blue は通常稼働**なので、
> provisioning が長引いてもユーザー影響はゼロです（計画上の問題にならない）。

そして最初にやってしまった説明ミス：

> **「provisioning 65分」を実測値テーブルに並べると、サービス停止65分と誤読されます。**
> 「ユーザー影響あり/なし」の列を必ず付けてください。関係者への説明が完全に変わります。

### tip 17. Blue/Green は前提条件を満たしていればソースを再起動しない {#tip-17}

Blue/Green はソースの binlog を必要とします。今回は

- `binlog_format = ROW`（両インスタンス `ParameterApplyStatus: in-sync`）
- `binlog_row_image = full`
- `backup_retention_period = 7`（binlog 自体が有効）

がすべて事前に満たされていたため、**BG 作成時にソースを modify / reboot する必要がありませんでした**。
リハーサルでもソース側の provisioning 中イベントに shutdown / restart は一切出ていません。

> **逆に言えば、これらが未設定なら BG 作成の時点でソースの再起動が必要になります。**
> 「Blue/Green ならノーダウンタイム」の前提条件です。先に確認してください。

### tip 18. 心配していたが問題にならなかったこと {#tip-18}

移行の話でよく挙がる懸念のうち、**RDS では該当しなかった**もの：

- **`mysql_native_password`**：コミュニティ版 8.4 ではデフォルト無効です。
  RDS mysql8.4 で**新規ユーザーの既定プラグインは `caching_sha2_password`**（`authentication_policy` で変更可）
  ですが、**`mysql_native_password` プラグイン自体は有効なまま**で（実機のパラメータは `ON` /
  `IsModifiable=false`）、プリチェックに警告として出ても
  **既存 DB ユーザーの認証は壊れません**（実機確認済み）
- **`SET_USER_ID` 権限の削除**：8.4 では `SET_ANY_DEFINER` に置き換わります（今回は影響なし）

プリチェック結果は本番実データで **`Errors: 0` / `Warnings: 3`** でした。

---

## 5. 切替のタイムライン

### 5-1. 全体（2日間）

#### 2026-07-30（木）

| 時刻 (JST) | 作業 | ユーザー影響 |
|---|---|---|
| 11:48 | 現状調査完了（live AWS + 公式ドキュメント）。課金インパクトとアップグレードパスを確定 | — |
| 12:04–12:09 | **stage を in-place で 8.4.10 へ**（約5分の停止）。ここで **MEMCACHED の2段方式が必要**と判明 | stage のみ |
| 14:32 | **リハーサル1**（prod-main スナップショットのクローン、200GB）。書き込み停止**1秒**、プリチェック `Errors: 0` を確認 | なし |
| 15:00 頃 | **カスタム OG の制限に気付き手順を全面修正**（リハーサル1は `default:mysql-8-0` で偶然回避していた） | — |
| 16:00 頃 | **リハーサル2**（prod-sub スナップショット + カスタム空 8.0 OG）。2段構えを検証。BG 作成12分 / green アップグレード7.5分 / 書き込み停止1秒（再現） | なし |
| 17:00 頃 | **stage で BG 切替テスト**（バージョン変更なし）。**アプリ停止16秒**を実測 → **ALB 遮断を手順から削除**。同時に **Terraform state 破損**を発見し修正手順を確立 | stage のみ |
| **17:25:26–17:26:43** | **prod の 8.0 用 OG から MEMCACHED を削除**（第1段、77秒）。**全リクエスト 200 / DB エラー0件** | **なし（実測確認）** |
| 17:30 | prod の 8.4 用 PG/OG 作成 + **PI ベースライン記録** | なし |
| 19:00–19:40 | アプリのリリース（migration 含む）。`migrate` は 19:39:28 → 19:40:32（64秒、`exitCode: 0`） | 通常リリース |
| **19:49:39** | **prod-main の BG 作成**（`--target-engine-version` は指定しない） | **なし** |
| **19:50:00** | **prod-sub の BG 作成** | **なし** |
| 19:50〜 | BG 監視を稼働開始（10分毎）。**ここから migration 禁止期間** | — |

#### 2026-07-31（金）— 標準サポート終了日

| 時刻 (JST) | 作業 | 実測 |
|---|---|---|
| 08:52 | **Go/No-Go 判定**：BG 両方 `AVAILABLE`、13時間分のレプリケーション遅延実績が**最大 1.0s / 60秒を超えたデータポイント0件**、監視 160回実行アラート0件、夜間 one-off タスク29件に DDL 混入なし → **Go** | — |
| **08:52:24–09:02:45** | **両 green を 8.4.10 へアップグレード**（並行、**10分21秒**）。Multi-AZ の sub も同時完了。クロスバージョンレプリケーションは**1分の中断で復帰** | 見積り 10〜25分 → 実測 10分 |
| 09:05 | プリチェックログ取得：**両方 `Errors: 0`**、項目12 memcached は `No issues found`（第1段が効いている） | — |
| 09:10 | **CLI オプションの誤りで一度失敗**（`describe-blue-green-deployments --blue-green-deployment-name` は存在しない）。`$GREEN` が空になり後続が弾かれたため実害なし | — |
| 10:00 | **green の実行計画検証**：blue と green に同一クエリを投げて `EXPLAIN FORMAT=JSON` 比較 → **プラン形状は全ケース一致**、退行なし → 続行可 | — |
| 11:00 | celery キューの空確認（`llen=0` / `unacked=0`）※切替直前にしか確認できない唯一の項目 | — |
| **11:02:58–11:03:33** | **prod-sub 切替**（最終リハーサル + state 張り替えの実演）。`--switchover-timeout 180`、**ALB 遮断なし** | **アプリ停止 18秒** / 切替 API 35秒 |
| 11:10 | sub の **Terraform state 張り替え**（`state rm` + `import`）→ `plan` が `0 to destroy` に。**危険な `identifier` リネーム差分が消滅** | — |
| 11:30 | sub の実測をもとに prod-main を最終判断。**失敗モードが `1290 read-only` であることが判明**し main への申し送りに追加 | — |
| 11:50 | celery キューを再度空確認、job を 0 に、1秒ポーリング開始 | なし |
| **12:07:17–12:07:52** | **prod-main 切替**（告知枠 12:00–13:00 内、昼の谷を狙う）。**ALB 遮断なし・web 停止なし** | **アプリ停止 約24秒** / 影響 約50リクエスト |
| 12:10 | 新本番の検証（job コンテナから Django 接続経由）：`VERSION=8.4.10` / `read_only=0` / 書き込みテスト OK | — |
| 12:15 | **Terraform state 張り替え**（`state rm` + `import`）+ `rds_params` に `engine_version = "8.4.10"` を反映 → `0 to destroy` | — |
| 12:20 | job 復帰、Auto Scaling の min を戻す | — |
| 13:00–14:00 | **PI 比較**（old1 が旧履歴を保持している間に同日直前1時間と突合）。退行の証拠なし | — |
| 夕方 | old1 のスナップショット取得 → **`--no-deletion-protection`（main のみ）** → 削除 → `plan` 再確認 | — |
| 夕方 | BG デプロイ削除、BG 監視を撤去 | — |

**MySQL 8.0 標準サポート最終日に完了。Extended Support 課金は発生せず**
（old1 を当日中に削除。8.0 のまま残せば prod-main 8 vCPU + prod-sub 4 vCPU で約 $29/日）。

### 5-2. 切替の瞬間（prod-main、秒単位）

RDS 内部で何が起きているかと、アプリから何が見えるかを並べます。

![prod-main の切替の瞬間を秒単位で示したタイムライン図。RDS 内部・1秒ポーラー・アプリログの3レーンで、12:07:20 の切替開始から 12:07:52 の完了報告までを並べ、RDS 起因の書き込み停止は約1秒だがアプリから見た停止は完全停止15秒と部分障害9秒を合わせた約24秒になることを示している](/blogs/images/rds-mysql-84-switchover-timeline.png)

**RDS 起因の書き込み停止は 1秒。アプリから見た停止は約 24秒。差の大半は DNS 伝播と再接続です。**

### 5-3. 切替タイミングの選び方（事前検討）

> 以下は**切替前に検討した内容**です。実際には準備が前倒しで終わり、
> 告知枠の内側で 12:07 に実施しました（5-1 / 5-2 が実績）。

「16秒（stage 実測）で済む」と分かった時点で、**業務時間中の実施が現実的**になりました。

| 案 | 影響リクエスト数（概算） | 休日出勤 | 深夜 | Extended Support |
|---|---|---|---|---|
| **7/31(金) 12:30**（昼の谷） | **約47** | なし | 準備30分のみ | **$0** |
| 8/1(土) 15:00 | 約12 | あり | なし | $24〜36 |
| 8/2(日) 11:00 | 約6 | あり | なし | $38〜74 |

12時台を5分刻みで実測すると、**谷は 12:25–12:50、最小は 12:35–12:40（2.34 req/s）、
13:00 に 9.51 req/s へ急回復**。時間帯別リクエスト数は以下でした。

| 時刻 | トラフィック | 16秒あたり |
|---|---|---|
| 平日 09時（ピーク） | 36,046/h | 約 160 |
| 平日 12時（昼の谷） | 10,502/h | **約 47** |
| 平日 22時 | 2,810/h | 約 12 |
| 日曜 14時 | 1,375/h | 約 6 |

**宣言枠は30分（12:20–12:50）、実行は 12:30、撤退期限 12:50。**
30分にした理由は**リトライ余地**です（ガードレール拒否で1回失敗しても、再試行が谷に収まる）。

利用者への告知は実態に沿って：

> 12:20〜12:50 の間に、**最大1分程度**接続エラーが発生する可能性があります

**撤退ラインを事前に決めておく**のが精神的に効きました。以下のいずれでも
**blue は完全に無変更**なので、月曜は 8.0 のまま通常営業できます。

| 事象 | 対応 |
|---|---|
| green 検証で問題発見 | 切替せず BG 削除して撤退 |
| ガードレール拒否 / タイムアウト | RDS が自動ロールバック（両環境に変更なし） |
| 12:50 までに完了しない | 撤退し、8/2(日) に再計画 |

---

## 6. 切替成功後は、実質ロールバックできない

**「old1 を残しておけばロールバックできる」は、実質的には成り立ちません。**

切替後に新本番へ書き込まれたデータは old1 に反映されないため、
**ロールバックは「切替後の書き込みを捨てる」選択**です。数時間以降は現実的ではありません。

実際の備えは別のところにありました。**8.4 で変わった変数のうち3つは dynamic で無停止に戻せる**
（tip 14 の表）。翌朝のピークへの備えは「old1 の保持」ではなく「無停止で戻せる手段の確認」でした。

そう整理できたので、**old1 は当日中に削除**しました（残せば Extended Support 課金対象）。

---

## 7. やってよかったこと（効果が大きかった順）

振り返って、効果が大きかった順：

1. **stage を先に in-place で上げた** — MEMCACHED の2段方式は、ここで踏まなければ本番当日に踏んでいた
2. **リハーサルを2回やった** — 1回目がカスタム OG の制限を偶然回避していたので、
   1回で止めていたら本番当日に `InvalidParameterCombination` を見ていた
3. **stage で BG 切替テストをした（バージョン変更なし）** — 「アプリ停止16秒」と
   「Terraform state が壊れる」の2大発見はここ。**バージョンを変えなくても BG は作れる**ので、
   切替の挙動だけを安全に測れます
4. **prod-sub を先に切り替えた** — 本番環境・本番トラフィックでの最終リハーサル。
   `1290 read-only` の失敗モードと state 張り替えを、影響の小さい方で1度通してから main に臨めた
5. **PI ベースラインを別ドキュメントに記録した** — 切替で PI 履歴がリセットされるため、
   これが無いと「退行したかどうか」を後から議論できない
6. **手順を Markdown で書き、実測値で毎回上書きした** — 訂正が4回入りました。
   誤った機構説明（tip 9）も後から訂正しています。
   **「手順書は実施のたびに間違いが見つかる前提の生き物」**として扱うのが正解でした

---

## 8. 残った課題

| # | 課題 |
|---|---|
| 1 | **ヘルスチェックが DB 書き込みに依存**（`/` + `SESSION_SAVE_EVERY_REQUEST = True`）。あと6秒で全断だった |
| 2 | **RDS Proxy の導入検討** — 切替/フェイルオーバー時のコネクション切替を吸収でき、アプリ改修なしで DNS 伝播問題を回避できる可能性 |
| 3 | **prod-main が Single-AZ** — sub は Multi-AZ だが本体は Single-AZ。可用性要件として意図どおりか要確認 |
| 4 | **メンテナンス手順の定型化** — 切替後に ECS タスクをローリング再起動して名前解決を張り直す手順 |
| 5 | **一意インデックスを参照しない外部キー3件** — 既存 FK は動くが、8.4.0 以降は既定で新規作成が拒否される。migration で再作成すると失敗する（アプリ側に共有済み。`restrict_fk_on_non_standard_key = OFF` で回避可） |
| 6 | **`ANALYZE TABLE` の検討** — InnoDB の永続統計自体は引き継がれるが、8.4 でコストモデルが変わったので再収集して再評価する価値がある（初回クエリが遅いのはバッファプールが冷えていることが主因） |
| 7 | **`innodb_buffer_pool_instances` 8→2 の継続監視** — static なので戻すには再起動が必要 |

---

## まとめ：この移行から持ち帰るべき3つ

1. **Blue/Green の「ダウンタイム1秒」は DB の書き込み停止のことで、アプリから見た停止ではない。**
   実測は 18〜24秒で、差の大半は **DNS 伝播**。ここはアプリの接続設定では制御できません。
2. **Blue/Green は Terraform state を壊す。** `DbiResourceId` が変わるので、
   **old1 を削除する前に** `state rm` + `import` が必須。忘れると本番 DB を新規作成する plan が残ります。
3. **リハーサル環境は本番と1箇所も違えてはいけない。**
   Option Group が違うだけで、本番当日に初めて出るエラーが1つ増えます。

そして最後にひとつ。**期限のある移行では、まず「逃げ道の有無」を確認してください。**
今回は `EngineLifecycleSupport` が既存インスタンスで変更不可だったため、
「オプトアウトして課金を止める」という選択肢が最初から存在しませんでした。
これが分かったのが期限の2日前だったので、2日で走り切ることになりました。
