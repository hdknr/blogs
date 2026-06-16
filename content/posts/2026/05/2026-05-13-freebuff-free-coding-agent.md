---
title: "FREEBUFF — DeepSeek V4 Pro・Kimi K2.6・MiniMax M2.7 が無料で使えるコーディングエージェント CLI"
date: 2026-05-13
lastmod: 2026-05-13
slug: "freebuff-free-coding-agent"
draft: false
source_url: "https://github.com/hdknr/blogs/issues/1#issuecomment-4439408922"
categories: ["AI/LLM"]
tags: ["FREEBUFF", "DeepSeek", "コーディングエージェント", "npm", "MiniMax", "Kimi", "MoE"]
description: "npm install -g freebuff の一行で DeepSeek V4 Pro・Kimi K2.6・MiniMax M2.7 が無料で使えるコーディングエージェント CLI FREEBUFF を解説。広告収益モデルの仕組み、各モデルのアーキテクチャ特徴、プライバシー注意点まで網羅。"
---

`npm install -g freebuff` の一行で、DeepSeek V4 Pro・Kimi K2.6・MiniMax M2.7 という 2026 年前半のトップクラス OSS モデル群を無料で使えるコーディングエージェントが登場した。その名は **FREEBUFF** だ。

## FREEBUFF とは何か

[FREEBUFF](https://freebuff.com/) は、AI コーディングエージェント製品 [Codebuff](https://codebuff.com/) の無料プランとして提供されるターミナル型 CLI エージェントだ。サブスクリプション不要・クレジット不要で、Claude Code や Aider に近い操作感でコードベースを自然言語で操作できる。

収益モデルは広告型。モデル推論のコストを CLI 内に表示されるテキスト広告で賄っており、ユーザーは金銭的な負担なしに強力なモデルを利用できる。

```bash
npm install -g freebuff
```

プロジェクトディレクトリで実行するだけで即座に使い始められる。

### 主な機能

| 機能 | 内容 |
|------|------|
| コード読み書き | 自然言語でファイルを編集・生成 |
| ターミナルコマンド実行 | ビルド・テスト・デプロイなどを代理実行 |
| Web リサーチ | 最新情報を取得してコーディングに活用 |
| ブラウザ操作 | Sub-agent 経由でブラウザを制御 |
| ディープシンク | ChatGPT サブスクを持つ場合はそちらを活用 |
| ファイルメンション | `@filename` 形式でファイルをコンテキストに追加 |
| Bash モード | シェルスクリプト的な操作 |

GitHub でオープンソース公開されており（[CodebuffAI/codebuff](https://github.com/CodebuffAI/codebuff)）、コードの透明性も確認できる。

## 使えるモデル一覧

FREEBUFF が接続するバックエンドでは、以下のモデルを切り替えて利用できる。

| モデル | 総パラメータ | 有効パラメータ | コンテキスト |
|--------|-------------|---------------|------------|
| DeepSeek V4 Pro | 1.6T | 49B | 1M トークン |
| DeepSeek V4 Flash | 284B | 13B | 1M トークン |
| Kimi K2.6 | 1T | 32B | 256K トークン |
| MiniMax M2.7 | 230B | 10B | 204.8K トークン |

いずれも 2026 年前半にリリースされた OSS 公開またはオープン API のフロンティアモデルだ。

## DeepSeek V4 Pro

[DeepSeek-V4-Pro](https://api-docs.deepseek.com/news/news260424) は DeepSeek が 2026 年 4 月 24 日にリリースした MoE（Mixture-of-Experts）モデルで、総パラメータ 1.6 兆・有効パラメータ 49B（490 億）という規模を持つ。ライセンスは MIT で Hugging Face からオープンウェイトを取得できる。

### アーキテクチャの特徴

- **ハイブリッドアテンション**: Compressed Sparse Attention（CSA）と Heavily Compressed Attention（HCA）を組み合わせ、1M トークンのコンテキストを単一トークン推論比で 27% の FLOP・10% の KV キャッシュで処理
- **Manifold-Constrained Hyper-Connections**: 安定した大規模訓練を実現
- **Muon オプティマイザ**: 32T トークンの学習データで訓練
- **混合精度**: MoE エキスパートに FP4、その他に FP8

### 推論モード

`<think>` タグで制御する 3 段階の推論深度を持つ。

非シンク（高速）→ Think High（中程度）→ Think Max（最大深度）の 3 段階で切り替える。

Codeforces レーティングで 3206 を記録し、コーディングベンチマークでオープンソース SOTA を達成している。

## Kimi K2.6

[Kimi K2.6](https://www.kimi.com/blog/kimi-k2-6) は Moonshot AI が 2026 年 4 月 20 日にリリースしたネイティブマルチモーダルなエージェントモデルだ。1 兆パラメータ（有効 32B・320 億）の MoE 構造に 400M パラメータのビジョンエンコーダ MoonViT を内蔵する。

### エージェント・スウォーム

前世代比で大幅に強化されたエージェント協調機能を持つ。

- **300 の専門サブエージェント** を並列展開
- **最大 4,000 ステップ** の長時間自律実行（12 時間超）
- Rust・Go・Python からフロントエンド・DevOps まで全スタック対応

SWE-Bench Verified で **80.2%**、AIME 2026 で **96.4%** という高スコアを記録している。

## MiniMax M2.7

[MiniMax M2.7](https://www.minimax.io/models/text/m27) は MiniMax が 2026 年 4 月上旬にリリースしたモデルで、**自己進化（Self-Evolution）** 能力が最大の特徴だ。

230B 総パラメータながら有効パラメータは 10B（100 億）と最小クラスで、推論コスト・速度の面で圧倒的に効率が良い。

### 自己進化の仕組み

[OpenClaw](https://github.com/openclaw/openclaw) エージェントハーネスフレームワーク上で、モデル自身が訓練スキャフォールドの最適化を 100 ラウンド以上繰り返し実施。人間の介入なしに内部評価で 30% の性能改善を達成した。

| 指標 | スコア |
|------|--------|
| SWE-Bench Verified | 78% |
| SWE-Pro | 56.22% |
| 推論速度 | 約 100 トークン/秒 |

API 価格も入力 約 $0.28 / 出力 $1.20（1M トークンあたり）と、同クラスのモデルで最安水準だ。

## インストールと使い方

```bash
# インストール
npm install -g freebuff

# プロジェクトディレクトリで起動
cd your-project
freebuff
```

起動後は Claude Code と同様にターミナル内で自然言語でコーディング指示を出せる。CLI 内に広告が表示されるが、それ以外の操作感は有料ツールと変わらない。

## 注意点

### プライバシー

FREEBUFF はクラウドバックエンドに接続する。コードがクラウド上の推論サーバーに送信されるため、**プロプライエタリなコードベースやシークレットを含むプロジェクトには使用しないこと** が推奨される。オープンソースプロジェクトや個人の学習用途に適している。

### 提供地域

すべての地域で利用できるわけではない。対応国の一覧は [freebuff.com](https://freebuff.com/) で確認できる。

## まとめ

FREEBUFF は「広告で無料」というシンプルなモデルで、2026 年前半の最強クラス OSS モデル群にアクセスできる珍しいサービスだ。DeepSeek V4 Pro の 1M コンテキスト・Kimi K2.6 の 300 エージェント協調・MiniMax M2.7 の自己進化という各モデルの個性を、`npm install` 一発で試せる。

個人プロジェクトや学習目的で有料 AI コーディングツールの代替を探している場合は、まず試してみる価値がある。
