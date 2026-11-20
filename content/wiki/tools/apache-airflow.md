---
title: "Apache Airflow"
description: "複数の処理の依存関係・スケジュール・再試行・履歴を、Python で書いた DAG として管理するワークフローのオーケストレーター"
date: 2026-11-20
lastmod: 2026-11-20
aliases: ["Airflow", "Airflow 3", "DAG", "TaskFlow API", "Cloud Composer", "Amazon MWAA", "CeleryExecutor"]
related_posts:
  - "/posts/2026/11/apache-airflow-intro/"
  - "/posts/2026/11/data-engineering-for-ai-engineers/"
tags: ["Apache Airflow", "データエンジニアリング", "データ基盤", "オーケストレーション"]
---

## 概要

Apache Airflow は、バッチのワークフローをオーケストレーションするためのプラットフォーム。cron が「決まった時刻にコマンドを起動する」だけなのに対し、処理間の依存関係、失敗時の再試行、実行履歴の可視化、担当期間を指定した過去の再実行（バックフィル）までを受け持つ。ワークフローは Python のコードとして書くので、Git で管理・レビュー・テストできる。

## 詳細

### DAG

ワークフローは **DAG**（Directed Acyclic Graph、有向非巡回グラフ）で表す。タスクを頂点、「このタスクの後にあのタスク」という依存関係を矢印にしたグラフで、枝分かれも合流もできるが、循環は認めない。循環を禁じるのは実行順を必ず決められるようにするためで、既定では上流がすべて成功したタスクから実行される（trigger rule `all_success`）。繰り返しは、スケジュールでの定期起動や動的タスクマッピングで表してきた。3.4.0 からは、タスクグループを実行時に決まる回数だけ繰り返す Task Loops（`.loop()`）もある。

タスクは、既製の**オペレーター**か、関数に `@task` を付ける **TaskFlow API** で書く。TaskFlow API では `load(chunk(extract()))` のような関数呼び出しで依存関係が決まる。Airflow 3 では import が `from airflow.sdk import dag, task` になった。

### 構成部品（Airflow 3）

| 部品 | 役割 |
|---|---|
| Scheduler | 実行すべきタスクを決めて Executor に渡す |
| Executor | タスクをどこでどう実行するかの設定。既定は `LocalExecutor`。`CeleryExecutor`、`KubernetesExecutor` などに切り替えられる |
| Dag processor | DAG ファイルを解析してメタデータ DB に保存する |
| API server | Web UI と REST API。ワーカーは Execution API 経由で状態を報告する |
| メタデータ DB | DAG・タスク・実行の状態を保存する |

### 担当期間・再実行・冪等性

DAG run ごとに担当期間（`data_interval_start` / `data_interval_end`）を持つ。処理対象を「現在時刻」ではなく「担当期間」で絞っておくのが、バックフィル（`airflow backfill create`）の前提になる。Airflow 3 では `catchup` の既定が `False`。

再試行やバックフィルを安全に使えるかは、タスクが**冪等**かで決まる。追記ではなく upsert か「期間ごとに消してから書く」にし、メール送信などの副作用は分離する。冪等性は Airflow の機能ではなく、DAG を書く側の約束。XCom は小さな値向けで、データ本体はストレージに置いてパスだけを渡す。

### Celery などのタスクキューとの違い

[Celery](/blogs/wiki/tools/celery/) はタスクをブローカー経由でワーカーに配る層、Airflow はワークフローの順序・期間・履歴を管理する層。

| 観点 | Celery | Airflow |
|---|---|---|
| 起点 | アプリのコードが投げる（イベント駆動） | スケジュールやデータの到着 |
| 粒度 | 小さく大量（メール 1 通、画像 1 枚） | バッチの 1 工程 |
| 時間の扱い | 担当期間の概念なし。beat は定期的に投げるだけ | DAG run ごとに担当期間 |
| 履歴と再実行 | 過去の期間を流し直す機能は標準ではない | タスクのクリア、バックフィル |
| 遅延 | すぐ実行。リクエストの裏の処理向き | Scheduler を経るので数秒かかることがある |

RAG なら、文書 1 件ごとの再インデックスは Celery、毎日の全体同期と取りこぼした日の埋め直しは Airflow、という分担がよくある。`CeleryExecutor` を使えば、Airflow が決めたタスクを Celery のワーカーで実行できる。

### 導入の目安と代替

処理が 1〜2 本で依存がなく、過去をやり直す必要もないなら cron と Python スクリプトで足りる（[オーバーエンジニアリング](/blogs/wiki/concepts/overengineering/)）。依存が時刻合わせで管理できなくなったとき、失敗に気づけない・過去をやり直せないことが実害になったときが導入の目安。cron の段階から「担当期間を引数で受け取る」「何度実行しても同じ結果」に書いておくと、そのまま Airflow のタスクにできる。

| ツール | 定義の中心 |
|---|---|
| Airflow | タスクと依存関係（DAG） |
| Dagster | 作られるデータ（アセット）。リネージと鮮度を扱いやすく、[dbt](/blogs/wiki/tools/dbt/) とよく組む |
| Prefect | Python の関数（`@flow` / `@task`） |

マネージド版には Cloud Composer（Google Cloud）と Amazon MWAA がある。最新の Airflow への対応には時間差がある。

## 関連ページ

- [Celery](/blogs/wiki/tools/celery/) — 下位の実行層として組み合わせられるタスクキュー
- [dbt](/blogs/wiki/tools/dbt/) — Airflow から起動されることの多い変換ツール
- [Apache Spark](/blogs/wiki/tools/apache-spark/) — Airflow が起動する重い計算ジョブ
- [Apache Kafka](/blogs/wiki/tools/apache-kafka/) — 定時バッチではなくイベントで流す場合
- [沈黙する失敗](/blogs/wiki/concepts/silent-failure/) — 夜間の処理が落ちても気づけない問題
- [RAG](/blogs/wiki/concepts/rag/) — ナレッジベースの定期同期の対象

## ソース記事

- [Apache Airflow 3 入門：AI エンジニアのための DAG・スケジューラー・再実行の基本](/blogs/posts/2026/11/apache-airflow-intro/) — 2026-11-20
- [AI エンジニアこそデータエンジニアリングを学ぶべき理由：RAG のデモが本番で崩れるところ](/blogs/posts/2026/11/data-engineering-for-ai-engineers/) — 2026-11-19
