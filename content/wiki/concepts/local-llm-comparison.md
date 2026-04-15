---
title: "ローカルLLM比較（2026年春）"
description: "2026年春時点のローカル実行可能LLMの比較。Gemma 4、Qwen3.5、BitNetの特性とユースケース別の選び方"
date: 2026-04-15
lastmod: 2026-04-15
aliases: ["ローカルLLM", "local-llm", "オープンソースLLM比較"]
related_posts:
  - "/posts/2026/04/gemma4-vs-qwen35-local-llm/"
  - "/posts/2026/04/microsoft-bitnet-open-source-1bit-llm/"
  - "/posts/2026/04/gemma4-api-economy-disruption/"
tags: ["ローカルLLM", "Gemma", "Qwen", "BitNet", "オープンソースLLM", "Apple Silicon"]
---

## 概要

2026年春時点でローカル実行（オンプレミス・デバイス上）が現実的な主要 LLM の比較。いずれも Apache 2.0 または MIT ライセンスで商用利用可能。API 従量課金に依存しないアーキテクチャの実現に活用される。

## 主要3モデルの特性比較

| 項目 | Gemma 4 31B | Qwen3.5-27B | BitNet b1.58 2B |
|------|-------------|-------------|-----------------|
| 開発元 | Google DeepMind | Alibaba Qwen | Microsoft Research |
| パラメータ | 31B | 27B | 2.4B |
| ライセンス | Apache 2.0 | Apache 2.0 | MIT |
| 4bit メモリ | 約19GB | 約16.7GB | **0.4GB**（ネイティブ1.58bit） |
| CPU 推論 | llama.cpp 経由 | llama.cpp 経由 | **ネイティブ対応** |
| マルチモーダル | 画像・音声 | 画像・音声・動画 | テキストのみ |
| コンテキスト長 | 256K | 262K（最大1M） | 限定的 |
| MMLU Pro | 85.2% | 86.1% | —（MMLU 約52%） |

## ユースケース別の選び方

| ユースケース | 推奨モデル | 理由 |
|------------|----------|------|
| 推論・数学タスク | Gemma 4 31B | AIME 89.2%の突出した性能 |
| コーディング支援 | Qwen3.5-27B | SWE-bench 72.4%の実務対応力 |
| マルチモーダル（OCR含む） | Gemma 4 31B | 日本語テキスト画像にも対応 |
| 24GB メモリ環境での運用 | Qwen3.5-27B | 4bit で 16.7GB と余裕がある |
| 省メモリ・省電力最優先 | BitNet 2B | 0.4GB で動作、最大82%省エネ |
| GPU なしのローエンド PC | BitNet 2B | CPU 専用最適化カーネルで高速 |
| 長コンテキスト（1M） | Qwen3.5-27B | 1M トークンへの拡張対応 |

## Apple Silicon での実行

| モデル | Ollama | MLX サポート | 推奨メモリ |
|--------|--------|-------------|-----------|
| Gemma 4 31B | 対応 | vMLX 1.3.26+ が必要 | 32GB 以上 |
| Qwen3.5-27B | 対応 | mlx-community で成熟 | 24GB 以上 |
| BitNet 2B | 要確認 | — | 8GB でも動作可能 |

## API 経済への影響

Gemma 4 の Apache 2.0 ライセンスと E2B モデルのスマートフォンオフライン動作は、SaaS の API 従量課金構造を変える可能性がある:

- 自社サーバーで Gemma 4 を稼働させることで、外部 API コストを固定インフラコストに変換できる
- E2B モデルはスマートフォン上で 1.5GB 未満のメモリで動作し、API 呼び出しゼロのオフライン AI アプリが実現可能
- BitNet はさらに一歩進み、CPU だけで 100B 規模のモデルを動作させるアーキテクチャを提供

## 関連ページ

- [Gemma 4](/blogs/wiki/concepts/gemma4/) — Google DeepMind のオープンソース LLM 詳細
- [Qwen](/blogs/wiki/tools/qwen/) — Alibaba のオープンソース LLM 詳細
- [BitNet](/blogs/wiki/tools/bitnet/) — Microsoft の 1-bit LLM 詳細
- [Ollama](/blogs/wiki/tools/ollama/) — ローカル LLM 実行環境

## ソース記事

- [Gemma 4 31B vs Qwen3.5-27B — ローカルLLM最強はどちらか](/blogs/posts/2026/04/gemma4-vs-qwen35-local-llm/) — 2026-04-07
- [Microsoft BitNet 完全オープンソース化：GPUなしで1000億パラメータLLMをCPUで動かす時代へ](/blogs/posts/2026/04/microsoft-bitnet-open-source-1bit-llm/) — 2026-04-07
- [Gemma 4 が API 経済を破壊する](/blogs/posts/2026/04/gemma4-api-economy-disruption/) — 2026-04-07
