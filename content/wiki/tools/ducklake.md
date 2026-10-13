---
title: "DuckLake"
description: "DuckDB チームのレイクハウスフォーマット。データは Parquet でオブジェクトストレージに、メタデータはすべて PostgreSQL などの SQL データベースに置く"
date: 2026-10-13
lastmod: 2026-10-13
aliases: ["ducklake", "DuckLake Manifesto", "data inlining", "レイクハウスフォーマット"]
related_posts:
  - "/posts/2026/10/ducklake-sql-lakehouse/"
  - "/posts/2026/10/apache-iceberg-duckdb/"
tags: ["DuckLake", "duckdb", "Apache Iceberg", "データレイク", "PostgreSQL", "Parquet", "データ基盤"]
---

## 概要

DuckLake は、DuckDB の開発チームが作ったレイクハウスフォーマット。データは Parquet ファイルとして S3 などに置き、**メタデータはすべてカタログデータベース（PostgreSQL・SQLite・DuckDB など）に格納**する。2025 年 5 月 27 日に発表、v1.0 は 2026 年 4 月 13 日（DuckDB v1.5.2 の `ducklake` 拡張で利用可能）。仕様と拡張はどちらも MIT ライセンスで、v1.0 は後方互換性が保証された本番利用向けの仕様として出された。

## 詳細

### なぜメタデータを SQL データベースに置くのか

[DuckLake Manifesto](https://ducklake.select/manifesto/) の出発点は「Iceberg や Delta Lake はデータベースを使わずに済むよう設計されたのに、結局カタログ層でデータベースを使っている。ならば残りのメタデータも全部そこに入れればいい」という主張。ファイルベースのメタデータの問題として次を挙げる。

- **リクエストが直列になる** — カタログ → メタデータファイル → マニフェストリスト → マニフェストと S3 への HTTP リクエストを順に投げ、それがレイテンシの下限になる
- **小さなメタデータファイルが増える** — 変更のたびにでき、ルートのメタデータは履歴とともに大きくなる
- **コミットが衝突しやすい** — コミットに時間がかかるため同時書き込みで衝突しやすい

DuckLake の書き込みは「Parquet を置く」→「ファイル・統計・スナップショットを 1 つの SQL トランザクションで記録」の 2 段階。スナップショットもテーブルの行にすぎない。なお「PostgreSQL カタログで数百 TB・数千ノードまでスケール」といった数字は開発チームの設計上の見込みで、第三者のベンチマークではない。

### DuckDB での使い方

`INSTALL ducklake;` のうえで `ATTACH 'ducklake:<カタログの場所>' AS my_ducklake;` するだけで、普通のテーブルと同じように SQL を書ける。変更のたびにスナップショットが作られ、`my_ducklake.snapshots()` で一覧、`AT (VERSION => n)` でタイムトラベルできる。

| カタログ | 向いている用途 | 注意点 |
|---|---|---|
| DuckDB ファイル | 1 人でローカル | クライアントは 1 つ |
| SQLite | ローカルで複数クライアント | 読み取りと書き込みを同時にはできない |
| PostgreSQL | 複数ユーザー・リモート | PostgreSQL 12 以上 |
| MySQL | — | DuckDB の MySQL コネクタの制約による既知の問題があり、公式には推奨されていない |

PostgreSQL カタログ（`ducklake:postgres:dbname=...`）とオブジェクトストレージの `DATA_PATH` を組み合わせると、**複数の DuckDB プロセスが同じデータセットを同時に読み書き**できる。素の DuckDB ファイルは 1 プロセスしか書き込めないので、DuckDB をマルチユーザー化する手段にもなる。

### v1.0 の主な機能

- **data inlining** — 一定行数未満の変更を Parquet に書かずカタログ DB に直接格納し、スモールファイル問題を避ける。既定で有効・しきい値 10 行（`ducklake_default_data_inlining_row_limit` やテーブル単位の `data_inlining_row_limit` で変更）。インライン化されたデータもクエリ・タイムトラベルできる。`ducklake_flush_inlined_data` で Parquet に書き出し、`CHECKPOINT` は書き出しに加えてスナップショットの期限切れ処理やファイル結合もまとめて行う
- **ソート済みテーブル** — `SET SORTED BY (...)` で範囲検索時にファイルを読み飛ばしやすくする
- **バケットパーティション** — `bucket(8, col)`。ハッシュは Iceberg と同じ murmur3
- **`COUNT(*)` のメタデータ応答** — S3 上でも件数を高速に返す
- **削除ベクター（experimental）** — Iceberg v3 と同じく Puffin ファイルにビットマップで保存。既定は positional delete

### Iceberg との互換性と移行

データファイルと positional delete ファイルは Iceberg 互換。DuckDB の `iceberg` 拡張と組み合わせて移行できる。

- **Iceberg → DuckLake**: `CALL iceberg_to_ducklake(...)` でメタデータだけをコピー（データファイルはそのまま、過去のスナップショットも扱える）
- **DuckLake → Iceberg**: `COPY FROM DATABASE ... TO ...` によるデータごとのコピー（メタデータのみのコピーは逆方向非対応）

まず DuckLake で小さく始め、他エンジンが必要になったら Iceberg へ移す道が残る。

### Iceberg との使い分け

| 観点 | Apache Iceberg | DuckLake |
|---|---|---|
| メタデータ | S3 上のファイル＋カタログ | SQL データベース |
| 対応エンジン | Spark、Trino、Flink、Athena、Snowflake、DuckDB など多数 | DuckDB 中心（Spark・Trino・DataFusion 向けクライアントも登場） |
| 運用に必要なもの | カタログサービス（Glue、S3 Tables、REST） | PostgreSQL などの RDB |
| 小さな書き込み | 小さなファイルが増えコンパクションが必要 | data inlining でカタログに吸収 |
| ガバナンス | Apache Software Foundation | DuckDB チーム（MIT） |

判断材料は、エンジンの多様性が要るか、小さな書き込みの頻度（ストリーミングなら DuckLake 有利）、PostgreSQL を運用できるか（カタログ DB の可用性とバックアップがそのままデータ基盤の信頼性になる）。

## 関連ページ

- [Apache Iceberg](/blogs/wiki/tools/apache-iceberg/) — 比較対象のオープンテーブルフォーマット
- [DuckDB](/blogs/wiki/tools/duckdb/) — `ducklake` 拡張を提供するエンジン
- [列指向ストレージ](/blogs/wiki/concepts/columnar-storage/) — データ本体の Parquet

## ソース記事

- [DuckLake 入門：メタデータを SQL データベースに置くレイクハウスフォーマットと Iceberg との違い](/blogs/posts/2026/10/ducklake-sql-lakehouse/) — 2026-10-13
- [Apache Iceberg 入門：データレイクを「テーブル」にする仕組みと DuckDB との関係](/blogs/posts/2026/10/apache-iceberg-duckdb/) — 2026-10-12
