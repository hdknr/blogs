---
title: "Obsidian Vault Writeback Loop"
description: "AI Agent と個人ナレッジを循環させる設計パターン。Vault から AI に文脈を渡し、得た学びを Vault に書き戻すループを構成する"
date: 2026-05-18
lastmod: 2026-05-18
aliases: ["Vault 書き戻し", "ナレッジ循環ループ", "writeback loop", "PKM フィードバックループ"]
related_posts:
  - "/posts/2026/05/github-vs-obsidian-ai-agent/"
  - "/posts/2026/05/claude-code-obsidian-vault-project-config/"
  - "/posts/2026/05/claude-code-obsidian-vault-writeback/"
  - "/posts/2026/05/claude-code-vault-writeback-automation/"
  - "/posts/2026/05/self-hosted-runner-vault-writeback/"
tags: ["Obsidian", "Claude Code", "PKM", "writeback", "ナレッジマネジメント"]
---

## 概要

Obsidian Vault Writeback Loop は、AI Agent が個人ナレッジ（Obsidian Vault）を **読み取るだけでなく、得た学びをそこに書き戻して自己強化する** 循環設計パターン。GitHub リポジトリに閉じた知識管理（プロジェクト型）に対して、Vault を中心に据えたネットワーク型のナレッジ管理を、Claude Code のフック・スキル・MCP・GitHub Actions self-hosted runner を組み合わせて実装する。

## 4 つの構成レイヤー

| レイヤー | 役割 | 主な構成要素 |
| --- | --- | --- |
| **読み取り** | Vault → AI Agent への文脈供給 | symlink (`.claude/knowledge/`) + 読み取り用 MCP (`vault-readonly`) |
| **書き戻し設計** | AI Agent → Vault inbox への安全な投入 | 書き込み用 MCP (`vault-inbox`)、inbox-first 原則 |
| **書き戻しトリガ** | いつ書き戻すかの発火制御 | Claude Code hooks（`PostToolUse` / `Stop` / `SessionEnd`）、Git `post-merge` |
| **昇格** | inbox → Vault 本体への統合 | 人間による週次レビュー（4 択フロー: 昇格 / 追記 / 保留 / 破棄） |

## 設計原則

1. **AI に Vault 正本を直接書かせない**: リンク構造を壊さないよう、`inbox/` にしか書かない
2. **読み取り MCP と書き込み MCP をサーバ単位で分離**: `@modelcontextprotocol/server-filesystem` は引数で渡したディレクトリしか公開しないため、サーバを分けるだけで構造的な物理隔離になる
3. **CLAUDE.md には安定パス（`.claude/knowledge/`）を書く**: Vault の生パスをコミットしない
4. **昇格判断は人間に残す**: AI に自動昇格させると Vault が壊れる
5. **書き戻し対象はリポジトリに収まらない知見だけ**: コードや設計書はリポジトリの `docs/` に置く

## 自動化レイヤーの段階導入

1. Claude Code `PostToolUse` フック — `gh pr merge` 直後に書き戻しを促す
2. Claude Code `Stop` フック — Daily Note の器を自動作成
3. Git `post-merge` フック — GitHub UI マージ派の取りこぼし回収
4. **Self-hosted runner + GitHub Actions** — マシン起動中なら必ず走る最後の砦（Vault・Skills・MCP がフル活用可能）

cloud-hosted Actions は Vault に書けない・Skills が使えない・会話文脈ゼロという三重苦のため、書き戻し用途では self-hosted runner に切り替えるのが正解。

## なぜループを閉じることが重要か

読み取り側だけ設定しても、Vault は「過去の自分のノート集」のスナップショットに固定される。書き戻し側を実装して初めて、AI Agent が「3 ヶ月前に別プロジェクトで試したあの技術、いまのバグに応用できるか？」という **プロジェクトを跨いだ伏線回収** を提案できるようになる。Vault が時間とともに自己強化される構造は、ループを閉じた瞬間に立ち上がる。

## 関連ページ

- [Obsidian](/blogs/wiki/tools/obsidian/) — Vault の母体となる PKM ツール
- [Claude Code](/blogs/wiki/tools/claude-code/) — 書き戻しを駆動する AI Agent
- [MCP](/blogs/wiki/concepts/mcp/) — Vault との接続プロトコル
- [Claude Code Hooks](/blogs/wiki/concepts/claude-code-hooks/) — 書き戻しの自動トリガ
- [LLM Wiki パターン](/blogs/wiki/concepts/llm-wiki-pattern/) — Karpathy 提唱の前段思想
- [Claude Code × Obsidian 統合ガイド](/blogs/wiki/guides/claude-code-obsidian-integration/) — 5 段階の実装手順

## ソース記事

- [GitHubで全部完結する開発者にObsidianは本当に必要か？](/blogs/posts/2026/05/github-vs-obsidian-ai-agent/) — 2026-05-18（思想・選定編）
- [Obsidian Vault を Claude Code に繋ぐ実践編](/blogs/posts/2026/05/claude-code-obsidian-vault-project-config/) — 2026-05-18（読み取り側）
- [Claude Code から個人 Obsidian Vault に「書き戻す」設計](/blogs/posts/2026/05/claude-code-obsidian-vault-writeback/) — 2026-05-18（書き戻し設計）
- [Obsidian Vault 書き戻しの自動化](/blogs/posts/2026/05/claude-code-vault-writeback-automation/) — 2026-05-18（フック自動化）
- [GitHub Actions self-hosted runner で Obsidian Vault 書き戻しを完成させる](/blogs/posts/2026/05/self-hosted-runner-vault-writeback/) — 2026-05-18（self-hosted runner）
