---
title: "GitHub Actions スクリプトインジェクション対策"
description: "GitHub Actions で ${{ }} テンプレート式の不適切な使用による攻撃を防ぐガイド"
date: 2026-04-06
lastmod: 2026-11-17
related_posts:
  - "/posts/2026/03/1e29bea3f9f5cdf4a2b11eec4a2ab536/"
  - "/posts/2026/03/5bbdc7bd98ff0dbdfde257d909d48d8c/"
  - "/posts/2026/03/2fb1416daa8c7baf370c69d0b1649625/"
tags: ["GitHub Actions", "CI/CD", "セキュリティ"]
---

## 概要

`${{ }}` テンプレート式はシェル起動前に展開されるため、攻撃者制御のコンテキスト（PR タイトル・ブランチ名・Issue 本文）をそのまま `run` に埋め込むとコマンドインジェクション成立。

## 対策

- `env` で環境変数に渡して `${VAR}` で参照
- actionlint・zizmor で自動検出
- サードパーティ Actions はコミットハッシュでピン留め

