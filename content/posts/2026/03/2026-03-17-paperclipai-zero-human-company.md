---
title: "Paperclip オープンソース化：0人会社を動かすエージェントオーケストレーション層"
date: 2026-03-17
lastmod: 2026-03-17
draft: false
source_url: "https://github.com/hdknr/blogs/issues/1#issuecomment-4078654700"
categories: ["AI/LLM"]
tags: ["エージェント", "オーケストレーション", "自律AI", "TypeScript", "OSS"]
---

AIエージェントを使った「0人会社（zero-human company）」のコンセプトが現実に近づいている。
[Paperclip](https://github.com/paperclipai/paperclip) は、そのためのオーケストレーション基盤としてオープンソース化されたツールだ。

## Paperclip とは

Paperclip は「ゼロヒューマン企業」を動かすためのオーケストレーション層（orchestration layer）。
人間なしで自律的に業務が進む組織を設計・運用するための基盤として設計されている。

GitHubリポジトリ: [paperclipai/paperclip](https://github.com/paperclipai/paperclip)

リリース後またたく間にスターが集まり、2026年3月時点で **53,000スター超** を記録している。

## 主な機能

Paperclip が提供する機能は次の通り:

- **組織図（Org Charts）** — エージェントの役割と階層を定義する
- **目標整合（Goal Alignment）** — 組織全体の目標を各エージェントのタスクに紐付ける
- **タスクの責任者（Task Ownership）** — どのエージェントが何を担うかを明確に割り当てる
- **予算管理（Budgets）** — エージェントが使用できるリソースや費用に上限を設定する
- **エージェントテンプレート（Agent Templates）** — 役割ごとの標準的なエージェント設定を再利用する

これらの仕組みにより、人間のオペレーターが常時介在しなくても「自律的に仕事が進む会社」を実現できる。

## クイックスタート

セットアップは `npx` で1コマンド:

```bash
npx paperclipai onboard
```

このコマンドを実行すると、初期の組織設計のガイドが始まる。TypeScript 製で、Node.js 環境があればすぐに試せる。

## なぜ注目されるのか

従来の AI エージェントフレームワークの多くは、単一エージェントまたは単純なマルチエージェントの連携を想定している。Paperclip が異なるのは、**企業・組織レベルの構造**をファーストクラスの概念として扱っている点だ。

- 単なるタスクキューではなく、**組織図と権限委譲**を持つ
- エージェント同士の目標が**整合されている**ことを保証する仕組みがある
- 予算制約により**無限ループや暴走**を防ぐ設計になっている

「AIエージェントに会社を任せる」という考えを本格的にサポートするインフラとして、エンジニアコミュニティの注目を集めている。

## 参考リンク

- [paperclipai/paperclip - GitHub](https://github.com/paperclipai/paperclip)
- [オープンソース化を告知したツイート（@dotta）](https://x.com/dotta/status/2029239759428780116)
