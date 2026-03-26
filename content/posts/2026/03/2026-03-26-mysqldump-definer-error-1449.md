---
title: "mysqldump エラー 1449: DEFINER が存在しないユーザーを参照している場合の対処法"
date: 2026-03-26
lastmod: 2026-03-26
draft: false
categories: ["データベース"]
tags: ["mysql", "mysqldump", "definer", "view", "トラブルシューティング"]
---

`mysqldump` でデータベースをダンプしようとしたら、こんなエラーが出て止まった経験はないでしょうか。

```
mysqldump: Got error: 1449: The user specified as a definer ('root'@'%') does not exist when using LOCK TABLES
```

これは MySQL の **DEFINER** という仕組みに起因するエラーです。ビューやストアドプロシージャの作成時に記録された「定義者（DEFINER）」ユーザーが、現在のサーバー上に存在しない場合に発生します。

## なぜ起きるのか

MySQL のビュー、ストアドプロシージャ、トリガー、イベントには `DEFINER` 属性があります。これはそのオブジェクトを作成した MySQL ユーザーを記録したもので、`SQL SECURITY DEFINER`（デフォルト）の場合、オブジェクトの実行は **DEFINER ユーザーの権限** で行われます。

`mysqldump` は `LOCK TABLES` を実行する際、ダンプ対象のビューなどの `DEFINER` ユーザーを参照します。このとき、DEFINER に設定されたユーザー（例: `'root'@'%'`）がサーバー上に存在しなければ、エラー 1449 で処理が中断されます。

よくあるシナリオ:

- 本番環境から別環境にデータベースをコピーした際、元の環境にいた `root@'%'` が移行先に存在しない
- MySQL のユーザーを整理した際、ビューの DEFINER を更新し忘れた
- `root@'localhost'` しか存在しないのに、ビューが `root@'%'` で作成されていた

## DEFINER が問題のオブジェクトを特定する

まず、どのオブジェクトが問題の原因かを `information_schema` で確認します。

```sql
-- ビュー
SELECT DEFINER, TABLE_SCHEMA, TABLE_NAME
FROM information_schema.VIEWS
WHERE DEFINER LIKE '%root@%';

-- ストアドプロシージャ / ファンクション
SELECT DEFINER, ROUTINE_SCHEMA, ROUTINE_NAME, ROUTINE_TYPE
FROM information_schema.ROUTINES
WHERE DEFINER LIKE '%root@%';

-- イベント
SELECT EVENT_CATALOG, EVENT_SCHEMA, EVENT_NAME, DEFINER
FROM information_schema.EVENTS
WHERE DEFINER LIKE '%root@%';

-- トリガー
SELECT TRIGGER_SCHEMA, TRIGGER_NAME, DEFINER
FROM information_schema.TRIGGERS
WHERE DEFINER LIKE '%root@%';
```

多くの場合、ビューが原因です。該当するオブジェクトが見つかったら、その定義を確認しましょう。

```sql
SHOW CREATE VIEW your_database.your_view_name;
```

## 対処法

### 方法1: DEFINER を修正する（推奨）

問題のオブジェクトを再作成して、存在するユーザーに DEFINER を書き換えます。

```sql
-- 1. 現在の定義を確認
SHOW CREATE VIEW mydb.my_view;

-- 2. ビューを削除
DROP VIEW mydb.my_view;

-- 3. DEFINER を修正して再作成
-- DEFINER=`root`@`%` → DEFINER=`root`@`localhost` に変更
CREATE ALGORITHM=UNDEFINED
  DEFINER=`root`@`localhost`
  SQL SECURITY DEFINER
  VIEW mydb.my_view AS
  SELECT ...;
```

さらに、`SQL SECURITY INVOKER` に変更することも検討できます。`INVOKER` にすると、ビューを呼び出したユーザーの権限で実行されるため、DEFINER ユーザーの存在に依存しなくなります。

```sql
CREATE ALGORITHM=UNDEFINED
  DEFINER=`root`@`localhost`
  SQL SECURITY INVOKER
  VIEW mydb.my_view AS
  SELECT ...;
```

### 方法2: --skip-lock-tables で回避する（一時的）

根本的な修正が難しい場合、`mysqldump` のオプションで一時的に回避できます。

```bash
mysqldump -u your_user -p --skip-lock-tables your_database > dump.sql
```

ただし、このオプションはテーブルロックをスキップするため、ダンプ中に書き込みが発生するとデータの整合性が保証されません。あくまで緊急時の回避策として使い、根本原因の修正を優先してください。

### 方法3: 存在しないユーザーを作成する（非推奨）

`'root'@'%'` を作成して権限を付与する方法もありますが、`root` をワイルドカードホスト `%` で公開するのはセキュリティリスクが非常に高いため推奨しません。

## 予防策

- **ビュー作成時に DEFINER を明示する**: デフォルトでは接続ユーザーが DEFINER になるため、環境によって異なるユーザーが設定される
- **SQL SECURITY INVOKER を検討する**: DEFINER に依存しない設計にすることで、環境移行時のトラブルを防げる
- **データベース移行時に DEFINER を確認する**: `information_schema.VIEWS` 等で DEFINER を一括チェックし、移行先に存在するユーザーに揃える

## まとめ

エラー 1449 の本質は、`mysqldump` を実行するユーザーの権限ではなく、ダンプ対象のオブジェクトが内部的に参照している DEFINER ユーザーの問題です。`--skip-lock-tables` で一時回避はできますが、根本的には DEFINER の修正が必要です。データベースを別環境にコピーしたり、ユーザーを整理したりする際は、ビューやプロシージャの DEFINER を忘れずに確認しましょう。
