---
title: "AI ネイティブなデータ分析基盤"
description: "人間と AI が同じ指標定義・同じ権限・同じ PII 規則でセルフサービス分析できるように設計したデータ基盤。データ照会チャットボットとの関係と、作る順番まで"
date: 2026-11-15
lastmod: 2026-11-15
aliases: ["AI ネイティブデータ基盤", "AI-native data platform", "データ分析基盤", "Laplace", "データ照会チャットボットと分析基盤"]
related_posts:
  - "/posts/2026/11/ai-native-data-platform-lightdash-mcp/"
  - "/posts/2026/11/aws-only-ai-native-data-platform/"
  - "/posts/2026/11/data-chatbot-and-data-platform/"
  - "/posts/2026/11/business-system-data-chatbot/"
tags: ["データ基盤", "セマンティックレイヤー", "mcp", "dbt", "データガバナンス"]
---

## 概要

AI ネイティブなデータ分析基盤とは、AI 用の特別な仕組みを足した基盤ではなく、**指標の定義・権限・PII の扱いを、人間にも AI にも同じ規則で効くように整理した**基盤のこと。代表例が PKSHA Technology の社内基盤「Laplace」（BigQuery・dbt・Lightdash・自前 MCP サーバー）で、SRE がほぼ 1 人・コードはほぼ全部 Claude Code に書かせて約 1 か月で立ち上げた。核の設計は DWH に依存しないので、AWS だけでも再現できる。

## 詳細

### 出発点：セルフサービスとガバナンスを同時に解く

もとは BI から本番 DB のリードレプリカに直接 SQL を投げていた。重いクエリが返らない、ダッシュボードのたびにエンジニアが要る、PII があるので権限を絞る――そして**権限を絞るほどエンジニア待ちが増える**。セルフサービス化とガバナンスを同時に解かないと進まない。

### 層の構成

| 層 | GCP 版（PKSHA） | AWS だけの構成案 |
|---|---|---|
| CDC 取り込み | Datastream | Aurora zero-ETL 連携（列を落とすなら AWS DMS） |
| DWH | [BigQuery](/blogs/wiki/tools/bigquery/) | [Amazon Redshift](/blogs/wiki/tools/amazon-redshift/) Serverless または小さめのプロビジョンド |
| 変換・指標定義 | [dbt](/blogs/wiki/tools/dbt/)（raw → staging → mart） | dbt-redshift |
| BI・権限 | [Lightdash](/blogs/wiki/tools/lightdash/)（セルフホスト） | 同じ（接続先を Redshift に） |
| AI の入口 | 自前 [MCP](/blogs/wiki/concepts/mcp/) サーバー | 同じ。Slack bot の LLM は Bedrock も可 |
| 実行基盤 | GKE Autopilot + Terraform | ECS Fargate + Terraform |
| 監査 | `INFORMATION_SCHEMA.JOBS` | `SYS_QUERY_HISTORY` + CloudTrail |

### DWH に依存しない 6 つの設計

1. **定義は 1 か所** — 指標は dbt の `schema.yml` だけに書き、BI も AI もそこを見る（[セマンティックレイヤー](/blogs/wiki/concepts/semantic-layer/)）
2. **DWH を直接読ませない** — 読めるのはパイプラインと保守者だけ。利用者は BI を通し、`required_attributes`（テーブル）と `user_attributes`（行）で制御
3. **PII は 3 段構え** — staging でソルト付き決定的ハッシュ、平文が要る列は `<table>_pii` に隔離、クエリ履歴を dbt で監査
4. **規則は CI で強制する契約に** — `*_pii` の命名・`data_class: pii` ラベル・`required_attributes` の宣言を dbt の CI で落とす。だから MCP の PII ガードが単純な名前マッチで済む
5. **AI の品質はサーバー側で担保** — `*_pii` を参照するクエリは実行しても行の値を返さず、件数・Lightdash の URL・SQL だけ返す。URL と SQL は LLM に作らせずツールが返す。チャート種別ガイド、設定キーの抽出、応答の整形（256 KB を絞る）、存在しないフィールドへの候補提示で 1 往復の自己修正を促す
6. **権限は期限付き** — 申請 → 承認 → 期限付きで属性付与 → 自動剥奪。「絞る」でなく「必要な人が必要な期間だけ持つ」

認証はユーザー単位の OAuth にし、AI が見られる範囲をその人が BI で見られる範囲に揃える。LLM が書いたコードは CI の lint、Terraform のユニットテスト、MCP のスモークテスト、理由と計測値を残すコミット、100 件超の決定ログで縛った。

### コストの罠はソース側の課金ルール

