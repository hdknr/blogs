---
title: "Apache Airflow 3 入門：AI エンジニアのための DAG・スケジューラー・再実行の基本"
date: 2026-11-20
lastmod: 2026-11-20
slug: "apache-airflow-intro"
draft: false
categories: ["ツール/開発環境"]
tags: ["Apache Airflow", "データエンジニアリング", "データ基盤", "オーケストレーション", "python"]
---

## はじめに

[RAG](/blogs/wiki/concepts/rag/) のナレッジベースを毎晩更新する、業務 DB から集計テーブルを作り直す、外部 API からデータを取り込んで加工する。最初は cron と Python スクリプト 1 本で始めることが多いはずです。ところが処理が増えてくると、次のような問題が出てきます。

- 「取り込みが終わってから変換を始める」といった処理の順番を、時刻をずらして無理やり合わせている
- 夜中に 1 つの処理が落ちても誰も気づかず、翌朝の検索結果が古いまま（[沈黙する失敗](/blogs/wiki/concepts/silent-failure/)）
- 先週の 3 日分だけやり直したいのに、日付を引数に取れる作りになっていない

[AI エンジニアこそデータエンジニアリングを学ぶべき理由](/blogs/posts/2026/11/data-engineering-for-ai-engineers/) では、Apache Airflow を「複雑なデータ処理をどうスケジュールし、管理するか」を解く道具として紹介しました。この記事はその続きで、AI エンジニアやアプリケーションエンジニア向けに次のことを整理します。

- Airflow が cron と比べて何をしてくれるか
- Airflow 3 を構成する部品
- TaskFlow API で小さな DAG を書く方法
- 再試行・バックフィルを安全に使うための冪等性
- Airflow が要らない場面と、代わりの選択肢

先に結論を言うと、Airflow を入れる目安は「処理間の依存と失敗対応が cron では手に負えなくなったとき」です。また、再実行しても結果が壊れないこと（冪等性）は Airflow が保証してくれるものではなく、DAG を書く側の責任です。

記事中のバージョンやコードは、2026 年 11 月時点の最新版 **Airflow 3.4.0**（2026-11-06 リリース）の公式ドキュメントに合わせています。

## 用語とプロダクト

| 用語・プロダクト | 意味 |
|---|---|
| Apache Airflow | Python でワークフローを定義し、スケジュール実行・監視するオープンソースのプラットフォーム |
| ワークフロー（オーケストレーション） | 複数の処理を、順番・依存関係・実行時刻を決めて動かすこと |
| DAG | Directed Acyclic Graph（有向非巡回グラフ）。タスクと依存関係の集まりで、Airflow のワークフローの単位 |
| タスク | DAG の中の 1 つの処理。「抽出する」「変換する」など |
| オペレーター | 決まった処理（SQL の実行、シェルの実行など）を提供するタスクの雛形 |
| TaskFlow API | Python 関数に `@task` を付けるだけでタスクを定義できる書き方 |
| DAG run | DAG を 1 回実行したもの。「11 月 19 日分の実行」のように、処理する期間と結び付く |
| data interval（担当期間） | その DAG run が処理を受け持つ期間。`data_interval_start` 〜 `data_interval_end` で表す |
| XCom | タスクの戻り値を次のタスクに受け渡す仕組み。小さな値向け |
| バックフィル | 過去の期間について DAG をまとめて実行し直すこと |
| 冪等性 | 同じ処理を何度実行しても、結果が 1 回実行したときと変わらない性質 |

Scheduler や Executor などの部品は、後の「Airflow 3 のアーキテクチャ」で説明します。

## Airflow が解く問題

Airflow の公式ドキュメントは、Airflow を「バッチワークフローをオーケストレーションするためのプラットフォーム」と説明しています。cron が「決まった時刻にコマンドを起動する」だけなのに対して、Airflow は次のことまで面倒を見ます。

- **依存関係**：「A と B が両方成功したら C を実行する」を、時刻ではなくグラフとして書ける
- **失敗時の扱い**：タスクごとに再試行回数や待ち時間を設定でき、失敗したタスクだけをやり直せる
- **履歴と可視化**：いつ、どのタスクが、どれだけ時間をかけて、成功したか失敗したかを Web UI で確認できる
- **期間との結び付き**：各実行が担当期間を持つので、過去の日付を指定した再実行（バックフィル）ができる

ワークフローは Python のコードとして書くので、Git で管理し、レビューし、テストできます。これは YAML や GUI でジョブを組むツールとの大きな違いです。

