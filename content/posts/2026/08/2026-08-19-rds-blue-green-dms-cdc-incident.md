---
title: "RDS の Blue/Green 切替で DMS が静かに死んだ話 — 18日間気付かなかった監視の三重の穴"
date: 2026-08-19
lastmod: 2026-08-19
slug: "rds-blue-green-dms-cdc-incident"
draft: false
categories: ["クラウド/インフラ"]
tags: ["aws", "dms", "rds", "mysql", "監視"]
---

MySQL 8.0 のサポート終了に伴う 8.4 へのメジャーバージョンアップを Blue/Green デプロイで実施した。
アプリの停止時間は 25 秒。移行そのものは成功だった。

**その裏で、同じ DB を参照していた DMS の CDC が停止し、18 日間誰も気付かなかった。**

この記事は、その障害の経緯・復旧作業・本来やるべきだったことの記録である。
DMS Serverless の運用上の落とし穴がいくつも出てきたので、同じ構成を使っている人の役に立てば幸いだ。

## TL;DR

- **Blue/Green 切替はインスタンス実体を入れ替えるため、binlog のファイル名とオフセットが無効になる。CDC は `Error 1236` で FATAL 停止し、`resume-processing` では二度と復帰できない**
- 監視は三重に壊れていた。EventBridge のイベントパターンが別製品向け、アラームが「メトリクス欠損 = 正常」設定、自動復旧 Lambda が復旧不能な起動タイプ固定
- 復旧作業でも DMS Serverless の制約を 4 つ踏んだ。とくに **config を作り直すと ARN が変わり、CloudWatch アラームの dimension が壊れる**
- 復旧の途中で **`mysql` スキーマ（パスワードハッシュを含む）が full load の対象になっている**ことに気付いた。`%.%` の include + exclude 方式の危うさ
- 教訓のうち最大のものは、**監視は「発火する事象」ではなく「検知したい事象」で確かめる**、ということ。
  今回のルールは計画停止では発火し、障害でだけ発火しなかった
- そして **復旧作業そのものが、残っていたアラームを壊した**。「復旧した」は「解決した」ではない
- **binlog 座標の不連続は避けられないが、それが障害になることは避けられる。** 切替前に CDC を止めて
  `CdcStartTime` で再開する手順にしていれば、欠損は数十秒で済んだ

## 構成

RDS MySQL の変更を DMS の CDC (Change Data Capture) で拾い、S3 に Parquet で吐いて分析基盤の入力にしていた。
DMS は Serverless 版（`aws_dms_replication_config`）を使い、Terraform で管理していた。

![RDS MySQL から DMS Serverless の CDC を経由して S3 に Parquet を出力する構成図。Blue/Green 切替によって green 側の binlog 座標が blue と一致せず、DMS が Error 1236 で FATAL 停止し、S3 への出力がゼロになる流れを示している](/blogs/images/rds-blue-green-dms-cdc-incident-architecture.png)

CDC の対象は `table_mappings` で全スキーマ・全テーブル。

```json
{
  "rules": [{
    "rule-type": "selection",
    "rule-action": "include",
    "object-locator": { "schema-name": "%", "table-name": "%" }
  }]
}
```

**この設定が後で効いてくる。**

## 何が起きたか

### 発端: Blue/Green 切替

MySQL 8.0 は標準サポート終了が迫っており、放置すると Extended Support の課金が始まる。
8.4 へのメジャーバージョンアップを Blue/Green デプロイで実施した。

Blue/Green デプロイは、現行（blue）と同一構成の green を作り、レプリケーションで追従させたうえで、
エンドポイントを green に切り替える方式だ。ダウンタイムは切替の瞬間だけで済む。実際 25 秒だった。

### DMS から見ると何が起きたか

DMS の CDC は、**「どこまで読んだか」を binlog のファイル名 + オフセットで記憶している**。

```text
RecoveryCheckpoint: checkpoint:V1#2#mysql-bin-changelog.473018:7237787:...
```

Blue/Green の切替でエンドポイントの向き先が green に変わると、DMS は green に再接続し、
**blue の座標である `mysql-bin-changelog.473018` の続きを要求する**。

green は blue の複製ではあるが、binlog は別物だ。そんなファイルは存在しない。

```text
Last Error Error 1236 reading binary log. Stop Reason FATAL_ERROR Error Level FATAL
```

