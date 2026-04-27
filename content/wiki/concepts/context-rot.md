---
title: "Context Rot（コンテキスト劣化）"
description: "会話が長くなるにつれ LLM の性能がトークン数に比例して低下する現象。能動的なセッション管理で防げる"
date: 2026-04-23
lastmod: 2026-04-23
aliases: ["Context Rot", "コンテキスト腐敗", "コンテキスト劣化"]
related_posts:
  - "/posts/2026/04/2026-04-17-claude-code-context-rot-session-management/"
tags: ["Claude Code", "コンテキスト管理", "LLM", "セッション管理", "プロンプトエンジニアリング"]
---

## 概要

コンテキストウィンドウが長くなるにつれてモデルの性能がトークン数に比例して低下する現象。古い・無関係なコンテンツが現在のタスクを妨害し、モデルの注意力が分散する。"Rot"（腐る）は Bit Rot・Code Rot と同じ、時間経過で静かに劣化する現象を指す慣用表現。

## 5 択のセッション管理

Anthropic テクニカルスタッフの Thariq 氏が整理した「ターンの終わりに行う 5 つの選択肢」:

| 選択肢 | 意味 | 向いている場面 |
|--------|------|----------------|
| **Continue** | 同じセッションで続行 | 短いタスクで文脈が整理されている |
| **Rewind**（Esc×2 / `/rewind`） | 前のメッセージに戻り再プロンプト | 誤った方向に進んだ試行錯誤を消したい |
| **`/clear`** | 白紙から新セッション | 重要情報を自分で持ち込みたい |
| **`/compact`** | セッションをモデル自身に要約させる | 手間をかけず文脈を圧縮したい |
| **Subagent** | 汚れ仕事を別エージェントに委譲 | 中間出力が大量で最終結果だけ欲しい |

## `/compact` vs `/clear` の使い分け

- **`/compact`**: モデルに要約を委ねる（lossy）。`/compact focus on the auth refactor, drop the test debugging` のように指示を添えると精度が上がる。デバッグ後に全く別タスクを指示する場面では特に精度が落ちやすい
- **`/clear`**: 手間はかかるが残るコンテキストは自分が必要と判断した情報だけになる（lossless）

## Subagent を使うパターン

「中間出力が大量に出るが、必要なのは最終結果だけ」という作業に有効。サブエージェントはクリーンな独自コンテキストウィンドウを持ち、中間の試行錯誤が親のコンテキストを汚染しない。

## 実践的な把握方法

`/usage` で自分のトークン使用量の推移を確認し、Context Rot が始まるしきい値を事前に把握しておく。鈍くなった後では遅い。

## 関連ページ

- [コンテキスト圧縮](/blogs/wiki/concepts/context-compression/) — 5 段階の圧縮カスケード
- [Claude Code](/blogs/wiki/tools/claude-code/) — Context Rot 管理コマンドの実装

## ソース記事

- [Claude Code のコンテキスト管理術 — Context Rot を防ぐ 5 つの選択肢](/blogs/posts/2026/04/2026-04-17-claude-code-context-rot-session-management/) — 2026-04-17
