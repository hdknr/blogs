---
title: "GitHub Spec Kit"
description: "GitHub が公開する MIT ライセンスの仕様駆動開発ツールキット。specify CLI で既存の AI エージェントにスラッシュコマンドを足し、constitution（原則）→ 仕様 → 計画 → タスク → 実装 → converge の流れで進める"
date: 2026-11-15
lastmod: 2026-11-15
aliases: ["Spec Kit", "spec-kit", "specify-cli", "specify", "speckit", "constitution"]
related_posts:
  - "/posts/2026/11/github-spec-kit-intro/"
  - "/posts/2026/11/spec-driven-development-overview/"
tags: ["Spec Kit", "SDD", "仕様駆動開発", "AI駆動開発", "claude-code"]
---

## 概要

**GitHub Spec Kit** は GitHub が 2025 年 9 月に公開した、[仕様駆動開発](/blogs/wiki/concepts/spec-driven-development/) のオープンソースのツールキット（MIT）である。専用 IDE の [Kiro](/blogs/wiki/tools/kiro/) と違い、Claude Code・GitHub Copilot・Gemini CLI・Codex CLI など手元のエージェント（40 以上）にスラッシュコマンドとテンプレートを追加する形で動く。最大の特徴は、すべての機能に共通して守らせる**原則（constitution）**で AI の判断を縛ることにある。

## 詳細

### 導入

CLI は `specify`（パッケージ `specify-cli`）。Python 3.11 以上と uv（推奨）か pipx が前提。

```bash
uv tool install specify-cli
specify init my-project --integration claude   # copilot / gemini / codex / cursor-agent / kiro-cli など
```

インストールせずに `uvx --from git+https://github.com/github/spec-kit.git specify init …` で 1 回だけ実行することもできる。`specify version`・`specify self check` で版と更新を確かめる。

### コマンドの流れ

コマンドは `/speckit.<名前>`（ドキュメントにはハイフン区切りの表記もあるので、実際はエージェントの補完に出る名前を使う）。

| 順 | コマンド | 役割 | 必須／任意 |
|---|---|---|---|
| 1 | `constitution` | プロジェクトの原則を決める | 最初に 1 回 |
| 2 | `specify` | 自然言語の説明から機能の仕様を作る | 必須 |
| 3 | `clarify` | 仕様の足りない点を的を絞って質問する | 任意 |
| 4 | `plan` | 仕様から設計の成果物を作る | 必須 |
| 5 | `checklist` | 要件の明確さ・漏れを確かめる（要件の単体テスト） | 任意 |
| 6 | `tasks` | 依存関係順の `tasks.md` を作る | 必須 |
| 7 | `analyze` | 成果物間の矛盾・抜け・曖昧さを報告（読み取りのみ） | 任意 |
| 8 | `implement` | タスクを依存関係順に実行する | 必須 |
| 9 | `converge` | コードベースを仕様・計画・タスクと照らし合わせる | 必須 |

短い流れは `specify` → `plan` → `tasks` → `implement` → `converge` で、`converge` が「Converged」と報告するまで implement と converge を繰り返す。

要点は、**`specify` には「何を・なぜ」だけを書き、技術の選択は `plan` で渡す**こと。仕様と技術選定を分けておけば、仕様を変えずに技術だけを差し替えられる。

### constitution（原則）

`memory/constitution.md` に置くプロジェクト共通のルールで、`plan` の段階で計画が原則に反していないかを関門として確かめる。AI が勝手に抽象化を増やしたりテストを後回しにしたりするのを抑える仕組みである。考え方をまとめた `spec-driven.md` の例は次のとおり（第 4〜6 条はプロジェクトごとに定める）。

| 条文 | 内容 |
|---|---|
| 第 1 条 Library-First | すべての機能は独立したライブラリとして始める |
| 第 2 条 CLI Interface Mandate | テキスト入出力と JSON に対応した CLI を持つ |
| 第 3 条 Test-First Imperative | 厳格なテスト駆動開発に従う |
| 第 7 条 Simplicity | 最初の実装ではプロジェクトを最大 3 つに |
| 第 8 条 Anti-Abstraction | フレームワークを余計な抽象化で包まない |
| 第 9 条 Integration-First Testing | 結合テストを優先する |

### 成果物

原則はプロジェクトに 1 つ、ほかは機能ごとに `spec.md`・`plan.md`・`research.md`・`data-model.md`・`contracts/`・`quickstart.md`・`tasks.md` ができる。作業用ファイルは `.specify/` の下で、置き場所は版によって変わる。現在は本体がブランチを作らず、作業中の機能は `.specify/feature.json` で管理する（番号付きブランチ `001-feature-name` はオプションの git 拡張。`spec-driven.md` の「自動でブランチを作る」は以前の動き）。

### 注意点

Böckeler 氏（martinfowler.com）は 2025 年 9 月の試用で、Spec-Anchored を志向しつつ実態は **Spec-First** にとどまる、Markdown が多く冗長でレビューが大変、問題の大きさに対して過剰、エージェントが指示のすべてには従わない、と評価した。その後 `converge` が加わったが、次の点は今も当てはまる。

- **小さな変更には重い**：短い流れを基本にし、任意のコマンドは必要なときだけ
- **成果物を読むのは人間**：少なくとも `spec.md` と `plan.md` は読んでから進む
- **仕様の保守は運用で決める**：作った後も更新し続けるかはツールではなくチームの決めごと

まずは小さな機能 1 つで specify から converge までを 1 回通すのがよい。

## 関連ページ

- [仕様駆動開発（SDD）](/blogs/wiki/concepts/spec-driven-development/) — 3 つのアプローチとツール比較
- [Kiro](/blogs/wiki/tools/kiro/) — 対になる専用 AI IDE
- [cc-sdd](/blogs/wiki/tools/cc-sdd/) — Kiro の文書構成を既存エージェントで使うスキル
- [Spec Workflow MCP](/blogs/wiki/tools/spec-workflow-mcp/) — 承認をダッシュボードで記録する MCP サーバー
- [Claude Code](/blogs/wiki/tools/claude-code/) — 主な実行先のエージェント

## ソース記事

- [GitHub Spec Kit とは？ 仕様駆動開発のコマンド・constitution と Kiro との違い](/blogs/posts/2026/11/github-spec-kit-intro/) — 2026-11-13
- [仕様駆動開発（SDD）とは？ 3 つのアプローチ・EARS 記法・Kiro / Spec Kit・TDD との違い](/blogs/posts/2026/11/spec-driven-development-overview/) — 2026-11-13
