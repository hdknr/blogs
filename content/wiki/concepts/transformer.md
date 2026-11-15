---
title: "Transformer（トランスフォーマー）"
description: "RNN をやめて Attention だけで系列を処理するニューラルネットワークのアーキテクチャ。並列に学習できることが現在の LLM の土台になった"
date: 2026-11-15
lastmod: 2026-11-15
aliases: ["トランスフォーマー", "Self-Attention", "セルフアテンション", "Scaled Dot-Product Attention", "Multi-Head Attention", "マルチヘッドアテンション", "Positional Encoding", "位置の埋め込み", "Attention Is All You Need"]
related_posts:
  - "/posts/2026/11/transformer-basics/"
  - "/posts/2026/10/ai-for-beginners-05-nlp/"
  - "/posts/2026/11/looped-transformer-nvidia-dory/"
  - "/posts/2026/05/subq-llm-subquadratic-sparse-attention/"
tags: ["Transformer", "ニューラルネットワーク", "ディープラーニング", "llm", "アテンション", "自然言語処理"]
---

## 概要

Transformer は、2017 年に Google の研究チームが論文「Attention Is All You Need」で発表した、ニューラルネットワークのアーキテクチャの 1 つ。CNN や RNN と同じく、「重み付き和を活性化関数に通す」単位を積み上げた[ニューラルネットワーク](/blogs/wiki/concepts/neural-network-basics/)の一種で、RNN の再帰をやめて **Attention を中心に**系列を処理する。

全単語を一斉に計算できるので GPU で大規模に学習でき、GPT・Gemini・Qwen など現在の LLM の多くがこの構造を土台にしている。

## 詳細

### RNN の 2 つの弱点と、その解決

| RNN の弱点 | 原因 | Transformer の解決 |
| --- | --- | --- |
| 長い文脈が苦手 | 情報が隠れ状態をバケツリレーで渡るうちに薄れる | **Attention** で離れた単語同士を 1 段で直接結ぶ |
| 学習が遅い | 前の単語の計算が終わらないと次に進めない | 全単語を**並列**に処理する |

Attention 自体は Transformer 以前から RNN の補助として機械翻訳で使われていた（Bahdanau ら, 2014）。Transformer の新しさは RNN を取り除き、Attention だけで組み立てた点にある。

### 層の構成

Transformer は同じ形の層を何段も積む。1 つの層は主に 2 つの部品からなり、それぞれに残差接続と正規化が付く。

- **Self-Attention**: 同じ文の中の各単語が、ほかの単語にどれだけ注目するかを計算して情報を集める。「それ（it）」が何を指すか、といった関係をとらえる
- **Multi-Head Attention**: 注目の仕方（ヘッド）を複数並べ、違う種類の関係を同時にとらえる
- **FFN（フィードフォワード層）**: 集めた情報を単語ごとに変換する。中身は MLP そのもので、学習した知識の多くはここの重みに蓄えられると考えられている
- **Positional Encoding**: 一斉に処理すると語順が消えるので、位置を表すベクトルを単語の埋め込みに足してから入力する。元の論文は正弦波（sin / cos）を使う

### Scaled Dot-Product Attention

Self-Attention の中心の計算は `Attention(Q, K, V) = softmax(Q·Kᵀ / √d_k) · V`。

1. 単語の埋め込みに重み行列を掛けて、Query（Q）・Key（K）・Value（V）を作る
2. Q と K の内積で全単語ペアの関連度を求め、√d_k（Key の次元数）で割る
3. softmax で各行を合計 1 の重みにし、その重みで V を混ぜる

NumPy なら `scores = Q @ K.T / np.sqrt(d_k)` の 1 行で全ペアの関連度が行列として求まる。ループがないことが、並列化しやすさそのものである。

### エンコーダーとデコーダーの使い分け

- **BERT**: エンコーダー側を、隠した単語を当てる課題（マスク言語モデル）で事前学習したもの。ファインチューニングして分類などに使う
- **GPT 型**: 次の 1 トークンを予測しては文末に足す処理を繰り返して生成する。過去トークンの Key / Value を層ごとに保存して使い回すのが **KV キャッシュ**で、層が多いほど、文脈が長いほどメモリを食う

### 弱点と改良の方向

- **計算量 O(n²)**: Self-Attention は全単語ペアを計算するので、文章の長さ n の 2 乗で計算量が増える。長い文脈ではここが壁になり、一部のペアだけを計算する疎な Attention や線形 Attention などが研究されている（[Subquadratic Sparse Attention](/blogs/wiki/concepts/subquadratic-attention/)）
- **深さ = パラメータ数**: 通常は層ごとに別の重みを持つので、深くするほどモデルが大きくなる。同じ層を重み共有のまま繰り返し通して深さだけを稼ぐのが [Looped Transformer](/blogs/wiki/concepts/looped-transformer/)

## 関連ページ

- [ニューラルネットワークの基礎](/blogs/wiki/concepts/neural-network-basics/) — パーセプトロンから MLP まで。FFN の土台
- [Subquadratic Sparse Attention](/blogs/wiki/concepts/subquadratic-attention/) — O(n²) の Attention を軽くする改良
- [Looped Transformer](/blogs/wiki/concepts/looped-transformer/) — 層を繰り返して深さを稼ぐ変種
- [Kimi K3](/blogs/wiki/tools/kimi-k3/) — Attention の記憶の持ち方を変えたモデル
- [AI-For-Beginners（Microsoft）](/blogs/wiki/tools/ai-for-beginners/) — RNN から Transformer・BERT までを扱う教材

## ソース記事

- [Transformer 入門 — Attention の仕組みと RNN との違い、ニューラルネットワークとの関係](/blogs/posts/2026/11/transformer-basics/) — 2026-11-15
- [自然言語処理の基礎をやさしく解説 — Microsoft AI-For-Beginners レッスン 13〜20](/blogs/posts/2026/10/ai-for-beginners-05-nlp/) — 2026-10-02（マルチヘッドアテンション、BERT）
- [Looped Transformer とは？ 同じ層を繰り返して 4B モデルを深くする NVIDIA Dory1.0-4B](/blogs/posts/2026/11/looped-transformer-nvidia-dory/) — 2026-11-15（層の構成、FFN、KV キャッシュ）
- [Claude Opus超えの新LLM「SubQ」— Subquadratic Sparse Attentionで1200万トークンを実現、コスト1/5に](/blogs/posts/2026/05/subq-llm-subquadratic-sparse-attention/) — 2026-05-08（O(n²) の壁）
