---
title: "Video Use"
description: "Claude Code のスキルとして動作する動画編集自動化ツール。音声トランスクリプトを主インターフェースとして LLM で動画編集を行う"
date: 2026-04-23
lastmod: 2026-04-23
aliases: ["video-use", "ビデオユース"]
related_posts:
  - "/posts/2026/04/2026-04-17-video-use-claude-code-video-editing/"
tags: ["Claude Code", "動画編集", "browser-use", "オープンソース", "ElevenLabs"]
---

## 概要

browser-use チームが開発した、Claude Code のスキルとして動作する動画編集自動化ツール。GitHub リポジトリ [browser-use/video-use](https://github.com/browser-use/video-use) で公開。カメラに向かって話した素材を Claude に渡すだけで `final.mp4` を生成できる。

## 設計の核心: LLM は動画を「見ない」

従来の素朴なアプローチ（30,000 フレーム × 1,500 トークン = 4,500 万トークン）の代わりに、2 層の情報表現を採用する:

| 層 | 内容 | 容量 |
|----|------|------|
| **Layer 1（常時ロード）** | ElevenLabs Scribe による音声トランスクリプト（`takes_packed.md`） | 約 12KB |
| **Layer 2（必要時のみ）** | フィルムストリップ + 波形 + ワードラベルの PNG | 判断が必要な場合のみ生成 |

browser-use が LLM に DOM を渡すのと同じ発想で、動画に対しては「テキスト + 必要時の画像」という形で情報を渡す。

## 主な機能

- **フィラーワード自動カット**: 「えー」「あの」「umm」「uh」などと無音部分を自動除去
- **自動カラーグレーディング**: セグメントごとにプリセットまたはカスタム ffmpeg チェーンを適用
- **字幕自動生成**: デフォルトは 2 ワードの大文字チャンク形式
- **30ms オーディオフェード**: すべてのカット点で自動適用
- **アニメーションオーバーレイ**: Manim / Remotion / PIL によるアニメーションをサブエージェントで並列生成
- **自己評価ループ**: レンダリング後に全カット境界を自動チェック、最大 3 回まで自動修正
- **セッションメモリ**: `project.md` に状態を保存して次回セッションで継続

## セットアップ

```bash
git clone https://github.com/browser-use/video-use
ln -s "$(pwd)/video-use" ~/.claude/skills/video-use
pip install -e video-use
brew install ffmpeg
# .env に ELEVENLABS_API_KEY を設定
```

## 使い方

動画素材フォルダに移動して Claude Code を起動し、自然言語で指示するだけ。出力はすべて `<videos_dir>/edit/` に格納される。

## 関連ページ

- [Claude Code](/blogs/wiki/tools/claude-code/) — スキルとして統合されている実行環境

## ソース記事

- [Video Use — Claude Code で動画編集を完全自動化するオープンソーススキル](/blogs/posts/2026/04/2026-04-17-video-use-claude-code-video-editing/) — 2026-04-17
