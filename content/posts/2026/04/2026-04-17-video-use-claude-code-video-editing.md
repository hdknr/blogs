---
title: "Video Use — Claude Code で動画編集を完全自動化するオープンソーススキル"
date: 2026-04-17
lastmod: 2026-04-17
draft: false
source_url: "https://github.com/hdknr/blogs/issues/1#issuecomment-4265198555"
categories: ["AI/LLM"]
tags: ["Claude Code", "動画編集", "browser-use", "Video Use", "オープンソース"]
---

Claude Code で動画編集が完全自動化できる「**Video Use**」が公開されました。browser-use チームが開発したオープンソーススキルです。カメラに向かって話した素材を Claude に渡すだけで `final.mp4` が完成します。

## Video Use とは

**Video Use** は、Claude Code のスキルとして動作する動画編集自動化ツールです。GitHub リポジトリ [browser-use/video-use](https://github.com/browser-use/video-use) で公開されており、100% オープンソースで利用できます（ただし ElevenLabs API キーが必要です）。

ブラウザ操作を自動化する [browser-use](https://github.com/browser-use/browser-use) を開発したチームが作成したもので、同じ「LLM に情報を読ませる」思想が動画編集に応用されています。

## 主な機能

- **フィラーワード自動カット** — 「えー」「あの」「umm」「uh」などの無駄な言葉や、テイク間の無音部分を自動で除去
- **自動カラーグレーディング** — セグメントごとにカラーグレード（ウォームシネマティック、ニュートラルパンチ、カスタム ffmpeg チェーンなど）を適用
- **字幕自動生成** — デフォルトでは 2 ワードの大文字チャンク形式。スタイルは完全カスタマイズ可能
- **30ms オーディオフェード** — すべてのカット点で自動的に適用され、ポップノイズを防止
- **アニメーションオーバーレイ** — [Manim](https://www.manim.community/) / [Remotion](https://www.remotion.dev/) / PIL によるアニメーションをサブエージェントで並列生成して追加可能
- **自己評価ループ** — レンダリング後にすべてのカット境界を自動チェック。問題があれば最大 3 回まで自動修正
- **セッションメモリ** — `project.md` に状態を保存し、次回セッションで継続作業が可能

## なぜ LLM で動画編集できるのか

Video Use の設計で興味深いのは、**LLM は動画を「見ない」** という点です。

> Naive approach: 30,000 frames × 1,500 tokens = **45M tokens of noise**.  
> Video Use: **12KB text + a handful of PNGs**.

### 2 層の情報表現

**Layer 1 — 音声トランスクリプト（常時ロード）**

ElevenLabs Scribe によって素材ごとにワードレベルのタイムスタンプ・話者分離・音声イベント（笑い、拍手など）を取得し、`takes_packed.md` という約 12KB のファイルに圧縮します。LLM はこのファイルを主な入力として動画編集を判断します。

```text
## C0103  (duration: 43.0s, 8 phrases)
  [002.52-005.36] S0 Ninety percent of what a web agent does is completely wasted.
  [006.08-006.74] S0 We fixed this.
```

**Layer 2 — ビジュアルコンポジット（必要時のみ）**

`timeline_view` ツールが任意の時間範囲についてフィルムストリップ + 波形 + ワードラベルの PNG を生成します。LLM がカット点の判断に迷う場合のみ呼び出されます。

### パイプライン

処理の流れは「トランスクリプト生成 → パック → LLM 推論 → EDL 生成 → レンダリング → 自己評価」の順です。自己評価で問題が検出された場合は修正・再レンダリングを最大 3 回繰り返してから結果をユーザーに返します。

browser-use が LLM にスクリーンショットではなく構造化 DOM を渡すのと同じ発想で、動画に対しては「テキスト + 必要時の画像」という形で情報を渡しています。

## セットアップ

```bash
# 1. リポジトリをクローンして Claude Code のスキルディレクトリにシンボリックリンク
git clone https://github.com/browser-use/video-use
cd video-use
ln -s "$(pwd)" ~/.claude/skills/video-use

# 2. 依存関係のインストール
pip install -e .
brew install ffmpeg           # 必須
brew install yt-dlp            # オプション（オンライン動画ダウンロード用）

# 3. ElevenLabs API キーを設定
cp .env.example .env
$EDITOR .env   # ELEVENLABS_API_KEY=... を設定
```

## 使い方

動画素材のフォルダに移動して Claude Code を起動し、自然言語で指示するだけです。

```bash
cd /path/to/your/videos
claude
```

Claude Code のセッションで:

```
edit these into a launch video
```

Video Use が素材を解析し、編集戦略を提案。承認すると `edit/final.mp4` が生成されます。出力はすべて `<videos_dir>/edit/` に格納されるため、`~/.claude/skills/video-use/` ディレクトリは常にクリーンな状態を保ちます。

## まとめ

Video Use は「LLM に情報をどう渡すか」という問題に対する巧みな解答です。動画を直接渡すのではなく、音声トランスクリプトという構造化テキストを主要インターフェースにすることで、コンテキスト消費を劇的に抑えながら高精度な編集判断を実現しています。

トーキングヘッド動画、チュートリアル、インタビュー、旅行動画など、あらゆるコンテンツタイプに対応しており、プリセットや複雑なメニュー操作なしに動画制作を自動化できる点が魅力です。
