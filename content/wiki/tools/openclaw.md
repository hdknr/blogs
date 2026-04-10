---
title: "OpenClaw"
description: "オープンソースの AI エージェント基盤フレームワーク。Claude、Grok、Ollama に対応"
date: 2026-04-06
lastmod: 2026-04-06
aliases: ["openclaw"]
related_posts:
  - "/posts/2026/03/openclaw-claude-code-setup/"
  - "/posts/2026/03/openclaw-overview/"
  - "/posts/2026/03/openclaw-agent-runtime/"
  - "/posts/2026/03/openclaw-china-security-warning/"
tags: ["agent", "オープンソース", "フレームワーク"]
---

## 概要

深圳で開発されたオープンソース AI エージェント基盤。複数の LLM（Claude、Grok、Ollama）に対応し、MCP 統合により任意のツール連携が可能。

## セキュリティ上の注意

中国 CNCERT が緊急セキュリティ警告を発出。デフォルト設定でローカルファイルシステム・環境変数・シェルへの広範なアクセスが有効になっている問題。コンテナ隔離、ネットワーク制限が必須。

## 関連ページ

- [AI エージェント](/blogs/wiki/concepts/ai-agent/) — OpenClaw が実装するパターン
- [MCP](/blogs/wiki/concepts/mcp/) — OpenClaw が採用するプロトコル

## ソース記事

- [OpenClaw セットアップ](/blogs/posts/2026/03/openclaw-claude-code-setup/) — 2026-03
- [OpenClaw 概要](/blogs/posts/2026/03/openclaw-overview/) — 2026-03
- [OpenClaw エージェントランタイム全体像](/blogs/posts/2026/03/openclaw-agent-runtime/) — 2026-03
- [OpenClaw セキュリティ警告](/blogs/posts/2026/03/openclaw-china-security-warning/) — 2026-03
