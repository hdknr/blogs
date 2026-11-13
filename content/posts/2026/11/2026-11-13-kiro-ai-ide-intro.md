---
title: "Kiro とは？ AWS の仕様駆動 AI IDE の Spec・Steering・Hooks と料金プラン"
date: 2026-11-13
lastmod: 2026-11-13
slug: "kiro-ai-ide-intro"
draft: false
categories: ["AI/LLM"]
tags: ["Kiro", "aws", "仕様駆動開発", "AI駆動開発", "EARS"]
---

**Kiro** は、AWS が開発・運営する AI 開発環境です。最大の特徴は **Spec（仕様）** です。AI に実装させる前に、要件・設計・タスクの 3 つの文書を作ってレビューする流れが、IDE に組み込まれています。仕様駆動開発（SDD）の代表的なツールとして名前が挙がることの多い製品です。

この記事では、Kiro の公式ドキュメント（[kiro.dev/docs](https://kiro.dev/docs/)）をもとに、Spec・Steering・Hooks といった主な機能と、料金プラン、向いている使い方を整理します。内容は 2026 年 11 月 13 日時点の公式ドキュメントにもとづきます。

あわせて読みたい関連記事です。

- SDD の全体像：[仕様駆動開発（SDD）とは？ 3 つのアプローチ・EARS 記法・Kiro / Spec Kit・TDD との違い](/blogs/posts/2026/11/spec-driven-development-overview/)
- Kiro が要件に使う記法：[EARS 記法とは？ 6 つのパターンと日本語での書き方・Kiro での使い方](/blogs/posts/2026/11/ears-requirements-syntax/)
- 対になる GitHub のツールキット：[GitHub Spec Kit とは？ 仕様駆動開発のコマンド・constitution と Kiro との違い](/blogs/posts/2026/11/github-spec-kit-intro/)
- Kiro に着想を得た Claude Code 向けのツール：[cc-sdd とは？ Claude Code・Codex で Kiro 式の仕様駆動開発を回すスキルと使い方](/blogs/posts/2026/11/cc-sdd-intro/)
- cc-sdd を軸にした開発フローの事例：[非エンジニアの社長が出した巨大 PR をどう受け止めるか — cc-sdd・CodeRabbit・Takumi Guard で組む AI 駆動開発フロー](/blogs/posts/2026/11/cc-sdd-coderabbit-takumi-guard-ai-dev-flow/)

## Kiro の概要

| 項目 | 内容 |
| --- | --- |
| 提供元 | AWS（公式サイトに "Built and run by AWS" と表記） |
| ベース | Code OSS（VS Code のオープンソース版）。拡張機能は OpenVSX（VS Code 互換のオープンな拡張機能レジストリ）から入れる |
| 発表 | 2025 年 7 月 14 日にプレビューとして公開 |
| 一般提供（GA） | 2025 年 11 月 17 日 |
| 提供形態 | IDE、CLI、Web、モバイルアプリ、Kiro Crew |
| IDE の対応 OS | macOS（Intel・Apple Silicon）、Windows 10/11（x64・ARM64）、Linux（Ubuntu 24 以降など） |

Code OSS をベースにしているので、エディターとしての操作感は VS Code とほぼ同じです。ただし拡張機能は VS Code Marketplace ではなく OpenVSX から入れるため、VS Code で使っている拡張機能がすべて見つかるとは限りません。

主な機能を先に一言でまとめておきます。

| 機能 | 何をするか |
| --- | --- |
| Spec | 要件・設計・タスクの文書を作ってから実装する |
| Steering | プロジェクトの規約や前提を Markdown で AI に渡す |
| Hooks | ファイルの保存などのイベントで、コマンドやプロンプトを自動実行する |
| MCP | 外部のツールやデータソースを AI につなぐ |

## Kiro の Spec：要件・設計・タスクを先に作る

### 3 つのファイル

Kiro の Spec は、1 つの機能ごとに次の 3 つのファイルを作ります（[Specs](https://kiro.dev/docs/specs/)）。

| ファイル | 内容 |
| --- | --- |
| `requirements.md` | ユーザーストーリーと受け入れ基準。EARS 記法で書く |
| `design.md` | 技術的なアーキテクチャ、シーケンス図、実装上の考慮事項 |
| `tasks.md` | 個別に追跡できるタスクに分けた実装計画 |

`requirements.md` の受け入れ基準は、EARS 記法の `WHEN [condition/event] THE SYSTEM SHALL [expected behavior]` の形で書きます（[Feature Specs](https://kiro.dev/docs/specs/feature-specs/)）。たとえば次のような形です。

```text
WHEN ユーザーが送信ボタンを押す THE SYSTEM SHALL 入力値を検証する
```

条件と期待する振る舞いを分けて書くので、そのままテストの観点になります。

### 進め方の選び方

機能開発の Spec（Feature Spec）の進め方は、次の 3 種類です。

- **Requirements-First**：要件 → 設計 → タスクの順に作る。何を作るかから固めたいときに向く
- **Design-First**：設計 → 要件 → タスクの順に作る。技術的な設計を先に固めたいときに向く
- **Quick Spec**：各段階の承認を待たずに、3 つの文書をまとめて自動で作る

Spec の基本は、各段階で人間が文書を確かめて承認してから次に進むことです。Quick Spec はその承認を省く代わりに、速く進めます。

### 不具合修正の Spec

不具合の修正には **Bugfix Spec** を使います（[Bugfix Specs](https://kiro.dev/docs/specs/bugfix-specs/)）。`requirements.md` の代わりに `bugfix.md` を作り、次の 3 つを書き分けます。

- 現在の振る舞い（不具合）
- 期待する振る舞い（正しい状態）
- 変えてはいけない振る舞い（回帰の防止）

設計の段階で根本原因を突き止めます。タスクには「不具合を再現できる」「不具合が直った」「回帰がない」を確かめるプロパティベーステスト（入力を大量に自動生成し、常に成り立つべき性質を確かめるテスト）が含まれます。なお、プロパティベーステストで仕様の正しさを確かめる機能は、公式ドキュメントでは IDE のみの対応とされています。

### タスクの実行

`tasks.md` のタスクは、1 つずつでも、まとめてでも実行できます。まとめて実行すると、Kiro はタスクの依存関係からグラフを作り、依存しないタスクを同じ「波（wave）」として並行に実行します。波どうしは順番に実行されます。

## チャットのエージェント・権限モード・チェックポイント

### 目的別のエージェント

Kiro のチャットは、汎用の **Default** エージェントのほかに、目的別の組み込みエージェントを選べます（[Chat](https://kiro.dev/docs/ide/chat/)）。

| エージェント | 用途 |
| --- | --- |
| Default | 一般的なコーディングの支援 |
| Spec | 要件・設計・タスクを作る構造化された機能開発 |
| Quick Spec | 最初に不明点を確かめたうえで、要件・設計・タスクを自動で作る |
| Plan | 変更は加えず、実装計画だけを作る |
| Bug Fix | 不具合の調査・診断・修正 |

### 権限モード

AI にどこまで任せるかは、チャットごとの **権限モード** で決めます（[Permission modes](https://kiro.dev/docs/ide/chat/autopilot/)）。

| モード | 動き |
| --- | --- |
| Supervised | ファイルを編集したターンのたびに止まり、人間の承認を待つ |
| Accept file changes | ファイルの作成・編集・削除は確認なしで行う。コマンドの実行は、ルールで許可していなければ確認する |
| Approve for me | 判断のつく操作はモデルが承認・拒否し、判断に迷うときだけ人間に確かめる |

`Accept file changes` は、Kiro IDE 1.4.154 より前は Autopilot と呼ばれていました。

### チェックポイント

変更をさかのぼる **チェックポイント** もあり、コードと会話を以前の任意の時点まで巻き戻せます。

## Kiro の Steering：プロジェクトの知識を AI に渡す

**Steering** は、プロジェクトについての知識を Markdown ファイルで Kiro に渡す仕組みです（[Steering](https://kiro.dev/docs/steering/)）。毎回のプロンプトで同じ前提を説明しなくて済みます。

- 置き場所：プロジェクトの `.kiro/steering/`（ワークスペース）と、`~/.kiro/steering/`（全プロジェクト共通）。両方にあって食い違う場合は、ワークスペースの指示が優先される
- 基本のファイル：`product.md`（製品）、`tech.md`（技術スタック）、`structure.md`（構成）。IDE の「Generate Steering Docs」で自動生成できる

各ファイルがいつ読み込まれるかは、ファイル冒頭の front matter で指定します。

| 読み込みモード | 動き |
| --- | --- |
| `always`（既定） | すべてのやり取りで読み込む |
| `fileMatch` | 指定したパターン（例：`components/**/*.tsx`）のファイルを扱うときだけ読み込む |
| `manual` | チャットで `#ファイル名` と指定したときだけ読み込む |
| `auto` | ファイルに書いた説明（description）と依頼の内容が合うときに読み込む |

```markdown
---
inclusion: fileMatch
fileMatchPattern: "components/**/*.tsx"
---

# コンポーネントの規約

- 関数コンポーネントで書く
- props の型は同じファイルに定義する
```

CLI では、4 つの読み込みモードがすべて使えるのは CLI V3 以降です。それより前の版では `always` のファイルだけが自動で読み込まれます。

AI コーディングエージェント向けの共通の指示ファイル `AGENTS.md` にも対応しています。`AGENTS.md` は読み込みモードを指定できず、常に読み込まれます。

## Kiro の Hooks：イベントで処理を自動実行する

**Hooks** は、特定のイベントが起きたときに、シェルコマンドかエージェントへのプロンプトを自動で実行する仕組みです（[Hooks](https://kiro.dev/docs/hooks/)）。設定は `.kiro/hooks/` に JSON ファイルとして置きます。

主なトリガーは次のとおりです（[Hook types](https://kiro.dev/docs/hooks/types/)）。使えるトリガーは IDE・CLI・Web で異なります。

| 種類 | トリガー |
| --- | --- |
| ファイル | 作成・保存・削除（エージェントが行った変更にだけ反応する） |
| タスク | Spec のタスクの実行前・実行後 |
| ツール | ツールの使用前・使用後 |
| セッション・プロンプト | プロンプトの送信、エージェントの停止など |

公式ドキュメントは、エージェントがファイルを変更した後にリンター・フォーマッター・型チェックを走らせる用途や、関連ファイルを自動生成する用途を挙げています。筆者の例を挙げると、「エージェントが TypeScript のファイルを保存したら ESLint で自動修正する」といった使い方が考えられます。

## MCP・モデル・CLI

### MCP

Kiro は MCP（Model Context Protocol）に対応しており、外部のツールやデータソースを MCP サーバーとして接続できます（[MCP](https://kiro.dev/docs/mcp/)）。ローカルで動く stdio 型のサーバーと、リモートの HTTP 型のサーバーの両方を使えます。

### 使えるモデル

推奨の **Auto** は Kiro のモデルルーターで、依頼に応じてモデルを選びます（[Available models](https://kiro.dev/docs/models/available-models/)）。特定のモデルを選ぶこともでき、Anthropic の Claude のほか、OpenAI のモデルやオープンウェイトのモデルが一覧に並んでいます。選べるモデルはプランによって異なり、頻繁に入れ替わるので、最新の一覧は公式ページで確かめてください。

### Kiro CLI

ターミナルで Kiro のエージェントを動かす **Kiro CLI** もあります（[CLI](https://kiro.dev/docs/cli/)）。

```bash
curl -fsSL https://cli.kiro.dev/install | bash
cd your-project  # 任意のプロジェクトのディレクトリ
kiro-cli
```

インストールスクリプトを実行前に確かめたい場合は、`curl -fsSL https://cli.kiro.dev/install -o install.sh` でいったん保存し、中身を読んでから実行してください。

CLI 3.0 以降は、Steering・カスタムエージェント・Hooks・権限・MCP の設定を IDE や Web と共有します。対話なしでプロンプトを実行するヘッドレスモードもあり、CI/CD のパイプラインに組み込めます。使い方は [CLI のドキュメント](https://kiro.dev/docs/cli/) を参照してください。

## Kiro の料金プラン（Free / Pro / Pro+ / Pro Max / Power）

[料金ページ](https://kiro.dev/pricing/)に掲載されている個人向けのプランは次のとおりです（2026 年 11 月 13 日時点）。

| プラン | 月額（1 ユーザー） | 月間クレジット |
| --- | --- | --- |
| Kiro Free | 0 ドル | 50 |
| Kiro Pro | 20 ドル | 1,000 |
| Kiro Pro+ | 40 ドル | 2,000 |
| Kiro Pro Max | 100 ドル | 5,000 |
| Kiro Power | 200 ドル | 10,000 |

- クレジットは、プロンプトに応じて行う作業の量を表す単位。単純なプロンプトは 1 クレジット未満、複雑な作業は通常それより多く消費する
- 個人プランでは、使い切らなかった月間クレジットは翌月に繰り越されない
- 追加のクレジットは 1 クレジット 0.04 ドルで購入できる
- 日本の請求先住所には消費税がかかる

料金とクレジットの条件は変わることがあるので、契約前に公式ページで確かめてください。

## Kiro の向き・不向き

### 向いている使い方

- **何を作るかを先に固めたい新機能**：要件 → 設計 → タスクの各段階で文書を確かめてから実装に入れる
- **チームで AI の使い方を揃えたい**：Steering でプロジェクトの規約を共有し、Hooks でリンターなどを自動で回せる
- **不具合修正の再発防止**：Bugfix Spec が「変えてはいけない振る舞い」を明示させる

### 注意したい点

Thoughtworks の Birgitta Böckeler 氏は、SDD ツールを比較した記事（[Understanding Spec-Driven-Development: Kiro, spec-kit, and Tessl](https://martinfowler.com/articles/exploring-gen-ai/sdd-3-tools.html)）で Kiro を取り上げています。氏の評価では、Kiro は主に **Spec-First** のツールです。Spec-First とは、実装前に仕様を書くが、実装後も仕様を保守し続けることまでは前提にしない、という使い方です。

つまり、Kiro を使えば仕様とコードが自動で同期し続けるわけではありません。長く運用するなら、仕様の更新をどの段階で誰が行うかを、チームで決めておく必要があります。

また、小さな修正にまで 3 つの文書を作ると、作る手間のほうが大きくなります。Default エージェントで直接直すか、Spec を使うかを、変更の大きさで使い分けるのが現実的です。

## Kiro 以外のエージェントで同じ流れを使うには（cc-sdd / Spec Kit / OpenSpec）

Kiro の IDE を使わずに、Claude Code などの既存のエージェントで同じ流れを取り入れるツールもあります。[cc-sdd](https://github.com/gotalab/cc-sdd) は Kiro に着想を得たツールで、`requirements.md` / `design.md` / `tasks.md` を作る流れを Claude Code や Cursor に持ち込みます。GitHub の [Spec Kit](https://github.com/github/spec-kit) や [OpenSpec](https://github.com/Fission-AI/OpenSpec) も、同じく既存のエージェントに SDD の流れを組み込むツールです。

それぞれの詳細は「[cc-sdd とは？ Claude Code・Codex で Kiro 式の仕様駆動開発を回すスキルと使い方](/blogs/posts/2026/11/cc-sdd-intro/)」「[GitHub Spec Kit とは？ 仕様駆動開発のコマンド・constitution と Kiro との違い](/blogs/posts/2026/11/github-spec-kit-intro/)」と「[OpenSpec とは？ 仕様駆動開発の使い方・/openspec-* スキルと Spec Kit・Kiro との違い](/blogs/posts/2026/05/openspec-spec-driven-development/)」で紹介しています。

## まとめ

- Kiro は AWS が提供する、Code OSS ベースの AI 開発環境。2025 年 7 月にプレビュー、同年 11 月に一般提供が始まった
- Spec は `requirements.md`（EARS 記法）・`design.md`・`tasks.md` の 3 ファイルで、実装の前に要件・設計・タスクを固める
- 進め方は Requirements-First・Design-First・Quick Spec の 3 種類で、不具合修正には Bugfix Spec がある
- 権限モード（Supervised / Accept file changes / Approve for me）で AI に任せる範囲を選べる
- Steering でプロジェクトの知識を、Hooks でイベント駆動の自動処理を、MCP で外部ツールを AI に渡せる
- Kiro CLI でターミナルからも使え、ヘッドレスモードで CI/CD にも組み込める
- 料金は無料プランから月 200 ドルのプランまでで、クレジット制
- 仕様の保守は自動ではないので、実装後に仕様を誰がどう更新するかは運用で決める
