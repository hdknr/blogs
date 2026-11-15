---
title: "Lightdash"
description: "dbt の schema.yml に書いた指標・ディメンションをそのまま探索画面にする BI ツール（コアは OSS）。ユーザー属性でテーブル・行の権限も制御する"
date: 2026-11-15
lastmod: 2026-11-15
aliases: ["Lightdash Cloud", "lightdash-tools", "Lightdash MCP"]
related_posts:
  - "/posts/2026/11/ai-native-data-platform-lightdash-mcp/"
  - "/posts/2026/11/aws-only-ai-native-data-platform/"
  - "/posts/2026/11/data-chatbot-and-data-platform/"
tags: ["dbt", "データ基盤", "セマンティックレイヤー", "mcp"]
---

## 概要

Lightdash は dbt と連携する BI ツール。dbt の `schema.yml` の `meta` に書いたメトリクスとディメンションを読み、YAML に定義した dbt モデルを原則 1 つずつ **Explore**（分析の起点）にする。定義を BI 側に二重に持たないので、[セマンティックレイヤー](/blogs/wiki/concepts/semantic-layer/)を dbt に一本化したい基盤に向く。コアは OSS で、一部の企業向け機能は別ライセンス。

## 詳細

### 権限制御

DWH を利用者に直接読ませず、Lightdash を唯一の入口にして BI 層で制御する。

- **`required_attributes`**（dbt の meta に宣言） — 属性を持たないユーザーにはテーブルを見せない
- **`user_attributes`** — ユーザーの属性値を、生成される SQL のフィルタに差し込んで行を絞る

PKSHA の事例では、PII テーブル用の属性を小さな社内ツールで「申請 → 承認 → 期限付き付与 → 自動剥奪」で管理した。業務システムと併用するなら、属性は業務システムの所属・役割から同期して二重管理を避ける。

### AI からの入口

Lightdash 組み込みの MCP は Enterprise Edition の機能（セルフホストでも Enterprise ライセンスが必要）。PKSHA の事例は OSS の [@lightdash-tools/mcp](https://github.com/yu-iskw/lightdash-tools) をベースに自前の MCP サーバーを作り、次を足した。

- ユーザー単位の OAuth（AI の見える範囲 = その人の Lightdash の範囲）
- `*_pii` を参照するクエリは行の値を返さず、件数・URL・SQL だけ返す PII ガード
- 10 種類のチャートの使いどころを返すツール、デプロイ中のソースから抜いた設定キーと enum
- チャート作成時に正しい URL とコンパイル済み SQL を必ず返す（LLM に URL を作らせない）
- 大きな Explore で 256 KB に達した応答を LLM 向けに絞り、存在しないフィールドには候補を返す

### 選定の比較

PKSHA の事例では Lightdash Cloud（現段階では費用対効果が合わない）、Looker（エンタープライズ契約が必須）、Cube + Metabase（定義が二重化）を見送り、OSS をセルフホストした。BigQuery・Redshift・Athena への接続に公式に対応しており、DWH を替えても BI 層はそのまま持ち込める。メタデータの保存には PostgreSQL（AWS なら RDS）を使う。

## 関連ページ

- [dbt](/blogs/wiki/tools/dbt/) — 定義の置き場所
- [セマンティックレイヤー](/blogs/wiki/concepts/semantic-layer/) — Lightdash が提供する層
- [AI ネイティブなデータ分析基盤](/blogs/wiki/concepts/ai-native-data-platform/) — Lightdash と MCP を組み合わせた基盤
- [MCP](/blogs/wiki/concepts/mcp/) — AI から Lightdash を操作するプロトコル

## ソース記事

- [BigQuery × dbt × Lightdash × MCP で作る AI ネイティブなデータ分析基盤：PKSHA の事例に学ぶ設計](/blogs/posts/2026/11/ai-native-data-platform-lightdash-mcp/) — 2026-11-15
- [AWS だけで作る AI ネイティブなデータ分析基盤：Aurora zero-ETL × Redshift × dbt 構成案](/blogs/posts/2026/11/aws-only-ai-native-data-platform/) — 2026-11-15
- [データ照会チャットボットはデータ分析基盤を作ってから？ツール呼び出し・Text-to-SQL・セマンティックレイヤーの関係と進め方](/blogs/posts/2026/11/data-chatbot-and-data-platform/) — 2026-11-15
