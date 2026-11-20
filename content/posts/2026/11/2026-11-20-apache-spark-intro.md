---
title: "Apache Spark 入門：AI エンジニアのための分散処理の基本と、使わなくてよい場面"
date: 2026-11-20
lastmod: 2026-11-20
slug: "apache-spark-intro"
draft: false
categories: ["データベース"]
tags: ["Apache Spark", "データエンジニアリング", "データ基盤", "データレイク", "duckdb"]
---

## はじめに

[AI エンジニアこそデータエンジニアリングを学ぶべき理由](/blogs/posts/2026/11/data-engineering-for-ai-engineers/)では、データエンジニアリングのロードマップに並ぶ道具を「それぞれが解く問題」で整理しました。そこで Apache Spark は「大規模なデータをどう計算するか」を解く道具として登場します。

この記事は、その Spark の入門編です。RAG やエージェントを作るアプリケーション側のエンジニアが、データ基盤チームの会話についていける程度を目標に、次の順で説明します。

- Spark が解く問題と、クラスター上での動き方（ドライバーとエグゼキューター）
- 遅延評価、DataFrame と Spark SQL、パーティションとシャッフル
- Hadoop MapReduce との関係（Spark は何を変えたのか）
- 手元で動く PySpark の小さな例
- Structured Streaming の概要
- データレイク、Apache Iceberg、Databricks との関係
- **Spark を使わなくてよい場面**（DuckDB、Polars、PostgreSQL で足りるケース）

バージョンや機能は、2026 年 11 月時点の公式ドキュメントとリリースノートで確認しています。

## 用語とプロダクト

先に、この記事に出てくる用語とプロダクトをまとめておきます。

| 用語・プロダクト | 意味 |
|---|---|
| Apache Spark | 複数のマシンにデータと計算を分散させて処理するエンジン。Python・SQL・Scala・Java などから使える |
| PySpark | Spark の Python API。`pip install pyspark` で入る |
| ドライバー（Driver） | ユーザーのプログラムを動かし、処理を計画してエグゼキューターに配るプロセス |
| エグゼキューター（Executor） | ワーカーノード上で実際にデータを処理するプロセス |
| クラスターマネージャー | マシン資源を割り当てる仕組み。Spark 付属の Standalone、YARN、Kubernetes など |
| DataFrame | 列名と型を持つ表形式の分散データ。pandas の DataFrame に似た操作ができる |
| パーティション | DataFrame を分割した単位。1 パーティションを 1 タスクが処理する |
| タスク | 1 パーティション分の処理。エグゼキューターが実行する最小の単位 |
| ステージ | シャッフルを境に区切られた、タスクのまとまり |
| Spark UI | ドライバーが立ち上げる Web 画面。ジョブ・ステージ・タスクの所要時間などを確認できる |
| シャッフル | `groupBy` や `join` のために、同じキーの行を同じパーティションへ集め直す処理 |
| 遅延評価 | 変換を書いた時点では実行せず、結果が必要になったときにまとめて実行する仕組み |
| Structured Streaming | DataFrame の API のまま、流れ続けるデータを処理する Spark の機能 |
| Hadoop MapReduce | 処理を map と reduce の 2 段で書く分散処理のモデルと、その Hadoop での実装。Spark の前の世代の計算エンジン |
| HDFS / YARN | Hadoop の分散ファイルシステムと、クラスターの資源管理の仕組み |
| [Apache Iceberg](/blogs/posts/2026/10/apache-iceberg-duckdb/) | データレイク上のファイル群を 1 つのテーブルとして扱うためのオープンなテーブルフォーマット |
| Databricks | Spark の開発者たちが創業した会社と、その Spark ベースのデータ基盤サービス |

## Spark が解く問題

Spark が解くのは「**1 台のマシンに載らない、または 1 台では時間がかかりすぎるデータを、どう計算するか**」という問題です。

数 TB のログを集計したい、毎晩数十億行のテーブルを変換したい、といった場面を考えます。1 台のマシンでは、メモリにもディスクにも収まらないか、収まっても処理が終わるまで何時間もかかります。そこでデータを小さな塊（パーティション）に分け、たくさんのマシンで並列に処理します。

