---
title: "Subquadratic Sparse Attention (SSA)"
description: "アテンション計算のコストをコンテキスト長の2乗からほぼ線形に削減するスパースアテンション機構。重要なk位置だけに絞ることでO(N²)→O(N×k)を実現"
date: 2026-05-20
lastmod: 2026-08-05
aliases: ["SSA", "スパースアテンション", "サブクアドラティック", "サブクアドラティックアテンション", "線形Attention", "DeltaNet", "KDA"]
related_posts:
  - "/posts/2026/05/subq-llm-subquadratic-sparse-attention/"
  - "/posts/2026/08/kimi-k3-memory-architecture/"
tags: ["アテンション", "Transformer", "LLM", "ロングコンテキスト", "スパースアテンション"]
---

## 概要

Subquadratic Sparse Attention（SSA）は、標準 Transformer の `O(N²)` アテンションを克服するために設計された **疎なアテンション機構**。各クエリトークンに対して「実際に重要な k 位置」だけを動的に選び、その部分集合のみアテンション計算を行う。k が N に対して十分小さければ計算量は `O(N × k)` でほぼ線形に近づく。

## 二次スケーリング問題

- 2017 年の Transformer 論文以降、ほぼ全ての主要 LLM はアテンション計算が `O(N²)` でスケールする
- コンテキスト長 N を大きくすると、計算量・メモリ・コストが指数的に増加
- 結果として現実の長文処理では **RAG・チャンク化・要約ループ**といった迂回策が必須となっていた

## SSA の発想

- 全 N 個と全 N 個を比較するのではなく、各クエリで **「本当に重要な k 個」を選択**してから比較
- どの位置が重要かを判断する選択器の設計が肝
- うまく機能すれば、長文を「分割せずに一度に」扱える

## SubQ における主張

- マイアミのスタートアップ Subquadratic が 2026 年 5 月に発表した LLM
- **1,200 万トークン**のコンテキスト長、FlashAttention 比 **52 倍高速**、推論コスト **$8（従来 $2,600）** を主張
- Claude Opus 4.7 超えのベンチマーク結果も提示
- ただし技術レポートが現時点で未公開、独立検証もないため懐疑論あり

## 記憶の作り替えの系譜

疎化以外にも、Attention の「記憶」の持ち方は段階的に置き換えられてきた。位置づけを整理すると次のようになる。

| 方式 | 記憶の持ち方 |
| --- | --- |
| Full Attention | すべてを保持。KV キャッシュが増え続ける |
| スパース Attention（SSA） | 重要な k 位置だけに絞る |
| 線形 Attention | 固定サイズの状態に折りたたむ |
| DeltaNet | 足すのではなく「差分で直す」 |
| KDA（Kimi Delta Attention） | 「忘れ方」を細かく分ける |

実運用のモデルは**一つの方式に賭けない**傾向がある。Kimi K3 は KDA 69 層 + Gated MLA 24 層の二段構えで、固定状態の効率と全結合の表現力を併せ持たせている。Kimi Linear 論文では 100 万トークン文脈で KV キャッシュ 75% 削減・デコード約 6 倍が報告されているが、論文のモデルは総 48B で K3 とは規模が別である。

## 関連ページ

- [Context Compression](/blogs/wiki/concepts/context-compression/) — 別アプローチでのコンテキスト圧縮
- [Context Rot](/blogs/wiki/concepts/context-rot/) — 長文化に伴う劣化問題
- [Kimi K3](/blogs/wiki/tools/kimi-k3/) — KDA を実装したモデルの詳細

## ソース記事

- [Claude Opus超えの新LLM「SubQ」— Subquadratic Sparse Attentionで1200万トークンを実現、コスト1/5に](/blogs/posts/2026/05/subq-llm-subquadratic-sparse-attention/) — 2026-05-08
- [Kimi K3 は2.8兆パラメータより「忘れ方」が新しい — KDA で読む記憶アーキテクチャと実運用コスト](/blogs/posts/2026/08/kimi-k3-memory-architecture/) — 2026-08-03
