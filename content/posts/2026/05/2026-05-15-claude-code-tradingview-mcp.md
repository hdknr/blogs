---
title: "Claude Code × TradingView — MCPサーバーでチャートを「会話で動かす」時代へ"
date: 2026-05-15
lastmod: 2026-05-15
slug: "claude-code-tradingview-mcp"
draft: false
source_url: "https://github.com/hdknr/blogs/issues/1#issuecomment-4462499338"
categories: ["AI/LLM"]
tags: ["claude-code", "TradingView", "mcp", "トレーディング", "自動売買", "Pine Script", "BitGet"]
description: "TradingView Desktop を MCP サーバー経由で Claude Code から操作する方法を解説。78個のツールによるチャート取得・Pine Script 開発・BitGet 自動発注まで、オープンソース実装3種を比較紹介。"
---

海外トレーダーコミュニティで爆発的に拡散している手法がある。Claude Code と TradingView を MCP（Model Context Protocol）サーバーで直接つなぎ、チャートを「手で操作する」から「会話で動かす」へ変えるアプローチだ。

本記事では、その仕組みと主要なオープンソース実装を解説する。

## なぜ今「Claude Code × TradingView」が注目されるのか

TradingView はトレーダーが日常的に使う株価・指標チャートツールだ。これまでは人間がUIを開き、銘柄を手入力し、RSI や MACD を目視で確認してから判断を下していた。

MCP を介して Claude Code と接続すると、この操作が一変する。

- 「このチャートパターンを探して」と日本語でお願いできる
- 過去データを使ったバックテストを数分で回せる
- 監視銘柄リストを朝一でスキャンし、サマリを返してもらえる
- Pine Script のオリジナル指標を口頭で指示し、そのままチャートに反映できる

操作の粒度が「GUI のクリック」から「自然言語の会話」へと抽象化される。

## アーキテクチャの核心：Electron の CDP を逆用する

