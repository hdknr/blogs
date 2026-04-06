---
title: "列指向ストレージ"
description: "データを列ごとに格納するストレージ方式。分析クエリの I/O 効率と圧縮率を大幅向上"
date: 2026-04-06
lastmod: 2026-04-06
aliases: ["Columnar Storage", "列指向"]
related_posts:
  - "/posts/2026/03/duckdb-columnar-arrow/"
tags: ["データベース", "OLAP", "Parquet", "Arrow"]
---

## 概要

行単位ではなく列単位でデータを格納。分析クエリで必要な列だけ読み込むため I/O が効率的で、同じ型のデータが連続するため圧縮率も向上。Parquet（ストレージ）、Arrow（メモリ）、DuckDB（エンジン）が列指向エコシステムを形成。

## 関連ページ

- [DuckDB](/blogs/wiki/tools/duckdb/) — 列指向 OLAP エンジン

## ソース記事

- [DuckDB と列指向ストレージ](/blogs/posts/2026/03/duckdb-columnar-arrow/) — 2026-03
