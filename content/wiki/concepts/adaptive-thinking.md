---
title: "アダプティブ・シンキング（Claude の思考深度制御）"
description: "Anthropic が導入した Claude の思考量を動的に調整する仕組み。ユーザーから「サイレント・ダウングレード」と批判され、/effort max で元の深度に戻せる"
date: 2026-04-13
lastmod: 2026-04-13
aliases: ["adaptive thinking", "effort level", "claude thinking depth"]
related_posts:
  - "/posts/2026/04/claude-thinking-nerfed/"
tags: ["claude", "claude-code", "思考深度", "Anthropic", "llm"]
---

## 概要

Anthropic が Claude Code に導入した、タスクの複雑さに応じて思考量（extended thinking のトークン数）を自動調整する仕組み。AMD の AI ディレクターが 7,000 セッションのログ分析で思考深度の 67% 低下を発見し、「サイレント・ダウングレード」として SNS で大きな議論を呼んだ。

## 発覚の経緯

2026年4月2日、AMD シニア AI ディレクター Stella Laurenzo 氏が GitHub Issue（anthropics/claude-code#42796）を投稿。2026年1〜3月の約 6,852 セッション（234,760 ツールコール、17,871 思考ブロック）を分析した結果:

| 指標 | 変更前（1月末〜2月中旬） | 変更後（3月8日〜23日） |
|------|--------------------------|------------------------|
| 思考の中央値（文字数） | 約 2,200 文字 | 約 600 文字（67% 減） |
| 思考ブロックの割合 | 約 30% | 約 15% |

## Anthropic の説明

Anthropic は「アダプティブ・シンキング」と「エフォートレベルの変更」の2点を認めた。

- **アダプティブ・シンキング**: タスクの複雑さを判断して思考量を動的に調整する仕組みを導入
- **エフォートレベルの変更**: デフォルトの effort レベルを意図的に下げた

ユーザーへの事前告知・変更履歴の明示はなく、「サイレントな仕様変更」として批判された。

## 対処方法

### 1. エフォートレベルを最大に設定

```bash
# Claude Code セッション内で実行
/effort max
```

### 2. アダプティブ・シンキングを無効化

環境変数を設定することで、常に最大の思考深度を強制できる。

```bash
export CLAUDE_CODE_DISABLE_ADAPTIVE_THINKING=1
```

ただし、レスポンス時間の増加とトークン消費増のトレードオフがある。

## 論点

- Anthropic は思考量削減で **API コスト削減とレスポンス高速化** を実現した可能性
- 一方、複雑なタスクでの **品質低下** を招くトレードオフ
- ユーザーへの透明性の欠如が最大の問題として指摘された

## 関連ページ

- [Claude の EQ（脳内トレース能力）](/blogs/wiki/concepts/claude-eq/)
- [Claude Mythos](/blogs/wiki/concepts/claude-mythos/)

## ソース記事

- [Claude の思考深度が67%低下？AMD AIディレクターの分析が示す「サイレント・ダウングレード」問題](/blogs/posts/2026/04/claude-thinking-nerfed/) — 2026-04-13
