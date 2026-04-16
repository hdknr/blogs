---
title: "Gemma 4"
description: "Google DeepMind が開発したオープンソース LLM シリーズ。Apache 2.0 ライセンスで商用利用可能。26B MoE はアクティブパラメータ約 3.8B、E2B はスマートフォンで動作する"
date: 2026-04-07
lastmod: 2026-04-16
aliases: ["Gemma4", "gemma-4"]
related_posts:
  - "/posts/2026/04/gemma4-api-economy-disruption/"
  - "/posts/2026/04/gemma4-vs-qwen35-local-llm/"
  - "/posts/2026/04/gemma4-31b-abliterated-crack/"
tags: ["Gemma", "Google", "オープンソースLLM", "MoE", "エッジAI", "Apache2.0"]
---

## 概要

Google DeepMind が 2026年4月にリリースした LLM シリーズ。Apache 2.0 ライセンスで商用利用に制限がなく、31B Dense から E2B（スマートフォン動作）まで4バリアントを提供。特に 26B MoE は総パラメータ数は 26B だが推論時アクティブは約 3.8B にとどまるため、一般的な GPU で実用的に動作する。

## モデルラインナップ

| モデル | パラメータ | 推論時アクティブ | コンテキスト | 主な用途 |
|--------|-----------|----------------|------------|------|
| **31B Dense** | 31B | 31B | 256K | サーバー/ワークステーション |
| **26B MoE** | 26B | 約 3.8B | 256K | サーバー/ワークステーション |
| **E4B** | — | 約 4B | 128K | エッジデバイス |
| **E2B** | — | 約 2.3B | 128K | スマートフォン |

## 主な特徴

- **Apache 2.0 ライセンス**: 商用利用・改変・再配布が自由
- **ネイティブ Function Calling**: ツール呼び出しをモデルが意味的に理解
- **構造化 JSON 出力**: API レスポンス向けの JSON 出力をネイティブサポート
- **256K コンテキスト**: 長文書の処理やコードベース全体の分析に対応
- **140+ 言語対応**: 日本語を含む多言語をサポート

## API 経済へのインパクト

Gemma 4 は外部 LLM API に依存する SaaS のコスト構造を変える可能性を持つ。

```text
従来: ユーザーリクエスト → 自社サーバー → OpenAI/Anthropic API（リクエストごと課金）
Gemma 4: ユーザーリクエスト → 自社サーバー（Gemma 4 稼働）→ インフラ固定費のみ
```

E2B モデルは量子化により 1.5GB 未満のメモリで動作し、スマートフォン上でオフライン推論が可能。API 呼び出しゼロのオフライン AI アプリが商用レベルで実現できる。

## Qwen3.5-27B との比較

| 観点 | Gemma 4 31B | Qwen3.5-27B |
|------|-------------|-------------|
| 推論・数学 | AIME 89.2%（優位） | — |
| コーディング | — | SWE-bench 72.4%（優位） |
| メモリ（Q4） | 約 19GB | 約 16.7GB（効率的） |
| マルチモーダル | テキスト・画像・音声 | テキスト・画像・音声・動画 |
| MLX 対応 | vMLX 必要 | mlx-community で充実 |

推論・数学・マルチモーダルには Gemma 4、コーディング・メモリ効率・MLX エコシステムには Qwen3.5 が向いている。

## Abliteration（安全性除去）モデル

Gemma 4 31B をベースに安全性制限を除去した「CRACK」モデルが Hugging Face で公開されている。

- **手法**: Abliteration（拒否方向の特定と重みの直交化）
- **量子化**: JANG_4M プロファイル（Attention=8bit、MLP=4bit）で 18GB に圧縮
- **性能劣化**: MMLU で -2.0%（74.5% vs 76.5%）にとどまる
- **HarmBench**: 93.7% のコンプライアンス率

詳細は [Abliteration](/blogs/wiki/concepts/abliteration/) を参照。

## ローカル実行

```bash
# Ollama で実行
ollama run gemma4:31b
```

Apple Silicon では標準の mlx_lm は未対応（2026年4月時点）。[vMLX](https://vmlx.net) を使う必要がある。

## 関連ページ

- [Ollama](/blogs/wiki/tools/ollama/) — ローカル LLM 実行環境
- [Qwen](/blogs/wiki/tools/qwen/) — Alibaba のオープンソース LLM（比較対象）
- [BitNet](/blogs/wiki/tools/bitnet/) — Microsoft の 1-bit LLM（別アプローチのエッジ AI）
- [ローカル LLM 比較](/blogs/wiki/concepts/local-llm-comparison/) — ローカル LLM の選択ガイド
- [Abliteration](/blogs/wiki/concepts/abliteration/) — LLM の安全性制限を除去する技術

## ソース記事

- [Gemma 4 がAPI経済を破壊する — オープンモデルがSaaS課金モデルを変える理由](/blogs/posts/2026/04/gemma4-api-economy-disruption/) — 2026-04-07
- [Gemma 4 31B vs Qwen3.5-27B — ローカルLLM最強はどちらか](/blogs/posts/2026/04/gemma4-vs-qwen35-local-llm/) — 2026-04-07
- [Gemma 4 31B の脱獄モデル「CRACK」登場 — Abliteration 技術でセーフティを除去](/blogs/posts/2026/04/gemma4-31b-abliterated-crack/) — 2026-04-06
