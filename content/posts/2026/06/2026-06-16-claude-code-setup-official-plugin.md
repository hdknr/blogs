---
title: "公式が出した claude-code-setup — Claude Code の混乱を整理する公式プラグインの全貌"
date: 2026-06-16
lastmod: 2026-06-16
slug: "claude-code-setup-official-plugin"
draft: false
source_url: "https://github.com/hdknr/blogs/issues/1#issuecomment-4714963243"
categories: ["AI/LLM"]
tags: ["claude-code", "プラグイン", "MCP", "Skills", "セットアップ"]
---

Claude Code を使い続けていると、いつの間にか設定がぐちゃぐちゃになってくる。どの MCP を入れればいいか分からない、Skills や Hooks の使い分けに迷う、CLAUDE.md が肥大化してきた……そんな悩みを持つユーザーに向けて、Anthropic が公式プラグイン `claude-code-setup` をリリースした。

## claude-code-setup とは

`claude-code-setup` は、Anthropic の社員 Isabella He が作成・管理する公式プラグインだ。[anthropics/claude-plugins-official](https://github.com/anthropics/claude-plugins-official) リポジトリ（スター数 30,000 超）に収録されており、2026年6月時点でインストール数は **161,711 件**に上る。

このプラグインの役割は一言でいえば「Claude Code の初期セットアップを自動化するアドバイザー」だ。プロジェクトのコードを読んで、そのプロジェクトに最適な MCP・Skills・Hooks・サブエージェント・スラッシュコマンドの構成を提案してくれる。

## インストール方法

Claude Code のチャットで以下のコマンドを実行するだけでインストールできる。

```
/plugin install claude-code-setup@claude-plugins-official
```

Claude Code のプラグインシステム（`/plugin` コマンド）は 2025年10月9日に正式発表されたもので、`claude-plugins-official` は Anthropic 公式のマーケットプレイス名だ。

## 何を分析してくれるのか

インストール後にプラグインを起動すると、プロジェクトの以下の情報を自動的に読み取る。

- **project structure** — ディレクトリ構成、ファイルの種類
- **dependencies** — `package.json` などのパッケージ情報
- **code patterns** — 既存コードのスタイルや設計パターン

これらの情報を元に、そのプロジェクトに合った構成を提案してくれる。

## 提案内容の詳細

### MCP サーバー

プロジェクトの技術スタックに応じた MCP サーバーを提案する。代表的なものは以下の通り。

- **context7** — ドキュメント参照用 MCP
- **Playwright** — フロントエンドの動作確認用 MCP

### Skills（スラッシュコマンド）

開発ワークフローを効率化するスラッシュコマンドを提案する。

| コマンド | 用途 |
|---|---|
| `/test` | テスト実行 |
| `/pr-review` | PR レビュー |
| `/explain` | コード説明 |

また、**Plan agent** や **frontend-design Skill** なども提案対象に含まれる。

### Subagents（サブエージェント）

以下の専門エージェントが提案される。

- **security reviewer** — セキュリティ観点のレビュー
- **performance reviewer** — パフォーマンス観点のレビュー
- **accessibility reviewer** — アクセシビリティ観点のレビュー

### Hooks（自動実行フック）

コード品質を自動で維持するためのフックが提案される。

- **auto-format** — コミット前の自動フォーマット
- **auto-lint** — コミット前の自動 Lint チェック

## 「自己流」から「公式推奨」へ

Claude Code を長く使っていると、試行錯誤の結果として個人ごとに独自の設定が積み重なりがちだ。`claude-code-setup` が示すのは、その逆の発想だ。

**自己流でぐちゃぐちゃに育てる**のではなく、**公式プラグインに「何を ON にすべきか」を確認してもらう**というアプローチである。

プラグイン自体はファイルを変更しない読み取り専用の設計になっており、あくまで提案のみを行う。採用するかどうかはユーザーが判断できる。

## Claude Code プラグインエコシステムの現状

`claude-code-setup` は、Claude Code のプラグインシステム全体の一部に過ぎない。プラグインシステムは Skills・Agents・Hooks・MCP サーバー・LSP サーバー・バックグラウンドモニターをパッケージ化して配布できる仕組みで、コミュニティによるサードパーティプラグインも多数存在する。

公式マーケットプレイス `claude-plugins-official` には、セキュリティ、開発効率化、特定フレームワーク対応など、様々なプラグインが収録されている。

## まとめ

`claude-code-setup` は、Claude Code の初期設定や環境整理に悩む開発者にとって、最初に試すべき公式プラグインだ。プロジェクトの構造を読んで最適な構成を提案してくれるため、何を入れればいいか分からない段階でも利用できる。

インストールは `/plugin install claude-code-setup@claude-plugins-official` の一行で完結する。Claude Code を整えるなら、まずこの土台を確認してみることをおすすめする。
