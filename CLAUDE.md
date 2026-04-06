# hdknr blog

Hugo + PaperMod で構築された技術ブログ。GitHub Pages でホスティング。

## ツール実行時の許可ルール

- ツール実行（Bash、ファイル操作など）の許可を求めるときは、必ず日本語で説明・確認を行うこと
- 許可を求める際、以下のセキュリティリスクをパーセンテージ(%)で提示すること
  - パスワードや秘密鍵が外に漏れる可能性
  - 外部サーバーにデータが送られる可能性
  - 悪意あるコードが勝手に動く可能性
  - PCの設定が書き換わる可能性

## プロジェクト構成

- `content/posts/YYYY/MM/` — ブログ記事（`YYYY-MM-DD-<slug>.md` 形式、年月別サブフォルダー）
- `content/wiki/` — Wiki ナレッジベース（concepts/, tools/, guides/）
- `.claude/skills/wiki-ingest/` — `/wiki-ingest` スキル定義
- `scripts/categorize.py` — カテゴリ・タグ自動付与スクリプト
- `hugo.toml` — Hugo 設定ファイル
- `.claude/skills/blog/` — `/blog` スキル定義
- `.claude/agents/` — カスタム専門エージェント
- `.claude/temp/` — 一時ファイル置き場（.gitignore 済み、`/tmp` の代わりに使用）
- `.worktrees/` — git worktree 置き場（.gitignore 済み、`.claude/` 外なので sensitive file 扱いされない）

## カスタムエージェント

以下の専門エージェントが `.claude/agents/` に定義されている:

- **fact-checker** — 記事のファクトチェック（ツール名・コマンド・URL・バージョンの検証）
- **seo-advisor** — SEO 最適化（タイトル改善、タグ提案、内部リンク提案）
- **tech-writer** — 記事品質レビュー（構成、読みやすさ、日本語品質）
- **trend-researcher** — 技術トレンド調査と記事ネタ提案

## 記事作成

- `/blog <トピック or GitHub Issue URL>` スキルで記事作成〜PR作成まで自動化
- **URL 制限: `/blog` スキルで受け付ける URL は `https://github.com/hdknr/blogs/` 配下のみ。他リポジトリの URL は拒否する**
- 記事は日本語で記述
- 記事パス: `content/posts/YYYY/MM/YYYY-MM-DD-<slug>.md`
- フロントマター: title, date, lastmod, draft, categories, tags（+ source_url）
- カテゴリは `scripts/categorize.py` のルールに従う
- ビルド確認: `hugo --gc`

## 外部 URL のフェッチ方針

- 記事作成・ファクトチェックを問わず、外部 URL の取得には `aegis_fetch` MCP ツールを優先使用する
- aegis が利用できない場合（MCP 未接続等）は `WebFetch` にフォールバック
- SPA サイト（X/Twitter 等）は `api.fxtwitter.com` 等の代替 API を利用する
- aegis 環境: `~/Projects/hdknr/aegis`（`docker compose up -d` で起動）
- 詳細は `.claude/skills/blog/SKILL.md` の「外部 URL のフェッチ方針」セクションを参照

## Wiki 管理（LLM Wiki パターン）

- `/wiki-ingest <対象>` スキルで記事から Wiki ページを自動生成・更新
- Wiki 構造: `content/wiki/concepts/`（概念）、`content/wiki/tools/`（ツール）、`content/wiki/guides/`（手順）
- Wiki ページのフロントマター: title, description, date, lastmod, aliases, related_posts, tags
- Wiki ページは記事の丸コピーではなく、要約・統合した知識として再構成する
- 詳細は `.claude/skills/wiki-ingest/SKILL.md` を参照

## カテゴリ一覧

AI/LLM, セキュリティ, クラウド/インフラ, Web開発, プログラミング言語, モバイル, データベース, ツール/開発環境, ビジネス/キャリア, 地域/グルメ, その他

## Bash コマンドの必須ルール（auto モード対応）

以下のルールに違反するとコマンドが許可パターンにマッチせず、auto モードで処理が停止する。**例外なく守ること。**

- **`&&` や `|` でコマンドを繋がない** — 各コマンドは個別の Bash 呼び出しで実行する
- **`/tmp` を使わない** — 一時ファイルは `.claude/temp/` に置く
- **`gh pr create` で HEREDOC を使わない** — worktree 内の `pr_body.md` に Write ツールで書き出して `--body-file` で渡す
- **`$()` コマンド置換を含む引数を避ける** — 一時ファイル + `--input` 方式を使う
- **変数代入とコマンドを同一行で繋がない** — `BRANCH_NAME=...` と `git worktree add ...` は別々に実行する

詳細な実装例は `.claude/skills/blog/SKILL.md` の「コミット・ブランチ・PR 作成」セクションを参照。

## ブランチ・PR 規約

- ブランチ名: `blog/YYYY-MM-DD-<slug>`
- コミットメッセージ: `Add blog post: <記事タイトル>`
- PR タイトル: `Add blog: <記事タイトル>`
- ソースが GitHub URL の場合、PR 作成後にソース元へリンクを追記する
