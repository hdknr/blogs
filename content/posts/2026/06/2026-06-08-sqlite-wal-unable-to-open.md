---
title: "SQLite の「unable to open database file」が高負荷時刻に散発する問題を WAL 化で根治した話"
date: 2026-06-08
lastmod: 2026-06-08
slug: "sqlite-wal-unable-to-open"
draft: false
gist_id: "81a75d6c694992b4769ebb647d245087"
gist_url: "https://gist.github.com/hdknr/81a75d6c694992b4769ebb647d245087"
categories: ["データベース"]
tags: ["sqlite", "wal", "sqlalchemy", "python", "database"]
---

# SQLite の「unable to open database file」が高負荷時刻に散発する問題を WAL 化で根治した話

ある自立型トレーディングシステムの運用中に、SQLite が `OperationalError: unable to open database file` を散発的に投げる慢性バグを追い詰めて修正した記録です。「ディスクは空いている」「ファイルは存在する」のにエラーが出る、という一見矛盾した現象の正体と、その根治・緩和の二段構えの対策をまとめます。

---

## WAL とは?

本題に入る前に、今回のキーになる **WAL（Write-Ahead Logging）** を簡単に押さえておきます。

SQLite には書き込み中のクラッシュからデータを守るための「ジャーナル方式」が複数あり、`journal_mode` PRAGMA で切り替えます。

- **`delete`（デフォルト）** — ロールバックジャーナル方式。トランザクションを開始するたびに `元DB-journal` というファイルを**新規作成**して変更前の内容を退避し、コミット時に削除する。書き込み中は DB 本体を直接書き換えるため、**読み取りと書き込みが互いをブロック**する。
- **`WAL`** — 先行書き込みログ方式。変更を DB 本体ではなく追記専用の `元DB-wal` ファイルに**追記**していき、後で「チェックポイント」で本体に反映する。`-wal` と `-shm`（共有メモリインデックス）は一度作られたら使い回されるため、**トランザクション毎のファイル新規作成が発生しない**。

WAL の主な利点:

| 特徴 | 効果 |
|------|------|
| 読み書きが互いをブロックしない | reader はトランザクション中の writer を待たずに読める（その逆も） |
| ジャーナルファイルを毎回作らない | ファイル作成のオーバーヘッドと競合がなくなる |
| 書き込みが概ね高速 | fsync 回数を減らせる（特に `synchronous=NORMAL` 併用時） |

**WAL が向いているケース**: 読み取りが多く・書き込みもそれなりにある、同一ホスト上の単一プロセス／複数プロセスからのアクセス。今回のように「書き込みデーモン 1 つ＋複数の reader」という構成は典型的な適用例です。

**WAL の注意点**: ① ネットワーク越しのファイルシステム（NFS など）では共有メモリが使えず非対応、② in-memory DB では効かない、③ `-wal` / `-shm` ファイルが DB 本体と併存するため、バックアップは単純な `cp` ではなく専用 API（後述）を使う必要がある。

> 一度 `WAL` に設定すると、その設定は DB ファイルに永続化され、以降の接続にも引き継がれます（接続ごとに毎回設定し直す必要はありませんが、本記事では確実を期して接続イベントで設定しています）。

---

## 1. 症状 — 自動エラーレポート

毎時 0 分に走る BTC 価格収集ジョブ `collect_btc` から、こんなエラーが自動 Issue 化されました。

```
OperationalError: (sqlite3.OperationalError) unable to open database file
[SQL: INSERT INTO btc_prices (timestamp, bid, ask, last, volume, source, created_at)
      VALUES (?, ?, ?, ?, ?, ?, ?)]
[parameters: ('2026-06-05 06:00:00.121421', 14995000.0, 15005000.0,
              15000000.0, 100.0, 'bitflyer', '2026-06-05 06:00:00.124079')]
```

