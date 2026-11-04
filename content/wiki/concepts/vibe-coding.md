---
title: "Vibe Coding"
description: "感覚的・直感的に AI に指示を出すコーディング手法。詳細なルール不要。CS 基礎知識と文章力が成果に直結する"
date: 2026-04-06
lastmod: 2026-10-30
aliases: ["ヴァイブコーディング", "バイブコーディング"]
related_posts:
  - "/posts/2026/03/vibe-coding-skills/"
  - "/posts/2026/03/claude-md-less-is-more/"
  - "/posts/2026/03/vibe-coding-cs-writing-skills/"
  - "/posts/2026/10/spec-loop-design-first-ai-development/"
  - "/posts/2026/10/extreme-programming-in-ai-era/"
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

## チーム開発での批判

チームで使うと、Vibe Coding の失敗パターンははっきりした形をとる。

- **判断の経緯が残らない巨大な差分** — 意図だけ伝えて隙間をモデルに埋めさせると、なぜそう書いたかの記録がない大きな差分が出る。レビューは「考古学」になり、テストはうっかり省かれる。逆に完全な仕様を先に書こうとするウォーターフォールも、仕様が膨らんで変更を阻むか無視される。その中間として「次の小さな仕様だけを書き、レビューし、テスト付きで実装する」を繰り返すのが [Spec Loop](/blogs/wiki/concepts/spec-driven-development/)
- **レビューの丸投げ** — vibe coding で作った巨大 PR を開いて他人にレビューさせるのは、XP の原則 Mutual Benefit（相互利益）の違反例として挙げられる。書く側は数秒でも、読む側には数十分の負担が転嫁される（[エクストリーム・プログラミング](/blogs/wiki/concepts/extreme-programming/)）

## Vibe Hacking（対義概念）

Vibe Coding の反対側が Vibe Hacking（AI による攻撃の民主化）。攻撃者が AI にターゲットを指定するだけで脆弱性発見・エクスプロイト作成が自動化される脅威。

## 関連ページ

- [ハーネスエンジニアリング](/blogs/wiki/concepts/harness-engineering/) — Vibe Coding の品質を担保する仕組み
- [Claude Code](/blogs/wiki/tools/claude-code/) — Vibe Coding の主要環境
- [Claude の EQ](/blogs/wiki/concepts/claude-eq/) — AI が意図を補完する「脳内トレース能力」
- [仕様駆動開発（Spec Loop）](/blogs/wiki/concepts/spec-driven-development/) — Vibe Coding とウォーターフォールの中間
- [エクストリーム・プログラミング（XP）](/blogs/wiki/concepts/extreme-programming/) — 巨大 PR の丸投げを Mutual Benefit で評価する

## ソース記事

- [Vibe Coding Skills](/blogs/posts/2026/03/vibe-coding-skills/) — 2026-03
- [CLAUDE.md Less is More](/blogs/posts/2026/03/claude-md-less-is-more/) — 2026-03
- [バイブコーディングで成果を上げる人の共通点——CS基礎知識と文章力がカギ](/blogs/posts/2026/03/vibe-coding-cs-writing-skills/) — 2026-03-17
- [Spec Loop — 次の小さな仕様だけを書いて回す、AI エージェント向け仕様駆動開発フレームワーク](/blogs/posts/2026/10/spec-loop-design-first-ai-development/) — 2026-10-25
- [AI 時代にこそ効くエクストリーム・プログラミング（XP）— 27 年前の価値・原則・実践を読み直す](/blogs/posts/2026/10/extreme-programming-in-ai-era/) — 2026-10-30
