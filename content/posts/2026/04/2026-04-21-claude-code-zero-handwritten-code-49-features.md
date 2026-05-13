---
title: "Claude Code で 2 日間に 49 PR を出荷 — 手書きコードゼロを実現する AI 開発ワークフロー"
date: 2026-04-21
lastmod: 2026-04-21
draft: false
description: "Claude Code の生みの親 Boris Cherny は 2 ヶ月以上手書きコードゼロ。2 日間で 49 PR を出荷した実績から、AI ファースト開発ワークフローの実態と開発生産性の変化を解説する。"
source_url: "https://github.com/hdknr/blogs/issues/1#issuecomment-4291432968"
categories: ["AI/LLM"]
tags: ["Claude Code", "claude", "AI開発", "vibe coding", "開発生産性"]
---

「もう 2 ヶ月以上、手でコードを書いていない」

Claude Code の生みの親であり、Anthropic でその開発を率いる Boris Cherny がそう語ったのは 2026 年 1 月のことだ。Andrej Karpathy の問いかけに応え、X への投稿でこう明かした。

> "For me personally, it has been 100% for two+ months now, I don't even make small edits by hand."

そして今、そのワークフローが広く注目を集めている。**2 日間で 49 の Pull Request を出荷**、コードは 100% AI 生成という実績が報告され、X では 30 分間のセッション動画が公開され 300 万回近く再生された。

## Boris Cherny とは

Boris Cherny は、Claude Code を 2024 年 9 月に社内の個人プロジェクトとして始めた人物だ。当初は自分のコーディングを助けるためのツールだったが、Anthropic 社内でその有効性が認められ、正式なプロダクトへと進化した。

彼は後にこう振り返っている。

> "When I created Claude Code as a side project back in September 2024, I had no idea it would grow to what it is today."

現在は Head of Claude Code として、Anthropic でツールの開発と方向性を担っている。

## 「手書きコードゼロ」の現実

Anthropic 社内での Claude Code の普及は急速だった。2025 年 11 月には全コードの 80% が手動記述だったが、2025 年 12 月には逆転し 80% が AI 生成に。その後、Boris 自身は 100% AI 生成へと到達した。

彼は、コードの修正であっても手で書くことはないと言う。Claude Code に説明すれば、エディタを開かずとも変更が完了する。

> "pretty much 100% of code at Anthropic is also AI-generated."

これは個人の極端な使い方ではなく、Anthropic 全社のエンジニアリング文化として定着しつつある。

## 2 日間で 49 PR 出荷 — それを可能にするもの

2026 年 1 月、Boris 本人が X に投稿した数字が話題になった。「前日に 22 PR、その前日に 27 PR を出荷した」というもので、2 日間で合計 49 の Pull Request を Claude Code と Opus 4.5 を使って 100% AI 生成で完遂したという内容だ。

これが現実になる背景には、以下のような変化がある。

### コードの記述がボトルネックではなくなった

Boris は語る。「コードは今やボトルネックではない」。制約は、何を作るかという判断と、AI に対する明確な指示の質に移った。

### 並列実行による高速化

Claude Code は複数の機能を並列で実装できる。1 人の開発者が複数の Claude Code セッションを起動し、それぞれが独立したタスクを同時進行できる。

### 反復の高速化

「動く最小単位」を AI に出力させて確認する → 修正指示を与える → 再出力という反復が、手でコードを書くよりはるかに速い。Boris はこの反復ループを一日に何十回も回せると言う。

## Boris Cherny のワークフロー

Anthropic のウェビナーや X の投稿から、Boris のアプローチの特徴をまとめると以下のようになる。

### 1. ほぼバニラ設定

意外なことに、Boris は Claude Code をほとんどカスタマイズしていない。

> "My setup might be surprisingly vanilla! Claude Code works great out of the box, so I personally don't customize it much."

カスタム設定や複雑なプロンプトエンジニアリングより、素のツールの能力を引き出すことを重視している。

### 2. 正確なタスク記述

Claude Code への指示は、**何をしたいか**を明確に記述することが鍵だ。曖昧な指示は修正の往復を増やすだけだと Boris は指摘する。要件を明確にしてから Claude Code に渡すことで、一発で近い出力が得られる確率が高まる。

### 3. 小さく始めて広げる

大きな機能を一度に実装させるのではなく、まず最小の動作単位から始めて段階的に機能を追加していく。Claude Code はコンテキストが明確なほど精度が上がる。

### 4. テストと検証を Claude に任せる

コードの記述だけでなく、テストの作成・実行・デバッグも Claude Code が担う。Boris はコードの「正しさ」の確認も含め、ほぼすべての工程を AI に委ねている。

## Anthropic のウェビナー

Boris Cherny 本人が Claude Code の活用方法を解説する公式ウェビナー「Claude Code for Service Delivery」が Anthropic のサイトで公開されている。チームでの導入方法や大規模な機能開発への応用など、具体的な手法を 30 分超で解説している内容だ。

また Lenny's Newsletter のポッドキャスト「Head of Claude Code: What happens after coding is solved」でも、コーディングが「解決済み」になった後の世界について語っている。

## コーディングが「解決済み」になった先

Boris は問う。「コーディングがボトルネックでなくなったら、次のボトルネックは何か？」

それは「何を作るか」という意思決定と、それを AI に正確に伝えるコミュニケーション能力だ。プログラミングのスキルセットは、コードを書く能力から AI を正しく使う能力へとシフトしている。

2 日間で 49 PR という数字は、単なる派手な話題ではない。ソフトウェア開発の開発生産性の概念そのものが書き換えられていることを示す、一つの指標だ。

## まとめ

| 指標 | 内容 |
|------|------|
| 手書きコード比率（Boris 個人） | 0%（2026 年 1 月時点で 2 ヶ月以上） |
| PR 出荷速度の事例 | 2 日間で 49 PR（22+27、Claude Code + Opus 4.5） |
| Anthropic 社内のコード比率 | ほぼ 100% AI 生成 |
| Boris のセットアップ | ほぼデフォルト設定 |

Claude Code の使い方に唯一の正解はないと Boris は強調する。しかし彼の事例は、AI ファースト開発の可能性の天井がまだ見えていないことを示唆している。

---

**参考リンク**

- [Claude Code for Service Delivery — Anthropic Webinar](https://www.anthropic.com/webinars/claude-code-service-delivery)
- [Head of Claude Code: What happens after coding is solved — Lenny's Newsletter](https://www.lennysnewsletter.com/p/head-of-claude-code-what-happens)
- [Boris Cherny on X: "100% for two+ months now"](https://x.com/bcherny/status/2015979257038831967)
- [Boris Cherny on X: "My setup might be surprisingly vanilla!"](https://x.com/bcherny/status/2007179832300581177)
