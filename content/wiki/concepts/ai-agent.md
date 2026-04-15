---
title: "AI エージェント"
description: "自律的にタスク実行できる AI システム。複数ステップの処理を自己制御で進める"
date: 2026-04-06
lastmod: 2026-04-15
aliases: ["AI Agent", "エージェント", "autonomous agent"]
related_posts:
  - "/posts/2026/03/ai-agent-qa/"
  - "/posts/2026/03/claude-code-agent-teams/"
  - "/posts/2026/04/autoagent-self-improving-agents/"
  - "/posts/2026/04/gemini-agent-mode/"
  - "/posts/2026/04/claude-managed-agents/"
  - "/posts/2026/04/claude-managed-agents-architecture/"
  - "/posts/2026/04/anthropic-vs-openai-harness-strategy/"
  - "/posts/2026/04/agent-harness-memory-lock-in/"
tags: ["agent", "LLM", "自律実行", "マネージドエージェント"]
---

## 概要

単一の応答ではなく、複数ステップのタスクを自律実行する AI システム。Claude Code、OpenAI Codex、Cursor など複数ツールで実装されている。エージェント間協調、分散実行、メモリ管理が 2026 年の主要トレンド。

## 主な実装パターン

- **シングルエージェント**: 1つの LLM が計画→実行→検証を繰り返す（Claude Code など）
- **マルチエージェント**: 複数のエージェントが役割分担して協調（Agent Teams）
- **メタエージェント**: エージェントのハーネスを AI 自身が改善（AutoAgent）

## 品質保証

AI エージェントの出力品質を担保するにはハーネスエンジニアリングが必須。CLAUDE.md（入力層）、Hooks（検証層）、Agent Skills（ワークフロー層）の多層構造で品質を保証する。

## エージェント基盤の分類

2026年時点の主要なエージェント基盤は大きく3種類に分類できる。

| 種別 | 代表例 | 特徴 |
|------|--------|------|
| **マネージドクラウド型** | Claude Managed Agents | インフラ不要、スケーラブル、ベンダー依存 |
| **ローカル自律型** | OpenClaw | プライバシー重視、カスタマイズ自由、セルフホスト |
| **クラウド連携型** | Gemini Agent | 特定サービス（Google Workspace 等）に最適化 |

## ハーネスとメモリのロックイン

LangChain 創設者 Harrison Chase が指摘する重要な概念。エージェントのメモリ（長期記憶）はハーネスの設計と不可分であり、クローズドなハーネスを使うと以下のリスクが生じる:

- コンパクション（会話圧縮）のロジックが不透明になる
- 長期メモリが第三者のサーバーに保存される
- ハーネス移行時にメモリの移植が困難になる

## 関連ページ

- [Claude Code](/blogs/wiki/tools/claude-code/) — 代表的な AI コーディングエージェント
- [Claude Managed Agents](/blogs/wiki/tools/claude-managed-agents/) — Anthropic のマネージドエージェント基盤
- [Gemini Agent](/blogs/wiki/tools/gemini-agent/) — Google Workspace 連携エージェント
- [OpenClaw](/blogs/wiki/tools/openclaw/) — ローカル自律型エージェント
- [ハーネスエンジニアリング](/blogs/wiki/concepts/harness-engineering/) — エージェント品質保証の設計パターン
- [自己改善エージェント](/blogs/wiki/concepts/self-improving-agents/) — エージェントが自律的に改善するパターン
- [MCP](/blogs/wiki/concepts/mcp/) — エージェントと外部ツールの接続プロトコル

## ソース記事

- [AI エージェント QA 手法](/blogs/posts/2026/03/ai-agent-qa/) — 2026-03
- [Claude Code Agent Teams](/blogs/posts/2026/03/claude-code-agent-teams/) — 2026-03
- [AutoAgent](/blogs/posts/2026/04/autoagent-self-improving-agents/) — 2026-04
- [Gemini Agentモード：Google Workspaceを自動化するAIエージェント](/blogs/posts/2026/04/gemini-agent-mode/) — 2026-04-07
- [Claude Managed Agents: パブリックベータ公開](/blogs/posts/2026/04/claude-managed-agents/) — 2026-04-10
- [Claude Managed Agents のアーキテクチャ](/blogs/posts/2026/04/claude-managed-agents-architecture/) — 2026-04-10
- [Anthropic vs OpenAI：Harness 戦略はなぜ真逆なのか](/blogs/posts/2026/04/anthropic-vs-openai-harness-strategy/) — 2026-04-13
- [エージェントハーネスとメモリのロックイン問題](/blogs/posts/2026/04/agent-harness-memory-lock-in/) — 2026-04-12
