# hdknr blog

Hugo + PaperMod で構築された技術ブログ。GitHub Pages でホスティング。

## プロジェクト構成

- `content/posts/` — ブログ記事（`YYYY-MM-DD-<slug>.md` 形式）
- `content/wiki/` — Wiki ページ
- `scripts/categorize.py` — カテゴリ・タグ自動付与スクリプト
- `hugo.toml` — Hugo 設定ファイル
- `.claude/skills/blog/` — `/blog` スキル定義

## 記事作成

- `/blog <トピック or GitHub Issue URL>` スキルで記事作成〜PR作成まで自動化
- 記事は日本語で記述
- フロントマター: title, date, lastmod, draft, categories, tags（+ source_url）
- カテゴリは `scripts/categorize.py` のルールに従う
- ビルド確認: `hugo --gc`

## カテゴリ一覧

AI/LLM, セキュリティ, クラウド/インフラ, Web開発, プログラミング言語, モバイル, データベース, ツール/開発環境, ビジネス/キャリア, 地域/グルメ, その他

## ブランチ・PR 規約

- ブランチ名: `blog/YYYY-MM-DD-<slug>`
- コミットメッセージ: `Add blog post: <記事タイトル>`
- PR タイトル: `Add blog: <記事タイトル>`
- ソースが GitHub URL の場合、PR 作成後にソース元へリンクを追記する
