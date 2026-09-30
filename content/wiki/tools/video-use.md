---
title: "Video Use"
description: "Claude Code のスキルとして動作する動画編集自動化ツール。音声トランスクリプトを主インターフェースとして LLM で動画編集を行う"
date: 2026-04-23
lastmod: 2026-09-30
aliases: ["video-use", "ビデオユース", "Hard Rules"]
related_posts:
  - "/posts/2026/04/video-use-claude-code-video-editing/"
  - "/posts/2026/09/video-use-silent-failures-hard-rules/"
tags: ["claude-code", "動画編集", "browser-use", "オープンソース", "ElevenLabs", "ffmpeg"]
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

必須要件はリポジトリ、`ffmpeg`（と `ffprobe`）、ElevenLabs API キーの 3 つ。2026 年 5 月に MIT ライセンスが付与され、README に貼れる**ワンペースト導入プロンプト**（`install.md`）でクローン・依存インストール・スキル登録・API キー入力までエージェント自身が処理するようになった。依存管理は `uv sync` が第一候補で `pip install -e .` はフォールバック。スキルの登録先は `~/.claude/skills/`（Claude Code）と `~/.codex/skills/`（Codex）。HyperFrames・Remotion・Manim などのアニメーションエンジンは必要になった時点で遅延インストールされる。

「完全無料でローカル完結」と紹介されがちだが、**音声認識は ElevenLabs Scribe の従量課金 API に依存する**。

## 使い方

動画素材フォルダに移動して Claude Code を起動し、自然言語で指示するだけ。出力はすべて `<videos_dir>/edit/` に格納される。アニメーションは HyperFrames（HTML/CSS/GSAP）が Remotion / Manim / PIL と並ぶ第一級の選択肢になり、スロットごとにエンジンを選ぶ形になった。

## 4 か月の修正は「沈黙する失敗」だった

2026 年 4 月以降にマージされた修正の中心は、どれも ffmpeg が正常終了し `final.mp4` ができ、ローカル再生でも正しく見えるのに中身が壊れている種類だった（[沈黙する失敗](/blogs/wiki/concepts/silent-failure/)）。

| 失敗 | 原因 | 修正 |
|---|---|---|
| ナレーションが消える | `-map` なしの既定選択が OBS のアプリ音声トラックを拾う | `--audio-track` で明示、無音トラックを拒否 |
| アップロード後だけ色が潰れる | HLG / PQ の転送特性メタデータが 8bit 出力に残る。QuickTime は再生時にトーンマップするので手元では正常に見える | Rec.709 SDR へトーンマップ |
| 30/60fps が 24fps に間引かれる | 出力レートの決め打ち | `avg_frame_rate` を計測。ロスレス連結のためレートはレンダリングごとに 1 つ |
| 縦動画が潰れる／伸びる | 横向き符号化 + 90/270 度の表示回転を符号化寸法だけで判定 | display-matrix の回転を読み実効寸法を入れ替える |
| 字幕が TikTok / Reels / Shorts の UI に隠れる | `MarginV=35` が下端 25〜30% の UI 帯に入る | `MarginV=90` |

レンダリング後の自己評価ループが捕まえられそうなのは字幕の 1 件だけ。自己評価はカット境界のフィルムストリップと波形を見る仕組みで、**コンテナ全体の属性やソース選択の妥当性は検査範囲の外**にある。

## Hard Rules と artistic freedom

`SKILL.md` は指示を 2 種類に分けている。具体的な値・プリセット・技法はすべて「通った 1 本の動画での一例」で裁量に任せ、必須なのは**外れると沈黙する失敗か壊れた出力になる 12 の Hard Rules**だけ（「They are not taste, they are correctness」）。

- 字幕はフィルタチェーンの最後に焼く
- セグメント単位で抽出し `-c copy` でロスレス連結する
- 全セグメント境界に 30ms のオーディオフェード
- オーバーレイは `setpts=PTS-STARTPTS+T/TB`
- マスター SRT は出力タイムライン基準のオフセット
- 単語の内側で切らず、カット端に 30〜200ms のパディング（Scribe は 50〜100ms ドリフトする）
- 単語単位の verbatim ASR のみ使い、トランスクリプトはソース単位でキャッシュ
- アニメーションはサブエージェントで並列生成、戦略はユーザー承認前に実行しない、出力は `<videos_dir>/edit/`

壊れ方が沈黙する箇所だけを非交渉の規則として抜き出し、それ以外は全部任せる、というエージェント向けツールの設計例になっている。

## 関連ページ

- [Claude Code](/blogs/wiki/tools/claude-code/) — スキルとして統合されている実行環境
- [沈黙する失敗](/blogs/wiki/concepts/silent-failure/) — 成功に見える失敗の一般形
- [ハーネスエンジニアリング](/blogs/wiki/concepts/harness-engineering/) — 非交渉の規則をランタイム側に置く設計

## ソース記事

- [Video Use — Claude Code で動画編集を完全自動化するオープンソーススキル](/blogs/posts/2026/04/video-use-claude-code-video-editing/) — 2026-04-17
- [Video Use の「沈黙する失敗」— ffmpeg が成功しても動画が壊れる 5 つの罠と 12 の Hard Rules](/blogs/posts/2026/09/video-use-silent-failures-hard-rules/) — 2026-09-02
