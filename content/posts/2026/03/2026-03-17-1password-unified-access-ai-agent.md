---
title: "1Password Unified Access：AIエージェント時代のシークレット管理が本格始動"
date: 2026-03-17
lastmod: 2026-03-17
slug: "1password-unified-access-ai-agent"
draft: false
source_url: "https://github.com/hdknr/blogs/issues/1#issuecomment-4077558341"
categories: ["セキュリティ"]
tags: ["1Password", "AIエージェント", "シークレット管理", "Claude Code", "Cursor"]
---

Claude Code や Cursor で開発していると、`.env` に書いた API キーを AI が普通にファイルシステムから読みに行く。`.gitignore` していても関係ない。この課題に対して、1Password が Anthropic・Cursor・GitHub・Vercel・Perplexity と連携し「AI エージェント時代のシークレット管理」を本気で構築し始めた。

## 何が発表されたのか

2026年3月17日、1Password は **1Password Unified Access** を発表した。人間・マシン・AI エージェントにまたがるアクセスを一元的に発見・保護・監査するためのプラットフォームだ。

従来のパスワードマネージャーの枠を超え、AI エージェントが本番環境で実際に動作する時代に合わせたクレデンシャル管理を提供する。

## なぜ必要なのか：.env 問題

AI コーディングツール（Claude Code、Cursor など）は、タスク遂行のためにローカルファイルシステム上のファイルを読む。`.env` ファイルに平文で保存された API キーやトークンは、AI エージェントから直接アクセスできてしまう。

`.gitignore` はリポジトリへのコミットを防ぐだけで、ローカルファイルシステム上での読み取りは防げない。つまり、現状の `.env` ベースのシークレット管理は AI エージェント時代には不十分だ。

## 各社との連携内容

### Anthropic（Claude Code / Cowork / ブラウザ拡張）

Anthropic は 1Password を統合し、Claude Code、Cowork、Claude ブラウザ拡張からボールト内のアイテムを安全にオートフィルできるようにする。ユーザーの同意のもと、Claude がサイトやサービスに 1Password から直接クレデンシャルを取得してログインできる仕組みだ。

### Cursor（Hooks による just-in-time シークレット）

Cursor との連携では、**Cursor Hooks** を活用した just-in-time なシークレット提供を実現する。

仕組みは以下の通り:

1. プロジェクトに `hooks.json` を設定
2. Cursor がシェルコマンドを実行する前に、1Password Environments Hook Script が起動
3. プロセスがアクセスを要求すると、1Password がユーザーに認証を求める
4. 承認されると、必要なシークレットがランタイムセッションのメモリ上にのみ提供される

これにより、平文キーがディスクやソースコードにコミットされることがなく、環境変数のハードコードやトークンの履歴残留も防げる。

1Password は Hook スクリプト集を [1Password/agent-hooks](https://github.com/1Password/agent-hooks) リポジトリで公開している。

### GitHub・Vercel

GitHub Actions や Vercel のデプロイ環境においても、CI/CD パイプライン上でのシークレット管理を 1Password 経由で統合する。

## 今後の展開

1Password は今後、以下の拡張を予定している:

- **スコープ付きクレデンシャル**: エージェントやマシンワークロードに対し、ランタイム時にスコープを限定したクレデンシャルを発行
- **きめ細かなポリシー**: チームごとに AI エージェントのタスク固有のアクセスルールを定義可能に
- **MCP 連携の拡充**: Cursor が外部 API やサービスを 1Password 経由で安全に利用できるよう MCP 統合を拡大

## 開発者が今すぐできること

1. **1Password SDK の AI エージェント統合チュートリアル**を確認する（[公式ドキュメント](https://developer.1password.com/docs/sdks/ai-agent/)）
2. Cursor ユーザーは **1Password Environments Hook** を導入し、`.env` の平文シークレットを排除する
3. `.env` ファイルへの依存を減らし、1Password Environments やシークレット参照（`op://vault/item/field`）への移行を検討する

AI エージェントがコードを書き、コマンドを実行し、API を叩く時代。シークレット管理のアプローチも根本から変える必要がある。
