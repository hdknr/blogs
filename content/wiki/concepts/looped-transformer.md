---
title: "Looped Transformer（ループ型 Transformer）"
description: "重みを共有した層を繰り返し通して、パラメータを増やさずに深さを稼ぐ Transformer。推論時にループ回数を選んで計算量と精度を調整できる"
date: 2026-11-15
lastmod: 2026-11-15
aliases: ["ループ型Transformer", "Looped Transformer", "latent recurrent model", "elastic depth", "Dory1.0-4B", "Dory", "latent reasoning"]
related_posts:
  - "/posts/2026/11/looped-transformer-nvidia-dory/"
tags: ["Looped Transformer", "Transformer", "llm", "kv-cache", "NVIDIA"]
---

## 概要

Looped Transformer は、一部の層を**重み共有のまま複数回繰り返し適用する** Transformer。通常の Transformer が層ごとに別の重みを持ち、深くするほどパラメータが増えるのに対し、こちらはパラメータ数を固定したまま「深さ」だけを増やせる。ループ回数は推論時に選べるため、1 つのチェックポイントで計算量と精度のバランスを変えられる（elastic depth）。

## 詳細

### 通常の Transformer との違い

| | 通常の Transformer | Looped Transformer |
|---|---|---|
| 深さの決まり方 | 層の数 N | ループ回数 k で可変 |
| 重み | 層ごとに別 | 共有ブロックを使い回す |
| パラメータ数 | 深さに比例して増える | k によらず一定 |
| 1 トークンあたりの計算 | 固定 | k に応じて増える |

### 典型的な構成（NVIDIA Dory1.0-4B）

2026 年 11 月の論文「Dory1.0-4B: A Looped Normalized-GPT」（arXiv:2611.03998）の構成。

- **入力ブロック 16 層 → 再帰ブロック 40 層 × k 回 → 出力ブロック 16 層**（物理 72 層）
- 実効的な深さは `32 + 40k` 層（k=1: 72 / k=2: 112 / k=4: 192）。パラメータは約 4B のまま
- 各ループの前に、入力ブロックの出力 x を足し戻して L2 正規化する。何周しても元のトークン表現を参照でき、情報が薄れない

```text
s_0 = x
u_t = N(s_{t-1} + x)
s_t = N(F(u_t))
```

- 学習時はループ回数 k を {1, 2, 3, 4} からサンプリングするため、推論時にどの k でも動く
- 重みは BF16 / MXFP8 / NVFP4 / GGUF で公開（ライセンス OpenMDW-1.1）

### ループ回数と効果

- 12 ベンチマーク平均は k=1 / 2 / 4 で 35.17 / 39.67 / 40.60。k≥2 で Qwen3.5-9B や Gemma 4 26B-A4B を上回る
- 伸びが大きいのはコーディング（SWE-bench Verified 50.3 → 61.8）、エージェント操作、長文脈
- k=4 ではエージェント系タスクの出力トークンが k=1 の 1/1.3〜1/2.5 に減る
- 総計算量の概算（出力トークン数 × 層適用回数）は k=2 で k=1 の 1.03〜1.25 倍。論文は **k=2 をデフォルト**、精度最優先なら k=4 を推奨

### KV キャッシュの扱い

ループのたびに K/V が生まれるため、素直に実装すると再帰ブロックの KV メモリはループ回数に比例して増える。

| 方式 | メモリ | 精度 |
|---|---|---|
| ループごとにキャッシュ（学習時と同じ） | k に比例 | 基準 |
| 最終ループのみキャッシュ | 非ループモデルと同じ | k=4 で最大 2.12 ポイント低下 |

「最終ループのみ」は再帰層ごとにキャッシュを 1 つだけ持って上書きする方式で、再学習なしで使える。

### 限界：知識は増えない

ループで伸びるのは**推論力**（持っている情報から結論を組み立てる力）で、**知識量**ではない。

- 事実知識を測る AA-Omniscience の正答率は、ループ回数によらず約 10% のまま
- 専門知識が要る GPQA Diamond は k=2 で頭打ち

パラメータに入っていない知識は、何周回しても出てこない。

### test-time compute の中での位置づけ

推論時の計算を増やして推論力を上げる方法は 2 系統ある。

- **思考をトークンとして生成する**: 回答前に思考過程のトークンを長く生成する（o シリーズ、Claude の extended thinking、DeepSeek-R1 など）
- **内部で深く計算する（latent reasoning）**: トークンを出さず、1 トークンあたりの計算を深くする（Looped Transformer）

両者は排他ではなく、Dory も思考ありと思考なしの両方の応答で学習されている。

### 推論力の測り方

推論力は基本的に、検証できる最終結果の**正答率**（テストが通るか、答えが合うか）で測る。速度はハードウェアに左右されるため指標にせず、代わりに出力トークン数・ターン数・計算量で効率を見る。正答率には知識やデータ汚染も混ざるので、「推論力が伸びた」と言うには、知識系ベンチマークが動いていないことをセットで示すと説得力が増す。

## 関連ページ

- [Transformer](/blogs/wiki/concepts/transformer/) — ループさせる前の、通常の Transformer の仕組み
- [ニューラルネットワークの基礎](/blogs/wiki/concepts/neural-network-basics/) — Transformer を構成する層（Attention と FFN）の土台
- [Subquadratic Sparse Attention](/blogs/wiki/concepts/subquadratic-attention/) — Attention と KV キャッシュの効率化という別方向のアーキテクチャ改良
- [Kimi K3](/blogs/wiki/tools/kimi-k3/) — 記憶の持ち方を変えて KV キャッシュを減らす別アプローチ
- [ローカル LLM 比較](/blogs/wiki/concepts/local-llm-comparison/) — 比較対象の Qwen3.5 / Gemma 4 系モデル

## ソース記事

- [Looped Transformer とは？ 同じ層を繰り返して 4B モデルを深くする NVIDIA Dory1.0-4B](/blogs/posts/2026/11/looped-transformer-nvidia-dory/) — 2026-11-15
