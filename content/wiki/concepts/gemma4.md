---
title: "Gemma 4"
description: "Google DeepMind が 2026年4月にリリースしたオープンソース LLM シリーズ。Apache 2.0 ライセンスで、エッジ向けから高性能サーバー向けまで4サイズを提供"
date: 2026-04-14
lastmod: 2026-04-14
aliases: ["Gemma4"]
related_posts:
  - "/posts/2026/04/gemma4-api-economy-disruption/"
  - "/posts/2026/04/gemma4-vs-qwen35-local-llm/"
  - "/posts/2026/04/gemma4-31b-abliterated-crack/"
tags: ["Gemma", "オープンソースLLM", "Google", "エッジAI", "MoE"]
---

## 概要

Google DeepMind が 2026年4月にリリースしたオープンソース LLM シリーズ。Apache 2.0 ライセンスで商用利用可能。エッジデバイスからサーバー/ワークステーションまで対応する4サイズ展開で、API 経済の構造に変化をもたらすと注目されている。

## ラインナップ

| モデル | パラメータ | 推論時アクティブ | コンテキスト | 用途 |
|--------|-----------|----------------|------------|------|
| E2B（MoE） | 〜8B | 約2B | 128K | スマートフォン・オフライン |
| E4B（MoE） | 〜16B | 約4B | 128K | エッジデバイス |
| 27B Dense | 27B | 27B | 256K | ミッドレンジサーバー |
| 31B Dense | 31B | 31B | 256K | サーバー/ワークステーション |

E2B モデルはスマートフォン上での完全オフライン動作が可能で、API 従量課金に依存しない自律型 AI の基盤となりうる。

## 主な特徴

- **マルチモーダル対応**: テキスト、画像、音声（モデルにより異なる）
- **Apache 2.0 ライセンス**: 商用利用・改変・再配布が自由
- **Ollama / llama.cpp 対応**: ローカル実行が容易

## Gemma 4 31B vs Qwen3.5-27B

ローカル LLM として競合する Qwen3.5-27B（Alibaba）との比較では、推論・マルチモーダル能力は Gemma 4 が優位、コーディング性能・長文コンテキスト（262K トークン）は Qwen3.5 が優位とされる。

## API 経済への影響

E2B モデルのスマートフォン上オフライン動作は、SaaS の API 従量課金モデルに依存しないアプリケーション開発を可能にする。Google が API 経済の構造そのものに挑戦しているとも解釈される。

## Abliteration（脱獄）モデルの登場

Gemma 4 31B をベースに Abliteration 技術でセーフティを除去した「Gemma-4-31B-JANG_4M-CRACK」が Hugging Face で公開された。知識性能の劣化は MMLU で -2.0% にとどまる一方、有害なリクエストへの対応も可能になっている。AI 安全性の議論において重要な事例となっている。

## 関連ページ

- [Ollama](/blogs/wiki/tools/ollama/) — Gemma 4 のローカル実行環境
- [BitNet](/blogs/wiki/tools/bitnet/) — 同時期のローカル LLM 選択肢

## ソース記事

- [Gemma 4 がAPI経済を破壊する](/blogs/posts/2026/04/gemma4-api-economy-disruption/) — 2026-04-07
- [Gemma 4 31B vs Qwen3.5-27B](/blogs/posts/2026/04/gemma4-vs-qwen35-local-llm/) — 2026-04-07
- [Gemma 4 31B の脱獄モデル「CRACK」登場](/blogs/posts/2026/04/gemma4-31b-abliterated-crack/) — 2026-04-06
