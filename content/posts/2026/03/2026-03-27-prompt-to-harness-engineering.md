---
title: "Prompt Engineering から Harness Engineering へ: AI エンジニアリングの進化と「仕組みの設計力」の時代"
date: 2026-03-27
lastmod: 2026-03-27
draft: false
description: "Prompt Engineering → Context Engineering → Harness Engineering。AI エンジニアリングの3つのパラダイムの進化を、OpenAI・Anthropic・Martin Fowler の事例とともに解説。"
source_url: "https://github.com/hdknr/blogs/issues/1#issuecomment-4140837410"
categories: ["AI/LLM"]
tags: ["Harness Engineering", "Context Engineering", "agent", "openai", "anthropic"]
---

AI エンジニアリングの中心概念が急速に変化している。2022年の「Prompt Engineering」から2025年の「Context Engineering」を経て、2026年は「Harness Engineering」の年になった。Anthropic、OpenAI、そして Martin Fowler まで、業界のキープレイヤーが揃ってこの概念を公式に取り上げている。

## 3つの時代: プロンプトからハーネスへ

### Prompt Engineering（2022〜）

ChatGPT の登場とともに広まった最初のパラダイム。LLM に対して**どんな言葉で指示するか**が品質を左右する、という考え方だ。Few-shot、Chain-of-Thought、Role Prompting といったテクニックが次々と開発された。

焦点は「1回のリクエストにおける入力テキストの最適化」にあった。

### Context Engineering（2025〜）

2025年中盤、Shopify CEO の Tobi Lutke が X への投稿をきっかけに「Context Engineering」という用語が急速に広まった。LangChain や Anthropic も相次いで解説記事を公開し、業界標準の概念として定着した。

Prompt Engineering が「何を言うか」に注目していたのに対し、Context Engineering は**「LLM に何を見せるか」を動的に制御するシステム**を設計する。RAG（Retrieval-Augmented Generation）、ツール呼び出し、メモリ管理など、LLM の入力コンテキスト全体をエンジニアリングの対象とする発想だ。

### Harness Engineering（2026〜）

2026年に入り、AI エージェントの実用化が本格化するなかで、Context Engineering をさらに拡張した「Harness Engineering」が登場した。

Context Engineering が「LLM に何を見せるか」を扱うのに対し、Harness Engineering は**エージェントの実行環境全体** —— 役割分担、フィードバックループ、品質検証、セッション管理まで含めた制御構造を設計する。

「ハーネス（harness）」は馬具の意味で、強力な馬（= AI モデル）を制御し、安定した成果を引き出すための仕組み全体を指す。

## 業界キープレイヤーの動き

### OpenAI: Codex チームの実践（2026年2月）