ただし、分散処理を自前で書くのは大変です。どのマシンにどの塊を割り当てるか、途中で 1 台落ちたらどう再実行するか、集計のためにマシン間でデータをどう受け渡すか。Spark はこうした部分を引き受け、利用者には「表に対する操作」を書くだけの API を提供します。

Spark は 2009 年に UC Berkeley の AMPLab で始まった研究プロジェクトで、その後 Apache Software Foundation に寄贈されました。現在の最新版は 2026 年 10 月 30 日に出た **Spark 4.3.0** です。4.3 から機能リリースを四半期ごとに出す方針に切り替わっています。

## Spark のドライバーとエグゼキューター

Spark のアプリケーションは、1 つの**ドライバー**と、複数の**エグゼキューター**で動きます。

![Spark の構成を示す図。上段では、ドライバー（SparkSession）がクラスターマネージャーに資源を要求し、クラスターマネージャーがワーカーノード上にエグゼキューターを起動し、ドライバーがエグゼキューターにタスクを配って結果を受け取る流れを示している。下段では、ステージ 1 で 3 つのパーティションがそれぞれ読み込み・filter・部分集計を行い、シャッフルで同じキーの行が同じパーティションに集められ、ステージ 2 でキーごとに最終集計される様子を示している](/blogs/images/apache-spark-intro-architecture.png)

- **ドライバー**は、利用者が書いた PySpark のプログラムを動かすプロセスです。`SparkSession` を作るのもここです。DataFrame に対する操作を受け取ると、それを実行計画に変換し、ステージとタスクに分けてエグゼキューターに配ります。
- **エグゼキューター**は、ワーカーノード上で動くプロセスです。割り当てられたタスク（1 パーティション分の処理）を実行し、結果をドライバーに返したり、次のステージのためにディスクへ書き出したりします。
- **クラスターマネージャー**は、エグゼキューターを起動するためのマシン資源を用意します。Spark 付属の Standalone のほか、YARN や Kubernetes が使えます。

手元の PC で試すときは `local[*]` を指定します。1 つのプロセスがドライバーとエグゼキューターの両方の役割を担い、CPU のコア数だけ並列に処理します。書いたコードはクラスターでもそのまま動くので、小さく試してから大きな環境へ持っていけます。

## Spark の遅延評価：書いた時点では動かない

Spark の DataFrame の操作は、**変換（transformation）** と **アクション（action）** に分かれます。

| 種類 | 例 | 実行されるか |
|---|---|---|
| 変換 | `select`、`filter`、`withColumn`、`groupBy().agg()`、`join` | その場では実行されない。新しい DataFrame（処理の計画）を返すだけ |
| アクション | `show`、`count`、`collect`、`write` | ここで初めて、溜まった変換がまとめて実行される |

変換を書いても、Spark は計画を積み上げるだけです。アクションが呼ばれると、オプティマイザー（Catalyst）が計画全体を見て最適化してから実行します。たとえば、不要な列を読まない、フィルターをできるだけ読み込みの近くに寄せる、といった処理です。

pandas に慣れていると、フィルターや列の追加を書いた行で処理が終わったように感じます。しかし Spark ではその行は一瞬で返り、時間がかかるのは `show()` や `write` の行です。エラーもアクションの行で初めて表に出ることがあります。どこで重い処理が走るかを意識しておくと、デバッグで迷いにくくなります。

## DataFrame と Spark SQL

Spark の処理は、DataFrame の API でも SQL でも書けます。どちらも同じオプティマイザーを通り、同じ実行計画になります。

- **DataFrame API**：Python のコードとして書きます。関数に分けたり、テストを書いたりしやすくなります。
- **Spark SQL**：DataFrame を一時ビューとして登録し、SQL で問い合わせます。SQL に慣れた人やデータアナリストと共有しやすくなります。

Spark 4.0 からは、標準 SQL に近い挙動をする ANSI モードがデフォルトになりました。たとえば数値に変換できない文字列を `CAST` すると、以前は黙って `NULL` になっていたところが、`CAST_INVALID_INPUT` エラーになります。`NULL` で受け流したいときは `try_cast` を使います。古いジョブを 4.x に移すときに引っかかりやすい変更です。

## パーティションとシャッフル：Spark が遅くなる原因

Spark の性能を左右するのが、パーティションとシャッフルです。

DataFrame はパーティションに分割されていて、1 パーティションを 1 タスクが処理します。`filter` や `withColumn` のように、各行を他の行と関係なく処理できる変換（狭い変換）は、パーティションの中だけで完結します。マシン間でデータを動かす必要がないので速く進みます。

