---
title: "SubQ"
description: "マイアミのスタートアップ Subquadratic が 2026 年 5 月に発表した LLM。Subquadratic Sparse Attention で 1200 万トークン・コスト 1/5 を主張する"
date: 2026-05-20
lastmod: 2026-05-20
aliases: ["Subquadratic", "SubQ LLM"]
related_posts:
  - "/posts/2026/05/subq-llm-subquadratic-sparse-attention/"
tags: ["SubQ", "LLM", "Subquadratic", "ロングコンテキスト", "スパースアテンション"]
---

## 概要

SubQ は、マイアミ拠点のスタートアップ **Subquadratic** が 2026 年 5 月 5 日に発表した LLM。独自のアテンション機構 **Subquadratic Sparse Attention（SSA）** によって 1200 万トークンのコンテキスト長、FlashAttention 比 52 倍高速、推論コスト $8（従来 $2,600）を主張している。

- **CEO**: Justin Dangel（5 回連続起業家）
- **CTO**: Alexander Whedon（元 Meta、元 TribeAI 生成 AI 部門長）

## 主張するスペック

- コンテキスト長 **1,200 万トークン**
- 競合比 **1,000 倍**のコンピュート削減
- 推論コスト **1/5 以下**
- Claude Opus 4.7 超えのベンチマーク結果

## 懐疑論

- **技術レポートが現時点で未公開**
- **独立検証も存在しない**
- スペック値がいずれも従来 LLM とのスケール差が極端に大きく、再現性確認待ち
- 「Claude Opus 超え」というキャッチコピーには、ベンチマーク選定バイアスの可能性

## 関連ページ

- [Subquadratic Sparse Attention (SSA)](/blogs/wiki/concepts/subquadratic-attention/) — SubQ が採用する新アテンション機構
- [Context Compression](/blogs/wiki/concepts/context-compression/) — 別アプローチでのコンテキスト圧縮

## ソース記事

- [Claude Opus超えの新LLM「SubQ」— Subquadratic Sparse Attentionで1200万トークンを実現、コスト1/5に](/blogs/posts/2026/05/subq-llm-subquadratic-sparse-attention/) — 2026-05-08
