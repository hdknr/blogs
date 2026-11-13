---
title: "cc-sdd とは？ Claude Code・Codex で Kiro 式の仕様駆動開発を回すスキルと使い方"
date: 2026-11-13
lastmod: 2026-11-13
slug: "cc-sdd-intro"
draft: false
categories: ["AI/LLM"]
tags: ["cc-sdd", "仕様駆動開発", "SDD", "claude-code", "Kiro"]
---

**cc-sdd** は、Claude Code や Codex などの AI コーディングエージェントに、仕様駆動開発（SDD）の進め方を持ち込むオープンソース（MIT ライセンス）のツールです。AWS の AI 開発環境 Kiro に着想を得ており、`requirements.md` / `design.md` / `tasks.md` を作ってから実装する Kiro と同じ流れを、手元のエージェントで回せます。

リポジトリの説明（description）は、cc-sdd を「承認した仕様を、長時間の自律的な実装に変える。最小限で適応しやすい SDD のハーネス」としています。仕様を人間と AI の間の約束として段階ごとに承認し、承認した仕様にもとづいて AI に実装させる、という考え方です。

要点は次の 3 つです。

- Kiro と同じ `requirements.md` / `design.md` / `tasks.md` を、Claude Code や Codex の上で作れる
- `/kiro-discovery` から `/kiro-impl` まで、`/kiro-*` のスキルを順に呼んで進める
- `/kiro-impl` は、タスクごとの実装役とレビュー役のサブエージェントで、テスト駆動開発の手順を回す