MySQL の Error 1236 は "Could not find first log file name in binary log index file"。
DMS はこれを FATAL として扱い、レプリケーションは停止した。

**そして 18 日間、S3 への出力はゼロになった。**

切替は 12:07 に完了し、S3 への最終書き込みは 12:01 だった。

## なぜ 18 日間気付かなかったのか

自動復旧の Lambda も、SNS 通知も、CloudWatch アラームも用意してあった。**全部機能していなかった。**

![監視の三重の穴を並べた図。穴1 は EventBridge のイベントパターンが DMS Classic 向けで障害イベントに一致しないこと、穴2 は CloudWatch アラームが treat_missing_data = notBreaching でメトリクス欠損を正常とみなすこと、穴3 は自動復旧 Lambda が resume-processing 固定で checkpoint 無効時に復旧できないことを、それぞれ設計上の期待・実際・結果の三段で示している](/blogs/images/rds-blue-green-dms-cdc-incident-monitoring-holes.png)

### 穴 1: 障害のイベントだけがパターンに一致しなかった

```hcl
event_pattern = jsonencode({
  source      = ["aws.dms"]
  detail-type = ["DMS Replication Task State Change"]
  detail      = { eventType = ["REPLICATION_TASK_STOPPED", "REPLICATION_TASK_FAILED"] }
})
```

これは **DMS Classic（レプリケーションインスタンス + タスク）** のイベント形式である。
DMS Serverless は別のソースタイプでイベントを出す。

障害後に「全 `aws.dms` イベントをログに落とすだけ」のルールを一時的に仕掛けて実物を採取したところ、こうだった。

```json
{
  "detail-type": "DMS Replication State Change",
  "source": "aws.dms",
  "resources": ["arn:aws:dms:ap-northeast-1:123456789012:replication-config:XXXXXXXX"],
  "detail": {
    "type": "REPLICATION_CONFIG",
    "category": "StateChange",
    "eventType": "REPLICATION_INITIALIZING",
    "detailMessage": "Replication with resource id, 'XXXXXXXX', is initializing."
  }
}
```

### ここで私は診断を間違えた

この時点で私はこう結論づけた——「`detail-type` も `eventType` も間違っている。
このルールは作られてから一度も発火していない」。根拠はこれだった。

```text
TriggeredRules : データポイントなし
storedBytes    : 0        # Lambda のロググループ
```

**この診断は間違いだった。** 後で Lambda のログを直接読んで分かった。

まず `storedBytes` は**反映が数時間遅れる**。0 だからログが無い、とは言えない。
実際にはログストリームが存在し、中身もあった。

そして DMS Serverless は、**2 系統のイベントを両方出していた。**

| detail-type | eventType | resources |
|---|---|---|
| `DMS Replication State Change` | `REPLICATION_*` | **replication-config ARN** |
| `DMS Replication Task State Change` | `REPLICATION_TASK_*` | **task ARN** |

つまり旧ルールが見ていた `DMS Replication Task State Change` は**実在する**。
計画停止のときは `REPLICATION_TASK_STOPPED` が飛び、**ルールは発火していたし、
Lambda も起動していた。**

では何が壊れていたのか。ログにこう出ていた。

```text
[INFO]  Received event: {"detail-type": "DMS Replication Task State Change",
        "resources": ["arn:aws:dms:...:task:serv-res-id-000000000000-xxx"], ...}
[ERROR] replicationConfigArn が指定されていません
```

問題は 2 つだった。

**1. 障害のイベントだけが別系統だった**

実測した全 eventType のうち task 系に存在するのは `REPLICATION_TASK_STARTED` と
`REPLICATION_TASK_STOPPED` の 2 つだけ。**`REPLICATION_TASK_FAILED` は出力されない。**
障害時に飛ぶのは config 系の `REPLICATION_FAILED` である。

だから「計画停止では発火するが、**本当に必要な障害のときだけ発火しない**」という
最悪の挙動になっていた。

**2. 発火しても Lambda が対象を特定できなかった**

Lambda は `detail.replicationConfigArn` を読もうとしていたが、
**このフィールドはどちらの系統のイベントにも存在しない。**
config ARN は `resources` 配列から取る必要がある。
task 系イベントの `resources` に入っているのは task ARN なので、そもそも取れない。

### 教訓: 「動いていない」の診断にも証拠の質がある

