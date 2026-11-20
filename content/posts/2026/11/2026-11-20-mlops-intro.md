---
title: "MLOps 入門：モデルを本番で回し続けるための実践とツール、LLMOps との関係"
date: 2026-11-20
lastmod: 2026-11-20
slug: "mlops-intro"
draft: false
categories: ["AI/LLM"]
tags: ["MLOps", "LLMOps", "MLflow", "機械学習", "データエンジニアリング"]
description: "MLOps とは何かを、データ・学習・評価・デプロイ・監視・再学習のライフサイクル、実験管理やモデルレジストリなどの中核プラクティス、MLflow・DVC・Kubeflow・Feast などの代表ツール、Google の成熟度レベル、LLMOps との関係から整理し、MLflow の最小コード例を紹介します。"
---

## はじめに

ノートブックで精度の良いモデルができた。ここまでは機械学習プロジェクトの入り口にすぎません。本番に載せたあとで、次のような問いが出てきます。

- 3 か月前にデプロイしたモデルは、どのデータ・どのコード・どのパラメータで作ったものか
- 新しいモデルは、いま本番で動いているモデルより本当に良いのか
- 入力データの傾向が変わって精度が落ちたとき、誰がいつ気づき、どう作り直すのか

こうした問いに仕組みで答えるのが **MLOps（Machine Learning Operations）** です。前回の記事「[AI エンジニアこそデータエンジニアリングを学ぶべき理由](/blogs/posts/2026/11/data-engineering-for-ai-engineers/)」では、RAG のデモが本番で崩れる原因の多くはデータの流れにある、と整理しました。この記事はその続きです。データの先にある「モデルを本番で回し続ける」ための考え方と道具を、AI エンジニアやアプリケーションエンジニア向けに入門としてまとめます。

この記事では次の内容を扱います。

- ML システムのライフサイクルと CT（継続的トレーニング）
- MLOps の中核となるプラクティスと代表的なツール
- Google の MLOps 成熟度レベル
- MLflow で実験管理とモデル登録を試す最小例
- LLMOps との関係と、AI エンジニアが始める順番

## 用語とプロダクト

先に、この記事に出てくる用語とプロダクトを整理しておきます。

| 用語 | 意味 |
|---|---|
| MLOps | 機械学習モデルの開発（ML）と運用（Ops）をつなぎ、本番で継続的に回すための実践の総称 |
| 実験管理（Experiment Tracking） | 学習のたびにパラメータ・指標・成果物を記録し、あとで比較できるようにすること |
| モデルレジストリ | 学習済みモデルを名前と版で管理し、どの版を本番に出すかを決める台帳 |
| 特徴量ストア（Feature Store） | 特徴量の定義・保存・取得を一元化し、学習時と推論時で同じ値を使えるようにする仕組み |
| CT（Continuous Training） | 新しいデータや性能劣化をきっかけに、モデルを自動で再学習・再提供すること |
| データドリフト | 本番の入力データの分布が、学習時のデータから変わっていくこと |
| LLMOps | LLM を使ったアプリケーション（RAG、エージェントなど）の運用に MLOps の考え方を広げたもの |

