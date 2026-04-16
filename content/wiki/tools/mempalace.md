---
title: "MemPalace"
description: "LLM に永続的なクロスセッションメモリを提供するオープンソース AI メモリシステム。SQLite + ChromaDB でローカル動作し、MCP 経由で主要 AI ツールと統合可能"
date: 2026-04-14
lastmod: 2026-04-14
aliases: []
related_posts:
  - "/posts/2026/04/mempalace-ai-memory/"
tags: ["MemPalace", "LLMメモリ", "ChromaDB", "MCP", "オープンソース"]
---

## 概要

2026年4月に GitHub で急速に注目を集めた AI メモリシステム。LongMemEval ベンチマークで 96.6% を公表し、1週間で 45,000 スター以上を獲得した。古代の記憶術「記憶の宮殿（Method of Loci）」にインスパイアされた階層構造で会話データを管理する。MIT ライセンスのオープンソース（Python）。

## アーキテクチャ：宮殿の構造

| 階層 | 役割 |
|------|------|
| Wing（翼） | トピックやプロジェクトをグループ化 |
| Hall（ホール） | メモリの種類を分類 |
| Room（部屋） | 特定の知識やアイデアを保持 |
| Closet / Drawer | さらに細かい情報の格納 |
| Tunnel（トンネル） | 異なる Room 間の関連を結ぶナレッジグラフ |

## 主な技術的特徴

- **完全ローカル動作**: SQLite + ChromaDB でローカルに永続化、外部 API 不要
- **MCP 対応**: Claude Code、ChatGPT、Cursor など主要 AI ツールと統合可能
- **AAAK 圧縮**: 独自の省略圧縮方式（ただし有効時はスコアが低下、後述）

## ベンチマークと論争

公表された「96.6%」スコアは、MemPalace の宮殿構造ではなく ChromaDB のデフォルト埋め込み（all-MiniLM-L6-v2）による Recall@5 の数値であることが指摘されている。また 100% スコアはテストセットへのオーバーフィッティング、AAAK 圧縮を有効にするとスコアは 84.2% に低下するという問題が確認された。開発チームはこれらを認め README を修正している。

## 導入が有効なケース

- 記憶の仕組みを持たない AI ツールに永続メモリを追加したい場合
- 複数の AI ツール間でメモリを共有したい場合

既に Claude Code の auto-memory や CLAUDE.md / MEMORY.md を活用している場合は重複する可能性が高い。

## 関連ページ

- [エージェントメモリのロックイン](/blogs/wiki/concepts/agent-memory-lock-in/) — メモリとハーネスの不可分性とロックインリスク
- [MCP](/blogs/wiki/concepts/mcp/) — MCP 経由で AI ツールと統合
- [RAG](/blogs/wiki/concepts/rag/) — ベクトル検索による知識拡張の概念
- [LLM Wiki パターン](/blogs/wiki/concepts/llm-wiki-pattern/) — AI と連携する知識管理の別アプローチ
- [claude-mem](/blogs/wiki/tools/claude-mem/) — Claude Code 専用の永続メモリプラグイン（別アプローチ）

## ソース記事

- [MemPalace とは？LongMemEval 96.6%を記録した AI メモリシステムの仕組みと論争](/blogs/posts/2026/04/mempalace-ai-memory/) — 2026-04-13
