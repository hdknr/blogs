---
title: "Celery"
description: "分散タスクキュー。非同期処理と定期タスク実行を実現し、claude -p を計画役にした再帰的なエージェントオーケストレーションの基盤にもなる"
date: 2026-04-06
lastmod: 2026-10-30
aliases: ["celery"]
related_posts:
  - "/posts/2026/03/claude-code-celery-orchestration/"
  - "/posts/2026/10/celery-claude-recursive-orchestration/"
tags: ["python", "django", "タスクキュー", "redis"]
---

## 概要

Redis や RabbitMQ をブローカーに、非同期タスク実行・定期タスク（beat）を実現。ECS Fargate 上では worker/beat を独立タスクとして実行。ログは CloudWatch Logs に出力。

## 詳細

### AI エージェントのオーケストレーション基盤として使う

Celery のタスクから Claude Code の非対話モード `claude -p` を呼び、**LLM は次の子タスクを JSON で提案するだけ、検査と投入はコードが行う**構成が組める。Anthropic のクラウドで動く Routines（scheduled tasks）と比べ、リトライ・冪等性・タイムアウト・上限をすべて自分のコードで握れ、間隔や回数の制約もない。

| 判断 | 担当 |
|---|---|
| 目的に対して次に何をすべきか | LLM（`claude -p --json-schema --tools ""`） |
| 実行してよいか（許可リスト・上限・重複） | Celery にも LLM にも依存しない検査関数 |
| 子タスクの並列実行・待ち合わせ・リトライ | Celery |
| いつ止めるか（深さ・回数・完了） | コード |

ポイント:

- **`chord(header)(callback)`** で子タスクを並列実行し、全部終わったら結果リストを持って計画タスクに戻る。再帰は LLM ではなくコードが起こす。`chord` は result backend が必須（RPC backend 非対応）
- header の子タスクが 1 つでも失敗するとコールバックは実行されず `ChordError` になる。子タスク側で例外を結果として返すなど方針を決める
- 歯止め: 深さ上限、1 回の分岐数上限、最初のタスク ID（`root_id`）ごとの呼び出し回数を Redis `INCR` で数える上限、タスク名＋引数のハッシュを Redis 集合に入れる重複排除、`max_retries`
- 計画ログを Redis に残し、毎回同じになる計画は固定の `chain` / `chord` に置き換えて段階的に決定論的な処理へ寄せる
- 定期実行は Celery Beat から最初のタスクを投げる。**Beat は 1 プロセスだけ**動かす（複数だとタスクが重複する）
- macOS の既定プール（prefork）では worker がタスク受信直後に `ValueError: not enough values to unpack` で失敗した例があり、手元では `--pool=threads` で動かす

`claude -p` 側のオプションや固定トークンの削り方は [claude -p によるヘッドレス実行](/blogs/wiki/guides/claude-p-headless/) にまとめた。

## 関連ページ

- [Redis](/blogs/wiki/tools/redis/) — Celery のブローカー/バックエンド
- [claude -p によるヘッドレス実行](/blogs/wiki/guides/claude-p-headless/) — 計画役として呼ぶ `claude -p` の使い方
- [オーケストレーター／コーダー分業と承認ゲート](/blogs/wiki/concepts/orchestrator-coder-split/) — LLM は提案、コードが検査する設計
- [マルチエージェント調整パターン](/blogs/wiki/concepts/multi-agent-coordination-patterns/)

## ソース記事

- [Claude Code + Celery: LLMが決定論的処理を動的に委譲するオーケストレーション](/blogs/posts/2026/03/claude-code-celery-orchestration/) — 2026-03-30
- [Celery と claude -p で組む再帰的なエージェントオーケストレーション](/blogs/posts/2026/10/celery-claude-recursive-orchestration/) — 2026-10-30