| プロダクト | 役割 |
|---|---|
| [MLflow](https://mlflow.org/) | 実験管理、モデルレジストリ、LLM アプリのトレーシング・評価・プロンプト管理を備えたオープンソースのプラットフォーム |
| [DVC](https://dvc.org/) | Git と組み合わせてデータやモデルの版を管理するオープンソースのツール。2025 年 11 月に Iterative.ai から lakeFS（Treeverse）へ開発が引き継がれた |
| [Kubeflow](https://www.kubeflow.org/) | Kubernetes 上で ML のワークフロー（学習パイプライン、モデル提供など）を動かすためのプロジェクト群。2026 年 8 月に CNCF の Graduated プロジェクトになった |
| [Feast](https://feast.dev/) | オープンソースの特徴量ストア |
| [Amazon SageMaker AI](https://aws.amazon.com/sagemaker/ai/) / [Vertex AI](https://docs.cloud.google.com/gemini-enterprise-agent-platform) | AWS と Google Cloud のマネージド ML プラットフォーム。パイプライン、モデルレジストリ、モデル監視をまとめて提供する。Vertex AI は 2026 年 4 月に Gemini Enterprise Agent Platform へ改称された |

## MLOps とは何か

普通のソフトウェアは、コードが同じなら同じように動きます。機械学習のシステムは違います。**コードに加えて、データとモデルという、時間とともに変化する 2 つの要素を抱えている**からです。コードを 1 行も変えなくても、入力データの傾向が変わればモデルの精度は落ちていきます。

そのため ML システムでは、作って終わりではなく、次のサイクルを回し続ける必要があります。

![MLOps のライフサイクルを示す図。データ収集・検証、学習、評価・検証、モデル登録、デプロイ、監視の 6 段階が左から右に並び、監視でドリフトや性能劣化を検知すると継続的トレーニングとしてデータ収集に戻るループになっている。各段階の下に DVC と Feast、MLflow Tracking、モデルレジストリ、CI/CD、ドリフト監視などの対応するプラクティスとツールがあり、学習パイプラインの自動化とメタデータ・系譜の管理が全体を支えている](/blogs/images/mlops-intro-lifecycle.png)

1. **データ収集・検証**：学習に使うデータを集め、欠損や分布の異常がないかを確かめる
2. **学習**：モデルを学習させ、条件と結果を記録する
3. **評価・検証**：評価用データで性能を測り、いまの本番モデルと比べる
4. **モデル登録**：合格したモデルを版付きで登録する
5. **デプロイ**：推論サービスやバッチ処理に載せる
6. **監視**：入力データや予測の品質を見張り、劣化したら再学習に戻る

Google Cloud のアーキテクチャガイド「[MLOps: Continuous delivery and automation pipelines in machine learning](https://docs.cloud.google.com/architecture/mlops-continuous-delivery-and-automation-pipelines-in-machine-learning)」は、ML システムに固有の性質を整理しています。そこでは、ソフトウェアの CI（継続的インテグレーション）・CD（継続的デリバリー）に加えて **CT（継続的トレーニング）** が挙げられています。再学習のきっかけとしては、定期実行、新しいデータの到着、性能の劣化、コンセプトドリフト（入力と正解の関係そのものが変わること）が例示されています。

## MLOps の中核となるプラクティス

### 実験管理

学習は何十回、何百回と繰り返します。どの実行でどのパラメータを使い、どんな指標が出て、どのモデルファイルができたか。記録がないと、「一番良かったのはどれか」「なぜあのときは精度が出たのか」が分からなくなります。MLflow Tracking のような実験管理ツールは、実行（run）ごとにパラメータ・指標・成果物をまとめて保存し、UI で比較できるようにします。

### データとモデルの版管理

コードは Git で版管理できますが、数 GB のデータセットやモデルファイルを Git にそのまま入れるのは現実的ではありません。DVC はデータの実体をクラウドストレージなどに置き、その参照（ハッシュを記したメタファイル）を Git で管理します。これで「このコミットのモデルはこのデータで学習した」という対応を再現できます。

### モデルレジストリ

学習済みモデルを「名前 + 版」で登録し、どの版が本番かを管理する台帳です。MLflow の Model Registry では、同じ名前で登録するたびに版番号が増えます。本番の版を指すには `champion` のような**エイリアス**を付け、切り替えるときはエイリアスの付け先を別の版に移します。アプリ側は `models:/<モデル名>@champion` という URI で読み込むので、デプロイのたびにコードを書き換えずに済みます。

### CI/CD に加わる CT（継続的トレーニング）

ML のパイプラインでは、テストと配布の対象がコードだけではありません。

- **CI**：コードのテストに加えて、データの検証（スキーマ、値の範囲）やモデルの検証（評価指標がしきい値を超えているか）も含める
- **CD**：モデル単体ではなく、モデルを作る学習パイプラインごと本番へ届ける
- **CT**：本番のパイプラインが、新しいデータでモデルを自動的に作り直して提供する

### 特徴量ストア

学習時は過去のデータからバッチで特徴量を作り、推論時はリアルタイムで特徴量を作る、という構成はよくあります。このとき 2 つの処理の実装がずれると、学習時と推論時で特徴量の値が食い違います。オフラインの評価では良かったモデルが、本番で振るわなくなるわけです（training-serving skew）。

特徴量ストアは特徴量の定義と保存を一か所にまとめ、学習用（オフラインストア）と推論用（オンラインストア）の両方に同じ定義から値を提供します。

Feast はさらに、学習データを作るときに「各時点で実際に手に入っていた値」だけを使う結合（point-in-time correct な結合）も提供します。これで、未来の情報が学習データに漏れ込むのを防ぎます。

### 監視とドリフト検知

デプロイしたモデルは、ソフトウェアとしての死活監視（レイテンシ、エラー率）に加えて、**予測の品質**も見張る必要があります。正解ラベルがすぐ手に入らない場合も多いので、入力データの分布が学習時からどれだけずれたか（データドリフト）を代わりの指標として監視するのが一般的です。Google Cloud では Vertex AI（現 Gemini Enterprise Agent Platform）の Model Monitoring が、こうしたドリフト検知をマネージドで提供してきました。AWS の SageMaker Model Monitor も同様の機能ですが、2026 年 7 月 30 日で新規顧客への提供を終えており（既存顧客は継続利用可）、AWS は代替としてオープンソースの監視ツールと Amazon CloudWatch などの組み合わせを案内しています。

## MLOps の代表的なツール：MLflow・DVC・Kubeflow・Feast

| ツール | 主な守備範囲 | 向いている場面 |
|---|---|---|
| MLflow | 実験管理、モデルレジストリ、モデルの保存形式、LLM アプリのトレーシング・評価 | まず実験管理から始めたい。特定のクラウドに縛られたくない |
| DVC | データ・モデルの版管理、Git ベースのパイプライン定義 | Git の運用にデータの版管理を足したい |
| Kubeflow | Kubernetes 上の学習パイプライン（Kubeflow Pipelines）、ノートブック、モデル提供 | すでに Kubernetes を運用しており、ML 基盤も載せたい |
| Feast | 特徴量ストア（オフライン / オンライン） | 学習と推論で同じ特徴量を使い回す必要がある |
| SageMaker AI / Vertex AI | パイプライン、モデルレジストリ、エンドポイント、モデル監視までのマネージド一式 | AWS や Google Cloud に寄せて、運用の手間を減らしたい |

最初から全部を揃える必要はありません。前回の[データエンジニアリングの記事](/blogs/posts/2026/11/data-engineering-for-ai-engineers/)と同じで、**どの道具がどの問題を解くのか**を押さえ、困りごとが出てから足すのが現実的です。多くのチームにとっての最初の一歩は、実験管理とモデルレジストリでしょう。

## 成熟度レベル：Google の MLOps レベル 0 / 1 / 2

自分たちがどこにいて、次に何をすべきかを考えるには、前述の Google Cloud のガイドが示す 3 段階の成熟度レベルが分かりやすい物差しになります。

| レベル | 状態 | 特徴 |
|---|---|---|
| レベル 0：手動プロセス | データ分析から学習・検証まで、すべてノートブックやスクリプトを手で実行する | データサイエンティストが作ったモデルをエンジニアに手渡す。CI/CD はなく、モデルの更新はまれ |
| レベル 1：ML パイプラインの自動化 | 学習パイプラインそのものを自動化し、CT を実現する | データ・モデルの自動検証、パイプラインの起動トリガー、メタデータ管理が加わる。特徴量ストアは必要に応じて導入する |
| レベル 2：CI/CD パイプラインの自動化 | パイプラインの部品を作り直したら、自動でビルド・テスト・デプロイされる | パイプライン自体の変更を素早く安全に本番へ届けられる |

レベル 0 が悪いわけではありません。モデルの更新が年に数回で済むなら、レベル 0 で十分なこともあります。ただし、データの傾向が頻繁に変わる領域や、複数のモデルを並行して運用する場合は、レベル 1 の「パイプラインを自動化して再学習を回す」段階が必要になってきます。

## MLflow で実験管理を始める最小例

雰囲気をつかむために、MLflow で学習を記録し、モデルを登録するまでの最小例を示します。コードは MLflow 3 系の書き方です（2 系では `log_model` の `name` 引数の代わりに `artifact_path` を使います）。まずトラッキングサーバーを起動します。

```bash
pip install "mlflow>=3" scikit-learn
mlflow server --port 5000
```

サーバーはターミナルを占有するので、以降は別のターミナルで作業します。macOS ではポート 5000 を AirPlay レシーバーが使っていることがあります。起動できないときは `--port 5001` などに変え、下のコードの URI もそろえてください。

続いて、scikit-learn のロジスティック回帰を学習し、パラメータ・指標・モデルを記録します。次のコードを `train.py` として保存し、`python train.py` で実行します。

```python
import mlflow
from mlflow import MlflowClient
from sklearn.datasets import load_iris
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split

mlflow.set_tracking_uri("http://localhost:5000")
mlflow.set_experiment("mlops-intro")

X, y = load_iris(return_X_y=True)
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

params = {"C": 1.0, "max_iter": 200}

with mlflow.start_run():
    mlflow.log_params(params)

    model = LogisticRegression(**params)
    model.fit(X_train, y_train)

    accuracy = accuracy_score(y_test, model.predict(X_test))
    mlflow.log_metric("accuracy", accuracy)

    # モデルを保存し、同時にモデルレジストリへ登録する
    model_info = mlflow.sklearn.log_model(
        sk_model=model,
        name="iris_model",
        registered_model_name="iris-classifier",
    )

# 登録した版に champion エイリアスを付ける
client = MlflowClient()
client.set_registered_model_alias(
    "iris-classifier", "champion", model_info.registered_model_version
)

# 推論側はエイリアスで読み込む
loaded = mlflow.pyfunc.load_model("models:/iris-classifier@champion")
print(loaded.predict(X_test[:5]))
```

最後に、テストデータ先頭 5 件の予測クラスが表示されます。

```text
[1 0 2 1 1]
```

ブラウザで `http://localhost:5000` を開くと、実行ごとのパラメータと accuracy を一覧で比較でき、Models 画面には `iris-classifier` の版とエイリアスが表示されます。`C` を変えて何度か実行し、良い版にエイリアスを付け替えると、レジストリの使い方がつかめます。

## LLM / RAG 時代の MLOps：LLMOps

LLM を API で呼ぶアプリケーションでは、自分でモデルを学習しないことがほとんどです。では MLOps は関係ないかというと、そうではありません。「変わるものを版で管理し、評価で比べ、本番を監視する」という骨格はそのまま残り、管理する対象が変わります。

### MLOps と LLMOps の違い

| MLOps で管理していたもの | LLMOps で管理するもの |
|---|---|
| 学習コードとハイパーパラメータ | プロンプト、モデル名、温度などの呼び出し設定 |
| 学習データ | RAG の索引に入れる文書、チャンク分割や埋め込みの設定 |
| 評価用データと評価指標 | 評価セット（質問と期待する回答の組）と、LLM-as-a-judge を含む評価 |
| モデルレジストリ | プロンプトの版管理（プロンプトレジストリ） |
| 予測の監視・ドリフト検知 | トレーシング（プロンプト・検索結果・ツール呼び出しの記録）、コストと品質の監視 |

特に効いてくるのが次の 3 つです。

- **プロンプトの版管理**：プロンプトの 1 行の変更で出力は大きく変わります。コードと同じく版を付け、どの版が本番かを追えるようにします。
- **評価セット**：「前より良くなった」を感覚ではなく数字で言うために、代表的な質問と期待する答えの組を用意し、変更のたびに回します。従来の ML の「検証データで本番モデルと比べる」に当たります。
- **トレーシング**：RAG やエージェントは、検索、ツール呼び出し、複数回の LLM 呼び出しを経て答えを出します。どの段階で何が渡されたかを記録しておかないと、回答がおかしいときに原因を追えません。

MLflow は、トレーシング、LLM-as-a-judge を使った評価、プロンプトレジストリといった生成 AI 向けの機能も備えています。たとえばプロンプトは次のように版付きで登録し、読み込めます（先ほどのトラッキングサーバーに接続する前提です）。

```python
import mlflow

mlflow.set_tracking_uri("http://localhost:5000")

prompt = mlflow.genai.register_prompt(
    name="summarization-prompt",
    template="次の文章を {{ num_sentences }} 文で要約してください。\n\n{{ sentences }}",
    commit_message="Initial commit",
)

# 版を指定して読み込み、変数を埋める
prompt = mlflow.genai.load_prompt("prompts:/summarization-prompt/1")
text = prompt.format(num_sentences=1, sentences="...")
```

OpenAI や Anthropic の SDK を使っているなら、`mlflow.openai.autolog()` や `mlflow.anthropic.autolog()` を呼ぶだけで LLM 呼び出しのトレースが記録されます。[MLflow のトレーシング](https://mlflow.org/docs/latest/genai/tracing/)は OpenTelemetry と互換性があり、ベンダーに縛られずにトレースを扱えます。LLM アプリ向けのオブザーバビリティツールはほかにも多く、このブログでは [Opik を使った AI エージェントの可視化](/blogs/posts/2026/03/opik-openclaw-observability/) も紹介しています。

## AI エンジニアが MLOps / LLMOps を始める順番

LLM アプリを作っている人が MLOps の知識を取り入れるなら、次の順番がおすすめです。

1. **評価セットを作る**：10〜50 件の代表的な質問と期待する答えから始め、プロンプトや RAG の設定を変えるたびに回す
2. **トレーシングを入れる**：本番で何が起きているかを見えるようにする。評価セットに足すべき失敗例もここから見つかる
3. **プロンプトと設定に版を付ける**：Git でもプロンプトレジストリでもよいので、本番の版を特定できるようにする
4. **自前で学習・ファインチューニングをするなら**：実験管理とモデルレジストリを入れ、そのうえでパイプラインの自動化（レベル 1）を検討する（ファインチューニングと RAG の使い分けは「[ローカルQwenに個人知識を覚えさせたい — ファインチューニング vs RAG](/blogs/posts/2026/03/qwen-finetuning-vs-rag/)」も参考になります）

前回の記事で見たとおり、RAG の品質はデータの流れに大きく左右されます。データエンジニアリングで「データを継続的に信頼できる形で届ける」仕組みを作り、MLOps / LLMOps で「そのデータを使うモデルやアプリを継続的に評価し、見張り、改善する」仕組みを作ります。この 2 つがそろって初めて、デモを本番で回し続けられるようになります。

## まとめ

- MLOps は、データ → 学習 → 評価 → デプロイ → 監視 → 再学習のサイクルを、本番で継続的に回すための実践の総称
- 中核のプラクティスは、実験管理、データとモデルの版管理、モデルレジストリ、CI/CD/CT、特徴量ストア、ドリフトの監視
- 代表的なツールは MLflow、DVC、Kubeflow、Feast、SageMaker AI、Vertex AI。全部を揃える必要はなく、まず実験管理とレジストリから
- Google の成熟度レベルでは、手動（レベル 0）→ ML パイプラインの自動化（レベル 1）→ CI/CD の自動化（レベル 2）と進む
- LLM / RAG の時代でも骨格は同じで、管理対象がプロンプト、評価セット、トレースに変わる
- LLM アプリなら、評価セット → トレーシング → プロンプトの版管理の順に始めるのがおすすめ

## 関連記事

- [AI エンジニアこそデータエンジニアリングを学ぶべき理由：RAG のデモが本番で崩れるところ](/blogs/posts/2026/11/data-engineering-for-ai-engineers/)
- [6ヶ月でAIエンジニアになるロードマップ — 無料リソースだけで学ぶ完全ガイド](/blogs/posts/2026/03/ai-engineer-6-months-roadmap/)
- [Agentic AI 学習ロードマップ — 「フルスタックインテリジェンス」を9ヶ月で習得する体系的な道筋](/blogs/posts/2026/03/cb9c696dbeb648e3286f2976b9a3eac6/)
- [Opik × OpenClaw — AI エージェントの動作を完全可視化するオブザーバビリティプラグイン](/blogs/posts/2026/03/opik-openclaw-observability/)
- [AIエージェントの自己改善が頭打ちになる理由 — ハーネスで組む4つの仕組みと、最後に残る「評価」](/blogs/posts/2026/09/agent-self-improvement-design/)
- [ローカルQwenに個人知識を覚えさせたい — ファインチューニング vs RAG](/blogs/posts/2026/03/qwen-finetuning-vs-rag/)
- [RAG（wiki）](/blogs/wiki/concepts/rag/)
