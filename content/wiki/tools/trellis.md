---
title: "Trellis"
description: "Claude Code などコーディングエージェントにプロジェクトの文脈を永続化させる、AI コーディング向けエンジニアリングフレームワーク"
date: 2026-06-24
lastmod: 2026-06-24
aliases: ["Trellis", "mindfold-ai/Trellis"]
related_posts:
  - "/posts/2026/06/trellis-claude-code-project-brain/"
tags: ["trellis", "Claude Code", "AIエージェント", "開発ワークフロー", "spec-driven"]
---

## 概要

Trellis（[mindfold-ai/Trellis](https://github.com/mindfold-ai/Trellis)）は、AI コーディングのためのエンジニアリングフレームワーク。プロジェクト内に `.trellis/` ディレクトリを作り、要件・規約・タスク・進捗・作業ログをリポジトリに永続化する。これにより Claude Code などのエージェントは、セッションをまたいで失われがちな文脈を毎回ゼロから説明されることなく把握できる。「賢いが健忘症のプログラマ」を「AI 開発チーム」に変える、と表現される。

## 詳細

### `.trellis/` ディレクトリ（プロジェクトの脳）

- `.trellis/spec/` — 再利用される規約・パターン・ガイド。毎セッション自動で文脈注入される
- `.trellis/tasks/` — タスクごとの PRD（要件定義）・実装/レビュー用コンテキスト・進捗ステータス
- `.trellis/workspace/` — セッションをまたいで文脈を保つ作業ジャーナル

これらはリポジトリにコミットされる通常のファイルで、チーム共有・Git 履歴・レビューが可能。AI の「記憶」を属人的なチャット履歴ではなくバージョン管理された資産として扱える。

### 4 フェーズのワークフロー・ループ

1. **Plan** — 要件を分析し `prd.md` に実装計画を書き出す（`trellis-brainstorm` / `trellis-research`）
2. **Implement** — 計画に沿ってコードを生成（`trellis-implement`、この時点では commit しない）
3. **Verify** — diff をレビューし lint・型チェック・テストを実行（`trellis-check`）
4. **Finish** — 得られた学びを `.trellis/spec/` に書き戻す（使うほど賢くなる）

### 導入

- 前提: Node.js ≥ 18.17.0（ワークフローのユーティリティが Python ≥ 3.9 を利用）
- インストール: `npm install -g @mindfoldhq/trellis@latest`
- 初期化: `trellis init -u your-name`
- Claude Code 以外に Cursor・Codex・OpenCode など複数プラットフォームに対応（マルチプラットフォーム設計）
- ライセンス: AGPL-3.0

## 関連ページ

- [Claude Code](/blogs/wiki/tools/claude-code/)
- [ハーネスエンジニアリング](/blogs/wiki/concepts/harness-engineering/)
- [Vibe Coding](/blogs/wiki/concepts/vibe-coding/)

## ソース記事

- [Claude Code は『賢いが健忘症のプログラマ』— Trellis でプロジェクトの脳を持たせる](/blogs/posts/2026/06/trellis-claude-code-project-brain/) — 2026-06-19