私は「メトリクスにデータが無い」「ロググループが 0 バイト」という 2 つの間接証拠から
「一度も発火していない」と断定した。**どちらも反映遅延のある値**で、断定の根拠にはならなかった。

ログを直接読めば 5 分で分かったことを、間接証拠で誤って結論づけた。
**監視の不備を調べるときに、監視の値だけを見て判断してはいけない。**

### 穴 2: アラームが「メトリクス欠損 = 正常」だった

CDC レイテンシや CPU 使用率のアラームは張ってあった。しかし。

```hcl
treat_missing_data = "notBreaching"
```

**レプリケーションが停止すると、メトリクスの送出自体が止まる。**
`notBreaching` は「データが無い = 閾値を超えていない = OK」と解釈する。

つまり **死ねば死ぬほど OK になる**アラームだった。4 本すべてが `OK` を表示したまま 18 日が過ぎた。

これは DMS に限った話ではない。**「稼働しているべきもの」の監視を、閾値超過型のメトリクスアラームだけで
組んではいけない。** 止まったときに何のシグナルも出ないからだ。

### 穴 3: 自動復旧 Lambda が復旧不能な起動タイプ固定だった

仮にイベントパターンが正しかったとしても、Lambda はこう書かれていた。

```python
client.start_replication(
    ReplicationConfigArn=arn,
    StartReplicationType="resume-processing"
)
```

`resume-processing` は checkpoint からの再開である。
**今回のように checkpoint そのものが無効になった障害では、何度リトライしても失敗する。**

三つの仕組みが、三つとも別の理由で機能しなかった。

## 復旧作業

方針は 2 択だった。

| 案 | 内容 | 欠損 |
|---|---|---|
| A | CDC を現時点から再開 | 18 日分が永久欠損 |
| B | `full-load-and-cdc` に変更して全量ロードからやり直す | 欠損なし |

B を選んだ。ここから DMS Serverless の制約を次々と踏むことになる。

### 制約 1: `replication_type` は provisioning 済みの config では変更できない

Terraform の plan は「in-place 更新 1 リソース」と出た。apply したら拒否された。

```text
InvalidParameterValueException: replication-type ... cannot be modified as the replication
is in deprovisioned. You can only modify replication configs before provisioning capacity.
```

**一度でもキャパシティをプロビジョニングした config は `replication_type` を変更できない。**
停止しても解決しない（すでに停止していた）。

レプリケーションのレコードだけを削除する `DeleteReplication` のような API があれば
リセットできそうなものだが、**そんな API は存在しない**（`delete-replication-config` しかない）。

結論: **config ごと作り直すしかない。**

```bash
terraform apply -replace='module.dms.aws_dms_replication_config.this["main"]'
# Apply complete! Resources: 1 added, 0 changed, 1 destroyed.
```

### 制約 2: 作り直すと ARN が変わる

ここが一番効いた。

| | ARN |
|---|---|
| 旧 | `arn:aws:dms:...:replication-config:myapp-prod-dms` |
| 新 | `arn:aws:dms:...:replication-config:K7QWZ3MXR2NPLVBD5TYAH8FJCS` |

**旧 ARN は識別子ベースだったが、再作成するとランダムなリソース ID が振られる。**

DMS のメトリクスの dimension はこのリソース ID を使う。

```text
実際のメトリクス : ReplicationConfigId=123456789012:K7QWZ3MXR2NPLVBD5TYAH8FJCS
アラームの設定   : ReplicationConfigId=123456789012:myapp-prod-dms
```

Terraform 側は識別子から dimension を組み立てていた。

```hcl
locals {
  alarm_dimension = "${account_id}:${var.prefix}-dms"   # ← 作り直すと一致しなくなる
}
```

**復旧作業そのものが、残っていたアラームまで壊した。**

正しくは ARN から導出すべきだった。

```hcl
"${account_id}:${element(split(":", aws_dms_replication_config.this.arn), 6)}"
```

なお `treat_missing_data` を `breaching` に直す修正を並行して用意していたのだが、
**dimension が壊れた状態で `breaching` にすると、正常でも永久に鳴り続ける**ことになる。
危うくそのまま適用するところだった。修正の順序が重要になる場面である。

### 制約 3: `table_mappings` は in-place で変更できる

一方で `table_mappings` は provisioning 済みでも変更できた（ARN も維持される）。
**`replication_type` だけが特別扱い**ということらしい。

