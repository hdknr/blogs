---
title: "Claude Code × HyperFrames でバズった Instagram リールを AI 完全再現 — 問われる「企画力」と「言語化力」"
date: 2026-04-27
lastmod: 2026-04-27
draft: false
description: "Claude Code に Instagram リールの URL を渡すだけで HyperFrames が 60 秒の縦型動画を自動生成。ショート動画制作の新しいワークフローと、AI 時代に必要な「企画力・言語化力」を解説。"
source_url: "https://github.com/hdknr/blogs/issues/1#issuecomment-4324247908"
categories: ["AI/LLM"]
tags: ["Claude Code", "HyperFrames", "動画生成", "HeyGen", "AI動画", "ショート動画"]
---

バズった筋トレ系 Instagram リールの URL を Claude Code に渡し、「構成を完全再現しつつ日本人女性を生成して HyperFrames で編集して」と指示したら 60 秒の縦型動画が完成した——そんなデモが X で話題を集めています。この記事では HyperFrames の仕組みと Claude Code を使ったワークフロー、そして AI 時代に求められるスキルを整理します。

## X で話題になったデモ

[@note_ai_mousigo（まな｜note×AIの申し子）](https://x.com/note_ai_mousigo) さんが 2026 年 4 月 26 日（JST）に投稿したデモが反響を呼んでいます。

> 待ってwww  
> これはヤバすぎるwww
>
> Claude Code にバズってる筋トレ系のインスタリールの URL を渡して、「構成を完全再現しつつ、日本人女性を生成して Renoise と Hyperframes で編集して」って伝えたらこうなった。
>
> もう何でもありだな Claude Code！
>
> ショート動画の価値も下がりそう😇  
> やっぱり AI マネタイズで大事になるのは、「企画力」「言語化力」だけだね！
>
> 詳しいやり方はリプ👇

出力された動画は 720×1280 の縦型 MP4、再生時間 60 秒。Claude Code が URL を解析して構成を把握し、新しい素材に差し替えて HyperFrames でレンダリングした結果です。

## HyperFrames とは

[HyperFrames](https://github.com/heygen-com/hyperframes) は HeyGen が開発したオープンソースの動画レンダリングフレームワークです（Apache 2.0 ライセンス）。

- **"Write HTML. Render video. Built for agents."** をキャッチコピーに、HTML / CSS / JS で動画コンポジションを記述し MP4・MOV・WebM に書き出せます
- LLM は HTML を流暢に書けるため、Claude Code や Gemini CLI と相性が抜群
- GSAP・SVG・Canvas などのアニメーションライブラリをそのまま使えるため、モーショングラフィックスも自由自在
- フレームレート単位での決定論的レンダリングで、実行環境が変わっても出力が一致する

2026 年 3 月に GitHub へ公開され、4 月には公式サイトと Claude Code 向けスキルが整備されました。スター数は 11,000 超（2026 年 4 月時点）。

### Claude Code でのセットアップ

HyperFrames は Claude Code スキルとして配布されており、インストール後は次のスラッシュコマンドが使えます：

- `/hyperframes` — コンポジションを作成・編集
- `/hyperframes-cli` — CLI コマンドを実行
- `/gsap` — GSAP アニメーションのヘルプ

## Renoise とは

[Renoise](https://www.renoise.com/) は Windows・Mac・Linux 対応の本格的な音楽制作 DAW です。トラッカーベースの UI でリズムパターンやサウンドデザインを組み立てられます。今回のデモでは、動画の BGM・効果音をこのツールで制作・合成したと推定されます。

## ワークフロー：リール URL → AI 再現動画

デモを分解すると、Claude Code が以下のステップを自律実行したと推定されます。

### 1. 動画構成の解析

渡された Instagram リールの URL から動画メタデータを取得し、場面構成・カット割り・テキストのタイミングを分析します。

### 2. ビジュアル素材の生成

「日本人女性を生成して」という指示に従い、画像生成 AI を呼び出して人物素材を作成します。

### 3. HyperFrames でのコンポジション

解析した構成をもとに Claude Code が HTML / CSS / JS でシーン定義を記述。HyperFrames が各フレームをレンダリングして MP4 に書き出します。

### 4. Renoise での音楽制作

Renoise で BGM・効果音を制作し、最終的な動画ファイルに合成します。

## なぜこれが可能になったのか

従来の動画編集ツールは GUI タイムライン操作が前提でした。HyperFrames は「動画をコードで書く」という発想で LLM が直接制御できるレイヤーを設け、Remotion（React ベース）とも共存できる設計でエコシステムが急拡大しています。

Claude Code はコード補完にとどまらず、ツール呼び出し・ファイル操作・複数ステップの実行を自律的にこなします。「リールの構成を再現して」という抽象的な指示を、URL 取得→構成分析→コード生成→レンダリングという具体的なステップに自動分解できる点が今回のデモを可能にしています。

## 問われるのは「企画力」と「言語化力」

投稿の末尾にある一文が本質を突いています：

> やっぱり AI マネタイズで大事になるのは、「企画力」「言語化力」だけだね！

生成・編集の「作業」は AI が代替できるようになっても、**何を作るか（企画）** と **どう伝えるか（言語化）** は人間が担い続けます。バズったリールを発見し、「これを別のターゲット向けに再構成したい」と言語化できる人が、AI ツールを最も効果的に活用できます。

## まとめ

| ツール | 役割 |
|---|---|
| **Claude Code** | 構成解析・コード生成・ワークフロー制御 |
| **HyperFrames** | HTML→MP4 動画レンダリング |
| **Renoise** | BGM・音響制作 |
| **画像生成 AI** | 人物・背景素材の生成 |

HyperFrames の登場で、Claude Code が扱える「メディア」がテキスト・画像からショート動画にまで拡張されました。同様のワークフローは広告クリエイティブ、教育コンテンツ、SNS 運用など幅広い用途に応用できます。

ツールの使い方よりも「何を作るか」を考える時間に投資することが、AI 時代のコンテンツ戦略の核心になりそうです。
