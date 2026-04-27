---
title: "Claude Harness"
description: "Claude Code の拡張機構（hooks / permissions / skills / MCP）をワンパッケージで組み込んだ外装プラグイン。v4.0.0 \"Hokage\" で Go ネイティブ化・harness.toml 1 本管理を実現"
date: 2026-04-27
lastmod: 2026-04-27
aliases: ["claude-code-harness", "Claude Code Harness"]
related_posts:
  - "/posts/2026/04/2026-04-14-claude-harness-v4-hokage/"
tags: ["Claude Code", "Claude Harness", "AI開発", "OSS", "Go", "ハーネスエンジニアリング"]
---

## 概要

Claude Code の拡張機構（hooks / permissions / plugin system / skills / MCP）を AI エンジニアが自作で組むと数日かかる設定を、インストール 1 回で手元に落とせる外装プラグイン。GitHub リポジトリ: [Chachamaru127/claude-code-harness](https://github.com/Chachamaru127/claude-code-harness)

Claude Code には強力な拡張機構があるが、`plugin.json` / `hooks.json` / `settings.json` / `.mcp.json` / `.claude-plugin/hooks.json` の 5〜6 本の JSON を整合させながら自律運用のワークフローを組むのは現実的でない。Harness はこれを 1 パッケージで提供する。

## v4.0.0 "Hokage" の主な変更点（2026-04-14）

| 改善点 | Before | After |
|---|---|---|
| フック実行速度 | ~300ms（bash → Node.js → TypeScript 3段ロケット） | ~10ms（Go バイナリ 1 本、**30 倍速**） |
| 設定ファイル数 | 5〜6 本を手動整合 | `harness.toml` 1 本（SSOT） |
| ガードレール R12 | warn | deny + Bash bypass 二重防御 |
| Node.js | 必要 | **不要**（ネイティブバイナリ 3 本で配布） |

### Go ネイティブ化の詳細

- pure-Go SQLite（`modernc.org/sqlite`）採用で Node.js ランタイム要件を完全排除
- `bin/harness` が `hooks.json` から直接呼ばれ、フック 1 回 ~10ms
- `bin/harness sync` で `plugin.json` / `hooks.json` / `settings.json` が全整合

### harness.toml による SSOT

```bash
# harness.toml を書いて
$ bin/harness sync
# plugin.json / hooks.json / settings.json が全て整合
```

### ガードレール強化

- R12（保護ブランチへの直接 push）を `deny` に格上げ
- Claude Code 2.1.98 で発見された Bash permission bypass 2 種をハーネス側で二層目として塞ぐ
- defense in depth: CC 本体が塞いだ穴を Harness が再度塞ぐ構造

## インストール

Claude Code v2.1.92 以上が必要。

```bash
# Claude Code を起動した状態で
/plugin marketplace add Chachamaru127/claude-code-harness
/plugin install claude-code-harness@claude-code-harness-marketplace
/harness-setup

# 更新
/plugin update claude-code-harness
```

インストール後は `/harness-plan` で最初の依頼を指示する。

## 関連ページ

- [Claude Code](/blogs/wiki/tools/claude-code/) — Harness が拡張する対象
- [ハーネスエンジニアリング](/blogs/wiki/concepts/harness-engineering/) — Harness が体現する設計概念
- [マルチエージェント調整パターン](/blogs/wiki/concepts/multi-agent-coordination-patterns/) — Plan → Work → Review の自律運用パターン

## ソース記事

- [Claude Harness v4.0.0 "Hokage" — Go ネイティブ化で 30 倍速、設定が harness.toml 1 本に](/blogs/posts/2026/04/2026-04-14-claude-harness-v4-hokage/) — 2026-04-14
