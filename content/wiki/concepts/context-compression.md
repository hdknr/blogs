---
title: "コンテキスト圧縮"
description: "LLM の会話が長くなった際にコンテキストウィンドウを管理する戦略群"
date: 2026-04-06
lastmod: 2026-04-06
aliases: ["Context Compression", "コンテキスト管理"]
related_posts:
  - "/posts/2026/04/claude-code-context-compression/"
tags: ["LLM", "claude-code", "コンテキスト"]
---

## 概要

LLM のコンテキストウィンドウには上限がある。会話が長くなると古い情報を捨てるか圧縮する必要があり、その戦略設計は AI コーディングエージェントの中心課題。

## Claude Code の5つの圧縮戦略

軽量な処理から順にカスケードとして適用される:

1. **Microcompact** — 古いツール結果を時間ベースで消去（API 呼び出し不要）
2. **Context Collapse** — 会話の部分範囲を要約で置換（直近の文脈は保持）
3. **Session Memory** — 重要情報を別ファイルに永続化（`/compact` 手動実行時にも使用）
4. **Full Compact** — 履歴全体を包括的に要約（auto-compact: 約33Kトークンのバッファ残し）
5. **PTL Truncation** — 最も古いメッセージ群を切り落とす最終手段

## カスケードの流れ

```
ツール結果バジェッティング → Microcompact → Context Collapse → Full Compact → PTL Truncation
```

## 実用的な対策

- タスクの区切りで `/compact` を手動実行する
- 圧縮で失われたくない情報は `CLAUDE.md` に記載する
- 異なるタスク間では `/clear` でリセットする
- 大きな出力はサブエージェントに委任する

## 関連ページ

- [Claude Code](/blogs/wiki/tools/claude-code/) — この圧縮戦略を実装しているツール
- [LLM Wiki パターン](/blogs/wiki/concepts/llm-wiki-pattern/) — 知識の永続化という関連アプローチ

## ソース記事

- [Claude Code のコンテキスト圧縮戦略 — ソースコードから見える5つのアプローチ](/blogs/posts/2026/04/claude-code-context-compression/) — 2026-04-02
