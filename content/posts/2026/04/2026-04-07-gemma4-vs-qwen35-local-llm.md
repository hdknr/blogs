---
title: "Gemma 4 31B vs Qwen3.5-27B — ローカルLLM最強はどちらか"
date: 2026-04-07
lastmod: 2026-04-07
draft: false
description: "Google Gemma 4 31BとAlibaba Qwen3.5-27Bをローカル実行の観点で徹底比較。ベンチマーク、メモリ要件、マルチモーダル、日本語対応、推論速度を検証する。"
categories: ["AI/LLM"]
tags: ["Gemma", "qwen", "llm", "Apple Silicon", "ollama"]
---

2026年春、ローカルで動かせる高性能 LLM の選択肢が充実してきた。中でも注目なのが **Google の Gemma 4 31B**（2026年4月リリース、Apache 2.0）と **Alibaba の Qwen3.5-27B**（2026年2月リリース）だ。どちらも密（dense）モデルで、Apple Silicon Mac や RTX 4090 クラスの GPU で実用的に動作する。

結論を先に述べると、**推論・マルチモーダルなら Gemma 4、コーディング・メモリ効率なら Qwen3.5** が適している。本記事では、その判断根拠を主要な観点から比較する。

## 基本スペック比較

| 項目 | Gemma 4 31B | Qwen3.5-27B |
|------|-------------|-------------|
| パラメータ数 | 31B | 27B |
| アーキテクチャ | Dense Transformer（Hybrid Attention） | Dense（Gated Delta Net + FFN） |
| コンテキスト長 | 256K トークン | 262K トークン（最大 1M 拡張可） |
| 対応言語 | 140+ 言語 | 201 言語 |
| マルチモーダル | ビジョン（画像理解・OCR） | ビジョン（画像理解） |
| ライセンス | Apache 2.0 | Apache 2.0 |
| 開発元 | Google DeepMind | Alibaba Qwen |

両モデルとも Apache 2.0 ライセンスで、商用利用に制限がない。コンテキスト長はほぼ同等だが、Qwen3.5 は 1M トークンまでの拡張に対応している点で有利だ。

## ベンチマーク比較

### 知識・推論

| ベンチマーク | Gemma 4 31B | Qwen3.5-27B | 優位 |
|-------------|-------------|-------------|------|
| MMLU-Pro | 85.2% | 86.1% | Qwen |
| GPQA Diamond | 84.3% | 85.5% | Qwen |
| AIME 2026（数学） | 89.2% | — | Gemma |

※ 「—」は公式ベンチマーク結果が公開されていない項目を示す。

知識系ベンチマーク（MMLU-Pro, GPQA Diamond）では **Qwen3.5 がわずかに上回る**。一方、数学の競技レベル問題（AIME 2026）では **Gemma 4 が 89.2%** と突出している。

### コーディング

| ベンチマーク | Gemma 4 31B | Qwen3.5-27B | 優位 |
|-------------|-------------|-------------|------|
| SWE-bench Verified | — | 72.4% | Qwen |
| LiveCodeBench | — | 80.7% | Qwen |
| Codeforces ELO | 2150 | — | Gemma |

コーディング関連では **Qwen3.5 が SWE-bench Verified 72.4%、LiveCodeBench 80.7%** と強い。Gemma 4 は Codeforces ELO 2150 で競技プログラミング系に強みを見せる。全体として、実務的なコーディングタスクでは Qwen3.5 が安定している。

### 総合

Arena AI リーダーボードでは **Gemma 4 31B がスコア 1,452** でオープンモデル第3位にランクイン。推論（reasoning）タスクでは Gemma 4 が平均 66.4 対 60.6 で優位だが、知識タスクでは Qwen3.5 が 80.6 対 61.3 と大差をつけている。

## メモリ要件と量子化

### Gemma 4 31B

| 量子化 | モデルサイズ | 必要メモリ |
|--------|------------|-----------|
| JANG_4M（dealignai 提供の混合精度、平均 5.1bit） | 18 GB | 24 GB+ |
| Q4_K_M（4bit） | 約 19 GB | 24 GB+ |
| Q8_0（8bit） | 約 34 GB | 36 GB+ |

### Qwen3.5-27B

| 量子化 | モデルサイズ | 必要メモリ |
|--------|------------|-----------|
| Q4_K_M（4bit） | 約 16.7 GB | 18 GB+ |
| Q8_0（8bit） | 約 30 GB | 32 GB+ |
| FP16 | 約 54 GB | 56 GB+ |

パラメータ数の差（31B vs 27B）がそのままメモリ要件に反映されている。**RTX 4090（24GB）や M2/M3 Mac（24GB）では Qwen3.5 の方が余裕がある**。Gemma 4 31B の Q4 量子化は 24GB 環境でもギリギリ動作するが、コンテキストを長くすると不足する可能性がある。

