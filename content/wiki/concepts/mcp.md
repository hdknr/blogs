---
title: "MCP (Model Context Protocol)"
description: "LLM が外部ツール・データベースと通信するためのオープンプロトコル"
date: 2026-04-06
lastmod: 2026-04-06
aliases: ["MCP", "Model Context Protocol"]
related_posts:
  - "/posts/2026/03/openclaw-claude-code-setup/"
  - "/posts/2026/03/sd-202604/"
tags: ["MCP", "protocol", "agent", "integration"]
---

## 概要

Anthropic が主導する、AI モデルと外部システムの連携のためのオープンプロトコル。Claude Code、Cursor など主要 AI ツールで採用が進み、AWS、GitHub、Google Workspace など主要プラットフォームが MCP Server を公開。

## 特徴

- ベンダーロックインを避けた相互運用性
- ツール定義の標準化（JSON Schema ベース）
- サブミリ秒レイテンシでの動作

## 関連ページ

- [AI エージェント](/blogs/wiki/concepts/ai-agent/) — MCP を利用してツール連携するシステム
- [Claude Code](/blogs/wiki/tools/claude-code/) — MCP の主要クライアント実装

## ソース記事

- [SD 2026年4月号](/blogs/posts/2026/03/sd-202604/) — 2026-03
