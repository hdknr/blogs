---
title: "AWS Compute Optimizer の使い方 — EC2 のサイズ適正化を無料で始める手順と落とし穴"
date: 2026-07-30
lastmod: 2026-08-06
slug: "aws-compute-optimizer"
draft: false
description: "AWS Compute Optimizer で EC2・RDS・Lambda のサイズを適正化する方法。オプトイン手順、Finding の読み方、メモリ推奨に CloudWatch Agent が必須という落とし穴、無料の 32 日ルックバックと有料機能の境界、boto3 で取得して分析するときのページネーターと maxResults の罠まで。"
source_url: "https://github.com/hdknr/blogs/issues/593#issuecomment-5124881656"
categories: ["クラウド/インフラ"]
tags: ["aws", "compute-optimizer", "ec2", "CloudWatch", "コスト最適化"]
---

「この EC2、本当に m5.2xlarge が必要なんだろうか」——
AWS を運用していると必ず一度は突き当たる問いです。
CPU 使用率を CloudWatch で眺めて、なんとなく `.xlarge` に落として、
繁忙期に泣く。あるいは怖いのでずっと過剰なままにして、毎月払い続ける。

**AWS Compute Optimizer** は、この「勘と度胸のサイジング」を機械的に潰すためのサービスです。
CloudWatch に溜まったメトリクスを AWS 側の分析エンジンにかけ、
リソースごとに「過剰なのか、足りていないのか、ちょうどいいのか」を分類して、
推奨インスタンスタイプと削減見込み額まで出してくれます。しかも**基本機能は追加料金なし**。

この記事で扱うのは次の 4 点です。

- 推奨が出るための前提条件（メトリクス量・Cost Explorer・Performance Insights）
- `Finding` / `Finding reasons` / `Performance risk` / `Platform differences` の読み分け
- メモリの推奨が出てこない理由と、その対処
- 無料で使える範囲（32 日ルックバックまで）と有料機能の境界
- boto3 で推奨を取得して分析に回すときの落とし穴

## AWS Compute Optimizer とは — 何をするサービスか

ざっくり言うと「使用率メトリクスを溜めて、機械学習で分析して、サイズ適正化（rightsizing）案を出す」だけのサービスです。
ただし入力と出力の間にいくつか前提条件が挟まっていて、そこを知らないと
「有効化したのに何も出てこない」「メモリの推奨が一切出ない」といった状態になります。

全体の流れは次のとおりです。

![AWS Compute Optimizer のデータフロー図。CloudWatch メトリクスを入力に機械学習で分析し、サイズ適正化推奨とアイドルリソース推奨を出力する流れ](/blogs/images/aws-compute-optimizer-dataflow.png)

図のとおり、分析対象は EC2 インスタンス、EC2 Auto Scaling グループ、EBS ボリューム、
Lambda 関数、ECS サービス（Fargate）、Aurora / RDS、Microsoft SQL Server ライセンスです。
メモリと GPU の使用率だけは統合 CloudWatch Agent が別途必要で、
ルックバック期間は 14 日・32 日・93 日から選べます。
削減額の算出に使う料金情報は Cost Explorer と
Cost Optimization Hub（日本語コンソールでは「コスト最適化ハブ」）から供給されます。

重要なのは、**Compute Optimizer 自身は新しくメトリクスを取らない**という点です。
既存の CloudWatch メトリクスを読むだけなので、
CloudWatch が見ていない指標（代表例がメモリ）については何も判断できません。
ここが後述する最大の落とし穴になります。

## 対応リソースと、推奨が出るための条件

