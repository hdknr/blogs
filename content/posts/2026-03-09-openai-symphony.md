---
title: "OpenAI Symphony — AI エージェントを自律的にオーケストレーションするオープンソースフレームワーク"
date: 2026-03-09
lastmod: 2026-03-09
draft: false
source_url: "https://github.com/hdknr/blogs/issues/1#issuecomment-4027391441"
categories: ["AI/LLM"]
tags: ["openai", "agent", "llm", "claude-code"]
---

OpenAI が **Symphony** というオープンソースの自動化基盤をリリースしました。Issue トラッカーから課題を読み取り、課題ごとに隔離ワークスペースを作成し、AI エージェントに実装を走らせるオーケストレーションフレームワークです。

## Symphony とは

Symphony は、AI コーディングエージェントを手動のプロンプト操作から**構造化された自律実行**へと移行させるためのフレームワークです。Elixir / Erlang BEAM ランタイム上に構築されており、長時間実行される独立した「実装ラン（implementation run）」を高い並行性と耐障害性で管理します。

従来の「AI にコードを書かせて PR を出す」という手動プロンプト型のワークフローを、**カンバンボードのタスクカードを移動するだけ**で管理できるようにします。

## 動作の仕組み

Symphony の基本的な流れは以下の通りです:

1. **課題の読み取り** — Issue トラッカー（現在は Linear をサポート）からタスクを継続的に監視
2. **隔離ワークスペースの作成** — 各課題に対して独立したワークスペースを生成
3. **エージェントの実行** — ワークスペース内でコーディングエージェントセッションを実行
4. **成果物の提出** — CI ステータス、PR レビューフィードバック、複雑度分析、操作動画などの「作業証明」を提供
5. **承認とマージ** — タスクが承認されると、エージェントが安全に PR をマージ

## 技術的な特徴

### WORKFLOW.md によるエージェント制御

エージェントのプロンプトやランタイム設定は、リポジトリ内の `WORKFLOW.md` に直接保存されます。これにより、AI の動作指示がコードとしてバージョン管理され、変更対象のブランチと同期されます。

### Elixir / BEAM ランタイムの採用

Elixir と Erlang/BEAM ランタイムを採用することで、以下のメリットがあります:

- **高い並行性** — 複数のエージェントセッションを同時に管理
- **耐障害性** — 個別の実装ランが失敗してもシステム全体に影響しない
- **長時間実行への対応** — エージェントの長時間稼働を安定的にサポート

### Poll-Dispatch-Resolve-Land ワークフロー

Symphony の中核となるワークフローパターンです:

- **Poll** — Issue トラッカーを定期的にポーリング
- **Dispatch** — 新しいタスクを検出してエージェントに割り当て
- **Resolve** — エージェントが実装を完了
- **Land** — 成果物を検証して PR をマージ

## 人の役割の変化

Symphony の導入により、エンジニアの役割は「コードを見張る」から**「仕事を承認・管理する」**側へとシフトします。AI エージェントが実装の実行を担い、人間はレビューと意思決定に集中できるようになります。

## OpenAI (Codex) は必須か？

現時点では**実質的に必須**です。SPEC.md を確認すると:

- コーディングエージェントのデフォルトコマンドは `codex app-server`
- プロトコルは Codex の JSON-RPC ライクな app-server プロトコルに依存
- 内部フィールド名も `codex_app_server_pid`, `codex_totals` など Codex 固有

`codex.command` 設定で実行コマンドを変更することは可能ですが、通信プロトコル（`initialize` → `initialized` → `thread/start` → `turn/start`）に互換性のあるエージェントが必要なため、他の AI エージェントを単純に差し替えることはできません。

## Claude Code で同様のことはできるか

Symphony の核心機能を分解し、Claude Code での代替手段を整理すると以下のようになります:

| Symphony の機能 | Claude Code での代替 |
|---|---|
| Issue トラッカーのポーリング | `gh` CLI + cron / スクリプトで可能 |
| 課題ごとの隔離ワークスペース | `--worktree` オプションで git worktree を自動作成可能 |
| エージェントの自律実行 | `claude -p "プロンプト"` でヘッドレス実行可能 |
| 並行実行・耐障害性 | 複数プロセスを起動すれば可能（BEAM ほど洗練されてはいない） |
| WORKFLOW.md による制御 | `CLAUDE.md` が同等の役割 |

簡易的な Symphony 風ワークフローなら、シェルスクリプトで組めます:

```bash
# GitHub Issue を取得して Claude Code で自律実行する例
gh issue list --state open --label "auto" --json number,title,body |
  jq -c '.[]' |
  while read -r issue; do
    number=$(echo "$issue" | jq -r '.number')
    title=$(echo "$issue" | jq -r '.title')
    body=$(echo "$issue" | jq -r '.body')

    # worktree で隔離実行
    claude -p "Issue #${number}: ${title}\n\n${body}\n\nこの Issue を解決して PR を作成してください" \
      --worktree
  done
```

ただし、Symphony が提供する**リトライ管理、並行数制御、状態遷移の追跡、stall 検出**といったオーケストレーション層は自前で構築する必要があります。本格的にやるなら、Elixir/BEAM のようなスーパバイザ機構を持つ言語か、既存のジョブキュー（Celery, Sidekiq 等）を組み合わせる方が現実的です。

## 利用方法

Symphony は Apache 2.0 ライセンスで公開されています。

- **リポジトリ**: [openai/symphony](https://github.com/openai/symphony)
- **仕様書**: [SPEC.md](https://github.com/openai/symphony/blob/main/SPEC.md)

煩雑な実験サイクルや実装タスクをシステム化したいチームにとって、研究開発の効率を見直す良いきっかけになりそうです。Symphony の設計思想自体は特定のツールに依存しない普遍的なものなので、Claude Code や他のエージェントでも同様のアーキテクチャを参考にできます。
