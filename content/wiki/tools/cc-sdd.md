---
title: "cc-sdd"
description: "Kiro に着想を得た MIT ライセンスの仕様駆動開発ツール。Claude Code・Codex などに 17 個の /kiro-* スキルを入れ、requirements.md・design.md・tasks.md を作ってから、実装役とレビュー役のサブエージェントで TDD を回す"
date: 2026-11-15
lastmod: 2026-11-15
aliases: ["cc-sdd", "gotalab/cc-sdd", "kiro-discovery", "kiro-impl", "Kiro スタイル"]
related_posts:
  - "/posts/2026/11/cc-sdd-intro/"
  - "/posts/2026/11/cc-sdd-coderabbit-takumi-guard-ai-dev-flow/"
  - "/posts/2026/11/spec-driven-development-overview/"
tags: ["cc-sdd", "仕様駆動開発", "SDD", "claude-code", "Kiro", "Agent Skills"]
---

## 概要

**cc-sdd**（[gotalab/cc-sdd](https://github.com/gotalab/cc-sdd)）は、AI コーディングエージェントに [仕様駆動開発](/blogs/wiki/concepts/spec-driven-development/) の進め方を持ち込む MIT ライセンスのツールである。[Kiro](/blogs/wiki/tools/kiro/) に着想を得ており、Kiro と同じ `requirements.md` / `design.md` / `tasks.md` を作ってから実装する流れを、IDE を替えずに Claude Code や Codex で回せる（既存の Kiro の仕様とも互換）。リポジトリは自らを「承認した仕様を長時間の自律的な実装に変える、最小限で適応しやすい SDD のハーネス」と説明する。

v3.0 から Agent Skills として配布され、どのエージェントにも同じ 17 個のスキルを入れる。文書は日本語を含む 14 言語で生成できる。

## 詳細

### 導入

```bash
npx cc-sdd@latest --claude-skills --lang ja            # Claude Code 用・日本語
npx cc-sdd@latest --codex-skills --lang ja             # Codex 用
npx cc-sdd@latest --claude-skills --lang ja --dry-run  # 書き込まずに確認
npx cc-sdd@latest --claude-skills --kiro-dir docs      # 仕様の置き場所を変える
```

安定版は Claude Code（`--claude-skills`）と Codex（`--codex-skills`）だけで、Cursor・GitHub Copilot・Devin・OpenCode・Gemini CLI・Antigravity はベータ。安定度は統合の成熟度で、ベータでは自律実装のループが最後まで回るとは限らないので、小さな機能で確かめてから使う。

### スキルの流れ

基本は `/kiro-discovery` → `/kiro-spec-init` → `/kiro-spec-requirements` → `/kiro-spec-design` → `/kiro-spec-tasks` → `/kiro-impl` で、各段階は人間のレビューのために止まる。

| スキル | 役割 |
|---|---|
| `/kiro-discovery` | 入口。作業の種類を見分けて `brief.md`（必要なら `roadmap.md`）を書き、次のスキルを示して止まる |
| `/kiro-spec-init` | `.kiro/specs/<機能名>/` を作る |
| `/kiro-spec-requirements` | 確認の質問を集めて `requirements.md` を作る |
| `/kiro-spec-design` | 必要なら `research.md` で調べ、`design.md` を作る |
| `/kiro-spec-tasks` | `tasks.md` を作る。並行可能なタスクに `(P)` |
| `/kiro-impl` | 承認したタスクを実装する |
| `/kiro-steering` | プロジェクト全体の規約・構成を `.kiro/steering/` に |
| `/kiro-validate-gap` | 既存コードと要件の差を分析（任意） |
| `/kiro-validate-impl` | タスクをまたぐ結合検証。GO / NO-GO / MANUAL_VERIFY_REQUIRED |
| `/kiro-spec-batch` | 大きな取り組みで、依存順に複数の仕様をまとめて作る |

目的別には、既存システムの拡張は `/kiro-steering` から、大きな取り組みは `/kiro-discovery` → `/kiro-spec-batch`、**小さな変更は `/kiro-discovery` からそのまま実装**する。discovery が依頼の規模や既存仕様の有無で「直接実装」「既存の仕様を拡張」「新しい仕様を作る」に振り分ける点が、重いループに小さな依頼まで乗せないための入口になっている。

### 文書の書き方

- `requirements.md`：要件と受け入れ基準を [EARS](/blogs/wiki/concepts/ears/) で書く。日本語でも When・If・While・Where・The system shall のキーワードは英語のまま
- `design.md`：Mermaid 図を含むアーキテクチャと File Structure Plan
- `tasks.md`：`- [ ]` のチェックボックスに `_Requirements:_`（対応要件）、`(P)`（並行可）、`_Boundary:_`（並行タスクが触ってよい範囲）、`_Depends:_`（自明でない依存）を付ける

テンプレートと生成ルール（EARS の書式・設計の原則・タスクの作り方）は `.kiro/settings/` にあり、チームの書き方に合わせて編集できる。

### `/kiro-impl` の進め方

サブエージェントを持つツールでは、タスクごとに新しい実装役を立て、別のレビュー役が確かめる（v3.0 以前は外部の Ralph Loop に頼っていた）。

| 役 | すること |
|---|---|
| 実装役 | TDD（RED → GREEN）で実装する |
| レビュー役 | `git diff`、TODO の残り、テスト実行、タスク範囲の逸脱を確かめる |
| デバッグ役 | 実装役が行き詰まるか、レビュー役が 2 回差し戻したときに呼ばれる（1 タスク最大 2 回） |

1 回に 1 タスクずつ進めて進捗を `tasks.md` に記録し、学びは「Implementation Notes」に残して後のタスクに渡す。完了報告の前に内部スキル `kiro-verify-completion` がテスト結果などの根拠を確かめ直す。`(P)` のタスクに `_Boundary:_` を書いておくと、レビュー役が範囲外の変更を見つけられる。

### 開発フローに組み込んだ事例

非エンジニアの社長が Claude Code で作った巨大 PR を受け止めるため、cc-sdd を軸に全員が同じプロセスを通るようにした事例がある。要件定義・設計・レビュアー・実装を別エージェントにし、計画が終わった時点で PR を作って CTO がレビューしてから実装に入る。PR では [CodeRabbit](/blogs/wiki/concepts/code-review-alternatives/) が別系統でレビューし、[Takumi Guard](/blogs/wiki/tools/takumi-guard/) が悪性パッケージを止め、司令塔エージェントが作業とレビューのループを回す。仕様を「エージェントへの命令書」ではなく**部品同士の契約**として扱い、人間はフェーズごとのゲートで承認する。ドメイン知識はあってもアーキテクチャの前提を知らない人のコードも、仕様と設計のフェーズを通せば「Google Cloud 前提なのに AWS 前提」のようなずれを実装前に見つけられる。

hdknr 版 spec-loop / dev-loop との比較は [要求仕様書作成ループ](/blogs/wiki/concepts/requirements-spec-loop/) にまとめた。

## 関連ページ

- [仕様駆動開発（SDD）](/blogs/wiki/concepts/spec-driven-development/) — SDD の全体像とツール比較
- [Kiro](/blogs/wiki/tools/kiro/) — 着想元の AI IDE
- [GitHub Spec Kit](/blogs/wiki/tools/github-spec-kit/) — 原則から始める別系統のツールキット
- [EARS 記法](/blogs/wiki/concepts/ears/) — `requirements.md` の書式
- [要求仕様書作成ループ](/blogs/wiki/concepts/requirements-spec-loop/) — cc-sdd を軸にしたフローと spec-loop / dev-loop の比較
- [Claude Code](/blogs/wiki/tools/claude-code/) — 安定版の実行先
- [作る役と確かめる役の分離（maker-checker）](/blogs/wiki/concepts/maker-checker/) — 実装役とレビュー役を分ける理由

## ソース記事

- [cc-sdd とは？ Claude Code・Codex で Kiro 式の仕様駆動開発を回すスキルと使い方](/blogs/posts/2026/11/cc-sdd-intro/) — 2026-11-13
- [非エンジニアの社長が出した巨大 PR をどう受け止めるか — cc-sdd・CodeRabbit・Takumi Guard で組む AI 駆動開発フロー](/blogs/posts/2026/11/cc-sdd-coderabbit-takumi-guard-ai-dev-flow/) — 2026-11-13
- [仕様駆動開発（SDD）とは？ 3 つのアプローチ・EARS 記法・Kiro / Spec Kit・TDD との違い](/blogs/posts/2026/11/spec-driven-development-overview/) — 2026-11-13
