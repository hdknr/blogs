---
title: "データエンジニアのためのデータ構造入門：ハッシュ・B-tree から LSM ツリー、Bloom フィルタ、HNSW まで"
date: 2026-11-20
lastmod: 2026-11-20
slug: "data-structures-for-data-engineers"
draft: false
description: "ハッシュ表・B-tree・ヒープ・ログから列指向・LSM ツリー・Bloom フィルタ・HyperLogLog・HNSW まで、データベースとデータ処理の速さを決めるデータ構造を、計算量の感覚と Python の例で整理します。"
categories: ["データベース"]
tags: ["データエンジニアリング", "データ構造", "データベース", "Parquet", "ベクトル検索"]
---

## はじめに

[AI エンジニアこそデータエンジニアリングを学ぶべき理由](/blogs/posts/2026/11/data-engineering-for-ai-engineers/) で紹介したデータエンジニアリングのロードマップでは、基礎の段階に Python・SQL・Linux・Git と並んで「データ構造」が置かれています。

アルゴリズムの教科書に出てくる配列やハッシュ表が、データ基盤の仕事とどう関係するのか。結論から言えば、**データベースやデータ処理ツールの「速い・遅い」「正確・近似」の違いは、ほとんどが中で使っているデータ構造の違いで説明できます**。重複排除が遅い、JOIN が終わらない、`COUNT(DISTINCT ...)` が高い、ベクトル検索の精度が落ちる。こうした現場の悩みは、データ構造を知っていると原因の見当が付きます。

この記事では、AI エンジニアやアプリケーションエンジニアに向けて、基本のデータ構造と、データエンジニアリングで特に出てくるデータ構造を、計算量の感覚、実際のツールでの使われ方、短いコード例（Python・SQL・Redis）で整理します。

## 用語

| 用語 | 意味 |
|---|---|
| 計算量（O 記法） | データ件数 n が増えたとき、処理時間やメモリがどう増えるかの目安。O(1) は件数に依らず一定、O(log n) は件数が 2 倍になっても 1 段増える程度、O(n) は件数に比例 |
| ハッシュ | 値から固定長の数値（ハッシュ値）を計算する関数。同じ値からは必ず同じハッシュ値が出る |
| インデックス | テーブルとは別に持つ、検索を速くするための補助的なデータ構造 |
| OLTP / OLAP | OLTP は 1 件ずつの読み書きが中心の業務処理、OLAP は大量の行を集計する分析処理 |
| 偽陽性 | 「ある」と答えたが実際には「ない」こと。確率的データ構造で許容する誤り |
| カーディナリティ | 列に含まれる値の種類の数。ユーザー ID なら高く、性別なら低い |
| 近似最近傍探索（ANN） | ベクトル同士の「近さ」で上位を探すとき、厳密さを少し諦めて速く探す方法 |
| 再現率 | 近似検索で、本当の上位 k 件のうち実際に返せた割合。1.0 なら取りこぼしなし |

## データ構造とデータエンジニアリングの対応表

先に全体像を表にします。左が教科書のデータ構造、右がそれを使っている代表的な場面です。

| データ構造 | 得意な操作 | データエンジニアリングでの出番 |
|---|---|---|
| 配列・リスト | 先頭からの走査、末尾への追加 | バッチ処理の読み込み、列指向フォーマットの 1 列分 |
| ハッシュ表・集合 | キーでの検索・追加が平均 O(1) | 重複排除、ハッシュ結合、ルックアップ表 |
| B-tree | 範囲検索・並べ替えが O(log n) | RDB のインデックス（PostgreSQL の既定） |
| ヒープ | 最大値・最小値の取り出し | 上位 k 件（トップ k）、優先度付きキュー |
| キュー・ログ | 末尾への追記、先頭からの順読み | Kafka のパーティション、データベースの WAL |
| 列指向レイアウト | 一部の列だけ大量に読む | Parquet、DuckDB、BigQuery |
| LSM ツリー | 大量の書き込み | RocksDB、Cassandra |
| Bloom フィルタ | 「確実にない」の判定 | LSM ツリーの読み込み、Parquet の読み飛ばし |
| HyperLogLog | 異なり数の近似 | `APPROX_COUNT_DISTINCT`、Redis の `PFCOUNT` |
| HNSW | ベクトルの近傍探索 | pgvector などのベクトルインデックス（RAG） |

