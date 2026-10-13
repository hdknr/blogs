---
title: "Apache Iceberg"
description: "S3 などのオブジェクトストレージ上のファイル群をデータベースのテーブルとして扱うオープンテーブルフォーマット。ACID・タイムトラベル・スキーマ進化を実現し、計算エンジンを用途ごとに選べるようにする"
date: 2026-10-13
lastmod: 2026-10-13
aliases: ["Iceberg", "オープンテーブルフォーマット", "テーブルフォーマット", "Open Table Format", "hidden partitioning", "隠れパーティショニング"]
related_posts:
  - "/posts/2026/10/apache-iceberg-duckdb/"
  - "/posts/2026/10/ducklake-sql-lakehouse/"
tags: ["Apache Iceberg", "データレイク", "Parquet", "S3", "aws", "データ基盤"]
---

## 概要

Apache Iceberg は、オブジェクトストレージ上に置かれたファイル群をデータベースのテーブルのように扱えるようにする**オープンテーブルフォーマット**。Netflix で開発され、Apache Software Foundation に寄贈された（Apache 2.0 ライセンス）。

Parquet が「1 つのファイルの中身をどう並べるか」を決める**ファイルフォーマット**なのに対し、Iceberg は「どのファイルの集まりがいまこのテーブルを構成しているか」を管理する**テーブルフォーマット**。データ本体は多くの場合 Parquet で保存されるので、両者は競合せずレイヤーが違う。

## 詳細

### データ基盤の 3 層での位置

| 層 | 役割 | 例 |
|---|---|---|
| 分散ストレージ | 大量のデータを安く保持する | S3、HDFS |
| 計算エンジン | クエリを実行する | Spark、Trino、Athena、Snowflake、DuckDB |
| テーブル化技術 | ファイル群をテーブルとして見せる | **Iceberg**、Delta Lake、Hudi |

価値の中心は機能より**設計思想**にある。従来の DWH はストレージ・テーブル管理・計算エンジンが 1 製品に閉じていたが、Iceberg はテーブル管理の層を OSS の仕様として切り出す。データは S3 に 1 か所だけ置き、BI チームは Snowflake、データエンジニアは Spark、アナリストは手元の DuckDB と、**用途ごとにエンジンを選べる**。代わりに、誰がどのエンジンから書き込めるかを決めるガバナンスは別途必要になる。

### 従来の S3 データレイクとの違い

| 項目 | 従来の S3 データレイク | Iceberg |
|---|---|---|
| 更新・削除 | ファイル（パーティション）単位の作り直しになりがち | レコード単位の UPDATE / DELETE / MERGE |
| 履歴管理 | スナップショットを自前で管理 | タイムトラベルで過去の状態を参照 |
| スキーマ変更 | 互換性の確認に手間 | スキーマ進化（既存ファイルを書き換えずに列の追加・削除・改名） |

AWS の解説は ACID トランザクションとインクリメンタル処理（前回から変わった分だけ処理）も主な特徴に挙げている。

### 仕組み：カタログ → メタデータ → データ

- **カタログ** — テーブル名と「最新のメタデータファイルの位置」を対応づける入り口。AWS では Glue Data Catalog や Amazon S3 Tables。ベンダー中立な **Iceberg REST カタログ**の API 仕様もある
- **メタデータファイル**（`vN.metadata.json`）— スキーマ、パーティション仕様、スナップショット一覧
- **マニフェストリスト** — スナップショットごとに 1 つ。構成するマニフェストを列挙
- **マニフェスト** — データファイルのパスと列ごとの最小値・最大値などの統計
- **データ層** — Parquet データファイルと、行の削除を記録する削除ファイル

書き込みは新しいファイルとスナップショットを追加し、最後にカタログが指すメタデータファイルを**アトミックに差し替える**ことで ACID を実現する。古いスナップショットをたどればタイムトラベル、マニフェストの列統計でファイルを開かずに読み飛ばせる。`day(event_time)` のような変換をテーブル定義に持たせる **hidden partitioning** により、利用者はパーティション列を意識せず `event_time` で絞り込むだけで済む。

### AWS での典型構成

各種ソースから S3 に取り込み → Glue / EMR で整形して Iceberg テーブルとして書き込み → 更新・削除・履歴は Iceberg に任せ → Athena などで参照。Athena、EMR、Glue、Redshift、Amazon Data Firehose が Iceberg に対応している。S3 Tables は Iceberg テーブルの保存に特化した S3 のバケット種別。

### DuckDB から使う

DuckDB の `iceberg` 拡張で読み書きできる（詳細は [DuckDB](/blogs/wiki/tools/duckdb/)）。

- `iceberg_scan` による直接読み取りは**読み取り専用**で、最新メタデータを判断するには `version-hint.text` かバージョン指定が必要
- カタログ（S3 Tables、Glue の Iceberg REST エンドポイント）に `ATTACH ... (TYPE ICEBERG)` すれば書き込みも可能。v1.4.0 で読み取り全面対応と書き込み初期対応、v1.4.2 で Iceberg v2 テーブルへの UPDATE / DELETE
- UPDATE / DELETE は positional delete を書く **merge-on-read のみ**（copy-on-write 非対応）。拡張はまだ experimental

重い ETL は Glue / EMR の Spark、DuckDB は手元の探索や軽い集計・小規模修正、という分担が無難。

### メタデータ設計への批判と DuckLake

[DuckLake](/blogs/wiki/tools/ducklake/) の Manifesto は、Iceberg のファイルベースのメタデータについて「カタログ → メタデータ → マニフェストリスト → マニフェストと S3 への直列リクエストが続く」「小さなメタデータファイルが増え、ルートのメタデータは履歴とともに肥大する」「コミットが遅く衝突しやすい」と指摘している。小さな書き込みが続くと小さなファイルが増え、定期的なコンパクションが必要になる点も対比される。

使い分けの目安は、**複数エンジンで同じテーブルを共有したいなら Iceberg**、読み書きがほぼ DuckDB だけなら DuckLake。

## 関連ページ

- [DuckLake](/blogs/wiki/tools/ducklake/) — メタデータを SQL データベースに置く別のレイクハウスフォーマット
- [DuckDB](/blogs/wiki/tools/duckdb/) — Iceberg を読み書きできる計算エンジンの 1 つ
- [列指向ストレージ](/blogs/wiki/concepts/columnar-storage/) — データ本体の Parquet の土台

## ソース記事

- [Apache Iceberg 入門：データレイクを「テーブル」にする仕組みと DuckDB との関係](/blogs/posts/2026/10/apache-iceberg-duckdb/) — 2026-10-12
- [DuckLake 入門：メタデータを SQL データベースに置くレイクハウスフォーマットと Iceberg との違い](/blogs/posts/2026/10/ducklake-sql-lakehouse/) — 2026-10-13