対応リソースごとに必要なメトリクス量が違います。公式の
[Resource requirements](https://docs.aws.amazon.com/compute-optimizer/latest/ug/requirements.html)
をまとめると次のようになります。

| リソース | 必要な条件 |
| --- | --- |
| EC2 インスタンス / EC2 Auto Scaling グループ | 過去 14 日間で **30 時間以上**の CloudWatch メトリクス（拡張インフラメトリクス＝後述の有料オプション有効時は、過去 93 日間で 30 時間以上） |
| EBS ボリューム | 実行中インスタンスに **30 時間以上連続でアタッチ**されていること（デタッチすると推奨は消える） |
| Lambda 関数 | 設定メモリが **1,792 MB 以下**、かつ過去 14 日間で **50 回以上**の呼び出し。CloudWatch メトリクスは不要 |
| ECS サービス（Fargate） | 過去 14 日間で **24 時間以上**のメトリクス。ステップスケーリングポリシーが未アタッチ、CPU とメモリにターゲット追跡ポリシーが未アタッチ、実行状態が `SteadyState` または `MoreWork` |
| Aurora / RDS DB インスタンス | 過去 14 日間で 30 時間以上のメトリクス。**過剰プロビジョニングの検出には RDS Performance Insights の有効化が必要** |
| 商用ソフトウェアライセンス | **Microsoft SQL Server on EC2 のみ**。30 時間以上*連続*したメトリクスと、CloudWatch Application Insights の有効化が必要 |

いくつか実務的に効く点を補足します。

- **RDS / Aurora は MySQL と PostgreSQL 系のみ**です。RDS for MySQL、RDS for PostgreSQL、Aurora MySQL 互換、Aurora PostgreSQL 互換が対象で、Oracle や SQL Server の RDS は対象外です。
- **Lambda は「メモリサイズが 1,792 MB 以下」という上限**があります。これを超える関数は `Finding` が `Unavailable`（理由コード `Inconclusive`）になり、コンソールにも出てきません。呼び出し 50 回未満の場合は理由コード `Insufficient data` です。
- **ECS on Fargate はターゲット追跡ポリシーの有無で出力が変わります**。CPU にだけターゲット追跡が付いていればメモリの推奨のみ、メモリにだけ付いていれば CPU の推奨のみが出ます。
- **EBS ボリュームのデタッチで履歴が失われる**点は要注意。デタッチしている間 CloudWatch にデータが報告されないため、推奨も参照できなくなります。

また、**Cost Explorer の有効化は必須**です。
Compute Optimizer は Cost Explorer の請求データを使って削減額と料金情報を埋めるので、
これを有効にしていないと削減額のカラムが機能しません。

## AWS Compute Optimizer をオプトイン（有効化）する — CLI での手順

作業の全体像は 3 ステップです。

1. オプトインする（この節）
2. ルックバック期間を無料の 32 日に設定する（後述の「料金」節）
3. 対象 EC2 に統合 CloudWatch Agent を入れる（後述の「落とし穴」節）

サービスはデフォルトで無効なので、まずオプトインします。
コンソールなら Compute Optimizer の画面で「Get started」→「Opt in」を押すだけですが、
CLI のほうが Organizations 一括処理を含めて確実です。

```bash
# 単一アカウントをオプトイン
aws compute-optimizer update-enrollment-status --status Active

# Organizations の管理アカウントから、全メンバーアカウントを一括オプトイン
aws compute-optimizer update-enrollment-status --status Active --include-member-accounts

# 状態を確認
aws compute-optimizer get-enrollment-status
```

`get-enrollment-status` の出力はこのような形です。

```json
{
    "status": "Active",
    "statusReason": "",
    "memberAccountsEnrolled": true,
    "numberOfMemberAccountsOptedIn": 24,
    "lastUpdatedTimestamp": "2026-07-30T09:41:12+09:00"
}
```

`status` は `Active` / `Inactive` / `Pending` / `Failed` の 4 値です。
メンバーアカウントの登録に時間がかかっている間は `Pending` になり、理由が `statusReason` に入ります。
`memberAccountsEnrolled` が `true` なら、メンバーアカウントも含めてオプトイン済み。
アカウントごとの詳細を見たいときは `get-enrollment-statuses-for-organization` を使います。

**`numberOfMemberAccountsOptedIn` が `0` でも異常とは限りません。**
このフィールドと `memberAccountsEnrolled` はどちらも
**「自アカウントが組織の管理アカウントである場合」にのみ意味を持つ**値です。
組織にメンバーアカウントが 1 つも無い構成（管理アカウント単独）なら、
`memberAccountsEnrolled: true` と `numberOfMemberAccountsOptedIn: 0` は同時に成立します。
矛盾ではなく、「メンバーも含める設定だが、含めるべきメンバーがいない」状態です。

```json
{
    "status": "Active",
    "memberAccountsEnrolled": true,
    "numberOfMemberAccountsOptedIn": 0,
    "lastUpdatedTimestamp": "2026-07-30T10:15:44+09:00"
}
```

`0` を見て不安になったら、まず組織の実際のアカウント数を確認してください。

```bash
aws organizations list-accounts --query 'length(Accounts)'
```

これが `1` なら管理アカウント単独なので `0` が正しい値です。
`2` 以上なのに `0` のままなら、オプトイン直後の伝播待ち
（オプトインしたアカウントがコンソールに現れるまで最大 24 時間）か、
信頼されたアクセスの有効化に失敗している可能性があります。
後者なら該当アカウントのオプトインステータスが `Failed` になり、
`Failed to enable trusted access` などの理由が付くので、
`get-enrollment-statuses-for-organization` で個別に確認します。

`--include-member-accounts` を使う場合、**AWS Organizations 側で「すべての機能」が有効化されている**必要があります。
コンソリデーテッドビリング（一括請求）のみの構成では一括オプトインができません。
一括オプトインを実行すると、Organizations 側で Compute Optimizer の信頼されたアクセスも有効になります。

オプトイン後に注意したいのが**タイムラグ**です。

- オプトインしたアカウントがコンソールに現れるまで最大 24 時間
- 推奨が生成されるまで**最大 24 時間**（メトリクスが十分溜まっている場合）
- メトリクスが 30 時間分溜まっていなければ、そもそもそれを待つ時間が必要

つまり「有効化したのに何も出ない」の大半は、**単に待ちが足りていない**だけです。
新規に立てた EC2 なら、最短でも 30 時間 + 分析時間が必要だと理解しておきましょう。

なお、オプトイン時にサービスリンクロールが自動で作られます。IAM 側での事前準備は不要です。

## Finding の読み方 — 3 分類では足りない

コンソールで最初に目に入るのが **Finding** カラムです。EC2 インスタンスの場合、次の 3 分類です。

| Finding | 意味 |
| --- | --- |
| **Under-provisioned** | CPU・メモリ・ネットワークなど、少なくとも 1 つのスペックがワークロードの性能要件を満たしていない。アプリのパフォーマンス低下につながる |
| **Over-provisioned** | 少なくとも 1 つのスペックを下げても性能要件を満たせる状態で、かつ不足しているスペックがない。不要なインフラコストにつながる |
| **Optimized** | すべてのスペックが性能要件を満たし、かつ過剰でもない。ただし Optimized でも**新世代インスタンスタイプが推奨されることがある** |

ここで止まってしまう人が多いのですが、**判断に本当に必要なのは隣のカラム**です。

### Finding reasons — どのスペックが問題なのか

`Finding reasons` は「何が過剰／不足なのか」を具体的に示します。
分析される軸はかなり細かく、次の 9 つそれぞれについて
`over-provisioned` / `under-provisioned` が付きます。

CPU、メモリ、GPU、EBS スループット、EBS IOPS、ネットワーク帯域、
ネットワーク PPS（パケット毎秒）、ディスク IOPS、ディスクスループット。

つまり「Over-provisioned だからサイズを下げよう」ではなく、
**「EBS IOPS が過剰なのか、CPU が過剰なのか」で打ち手が変わる**わけです。
EBS IOPS やスループットが過剰なだけなら、インスタンスタイプを変えるのではなく
[EBS Elastic Volumes](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/ebs-modify-volume.html)
でボリューム側の設定を下げるのが正解になるケースもあります。

### Performance risk — 5 段階のリスク評価

`Performance risk` は、現在および推奨インスタンスタイプがワークロード要件を満たさない可能性を表します。
`very low` / `low` / `medium` / `high` / `very high` の 5 段階で、
API・CLI・SDK では `0`（very low）から `4`（very high）の数値です。

このスコアは 8 つの軸ごとに個別に計算されます。
対象は CPU、メモリ、EBS スループット、EBS IOPS、ディスクスループット、
ディスク IOPS、ネットワークスループット、ネットワーク PPS で、
`Finding reasons` の 9 軸から GPU を除いたものです。
そのうち**最も高い値**がリソース全体のスコアになります。
`very low` は「常に十分な性能を提供すると予測される」という意味なので、
ここが `medium` 以上の推奨は、そのまま適用せず自分で検証すべき対象だと考えてください。

### Migration effort と Platform differences — 適用コストの見積り

推奨が Graviton（Arm）系だった場合、移行の手間が跳ね上がります。`Migration effort` はその目安です。

- **Very low** — 推奨タイプが現在と同じ CPU アーキテクチャ
- **Low** — ワークロードが Amazon EMR と推定され、Graviton タイプが推奨されている
- **Medium** — ワークロードタイプが推定できないが、Graviton タイプが推奨されている
- **High** — CPU アーキテクチャが異なり、かつ推奨アーキテクチャで動く互換バージョンが知られていない

この推定に使われるのが `Inferred workload types` で、インスタンス名・タグ・設定から
Amazon EMR、Apache Cassandra、Apache Hadoop、Memcached、NGINX、PostgreSQL、Redis、Kafka、SQL Server を推定します。

さらに `Platform differences` では、アーキテクチャ、ハイパーバイザー（Xen → Nitro など）、
インスタンスストアの有無、ネットワークインターフェイス（ENA ドライバ）、
ストレージインターフェイス（NVMe ドライバ）、仮想化タイプ（PV → HVM）の差異が示されます。
「インスタンスストアが使えなくなる」「NVMe ドライバの導入が必要」といった差分は、
**削減額だけ見ていると見落とします**。

## 最大の落とし穴：メモリは CloudWatch Agent がないと見えない

ここが実務上いちばん重要な点です。

**Compute Optimizer のメモリ使用率分析は、統合 CloudWatch Agent を入れているリソースに対してのみ行われます。**

EC2 の標準メトリクスにメモリ使用率は含まれていません。
したがって Agent を入れていないインスタンスでは、
Compute Optimizer は CPU とネットワークとディスク I/O だけを見て判断します。

これが何を招くか。
**「CPU は暇だがメモリはひっ迫している」インスタンスが Over-provisioned と判定される**のです。
推奨に従ってサイズを落とすと、メモリ不足で OOM を踏みます。

GPU も同様で、`GPUUtilization` と `GPUMemoryUtilization` は
統合 CloudWatch Agent を入れているリソースでのみ分析されます。

対策はシンプルです。

1. 最適化対象にする EC2 には[統合 CloudWatch Agent](https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/Install-CloudWatch-Agent.html) を入れる
2. 入れていないインスタンスの推奨は「CPU 観点のみの意見」として割り引いて読む

`Finding reasons` に memory 系の理由が一切出てこないインスタンスは、
Agent が入っていない可能性が高いというシグナルにもなります。

## アイドルリソース推奨 — 対象は 12 種類に拡大（2026 年 6 月）

サイズ適正化とは別の軸として、**アイドルリソース推奨**があります。
「サイズを下げる」ではなく「そもそも停止・削除できる」リソースを洗い出す機能です。

### 対応リソース（12 種類）

2024 年 11 月に登場し、
[2026 年 6 月 8 日に 6 種類のリソースタイプが追加](https://aws.amazon.com/about-aws/whats-new/2026/06/aws-compute-optimizer-six-new-idle/)されました。
現在の対応リソースは以下のとおりです。

- **コンピュート**: EC2 インスタンス、EC2 Auto Scaling グループ、ECS サービス（Fargate）
- **ストレージ・ネットワーク**: EBS ボリューム、NAT Gateway
- **データベース・キャッシュ**: Aurora / RDS、DynamoDB、ElastiCache、MemoryDB、DocumentDB
- **その他**: WorkSpaces、SageMaker エンドポイント

### アイドル判定の基準

判定基準が明示されているのが実用的です。主なものを挙げます。

| リソース | アイドル判定の基準 |
| --- | --- |
| EC2 インスタンス | 14 日間で CPU 使用率のピークが **5% 未満**、かつネットワーク I/O が **1 日 5 MB 未満** |
| EC2 Auto Scaling グループ | 14 日間でピーク CPU 5% 超・ネットワーク 5 MB/日 超のインスタンスが 1 台もない |
| ECS サービス（Fargate） | CPU とメモリのピーク使用率が **1% 未満** |
| RDS for MySQL / PostgreSQL | リードレプリカでなく、DB 接続がゼロで CPU・読み書きも低水準 |
| NAT Gateway | `available` 状態でルートテーブルに未関連付け、アクティブ接続ゼロ、送受信パケットもゼロ |
| DynamoDB | **プロビジョンドテーブルのみ**。テーブルと全 GSI で消費 RCU / WCU がゼロ |
| ElastiCache | **Redis と Valkey エンジンのみ**。新規接続ゼロ、エンジン CPU 1% 未満、キャッシュヒット／ミス／get／set がゼロ。ノード単位で評価し、全ノードがアイドルのときのみクラスタがアイドル |
| MemoryDB | 新規接続ゼロ、エンジン CPU 1% 未満、キースペースのヒット／ミスがゼロ |
| DocumentDB | プロビジョンド・サーバーレス両対応（Elastic クラスタは除外）。DB 接続がゼロ |
| WorkSpaces | **Always On のみ**（Auto Stop / Standby は除外）。**63 日間**ユーザー接続なし |
| SageMaker エンドポイント | 14 日間で呼び出しがゼロ |

### ルックバック期間の例外

ルックバック期間の例外が地味に大事です。

- **EBS ボリュームと NAT Gateway のアタッチ状態は 32 日間のルックバックで判定**されます。EBS の推奨ルックバック期間を 14 日に変更しても、「アタッチされていないか」の判定は 32 日間のままです。
- **WorkSpaces のユーザー接続活動は 63 日間**で判定されます。長期休暇を挟んでも誤判定しないための設計でしょう。
- **ElastiCache はオプトインから推奨が出るまで最大 48 時間**かかります（他は 24 時間）。

### 推奨は「削除」だけではない

推奨アクションも具体的です。アイドルな Aurora MySQL / PostgreSQL には
「DB インスタンスクラスを `db.serverless` に変更する」、
RDS MySQL / PostgreSQL には「最大 7 日間停止できる」、
DynamoDB プロビジョンドテーブルには「オンデマンドモードへの切り替え」といった提案が付きます。
**削除だけでなく「安いモードへの切り替え」も選択肢として出してくる**のが便利なところです。

## AWS Compute Optimizer の料金 — 無料枠と拡張インフラメトリクス（有料）の境界

ここを誤解している記事が多いので明確にします。

**Compute Optimizer 自体に追加料金はありません。**
支払うのは分析対象の AWS リソース代と、CloudWatch の監視料金だけです。

有料なのは**拡張インフラメトリクス（Enhanced infrastructure metrics）**という単一の機能です。

| ルックバック期間 | 料金 | 備考 |
| --- | --- | --- |
| **14 日** | 無料 | デフォルト |
| **32 日** | 無料 | 月末処理のような月次パターンを拾える |
| **93 日** | **有料** | 拡張インフラメトリクスの有効化が必要 |

拡張インフラメトリクスの単価は **1 リソースあたり 1 時間 $0.0003360215**。
常時稼働のリソースなら**月額およそ $0.25/リソース**です。
対象は EC2 インスタンス、EC2 Auto Scaling グループに属するインスタンス、
そして RDS DB インスタンスです。

**注目すべきは 32 日が無料であること**です。
デフォルトの 14 日だと、月末バッチや月次締め処理のピークをまたげない可能性があります。
32 日にしておけば必ず月次サイクルを 1 周含められるので、
**まず 32 日に設定しておくのは、コストゼロでできる精度改善**です。
32 日ルックバックは EC2 インスタンス、EC2 Auto Scaling グループ、RDS データベース、
EBS ボリューム、ECS サービスの 5 種類でサポートされます。

93 日（有料）が本当に効くのは、四半期単位の季節変動があるワークロードです。
逆に言えば、負荷が平坦なワークロードに 93 日を払う意味は薄いので、
**組織全体に一律で有効化せず、季節性のあるリソースに絞る**のが筋のいい使い方です。
設定はリソースレベル・アカウントレベル・組織レベルで可能で、
**リソースレベルがアカウントレベルを、アカウントレベルが組織レベルを上書きします**
（Auto Scaling グループに属する EC2 は、グループ側の設定が個別インスタンスの設定を上書き）。

有効化後、実際に反映されるのは次の推奨更新時（最大 24 時間後）です。
それまでは `Active-pending` のようなステータスが付き、
推奨一覧の `Effective enhanced infrastructure metrics` カラムで反映状況を確認できます。

## 削減額を正しく出す — Cost Optimization Hub（コスト最適化ハブ）との連携

削減額のカラムには 2 種類あります。

- **Estimated monthly savings (On-Demand)** — オンデマンド料金前提の削減額
- **Estimated monthly savings (after discounts)** — Savings Plans / リザーブドインスタンスの割引を織り込んだ削減額

後者を出すのが**節約額見積もりモード（savings estimation mode）**です。
ここで誤解しやすいのですが、**明示設定しなくても既定で有効になるケースがあります**。
既定の挙動はアカウント種別と Cost Optimization Hub の登録状況で決まります。

| アカウント種別 | 既定の節約額見積もりモード |
| --- | --- |
| 管理アカウント / 委任管理者 | **`AfterDiscounts`**（割引反映済み） |
| スタンドアロンアカウント | **`AfterDiscounts`**（割引反映済み） |
| メンバーアカウント（管理アカウントがコスト最適化ハブにオプトイン済み） | **`AfterDiscounts`**（割引反映済み） |
| メンバーアカウント（管理アカウントが未オプトイン） | `BeforeDiscounts`（オンデマンドのみ） |

つまり**管理アカウントがコスト最適化ハブを有効にするかどうかが、
組織全体の既定値を決めるスイッチ**になっています。
管理アカウントがオプトアウトすると、明示設定のないメンバーアカウントは
`BeforeDiscounts` に戻ります。
なお Cost Explorer で「Linked account discounts」を無効にしている場合も
`BeforeDiscounts` になります。

Cost Optimization Hub を有効化していると、推奨の生成に
**Cost Optimization Hub のデータ**が使われます。ここには自社固有の割引が含まれます。
有効化していない場合は Cost Explorer のデータとオンデマンド料金情報が使われます。

これは実務上かなり重要です。
Savings Plans や RI を大量に持っている組織では、
**オンデマンド前提の削減額は「実際には削減されない額」を含んでいます**。
コミットメントで既に安く買っているインスタンスをダウンサイズしても、
コミット分は払い続けるので額面どおりには減りません。
経営に数字を出す前に、必ず Cost Optimization Hub を有効化して割引反映済みの数字にしましょう。

なお削減額の計算方法は「現在のインスタンスの稼働時間数 × 現在と推奨タイプのレート差」で、
ダッシュボードに出る数字は**アカウント内の全 Over-provisioned インスタンスの合計**です。

### 設定の依存関係

3 つの設定には順序があります。**Compute Optimizer のオプトインが先**です。

```text
① Cost Explorer 有効化（請求データの供給元。API 不可、コンソールのみ）
        ↓
② Compute Optimizer オプトイン（前述の update-enrollment-status）
        ↓
③ コスト最適化ハブ 有効化（Compute Optimizer の推奨を取り込む）
        ↓
④ 節約額見積もりモード（既定で有効なケースあり。必要時のみ調整）
```

②を飛ばして③を有効化すると、後述のエラーメッセージが出ます。

### 操作手順 ①：Cost Explorer を有効化する（前提）

Compute Optimizer とコスト最適化ハブの両方が Cost Explorer を前提にしているので、
まずここから始めます。**API では有効化できません**（コンソールから初回アクセスするのが唯一の方法）。

1. **Billing and Cost Management（請求とコスト管理）** コンソールを開く（`https://console.aws.amazon.com/costmanagement/`）
2. ナビゲーションペインで **Cost Explorer** を選択
3. 「**Cost Explorer へようこそ**（Welcome to Cost Explorer）」ページで「**Cost Explorer の起動**（Launch Cost Explorer）」を選択

当月分のデータが見えるまで約 24 時間、残りはさらに数日かかります。
なお有効化の副作用として **Cost Anomaly Detection が自動設定される**点に注意してください
（AWS サービスモニターと日次サマリー通知が作られます。不要なら後からオプトアウト可能）。

### 操作手順 ②：Cost Optimization Hub（コスト最適化ハブ）を有効化する

コスト最適化ハブは **Cost Explorer の中ではなく、Billing and Cost Management の
ナビゲーションペインに独立した項目**として並んでいます。ここが最初に迷うポイントです。

1. **Billing and Cost Management（請求とコスト管理）** コンソールを開く（`https://console.aws.amazon.com/costmanagement/`）
2. ナビゲーションペインで「**Cost Optimization Hub**」を選択
3. 組織／メンバーアカウントの範囲を選ぶ
   - **Enable Cost Optimization Hub for this account and all member accounts** — このアカウントと全メンバーアカウントの推奨を取り込む
   - **Enable Cost Optimization Hub for this account only** — このアカウントのみ
4. 「**有効化**（Enable）」を選択

> **表記が揺れている点に注意。** 日本語コンソールでは、ナビゲーションペインの項目名と
> 有効化時の選択肢は「**Cost Optimization Hub**」と英語のままですが、
> 後述のオプトアウト画面のチェックボックスは「**コスト最適化ハブを有効にする**」と
> 日本語になっています。コンソール内を検索するときは
> 「コスト最適化」「Cost Optimization」の両方を試すのが確実です。

**組織全体を選ぶなら管理アカウントで実施してください。**
前掲の表のとおり、これがメンバーアカウントの既定値を `AfterDiscounts` にするスイッチです。
Organizations の「すべての機能」有効化が前提で、
実行すると Cost Optimization Hub の信頼されたアクセスも有効になります。

必要な IAM 権限は次の 3 つ（組織全体の場合は `organizations:EnableAWSServiceAccess` を追加）。

- `iam:CreateServiceLinkedRole` — `AWSServiceRoleForCostOptimizationHub` の作成
- `iam:PutRolePolicy`
- `cost-optimization-hub:UpdateEnrollmentStatus`

推奨事項の取り込み完了まで**最大 24 時間**かかります。
また、無効化する場合は経路が変わり、
ナビゲーションペインの**「コスト管理の設定」→「詳細設定」→「Cost Optimization Hub」タブ**から
「**コスト最適化ハブを有効にする**」のチェックを外して「**設定を保存**」です。
**管理アカウントから全メンバーアカウントを一括オプトアウトすることはできず**、
メンバーアカウントごとに実施する必要があります。

> 推奨事項は**米国東部（バージニア北部）リージョンに保存**されます。
> データの保存場所に制約がある場合は事前に確認してください。

#### 「Ensure that you are enrolled into Compute Optimizer」と出たら

有効化直後にこのメッセージが出ることがあります。

```text
Ensure that you are enrolled into Compute Optimizer to view the cost efficiency.
Request ID: xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
```

**これはコスト最適化ハブの有効化が失敗したという意味ではありません。**
「**コスト効率性（cost efficiency）メトリクスが計算できない**」という表示です。
コスト効率性はページ上部に出る指標で、計算式は次のとおり
Compute Optimizer 由来の削減余地を分母・分子に使うため、依存しています。

```text
コスト効率性 = 1 -（潜在的削減額 / 最適化可能な支出の合計）× 100%
```

まず現状を確認します。

```bash
aws compute-optimizer get-enrollment-status
```

`status` が `Inactive` なら、依存関係②が抜けています。オプトインしてください
（コンソールなら Compute Optimizer → 「Get started」→「Opt in」）。

```bash
aws compute-optimizer update-enrollment-status --status Active
```

**`status` が `Active` なのにメッセージが出る場合**は、次の 3 つを順に疑います。

1. **オプトインしたばかり（最も多い）** — この記事の手順どおりに進めた直後は、
   まさにこの状態です。`lastUpdatedTimestamp` を見てください。
   推奨の生成には**最大 24 時間**かかり、
   コスト最適化ハブ側の取り込みにも別途**最大 24 時間**かかります。
   推奨が 0 件のうちはコスト効率性を計算できないので、
   メッセージが出るのが正常な状態です。実際に 0 件かどうかは次で確認できます。

   ```bash
   aws compute-optimizer get-recommendation-summaries
   ```

   全リソースタイプの件数が 0 なら、まだ分析が終わっていないだけです。

2. **そもそも対象リソースが無い / メトリクスが足りない** — 24 時間経っても 0 件なら、
   記事前半の要件（EC2 なら 30 時間以上のメトリクス）を満たすリソースが
   存在しない可能性があります。**停止中のインスタンスは対象外**である点に注意してください。
   停止中は CloudWatch にデータが報告されないため、30 時間の要件を満たせません。
   稼働中リソースの有無を確認します。

   ```bash
   aws ec2 describe-instances \
     --filters Name=instance-state-name,Values=running \
     --query 'length(Reservations[].Instances[])'
   ```

3. **使用量のばらつきが大きい** — 公式 FAQ に
   「high variance in your AWS usage」の場合は生成されないと明記されており、
   **使用量が安定すれば自動的に生成**されます。この場合も待つのが正解で、
   設定をいじる必要はありません。

なお**新規に使い始めた直後は履歴グラフも出ません**。
これも異常ではなく、データの蓄積待ちです。
①②を済ませていても、推奨事項の取り込みには最大 24 時間かかる点も併せて思い出してください。

### 操作手順 ③：節約額見積もりモードをリージョン単位で調整する

既定値のままで良いケースが多いですが、
メンバーアカウントに対して明示設定したい場合はこちらです。
設定先は Billing ではなく **Compute Optimizer 側のコンソール**です。

1. **Compute Optimizer** コンソールを開く（`https://console.aws.amazon.com/compute-optimizer/`）
2. ナビゲーションペインで「**全般**（General）」を選択
3. 「**節約額見積もりモード**（Savings estimation mode）」タブ →「**編集**（Edit）」
4. 有効にしたい**リージョンを選択**して「**保存**（Save）」（解除は選択を外す）

**設定はリージョン単位**である点に注意してください。
反映（割引反映済みの推奨が出るまで）に最大 24 時間かかります。
なお有効化できるのは**組織の管理アカウントまたは委任管理者のみ**です。

CLI でも設定できます。`--resource-type` は**必須**です。

```bash
# 節約額見積もりモードを割引反映済みに（アカウント単位）
aws compute-optimizer put-recommendation-preferences \
  --resource-type Ec2Instance \
  --savings-estimation-mode AfterDiscounts

# 併せて、記事前半で推奨した「無料の 32 日ルックバック」もここで設定できる
aws compute-optimizer put-recommendation-preferences \
  --resource-type Ec2Instance \
  --look-back-period DAYS_32

# 現在の設定を確認
aws compute-optimizer get-effective-recommendation-preferences \
  --resource-arn arn:aws:ec2:ap-northeast-1:123456789012:instance/i-0123456789abcdef0
```

`--resource-type` の有効値は
`Ec2Instance` / `AutoScalingGroup` / `EbsVolume` / `EcsService` / `RdsDBInstance` / `AuroraDBClusterStorage`、
`--look-back-period` は `DAYS_14` / `DAYS_32` / `DAYS_93`（93 日は拡張インフラメトリクスが必要）です。
`Ec2Instance` はスタンドアロンインスタンスと Auto Scaling グループ内のインスタンスの両方を含み、
`AutoScalingGroup` はグループ内のインスタンスのみを対象とします。

なお **Auto Scaling グループのルックバック期間はリソースレベルでしか設定できません**
（`--scope name=ResourceArn,value=<ASG の ARN>` を指定）。
組織レベル・アカウントレベルでは設定できないので、
一括で 32 日にしたつもりが ASG だけ 14 日のまま、という状態になりがちです。

## AWS CLI で運用に組み込む（`export-*` で S3 出力）

コンソールを人が見に行く運用は続きません。CLI でエクスポートして定期レビューに乗せます。

主なサブコマンドは以下です。

```bash
# 全リソースタイプの推奨サマリを取得（まず全体像を見る）
aws compute-optimizer get-recommendation-summaries

# EC2 インスタンスの推奨を取得
aws compute-optimizer get-ec2-instance-recommendations

# 過剰プロビジョニングのものだけに絞る
aws compute-optimizer get-ec2-instance-recommendations \
  --filters name=Finding,values=Overprovisioned

# アイドルリソース推奨を取得
aws compute-optimizer get-idle-recommendations

# RDS / Aurora の推奨を取得
aws compute-optimizer get-rds-database-recommendations
```

フィルタ値の表記に注意してください。
コンソールの表示名は `Over-provisioned` とハイフン入りですが、
CLI に渡す値は**ハイフンなしの `Overprovisioned`** です
（同様に `Underprovisioned`、`Optimized`）。
`Finding reasons` で絞るなら `--filters name=FindingReasonCodes,values=MemoryUnderprovisioned`
のように、こちらもハイフンなしのキャメルケースで指定します。

リソースタイプごとに `get-*` と `export-*` が対になっています。

- `get-` 系: `get-ec2-instance-recommendations`、`get-auto-scaling-group-recommendations`、`get-ebs-volume-recommendations`、`get-lambda-function-recommendations`、`get-ecs-service-recommendations`、`get-rds-database-recommendations`、`get-license-recommendations`、`get-idle-recommendations`、`get-recommendation-summaries`
- `export-` 系: 上記に対応する `export-*`（S3 への CSV / JSON 出力）
- 推奨設定: `put-recommendation-preferences`、`get-recommendation-preferences`、`get-effective-recommendation-preferences`、`delete-recommendation-preferences`
- 登録状態: `update-enrollment-status`、`get-enrollment-status`、`get-enrollment-statuses-for-organization`
- 投影メトリクス: `get-ec2-recommendation-projected-metrics`、`get-ecs-service-recommendation-projected-metrics`、`get-rds-database-recommendation-projected-metrics`

**`export-*` 系が実務の主役**です。コンソールのダッシュボード一覧は CSV で直接ダウンロードできませんが、
`export-*` なら S3 に出力できます。
これを月次で回して BI に流し込めば、「アカウント横断で削減余地の大きい上位 20 リソース」を
機械的に作れます。

`get-*-recommendation-projected-metrics` は、推奨タイプに変更した場合の
使用率を予測したグラフデータです。コンソールでは現在のメトリクスに
推奨タイプの予測値が重ね描きされ、**推奨タイプでも性能しきい値の内側に収まるか**を目で確認できます。
`medium` 以上のパフォーマンスリスクを検証するときは、まずここを見ます。

## boto3 で取得して Claude Code に分析させる

CLI と `jq` で組み合わせを探るのは、リソースが数百を超えると厳しくなります。
そこで **boto3 で JSON に落として、Claude Code に読ませる**のが実用的です。
「削減額上位 20 件を挙げて、パフォーマンスリスクが `medium` 以上のものは除外して」
のような問いをそのまま投げられるようになります。

ただし boto3 の `compute-optimizer` クライアントには、
API リファレンスを読まないと踏む落とし穴がいくつかあります。

| 落とし穴 | 内容 |
| --- | --- |
| **ページネーターが無い** | boto3 にページネーターがあるのは `DescribeRecommendationExportJobs` / `GetEnrollmentStatusesForOrganization` / `GetLambdaFunctionRecommendations` / `GetRecommendationPreferences` / `GetRecommendationSummaries` の **5 つだけ**。EC2・RDS・アイドルには無いので `nextToken` を自分で回す |
| **`maxResults` の上限がリソースで違う** | EC2・ASG・EBS・Lambda・RDS は **1000** だが、**アイドル推奨だけ 100**。共通化して 1000 を投げると `InvalidParameterValueException` になる |
| **`accountIds` は 1 リクエスト 1 アカウントのみ** | 公式に「You can only specify one account ID per request」と明記。組織横断で集めるにはメンバーアカウントごとに呼ぶ必要がある |
| **レスポンスキーが不揃い** | `instanceRecommendations` / `volumeRecommendations` / `rdsDBRecommendations` / `idleRecommendations` と命名規則が揃っていない。さらに **Lambda だけ `errors` フィールドが無い** |
| **`errors` が結果と同居する** | 非対応インスタンスファミリーなどは例外ではなく、同じレスポンスの `errors` 配列に入る。捨てると「なぜこのリソースが出てこないのか」が追えなくなる |
| **数値が `Decimal`** | `json.dumps` がそのままでは `TypeError` で落ちる。`default=` を渡す |

これらを踏まえた取得スクリプトです。

```python
#!/usr/bin/env python3
"""Compute Optimizer の推奨を全ページ取得して JSON に落とす。"""

import argparse
import decimal
import json
import pathlib

import boto3

# (出力名, メソッド名, レスポンスキー, maxResults 上限)
TARGETS = [
    ("ec2", "get_ec2_instance_recommendations", "instanceRecommendations", 1000),
    ("asg", "get_auto_scaling_group_recommendations", "autoScalingGroupRecommendations", 1000),
    ("ebs", "get_ebs_volume_recommendations", "volumeRecommendations", 1000),
    ("lambda", "get_lambda_function_recommendations", "lambdaFunctionRecommendations", 1000),
    ("rds", "get_rds_database_recommendations", "rdsDBRecommendations", 1000),
    ("idle", "get_idle_recommendations", "idleRecommendations", 100),  # ← 100 が上限
]


def paginate(method, result_key, page_size, **kwargs):
    """nextToken を手で回す（ページネーターが無いため）。"""
    items, errors, token = [], [], None
    while True:
        if token:
            kwargs["nextToken"] = token
        resp = method(maxResults=page_size, **kwargs)
        items.extend(resp.get(result_key, []))
        errors.extend(resp.get("errors", []))  # Lambda には無いので get で
        token = resp.get("nextToken")
        if not token:
            return items, errors


def encode(obj):
    if isinstance(obj, decimal.Decimal):
        return float(obj)
    raise TypeError(f"not JSON serializable: {type(obj)}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--region", default="ap-northeast-1")
    ap.add_argument("--profile")
    ap.add_argument("--account-id", help="1 リクエスト 1 アカウントのみ指定可")
    ap.add_argument("--out", default="./co")
    args = ap.parse_args()

    co = boto3.Session(
        profile_name=args.profile, region_name=args.region
    ).client("compute-optimizer")

    common = {"accountIds": [args.account_id]} if args.account_id else {}
    outdir = pathlib.Path(args.out)
    outdir.mkdir(parents=True, exist_ok=True)

    for name, method_name, key, page_size in TARGETS:
        try:
            items, errors = paginate(
                getattr(co, method_name), key, page_size, **common
            )
        except co.exceptions.OptInRequiredException:
            print(f"{name}: オプトインされていません")
            continue
        except Exception as e:  # 未対応リージョン等は他を止めずに続行
            print(f"{name}: 取得失敗 {type(e).__name__}: {e}")
            continue

        (outdir / f"{name}.json").write_text(
            json.dumps({"items": items, "errors": errors},
                       default=encode, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        print(f"{name}: {len(items)} 件 (errors: {len(errors)})")


if __name__ == "__main__":
    main()
```

```bash
pip install boto3
python fetch_compute_optimizer.py --region ap-northeast-1 --out ./co
```

あとは Claude Code に `./co/` を読ませて分析させます。

```text
./co/ec2.json と ./co/idle.json を読んで、次を出してください。

1. 推定月間削減額の上位 20 リソース（削減額・現在のタイプ・推奨タイプ・
   パフォーマンスリスク・移行の労力を表で）
2. そのうち Finding reasons にメモリ関連が一切出てこないものに印を付ける
   （CloudWatch Agent 未導入の疑いがあり、判断材料が足りない）
3. Platform differences にアーキテクチャ差異があるものを別掲
   （Graviton 移行が必要で、削減額どおりには進まない）
4. errors 配列の中身を集計して、分析対象から漏れた理由の内訳
```

**ポイントは 2 と 4** です。
削減額の降順に並べるだけなら Excel でもできますが、
「メモリの判断材料が無いまま Over-provisioned と言われているリソース」と
「そもそも分析対象から漏れたリソース」を仕分ける作業は、
JSON の構造を横断して見る必要があるため LLM に投げるのが向いています。

組織横断で集めたい場合は、`get_enrollment_statuses_for_organization`
（こちらはページネーターがあります）でメンバーアカウント一覧を取り、
`--account-id` を変えてループさせます。

### S3 エクスポートを使う場合

`export_*` 系は S3 に CSV（メタデータは JSON）を出力します。
定期実行して BI に流すならこちらですが、**バケットポリシーの準備が必要**です。
サービスプリンシパル `compute-optimizer.amazonaws.com` に対して
以下 **3 つのステートメントすべて**が必要で、1 つでも欠けるとジョブが失敗します。

- `s3:GetBucketAcl`（バケットの ACL 取得）
- `s3:GetBucketPolicyStatus`（バケットが公開されていないかの確認）
- `s3:PutObject`（エクスポートファイルの書き込み）

`s3:PutObject` のリソースパスは
`arn:aws:s3:::<bucket>/compute-optimizer/<アカウントID>/*` の形で、
`compute-optimizer/<アカウントID>/` の部分は Compute Optimizer 側が自動で付けます。
ポリシー内のバケット名・プレフィックス・アカウント番号が
エクスポートリクエストの指定と一致しない場合も失敗します。
バケットは**公開設定不可**、かつ Requester Pays 不可です。

## 実務チェックリスト

公式ドキュメントには書いてあるが読み飛ばしやすい点を、確認順にまとめます。

1. **メモリ推奨には統合 CloudWatch Agent が必須です。** これを入れずに Over-provisioned を信じると OOM を踏みます。最重要項目です。
2. **RDS の過剰プロビジョニング検出には Performance Insights が必要です。** 有効化していないと「下げられる」判定が出ません。
3. **Cost Explorer は必須、Cost Optimization Hub（コスト最適化ハブ）は実質必須です。** 前者がないと削減額が出ず、後者がないと数字が割引前で過大になります。**管理アカウントでコスト最適化ハブを有効にすると、メンバーアカウントの節約額見積もりモードの既定値が `AfterDiscounts` になります**（請求とコスト管理 → Cost Optimization Hub）。
12. **設定の順序に依存関係があります。** Cost Explorer → Compute Optimizer オプトイン → コスト最適化ハブの順です。Compute Optimizer 未オプトインのままハブを有効化すると「Ensure that you are enrolled into Compute Optimizer」と表示されます（ハブの有効化自体は失敗していません）。
4. **32 日ルックバックは無料です。** 月次パターンを拾えるので、まず設定しておきます。93 日（有料）は季節性のあるリソースに絞ります。
5. **繁忙期を含む期間で判断します。** 14 日間が閑散期に当たっていれば、当然「過剰」と出ます。年次イベントを持つシステムには 93 日でも足りないことがあります。
6. **パフォーマンスリスクが `medium` 以上の推奨は、そのまま適用しません。** 投影メトリクスで検証します。
7. **Platform differences を必ず読みます。** インスタンスストアの喪失、NVMe / ENA ドライバの要否、Arm への再コンパイル。削減額だけ見て適用すると起動しません。
8. **Optimized でも新世代への移行提案が出ます。** 「Optimized なら何もしなくていい」ではありません。世代を上げれば同性能で安くなることは多いです。
9. **推奨は 1 日 1 回更新です。** 変更直後にコンソールを見ても反応しません。
10. **対象外のサービスがあります。** S3 や DynamoDB のキャパシティ設計そのもの（サイズ適正化）は対象外で、DynamoDB はアイドル判定のみです。全コストを Compute Optimizer だけで見ようとしないことです。
11. **boto3 で集める場合は `nextToken` を自分で回します。** EC2・RDS・アイドルにページネーターはありません。アイドル推奨の `maxResults` 上限が 100 である点、`accountIds` が 1 リクエスト 1 アカウントである点も忘れずに。

## まとめ

Compute Optimizer は「無料で始められて、そのまま信じると事故る」タイプのサービスです。
オプトイン自体は 1 コマンドで済みますが、
**出てきた `Finding` をそのまま適用する運用は危険**です。
前掲のチェックリストを踏まえたうえで、着手順序についてひとつ提案があります。

**アイドルリソース推奨から始めるのが、投資対効果としては圧倒的に有利です。**
サイズ適正化は「どこまで下げて大丈夫か」という判断を人間が負う必要があり、
メモリの可視化、パフォーマンスリスクの検証、Platform differences の確認と、
前提を揃えるコストがそれなりにかかります。

一方アイドルリソース推奨は、判断に迷う要素がほとんどありません。
CPU 5% 未満・ネットワーク 5 MB/日 未満で 14 日間動いていた EC2、
ルートテーブルに紐づいていない NAT Gateway、
63 日間誰もログインしていない Always On の WorkSpaces。
これらは「使われていない」ことがほぼ確定しており、そのまま削減候補として扱えます。
2026 年 6 月に ElastiCache や DocumentDB、SageMaker エンドポイントまで対象が広がったことで、
ここだけでも拾える額はかなり増えました。
アイドルリソースを片付けてから、腰を据えてサイズ適正化に取りかかる。これが現実的な順序です。

## 参考リンク

- [AWS Compute Optimizer（公式）](https://aws.amazon.com/jp/compute-optimizer/)
- [Resource requirements — AWS Compute Optimizer](https://docs.aws.amazon.com/compute-optimizer/latest/ug/requirements.html)
- [Viewing EC2 instance recommendations — AWS Compute Optimizer](https://docs.aws.amazon.com/compute-optimizer/latest/ug/view-ec2-recommendations.html)
- [Viewing idle resource recommendations — AWS Compute Optimizer](https://docs.aws.amazon.com/compute-optimizer/latest/ug/view-idle-recommendations.html)
- [Enhanced infrastructure metrics — AWS Compute Optimizer](https://docs.aws.amazon.com/compute-optimizer/latest/ug/enhanced-infrastructure-metrics.html)
- [Rightsizing recommendation preferences — AWS Compute Optimizer](https://docs.aws.amazon.com/compute-optimizer/latest/ug/rightsizing-preferences.html)
- [Opting in to AWS Compute Optimizer](https://docs.aws.amazon.com/compute-optimizer/latest/ug/account-opt-in.html)
- [Getting started with Cost Optimization Hub — AWS Cost Management](https://docs.aws.amazon.com/cost-management/latest/userguide/coh-getting-started.html)
- [Savings estimation mode — AWS Compute Optimizer](https://docs.aws.amazon.com/compute-optimizer/latest/ug/savings-estimation-mode.html)
- [Activating savings estimation mode — AWS Compute Optimizer](https://docs.aws.amazon.com/compute-optimizer/latest/ug/activate-savings-estimation-mode.html)
- [Enabling Cost Explorer — AWS Cost Management](https://docs.aws.amazon.com/cost-management/latest/userguide/ce-enable.html)
- [PutRecommendationPreferences — API リファレンス](https://docs.aws.amazon.com/compute-optimizer/latest/APIReference/API_PutRecommendationPreferences.html)
- [boto3 ComputeOptimizer クライアントリファレンス](https://docs.aws.amazon.com/boto3/latest/reference/services/compute-optimizer.html)
- [Specifying an existing S3 bucket for your recommendations export](https://docs.aws.amazon.com/compute-optimizer/latest/ug/create-s3-bucket-policy-for-compute-optimizer.html)
- [AWS Compute Optimizer now supports idle recommendations for six additional resource types](https://aws.amazon.com/about-aws/whats-new/2026/06/aws-compute-optimizer-six-new-idle/)
- [AWS Compute Optimizer now supports 32-day lookback for EBS volume and ECS service rightsizing recommendations](https://aws.amazon.com/about-aws/whats-new/2026/06/aws-compute-optimizer-ebs-ecs-32-day-lookback/)
- [AWS Compute Optimizer を使った最適化分析 — NHN テコラス Tech Blog](https://techblog.nhn-techorus.com/archives/22517)
- [AWS Compute Optimizer で EC2 Instance を最適化する — サーバーワークスエンジニアブログ](https://blog.serverworks.co.jp/tech/2020/03/17/checking-compute-optimizer/)
