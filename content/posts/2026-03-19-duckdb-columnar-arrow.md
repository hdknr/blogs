---
title: "DuckDBとApache Arrowの関係を整理する：列指向DB・ゼロコピー連携・使い分け"
date: 2026-03-19
lastmod: 2026-03-19
draft: false
categories: ["データベース"]
tags: ["duckdb", "python"]
---

DuckDB は「SQLite の分析版」とも呼ばれるインプロセス OLAP データベースです。Apache Arrow と同じ列指向の思想を持ちますが、両者の役割は異なります。この記事では DuckDB のアーキテクチャ、Arrow との関係、そして従来の行指向 DB との違いを整理します。

## DuckDB と Apache Arrow の位置付け

| | DuckDB | Apache Arrow |
|---|---|---|
| **何か** | SQL データベースエンジン | インメモリ列指向データフォーマット（仕様+ライブラリ） |
| **目的** | SQL クエリの実行・最適化 | アプリケーション間のゼロコピーデータ交換 |
| **ストレージ** | 独自の列指向形式 + 外部ファイル対応 | メモリ上のデータレイアウト仕様 |

Arrow は「データの並べ方の規格」、DuckDB は「その上で SQL を実行するエンジン」です。Arrow 単体ではクエリを実行できず、DuckDB 単体でもデータ交換の標準規格にはなりません。両者は補完関係にあります。

## DuckDB の高速性を支える3つの柱

### 1. 列指向ストレージ

行単位ではなく列単位でデータを格納します。分析クエリ（`SUM`, `AVG`, `GROUP BY` など）で必要な列だけを読み込むため、I/O が効率的です。

### 2. ベクトル化実行エンジン

1行ずつではなく、列のチャンク（ベクトル）単位で処理します。これにより CPU キャッシュのヒット率が上がり、SIMD 命令も活用できます。

### 3. 自動並列化

マルチコアを自動的に活用し、クエリを並列実行します。ユーザー側で並列化の設定を意識する必要はありません。

## 行指向と列指向の違い

```
行指向 (MySQL, PostgreSQL, SQLite):
  行1: [id=1, name="Alice", age=30]
  行2: [id=2, name="Bob",   age=25]

列指向 (DuckDB, Arrow):
  id:   [1, 2]
  name: ["Alice", "Bob"]
  age:  [30, 25]
```

`SELECT AVG(age) FROM users` のようなクエリでは、列指向なら `age` 列だけ読めば済むので、行指向より圧倒的に高速です。一方で、`INSERT INTO` のような1行ずつの書き込みは行指向の方が得意です。

| 操作 | 行指向が有利 | 列指向が有利 |
|---|---|---|
| 1行の INSERT/UPDATE | ✅ | |
| 特定行の SELECT (WHERE id=1) | ✅ | |
| 集計クエリ (SUM, AVG, COUNT) | | ✅ |
| 大量データのスキャン | | ✅ |
| GROUP BY + 集計 | | ✅ |

## Arrow とのゼロコピー連携

DuckDB と Arrow の連携で最も重要なのがゼロコピー統合です。データのメモリコピーが発生しないため、大規模データでもオーバーヘッドが極めて小さくなります。

```python
import duckdb
import pyarrow as pa

# Arrow テーブルを直接 SQL でクエリ（データコピーなし）
arrow_table = pa.table({"x": [1, 2, 3], "y": ["a", "b", "c"]})
result = duckdb.sql("SELECT * FROM arrow_table WHERE x > 1")

# 結果を Arrow 形式で取得（これもゼロコピー）
arrow_result = result.arrow()
```

このゼロコピー連携の利点は以下の通りです。

- **メモリ効率**: データの複製が不要なため、メモリ消費を抑えられる
- **フィルタープッシュダウン**: DuckDB のオプティマイザがフィルターや射影を Arrow スキャン側にプッシュダウンし、必要な列・パーティションだけを読み込む
- **メモリ超過データの処理**: 両ライブラリがストリーミングに対応しているため、メモリに収まらないデータも処理可能

## Pandas・Polars エコシステムとの統合

DuckDB は Python のデータ分析エコシステムとシームレスに統合できます。

```python
import duckdb
import pandas as pd

# Pandas DataFrame を直接 SQL でクエリ
df = pd.DataFrame({"category": ["A", "B", "A"], "value": [10, 20, 30]})
result = duckdb.sql("SELECT category, SUM(value) FROM df GROUP BY category")
print(result.df())  # 結果を Pandas DataFrame で取得
```

Polars との連携も同様にゼロコピーで動作します。2026年現在、「DuckDB + Polars + Pandas」を組み合わせたワークフローが Python データ処理の主流になりつつあります。

## 外部ファイルの直接クエリ

DuckDB の大きな特徴として、CSV・JSON・Parquet ファイルをロードなしで直接クエリできます。

```sql
-- CSV を直接クエリ
SELECT * FROM read_csv_auto('sales.csv') WHERE amount > 1000;

-- Parquet を直接クエリ（列指向フォーマット同士で特に高速）
SELECT region, SUM(amount) FROM read_parquet('sales.parquet') GROUP BY region;

-- JSON も対応
SELECT * FROM read_json_auto('logs.json') WHERE level = 'error';
```

特に Parquet ファイルとの組み合わせは、ファイル自体が列指向フォーマットであるため、DuckDB の列指向エンジンと相性が良く最も高速に動作します。

## SQLite との使い分け

| ユースケース | SQLite | DuckDB |
|---|---|---|
| OLTP（トランザクション処理） | ✅ | |
| OLAP（分析処理） | | ✅ |
| 1行ずつの INSERT/UPDATE | ✅ | |
| 大量データの集計・分析 | | ✅ |
| ファイル直接クエリ（CSV/Parquet） | | ✅ |
| アプリケーション組み込み | ✅ | ✅ |
| サーバー不要 | ✅ | ✅ |

両者は競合ではなく補完関係です。トランザクション処理には SQLite、分析処理には DuckDB という使い分けが基本になります。

## まとめ

- DuckDB は Arrow と同じ**列指向の思想**を持つ SQL 実行エンジン
- Arrow が「データフォーマット仕様」なのに対し、DuckDB は「クエリ実行エンジン」
- 両者はゼロコピーで連携でき、Pandas/Polars とも統合が進んでいる
- 行指向 DB（SQLite, PostgreSQL）とは得意分野が異なり、分析クエリで圧倒的な性能を発揮する

## 参考リンク

- [DuckDB 公式ドキュメント](https://duckdb.org/docs/stable/)
- [DuckDB Quacks Arrow: Zero-Copy Data Integration（DuckDB 公式ブログ）](https://duckdb.org/2021/12/03/duck-arrow)
- [Apache Arrow と DuckDB のゼロコピー統合（Arrow 公式ブログ）](https://arrow.apache.org/blog/2021/12/03/arrow-duckdb/)
