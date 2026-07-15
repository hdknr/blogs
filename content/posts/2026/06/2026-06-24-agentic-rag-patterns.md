---
title: "Agentic RAGの3つのパターン：Router、Self-Correction、Multi-step Retrieval"
date: 2026-06-24
lastmod: 2026-06-24
slug: "agentic-rag-patterns"
draft: false
source_url: "https://github.com/hdknr/blogs/issues/1#issuecomment-4785295897"
categories: ["AI/LLM"]
tags: ["RAG", "Agentic RAG", "LangGraph", "LlamaIndex", "AIエージェント"]
---

## はじめに

従来の RAG（Retrieval-Augmented Generation）は「検索して答える」一方通行のパイプラインです。シンプルな質問には効果的ですが、複雑な質問になると精度が落ちるという限界がありました。

その発展系として注目されているのが **Agentic RAG** です。エージェントが検索・評価・再検索を自律的に繰り返すことで、より高品質な回答を生成できます。本記事では Agentic RAG の代表的な3つのパターンを整理します。

## 従来の RAG の限界

従来の RAG は「ベクトル検索でドキュメントを取得し、そのコンテキストを LLM に渡して回答を生成する」シンプルなパイプラインで動作します。しかし以下のような課題があります。

- **複雑な質問への対応が難しい** — 一度の検索で必要な情報がすべて取得できない
- **検索先が単一** — 複数のデータソースを使い分けられない
- **品質フィードバックなし** — 生成した回答が正確かどうか検証できない

## Agentic RAG とは

Agentic RAG では、LLM がエージェントとして機能し、ツール呼び出しや思考ループを通じて検索戦略を動的に決定します。単なる「検索 → 生成」にとどまらず、反復・分岐・評価といったステップを自律的に実行できる点が特徴です。

以下の図に、Agentic RAG の主要な3つのパターンをまとめます。

![Agentic RAGの3つのパターン（Router、Self-Correction、Multi-step Retrieval）を示すフロー図](/blogs/images/agentic-rag-patterns.png)

## 3つの主要パターン

### ① Router：検索先の自動切り替え

Router パターンは、質問の内容に応じて最適なデータソースを自動的に選択します。質問をRouter Agentが分類し、社内DB・Web検索・APIなど複数のデータソースから最適なものを選んで検索します。

**ユースケース:**

- 社内 FAQ と外部情報を使い分けたい
- 技術ドキュメントと製品情報で検索先を変えたい

**LangGraph での実装イメージ:**

```python
from langgraph.graph import StateGraph, END
from typing import TypedDict

class State(TypedDict):
    question: str
    source: str
    context: str
    answer: str

def router_node(state: State) -> State:
    question = state["question"]
    # LLM でデータソースを判定
    source = classify_datasource(question)  # 補助関数は省略
    return {**state, "source": source}

def retrieve_node(state: State) -> State:
    if state["source"] == "internal":
        context = search_internal_db(state["question"])
    elif state["source"] == "web":
        context = search_web(state["question"])
    else:
        context = search_api(state["question"])
    return {**state, "context": context}

graph = StateGraph(State)
graph.add_node("router", router_node)
graph.add_node("retrieve", retrieve_node)
graph.add_edge("router", "retrieve")
app = graph.compile()
```

### ② Self-Correction：自己評価と再検索

Self-Correction パターンは CRAG（Corrective RAG）とも呼ばれます。検索で取得したドキュメントの**関連性**を LLM が評価し、関連性が低い場合は検索クエリを改善して再検索するサイクルを持ちます。

流れは「検索 → ドキュメント関連性評価 → OK なら回答生成、NG なら再検索」です。回答の精度だけでなく、そもそも取得したドキュメントが質問に適切かどうかを自己評価できる点が特徴です。

**LangGraph での実装イメージ:**

```python
from langgraph.graph import StateGraph, END

def evaluator_node(state: State) -> State:
    # 取得ドキュメントの関連性を評価
    score = grade_document_relevance(
        state["question"], state["context"]
    )
    return {**state, "relevance_score": score}

def should_retry(state: State) -> str:
    if state["relevance_score"] < 0.7:
        return "retry"
    return "done"

graph.add_node("evaluate", evaluator_node)
graph.add_conditional_edges(
    "evaluate",
    should_retry,
    {"retry": "retrieve", "done": END}
)
app = graph.compile()
```

**ユースケース:**

- 法律・医療など高精度が求められる領域
- 事実確認が重要なビジネス文書の生成

### ③ Multi-step Retrieval：質問の分解と統合

Multi-step Retrieval パターンは、複雑な質問を複数のサブ質問に分解し、それぞれの検索結果を統合して最終回答を生成します。Planner がサブ質問を生成し、各サブ質問を並列に検索・回答した後、Synthesizer が統合します。

**LlamaIndex Workflows での実装イメージ:**

```python
from llama_index.core.workflow import (
    Workflow, step, Event, StartEvent, StopEvent
)

class QuestionDecomposedEvent(Event):
    sub_questions: list[str]

class SubResultEvent(Event):
    question: str
    result: str

class MultiStepRAGWorkflow(Workflow):
    @step
    async def decompose(
        self, ev: StartEvent
    ) -> QuestionDecomposedEvent:
        sub_questions = decompose_question(ev.question)
        return QuestionDecomposedEvent(sub_questions=sub_questions)

    @step
    async def retrieve_each(
        self, ctx, ev: QuestionDecomposedEvent
    ) -> SubResultEvent:
        # 各サブ質問を個別のイベントとして送出
        for q in ev.sub_questions:
            result = await retrieve_and_generate(q)
            ctx.send_event(SubResultEvent(question=q, result=result))

    @step
    async def synthesize(
        self, ctx, ev: SubResultEvent
    ) -> StopEvent:
        # 全サブ質問の結果が揃うまで収集
        results = ctx.collect_events(
            ev, [SubResultEvent] * expected_count
        )
        if results is None:
            return  # まだ揃っていない
        final_answer = synthesize_results(results)
        return StopEvent(result=final_answer)
```

