---
title: "ByteDance DeerFlow — オープンソースの SuperAgent 基盤でAIエージェントを自律運用する"
date: 2026-03-11
lastmod: 2026-03-11
draft: false
source_url: "https://github.com/hdknr/blogs/issues/1#issuecomment-4035407734"
categories: ["AI/LLM"]
tags: ["llm", "agent", "claude-code", "python"]
---

ByteDance がオープンソースで公開した AI エージェント基盤「DeerFlow」（Deep Exploration and Efficient Research Flow）が注目を集めている。サブエージェントの自動振り分け、サンドボックスでのコード実行、長期メモリ、Claude Code 連携など、プロダクション運用を見据えた機能が揃っている。

## DeerFlow とは

DeerFlow は、LangGraph / LangChain をベースに構築されたオープンソースの「SuperAgent ハーネス」。複雑なタスクをサブエージェントに分解し、メモリとサンドボックスを活用しながら自律的に処理する。

2026年2月27日に v2.0 がリリースされ、GitHub Trending で **#1** を獲得。v2.0 は v1 とコードを共有しない完全な書き直しで、プロダクション環境でのデプロイに焦点を当てている。

## 主な機能

### サブエージェントの自動振り分け

複雑なタスクを並列のサブエージェントワークフローに分解する。各サブエージェントは隔離されたコンテキストで動作し、スコープされたツールと終了条件を持つ。

### サンドボックス実行

タスクはコンテナ化された Docker 環境で実行される。専用のファイルシステムが用意され、入力・作業・出力のディレクトリが分離されている。

```
/mnt/user-data/uploads/   ← 入力ファイル
/mnt/user-data/workspace/  ← 作業ディレクトリ
/mnt/user-data/outputs/    ← 最終成果物
```

3つの実行モードをサポート:
- **ローカル実行** — 開発用
- **Docker 実行** — 単一サーバーでのプロダクション
- **Kubernetes 実行** — マルチサーバー環境

### スキルシステム

機能モジュールは Markdown ファイルとして提供される。リサーチ、レポート生成、スライド作成、Web ページ、画像/動画生成のスキルが組み込まれており、タスクの必要に応じてプログレッシブにロードされる。

### 長期メモリ

セッションをまたいだ永続的なプロファイルを構築できる。ユーザーの好み、ライティングスタイル、蓄積された知識をローカルに保存する。

### コンテキスト管理

タスクの要約、中間結果のファイルシステムへのオフロード、長時間セッションでの圧縮された状態管理によって、コンテキストウィンドウを効率的に利用する。

## セットアップ

### Docker での起動（推奨）

```bash
git clone https://github.com/bytedance/deer-flow.git
cd deer-flow
make config        # config.yaml を設定
make docker-init
make docker-start
```

`http://localhost:2026` でアクセスできる。

### ローカル開発

```bash
make check
make install
make setup-sandbox
make dev
```

### API キーの設定

`config.yaml` で OpenAI 互換 API のモデル定義を行い、`.env` ファイルで API キーを設定する。

## Claude Code との連携

DeerFlow は Claude Code との連携スキルを提供している。

```bash
npx skills add https://github.com/bytedance/deer-flow --skill claude-to-deerflow
```

これにより、Claude Code のターミナルからタスクの送信、ステータス確認、スレッド管理が可能になる。

## Python クライアント

```python
from src.client import DeerFlowClient

client = DeerFlowClient()
response = client.chat("リサーチタスクを実行", thread_id="my-thread")
```

## メッセージングチャネル連携

DeerFlow は複数のメッセージングプラットフォームと連携できる:

- **Telegram** — Bot API（ロングポーリング）
- **Slack** — Socket Mode
- **Feishu/Lark** — WebSocket

MCP サーバー（HTTP/SSE）もサポートしており、OAuth トークンフローに対応する。

## 推奨されるモデル要件

DeerFlow を効果的に使うには、以下の能力を持つ LLM が推奨される:

- 100K+ トークンのロングコンテキスト
- 適応的プランニングのための推論能力
- マルチモーダル入力
- ツール使用・関数呼び出し

## 既存のエージェントフレームワークとの違い

DeerFlow の特徴は「SuperAgent ハーネス」というコンセプトにある。単なるエージェントフレームワークではなく、エージェントが実際に動作する**ランタイム環境**を提供する点が異なる。実際のファイルシステム、bash ターミナル、コード実行環境を持ち、コマンドの提案ではなく実行ができる。

### OpenClaw との比較

DeerFlow と同時期に注目を集めている [OpenClaw](https://openclaw.ai/) は、自律型のコーディングエージェントである。両者はマルチエージェント構成や Markdown ベースのスキル定義など表面的に似た要素を持つが、レイヤーが異なる。

| 観点 | DeerFlow | OpenClaw |
|------|----------|----------|
| **位置づけ** | エージェント実行基盤（ランタイム） | コーディングエージェント |
| **主な役割** | サブエージェントの振り分け・管理・実行環境の提供 | コード生成・開発タスクの自律実行 |
| **基盤技術** | LangGraph / LangChain | 独自実装 |
| **サンドボックス** | Docker / Kubernetes による隔離実行 | ホスト環境で直接実行 |
| **ターゲットユーザー** | エージェントシステムを構築・運用するエンジニア | 開発タスクを AI に委譲したい個人・チーム |
| **スケーリング** | K8s によるマルチサーバー対応 | 単一サーバー運用が基本 |

比喩的に言えば、**DeerFlow はオフィス環境とマネジメント基盤**、**OpenClaw はそこで働く社員**に相当する。DeerFlow はエージェントが安全に動作する場所と仕組みを提供し、OpenClaw は具体的なタスクを実行する。理論的には DeerFlow の基盤上で OpenClaw 的なエージェントを動かす構成も可能であり、競合というよりは補完的な関係にある。

## まとめ

DeerFlow は、AI エージェントの自律運用に必要な要素——サブエージェント分割、サンドボックス実行、永続メモリ、スキルシステム——を一つのフレームワークにまとめた意欲的なプロジェクト。v2.0 で Docker / Kubernetes デプロイに対応し、プロダクション利用も視野に入る。Claude Code との連携や MCP サポートにより、既存のワークフローに組み込みやすい設計になっている。

OpenClaw のようなコーディングエージェントとはレイヤーが異なり、DeerFlow は「エージェントを動かす基盤」として位置づけられる。どちらか一方ではなく、用途に応じて使い分け、あるいは組み合わせるのが現実的なアプローチだ。
