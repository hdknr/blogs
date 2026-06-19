---
title: "oh-my-openagent"
description: "Claude Code・Codex・Gemini CLI を統合管理する TypeScript 製マルチエージェントハーネス。Team Mode で最大 8 並列実行、ulw コマンドで自律実行に対応"
date: 2026-05-20
lastmod: 2026-05-20
aliases: ["omo", "oh-my-opencode", "openagent"]
related_posts:
  - "/posts/2026/05/oh-my-openagent-multi-ai-agent-harness/"
tags: ["oh-my-openagent", "agent", "Claude Code", "Codex", "Gemini CLI", "harness"]
---

## 概要

oh-my-openagent（omo）は、**Claude Code・OpenAI Codex・Gemini CLI** といった複数のコーディングエージェントを一元管理し、タスクに応じて最適なモデルへ自動ルーティングする TypeScript 製ハーネス。元は **oh-my-opencode** という名称で 2025 年 12 月にリリースされ、後にマルチエージェント対応強化に伴いリブランド。GitHub スター数は 5.7 万超（2026 年 5 月時点）。

- **作者**: code-yeongyu
- **GitHub**: [code-yeongyu/oh-my-openagent](https://github.com/code-yeongyu/oh-my-openagent)
- **公式**: [ohmyopenagent.com](https://ohmyopenagent.com/)
- **ライセンス**: SUL-1.0

## 主要機能

- **エージェント自動ルーティング**: タスク内容を解析して Claude Code / Codex / Gemini CLI から最適なモデルを選択
- **Team Mode**: 最大 8 並列で複数エージェントを同時実行
- **`ulw` コマンド**: ユーザーの介入なしに長時間自律実行する「ultraloop」モード
- 単一エージェントに丸投げするのではなく、**専門化されたエージェント群がタスクを分担**して品質と速度を両立する設計

## 関連ページ

- [Claude Code](/blogs/wiki/tools/claude-code/) — 主要対応エージェント
- [Claude Harness](/blogs/wiki/tools/claude-harness/) — ハーネス概念
- [Harness Engineering](/blogs/wiki/concepts/harness-engineering/) — ハーネス設計の概念
- [Multi-Agent Coordination Patterns](/blogs/wiki/concepts/multi-agent-coordination-patterns/) — マルチエージェント連携

## ソース記事

- [oh-my-openagent — Claude Code・Codex・Gemini CLI を統合管理する AIエージェントハーネス（★5.7万）](/blogs/posts/2026/05/oh-my-openagent-multi-ai-agent-harness/) — 2026-05-11
