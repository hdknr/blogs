---
title: "claude -p によるヘッドレス実行"
description: "Claude Code の非対話モード claude -p を、構造化出力を返す関数としてスクリプトやジョブから呼ぶための手順と注意点。--bare による入力トークン削減、Celery からの呼び出し"
date: 2026-10-30
lastmod: 2026-10-30
aliases: ["claude -p", "headless", "ヘッドレスモード", "--bare", "--json-schema", "apiKeyHelper"]
related_posts:
  - "/posts/2026/10/claude-p-input-tokens-bare/"
  - "/posts/2026/10/celery-claude-recursive-orchestration/"
tags: ["claude-code", "claude -p", "トークン最適化", "prompt-caching", "celery"]
---

## 概要

`claude -p` は Claude Code の非対話（ヘッドレス）モードで、`--output-format json` と `--json-schema` を組み合わせると「スキーマどおりの JSON を返す 1 回の関数呼び出し」として使える。ただし中身は Claude Code そのものなので、プロンプトを短くしても既定では Claude Code のシステムプロンプトや設定由来の情報が毎回送られる。小さな判断を大量に呼ぶ自動化では、この **固定分** を `--bare` で削り、キャッシュに乗せる設計が要る。

## 詳細

### 構造化出力を返す関数として使う

| オプション | 役割 |
|---|---|
| `--output-format json` | 結果を 1 つの JSON で返す（`session_id`・`total_cost_usd`・`usage` を含む） |
| `--json-schema '<schema>'` | 出力を JSON Schema で検証。検証済みの値は `structured_output` に入る |
| `--tools ""` | 組み込みツールをすべて無効化（判断だけさせる） |
| `--max-budget-usd` | 1 回の費用上限（推定値で判定するので僅かに超えうる） |
| `--no-session-persistence` | セッションをディスクに保存しない |

- 構造化出力が得られずに終わると `structured_output` が欠ける。**欠けたら失敗として扱いリトライ**する
- `--json-schema` 付きの呼び出しは 2 ターンかかった例があり、`--max-turns 1` に絞ると返せない可能性がある

### 入力トークンの実測（固定分）

数百トークンの計画プロンプトを Sonnet で呼んだときの入力（`cache_creation_input_tokens` + `cache_read_input_tokens`）:

| 呼び出し方 | 入力トークン |
|---|---|
| 既定（リポジトリ内） | 約 13,400 |
| 既定（空のディレクトリ） | 約 8,600 |
| `--system-prompt` で差し替え | 約 14,400（減らない） |
| `--setting-sources ""` | 約 6,500 |
| 上記＋`--strict-mcp-config`＋`--system-prompt` | 約 4,100 |
| `--bare` | 約 700 |

読み取れること:

- 自分のプロンプトより固定分のほうがはるかに大きい
- **実行ディレクトリ**（CLAUDE.md の有無）で約 4,900 トークン変わる。作業ディレクトリも設計の一部
- システムプロンプトの差し替えだけでは効かず、効くのは設定ファイルの読み込み停止、最も効くのは hooks・プラグイン・MCP・CLAUDE.md の自動読み込みをまとめて省く `--bare`
- プロンプトキャッシュも大きい。既定の 2 回目は推定約 0.055 → 0.003 ドル。固定部分を毎回同じに保つ

数値は環境依存なので、`jq '.usage.cache_creation_input_tokens + .usage.cache_read_input_tokens' out.json` で自分の環境を測ってから決める。

### `--bare` の認証と課金

- 認証は `ANTHROPIC_API_KEY` か `--settings` で渡す `apiKeyHelper` のみ。サブスクリプションの OAuth は使われず、**Claude Console の組織の API 利用として課金**される（Team / Max の月次 API クレジットを充てられる）
- 環境変数だけでは「Not logged in」になった例があり、キーを標準出力に返すスクリプトを `apiKeyHelper` に指定すると動いた
- キーのファイルは権限 600、本番ではシークレットマネージャーや Workload Identity Federation を検討する

### 使い分け

- リポジトリを読ませながら考える判断 → 既定の `claude -p`（ツール有効でさらに固定分が増える）
- プロンプトに含めた情報だけで決まる判断（計画・分類） → `claude -p --bare` か Messages API の直接呼び出し

### Celery から計画役として呼ぶ

[Celery](/blogs/wiki/tools/celery/) のタスクから `claude -p --tools "" --json-schema ...` を呼び、**LLM には次の子タスクを JSON で提案させるだけ**にする構成。許可リスト・重複・分岐数の検査と投入はコード、並列実行と待ち合わせは Celery の `chord`、再帰もコールバックで起こす。歯止めとして深さ・`root_id` ごとの呼び出し回数（Redis の `INCR`）・1 回の費用上限・リトライ上限を重ねる。子タスクの結果は `<task-results>` で囲んでデータとして渡すが、最終防御は許可リスト検査の側に置く。

計画役は入力・出力・失敗（`ValueError` / `SubprocessError`）の約束さえ守れば Codex CLI（`codex exec --output-schema --sandbox read-only`）などに差し替えられる。費用上限オプションがない計画役では、呼び出し回数の上限がほぼ唯一の費用の歯止めになる。設計の背景は [オーケストレーター／コーダー分業と承認ゲート](/blogs/wiki/concepts/orchestrator-coder-split/) を参照。

## 関連ページ

- [Claude Code](/blogs/wiki/tools/claude-code/)
- [Celery](/blogs/wiki/tools/celery/) — `claude -p` を呼ぶタスクキュー
- [オーケストレーター／コーダー分業と承認ゲート](/blogs/wiki/concepts/orchestrator-coder-split/) — LLM は提案、コードが検査して投入
- [Claude Code Remote Control](/blogs/wiki/guides/claude-code-remote-control/) — 対話セッションを外から操作する別ルート
- [AI エージェント時代のシークレット管理](/blogs/wiki/guides/ai-agent-secret-management/) — API キーの置き場所

## ソース記事

- [claude -p の入力トークンを実測 — Claude Code の既定 1 万前後を --bare で約 700 に減らす](/blogs/posts/2026/10/claude-p-input-tokens-bare/) — 2026-10-30
- [Celery と claude -p で組む再帰的なエージェントオーケストレーション](/blogs/posts/2026/10/celery-claude-recursive-orchestration/) — 2026-10-30
