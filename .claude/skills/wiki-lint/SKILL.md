---
name: wiki-lint
description: Wiki の健全性チェック（矛盾検出、孤立ページ、欠落リンク、古い記述）
arguments: []
---

Wiki ナレッジベースの健全性をチェックし、問題を報告・修正します。

## チェック項目

### 1. 孤立ページ検出

他のどの Wiki ページからもリンクされていないページを検出する。

- `content/wiki/` 内の全ページを走査
- 各ページの「関連ページ」セクションのリンク先を収集
- どこからもリンクされていないページをリストアップ

### 2. 欠落リンク検出

Wiki ページ内のリンクが存在しないページを指している場合を検出する。

- 各ページの内部リンク（`/blogs/wiki/...`）を抽出
- リンク先のファイルが `content/wiki/` に存在するか確認
- 存在しないリンクをリストアップ

### 3. related_posts の検証

`related_posts` フロントマターで参照しているブログ記事が実在するか確認する。

- 各 Wiki ページの `related_posts` を抽出
- 対応する `content/posts/` のファイルが存在するか確認
- 存在しない参照をリストアップ

### 4. 古い記述の検出

`lastmod` が古い Wiki ページで、ソース記事が更新されている可能性があるものを検出する。

- Wiki ページの `lastmod` と `related_posts` の記事の `lastmod` を比較
- 記事のほうが新しい場合、Wiki ページの更新が必要な可能性をフラグ

### 5. フロントマター整合性

必須フロントマター項目が欠落しているページを検出する。

- 必須: title, description, date, lastmod, related_posts, tags
- 推奨: aliases

## 出力フォーマット

```markdown
## Wiki Lint レポート

### 孤立ページ (X件)
- `concepts/xxx.md` — どこからもリンクされていない

### 欠落リンク (X件)
- `tools/yyy.md` → `/blogs/wiki/concepts/zzz/` — リンク先が存在しない

### related_posts 不整合 (X件)
- `guides/aaa.md` → `/posts/2026/01/bbb/` — 記事が存在しない

### 古い可能性のあるページ (X件)
- `concepts/ccc.md` (lastmod: 2026-01-01) — ソース記事が 2026-03-15 に更新

### フロントマター不備 (X件)
- `tools/ddd.md` — aliases が未設定

### 統計
- 総ページ数: XX
- concepts: XX / tools: XX / guides: XX
```

## 修正の提案

問題が見つかった場合、以下の対応を提案する:

- **孤立ページ**: 関連する Wiki ページに相互リンクを追加
- **欠落リンク**: リンク先ページの作成、またはリンクの削除
- **related_posts 不整合**: 正しいパスに修正、または参照を削除
- **古いページ**: `/wiki-ingest` でソース記事を再読み込みして更新
- **フロントマター不備**: 欠落項目を補完

ユーザーの確認後に修正を実施する。
