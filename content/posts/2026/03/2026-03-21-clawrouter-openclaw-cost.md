---
title: "ClawRouter — OpenClaw の API コストを最大92%削減するオープンソース LLM ルーター"
date: 2026-03-21
lastmod: 2026-03-21
draft: false
source_url: "https://github.com/hdknr/blogs/issues/1#issuecomment-4102696274"
categories: ["AI/LLM"]
tags: ["llm", "agent", "openclaw", "openai"]
---

OpenClaw を使っていて API コストが気になっていませんか？ **ClawRouter** は、リクエストごとに最安のモデルを自動選択してくれるオープンソースの LLM ルーターです。最大約92%のコスト削減が期待でき、しかも完全無料で利用できます。

## ClawRouter とは

[ClawRouter](https://github.com/BlockRunAI/ClawRouter) は、OpenClaw 向けに設計されたエージェントネイティブな LLM ルーターです。MIT ライセンスで公開されており、誰でも無料で利用できます。

主な特徴:

- **55以上のモデルに対応** — DeepSeek V3.2、Nemotron Ultra 253B、Mistral Large 3 675B、Llama 4 Maverick など
- **1ms 未満のルーティング** — すべてローカルで処理されるため、レイテンシの追加はほぼゼロ
- **15次元のリクエスト分析** — 各リクエストを多次元で要素分解し、最適なモデルをスコアリング
- **11モデルが完全無料** — 簡単なクエリは無料モデルに自動ルーティング

## どれくらいコストが下がるのか

ClawRouter の公式ベンチマークによると:

| 指標 | 値 |
|------|-----|
| ClawRouter 平均コスト | $2.05 / 100万トークン |
| Claude Opus 直接利用 | $25 / 100万トークン |
| **削減率** | **約92%** |

たとえば「2+2は？」のような簡単な質問は、DeepSeek などの無料モデルに自動ルーティングされます。一方、複雑な推論が必要なタスクにはプレミアムモデルが選択されるため、品質を犠牲にしません。

## 仕組み

ClawRouter は各リクエストに対して以下のプロセスを実行します:

1. **リクエスト分析** — 入力テキストを15次元で要素分解（タスクの複雑さ、必要な推論能力、言語、コンテキスト長など）
2. **スコアリング** — 各モデルの能力とコストを総合的に評価
3. **ルーティング** — 最もコスト効率の良いモデルを自動選択

この全プロセスが 1ms 未満で完了します。

## セットアップ

ClawRouter は OpenClaw、ElizaOS、および OpenAI 互換 API を使うあらゆるエージェントと統合できます。

```bash
# ClawRouter のインストール
git clone https://github.com/BlockRunAI/ClawRouter.git
cd ClawRouter
```

詳細な設定手順は [GitHub リポジトリの README](https://github.com/BlockRunAI/ClawRouter) を参照してください。

特徴的なのは、従来の API キーではなく **ウォレットベースの認証** を採用している点です。USDC（米ドル連動のステーブルコイン）によるリクエスト単位の課金で、サブスクリプションやクレジットカードは不要です。Base と Solana のチェーンに対応しています。

## 類似ツールとの比較

ClawRouter 以外にも、OpenClaw の API コストを最適化するツールが登場しています:

- **[ibl.ai OpenClaw Router](https://github.com/iblai/iblai-openclaw-router)** — 最大70%のコスト削減を謳うインテリジェントモデルルーター
- **[ClawRoute](https://github.com/atharv404/ClawRoute)** — 60〜90%のコスト削減を目指す別実装

LLM ルーティングは、OpenClaw エコシステムにおける重要なインフラレイヤーとして注目を集めています。

## まとめ

ClawRouter は「簡単なタスクにプレミアムモデルの料金を払う」という無駄を解消してくれます。MIT ライセンスのオープンソースで、導入のハードルも低いため、OpenClaw の API コストに悩んでいるなら試してみる価値があるでしょう。

- GitHub: [BlockRunAI/ClawRouter](https://github.com/BlockRunAI/ClawRouter)
- ライセンス: MIT（完全無料）
- 対応モデル: 55以上（うち11モデルは無料）
