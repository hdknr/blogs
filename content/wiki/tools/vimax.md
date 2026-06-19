---
title: "ViMax"
description: "香港大学 HKUDS が開発したオープンソースのマルチエージェント動画生成フレームワーク。1行のアイデアから脚本・絵コンテ・動画までを自動生成する"
date: 2026-05-20
lastmod: 2026-05-20
aliases: ["Vimax", "Video Maximizer", "HKU ViMax"]
related_posts:
  - "/posts/2026/05/vimax-hku-agentic-video-generation/"
tags: ["ViMax", "動画生成", "マルチエージェント", "オープンソース", "RAG", "Python"]
---

## 概要

ViMax（**Vi**deo **Max**imizer）は、香港大学データインテリジェンスラボ（HKUDS）が開発したオープンソースのマルチエージェント動画生成フレームワーク。1 行のテキストアイデアを入力するだけで、脚本執筆・絵コンテ設計・キャラクター管理・最終動画レンダリングまでをエンドツーエンドで自律実行する。

- **GitHub**: [HKUDS/ViMax](https://github.com/HKUDS/ViMax)
- **ライセンス**: MIT
- **言語**: Python 3.12+
- **Stars**: 3,800+（2026 年 5 月時点）

## アーキテクチャ

「Director（監督）・Screenwriter（脚本家）・Producer（プロデューサー）・Video Generator（映像生成）をひとつに」という設計コンセプト。各役割をエージェントとして分離し、RAG をまたぐマルチエージェント構成にしている。

## 4 つの生成モード

- **Idea2Video**: 1 行のテキストアイデアから動画一括生成
- **Novel2Video**: 小説テキストから動画化
- **Script2Video**: 既存脚本から映像生成
- **AutoCameo**: キャラクター一貫性を保ったままカメオ出演を自動挿入

## 関連ページ

- [Multi-Agent Coordination Patterns](/blogs/wiki/concepts/multi-agent-coordination-patterns/) — マルチエージェント設計
- [Video Use](/blogs/wiki/tools/video-use/) — 動画系 AI ツール
- [Arcads](/blogs/wiki/tools/arcads/) — AI 動画広告ツール

## ソース記事

- [ViMax — 1行のアイデアから脚本・絵コンテ・動画まで自動生成する香港大学発マルチエージェントフレームワーク](/blogs/posts/2026/05/vimax-hku-agentic-video-generation/) — 2026-05-11
