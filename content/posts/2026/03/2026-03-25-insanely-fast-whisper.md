---
title: "insanely-fast-whisper: 150分の音声を98秒で文字起こしする CLI ツール"
date: 2026-03-25
lastmod: 2026-03-25
draft: false
description: "OpenAI Whisper をベースに Flash Attention 2 とバッチ処理で高速化した文字起こし CLI ツール insanely-fast-whisper の紹介。150分の音声を98秒で処理できる。"
source_url: "https://github.com/hdknr/blogs/issues/1#issuecomment-4129395791"
categories: ["AI/LLM"]
tags: ["openai", "python", "llm"]
---

音声の文字起こし（トランスクリプション）は AI の実用的な応用の一つだが、長時間の音声ファイルを処理するには時間がかかる。[insanely-fast-whisper](https://github.com/Vaibhavs10/insanely-fast-whisper) は、OpenAI の Whisper モデルを Flash Attention 2 とバッチ処理で高速化し、150分の音声をわずか98秒で文字起こしできる CLI ツールだ。

## 概要

insanely-fast-whisper は、Hugging Face の Transformers、Optimum、flash-attn を組み合わせた文字起こし CLI だ。2026年3月時点で GitHub スター 11,000 以上を獲得しており、コミュニティ主導で開発が進んでいる。

主な特徴:

- **高速処理**: Nvidia A100 GPU で 150分の音声を約98秒で文字起こし
- **簡単なインストール**: `pipx install` でワンコマンド導入
- **複数モデル対応**: Whisper large-v3、distil-whisper など
- **Mac 対応**: Apple Silicon (MPS) でも動作
- **翻訳機能**: 文字起こしだけでなく、英語への翻訳も可能

## ベンチマーク

Nvidia A100 (80GB) での 150分音声の処理時間比較:

| 構成 | 処理時間 |
|---|---|
| large-v3 (fp32) | 約31分 |
| large-v3 (fp16 + batching + BetterTransformer) | 約5分 |
| **large-v3 (fp16 + batching + Flash Attention 2)** | **約1分38秒** |
| distil-large-v2 (fp16 + batching + BetterTransformer) | 約3分16秒 |
| **distil-large-v2 (fp16 + batching + Flash Attention 2)** | **約1分18秒** |
| large-v2 (Faster Whisper, fp16) | 約9分23秒 |

Flash Attention 2 の効果が顕著で、BetterTransformer と比較しても約2.5〜3倍の高速化を実現している。

## インストールと使い方

### インストール

```bash
pipx install insanely-fast-whisper
```

`pipx` がない場合は先にインストールする:

```bash
pip install pipx
# または
brew install pipx
```

### 基本的な使い方

```bash
insanely-fast-whisper --file-name <音声ファイルのパスまたは URL>
```

### Flash Attention 2 を有効にする

```bash
insanely-fast-whisper --file-name <音声ファイル> --flash True
```

### Mac で使う場合

Apple Silicon Mac ではデバイスに MPS を指定する:

```bash
insanely-fast-whisper --file-name <音声ファイル> --device-id mps
```

### distil-whisper モデルを使う

より軽量な distil-whisper を使いたい場合:

```bash
insanely-fast-whisper --model-name distil-whisper/large-v2 --file-name <音声ファイル>
```

### インストールせずに実行

`pipx run` を使えばインストール不要で実行できる:

```bash
pipx run insanely-fast-whisper --file-name <音声ファイル>
```

## 主要な CLI オプション

| オプション | 説明 | デフォルト |
|---|---|---|
| `--file-name` | 音声ファイルのパスまたは URL | (必須) |
| `--device-id` | GPU デバイス ID（Mac は `mps`） | `0` |
| `--model-name` | 使用するモデル名 | `openai/whisper-large-v3` |
| `--task` | `transcribe`（文字起こし）または `translate`（翻訳） | `transcribe` |
| `--language` | 入力音声の言語 | 自動検出 |
| `--batch-size` | 並列バッチ数（OOM 時は減らす） | `24` |
| `--flash` | Flash Attention 2 の有効化 | `False` |
| `--transcript-path` | 出力ファイルのパス | `output.json` |

## 高速化の仕組み

insanely-fast-whisper の高速化は主に3つの技術に支えられている:

1. **Flash Attention 2**: メモリアクセスパターンを最適化した注意機構の実装。GPU のメモリ帯域幅を効率的に活用する
2. **バッチ処理**: 音声をチャンクに分割し、複数チャンクを同時に処理する。デフォルトのバッチサイズは 24
3. **fp16（半精度浮動小数点）**: 計算精度を 32bit から 16bit に切り替えることで、処理速度を向上させる

## 動作要件

- **GPU**: NVIDIA GPU（CUDA 対応）または Apple Silicon Mac（MPS）
- **Python**: 3.10 以上推奨（3.11 では `pipx` のバージョン解析に問題がある場合あり）
- **Flash Attention 2**: NVIDIA GPU のみ対応（Ampere 以降推奨）

## まとめ

insanely-fast-whisper は、Whisper の文字起こし性能を Flash Attention 2 で劇的に高速化するツールだ。CLI 一つで導入でき、長時間の音声ファイルも数分以内で処理できる。議事録作成、ポッドキャストの書き起こし、動画の字幕生成など、音声データを扱う場面で活用できるだろう。
