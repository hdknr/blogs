---
title: "Graphite"
description: "スタックドPR・マージキュー・AI コードレビューで AI ファースト開発を加速する GitHub PR ワークフロー拡張プラットフォーム"
date: 2026-04-23
lastmod: 2026-04-23
aliases: ["グラファイト", "スタックドPR", "Graphite Agent"]
related_posts:
  - "/posts/2026/04/2026-04-19-graphite-stacked-prs-merge-queue/"
tags: ["開発ツール", "GitHub", "CI/CD", "AI コードレビュー", "ハーネスエンジニアリング"]
---

## 概要

Graphite は GitHub 上の PR ワークフローを拡張する開発者プラットフォーム。2025年3月に Anthropic から $52M の Series B を調達。元 Airbnb・Meta エンジニア出身チームが、Meta 内部ツール（Phabricator/Sapling）のスタック開発体験を GitHub に持ち込んだ。AI が大量に PR を量産する「AI ファースト開発」環境での詰まりを解消する。

## 3本柱

### 1. スタックドPR

大きな変更を依存関係のある小さな PR の連鎖に分割する。DB スキーマ→API→認証ミドルウェアのような依存チェーンを独立した PR として管理し、レビュアーの認知負荷を下げる。

```bash
gt stack   # 現在のスタック状態を確認
gt submit  # スタック全体を一括 PR 作成
gt sync    # main の変更を全 PR にリベース
```

### 2. マージキュー（スタック対応）

スタックの依存関係を理解した上で main へのマージを直列化。CI が通ったものから順番にマージされるため、コンフリクトなしに高頻度デプロイが可能になる。

### 3. Graphite Agent（旧 Diamond）

AI によるコードレビューと対話的修正。差分を理解した上でコメントし、Chat で修正まで完結できる。

## AI ファースト開発との相性

CreaoAI の事例では、Graphite 採用により 25 名チームで 6 週間のリリースサイクルを 1 日に短縮。AI エージェントが量産した PR をマージキューで管理することで、人間のレビュー待ち時間を排除した。

## 関連ページ

- [ハーネスエンジニアリング](/blogs/wiki/concepts/harness-engineering/)
- [AI エージェント](/blogs/wiki/concepts/ai-agent/)

## ソース記事

- [Graphite 徹底解説 — スタックドPRとマージキューがAIファースト開発を加速する理由](/blogs/posts/2026/04/2026-04-19-graphite-stacked-prs-merge-queue/) — 2026-04-19
