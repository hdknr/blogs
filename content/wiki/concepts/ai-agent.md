---
title: "AI エージェント"
description: "自律的にタスク実行できる AI システム。複数ステップの処理を自己制御で進める"
date: 2026-04-06
lastmod: 2026-04-06
aliases: ["AI Agent", "エージェント", "autonomous agent"]
related_posts:
  - "/posts/2026/03/ai-agent-qa/"
  - "/posts/2026/02/agent-skills-guide/"
  - "/posts/2026/03/claude-code-agent-teams/"
  - "/posts/2026/04/autoagent-self-improving-agents/"
tags: ["agent", "LLM", "自律実行"]
---

## 概要

単一の応答ではなく、複数ステップのタスクを自律実行する AI システム。Claude Code、OpenAI Codex、Cursor など複数ツールで実装されている。エージェント間協調、分散実行、メモリ管理が 2026 年の主要トレンド。

## 主な実装パターン

- **シングルエージェント**: 1つの LLM が計画→実行→検証を繰り返す（Claude Code など）
- **マルチエージェント**: 複数のエージェントが役割分担して協調（Agent Teams）
- **メタエージェント**: エージェントのハーネスを AI 自身が改善（AutoAgent）

## 品質保証

AI エージェントの出力品質を担保するにはハーネスエンジニアリングが必須。CLAUDE.md（入力層）、Hooks（検証層）、Agent Skills（ワークフロー層）の多層構造で品質を保証する。

## 関連ページ

- [Claude Code](/blogs/wiki/tools/claude-code/) — 代表的な AI コーディングエージェント
- [ハーネスエンジニアリング](/blogs/wiki/concepts/harness-engineering/) — エージェント品質保証の設計パターン
- [自己改善エージェント](/blogs/wiki/concepts/self-improving-agents/) — エージェントが自律的に改善するパターン
- [MCP](/blogs/wiki/concepts/mcp/) — エージェントと外部ツールの接続プロトコル

## ソース記事

- [AI エージェント QA 手法](/blogs/posts/2026/03/ai-agent-qa/) — 2026-03
- [Agent Skills ガイド](/blogs/posts/2026/02/agent-skills-guide/) — 2026-02
- [Claude Code Agent Teams](/blogs/posts/2026/03/claude-code-agent-teams/) — 2026-03
- [AutoAgent](/blogs/posts/2026/04/autoagent-self-improving-agents/) — 2026-04
