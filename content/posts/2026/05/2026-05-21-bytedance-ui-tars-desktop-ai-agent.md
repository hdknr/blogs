---
title: "ByteDance製AIエージェント「UI-TARS-desktop」— ⭐3.5万超のPC画面操作AIの全貌"
date: 2026-05-21
lastmod: 2026-05-21
slug: "bytedance-ui-tars-desktop-ai-agent"
draft: false
source_url: "https://github.com/hdknr/blogs/issues/1#issuecomment-4504061323"
categories: ["AI/LLM"]
tags: ["ByteDance", "AIエージェント", "GUI自動化", "マルチモーダルAI", "オープンソース"]
---

TikTokの親会社として知られるByteDanceが、オープンソースのマルチモーダルAIエージェントスタック「**UI-TARS-desktop**」を公開した。GitHub上でスター数が3万5千を超えており、「PC画面を直接見て操作するAI」という次世代のコンピュータ操作パラダイムを提示している。

## UI-TARS-desktop とは

[UI-TARS-desktop](https://github.com/bytedance/UI-TARS-desktop) は、ByteDanceが開発したオープンソースのマルチモーダルAIエージェントスタックだ。リポジトリの説明には「The Open-Source Multimodal AI Agent Stack: Connecting Cutting-Edge AI Models and Agent Infra」とある。

このリポジトリは、2つのプロジェクトを含んでいる：

| プロジェクト | 概要 |
|---|---|
| **Agent TARS** | CLIとWeb UIを持つ汎用マルチモーダルAIエージェント |
| **UI-TARS Desktop** | UI-TARSモデルを搭載したデスクトップアプリ |

## Agent TARS の概要

**Agent TARS** は、GUIエージェント機能とビジョン能力をターミナル・コンピュータ・ブラウザにもたらす汎用エージェントだ。

### インストールと起動

```bash
# npx で即起動
npx @agent-tars/cli@latest

# グローバルインストール（Node.js >= 22 が必要）
npm install @agent-tars/cli@latest -g

# プロバイダーとモデルを指定して実行
agent-tars --provider anthropic --model claude-3-7-sonnet-latest --apiKey your-api-key
agent-tars --provider volcengine --model doubao-1-5-thinking-vision-pro-250428 --apiKey your-api-key
```

### 主要機能

- **ワンクリック起動** — Web UI（ヘッドフル）とサーバー（ヘッドレス）の両モードをサポート
- **ハイブリッドブラウザエージェント** — GUIエージェント、DOM操作、またはハイブリッド戦略でブラウザを制御
- **イベントストリーム** — プロトコル駆動のイベントストリームがContext EngineeringとAgent UIを動かす
- **MCP統合** — MCPプロトコル上に構築されており、外部MCPサーバーを接続して現実世界のツールと連携できる

実際の活用例として、「9月1日のサンノゼからニューヨークへの最早便と、9月6日の最終便をPricelineで予約してほしい」という自然言語指示に対して、エージェントが自律的にブラウザを操作して予約を実行するデモが公開されている。

## UI-TARS Desktop の概要

**UI-TARS Desktop** は、[UI-TARSモデル](https://github.com/bytedance/UI-TARS)をベースにしたデスクトップアプリだ。ローカルとリモートの両方でコンピュータおよびブラウザのオペレーターを提供する。

### バージョン履歴

- **v0.1.0（2025-04-20）** — UIを刷新し、ブラウザ操作機能を追加。UI-TARS-1.5モデルをサポート
- **v0.2.0（2025-06-11）** — **リモートコンピュータオペレーター**と**リモートブラウザオペレーター**を追加。設定不要・無料で利用可能（リリース当初は中国本土のみ対応）
- **v0.3.0（2025-11-04）** — シェルコマンドと複数ファイル表示のストリーミング対応、ツール呼び出しのタイミング統計、イベントストリームビューアーを追加（執筆時点での最新バージョン）

## PC画面を「見て・操作する」AIエージェントの意味

このプロジェクトが注目を集める理由は、AIが「クリック・タイピング」レベルで人間の代わりにタスクを実行できるという点だ。

従来の自動化ツールはAPIやDOMへのアクセスが前提だったが、UI-TARSアプローチは**視覚入力（スクリーンショット）から直接UI要素を認識して操作する**。これにより：

- APIが存在しないレガシーシステムの操作
- Webアプリのスクレイピングやフォーム入力
- デスクトップアプリの自動操作

といったことが、人間が手でやるのと同じ方法でAIに委託できるようになる。

## MCPエコシステムとの統合

Agent TARSはMCP（Model Context Protocol）の上に構築されており、Claudeなどのモデルと外部ツールの橋渡しをする標準プロトコルとの親和性が高い。MCPサーバーをマウントして、さまざまな現実世界のツールと接続できる点も見逃せない。

Claude Codeや他のAIエージェントとのワークフロー統合においても、このGUIオペレーター能力は強力な補完的役割を果たすと考えられる。

## まとめ

ByteDanceのUI-TARS-desktopは、「PC画面を見て操作するAI」を一般ユーザーが試せるオープンソースプロジェクトとして、AIエージェント分野における重要な一歩だ。

- **Agent TARS**：CLIとWeb UIを持つ汎用マルチモーダルエージェント
- **UI-TARS Desktop**：ローカル・リモートのコンピュータおよびブラウザ操作に特化したデスクトップアプリ

画面の前でモニターを見続けるだけの反復作業は、こうした技術によって着実に自動化されていく。エンジニアとして注目しておきたいプロジェクトだ。

- GitHub: [bytedance/UI-TARS-desktop](https://github.com/bytedance/UI-TARS-desktop)
- 公式サイト: [agent-tars.com](https://agent-tars.com)
