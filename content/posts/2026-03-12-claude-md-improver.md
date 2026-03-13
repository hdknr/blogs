---
title: "CLAUDE.mdを採点・改善してくれるClaude Code公式プラグイン claude-md-improver"
date: 2026-03-12
lastmod: 2026-03-12
draft: false
source_url: "https://github.com/hdknr/blogs/issues/1#issuecomment-4050693809"
categories: ["ツール/開発環境"]
tags: ["claude-code", "claude", "prompt"]
---

Claude Code を使っていると、プロジェクトのコンテキストを伝える `CLAUDE.md` の質が作業効率に直結することに気づきます。Anthropic 公式プラグイン **claude-md-management** に含まれる `claude-md-improver` スキルは、CLAUDE.md を自動で採点し、改善点を提案してくれる便利なツールです。

## claude-md-management プラグインとは

[claude-md-management](https://github.com/anthropics/claude-plugins-official/tree/main/plugins/claude-md-management) は、Anthropic が公式に管理している Claude Code プラグインです。CLAUDE.md ファイルの品質を監査し、セッションで得た知見を反映するための2つの機能を提供します。

| 機能 | 目的 | 使いどころ |
|---|---|---|
| `claude-md-improver`（スキル） | CLAUDE.md をコードベースの現状に合わせる | 定期的なメンテナンス |
| `/revise-claude-md`（コマンド） | セッション中の学びを記録する | セッション終了時 |

## インストール方法

ターミナルから以下のコマンドでインストールできます。

```bash
claude plugin add claude-md-management
```

Claude Code セッション内からは、`/plugin` コマンドで UI を開き、`claude-md-management` を選択してインストールすることもできます。

インストールスコープは以下の3種類から選べます。

| スコープ | 説明 |
|----------|------|
| User | 自分の全プロジェクトで有効（デフォルト） |
| Project | このリポジトリの全コラボレーターで有効（`.claude/settings.json` に記録） |
| Local | このリポジトリの自分だけで有効 |

その他のプラグイン管理コマンド:

```bash
claude plugin list          # インストール済みプラグインの一覧
claude plugin update --all  # 全プラグインを更新
claude plugin remove claude-md-management  # アンインストール
```

## claude-md-improver の使い方

Claude Code のセッション中に、以下のように話しかけるだけで起動します。

```
"audit my CLAUDE.md files"
"CLAUDE.mdをチェックして"
```

すると、リポジトリ内のすべての CLAUDE.md ファイルを自動で検出し、品質レポートを出力してくれます。

## 評価基準と採点

6つの評価基準でスコアリングされ、A〜Fのグレードが付きます。

| 基準 | 重要度 | チェック内容 |
|------|--------|-------------|
| コマンド/ワークフロー | 高 | ビルド・テスト・デプロイのコマンドが記載されているか |
| アーキテクチャの明確さ | 高 | コードベースの構造を Claude が理解できるか |
| 非自明なパターン | 中 | ハマりポイントや特殊なルールが書かれているか |
| 簡潔さ | 中 | 冗長な説明や自明な情報がないか |
| 最新性 | 高 | 現在のコードベースの状態を反映しているか |
| 実行可能性 | 高 | 指示がコピペで実行できる具体的なものか |

### グレードの目安

- **A (90-100)**: 包括的で最新、すぐ実行可能
- **B (70-89)**: 良いカバレッジ、軽微な不足あり
- **C (50-69)**: 基本情報はあるが主要セクションが欠落
- **D (30-49)**: まばら、または古い
- **F (0-29)**: 未作成、または著しく古い

## レポートの出力例

採点結果は以下のような形式で表示されます。

```
## CLAUDE.md Quality Report

### Summary
- Files found: 3
- Average score: 72/100
- Files needing update: 2

### ./CLAUDE.md (Project Root)
Score: 75/100 (Grade: B)

| Criterion        | Score | Notes                        |
|------------------|-------|------------------------------|
| Commands         | 18/20 | ビルドコマンドは完備         |
| Architecture     | 12/20 | ディレクトリ構成の説明が不足 |
| Non-obvious      | 10/15 | 環境変数の注意点を追加すべき |
| Conciseness      | 13/15 | 良好                         |
| Currency         | 10/15 | 一部古い記述あり             |
| Actionability    | 12/15 | 概ねコピペ可能               |
```

## 改善提案とその適用

レポート出力後、具体的な改善案が diff 形式で提示されます。承認すると自動的に CLAUDE.md に反映されます。

```diff
+ ## Environment Setup
+
+ Required environment variables:
+ ```bash
+ export DATABASE_URL=postgres://localhost:5432/mydb
+ export REDIS_URL=redis://localhost:6379
+ ```
```

改善提案は「本当に役立つ情報」に絞られており、コードから自明な内容や一般的なベストプラクティスは追加されません。

## /revise-claude-md コマンド

もう一つの機能 `/revise-claude-md` は、セッション中に発見した知見を CLAUDE.md に反映するためのコマンドです。

```
/revise-claude-md
```

セッション中に見つけた bash コマンド、コードパターン、環境の癖などを自動で検出し、適切な CLAUDE.md（または `.claude.local.md`）への追記を提案してくれます。

## 良い CLAUDE.md のポイント

プラグインが推奨する CLAUDE.md の原則は以下の通りです。

- **簡潔で人間が読みやすい**: 密度が高い方が冗長よりも良い
- **コピペ可能なコマンド**: すべてのコマンドがそのまま実行できる
- **プロジェクト固有の情報**: 一般的なアドバイスではなく、このプロジェクトならではのパターン
- **非自明なハマりポイント**: よくある間違いや注意点

推奨セクション構成:

1. Commands（ビルド、テスト、開発、リント）
2. Architecture（ディレクトリ構成）
3. Key Files（エントリポイント、設定ファイル）
4. Code Style（プロジェクトの規約）
5. Environment（必要な環境変数、セットアップ）
6. Testing（コマンド、パターン）
7. Gotchas（特殊な事情、よくある間違い）

## Tips

- セッション中に `#` キーを押すと、Claude が自動で学びを CLAUDE.md に反映してくれます
- 個人的な設定は `.claude.local.md` に書いてチームと分離できます（`.gitignore` に追加）
- ユーザー共通の設定は `~/.claude/CLAUDE.md` に置けます
- モノレポでは `packages/*/CLAUDE.md` にパッケージ固有のコンテキストを配置可能です

CLAUDE.md の品質がそのまま Claude Code の出力品質に影響するので、定期的に `claude-md-improver` で監査しておくのがおすすめです。
