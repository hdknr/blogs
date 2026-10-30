---
title: "DuckDB"
description: "インプロセス OLAP データベース。列指向アーキテクチャで分析クエリを高速実行し、Iceberg や DuckLake のテーブルを読み書きする計算エンジンにもなる"
date: 2026-04-06
lastmod: 2026-10-30
aliases: ["duckdb"]
related_posts:
  - "/posts/2026/03/duckdb-columnar-arrow/"
  - "/posts/2026/10/apache-iceberg-duckdb/"
  - "/posts/2026/10/ducklake-sql-lakehouse/"
  - "/posts/2026/10/redshift-vs-lakehouse/"
  - "/posts/2026/10/lakehouse-ecosystem-2026/"
  - "/posts/2026/10/ai-agent-data-platform/"
tags: ["データベース", "OLAP", "SQL", "python", "duckdb"]
---

## 概要

列指向ストレージを採用した SQL データベースエンジン。Apache Arrow、Parquet と同じエコシステムの一部で、分析ワークロード（集計、GROUP BY）で従来の行指向 DB より圧倒的に高速。ベクトル化実行エンジンと自動並列化で OLAP に最適化。プロセス内で動くので、ノート PC や Lambda のような小さな環境でも使える。

## 詳細

### データレイク上の計算エンジンとして

「分散ストレージ／計算エンジン／テーブル化技術」というデータ基盤の 3 層で見ると、DuckDB は**計算エンジンの 1 つ**。Spark クラスタを立てるほどではない規模の分析を、S3 上のテーブルに対して直接実行できる。

### Apache Iceberg を読み書きする（`iceberg` 拡張）

- `iceberg_scan('.../metadata/v1.metadata.json')` でカタログなしに読める。ただし**読み取り専用**で、最新メタデータの判断に `version-hint.text` かバージョン指定が要る（`unsafe_enable_version_guessing` は ACID を破りうるので既定で無効）。S3 上なら httpfs と `CREATE SECRET` も必要
- `iceberg_snapshots()` でスナップショット一覧、`snapshot_from_timestamp` でタイムトラベル
- カタログに `ATTACH`（S3 Tables は `ENDPOINT_TYPE s3_tables`、Glue の Iceberg REST エンドポイントは `AUTHORIZATION_TYPE 'sigv4'`）すると、通常のテーブルと同じ SQL で SELECT / UPDATE / `AT (TIMESTAMP => ...)` が書ける
- 読み取り全面対応と書き込み初期対応は v1.4.0、Iceberg v2 への UPDATE / DELETE は v1.4.2
- 制約: 書き込みにはカタログへの ATTACH が必要。UPDATE / DELETE は positional delete を書く merge-on-read のみで、`write.update.mode` / `write.delete.mode` が merge-on-read 以外だと失敗する。拡張はまだ experimental

### DuckLake を使う（`ducklake` 拡張）

`ATTACH 'ducklake:metadata.ducklake' AS my_ducklake;` だけでスナップショット・タイムトラベル付きのレイクハウスになる。カタログに PostgreSQL を使えば複数の DuckDB プロセスから同時に読み書きでき、素の DuckDB ファイルの「書き込みは 1 プロセスのみ」という制約を越えられる。詳細は [DuckLake](/blogs/wiki/tools/ducklake/)。

### Lance を読む（`lance` 拡張）

`INSTALL lance; LOAD lance;` のうえで `.lance` のパスを `FROM` に書けば、AI 向けレイクハウスフォーマット Lance のデータセットを読める。DuckDB 自身の検証では、Lance が常に Parquet より速いわけではなく処理の種類で結果が分かれる。

### 料金と規模の位置

Redshift Serverless（RPU 時間課金）や Athena（スキャン量課金）と違い、DuckDB はエンジンの利用料がかからず、実行するマシンの能力が上限になる。AI エージェントに社内データを分析させる基盤でも、試行段階は手元の DuckDB（＋ DuckLake）で始めるのが勧められている。

### 使い分けの目安

重い ETL は Glue / EMR の Spark で Iceberg に書き、DuckDB は手元での探索・軽い集計・小規模修正に使うのが無難。DuckDB だけで完結する小さな構成なら DuckLake、組織横断で複数エンジンが同じテーブルを共有するなら Iceberg。

## 関連ページ

- [列指向ストレージ](/blogs/wiki/concepts/columnar-storage/) — DuckDB が採用するストレージ方式
- [Apache Iceberg](/blogs/wiki/tools/apache-iceberg/) — DuckDB から読み書きできるオープンテーブルフォーマット
- [DuckLake](/blogs/wiki/tools/ducklake/) — DuckDB チームのレイクハウスフォーマット
- [レイクハウス](/blogs/wiki/concepts/lakehouse/) — フォーマット・カタログ・エンジンを組み合わせる全体像

## ソース記事

- [DuckDB と列指向ストレージ](/blogs/posts/2026/03/duckdb-columnar-arrow/) — 2026-03
- [Apache Iceberg 入門：データレイクを「テーブル」にする仕組みと DuckDB との関係](/blogs/posts/2026/10/apache-iceberg-duckdb/) — 2026-10-12
- [DuckLake 入門：メタデータを SQL データベースに置くレイクハウスフォーマットと Iceberg との違い](/blogs/posts/2026/10/ducklake-sql-lakehouse/) — 2026-10-13
- [Redshift か、S3 ＋ Iceberg のレイクハウスか：DWH とオープンテーブルフォーマットの選び方](/blogs/posts/2026/10/redshift-vs-lakehouse/) — 2026-10-13
- [Iceberg と DuckLake の先へ：2026 年に注目したいレイクハウスの技術とプロダクト](/blogs/posts/2026/10/lakehouse-ecosystem-2026/) — 2026-10-13
- [AI エージェントのためのデータ基盤：レイクハウスを土台に「意味・費用・権限・取り消し」を設計する](/blogs/posts/2026/10/ai-agent-data-platform/) — 2026-10-13
