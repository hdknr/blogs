---
title: "Apache Spark"
description: "1 台に載らないデータをパーティションに分け、多数のマシンで並列に計算する分散処理エンジン。Hadoop MapReduce の後継で、データレイク・レイクハウスの代表的な計算エンジン"
date: 2026-11-20
lastmod: 2026-11-20
aliases: ["Spark", "PySpark", "Spark SQL", "Structured Streaming", "Spark Declarative Pipelines"]
related_posts:
  - "/posts/2026/11/apache-spark-intro/"
  - "/posts/2026/11/data-engineering-for-ai-engineers/"
tags: ["Apache Spark", "データエンジニアリング", "データ基盤", "データレイク"]
---

## 概要

Apache Spark は、1 台のマシンに載らない、または 1 台では時間がかかりすぎるデータを、パーティションに分けて多数のマシンで並列に計算するエンジン。DataFrame の API か SQL で「表に対する操作」を書くと、タスクの配布・障害時の再実行・マシン間のデータ受け渡しを Spark が引き受ける。データを保存する製品ではなく**計算エンジン**で、データはデータレイクや [Apache Iceberg](/blogs/wiki/tools/apache-iceberg/) のテーブルに置く。

## 詳細

### 動き方

| 部品・概念 | 役割 |
|---|---|
| ドライバー | 利用者のプログラムを動かし、実行計画を作ってタスクを配る |
| エグゼキューター | ワーカーノード上で、1 パーティション分の処理（タスク）を実行する |
| クラスターマネージャー | Standalone・YARN・Kubernetes など。エグゼキューターの資源を用意する |
| 遅延評価 | 変換（`filter`、`groupBy` など）は計画を積むだけ。アクション（`show`、`write`）の時点でオプティマイザー（Catalyst）が全体を最適化して実行する |
| シャッフル | `groupBy` や `join` で同じキーの行を同じパーティションへ集め直す処理。ディスクとネットワークを使うので最も重い。ステージはシャッフルを境に切れる |

遅いジョブはまずシャッフルを疑う。シャッフルの前に行と列を落とす、小さい表はブロードキャスト結合にする、キーの偏り（スキュー）を Spark UI で確かめる。Spark 3.2 以降は AQE（Adaptive Query Execution）が既定で有効で、実行時にパーティションをまとめたり分割したりする。Spark 4.0 からは ANSI モードが既定になり、変換できない値の `CAST` は `NULL` ではなくエラーになる。

### Hadoop MapReduce との関係

Spark は 2009 年に UC Berkeley の AMPLab で、MapReduce が苦手な反復計算（機械学習）と対話的な分析を速くするために始まった。MapReduce はジョブの区切りごとに中間結果を分散ファイルシステムへ書き出すが、Spark は中間データをメモリに置いたまま次の処理へ渡せる（2010 年の HotCloud 論文で RDD を導入し、2012 年の NSDI 論文で詳述）。

仕組みの上では MapReduce の一般化と見られる。map は狭い変換、reduce は広い変換に当たり、map と reduce の境目のシャッフルを 1 つのジョブの中に何回でも置ける（DAG のステージ）。障害時は、ディスクの中間結果から再実行する代わりに、系譜（lineage）をたどって失われたパーティションだけを計算し直す。Hadoop の環境では、保存（HDFS）と資源管理（YARN）はそのままで、計算エンジンだけが MapReduce から Spark へ移った。

### ストリーム処理

Structured Streaming は、ストリームを「行が追加され続ける表」とみなし、バッチと同じ DataFrame の API で書ける。`checkpointLocation` に処理済みの位置と状態を保存するので、落ちても続きから再開できる。既定はマイクロバッチで、4.1 で 1 秒未満の遅延の Real-Time Mode が入った。4.1 では、データセットとクエリを宣言すると依存の順序・チェックポイント・リトライを Spark が受け持つ Declarative Pipelines も入っている。

### 周辺の製品

- **データレイク / [レイクハウス](/blogs/wiki/concepts/lakehouse/)**：Spark は S3 上の Parquet や Iceberg テーブルを読み書きする代表的なエンジン。Iceberg には `MERGE INTO` やスナップショットの参照ができる
- **Databricks**：Spark の開発者たちが 2013 年に創業した会社と、Spark を中心にしたクラウドのデータ基盤。Spark 自体はオープンソースなので、Amazon EMR、Google Cloud の Dataproc、自前の Kubernetes でも動く

### 使わなくてよい場面

分散処理には固定費（エグゼキューターの起動、タスクの配布、シャッフル）がある。データが 1 台に収まるなら払う理由は薄い（[オーバーエンジニアリング](/blogs/wiki/concepts/overengineering/)）。

| データの規模・用途 | まず検討する道具 |
|---|---|
| 業務 DB の数 GB | PostgreSQL などに SQL を投げる |
| 数 GB〜数百 GB の Parquet・CSV の集計 | [DuckDB](/blogs/wiki/tools/duckdb/) |
| Python の中の DataFrame 加工 | Polars |
| 数 TB 以上を毎日変換、多数のジョブを共有クラスターで回す | Spark |

RAG の前処理や埋め込みの作成は、多くの場合 Python と DuckDB で始められる。基盤チームが Spark で作ったテーブル（Iceberg や Parquet）を DuckDB から読む分担もできる。

## 関連ページ

- [Apache Iceberg](/blogs/wiki/tools/apache-iceberg/) — Spark が読み書きする代表的なテーブルフォーマット
- [レイクハウス](/blogs/wiki/concepts/lakehouse/) — Spark が計算を担う構成
- [DuckDB](/blogs/wiki/tools/duckdb/) — データが 1 台に収まるときの選択肢
- [列指向ストレージ](/blogs/wiki/concepts/columnar-storage/) — Parquet の背景
- [Apache Kafka](/blogs/wiki/tools/apache-kafka/) — Structured Streaming の代表的な入力元
- [Apache Airflow](/blogs/wiki/tools/apache-airflow/) — Spark のジョブを順番どおりに起動・管理する

## ソース記事

- [Apache Spark 入門：AI エンジニアのための分散処理の基本と、使わなくてよい場面](/blogs/posts/2026/11/apache-spark-intro/) — 2026-11-20
- [AI エンジニアこそデータエンジニアリングを学ぶべき理由：RAG のデモが本番で崩れるところ](/blogs/posts/2026/11/data-engineering-for-ai-engineers/) — 2026-11-19
