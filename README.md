# hdknr blog

https://hdknr.github.io/blogs/

Hugo + PaperMod で構築された技術ブログ。GitHub Pages でホスティング。

## スクリプト

### blog-batch.sh — 未ブログ化コメントの一括処理

Issue コメントのうち、まだブログ化されていないもの（🚀 リアクションなし）を `claude -p` で一括処理する。

```bash
# 未ブログ化コメントの一覧確認
./scripts/blog-batch.sh 1 --dry-run

# 3件だけブログ化
./scripts/blog-batch.sh 1 --limit 3

# レビュー省略で高速に処理
./scripts/blog-batch.sh 1 --skip-review --limit 5

# opus モデルで処理
./scripts/blog-batch.sh 1 --model opus --limit 3

# 夜間バッチ（帰宅前に実行、翌朝PRレビュー）
nohup ./scripts/blog-batch.sh 1 --overnight > .claude/temp/blog-batch-stdout.log 2>&1 &

# 翌朝：レポート確認
cat .claude/temp/blog-batch-report-*.md
```

#### オプション

| オプション | 説明 | デフォルト |
|---|---|---|
| `--dry-run` | 一覧表示のみ（ブログ作成しない） | - |
| `--limit N` | 処理件数の上限 | 全件 |
| `--skip-review` | ファクトチェック・エージェントレビューを省略 | false |
| `--model MODEL` | 使用モデル | sonnet |
| `--interval SECS` | 処理間のインターバル（秒） | 5 |
| `--overnight` | 夜間バッチモード（レビュー省略 + インターバル60秒） | - |

#### ブログ化状態の管理

コメントのブログ化状態は GitHub リアクション（🚀）で管理される。

- 🚀 あり → ブログ化済み
- 🚀 なし → 未ブログ化
- `/blog` スキルで記事作成時に自動付与
- 重複等でスキップする場合は手動で付与

### categorize.py — カテゴリ・タグ自動付与

```bash
python scripts/categorize.py
```
