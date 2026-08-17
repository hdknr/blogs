---
title: "LLMLOOP を読む: LLM生成コードを5つのフィードバックループで磨き上げる仕組み"
date: 2026-06-26
lastmod: 2026-06-26
slug: "llmloop-code-generation-feedback-loops"
draft: false
source_url: "https://github.com/hdknr/blogs/issues/1#issuecomment-4806750843"
description: "LLMが生成したコードにありがちなコンパイルエラーやテスト失敗を、5つの自動フィードバックループで反復的に直していく研究 LLMLOOP を読む。HumanEval-X での pass@10 が76.22%から90.24%に改善した仕組みと、実際の著者・出典を確認した。"
categories: ["AI/LLM"]
tags: ["llm", "Java", "コード生成", "ミューテーションテスト", "静的解析"]
---

X（旧Twitter）で「Anthropicのシニアエンジニアが書いたLoop Engineeringの論文」として紹介されていた投稿をきっかけに、元ネタの論文 **LLMLOOP** を実際に確認してみた。結論から言うと、紹介文にあった著者情報は誤りで、正体は学術機関の研究者によるソフトウェア工学の論文だった。ただし、そこで説明されている「LLMにコードを1回生成させて終わりにせず、複数のフィードバックループで磨き続ける」というアイデア自体は実証データ付きで興味深い内容だったので、正しい出典を添えて内容を整理する。

## まず出典を確認する

紹介元のポストでは論文の著者について具体的な言及があったが、実際に arXiv と ICSME（International Conference on Software Maintenance and Evolution）の情報を確認したところ、著者は次の5名で、Anthropic とは無関係だった。

- Ravin Ravi（University of Auckland）
- Dylan Bradshaw（University of Auckland）
- Stefano Ruberto（European Commission, Joint Research Centre）
- Gunel Jahangirova（King's College London）
- Valerio Terragni（University of Auckland）

論文タイトルは *"LLMLOOP: Improving LLM-Generated Code and Tests through Automated Iterative Feedback Loops"* で、arXiv に 2026年3月付で公開され（[arXiv:2603.23613](https://arxiv.org/abs/2603.23613)）、ICSME 2025 の Tool Demonstration Track に採択されている。実装は GitHub 上で公開されている（[ravinravi03/LLMLOOP](https://github.com/ravinravi03/LLMLOOP)）。

SNS で技術系の紹介ポストを見かけたとき、著者や所属先の情報は思いのほか不正確に伝わりやすい。今回のように「有名企業のエンジニアが書いた」といった権威づけは特に誤情報が混ざりやすいポイントなので、興味を持った論文は一次情報（arXiv、学会サイト）まで遡って確認するのが安全だ。

## 解決したい課題

LLM にコード生成をさせると、次のような問題が頻繁に起きる。

- コンパイルが通らない
- テストが失敗する
- 静的解析で引っかかる品質の低いコード（未使用変数、空の catch ブロックなど）
- テスト自体が甘く、バグを検出できない

これを毎回人間が手直しするのは非効率で、開発者が同じ修正作業を繰り返すことになる。LLMLOOP はこの「生成 → 検証 → 修正」のサイクルを自動化するフレームワークだ。

## 5つのフィードバックループ

LLMLOOP は Java のコードとテストを対象に、以下の5つのループを順番に回す。各ループで問題が見つかると、その内容（エラーメッセージ、失敗したテストのスタックトレース、静的解析の指摘、生き残った mutant（変異体）など）を LLM にフィードバックし、再生成させる。

![LLMLOOPの5つのフィードバックループを示した図。LLMが生成したコードはLoop1(コンパイル)、Loop2(テスト実行)、Loop3(静的解析、PMD)、Loop4(テスト生成、EvoSuite/LLM)、Loop5(mutant解析、PIT)の順に検証される。各ループで問題が見つかるとLLMにフィードバックして再生成し、最終的にコンパイル可能なコードと高品質なテストスイートを出力する。](/blogs/images/llmloop-five-loops-architecture.png)

1. **Loop 1: コンパイル** — 生成された Java コードをコンパイルし、エラーがあれば内容を LLM にフィードバックして再生成する。
2. **Loop 2: テスト実行** — 用意されたテストケースを実行し、失敗したテストとスタックトレースを LLM に渡して修正させる。
3. **Loop 3: 静的解析（PMD）** — 多言語対応の静的解析ツール PMD を使い、未使用変数や空の catch ブロックといった品質問題を検出して修正を促す。
4. **Loop 4: テスト生成** — 探索ベースのテスト生成ツール EvoSuite と LLM によるテスト生成の両方を使い、カバレッジや期待動作の観点からテストを追加する。
5. **Loop 5: mutant 解析（PIT）** — ミューテーションテストツール PIT でコードに意図的な変異（mutant）を加え、生き残った mutant（＝既存テストで検出できなかった変異）の情報を LLM にフィードバックしてテストを強化する。

なお、生成コードの実行はすべて Docker サンドボックス内で行われる。LLM が生成した未検証のコードをホスト側で直接実行しないようにする設計は、実運用を意識したフレームワークとして妥当な判断だ。

## 評価結果: HumanEval-X での pass@10

論文では HumanEval-X（Java向けの164問からなるコーディング問題集）を使い、GPT-4o-mini を各問題につき10回生成させて評価している。

| 指標 | ベースライン | LLMLOOP |
| --- | --- | --- |
| pass@1 | 71.65% | 80.85% |
| pass@10 | 76.22% | 90.24% |
| 解けた問題数（平均） | 117.5 | 132.6 |

pass@10（10回中少なくとも1回正解が出る確率）が76.22%から90.24%まで改善しており、特にコンパイルループ単体でも pass@1 を約4.75ポイント押し上げる寄与があったと報告されている。「1回生成させて終わり」にせず、フィードバックループで検証と修正を繰り返す設計が、最終的なコード品質の差になって表れている。

## 実装上のポイント

- Java / Maven ベースのフレームワークで、PMD は Maven プラグインとして組み込まれている。
- リトライ回数や温度（temperature）、解析の深さなどはコマンドラインフラグで設定可能。
- 評価では OpenAI API 経由で GPT-4o-mini を利用している。

## まとめ

紹介元のポストにあった「Anthropicのシニアエンジニアが書いた」という情報は誤りだったが、LLMLOOP 自体は「LLMの生成物を検証系と組み合わせて反復的に磨き上げる」というアイデアを、コンパイル・テスト・静的解析・テスト生成・ミューテーション解析という5つの具体的なループに落とし込み、ベンチマークで効果を示した実証研究として読む価値がある内容だった。LLM を使ったコード生成パイプラインを設計する際、どの検証ステップをどう自動化してフィードバックループに組み込むかを考えるうえで、参考になる事例だ。
