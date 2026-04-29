---
title: "Microsoft VibeVoice 徹底解説 — 60分の文字起こしと長尺音声合成をローカル無料で（OSS音声AI）"
date: 2026-04-29
lastmod: 2026-04-29
draft: false
source_url: "https://github.com/hdknr/blogs/issues/1#issuecomment-4341243694"
categories: ["AI/LLM"]
tags: ["microsoft", "vibevoice", "音声認識", "文字起こし", "音声合成", "oss", "tts", "asr"]
---

VibeVoice は、60 分の長尺 ASR（音声認識）と 90 分のマルチ話者 TTS（音声合成）をローカル無料で実現する Microsoft 製の OSS 音声 AI。本記事では特徴・モデル構成・TTS コード削除の経緯を解説する。

[microsoft/VibeVoice](https://github.com/microsoft/VibeVoice) は GitHub スター数 **45,000 超**（2026-04-29 時点）。ICLR 2026 に Oral 採択されたペーパーも公開されており、ASR・TTS の両領域で「フロンティア級」と呼べる性能を、軽量モデルで提供している。一方で、後述のとおり利用可能性については**重要な注意点**がある。

## VibeVoice とは何か

VibeVoice は、TTS と ASR を統合した「音声 AI モデルファミリー」として Microsoft Research が公開している OSS。中核のイノベーションは、**7.5 Hz という超低フレームレートで動作する連続音声トークナイザー**（Acoustic + Semantic）を用いて、長尺音声の処理効率と忠実度を両立した点にある。

LLM（Qwen2.5 1.5B ベース）が文脈・対話の流れを理解し、Diffusion ヘッドで高品質な音響細部を生成する **next-token diffusion** フレームワークを採用している。

## モデルラインナップ

| モデル | パラメータ | 用途 | 状態 |
|---|---|---|---|
| VibeVoice-ASR-7B | 7B | 60分対応の話者識別付き音声認識 | ✅ 利用可能 |
| VibeVoice-TTS-1.5B | 1.5B | 90分・最大4話者の長尺TTS | ⚠️ コード削除済み |
| VibeVoice-Realtime-0.5B | 0.5B | 約300ms の低遅延ストリーミングTTS | ✅ 利用可能 |

### 1. VibeVoice-ASR — 60分の長尺音声認識（文字起こし）

従来の ASR は音声を短いチャンクに分割するため、長尺になると話者識別や文脈の一貫性が失われやすい。VibeVoice-ASR は **64K トークン長で最大 60 分の連続音声を 1 パスで処理**できる。

主な特徴:

- **構造化された出力**: 「**Who（誰が）/ When（いつ）/ What（何を）**」の3要素を含むトランスクリプトを生成（ASR + ダイアライゼーション + タイムスタンプ）
- **50言語以上のマルチリンガル対応**: ネイティブで多言語サポート
- **ホットワード指定**: ドメイン固有の専門用語・人名・背景情報をプロンプトとして与えて認識精度を向上
- **vLLM による高速推論**: 通常の Transformers 経由に加えて vLLM 推論にも対応
- **Hugging Face Transformers 統合**: 2026-03-06 のリリースで `transformers` ライブラリから直接利用可能に

オンラインの [Playground](https://aka.ms/vibevoice-asr) で試せる。

### 2. VibeVoice-Realtime-0.5B — 300ms 起動のリアルタイム音声合成

リアルタイム音声生成向けの軽量モデル。

- パラメータサイズ **0.5B**（デプロイメントしやすい）
- **初回発話までのレイテンシは約 300 ミリ秒**
- ストリーミングテキスト入力に対応
- 約 10 分の長尺生成も可能
- 2025-12-16 のアップデートで、**9言語**（DE / FR / IT / **JP** / KR / NL / PL / PT / ES）の多言語ボイスと、英語の 11 種類のスタイルボイスを実験的に追加

[Colab デモ](https://colab.research.google.com/github/microsoft/VibeVoice/blob/main/demo/vibevoice_realtime_colab.ipynb) で実際に動かせる。

### 3. VibeVoice-TTS-1.5B — 90分・4話者の長尺TTS（提供停止中）

ICLR 2026 に Oral 採択された目玉モデル。**1パスで最大 90 分**、最大 **4 話者**の対話音声を、話者一貫性を保ったまま生成できる。ただし、後述の事情により**現状はコードが削除されている**。

## ⚠️ VibeVoice-TTS のコードは削除されている

リポジトリの News セクションに、Microsoft からの以下の声明が掲載されている:

> **2025-09-05**: VibeVoice is an open-source research framework intended to advance collaboration in the speech synthesis community. After release, we discovered instances where the tool was used in ways inconsistent with the stated intent. Since responsible use of AI is one of Microsoft's guiding principles, we have removed the VibeVoice-TTS code from this repository.

つまり、2025-08-25 に公開された VibeVoice-TTS は、**意図に反する使われ方（おそらくディープフェイク等の悪用）が確認されたため、Microsoft が同年 9 月にコードをリポジトリから削除している**。README のモデル一覧でも VibeVoice-TTS-1.5B の Quick Try は "Disabled" と表示されている。

ペーパーや Hugging Face のウェイト情報は残っているが、**「Microsoft 公式の TTS-1.5B をすぐに動かす」ことは現状できない**。代替として:

- **長尺 TTS が欲しい場合**: VibeVoice-Realtime-0.5B（10分まで）または他の OSS TTS を検討
- **研究目的**: ペーパー（[ICLR 2026 Oral](https://openreview.net/pdf?id=FihSkzyxdv)）で技術詳細は公開されている

## ライセンスと商用利用上の留意点

VibeVoice の README 末尾には「Risks and Limitations」セクションがあり、以下の警告が明記されている:

- **ベースモデル（Qwen2.5 1.5b）由来のバイアス・誤り**を継承する可能性がある
- **ディープフェイクや偽情報生成への悪用リスク**: 高品質な合成音声は、なりすまし・詐欺・偽情報拡散に悪用される懸念がある
- ユーザーは生成コンテンツの信頼性を確認し、誤解を招く形で使わない責任を負う
- AI 生成コンテンツの開示が推奨されている

実際に TTS コードが削除された前例があるため、**配布形態が今後変わる可能性**も念頭に置きたい。

## まとめ — 何ができて、何ができないか

VibeVoice の **2026-04-29 時点で利用可能なもの**:

- ✅ **VibeVoice-ASR-7B**: 60分一発文字起こし／話者識別＋タイムスタンプ／50言語＋ホットワード対応／Hugging Face Transformers 統合済み
- ✅ **VibeVoice-Realtime-0.5B**: 約300msレイテンシ／ストリーミング入力／9言語ボイス／Colab で即時実行可

**現状利用が制限されているもの**:

- ⚠️ **VibeVoice-TTS-1.5B**: 90分・4話者の長尺TTSはコードが削除済み（悪用報告のため）

「ローカルで完全無料で動く長尺ASR」という用途では、現状 VibeVoice-ASR が最有力候補と言える。一方、長尺マルチ話者 TTS については、Microsoft 自身が責任ある AI の観点から提供を停止している点を踏まえて代替手段を検討する必要がある。

## 参考リンク

- [microsoft/VibeVoice (GitHub)](https://github.com/microsoft/VibeVoice)
- [VibeVoice Project Page](https://microsoft.github.io/VibeVoice)
- [VibeVoice-ASR Playground](https://aka.ms/vibevoice-asr)
- [VibeVoice-Realtime-0.5B Colab](https://colab.research.google.com/github/microsoft/VibeVoice/blob/main/demo/vibevoice_realtime_colab.ipynb)
- [Hugging Face Collection](https://huggingface.co/collections/microsoft/vibevoice-68a2ef24a875c44be47b034f)
- [TTS Paper (ICLR 2026 Oral)](https://openreview.net/pdf?id=FihSkzyxdv)
- [ASR Technique Report](https://arxiv.org/pdf/2601.18184)
