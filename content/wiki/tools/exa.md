---
title: "Exa"
description: "AI/LLM のためのセマンティック検索エンジン。Claude MCP プラグインとしても提供"
date: 2026-04-25
lastmod: 2026-04-25
aliases: ["exa search", "exa for claude", "exa mcp"]
related_posts:
  - "/posts/2026/04/2026-04-25-exa-for-claude-mcp-plugin/"
tags: ["search", "mcp", "claude-code", "rag", "semantic-search"]
---

## 概要

Exa は LLM/AI エージェント向けに最適化されたセマンティック検索 API。Google などのキーワード検索エンジンと異なり、**自然言語クエリと意図でドキュメントをマッチング**するため、AI エージェントのコンテキスト取得に向く。

公式: <https://exa.ai/>

## 主要機能

- **Neural Search**: 埋め込みベースのセマンティック検索
- **Keyword Search**: 従来型のキーワード一致検索もサポート
- **Find Similar**: 与えた URL/ドキュメントと意味的に近いページを取得
- **Contents API**: 検索結果のフルテキスト・要約・ハイライトを返す
- **Live Crawl**: 検索時にリアルタイムでクロールするモード

## Claude / Claude Code での利用

**Exa for Claude（MCP プラグイン）** として提供されており、Claude Code から MCP 経由で呼び出せる。導入後は通常の Web Search ツールに加えて Exa の高度なセマンティック検索を利用できる。

[Model Context Protocol](/blogs/wiki/concepts/mcp/) サーバとして接続するため、API キー設定とサーバ起動の標準的な MCP セットアップで動く。

## 想定ユースケース

- **RAG のクエリリライタ**: 「自然言語の質問」→ 関連ドキュメント取得（[RAG](/blogs/wiki/concepts/rag/)）
- **エージェントの調査タスク**: 競合調査、技術調査、論文検索
- **コーディング支援**: GitHub やドキュメントサイトを横断したコード例・ライブラリ調査

## 関連ページ

- [MCP（Model Context Protocol）](/blogs/wiki/concepts/mcp/)
- [RAG](/blogs/wiki/concepts/rag/)
- [Claude Code](/blogs/wiki/tools/claude-code/)

## ソース記事

- [Exa for Claude MCP プラグイン](/blogs/posts/2026/04/2026-04-25-exa-for-claude-mcp-plugin/) — 2026-04-25
