---
title: "Gemma 4 31Bの脱獄モデル「CRACK」登場 — Abliteration技術でセーフティを除去"
date: 2026-04-06
lastmod: 2026-04-06
draft: false
source_url: "https://github.com/hdknr/blogs/issues/1#issuecomment-4194462489"
categories: ["AI/LLM"]
description: "Google Gemma 4 31Bの安全性制限を除去した脱獄モデルCRACKの技術解説。Abliteration手法の仕組み、JANG_4M量子化で18GBに収めたスペック、HarmBenchとMMLUのベンチマーク結果を紹介。"
tags: ["Gemma", "Abliteration", "MLX", "Apple Silicon", "AI安全性"]
---

Google の Gemma 4 31B モデルをベースに、安全性制限を除去した「**Gemma-4-31B-JANG_4M-CRACK**」が [Hugging Face で公開](https://huggingface.co/dealignai/Gemma-4-31B-JANG_4M-CRACK)された。開発元の dealignai は、**Abliteration**（アブリテレーション）と呼ばれる手法でモデルの拒否行動を除去した。知識性能の劣化は MMLU で **-2.0%** にとどまる。

## Abliteration とは何か

Abliteration は、LLM の学習済み拒否メカニズムを**再学習なし**で除去する手法だ。2024年頃から研究が進み、現在では複数のバリエーションが存在する。

基本的な仕組みは以下の通り:

1. **拒否方向の特定**: 有害なプロンプトと無害なプロンプトをモデルに入力し、残差ストリーム（Transformer 内部の中間表現が流れる経路）の活性化を記録する。両者の平均差分ベクトルが「拒否方向」（refusal direction）となる
2. **重み直交化**: 特定した拒否方向に対してモデルの重み行列を直交化（orthogonalization）する。直感的には、拒否方向の成分を重みから差し引く操作にあたる。これにより、モデルはその方向への活性化を生成できなくなる
3. **性能保持**: 拒否方向のみをターゲットにするため、モデルの汎用的な知識や推論能力への影響は最小限に抑えられる

最近の改良版である **Norm-Preserving Biprojected Abliteration** では、ベクトルのノルムを保持しながら除去を行うことで、さらに性能劣化を抑えている。

## CRACK モデルのスペック

| 項目 | 値 |
|------|-----|
| ベースモデル | `google/gemma-4-31b-it` |
| アーキテクチャ | Dense Transformer + Hybrid Sliding/Global Attention |
| 量子化プロファイル | JANG_4M（CRITICAL=8-bit, COMPRESS=4-bit） |
| 平均ビット数 | 5.1 bits |
| モデルサイズ | **18 GB** |
| ビジョン | マルチモーダル対応（ビジョンエンコーダは量子化せず float16 を維持） |
| フォーマット | JANG v2（MLX ネイティブ safetensors） |

### JANG_4M のビット割り当て

JANG プロファイルの特徴は、アテンション層とMLP層で異なるビット精度を割り当てる点にある:

- **CRITICAL（8-bit）**: Attention の Q/K/V/O 重み、エンベディング
- **COMPRESS（4-bit）**: MLP の gate/up/down projection、その他の重み

Dense モデルは MLP 部分の量子化耐性が高いため、この戦略により 18GB という実用的なサイズを実現している。

## ベンチマーク結果

### HarmBench（159 プロンプト）

全体で **93.7% のコンプライアンス率**（有害プロンプトに対して拒否せず応答した割合、149/159）を記録:

| カテゴリ | スコア |
|---------|--------|
| サイバー犯罪/侵入 | 33/33（100%） |
| 違法行為 | 46/47（98%） |
| 偽情報 | 26/27（96%） |
| 化学/生物 | 18/19（95%） |
| 有害コンテンツ | 16/17（94%） |
| ハラスメント | 10/16（62%） |

### MMLU（200問、10科目）

CRACK 版のスコアは **74.5%**（149/200）で、量子化のみの JANG_4M 版（76.5%）と比較して **-2.0%** の劣化にとどまる。

## 動作環境

- **Apple Silicon Mac**（24GB 以上のユニファイドメモリ）
- [vMLX](https://vmlx.net) 1.3.26 以上が推奨
- 標準の `mlx_lm` や `mlx_vlm` は 2026年4月時点では Gemma 4 に未対応（mlx_lm v0.31.2 / mlx_vlm v0.4.1）

```python
# vMLX での利用（推奨）
# vMLX アプリまたは API 経由で直接ロード

# 手動で MLX ロードする場合
from mlx_vlm.models.gemma4 import Model
# mlx_vlm の gemma4 対応版（vMLX バンドル版）が必要
```

## AI 安全性の観点から

Abliteration 技術の登場は、LLM の安全性設計における重要な論点を提起している:

- **安全性アラインメントの脆弱性**: 重みの線形操作だけで拒否行動を除去できる。これは現在の RLHF/RLAIF ベースの安全性対策が根本的に脆弱であることを意味する
- **オープンモデルのジレンマ**: モデルの重みが公開されている以上、Abliteration のような手法を完全に防ぐことは原理的に困難
- **研究の透明性**: dealignai は「AI 安全性の理解を深めるため」として研究を公開しており、攻撃と防御の両面での知見蓄積に貢献している

## 関連リソース

- [Hugging Face モデルカード](https://huggingface.co/dealignai/Gemma-4-31B-JANG_4M-CRACK)
- [Abliteration 解説記事（Maxime Labonne）](https://huggingface.co/blog/mlabonne/abliteration)
- [Norm-Preserving Biprojected Abliteration](https://huggingface.co/blog/grimjim/norm-preserving-biprojected-abliteration)
- [Gemma 4 公式ブログ](https://blog.google/innovation-and-ai/technology/developers-tools/gemma-4/)
