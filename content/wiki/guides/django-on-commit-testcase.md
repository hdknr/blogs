---
title: "Django の transaction.on_commit と TestCase の相性"
description: "Django の TestCase(ロールバック方式)では transaction.on_commit が発火しない。正しい本番修正が離れた結合テストを赤にする事例と、captureOnCommitCallbacks による解決を解説する"
date: 2026-07-15
lastmod: 2026-07-15
aliases: ["on_commit", "captureOnCommitCallbacks", "TestCase on_commit", "TransactionTestCase"]
related_posts:
  - "/posts/2026/07/django-on-commit-testcase/"
tags: ["django", "python", "celery", "テスト", "on_commit"]
---

## 概要

Django の `TestCase` はテスト全体を1つのトランザクションで包み最後に ROLLBACK するため、**`transaction.on_commit` のコールバックが発火しない**。この性質を知らないと、「本番として100%正しい修正」が、変更箇所と無関係な場所の結合テストを後から静かに赤にする事故が起きる。直し方は簡単だが、難しいのは気づくこと。

## 詳細

### ベースクラスによる違い

| ベースクラス | 仕組み | `on_commit` |
|---|---|---|
| `TransactionTestCase` | 各テストで実際に BEGIN/COMMIT しテーブルを truncate | **発火する** |
| `TestCase` | テスト全体を1トランザクションで包み最後に ROLLBACK | **発火しない**（commit が来ない） |

Celery eager モード（`CELERY_TASK_ALWAYS_EAGER=True`）でも、`on_commit` に載った関数は commit 時にしか呼ばれないため `TestCase` では実行されない。

### 起きた事故（要約）

「Celery タスクが DB コミット前に `.delay()` されて未コミット行を掴めずサイレント失敗する」という実バグを、`transaction.on_commit` 経由の enqueue に直した。本番として正しく、新挙動のユニットテストも足されていた。

```python
# 変更前
if exec_async:
    importfile_load_excel.delay(instance.id)
# 変更後（本番として正しい）
if exec_async:
    transaction.on_commit(lambda: importfile_load_excel.delay(importfile_id))
```

ところが該当の結合テストは高速化のため `TestCase` ベースへ移行済みで、移行時点では `.delay()` が eager で同期実行されるため `on_commit` 非依存だった。修正が `.delay()` を `on_commit` の中へ移した瞬間、この前提が後から崩れ、取込タスクが走らず反映 API が 400 を返して落ちた（`TransactionTestCase` ベースの同種テストは無事＝根本原因の裏付け）。

ローカルでは緑だったのは、**手元の checkout が原因コミットより古かった**だけ。環境依存の false-fail ではない。

### 直し方

本番修正は正しいので触らず、**テスト側**で非同期取込を起こす API 呼び出しを `on_commit` 発火コンテキストで囲む。

```python
with self.captureOnCommitCallbacks(execute=True):
    response = client.post(".../import/create/", req, format="json")
self.assertResponse(response, 201, "作成")
```

同期取込（`exec_async=False`）では登録される `on_commit` コールバックが無いので `with` は実質 no-op。sync/async 両対応の共通ヘルパにそのまま入れられる。

### 再発防止（3点）

1. **`on_commit` を足すときは「それを踏むテストの実行モデル」まで見る** — 経路を grep し、`TestCase` ベースは `captureOnCommitCallbacks` で囲むか `TransactionTestCase` へ戻す
2. **高速化のための `TestCase` 移行は「今 on_commit 非依存」を保証するだけ** — 非同期ディスパッチを必ず伴う結合テストは最初から `TransactionTestCase` に置くか、REST テスト基盤側で既定的に `captureOnCommitCallbacks` に通す薄いヘルパを用意する
3. **横断層（`files/` 等）を触る PR はマージ後に日次監査を手動トリガ** — 安全網は機能したが1日遅れた

> 「テストが緑」は「コードが正しい」ではなく「**テストが実際にその経路を実行した上で緑**」でなければ意味がない。

## 関連ページ

- [AI エージェントにリファクタさせる時の完了の定義](/blogs/wiki/concepts/ai-refactor-completion-boundary/) — この事故をプロンプト設計の視点で一般化
- [自動テスト修正パイプライン](/blogs/wiki/guides/auto-test-fix-pipeline/) — 横断スイープと監査の手順化
- [Brownfield リファクタリング](/blogs/wiki/concepts/brownfield-refactoring/) — signals など暗黙の副作用を凍結してから触る

## ソース記事

- [Django の transaction.on_commit と TestCase の相性](/blogs/posts/2026/07/django-on-commit-testcase/) — 2026-07-08
