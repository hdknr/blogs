---
title: "ローカルで動くコーディングAI——Gemma 4 12B Coder（Fable 5蒸留版）を試す"
date: 2026-06-16
lastmod: 2026-06-24
slug: "gemma-4-12b-coder-fable5-local"
draft: false
source_url: "https://github.com/hdknr/blogs/issues/1#issuecomment-4714988245"
description: "VRAM 12GB で動く Gemma 4 12B Coder の GGUF 量子化バリアント比較、Ollama / llama.cpp での実行手順、Fable 5 蒸留の仕組みを解説する。"
categories: ["AI/LLM"]
tags: ["Gemma4", "GGUF", "ローカルLLM", "llama.cpp", "ollama"]
---

## Gemma 4 12B Coder（Fable 5蒸留版）とは

コンシューマー向け GPU でフロンティアモデル級のコーディング能力をオフラインで動かせる——そんなモデルが登場した。**Gemma 4 12B Coder（Fable 5 / Composer 2.5 蒸留版）**だ。

Google の Gemma 4 12B をベースに、Anthropic の Fable 5 と Composer 2.5 の推論トレース（Chain-of-Thought）を蒸留してファインチューニングされている。12GB の VRAM があれば推奨量子化（Q4_K_M）で動き、クラウドも API キーも不要なプライベート・コーディングアシスタントとして使える。

## Fable 5 の推論能力を 12B モデルに蒸留する仕組み

### 知識蒸留とは

このモデルの核心は**知識蒸留（Knowledge Distillation）**だ。大規模モデルの出力を教師データとして小規模モデルに学習させる手法で、Fable 5 や Composer 2.5 が Python コーディングタスクを解いた際の推論チェーンだけを学習データとして使用する。さらに、実際のテストを通過したコードのみを採用することで、**「考え方が正しく、コードも動く」サンプルだけ**が訓練データになっている。

フロンティアモデルの思考プロセスを 12B のコンパクトな重みに「焼き付ける」ことで、巨大なモデルに頼らずとも高品質な推論を実現している。

### ベースモデル：Gemma 4 12B

Google DeepMind が開発した Gemma 4 12B は、以下の特徴を持つ。

- **256K トークン**のコンテキストウィンドウ
- テキスト・画像・音声・動画のマルチモーダル入力
- エンコーダーレスアーキテクチャ（全モダリティが単一 Transformer に直接流入）
- Apache 2.0 ライセンス

コーディング特化モデルはこの Gemma 4 12B-it（インストラクションチューニング済み）を起点にしている。

## Hugging Face からの GGUF ダウンロード方法

Hugging Face の `yuxinlu1/gemma-4-12B-coder-fable5-composer2.5-v1-GGUF` リポジトリから量子化済みファイルをダウンロードできる。

### 量子化バリアントと必要 VRAM

| 量子化 | ファイルサイズ | 最低 VRAM 目安 |
|--------|-------------|--------------|
| Q2_K   | 4.5 GB      | 8 GB         |
| Q3_K_M | 5.7 GB      | 8 GB         |
| Q4_K_M | 6.87 GB     | **12 GB（推奨）** |
| Q6_K   | 9.11 GB     | 16 GB        |
| Q8_0   | 11.8 GB     | 16 GB        |

8 GB GPU なら Q2_K または Q3_K_M で動き、12 GB なら推奨の Q4_K_M が選べる。量子化が高いほど精度は元モデルに近づく。

### コンテキスト長の目安（VRAM 別）

| VRAM   | 量子化  | 実用的なコンテキスト長 |
|--------|---------|----------------------|
| 8 GB   | Q2_K    | 〜16K トークン        |
| 12 GB  | Q4_K_M  | 〜30K トークン        |
| 16 GB  | Q4_K_M  | 〜64K トークン        |
| 24 GB+ | Q4_K_M  | 256K トークン（最大）  |

## Ollama / llama.cpp / LM Studio での実行手順

### Ollama で使う（最も手軽）

```bash
ollama run xentriom/gemma-4-12B-coder-fable5-composer2.5-v1
```

初回実行時に自動でモデルがダウンロードされる。インストール方法は [ollama.com](https://ollama.com) を参照。

### llama.cpp のサーバーモードで使う

[llama.cpp](https://github.com/ggerganov/llama.cpp) をビルドした後、以下のコマンドでサーバーを起動する。

```bash
llama-server \
  --model gemma-4-12B-coder-fable5-composer2.5-v1-Q4_K_M.gguf \
  --n-gpu-layers 99 \
  --ctx-size 32768 \
  --port 18080
```

起動後は `http://localhost:18080` で Web UI が利用できる。`--n-gpu-layers 99` で GPU に全レイヤーをオフロードし、`--ctx-size` でコンテキスト長を調整する。

### GUI アプリで使う

- **LM Studio**：モデルを検索してワンクリックで読み込める
- **Jan**：OpenAI 互換 API として他ツールから呼び出せる

## 使いどころ

このモデルが特に力を発揮する場面は以下だ。

- **オフライン環境**でのコーディング支援（社内ネットワーク、飛行機内など）
- **プライバシーを重視**するプロジェクト（コードを外部 API に送りたくない場合）
- **長いコンテキスト**が必要なタスク（大きなファイルを丸ごと渡して変更を依頼するなど）
- **デバッグや複雑なアルゴリズム**の生成（Fable 5 の推論品質が活きる）

## コミュニティの反応

Hugging Face でのダウンロード数は公開直後から 6,000 を超え、v2 もリリース済みだ（v2 GGUF は `yuxinlu1/gemma-4-12B-agentic-fable5-composer2.5-v2-3.5x-tau2-GGUF` として公開）。v2 ではエージェント能力がさらに強化されている。

## まとめ

フロンティアモデルの推論能力を蒸留することで、コンシューマー機材で動く高品質なコーディングアシスタントを実現した好例だ。クラウド API の料金や情報漏洩リスクを気にせずに、Fable 5 クラスの推論トレースで訓練されたモデルをローカルで使えるのは魅力的だ。

12 GB GPU を持つ開発者なら今すぐ試せる。まずは Ollama でワンコマンド実行してみるのが一番手軽だろう。

## 参考リンク

- [yuxinlu1/gemma-4-12B-coder-fable5-composer2.5-v1-GGUF — Hugging Face](https://huggingface.co/yuxinlu1/gemma-4-12B-coder-fable5-composer2.5-v1-GGUF)
- [Ollama: xentriom/gemma-4-12B-coder-fable5-composer2.5-v1](https://ollama.com/xentriom/gemma-4-12B-coder-fable5-composer2.5-v1)
- [Gemma 4 model overview — Google AI for Developers](https://ai.google.dev/gemma/docs/core)
- [Welcome Gemma 4: Frontier multimodal intelligence on device — Hugging Face Blog](https://huggingface.co/blog/gemma4)
