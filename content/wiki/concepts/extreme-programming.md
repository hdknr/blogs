---
title: "エクストリーム・プログラミング（XP）"
description: "Kent Beck の XP を 5 つの価値・14 の原則・24 の実践の 3 層として捉え直し、AI がコードを安くした時代にどの部分の重みが増し、どの実践が入れ替わるかを整理する"
date: 2026-10-30
lastmod: 2026-10-30
aliases: ["XP", "Extreme Programming", "Extreme Programming Explained", "Kent Beck", "Mutual Benefit", "相互利益", "Baby Steps"]
related_posts:
  - "/posts/2026/10/extreme-programming-in-ai-era/"
  - "/posts/2026/10/replacing-mandatory-code-review/"
tags: ["エクストリーム・プログラミング", "開発手法", "AI駆動開発", "コードレビュー", "tdd"]
---

## 概要

1999 年に Kent Beck が『Extreme Programming Explained』で示した開発手法。「ペアプロと TDD」と同一視されがちだが、本体は **価値 5・原則 14・実践 24** の 3 層の体系である（この数は 2004 年の第 2 版。初版の実践は 12 個）。名前は、良いとされる実践を極端まで引き上げることに由来する（レビューが良いなら常時ペアでレビューする、など）。

AI でコードを書くコストが下がった 2026 年に読み直されており、その見立ては「**AI が XP を不要にしたのではなく、XP の中で何が重要かを入れ替えつつある**」というもの（Anton Zaides「Extreme Programming 1999->2026」）。

## 詳細

### なぜ 3 層なのか

- **価値**は方向を決めるが曖昧になりやすい（「コミュニケーション重視」と言いながら 1,000 ページの文書を書ける）
- **実践**は具体的で、やったかどうかがはっきりする。ただし状況に依存する
- **原則**が両者を橋渡しする

実践は状況依存なので AI の登場で入れ替わるが、価値と原則は**新しい実践の良し悪しを判断する物差し**として残る。これが XP を今読み直す一番の価値である。

### AI 時代に重みを増す価値

| 価値 | AI 時代の文脈 |
|---|---|
| Communication | 「AI で何でも速くなる」と信じる経営層に、ソフトウェア開発がまだ難しい理由を説明する |
| Simplicity | 書くのが安くなるほど巨大な設計を作りたくなる。LLM 自身も計画でスコープを膨らませがち |
| Feedback | これまで以上に正しい |
| Courage | 上に間違いを指摘する、無理な要求から部下を守る、不満に同調せず解決策を探す |
| Respect | 最も欠けている。AI が書いた巨大な PR を他人にレビューさせるのは敬意を欠く |

### AI 時代に重要な原則

- **Humanity** — 個人とチームのニーズの均衡。常に自分を犠牲にするやり方は続かない。チャットボット導入後に 8,500 人のサポート担当を再教育した IKEA の例
- **Mutual Benefit** — 「最も重要で最も守るのが難しい原則」。Claude で書いた読み切れない長文メッセージや、[vibe coding](/blogs/wiki/concepts/vibe-coding/) で作った巨大 PR のレビュー丸投げは、書く側の数秒を読む側の数十分に転嫁する違反例
- **Quality** — 「品質はコントロール変数ではない」。下げても速くならず、上げても遅くならない。AI slop があふれる中で誇りを持てる仕事をすること

残りの原則も有効で、とくに **Baby Steps**（正しい方向だとわかる最小の一歩）と **Redundancy**（欠陥は単一の実践では防げないので、重複しても複数の実践で捕まえる）は AI エージェントに作業を任せる指針としてそのまま使える。

### 24 の実践の 4 分類

| 分類 | 実践 |
|---|---|
| もっと重要になった（5） | Whole Team、Team Continuity、Shrinking Teams、Energized Work、Real Customer Involvement |
| 議論が分かれる（4） | Pair Programming、Code and Tests Only、Incremental Design、Test-First Programming |
| 常識になった（7） | Single Code Base、Daily Deployment、Ten-Minute Build、Continuous Integration、Root-Cause Analysis、Negotiated Scope Contract、Shared Code |
| 今も有効か問われる（8） | Stories、Weekly / Quarterly Cycle、Slack、Incremental Deployment、Sit Together、Informative Workspace、Pay-Per-Use |

議論が分かれる 4 つの論点:

- **Pair Programming** — 「すべての本番コード」が引っかかる。プロンプトを見られるのを嫌う人が多い一方、Claude とだけ作業してチーム内の学びが失われる懸念
- **Code and Tests Only** — LLM 時代には極端すぎる。CLAUDE.md・スキル・ルールがないとエージェントは毎回コードベースを調べ直す
- **Incremental Design** — 本格的な設計は LLM で簡単になった。課題は不要な「怪物」を作る誘惑に抗ってスコープを絞ること
- **Test-First Programming** — LLM に良いテストを書かせるのは難しく、テストを通すためにテスト側を書き換える問題がある（[ミューテーションテスト](/blogs/wiki/concepts/mutation-testing/)で検出力を確かめる）

Energized Work については、LLM による効率化の恩恵が働く人の生活に還元されておらず、2 倍できるようになっても労働時間はむしろ増えている、という指摘がある。

### 新しい実践を価値と原則で評価する

AI 時代に生まれつつある実践の例:

- **必須コードレビューの廃止** — レビューのボトルネックは Mutual Benefit の問題。廃止するなら役割ごとに代替手段を用意する（[必須コードレビューの代替](/blogs/wiki/concepts/code-review-alternatives/)）
- **並列化** — 4〜5 個のプロジェクトを並行できるとして、そうすべきか。Humanity の観点で改善と人間らしさの均衡を問う

## 関連ページ

- [必須コードレビューの代替](/blogs/wiki/concepts/code-review-alternatives/) — Mutual Benefit と Redundancy をレビューの再設計に当てはめる
- [Vibe Coding](/blogs/wiki/concepts/vibe-coding/) — 巨大 PR の丸投げという Mutual Benefit 違反
- [仕様駆動開発（Spec Loop）](/blogs/wiki/concepts/spec-driven-development/) — Baby Steps を AI エージェント向けに形式化した進め方
- [ミューテーションテスト](/blogs/wiki/concepts/mutation-testing/) — Test-First で生成したテストが効いているかを測る
- [ハーネスエンジニアリング](/blogs/wiki/concepts/harness-engineering/) — CI・テストで AI の出力を囲む環境

## ソース記事

- [AI 時代にこそ効くエクストリーム・プログラミング（XP）— 27 年前の価値・原則・実践を読み直す](/blogs/posts/2026/10/extreme-programming-in-ai-era/) — 2026-10-30
- [必須コードレビューをやめるなら、品質は何で担保するのか — レビューが担っていた 8 つの役割と AI 時代の代替手段](/blogs/posts/2026/10/replacing-mandatory-code-review/) — 2026-10-30
