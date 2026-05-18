---
title: "Claude Code × Obsidian Vault 統合ガイド"
description: "個人 Obsidian Vault を Claude Code に繋いで読み書き双方向のナレッジ循環を実装する 5 段階の手順。symlink + MCP + フック + self-hosted runner の組み合わせで構成する"
date: 2026-05-18
lastmod: 2026-05-18
aliases: ["Obsidian Claude Code 統合", "Vault 統合", "AI Agent ナレッジ循環"]
related_posts:
  - "/posts/2026/05/github-vs-obsidian-ai-agent/"
  - "/posts/2026/05/claude-code-obsidian-vault-project-config/"
  - "/posts/2026/05/claude-code-obsidian-vault-writeback/"
  - "/posts/2026/05/claude-code-vault-writeback-automation/"
  - "/posts/2026/05/self-hosted-runner-vault-writeback/"
tags: ["Claude Code", "Obsidian", "MCP", "Hooks", "writeback", "PKM"]
---

## 概要

本ガイドは、個人 Obsidian Vault を Claude Code に統合し、AI Agent が個人ナレッジを **読み取り・書き戻し** の両方向で活用する循環構造を実装する手順をまとめる。シリーズ 5 記事の実装ステップを 5 段階のロードマップに整理した、再現用ピラー（土台）ガイド。

## 5 段階ロードマップ

### ステップ 1: Vault の機密性に対応した接続方式を選ぶ

| 方式 | 接続スコープ | 特徴 |
| --- | --- | --- |
| **A. グローバル MCP** | `-s user` | 全プロジェクト共通。個人プロジェクト中心の人向け |
| **B. プロジェクト local MCP** | `-s local`（デフォルト） | `.claude/settings.local.json` に gitignored で書く。機密プロジェクトに向く |
| **C. symlink** | `.claude/knowledge/` | Vault サブセットを安定パスで取り込む。CLAUDE.md からの参照を一貫させる |

**推奨**: 方式 B + C のハイブリッド。symlink で安定パスを提供し、検索・走査は MCP を使う。

```bash
mkdir -p <proj>/.claude/knowledge
ln -s ~/Documents/ObsidianVault/topics/nextjs <proj>/.claude/knowledge/nextjs
echo ".claude/knowledge/" >> .gitignore

claude mcp add -s local vault-readonly -- \
  npx -y @modelcontextprotocol/server-filesystem ~/Documents/ObsidianVault
```

### ステップ 2: CLAUDE.md と Skills を階層別に配置

- **`~/.claude/CLAUDE.md`**: 全プロジェクト共通の Vault 参照ルール
- **`<proj>/CLAUDE.md`**: プロジェクト固有の参照ポイント（「個人 Vault がない人でも壊れない逃げ道」を明示する）
- **`~/.claude/skills/`**: Vault 横断スキル（`vault-search`, `vault-daily-log`, `summary-back-to-vault`）
- **`<proj>/.claude/skills/`**: プロジェクト固有のワークフロー（`decision-log` など）

### ステップ 3: 書き戻し（writeback）の安全設計

書き込み用 MCP を読み取り用と分離し、**`inbox/` にしか書けない** よう物理隔離する。

```bash
# 読み取り専用ルート
claude mcp add -s local vault-readonly -- \
  npx -y @modelcontextprotocol/server-filesystem ~/Documents/ObsidianVault

# 書き込み用（inbox 限定）
claude mcp add -s local vault-inbox -- \
  npx -y @modelcontextprotocol/server-filesystem ~/Documents/ObsidianVault/inbox
```

permissions で symlink 越しの書き込みも禁止:

```jsonc
{
  "permissions": {
    "deny": [
      "Write(.claude/knowledge/**)",
      "Edit(.claude/knowledge/**)"
    ]
  }
}
```

書き戻しの 3 パターン:

- **`summary-back-to-vault`**（PR 完了時）: 「他プロジェクトでも再利用できそうな知見」だけを inbox に
- **`vault-daily-log`**（日次）: Daily Note に 1〜3 行追記
- **`decision-log`**（ADR 二重書き）: プロジェクト docs と Vault inbox の両方に出力

### ステップ 4: フックでトリガを自動化

[Claude Code Hooks](/blogs/wiki/concepts/claude-code-hooks/) で書き戻しを自動発火させる。`PostToolUse` フックで `gh pr merge` を検出すると、AI Agent に書き戻しを促せる。

```bash
# PostToolUse: PR マージ直後に AI へ書き戻しを促す
if echo "$COMMAND" | grep -qE '^gh pr merge'; then
  echo "[automation hint] /summary-back-to-vault を実行して Vault に書き戻してください。"
fi
```

`Stop` フックで Daily Note の器を自動作成し、AI に中身を書かせる分業も併用可。

### ステップ 5: Self-hosted runner で漏れを拾う

マシン起動中の取りこぼし対策として、self-hosted runner を立てる。Vault・Skills・MCP がフル活用できるため、cloud-hosted Actions より書き戻しの質が高い。

```yaml
on:
  pull_request:
    types: [closed]
jobs:
  writeback:
    if: github.event.pull_request.merged == true
    runs-on: [self-hosted, macos, local-vault]
    steps:
      - uses: actions/checkout@v4
      - run: claude -p "/summary-back-to-vault ..." --max-budget-usd 0.50
```

## 設計原則のまとめ

1. **Vault は gitignored 層で繋ぐ** — Vault パスをリポジトリに残さない
2. **読み取り MCP と書き込み MCP をサーバ単位で分離** — 物理的に書ける範囲を絞る
3. **inbox-first** — AI は `inbox/` にしか書かない。本棚は人間が編集する
4. **書き戻すのはリポジトリに収まらないメタ知識だけ** — コードや設計書はリポジトリへ
5. **フックは器を用意し、AI が中身を書く** — 自動化レイヤーの分業

## 関連ページ

- [Obsidian Vault Writeback Loop](/blogs/wiki/concepts/obsidian-vault-writeback-loop/) — 循環ループの全体設計
- [Claude Code Hooks](/blogs/wiki/concepts/claude-code-hooks/) — フックイベントの一覧と使い分け
- [Obsidian](/blogs/wiki/tools/obsidian/) — Vault の母体
- [Claude Code](/blogs/wiki/tools/claude-code/) — AI Agent 本体
- [MCP](/blogs/wiki/concepts/mcp/) — Vault との接続プロトコル
- [LLM Wiki パターン](/blogs/wiki/concepts/llm-wiki-pattern/) — 前段の思想的背景

## ソース記事

- [GitHubで全部完結する開発者にObsidianは本当に必要か？](/blogs/posts/2026/05/github-vs-obsidian-ai-agent/) — 2026-05-18
- [Obsidian Vault を Claude Code に繋ぐ実践編](/blogs/posts/2026/05/claude-code-obsidian-vault-project-config/) — 2026-05-18
- [Claude Code から個人 Obsidian Vault に「書き戻す」設計](/blogs/posts/2026/05/claude-code-obsidian-vault-writeback/) — 2026-05-18
- [Obsidian Vault 書き戻しの自動化](/blogs/posts/2026/05/claude-code-vault-writeback-automation/) — 2026-05-18
- [GitHub Actions self-hosted runner で Obsidian Vault 書き戻しを完成させる](/blogs/posts/2026/05/self-hosted-runner-vault-writeback/) — 2026-05-18
