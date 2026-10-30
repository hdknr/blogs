---
title: "レイクハウス"
description: "データをオープンな形式でオブジェクトストレージに 1 か所だけ置き、テーブルフォーマット・カタログ・計算エンジンを差し替え可能な層として組み合わせるデータ基盤のアーキテクチャ。DWH 一体型との使い分けと、AI エージェント向けの守りまで"
date: 2026-10-30
lastmod: 2026-10-30
aliases: ["Lakehouse", "データレイクハウス", "Data Lakehouse", "レイクハウスアーキテクチャ", "Delta Lake", "Apache Hudi", "Apache Paimon", "Apache XTable", "Delta UniForm", "Apache Polaris", "Unity Catalog", "Lakekeeper", "Apache Fluss", "Lance", "Vortex"]
related_posts:
  - "/posts/2026/10/apache-iceberg-duckdb/"
  - "/posts/2026/10/ducklake-sql-lakehouse/"
  - "/posts/2026/10/redshift-vs-lakehouse/"
  - "/posts/2026/10/lakehouse-ecosystem-2026/"
  - "/posts/2026/10/ai-agent-data-platform/"
tags: ["データレイク", "データ基盤", "Apache Iceberg", "Delta Lake", "Apache Hudi", "Apache Paimon", "DuckLake", "Redshift", "aws"]
---

## 概要

レイクハウスは、S3 などのオブジェクトストレージに**オープンな形式（Parquet ＋テーブルフォーマット）でデータを 1 か所だけ置き**、その上のカタログと計算エンジンを用途ごとに選ぶデータ基盤の作り方。従来の DWH が「ストレージ・テーブル管理・計算」を 1 製品に閉じていたのに対し、各層を差し替え可能な部品に分ける。

個々の製品はまだ入れ替わりが激しいが、2026 年時点の大勢は「[Apache Iceberg](/blogs/wiki/tools/apache-iceberg/) を共通の土台にし、用途に応じて周辺技術を足す」方向にある。

## 詳細

### 層の構成

| 層 | 役割 | 例 |
|---|---|---|
| ストレージ | データを安く保持 | S3、GCS、Azure Data Lake Storage |
| ファイルフォーマット | 1 ファイルの中身の並べ方 | Parquet、ORC、Avro、Vortex |
| テーブルフォーマット | どのファイル群がテーブルを構成するか | Iceberg、Delta Lake、Hudi、Paimon、DuckLake |
| カタログ | テーブル名 → 最新メタデータの位置、権限 | Glue Data Catalog / S3 Tables、Polaris、Unity Catalog、Gravitino、Lakekeeper |
| 計算エンジン | クエリ実行 | Spark、Flink、Trino、Athena、Redshift、Snowflake、[DuckDB](/blogs/wiki/tools/duckdb/) |

ファイルフォーマットの土台は[列指向ストレージ](/blogs/wiki/concepts/columnar-storage/)。

### テーブルフォーマットの得意分野

| フォーマット | 推進役 | 得意なこと |
|---|---|---|
| Apache Iceberg | Apache | 多数のエンジンでの共有。対応製品が最多 |
| Delta Lake | Databricks（Linux Foundation） | Databricks / Spark との統合 |
| Apache Hudi | Apache | upsert・削除とインデックス（CDC 向き） |
| Apache Paimon | Apache（Flink 発） | LSM ツリーでストリーミングの継続更新 |
| [DuckLake](/blogs/wiki/tools/ducklake/) | DuckDB チーム | メタデータを SQL DB に置く軽量構成 |

データファイルは共通の Parquet なので、**メタデータだけ変換すれば**コピーなしで別フォーマットとして読める。Apache XTable は Hudi・Iceberg・Delta 間を双方向に変換し（0.4.0 で Paimon と素の Parquet を変換元に追加、まだインキュベーション段階）、Delta UniForm は Delta から Iceberg などへの一方向。変換先では読み取り用と考えるのが安全。

### カタログは「Iceberg REST」が共通言語に

カタログは Iceberg REST カタログの API を実装する方向に収れんしつつあり、エンジンは実装を問わず接続できる。Apache Polaris（Snowflake・Dremio 発、2026 年 2 月にトップレベル昇格）、Unity Catalog OSS 版、複数種類のデータソースを束ねる Apache Gravitino、OpenFGA で細かな権限管理ができる Rust 製の Lakekeeper などがある。カタログは**誰がどのテーブルを読めるか**というガバナンスの中心にもなりつつあり、フォーマットと同じくらい重要な選択になる。AWS で完結するなら Glue Data Catalog / S3 Tables、マルチクラウド・マルチエンジンなら OSS の REST カタログが候補。

### 鮮度と AI 向けの拡張

- **Apache Fluss** — 小さなファイル問題でレイクハウスが苦手だった鮮度を補うストリーミングストレージ。最新データは Fluss、履歴は Paimon / Iceberg に置き、Union Read で 1 テーブルとして読む（2026 年 8 月にトップレベル昇格）
- **Lance** — ベクトル・テキスト・画像・音声をまとめて持てる AI 向けレイクハウスフォーマット。ランダムアクセスに強く、DuckDB の `lance` 拡張でも読める。ただし常に Parquet より速いわけではない
- **Vortex** — 圧縮した Arrow 配列を扱う、Parquet の次を狙う列指向ファイルフォーマット

