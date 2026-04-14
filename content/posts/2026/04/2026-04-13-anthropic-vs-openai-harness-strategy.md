---
title: "Anthropic vs OpenAI：Coding Agent の Harness 戦略はなぜ真逆なのか"
date: 2026-04-13
lastmod: 2026-04-13
draft: false
description: "Anthropic（Managed Agent）と OpenAI（Codex + Symphony）の Harness 戦略を比較。AI コーディングエージェントの設計思想がなぜ真逆なのか、両社が目指す未来像を分析する。"
source_url: "https://github.com/hdknr/blogs/issues/1#issuecomment-4239418055"
categories: ["AI/LLM"]
tags: ["anthropic", "openai", "claude-code", "codex", "agent", "Harness Engineering", "Managed Agent"]
---

AI コーディングエージェントの設計思想において、Anthropic と OpenAI は「Harness（ハーネス）」という同じキーワードを使いながら、まったく異なる方向に進んでいます。この記事では、両社の戦略の違いを整理し、それぞれが目指す未来像を考察します。

## Harness とは何か

Harness（ハーネス）とは、AI エージェントが安定して動作するための「足場」や「制御環境」を指す概念です。AI モデルが単体で完璧な出力を返すことは難しいため、ツール連携・コンテキスト管理・エラーリカバリーなどの仕組みで補強する必要があります。この補強の仕組み全体を Harness と呼びます。

両社ともこの Harness の重要性を認識していますが、そのアプローチは対照的です。

## OpenAI：AI が人間を置き換える「Harness Engineering」

OpenAI は **Harness Engineering** という概念を提唱し、2026年2月に自社の実践事例を公開しました。

### 実績：3人で100万行のコード

OpenAI の内部実験では、わずか3人のエンジニアが Codex を使い、5ヶ月間で約100万行のコードを含む製品を開発しました。アプリケーションロジック、テスト、CI 設定、ドキュメント、オブザーバビリティ、内部ツールに至るまで、すべてのコードを Codex が生成しています。

エンジニア1人あたり1日平均3.5件の PR をマージするスループットを実現し、従来の手動開発と比較して約10倍の速度で開発が進んだと報告されています。

### OpenAI Symphony：プログラマーをプロジェクトマネージャーに

2026年3月、OpenAI は **Symphony** をオープンソースで公開しました。Elixir/BEAM で構築されたこのフレームワークは、Linear などのイシュートラッカーと連携し、タスクを自動的に AI エージェントに割り当てて実行します。

Symphony の設計思想は明確です。プログラマーはコードを書く人ではなく、AI エージェントに仕事を指示するプロジェクトマネージャーになる、というものです。コマンドラインでの対話すら不要で、イシュートラッカー上で要件を記述すれば AI が実装を担当します。

OpenAI のメッセージは一貫しています。**ソフトウェアエンジニアの仕事は「コードを書くこと」から「AI が正しく動く環境を設計すること」に変わる** ということです。

## Anthropic：モデルの成長に合わせて足場を外す

Anthropic は、OpenAI とは異なるアプローチを取っています。モデルに足場（Harness）を提供しつつ、モデルが賢くなるにつれてその足場を外していくという戦略です。

### 具体例：コンテキスト管理の進化

Sonnet 4.5 の時代、モデルはコンテキストウィンドウが満杯に近づくと、タスクを急いで終わらせようとする傾向がありました。そこで Claude Code には、コンテキストが一定量を超えると自動的にリセットする特殊なロジック（Harness）が組み込まれていました。

しかし Opus 4.5 がリリースされると、モデル自体がコンテキスト管理を適切に処理できるようになり、この Harness は不要になりました。

### Claude Managed Agent：Harness をプラットフォームに吸収

この経験から Anthropic が導き出した結論が、2026年4月にリリースされた **Managed Agent** です。

Managed Agent の発想はシンプルです。モデルのアップグレードのたびに利用者側で Harness を調整するのは非効率です。ならば、Anthropic 自身がその調整を担えばよい。サンドボックス化、権限管理、ステート永続化、エラーリカバリーといった Agent 運用に必要な基盤を、API として提供する形です。

利用者はツール定義とビジネスロジックを用意するだけでよく、Agent の実行環境は Anthropic が管理します。

## 両社の戦略比較

| 観点 | OpenAI | Anthropic |
|------|--------|-----------|
| Harness の位置づけ | エンジニアが設計する環境 | プラットフォームが提供する基盤 |
| 人間の役割 | プロジェクトマネージャー | AI との協働者 |
| 製品の方向性 | Codex + Symphony | Claude Code + Managed Agent |
| 最終目標 | AI がソフトウェア開発を担う | Agent 実行基盤をプラットフォーム化する |

## 2つの未来像

OpenAI は「AI にソフトウェア開発を全面的に任せる」方向に進んでいます。Harness Engineering は、人間が AI のための環境を整え、AI が自律的にコードを書く世界を目指しています。

一方 Anthropic は「Agent の実行基盤をプラットフォームとして提供する」方向に進んでいます。利用者がツールとロジックを定義し、Anthropic がその実行環境を管理する。いわば **Agent OS** のような存在を目指しているといえます。

Claude Code が人間との協調を重視する設計であるのに対し、Codex が AI の自律性を重視する設計であることは、この戦略の違いをそのまま反映しています。

どちらのアプローチも AI がより多くの仕事を担う未来を見据えていますが、そのルートは対照的です。今後のモデル性能の進化が、どちらの賭けが正しかったかを明らかにしていくでしょう。

## 参考リンク

- [Harness engineering: leveraging Codex in an agent-first world（OpenAI）](https://openai.com/index/harness-engineering/)
- [openai/symphony（GitHub）](https://github.com/openai/symphony)
- [Get started with Claude Managed Agents（Anthropic）](https://platform.claude.com/docs/en/managed-agents/quickstart)
