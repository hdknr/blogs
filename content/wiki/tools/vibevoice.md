---
title: "VibeVoice"
description: "Microsoft が公開する OSS の音声 AI ファミリー（ASR・TTS・リアルタイム TTS）"
date: 2026-04-29
lastmod: 2026-04-29
aliases: ["microsoft vibevoice", "vibevoice-asr", "vibevoice-tts"]
related_posts:
  - "/posts/2026/04/2026-04-29-vibevoice-microsoft-voice-ai/"
tags: ["microsoft", "音声認識", "音声合成", "asr", "tts", "oss"]
---

## 概要

VibeVoice は Microsoft Research が公開している OSS の音声 AI モデルファミリーで、長尺音声の文字起こし（ASR）と音声合成（TTS）を統合的に扱える。中核は **7.5 Hz の超低フレームレート連続音声トークナイザー** + Qwen2.5 1.5B ベースの **next-token diffusion** フレームワーク。

GitHub リポジトリ: [microsoft/VibeVoice](https://github.com/microsoft/VibeVoice)

## モデル構成（2026-04-29 時点）

| モデル | パラメータ | 用途 | 状態 |
|---|---|---|---|
| **VibeVoice-ASR-7B** | 7B | 60分1パスの長尺音声認識（話者識別＋タイムスタンプ＋50言語＋ホットワード対応） | ✅ 利用可 |
| **VibeVoice-Realtime-0.5B** | 0.5B | 約300ms レイテンシのストリーミング TTS（9 言語ボイス） | ✅ 利用可 |
| VibeVoice-TTS-1.5B | 1.5B | 90分・最大4話者の長尺 TTS | ⚠️ 2025-09-05 にコード削除（悪用報告のため） |

ASR は 64K トークン長で **60 分の連続音声を 1 パスで処理**でき、Who（話者）/ When（タイムスタンプ）/ What（内容）の構造化出力に対応する。

## 特徴

- **構造化トランスクリプト**: ASR + ダイアライゼーション + タイムスタンプを同時実行
- **カスタムホットワード**: 固有名詞・専門用語を事前指定して認識精度を向上
- **vLLM 高速推論**: PyTorch / Transformers 統合に加え vLLM 経由の推論にも対応
- **多言語**: ASR は 50 言語以上、Realtime TTS は 9 言語ボイス（日本語含む）
- **Hugging Face Transformers 統合**: 2026-03-06 リリースで `transformers` ライブラリから直接呼び出せる

## 利用形態

**実装言語**: Python 100%（公式バインディングなし）

**推奨デプロイ**: サーバ側 GPU で推論し、クライアント（iPad/iPhone/Web）は録音・再生・UI に専念する。iPadOS / iOS では Python ランタイムも CUDA も使えないため、端末上でモデルを直接動かすのは現実的でない。

## 注意点

- **TTS-1.5B のコード削除**: ディープフェイク等の悪用報告を受けて Microsoft が同モデルのコードをリポジトリから削除している。長尺マルチ話者 TTS は現状利用不可
- **責任ある AI**: ベースモデル（Qwen2.5 1.5B）由来のバイアスを継承。生成音声のディープフェイク悪用リスクに留意

## 関連ページ

- [Qwen](/blogs/wiki/tools/qwen/) — VibeVoice のベース LLM
- [vLLM](https://github.com/vllm-project/vllm) — 推論バックエンド

## ソース記事

- [Microsoft VibeVoice 徹底解説](/blogs/posts/2026/04/2026-04-29-vibevoice-microsoft-voice-ai/) — 2026-04-29
