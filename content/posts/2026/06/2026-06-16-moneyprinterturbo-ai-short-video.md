---
title: "テーマを入力するだけでショート動画が自動完成 — スター8.8万超のOSS「MoneyPrinterTurbo」徹底解説"
date: 2026-06-16
lastmod: 2026-06-16
slug: "moneyprinterturbo-ai-short-video"
draft: false
description: "テーマを1行入力するだけで台本・映像・字幕・BGMを含むショート動画を自動生成するOSS MoneyPrinterTurbo の全機能と導入手順を解説。TikTok・YouTube Shorts の量産に対応。"
source_url: "https://github.com/hdknr/blogs/issues/1#issuecomment-4714976862"
categories: ["AI/LLM"]
tags: ["MoneyPrinterTurbo", "ショート動画", "AI動画生成", "Python", "docker"]
---

テーマ（キーワード）を1つ入力するだけで、台本・映像素材・字幕・BGMまで込みのショート動画が自動生成される。そのOSSが **MoneyPrinterTurbo** だ。2024年3月の公開から約2年でGitHubスター数は **8.8万超** に達し、TikTok・YouTube Shorts向けコンテンツ制作を自動化したい個人・クリエイターの間で広く使われている。

## MoneyPrinterTurboとは

- **リポジトリ**: [harry0703/MoneyPrinterTurbo](https://github.com/harry0703/MoneyPrinterTurbo)
- **言語**: Python
- **ライセンス**: MIT
- **説明**: 「利用AI大模型，一键生成高清短视频 / Generate short videos with one click using AI LLM.」

動画生成に必要な全工程をパイプライン化している。

1. LLM（GPT・Gemini・DeepSeek 等）が入力テーマから台本を自動生成
2. Pexels・Pixabay・Coverr などのフリー素材サービスから映像クリップを自動取得
3. Edge TTS / Azure TTS V2 でナレーション音声を合成
4. Whisper（または Edge モード）で字幕を自動生成・タイムコード付与
5. MoviePy で全素材を合成し、最終動画として出力

## 主な機能

| 機能 | 詳細 |
|------|------|
| フォーマット対応 | 縦型 9:16（1080×1920）/ 横型 16:9（1920×1080） |
| バッチ生成 | 複数テーマを一括で動画化 |
| 字幕カスタマイズ | フォント・位置・色・サイズ・縁取り効果を調整可能 |
| 複数 LLM 対応 | OpenAI・Gemini・DeepSeek・Azure など設定ファイルで切替 |
| 音声合成 | Edge TTS（無料）/ Azure TTS V2（高品質・有料）を選択可能 |
| WebUI | Streamlit ベースの GUI を同梱 |
| REST API | `main.py` 起動で Swagger UI 付きの API サーバーが立ち上がる |

## インストール方法

### 方法1: Windows 向け一括パッケージ

[GitHub Releases](https://github.com/harry0703/MoneyPrinterTurbo/releases/latest) から ZIP をダウンロードし、`update.bat` で最新化した後 `start.bat` を実行するだけで動く。コマンドライン操作不要。

### 方法2: Docker（推奨・マルチプラットフォーム）

```bash
git clone https://github.com/harry0703/MoneyPrinterTurbo.git
cd MoneyPrinterTurbo
docker compose -f docker-compose.release.yml up
```

Docker 環境があれば OS 依存を排除できる最もポータブルな方法。

### 方法3: 手動セットアップ（macOS / Linux）

```bash
git clone https://github.com/harry0703/MoneyPrinterTurbo.git
cd MoneyPrinterTurbo
uv sync --frozen
```

Python パッケージ管理に [uv](https://github.com/astral-sh/uv) を採用しているため、依存解決が高速。

## 起動方法

### WebUI

```bash
# macOS / Linux
sh webui.sh
# または
uv run streamlit run ./webui/Main.py
```

ブラウザが自動起動し、テーマ入力から動画ダウンロードまでをクリック操作で完結できる。

### API サーバー

```bash
uv run python main.py
```

起動後、`http://127.0.0.1:8080/docs` で Swagger UI が確認できる。CI/CD パイプラインや外部アプリとの統合に使いやすい。

### CLI

```bash
uv run python cli.py --video-subject "日本の桜の名所5選"
```

スクリプトからバッチ実行したい場合はこれが最も柔軟。

## 設定（config.toml）

`config.toml` を編集することで、LLM プロバイダーや音声合成エンジンを自由に組み合わせられる。主要な設定項目の抜粋（全オプションは `config.example.toml` を参照）:

```toml
[llm]
provider = "openai"        # openai / gemini / azure / deepseek / aihubmix など

[tts]
provider = "edge"          # edge（無料）/ azure（高品質）

[subtitle]
mode = "edge"              # edge（高速）/ whisper（高精度）
```

カスタムフォントは `resource/fonts/`、BGM は `resource/songs/` に置くだけで自動認識される。

## ユースケース

- **TikTok・YouTube Shorts の量産**: 商品紹介や知識系コンテンツをバッチ生成し、定期投稿のネタを自動補充
- **教育コンテンツ**: 単語解説・ニュースまとめなどのナレーション付き縦型動画を即席作成
- **個人メディア運営**: ブログ記事のテキストを動画に変換し、リーチを広げる

## まとめ

MoneyPrinterTurbo はテーマを1行入力するだけで台本・映像・字幕・BGMまで全工程が自動化されたパイプラインを無料で提供している。MIT ライセンスなので商用利用も自由。WebUI・API・CLI の3種類のインターフェースが揃っており、個人の手作業からバッチ自動化まで幅広いスケールに対応できる点が、8万超のスターを集めた理由だろう。

LLM 料金を最小化したい場合は DeepSeek や Gemini Flash をバックエンドにする選択肢もある。まずは Docker で立ち上げて、自分のテーマで試してみてほしい。
