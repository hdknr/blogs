---
title: "無料なのに使わないのはもったいない：AI株式分析・金融端末・サイバー調査のGitHub 3選"
date: 2026-06-16
lastmod: 2026-06-16
slug: "free-github-repos-tradingagents-fincept-flowsint"
draft: false
source_url: "https://github.com/hdknr/blogs/issues/1#issuecomment-4714892316"
description: "TradingAgents（GitHub 86k stars）、Fincept Terminal（26k stars）、Flowsint（6.7k stars）── 本来なら有料級の金融AI分析・OSINT調査機能を無料で提供するオープンソースGitHubリポジトリ3選。"
categories: ["AI/LLM"]
tags: ["TradingAgents", "Flowsint", "OSINT", "金融AI", "agent", "python"]
---

「これが無料なのはおかしい」——Xでそう話題になったGitHubリポジトリがある。AI株式分析チームを丸ごとシミュレートするフレームワーク、Bloomberg級の金融データ端末、サイバー調査向けのグラフ可視化ツール。どれも本来なら有料級の機能を持ちながら、完全オープンソースで公開されている。本記事では、その中から厳選した3つを紹介する。

## TradingAgents — ウォール街のチームをPC上で動かすAIフレームワーク

**リポジトリ**: [TauricResearch/TradingAgents](https://github.com/TauricResearch/TradingAgents)（★86,000+）

TradingAgents は、複数のLLMエージェントが協調して株式投資戦略を議論・実行するマルチエージェント金融トレーディングフレームワークだ。

### アーキテクチャ

4種類のアナリストエージェントが並列で市場を分析する：

| エージェント | 担当領域 |
|---|---|
| ファンダメンタルアナリスト | 決算・財務指標・内部者取引 |
| センチメントアナリスト | SNS・コミュニティの雰囲気 |
| ニュースアナリスト | Bloomberg・Reuters・FinhubのRTデータ |
| テクニカルアナリスト | チャートパターン・指標 |

各アナリストの分析結果はリサーチャーチームが統合し、トレーダーエージェントが取引提案を作成する。リスク管理チーム（Aggressive / Neutral / Conservative の3段階）がリスク評価を行い、マネージャーエージェントが最終的な売買判断を下す。OpenAI、Anthropic、Google、DeepSeekなど複数のLLMプロバイダーに対応しており、用途に応じてモデルを選択できる点が特徴だ。

### データソース

- **市場データ**: Yahoo Finance、各種チャート
- **ソーシャルデータ**: X（旧Twitter）、Reddit、EODHD APIs
- **ニュース**: Bloomberg、Finnhub、Reuters、Reddit
- **ファンダメンタル**: 企業プロファイル、財務履歴、インサイダー取引

### インストールと使い方

```bash
git clone https://github.com/TauricResearch/TradingAgents.git
cd TradingAgents
pip install -r requirements.txt
```

環境変数に各種APIキー（OpenAI、FinnHub等）を設定した後：

```bash
python main.py
```

対話形式で分析対象の銘柄、日付範囲、使用するLLMモデルを指定できる。「24時間稼働するウォール街チームをPC上で動かす感覚」という表現がこれほど的確なシステムも珍しい。

---

## Fincept Terminal — Bloombergライクな金融データ端末

**リポジトリ**: [Fincept-Corporation/FinceptTerminal](https://github.com/Fincept-Corporation/FinceptTerminal)（★26,000+）

Fincept Terminal は、Pythonで構築されたターミナルベースの金融分析プラットフォームだ。リアルタイム市場データ、AIチャット、バックテスト、アルゴリズム取引など、Bloomberg端末に匹敵する機能を無料で提供する。

### 主な機能

- **DASHBOARD**: 主要指数・為替・コモディティのリアルタイム概況
- **MARKETS**: 株式・暗号資産・ETFの詳細データ
- **NEWS**: 1000件超のライブニュースフィード（フィルタリング・AI分析対応）
- **AI CHAT**: 市場状況についてAIと対話
- **BACKTEST**: 戦略のバックテスト
- **ALGO**: アルゴリズム取引の設定・実行
- **QUANT LAB**: 定量分析環境

ターミナルのUIは洗練されており、コマンドパレット（`Enter Command ⌘`）から素早く各機能にアクセスできる。

### インストール

```bash
pip install fincept-terminal
fincept
```

`pip install` 一発で起動できる手軽さも特徴だ。個人投資家が本格的な定量分析を行うための環境として、これ以上コストパフォーマンスの高いツールはほとんど存在しない。

---

## Flowsint — OSINT調査のためのグラフ可視化プラットフォーム

**リポジトリ**: [reconurge/flowsint](https://github.com/reconurge/flowsint)（★6,700+）

Flowsint は、サイバーセキュリティアナリストや調査者向けのオープンソースグラフ調査プラットフォームだ。ドメイン、IPアドレス、DNSレコード、証明書などの情報をグラフとして可視化し、複雑な関係性を直感的に把握できる。

### 何ができるか

- ドメイン・IPアドレスの関連グラフを自動構築
- 隣接ノード（169件超など）をワンクリックで展開
- 複数のエンリッチャー（外部データソース）からの情報統合
- フィルタリング・検索による絞り込み
- デスクトップアプリ版（[Onivoid/flowsint-desktop](https://github.com/Onivoid/flowsint-desktop)）も提供

### ユースケース

- **脅威インテリジェンス**: 不審なIPの関連ドメインを追跡
- **ペネトレーションテスト**: 攻撃対象の偵察フェーズでの情報収集
- **詐欺調査**: 詐欺サイトのインフラ関係性の解明
- **ジャーナリズム**: 企業・団体のネットワーク関係の調査

Maltego等の商用ツールと同等のグラフ調査機能をオープンソースで実現している点が評価されている理由だ。

### インストール（Docker推奨）

```bash
git clone https://github.com/reconurge/flowsint.git
cd flowsint
docker compose up -d
```

ブラウザで `http://localhost:5173` にアクセスすると調査インターフェースが立ち上がる。起動前に `.env` ファイルで `NEO4J_USERNAME` 等の環境変数を設定する必要がある。

---

## まとめ

| ツール | 用途 | Stars |
|---|---|---|
| TradingAgents | LLMマルチエージェント株式分析 | 86k |
| Fincept Terminal | 金融データ端末・バックテスト | 26k |
| Flowsint | OSINT・グラフ調査 | 6.7k |

3つともビジネス領域では数万〜数十万円の有料ツールで実現されてきた機能を、オープンソースで無料提供している。TradingAgentsは金融機関のリサーチ部門が行うような多角的分析を自動化し、Fincept Terminalはプロ向け端末の代替となり、FlowsintはMaltegoのようなサイバー調査ツールに迫る機能を持つ。

「無料なのに使わないのはもったいない」——この言葉が決して誇張でないことは、実際に触れてみれば一目瞭然だ。
