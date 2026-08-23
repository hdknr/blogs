---
title: "Plane"
description: "OSS の Jira 代替プロジェクト管理ツール。セルフホスト前に確認すべき3つの落とし穴がある"
date: 2026-08-23
lastmod: 2026-08-23
aliases: ["Plane.so"]
related_posts:
  - "/posts/2026/08/plane-oss-jira-alternative-selfhost/"
tags: ["Plane", "Jira", "セルフホスト", "docker", "OSS"]
---

## 概要

OSS の Jira 代替として人気のプロジェクト管理ツール。セルフホスト可能だが、実際に運用に入る前に確認しておくべき点が 3 つある。

## セルフホスト前の3つの落とし穴

### 1. docker-compose.yml の実態は13サービス

「Docker で簡単に立つ」という紹介とは裏腹に、構成は 13 サービスに及ぶ。Celery のために **RabbitMQ が別立て**になっており、単一コンテナで済む規模ではない。運用対象として見積もる必要がある。

### 2. 無償版が Community / Commercial の2製品に分岐している

無償版が 2 系統に分かれており、**席数についての公式説明も矛盾している**。どちらを使うかで制約が変わるため、導入前に現物のライセンス表記を確認すること。

### 3. Jira 移行ツールは AGPL 版に含まれない

Jira からの移行を前提に検討している場合、これが最大の落とし穴。**移行ツールは AGPL 版に同梱されていない**。「OSS だから Jira から乗り換えられる」という前提が崩れる。

## 関連ページ

- [Celery](/blogs/wiki/tools/celery/) — Plane が非同期処理に使用

## ソース記事

- [OSS の Jira 代替 Plane をセルフホストする前に確認した3つの落とし穴](/blogs/posts/2026/08/plane-oss-jira-alternative-selfhost/) — 2026-08-09
