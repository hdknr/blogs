---
title: "Qwen（クウェン）"
description: "Alibaba の Qwen チームが開発するオープンソース LLM シリーズ。コーディング性能・長コンテキスト・メモリ効率に優れ、Apache 2.0 ライセンスで商用利用可能"
date: 2026-04-15
lastmod: 2026-04-15
aliases: ["Qwen3.5", "通義千問"]
related_posts:
  - "/posts/2026/04/gemma4-vs-qwen35-local-llm/"
tags: ["Qwen", "オープンソースLLM", "Alibaba", "ローカルLLM", "コーディング"]
---

## 概要

Alibaba の Qwen チームが開発・公開する大規模言語モデルシリーズ。Apache 2.0 ライセンスで商用利用可能。コーディング性能、長コンテキスト対応、メモリ効率のバランスが優れており、ローカル LLM として実用性の高い選択肢。

## Qwen3.5-27B の主要スペック

| 項目 | 内容 |
|------|------|
| パラメータ数 | 27B |
| アーキテクチャ | Dense（Gated Delta Net + FFN） |
| コンテキスト長 | 262K トークン（最大 1M 拡張可） |
| 対応言語 | 201 言語 |
| マルチモーダル | ビジョン（画像理解） |
| ライセンス | Apache 2.0 |
| リリース | 2026年2月 |

## ベンチマーク（Qwen3.5-27B）

| ベンチマーク | スコア | 備考 |
|-------------|--------|------|
| SWE-bench Verified | 72.4% | コーディング課題解決 |
| LiveCodeBench | 80.7% | コーディング性能 |
| MMLU-Pro | 86.1% | 知識・推論 |
| GPQA Diamond | 85.5% | 科学的推論 |

## メモリ要件

| 量子化 | モデルサイズ | 必要メモリ |
|--------|------------|-----------|
| Q4_K_M（4bit） | 約 16.7 GB | 18 GB+ |
| Q8_0（8bit） | 約 30 GB | 32 GB+ |
| FP16 | 約 54 GB | 56 GB+ |

4bit 量子化で 16.7GB と、24GB メモリ環境（RTX 4090 / M2 Mac 24GB）で余裕を持って動作する。

## ローカル実行

```bash
# Ollama で実行
ollama run qwen3.5:27b
```

MLX（Apple Silicon）エコシステムのサポートが成熟しており、`mlx-community` の量子化モデルがすぐに利用できる。

## Gemma 4 との使い分け

| 観点 | Qwen3.5-27B | Gemma 4 31B |
|------|-------------|-------------|
| コーディング | 優位（SWE-bench 72.4%） | — |
| 推論・数学 | — | 優位（AIME 89.2%） |
| マルチモーダル | 基本対応 | 優位（OCR 含む） |
| メモリ効率 | 優位（4bit: 16.7GB） | 4bit: 約 19GB |
| MLX サポート | 成熟 | 発展途上 |

コーディング支援・メモリ効率・MLX 活用を重視するなら Qwen3.5、推論・数学・マルチモーダルを重視するなら Gemma 4 が適している。

## 関連ページ

- [ローカルLLM比較（2026年春）](/blogs/wiki/concepts/local-llm-comparison/) — Gemma 4 / Qwen3.5 / BitNet の横断比較
- [Gemma 4](/blogs/wiki/concepts/gemma4/) — Google DeepMind のオープンソース LLM
- [Ollama](/blogs/wiki/tools/ollama/) — ローカル LLM 実行環境
- [BitNet](/blogs/wiki/tools/bitnet/) — CPU 専用の超軽量 LLM

## ソース記事

- [Gemma 4 31B vs Qwen3.5-27B — ローカルLLM最強はどちらか](/blogs/posts/2026/04/gemma4-vs-qwen35-local-llm/) — 2026-04-07
