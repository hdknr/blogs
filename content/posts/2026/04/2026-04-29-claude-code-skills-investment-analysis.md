---
title: "Claude Code Skills × 投資分析シリーズ — スクリプト自動化からマルチ AI エージェントへの進化"
date: 2026-04-29
lastmod: 2026-04-29
slug: "claude-code-skills-investment-analysis"
draft: false
source_url: "https://github.com/hdknr/blogs/issues/1#issuecomment-4340870228"
categories: ["AI/LLM"]
tags: ["claude-code", "投資分析", "マルチエージェント", "python", "GraphRAG"]
---

ChatGPT に「Claude Code で株ツールを作っている人の事例を調べてくれ」と聞いて見つかった記事シリーズが話題になっている。Zenn の [okikusan](https://zenn.dev/okikusan) さんによる **Claude Code Skills × 投資分析シリーズ** は、試行錯誤の過程が詳らかに書かれており、Claude Code を使った個人開発の実践例として非常に参考になる。

本記事ではこのシリーズ（Vol.1〜5）の内容を紹介する。

## シリーズ概要

[Claude Code Skills × 投資分析シリーズ — 記事一覧](https://zenn.dev/okikusan/articles/23041c3800a927)

「自然言語で話しかけるだけで、銘柄探索・分析・ポートフォリオ管理・リスク評価が自動実行される」投資分析システムを Claude Code Skills を使って構築・進化させてきたシリーズ。

全 5 本の記事で、**スクリプトによる自動化** から始まり、**GraphRAG による学習**、**高度な分析機能の追加**を経て、最終的には **6 つの AI エージェントが自律的に連鎖するマルチエージェントオーケストレーション**、さらには **4 つの異なる AI が反証し合う DeepThink** へと進化している。

## Vol.1: 株スクリーニングを自動化した話

**テーマ: スクリプトで自動化**

[記事リンク](https://zenn.dev/okikusan/articles/eacc59ca26e566)

Python × yfinance × Claude Code Skills で、株式スクリーニングからポートフォリオ管理まで投資分析を自動化した第一弾。4 つのスクリーナーエンジンとヘルスチェック機能を実装している。

主な実装内容:

- yfinance を使った株価データ取得
- 4 つのスクリーナーエンジン（QueryScreener・PullbackScreener・AlphaScreener・ValueScreener）
- ポートフォリオのヘルスチェック機能
- Claude Code Skills による自然言語インターフェース

## Vol.2: 使うほど賢くなる投資分析 AI

**テーマ: GraphRAG で学習**

[記事リンク](https://zenn.dev/okikusan/articles/37dfaec84afec2)

Neo4j ナレッジグラフを導入し、過去の分析・売買・投資メモを蓄積することで、使うほど文脈を踏まえた判断ができるようになる仕組みを実装。

GraphRAG（Graph Retrieval-Augmented Generation）の活用により、単なるスクリプト実行から「記憶を持つ AI」への進化を実現している。

## Vol.3: 処方箋エンジン・逆張り検出・銘柄クラスタリング

**テーマ: 分析機能を高度化**

[記事リンク](https://zenn.dev/okikusan/articles/655df6dd36dfd4)

Vol.2 までの基盤に 7 つの新機能を追加した機能拡張編（主要 3 点を紹介）:

- **PF 処方箋エンジン**: ポートフォリオの課題を診断して改善提案
- **逆張りシグナル検出**: 過売り・過買いの銘柄を自動検出
- **コミュニティベースの銘柄クラスタリング**: 類似銘柄をグルーピング

## Vol.4: ゼロから再設計。マルチ AI エージェントが自律的に動く投資アシスタントに

**テーマ: Agentic AI Pattern で自律化**

[記事リンク](https://zenn.dev/okikusan/articles/2a3ec2999d6581)

Vol.1〜3 の構造を抜本的に再設計し、完全リニューアル。6 つの AI エージェントが連鎖して自律的に動くマルチエージェントオーケストレーションを実現:

| エージェント | 役割 |
|---|---|
| Screener | 銘柄スクリーニング |
| Analyst | 詳細分析 |
| Health Checker | ポートフォリオ健全性チェック |
| Researcher | 情報収集 |
| Strategist | 投資戦略立案 |
| Reviewer | 総合レビュー |

マルチ LLM（GPT / Gemini / Claude）によるレビュー、自律修正ループ、GraphRAG による文脈注入を実装。「6 つのエージェントが連鎖して動く」設計は、Claude Code Skills の真髄を示す実装例と言える。

## Vol.5: 4 つの AI に反証させて考え直す DeepThink を実装【最新】

**テーマ: マルチ LLM Swarm で深掘り**

[記事リンク](https://zenn.dev/okikusan/articles/254deb4b0ddf10)

通常モード（Few-shot）は 1 回答えて終わりだが、DeepThink（Zero-shot）は異なる。結論を出した後に 4 つの AI（Claude / GPT / Gemini / Grok）が同時にレビューし、反証→修正→再評価を収束するまで自律ループする。

特徴:

- **2 層モデル**: インフラ層固定 + 推論層動的割当
- **役割分担**: 各 AI の得意・不得意に応じた役割分担
- **出力構成**: エグゼクティブサマリー + Swarm 議論の統合 + 詳細の 3 部構成

## 技術スタック

シリーズで使用している技術スタック（原記事記載の値）:

| 分類 | 技術 |
|---|---|
| ランタイム | Claude Code（claude-sonnet-4-6） |
| 外部 LLM | gpt-5.4（OpenAI）、gemini-3.1-pro-preview（Google）、Grok（xAI） |
| データ取得 | yfinance（Yahoo Finance API） |
| リアルタイム情報 | Grok API（X センチメント・ニュース）、Gemini Grounding（Google 検索） |
| ナレッジグラフ | Neo4j（GraphRAG） |
| 言語 | Python 3.10+ |

## リポジトリ

- **Vol.4（現行）**: [okikusan-public/stock_skills_2](https://github.com/okikusan-public/stock_skills_2)
- **Vol.1〜3（旧）**: [okikusan-public/stock_skills](https://github.com/okikusan-public/stock_skills)

Vol.4 でアーキテクチャを完全リニューアルしたため、新リポジトリとして公開されている。`.claude/` ディレクトリ内に skills・agents・tools が整理されており、Claude Code Skills の実装例として参考にしやすい構成になっている。

## まとめ

このシリーズは Claude Code Skills を実際の業務課題（投資分析）に適用し、Vol.1 の単純なスクリプト自動化から Vol.5 のマルチ LLM Swarm まで、段階的に進化させていく過程が記録されている。

特に注目すべきは以下の 2 点:

1. **試行錯誤の過程が詳細に記録されている** — 完成形だけでなく、なぜこのアーキテクチャを選んだか、どこで躓いたかが分かる
2. **実用的なドメイン（投資分析）への適用** — 抽象的なデモではなく、実際に使っているシステムを公開している

Claude Code Skills を使った個人開発の参考として、シリーズ全体を通読する価値がある。
