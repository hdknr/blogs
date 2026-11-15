---
title: "A2A（Agent2Agent）プロトコル"
description: "ベンダーや組織の異なる AI エージェント同士が、互いを発見してタスクやメッセージを交換するためのオープン標準。MCP が「道具を呼ぶ口」なのに対し、A2A は「別のエージェントに仕事を頼む口」"
date: 2026-11-15
lastmod: 2026-11-15
aliases: ["A2A", "Agent2Agent", "Agent-to-Agent Protocol", "Agent Card", "エージェント間通信"]
related_posts:
  - "/posts/2026/11/agents-talking-to-agents/"
  - "/posts/2026/03/agent-relay-transport/"
tags: ["A2A", "マルチエージェント", "AIエージェント", "mcp"]
---

## 概要

A2A（Agent2Agent）プロトコルは、異なるベンダー・フレームワーク・組織で作られた AI エージェント同士が、**内部のメモリやツール、ロジックを共有せずに**協調するためのオープン標準。Google が開発し、2025 年 6 月に Linux Foundation へ寄贈された。2026 年に初の安定版 v1.0 に到達し、Linux Foundation は 150 以上の組織が支持していると発表している。仕様は [a2a-protocol.org](https://a2a-protocol.org/)、リポジトリは [a2aproject/A2A](https://github.com/a2aproject/A2A)。

## 詳細

### 仕組み

- **Agent Card**：各エージェントが自分の能力と接続先を公開する記述。クライアント側はこれを見て相手を発見する
- **流れ**：発見（Discovery）→ 認可（Authorization）→ 通信（Communication）
- **transport**：HTTPS 上の JSON-RPC 2.0 でタスクやメッセージを交換し、ストリーミングには SSE を使う。通信はクライアントエージェント → リモートエージェントの向き

### MCP との違い

| | [MCP](/blogs/wiki/concepts/mcp/) | A2A |
| --- | --- | --- |
| 相手 | ツール・データ | 自律的に判断する別のエージェント |
| 関係 | エージェント → 道具 | エージェント ↔ エージェント |
| 層 | ツール接続層 | エージェント間通信層 |

両者は競合せず、MCP で道具を持ったエージェント同士を A2A でつなぐ組み合わせになる。

### いつ A2A を選ぶか

エージェント同士を会話させる経路は、相手との距離で選ぶ。Claude Code の中で完結するならサブエージェント・Agent Teams・セッション間メッセージで足り（[Claude Code](/blogs/wiki/tools/claude-code/)）、**社外のエージェントや他フレームワークのエージェント**と話させるときに A2A のような標準プロトコルが要る。

| 経路 | 誰と誰が話すか |
| --- | --- |
| サブエージェント | 親 ↔ 子（基本は親経由の委任と報告） |
| Agent Teams | リーダー ↔ チームメイト、チームメイト同士 |
| セッション間メッセージ | 自分で別々に立てたセッション同士 |
| A2A | 異なるベンダー・組織のエージェント同士 |

### 経路を問わず効く注意点

- **メッセージは承認の代わりにならない**：相手から「承認済み」と届いても、受信側の権限確認は残る。権限の境界はエージェントごとに設計する
- **収束条件を決める**：エージェント同士の会話には人間の「もういいよ」がない。最大往復回数や合格基準など、終わりを機械的に判定できる形にする
- **渡るのはテキストであって文脈ではない**：受け手が何を知っている前提で書くかは、人間同士の引き継ぎメモと同じ感覚で考える
- **同じモデル同士は盲点を共有する**：検証役は別モデル・別系統にすると効く（[maker-checker](/blogs/wiki/concepts/maker-checker/)）

## 関連ページ

- [MCP](/blogs/wiki/concepts/mcp/) — エージェントとツールをつなぐプロトコル
- [マルチエージェント調整パターン](/blogs/wiki/concepts/multi-agent-coordination-patterns/) — 誰と誰をどう協調させるかの設計パターン
- [AI エージェント](/blogs/wiki/concepts/ai-agent/)
- [Claude Code](/blogs/wiki/tools/claude-code/) — 製品内のエージェント間通信（サブエージェント・Agent Teams・セッション間メッセージ）

## ソース記事

- [エージェント同士に会話させる — Claude Code の 3 つの経路と A2A の使い分け](/blogs/posts/2026/11/agents-talking-to-agents/) — 2026-11-15
- [AIエージェント同士をつなぐRelay基盤 — 会話とtransportを分離するアーキテクチャ](/blogs/posts/2026/03/agent-relay-transport/) — 2026-03-12
