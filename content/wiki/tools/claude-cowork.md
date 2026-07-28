---
title: "Claude Cowork"
description: "Anthropic のデスクトップ向け製品。画面録画から Agent Skills を生成する「Record a skill」を搭載"
date: 2026-07-28
lastmod: 2026-07-28
aliases: ["Cowork", "Record a skill", "スキルの録画"]
related_posts:
  - "/posts/2026/07/claude-cowork-record-a-skill/"
tags: ["Claude", "Anthropic", "Agent Skills", "業務自動化", "Cowork"]
---

## 概要

Anthropic のデスクトップ向け製品。2026 年 7 月 21 日に **Record a skill（スキルの録画）** が追加された。画面録画で実際の作業手順を見せることで、その手順を [Agent Skills](/blogs/wiki/tools/claude-code/) 形式のスキルとして生成させられる。

「プロンプトで説明する」から「仕事を覚えさせる」への移行を狙った機能である。

## Record a skill の流れ

1. 画面録画を開始する
2. いつもの作業を実際にやってみせる
3. 録画を止めると、手順がスキルとして生成される
4. 以降はそのスキルを呼び出して同じ作業を任せる

## 何が変わるのか

従来のプロンプト運用では、暗黙知になっている手順を**言語化して説明しきる**必要があった。「どのタブを開いて、どこをコピーして、どのフォーマットに貼るか」を文章で表現するコストが、非エンジニアにとっての参入障壁になっていた。

録画であれば、**やって見せるだけで手順が残る**。言語化を経由しない分、業務移管のコストが下がる。

## 注意点：「一回の録画」と「汎用的なスキル」は違う

一度の録画は「その日の、その条件での 1 回の作業」でしかない。例外処理・条件分岐・エラー時の対応は録画に写らないため、そのままでは脆いスキルになる。

生成されたスキルは**出発点**として扱い、条件分岐や停止条件を後から書き足す運用が現実的である。これは [AIエージェント設計の5レイヤー](/blogs/wiki/concepts/ai-agent-design-layers/) でいう「スキル」横断レイヤーの設計そのものにあたる。

## 向いている業務

- 手順が固定的で、繰り返し発生する定型作業
- 複数ツールをまたぐが、判断がほとんど入らない転記・集計
- 属人化していて引き継ぎ資料が存在しない作業

逆に、毎回判断が変わる業務や、失敗コストが高い業務（送金・公開・削除）は、録画だけで自動化すべきではない。

## 背景にある Agent Skills

Record a skill が生成するのは Agent Skills 形式のスキルである。Agent Skills はすでにベンダー横断のオープン標準として整備が進んでおり、Claude Code の `.claude/skills/<name>/SKILL.md` と同じ枠組みに乗る。

## 関連ページ

- [Claude Code](/blogs/wiki/tools/claude-code/) — 同じ Agent Skills 形式を扱う CLI 環境
- [AIエージェント設計の5レイヤー](/blogs/wiki/concepts/ai-agent-design-layers/) — スキル横断レイヤーの位置づけ
- [ハーネスエンジニアリング](/blogs/wiki/concepts/harness-engineering/) — スキルを含む4層構造

## ソース記事

- [Claude Cowork「Record a skill」——プロンプトで説明する時代から、仕事を覚えさせる時代へ](/blogs/posts/2026/07/claude-cowork-record-a-skill/) — 2026-07-24
