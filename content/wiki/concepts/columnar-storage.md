---
title: "列指向ストレージ"
description: "データを列ごとに格納するストレージ方式。分析クエリの I/O 効率と圧縮率を大幅向上"
date: 2026-04-06
lastmod: 2026-10-13
aliases: ["Columnar Storage", "列指向"]
related_posts:
  - "/posts/2026/03/duckdb-columnar-arrow/"
  - "/posts/2026/10/apache-iceberg-duckdb/"
  - "/posts/2026/10/ducklake-sql-lakehouse/"
tags: ["データベース", "OLAP", "Parquet", "Arrow"]
---

## 概要

行単位ではなく列単位でデータを格納。分析クエリで必要な列だけ読み込むため I/O が効率的で、同じ型のデータが連続するため圧縮率も向上。Parquet（ストレージ）、Arrow（メモリ）、DuckDB（エンジン）が列指向エコシステムを形成。

## 詳細

### ファイルフォーマットの上に「テーブルフォーマット」が乗る

Parquet は「1 つのファイルの中身をどう並べるか」を決める**ファイルフォーマット**。S3 に Parquet を置くだけでも Athena や Spark から SQL を投げられるが、1 行の修正・過去の状態への巻き戻し・列の追加は難しい。

そこで「どのファイルの集まりがいまこのテーブルを構成しているか」を管理する**テーブルフォーマット**を上に重ねる。

- [Apache Iceberg](/blogs/wiki/tools/apache-iceberg/) — メタデータを S3 上のファイル階層（メタデータファイル → マニフェストリスト → マニフェスト）とカタログで持つ。マニフェストの列ごとの最小値・最大値を使い、ファイルを開かずに読み飛ばせる
- [DuckLake](/blogs/wiki/tools/ducklake/) — 同じく Parquet をデータに使い、メタデータは SQL データベースに置く

どちらもデータ本体は列指向の Parquet で、競合ではなくレイヤーが違う。

## 関連ページ

- [DuckDB](/blogs/wiki/tools/duckdb/) — 列指向 OLAP エンジン
- [Apache Iceberg](/blogs/wiki/tools/apache-iceberg/) — Parquet の上に乗るオープンテーブルフォーマット
- [DuckLake](/blogs/wiki/tools/ducklake/) — メタデータを SQL データベースに置くレイクハウスフォーマット

## ソース記事

- [DuckDB と列指向ストレージ](/blogs/posts/2026/03/duckdb-columnar-arrow/) — 2026-03
- [Apache Iceberg 入門：データレイクを「テーブル」にする仕組みと DuckDB との関係](/blogs/posts/2026/10/apache-iceberg-duckdb/) — 2026-10-12
- [DuckLake 入門：メタデータを SQL データベースに置くレイクハウスフォーマットと Iceberg との違い](/blogs/posts/2026/10/ducklake-sql-lakehouse/) — 2026-10-13
