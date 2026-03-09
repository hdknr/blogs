---
name: blog
description: Hugo ブログ記事を新規作成し、PR を作成する
arguments:
  - name: topic
    description: "記事のトピック、タイトル、または GitHub Issue コメント URL"
    required: true
  - name: date
    description: "記事の日付（YYYY-MM-DD 形式）。省略時は本日"
    required: false
---

指定されたトピックで Hugo ブログ記事を作成し、PR を作成してください。

## 手順

### 1. トピックの種類を判定する

トピック引数が以下のいずれかを判定する:

- **GitHub Issue コメント URL**: `https://github.com/{owner}/{repo}/issues/{number}#issuecomment-{id}` 形式
- **GitHub Issue URL**: `https://github.com/{owner}/{repo}/issues/{number}` 形式
- **テキストトピック**: 上記以外のテキスト

### 2. GitHub Issue コメント URL の場合

URL からコメント内容を取得してブログ記事のソースにする:

1. URL をパースして `owner`, `repo`, `issue_number`, `comment_id` を抽出する
2. コメント本文を取得する:
   ```bash
   gh api /repos/{owner}/{repo}/issues/comments/{comment_id} --jq '{body, created_at, html_url}'
   ```
3. Issue のタイトルも取得する:
   ```bash
   gh api /repos/{owner}/{repo}/issues/{issue_number} --jq '{title, body}'
   ```
4. コメント本文をブログ記事の内容として使用する
5. 記事タイトルはコメント内容の最初の見出し（`#` or `##`）から取得する。見出しがなければ Issue タイトルを使用する
6. 日付はコメントの `created_at` から取得する（引数で上書き可能）
7. フロントマターに `source_url` としてコメントの `html_url` を記録する

### 3. GitHub Issue URL の場合

Issue 本文を取得してブログ記事のソースにする:

1. URL をパースして `owner`, `repo`, `issue_number` を抽出する
2. Issue の情報を取得する:
   ```bash
   gh api /repos/{owner}/{repo}/issues/{issue_number} --jq '{title, body, created_at, html_url}'
   ```
3. Issue 本文をブログ記事の内容として使用する
4. 記事タイトルは Issue タイトルを使用する
5. フロントマターに `source_url` として Issue の `html_url` を記録する

### 4. テキストトピックの場合

- トピックに基づいて、技術ブログ記事としてふさわしい内容を作成する
- ユーザーがトピックのみ指定した場合は、WebSearch で最新情報を調査して記事を作成する
- ユーザーが内容も指定した場合は、その内容をベースに記事を整形する

### 5. 対象日付を決定する

- 引数で日付（YYYY-MM-DD）が指定されている場合はその日付を使用する
- GitHub URL の場合はコメント/Issue の `created_at` を使用する
- それ以外の場合は今日の日付を使用する（`date +%Y-%m-%d`）

### 6. 記事ファイルを作成する

- ファイルパス: `content/posts/YYYY-MM-DD-<slug>.md`
- `<slug>` はトピックから生成する（英数字・ハイフンのみ、小文字）
- 同名ファイルが既に存在する場合はサフィックスを追加する（例: `-2`）

### 7. カテゴリとタグを自動付与する

- `scripts/categorize.py` のルールに基づいて、記事の内容からカテゴリとタグを判定する
- カテゴリは以下から最適なものを1つ選択する:
  - AI/LLM, セキュリティ, クラウド/インフラ, Web開発, プログラミング言語,
    モバイル, データベース, ツール/開発環境, ビジネス/キャリア, 地域/グルメ, その他
- タグは内容に関連するものを最大5つ選択する

## フロントマターのテンプレート

GitHub URL ソースの場合:

```yaml
---
title: "記事タイトル"
date: YYYY-MM-DD
lastmod: YYYY-MM-DD
draft: false
source_url: "https://github.com/..."
categories: ["カテゴリ"]
tags: ["tag1", "tag2"]
---
```

テキストトピックの場合:

```yaml
---
title: "記事タイトル"
date: YYYY-MM-DD
lastmod: YYYY-MM-DD
draft: false
categories: ["カテゴリ"]
tags: ["tag1", "tag2"]
---
```

## 記事の構成ガイドライン

- 見出し（##）を使って構造化する
- コード例がある場合はシンタックスハイライト付きのコードブロックを使用する
- 日本語で記述する
- 冒頭に概要・導入を書く
- 実用的な情報を含める（コマンド例、設定例、コードサンプルなど）
- GitHub コメント/Issue からの内容はそのまま活かしつつ、ブログ記事として読みやすく整形する

## コミット・ブランチ・PR 作成（worktree 方式）

記事作成後、以下の手順で PR を作成する。
**重要: git worktree を使い、メインの作業ディレクトリのブランチを汚さないようにする。**

1. ブランチ名を決定する: `blog/YYYY-MM-DD-<slug>`
2. worktree を作成してそこで作業する:
   ```bash
   # メインリポジトリのルートで実行（main ブランチのまま）
   BRANCH_NAME="blog/YYYY-MM-DD-<slug>"
   WORKTREE_DIR="../blogs-worktree-<slug>"

   git worktree add -b "$BRANCH_NAME" "$WORKTREE_DIR" main
   ```
3. worktree 内で記事ファイルを作成する:
   - 記事の書き込み先: `$WORKTREE_DIR/content/posts/YYYY-MM-DD-<slug>.md`
4. worktree 内で Hugo ビルド確認:
   ```bash
   cd "$WORKTREE_DIR" && hugo --gc 2>&1 | tail -5
   ```
5. worktree 内でコミット・プッシュ:
   ```bash
   cd "$WORKTREE_DIR"
   git add content/posts/YYYY-MM-DD-<slug>.md
   git commit -m "Add blog post: <記事タイトル>"
   git push -u origin "$BRANCH_NAME"
   ```
6. PR を作成する:
   ```bash
   cd "$WORKTREE_DIR"
   gh pr create --repo hdknr/blogs --title "Add blog: <記事タイトル>" --body "$(cat <<'EOF'
   ## Summary
   - 新規ブログ記事: <記事タイトル>
   - ファイル: content/posts/YYYY-MM-DD-<slug>.md
   - ソース: <source_url or "オリジナル">

   🤖 Generated with [Claude Code](https://claude.com/claude-code)
   EOF
   )"
   ```
7. PR の URL を控える（ソース元への追記に使用する）
8. worktree を削除する:
   ```bash
   cd <メインリポジトリのルート>
   git worktree remove "$WORKTREE_DIR"
   ```

## ソース元への PR リンク追記

PR 作成後、トピックが GitHub URL だった場合はソース元にブログ PR のリンクを追記する。

### Issue コメント URL がソースの場合

元のコメントを更新して、末尾にブログ PR リンクを追記する:

1. 現在のコメント本文を取得する:
   ```bash
   gh api /repos/{owner}/{repo}/issues/comments/{comment_id} --jq '.body'
   ```
2. コメント本文の末尾に PR リンクを追記して更新する:
   ```bash
   gh api /repos/{owner}/{repo}/issues/comments/{comment_id} \
     --method PATCH \
     --field body="<既存の本文>

   ---
   📝 Blog: <PR_URL>"
   ```

### Issue URL がソースの場合

Issue に新しいコメントを追加して PR リンクを通知する:

```bash
gh api /repos/{owner}/{repo}/issues/{issue_number}/comments \
  --method POST \
  --field body="📝 この Issue からブログ記事を作成しました: <PR_URL>"
```

## 後処理

1. worktree は PR 作成手順の中で削除済み（メインリポジトリは main ブランチのまま）
2. 作成した PR の URL をユーザーに伝える
