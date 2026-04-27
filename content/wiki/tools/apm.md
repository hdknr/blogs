---
title: "APM（Agent Package Manager）"
description: "AI エージェントの設定（スキル・プロンプト・MCP サーバーなど）を apm.yml で宣言的に管理・共有する Microsoft 製 OSS ツール"
date: 2026-04-23
lastmod: 2026-04-23
aliases: ["Agent Package Manager", "エージェントパッケージマネージャー"]
related_posts:
  - "/posts/2026/04/2026-04-17-apm-agent-package-manager/"
tags: ["AI エージェント", "Claude Code", "開発ツール", "パッケージ管理"]
---

## 概要

APM（Agent Package Manager）は Microsoft がオープンソースで開発している AI エージェント向けの依存関係マネージャー。`npm` や `pip` がライブラリを管理するように、APM はエージェントが必要とするコンテキスト（スキル・プロンプト・プラグイン・MCP サーバーなど）を `apm.yml` に宣言して管理する。

プロジェクトに `apm.yml` を 1 つ置くだけで、リポジトリをクローンした全員が同じエージェント環境を即座に再現できる。

## 対応エージェント

GitHub Copilot、Claude Code、Cursor、OpenCode、Codex CLI

## 解決する問題

AI コーディングエージェントのセットアップは現状、開発者が各自で手動で行うため移植性も再現性もない。APM で宣言的管理することでチーム全員が同一環境を共有できる。

## 関連ページ

- [Claude Code](/blogs/wiki/tools/claude-code/)
- [AI エージェント](/blogs/wiki/concepts/ai-agent/)

## ソース記事

- [APM（Agent Package Manager）— AI エージェント設定を npm のように管理するツール](/blogs/posts/2026/04/2026-04-17-apm-agent-package-manager/) — 2026-04-17
