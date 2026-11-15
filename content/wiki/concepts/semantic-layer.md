---
title: "セマンティックレイヤー"
description: "「売上」「アクティブユーザー」などの指標の定義（計算式・粒度・結合）を 1 か所にまとめ、BI と AI が同じ定義で数字を出すための層"
date: 2026-11-15
lastmod: 2026-11-15
aliases: ["Semantic Layer", "メトリクスレイヤー", "Metrics Layer", "dbt Semantic Layer", "指標定義"]
related_posts:
  - "/posts/2026/11/ai-native-data-platform-lightdash-mcp/"
  - "/posts/2026/11/aws-only-ai-native-data-platform/"
  - "/posts/2026/11/data-chatbot-and-data-platform/"
  - "/posts/2026/10/ai-agent-data-platform/"
tags: ["セマンティックレイヤー", "データ基盤", "dbt", "Text-to-SQL", "AI-ready"]
---

## 概要

セマンティックレイヤーは、指標の定義（計算式・集計の粒度・結合）を 1 か所に集める層。ツールや人によって「売上」の数字がずれるのを防ぐ。AI に分析させる時代には「あると便利」ではなく**前提条件**になる。LLM が迷わず、定義済みの指標名と切り口を選ぶだけで答えられるからだ。

## 詳細

### なぜ AI 時代に重要になったか

PKSHA の事例は DIKW モデルを Data / Information / Knowledge / Insight / Narrative / Action の 6 層に広げ、AI 以後の最大の変化を「Insight 層の民主化」（誰もが AI を通じて洞察にたどり着ける）と位置づけた。その前提が、AI が迷わない明確な指標定義である。

[Text-to-SQL](/blogs/wiki/concepts/text-to-sql/) が誤るのは SQL の文法より「売上は税込か、返品を引くか」といった意味の部分。セマンティックレイヤーはこの判断を LLM から取り上げる。dbt Labs のベンチマーク（2026 年 4 月、11 問・1 データセット、実施者は製品提供元）では、定義済み指標の範囲の質問でセマンティックレイヤーが 100%、Text-to-SQL が 5〜6 割台。ただし**定義の外の質問には答えられない**ため、全体では 72.7% 対 64.5% と差が縮む。

### 定義を二重に持たない

「意味の定義を 1 か所に集める」ことが設計の核になる。PKSHA の事例が BI に [Lightdash](/blogs/wiki/tools/lightdash/) を選んだのも、[dbt](/blogs/wiki/tools/dbt/) の `schema.yml` に書いた指標をそのまま探索画面にするから。見送った候補の理由もこの観点で一貫している。

| 候補 | 見送った理由 |
|---|---|
| Lightdash Cloud | 現段階では費用対効果が合わない |
| Looker | エンタープライズ契約が必須で高コスト |
| Cube + Metabase | 定義が dbt と Cube に二重化する |

定義が 1 か所にあると、AI は定義済みの指標だけを使って分析でき、PII の制御も命名とラベルの契約に落とし込める。BI の選定・AI の挙動・ガバナンスまで、この 1 つの判断が効く。

### 実装の形

| 方式 | 定義の置き場所 | AI からの入口 |
|---|---|---|
| dbt Semantic Layer | dbt のメトリクス定義 | dbt MCP サーバー（`list_metrics`・`query_metrics` など） |
| Lightdash | dbt の `schema.yml` の `meta` | Lightdash の MCP（Enterprise）または OSS ベースの自前 MCP サーバー |
| 軽量な自前定義 | `dataset.yaml` などでカラムの意味・単位・値域 | 自前の MCP サーバー（[AI-ready データ設計](/blogs/wiki/concepts/ai-ready-data/)） |

### オントロジーとの関係

[オントロジー](/blogs/wiki/concepts/ontology/)は用語・同義語・関係まで含む業務の意味の層で、セマンティックレイヤーはそのうち**指標の計算**に特化した層と見られる。NVIDIA Auto Ontology は既存のセマンティックモデルを「置き換えず補完する」と明記している。

### 業務システムの正本と二重にしない

業務システムの帳票の数字はアプリのコードで計算されている。分析基盤で同じ指標を dbt に定義すると、計算が 2 か所に存在する。

- 帳票と同じ数字が要る質問は業務システムのツールで答え、セマンティックレイヤーの数字は「分析用」と明示する
- 代表的な案件・月で、業務 API の値と mart の値を突き合わせるテストを回す
- コードは 2 つでも、「何をどう数えるか」の仕様書は 1 つにする
- 指標と列の説明は `schema.yml` を正にし、ツールの `description` も同じ用語集から書く

### 何を定義するか

指標を作り込む前に、利用者が実際に聞いた質問を集める。データ照会チャットボットの Text-to-SQL のログに繰り返し現れる「集計・推移」が、dbt の指標に昇格させる候補になる。

## 関連ページ

- [dbt](/blogs/wiki/tools/dbt/) — 指標定義の置き場所
- [Lightdash](/blogs/wiki/tools/lightdash/) — dbt の定義をそのまま使う BI
- [Text-to-SQL](/blogs/wiki/concepts/text-to-sql/) — 定義の外の質問を受け持つ経路
- [オントロジー](/blogs/wiki/concepts/ontology/) — より広い業務の意味の層
- [AI ネイティブなデータ分析基盤](/blogs/wiki/concepts/ai-native-data-platform/) — セマンティックレイヤーを中心にした基盤設計
- [AI-ready データ設計](/blogs/wiki/concepts/ai-ready-data/) — LLM に計算させない設計パターン
- [レイクハウス](/blogs/wiki/concepts/lakehouse/) — エージェント向け基盤の 4 つの守りの「意味」

## ソース記事

- [BigQuery × dbt × Lightdash × MCP で作る AI ネイティブなデータ分析基盤：PKSHA の事例に学ぶ設計](/blogs/posts/2026/11/ai-native-data-platform-lightdash-mcp/) — 2026-11-15
- [AWS だけで作る AI ネイティブなデータ分析基盤：Aurora zero-ETL × Redshift × dbt 構成案](/blogs/posts/2026/11/aws-only-ai-native-data-platform/) — 2026-11-15
- [データ照会チャットボットはデータ分析基盤を作ってから？ツール呼び出し・Text-to-SQL・セマンティックレイヤーの関係と進め方](/blogs/posts/2026/11/data-chatbot-and-data-platform/) — 2026-11-15
- [AI エージェントのためのデータ基盤：レイクハウスを土台に「意味・費用・権限・取り消し」を設計する](/blogs/posts/2026/10/ai-agent-data-platform/) — 2026-10-13