一方、`groupBy` で集計する、`join` で 2 つの表を結合する、といった広い変換では、同じキーを持つ行を同じパーティションに集めなければなりません。これが**シャッフル**です。各エグゼキューターが中間データをディスクに書き、ネットワーク越しに他のエグゼキューターが読みにいきます。上の図の下段のように、シャッフルを境に処理は**ステージ**に分かれます。

シャッフルはディスクとネットワークを使うので、Spark のジョブで最も重くなりがちな処理です。Spark ジョブが遅いときは、まずシャッフルを疑います。

- 不要な列や行を、シャッフルの前に `select` や `filter` で落としておく
- 小さい表との `join` は、小さい表を全エグゼキューターに配るブロードキャスト結合にする（Spark は小さい表なら自動で選ぶ）
- 特定のキーに行が偏る（スキュー）と、そのキーを担当するタスクだけが終わらない。Spark UI でタスクごとの所要時間のばらつきを確認する

シャッフル後のパーティション数は `spark.sql.shuffle.partitions`（デフォルト 200）で決まります。ただし Spark 3.2 以降は Adaptive Query Execution（AQE）がデフォルトで有効です。AQE は実行時のデータ量を見て小さすぎるパーティションをまとめたり、偏ったパーティションを分割したりしてくれます。最初はデフォルトのまま動かし、Spark UI で遅いステージを見つけてから調整するのが現実的です。

## Hadoop MapReduce との関係

Spark は、Hadoop MapReduce の弱点を解くために作られました。仕組みの上では、MapReduce を一般化したものと見ることができます。

MapReduce は、処理を **map**（各レコードを変換してキーと値の組を出す）と **reduce**（同じキーの値をまとめて集計する）の 2 段で書くモデルです。2 段のあいだでは、同じキーの組を同じ reducer に集める**シャッフル**が走ります。Hadoop の MapReduce は 1 つのジョブの出力を HDFS（分散ファイルシステム）に書き出します。そのため、複数のジョブをつなぐ処理では、ジョブの区切りごとにディスクを往復します。

この往復が特に重くなるのが、同じデータを何度も読み直す処理です。機械学習の反復計算や、同じデータに次々と問い合わせる対話的な分析がこれに当たります。Spark はここを狙って生まれました。中間データをメモリに置いたまま次の処理へ渡せるようにしたのが、初期の論文の主題です。2010 年の HotCloud 論文で RDD（Resilient Distributed Datasets）という抽象が導入され、2012 年の NSDI 論文で RDD を主題に詳しく論じられました。

この記事で説明してきた仕組みは、MapReduce と次のように対応します。

| MapReduce | Spark |
|---|---|
| map | 狭い変換（`filter`、`select`、`withColumn` など。シャッフルが要らない） |
| map と reduce のあいだのシャッフル | シャッフル（考え方は同じ） |
| reduce | 広い変換（`groupBy().agg()`、`join` など） |
| 1 ジョブは map → reduce の 2 段で固定。長い処理はジョブを連ねる | 1 つのジョブが何段にも連なる DAG になり、シャッフルの位置でステージが切れる |
| 障害時は、ディスクに残った入力や map の出力を使って、失敗したタスクを再実行する | 障害時は、系譜（lineage：どの入力からどの変換で作ったか）をたどり、失われたパーティションだけを計算し直す |

前の節の「シャッフルを境に処理はステージに分かれる」は、MapReduce の map と reduce の境目を、1 つのジョブの中に何回でも置けるようにしたものだと読めます。遅延評価で処理全体を見てから実行計画を立てられるのも、2 段で固定された MapReduce にはない点です。

その後、Hadoop の利用環境では、計算エンジンの役割が MapReduce から Spark へ移っていきました。Spark は HDFS のデータを読め、Hadoop のクラスターマネージャーである YARN の上でも動きます。そのため、保存（HDFS）と資源管理（YARN）は Hadoop のまま、計算だけ Spark に替える構成が広く使われました。今は HDFS の代わりに S3 などのオブジェクトストレージを使い、その上に [Apache Iceberg](/blogs/posts/2026/10/apache-iceberg-duckdb/) などのテーブルフォーマットを置く構成が増えています（後述）。