メインの実装は [tradesdontlie/tradingview-mcp](https://github.com/tradesdontlie/tradingview-mcp) だ。

TradingView Desktop は Electron（Chromium ベース）で動いている。CDP（Chrome DevTools Protocol）とは、Chromium ベースのアプリにデバッグ・操作用の WebSocket インターフェースを公開するプロトコルだ。Electron アプリは `--remote-debugging-port` フラグを付けて起動すると CDP が有効になり、外部プロセスがブラウザ内部を操作できる。VS Code や Discord が同じ仕組みで拡張機能を動かしているのと同じ発想だ。

![Claude Code → MCP Server → CDP → TradingView Desktop の接続フロー。すべてローカル完結でTradingViewサーバーへの外部接続なし](/blogs/images/claude-code-tradingview-mcp-architecture.png)

接続はすべてローカル完結。TradingView のサーバーには一切アクセスしない。依存ライブラリも `@modelcontextprotocol/sdk` と `chrome-remote-interface` の2つだけで、Node.js 18+ があれば動く。

### セットアップ手順

```bash
git clone https://github.com/tradesdontlie/tradingview-mcp.git
cd tradingview-mcp
npm install
```

`~/.claude/.mcp.json` に追記する。

```json
{
  "mcpServers": {
    "tradingview": {
      "command": "node",
      "args": ["/path/to/tradingview-mcp/src/server.js"]
    }
  }
}
```

TradingView Desktop を CDP モードで起動する（Mac の場合）。

```bash
/Applications/TradingView.app/Contents/MacOS/TradingView --remote-debugging-port=9222
```

リポジトリ付属のシェルスクリプト `scripts/launch_tv_debug_mac.sh` を使っても同じだ。

## 78個の MCP ツールで何ができるか

接続が確立すると、Claude Code から呼び出せるツールが78個に増える。主なカテゴリを紹介する。

### データ取得

| ツール | 内容 |
|--------|------|
| `chart_get_state` | シンボル・時間足・全インジケーター名 + ID を取得 |
| `data_get_study_values` | RSI / MACD / ボリンジャーバンド / EMA などのリアルタイム値 |
| `quote_get` | 最新価格・OHLC・出来高 |
| `data_get_pine_lines` | Pine Script の `line.new()` で描画されたカスタムラインデータ |
| `capture_screenshot` | チャートのスクリーンショットを取得 |

### チャート操作

| ツール | 内容 |
|--------|------|
| `chart_set_symbol` | 表示銘柄を切り替える |
| `chart_set_timeframe` | 時間足を変更する |
| `chart_set_type` | チャート種類（ローソク足・バーなど）を変更する |
| `draw_shape` | ライン・シェイプを描画する |
| `alert_create` | アラートを作成する |

### Pine Script 開発支援

| ツール | 内容 |
|--------|------|
| `pine_set_source` | Pine Script コードをチャートに注入する |
| `pine_smart_compile` | コンパイルしてエラーを返す |
| `pine_get_errors` | コンパイルエラー一覧を取得する |

「このインジケーターのロジックをコードにして」と Claude に依頼すると、Pine Script を書いてそのままチャートに反映するまでを一気に実行できる。

### バッチ・リプレイ

| ツール | 内容 |
|--------|------|
| `batch_run` | 複数銘柄を一括操作する |
| `replay_start` / `replay_step` | リプレイ練習を制御する |

## API ベースの別実装：atilaahmettaner/tradingview-mcp

TradingView Desktop に直接接続するのではなく、**Yahoo Finance API + Reddit センチメント + RSS ニュース**を組み合わせた研究・分析向けの実装も存在する。[atilaahmettaner/tradingview-mcp](https://github.com/atilaahmettaner/tradingview-mcp) が Python 製でこのアプローチを採用している。

```bash
pip install tradingview-mcp-server
```

30以上のツールを提供し、代表的なものは以下の通り。

- `get_technical_analysis` — RSI / MACD / ボリンジャーバンドなど23指標の BUY / SELL / HOLD 判定
- `backtest_strategy` — 6戦略のバックテスト（Sharpe 比、Calmar 比、期待値付き）
- `compare_strategies` — 全6戦略を同一銘柄で比較してランキング
- `market_sentiment` — Reddit の感情分析（Bullish / Bearish スコア）
- `financial_news` — Reuters / CoinDesk などのライブ RSS フィード
- `market_snapshot` — S&P500, NASDAQ, VIX, BTC, ETH, EUR/USD の一覧

Binance, KuCoin, Bybit, NASDAQ, NYSE など主要取引所に対応している。

## 自動売買への応用：BitGet 発注まで一気通貫

[jackson-video-resources/claude-tradingview-mcp-trading](https://github.com/jackson-video-resources/claude-tradingview-mcp-trading) は tradesdontlie の MCP をベースに、**BitGet への自動発注**まで実装している。

発注フローは次の5ステップだ。

1. `rules.json` の戦略ルールを読み込む
2. TradingView から価格・インジケーターデータを取得する
3. 生ローソク足データから MACD を計算する
4. 全エントリー条件を検証するセーフティチェックを通過する
5. 全条件パスなら BitGet API で発注し、`trades.csv` に記録する

VPS 24時間運用（Hostinger など）と cron スケジューリングにも対応しており、完全自動のトレードシステムを OSS で構築できる。

## 注意点とリスク

技術的には非常に興味深いが、実運用前に把握しておくべきリスクがある。

**TradingView 利用規約の問題**

TradingView の利用規約は自動データ収集を禁じている。CDP 経由でのデータ取得がこれに抵触する可能性があり、アカウント BAN のリスクが存在する。自己責任での利用となる。

**有料サブスクリプションが必須**

Desktop 版の CDP 接続には TradingView の有料プランが必要だ。無料プランでは動作しない。

**TradingView アップデートで壊れる可能性**

内部の undocumented API を利用しているため、TradingView 側のアップデートでいつでも動作しなくなるリスクがある。

## まとめ

MCP プロトコルを介した Claude Code × TradingView の接続は、「ツールを手で操作する」から「ツールを会話で動かす」への根本的な操作パラダイムシフトを体現している。

Pine Script の開発支援から朝のウォッチリストスキャン、さらには自動発注まで、オープンソースで揃ってきた実装群はトレーダーの開発コストを大幅に下げる可能性を持つ。一方で利用規約リスクと undocumented API 依存という現実的な制約も存在する。

Claude Code による自動取引の他の実践例として、[Claude × BTC自動取引 — モンテカルロ法で1万通りのシナリオを検証](/blogs/posts/2026/05/claude-btc-trading-montecarlo/)や[日経225マイクロ先物 × Monte Carlo 自動売買判定](/blogs/posts/2026/05/nikkei225-micro-monte-carlo-claude/)も参照してほしい。

興味を持った方はまず [tradesdontlie/tradingview-mcp](https://github.com/tradesdontlie/tradingview-mcp) の README を読み、ローカル環境で試してみるのが第一歩だ。
