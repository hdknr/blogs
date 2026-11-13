---
title: "GitHub Spec Kit とは？ 仕様駆動開発のコマンド・constitution と Kiro との違い"
date: 2026-11-13
lastmod: 2026-11-13
slug: "github-spec-kit-intro"
draft: false
categories: ["AI/LLM"]
tags: ["Spec Kit", "SDD", "仕様駆動開発", "AI駆動開発", "claude-code"]
---

**GitHub Spec Kit** は、GitHub が公開しているオープンソース（MIT ライセンス）の仕様駆動開発（SDD）のツールキットです。Claude Code や GitHub Copilot などの AI コーディングエージェントに、「原則 → 仕様 → 計画 → タスク → 実装」という決まった進め方と、そのためのテンプレートを持ち込みます。

専用の AI 開発環境を使う [Kiro](/blogs/posts/2026/11/kiro-ai-ide-intro/) とは違い、Spec Kit は手元のエージェントにスラッシュコマンドを追加する形で動きます。

この記事では、Spec Kit の公式ドキュメント（[github.github.io/spec-kit](https://github.github.io/spec-kit/)）とリポジトリ（[github/spec-kit](https://github.com/github/spec-kit)）をもとに、インストール方法、コマンドの流れ、原則（constitution）の考え方、使うときの注意点を整理します。内容は 2026 年 11 月 13 日時点のもので、最新のリリースは v1.4.0 です。

あわせて読みたい関連記事です。

- SDD の全体像：[仕様駆動開発（SDD）とは？ 3 つのアプローチ・EARS 記法・Kiro / Spec Kit・TDD との違い](/blogs/posts/2026/11/spec-driven-development-overview/)
- 対になる AI 開発環境：[Kiro とは？ AWS の仕様駆動 AI IDE の Spec・Steering・Hooks と料金プラン](/blogs/posts/2026/11/kiro-ai-ide-intro/)

## Spec Kit の概要

| 項目 | 内容 |
| --- | --- |
| 提供 | GitHub（リポジトリ `github/spec-kit`） |
| ライセンス | MIT |
| 発表 | 2025 年 9 月 2 日の GitHub ブログ（[Spec-driven development with AI: Get started with a new open source toolkit](https://github.blog/ai-and-ml/generative-ai/spec-driven-development-with-ai-get-started-with-a-new-open-source-toolkit/)） |
| CLI | `specify`（パッケージ名 `specify-cli`） |
| 前提 | Python 3.11 以上、uv（Python のパッケージ管理ツール。推奨）か pipx、対応する AI コーディングエージェント |
| 対応 OS | Linux、macOS、Windows |

README は Spec Kit を「AI コーディングエージェントに、構造化されたプロセス、再利用できるテンプレート、記録に残る成果物を与えるオープンソースのツールキット」と説明しています。

## Spec Kit のインストール方法と specify init

`specify` CLI を入れて、プロジェクトを初期化します（[Installation](https://github.github.io/spec-kit/installation.html)）。`--integration` で、使う AI コーディングエージェントを指定します。

```bash
# CLI をインストール（PyPI から）
uv tool install specify-cli

# プロジェクトを初期化（Claude Code を使う場合）
specify init my-project --integration claude
cd my-project
```

インストールせずに 1 回だけ実行することもできます（[One-time](https://github.github.io/spec-kit/install/one-time.html)）。

```bash
uvx --from git+https://github.com/github/spec-kit.git specify init my-project --integration claude
```

インストール後は、`specify version` でバージョンを、`specify self check` で新しいリリースがあるかを確かめられます。

### 対応しているエージェント

[Integrations](https://github.github.io/spec-kit/integrations/index.html) のページには 40 を超えるエージェントが並んでいます。主なものは次のとおりです。

| エージェント | `--integration` の値 |
| --- | --- |
| Claude Code | `claude` |
| GitHub Copilot | `copilot` |
| Gemini CLI | `gemini` |
| Codex CLI | `codex` |
| Cursor | `cursor-agent` |
| Kiro CLI | `kiro-cli` |

Kiro の CLI も対象に入っているので、Kiro の上で Spec Kit の進め方を使うこともできます。

## Spec Kit のコマンド一覧と使い方

初期化すると、エージェントに Spec Kit のスラッシュコマンドが追加されます。公式ドキュメントでは、`/speckit.specify`（ドット区切り）と `/speckit-specify`（ハイフン区切り）の 2 つの表記が使われています。実際の名前は、エージェントのコマンド補完に出てくるものを使ってください。

[Quickstart](https://github.github.io/spec-kit/quickstart.html) に沿って、コマンドを順に並べます。表では先頭の `/speckit.` を省いています。

| 順 | コマンド | 役割 | 必須／任意 |
| --- | --- | --- | --- |
| 1 | `constitution` | プロジェクトの指針となる原則を決める | プロジェクトごとに 1 回、最初に行う |
| 2 | `specify` | 自然言語の説明から、機能の仕様を作る | 必須 |
| 3 | `clarify` | 仕様の足りない点について、的を絞った質問をする | 任意 |
| 4 | `plan` | 仕様から設計の成果物を作る | 必須 |
| 5 | `checklist` | 要件が明確か・漏れがないかを確かめるチェックリストを作る（要件の単体テストにあたる） | 任意 |
| 6 | `tasks` | 依存関係の順に並べた `tasks.md` を作る | 必須 |
| 7 | `analyze` | 成果物どうしの矛盾・抜け・曖昧さを報告する（読み取りだけで、何も変更しない） | 任意 |
| 8 | `implement` | `tasks.md` のタスクを依存関係の順に実行する | 必須 |
| 9 | `converge` | コードベースを仕様・計画・タスクと照らし合わせる | 必須 |

原則を決めたあとの短い流れは、`specify` → `plan` → `tasks` → `implement` → `converge` です。`implement` と `converge` は、`converge` が「Converged（収束した）」と報告するまで繰り返します。

エージェントのチャット欄で、次のように入力して進めます（シェルではありません）。

```text
/speckit.specify 写真をアルバムにまとめて共有できるアプリを作る。アルバムは日付でまとめ、ドラッグ＆ドロップで並べ替えられる
/speckit.plan フロントエンドは Vite と素の HTML/CSS/JavaScript、データはローカルの SQLite に保存する
/speckit.tasks
/speckit.implement
/speckit.converge
```

ポイントは、`specify` では「何を・なぜ作るか」だけを書き、技術の選択は `plan` で渡すことです。仕様と技術選定を分けておくと、仕様を変えずに技術だけを差し替えることもできます。

## Spec Kit の constitution（原則）とは

`constitution` で作る原則は、すべての機能に共通して守らせるルールです。Spec Kit の考え方をまとめた [spec-driven.md](https://github.com/github/spec-kit/blob/main/spec-driven.md) には、原則の例として次のような条文が載っています（第 4〜6 条は各プロジェクトで定めるものとされているため、ここには載せていません）。

| 条文 | 内容 |
| --- | --- |
| 第 1 条 Library-First | すべての機能は、独立したライブラリとして始める |
| 第 2 条 CLI Interface Mandate | 機能はテキストの入出力と JSON に対応した CLI を持つ |
| 第 3 条 Test-First Imperative | 実装は厳格なテスト駆動開発に従う（交渉の余地なし） |
| 第 7 条 Simplicity | 最初の実装ではプロジェクトを最大 3 つにとどめる |
| 第 8 条 Anti-Abstraction | フレームワークの機能を、余計な抽象化で包まずにそのまま使う |
| 第 9 条 Integration-First Testing | 結合テストを優先する |

これらはあくまで考え方の例なので、自分のプロジェクトでは `constitution` で必要な原則を書きます。

spec-driven.md によれば、`plan` の段階では、計画が原則（単純さ・抽象化の禁止・結合テストの優先など）に反していないかを関門として確かめます。AI が勝手に抽象化を増やしたり、テストを後回しにしたりするのを、原則で抑える仕組みです。

## Spec Kit が作るファイルと機能の管理

spec-driven.md では、次のような成果物が作られると説明されています。原則はプロジェクト全体で 1 つ、それ以外は機能ごとに作られます。

| ファイル | 単位 | 内容 |
| --- | --- | --- |
| `memory/constitution.md` | プロジェクト | プロジェクトの原則 |
| `spec.md` | 機能 | 機能の仕様 |
| `plan.md` | 機能 | 実装計画 |
| `research.md` | 機能 | 技術調査の結果 |
| `data-model.md` | 機能 | データモデル |
| `contracts/` | 機能 | API などの契約 |
| `quickstart.md` | 機能 | 動作確認の手順 |
| `tasks.md` | 機能 | タスクの一覧 |

Spec Kit の作業用のファイルは `.specify/` の下に置かれます。ファイルの置き場所はバージョンによって変わっているので、実際の構成は `specify init` の結果で確かめてください。

### 機能ごとのブランチ

現在のクイックスタートでは、Spec Kit 本体はブランチを作りません。作業中の機能は、ブランチではなく `.specify/feature.json` で管理されます。番号付きのブランチ（`001-feature-name` など）が必要なら、オプションの git 拡張を使います。

なお spec-driven.md には、`specify` が `003-chat-system` のような番号付きのブランチを自動で作ると書かれていますが、これは以前の動きです。

## Spec Kit のデメリットと使うときの注意点

Birgitta Böckeler 氏は、SDD ツールを比較した記事（[Understanding Spec-Driven-Development: Kiro, spec-kit, and Tessl](https://martinfowler.com/articles/exploring-gen-ai/sdd-3-tools.html)）で Spec Kit を試し、次のように評価しています。Spec-First・Spec-Anchored という分類については、[SDD の概要記事](/blogs/posts/2026/11/spec-driven-development-overview/)で説明しています。

- GitHub は仕様を保守し続ける **Spec-Anchored** を目指しているように見えるが、実際には仕様を最初に書くだけの **Spec-First** にとどまる
- レビューしなければならない Markdown ファイルが非常に多く、冗長で読むのが大変だった
- 問題の大きさに対して過剰に感じた
- エージェントが指示のすべてには従わないことがよくあった

氏自身が、ツールは急速に変わっているので 2025 年 9 月に試した後で変わっている可能性がある、と断っています。実際、その後のリリースで加わった `converge` は、コードベースを仕様と照らし合わせる役割を持っています。それでも、次の点は今も当てはまります。

- **小さな変更には重い**：数行の修正にまで仕様・計画・タスクを作ると、レビューの手間のほうが大きくなる。短い流れを基本にし、任意のコマンドは必要なときだけ使う
- **成果物を読むのは人間**：Markdown が多く作られるほど、レビューされないまま進むおそれがある。少なくとも `spec.md` と `plan.md` は人間が読んでから次に進む
- **仕様の保守は運用で決める**：仕様を作った後も更新し続けるかどうかは、ツールではなくチームの決めごとになる

## Kiro・OpenSpec との違い

| | Spec Kit | Kiro | OpenSpec |
| --- | --- | --- | --- |
| 形態 | 既存のエージェントに追加するツールキット | 専用の AI 開発環境（IDE・CLI など） | 既存のエージェントに追加するツール |
| 提供 | GitHub（MIT ライセンス） | AWS | オープンソース（MIT ライセンス） |
| 進め方 | 原則 → 仕様 → 計画 → タスク → 実装 | 要件 → 設計 → タスク → 実装 | 変更の提案 → 適用 → アーカイブ |
| 特徴 | 原則（constitution）で AI の判断を縛る | IDE に統合された Spec・Steering・Hooks | 変更を差分で扱い、既存のコードベースにも対応する |

選び方の目安は次のとおりです。

- すでに使っているエージェントを替えずに、決まった手順で SDD を試したい → Spec Kit
- IDE ごと統合された環境で、規約やフックまでまとめて扱いたい → Kiro
- 既存のコードへの変更を、差分の提案として軽く回したい → OpenSpec（[OpenSpec の紹介記事](/blogs/posts/2026/05/openspec-spec-driven-development/)）

## まとめ

- Spec Kit は GitHub が公開する MIT ライセンスの SDD ツールキットで、2025 年 9 月に発表された
- `specify` CLI でプロジェクトを初期化すると、Claude Code や GitHub Copilot など 40 を超えるエージェントにスラッシュコマンドが追加される
- 最初に constitution で原則を決め、その後は specify → plan → tasks → implement → converge で進める。clarify・checklist・analyze は任意
- `specify` には「何を・なぜ」だけを書き、技術の選択は `plan` で渡す
- 原則（constitution）で、テスト先行や過剰な抽象化の禁止といったルールを AI に守らせる
- 成果物が多くなりやすいので、小さな変更には短い流れを使い、仕様の保守は運用で決める
- まずは小さな機能 1 つで、specify から converge までを 1 回通してみるのがおすすめ
