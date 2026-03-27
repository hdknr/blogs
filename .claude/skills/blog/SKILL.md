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

## URL 制限（セキュリティ）

**重要: トピックとして GitHub URL が指定された場合、`https://github.com/hdknr/blogs/` 配下の URL のみ受け付ける。**

- 許可: `https://github.com/hdknr/blogs/issues/...`, `https://github.com/hdknr/blogs/pull/...` など
- 拒否: 上記以外のすべての GitHub URL（他のリポジトリ、他のオーナー）
- 拒否された場合はエラーメッセージを表示して処理を中断する:
  「エラー: このスキルで受け付ける URL は https://github.com/hdknr/blogs/ 配下のみです。」

## 手順

### 1. トピックの種類を判定する

トピック引数が以下のいずれかを判定する:

- **GitHub Issue コメント URL**: `https://github.com/hdknr/blogs/issues/{number}#issuecomment-{id}` 形式
- **GitHub Issue URL**: `https://github.com/hdknr/blogs/issues/{number}` 形式
- **テキストトピック**: 上記以外のテキスト（URL でないもの）
- **許可されていない URL**: 上記以外の URL → エラーで中断

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

- ファイルパス: `content/posts/YYYY/MM/YYYY-MM-DD-<slug>.md`
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

## 外部 URL のフェッチ方針

記事作成・ファクトチェックを問わず、外部 URL のコンテンツを取得する際は以下の優先順位に従う:

1. **`aegis_fetch` を優先使用する**
   - セキュリティスキャン（verdict: allow/warn/block）付きでコンテンツを取得できる
   - verdict が "warn" → ユーザーに警告を表示して確認を求める
   - verdict が "block" → コンテンツを使用せず、ユーザーに報告する
   - 取得した HTML/JSON の解析は Claude が直接行う

2. **`aegis_fetch` が利用できない場合は `WebFetch` にフォールバック**
   - MCP 未接続、aegis 未起動などの場合

3. **SPA（JavaScript 描画）サイトの場合**
   - `aegis_fetch` / `WebFetch` どちらでも生 HTML からコンテンツを取得できない場合がある
   - X (Twitter) の場合: URL を `api.fxtwitter.com` に変換して JSON API 経由で取得する
   - その他の SPA: `WebSearch` で該当ページの情報を検索する

## 記事の構成ガイドライン

- 見出し（##）を使って構造化する
- コード例がある場合はシンタックスハイライト付きのコードブロックを使用する
- 日本語で記述する
- 冒頭に概要・導入を書く
- 実用的な情報を含める（コマンド例、設定例、コードサンプルなど）
- GitHub コメント/Issue からの内容はそのまま活かしつつ、ブログ記事として読みやすく整形する

## ファクトチェック（情報検証）

記事をコミットする前に、以下の手順で記事内の事実関係を検証する。
**このステップは省略してはならない。**

### 検証対象

記事内の以下の項目をすべて抽出して検証する:

1. **ツール・サービス・ライブラリの存在確認**
   - 記事で言及しているツール、プラグイン、ライブラリ、サービスが実在するか
   - GitHub リポジトリの URL が記載されている場合、`gh api` で存在を確認する:
     ```bash
     gh api /repos/{owner}/{repo} --jq '.full_name' 2>&1
     ```
   - 公式サイトの URL がある場合、「外部 URL のフェッチ方針」に従って取得・検証する

2. **コマンド・APIの正確性**
   - 記事に記載されているインストールコマンドや CLI コマンドが正しい構文か
   - WebSearch で公式ドキュメントを検索し、コマンド構文を照合する

3. **機能・仕様の正確性**
   - 記事で説明している機能や仕様が実際に存在するか
   - WebSearch で公式ドキュメントやリリースノートを確認する

4. **バージョン・日付の正確性**
   - 記載されているバージョン番号やリリース日が正しいか

### 検証手順