DAG は、タスクを頂点、依存関係を矢印としたグラフです。「非巡回」なので、循環する依存（A → B → A）は書けません。タスクの作り方は大きく 2 つあります。SQL の実行やクラウドサービスの操作のようなよくある処理は、**オペレーター**として用意されています（データベースやクラウド向けのものはプロバイダーパッケージとして別に配布）。自分で書く処理は、普通の Python 関数に `@task` を付ける **TaskFlow API** で書けます。アプリケーションエンジニアが最初に書くなら、関数呼び出しの形で依存関係が決まる TaskFlow API が分かりやすいでしょう。

## Airflow 3 のアーキテクチャ：Scheduler・Executor・API server

Airflow 3 は、次のような部品の組み合わせで動きます。

![Apache Airflow 3 の主なコンポーネントの関係を示した図。DAG ファイルを Dag processor が解析してメタデータ DB に保存し、Scheduler がメタデータ DB を見て実行するタスクを決めてワーカーに投入する。ワーカーは実行状態を Execution API 経由で API server に報告し、利用者はブラウザや CLI から API server を通じて操作・監視する](/blogs/images/apache-airflow-intro-architecture.png)

| 部品 | 役割 |
|---|---|
| Scheduler | スケジュールされたワークフローを起動し、実行すべきタスクを Executor に渡す |
| Executor | Scheduler の設定項目で、独立したプロセスではない。タスクをどこでどう実行するかを決める |
| Dag processor | DAG ファイルを解析し、シリアライズしてメタデータ DB に保存する |
| API server | Web UI と REST API を提供する。DAG やタスクの確認・手動実行・デバッグはここから行う |
| メタデータ DB | タスク・DAG・変数などの状態を保存する |
| ワーカー（Workers） | Scheduler から渡されたタスクを実際に実行する（Executor によっては不要） |
| Triggerer | 外部の完了待ちなどで一時停止（defer）したタスクを、非同期のイベントループで見張る（任意） |

Executor の既定値は `LocalExecutor` で、Scheduler のプロセスの中でタスクを実行します。処理が増えてきたら、キュー経由でワーカーを増やす `CeleryExecutor`（[Celery](/blogs/wiki/tools/celery/) を使う）や、タスクごとに Pod を起動する `KubernetesExecutor` などに切り替えます。Airflow 2.10 以降は、複数の Executor を併用することもできます。

Airflow 3 では、タスクが状態をメタデータ DB に直接書き込むのではなく、API server の Execution API を通じて報告する構成になりました。DAG を書くための API も `airflow.sdk`（Task SDK）にまとめられています。読者にとって実際に変わるのは import の書き方で、Airflow 2 系の記事でよく見る `from airflow.decorators import dag, task` ではなく、`from airflow.sdk import dag, task` と書くのが 3 系の流儀です。

## TaskFlow API で DAG を書く：RAG ナレッジ更新の例

RAG のナレッジベースを毎日更新する例を考えます。「前日に更新された社内文書を取り出す → チャンクに分割する → ベクトルストアに登録する」という 3 段の処理です。`fetch_updated_documents`・`split_into_chunks`・`upsert_to_vector_store` の 3 つは、自分の環境に合わせて実装する関数として省略しています。

```python
from datetime import timedelta

import pendulum
from airflow.sdk import dag, task
from airflow.timetables.trigger import CronTriggerTimetable

# fetch_updated_documents / split_into_chunks / upsert_to_vector_store は
# 自前の関数（ここでは省略）


@dag(
    # 毎日 2:00（日本時間）に実行。interval で「直前の 1 日分」を data interval にする
    schedule=CronTriggerTimetable(
        "0 2 * * *",
        timezone="Asia/Tokyo",
        interval=timedelta(days=1),
    ),
    start_date=pendulum.datetime(2026, 11, 1, tz="Asia/Tokyo"),
    catchup=False,
    default_args={
        "retries": 3,
        "retry_delay": timedelta(minutes=5),
    },
    tags=["rag"],
)
def rag_knowledge_sync():
    @task()
    def extract(*, data_interval_start, data_interval_end) -> list[dict]:
        # 担当期間に更新された文書だけを取り出す
        return fetch_updated_documents(since=data_interval_start, until=data_interval_end)

    @task()
    def chunk(documents: list[dict]) -> list[dict]:
        return [c for doc in documents for c in split_into_chunks(doc)]

    @task()
    def load(chunks: list[dict]) -> None:
        # 文書 ID と版をキーに upsert する。同じ期間を再実行しても重複しない
        upsert_to_vector_store(chunks, key=("doc_id", "version"))

    load(chunk(extract()))


rag_knowledge_sync()
```