### 制約 4: `start-replication`（fresh start）は初回実行時のみ有効

設定を直して再実行しようとしたら、また拒否された。

```text
InvalidParameterCombinationException: Start Type : START_REPLICATION,
valid only for replications running for the first time
```

一度でも走ったレプリケーションには `resume-processing` か `reload-target` しか使えない。
全量ロードをやり直したいので `reload-target` が正解。

自作の復旧スクリプトは `start-replication` を決め打ちしていた。
**「中断して設定を直してから再実行する」という、スクリプトが本来いちばん必要な場面で使えなかった。**

### ちなみに全量ロードは想定よりずっと遅かった

777 テーブル / 62.5GB の full load を DCU 最大 4 で流したところ、
開始から 53 分で進捗 9% だった。単純外挿で **10 時間超**。
しかも残りに最大のスキーマ（56GB）が控えている。

「数時間で終わるだろう」という見積もりは甘かった。
**全量ロードは『いざとなればやり直せる』と気軽に言える操作ではない。**
だからこそ後述の「そもそも全量ロードを避ける」が効いてくる。

## 復旧の途中で見つけた別の問題

全量ロードが走り出した直後、対象テーブル数が想定と合わないことに気付いた。

- 事前に `information_schema` から数えたアプリ系テーブル: **777**
- DMS が読み込み対象にしたテーブル: **939**

162 件多い。内訳を `describe-replication-table-statistics` で取ったところ、こうだった。

| スキーマ | 件数 |
|---|---:|
| アプリ系 9 スキーマ | 777 |
| `performance_schema` | 114 |
| **`mysql`** | **47** |
| `sys` | 1 |

`mysql` スキーマの中身を見て手が止まった。

```text
user, global_grants, tables_priv, columns_priv, procs_priv, proxies_priv,
password_history, slave_master_info, ...
```

**`mysql.user` は全 DB ユーザーの `authentication_string`、つまりパスワードハッシュを保持している。**
これが Parquet として S3 に書き出されようとしていた。権限テーブル群も同様だ。

### なぜ今まで表面化しなかったのか

`table_mappings` は以前から `%.%` だった。しかし **CDC ではシステムスキーマの変更が binlog に乗らない**。
だから S3 にはアプリ系 9 スキーマの prefix しか存在しなかった。

**full load は binlog を経由せず直接テーブルを読む。切り替えた瞬間に初めて露出する。**

そして重要な点として、**DMS は MySQL のシステムスキーマを自動除外しない**。
私は「さすがに除外するだろう」と根拠なく思い込んでいた。

幸い検知が早く、`loaded=19/939` の時点で `stop-replication` できた。
システムスキーマは全件 `Before load` のままで、**S3 には一度も書かれていない**。

### 教訓: `%.%` + exclude は allowlist ではない

これが今回いちばん普遍的な教訓かもしれない。

```json
{ "rule-action": "include", "object-locator": { "schema-name": "%" } }
```

**「全部入れてから要らないものを除く」方式は、自分が知らないものを防げない。**
今回は「システムスキーマが対象に入る」ことを知らなかったから、除外リストにも入っていなかった。

必要なスキーマを列挙する allowlist なら、この問題は原理的に起きなかった。

## 本来やるべきだったこと

### 1. Blue/Green の事前チェックに「binlog を読む下流」を入れる

移行計画のドキュメントを後から grep したら、DMS への言及は SNS 通知先の確認 1 行だけだった。
**下流の棚卸しがされていなかった。**

Blue/Green は「アプリから見れば無停止」だが、**binlog の連続性を前提にしている全てのものを壊す**。
DMS に限らず、レプリカ、Debezium、その他 CDC ツールすべてが対象になる。

チェックリストに入れるべきだったのはこうだ。

- 切替前: **CDC を停止する**（FATAL 状態に落とさない）。停止時刻を記録する
- 切替後: **`resume-processing` は使えない前提で**復旧方式を選ぶ
- 切替により CDC の checkpoint が失われることを、関係者に事前に共有する

### 実は全量ロードすら不要だったかもしれない

これは障害の後に気付いたのだが、`StartReplication` API は **CDC の開始位置を指定できる**。

```json
{
  "StartReplicationType": "",
  "CdcStartTime": "1970-01-01T00:00:00",
  "CdcStartPosition": "",
  "CdcStopPosition": ""
}
```

