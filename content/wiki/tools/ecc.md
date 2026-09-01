---
title: "ECC (Everything Claude Code)"
description: "Claude Code 向けにエージェント68種・スキル286種・フック・MCP設定・AgentShield を網羅したオープンソースの『エージェントハーネスOS』。役割を tools・model の割り当てで強制する設計が特徴"
date: 2026-07-15
lastmod: 2026-09-01
aliases: ["ECC", "Everything Claude Code", "AgentShield"]
related_posts:
  - "/posts/2026/06/everything-claude-code-ecc/"
  - "/posts/2026/09/ecc-everything-claude-code-agent-constraints/"
  - "/posts/2026/04/ecc-instinct-system/"
tags: ["claude-code", "ecc", "agent", "mcp", "hooks", "security", "OSS"]
---

## 概要

ECC（Everything Claude Code、`affaan-m/ECC`）は Claude Code 向けのスキル・エージェント・フック・MCP・ワークフローを網羅した MIT ライセンスの総合コレクション。「エージェントハーネスのオペレーティングシステム」を標榜し、245K 超のスターを獲得（v2.2.0、2026年9月時点）。Claude Code・Codex・Cursor・OpenCode・Gemini・Zed のほか、Qwen・Kimi・CodeBuddy など 10 種類以上のハーネスに対応する。

> リポジトリは `affaan-m/everything-claude-code` から **`affaan-m/ECC` に改称**済み（旧 URL はリダイレクトする）。npm パッケージ名は `ecc-universal` のまま据え置かれている。

## 詳細

### 主要コンポーネント

| 種別 | v2.0.0（2026-06） | v2.2.0（2026-09） |
| --- | --- | --- |
| エージェント | 67 | **68** |
| スキル | 271 | **286** |
| コマンド | 92 | **94**（legacy command shims） |

- **エージェント（68種）**: `planner` / `architect` / `code-reviewer` / `security-reviewer` / `tdd-guide` / `loop-operator` など専門タスク委譲用のサブエージェント。内訳は `*-reviewer` 23 体、`*-build-resolver` 12 体ほか
- **スキル（286種）**: backend/frontend patterns、tdd-workflow、security-review、autonomous-loops、mle-workflow、django-patterns など
- **コマンド（94種）**: 新機能ではなく、従来の `/コマンド` 呼び出しとの互換レイヤー（legacy command shims）
- **フック**: ツールイベントに反応する自動化。`ECC_HOOK_PROFILE`（minimal/standard/strict）で強度を制御
- **ルール（22パック）**: `~/.claude/rules/ecc/` の常時適用ガイドライン（言語別）。プラグイン経由では配布されず手動コピーが必要
- **MCP 設定**: GitHub・Supabase・Vercel・Railway 等のサーバー設定

### 役割を frontmatter で強制する設計

ECC の特徴は数の多さより、`agents/*.md` の frontmatter で各エージェントを縛っている点にある。

**tools — できることの上限**

| 区分 | 体数 | 該当 |
| --- | --- | --- |
| 完全密閉（Write / Edit / Bash なし） | 13 | `planner`、`architect` など判断だけを返す役 |
| Write / Edit なし、Bash あり | 27 | `*-reviewer` 23 体中 21 体 |
| 書き込み可（Write / Edit あり） | 28 | `*-build-resolver` 12 体は例外なく全てここ |

`planner` と `architect` は `tools: Read, Grep, Glob` のみで、実装する手段自体を渡されていない。一方レビュー役の多くは（テスト実行のため）Bash を持つので、権限の壁は計画フェーズほど堅くない。**計画は物理的な制約、レビューは意図の表明**という二段構えになっている。

**model — かけるコストの割り当て**

68 体すべてが `model:` を明示する。opus 4 体（`architect` / `planner` / `spec-miner` / `healthcare-reviewer`）、sonnet 58 体、haiku 6 体（`docs-lookup` / `doc-updater` など機械的な役）。opus の 4 体のうち 2 体は上記の「完全密閉」側に属する。

**Prompt Defense Baseline — 信頼境界**

68 体中 67 体が同一の[プロンプトインジェクション](/blogs/wiki/concepts/prompt-injection/)防御前文を本文冒頭に持つ。役割・人格の変更を拒否する、秘密情報を出力しない、外部から取得したデータを信頼しない、不可視文字や同形異字を疑う、といった内容。サブエージェント 1 体 1 体を独立した信頼境界として扱う設計思想の表れ。

### コンテキスト予算

286 スキルの本文は合計約 257 万文字にのぼるが、[progressive disclosure](/blogs/wiki/concepts/context-rot/) により常時ロードされるのは frontmatter の `name` + `description` だけ。それでも **286 スキル分で約 7.8 万文字（1トークン≒4文字換算で約 2 万トークン相当）**、エージェント 68 体分と合わせて 2 万数千トークンが作業開始前から占有される。

作者自身が「286 スキルを一気に全部入れるのが、いちばん早く悪化する方法」と警告しており、`minimal` プロファイルの説明文も `Low-context Claude Code setup` と明記されている。インストールプロファイルは `minimal` / `core` / `developer` / `security` / `research` / `full` がモジュール単位で定義されている。

### 継続学習（instinct システム）

`continuous-learning-v2` はセッションから学んだパターンを「インスティンクト（instinct）」として保存し将来のセッションで再利用する。`/instinct-status` `/instinct-import` `/instinct-export` `/evolve` で管理する。

### AgentShield — セキュリティ監査

Claude Code の設定（CLAUDE.md / settings.json / MCP / フック / エージェント定義）に潜む脆弱性を検出する。`npx ecc-agentshield scan`（インストール不要）、`--fix` で自動修正、`--opus` で攻撃者・防御者・監査者の3エージェントによる深掘り分析（1282テスト・102ルールの静的解析）。

### インストール

```bash
# npm 経由（Node.js 18 以上）
npx ecc-universal setup

# プロファイルを絞る
npx ecc-universal install --profile minimal --target claude

# 導入後の点検
npx ecc-universal doctor
npx ecc-universal list-installed
```

Claude Code のプラグインとして入れる場合:

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
- [プロンプトインジェクション](/blogs/wiki/concepts/prompt-injection/) — Prompt Defense Baseline が防ごうとしているもの
- [Context Rot（コンテキスト劣化）](/blogs/wiki/concepts/context-rot/) — スキルを入れすぎると起きること

## ソース記事

- [サブエージェントの役割は tools で縛る — ECC の68体を数えて見えた設計と抜け穴](/blogs/posts/2026/09/ecc-everything-claude-code-agent-constraints/) — 2026-09-01（v2.2.0 時点の権限設計の集計）
- [ECC（Everything Claude Code）— 220K スターの Claude Code 最強エコシステムガイド](/blogs/posts/2026/06/everything-claude-code-ecc/) — 2026-06-24（v2.0.0 時点のカタログ全体像）
- [ECC の instinct システム詳解](/blogs/posts/2026/04/ecc-instinct-system/) — 2026-04-26
