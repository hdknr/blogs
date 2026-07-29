---
title: "Ruflo: Claude Code を 100 以上のエージェント群に変えるオープンソースハーネス"
date: 2026-06-16
lastmod: 2026-06-16
slug: "ruflo-claude-code-agent-swarm"
draft: false
description: "Ruflo（元 Claude Flow）は npx 一行で Claude Code を 100 以上の専門エージェントが協調するスウォームに変えるオープンソースハーネス。インストール方法からスウォーム・トポロジー・メモリ・フェデレーション機能まで解説。"
source_url: "https://github.com/hdknr/blogs/issues/1#issuecomment-4714996948"
categories: ["AI/LLM"]
tags: ["Claude Code", "Ruflo", "マルチエージェント", "MCP", "claude-flow"]
---

## はじめに

Claude Code は単体でも強力なツールだが、**Ruflo** と組み合わせると 100 以上のエージェントが並列で協調動作するスウォームに変貌する。

Ruflo（ルフロ）は、もともと **Claude Flow** という名前で知られていたオープンソースのエージェント・メタハーネスだ。現在の名称に改名されるとともに、Rust ベースの AI エンジンが追加された。主言語は TypeScript だが、メモリ・埋め込み・プラグインシステムには Rust が使われている。

- GitHub: [ruvnet/ruflo](https://github.com/ruvnet/ruflo)
- スター: 61,000 以上（2026 年 6 月時点）
- フォーク: 7,100 以上
- ライセンス: MIT

## Ruflo とは何か

Ruflo 自身の説明によると:

> Agent = Model + Harness.  
> モデルがコードを書き、ハーネスはツール・メモリ・ループ・サンドボックス・制御を与えて実際に動かす。**Ruflo がそのハーネス**だ。

`npx ruflo init` の一行で Claude Code に「神経系」が加わる。エージェントはスウォームに自己組織化し、タスクから学習し、セッションをまたいで記憶を保持する。開発者はコードを書き続けるだけで、エージェント間の調整は Ruflo が担う。

## インストール方法

Ruflo には 2 つのインストールパスがある。

### パス A: Claude Code プラグイン（軽量版）

スラッシュコマンドとエージェント定義のみを追加する。MCP サーバーは登録されないため、`memory_store` や `swarm_init` などのツールは呼び出せない。まず試したい場合に適している。

```bash
/plugin marketplace add ruvnet/ruflo
/plugin install ruflo-core@ruflo
/plugin install ruflo-swarm@ruflo
/plugin install ruflo-rag-memory@ruflo
```

### パス B: フル CLI インストール（推奨）

98 のエージェント、60 以上のコマンド、MCP サーバー、フック、デーモンを含む完全な Ruflo ループが有効になる。

```bash
# macOS / Linux / WSL
curl -fsSL https://cdn.jsdelivr.net/gh/ruvnet/ruflo@main/scripts/install.sh | bash

# 全プラットフォーム対応（Windows PowerShell 含む）
npx ruflo@latest init
```

Claude Code の MCP サーバーとして追加する場合:

```bash
claude mcp add ruflo -- npx ruflo@latest mcp start
```

## 主な機能

### 100 以上の専門エージェント

coder、tester、reviewer、architect、security など、役割に特化したエージェントが 100 以上用意されている。フルインストール時は 98 種類のエージェントが即座に使用可能で、随時追加されている。フックシステムがタスクを自動的に適切なエージェントにルーティングする。

### スウォーム・コーディネーション

エージェント群は複数のトポロジーで協調動作する:

| トポロジー | 特徴 |
|-----------|------|
| 階層型 (Hierarchical) | Queen エージェントがトップダウンで指揮 |
| メッシュ (Mesh) | 全エージェントが相互に連携するフラット構造 |
| アダプティブ (Adaptive) | タスクに応じてトポロジーを動的に切り替え |

コンセンサスには Raft、Byzantine Fault Tolerance（BFT）、Gossip プロトコルを採用している。

### 自己学習メモリ

- **AgentDB**: HNSW（近似最近傍探索アルゴリズム）インデックスによるベクトルメモリ。データ件数が増えるほど全件探索（brute force）比で 1.9〜4.7 倍高速になり、recall@10 は約 0.99 を維持
- **SONA**: 成功パターンを学習するニューラルパターンシステム
- **RAG 統合**: ハイブリッド検索・グラフホップ・多様性ランキングによるスマート検索

タスクのたびに学習が積み重なり、ルーターの精度は 89% を達成するとされている。

### エージェント・フェデレーション

異なるマシンやチームのエージェントが、ゼロトラストセキュリティで安全に連携できる。

- **認証**: mTLS + ed25519 チャレンジ・レスポンス（API キーや共有シークレット不要）
- **PII 保護**: 14 種類の個人情報を検出し、アウトバウンド前に自動除去または匿名化
- **信頼スコアリング**: 成功率・稼働率・脅威評価・整合性の 4 指標で継続評価
- **コンプライアンス**: HIPAA、SOC2、GDPR 対応の監査ログ

```bash
# フェデレーションの初期化と接続例
# ※ federation サブコマンドは npm パッケージ名 claude-flow のまま提供されている
npx claude-flow@latest federation init
npx claude-flow@latest federation join wss://team-b.example.com:8443
npx claude-flow@latest federation send --to team-b --type task-request \
  --message "Analyze transaction patterns for account anomalies"
```

### マルチモデル Web UI

ホスト型デモ [flo.ruv.io](https://flo.ruv.io/) では Claude、Qwen、Gemini、OpenAI を同じチャット画面から利用できる。約 210 の MCP ツールを並列で呼び出せる。自己ホスト可能な Docker イメージも提供されている。

## Claude Code 単体との比較

| 機能 | Claude Code のみ | + Ruflo |
|------|-----------------|---------|
| エージェント協調 | 独立、文脈共有なし | 共有メモリ・コンセンサスによるスウォーム |
| メモリ | セッション内のみ | HNSW ベクトルメモリ（サブミリ秒検索） |
| 学習 | 静的 | SONA による自己学習 |
| タスクルーティング | 手動 | インテリジェント自動ルーティング（精度 89%） |
| バックグラウンドワーカー | なし | 12 の自動トリガーワーカー |
| LLM プロバイダー | Anthropic のみ | 5 プロバイダー（フェイルオーバー付き） |

## プラグイン・エコシステム

Ruflo は 35 のプラグインを提供している。主なプラグインの一例:

| プラグイン | 機能 |
|-----------|------|
| ruflo-swarm | 複数エージェントのチーム協調 |
| ruflo-rag-memory | ハイブリッド検索・グラフホップ対応 RAG |
| ruflo-federation | 異マシン間のセキュアなエージェント連携 |
| ruflo-security-audit | 脆弱性・CVE スキャン |
| ruflo-testgen | テスト不足の検出と自動生成 |
| ruflo-intelligence | 過去の成功から学習する自己最適化 |
| ruflo-cost-tracker | トークン使用量の追跡とコストアラート |

## 技術スタック

主言語は **TypeScript**（コードベース全体の大部分）で、AI エンジン・メモリ・埋め込みシステムには **Rust** が使われている。WASM サンドボックス（rvagent）によるエージェントの安全な実行環境も提供する。フロントエンドは Svelte、コンテナは Docker で自己ホスト可能だ。

## まとめ

Ruflo は Claude Code の使い方を変えない。`npx ruflo init` した後も、既存のワークフローをそのままに、100 以上のエージェントが裏で動き始める。メモリ、自己学習、異マシン間フェデレーション——これらがすべて既存のワークフローに自動で組み込まれる。

まず Claude Code プラグイン版で試し、本番利用が見えたら CLI フルインストールに切り替えるのが現実的な導入ステップだろう。

- [GitHub リポジトリ (ruvnet/ruflo)](https://github.com/ruvnet/ruflo) — ソースコード・ドキュメント・プラグイン一覧
- [Web UI Beta (flo.ruv.io)](https://flo.ruv.io/) — アカウント不要で試せるマルチモデルチャット
- [Goal Planner (goal.ruv.io)](https://goal.ruv.io/) — 自然言語のゴールをエージェントプランに分解
