---
title: "Django の transaction.on_commit と TestCase の相性 — 正しい本番修正が「昨日まで緑だったテスト」を赤にした話"
date: 2026-07-08
lastmod: 2026-07-08
slug: "django-on-commit-testcase"
draft: false
description: "Django の TestCase（ロールバック方式）では transaction.on_commit が発火しない。正しい本番修正が結合テストを離れた場所で壊した事例と、captureOnCommitCallbacks による解決を解説する。"
categories: ["Web開発"]
tags: ["django", "python", "celery", "テスト", "on_commit"]
---

## TL;DR

- ある日、日次テスト監査が非同期取込テスト（`test_booktempfile.py` / `test_ordertempfile.py`）を失敗として起票しはじめた。
- 直接の引き金は、**まったく正しい本番バグ修正**だった。「Celery タスクが DB コミット前に `.delay()` されて未コミット行を掴めない」という実バグを、`transaction.on_commit` 経由の enqueue に直して解消したもの。
- ところが該当テストは高速化のため `TransactionTestCase` から `TestCase` ベースへ移行済みで、**`TestCase` では `on_commit` コールバックが発火しない**。その結果、create 時の取込タスクが実行されず、「取込が完了していない」状態で反映 API が 400 になって落ちた。
- 修正はテスト側。非同期取込を起こす API 呼び出しを `self.captureOnCommitCallbacks(execute=True)` で囲むだけ。
- **本質的な教訓**: 「本番コードに `on_commit` を足す」変更は、`TestCase` ベースのテストが踏んでいる限り**変更箇所では何も壊れず、離れた場所で後から静かに壊れる**。共有ディスパッチ層を触るときは、それを踏むテストの実行モデル（commit するか否か）まで含めて確認する。

---

## 何が起きたか

ある業務システム（EPM サーバー）には「Excel を取込 → 一時テーブルへ → 本番反映」という取込フローがあり、`exec_async=True` で非同期実行できる。これを検証する結合テストが仕訳取込（books）と受注取込（sales）にある。

これらは**2 日前まで監査で緑**だったのに、昨日の監査から次のように落ちはじめた。

```
# 受注取込: test_exec_async
PATCH /api/rest/files/importfile/1/exec/ -> 400
{'status': ['取込が完了したファイルのデータのみ反映が可能']}

# 仕訳取込: test_load_async / test_load_receipt_mssql_async
AssertionError: {True} != set(valid_set)   # 取込結果が空 / 全て invalid
```

ローカルで単独実行しても、ファイル全体で実行しても**緑**。「環境依存の false-fail か？」と一瞬疑うが、それは誤り。**手元の checkout が原因コミットより古かっただけ**だった（つまりローカルには原因となる修正がまだ反映されていなかった）。

## なぜ起きたか（根本原因）

犯人は、AI によるコード監査が見つけた実バグの修正 PR だった。監査が検出した実バグのうちの 1 件を直したもので、内容はこうだ。

> `tasks/tasks.py`: `exec_async=True` 取込が atomic な `save()` 内から **commit 前に `.delay()`** していたため、タスクが未コミット行を取得できず `None` でサイレント失敗（signal 規約違反）。`.delay()` のみ `transaction.on_commit` に載せる。

差分はこれだけ：

```python
# 変更前（files/tasks/tasks.py の importfile_load 受信）
if exec_async:
    importfile_load_excel.delay(instance.id)

# 変更後
if exec_async:
    transaction.on_commit(lambda: importfile_load_excel.delay(importfile_id))
```

これは本番として **100% 正しい**。トランザクションがコミットされる前にワーカーがタスクを拾うと、ワーカー側の別コネクションからは行がまだ見えず、タスクが空振りする典型的な競合だ。`on_commit` に載せるのが定石である。

問題は**テストの実行モデル**にある。

| ベースクラス | 仕組み | `on_commit` |
|---|---|---|
| `TransactionTestCase` | 各テストで実際に BEGIN/COMMIT し、テーブルを truncate | **発火する** |
| `TestCase` | テスト全体を 1 つのトランザクションで包み、最後に ROLLBACK | **発火しない**（commit が来ない） |

該当ファイルは、テスト高速化施策で `TestCase` ベースの高速クラス（ここでは `RestFastTestCase` と呼ぶ）へ移行済みだった。移行の契約は明快で、コード内にもこう書いてある。

> **使用条件**: `transaction.on_commit()` に依存しないテストのみ。… 依存するテストは `TransactionTestCase` ベースのままにするか、対象処理を `self.captureOnCommitCallbacks(execute=True)` で囲む必要がある。

移行した当時、この取込テストは**確かに `on_commit` 非依存だった**。`.delay()` は Celery eager モード（`CELERY_TASK_ALWAYS_EAGER=True`）で**その場で同期実行**されるので、`TestCase` でも問題なく動いていた。

