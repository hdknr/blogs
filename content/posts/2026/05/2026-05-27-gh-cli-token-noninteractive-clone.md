---
title: "gh コマンドでトークン認証して非対話的にクローンする — CI/CD・使い捨てコンテナ向け認証パターン完全ガイド"
date: 2026-05-27
lastmod: 2026-05-27
slug: "gh-cli-token-noninteractive-clone"
draft: false
description: "ブラウザもキーボードもない CI/CD・コンテナ環境で gh / git clone をトークン認証する方法を整理。GH_TOKEN 環境変数・--with-token・GitHub Apps の使い分けと、gh auth token --web という誤情報の訂正、トークン履歴残留のセキュリティ注意点を解説。"
source_url: "https://github.com/hdknr/blogs/issues/93#issuecomment-4551836728"
categories: ["ツール/開発環境"]
tags: ["GitHub CLI", "gh", "認証", "GH_TOKEN", "CI/CD"]
---

`gh`（GitHub CLI）は通常、`gh auth login` の対話的なブラウザフローで認証します。しかし CI/CD パイプライン、共有サーバー、使い捨てコンテナのような **ブラウザもキーボード入力もない環境** では、その対話フローは使えません。

こうした「ヘッドレス（非対話）」環境では、**アクセストークン（パーソナルアクセストークンなど）を環境変数で渡す** ことでクローンを自動化できます。本記事では、推奨される認証パターンと、その際に陥りがちな落とし穴・セキュリティ上の注意点を整理します。

> なお、本記事を書く過程で「`gh auth token --web` でトークン生成画面を開ける」という情報を検証したところ、**そのようなフラグは存在しません**でした。よくある誤情報なので、後半で正しい代替手段とあわせて解説します。

## 方法1：環境変数 `GH_TOKEN` を使う（最もおすすめ）

`gh` は、環境変数 `GH_TOKEN`（または `GITHUB_TOKEN`）にトークンが設定されていると、それを自動的に認証に使用します。`gh auth login` のような状態の保存を一切行わないため、自動化環境に最も適しています。

一時的にトークンを渡してクローンする場合は、1 行で実行できます。

```bash
GH_TOKEN=ghp_YourTokenHere gh repo clone owner/repo
```

`gh auth login --help` のドキュメントにも、

> Alternatively, gh will use the authentication token found in environment variables. This method is most suitable for "headless" use of gh such as in automation.

と明記されており、**自動化での利用は `GH_TOKEN` が公式推奨**です。

- **メリット:** 認証情報をローカルに保存（ログイン状態を作成）しないため、CI/CD・共有サーバー・使い捨てコンテナで安全。
- **注意点:** トークンには対象リポジトリへのアクセス権限が必要です。クラシックな PAT なら `repo` スコープ、Fine-grained PAT なら対象リポジトリの Contents 読み取り権限などを付与しておきます。

### GitHub Actions での書き方

GitHub Actions では、自動的に払い出される `github.token` をそのまま渡すのが定石です。

```yaml
env:
  GH_TOKEN: ${{ github.token }}
```

これも `gh auth login --help` に記載されている公式の作法です。

## 方法2：`gh auth login --with-token` でトークンを記憶させる

一度ログイン状態を作り、それ以降は素の `gh` コマンドを使いたい場合は、標準入力からトークンをパイプで渡します。

```bash
echo "ghp_YourTokenHere" | gh auth login --with-token
```

ログインが完了すれば、以降は通常どおりクローンできます。

```bash
gh repo clone owner/repo
```

`--with-token` は **クラシック（classic）PAT を標準入力で受け取る** フラグです。`gh` の全機能を使う場合に推奨されるスコープとして、公式ドキュメントでは `repo`、`read:org`、`gist` が挙げられています（クローンだけなら `repo` で足ります）。

> Fine-grained PAT を `--with-token` に渡すと、リソースごとのスコープ制約が他リソース操作時に予期しない挙動を招くことがある、と公式が注意喚起しています。Fine-grained PAT を使うなら、方法1の `GH_TOKEN` 経由が無難です。

## 補足：素の `git clone` でトークンを使う

`gh` を使わず、標準の `git clone` でトークン認証したい場合は、URL にトークンを埋め込みます。

