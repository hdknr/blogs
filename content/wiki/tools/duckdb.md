---
title: "DuckDB"
description: "インプロセス OLAP データベース。列指向アーキテクチャで分析クエリを高速実行"
date: 2026-04-06
lastmod: 2026-04-06
aliases: ["duckdb"]
related_posts:
  - "/posts/2026/03/duckdb-columnar-arrow/"
tags: ["データベース", "OLAP", "SQL", "Python"]
---

## 概要

列指向ストレージを採用した SQL データベースエンジン。Apache Arrow、Parquet と同じエコシステムの一部で、分析ワークロード（集計、GROUP BY）で従来の行指向 DB より圧倒的に高速。ベクトル化実行エンジンと自動並列化で OLAP に最適化。

## 関連ページ

- [列指向ストレージ](/blogs/wiki/concepts/columnar-storage/) — DuckDB が採用するストレージ方式

## ソース記事

- [DuckDB と列指向ストレージ](/blogs/posts/2026/03/duckdb-columnar-arrow/) — 2026-03
