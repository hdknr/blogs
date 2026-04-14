---
title: "Claude Managed Agents"
description: "Anthropic が提供する本番運用可能なマネージド AI エージェント基盤。Brain / Session / Hands の3層分離アーキテクチャで構成される"
date: 2026-04-14
lastmod: 2026-04-14
aliases: ["CMA", "Managed Agents"]
related_posts:
  - "/posts/2026/04/claude-managed-agents/"
  - "/posts/2026/04/claude-managed-agents-architecture/"
  - "/posts/2026/04/anthropic-vs-openai-harness-strategy/"
  - "/posts/2026/04/agent-harness-memory-lock-in/"
tags: ["claude", "anthropic", "agent", "mcp", "architecture"]
---

## 概要

2026年4月8日に Anthropic がパブリックベータ公開した、AI エージェントの構築・デプロイ・運用に必要なインフラを一括提供する API スイート。開発者はモデル、システムプロンプト、ツール、MCP サーバーを定義するだけで、本番レベルのエージェントを稼働させられる。

## 主な機能

| 機能 | 説明 |
|------|------|
| セキュアなサンドボックス | エージェントの実行環境を安全に分離 |
| 長時間実行セッション | 数時間にわたるタスクも途中状態を維持 |
| 永続的な状態管理 | コンテキストウィンドウ外にセッションログを保持 |
| マルチエージェント連携 | 複数エージェントのフリート管理 |
| MCP 統合 | HubSpot などの外部サービスと即座に連携可能 |

料金は API 従量課金に加えてセッション時間あたり $0.08。

## アーキテクチャ：Brain / Session / Hands

Claude Managed Agents は OS の抽象化パターンにならい、3つのコンポーネントを分離したメタハーネス設計を採用している。

### Brain（ステートレスなハーネス + Claude）

- Agent Harness と Claude（LLM 推論）で構成
- ステートレスなため、クラッシュしても `wake(sessionId)` で復旧可能
- プロンプトキャッシュ、コンパクション、コンテキストエンジニアリングを担当
- TTFT（最初のトークンまでの時間）を p50 で約60%、p95 で90%以上改善

### Session（永続コンテキスト）

- コンテキストウィンドウの外に存在する append-only のイベントログ
- `getEvents()` インターフェースでイベントストリームの任意スライスを取得可能
- 長時間タスクでもコンテキストを回復可能な形で保存

### Hands（使い捨て可能なサンドボックス + ツール）

- Brain から `execute(name, input) → string` で呼び出される統一インターフェース
- コンテナが落ちても Brain やセッションに波及しない障害分離
- 認証情報はサンドボックス内から到達不可能（プロンプトインジェクション対策）

## API の基本フロー

```text
POST /v1/agents        # Agent 定義
POST /v1/environments  # コンテナテンプレート
POST /v1/sessions      # セッション開始
POST /v1/sessions/{id}/events  # イベント送信
GET  /v1/sessions/{id}/stream  # SSE でレスポンス受信
```

ベータヘッダー `managed-agents-2026-04-01` が必要。

## ベンダーロックインの課題

LangChain 創設者 Harrison Chase が指摘する通り、Claude Managed Agents ではメモリ（長期セッション状態）が Anthropic のクラウドに保存され、外部から直接アクセスできない。これはハーネスとメモリのロックイン問題の一例とされる。開発者は移植性を意識した設計が求められる。

## 関連ページ

- [ハーネスエンジニアリング](/blogs/wiki/concepts/harness-engineering/) — エージェント品質保証の設計パターン
- [AI エージェント](/blogs/wiki/concepts/ai-agent/) — エージェント基盤の概念
- [MCP](/blogs/wiki/concepts/mcp/) — エージェントと外部ツールの接続プロトコル
- [OpenClaw](/blogs/wiki/tools/openclaw/) — ローカル自律型エージェントとの対比

## ソース記事

- [Claude Managed Agents: パブリックベータ公開](/blogs/posts/2026/04/claude-managed-agents/) — 2026-04-10
- [Claude Managed Agents のアーキテクチャ](/blogs/posts/2026/04/claude-managed-agents-architecture/) — 2026-04-10
- [Anthropic vs OpenAI：Harness 戦略の比較](/blogs/posts/2026/04/anthropic-vs-openai-harness-strategy/) — 2026-04-13
- [エージェントハーネスとメモリのロックイン問題](/blogs/posts/2026/04/agent-harness-memory-lock-in/) — 2026-04-12
