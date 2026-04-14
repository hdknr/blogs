---
title: "Gemini Agent"
description: "Google の Gemini に搭載されたエージェントモード。Gmail・Calendar・Drive など Google Workspace を横断して複雑なマルチステップタスクを自動実行する"
date: 2026-04-15
lastmod: 2026-04-15
aliases: ["Gemini Agentモード"]
related_posts:
  - "/posts/2026/04/gemini-agent-mode/"
tags: ["Gemini", "AIエージェント", "Google Workspace", "自動化"]
---

## 概要

Google が Gemini に追加したエージェント機能。単一の質問に答えるチャットではなく、複数ステップにわたる複雑なタスクを自律的に実行できる。Google Workspace（Gmail・Calendar・Drive・Slides）の各サービスを横断して操作が可能。

## 主な機能

| 機能 | 内容 |
|------|------|
| マルチステップ実行 | メール確認→カレンダー調整→資料作成を連続処理 |
| スケジュール実行 | 設定した時間帯に自動でタスクを実行 |
| Google Workspace 統合 | Gmail・Drive・Calendar・Slides を統合操作 |
| ユーザーコントロール | 実行前の確認、中断、取り消しが可能 |

## 利用条件

Google AI Ultra プランのサブスクライバー向けに提供（2026年4月時点）。一般ユーザーへの段階的な展開が予定されている。

## OpenClaw との比較

- **Gemini Agent**: クラウド管理、Google Workspace との統合が強み、セットアップ不要
- **OpenClaw（Claude Code ベース）**: ローカル実行、コードベースへの直接アクセス、技術者向け

業務効率化や非エンジニアのタスク自動化では Gemini Agent が、ソフトウェア開発自動化では OpenClaw のようなローカルエージェントが適している。

## 関連ページ

- [AI エージェント](/blogs/wiki/concepts/ai-agent/) — エージェントの基本概念
- [Claude Managed Agents](/blogs/wiki/tools/claude-managed-agents/) — Anthropic のマネージドエージェント基盤
- [MCP](/blogs/wiki/concepts/mcp/) — エージェントとツール連携のプロトコル

## ソース記事

- [Gemini Agentモード：Google Workspaceを丸ごと自動化するAIエージェントの実力](/blogs/posts/2026/04/gemini-agent-mode/) — 2026-04-07