つまり本来の理想的な手順はこうだったはずだ。

1. 切替**前**に CDC を停止し、停止時刻を記録する
2. Blue/Green 切替
3. `--cdc-start-time <停止時刻>` で再開する

**欠損は切替の数十秒だけで、全量ロードは要らない。**
今回の「62.5GB を読み直す」という重い復旧は、事前に止めてさえいれば避けられた可能性がある。

（`full-load-and-cdc` の config でこれが効くのか、`cdc` に戻す必要があるのかは未検証。
検証環境で先に確かめるべき事項として残っている）

**「壊れることが分かっている操作」の前に止めておく**という当たり前のことが、
復旧コストを数時間から数十秒に変えたかもしれない、という話である。

### 2. 「作った監視」を「発火する監視」にする

今回いちばん厄介だったのは、**「計画停止では発火するが、障害では発火しない」**という
中途半端な壊れ方だった。もし完全に沈黙していれば、誰かが停止操作をしたときに
「あれ、通知が来ないぞ」と気付けたかもしれない。実際には通知は来ていたのだ。

だから「たまたま発火した実績がある」ことは、**監視が機能している証拠にならない。**
確認すべきは「**検知したい事象で**発火するか」である。

ドキュメントを読んで書いたイベントパターンが正しいとは限らない。
今回、AWS のドキュメントには DMS Serverless の `detail-type` が明記されていなかった。
だから **実イベントを採取してから書く**のが正しい順序だった。

実際、復旧作業の前に「全 `aws.dms` イベントをログに落とすだけ」のルール
（ターゲットはロググループのみ、Lambda も SNS も繋がない）を仕込んだところ、
**2 分で実データが取れた**。何が飛んでくるか分からないものを調べるのに、
フィルタを書いてから調べるのは順序が逆である。

そして最後に、**直したら実際に発生させて確かめる。**
今回は修正後、本番のレプリケーションを実際に停止させて次を確認した。

| 検証項目 | 期待 | 結果 |
|---|---|---|
| 通知ルールが発火する | する | ✅ |
| 復旧ルールが発火**しない**（計画停止だから） | しない | ✅ |
| 自動復旧 Lambda が起動**しない** | しない | ✅ |

「発火すること」だけでなく「**発火しないこと**」も検証項目になる。
計画停止のたびに自動復旧が動いて作業と喧嘩する、という別の事故を防ぐためだ。

### 3. 「稼働しているべきもの」は状態そのものを監視する

閾値超過型のメトリクスアラームは、**メトリクスが出ている間しか機能しない**。
止まったら黙る。

- `treat_missing_data` を `breaching` にする（メトリクス欠損を異常とみなす）
- もしくは `describe-replications` の `Status` を定期的にチェックする

後者のほうが本質的だ。「動いているべきものが動いていない」は、
メトリクスの値ではなく**状態**の問題である。

### 4. 自動復旧は「復旧できないケース」を想定する

`resume-processing` 固定の自動復旧は、checkpoint が生きている軽い障害しか直せない。

- `resume-processing` が失敗したらフォールバックする、もしくは
- **復旧不能と判断して通知だけ出す**

「自動復旧があるから大丈夫」と思っていたものが、実は一番重い障害では無力だった、というのが最悪のパターンである。

### 5. `table_mappings` は allowlist にする

前述のとおり。`%.%` + exclude は、知らないものを防げない。

### 6. インフラの識別子は「名前ベースだろう」と仮定しない

私は「ARN は識別子ベースだから作り直しても変わらない」と判断し、そのまま伝えた。**外れた。**

古い DMS は名前ベースの ARN を作っていたが、現在の API はランダムなリソース ID を振る。
リソースを作り直す前に、**ARN を参照している箇所（アラームの dimension、IAM ポリシー、
Lambda の環境変数）を洗い出す**べきだった。

そしてそもそも、**dimension のような派生値は、識別子から組み立てるのではなく
リソースの属性から導出しておく**べきだった。そうしていれば作り直しに自動追従した。

## で、次回のバージョンアップは大丈夫なのか

この記事を書いている時点での正直な答えは **「まだ大丈夫ではない。ただし手順を整えれば防げる」** である。

ここは書き分けが要る。混同すると打ち手を間違える。

| | 避けられるか |
|---|---|
| **binlog 座標が不連続になること** | **避けられない**。Blue/Green はインスタンス実体を入れ替えるので、これは仕様 |
| **それが障害になること** | **避けられる**。リリース手順に DMS を組み込めばよい |

