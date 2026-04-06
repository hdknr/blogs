---
title: "Redis"
description: "高速インメモリデータストア。キャッシュ・セッション・キューイング・分散ロックに利用"
date: 2026-04-06
lastmod: 2026-04-06
aliases: ["redis"]
related_posts:
  - "/posts/2023/05/redis/"
  - "/posts/2026/03/redis-fenced-lock-python/"
  - "/posts/2026/03/redis-shared-state-antipattern/"
tags: ["Redis", "キャッシュ", "データストア", "Django"]
---

## 概要

インメモリストレージで、Memcached より豊富なデータ構造（List・Set・Sorted Set・Stream）対応。Django キャッシング・Celery ブローカー・セッションストアとして広く活用。ElastiCache クラスターモードでシャーディング・高可用性確保。

## 分散ロック

Lua スクリプトによる複数コマンドのアトミック実行で競合状態を回避。フェンシングトークンで堅牢なロック実装が可能。

## 関連ページ

- [分散ロック](/blogs/wiki/concepts/distributed-lock/) — Redis を使った排他制御
- [Celery](/blogs/wiki/tools/celery/) — Redis をブローカーとして利用

## ソース記事

- [Redis](/blogs/posts/2023/05/redis/) — 2023-05
- [Redis フェンシングロック](/blogs/posts/2026/03/redis-fenced-lock-python/) — 2026-03
