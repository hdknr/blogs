---
title: "ViMax — 1行のアイデアから脚本・絵コンテ・動画まで自動生成する香港大学発マルチエージェントフレームワーク"
date: 2026-05-11
lastmod: 2026-05-11
slug: "vimax-hku-agentic-video-generation"
draft: false
source_url: "https://github.com/hdknr/blogs/issues/1#issuecomment-4424569782"
description: "香港大学 HKUDS が開発したオープンソース動画生成フレームワーク ViMax の全機能を解説。Idea2Video・Novel2Video・Script2Video・AutoCameo の4モードと、RAG ベースのマルチエージェントアーキテクチャを日本語で詳しく紹介します。"
categories: ["AI/LLM"]
tags: ["ViMax", "動画生成", "マルチエージェント", "オープンソース", "RAG", "Python", "Gemini"]
---

香港大学データインテリジェンスラボ（HKUDS）が開発したオープンソースの動画生成フレームワーク **ViMax** が GitHub で急速にスターを伸ばしている（3,800超・MIT ライセンス）。1行のテキストアイデアを入力するだけで、脚本執筆・絵コンテ設計・キャラクター管理・最終動画レンダリングまでを自律的に実行するエンドツーエンドのマルチエージェントシステムだ。

## ViMax とは

ViMax（**Vi**deo **Max**imizer）は「Director（監督）・Screenwriter（脚本家）・Producer（プロデューサー）・Video Generator（映像生成）をひとつに」という設計コンセプトで開発された動画生成フレームワークだ。従来、テキストから動画を生成するには複数のツールを組み合わせる必要があった。ViMax はそのパイプライン全体をマルチエージェント構成で自動化する。

