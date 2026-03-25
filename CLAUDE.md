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

- `content/posts/` — ブログ記事（`YYYY-MM-DD-<slug>.md` 形式）
- `content/wiki/` — Wiki ページ
- `scripts/categorize.py` — カテゴリ・タグ自動付与スクリプト
- `hugo.toml` — Hugo 設定ファイル
- `.claude/skills/blog/` — `/blog` スキル定義
- `.claude/agents/` — カスタム専門エージェント
- `.claude/temp/` — 一時ファイル置き場（.gitignore 済み、`/tmp` の代わりに使用）

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
- フロントマター: title, date, lastmod, draft, categories, tags（+ source_url）
- カテゴリは `scripts/categorize.py` のルールに従う
- ビルド確認: `hugo --gc`

## 外部 URL のフェッチ方針

- 記事作成・ファクトチェックを問わず、外部 URL の取得には `aegis_fetch` MCP ツールを優先使用する
- aegis が利用できない場合（MCP 未接続等）は `WebFetch` にフォールバック
- SPA サイト（X/Twitter 等）は `api.fxtwitter.com` 等の代替 API を利用する
- aegis 環境: `~/Projects/hdknr/aegis`（`docker compose up -d` で起動）
- 詳細は `.claude/skills/blog/SKILL.md` の「外部 URL のフェッチ方針」セクションを参照

## カテゴリ一覧

AI/LLM, セキュリティ, クラウド/インフラ, Web開発, プログラミング言語, モバイル, データベース, ツール/開発環境, ビジネス/キャリア, 地域/グルメ, その他

## ブランチ・PR 規約

- ブランチ名: `blog/YYYY-MM-DD-<slug>`
- コミットメッセージ: `Add blog post: <記事タイトル>`
- PR タイトル: `Add blog: <記事タイトル>`
- ソースが GitHub URL の場合、PR 作成後にソース元へリンクを追記する
