---
title: "MCP (Model Context Protocol)"
description: "LLM が外部ツール・データベースと通信するためのオープンプロトコル"
date: 2026-04-06
lastmod: 2026-08-23
aliases: ["MCP", "Model Context Protocol"]
related_posts:
  - "/posts/2026/03/openclaw-claude-code-setup/"
  - "/posts/2026/03/sd-202604/"
  - "/posts/2026/08/digital-agency-mcp-ai-ready-data/"
tags: ["mcp", "protocol", "agent", "integration"]
---

## 概要

Anthropic が主導する、AI モデルと外部システムの連携のためのオープンプロトコル。Claude Code、Cursor など主要 AI ツールで採用が進み、AWS、GitHub、Google Workspace など主要プラットフォームが MCP Server を公開。

## 特徴

- ベンダーロックインを避けた相互運用性
- ツール定義の標準化（JSON Schema ベース）
- サブミリ秒レイテンシでの動作

## AI-ready なデータ公開への応用

デジタル庁の行政手続 MCP サーバー（約 75,000 件）は、**LLM に検索・集計条件の指定だけを任せ、算術はサーバー側で実行する** 設計を採る。`dataset.yaml` による意味定義、Parquet 採用、ファジーマッチの適用範囲の限定がポイント。

詳細: [AI-ready データ設計](/blogs/wiki/concepts/ai-ready-data/)

## 関連ページ

- [AI エージェント](/blogs/wiki/concepts/ai-agent/) — MCP を利用してツール連携するシステム
- [Claude Code](/blogs/wiki/tools/claude-code/) — MCP の主要クライアント実装

## ソース記事

- [SD 2026年4月号](/blogs/posts/2026/03/sd-202604/) — 2026-03
- [デジタル庁の行政手続 MCP サーバーに学ぶ「LLM に計算させない」データ設計](/blogs/posts/2026/08/digital-agency-mcp-ai-ready-data/) — 2026-08-16
