---
title: "Karpathyが語るAgentic Workの未来：Claude Tag・Opus 4.8・Fable 5から読む「AI同僚」時代"
date: 2026-06-27
lastmod: 2026-06-30
slug: "karpathy-anthropic-agentic-work"
draft: false
description: "KarpathyのAnthropic入社、Claude Opus 4.8のeffort controlとDynamic Workflows、Claude Tag、Fable 5/Mythos 5の輸出規制騒動を整理し、AIが組織に常駐する「Agentic Work」の流れを解説する。"
source_url: "https://github.com/hdknr/blogs/issues/1#issuecomment-4815314799"
categories: ["AI/LLM"]
tags: ["Karpathy", "Anthropic", "Claude Tag", "Claude Opus 4.8", "AIエージェント"]
---

## はじめに

2026年5月以降、Andrej Karpathy氏の発言とAnthropicの一連の発表をつなげると、AIの立ち位置が「質問に答えるチャットボット」から「組織の中で働く同僚」へ移りつつあることが見えてくる。本記事では、Karpathy氏のAnthropic入社を起点に、Claude Opus 4.8・Claude Tag・Claude Fable 5/Mythos 5という一連の発表を整理し、その先にある「Agentic Work」という流れを解説する。

## KarpathyのAnthropic入社が意味すること