以降、上から順に見ていきます。

## 配列・リスト：何も考えないときの基本形

配列（Python ではリスト）は、値を順番に並べただけの構造です。末尾への追加は O(1)（たまに領域の拡張が起きるので「償却」O(1)）、i 番目の取得も O(1) です。一方で、**値が含まれているかの確認（`x in list`）は先頭から順に見るので O(n) です**。先頭への挿入や先頭からの削除も、後ろの要素を全部ずらすので O(n) かかります（[Python 公式の計算量の表](https://docs.python.org/3/builtins/time-complexity.html)）。

データ処理では、「処理済み ID の一覧をリストに入れて、新しいレコードごとに `in` で確認する」コードがよく遅さの原因になります。10 万件の処理済みリストに対して 10 万件を確認すると、比較は最大で 100 億回です。

```python
import timeit

ids = list(range(100_000))
id_set = set(ids)

print("list:", timeit.timeit(lambda: 99_999 in ids, number=1_000))    # 毎回 O(n)
print("set: ", timeit.timeit(lambda: 99_999 in id_set, number=1_000))  # 平均 O(1)
```

手元の環境ではリストが集合の 1 万倍以上遅くなりました（探す値がリストの末尾にあるので、リストにとっては最悪の場合です。倍率は環境で変わります）。最初に覚えるべき規則は、**「含まれるか」を何度も聞くなら集合（set）か辞書（dict）を使う**ことです。

なお先頭から出し入れするキューが要るときは、リストではなく `collections.deque` を使います。`deque` は両端の追加・削除が O(1) です。

## ハッシュ表・集合：重複排除と結合の主役

ハッシュ表は、キーのハッシュ値から格納場所を計算する構造です。Python の `dict` と `set` がこれにあたり、検索・追加・削除は**平均 O(1)** です。ただし前述の Python 公式の計算量の表にあるとおり、すべてのキーが同じハッシュ値になる最悪の場合は O(n) まで落ちます。

### 重複排除：「最新版だけ残す」

冒頭の記事で挙げた RAG の本番課題に「同じ文書が 3 回改訂されたとき、検索で必ず最新版が返るか」がありました。取り込み時に文書 ID をキーにした辞書で最新版だけを残せば、全件を 1 回走査するだけ（O(n)）で済みます。

```python
docs = [
    {"doc_id": "A", "version": 1, "body": "初版"},
    {"doc_id": "B", "version": 1, "body": "初版"},
    {"doc_id": "A", "version": 3, "body": "第3版"},
    {"doc_id": "A", "version": 2, "body": "第2版"},
]

latest: dict[str, dict] = {}
for d in docs:
    cur = latest.get(d["doc_id"])
    if cur is None or d["version"] > cur["version"]:
        latest[d["doc_id"]] = d

print([(d["doc_id"], d["version"]) for d in latest.values()])
# [('A', 3), ('B', 1)]
```

### ハッシュ結合：JOIN の中身

SQL の JOIN も、多くのデータベースは内部でハッシュ表を作って実行します（ハッシュ結合）。小さいほうの表でハッシュ表を作り（build）、大きいほうの表を 1 行ずつ流してハッシュ表を引く（probe）ので、大きい表の行数を n、小さい表の行数を m とすると、全体で O(n + m) です。二重ループで突き合わせる O(n × m) とは桁が違います。

```python
orders = [(1, "u1", 1200), (2, "u2", 800), (3, "u1", 300)]
users = [("u1", "営業部"), ("u2", "開発部")]

# build: 小さい表からハッシュ表を作る
dept_by_user = {user_id: dept for user_id, dept in users}

# probe: 大きい表を 1 回だけ走査する
joined = [
    (oid, dept_by_user[uid], amount)
    for oid, uid, amount in orders
    if uid in dept_by_user
]
print(joined)
# [(1, '営業部', 1200), (2, '開発部', 800), (3, '営業部', 300)]
```

実行計画（`EXPLAIN`）に `Hash Join` と出ていれば、この形で動いています。ハッシュ表がメモリに収まらないとディスクへの書き出しが起きて急に遅くなるので、どちらの表からハッシュ表を作るか（build 側にするか）が性能に効きます。

## B-tree：データベースのインデックス

ハッシュ表は「キーが一致するもの」を探すのは得意ですが、「2026 年 11 月の注文」のような**範囲の検索や並べ替えはできません**。ハッシュ値は元の値の大小関係を保たないからです。

そこで RDB のインデックスには B-tree（正確には多くの実装が B+tree という変種）が使われます。B-tree はキーを並べた状態で保ち、1 つのノードに多数のキーを持たせて木を浅くした構造です。検索・挿入・削除は O(log n) です。ノードの大きさをディスクのページに合わせてあるので、何億行あっても数回のページ読み込みで目的の行に届きます。

PostgreSQL では `CREATE INDEX` の既定が B-tree で、`<`、`<=`、`=`、`>=`、`>` の比較や `BETWEEN`、`IN`、前方一致の `LIKE 'foo%'` に使えます。並べ替えた順に行を返せるので、`ORDER BY` の並べ替えを省ける場合もあります（[PostgreSQL のインデックスの種類](https://www.postgresql.org/docs/current/indexes-types.html)）。逆に `LIKE '%bar'` のような後方一致には使えません。

「並べたまま保つと範囲検索が速い」感覚は、Python の `bisect`（二分探索）で確かめられます。

```python
import bisect

# 日付順に並んだ注文（B-tree の葉が並んでいる状態のイメージ）
dates = ["2026-10-28", "2026-11-01", "2026-11-05", "2026-11-19", "2026-12-02"]

lo = bisect.bisect_left(dates, "2026-11-01")   # O(log n) で範囲の始点を探す
hi = bisect.bisect_left(dates, "2026-12-01")   # O(log n) で範囲の終点を探す
print(dates[lo:hi])
# ['2026-11-01', '2026-11-05', '2026-11-19']
```

インデックスは読み込みを速くする代わりに、書き込みのたびに木の更新が必要になります。大量のデータを一括で投入するときに、インデックスを一度外してから入れ直す手順がよく使われるのはこのためです。

## ヒープ：全部並べずに上位 k 件を取る

「スコアの高い上位 10 件」が欲しいとき、全件を並べ替えると O(n log n) かかります。ヒープは「親は必ず子以下」という条件だけを保つ木で、全体はきちんと並んでいませんが、最小値（または最大値）は根からすぐ取り出せます。**大きさ k のヒープを保ちながら全件を 1 回走査すれば O(n log k)** で上位 k 件が取れます。

Python の `heapq` は最小ヒープで、`heapq.nlargest` がまさにこの用途の関数です。公式ドキュメントは、k が小さいときに向いていて、k が大きいなら `sorted()`、k = 1 なら `max()` / `min()` のほうが効率がよいと説明しています（[heapq](https://docs.python.org/3/library/heapq.html)）。

```python
import heapq
import random

random.seed(0)
scores = [(random.random(), f"chunk-{i}") for i in range(1_000_000)]

top5 = heapq.nlargest(5, scores)  # 100 万件を並べ替えずに上位 5 件
for score, chunk_id in top5:
    print(f"{score:.6f} {chunk_id}")
```

RAG で類似度の上位 k 件のチャンクを選ぶ処理、ジョブスケジューラーの優先度付きキュー、SQL の `ORDER BY ... LIMIT k`（PostgreSQL の実行計画では `top-N heapsort` と表示されます）が同じ考え方です。

## キュー・ログ：追記するだけの構造が基盤を支える

キューは「先に入れたものから先に出す」構造です。データ基盤では、これを**消さずに追記し続ける「ログ」として使う**場面が重要です。

### Kafka のパーティション

Apache Kafka のトピックはパーティションに分かれ、各パーティションは「順序付きで変更されないレコードの並びに、追記され続けるコミットログ」です。各レコードにはパーティション内で連番の**オフセット**が振られ、コンシューマーは自分がどこまで読んだかをオフセットで管理します。古いオフセットに戻せば過去のデータを読み直せます（[Kafka の Introduction](https://kafka.apache.org/24/getting-started/introduction/)）。順序が保証されるのは 1 つのパーティションの中だけで、トピック全体の順序は保証されません。

冒頭の記事で挙げた「同期処理が途中で落ちて再実行したとき、重複データが生まれないか」という問いは、このオフセットの扱い方の問題です。追記だけのログなら「どこまで処理したか」を 1 つの数字で表せるので、再実行の起点がはっきりします。

### WAL（先行書き込みログ）

データベースも内部に追記型のログを持っています。PostgreSQL の WAL（Write-Ahead Logging）は、データファイルを変更する前にその変更内容をログに書き出しておく仕組みです。コミット時にはログだけをディスクに確定すればよく、**WAL は先頭から順に書くので、ばらばらの位置にあるデータページを書き出すより安く済みます**（[PostgreSQL の WAL の説明](https://www.postgresql.org/docs/current/wal-intro.html)）。クラッシュしたらログから変更をやり直します。

CDC（変更データキャプチャ）は、この WAL を外部から読んで変更を下流に流す技術です。追記型のログは、耐障害性・再実行・下流への配信をまとめて支えている基盤だと言えます。

## 行指向と列指向：同じ表でも並べ方で速さが変わる

ここからはデータエンジニアリング特有のデータ構造です。まず、表をディスクにどう並べるか。

![同じ 3 行の表（id・部署・金額）を、行指向では 1 行ぶんの値を続けて、列指向では 1 列ぶんの値を続けてディスクに並べる様子を比べた図。列指向では SUM(金額) が金額の列だけを読めばよいことを示している](/blogs/images/data-structures-row-vs-columnar.png)

- **行指向**（PostgreSQL、MySQL など）は 1 行の値を続けて置きます。1 件の取得・更新が 1 か所で済むので OLTP に向きます
- **列指向**（Parquet、DuckDB、BigQuery など）は 1 列の値を続けて置きます。`SUM(金額)` のように一部の列だけを大量に読む OLAP では、必要な列だけ読めばよく、同じ型の値が並ぶので圧縮もよく効きます

Parquet ファイルは、行をいくつかの**行グループ**に分け、各行グループの中に列ごとの**列チャンク**を並べた構造です。ファイル末尾のフッターに各列チャンクの位置などのメタデータがまとまっていて、読み手はまずフッターを読み、必要な列チャンクだけを取りに行きます（[Parquet の File Format](https://parquet.apache.org/docs/file-format/)）。

Parquet は列チャンクやページごとに最小値・最大値の統計を持てるので（[Parquet の Page Index](https://parquet.apache.org/docs/file-format/pageindex/)）、`WHERE 日付 >= '2026-11-01'` で範囲外の塊を開かずに読み飛ばせます。DuckDB はこの最小値・最大値のインデックス（ゾーンマップ）を、一般的なデータ型のすべての列に自動で作ります。`CREATE INDEX` で明示的に作るインデックスは ART（Adaptive Radix Tree）という木構造です（[DuckDB の Indexes](https://duckdb.org/docs/stable/sql/indexes)）。

```python
# pip install duckdb。orders.parquet は手元の Parquet ファイルに置き換えて試してください
import duckdb

# 使うのは amount と order_date の 2 列だけ。Parquet なら他の列の列チャンクは読まずに済む
duckdb.sql("SELECT SUM(amount) FROM 'orders.parquet' WHERE order_date >= '2026-11-01'").show()
```

列指向エコシステムの全体像は [DuckDB・Apache Arrow・Parquet の関係を整理する](/blogs/posts/2026/03/duckdb-columnar-arrow/) と wiki の [列指向ストレージ](/blogs/wiki/concepts/columnar-storage/)、Parquet の上に乗るテーブルフォーマットは wiki の [レイクハウス](/blogs/wiki/concepts/lakehouse/) にまとめています。

## LSM ツリー：書き込みを追記に変える

B-tree は更新のたびに木の途中のページを書き換えます。書き込みが集中すると、ディスク上のばらばらな位置を書き換えるランダム書き込みが増えます。LSM ツリー（Log-Structured Merge-tree）は、**書き込みをいったんメモリに溜め、並べた塊として追記していく**ことでこれを避ける構造です。

RocksDB を例にすると、流れは次のとおりです（[RocksDB Overview](https://github.com/facebook/rocksdb/wiki/RocksDB-Overview)）。

1. 書き込みは WAL に記録しつつ、メモリ上の **memtable** に入れる
2. memtable がいっぱいになると、キー順に並んだ **SST ファイル**としてディスクに書き出す（書き出し後、対応する WAL は消せる）
3. SST ファイルが増えてきたら、背後で複数のファイルを読み込んでマージし、上書き・削除済みのキーを取り除いた大きなファイルにまとめ直す（**コンパクション**）

Apache Cassandra も同じく memtable と、変更されない並べ済みの SSTable で構成されています（[Cassandra の Storage Engine](https://cassandra.apache.org/doc/latest/cassandra/architecture/storage-engine.html)）。

代わりに読み込みは不利になります。あるキーを探すとき、memtable と複数の SST ファイルを新しい順に見ていく必要があるからです。そこで次の Bloom フィルタが登場します。

## Bloom フィルタ：「確実にない」を安く判定する

Bloom フィルタは、ビット列と複数のハッシュ関数で「ある値が集合に含まれるか」を判定する確率的データ構造です。答えは「**確実にない**」か「**たぶんある**」の 2 通りです。偽陰性（あるのにないと答える）は起きませんが、偽陽性（ないのにあると答える）は一定の確率で起きます。要素そのものは保存しないので、集合を丸ごと持つよりずっと小さく済みます。

仕組みを最小限の Python で書くと次のようになります。

```python
import hashlib


class BloomFilter:
    def __init__(self, size_bits: int, num_hashes: int):
        self.size = size_bits
        self.k = num_hashes
        self.bits = bytearray(size_bits // 8 + 1)

    def _positions(self, item: str):
        for i in range(self.k):
            h = hashlib.sha256(f"{i}:{item}".encode()).digest()
            yield int.from_bytes(h[:8], "big") % self.size

    def add(self, item: str) -> None:
        for p in self._positions(item):
            self.bits[p // 8] |= 1 << (p % 8)

    def might_contain(self, item: str) -> bool:
        return all(self.bits[p // 8] & (1 << (p % 8)) for p in self._positions(item))


bf = BloomFilter(size_bits=10_000, num_hashes=7)
for user_id in ("u1", "u2", "u3"):
    bf.add(user_id)

print(bf.might_contain("u2"))    # True（入れたものは必ず True）
print(bf.might_contain("u999"))  # 多くの場合 False。まれに True（偽陽性）
```

データ基盤での使われ方は次のとおりです。

- **LSM ツリーの読み込み**：Cassandra は SSTable ごとにパーティションキーの Bloom フィルタを持ち、「確実にない」SSTable を読まずに済ませます。偽陽性の確率は `bloom_filter_fp_chance` で設定でき、既定はコンパクション方式によって 0.1 か 0.01 です（[Cassandra の Bloom Filters](https://cassandra.apache.org/doc/4.0/cassandra/operating/bloom_filters.html)）
- **Parquet の読み飛ばし**：ユーザー ID のようなカーディナリティの高い列では、最小値・最大値の範囲が広すぎて読み飛ばしに使えません。Parquet は列チャンクごとに Bloom フィルタを持てる仕様で、値 1 つあたり約 10 ビットで偽陽性率はおよそ 1% になります（[Parquet の Bloom Filter](https://parquet.apache.org/docs/file-format/bloomfilter/)）
- **PostgreSQL の `bloom` 拡張**：Bloom フィルタを使ったインデックスを追加できます（[bloom](https://www.postgresql.org/docs/current/bloom.html)）

標準の Bloom フィルタは要素を削除できない点に注意してください。ビットは複数の要素で共有されるので、1 つを消すと他の要素まで「ない」ことになりかねないからです。

## HyperLogLog：異なり数をほぼ一定のメモリで数える

「今日のユニークユーザー数」を正確に数えるには、見たユーザー ID をすべて集合に入れておく必要があり、メモリは件数に比例して増えます。HyperLogLog は、**わずかな誤差と引き換えに、件数に依らずほぼ一定のメモリで異なり数（カーディナリティ）を推定する**データ構造です。

[Redis](/blogs/wiki/tools/redis/) の実装は 1 キーあたり最大 12KB で、標準誤差は 0.81% です。`PFADD` で追加、`PFCOUNT` で推定値の取得、`PFMERGE` で複数の HyperLogLog の統合ができます（[Redis の HyperLogLog](https://redis.io/docs/latest/develop/data-types/probabilistic/hyperloglogs/)）。

```text
> PFADD visitors:2026-11-20 u1 u2 u3 u2
(integer) 1
> PFCOUNT visitors:2026-11-20
(integer) 3
> PFADD visitors:2026-11-21 u3 u4
(integer) 1
> PFMERGE visitors:week visitors:2026-11-20 visitors:2026-11-21
OK
> PFCOUNT visitors:week
(integer) 4
```

**統合（マージ）できる**ことがデータ基盤では特に効きます。日ごとの HyperLogLog を保存しておけば、週や月のユニーク数を元データに戻らずに出せます。正確な `COUNT(DISTINCT ...)` は日ごとの結果を足し合わせられない（同じユーザーを二重に数える）ので、この差は大きいです。

BigQuery の `APPROX_COUNT_DISTINCT` や HyperLogLog++ の関数群（`HLL_COUNT.INIT` で途中結果を作り、`HLL_COUNT.MERGE` で統合する）も同じ考え方です（[BigQuery の HyperLogLog++ functions](https://docs.cloud.google.com/bigquery/docs/reference/standard-sql/hll_functions)）。ダッシュボードの数字が「だいたい」でよいなら、近似関数のほうが速く安く済みます。

## HNSW：RAG を支えるベクトルインデックス

RAG では、質問文の埋め込みベクトルに近いチャンクを探します。全件と距離を計算する総当たりは O(n) なので、件数が増えると遅くなります。そこで、**厳密さを少し諦めて速く探す近似最近傍探索（ANN）のインデックス**を使います。代表が HNSW（Hierarchical Navigable Small World）です。

HNSW は、ベクトル同士を「近いもの」でつないだグラフを何層にも重ねた構造です。上の層はまばらで遠くまで一気に移動でき、下の層ほど密で細かく近傍をたどれます。探索は最上層から始めて、各層で目的に近い点へ移動しながら下りていきます。提案論文（Malkov と Yashunin、[arXiv:1603.09320](https://arxiv.org/abs/1603.09320)）は、総当たりが件数に比例するのに対し、HNSW は対数的なスケーリングを実現すると述べています。

PostgreSQL の拡張 pgvector は HNSW と IVFFlat の 2 種類の近似インデックスを持っています（[pgvector](https://github.com/pgvector/pgvector)）。

```sql
-- m: 各点がつなぐ近傍の数（既定 16）、ef_construction: 構築時の候補数（既定 64）
CREATE INDEX ON items USING hnsw (embedding vector_l2_ops) WITH (m = 16, ef_construction = 64);

-- 検索時の候補数（既定 40）。増やすと再現率が上がり、遅くなる
SET hnsw.ef_search = 100;
SELECT id FROM items ORDER BY embedding <-> '[0.1, 0.2, 0.3]' LIMIT 5;
```

pgvector の README によれば、HNSW は IVFFlat より速度と再現率のバランスがよい一方、構築が遅くメモリを多く使います。IVFFlat と違って学習の手順が要らないので、空のテーブルにも作れます。

近似インデックスである以上、**本当に一番近いチャンクを取りこぼすことがあります**。RAG の検索精度が落ちたとき、埋め込みモデルやチャンク分割だけでなく、`ef_search` のようなインデックスのパラメーターも疑う対象になります。RAG 全体の構成は wiki の [RAG](/blogs/wiki/concepts/rag/) にまとめています。

## データ構造の選び方早見表

最後に、場面ごとの選び方をまとめます。

| やりたいこと | まず考えるデータ構造 | 注意点 |
|---|---|---|
| 「含まれるか」を何度も確認する | 集合・辞書 | リストの `in` は O(n) |
| 最新版だけ残す・重複を消す | 辞書（キー → 最新レコード） | キーの定義を業務と合わせる |
| 2 つの表を突き合わせる | ハッシュ結合 | 小さい表がメモリに収まるか |
| 範囲検索・並べ替え | B-tree インデックス | 書き込みは遅くなる |
| 上位 k 件 | ヒープ | k が大きければ並べ替えのほうが速い |
| 再実行できる取り込み | 追記型ログ＋オフセット | 処理済みオフセットの保存場所 |
| 一部の列だけ大量に集計 | 列指向（Parquet・DuckDB） | 1 行単位の更新は苦手 |
| 大量の書き込み | LSM ツリー | 読み込みとコンパクションの負荷 |
| 「確実にない」を安く判定 | Bloom フィルタ | 偽陽性がある。削除できない |
| ユニーク数を安く数える | HyperLogLog | 誤差がある。統合はできる |
| ベクトルの近傍探索 | HNSW | 近似なので取りこぼしがある |

## まとめ

- データベースやデータ処理ツールの速さ・正確さの違いは、多くが中のデータ構造で説明できる
- 基本の配列・ハッシュ表・B-tree・ヒープ・ログは、重複排除、JOIN、インデックス、上位 k 件、再実行可能な取り込みにそのまま対応する
- データエンジニアリングでは、列指向・LSM ツリー・Bloom フィルタ・HyperLogLog・HNSW のように、**読み書きの偏りや「近似でよい」ことを前提に作られた構造**が多い
- どの構造も何かを得る代わりに何かを諦めている。その交換条件を知っていれば、ツールの選定や性能問題の切り分けで迷いにくくなる

## 関連記事

- [AI エンジニアこそデータエンジニアリングを学ぶべき理由：RAG のデモが本番で崩れるところ](/blogs/posts/2026/11/data-engineering-for-ai-engineers/)
- [DuckDB・Apache Arrow・Parquet の関係を整理する：列指向エコシステムの全体像](/blogs/posts/2026/03/duckdb-columnar-arrow/)
- [Apache Iceberg 入門：データレイクを「テーブル」にする仕組みと DuckDB との関係](/blogs/posts/2026/10/apache-iceberg-duckdb/)
- [Claude Code で大量データを扱うなら SQLite/DuckDB を使おう](/blogs/posts/2026/03/claude-code-sqlite-duckdb/)
- [Agentic RAG の 3 つのパターン：Router、Self-Correction、Multi-step Retrieval](/blogs/posts/2026/06/agentic-rag-patterns/)
- [AI エージェントのためのデータ基盤：レイクハウスを土台に「意味・費用・権限・取り消し」を設計する](/blogs/posts/2026/10/ai-agent-data-platform/)
- wiki：[列指向ストレージ](/blogs/wiki/concepts/columnar-storage/) / [RAG](/blogs/wiki/concepts/rag/) / [DuckDB](/blogs/wiki/tools/duckdb/)
