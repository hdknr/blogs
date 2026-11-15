---
title: "BigQuery"
description: "Google Cloud のサーバーレス DWH。オンデマンド課金はスキャン量で決まり、CDC の適用がテーブル全体を読む点がコストの落とし穴になる"
date: 2026-11-15
lastmod: 2026-11-15
aliases: ["Google BigQuery", "Datastream", "BigQuery CDC", "Policy Tags"]
related_posts:
  - "/posts/2026/11/ai-native-data-platform-lightdash-mcp/"
  - "/posts/2026/11/aws-only-ai-native-data-platform/"
tags: ["bigquery", "データ基盤", "gcp", "dbt"]
---

## 概要

BigQuery は Google Cloud のサーバーレス DWH。インフラを管理せずに大規模な集計ができ、オンデマンド課金では**クエリがスキャンしたデータ量**で料金が決まる。dbt・Lightdash と組み合わせた AI ネイティブなデータ分析基盤（PKSHA の Laplace）の DWH として使われた。

## 詳細

### 取り込みの経路

PKSHA の事例では、AWS の Aurora から 3 経路で取り込んだ。

| 経路 | 用途 |
|---|---|
| Datastream（CDC） | Aurora の binlog を読み BigQuery に直接書く主経路。200 テーブル弱 |
| AWS Glue | CDC から外した幅の広い列を毎時転送 |
| GCS に Avro を push → 外部テーブル | スナップショット経路（AWS のコストデータ）。認証はキーレスの Workload Identity Federation |

### CDC のコストの落とし穴

BigQuery の CDC は**変更を適用するたびにテーブル全体を読み、パーティションでは削減できない**（ドキュメントに明記）。オンデマンド課金ではこれがそのまま請求に乗り、事例では 1 日約 330 USD、ピーク日は 43.5 TiB（95% が上位 5 テーブル）を読んだ。

- `max_staleness`（反映の遅れの許容）を緩めると、読み込みは 1 日約 0.3 TiB に下がった
- Datastream は**ソース側で処理した量**で課金される。量の 86% を占めた 1 テーブルの JSON 列をソース側で除外し、月約 400 USD 削減
- 2 つの対策で、月 1 万 USD 近くになりえた読み込みコストが月 70 USD 前後に

スナップショットを選ばなかったのは、Aurora のスナップショットエクスポートが**インスタンス全体のデータ量**で課金されるため（数 MB のテーブルでも数 TB 分）。教訓は、パイプラインの単価だけでなく**ソース側の課金ルール**まで見積もること。

### 権限と監査

- 利用者に BigQuery を直接読ませず、BI（Lightdash）を通して制御する
- 列単位の Policy Tags は、タクソノミーと IAM の運用が重いとして不採用
- `INFORMATION_SCHEMA.JOBS`（ジョブ履歴）を dbt で監査する

### AWS との対応

本番が AWS にある組織では、分析のためだけに GCP を持つと権限・ネットワーク・請求・監査が二重になる。AWS で置き換えるなら DWH は [Amazon Redshift](/blogs/wiki/tools/amazon-redshift/)、課金はスキャン量から計算時間（RPU 時間）に変わる。DWH を持たない S3 + Iceberg + Athena 案もある（[レイクハウス](/blogs/wiki/concepts/lakehouse/)）。

## 関連ページ

- [AI ネイティブなデータ分析基盤](/blogs/wiki/concepts/ai-native-data-platform/) — BigQuery を DWH にした基盤の全体設計
- [Amazon Redshift](/blogs/wiki/tools/amazon-redshift/) — AWS 側の対応する DWH
- [dbt](/blogs/wiki/tools/dbt/) — BigQuery 上の変換
- [列指向ストレージ](/blogs/wiki/concepts/columnar-storage/) — スキャン量課金の背景

## ソース記事

- [BigQuery × dbt × Lightdash × MCP で作る AI ネイティブなデータ分析基盤：PKSHA の事例に学ぶ設計](/blogs/posts/2026/11/ai-native-data-platform-lightdash-mcp/) — 2026-11-15
- [AWS だけで作る AI ネイティブなデータ分析基盤：Aurora zero-ETL × Redshift × dbt 構成案](/blogs/posts/2026/11/aws-only-ai-native-data-platform/) — 2026-11-15