## PySpark を手元で動かす

PySpark は `pip` で入ります。Spark 4.3 は Java 17／21／25 と Python 3.11 以上で動くので、事前に JDK を入れておきます。`java -version` で 17 以上が表示されれば準備はできています。

```bash
java -version
python3 -m venv .venv
source .venv/bin/activate
pip install pyspark
```

注文データを DataFrame にして、カテゴリごとに売上を集計する例です。

```python
from pyspark.sql import SparkSession
from pyspark.sql import functions as F

spark = (
    SparkSession.builder
    .appName("spark-intro")
    .master("local[*]")  # 手元の CPU コアを全部使う
    .getOrCreate()
)

orders = spark.createDataFrame(
    [
        (1, "book", 1200, "2026-11-01"),
        (2, "food", 800, "2026-11-01"),
        (3, "book", 3000, "2026-11-02"),
        (4, "game", 6500, "2026-11-02"),
        (5, "food", 450, "2026-11-03"),
    ],
    ["order_id", "category", "amount", "order_date"],
)

# ここまでは「変換」なので、まだ何も計算されない
summary = (
    orders
    .filter(F.col("amount") >= 500)
    .groupBy("category")
    .agg(
        F.count("*").alias("orders"),
        F.sum("amount").alias("total"),
    )
    .orderBy(F.desc("total"))
)

summary.explain()  # 実行計画を表示（Exchange がシャッフル）
summary.show()     # アクション：ここで初めて実行される
```

`show()` の結果は次のようになります。

```text
+--------+------+-----+
|category|orders|total|
+--------+------+-----+
|    game|     1| 6500|
|    book|     2| 4200|
|    food|     1|  800|
+--------+------+-----+
```

`explain()` は物理実行計画を表示します。Spark 4.3.0 で実行すると、次のような計画になります（下から上へ読みます）。

```text
== Physical Plan ==
AdaptiveSparkPlan isFinalPlan=false
+- Sort [total#5L DESC NULLS LAST], true, 0
   +- Exchange rangepartitioning(total#5L DESC NULLS LAST, 200), ENSURE_REQUIREMENTS, [plan_id=26]
      +- HashAggregate(keys=[category#1], functions=[count(1), sum(amount#2L)])
         +- Exchange hashpartitioning(category#1, 200), ENSURE_REQUIREMENTS, [plan_id=23]
            +- HashAggregate(keys=[category#1], functions=[partial_count(1), partial_sum(amount#2L)])
               +- Project [category#1, amount#2L]
                  +- Filter (isnotnull(amount#2L) AND (amount#2L >= 500))
                     +- Scan ExistingRDD[order_id#0L,category#1,amount#2L,order_date#3]
```

`#5L` や `plan_id` の番号は実行のたびに変わります。読みどころは次の 3 点です。

- **`Exchange`**：シャッフルです。`hashpartitioning(category#1, 200)` は `groupBy` のために category ごとに行を集め直すもの、`rangepartitioning` は `orderBy` で並べ替えるためのものです
- **`HashAggregate` が 2 回**：各パーティションで部分集計（`partial_count`、`partial_sum`）してからシャッフルし、最後にまとめて集計しています。シャッフルで動くデータ量を減らす工夫で、図の下段がこの流れにあたります
- **`Project`**：`order_id` と `order_date` がここで落とされています。不要な列を早めに捨てる最適化です

同じ集計は Spark SQL でも書けます。以降の例は、先ほどの `spark` と `F` をそのまま使います。

```python
orders.createOrReplaceTempView("orders")

spark.sql("""
    SELECT category, COUNT(*) AS orders, SUM(amount) AS total
    FROM orders
    WHERE amount >= 500
    GROUP BY category
    ORDER BY total DESC
""").show()
```

実際の業務では、メモリ上のリストではなく、データレイク上の Parquet ファイルなどを読み書きします。

```python
logs = spark.read.parquet("s3a://my-bucket/logs/2026/11/")
(
    logs.filter(F.col("status") >= 500)
    .groupBy("path")
    .count()
    .write.mode("overwrite")
    .parquet("s3a://my-bucket/reports/errors/")
)
```

S3 などのクラウドストレージを読むには、追加ライブラリ（公式ドキュメントでは `hadoop-cloud` モジュールを案内しており、S3 用のコネクターは `hadoop-aws` に含まれます）と認証の設定が別途必要です。ここではコードの形だけ示しています。

