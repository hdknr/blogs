---
title: "dmux"
description: "AI エージェント（Claude Code / Codex 等）の並列実行を安全に管理するツール。git worktree + branch の自動隔離でファイル競合を防ぐ"
date: 2026-04-15
lastmod: 2026-04-15
aliases: ["dmux", "AI エージェント並列実行"]
related_posts:
  - "/posts/2026/04/2026-04-15-dmux-parallel-ai-agents/"
tags: ["dmux", "Claude Code", "git worktree", "AI エージェント", "並列実行"]
---

## 概要

Claude Code や OpenAI Codex などの AI コーディングエージェントを並列実行する際に発生しがちなファイル競合問題を解決するツール。内部で **git worktree + branch の自動隔離**を行い、各エージェントが独立した環境で作業できるようにする。

## 背景：並列実行の課題

ターミナルを複数開いたり tmux でペインを分割して AI エージェントを並列実行すると、すべてのエージェントが同一のワーキングディレクトリを共有するため:

- **共通ファイルの同時上書き** — 複数エージェントが同じファイルを編集し、片方の変更が消える
- **変更の消失** — あるエージェントが直したコードを別のエージェントが元に戻す

dmux はこれらの問題を git worktree の仕組みで自動解決する。

## 主な機能

| 機能 | 説明 |
|------|------|
| 自動隔離 | エージェントごとに git worktree + ブランチを自動作成 |
| 衝突の自動解決 | マージ競合を AI が自動解決 |
| エージェント切り替え | Claude Code、Codex、Opus、Composer 等を簡単に切り替え |
| A/B テスト | 複数エージェントの出力を並べて比較検証 |

## git worktree による隔離の仕組み

```
リポジトリ
├── (メインディレクトリ)   ← ブランチ: main
├── .worktrees/agent-1/   ← ブランチ: agent/task-a  ← エージェント1
└── .worktrees/agent-2/   ← ブランチ: agent/task-b  ← エージェント2
```

git worktree は同一リポジトリを複数ディレクトリに展開する Git 標準機能。各エージェントが別ブランチで動くため、同一ファイルへの同時書き込みが発生しない。dmux はこの仕組みを自動化する。

## 関連ページ

- [Claude Code](/blogs/wiki/tools/claude-code/) — dmux の主要対象エージェント
- [マルチエージェント調整パターン](/blogs/wiki/concepts/multi-agent-coordination-patterns/) — 複数エージェント協調の設計パターン

## ソース記事

- [dmux：Claude Code / Codex を安全に並列実行するための git worktree 管理ツール](/blogs/posts/2026/04/2026-04-15-dmux-parallel-ai-agents/) — 2026-04-15
