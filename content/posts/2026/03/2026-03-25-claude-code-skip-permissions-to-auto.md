---
title: "Claude Code: dangerously-skip-permissions をやめて auto mode に移行する"
date: 2026-03-25
lastmod: 2026-03-25
draft: false
description: "Claude Code の dangerously-skip-permissions は権限チェックを完全無視する危険なオプション。auto mode なら安全性チェック付きでツールを自動承認できる。設定方法と違いを解説。"
source_url: "https://github.com/hdknr/blogs/issues/1#issuecomment-4129378712"
categories: ["AI/LLM"]
tags: ["claude-code", "claude", "anthropic", "agent", "security"]
---

Claude Code で長時間タスクを実行する際、許可プロンプトを回避するために `--dangerously-skip-permissions` を使っていた開発者は少なくないだろう。しかし、auto mode の登場により、安全性を保ちながら同様の利便性を得られるようになった。この記事では、両者の違いと auto mode への移行方法を解説する。

## dangerously-skip-permissions の問題

`claude --dangerously-skip-permissions` は、すべての権限チェックを無効化するフラグだ。ファイルの書き込み、シェルコマンドの実行、外部通信など、あらゆる操作が無条件で許可される。

このフラグには以下のリスクがある:

- **プロンプトインジェクション**: 悪意あるファイルを読み込んだ場合、任意のコマンドが無条件で実行される
- **意図しない破壊操作**: `rm -rf` のような危険なコマンドもチェックなしで実行される
- **認証情報の漏洩**: `.env` ファイルの内容を外部に送信するような操作も通過する
- **Anthropic の開発者も不使用**: 社内でも使用が推奨されていない

鹿野 壮 氏（[@tonkotsuboy_com](https://x.com/tonkotsuboy_com)、Ubie）は当時の状況をこう振り返っている:

> 「男は黙って claude --dangerously-skip-permissions」。そうやって生きてきたけど、Anthropicの開発者が使ってなかったり、プロジェクトでは禁止されたりで、肩身の狭い日々でした

## auto mode とは

auto mode は、dangerously-skip-permissions に代わる安全な選択肢だ。ツールの実行を自動承認しつつ、バックグラウンドで安全性チェックを行う。

### 両者の比較

| | dangerously-skip-permissions | auto mode |
|---|---|---|
| 権限チェック | 完全無効 | バックグラウンドで実行 |
| 安全性 | なし | セーフガード付き |
| プロンプトインジェクション耐性 | なし | あり |
| 危険なコマンドの実行 | 無条件で実行 | 検出してブロック |
| 公式ステータス | 推奨されていない | リサーチプレビュー（2026年3月時点） |

## auto mode の設定方法

### 起動時に指定する

```bash
claude --permission-mode auto
```

### settings.json でデフォルトにする

`settings.json` の `permissions` に `"defaultMode": "auto"` を指定すれば、毎回のフラグ指定が不要になる:

```json
{
  "permissions": {
    "defaultMode": "auto"
  }
}
```

この設定は以下の場所に配置できる:

- **プロジェクト単位**: `.claude/settings.json`（リポジトリにコミット可能）
- **ユーザー単位**: `~/.claude/settings.json`

### 許可パターンとの併用

auto mode は、`settings.json` の `permissions.allow` で定義した許可パターンと併用できる。許可パターンにマッチするコマンドは即座に実行され、マッチしないコマンドは auto mode のセーフガードが判断する:

```json
{
  "permissions": {
    "defaultMode": "auto",
    "allow": [
      "Bash(git:*)",
      "Bash(npm:*)",
      "Bash(hugo:*)"
    ]
  }
}
```

## 移行のポイント

### 1. CI/CD での使用

CI/CD 環境では引き続き `--dangerously-skip-permissions` が必要な場合がある。ただし、Docker コンテナ内など隔離された環境での使用に限定すべきだ。

### 2. Team プランの要件

2026年3月時点で、auto mode は Team プラン以上で利用可能。個人プランへの展開も計画されている。

### 3. 既存の許可パターンの活用

auto mode に移行しても、`settings.json` の許可パターンは引き続き有効だ。よく使うコマンドを許可パターンに登録しておけば、auto mode のオーバーヘッドなく即座に実行される。

## まとめ

`--dangerously-skip-permissions` は「許可プロンプトが煩わしい」という課題への暫定的な解決策だった。auto mode は同じ課題をより安全に解決する。

移行手順は簡単だ:

1. `settings.json` に `"defaultMode": "auto"` を追加する
2. よく使うコマンドは `permissions.allow` に登録する
3. `--dangerously-skip-permissions` の使用を CI/CD の隔離環境に限定する

セキュリティと利便性のバランスを取りながら、Claude Code を活用していこう。