発生時刻は **06:00 UTC = 15:00 JST**。スタックトレースを追うと、セッション管理ヘルパーの `session.commit()` 内の INSERT フラッシュで落ちていました。

ポイントは **次のサイクルで自己回復する** こと。価格テーブルはその後も問題なく蓄積され、データ欠損はこの 1 サイクルだけ。つまり「運用は止まらないが、毎日のようにエラー Issue が湧く」という、地味に厄介なノイズ源でした。

---

## 2. 「これは前にも見た」— 既知の慢性パターン

調べると、同じシグネチャのエラーは過去にも切り出し調査されていました。当時の計測がよくできていて、**発生時刻に明確な偏り**があったのです。

| JST 時刻 | 件数 | 対応ジョブ |
|---|---|---|
| 04:50 | 21 | 価格プリフェッチ (cron minute=50) |
| 05:00 | 20 | 日次プラン生成 (cron minute=0) |
| 09:00〜15:00 | 各数件 | ユニバース価格スキャン (毎時 minute=0) |

**重いジョブが走る `minute=0` / `minute=50` に集中**している。4 週間で 79 件。今回の事例（15:00 JST）もユニバース価格スキャンと BTC 収集が同時に起動するスロットで、ぴったり一致しました。

つまり今回の自動エラーは単発の新規バグではなく、**以前から続く慢性パターンの再発インスタンス**だったわけです。

---

## 3. 犯人探し — 仮説の絞り込み

`unable to open database file` は SQLite では割と漠然としたエラーで、原因の候補が複数あります。先行調査で挙がっていた仮説を、現在のデータで検証し直しました。

### 仮説A: ディスク逼迫 → 棄却

先行調査の時点ではディスク使用率が **94%** で「APFS のスナップショット領域や Spotlight インデックスと競合しているのでは」という説がありました。しかし今回確認すると、ディスクは整理されて **空き 72GB** に改善済み。それでもエラーは再発していました。

```
$ df -h /
/dev/disk3s1s1   926Gi  12Gi  72Gi  15%  /     ← 余裕あり
```

→ **ディスク逼迫は原因ではない。**

### 仮説B: ロールバックジャーナルの作成レース → 本命

決め手は `journal_mode` の設定でした。

```
$ sqlite3 app.db "PRAGMA journal_mode;"
delete                          ← WAL ではない
```

SQLite のデフォルトである **`journal_mode=delete`** は、**トランザクションを開始するたびに `app.db-journal` というロールバックジャーナルファイルを新規 `open()` する**仕組みです。コミットすると削除し、次のトランザクションでまた作る。

ここでこのシステムは、複数のジョブ（価格プリフェッチ / 日次プラン生成 / ユニバース価格スキャン / BTC 収集）が同じ毎時 0 分に並列で DB 接続を開きます。さらに AI エージェントをサブプロセスで大量起動するため、同一ディレクトリへのファイル作成が瞬間的に集中します。

> 複数プロセス／接続が同じ瞬間に `app.db-journal` を `open(O_CREAT)` しようとすると、APFS のディレクトリエントリ更新と SQLite の open がレースし、一瞬だけ "unable to open database file" を返す。

先行調査の観測で、エラー直後に **別ライブラリ内部の SQLite キャッシュ DB も同じエラーを出していた**ことも傍証になりました。アプリ DB 固有ではなく「その瞬間に開かれる SQLite 接続が広く失敗する」 → ファイル作成の競合という筋が通ります。

→ **journal_mode=delete によるジャーナル作成レースが本命。**

---

## 4. 対策 — 根治と緩和の二段構え

原因が「トランザクションごとのジャーナルファイル作成」なら、**それ自体を無くせばいい**。WAL モードへの切り替えが根治策、リトライが保険、という二段構えにしました。

### 対策1: WAL 化（根治）

接続ごとに PRAGMA を設定します。エンジン生成箇所に SQLAlchemy の `connect` イベントリスナーを仕込みました。

