---
title: "DuckDB・Apache Arrow・Parquetの関係を整理する：列指向エコシステムの全体像"
date: 2026-03-19
lastmod: 2026-03-19
draft: false
categories: ["データベース"]
tags: ["duckdb", "python"]
---

DuckDB は「SQLite の分析版」とも呼ばれるインプロセス OLAP データベースです。Apache Arrow、Apache Parquet と同じ列指向の思想を持ちますが、三者の役割はそれぞれ異なります。この記事では DuckDB のアーキテクチャ、Arrow・Parquet との関係、そして従来の行指向 DB との違いを整理します。

## Parquet・Arrow・DuckDB の位置付け

| | Parquet | Arrow | DuckDB |
|---|---|---|---|
| **何か** | ディスク上の列指向ファイル形式 | インメモリ列指向データフォーマット（仕様+ライブラリ） | SQL データベースエンジン |
| **レイヤー** | ストレージ（ディスク） | データ交換（メモリ） | クエリ実行（エンジン） |
| **目的** | 効率的な永続化・圧縮 | アプリケーション間のゼロコピーデータ交換 | SQL クエリの実行・最適化 |

三者は列指向エコシステムの異なるレイヤーを担っており、補完関係にあります。

```
[ディスク]  Parquet ファイル（列指向・圧縮済み）
    ↓ 読み込み（必要な列だけ）
[メモリ]   Arrow フォーマット（列指向・ゼロコピー）
    ↓ クエリ実行
[エンジン]  DuckDB（ベクトル化 SQL 実行）
```

Parquet は「データの保存形式」、Arrow は「メモリ上のデータの並べ方の規格」、DuckDB は「SQL を実行するエンジン」です。三者とも列指向という共通思想を持つため、組み合わせるとデータ変換のオーバーヘッドがほぼ発生しません。

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

### Polars とは

[Polars](https://pola.rs/) は Rust で実装された高速な DataFrame ライブラリです。内部データ形式に Apache Arrow を採用しており、列指向エコシステムの一員として DuckDB・Arrow・Parquet と自然に連携します。

Pandas との主な違いは以下の通りです。

| | Pandas | Polars |
|---|---|---|
| **実装言語** | C / Python | Rust |
| **内部データ形式** | 独自（NumPy ベース） | Apache Arrow |
| **実行モデル** | 即時実行のみ | 即時実行 + 遅延実行（Lazy） |
| **マルチスレッド** | 基本シングルスレッド | 自動並列化 |
| **メモリ効率** | コピーが多い | ゼロコピー・Arrow ベース |

Polars の遅延実行（Lazy API）は、DuckDB のクエリオプティマイザと似た発想で、処理グラフ全体を見てから最適な実行計画を立てます。不要な列の除去やフィルターの先行実行が自動で行われます。

### DuckDB × Polars の連携

DuckDB は Polars の DataFrame を Arrow 経由でゼロコピーのまま SQL クエリできます。

```python
import duckdb
import polars as pl

# Polars DataFrame を作成
lf = pl.LazyFrame({"name": ["Alice", "Bob", "Charlie"], "score": [85, 92, 78]})
df = lf.collect()

# DuckDB から直接 SQL でクエリ（Arrow 経由・ゼロコピー）
result = duckdb.sql("SELECT name, score FROM df WHERE score >= 80")
print(result.pl())  # 結果を Polars DataFrame で取得
```

Polars の得意な変換処理と DuckDB の SQL クエリを組み合わせることで、それぞれの強みを活かしたワークフローが構築できます。2026年現在、「DuckDB + Polars + Pandas」を組み合わせたワークフローが Python データ処理の主流になりつつあります。

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

## Apache Parquet とは

Apache Parquet はディスク上の列指向ファイルフォーマットです。CSV や JSON の「列指向版」と考えるとわかりやすいでしょう。

```
CSV（行指向）:
  id,name,age
  1,Alice,30
  2,Bob,25
  → 1行ずつ順番に格納

Parquet（列指向）:
  id列:   [1, 2]       ← まとめて圧縮
  name列: [Alice, Bob]  ← まとめて圧縮
  age列:  [30, 25]      ← まとめて圧縮
```

### Parquet の利点

- **圧縮効率が高い**: 同じ型のデータが連続するため、CSV の 1/5〜1/10 程度のサイズになることが多い
- **不要な列を読み飛ばせる**: `SELECT age FROM ...` なら age 列だけ読む（CSV は全行パースが必要）
- **パーティション除去**: フィルター条件に合わないデータブロックをまるごとスキップできる

### DuckDB と Parquet の組み合わせが速い理由

両方とも列指向のため、DuckDB のオプティマイザがフィルターと列選択を Parquet のスキャン段階にプッシュダウンできます。

```sql
-- CSV: 全行パースしてからフィルター（遅い）
SELECT AVG(age) FROM read_csv_auto('users.csv') WHERE country = 'JP';

-- Parquet: age列とcountry列だけ読み、該当ブロックだけスキャン（速い）
SELECT AVG(age) FROM read_parquet('users.parquet') WHERE country = 'JP';
```

具体的には以下の最適化が自動で行われます。

- **Column Pruning**: クエリに必要な列だけを読み込む
- **Predicate Pushdown**: 条件に合わないデータブロックを丸ごとスキップ
- **ゼロコピー処理**: 読み込んだデータは Arrow 形式でメモリコピーなしに処理

### CSV → Parquet への変換

DuckDB 自体で簡単に変換できます。一度 Parquet に変換しておけば、以降のクエリが劇的に速くなります。

```sql
-- CSV を Parquet に変換（DuckDB のワンライナー）
COPY (SELECT * FROM read_csv_auto('data.csv')) TO 'data.parquet' (FORMAT PARQUET);
```

## データフォーマットの比較

| フォーマット | 用途 | サイズ | 分析速度 | 人間の可読性 |
|---|---|---|---|---|
| CSV / JSON | 小規模データ・データ交換 | 大 | 遅い | ✅ |
| Parquet | 大規模データの永続化 | 小（圧縮） | 速い | |
| Arrow | メモリ上のデータ交換 | - | 最速（ゼロコピー） | |

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

- **Parquet**（ディスク）→ **Arrow**（メモリ）→ **DuckDB**（クエリ）が列指向データ分析のゴールデンスタック
- 三者は列指向という共通思想を持ち、組み合わせるとデータ変換のオーバーヘッドが最小になる
- Parquet は CSV に比べてファイルサイズが 1/5〜1/10 で、必要な列だけ読める
- DuckDB と Arrow はゼロコピーで連携でき、Pandas/Polars とも統合が進んでいる
- 行指向 DB（SQLite, PostgreSQL）とは得意分野が異なり、分析クエリで圧倒的な性能を発揮する

## 参考リンク

- [DuckDB 公式ドキュメント](https://duckdb.org/docs/stable/)
- [DuckDB Quacks Arrow: Zero-Copy Data Integration（DuckDB 公式ブログ）](https://duckdb.org/2021/12/03/duck-arrow)
- [Apache Arrow と DuckDB のゼロコピー統合（Arrow 公式ブログ）](https://arrow.apache.org/blog/2021/12/03/arrow-duckdb/)
- [Parquet とは何なのか — 不要なデータを読み飛ばせることの真価（サーバーワークスブログ）](https://blog.serverworks.co.jp/2025/06/11/085838)
- [DuckDB で CSV より Parquet が速い理由（grasys blog）](https://blog.grasys.io/post/nishino/duckdb-apache-parquet/)