1. 記事から検証すべき事実（claims）をリストアップする
2. 各事実について WebSearch または `gh api` で裏付けを取る
3. 検証結果を以下の形式で整理する:
   - ✅ **確認済み**: 裏付けが取れた事実
   - ⚠️ **要修正**: 部分的に正しいが修正が必要な事実
   - ❌ **誤り**: 裏付けが取れなかった事実（ハルシネーションの可能性）
   - ℹ️ **未確認**: 検証できなかったが重大なリスクは低い事実
4. ⚠️ または ❌ の項目がある場合は、記事を修正してから次のステップに進む
5. 検証結果をユーザーに報告し、修正内容の確認を求める

### 検証の重点ポイント

- **GitHub リポジトリの存在**: 記事内の GitHub URL は必ず `gh api` で確認する
- **コマンド構文**: インストールコマンドや設定コマンドは公式ドキュメントと照合する
- **プラグイン・拡張機能**: 「公式」と謳っている場合、本当に公式かを確認する
- **ソースがない独自の主張**: ソース元にない情報を記事作成時に追加した場合、特に慎重に検証する

## エージェントレビュー（品質向上）

ファクトチェック完了後、コミット前に以下の 2 つのカスタムエージェントを **並列実行** して記事の品質を高める。
**このステップは省略してはならない。**

### 実行方法

Agent ツールで `tech-writer` と `seo-advisor` を同時に起動する:

```
Agent(subagent_type="tech-writer", prompt="以下の記事をレビューしてください: $WORKTREE_DIR/content/posts/YYYY/MM/YYYY-MM-DD-<slug>.md")
Agent(subagent_type="seo-advisor", prompt="以下の記事を分析してください: $WORKTREE_DIR/content/posts/YYYY/MM/YYYY-MM-DD-<slug>.md")
```

- 2 つのエージェントは独立しているため、必ず **1 つのメッセージで並列起動** する
- エージェントは記事を読み取ってレビュー結果を返すだけで、ファイルは編集しない

### レビュー結果の反映

1. 両エージェントの結果を受け取る
2. 改善提案を以下の基準でフィルタリングする:
   - **即座に反映**: 誤字脱字、表記揺れ、明らかな構成の問題、タグの過不足
   - **ユーザーに確認**: タイトルの変更提案、カテゴリの変更提案、大幅な構成変更
   - **スキップ**: 好みの問題（文体の微調整など）、既存記事への内部リンク追加（別 PR で対応）
3. 反映した改善内容をユーザーに簡潔に報告する

## コミット・ブランチ・PR 作成（worktree 方式）

記事作成後、以下の手順で PR を作成する。
**重要: git worktree を使い、メインの作業ディレクトリのブランチを汚さないようにする。**
**重要: コマンドを `&&` で繋がないこと。** `&&` で繋いだ複合コマンドは許可パターンにマッチせず、毎回確認が求められる。各コマンドは個別の Bash 呼び出しとして実行する。

1. ブランチ名を決定する: `blog/YYYY-MM-DD-<slug>`
2. worktree を作成する:
   ```bash
   # メインリポジトリのルートで実行（main ブランチのまま）
   BRANCH_NAME="blog/YYYY-MM-DD-<slug>"
   git worktree add -b "$BRANCH_NAME" "../blogs-worktree-<slug>" main
   ```
3. **worktree の絶対パスを取得する（重要）:**
   ```bash
   git worktree list
   ```
   出力から worktree の絶対パスを読み取り、以降はその絶対パスを `$WORKTREE_DIR` として使う。
   **相対パスから絶対パスを推測してはならない。** Write ツールは存在しないパスにもファイルを作成するため、パスを間違えてもエラーにならず手戻りが発生する。
4. worktree 内で記事ファイルを作成する:
   - 記事の書き込み先: `$WORKTREE_DIR/content/posts/YYYY/MM/YYYY-MM-DD-<slug>.md`