ポイントは次のとおりです。

- **依存関係は関数呼び出しで決まる**：`load(chunk(extract()))` と書くだけで、extract → chunk → load の順に実行される。戻り値は XCom で次のタスクに受け渡される
- **`default_args` の `retries`**：一時的なネットワークエラーなどで落ちても、5 分おきに最大 3 回まで再試行する
- **`data_interval_start` / `data_interval_end`**：タスク関数のキーワード引数にこの名前を書くと、その DAG run の担当期間が渡される。「今日の日付」ではなく「担当期間」で処理を書くのが、後述のバックフィルの前提になる
- **スケジュールの指定**：`schedule="@daily"` のような文字列だけを渡すと、Airflow 3 の既定では担当期間の幅がゼロになる（開始と終了が同じ時刻）。この例では期間で差分を取りたいので、`CronTriggerTimetable` に `interval` を渡して「起動時刻までの 1 日分」を担当期間にしている

なお、XCom は既定ではメタデータ DB に保存され、公式ドキュメントも大きな値（データフレームなど）の受け渡しには使わないよう注意しています。実際の運用では、データ本体はオブジェクトストレージに置き、タスク間では保存先のパスだけを渡すのが一般的です。

手元で試すだけなら、公式のクイックスタートの手順が手軽です。Airflow 3.4.0 が対応する Python は 3.11 以上です。制約ファイル（constraints）を指定してインストールし、`airflow standalone` を実行すると、必要な部品がまとめて起動します。

```bash
AIRFLOW_VERSION=3.4.0
PYTHON_VERSION=3.12
CONSTRAINT_URL="https://raw.githubusercontent.com/apache/airflow/constraints-${AIRFLOW_VERSION}/constraints-${PYTHON_VERSION}.txt"
pip install "apache-airflow==${AIRFLOW_VERSION}" --constraint "${CONSTRAINT_URL}"
airflow standalone
```

起動後、`http://localhost:8080` で UI が開きます。

## 再実行（再試行・バックフィル）と冪等性

Airflow を使う価値が一番出るのは、処理が失敗したときと、過去をやり直したいときです。

### 再試行

タスク単位で `retries` と `retry_delay` を設定できます。DAG 全体ではなく、失敗したタスクだけが再試行されるので、成功済みの重い取り込みをやり直す必要はありません。UI から特定のタスクを「クリア」して再実行することもできます。クリアは、タスクの状態をリセットして Scheduler にもう一度実行させる操作です。

### catchup とバックフィル

`catchup` は、`start_date` を過去に設定して DAG を有効にしたときの動作を決める設定です。過ぎてしまった期間の実行をまとめて作るかどうかを指定します。Airflow 3 では既定値が `False`（`scheduler.catchup_by_default=False`）なので、有効にした時点から先だけが実行されます。

過去の期間を意図的にやり直したいときは、**バックフィル**を使います。Airflow 3 では UI の Trigger 画面から実行するか、CLI で次のように指定します。

```bash
airflow backfill create --dag-id rag_knowledge_sync \
    --from-date 2026-11-10 \
    --to-date 2026-11-12 \
    --reprocess-behavior failed \
    --max-active-runs 3
```

`--reprocess-behavior` では、すでに実行済みの期間をどう扱うか（失敗した分だけやり直す、など）を選べます。`--max-active-runs 3` は、同時に走らせる DAG run を 3 つまでに抑える指定です。

### 冪等なタスクの書き方

再試行やバックフィルを安全に使えるかどうかは、タスクが**冪等**かどうかで決まります。同じ期間を 2 回実行したときに、データが 2 倍にならないように作っておく必要があります。

- **追記（INSERT）ではなく upsert か「期間ごとに削除してから書き込む」にする**：上の例では文書 ID と版をキーに upsert している
- **「現在時刻」ではなく「担当期間」でデータを絞る**：`datetime.now()` で処理対象を決めると、再実行した日によって結果が変わってしまう
- **外部への副作用（メール送信、課金 API の呼び出しなど）は分離する**：再試行で二重に送られても困らない作りにするか、別タスクにして再試行回数を絞る

冪等性は Airflow の機能ではなく、DAG を書く側が守るべき設計上の約束です。前回の記事では「同期処理が途中で落ちて再実行したとき、重複データが生まれないか」という問いを挙げました。この問題は、Airflow を入れても自動では解決しません。

## cron で十分な場面と Airflow を入れる目安