実行中は、ドライバーが Spark UI（ローカルなら通常 `http://localhost:4040`）を立ち上げます。ジョブ、ステージ、タスクごとの所要時間やシャッフルの量が見られるので、遅い処理を探すときの入口になります。

## Spark Structured Streaming の概要

Spark にはバッチ処理だけでなく、流れ続けるデータを扱う **Structured Streaming** もあります。特徴は、ストリームを「行が追加され続ける表」とみなし、バッチと同じ DataFrame の API で処理を書ける点です。

```python
events = (
    spark.readStream
    .format("rate")            # 動作確認用に、毎秒行を生成するソース
    .option("rowsPerSecond", 10)
    .load()
)

counts = events.groupBy(F.window("timestamp", "10 seconds")).count()

query = (
    counts.writeStream
    .outputMode("update")
    .format("console")
    .option("checkpointLocation", "./checkpoints/rate-demo")
    .start()
)
query.awaitTermination()
```

実際には `rate` の代わりに Kafka などをソースにし、結果をテーブルに書き込みます。`checkpointLocation` に処理済みの位置と集計の状態を保存しておくことで、ジョブが落ちて再起動しても続きから処理できます。[AI エンジニアこそデータエンジニアリングを学ぶべき理由](/blogs/posts/2026/11/data-engineering-for-ai-engineers/)で挙げた「同期処理が途中で落ちて再実行したとき、重複データが生まれないか」という問いに、仕組みの側から答える部分です。手元で試したときは、Ctrl+C で止めます。

デフォルトは、短い間隔で小さなバッチを繰り返すマイクロバッチ方式です。Spark 4.1 では、1 秒未満の遅延で処理する Real-Time Mode が入りました。4.3 では集計や重複排除のような状態を持つ処理でも、100 ミリ秒程度の遅延で動かせるようになっています。

Spark 4.1 では Spark Declarative Pipelines も入りました。データセットとクエリを宣言すると、依存関係の順序づけ、並列化、チェックポイント、リトライを Spark が面倒を見るフレームワークです。4.3 では、レコードの変更履歴をバージョン付きの行として残す SCD Type 2 にも対応しました。パイプラインの運用を Spark 側に寄せていく流れを示す機能です。

## データレイク、Iceberg、Databricks との関係

Spark はデータを保存する製品ではなく、**計算エンジン**です。データは別の場所にあり、Spark はそれを読んで計算し、書き戻します。そのため、周辺の製品との関係を押さえておくと全体像がつかみやすくなります。

- **データレイク**：S3 などのオブジェクトストレージに、Parquet などのファイルとしてデータを置く構成です。Spark は昔から、ここを読み書きする代表的なエンジンでした。
- **Apache Iceberg**：ファイルの集まりに、テーブルとしてのスキーマ、スナップショット、トランザクションを与えるテーブルフォーマットです。Spark は Iceberg の主要なエンジンの 1 つで、Spark から Iceberg テーブルに対して `MERGE INTO` や過去のスナップショットの参照ができます。仕組みは [Apache Iceberg 入門](/blogs/posts/2026/10/apache-iceberg-duckdb/) と [wiki の Apache Iceberg](/blogs/wiki/tools/apache-iceberg/) にまとめています。
- **レイクハウス**：データレイクとテーブルフォーマットを組み合わせ、DWH（データウェアハウス）のように扱う構成です。Spark はその上で変換や集計を担う代表的な計算エンジンです（[wiki のレイクハウス](/blogs/wiki/concepts/lakehouse/)）。
- **Databricks**：Spark を最初に作った開発者たちが 2013 年に創業した会社で、Spark を中心にしたデータ基盤をクラウドサービスとして提供しています。テーブルフォーマットは自社発の Delta Lake を中心にしつつ、Iceberg にも対応しています。Spark そのものはオープンソースなので、Databricks を使わなくても、Amazon EMR や Google Cloud の Dataproc、自前の Kubernetes などで動かせます。

## Spark を使わなくてよい場面：DuckDB・Polars・PostgreSQL との使い分け

[AI エンジニアこそデータエンジニアリングを学ぶべき理由](/blogs/posts/2026/11/data-engineering-for-ai-engineers/)では、「Python のスクリプトと PostgreSQL で済む問題なのに、先に Kafka、Spark、Kubernetes を一式揃えてしまう」という誤りを取り上げました。Spark の入門記事で一番伝えたいのは、実はここです。