- Aurora スナップショットの S3 エクスポートは**スナップショット全体のサイズ**で課金される（AWS の中でも同じ）。日次の全量コピーには使わない
- BigQuery の CDC は適用のたびにテーブル全体を読む（1 日約 330 USD）。`max_staleness` を緩めて約 1/100 に
- Datastream の量の 86% が 1 テーブルの JSON 列だった。ソース側で除外して月約 400 USD 削減
- Redshift Serverless は CDC が流れ続けると**アイドルにならない**。`REFRESH_INTERVAL` を延ばす、PoC で RPU 時間を測ってプロビジョンド＋リザーブドと比べる
- 予算アラートは全体と主要サービスごとに最初から置く

### データ照会チャットボットとの関係

業務システムのデータ照会チャットボットと分析基盤は、**答える質問の種類が違う補完関係**。

| 観点 | チャットボット（ツール呼び出し） | 分析基盤 |
|---|---|---|
| 典型的な質問 | 「この案件の今月の原価は？」 | 「事業所別の原価率の推移は？」 |
| 鮮度 | リアルタイム | CDC の分だけ遅れる |
| 権限 | 業務システムの行単位の権限 | BI 層のユーザー属性 |
| 数字の正本 | 業務システムのコード | dbt の指標定義 |

完成形は「3 経路を持つ 1 つの窓口」。経路はアプリがログイン中の役割で決め、優先順位は決定論的な順に ①→②→③。

| 経路 | 使える人 | 問い合わせ先 | 数字の扱い |
|---|---|---|---|
| ① 業務照会（ツール呼び出し） | 全員 | 業務ロジック → 業務 DB | 正本 |
| ② 定型分析（セマンティックレイヤー） | BI 権限を持つ人 | BI / dbt の MCP → DWH | 分析用の公式指標 |
| ③ 探索（[Text-to-SQL](/blogs/wiki/concepts/text-to-sql/)） | 許可された役割だけ | DWH の mart（当初はレプリカ） | 調査用 |

### 作る順番：分析基盤を待たない

1. ① ツール呼び出しのチャットボット（分析基盤不要。最初に価値が出る）
2. ③ Text-to-SQL を許可された役割に開放（読み取り専用レプリカ）。目的は精度より**ログ集め**
3. 合図が出たら分析基盤を作る — レプリカが重い、複数システムをまたぐ、過去時点の値が要る、同じ集計が繰り返し来る、ダッシュボードの要求
4. ② を足し、③ の接続先を DWH の mart に移す

最初から主な要求が経営のダッシュボードや複数システム横断なら、分析基盤から始める。どちらでも、mart は実際に聞かれた質問から設計する。

### 二重にしない 3 つのもの

- **数字の正本** — 帳票と同じ数字は ① で答え、② は分析用と明示。業務 API と mart の値を突き合わせるテスト
- **権限** — BI の属性は業務システムの所属・役割から同期し、② を ① より広くしない
- **用語** — 分析指標は `schema.yml` を正にし、ツールの `description` も同じ用語集から書く（[オントロジー](/blogs/wiki/concepts/ontology/)）

## 関連ページ

- [セマンティックレイヤー](/blogs/wiki/concepts/semantic-layer/) — 基盤の核になる定義の層
- [Text-to-SQL](/blogs/wiki/concepts/text-to-sql/) — チャットボット側の探索経路と改善サイクル
- [dbt](/blogs/wiki/tools/dbt/) / [Lightdash](/blogs/wiki/tools/lightdash/) — 定義と BI
- [BigQuery](/blogs/wiki/tools/bigquery/) / [Amazon Redshift](/blogs/wiki/tools/amazon-redshift/) — DWH の選択肢
- [レイクハウス](/blogs/wiki/concepts/lakehouse/) — DWH を持たない S3 + Iceberg + Athena 案の土台
- [AI-ready データ設計](/blogs/wiki/concepts/ai-ready-data/) — LLM に計算させない原則
- [Claude Code](/blogs/wiki/tools/claude-code/) — 基盤のコードを書き、分析の窓口にもなった

## ソース記事

- [BigQuery × dbt × Lightdash × MCP で作る AI ネイティブなデータ分析基盤：PKSHA の事例に学ぶ設計](/blogs/posts/2026/11/ai-native-data-platform-lightdash-mcp/) — 2026-11-15
- [AWS だけで作る AI ネイティブなデータ分析基盤：Aurora zero-ETL × Redshift × dbt 構成案](/blogs/posts/2026/11/aws-only-ai-native-data-platform/) — 2026-11-15
- [データ照会チャットボットはデータ分析基盤を作ってから？ツール呼び出し・Text-to-SQL・セマンティックレイヤーの関係と進め方](/blogs/posts/2026/11/data-chatbot-and-data-platform/) — 2026-11-15
- [Text-to-SQL vs ツール呼び出し — 権限管理のある業務システムに AI データ照会を組み込む](/blogs/posts/2026/11/business-system-data-chatbot/) — 2026-11-15
