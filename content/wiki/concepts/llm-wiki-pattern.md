---
title: "LLM Wiki パターン"
description: "AI エージェントに個人ナレッジベースを継続的に構築・保守させるパターン"
date: 2026-04-05
lastmod: 2026-04-06
aliases: ["LLM Wiki", "Karpathy Wiki"]
related_posts:
  - "/posts/2026/04/karpathy-llm-wiki/"
tags: ["LLM", "ナレッジマネジメント", "AIエージェント", "RAG"]
---

## 概要

Andrej Karpathy が提案した、LLM エージェントに個人ナレッジベース（Wiki）を継続的に構築・保守させるパターン。RAG が「毎回ゼロから読み直す」のに対し、LLM Wiki は知識を積み上げて複利的に成長させる。

## 三層構造

| 層 | 役割 | 誰が扱うか |
|---|---|---|
| **Raw Sources** | 論文・記事・メモなどの原本資料 | 人間がキュレーション、AI は読むだけ |
| **Wiki** | AI が生成・保守するマークダウン群 | AI が書き、人間が読む |
| **Schema** | AI への管理指示（構造・命名規則・ワークフロー） | 人間が定義 |

## 三つの基本操作

- **Ingest（取り込み）**: 新しい資料を投入し、AI に Wiki を更新させる
- **Query（質問）**: Wiki に対して質問し、統合的な回答を得る
- **Lint（保守）**: 矛盾・古い記述・孤立ページなどを定期チェック

## なぜ機能するか

人間が Wiki を放棄する主因は保守コスト。LLM は相互参照の更新、要約の最新化、一貫性維持を飽きずに続けられる。保守コストがほぼゼロになることで Wiki が持続する。

## 関連ページ

- [コンテキスト圧縮](/blogs/wiki/concepts/context-compression/) — LLM の文脈管理における関連技術
- [Claude Code](/blogs/wiki/tools/claude-code/) — LLM Wiki の実行環境として利用可能

## ソース記事

- [Karpathy の LLM Wiki — AIエージェントが育てる個人ナレッジベースという新パターン](/blogs/posts/2026/04/karpathy-llm-wiki/) — 2026-04-05
