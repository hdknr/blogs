---
title: "SuperpowersとGrill with Docs：Claude Codeエージェント設計思想の変遷"
date: 2026-07-06
lastmod: 2026-07-06
slug: "superpowers-grill-with-docs-agent-workflow"
draft: false
description: "Claude Code のスキル運用は Superpowers の詳細な実行計画から、mattpocock/skills の grill-with-docs → to-spec → implement へ。両者が前提とするエージェントの実行能力の違いから、設計思想の分岐を整理する。"
source_url: "https://github.com/hdknr/blogs/issues/1#issuecomment-4888313217"
categories: ["AI/LLM"]
tags: ["claude-code", "superpowers", "grill-with-docs", "AIエージェント", "mattpocock"]
---

## はじめに

Claude Code のエージェント運用スキルとして、一時期は [Superpowers](https://github.com/obra/superpowers) が大きな注目を集めていました。ところが最近は [Grill with Docs](https://github.com/mattpocock/skills)（正確には `mattpocock/skills` に含まれる `grill-with-docs` を起点としたワークフロー）に言及する声が増えています。

X（旧Twitter）で `@kasong2048`（書籍『React設計原理』の著者）氏がこの変化について興味深い考察を投稿していました。要約すると「両者はエージェントの発展段階が異なる時期に最適化された、別々のベストプラクティスだ」という指摘です。本記事では、この考察を出発点に、両者が前提とするエージェントの実行能力の違いを軸に設計思想の差を整理します。

## Superpowers：詳細な実行計画で長期タスクを支える

[Superpowers](https://github.com/obra/superpowers) は Jesse Vincent 氏（Prime Radiant）が開発した、Claude Code 向けの「エージェント的スキルフレームワーク兼ソフトウェア開発方法論」です。7段階ワークフローの詳細は [Superpowers — AIコーディングエージェント・フレームワーク](/blogs/posts/2026/03/superpowers-ai-coding-agent-framework/) で解説した。Anthropic 公式のプラグインマーケットプレイスからも、Claude Code のセッション内で次を実行してインストールできます（シェルではなくスラッシュコマンドです）。

```text
/plugin install superpowers@claude-plugins-official
```

Superpowers の中核には、着手前にアイデアを深掘りする `brainstorming` スキルと、承認された設計を実行可能なタスクに分解する `writing-plans` スキルがあります。`writing-plans` は作業を2〜5分単位の小さなタスクに分割し、各タスクに正確なファイルパス・完成されたコード・検証手順まで書き込みます。

この設計が前提としているのは次の2点です。

1. **エージェントは長時間タスクを一気に実行できない** ため、コンテキストが Compact（要約）された後も迷わないよう、Plan の TODO を実行のアンカーとして残す必要がある
2. **エージェントの長時間実行にはブレが生じる** ため、実行計画は「各ステップで何をするか」を細部まで具体的に書いておく必要がある

つまり Superpowers は、エージェントがまだ自律的に長い計画を安定して遂行できないという前提に立ち、「計画側で確実性を担保する」アプローチだと言えます。

## Grill with Docs：5行のGoalで足りるという前提

一方 [mattpocock/skills](https://github.com/mattpocock/skills)（Matt Pocock 氏が公開している「Skills for Real Engineers」）は、`grill-with-docs → to-spec → to-tickets → implement → code-review` という一連のスキルチェーンを提供しています。スキル15種の全体像は [mattpocock/skills](/blogs/posts/2026/06/mattpocock-skills/) と [Skills for Real Engineers](/blogs/posts/2026/04/matt-pocock-skills-for-real-engineers/) で扱いました。

`grill-with-docs` は、実装に入る前に設計案をコードベースの実際の用語や既存の `CONTEXT.md`・ADR（Architecture Decision Record）と突き合わせ、あいまいな用語や既存の決定と矛盾する箇所を一問一答形式で洗い出すスキルです（この深さ優先の質問戦略は [grill-me](/blogs/posts/2026/05/claude-code-grill-me/) で詳しく見た）。ここで用語や決定事項が固まったら、それを共有ドキュメントに書き戻します。

`implement` スキルは次のコマンドで導入できます。

```bash
npx skills add mattpocock/skills --skill=implement
```

公式ドキュメントによれば `implement` は「何を作るか決める」スキルではなく、すでに固まった spec やチケットを実行する役割に徹しています。実際に `/implement` を呼び出すと、次のような Goal に沿って動作します。

- **目標**：PRD や spec、チケットを参照する（`to-spec` / `to-tickets` が事前に用意）
- **やり方**：`tdd` スキルを内部で駆動し、テスト駆動開発で実装する
- **実行の制約**：型チェックをこまめに実行し、単体ファイルのテストをその都度流し、最後に全体テストスイートを実行する
- **通過基準**：`code-review` による最終レビューをパスする
- **完了の定義**：現在のブランチへのコミットまで行う

この目標はわずか数行ですが、それで足りるのは「実装対象のインターフェース（seam＝テストや実装が張り付く安定した境界線）が `to-spec` の段階ですでに合意されている」という前提があるからです。`implement` は seam を新たに発明せず、既に決まったものに沿ってテストを書き、実装します。

## 二つの思想の違い

| 観点 | Superpowers | Grill with Docs系 |
|---|---|---|
| 前提とするエージェントの能力 | 長時間・複雑タスクの自律実行はまだ不安定 | 目標さえ明確なら実行を安定してこなせる |
| 計画の書き方 | 各ステップを具体的に指示（2〜5分粒度） | 目標・制約・完了条件を簡潔に定義 |
| 確実性の担保先 | 実行計画（Plan）側 | 事前の合意形成（spec / seam）側 |
| 想定するタスク規模 | 長期・複雑な開発フロー全体 | 合意済みの1チケット単位の実装 |

`@kasong2048` 氏の考察が示すように、この違いは「どちらが優れているか」という優劣の話ではありません。Claude Code などのコーディングエージェントの実行能力がどの段階にあるかによって、最適な設計が変わるという話として捉えるのが妥当でしょう。エージェントの長時間タスク遂行能力やコンテキスト管理が向上するほど、詳細な逐次指示よりも「明確な目標と制約を渡すだけ」で足りる場面が増えていく、という流れです。

## まとめ

- **Superpowers**（`obra/superpowers`）は、エージェントがまだ長時間タスクを安定してこなせない前提に立ち、詳細な実行計画で確実性を担保するスキルフレームワーク
- **Grill with Docs系**（`mattpocock/skills` の `grill-with-docs → to-spec → to-tickets → implement → code-review`）は、事前に seam や仕様を固めておけば、エージェントは簡潔な目標だけで実行できるという前提に立つ
- どちらも「エージェントの実行能力に応じたベストプラクティス」であり、コーディングエージェントの進化とともに主流のワークフローも変化していくことがうかがえます

自分のチームで Claude Code のスキルを導入する際は、エージェントにどこまで自律的な判断を任せられるかを見極めた上で、どちらの思想に寄せるか（あるいは両者を組み合わせるか）を検討すると良さそうです。

## 関連記事

- [AIエージェント設計の5レイヤー](/blogs/posts/2026/07/ai-agent-design-engineering-layers/) — 「計画側で担保するか、事前合意側で担保するか」を上位のレイヤー論に接続する
- [Superpowers — AIコーディングエージェント・フレームワーク](/blogs/posts/2026/03/superpowers-ai-coding-agent-framework/) — Superpowers 側の使い方
- [mattpocock/skills](/blogs/posts/2026/06/mattpocock-skills/) — grill-with-docs 系スキルの全体像
- [Sandcastle と AFK 開発](/blogs/posts/2026/05/matt-pocock-sandcastle-afk-development/) — 自律実行能力をめぐる別角度の議論
