---
title: "DFlash"
description: "Apple Silicon 向け MLX フレームワークで動作するブロック拡散型投機的デコード実装。ローカル LLM を最大 4.1 倍高速化"
date: 2026-04-23
lastmod: 2026-04-23
aliases: ["dflash-mlx", "Block Diffusion Flash Speculative Decoding"]
related_posts:
  - "/posts/2026/04/2026-04-15-dflash-mlx-apple-silicon-llm/"
tags: ["Apple Silicon", "MLX", "ローカルLLM", "推論高速化", "推測デコード"]
---

## 概要

DFlash（Block Diffusion for Flash Speculative Decoding）は投機的デコードを発展させた推論加速技術の MLX 実装（[dflash-mlx](https://github.com/Aryagm/dflash-mlx)）。Qwen3.5-9B モデルで **4.1 倍**のスループット向上を達成。精度を落とさない exact speculative decoding（ロスレス）。

## 仕組み

通常の推測デコードは小さなドラフトモデルが 1 トークンずつ予測するのに対し、DFlash はドラフトモデルが **16 トークンを並列生成**。ターゲットモデルが 1 回のフォワードパスでまとめて検証するため大幅なスループット向上を実現。Apple 独自の Metal カーネルでロールバック処理を実装しオーバーヘッドを最小化。

## インストール

```bash
git clone https://github.com/aryagm/dflash-mlx.git
cd dflash-mlx
uv sync
uv run dflash-mlx --max-new-tokens 128
```

## 関連ページ

- [ローカル LLM 比較](/blogs/wiki/concepts/local-llm-comparison/)

## ソース記事

- [MacのローカルLLMが4.1倍速に！Apple Silicon向け新技術「DFlash」](/blogs/posts/2026/04/2026-04-15-dflash-mlx-apple-silicon-llm/) — 2026-04-15
