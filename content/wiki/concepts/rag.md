---
title: "RAG (Retrieval-Augmented Generation)"
description: "外部データベースから情報検索し、それを基に LLM が応答を生成する技術"
date: 2026-04-06
lastmod: 2026-04-06
aliases: ["RAG", "検索拡張生成"]
related_posts:
  - "/posts/2024/04/getai-rag/"
  - "/posts/2026/04/karpathy-llm-wiki/"
tags: ["RAG", "LLM", "ベクトル検索", "ナレッジマネジメント"]
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

## 関連ページ

- [LLM Wiki パターン](/blogs/wiki/concepts/llm-wiki-pattern/) — RAG の限界を超える知識積み上げ型アプローチ
- [AI エージェント](/blogs/wiki/concepts/ai-agent/) — RAG を内部で利用するシステム

## ソース記事

- [getAI RAG](/blogs/posts/2024/04/getai-rag/) — 2024-04
- [Karpathy の LLM Wiki](/blogs/posts/2026/04/karpathy-llm-wiki/) — 2026-04
