---
title: "マルチエージェント調整パターン"
description: "複数 AI エージェントを協調させる5つの設計パターン。Anthropic が体系化した Generator-Verifier・Orchestrator-Subagent・Agent Teams・Message Bus・Shared State"
date: 2026-04-11
lastmod: 2026-04-11
aliases: ["マルチエージェントパターン", "multi-agent-coordination"]
related_posts:
  - "/posts/2026/04/anthropic-multi-agent-coordination-patterns/"
  - "/posts/2026/04/claude-managed-agents-architecture/"
  - "/posts/2026/04/claude-managed-agents/"
tags: ["マルチエージェント", "AIアーキテクチャ", "設計パターン", "Anthropic", "エージェント"]
---

## 概要

Anthropic が 2026年4月に公開した、複数 AI エージェントを協調させるための5つの設計パターン。「まず Orchestrator-Subagent から始め、観察した制約に応じて発展させる」という設計哲学が基本。

## 5 つのパターン

### 1. Generator-Verifier（生成・検証）

一方のエージェントが出力を生成し、もう一方が明示的な基準で検証。不合格なら生成エージェントにフィードバックが戻り、合格か最大反復回数に達するまでループ。

- **向いているケース**: コード生成＋テスト実行など、品質基準が明確なタスク
- **注意点**: 検証基準の設計が甘いと「品質管理の幻想」になる

### 2. Orchestrator-Subagent（オーケストレーター・サブエージェント）

リーダーエージェントが計画を立て、専門化されたサブエージェントにタスクを委任。Anthropic 推奨の**デフォルト出発点**。

- **向いているケース**: セキュリティ・テストカバレッジ・スタイルを分担するコードレビュー等
- **注意点**: サブエージェント間の依存が高いと情報ボトルネックになる

### 3. Agent Teams（エージェントチーム）

コーディネーターが**永続的な**ワーカーエージェントを生成。ワーカーはアサインをまたいで生存し、ドメイン知識を蓄積する点が Orchestrator-Subagent との違い。

- **向いているケース**: 大規模コードベースの長期・並列マイグレーション
- **注意点**: タスク間の独立性が必要。完了検知が難しい

### 4. Message Bus（メッセージバス）

エージェントが共有ルーター経由でパブリッシュ・サブスクライブ。実行順序があらかじめ決まらないイベント駆動型。

- **向いているケース**: セキュリティアラートが動的に多段階調査をトリガーするようなパイプライン
- **注意点**: イベント連鎖のトレーサビリティが低下しやすい

### 5. Shared State（共有ステート）

中央コーディネーターなしに、エージェントが永続ストレージを直接読み書き。他エージェントの発見をリアルタイムに参照できる。

- **向いているケース**: 一方の調査が即座に他方の探索方向に影響する協調リサーチ
- **注意点**: 収束条件が必須。なければ際限なくトークンを消費する

## 選択の目安

| パターン | 向いているケース |
|---|---|
| Orchestrator-Subagent | 多くのユースケースの出発点 |
| Generator-Verifier | 品質基準が明確で反復検証が必要 |
| Agent Teams | 並列・長期・ドメイン蓄積が必要 |
| Message Bus | イベント駆動で動的にワークフローが変化 |
| Shared State | エージェント間でリアルタイムに知識を共有したい |

実際のプロダクションでは複数パターンを組み合わせることも多い。

## 関連ページ

- [Claude Managed Agents](/blogs/wiki/tools/claude-managed-agents/)
- [エージェントメモリのロックイン](/blogs/wiki/concepts/agent-memory-lock-in/)
- [ハーネスエンジニアリング](/blogs/wiki/concepts/harness-engineering/)

## ソース記事

- [Anthropic が解説するマルチエージェント調整パターン 5 選](/blogs/posts/2026/04/anthropic-multi-agent-coordination-patterns/) — 2026-04-11
- [Claude Managed Agents のアーキテクチャ: Brain / Session / Hands の分離設計](/blogs/posts/2026/04/claude-managed-agents-architecture/) — 2026-04-10