Spark には、ドライバーとエグゼキューターの起動、タスクの配布、シャッフルといった分散処理のための固定費があります。データが 1 台に収まるなら、この固定費を払う理由はほとんどありません。

| データの規模・用途 | まず検討する道具 |
|---|---|
| 業務システムの DB に入っている数 GB 程度のデータ | PostgreSQL などの RDB にそのまま SQL を投げる |
| 数 GB〜数百 GB の Parquet や CSV をまとめて集計する | [DuckDB](/blogs/wiki/tools/duckdb/)。1 台の上で列指向・並列に処理する |
| Python の中で DataFrame として加工する | Polars。Rust 製で、遅延評価とマルチスレッド処理に対応している |
| 数 TB 以上を毎日変換する、多数のジョブを共有のクラスターで回す | Spark |

最近の 1 台のマシンは、数十コアと数百 GB のメモリを持てます。[列指向ストレージ](/blogs/wiki/concepts/columnar-storage/)の Parquet を DuckDB や Polars で読めば、数億行の集計でも 1 台で数秒から数分で終わることが珍しくありません（DuckDB・Arrow・Parquet の関係は[列指向エコシステムの全体像](/blogs/posts/2026/03/duckdb-columnar-arrow/)で整理しています）。

Spark が必要になってくるのは、次のような状況です。

- データが 1 台のディスクやメモリに収まらない規模になった
- 処理時間を、マシンを足すことで縮めたい
- すでに組織に Spark（あるいは Databricks や EMR）の基盤があり、ジョブをそこに載せるほうが運用が楽
- ストリーム処理とバッチ処理を同じ API と同じ基盤で扱いたい

AI エンジニアの立場でいえば、RAG のための文書の前処理や埋め込みの作成は、多くの場合 Python と DuckDB で始められます。データ基盤チームが Spark でテーブルを作っているなら、その出力（Iceberg や Parquet のテーブル）を DuckDB から読む、という分担もできます。

## まとめ

- Spark は、1 台に載らないデータをパーティションに分け、多数のマシンで並列に計算するエンジン。2026 年 11 月時点の最新は 4.3.0
- ドライバーが処理を計画してタスクを配り、エグゼキューターがパーティションごとに実行する
- DataFrame の操作は遅延評価で、アクションの時点で最適化されてからまとめて実行される
- `groupBy` や `join` で起きるシャッフルが最も重い。前もって行や列を減らし、Spark UI で遅いステージを探す
- Structured Streaming は、ストリームをバッチと同じ DataFrame の API で扱える
- Spark は計算エンジンで、データは Iceberg などのテーブルとしてデータレイクに置く。Databricks は Spark を中心にしたマネージドサービス
- **データが 1 台に収まるなら、DuckDB、Polars、PostgreSQL で十分なことが多い。Spark は必要になってから導入すればよい**

## 関連記事

- [AI エンジニアこそデータエンジニアリングを学ぶべき理由：RAG のデモが本番で崩れるところ](/blogs/posts/2026/11/data-engineering-for-ai-engineers/)
- [Apache Iceberg 入門：データレイクを「テーブル」にする仕組みと DuckDB との関係](/blogs/posts/2026/10/apache-iceberg-duckdb/)
- [Iceberg と DuckLake の先へ：2026 年に注目したいレイクハウスの技術とプロダクト](/blogs/posts/2026/10/lakehouse-ecosystem-2026/)
- [Redshift か、S3 ＋ Iceberg のレイクハウスか：DWH とオープンテーブルフォーマットの選び方](/blogs/posts/2026/10/redshift-vs-lakehouse/)
- [DuckLake 入門：メタデータを SQL データベースに置くレイクハウスフォーマットと Iceberg との違い](/blogs/posts/2026/10/ducklake-sql-lakehouse/)
- [AI エージェントのためのデータ基盤：レイクハウスを土台に「意味・費用・権限・取り消し」を設計する](/blogs/posts/2026/10/ai-agent-data-platform/)
- [DuckDB・Apache Arrow・Parquetの関係を整理する：列指向エコシステムの全体像](/blogs/posts/2026/03/duckdb-columnar-arrow/)