```python
def _set_sqlite_pragmas(dbapi_conn, _connection_record):
    cursor = dbapi_conn.cursor()
    cursor.execute("PRAGMA busy_timeout=5000")   # WAL 切替自体の競合も防ぐため先に
    cursor.execute("PRAGMA journal_mode=WAL")
    cursor.execute("PRAGMA synchronous=NORMAL")
    cursor.close()


def get_engine(url=None):
    db_url = url or get_settings().database_url
    if db_url not in _engine_cache:
        engine = create_engine(db_url, echo=False)
        if db_url.startswith("sqlite"):
            event.listen(engine, "connect", _set_sqlite_pragmas)
        _engine_cache[db_url] = engine
    return _engine_cache[db_url]
```

各 PRAGMA の意図:

| PRAGMA | 値 | 目的 |
|--------|-----|------|
| `busy_timeout` | 5000 | writer 競合時に即エラーにせず最大 5 秒待つ。**WAL 切替自体がロック競合で落ちないよう最初に設定** |
| `journal_mode` | WAL | トランザクション毎の `-journal` 新規作成を不要化 → **レースの根本除去**。読み書きが互いをブロックしない |
| `synchronous` | NORMAL | WAL では FULL と同等の耐障害性で fsync 回数を削減 |

WAL は writer が `-journal` を毎回作らず、追記専用の `-wal` ファイルに書く方式。これでファイル作成レースの土俵そのものが消えます。前提として **writer プロセスは監視デーモン 1 つ**、reader（CLI / pytest）は読み取りなので、WAL の制約（同一ホスト内マルチプロセスは OK）にも合致します。

### 対策2: 限定リトライ（緩和）

WAL 化しても残る瞬断を吸収する保険として、セッションのコミットにリトライを足しました。ただし **無条件リトライは危険**なので、強いガードを付けています。

```python
def _commit_with_retry(session, flush_state):
    for attempt in range(1, COMMIT_RETRIES + 1):
        pending = list(session.new)              # rollback で消えるので控える
        has_non_insert = bool(session.dirty) or bool(session.deleted)
        try:
            session.commit()
            return
        except OperationalError as e:
            retryable = (
                RETRYABLE_SQLITE_ERROR in str(e)   # "unable to open database file" 限定
                and pending                        # pending な INSERT がある
                and not has_non_insert             # UPDATE/DELETE を含まない
                and not flush_state["flushed"]     # まだ flush されていない
                and attempt < COMMIT_RETRIES
            )
            if not retryable:
                raise
            session.rollback()
            for obj in pending:
                session.add(obj)                   # 控えた pending を再投入
            time.sleep(COMMIT_BACKOFF_SEC * attempt)
```

**なぜここまでガードするのか** — リトライの本質は「rollback してやり直す」ことですが、これが安全なのは限られた条件だけです。

- **UPDATE/DELETE を含む場合**: rollback すると persistent オブジェクトへの変更が失われ、再現できない → 即時 raise
- **yield 中に flush 済みの場合**: rollback 後の再コミットは flush 済み行を含まず、**サイレントな部分喪失**になる → 即時 raise。SQLAlchemy の `after_flush` イベントで flush の発生を追跡しています
- **別シグネチャ（`database is locked` 等）**: そもそも対象外 → 即時 raise

「INSERT のみ・flush 未実行」という、やり直しても完全に同じ結果になるトランザクションに限ってのみリトライする、という設計です。

---

## 5. テスト — 実 SQLite ファイルで瞬断を再現

このプロジェクトには「**DB に書き込むテストは MagicMock ではなく実 SQLite セッションを使う**」という規約があります（過去に MagicMock が NOT NULL 制約を空振りさせて本番バグを見逃した経緯あり）。WAL は in-memory DB では効かないので、`tmp_path` の実ファイル DB で検証しました。

検証項目:

