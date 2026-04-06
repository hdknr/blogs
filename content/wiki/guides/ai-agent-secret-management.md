---
title: "AI エージェント時代のシークレット管理"
description: "AI エージェントが平文の .env にアクセスする問題への対策ガイド"
date: 2026-04-06
lastmod: 2026-04-06
related_posts:
  - "/posts/2026/03/1password-unified-access-ai-agent/"
tags: ["セキュリティ", "シークレット管理", "AI エージェント", "1Password"]
---

## 概要

AI エージェント（Claude Code、Cursor）はローカルの .env から平文で API キーを読み込む。1Password Unified Access は just-in-time シークレット供給でメモリ上でのみ提供。スコープ付きクレデンシャルと MCP 連携で実現。

## 関連ページ

- [Claude Code](/blogs/wiki/tools/claude-code/) — シークレット管理が必要な環境
- [プロンプトインジェクション](/blogs/wiki/concepts/prompt-injection/) — シークレット漏洩につながる攻撃

## ソース記事

- [1Password Unified Access](/blogs/posts/2026/03/1password-unified-access-ai-agent/) — 2026-03
