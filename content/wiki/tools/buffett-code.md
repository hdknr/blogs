---
title: "バフェット・コード"
description: "EDINET の XBRL データを活用した企業財務分析 SaaS。Web API・スプレッドシート連携・MCP Server を提供し、個人投資家から機関投資家まで対応"
date: 2026-04-15
lastmod: 2026-04-15
aliases: ["buffett-code", "バフェットコード"]
related_posts:
  - "/posts/2026/04/buffett-code-analysis/"
tags: ["財務分析", "EDINET", "XBRL", "投資", "MCP", "Python"]
---

## 概要

金融庁 EDINET に開示された有価証券報告書の XBRL データを独自にパースし、企業財務データを一括取得・分析できる SaaS。個人投資家向けのスクリーニング機能から、機関投資家・エンジニア向けの API まで幅広く対応する。

## 主な機能

### データアクセス方法

| 方法 | 概要 | 主な用途 |
|------|------|----------|
| Web UI | ブラウザでスクリーニング・比較 | 個人投資家のリサーチ |
| Web API | REST API で財務データ取得 | システム連携・自動化 |
| スプレッドシート | Google Sheets / Excel アドイン | 定型レポート作成 |
| MCP Server | AI ツールからの直接アクセス | Claude Code などとの連携 |
| Python ライブラリ | `pip install buffett_code` | データ分析・Jupyter |

### 取得できる主なデータ

- PER・PBR・ROE・ROIC 等の財務指標
- 時系列の貸借対照表・損益計算書・キャッシュフロー計算書
- スクリーニング（条件絞り込みによる銘柄抽出）

## MCP Server との連携

Claude Code などの AI ツールから直接バフェット・コードの財務データにアクセスできる MCP Server を提供。自然言語で「PBR が1倍以下でROEが10%以上の銘柄を探して」といった分析が可能になる。

## 関連ページ

- [EDINET XBRL Python ガイド](/blogs/wiki/guides/edinet-xbrl-python/) — EDINET XBRL の基礎と Python での処理
- [MCP](/blogs/wiki/concepts/mcp/) — AI ツール連携のプロトコル

## ソース記事

- [バフェット・コード徹底分析 — EDINET XBRLを活用した企業分析SaaSの全貌](/blogs/posts/2026/04/buffett-code-analysis/) — 2026-04-07
