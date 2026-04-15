---
title: "OpenClaw"
description: "オープンソースの AI エージェント基盤フレームワーク。Claude、Grok、Ollama に対応。ローカル自律型エージェントとして Claude Managed Agents と対照的な設計思想を持つ"
date: 2026-04-06
lastmod: 2026-04-15
aliases: ["openclaw"]
related_posts:
  - "/posts/2026/03/openclaw-claude-code-setup/"
  - "/posts/2026/03/openclaw-overview/"
  - "/posts/2026/03/openclaw-agent-runtime/"
  - "/posts/2026/03/openclaw-china-security-warning/"
  - "/posts/2026/04/gemini-agent-mode/"
  - "/posts/2026/04/claude-managed-agents-architecture/"
tags: ["agent", "オープンソース", "フレームワーク", "ローカルエージェント"]
---

## 概要

深圳で開発されたオープンソース AI エージェント基盤。2025年11月に「Clawdbot」として公開後、商標問題で改名。複数の LLM（Claude、Grok、Ollama）に対応し、MCP 統合により任意のツール連携が可能。GitHub スターは25万を超える。

## 設計思想：ローカル自律型

OpenClaw は Gateway デーモンがユーザーのデバイスに常駐し、自律的にタスクを処理する設計。Claude Managed Agents（クラウド管理型）とは対照的なアーキテクチャを持つ。

| 観点 | OpenClaw | Claude Managed Agents |
|------|----------|-----------------------|
| 実行場所 | ローカルデバイス | Anthropic クラウド |
| 常駐性 | Gateway デーモンが常駐 | セッション単位のオンデマンド |
| データ管理 | SOUL.md / MEMORY.md でローカル管理 | Anthropic サーバーに保存 |
| カスタマイズ | ClawHub の 13,000+ スキル | MCP サーバー + 組み込みツール |
| 障害分離 | 単一デーモン（Gateway + Runtime 結合） | Brain / Session / Hands が独立 |

## Gemini Agent との比較

Google Gemini Agent モード（クラウド型、Google Workspace 専用）との対比:

- **Gemini Agent**: クラウド管理、Google Workspace との統合が強み、スケジュール実行可能
- **OpenClaw**: セルフホスト、データがデバイスから出ない、100以上のビルトインスキル

## セキュリティ上の注意

中国 CNCERT が緊急セキュリティ警告を発出。デフォルト設定でローカルファイルシステム・環境変数・シェルへの広範なアクセスが有効になっている問題。コンテナ隔離、ネットワーク制限が必須。また、Cisco・Giskard の研究チームがサードパーティスキルにおけるデータ流出・プロンプトインジェクションリスクを指摘（CVE-2026-25253、CVSS 8.8）。

## 関連ページ

- [AI エージェント](/blogs/wiki/concepts/ai-agent/) — OpenClaw が実装するパターン
- [Claude Managed Agents](/blogs/wiki/tools/claude-managed-agents/) — クラウド型マネージドエージェントとの対比
- [Gemini Agent](/blogs/wiki/tools/gemini-agent/) — クラウド連携型エージェントとの対比
- [MCP](/blogs/wiki/concepts/mcp/) — OpenClaw が採用するプロトコル

## ソース記事

- [OpenClaw セットアップ](/blogs/posts/2026/03/openclaw-claude-code-setup/) — 2026-03
- [OpenClaw 概要](/blogs/posts/2026/03/openclaw-overview/) — 2026-03
- [OpenClaw エージェントランタイム全体像](/blogs/posts/2026/03/openclaw-agent-runtime/) — 2026-03
- [OpenClaw セキュリティ警告](/blogs/posts/2026/03/openclaw-china-security-warning/) — 2026-03
- [Gemini Agentモード：Google Workspaceを自動化するAIエージェント](/blogs/posts/2026/04/gemini-agent-mode/) — 2026-04-07
- [Claude Managed Agents のアーキテクチャ：Brain / Session / Hands の分離設計](/blogs/posts/2026/04/claude-managed-agents-architecture/) — 2026-04-10
