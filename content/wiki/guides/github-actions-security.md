---
title: "GitHub Actions スクリプトインジェクション対策"
description: "GitHub Actions で ${{ }} テンプレート式の不適切な使用による攻撃を防ぐガイド"
date: 2026-04-06
lastmod: 2026-04-06
related_posts:
  - "/posts/2026/03/github-actions-script-injection-complete-guide/"
  - "/posts/2026/03/github-actions-script-injection-untrusted-input/"
tags: ["GitHub Actions", "CI/CD", "セキュリティ"]
---

## 概要

`${{ }}` テンプレート式はシェル起動前に展開されるため、攻撃者制御のコンテキスト（PR タイトル・ブランチ名・Issue 本文）をそのまま `run` に埋め込むとコマンドインジェクション成立。

## 対策

- `env` で環境変数に渡して `${VAR}` で参照
- actionlint・zizmor で自動検出
- サードパーティ Actions はコミットハッシュでピン留め

## ソース記事

- [GitHub Actions スクリプトインジェクション完全ガイド](/blogs/posts/2026/03/github-actions-script-injection-complete-guide/) — 2026-03
- [信頼できない入力の扱い](/blogs/posts/2026/03/github-actions-script-injection-untrusted-input/) — 2026-03
