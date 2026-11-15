---
title: "MCP (Model Context Protocol)"
description: "LLM が外部ツール・データベースと通信するためのオープンプロトコル"
date: 2026-04-06
lastmod: 2026-11-15
aliases: ["MCP", "Model Context Protocol"]
related_posts:
  - "/posts/2026/03/openclaw-claude-code-setup/"
  - "/posts/2026/03/sd-202604/"
  - "/posts/2026/08/digital-agency-mcp-ai-ready-data/"
  - "/posts/2026/11/ai-native-data-platform-lightdash-mcp/"
  - "/posts/2026/11/nvidia-auto-ontology/"
  - "/posts/2026/11/data-chatbot-and-data-platform/"
tags: ["mcp", "protocol", "agent", "integration"]
---

## 概要

Anthropic が主導する、AI モデルと外部システムの連携のためのオープンプロトコル。Claude Code、Cursor など主要 AI ツールで採用が進み、AWS、GitHub、Google Workspace など主要プラットフォームが MCP Server を公開。

## 特徴

- ベンダーロックインを避けた相互運用性
- ツール定義の標準化（JSON Schema ベース）
- サブミリ秒レイテンシでの動作

## AI-ready なデータ公開への応用

デジタル庁の行政手続 MCP サーバー（約 75,000 件）は、**LLM に検索・集計条件の指定だけを任せ、算術はサーバー側で実行する** 設計を採る。`dataset.yaml` による意味定義、Parquet 採用、ファジーマッチの適用範囲の限定がポイント。

詳細: [AI-ready データ設計](/blogs/wiki/concepts/ai-ready-data/)

## データ分析基盤の入口としての MCP サーバー

データ基盤で MCP サーバーを作るときの設計の要点。

- **認証はユーザー単位の OAuth** — AI が見られる範囲を、その人が BI で見られる範囲に揃える（PKSHA の Lightdash 向け自前 MCP サーバー）
- **品質はサーバー側で担保** — URL や SQL のような間違えると困るものは LLM に作らせずツールが返す。巨大な応答は LLM 向けに絞り、存在しないフィールドには候補を返して 1 往復で自己修正させる
- **機微な値は返さない** — PII テーブルを参照するクエリは件数・URL・SQL だけを返し、中身は人が自分の権限で確認する
- **読み取り専用のツールに限る** — NVIDIA Auto Ontology の MCP サーバーは `check_answerable`・`ask_question` など読み取り専用ツールだけを持ち、呼び出しはサインインしたユーザーの権限で動く
- **既製の MCP サーバー** — dbt Labs の dbt MCP サーバー、Lightdash の組み込み MCP（Enterprise）など。データ照会チャットボットでは、定型分析の経路をこうした BI / dbt の MCP サーバーに任せる

詳細: [AI ネイティブなデータ分析基盤](/blogs/wiki/concepts/ai-native-data-platform/)、[NVIDIA Auto Ontology](/blogs/wiki/tools/nvidia-auto-ontology/)

## 関連ページ

- [AI エージェント](/blogs/wiki/concepts/ai-agent/) — MCP を利用してツール連携するシステム
- [Claude Code](/blogs/wiki/tools/claude-code/) — MCP の主要クライアント実装
- [AI-ready データ設計](/blogs/wiki/concepts/ai-ready-data/) — MCP でデータを公開する設計パターン
- [Lightdash](/blogs/wiki/tools/lightdash/) / [dbt](/blogs/wiki/tools/dbt/) — MCP から定義済み指標を引く BI と変換ツール

## ソース記事

- [SD 2026年4月号](/blogs/posts/2026/03/sd-202604/) — 2026-03
- [デジタル庁の行政手続 MCP サーバーに学ぶ「LLM に計算させない」データ設計](/blogs/posts/2026/08/digital-agency-mcp-ai-ready-data/) — 2026-08-16
- [BigQuery × dbt × Lightdash × MCP で作る AI ネイティブなデータ分析基盤：PKSHA の事例に学ぶ設計](/blogs/posts/2026/11/ai-native-data-platform-lightdash-mcp/) — 2026-11-15
- [NVIDIA Auto Ontology とは — オントロジー自動生成で AI エージェントの Text-to-SQL 精度を上げる](/blogs/posts/2026/11/nvidia-auto-ontology/) — 2026-11-15
- [データ照会チャットボットはデータ分析基盤を作ってから？ツール呼び出し・Text-to-SQL・セマンティックレイヤーの関係と進め方](/blogs/posts/2026/11/data-chatbot-and-data-platform/) — 2026-11-15
