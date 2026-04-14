---
title: "Vibe Coding"
description: "感覚的・直感的に AI に指示を出すコーディング手法。詳細なルール不要。CS 基礎知識と文章力が成果に直結する"
date: 2026-04-06
lastmod: 2026-04-15
aliases: ["ヴァイブコーディング", "バイブコーディング"]
related_posts:
  - "/posts/2026/03/vibe-coding-skills/"
  - "/posts/2026/03/claude-md-less-is-more/"
  - "/posts/2026/03/vibe-coding-cs-writing-skills/"
tags: ["vibe-coding", "プロンプト", "開発手法", "CHI2026", "文章力"]
---

## 概要

従来の厳密なプロンプト設計から脱却し、「こんな感じ」という曖昧な指示でも AI が意図を理解する開発手法。Constitutional AI の進化により、細かいルール記述より価値観駆動の指示が有効に。実際のコードを読み書きしない開発スタイルとしても定義される。

## 成果に影響する要因（CHI2026 研究）

CHI2026 採択論文の実験から、バイブコーディングの成果を左右する要因が明らかになった。

| 要因 | 傾向 |
|------|------|
| CS 基礎知識 | あるほど成績が高い |
| 文章力 | 高いほど成績が高い |
| LLM 利用頻度 | **高いほど成績が低い**（意外な逆相関） |

### CS 基礎知識が重要な理由

コードを書かなくても、問題分解・アルゴリズム的発想・データ構造の概念が AI への指示を構造化するのに役立つ。

### 文章力が鍵となるプロセス

```
文章力が高い → プロンプトの品質が高い → アプリの出来が良い
```

### LLM ヘビーユーザーの逆説

LLM を多用するほど自分で言語化する機会が減り、プロンプト品質が下がる可能性がある。あるいは、もともと言語化が苦手な人が LLM に頼りやすい傾向があるとも考えられる。

## Vibe Hacking（対義概念）

Vibe Coding の反対側が Vibe Hacking（AI による攻撃の民主化）。攻撃者が AI にターゲットを指定するだけで脆弱性発見・エクスプロイト作成が自動化される脅威。

## 関連ページ

- [ハーネスエンジニアリング](/blogs/wiki/concepts/harness-engineering/) — Vibe Coding の品質を担保する仕組み
- [Claude Code](/blogs/wiki/tools/claude-code/) — Vibe Coding の主要環境
- [Claude の EQ](/blogs/wiki/concepts/claude-eq/) — AI が意図を補完する「脳内トレース能力」

## ソース記事

- [Vibe Coding Skills](/blogs/posts/2026/03/vibe-coding-skills/) — 2026-03
- [CLAUDE.md Less is More](/blogs/posts/2026/03/claude-md-less-is-more/) — 2026-03
- [バイブコーディングで成果を上げる人の共通点——CS基礎知識と文章力がカギ](/blogs/posts/2026/03/vibe-coding-cs-writing-skills/) — 2026-03-17
