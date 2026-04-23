---
title: "エージェントハーネスとユーザーハーネス — ハーネスエンジニアリングの全体像を正しく理解する"
date: 2026-04-23
lastmod: 2026-04-23
draft: false
source_url: "https://github.com/hdknr/blogs/issues/1#issuecomment-4304066838"
categories: ["AI/LLM"]
tags: ["ハーネスエンジニアリング", "AIエージェント", "CLAUDE.md", "エージェント設計", "Claude Code"]
---

r.kagaya 氏（@ry0_kaga、AstarMinds CTO）が Zenn に公開した記事がある。「[ハーネスエンジニアリングとは何で、何ではないのか 〜作る側のハーネス、使う側のハーネス〜](https://zenn.dev/r_kaga/articles/329afdc151899f)」という記事だ。ハーネスエンジニアリングをめぐる言葉の混乱を整理し、エージェントハーネスとユーザーハーネスという2層の区分を提示している。

CLAUDE.md や Skills を書けば「ハーネスエンジニアリングをやっている」と言える。でも、それはハーネスエンジニアリングの全体ではない。この記事ではその全体像を整理する。

## そもそも「ハーネス」の定義が割れている

前提として、ハーネスエンジニアリングという言葉には統一された定義がない。同じ言葉を使いながら、各社・各人が指しているものが違う。

### 用語の来歴

「ハーネス」の原義は馬具だ。馬を馬車に繋ぎ、方向を制御し、力を伝達する装備。ソフトウェア文脈では 2020 年の [lm-eval-harness](https://github.com/EleutherAI/lm-evaluation-harness)（言語モデル評価ハーネス）が初出とされる（r.kagaya 氏による整理）。2024 年に All Hands AI / OpenHands が「エージェントハーネス」に拡張。2026 年に Mitchell Hashimoto（Terraform 創業者）が「Engineer the Harness」と命名し、OpenAI の記事で広まった。

### 各社の定義

| 誰が | 何と言っているか |
|------|-----------------|
| LangChain (Vivek Trivedy) | 「Agent = Model + Harness。モデルでなければハーネス」 |
| Anthropic | 「LLM を呼び出し、ツールコールをルーティングする制御ループ」 |
| OpenAI | 宣言的制約 + サンドボックス + スケーリング |
| Böckeler / Martin Fowler | サイバネティクス的制御。フィードフォワード × フィードバック |
| Phil Schmid (Hugging Face) | Model = CPU, Harness = OS |
| Bedi (Composio CEO) | 「システムエンジニアリングのサブセットに新しい名前をつけているだけ」 |

LangChain の「モデルでなければハーネス」は極めて広い。Anthropic の「制御ループ」はエージェント実装寄り。「そもそも新しい概念ですらない」と言う人もいる。さらにベンダー（作り手）と利用者（使い手）で意味が違うという構造的な問題もある。

## エージェントハーネスとユーザーハーネス

この混乱を整理する鍵が、エージェントハーネス（ビルダーハーネスとも）とユーザーハーネスの区別だ。Birgitta Böckeler の記事（[Martin Fowler のサイト](https://martinfowler.com/articles/harness-engineering.html)）の同心円モデルが理解しやすい。

### エージェントハーネス

エージェント構築側が実装する「モデルの周囲のインフラ」だ。Claude Code や Codex というプロダクト自体がエージェントハーネスを内包している。

具体的には以下のコンポーネントが含まれる（Akshay Pachaar が各社の知見を統合した 12 コンポーネントより）:

- Orchestration Loop
- Tools / ツールコール管理
- Memory（短期・長期）
- Context Management
- Guardrails（ガードレール）
- Verification Loops（検証ループ）

Anthropic の「harness design for long-running apps」もこちら側の話だ。Planner-Generator-Evaluator の 3 エージェント構成やコンテキストリセットの設計はエージェントを作る側の設計判断である。

### ユーザーハーネス

利用者が自分の環境に合わせてエージェントの振る舞いを制約・設定する仕組みだ。

- CLAUDE.md / AGENTS.md（ルールファイル）
- Skills（手順の標準化）
- Hooks（決定論的な行動強制）
- MCP（外部ツール連携）
- テスト・lint・型チェック（計算的センサー）
- ワークフロー定義・パイプライン化

Claude Code や Codex を使っている人がやっている「ハーネスエンジニアリング」のほとんどはここに該当する。エージェントハーネスは Claude Code 本体が内包しており、ユーザーはその上に自分の制約や仕組みを載せている。

Martin Fowler サイトの記事はユーザーハーネスを「特定のユースケースと社内システム向けにカスタマイズされた要素」と明確に定義している。この定義においてユーザーハーネスの設計もハーネスエンジニアリングの一部だ。

> ハーネスはレイヤリングであり、排他ではない。ハーネス ⊇ コンテキスト ⊇ プロンプト。

## 「CLAUDE.md 書いたらハーネスエンジニアリング」の何が足りないか

とはいえ、ユーザーハーネスに限定しても CLAUDE.md / Skills / Hooks の整備がすべてだと思って止まるのはもったいない。

[Martin Fowler サイトの記事](https://martinfowler.com/articles/harness-engineering.html)はハーネスを 2 軸で整理している。

| フェーズ | 計算的（決定論・安価・高速） | 推論的（LLM 判断・意味的） |
|--|--|--|
| **ガイド（事前）** | LSP、CLI、コードモッド | AGENTS.md、Skills、アーキテクチャドキュメント |
| **センサー（事後）** | linter、型チェック、テスト、ArchUnit | AI コードレビュー、LLM-as-judge |

CLAUDE.md や Skills はこのマトリクスの右上（**推論的ガイド**）に位置する。ユーザーハーネスの 4 象限のうちの 1 象限でしかない。

### 抜けがちな要素

**計算的センサー（フィードバック）の組み込み**

lint・型チェック・テストをエージェントの実行ループに組み込んでいるか。「CLAUDE.md に『テストを実行してください』と書く」のと「Hook で毎回強制する」のでは信頼性が全く違う。

**検証ループ（Verification Loops）**

エージェントの出力を別の仕組みで検証する構造はあるか。Boris Cherny（Claude Code creator）は[X での発言](https://x.com/bcherny/status/2007179861115511237)で「モデルに自分の仕事を検証する手段を与えると、品質が 2〜3 倍向上する」と述べている。バックプレッシャーがなければエージェントは自分に甘い。

**評価と計測**

そのハーネスが効いているかをデータで示せるか。Context Rot という構造的限界がある。効果を測らないと善意のルール追加が逆効果になりえる。

## エージェントハーネスとユーザーハーネスの間

整理してきたが、実際にはグラデーションがある。

たとえば Claude Agent SDK や Codex SDK を使って仕様から PR までのパイプラインをコードで書く場合。オーケストレーションループを自分で定義し、Generator/Evaluator の分離をクロスモデルで実装し、決定論的ステップとエージェント的自由を交互に配置する。

これは純粋なエージェントハーネス（Claude Code 本体を作る）でもなく、シンプルなユーザーハーネス（CLAUDE.md/Skills を書く）でもない。**その間にある中間レイヤー**だ。既存のエージェントハーネスの上に自前のオーケストレーションを載せている形。

エージェントハーネスを備えた SDK の活用が増えるにつれ、こういう中間レイヤーは増えていくだろう。エージェントハーネスとユーザーハーネスの境界はさらに曖昧になっていく。

## Thin Harness, Fat Skills という設計思想

Garry Tan（YC CEO）は**Thin Harness, Fat Skills** と明言している。ハーネス自体は薄く保ち（200 行程度のループ管理）、知能は Skills に、実行は決定論的ツールに委ねる。

「薄いハーネス + 厚いスキル」はユーザーハーネスにおける有力な設計思想だ。エージェントを構築する側でもない限り、重厚なオーケストレーションレイヤーを自前で書く必要はない。Claude Code 自体がエージェントハーネスを内包しているのだから。

## まとめ

| | 内容 |
|--|--|
| **エージェントハーネス** | エージェント構築側が実装するモデル周囲のインフラ（Claude Code 本体等） |
| **ユーザーハーネス** | 利用者が設定・制約する仕組み（CLAUDE.md / Skills / Hooks / MCP 等） |
| **中間レイヤー** | SDK を使った自前オーケストレーション（Generator/Evaluator 分離等） |

- ハーネスエンジニアリングには**エージェントハーネスとユーザーハーネスの 2 層**がある
- CLAUDE.md / Skills / Hooks の整備はユーザーハーネスの一部（推論的ガイド象限）であり全体ではない
- 足りがちなのは**計算的センサー・検証ループ・評価と計測**
- 各社で定義も設計思想も違う。単一の正解はない
- 「エージェントハーネス」と「ユーザーハーネス」でシンプルに語る方が伝わりやすい

r.kagaya 氏も言うように、「何がハーネスで何がハーネスじゃないか」へのこだわりよりも、「エージェントで開発する環境や設計をより良くする」ことが実務的な関心事だ。

## 参考

- [ハーネスエンジニアリングとは何で、何ではないのか（Zenn）](https://zenn.dev/r_kaga/articles/329afdc151899f) — r.kagaya
- [Harness Engineering（Martin Fowler）](https://martinfowler.com/articles/harness-engineering.html) — Birgitta Böckeler
- [Harness Engineering（OpenAI）](https://openai.com/index/harness-engineering/)
- [Agent Harness（ブログ）](https://blog.generative-agents.co.jp/entry/agent-harness)
