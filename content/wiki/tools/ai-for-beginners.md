---
title: "AI-For-Beginners（Microsoft）"
description: "Microsoft が GitHub で公開する無料の AI 入門カリキュラム。シンボリック AI からニューラルネットワーク、CV、NLP、Transformer までを 24 レッスンで辿る。日本語版あり"
date: 2026-09-30
lastmod: 2026-09-30
aliases: ["AI For Beginners", "microsoft/AI-For-Beginners", "12 Weeks, 24 Lessons, AI for All"]
related_posts:
  - "/posts/2026/09/microsoft-ai-for-beginners/"
  - "/posts/2026/09/ai-for-beginners-01-intro-history/"
  - "/posts/2026/09/ai-for-beginners-02-symbolic-ai/"
  - "/posts/2026/09/ai-for-beginners-03-neural-networks/"
tags: ["Microsoft", "AI-For-Beginners", "機械学習", "ディープラーニング", "llm"]
---

## 概要

[microsoft/AI-For-Beginners](https://github.com/microsoft/AI-For-Beginners) は、Microsoft（主執筆者 Dmitry Soshnikov 氏）が 2021 年から MIT ライセンスで公開している AI 入門カリキュラム。「12 Weeks, 24 Lessons, AI for All!」を掲げ、知識表現 → ニューラルネットワーク → CV / NLP → Transformer → LLM と、歴史と構造の順に積み上げる。日本語版は README だけでなく各レッスン本文と Jupyter Notebook まで `translations/ja/` に揃っている。

生成 AI から入った人が、**LLM の「手前」を下から積み直す**教材として価値がある。LLM の章そのものは古い。

## 詳細

### 構成

| パート | レッスン | 主な内容 |
|---|---|---|
| I. AI 入門 | 01 | AI の定義と歴史、2 つのアプローチ |
| II. シンボリック AI | 02 | 知識表現、エキスパートシステム、オントロジー |
| III. ニューラルネットワーク | 03〜05 | パーセプトロン、多層パーセプトロンの自作、PyTorch / TensorFlow と過学習 |
| IV. コンピュータビジョン | 06〜12 | OpenCV、CNN、転移学習、VAE、GAN、物体検出、セグメンテーション |
| V. 自然言語処理 | 13〜20 | BoW / TF-IDF、Word2Vec、RNN、Transformer と BERT、固有表現抽出、LLM |
| VI. その他 | 21〜23 | 遺伝的アルゴリズム、深層強化学習、マルチエージェント |
| VII. AI 倫理 | 24 | 責任ある AI |

前後に環境構築のレッスン 0 とマルチモーダル（CLIP / VQGAN）のレッスン 25 が付く。各レッスンに講義前後のクイズ、PyTorch 版と TensorFlow 版の Notebook、一部にラボがあり、**Notebook を動かす前提**の教材である。古典的な機械学習（回帰・決定木）は姉妹カリキュラム ML-For-Beginners の担当で扱わない。

### レッスン 01 の地図

- AI の対象は「人間は経験からできるが、**手順を書き出せない問題**」（写真から年齢を当てる、など）
- 知能を載せる方法は、推論をまねるトップダウン（[記号的 AI](/blogs/wiki/concepts/symbolic-ai/)）と、脳の構造をまねるボトムアップ（[ニューラルネットワーク](/blogs/wiki/concepts/neural-network-basics/)）の 2 本柱。ほかに創発的・マルチエージェント的アプローチと進化的アプローチ
- チューリングテストは知能を定義する代わりに「人間と区別できるか」という判定方法を与えた。2014 年の Eugene Goostman について教材は「ボットではなく作者が人間を欺いた」と釘を刺す。2025 年にはペルソナを与えた GPT-4.5 が 3 者間テストで 73% の確率で人間と判定された。**区別できないことと理解していることは別**
- チェスは「探索（アルファベータ枝刈り）→ 事例ベース推論 → ニューラルネットワーク＋強化学習」、対話は「ELIZA → ハイブリッド型アシスタント → ニューラルネットワークだけの対話」と主役が移った。後者は教材の予想どおり LLM で実現した

### 割り切って読むべきところ

- **LLM の章は GPT-2 / GPT-3 の時代で止まっている** — RLHF・指示チューニング・RAG・エージェントは扱わない。GPT ファミリーの表の「GPT-4 は 100 兆パラメータ」は英語原文ごと誤り（公開前の噂の値）
- **日本語版は Co-op Translator による機械翻訳** — レッスン 01 の「話すプログラム」の節は本文が途中で欠落している。数式や用語で引っかかったら英語原文と突き合わせる
- **レッスン 01 の史実の圧縮** — AI の冬は一般に 2 回（1970 年代と 1980 年代末）。2015 年に画像分類で人間の推定精度を初めて上回った論文は ResNet ではなく PReLU の *Delving Deep into Rectifiers*
- **Notebook は 2021〜2022 年のライブラリのまま** — 今の環境では動かないセルがある（MNIST データ形式の差し替え、NumPy 2、Matplotlib、Keras 3。詳細は[ニューラルネットワークの基礎](/blogs/wiki/concepts/neural-network-basics/)）
- レッスン 02 の Microsoft Concept Graph の演習は API 停止で動かない。日本語版ディレクトリには `data/` が無く FamilyOntology は失敗する

### 日本語版だけをクローンする

リポジトリには 50 以上の言語の翻訳が入っていて大きい。README の sparse-checkout 手順をそのまま使うと日本語版も消えるので、除外したうえで `ja` だけを戻す。

```bash
git clone --depth 1 --filter=blob:none --sparse https://github.com/microsoft/AI-For-Beginners.git
cd AI-For-Beginners
git sparse-checkout set --no-cone '/*' '!translations' '!translated_images' '/translations/ja/' '/translated_images/ja/'
```

日本語版の本文は画像を `translated_images/ja/` から相対パスで参照するので、**`translated_images/ja/` も戻さないと図が全部リンク切れになる**。作業ディレクトリ全体は約 222MB になった。

### LLM を説明できるようになりたい場合の絞り方

1. レッスン 03〜05 でニューラルネットワークと学習の仕組み
2. レッスン 13〜18 でテキスト表現から Transformer / BERT まで
3. レッスン 20 で言語モデルとしての GPT の考え方（GPT-4 の行は読み飛ばす）
4. 現在の LLM 活用は Microsoft の Generative AI for Beginners / AI Agents for Beginners に引き継ぐ

## 関連ページ

- [記号的 AI（知識表現とエキスパートシステム）](/blogs/wiki/concepts/symbolic-ai/) — パート II の内容
- [ニューラルネットワークの基礎](/blogs/wiki/concepts/neural-network-basics/) — パート III の内容と Notebook の動かし方
- [RAG](/blogs/wiki/concepts/rag/) — 教材が扱わない現在の LLM 活用の一例
- [AI エージェント](/blogs/wiki/concepts/ai-agent/) — 同上

## ソース記事

- [Microsoft の AI-For-Beginners 日本語版 — LLM の「手前」を積み直す教材として使う](/blogs/posts/2026/09/microsoft-ai-for-beginners/) — 2026-09-29
- [AI の歴史と基本をやさしく解説 — Microsoft AI-For-Beginners レッスン 01](/blogs/posts/2026/09/ai-for-beginners-01-intro-history/) — 2026-09-29
- [知識表現とエキスパートシステムをやさしく解説 — Microsoft AI-For-Beginners レッスン 02](/blogs/posts/2026/09/ai-for-beginners-02-symbolic-ai/) — 2026-09-30
- [ニューラルネットワークの基礎をやさしく解説 — Microsoft AI-For-Beginners レッスン 03〜05](/blogs/posts/2026/09/ai-for-beginners-03-neural-networks/) — 2026-09-30
