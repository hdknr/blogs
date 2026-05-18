---
title: "Obsidian"
description: "ローカルファーストの Markdown ベース PKM（個人知識管理）ツール。データはすべて自分のマシンに保存されベンダーロックインなし"
date: 2026-04-23
lastmod: 2026-05-18
aliases: ["オブシディアン", "PKM", "Personal Knowledge Management", "第二の脳"]
related_posts:
  - "/posts/2026/04/obsidian-pkm-second-brain/"
  - "/posts/2026/05/github-vs-obsidian-ai-agent/"
  - "/posts/2026/05/claude-code-obsidian-vault-project-config/"
  - "/posts/2026/05/claude-code-obsidian-vault-writeback/"
  - "/posts/2026/05/claude-code-vault-writeback-automation/"
  - "/posts/2026/05/self-hosted-runner-vault-writeback/"
tags: ["PKM", "ナレッジ管理", "Markdown", "ツール", "Claude Code"]
---

## 概要

Obsidian はローカルファイルベースの Markdown エディタであり、個人の知識管理（PKM）に特化したツール。個人利用は完全無料、データはすべて自分のマシン上の `.md` ファイルとして保存されるため、ベンダーロックインがない。2,700 種以上のコミュニティプラグインが存在する。

## 設計哲学

「Your thoughts are yours（あなたの思考はあなたのもの）」。ローカルファースト・プレーンテキスト・オフライン動作・ベンダーロックインなしを基本原則とする。

## 主な機能

- **バックリンクとグラフビュー**: ノート間の双方向リンクと視覚的な知識マップ
- **Dataview プラグイン**: Markdown ファイルをデータベースとしてクエリ
- **Templater**: 動的テンプレートで繰り返し作業を自動化
- **Canvas**: ホワイトボード的なビジュアル思考ツール
- **AI 連携**: Smart Composer / Copilot プラグインで LLM をノート作成に統合

## 料金

| プラン | 価格 | 用途 |
|---|---|---|
| 個人 | 無料 | 個人利用 |
| Commercial | $50/年 | 商用利用 |
| Sync | $10/月 | デバイス間同期 |
| Publish | $20/月 | Web 公開 |

## AI Agent との統合（Claude Code）

Obsidian Vault は単なるノートアプリではなく、**AI Agent に「個人ナレッジ層」として常時参照させる Markdown 倉庫** として機能する。Claude Code との統合では次のレイヤーで連携する。

- **読み取り**: `.claude/knowledge/` symlink + 読み取り用 MCP (`vault-readonly`)
- **書き戻し（writeback）**: 書き込み用 MCP (`vault-inbox`) で `~/Documents/ObsidianVault/inbox/` にのみ書く
- **自動化**: Claude Code hooks（`PostToolUse` / `Stop`）と GitHub Actions self-hosted runner を組み合わせ、PR マージや日次のタイミングで書き戻しを発火

Vault が AI Agent 越しに自己強化される循環構造を構築できる（[Obsidian Vault Writeback Loop](/blogs/wiki/concepts/obsidian-vault-writeback-loop/) 参照）。

## 関連ページ

- [Obsidian Vault Writeback Loop](/blogs/wiki/concepts/obsidian-vault-writeback-loop/) — Vault と AI Agent を繋ぐ循環設計パターン
- [Claude Code × Obsidian Vault 統合ガイド](/blogs/wiki/guides/claude-code-obsidian-integration/) — 5 段階の実装手順
- [Claude Code](/blogs/wiki/tools/claude-code/) — Vault と連携する AI Agent
- [LLM Wiki パターン](/blogs/wiki/concepts/llm-wiki-pattern/) — Karpathy 提唱の思想的背景

## ソース記事

- [Obsidian 完全ガイド — ローカルファーストで「第二の脳」を構築する](/blogs/posts/2026/04/obsidian-pkm-second-brain/) — 2026-04-17
- [GitHubで全部完結する開発者にObsidianは本当に必要か？](/blogs/posts/2026/05/github-vs-obsidian-ai-agent/) — 2026-05-18
- [Obsidian Vault を Claude Code に繋ぐ実践編](/blogs/posts/2026/05/claude-code-obsidian-vault-project-config/) — 2026-05-18
- [Claude Code から個人 Obsidian Vault に「書き戻す」設計](/blogs/posts/2026/05/claude-code-obsidian-vault-writeback/) — 2026-05-18
- [Obsidian Vault 書き戻しの自動化](/blogs/posts/2026/05/claude-code-vault-writeback-automation/) — 2026-05-18
- [GitHub Actions self-hosted runner で Obsidian Vault 書き戻しを完成させる](/blogs/posts/2026/05/self-hosted-runner-vault-writeback/) — 2026-05-18
