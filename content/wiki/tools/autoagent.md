---
title: "AutoAgent"
description: "AI エージェントのハーネスを AI 自身が自律的に改善する Python 製 OSS ライブラリ"
date: 2026-04-06
lastmod: 2026-04-06
aliases: ["autoagent"]
related_posts:
  - "/posts/2026/04/autoagent-self-improving-agents/"
tags: ["agent", "python", "github", "自動最適化"]
---

## 概要

Kevin Gu 氏（Third Layer CTO）が開発した Python 製 OSS ライブラリ。メタエージェントとタスクエージェントの二重構造で、エージェントのハーネス（プロンプト・ツール・オーケストレーション）を自律的に最適化する。24時間の自律最適化で SpreadsheetBench・TerminalBench 世界1位を達成。

## 基本情報

- **GitHub**: [kevinrgu/autoagent](https://github.com/kevinrgu/autoagent)
- **ライセンス**: MIT
- **言語**: Python
- **依存**: Docker, Python 3.10+, uv

## ベンチマーク

| ベンチマーク | スコア | 順位 |
|---|---|---|
| SpreadsheetBench | 96.5% | 1位 |
| TerminalBench（GPT-5スコア） | 55.1% | 1位 |

## プロジェクト構成

```
agent.py          -- ハーネス本体（メタエージェントの編集対象）
program.md        -- メタエージェントへの方針指示（人間が編集）
tasks/            -- 評価タスク（Harbor フォーマット）
```

人間は `program.md` にゴールを書き、`agent.py` の改善はメタエージェントに任せる。

## 関連ページ

- [自己改善エージェント](/blogs/wiki/concepts/self-improving-agents/) — AutoAgent が実装するパターン
- [Claude Code](/blogs/wiki/tools/claude-code/) — メタエージェントの実行環境として利用可能

## ソース記事

- [AutoAgent — AIがAIを育てる自己改善エージェントOSSライブラリ](/blogs/posts/2026/04/autoagent-self-improving-agents/) — 2026-04-05
