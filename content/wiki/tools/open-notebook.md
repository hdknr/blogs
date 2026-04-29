---
title: "Open Notebook"
description: "Google NotebookLM のオープンソース代替。プライバシー重視のローカル運用も可能"
date: 2026-04-22
lastmod: 2026-04-22
aliases: ["open notebook lm", "notebooklm oss"]
related_posts:
  - "/posts/2026/04/2026-04-22-open-notebook-notebooklm-oss/"
tags: ["oss", "notebooklm", "rag", "プライバシー", "ai-notebook"]
---

## 概要

Open Notebook は、Google NotebookLM のような「**ノートにソース文書を集約 → AI に質問**」型のリサーチツールを OSS で実装したプロジェクト。プライベートな文書や機密データを外部 SaaS にアップロードしたくないユースケースで、ローカル LLM や任意の API バックエンドと組み合わせて使える点が特徴。

## NotebookLM との関係

NotebookLM は Google が提供する**ソース駆動の AI ノート**で、PDF・Web・YouTube などをノートに追加すると LLM が文脈を理解した回答を返す。Open Notebook はその**オープンソース版**として、機能を再現しつつバックエンド LLM を差し替えられる柔軟性を持つ。

## 想定ユースケース

- **機密文書の要約・QA**: 社外秘・クライアント文書を外部にアップロードせず分析
- **研究ノート**: 論文・ノート・実験ログを統合してエージェント風に質問
- **個人の知識ベース**: Obsidian や Markdown ファイル群と連携した「自分専用 NotebookLM」

## 関連ページ

- [RAG](/blogs/wiki/concepts/rag/) — 同じ「文書集約 + 質問応答」のパターンの背景概念
- [Obsidian](/blogs/wiki/tools/obsidian/) — 個人ノートとの組み合わせ候補
- [Ollama](/blogs/wiki/tools/ollama/) — ローカル LLM バックエンド

## ソース記事

- [Open Notebook — NotebookLM の OSS 代替](/blogs/posts/2026/04/2026-04-22-open-notebook-notebooklm-oss/) — 2026-04-22