Iceberg 自体も v3 で削除ベクター、行の系譜（row lineage）、Variant 型、列の既定値が加わった。

### DWH 一体型（Redshift）との使い分け

Redshift と Iceberg は同じ土俵にない。Redshift は 3 層を 1 製品に持つ DWH、Iceberg は形式にすぎない。しかも Redshift は 2025 年 11 月から Iceberg に書き込め（2026 年 8 月に v3 対応）、両者は組み合わせられる。比べるべきは**データの置き場所**。

| 状況 | 向いている構成 |
|---|---|
| 少人数で 1 台に収まる規模 | DuckDB ＋ DuckLake（または S3 の Iceberg を DuckDB で読む） |
| 複数チームが別々のエンジンで同じデータを使う | S3 ＋ Iceberg |
| 多数の人が BI で同じ集計を同時に見る | Redshift の内部ストレージ（RMS） |
| 両方ある（大半の組織） | 共有データは Iceberg、頻繁に読む集計だけ RMS |

「データを広く開示する」が**多くの人**に同じ集計を見せる意味なら DWH、**多くのチームやシステム**に元データを使わせる意味ならレイクハウスが向く。料金構造も違い、Redshift Serverless は RPU 時間（アイドル時は無料）、Athena はスキャン量、DuckDB はエンジン料なしで、どれが安いかは頻度とデータ量で逆転する。

Redshift から Iceberg への書き込みは 1 文 1 トランザクション、競合時は自動再試行なし、ストアドプロシージャから書けないなどの制約がある。複数テーブルをまとめて更新する ETL は RMS に残すのが無難。

### AI エージェントの土台として

レイクハウスは AI エージェント向けのデータ基盤の土台に向く。エージェントが問いに応じてエンジンを選べ、製品を入れ替えてもデータは残り、スナップショットで書き込みを取り消せるから。ただしそれだけでは足りず、MCP サーバーからテーブルまでの各層に 4 つの守りを置く。

1. **意味** — セマンティックレイヤー（dbt Semantic Layer など）で指標を定義し、LLM には指標名と切り口だけを選ばせる。詳細は [AI-ready データ設計](/blogs/wiki/concepts/ai-ready-data/)
2. **費用** — Athena はワークグループごとのクエリ単位スキャン上限（超過でキャンセル）、Redshift Serverless は最大 RPU と期間ごとの RPU 時間上限。エージェント専用のワークグループを分ける
3. **権限** — カタログでエージェント用ロールの読めるテーブルを絞り、既定は読み取り専用。MCP サーバー側の制限と二重に守る
4. **取り消し** — Iceberg のブランチで WAP（Write-Audit-Publish）を回し、検証を通ったものだけ `main` に fast-forward。失敗はスナップショットへロールバック

段階的に進めるのが現実的で、試行（DuckDB ＋ DuckLake）→ チーム利用（S3 ＋ Iceberg、費用と権限）→ 業務組み込み（セマンティックレイヤーと Redshift、ブランチでの検証）と、前の段階の守りを外さずに積み増す。

## 関連ページ

- [Apache Iceberg](/blogs/wiki/tools/apache-iceberg/) — レイクハウスの共通の土台になっているテーブルフォーマット
- [DuckLake](/blogs/wiki/tools/ducklake/) — メタデータを SQL DB に置く軽量な選択肢
- [DuckDB](/blogs/wiki/tools/duckdb/) — 手元で動く計算エンジン
- [列指向ストレージ](/blogs/wiki/concepts/columnar-storage/) — Parquet・Arrow・Vortex の背景
- [AI-ready データ設計](/blogs/wiki/concepts/ai-ready-data/) — エージェントに意味を渡す設計
- [MCP](/blogs/wiki/concepts/mcp/) — エージェントがデータにアクセスする窓口

## ソース記事

- [Apache Iceberg 入門：データレイクを「テーブル」にする仕組みと DuckDB との関係](/blogs/posts/2026/10/apache-iceberg-duckdb/) — 2026-10-12
- [DuckLake 入門：メタデータを SQL データベースに置くレイクハウスフォーマットと Iceberg との違い](/blogs/posts/2026/10/ducklake-sql-lakehouse/) — 2026-10-13
- [Redshift か、S3 ＋ Iceberg のレイクハウスか：DWH とオープンテーブルフォーマットの選び方](/blogs/posts/2026/10/redshift-vs-lakehouse/) — 2026-10-13
- [Iceberg と DuckLake の先へ：2026 年に注目したいレイクハウスの技術とプロダクト](/blogs/posts/2026/10/lakehouse-ecosystem-2026/) — 2026-10-13
- [AI エージェントのためのデータ基盤：レイクハウスを土台に「意味・費用・権限・取り消し」を設計する](/blogs/posts/2026/10/ai-agent-data-platform/) — 2026-10-13