- **GitHub**: [HKUDS/ViMax](https://github.com/HKUDS/ViMax)
- **ライセンス**: MIT
- **言語**: Python 3.12+
- **Stars**: 3,852+（2026年5月時点）

## 4つの生成モード

ViMax には入力形式に応じた 4 つのモードが用意されている。

### Idea2Video

1 行の概念・プロンプトを入力すると、ストーリーテリング・キャラクターデザイン・動画制作まで完全自動化される。「アイデアをそのまま映像に」したいユーザー向けのモードだ。

### Novel2Video

小説の章や全文を入力すると、エピソード形式の動画に変換される。RAG（検索拡張生成）ベースのナラティブ圧縮機能でキャラクターの登場追跡とシーンごとの視覚的解釈を行う。長編小説の映像化に適している。

### Script2Video

ユーザーが書いたシナリオを動画化する。シーン・セリフ・スタイルを明示的に指定でき、映像表現への細かいコントロールが可能。

### AutoCameo

自分の写真をアップロードすると、生成された動画に本人が一貫したキャラクターとして登場する機能。個人の顔や姿を主人公として組み込める。

## 主要な技術的特徴

### インテリジェントな長編スクリプト生成（RAG ベース）

小説規模のテキストを解析し、マルチシーン形式に分割する。重要な伏線やキャラクターの台詞を保持しながら、映像に適した脚本へ変換する。

### 表現力豊かな絵コンテ設計

ショットレベルの絵コンテシステムに映画製作の語彙（カメラアングル・カット・テンポ・ナラティブリズム）を採用している。

### マルチカメラ撮影シミュレーション

同一シーン内でのキャラクター配置・背景の一貫性を保ちながら、複数のカメラアングルをシミュレートする。

### インテリジェントな参照画像選択

タイムライン上の過去の絵コンテを参照画像として自動選択し、長尺動画でもキャラクターや背景の整合性を維持する。

### 並列候補生成 + MLLM による一貫性チェック

複数の候補画像を並列生成し、マルチモーダル LLM（MLLM — テキストと画像を同時に扱える大規模言語モデル）が最も一貫性の高い画像を選択する。人間のクリエイターのレビューワークフローを自動化したアプローチだ。

### 並列ショット生成による高速化

同じカメラからの連続するショットを並列処理することで、生成時間を大幅に短縮する。

### 音声・映像バインディング

音声・効果音・映像を同期させ、没入感のある最終出力を生成する。

## マルチエージェントパイプラインの構造

ViMax の処理パイプラインは以下の層で構成されている。

![ViMax のマルチエージェント処理パイプライン — 入力層からスクリプト解析・シーン計画・ビジュアル合成を経て最終動画を出力する全体の流れ](/blogs/images/vimax-pipeline.png)

## インストールと設定

**動作環境**: Linux または Windows / Python 3.12+ / `uv`（Astral パッケージマネージャー）

`uv` が未インストールの場合は先にインストールする:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

```bash
git clone https://github.com/HKUDS/ViMax.git
cd ViMax
uv sync
```

**必要な API キー（3つの外部サービス）**:

1. **チャットモデル** — デフォルト: `google/gemini-2.5-flash-lite-preview-09-2025`（OpenRouter 経由）。代替として MiniMax-M2.7（100万トークンコンテキスト）や MiniMax-M2.5 も利用可能。
2. **画像生成** — Google Nanobanana API キー
3. **動画生成** — Google Veo API キー

設定ファイル（`configs/idea2video.yaml` の例）:

```yaml
chat_model:
  init_args:
    model: google/gemini-2.5-flash-lite-preview-09-2025
    model_provider: openai
    api_key: <YOUR_API_KEY>
    base_url: https://openrouter.ai/api/v1

image_generator:
  class_path: tools.ImageGeneratorNanobananaGoogleAPI
  init_args:
    api_key: <YOUR_API_KEY>

video_generator:
  class_path: tools.VideoGeneratorVeoGoogleAPI
  init_args:
    api_key: <YOUR_API_KEY>

working_dir: .working_dir/idea2video
```

**実行エントリポイント**:
- `main_idea2video.py` — Idea2Video モード
- `main_script2video.py` — Script2Video モード

**Script2Video の使用例**:

```python
script = """
EXT. 学校のジム - 昼
ジョン（18歳、男性、長身、アスリート体型）がバスケットボールの練習をしている...
"""
user_requirement = "20ショット以内のテンポの速い映像"
style = "Animate Style"
```

**スタイルプリセット**: Cartoon、Cinematic、Modern Tech、Animate Style など

## 注意点・制限事項

- **対応 OS**: Linux と Windows のみ。macOS はサポート外
- **外部 API 必須**: チャットモデル（OpenRouter）・画像生成（Nanobanana）・動画生成（Google Veo）の3種類の API キーが必要で、それぞれ利用コストが発生する
- **Python 3.12+**: システムの Python バージョンが 3.12 未満の場合は事前アップグレードが必要
- **生成時間**: 複数のエージェントが直列・並列で動作するため、動画1本の生成に数分〜数十分かかる場合がある
- **モデル名の変動**: デフォルトのチャットモデル `google/gemini-2.5-flash-lite-preview-09-2025` はプレビュー版のため、今後変更される可能性がある（2026年5月時点）

## 活用シーン

ViMax が特に効果を発揮する用途は以下のとおり:

- **コンテンツクリエイター・個人メディア**: SNS 用の動画を効率的に量産
- **小説家・物語作家**: 執筆した小説を映像化してプレビュー
- **広告・マーケティングチーム**: コンセプト動画の高速プロトタイピング
- **教育コンテンツ制作者**: 授業動画や説明動画の作成
- **インディーズ映像制作者**: 映画・ゲームのシネマティック映像

## まとめ

ViMax は「1行書くだけで動画ができる」というコンセプトを、マルチエージェントアーキテクチャと RAG ベースの一貫性管理によって実用レベルで実現したフレームワークだ。Runway や HeyGen のような商用サービスの機能をオープンソースで統合した点が際立っており、コンテンツ制作の自動化を検討している開発者やクリエイターにとって試す価値がある。

AutoCameo や Novel2Video など独自機能のロードマップも活発に進んでおり、今後のアップデートにも注目したい。