OpenAI は2026年2月、公式ブログで「[Harness engineering: leveraging Codex in an agent-first world](https://openai.com/index/harness-engineering/)」を公開した。

5ヶ月間の内部実験で、小規模なエンジニアチームが Codex エージェントを通じて**約100万行のコードを含むベータ製品を構築**した。手書きのソースコードはゼロだ。チームの役割は「コードを書く」から「エージェントが確実に正しいコードを生産する環境を設計する」へとシフトした。

同時に公開された「[Unlocking the Codex harness: how we built the App Server](https://openai.com/index/unlocking-the-codex-harness/)」では、ハーネスの具体的な実装アーキテクチャが詳述されている。

### Anthropic: ハーネス設計によるベンチマーク改善（2026年3月）

Anthropic は3月に「[Harness design for long-running application development](https://www.anthropic.com/engineering/harness-design-long-running-apps)」を公式エンジニアリングブログで公開した。

注目すべきは、**同じモデルでもハーネスの有無でベンチマーク結果が大幅に変わる**という実証だ。ハーネス（スキャフォールド）の違いだけで20ポイント以上のスコア差が生じ、「中位モデル＋適切に設計されたハーネス」が「最先端モデル＋未整備なハーネス」を上回るケースすらある。

Anthropic の事例では、Planner・Generator・Evaluator の3エージェント構成で、Claude が6時間かけてフルスタックアプリケーションを自律構築している。詳細は「[Anthropic の3エージェント・ハーネス設計](/posts/2026/03/2026-03-27-anthropic-harness-design-three-agents/)」を参照。

### Martin Fowler / Birgitta Böckeler: ソフトウェアエンジニアリングの視点（2026年2月）

Thoughtworks の Distinguished Engineer である Birgitta Böckeler が、[martinfowler.com で解説記事](https://martinfowler.com/articles/exploring-gen-ai/harness-engineering.html)を公開した（2026年2月17日）。Martin Fowler 自身も X で「OpenAI の『Harness Engineering』は AI 対応ソフトウェア開発の重要なフレーミングだ」と紹介している。

Böckeler はハーネスを「AI エージェントを制御下に置くためのツールとプラクティス」と表現し、OpenAI の記事を分析して3つの構成要素を整理した:

1. **Context Engineering**: コードベース内のナレッジベースの継続的な整備と、動的コンテキストへのアクセス
2. **アーキテクチャ上の制約**: LLM ベースのエージェントだけでなく、決定論的なカスタムリンターや構造テストによる監視
3. **ガベージコレクション**: 定期実行エージェントによるドキュメントの不整合やアーキテクチャ違反の検出

martinfowler.com で取り上げられたことは、Harness Engineering が単なるバズワードではなく、**ソフトウェアエンジニアリングの正統な拡張**として認知されつつあることを示している。

## なぜ「仕組みの設計力」が決定的になったのか

3つのパラダイムの進化を俯瞰すると、焦点が一貫して「外側」に広がっていることがわかる。

| パラダイム | 焦点 | 制御対象 |
|---|---|---|
| Prompt Engineering | 入力テキスト | 1回のリクエスト |
| Context Engineering | 入力コンテキスト全体 | RAG・ツール・メモリ |
| Harness Engineering | 実行環境全体 | エージェントの役割・ループ・検証 |

モデルの性能が一定水準を超えた今、差を生むのは**モデルの外側をどう設計するか**だ。同じ Claude Opus でも、ハーネスの設計次第でベンチマーク結果が劇的に変わるという Anthropic の実証がそれを裏付けている。

## 実務への示唆

Harness Engineering は大規模チーム専用の概念ではない。個人開発者でも以下のような「ハーネス」を日常的に構築できる。

- **CLAUDE.md / AGENTS.md**: エージェントへの指示書設計（ポインタ設計で50行以下に）
- **Hooks**: ファイル編集のたびにリンター・フォーマッターを自動実行
- **計画→実行の分離**: いきなりコードを書かせず、まず計画を出力させてレビュー
- **E2E テスト**: エージェントの出力を決定論的に検証する仕組み
- **セッション間の状態管理**: Git ログや構造化された進捗ファイルで前回の状態を引き継ぐ

具体的な実装パターンについては「[Harness Engineering ベストプラクティス 2026](/posts/2026/03/2026-03-09-harness-engineering/)」も参照してほしい。

プロンプトを磨くことは依然として重要だが、それだけでは不十分な時代に入った。モデルの力を最大限に引き出すには、その外側に「仕組み」を組む必要がある。

## 参考リンク

- [Harness engineering: leveraging Codex in an agent-first world](https://openai.com/index/harness-engineering/) — OpenAI 公式ブログ（2026年2月）
- [Unlocking the Codex harness: how we built the App Server](https://openai.com/index/unlocking-the-codex-harness/) — OpenAI 公式ブログ（2026年2月）
- [Harness design for long-running application development](https://www.anthropic.com/engineering/harness-design-long-running-apps) — Anthropic 公式エンジニアリングブログ（2026年3月）
- [Harness Engineering](https://martinfowler.com/articles/exploring-gen-ai/harness-engineering.html) — Martin Fowler / Birgitta Bockeler
- [The rise of "context engineering"](https://blog.langchain.com/the-rise-of-context-engineering/) — LangChain ブログ
- [元ツイート](https://x.com/kawai_design/status/2037313908969750831) — KAWAI 氏（@kawai_design）
