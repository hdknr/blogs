---
title: "RAG (Retrieval-Augmented Generation)"
description: "外部データベースから情報検索し、それを基に LLM が応答を生成する技術"
date: 2026-04-06
lastmod: 2026-07-15
aliases: ["RAG", "検索拡張生成", "Agentic RAG", "CRAG", "Text-to-SQL"]
related_posts:
  - "/posts/2026/04/karpathy-llm-wiki/"
  - "/posts/2026/03/rag-adaptive-search-strategy/"
  - "/posts/2026/06/agentic-rag-patterns/"
tags: ["RAG", "LLM", "ベクトル検索", "ナレッジマネジメント", "アダプティブ検索", "Agentic RAG"]
---

## 概要

最新のドキュメントやナレッジベースをベクトル DB に保存し、クエリ時に関連文書を検索して LLM に供与する手法。LLM の知識カットオフを補い、ハルシネーション低減に効果的。

## 仕組み

1. ドキュメントをチャンクに分割
2. Embeddings でベクトル化してベクトル DB に格納
3. クエリ時に類似ベクトルを検索
4. 検索結果をコンテキストとして LLM に渡す

## RAG の限界と LLM Wiki

Karpathy は RAG を「毎日同じ本を初めて読む人に質問を投げるようなもの」と評し、知識を積み上げる LLM Wiki パターンを提案した。RAG は都度検索、LLM Wiki は事前コンパイル。

## アダプティブ検索 RAG（新手法）

従来の RAG は検索戦略が固定されているため、クエリに合わない場合は精度が著しく低下する。**モデル自身が検索方法を選択・組み合わせる**アダプティブ RAG は、この問題に対応する新手法。

### 3つの検索戦略

| 検索戦略 | 向いているケース |
|----------|-----------------|
| **キーワード検索** | 固有名詞・型番・コマンドなど特定語句の検索 |
| **意味検索（セマンティック）** | 概念的な質問、言い換えが多い文書 |
| **チャンク全文読み** | 文脈・前後関係が重要な長文 |

モデルの推論能力が高いほど検索戦略の判断精度が向上するため、モデル進化と共に RAG 全体の性能が自然にスケールする構造となっている。読み込むテキスト量は従来と同等以下でも回答精度は向上する。

## Agentic RAG の3つのパターン

従来の「検索 → 生成」の一方通行を超え、LLM がエージェントとして検索・評価・再検索を自律的に繰り返すのが **Agentic RAG**。代表的な3パターンは組み合わせても使える。

| パターン | 解決する課題 | キーワード |
|---|---|---|
| **Router** | 検索先が単一で最適な情報源を使えない | 質問を分類し社内DB・Web・API・SQL へ振り分け |
| **Self-Correction（CRAG）** | 取得ドキュメントの関連性を保証できない | 関連性を評価し低ければクエリを改善して再検索 |
| **Multi-step Retrieval** | 複雑な質問を一度の検索で解決できない | 質問を分解し並列検索して Synthesizer が統合 |

実装は **LangGraph**（グラフ・サイクルの表現が得意、Router/Self-Correction 向き）と **LlamaIndex Workflows**（イベント駆動・並列、Multi-step 向き）が代表的。

### 構造化データへの応用

RAG の対象はテキスト文書に限らない。金融取引履歴・株価のような構造化・数値・時系列データは、ベクトルの意味的類似度では正確に取れないため、**集計・フィルタ・結合はクエリエンジンに任せる**のが正解。Agentic RAG の「検索」の実体はエージェントが呼ぶ**ツール**で、SQL クエリでも DataFrame 操作でもよい。PostgreSQL（`pgvector` でハイブリッド）には Text-to-SQL、Arrow/Parquet には DuckDB/Polars を使う。実務上は「計算は LLM にさせず SQL/DataFrame に任せる」「Text-to-SQL は read-only・タイムアウト・行数上限で囲う」がハルシネーション・安全性の要点。

### バックエンド LLM の使い分け

Agentic RAG は1質問で LLM を何度も呼ぶ（Router 判定 → クエリ生成 → 関連性評価 → 統合）ため、役割ごとにモデルを使い分けるのが定石。軽い分類・スコアリングは安価な小型モデル、SQL/クエリ生成は中位、Planner/Synthesizer は中〜上位、と割り当てるとコスト効率と品質が両立する。

## 関連ページ

- [LLM Wiki パターン](/blogs/wiki/concepts/llm-wiki-pattern/) — RAG の限界を超える知識積み上げ型アプローチ
- [AI エージェント](/blogs/wiki/concepts/ai-agent/) — RAG を内部で利用するシステム
- [MemPalace](/blogs/wiki/tools/mempalace/) — ベクトル検索による永続メモリシステム

## ソース記事

- [Karpathy の LLM Wiki](/blogs/posts/2026/04/karpathy-llm-wiki/) — 2026-04
- [AIが自分で調べ方を選ぶRAG — モデル推論能力でスケールする新手法](/blogs/posts/2026/03/rag-adaptive-search-strategy/) — 2026-03-17
- [Agentic RAG の3つのパターン：Router、Self-Correction、Multi-step Retrieval](/blogs/posts/2026/06/agentic-rag-patterns/) — 2026-06-24
