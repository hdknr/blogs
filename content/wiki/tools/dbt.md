---
title: "dbt"
description: "DWH 上のデータ変換を SQL で書くツール。raw → staging → mart の層構成と、schema.yml の指標定義で BI と AI の共通の定義源になる"
date: 2026-11-15
lastmod: 2026-11-15
aliases: ["dbt Core", "data build tool", "dbt Labs", "dbt-bigquery", "dbt-redshift", "dbt-athena", "dbt MCP サーバー", "dbt-mcp"]
related_posts:
  - "/posts/2026/11/ai-native-data-platform-lightdash-mcp/"
  - "/posts/2026/11/aws-only-ai-native-data-platform/"
  - "/posts/2026/11/data-chatbot-and-data-platform/"
  - "/posts/2026/10/ai-agent-data-platform/"
tags: ["dbt", "データ基盤", "セマンティックレイヤー", "SQL"]
---

## 概要

dbt は、DWH に取り込んだ生データを分析しやすい形に変換する処理を SQL（＋ YAML）で書くツール。モデルの列・説明・テストを `schema.yml` に書け、そこに指標の定義も置ける。AI に分析させる基盤では、**BI と AI が同じ定義を見るための唯一の定義源**として使われる。

## 詳細

### 層構成

| 層 | 中身 |
|---|---|
| raw | 取り込んだまま |
| staging | 型・名前を整える。PII のハッシュ化もここで行う |
| mart | 分析用に集計・結合したテーブル群 |

PKSHA の事例では Aurora の 200 テーブル弱を mart まで出すために staging と mart で 577 モデルを作った。dbt のモデル名はプロジェクト内で一意である必要があるので、**プロダクトごとにプロジェクトを分け、プロジェクト境界を名前空間の境界にして**衝突を仕組みで防いでいる。

### アダプタ

DWH ごとに dbt-bigquery・dbt-redshift・dbt-athena などのアダプタがある。DWH を乗り換えるとハッシュ関数などの SQL 方言は書き換えが要るが、「どこに何を書くか」という設計は変わらない。

### ガバナンスの置き場所としての `meta`

- `required_attributes` をモデルの meta に宣言し、BI（[Lightdash](/blogs/wiki/tools/lightdash/)）で属性を持たないユーザーからテーブルを隠す
- `data_class: pii` のラベルと `*_pii` の命名を **dbt の CI で強制**し、ルールを人に覚えさせず契約にする
- BigQuery の `INFORMATION_SCHEMA.JOBS` のようなクエリ履歴を dbt のモデルで監査する

### AI からの入口

- **dbt Semantic Layer + dbt MCP サーバー**（[dbt-labs/dbt-mcp](https://github.com/dbt-labs/dbt-mcp)） — エージェントが `list_metrics`・`query_metrics` などで定義済み指標を引く
- **Lightdash 経由** — `schema.yml` の指標を Lightdash の MCP（または自前 MCP サーバー）から使う

dbt Labs は 2026 年 4 月に、セマンティックレイヤーと生テーブルへの Text-to-SQL の正答率比較を公開している（詳細は[セマンティックレイヤー](/blogs/wiki/concepts/semantic-layer/)）。

### 業務システムとの二重定義に注意

業務システムの帳票と同じ指標を dbt でも定義すると、計算が 2 か所に存在する。代表値を業務 API と mart で突き合わせるテストを定期的に回し、計算ルールの仕様書は 1 つにする。

## 関連ページ

- [セマンティックレイヤー](/blogs/wiki/concepts/semantic-layer/) — dbt が担う定義の層
- [Lightdash](/blogs/wiki/tools/lightdash/) — dbt の定義をそのまま探索画面にする BI
- [AI ネイティブなデータ分析基盤](/blogs/wiki/concepts/ai-native-data-platform/) — dbt を中心にした基盤設計
- [BigQuery](/blogs/wiki/tools/bigquery/) / [Amazon Redshift](/blogs/wiki/tools/amazon-redshift/) — 主な変換先の DWH
- [Apache Airflow](/blogs/wiki/tools/apache-airflow/) — dbt の実行を他の処理と順番どおりに起動するオーケストレーター

## ソース記事

- [BigQuery × dbt × Lightdash × MCP で作る AI ネイティブなデータ分析基盤：PKSHA の事例に学ぶ設計](/blogs/posts/2026/11/ai-native-data-platform-lightdash-mcp/) — 2026-11-15
- [AWS だけで作る AI ネイティブなデータ分析基盤：Aurora zero-ETL × Redshift × dbt 構成案](/blogs/posts/2026/11/aws-only-ai-native-data-platform/) — 2026-11-15
- [データ照会チャットボットはデータ分析基盤を作ってから？ツール呼び出し・Text-to-SQL・セマンティックレイヤーの関係と進め方](/blogs/posts/2026/11/data-chatbot-and-data-platform/) — 2026-11-15
- [AI エージェントのためのデータ基盤：レイクハウスを土台に「意味・費用・権限・取り消し」を設計する](/blogs/posts/2026/10/ai-agent-data-platform/) — 2026-10-13