この記事では、cc-sdd のリポジトリ（[gotalab/cc-sdd](https://github.com/gotalab/cc-sdd)）とドキュメントをもとに、次の内容を整理します。内容は 2026 年 11 月 13 日時点のもので、最新のリリースは v3.1.0 です。

- インストール方法とエージェント別のオプション
- スキルを呼ぶ順番
- 作られるファイルと書き方
- `/kiro-impl` による実装の進め方

あわせて読みたい関連記事です。

- SDD の全体像：[仕様駆動開発（SDD）とは？ 3 つのアプローチ・EARS 記法・Kiro / Spec Kit・TDD との違い](/blogs/posts/2026/11/spec-driven-development-overview/)
- 着想元の Kiro：[Kiro とは？ AWS の仕様駆動 AI IDE の Spec・Steering・Hooks と料金プラン](/blogs/posts/2026/11/kiro-ai-ide-intro/)

## cc-sdd の概要

| 項目 | 内容 |
| --- | --- |
| 作者 | Gota 氏（GitHub の gotalab） |
| ライセンス | MIT |
| 公開 | 2025 年 7 月にリポジトリを作成 |
| 最新リリース | v3.1.0（2026 年 9 月 23 日） |
| 配布形態 | Agent Skills（v3.0 から）。どのエージェントにも同じ 17 個のスキルを入れる |
| 対応エージェント | Claude Code、Codex、Cursor、GitHub Copilot、Devin、OpenCode、Gemini CLI、Antigravity |
| 生成する文書の言語 | 日本語・英語を含む 14 言語 |

README には「Kiro-inspired（Kiro に着想を得た）」とあり、「既存の Kiro の仕様は互換性があり、持ち運べる」とも書かれています。日本語の README では「Kiro スタイル」と表現されています。

## cc-sdd のインストール（npx cc-sdd）と対応エージェント

プロジェクトのディレクトリで `npx` を実行します。既定では Claude Code 用のスキルが入り、生成される文書は英語になります。

```bash
cd your-project
npx cc-sdd@latest
```

エージェントと文書の言語は、オプションで指定します。

```bash
# Claude Code 用、文書は日本語
npx cc-sdd@latest --claude-skills --lang ja

# Codex 用、文書は日本語
npx cc-sdd@latest --codex-skills --lang ja
```

何が作られるかを事前に確かめたいときは `--dry-run` を、仕様の置き場所を `.kiro` 以外に変えたいときは `--kiro-dir` を使います。

```bash
# 作られるファイルを確かめるだけで、書き込まない
npx cc-sdd@latest --claude-skills --lang ja --dry-run

# 仕様の置き場所を docs/ にする
npx cc-sdd@latest --claude-skills --lang ja --kiro-dir docs
```

エージェントごとのオプションと安定度は次のとおりです（[Agent Compatibility](https://github.com/gotalab/cc-sdd/blob/main/docs/guides/agent-compatibility.md)）。

| エージェント | オプション | 安定度 |
| --- | --- | --- |
| Claude Code | `--claude-skills` | 安定版 |
| Codex | `--codex-skills` | 安定版 |
| Cursor | `--cursor-skills` | ベータ |
| GitHub Copilot | `--copilot-skills` | ベータ |
| Devin | `--devin` | ベータ |
| OpenCode | `--opencode-skills` | ベータ |
| Gemini CLI | `--gemini-skills` | ベータ |
| Antigravity | `--antigravity` | ベータ |

README によると、この安定度は統合の成熟度を表すものです。スキルを入れただけで、自律的な実装のループが最後まで回るとは限りません。

## cc-sdd のスキル（/kiro-*）の使い方

### 基本の流れ

新しい機能を作るときは、エージェントのチャット欄で次の順にスキルを呼び出します（README の「Common workflows」）。

```text
/kiro-discovery 写真アルバム（アップロード・タグ付け・共有）
/kiro-spec-init photo-albums
/kiro-spec-requirements photo-albums
/kiro-spec-design photo-albums
/kiro-spec-tasks photo-albums
/kiro-impl photo-albums
```

| スキル | 役割 |
| --- | --- |
| `/kiro-discovery` | 入口。作業の種類を見分けて `brief.md`（必要なら `roadmap.md`）を書き、次に使うスキルを示して止まる |
| `/kiro-spec-init` | 機能ごとの作業場所 `.kiro/specs/<機能名>/` を作る |
| `/kiro-spec-requirements` | 確認の質問を集めて、`requirements.md` を作る |
| `/kiro-spec-design` | 必要なら `research.md` で調査し、`design.md` を作る |
| `/kiro-spec-tasks` | `tasks.md` を作る。並行して実行できるタスクには `(P)` を付ける |
| `/kiro-impl` | 承認したタスクを実装する |

各段階は人間のレビューのために止まり、承認してから次に進みます。

### 目的別の流れ

README は、作業の種類や大きさに応じて、次の流れを示しています。

**既存のシステムを拡張する**

1. `/kiro-steering`
2. `/kiro-discovery` か `/kiro-spec-init`
3. （任意）`/kiro-validate-gap`
4. `/kiro-spec-design` → `/kiro-spec-tasks` → `/kiro-impl`

**大きな取り組み**：`/kiro-discovery` → `/kiro-spec-batch`（依存関係の順に複数の仕様をまとめて作る）

**小さな変更**：`/kiro-discovery` → そのまま実装

### そのほかのスキル

17 個のスキルのうち、主なものを紹介します。全体は [Skill Reference](https://github.com/gotalab/cc-sdd/blob/main/docs/guides/skill-reference.md) を参照してください。

| スキル | 役割 |
| --- | --- |
| `/kiro-steering` | プロジェクト全体の知識（規約や構成）を `.kiro/steering/` に作る・更新する |
| `/kiro-steering-custom` | 特定の領域についての知識を追加する |
| `/kiro-validate-gap` | 既存のコードと要件の差を分析する（任意） |
| `/kiro-validate-impl` | タスクをまたいだ結合の検証。結果は GO / NO-GO / MANUAL_VERIFY_REQUIRED のいずれか |
| `/kiro-spec-quick` | 仕様の 4 段階（init → requirements → design → tasks）を順に進め、段階ごとに承認を待つ（任意） |
| `/kiro-spec-status` | 進み具合と承認の状況をまとめる |

## .kiro/specs に作られるファイル（requirements.md・design.md・tasks.md）

| 置き場所 | 内容 |
| --- | --- |
| `.kiro/specs/<機能名>/` | `brief.md`、`requirements.md`、`research.md`（必要なとき）、`design.md`、`tasks.md` |
| `.kiro/steering/` | プロジェクト全体の知識 |
| `.kiro/settings/templates/` | 仕様のテンプレート（`requirements.md`・`design.md`・`tasks.md`） |
| `.kiro/settings/rules/` | 生成の原則（EARS の書式、設計の原則、タスクの作り方など） |
| `.claude/skills/` など | エージェントごとのスキル（Codex は `.agents/skills/`、Cursor は `.cursor/skills/` など） |

### 各文書の書き方

**`requirements.md`**

要件と受け入れ基準を EARS 形式（決まった型で要件を書く記法。詳しくは「[EARS 記法とは？ 6 つのパターンと日本語での書き方・Kiro での使い方](/blogs/posts/2026/11/ears-requirements-syntax/)」）で書きます。文書を日本語で作る場合も、When・If・While・Where・The system shall といった EARS のキーワードは英語のまま残します。

**`design.md`**

Mermaid の図を含むアーキテクチャと、どのファイルをどう置くかの計画（File Structure Plan）を書きます。

**`tasks.md`**

`- [ ]` のチェックボックスでタスクを並べます。タスクには、次の注記を付けます。

- `_Requirements:_`：どの要件に対応するか
- `(P)`：並行して実行できるタスクの印（タスク番号の直後に付ける）
- `_Boundary:_`：並行タスクが触ってよい範囲。範囲が自明なら省略する
- `_Depends:_`：自明でない依存があるときだけ書く

テンプレートと原則は `.kiro/settings/` の下にあるので、チームの書き方に合わせて編集できます。

## `/kiro-impl` の進め方

`/kiro-impl` は、タスクを指定せずに実行すると、承認したタスクを順に自律的に進めます。タスクを指定すると、そのタスクだけを実装します。

サブエージェントの機能を持つツール（Claude Code など）では、タスクごとに新しい実装役のサブエージェントを立て、別のレビュー役のサブエージェントが確かめます（[Skill Reference](https://github.com/gotalab/cc-sdd/blob/main/docs/guides/skill-reference.md)）。

| 役 | すること |
| --- | --- |
| 実装役 | テスト駆動開発（先に失敗するテストを書く RED → 通す GREEN）で実装する |
| レビュー役 | `git diff` を確かめ、TODO が残っていないかを探し、テストを走らせ、タスクの範囲を守っているかを見る |
| デバッグ役 | 実装役が行き詰まったとき、またはレビュー役が 2 回差し戻したときに呼ばれる。デバッグ役を呼べるのは 1 タスクにつき最大 2 回まで |

進め方の特徴は次のとおりです。

- 1 回に 1 タスクずつ進め、進み具合は `tasks.md` に記録する
- 実装中に得た学びは `tasks.md` の「Implementation Notes」に残し、後のタスクの実装役に渡す
- 完了を報告する前に、テスト結果などの根拠を改めて確かめる。これは `kiro-verify-completion` という内部のスキルが自動で行う（利用者が直接呼ぶものではない）
- サブエージェントの機能がないツールでは、同じ手順を 1 つのセッションの中で行う

v3.0 からは、この流れがエージェント自身のサブエージェントで動くようになりました。以前は Ralph Loop という外部のツールに頼っていました。

## cc-sdd を使うときのポイント

- **小さな変更には仕様を作らない**：README 自身が、小さな変更は `/kiro-discovery` から直接実装する流れを示している。仕様は、要件や設計を人間と合意する価値がある変更に使う
- **既存のコードがあるなら steering から**：`/kiro-steering` でプロジェクトの規約と構成を先に書かせると、仕様と設計が既存のコードとずれにくい
- **並行タスクには範囲を書く**：`(P)` のタスクに `_Boundary:_` を書いておくと、レビュー役が範囲外の変更を見つけられる
- **安定版は Claude Code と Codex**：ほかのエージェントはベータなので、自律的な実装のループが最後まで回るかを小さな機能で確かめてから使う

## Kiro・Spec Kit・OpenSpec との違い

| | cc-sdd | Kiro | Spec Kit | OpenSpec |
| --- | --- | --- | --- | --- |
| 形態 | 既存のエージェントに追加するスキル | 専用の AI 開発環境 | 既存のエージェントに追加するツールキット | 既存のエージェントに追加するスキル |
| 進め方 | discovery → 要件 → 設計 → タスク → 実装 | 要件 → 設計 → タスク → 実装 | 原則 → 仕様 → 計画 → タスク → 実装 | 提案 → 実装 → アーカイブ |
| 特徴 | Kiro と同じ文書構成。サブエージェントによる実装とレビュー | IDE に統合された Spec・Steering・Hooks | 原則（constitution）で AI の判断を縛る | 変更を差分で扱う |

Kiro の文書構成をそのまま使いたいが、IDE は替えずに Claude Code や Codex で進めたい、という場合に cc-sdd が合います。Spec Kit と OpenSpec については「[GitHub Spec Kit とは？](/blogs/posts/2026/11/github-spec-kit-intro/)」と「[OpenSpec とは？](/blogs/posts/2026/05/openspec-spec-driven-development/)」で紹介しています。

cc-sdd を軸に、レビューや依存パッケージのチェックまで組み込んだ開発フローの事例は、「[非エンジニアの社長が出した巨大 PR をどう受け止めるか — cc-sdd・CodeRabbit・Takumi Guard で組む AI 駆動開発フロー](/blogs/posts/2026/11/cc-sdd-coderabbit-takumi-guard-ai-dev-flow/)」で紹介しています。

## まとめ

- cc-sdd は、Kiro に着想を得た MIT ライセンスの SDD ツールで、Claude Code や Codex などに 17 個のスキルを入れる
- `npx cc-sdd@latest --claude-skills --lang ja` のように、エージェントと文書の言語を選んでインストールする
- 基本の流れは `/kiro-discovery` → `/kiro-spec-init` → `/kiro-spec-requirements` → `/kiro-spec-design` → `/kiro-spec-tasks` → `/kiro-impl`
- 仕様は `.kiro/specs/<機能名>/` に、Kiro と同じ `requirements.md`・`design.md`・`tasks.md` として作られる
- `/kiro-impl` は、タスクごとの実装役とレビュー役のサブエージェントで、テスト駆動開発の手順を回す
- 小さな変更には仕様を作らず、合意する価値のある変更にだけ使う