今回の障害は「Blue/Green をやったから」起きたのではない。
**「Blue/Green の手順に DMS が入っていなかったから」起きた。**

具体的には、こうしていれば起きなかった。

1. 切替**前**に CDC を停止する（時刻を記録）
2. Blue/Green 切替
3. `--cdc-start-time <停止時刻>` で再開する

停止していれば FATAL 状態に落ちない。落ちなければ 18 日間の沈黙も、
62.5GB の全量ロードもなかった。**欠損は切替の数十秒だけで済んだはずである。**

「構造的な制約だから仕方ない」で止めると、手順を整える動機が失われる。
制約は消せなくても、**制約を織り込んだ手順は書ける。** そこが本質だった。

以下は「手順が整うまでの間、どこまで守りが固まっているか」の話である。

### 改善されたこと

| | 今回 | 次回 |
|---|---|---|
| `replication_type` | `cdc` だったため **config 作り直しが必要**（ARN が変わる） | 既に `full-load-and-cdc` なので**作り直し不要** |
| binlog 保持 | 24h | 72h |
| システムスキーマ | full load で流出しかけた | 常時除外 |
| 復旧手順 | その場で調べながら制約を 4 つ踏んだ | スクリプト化 + 制約を文書化 |

config を作り直さずに済むのは大きい。今回の混乱の大半（ARN 変更 → アラーム破壊）は
そこから派生していた。

### まだ直っていないこと

- EventBridge のイベントパターン（実データは採取済みだが未修正）
- 自動復旧 Lambda の起動タイプ（`resume-processing` 固定のまま）
- **アラームの dimension は「今回の復旧作業によって」壊れた。この一点では障害前より悪い**
- Blue/Green の手順書そのもの

**そして何より、リリース手順そのものがまだ書かれていない。**

インシデント対応でいちばん危ういのは、「復旧した」を「解決した」と読み替えてしまうことだ。
復旧はしたが、検知できない状態は残っているし、次回同じ手順で同じことをやれば同じ結果になる。

監視は「壊れたことに気付く」ための仕組みでしかない。
**壊さないための仕組みは手順のほうにある。**

## まとめ: DMS Serverless の制約表

同じことをやる人のために、今回判明した制約をまとめておく。

| 操作 | 可否 |
|---|---|
| `replication_type` の変更 | **provisioning 済みでは不可**。config を作り直す必要があり、**ARN が変わる** |
| `table_mappings` の変更 | **provisioning 済みでも in-place で可能**（ARN 維持） |
| `start-replication`（fresh） | **初回実行時のみ**。2 回目以降は `resume-processing` / `reload-target` |
| レプリケーションレコードのみ削除 | **API が存在しない**（`delete-replication-config` のみ） |
| システムスキーマの自動除外 | **しない**。`mysql` / `performance_schema` / `sys` は明示的に除外する |

CDC の checkpoint に関しては、こう覚えておけばよい。

> **binlog の座標を記憶する仕組みは、インスタンス実体が入れ替わる操作すべてに弱い。**
> Blue/Green デプロイ、スナップショットからの復元、リージョン移行 — いずれも同じ。

## おわりに

移行そのものは 25 秒のダウンタイムで成功した。「成功した移行」だった。

しかし成功の定義が「アプリが動き続けること」に閉じていたために、
下流のデータパイプラインが 18 日間死んでいたことに誰も気付かなかった。

そして皮肉なことに、それを検知するはずだった仕組みは 3 つとも用意されていた。
**用意されていたが、一度も動作確認されていなかった。**

「監視を作った」は「監視がある」ではない。**検知したい事象で**発火を確認して初めて監視になる。
今回のルールは計画停止では発火していた。動いているように見えて、肝心の障害だけ素通りしていた。

そしてもう一つ。この記事の初稿では「根本原因は構造的で、こちら側では回避できない」と書いていた。
だがそれは間違いだった。**避けられないのは binlog 座標の不連続であって、それが障害になることではない。**
切替前に止めて `CdcStartTime` で再開する——それだけで防げた。

「仕方ない」で片付けた瞬間に、手順を整える動機は失われる。
構造的な制約は消せなくても、**制約を織り込んだ手順は書ける。**
今回いちばん高くついた教訓は、結局そこだった。