**ユースケース:**

- 研究タスクの自動化（複数の論文・レポートを横断検索）
- 「A と B を比較して C を考慮した上で提案して」のような複合的な要求

## 実装技術の選択

| フレームワーク | 特徴 | 向いているパターン |
|---|---|---|
| **LangGraph** | グラフベースの状態管理、サイクル（ループ）の表現が得意 | Router、Self-Correction |
| **LlamaIndex Workflows** | イベント駆動、並列ステップの記述が簡潔 | Multi-step Retrieval |
| **LangChain LCEL** | チェーンの組み合わせが直感的 | Router（シンプルな場合） |

これらのフレームワークはいずれも Python ベースで、既存の LLM・ベクターストアと組み合わせやすい設計になっています。

## 構造化データへの応用：金融取引履歴・株価

Agentic RAG の対象データはテキスト文書に限りません。金融取引履歴や株価推移のような**構造化・数値・時系列データ**を Arrow 形式や PostgreSQL のような RDBMS に持たせ、それを検索対象にすることも可能です。むしろ、こうした数値データこそ Agentic RAG が従来 RAG より効く典型例です。

### なぜベクトル検索ではなくクエリなのか

従来 RAG は「テキストを埋め込みベクトルに変換し、意味的類似度で検索する」ことが前提でした。しかし「2026年 Q1 の平均株価」のような質問は、埋め込みの類似度では正確に取得できません。**集計・フィルタ・結合はクエリエンジンに任せる**のが正解です。

Agentic RAG における「検索（retrieval）」の実体は、エージェントが呼び出す**ツール**です。ツールはベクトル検索に限らず、SQL クエリでも DataFrame 操作でも構いません。前掲の Router パターンで `search_api` や社内 DB を候補にしていたのは、まさにこの発想です。

### データ形式ごとの使い分け

| 形式 | 向いている用途 | retrieval ツール |
|---|---|---|
| **PostgreSQL（RDBMS）** | ライブ／トランザクショナルな取引履歴、更新頻度の高いデータ、権限制御 | **Text-to-SQL**（エージェントが SQL を生成・実行） |
| **Arrow / Parquet** | 大量の株価ヒストリカルデータの列指向分析、インメモリ高速集計 | **DuckDB / Polars**（Arrow/Parquet をゼロコピーで読み、SQL・DataFrame クエリ） |

- **PostgreSQL** は `pgvector` を足せば、ニュースやレポートなどのテキストはベクトル検索、数値は SQL、という**ハイブリッド構成**を 1 つの DB で実現できます。
- **Arrow** は DuckDB や Polars がネイティブに読めるため、「過去10年の日次株価から移動平均を計算」のような分析クエリが高速です。エージェントには「SQL を投げるツール」として見せます。

### 3つのパターンへの対応

- **Router** — 質問を「ニュース検索（ベクトル）」か「株価集計（SQL / DuckDB）」に振り分ける。数値質問なら Text-to-SQL 経路へ誘導する。
- **Multi-step Retrieval** — 「A社とB社の直近四半期を比較し、業界平均も考慮して」という要求をサブ質問に分解し、各社の株価と業界平均を別々に SQL で取得したうえで Synthesizer が統合する。
- **Self-Correction** — 生成した SQL がエラーや空結果を返したら再生成する、あるいは取得結果が質問に対して妥当かを評価して再クエリする（構造化データ版 CRAG）。

### 実務上の注意点

1. **計算は LLM にさせない** — 合計・平均・成長率などの計算は必ず SQL / DataFrame エンジンに任せ、LLM は結果の解釈に専念させる（数値のハルシネーション回避）。
2. **Text-to-SQL の安全性** — 生成された SQL は read-only ロール・タイムアウト・行数上限で囲う。
3. **スキーマをコンテキストに渡す** — テーブル定義やカラムの説明をツールの記述に含めると、SQL 生成の精度が上がる。

## 実際の応用例

### 社内ナレッジ検索

Router を使って「この機能の仕様は？」には社内 Wiki を、「競合他社の最新動向は？」には Web 検索を自動選択します。「仕様を確認してレポートを作成して」のような複合的な依頼には Multi-step Retrieval を活用します。

### 法律・医療領域

Self-Correction を活用し、取得したドキュメントが質問に適切かどうかを LLM がチェックします。関連性の低いドキュメントは自動的に再検索・再取得されます。

### 研究タスクの自動化

Multi-step Retrieval で複数の論文を並列検索し、Synthesizer が矛盾点や共通点を整理した上で最終的な考察を生成します。

## まとめ

Agentic RAG の3つのパターンをまとめると以下になります。

| パターン | 解決する課題 | キーワード |
|---|---|---|
| **Router** | 検索先が単一で最適な情報源を使えない | 分類・振り分け |
| **Self-Correction** | 取得ドキュメントの関連性を保証できない | 評価・再試行 |
| **Multi-step Retrieval** | 複雑な質問を一度の検索で解決できない | 分解・並列・統合 |

これらのパターンは組み合わせることも可能です。たとえば「Router で検索先を選択 → Multi-step で分解して検索 → Self-Correction で関連性チェック」という複合的なパイプラインを構築することで、より高度な RAG システムを実現できます。

LangGraph と LlamaIndex Workflows はそれぞれの得意領域が異なります。既存の RAG パイプラインの限界を感じている方は、ユースケースに合ったパターンと実装フレームワークを選んで Agentic RAG への移行を検討してみてください。
