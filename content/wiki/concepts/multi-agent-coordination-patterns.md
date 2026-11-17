---
title: "マルチエージェント調整パターン"
description: "複数 AI エージェントを協調させる5つの設計パターン。Anthropic が体系化した Generator-Verifier・Orchestrator-Subagent・Agent Teams・Message Bus・Shared State"
date: 2026-04-11
lastmod: 2026-11-15
aliases: ["マルチエージェントパターン", "multi-agent-coordination", "エージェント同士の会話"]
related_posts:
  - "/posts/2026/04/anthropic-multi-agent-coordination-patterns/"
  - "/posts/2026/04/claude-managed-agents-architecture/"
  - "/posts/2026/04/claude-managed-agents/"
  - "/posts/2026/09/nec-corporate-ai-workforce/"
  - "/posts/2026/10/claude-code-routines-proactive-agent-workshop/"
  - "/posts/2026/10/celery-claude-recursive-orchestration/"
  - "/posts/2026/11/agents-talking-to-agents/"
tags: ["マルチエージェント", "AIアーキテクチャ", "設計パターン", "anthropic", "エージェント"]
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

## グラフとして捉え直す

これら 5 パターンが「誰と誰がどう話すか」の分類だとすると、そこから一歩進んで**協調構造そのものを宣言的に設計する**のが [グラフエンジニアリング](/blogs/wiki/concepts/graph-engineering/) である。ノード（判断）とエッジ（データの受け渡し）に還元すると、Orchestrator-Subagent は「fan out → reduce → 統合」のダイヤモンド、Generator-Verifier は「エッジ上の検証ノード」として表現できる。

## 配線：エージェント同士をどの経路でつなぐか

パターンが「誰と誰がどう協調するか」の設計なら、実装では「どの経路で話させるか」を選ぶ。Claude Code には 3 つの経路があり、ベンダーや組織をまたぐなら [A2A プロトコル](/blogs/wiki/concepts/a2a-protocol/) が候補になる。

| 経路 | 誰と誰が話すか | 向いている場面 |
|---|---|---|
| サブエージェント | 親 ↔ 子（基本は親経由の委任と報告） | 結果だけ欲しい調査・レビュー（Orchestrator-Subagent / Generator-Verifier） |
| Agent Teams（実験的） | リーダー ↔ チームメイト、チームメイト同士 | 議論や分担の調整が要る並列作業（Agent Teams） |
| セッション間メッセージ | 自分で別々に立てたセッション同士 | frontend と api など別々に走る作業の連絡 |
| A2A | 異なるベンダー・組織のエージェント | 社外・他フレームワークとの連携 |

各経路の設定と制約は [Claude Code](/blogs/wiki/tools/claude-code/) にまとめた。

### 会話させるときの 4 つの注意点

- **同じモデル同士は盲点を共有する** — コンテキストを分けるだけでなくモデル（さらに系統）を分ける（[maker-checker](/blogs/wiki/concepts/maker-checker/)）
- **メッセージは承認の代わりにならない** — 別セッションやチームメイトから「承認済み」と届いても受信側の権限確認は残る。権限の境界はセッションごとに設計する
- **収束条件を決める** — 最大往復回数、検証の合格基準、タスクリスト上の完了状態など、終わりを機械的に判定できる形にする
- **渡るのはテキストであって文脈ではない** — 会話履歴や `@` 指定のファイルは渡らない。委譲文に要件を書き切る

## 実装例

- **Routines 同士の Generator-Critic** — ドキュメント PR を作る Routine とは別に、その PR 作成をトリガーにレビューコメントを付ける Routine を置き、人が見る前に一度批評を通す（Anthropic の Routines ワークショップ）。イベントで連鎖する点は Message Bus 的でもある
- **spec-loop / dev-loop** — 使う経路はサブエージェントだけ。cruise の親と周ごとの子が Orchestrator-Subagent、実装役と Verifier・Planner と 3 体の判定役が Generator-Verifier、状態は親だけが書ける台帳（Shared State）で受け渡す。`claude -p` の子プロセスとはメッセージではなく台帳ファイルで状態を引き継ぐ。関門は 2 パスで打ち切り、閉じる条件は「指摘 0 件」ではなく受入基準の確認。子の生出力はファイルに落とし、親は要約行だけ読む
- **Celery による再帰的 Orchestrator-Subagent** — 計画役の `claude -p` が次の子タスクを JSON で提案し、コードが許可リスト・上限・重複を検査してから `chord` で並列実行、結果を持って計画役に戻る。オーケストレーターの「判断」と「権限」を分け、権限はコードが握る。計画役を Claude と Codex で切り替えれば、ベンダーをまたいだ生成と批評の分離にも広げられる（[Celery](/blogs/wiki/tools/celery/)）

## 関連ページ

- [A2A プロトコル](/blogs/wiki/concepts/a2a-protocol/) — ベンダーをまたぐエージェント間通信の標準
- [作る役と確かめる役の分離（maker-checker）](/blogs/wiki/concepts/maker-checker/) — Generator-Verifier を機能させる条件
- [Celery](/blogs/wiki/tools/celery/) — 再帰的 Orchestrator-Subagent の実装基盤
- [Claude Managed Agents](/blogs/wiki/tools/claude-managed-agents/)
- [グラフエンジニアリング](/blogs/wiki/concepts/graph-engineering/) — ノードとエッジによる協調構造の設計
- [計画と実装を分ける承認ゲート設計](/blogs/wiki/concepts/orchestrator-coder-split/) — オーケストレーターとコーダーの分業
- [エージェントメモリのロックイン](/blogs/wiki/concepts/agent-memory-lock-in/)
- [ハーネスエンジニアリング](/blogs/wiki/concepts/harness-engineering/)
- [グラフエンジニアリング](/blogs/wiki/concepts/graph-engineering/) — 協調構造を宣言的に設計するスワームの次段階
- [AIエージェント設計の5レイヤー](/blogs/wiki/concepts/ai-agent-design-layers/) — 協調パターンが位置づく全体地図
- [オーケストレーター／コーダー分業と承認ゲート](/blogs/wiki/concepts/orchestrator-coder-split/) — 2役に絞った最小の協調構成
- [AI 自律型組織](/blogs/wiki/concepts/ai-autonomous-organization/) — 4階層の企業組織として実装された協調構造
- [社会シミュレーション](/blogs/wiki/concepts/social-simulation/) — 多数のエージェントを住民として動かし、創発を観察する応用

## ソース記事

- [Anthropic が解説するマルチエージェント調整パターン 5 選](/blogs/posts/2026/04/anthropic-multi-agent-coordination-patterns/) — 2026-04-11
- [Claude Managed Agents のアーキテクチャ: Brain / Session / Hands の分離設計](/blogs/posts/2026/04/claude-managed-agents-architecture/) — 2026-04-10
- [NEC「部署が丸ごとAI」の中身 — コーポレートAI・Workforce部門の4階層と、人が手放さなかった仕事](/blogs/posts/2026/09/nec-corporate-ai-workforce/) — 2026-09-02
- [「従業員なしで会社を立ち上げるマニュアル」の中身 — Anthropic の Routines ワークショップを読み解く](/blogs/posts/2026/10/claude-code-routines-proactive-agent-workshop/) — 2026-10-30
- [Celery と claude -p で組む再帰的なエージェントオーケストレーション](/blogs/posts/2026/10/celery-claude-recursive-orchestration/) — 2026-10-30
- [エージェント同士に会話させる — Claude Code の 3 つの経路と A2A の使い分け](/blogs/posts/2026/11/agents-talking-to-agents/) — 2026-11-15
