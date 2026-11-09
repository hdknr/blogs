---
title: "NVIDIA RE-USE"
description: "NVIDIA の 9.6M パラメータの多言語ユニバーサル音声強調モデル。雑音・残響・コーデック歪みなどを除き、話者の声質を保ったまま文字起こし精度を上げる前処理に使える"
date: 2026-11-09
lastmod: 2026-11-09
aliases: ["RE-USE", "NemotronLabs RE-USE", "NVIDIA-NemotronLabs-RE-USE", "音声強調", "Universal Speech Enhancement"]
related_posts:
  - "/posts/2026/11/nvidia-re-use-speech-enhancement/"
tags: ["NVIDIA", "huggingface", "音声認識", "文字起こし", "オープンソース"]
---

## 概要

NemotronLabs RE-USE は、NVIDIA の研究チームによる**多言語ユニバーサル音声強調**（Universal Speech Enhancement, USE）モデル。パラメータ数は 9.6M と小さく、録音の劣化をまとめて取り除いて話し声を聞き取りやすくする。

STT（Speech-to-Text）のモデルを替えずに、その前段に挟んで入力音声をきれいにする用途に向く。モデルカードのベンチマークでは、前処理に挟むだけで ASR の文字正解率が 81.3% から 89.2% に上がっている。

## 詳細

### 特徴

- **多様な劣化に対応**: 加算性ノイズ、残響、クリッピング、帯域制限、コーデック歪み、パケットロス、低品質マイクの歪み
- **複数のサンプリングレート**: 8〜48 kHz（8 / 16 / 22.05 / 24 / 32 / 44.1 / 48 kHz）のモノラル入力
- **言語非依存を狙う**: 学習データは英・独・西・仏・中だが、言語に依存しない処理を目指す
- **主話者を優先**: 声が重なると主話者を残し他の話者を抑える
- **構成**: 畳み込みエンコーダ／デコーダの間に双方向 Mamba（状態空間モデル）を 30 層。学習データは LibriTTS・VCTK・Common Voice などに DNS5 のノイズとシミュレーションした残響を合成した約 2,500 時間

### ベンチマーク（URGENT 2025 非ブラインドテスト、モデルカードより）

| モデル | パラメータ数 | PESQ | STOI | 話者類似度 | ASR 文字正解率（%） |
|---|---:|---:|---:|---:|---:|
| 処理なし | - | 1.34 | 0.50 | 0.73 | 81.29 |
| Sidon | 250M | 1.73 | 0.62 | 0.74 | 84.68 |
| UniPASE | 500M | 2.17 | 0.76 | 0.81 | 87.28 |
| RE-USE | 9.6M | 2.57 | 0.78 | 0.86 | 89.17 |

- **話者類似度 0.86** は比較対象で最高。ノイズ除去で声質まで変わるモデルが多い中、「声色が変わらない」という体感と一致する
- ASR は OWSM v3.1 で測定
- 一方、聞いた感じの自然さを推定する DNSMOS・UTMOS では 250M の Sidon が上回る。全指標で勝っているわけではない

### 文字起こしパイプラインでの使い方

ボイスレコーダーや指輪型レコーダー（Core Devices の Index 01 など）で録った劣化音声を RE-USE に通し、その出力を Whisper などの STT に渡す。STT 側に手を入れず、STT を替えても前処理の 1 段はそのまま使える。

### 動かし方と制約

- **まずは Gradio デモ**: Hugging Face の Space に自分の録音を上げて効果を確かめるのが早い
- **公式の動作環境は Linux + NVIDIA GPU**（A100）: コードは `mamba-ssm` を直接 import し、推論スクリプトは CUDA がないと `Currently, CPU mode is not supported.` で止まる。環境構築は SEMamba リポジトリの Docker が案内されている。Mac で動いたという報告はあるが方法は公開されていない
- **実行**: `huggingface-cli download` でモデル一式を取得し、`noisy_audio/` に置いて `sh inference.sh`（出力は `enhanced_audio/` に `.flac`）。ステレオは ffmpeg でモノラルにしておく。帯域拡張には `resampy` が要る
- **長い音声**: 学習データは 10 秒未満のクリップ。30 秒を超える音声や GPU メモリ不足には `long_noisy_audio/` に置いて `sh inference_chunk.sh`。出力先はモデルカードの表記と違い小文字の `long_enhanced_audio/`

### ライセンス

Hugging Face には 2 つのリポジトリがある。先行版の `nvidia/RE-USE` は独自ライセンス（`other`）。`nvidia/NVIDIA-NemotronLabs-RE-USE` は OpenMDW-1.1 で、モデルカードに「商用利用可能」と明記されている。業務の録音にはこちらが無難。

## 関連ページ

- [VibeVoice](/blogs/wiki/tools/vibevoice/) — Microsoft の OSS 音声 AI（ASR・TTS）
- [Indra OCR](/blogs/wiki/tools/indra-ocr/) — 同じく「LLM に渡す前の前処理」を担う軽量モデル（文書側）

## ソース記事

- [NVIDIA RE-USE — 9.6M パラメータの音声強調モデルを文字起こしの前処理に挟む](/blogs/posts/2026/11/nvidia-re-use-speech-enhancement/) — 2026-11-05
