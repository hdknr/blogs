---
title: "RAG (Retrieval-Augmented Generation)"
description: "外部データベースから情報検索し、それを基に LLM が応答を生成する技術"
date: 2026-04-06
lastmod: 2026-04-16
aliases: ["RAG", "検索拡張生成"]
related_posts:
  - "/posts/2024/04/getai-rag/"
  - "/posts/2026/04/karpathy-llm-wiki/"
  - "/posts/2026/03/rag-adaptive-search-strategy/"
tags: ["RAG", "LLM", "ベクトル検索", "ナレッジマネジメント", "アダプティブ検索"]
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

## 関連ページ

- [LLM Wiki パターン](/blogs/wiki/concepts/llm-wiki-pattern/) — RAG の限界を超える知識積み上げ型アプローチ
- [AI エージェント](/blogs/wiki/concepts/ai-agent/) — RAG を内部で利用するシステム
- [MemPalace](/blogs/wiki/tools/mempalace/) — ベクトル検索による永続メモリシステム

## ソース記事

- [getAI RAG](/blogs/posts/2024/04/getai-rag/) — 2024-04
- [Karpathy の LLM Wiki](/blogs/posts/2026/04/karpathy-llm-wiki/) — 2026-04
- [AIが自分で調べ方を選ぶRAG — モデル推論能力でスケールする新手法](/blogs/posts/2026/03/rag-adaptive-search-strategy/) — 2026-03-17
