---
title: "ハーネスエンジニアリング"
description: "AI エージェントの出力品質を保証する設計パターン。検証層・制約層・フィードバック層で構成"
date: 2026-04-06
lastmod: 2026-04-14
aliases: ["Harness Engineering"]
related_posts:
  - "/posts/2026/03/harness-engineering/"
  - "/posts/2026/03/ai-agent-qa/"
  - "/posts/2026/03/claude-code-review/"
  - "/posts/2026/04/anthropic-vs-openai-harness-strategy/"
  - "/posts/2026/04/agent-harness-memory-lock-in/"
tags: ["agent", "品質保証", "CLAUDE.md", "設計パターン", "ロックイン"]
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

## Anthropic vs OpenAI のハーネス戦略

両社はともにハーネスの重要性を認識しているが、アプローチが対照的だ。

| 観点 | OpenAI | Anthropic |
|------|--------|-----------|
| ハーネスの位置づけ | エンジニアが設計する環境（Harness Engineering） | プラットフォームが提供する基盤（Managed Agent） |
| 人間の役割 | プロジェクトマネージャー | AI との協働者 |
| 製品 | Codex + Symphony | Claude Code + Managed Agent |

OpenAI は AI がソフトウェア開発を全面的に担う方向を目指し、Anthropic はエージェント実行基盤を「Agent OS」としてプラットフォーム化している。

## ハーネスとメモリのロックイン

LangChain 創設者 Harrison Chase が指摘する通り、ハーネスとメモリは不可分だ。メモリはコンテキストの一形態であり、ハーネスの中核的な責任。クローズドなハーネスを使うことは、以下の4層すべての管理を第三者に委ねることを意味する:

1. **コンテキストウィンドウ内のメッセージ履歴** — 構成方法でモデルの応答が変わる
2. **コンパクション（会話の要約圧縮）** — 何を残し何を捨てるかでエージェントの「記憶の質」が変わる
3. **永続ファイル・データベース（長期メモリ）** — エージェントの「人格」を形成する
4. **設定・スキルのロード方式** — エージェントの能力を規定する

## 関連ページ

- [AI エージェント](/blogs/wiki/concepts/ai-agent/) — ハーネスで品質保証される対象
- [エージェントメモリのロックイン](/blogs/wiki/concepts/agent-memory-lock-in/) — ハーネスとメモリの不可分性とロックインリスク
- [Claude Code](/blogs/wiki/tools/claude-code/) — ハーネスエンジニアリングの主要実装環境
- [Claude Managed Agents](/blogs/wiki/tools/claude-managed-agents/) — Anthropic のマネージドハーネス
- [自己改善エージェント](/blogs/wiki/concepts/self-improving-agents/) — ハーネス自体を AI が改善するパターン

## ソース記事

- [ハーネスエンジニアリング](/blogs/posts/2026/03/harness-engineering/) — 2026-03
- [AI エージェント QA 手法](/blogs/posts/2026/03/ai-agent-qa/) — 2026-03
- [Anthropic vs OpenAI：Harness 戦略はなぜ真逆なのか](/blogs/posts/2026/04/anthropic-vs-openai-harness-strategy/) — 2026-04-13
- [エージェントハーネスとメモリのロックイン問題](/blogs/posts/2026/04/agent-harness-memory-lock-in/) — 2026-04-12
