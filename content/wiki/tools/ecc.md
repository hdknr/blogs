---
title: "ECC (Everything Claude Code)"
description: "Claude Code 向けにエージェント67種・スキル271種・フック・MCP設定・AgentShield を網羅したオープンソースの『エージェントハーネスOS』"
date: 2026-07-15
lastmod: 2026-07-15
aliases: ["ECC", "Everything Claude Code", "AgentShield"]
related_posts:
  - "/posts/2026/06/everything-claude-code-ecc/"
tags: ["claude-code", "ecc", "agent", "mcp", "hooks", "security", "OSS"]
---

## 概要

ECC（Everything Claude Code、`affaan-m/ECC`）は Claude Code 向けのスキル・エージェント・フック・MCP・ワークフローを網羅した MIT ライセンスの総合コレクション。「エージェントハーネスのオペレーティングシステム」を標榜し、220K 超のスターを獲得（v2.0.0、2026年6月）。Claude Code・Codex・Cursor・OpenCode・Gemini・Zed・GitHub Copilot に対応する。

## 詳細

### 主要コンポーネント

- **エージェント（67種）**: `planner` / `architect` / `code-reviewer` / `security-reviewer` / `tdd-guide` / `loop-operator` など専門タスク委譲用のサブエージェント
- **スキル（271種）**: backend/frontend patterns、tdd-workflow、security-review、autonomous-loops、mle-workflow、django-patterns など
- **フック**: ツールイベントに反応する自動化。`ECC_HOOK_PROFILE`（minimal/standard/strict）で強度を制御
- **ルール**: `~/.claude/rules/ecc/` の常時適用ガイドライン（言語別）。プラグイン経由では配布されず手動コピーが必要
- **MCP 設定**: GitHub・Supabase・Vercel・Railway 等のサーバー設定

### 継続学習（instinct システム）

`continuous-learning-v2` はセッションから学んだパターンを「インスティンクト（instinct）」として保存し将来のセッションで再利用する。`/instinct-status` `/instinct-import` `/instinct-export` `/evolve` で管理する。

### AgentShield — セキュリティ監査

Claude Code の設定（CLAUDE.md / settings.json / MCP / フック / エージェント定義）に潜む脆弱性を検出する。`npx ecc-agentshield scan`（インストール不要）、`--fix` で自動修正、`--opus` で攻撃者・防御者・監査者の3エージェントによる深掘り分析（1282テスト・102ルールの静的解析）。

### インストール

```text
/plugin marketplace add https://github.com/affaan-m/ECC
/plugin install ecc@ecc
```

プラグイン経由と手動インストールの重複は動作の二重化を招くので避ける。

## 関連ページ

- [Claude Code](/blogs/wiki/tools/claude-code/) — ECC が拡張する対象環境
- [ハーネスエンジニアリング](/blogs/wiki/concepts/harness-engineering/) — ECC が体現するハーネス設計の思想
- [Claude Code Hooks](/blogs/wiki/concepts/claude-code-hooks/) — フックの仕組み
- [自律改善システムの設計](/blogs/wiki/concepts/autonomous-system-design/) — autonomous-loops スキルと関連

## ソース記事

- [ECC（Everything Claude Code）— 220K スターの Claude Code 最強エコシステムガイド](/blogs/posts/2026/06/everything-claude-code-ecc/) — 2026-06-24
