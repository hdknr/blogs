---
title: "BitNet"
description: "Microsoft Research が開発した 1-bit LLM 専用の推論フレームワーク。GPU 不要で CPU 上で大規模 LLM を実行できる"
date: 2026-04-14
lastmod: 2026-04-14
aliases: ["bitnet.cpp", "BitNet b1.58"]
related_posts:
  - "/posts/2026/04/microsoft-bitnet-open-source-1bit-llm/"
tags: ["BitNet", "Microsoft", "1-bit LLM", "CPU推論", "量子化", "ローカルLLM"]
---

## 概要

Microsoft Research が開発し 2026年にオープンソース（MIT ライセンス）化した 1-bit LLM 専用推論フレームワーク。すべての重みを -1、0、+1 の3値（log2(3) ≒ 1.58bit）で表現し、GPU なしで CPU 上での実用的な LLM 推論を実現する。GitHub では 37,000 以上のスターを獲得している。

## 主な特徴

### GPU 不要の CPU 推論

llama.cpp をベースに 1-bit 推論向けに最適化した C++ フレームワーク（bitnet.cpp）。専用カーネルにより CPU 上で高速に動作する。

- x86 CPU: 従来比 2.37〜6.17 倍の高速化
- ARM CPU（Apple Silicon 含む）: 従来比 1.37〜5.07 倍の高速化
- 100B パラメータモデルを単一 CPU で 5〜7 トークン/秒で処理可能

### 省メモリ・省エネルギー

- BitNet b1.58 2B-4T モデルのメモリ使用量: わずか **0.4GB**（同規模通常モデルの 1/7〜1/20）
- エネルギー削減: x86 で最大 82.2%、ARM で最大 70.0%

## 主要モデル：BitNet b1.58 2B-4T

Hugging Face で公開されている初のオープンソースネイティブ 1-bit LLM。2.4B パラメータ、4T トークンで学習。同規模フル精度モデルと同等の性能（MMLU 約 52%）を達成。

## 他のローカル LLM との比較

| 項目 | BitNet 2.4B | Gemma 4 E4B | Qwen3.5 4B |
|------|-------------|-------------|------------|
| メモリ | **0.4GB** | 約5GB（4bit量子化） | 約3GB（4bit量子化） |
| CPU 推論 | ネイティブ対応 | llama.cpp 経由 | llama.cpp 経由 |
| マルチモーダル | テキストのみ | 画像・音声対応 | 画像・音声・動画対応 |
| MMLU | 約52% | 69.4%（Pro） | 79.1%（Pro） |

省メモリ・省電力が最優先の場合は BitNet、性能とのバランスを求めるなら Qwen3.5 が適している。

## 動作環境

- Python 3.9 以上、CMake 3.22 以上、Clang 18 以上
- Linux / macOS（x86_64、ARM）、Windows（x86_64、Visual Studio 2022 必須）

## 関連ページ

- [ローカルLLM比較（2026年春）](/blogs/wiki/concepts/local-llm-comparison/) — Gemma 4 / Qwen3.5 / BitNet の横断比較
- [Gemma 4](/blogs/wiki/concepts/gemma4/) — 同時期のオープンソース LLM
- [Qwen](/blogs/wiki/tools/qwen/) — 同時期の Alibaba オープンソース LLM
- [Ollama](/blogs/wiki/tools/ollama/) — CPU での LLM 実行の代替手段

## ソース記事

- [Microsoft BitNet 完全オープンソース化](/blogs/posts/2026/04/microsoft-bitnet-open-source-1bit-llm/) — 2026-04-07
