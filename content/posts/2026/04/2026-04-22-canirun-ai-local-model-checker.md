---
title: "CanIRun.ai — ブラウザだけで自分のPCがどのローカルAIを動かせるか即判定"
date: 2026-04-22
lastmod: 2026-04-22
draft: false
source_url: "https://github.com/hdknr/blogs/issues/1#issuecomment-4304017679"
categories: ["AI/LLM"]
tags: ["ローカルLLM", "VRAM", "WebGPU", "CanIRun.ai", "LM Studio"]
---

「自分のPCでローカルAIを動かしたい、でもどのモデルが動くか分からない」。そんな悩みを一発で解決してくれる Web サービスが **[CanIRun.ai](https://canirun.ai)** だ。インストール不要、登録不要で、サイトにアクセスするだけでハードウェアを自動検出し、数百のモデルに対して動作可否を判定してくれる。

## 何ができるのか

CanIRun.ai は、ブラウザの **WebGPU API** を使って以下のハードウェア情報を自動取得する。

- GPU の種類と VRAM 容量（GPU 名を WebGPU/WebGL で取得し、内部 DB から VRAM を割り出す）
- GPU メモリ帯域幅（内部スペックシート DB から参照）
- システム RAM
- CPU コア数

取得した情報をもとに、カタログに登録された全モデルとの適合性を即座に算出する。

## 6 段階の互換性評価

各モデルに対して、**S〜F の 6 段階グレード** が色分けで表示される。

| グレード | ラベル | 意味 |
|----------|--------|------|
| **S** | Runs great | 余裕で動作 |
| **A** | Runs well | 快適に動作 |
| **B** | Decent | まずまず動作 |
| **C** | Tight fit | ギリギリ動作 |
| **D** | Barely runs | かろうじて動作 |
| **F** | Too heavy | 動作不可 |

グレードに加え、アーキテクチャの種類・コンテキストウィンドウサイズ・量子化レベル（Q2_K〜F16 といった精度とサイズのトレードオフを示すレベル）ごとのメモリ要件など、詳細な技術情報も確認できる。

## 対応モデルの幅広さ

カタログは **1GB 未満の軽量モデルから数百 GB の巨大モデルまで** 網羅している。

**軽量モデル（〜数 GB）**
- Qwen 3 0.6B
- Llama 3.2 1B
- Gemma 3 1B

**中規模モデル（8〜70B クラス）**
- Llama 3.1 8B
- Mistral Nemo 12B
- Qwen 2.5 32B
- Llama 3.3 70B

**大規模・MoE モデル**
- DeepSeek R1 671B
- DeepSeek V3.2 685B
- Kimi K2 1T

モデルはタスク種別（チャット・コード・ビジョン・推論）、プロバイダー、ライセンス、性能指標でフィルタリングできる。データソースは [llama.cpp](https://github.com/ggml-org/llama.cpp)、[Ollama](https://ollama.com)、[LM Studio](https://lmstudio.ai) から取得している。

## 使い方まとめ

1. [https://canirun.ai](https://canirun.ai) にアクセス（Chrome など WebGPU 対応ブラウザを推奨）
2. ハードウェア情報が自動検出される
3. モデル一覧に S〜F のグレードが表示される
4. タスクやプロバイダーで絞り込んで目当てのモデルを探す

## 注意点

WebGPU API はブラウザから取得できる情報に限界があるため、検出結果が正確でない場合がある。特に以下のケースでは実際のスペックと若干ずれることがある。

- VRAM と RAM を共有する **ノート PC の統合グラフィックス**
- VRAM と RAM を統合した **Apple Silicon（M シリーズ）**

ローカル LLM を試したいが「何が動くか分からない」という段階で詰まっている人には、CanIRun.ai が最初の一歩として有効なツールだろう。