```bash
git clone https://oauth2:ghp_YourTokenHere@github.com/owner/repo.git
```

ユーザー名の部分に `oauth2` という文字列を入れるのがポイントです（実際にはユーザー名部分は任意の文字列でよく、トークンがパスワード扱いで認証されます）。

> ⚠️ **セキュリティ注意:** この方法はトークンが **シェル履歴（`~/.bash_history` など）** と **`.git/config` の `remote.origin.url`** に平文で残ります。使い捨てコンテナならともかく、永続環境では避けるべきです。CI ではログにトークンが出力されないよう、マスキング設定も確認してください。

## 「`gh` だけでトークンを新規発行」はできない

ここからは、よくある誤解の訂正です。

**有効なトークンを持っていない状態から、`gh` コマンドだけで新しい PAT を発行して文字列として取得することはできません。** GitHub のトークン（`ghp_...` / `github_pat_...`）は、セキュリティ設計上、**Web サイト上でユーザーが手動生成する**のが基本だからです。

### `gh auth token --web` は存在しない

「`gh auth token --web` で、スコープが選択済みのトークン生成画面をブラウザで開ける」という情報を見かけることがありますが、これは **誤り** です。実際に手元の `gh` で確認すると、`gh auth token` が受け付けるフラグは次の 2 つだけです。

```text
$ gh auth token --help
...
FLAGS
  -h, --hostname string   The hostname of the GitHub instance authenticated with
  -u, --user string       The account to output the token for
```

`--web` フラグは存在せず、`gh auth token` は **すでに保存済みのトークンを標準出力に表示するだけ** のコマンドです。トークン生成画面を開きたいだけなら、ブラウザで直接 `https://github.com/settings/tokens` を開くのが確実です。

### 推奨：そもそもトークンを「取得」せずに済ませる

目的が「`gh repo clone` を自動化したい」だけなら、トークンを画面に表示してコピペする必要はありません。一度ログインしてしまえば、以降は認証情報が安全に保存されます。

```bash
gh auth login
```

画面の指示に従い「GitHub.com」→「HTTPS」→「Log in with a web browser」を選ぶと、ブラウザでワンタイムコードを入力して承認できます。一度成功すれば、以降は素の `gh repo clone` / `git clone` が通ります。

### 既存のログイン状態からトークンを「確認」する

過去にそのマシンで `gh auth login` 済みなら、`gh` が内部で使っているトークンを表示できます。

```bash
gh auth token
```

`ghp_` や `gho_` で始まる現在有効なトークンが出力されるので、これをスクリプトや `GH_TOKEN` に渡して使い回せます。

## 完全自動化したいなら GitHub Apps

「人間のブラウザ操作を一切挟まず、コマンドだけでトークンを動的に発行したい」という高度な自動化を目指すなら、PAT ではなく **GitHub Apps** を使います。

1. GitHub App を作成し、対象リポジトリ/組織にインストールする
2. App の秘密鍵で JWT（JSON Web Token）を生成する
3. その JWT で API を叩き、有効期限の短い **インストールアクセストークン** を動的に取得する

この方式は、トークンが短命（デフォルト 1 時間）で自動失効するため、長寿命の PAT をばらまくよりはるかに安全です。ただし `gh` だけでは完結せず、JWT 生成スクリプト（`curl` や各言語の JWT ライブラリ）が別途必要になります。

## まとめ

| やりたいこと | 推奨手段 |
| --- | --- |
| CI/CD・コンテナで非対話クローン | `GH_TOKEN=...` を環境変数で渡す |
| GitHub Actions 内 | `GH_TOKEN: ${{ github.token }}` |
| 一度ログインして以降は素の gh | `echo ghp_... \| gh auth login --with-token` |
| 素の git でトークン認証 | `https://oauth2:ghp_...@github.com/...`（履歴残留に注意） |
| トークン生成画面を開く | ブラウザで `github.com/settings/tokens`（`gh auth token --web` は存在しない） |
| 既存トークンを確認 | `gh auth token` |
| 完全無人でトークン動的発行 | GitHub Apps + JWT |

非対話環境では `GH_TOKEN` 環境変数が最もクリーンで安全です。トークンを URL や履歴に残す方法は手軽ですが、永続環境では漏洩リスクがあるため、用途に応じて使い分けてください。