5. worktree 内で Hugo ビルド確認（`cd` を使わず `--source` で指定）:
   ```bash
   hugo --source "$WORKTREE_DIR" --gc 2>&1 | tail -5
   ```
6. worktree 内でコミット・プッシュ（`cd` を使わず `git -C` で指定）:
   ```bash
   git -C "$WORKTREE_DIR" add content/posts/YYYY/MM/YYYY-MM-DD-<slug>.md
   git -C "$WORKTREE_DIR" commit -m "Add blog post: <記事タイトル>"
   git -C "$WORKTREE_DIR" push -u origin "$BRANCH_NAME"
   ```
7. PR を作成する（`--head` でブランチを明示指定し、`cd` を使わない）:
   まず PR 本文を一時ファイルに書き出し、`--body-file` で渡す（HEREDOC 内の `#` がセキュリティチェックに引っかかるのを回避）:
   ```bash
   cat > .claude/temp/pr_body.md <<'EOF'
   ## Summary
   - ...

   🤖 Generated with [Claude Code](https://claude.com/claude-code)
   EOF
   gh pr create --repo hdknr/blogs --head "$BRANCH_NAME" --title "Add blog: <記事タイトル>" --body-file .claude/temp/pr_body.md
   rm .claude/temp/pr_body.md
   ```
   **注意: `cd "$WORKTREE_DIR" && gh pr create` は使わないこと。** `cd` で始まるコマンドは `Bash(gh:*)` の許可パターンにマッチせず、毎回確認が求められる。`--head` フラグでブランチを指定すれば worktree 内にいる必要はない。
   **注意: `--body "$(cat <<'EOF'...)"` 方式は使わないこと。** HEREDOC 内の `#` 付き行がセキュリティチェック（"quoted newline followed by #-prefixed line"）に引っかかり、毎回確認が求められる。
8. PR の URL を控える（ソース元への追記に使用する）
9. worktree を削除する:
   ```bash
   git worktree remove "$WORKTREE_DIR"
   ```

## ソース元への PR リンク追記

PR 作成後、トピックが GitHub URL だった場合はソース元にブログ PR のリンクを追記する。

### Issue コメント URL がソースの場合

元のコメントを更新して、末尾にブログ PR リンクを追記する。
**注意: `$()` コマンド置換は使わないこと。** 置換を含むコマンドはセキュリティチェックが発動し、許可設定に関わらず毎回確認が求められる。代わりに一時ファイルと `--input` を使う。

1. 現在のコメント本文を一時ファイルに保存する:
   ```bash
   gh api /repos/{owner}/{repo}/issues/comments/{comment_id} --jq '.body' > .claude/temp/blog_comment_body.txt
   ```
2. PR リンクを末尾に追記する（Read + Edit ツールを使用し、Bash の printf を避ける）:
   - Read ツールで `.claude/temp/blog_comment_body.txt` を読み取る
   - Edit ツールでファイル末尾に `\n\n---\n📝 Blog: <PR_URL>` を追記する
   - **注意: `printf '\n\n---\n...'` は使わないこと。** `\n` エスケープがセキュリティチェック（quoted newline 検出）に抵触し、毎回同意が求められる。
3. jq で JSON を構築して一時ファイルに書き出す（パイプ `|` で繋がず個別に実行）:
   ```bash
   jq -n --rawfile body .claude/temp/blog_comment_body.txt '{body: $body}' > .claude/temp/patch_body.json
   ```
4. `gh api` で PATCH する（`--input` でファイルから読み取り）:
   ```bash
   gh api /repos/{owner}/{repo}/issues/comments/{comment_id} --method PATCH --input .claude/temp/patch_body.json
   ```
5. 一時ファイルを削除する（`&&` で繋がず個別に実行）:
   ```bash
   rm .claude/temp/blog_comment_body.txt
   ```
   ```bash
   rm .claude/temp/patch_body.json
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
