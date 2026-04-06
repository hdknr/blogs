---
title: "ハーネスエンジニアリング"
description: "AI エージェントの出力品質を保証する設計パターン。検証層・制約層・フィードバック層で構成"
date: 2026-04-06
lastmod: 2026-04-06
aliases: ["Harness Engineering"]
related_posts:
  - "/posts/2026/03/harness-engineering/"
  - "/posts/2026/03/ai-agent-qa/"
  - "/posts/2026/03/claude-code-review/"
tags: ["agent", "品質保証", "CLAUDE.md", "設計パターン"]
---

## 概要

AI エージェント全盛時代に必須の設計手法。CLAUDE.md（入力層）、MEMORY.md（実行記録層）、Hooks（検証層）、Agent Skills（ワークフロー層）の4層で AI 出力の品質を決定論的に保証する。Anthropic 公式の推奨パターン。

## 4層構造

| 層 | 役割 | 実装 |
|---|---|---|
| 入力層 | AI への指示・制約 | CLAUDE.md |
| 記録層 | 学習・実行履歴 | MEMORY.md |
| 検証層 | 出力の事前/事後チェック | Hooks (PreToolUse/PostToolUse) |
| ワークフロー層 | 構造化タスク定義 | Agent Skills (SKILL.md) |

## 関連ページ

- [AI エージェント](/blogs/wiki/concepts/ai-agent/) — ハーネスで品質保証される対象
- [Claude Code](/blogs/wiki/tools/claude-code/) — ハーネスエンジニアリングの主要実装環境
- [自己改善エージェント](/blogs/wiki/concepts/self-improving-agents/) — ハーネス自体を AI が改善するパターン

## ソース記事

- [ハーネスエンジニアリング](/blogs/posts/2026/03/harness-engineering/) — 2026-03
- [AI エージェント QA 手法](/blogs/posts/2026/03/ai-agent-qa/) — 2026-03
