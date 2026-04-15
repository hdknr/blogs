---
title: "GenAI-DrawIO-Creator"
description: "自然言語から draw.io XML を自動生成するフレームワーク。AWS Japan AI チームが開発し arXiv で公表。Claude 3.7 (Amazon Bedrock) を使用"
date: 2026-04-15
lastmod: 2026-04-15
aliases: ["draw.io AI生成", "drawio自動生成"]
related_posts:
  - "/posts/2026/03/genai-drawio-creator/"
tags: ["draw.io", "Amazon Bedrock", "Claude", "図解生成", "arXiv"]
---

## 概要

AWS Japan AI チームが開発した、自然言語のテキストから draw.io XML 形式のダイアグラムを自動生成するフレームワーク。論文名は「GenAI-DrawIO-Creator」（arXiv 2601.05162、2026年1月）。GitHub Trending 2位を記録した実装が公開されている。

## 評価結果

| 指標 | 結果 |
|------|------|
| 初回セマンティック精度 | 94% |
| フィードバック後の精度 | 100% |
| 平均生成時間 | 7.4 秒（手動比約5倍速） |

## 仕組み

- **LLM**: Claude 3.7（Amazon Bedrock 経由）
- **変換**: 自然言語テキスト → draw.io XML
- **フィードバックループ**: 初回生成後に精度が不十分な場合は自動再生成
- **出力**: draw.io でそのまま開ける XML ファイル

## GitHub 実装

- リポジトリ: [DayuanJiang/next-ai-draw-io](https://github.com/DayuanJiang/next-ai-draw-io)
- ライセンス: 公開済み
- 公開直後に GitHub Trending 2位を記録

## 関連ページ

- [MCP](/blogs/wiki/concepts/mcp/) — Claude との連携プロトコル
- [AI エージェント](/blogs/wiki/concepts/ai-agent/) — 自律的な図解生成の文脈

## ソース記事

- [AWS Japan AI チームが draw.io 図解自動生成を arXiv 論文化](/blogs/posts/2026/03/genai-drawio-creator/) — 2026-03-17