修正 PR が `.delay()` を `on_commit` の中へ移した瞬間、この前提が**後から崩れた**。因果を追うとこうなる。

1. eager モードでも、`on_commit` に載った関数は commit 時にしか呼ばれない。
2. `TestCase` は commit しないので、その関数は永遠に呼ばれない。
3. create 時の取込タスクが走らない。
4. 「取込未完了」の状態で反映 API が 400 を返す。仕訳取込側は取込結果が空になって valid 判定が落ちる。

### なぜ仕入取込の同種テストは無事だったのか

同じ非同期取込テストが仕入取込（purchases）にもある（`test_load_purchase_async`）。だがこれは `TransactionTestCase` ベースのクラスに置かれていて、**`on_commit` が自然に発火する**。だから修正 PR の影響を受けず、監査も拾わなかった。

この非対称性こそが「なぜ 2 ファイルだけ落ちたのか」の答えであり、根本原因が **`TestCase` × `on_commit`** であることの決定的な裏付けになっている。

## どう直したか

本番修正は正しいので触らない。**テスト側**で、非同期取込を起こす API 呼び出しを `on_commit` 発火コンテキストで囲む。

```python
# exec_async=True の取込は load タスクが transaction.on_commit 経由の
# enqueue になった。TestCase ベースは commit しないため
# captureOnCommitCallbacks で on_commit を発火させる（同期取込では no-op）。
with self.captureOnCommitCallbacks(execute=True):
    response = client.post(".../import/create/", req, format="json")
self.assertResponse(response, 201, "作成")
```

同期取込（`exec_async=False`）のときは登録される `on_commit` コールバックが無いので、この `with` は実質 no-op。sync/async 両対応の共通ヘルパにそのまま入れられる。

## 本来どうすべきだったか（再発防止）

これは「誰かがミスした」話ではない。**正しい修正が、離れた場所の暗黙の前提を壊した**という、分散した知識のほころびの話だ。防ぐ観点は 3 つ。

### 1. `on_commit` を足すときは「それを踏むテストの実行モデル」まで見る

`transaction.on_commit` の追加は、**変更した関数のユニットテストでは決して失敗しない**。今回の修正 PR も新挙動のユニットテスト（`.delay()` をモックして「commit 前は呼ばれない／commit 後に呼ばれる」を検証）はきちんと足していた。だが、create → load → exec を通しで叩く**既存の結合テスト**が `TestCase` 上にあることまでは視界に入っていなかった。

チェックリスト化するなら：

> **本番コードに `transaction.on_commit` を新規追加したら、その経路を叩くテストを grep し、`TestCase` ベースのものは `captureOnCommitCallbacks` で囲むか `TransactionTestCase` へ戻す。**

### 2. 高速化のための `TestCase` 移行は「今 on_commit 非依存」を保証するだけで、「将来も」は保証しない

`TestCase` ベースへの移行は、移行時点のスナップショットに対して安全なだけだ。`on_commit` 依存は**後から本番側の変更で注入されうる**。この脆さを踏まえると、選択肢は次のようになる。

- 取込のような「非同期ディスパッチを必ず伴うフロー」の結合テストは、最初から `TransactionTestCase` に置く（仕入取込が結果的に正解だった）。
- あるいは REST テスト基盤側で、エンドポイント呼び出しを既定で `captureOnCommitCallbacks` に通す薄いヘルパを用意し、「明示的に囲まないと on_commit が死ぬ」という落とし穴自体を減らす。

### 3. 横断層（`files/` 等）を触る PR は、マージ後に日次監査を手動トリガする

安全網（日次テスト監査）は機能した —— ただし**1 日遅れて**。今回の修正 PR は `files/` という全取込フロー共通の層を変更しており、影響はアプリ横断だった。運用ルールには既に「大規模・アプリ横断変更のマージ後は日次テスト監査を手動トリガ」とある。`files/` の signal / dispatch 変更はまさにその対象で、PR 時点で回していれば当日中に検知できた。

---

## まとめ

- `TestCase`（ロールバック方式）では `transaction.on_commit` が**発火しない**。eager Celery でも `on_commit` に載れば同じ。
- だから「`.delay()` を `on_commit` に移す」という**正しい本番修正**が、`TestCase` 上の結合テストを**変更箇所と無関係な場所で**壊すことがある。
- 直し方は簡単（`captureOnCommitCallbacks` で囲む）。難しいのは**気づくこと**。
- 気づくための仕組み: ① `on_commit` 追加時に経路テストの実行モデルを確認、② 非同期フローの結合テストは `TransactionTestCase` を既定に、③ 横断層 PR はマージ後に監査を手動トリガ。

> 「テストが緑」は「コードが正しい」ではなく「**テストが実際にその経路を実行した上で緑**」でなければ意味がない。`on_commit` はその “実行したつもり” が最も起きやすい場所のひとつだ。
