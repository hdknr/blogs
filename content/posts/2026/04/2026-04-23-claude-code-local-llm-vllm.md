---
title: "Claude Code をローカル LLM（vLLM + MiniMax-M2.7）で爆速稼働させる方法"
date: 2026-04-23
lastmod: 2026-04-23
draft: false
description: "vLLM + MiniMax-M2.7 を使い Claude Code をローカル LLM で動かす方法。4× GPU / 8× GPU 構成のサーバー起動コマンド、環境変数設定、Prefix Caching による高速化、旧バージョン対応まで一通り解説する。"
source_url: "https://github.com/hdknr/blogs/issues/1#issuecomment-4303875610"
categories: ["AI/LLM"]
tags: ["claude-code", "vllm", "llm", "ローカルLLM", "prefix-caching"]
---

Claude Code を Anthropic の API ではなく、手元のマシンで動かすローカル LLM サーバーに接続することで、API コストをゼロにしながら最強のコーディングエージェントを使い倒せる。本記事では **vLLM + MiniMax-M2.7** を組み合わせた構成を紹介する。

## なぜローカル LLM で Claude Code を動かすのか

| 課題 | 解決策 |
|------|--------|
| API 費用が嵩む | ローカル推論でコストゼロ |
| 機密コードをクラウドに送りたくない | データがマシン外に出ない |
| レスポンスが遅い | vLLM の高速推論エンジン |

開発コストを抑えつつ、機密性の高いコードのデバッグや大規模リファクタリングにも安心して使える環境が手に入る。

## 技術スタック

- **vLLM** — OpenAI 互換 / Anthropic 互換の高速推論サーバー
- **MiniMax-M2.7** — Claude Code との相性が高いオープンモデル（コーディング・エージェント特化）
- **Prefix Caching** — 繰り返し送信されるシステムプロンプトをキャッシュしてレイテンシをほぼゼロに

## vLLM で MiniMax-M2.7 を起動する

### 必要なハードウェア

| 構成 | GPU メモリ | KV Cache |
|------|-----------|----------|
| 4× GPU | 96 GB × 4 | 400K トークン |
| 8× GPU | 144 GB × 8 | 3M トークン |

### サーバー起動コマンド

**4× GPU 構成（推奨）:**

```bash
SAFETENSORS_FAST_GPU=1 vllm serve MiniMaxAI/MiniMax-M2.7 \
  --trust-remote-code \
  --tensor-parallel-size 4 \
  --enable-auto-tool-choice \
  --tool-call-parser minimax_m2 \
  --reasoning-parser minimax_m2_append_think \
  --served-model-name minimax-m2-7
```

**8× GPU 構成（大規模 KV Cache が必要な場合）:**

```bash
SAFETENSORS_FAST_GPU=1 vllm serve MiniMaxAI/MiniMax-M2.7 \
  --trust-remote-code \
  --tensor-parallel-size 8 \
  --enable-auto-tool-choice \
  --tool-call-parser minimax_m2 \
  --reasoning-parser minimax_m2_append_think \
  --served-model-name minimax-m2-7 \
  --enable_expert_parallel
```

`--served-model-name` でスラッシュなしのエイリアスを付けるのがポイント。Claude Code はスラッシュを含むモデル名を認識できないため、エイリアスが必須。8× GPU 構成では `--enable_expert_parallel` を追加することで Expert Parallel を活用でき、スループットが向上する。

## Claude Code を vLLM に向ける環境変数

```bash
export ANTHROPIC_BASE_URL=http://localhost:8000
export ANTHROPIC_API_KEY=dummy
export ANTHROPIC_DEFAULT_OPUS_MODEL=minimax-m2-7
export ANTHROPIC_DEFAULT_SONNET_MODEL=minimax-m2-7
export ANTHROPIC_DEFAULT_HAIKU_MODEL=minimax-m2-7
```

`ANTHROPIC_BASE_URL` をローカルの vLLM サーバーに向けるだけで、Claude Code はそのまま動作する。`ANTHROPIC_API_KEY` はダミー値で構わない。

これらを `~/.zshrc` や `~/.bashrc` に記載しておけば、次回以降は設定不要。

## Prefix Caching でさらに高速化

vLLM の Prefix Caching を有効にすると、Claude Code が毎回送信するシステムプロンプト（数千トークン）のエンコードをスキップできる。

```bash
SAFETENSORS_FAST_GPU=1 vllm serve MiniMaxAI/MiniMax-M2.7 \
  --trust-remote-code \
  --tensor-parallel-size 4 \
  --enable-auto-tool-choice \
  --tool-call-parser minimax_m2 \
  --reasoning-parser minimax_m2_append_think \
  --served-model-name minimax-m2-7 \
  --enable-prefix-caching
```

システムプロンプトの初回読み込みだけ数秒かかるが、2 回目以降はほぼゼロ秒になる。

## vLLM の旧バージョンへの対応

vLLM 0.17.1 以前（0.17.1 を含む）のバージョンを使う場合は、`~/.claude/settings.json` に以下を追記する。

```json
{
  "env": {
    "CLAUDE_CODE_ATTRIBUTION_HEADER": "0"
  }
}
```

これはキャッシュ関連のバグを回避するための設定。最新版を使う場合は不要。

## API コストをかけずにできること

| ユースケース | 利点 |
|------------|------|
| 機密コードのデバッグ | データがローカルから出ない |
| 大規模リファクタリング | トークン消費を気にせず実行 |
| 繰り返し試行が必要な作業 | コストゼロで何度でも試せる |
| CI/CD 組み込み | サーバーコスト = インフラ費のみ |

## Claude Code + vLLM ローカル実行まとめ

Claude Code に必要なのは Anthropic 互換の API エンドポイント。vLLM はその互換 API を実装しており、`ANTHROPIC_BASE_URL` を差し替えるだけで接続できる。MiniMax-M2.7 はコーディング・エージェントワークフロー向けに設計されており、Claude Code との相性も良い。Prefix Caching を加えることで、インタラクティブな開発体験を損なわずにローカル実行を実現できる。