- WAL / busy_timeout / synchronous が実際に接続へ適用されること
- `commit` を 2 回失敗 → 3 回目成功させ、**INSERT が 1 件も失われない**こと
- リトライ上限まで失敗したら raise し、無限ループしないこと
- `database is locked`（別シグネチャ）は **1 回で即 raise**
- UPDATE を含むトランザクション / flush 済みトランザクションは **リトライせず即 raise**

エラー再現の fixture も、短い代用文字列ではなく **本番と同じシグネチャ**を作るヘルパーにしました。これも規約（「エラー文字列を fixture に使う場合は実例外を再現する」）に沿ったものです。

```python
def sqlite_unable_to_open_error():
    orig = sqlite3.OperationalError(RETRYABLE_SQLITE_ERROR)
    return OperationalError(
        statement="INSERT INTO btc_prices (...) VALUES (?, ?, ?, ?, ?, ?, ?)",
        params=("2026-06-05 06:00:00.121421", 14995000.0, ...),
        orig=orig,
    )
```

`RETRYABLE_SQLITE_ERROR` という定数を本番コードと fixture の両方から参照させ、substring 判定のドリフトを防いでいます。

---

## 6. デプロイ時の落とし穴 — WAL とバックアップ

WAL 化には運用上の注意が 1 つあります。**`app.db-wal` / `app.db-shm` が DB 本体と併存する**ようになるため、

> `cp app.db` だけで手動コピーすると、WAL に溜まった未チェックポイント分が欠落する。

幸い、このシステムのバックアップは `sqlite3.Connection.backup()` API を使っており、WAL でも整合スナップショットを生成できることを確認済み。ドキュメントに「手動コピーは NG、必ずバックアップコマンドを使う」と明記しました。

ロールバックも簡単で、問題が出たら全プロセス停止後に `sqlite3 app.db "PRAGMA journal_mode=delete"` で戻せます。

---

## 7. リリースと反映確認

修正をマージ後、launchd 管理の監視デーモンを再起動しました。

```
$ launchctl kickstart -k "gui/$(id -u)/com.example.monitor"
```

WAL は **遅延接続**のため、再起動直後はまだ `delete` のまま。最初の DB ジョブが接続を開いた時点で初めて WAL に永続切替されます。新コード経由で実セッションを開いて確認:

```
$ python3 -c "import sqlite3; c=sqlite3.connect('app.db'); \
              print(c.execute('PRAGMA journal_mode').fetchone()[0])"
wal                             ← 永続切替を確認
```

`-wal` / `-shm` ファイルは接続中のみ可視で、クローズ時にチェックポイントされて消えるのは WAL の正常動作です。

効果（高負荷スロットでのエラー消失）は数日後に `04:50` / `05:00` JST の監視ログを見れば判定できます。それが確認できたら、4 週間追い続けた慢性パターンの調査チケットをようやくクローズできます。

---

## まとめ

- **症状**: SQLite `unable to open database file` が高負荷ジョブの毎時 0 分／50 分に散発（自己回復するがエラー Issue がノイズ化）
- **真因**: `journal_mode=delete` がトランザクション毎にジャーナルファイルを新規作成 → 並列接続時のファイル作成レース。ディスク逼迫は無関係だった
- **根治**: `journal_mode=WAL`（+ `busy_timeout` / `synchronous=NORMAL`）でジャーナル作成自体を廃止
- **緩和**: `unable to open database file` 限定のコミットリトライ。ただし「INSERT のみ・flush 未実行」に厳格に限定し、データ喪失を絶対に起こさない設計
- **教訓**: 「ディスクは空いている」「ファイルは在る」のに開けないエラーは、**ファイルの存在ではなく作成の競合**を疑う。そして緩和策のリトライは、それ自体がデータ整合性を壊さないようガード条件を詰めることが本体

エラーメッセージの字面（"unable to open") に引きずられず、**いつ・どのジョブで・何と同時に**起きているかという時系列の偏りが、原因特定の最大の手がかりになった一件でした。