**32GB 以上のメモリ**があれば、両モデルとも快適に動作する。

## ローカル実行環境

### Ollama

両モデルとも Ollama で手軽に実行できる。

```bash
# Gemma 4 31B
ollama run gemma4:31b

# Qwen3.5-27B
ollama run qwen3.5:27b
```

Ollama は 0.19 から MLX バックエンドをプレビューサポートしており、Apple Silicon での高速化が期待できる。

### MLX（Apple Silicon 向け）

| 項目 | Gemma 4 31B | Qwen3.5-27B |
|------|-------------|-------------|
| MLX 対応 | vMLX 1.3.26+ が必要 | mlx-community で対応済み |
| 標準 mlx_lm | 2026年4月時点で未対応 | 対応済み |

Gemma 4 は MLX のエコシステムサポートがまだ発展途上で、専用の [vMLX](https://vmlx.net) が必要な点がやや不便だ。Qwen3.5 は mlx-community の量子化モデルが豊富で、すぐに使い始められる。

### 推論速度の目安（Apple Silicon）

llama.cpp ベースでの参考値:

- **Gemma 4 31B**: M5 Max で約 15 tok/s（llama.cpp、MLX 非使用時）
- **Gemma 4 26B MoE**: M2 Ultra で約 300 tok/s（参考）

Qwen3.5-27B の Apple Silicon 上での公式ベンチマークは 2026年4月時点で未公開だが、パラメータ数が約13%少ないため、同じ量子化レベルでは Gemma 4 31B より高速になると見込まれる。

※ 上記の Gemma 4 26B MoE は本記事の比較対象（Dense モデル）ではなく、参考値として掲載。

## 日本語対応

| 項目 | Gemma 4 31B | Qwen3.5-27B |
|------|-------------|-------------|
| 学習言語数 | 140+ | 201 |
| 日本語対応 | 明示的にサポート | 明示的にサポート |
| 日本語 OCR | ビジョン機能で対応 | 未検証 |

両モデルとも日本語をサポートしている。Gemma 4 はマルチモーダル機能により日本語テキストを含む画像の OCR にも対応しており、書類処理などの用途で有利だ。Qwen3.5 は 201 言語という幅広い言語カバレッジを持つ。

日本語の文章生成品質は、両モデルとも実用レベルに達しているが、個別のタスクでの優劣はプロンプトや用途に依存する部分が大きい。

## どちらを選ぶべきか

### Gemma 4 31B が向いているケース

- **推論・数学タスク**が中心（AIME 89.2%）
- **マルチモーダル**（画像理解・OCR）を重視
- 32GB 以上のメモリがある環境

### Qwen3.5-27B が向いているケース

- **コーディング支援**が主な用途（SWE-bench 72.4%）
- **24GB メモリ**で動かしたい（4bit で 16.7GB）
- **MLX エコシステム**をすぐ使いたい
- **長コンテキスト**（1M トークン拡張）が必要

### まとめ

| 観点 | 推奨 |
|------|------|
| 推論・数学 | Gemma 4 31B |
| コーディング | Qwen3.5-27B |
| マルチモーダル | Gemma 4 31B |
| メモリ効率 | Qwen3.5-27B |
| エコシステム成熟度 | Qwen3.5-27B |
| 知識ベンチマーク | Qwen3.5-27B |
| ライセンス | 同等（Apache 2.0） |

両モデルとも優秀で、明確な「最強」は存在しない。用途とハードウェア環境に応じて選ぶのが正解だ。推論とマルチモーダルなら Gemma 4、コーディングとメモリ効率なら Qwen3.5 という棲み分けになるだろう。

## 参考リンク

- [Gemma 4 公式ブログ](https://blog.google/innovation-and-ai/technology/developers-tools/gemma-4/)
- [Gemma 4 — Google DeepMind](https://deepmind.google/models/gemma/gemma-4/)
- [Qwen3.5-27B — Hugging Face](https://huggingface.co/Qwen/Qwen3.5-27B)
- [Qwen 3.5 vs Gemma 4 ベンチマーク比較（Maniac）](https://www.maniac.ai/blog/qwen-3-5-vs-gemma-4-benchmarks-by-size)
- [Gemma 4 31B vs Qwen3.5-27B（Artificial Analysis）](https://artificialanalysis.ai/models/comparisons/gemma-4-31b-vs-qwen3-5-27b)
- [Ollama — gemma4:31b](https://ollama.com/library/gemma4:31b)
- [Ollama — qwen3.5:27b](https://ollama.com/library/qwen3.5:27b)