Airflow は Scheduler、API server、メタデータ DB などを常に動かしておく必要があり、それ自体が運用対象になります。次のような場面では、cron（やクラウドのスケジューラー）と Python スクリプトで十分なことが多いでしょう。

- 処理が 1 〜 2 本で、互いに依存していない
- 失敗したら翌日に再実行すれば済み、過去の期間をやり直す必要がない
- 処理の履歴を UI で追う人がいない

前回の記事でも、Python スクリプトと PostgreSQL で済むのに、先に大きな基盤を組んでしまう失敗（[オーバーエンジニアリング](/blogs/wiki/concepts/overengineering/)）が挙げられていました。Airflow を検討し始める目安は、**処理間の依存が増えて時刻合わせで管理できなくなったとき**や、**失敗に気づけない・過去をやり直せないことが実害になったとき**です。

cron で始める場合も、スクリプトを「担当期間を引数で受け取る」「何度実行しても結果が同じ」形で書いておくと、後で Airflow に載せ替えるときにそのままタスクにできます。

## Airflow の代替：Dagster・Prefect・マネージドサービス

| ツール | 定義の中心 | 向いている場面 |
|---|---|---|
| Apache Airflow | タスクと依存関係（DAG） | 定時バッチを多数抱え、実績のある定番を使いたい |
| Dagster | 作られるデータ（アセット） | テーブル間の系譜（リネージ）やデータの鮮度を管理したい |
| Prefect | Python の関数（`@flow` / `@task`） | 条件分岐やループの多い処理を、普通の Python として書きたい |

### Dagster

ワークフローを「タスクの順番」ではなく「作られるデータ（アセット）」を中心に定義するツールです。どのテーブルがどのテーブルから作られるかという系譜や、データの鮮度を扱いやすいのが特徴です。[dbt](/blogs/wiki/tools/dbt/) と組み合わせる構成もよく使われます。

### Prefect

普通の Python 関数に `@flow` と `@task` を付けて書くツールです。DAG を事前に組み立てるというより、Python のコードをそのまま実行して記録する感覚に近く、条件分岐やループを素直に書けます。

### マネージドサービス

Airflow 自体を運用したくない場合は、クラウド事業者のマネージドサービスを使えます。

- **Cloud Composer**（Google Cloud）：2026 年 4 月に「Managed Service for Apache Airflow」へ移行していくと発表されている
- **Amazon MWAA**（Amazon Managed Workflows for Apache Airflow）：AWS のマネージド Airflow。2026 年 9 月に Airflow 3.3.1 への対応が発表された

どちらも、最新の Airflow がリリースされてから対応するまでに時間差があります。使える機能は、サービス側が対応しているバージョンで確認してください。

### Airflow 側の動き

Airflow も、動的なワークフローへの対応を進めています。3.4.0 では、実行時に回数が決まるループ（Task Loops）が追加されました。

## まとめ

- Airflow は、複数の処理の依存関係・スケジュール・再試行・履歴を、Python のコードとして管理するためのツール
- ワークフローは DAG、処理の単位はタスク。TaskFlow API なら `@task` を付けた関数の呼び出しで依存関係を書ける
- Scheduler が実行するタスクを決め、Executor の設定に従ってワーカーが実行する。Airflow 3 では API server が UI と Execution API を受け持つ
- 再試行とバックフィルを安全に使えるかは、タスクを冪等に書けるかで決まる
- 処理が少なく依存もないうちは cron で十分。依存と失敗対応が手に負えなくなってから導入を考えればよい

まずは `airflow standalone` で上の DAG（関数の中身はダミーで構いません）を動かし、UI で DAG run とタスクの状態を眺めてみるのがおすすめです。

## 関連記事

- [AI エンジニアこそデータエンジニアリングを学ぶべき理由：RAG のデモが本番で崩れるところ](/blogs/posts/2026/11/data-engineering-for-ai-engineers/)
- [AWS だけで作る AI ネイティブなデータ分析基盤：Aurora zero-ETL × Redshift × dbt 構成案](/blogs/posts/2026/11/aws-only-ai-native-data-platform/)
- [Claude Code + Celery: LLMが決定論的処理を動的に委譲するオーケストレーション](/blogs/posts/2026/03/claude-code-celery-orchestration/)
- [wiki: dbt](/blogs/wiki/tools/dbt/)
- [wiki: Celery](/blogs/wiki/tools/celery/)
- [wiki: AI ネイティブなデータ分析基盤](/blogs/wiki/concepts/ai-native-data-platform/)