2026年5月19日、OpenAI共同創業者でTeslaのAI部門を率いた経歴を持つAndrej Karpathy氏が、Anthropicに参加したと発表した([Axios](https://www.axios.com/2026/05/19/anthropic-openai-karpathy-andrej-claude)、[TechCrunch](https://techcrunch.com/2026/05/19/openai-co-founder-andrej-karpathy-joins-anthropics-pre-training-team/))。配属先はClaudeの根本的な能力を作る**pretraining**チームで、Claude自身を使ってpretraining研究を加速するチームの立ち上げにも関わるとされる。

LLMの能力は大きく「pretraining(事前学習で知識・推論力の土台を作る)」と「post-training(指示追従や安全性を調整する)」の2段階で作られる。Karpathy氏が入ったのは前者であり、次世代Claudeの基礎能力そのものに関わる動きだと言える。

## Claude Opus 4.8：「考える量」を選べるAI

Karpathy氏の入社から約1週間後の2026年5月28日、Anthropicは[Claude Opus 4.8](https://www.anthropic.com/news/claude-opus-4-8)を発表した。目立った新機能は次の2つだ。

- **effort control**: タスクごとにClaudeがどれだけ計算・推論を使うかを low / medium / high / xhigh / max の5段階から選べる仕組み（`xhigh` は high と max の間の水準で、コーディングやエージェント用途で推奨される）
- **Dynamic Workflows**: Claude Codeがタスクに応じて自らオーケストレーション用のスクリプトを組み、数百規模のサブエージェントを並列に動かす研究プレビュー機能。コードベース全体の移行やセキュリティ監査など大規模な作業を対象とする

## AIのUIは「サイト→アプリ→組織」へ：Claude Tag

2026年6月23日、AnthropicはClaudeをSlackのチームメンバーとして参加させる**Claude Tag**をベータ公開した。チームで1つのClaudeを共有し、非同期に作業を任せ、必要に応じて自発的に通知する仕組みだ。Karpathy氏はこれを「LLMのUI/UXにおける3回目の大きな再設計」と評しており、第1がWebサイト(ChatGPTなど)、第2がアプリ(Claude Codeなど)、第3が組織常駐型のAIだとしている。

Claude Tagの実務的な検証は、Enterprise環境での試用レポートを扱った既報([Claude Tag を Enterprise 環境で検証](/blogs/posts/2026/06/claude-tag-enterprise-slack-workflow/))で詳しく取り上げているので、そちらも参照してほしい。

## Fable 5とMythos 5：発表3日後の停止と輸出規制解除

2026年6月9日、Anthropicは[Claude Fable 5とClaude Mythos 5](https://www.anthropic.com/news/claude-fable-5-mythos-5)を発表した。両者は同じ基盤モデルで、Fable 5は一般利用向けに安全策を強化したモデル、Mythos 5はガードレールを一部緩和した限定提供版だ。Mythos 5は「Project Glasswing」という米政府との協業プログラムを通じて、承認済みの利用者(サイバー防御など)にのみ提供されている。

ところが発表からわずか3日後の6月12日、[Anthropicは両モデルへのアクセスを停止した](https://www.anthropic.com/news/fable-mythos-access)。米政府が国家安全保障・輸出管理上の権限を根拠に、外国籍の利用者(Anthropicの外国籍従業員を含む)へのアクセス制限を指示したためだ。国籍を正確に判別して制御するのが難しいことから、Anthropicはすべての顧客に対して両モデルを一時停止する形で対応した。指摘されたのは特定のjailbreak手法(コードベースの脆弱性修正をClaudeに依頼する形での回避)だったが、Anthropicは他の公開モデルでも同様の手法で回避可能な既知の小さな脆弱性だと反論している。

その後Anthropicは該当手法をブロックする分類器を導入し、米商務省は2026年6月30日に輸出規制を解除、両モデルへのアクセスは約2週間半ぶりに復旧した([CNN](https://www.cnn.com/2026/06/30/tech/anthropic-export-control-ban-lifted-white-house))。AIの能力が「情報を出す」段階を超えて「実際に操作する」段階に入るほど、国家安全保障や輸出管理の対象になり得ることを示した出来事だ。

## Software 3.0とAgentic Engineering

Karpathy氏はソフトウェア開発の歴史をSoftware 1.0(人間が明示的にコードを書く)、2.0(ニューラルネットワークを学習させる)、3.0(自然言語でLLMをプログラムする)という3段階で説明している。Software 3.0では、プロンプト・文脈・ツール・メモリ・評価基準そのものがプログラムの一部になる。

同氏は2025年に広めた「vibe coding」(自然言語でAIに指示しながら作る開発スタイル)に続き、「Agentic Engineering」という言葉も使い始めている。vibe codingが開発の参入障壁を下げる一方、Agentic Engineeringは要件定義・タスク分解・権限設計・レビューといった、人間側の設計力を問う工学だと位置づけられている。

## 数字で見るAI開発の加速

Anthropicは自社の分析結果として以下を公開している([When AI builds itself](https://www.anthropic.com/institute/recursive-self-improvement))。

- 2026年5月時点で、Anthropicのコードベースにマージされたコードの80%以上をClaudeが作成
- 2026年第2四半期、エンジニア1人あたりの1日のマージ量が2024年比で約8倍に増加
- 2026年3月の研究部門130人への調査では、Claude Mythos Previewにより生産性が平均約4倍になったと自己評価(ただしAnthropic自身も自己申告値であり実際の向上幅を過大評価している可能性を認めている)
- 約23万5000人・40万件のClaude Codeセッション分析([Anthropic研究](https://www.anthropic.com/research/claude-code-expertise))では、人間が計画の約70%、Claudeが実行の約80%を担うという役割分担が確認された
- 2026年4月には、Claudeが800件以上の修正でAPIエラーの一種を約1000分の1に削減した事例もあり、担当エンジニアは人間だけなら約4年かかった可能性があると見積もっている

## AI Exponentialという政策提案

Anthropicは急速な能力向上を「AI Exponential」という枠組みで捉え、[政策提案](https://www.anthropic.com/policy-on-the-ai-exponential/epf)を行っている。強力なAIシステムへの透明性義務や独立した能力評価、危険なデプロイを政府が止める権限を含む「Advanced AI Framework」と、労働市場や富の分配への影響を扱う「Economic Policy Framework」の2本柱だ。

## それでも「同僚」を無条件に信頼してはいけない

Claude TagやDynamic Workflowsが示す方向性は魅力的だが、AIエージェントには重大な制約が残る。もっともらしく間違える、権限が強いほど事故の影響が大きい、監査可能性が必要、といった課題は変わらない。Fable 5/Mythos 5の一件が示すように、能力が上がるほど権限・評価・監査・承認・停止手段を備えたシステムとして管理する必要性も増していく。

## まとめ

KarpathyのAnthropic入社、Claude Opus 4.8のeffort controlとDynamic Workflows、Claude Tag、そしてFable 5/Mythos 5をめぐる輸出規制の顛末――これらは個別のニュースに見えて、実は「AIが組織の中に常駐し、長時間・非同期に働く存在になる」という一つの流れでつながっている。競争力を左右するのは、どのモデルを使うかだけでなく、AIが働ける権限・文脈・評価の仕組みをどう設計するかにある。
