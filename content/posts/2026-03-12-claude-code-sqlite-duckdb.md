---
title: "Claude Codeで大量データを扱うならSQLite/DuckDBを使おう"
date: 2026-03-12
lastmod: 2026-03-12
draft: false
source_url: "https://github.com/hdknr/blogs/issues/1#issuecomment-4049725427"
categories: ["AI/LLM"]
tags: ["claude-code", "sqlite", "duckdb"]
---

Claude Code で Markdown や JSON ファイルを直接編集してデータ管理を行うのは、少量のデータなら問題ありません。しかし、レコード数が100件を超えるような規模になると、スキーマ違反や細かいスクリプト制御の問題、パフォーマンスの低下が発生しやすくなります。こうした場面では、SQLite や DuckDB を活用するのが効果的です。

## Markdown/JSON 直接編集の限界

Claude Code にMarkdown ファイルや JSON ファイルを直接編集させる方法は、手軽で分かりやすい反面、データ量が増えると以下の問題が顕在化します。

- **スキーマ違反**: JSON の構造が崩れたり、必須フィールドが欠落するケースが発生する
- **細かいスクリプト制御が必要になる**: データの整合性を保つために、バリデーションや変換のスクリプトが増えていく
- **パフォーマンス低下**: ファイル全体を読み込んで書き戻す処理が、レコード数に比例して遅くなる

## SQLite を使うメリット

SQLite はファイルベースの軽量データベースで、Claude Code との相性が良好です。

```bash
# SQLite データベースを作成してテーブルを定義
sqlite3 data.db "CREATE TABLE items (id INTEGER PRIMARY KEY, name TEXT, value REAL);"

# Claude Code から SQL でデータを操作
sqlite3 data.db "INSERT INTO items (name, value) VALUES ('example', 42.0);"
sqlite3 data.db "SELECT * FROM items WHERE value > 10;"
```

- **ACID準拠**: データの整合性がデータベースエンジンによって保証される
- **SQL によるクエリ**: 複雑な検索・集計・更新が簡潔に記述できる
- **単一ファイル**: `.db` ファイル1つで完結し、バックアップやコピーが容易

## DuckDB を使うメリット

DuckDB は分析用途に特化したインプロセスデータベースです。CSV、Parquet、JSON などのファイルを直接 SQL でクエリできます。

```sql
-- CSV ファイルを直接クエリ（データのロード不要）
SELECT * FROM read_csv_auto('data.csv') WHERE category = 'A' LIMIT 10;

-- JSON ファイルも同様にクエリ可能
SELECT * FROM read_json_auto('records.json') WHERE status = 'active';

-- 集計処理も高速
SELECT category, COUNT(*), AVG(value) FROM read_csv_auto('data.csv') GROUP BY category;
```

- **ファイル直接クエリ**: 既存の CSV/JSON/Parquet ファイルをそのまま分析できる
- **高速な分析処理**: 列指向ストレージによる効率的な集計
- **MCP サーバー連携**: DuckDB の MCP サーバーを使えば、Claude Code から直接クエリを実行して結果を解釈できる

## 使い分けの目安

| ユースケース | 推奨ツール |
|---|---|
| 設定ファイルや少量データ（〜数十件） | Markdown / JSON |
| トランザクションが必要なデータ管理 | SQLite |
| 大量データの分析・集計 | DuckDB |
| 既存 CSV/Parquet の探索的分析 | DuckDB |

## Claude Code との連携パターン

### CLAUDE.md にデータベース操作のルールを記述する

```markdown
# データベース操作ルール
- データの追加・更新は SQLite (`data.db`) に対して SQL で行う
- Markdown や JSON ファイルを直接編集してデータを管理しない
- クエリ結果の確認には `sqlite3 data.db "SELECT ..."` を使用する
```

### System Skill パターン

CLI ツール、SKILL.md、SQLite データベースを組み合わせることで、Claude Code にデータ操作を体系的に行わせることができます。SKILL.md にデータベースのスキーマと操作手順を記述しておけば、Claude Code が適切な SQL を生成して実行します。

## まとめ

Claude Code で100件を超えるデータを扱う場合は、Markdown や JSON の直接編集から SQLite や DuckDB に切り替えることで、データの整合性とパフォーマンスの両方を改善できます。用途に応じて SQLite（トランザクション重視）と DuckDB（分析重視）を使い分けましょう。
