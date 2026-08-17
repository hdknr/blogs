---
title: "ローカルLLM比較（2026年春）"
description: "2026年春時点のローカル実行可能LLMの比較。Gemma 4、Qwen3.5、BitNetの特性とユースケース別の選び方"
date: 2026-04-15
lastmod: 2026-08-05
aliases: ["ローカルLLM", "local-llm", "オープンソースLLM比較"]
related_posts:
  - "/posts/2026/04/gemma4-vs-qwen35-local-llm/"
  - "/posts/2026/04/microsoft-bitnet-open-source-1bit-llm/"
  - "/posts/2026/04/gemma4-api-economy-disruption/"
  - "/posts/2026/04/claude-rate-limit-mac-mini-local-model/"
  - "/posts/2026/08/local-model-delegation-dev-loop/"
  - "/posts/2026/08/kimi-k3-memory-architecture/"
tags: ["ローカルLLM", "Gemma", "qwen", "BitNet", "オープンソースLLM", "Apple Silicon"]
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

## Claude レート制限フォールバック構成

Claude Max のレート制限（$200/月で3時間で消費する事例あり）への対策として、Mac Mini + ローカルモデルの組み合わせが有効。

- **Mac Mini（Apple Silicon）** に複数の量子化モデルを配置（例: 5モデル、合計約 350 億パラメーター）
- Claude がレート制限に達したら自動でローカルモデルへフォールバック
- 用途：メール整理・コンテキスト圧縮・深夜バッチ処理など
- コスト比較：同等業務を3人のエンジニア月 $15,000 → Mac Mini 一台 $599 + ローカルモデル

## API 経済への影響

Gemma 4 の Apache 2.0 ライセンスと E2B モデルのスマートフォンオフライン動作は、SaaS の API 従量課金構造を変える可能性がある:

- 自社サーバーで Gemma 4 を稼働させることで、外部 API コストを固定インフラコストに変換できる
- E2B モデルはスマートフォン上で 1.5GB 未満のメモリで動作し、API 呼び出しゼロのオフライン AI アプリが実現可能
- BitNet はさらに一歩進み、CPU だけで 100B 規模のモデルを動作させるアーキテクチャを提供

## 何をローカルモデルに委譲するか

開発ループの一部をローカルの小さいモデル（27B クラス）に振るとき、節約の成否は「どのモデルが安いか」ではなく **その工程が高ボリューム・低判断かどうか**の一点に収束する。

- **subagent 単位で振り分ける機構はない** — ツール化するのが本命
- **生データがモデルの文脈に入った時点で節約は消える** — スクリプトがファイルを直接読む形にする
- **モデルを使わない選択肢を先に潰す** — grep で済む判定に安いモデルを使うのは横滑り
- **判定・敵対的レビュー・pass/fail は手放さない** — 委譲してよいのは証拠の圧縮であって、証拠からの結論ではない
- **速度改善は期待しない** — 得られるのはコストとデータの局所性

「安そうな工程」という直感は当たらない。なお haiku ティアを使えば 0 インフラで同じ分担が組める場合がある。

## 関連ページ

- [Gemma 4](/blogs/wiki/concepts/gemma4/) — Google DeepMind のオープンソース LLM 詳細
- [Qwen](/blogs/wiki/tools/qwen/) — Alibaba のオープンソース LLM 詳細
- [BitNet](/blogs/wiki/tools/bitnet/) — Microsoft の 1-bit LLM 詳細
- [Ollama](/blogs/wiki/tools/ollama/) — ローカル LLM 実行環境
- [Kimi K3](/blogs/wiki/tools/kimi-k3/) — 記憶設計から見る大規模モデル
- [ループエンジニアリング](/blogs/wiki/concepts/loop-engineering/) — 反復工程をどのモデルに振るかの設計

## ソース記事

- [Gemma 4 31B vs Qwen3.5-27B — ローカルLLM最強はどちらか](/blogs/posts/2026/04/gemma4-vs-qwen35-local-llm/) — 2026-04-07
- [Microsoft BitNet 完全オープンソース化：GPUなしで1000億パラメータLLMをCPUで動かす時代へ](/blogs/posts/2026/04/microsoft-bitnet-open-source-1bit-llm/) — 2026-04-07
- [Gemma 4 が API 経済を破壊する](/blogs/posts/2026/04/gemma4-api-economy-disruption/) — 2026-04-07
- [Claude のレート制限対策に Mac Mini とローカルモデルを活用する](/blogs/posts/2026/04/claude-rate-limit-mac-mini-local-model/) — 2026-04-15
- [ローカルモデルに何を任せるか — Claude Code の開発ループに小さいモデルを混ぜる設計](/blogs/posts/2026/08/local-model-delegation-dev-loop/) — 2026-08-03（委譲は「高ボリューム・低判断」に限る）
- [Kimi K3 は2.8兆パラメータより「忘れ方」が新しい](/blogs/posts/2026/08/kimi-k3-memory-architecture/) — 2026-08-03
