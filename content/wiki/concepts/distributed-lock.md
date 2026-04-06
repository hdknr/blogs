---
title: "分散ロック"
description: "複数サーバー環境で共有リソースへのアクセスを排他制御する仕組み"
date: 2026-04-06
lastmod: 2026-04-06
aliases: ["Distributed Lock"]
related_posts:
  - "/posts/2026/03/redis-fenced-lock-python/"
  - "/posts/2024/01/django-cache-lock/"
tags: ["Redis", "Django", "同時実行制御"]
---

## 概要

Redis-py の Lock クラスは UUID ベースのトークン管理を提供。フェンシングトークン（単調増加する数値）を実装することで、GC pause による False Positive を防止する堅牢な分散ロックが実現可能。Lua スクリプトでアトミック性を保証。

## 関連ページ

- [Redis](/blogs/wiki/tools/redis/) — 分散ロックの基盤

## ソース記事

- [Redis フェンシングロック](/blogs/posts/2026/03/redis-fenced-lock-python/) — 2026-03
- [Django Cache Lock](/blogs/posts/2024/01/django-cache-lock/) — 2024-01
