---
title: "Amazon Redshift"
description: "AWS の DWH。Aurora zero-ETL 連携で取り込みを自作せずに済む一方、列単位で PII を落とせない点と、Serverless が CDC でアイドルにならない点に注意が要る"
date: 2026-11-15
lastmod: 2026-11-15
aliases: ["Redshift", "Redshift Serverless", "Aurora zero-ETL", "zero-ETL 連携", "RPU"]
related_posts:
  - "/posts/2026/11/aws-only-ai-native-data-platform/"
  - "/posts/2026/10/redshift-vs-lakehouse/"
  - "/posts/2026/10/ai-agent-data-platform/"
tags: ["Redshift", "aws", "データ基盤", "dbt"]
---

## 概要

Amazon Redshift は、ストレージ・テーブル管理・計算を 1 製品に持つ AWS の DWH。ノードを常時起動するプロビジョンドと、使った RPU（Redshift Processing Unit）時間だけ課金する Serverless の 2 形態がある。Aurora からの **zero-ETL 連携**で取り込みを自作せずに済むため、AWS だけで AI ネイティブなデータ分析基盤を作るときの DWH の第一候補になる。

## 詳細

### Aurora zero-ETL 連携

Aurora の変更を Redshift に自動で複製し続ける機能で、GCP の Datastream にいちばん近い。連携そのものに追加料金はないが、Redshift の計算・ストレージ、初回取り込み、Aurora 側の I/O、AZ 間転送は課金される。

**データフィルタはデータベース単位・テーブル単位で、列・行単位には対応しない**。PII 列もそのまま raw 層まで届くので、次のどちらかで対処する。

- **raw スキーマを閉じる** — dbt 実行ロールと保守者だけが読め、BI の接続ユーザーには staging と mart だけ `GRANT`。`REVOKE` は直接付与した権限しか取り消さないので、raw には最初から `PUBLIC` に権限を付けない
- **列を落としたいテーブルだけ AWS DMS** — テーブルマッピングの `remove-column` 変換ルールで除外。止まっても気づける監視を最初から置く

### Serverless の費用は「止まらない計算」に注意

Serverless はクエリがない間は計算課金が止まるのが利点だが、CDC で変更が絶えず流れ込むと**アイドルにならない**おそれがある。

- `REFRESH_INTERVAL` を延ばす、基本容量を小さめ（8 RPU）にする
- 変更が常に流れる用途では、小さめのプロビジョンド＋リザーブドインスタンスのほうが安い場合がある
- PoC で 1〜2 週間 RPU 時間を測ってから形態を決め、AWS Budgets と Cost Anomaly Detection を最初から置く

### DB 側の防御線

BigQuery の Policy Tags と違い、Redshift では RLS・動的データマスキング・列単位の権限を SQL で宣言できる。BI 層（Lightdash）の権限制御を主にし、`<table>_pii` などの重要テーブルだけに RLS やマスキングを重ねると、BI の設定ミスを DB 側で止められる。

監査用の `SYS_QUERY_HISTORY` は、スーパーユーザー以外には自分のクエリしか見えない。全員分を追うには監査ロールに `sys:monitor` を付ける（または `SYSLOG ACCESS UNRESTRICTED`）。

### 周辺との組み合わせ

- 変換は dbt-redshift、BI は Lightdash（Redshift 接続に公式対応）、実行基盤は ECS Fargate
- コストデータは CUR 2.0 の Data Exports で S3 に出し、Redshift 連携用の出力形式とスクリプトで取り込む
- Redshift は Iceberg への書き込みにも対応し、レイクハウスと組み合わせられる（使い分けは[レイクハウス](/blogs/wiki/concepts/lakehouse/)）
- 鮮度要件が緩くクエリが少ないなら、DWH を持たない S3（Iceberg）+ Athena 案も候補。ただし CDC を Iceberg にマージする処理を自作することになる

## 関連ページ

- [AI ネイティブなデータ分析基盤](/blogs/wiki/concepts/ai-native-data-platform/) — Redshift を DWH にした AWS だけの構成案
- [BigQuery](/blogs/wiki/tools/bigquery/) — GCP 側の対応する DWH
- [レイクハウス](/blogs/wiki/concepts/lakehouse/) — Redshift と S3 + Iceberg の使い分け
- [dbt](/blogs/wiki/tools/dbt/) — Redshift 上の変換

## ソース記事

- [AWS だけで作る AI ネイティブなデータ分析基盤：Aurora zero-ETL × Redshift × dbt 構成案](/blogs/posts/2026/11/aws-only-ai-native-data-platform/) — 2026-11-15
- [Redshift か、S3 ＋ Iceberg のレイクハウスか：DWH とオープンテーブルフォーマットの選び方](/blogs/posts/2026/10/redshift-vs-lakehouse/) — 2026-10-13
- [AI エージェントのためのデータ基盤：レイクハウスを土台に「意味・費用・権限・取り消し」を設計する](/blogs/posts/2026/10/ai-agent-data-platform/) — 2026-10-13
