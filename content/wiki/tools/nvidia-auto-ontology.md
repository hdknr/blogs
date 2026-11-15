---
title: "NVIDIA Auto Ontology"
description: "DB のメタデータからオントロジー（用語・SQL 属性・関係）を自動生成し、人が認定した定義で AI エージェントの Text-to-SQL を正確にする NVIDIA の OSS（Apache-2.0）"
date: 2026-11-15
lastmod: 2026-11-15
aliases: ["Auto Ontology", "auto-ontology", "NVIDIA/auto-ontology", "auto-ontology-eval", "Ossie YAML"]
related_posts:
  - "/posts/2026/11/nvidia-auto-ontology/"
  - "/posts/2026/11/business-system-data-chatbot/"
tags: ["NVIDIA", "オントロジー", "Text-to-SQL", "mcp", "AIエージェント"]
---

## 概要

[NVIDIA/auto-ontology](https://github.com/NVIDIA/auto-ontology) は、企業 DB のメタデータとクエリ履歴から[オントロジー](/blogs/wiki/concepts/ontology/)の草案を自動生成し、人が検証・認定した定義を MCP・CLI・REST API でエージェントに提供する OSS。[Text-to-SQL](/blogs/wiki/concepts/text-to-sql/) の精度をプロンプトやモデルの賢さに頼らず、「業務上の意味」と「結合の仕方」をデータ化して上げる。2026 年 4 月公開、ライセンスは Apache-2.0。既存のセマンティックモデルは置き換えず補完する位置づけ。

## 詳細

### 5 つの機能と 3 種類の定義

Discover（生成）・Ground（意味を与える）・Validate（定義と照合し出典を付ける）・Expose（MCP / CLI / API）・Learn（認定された修正を還元）。オントロジーは次の 3 種類で構成される。

| 定義 | 内容 | 防ぐ誤り |
|---|---|---|
| 用語（Terms） | 業務概念・説明・同義語と、保持する列 | 言葉と列の対応 |
| SQL 属性 | 用語の下に置くレビュー済み SQL 式（利益率など） | 指標の計算式 |
| 関係 | テーブルの結合方法（中間テーブル含む）。キーとデータから推定 | 結合の経路 |

人が認定するのは用語・説明・SQL 属性で、どのセマンティック外部キーで結合するかはコンパイルのたびに選び直される。

### 生成（セマンティックコンパイル）

カタログ取り込み（テーブル・列・キー・ビュー・クエリ履歴、pgvector に埋め込み、任意で PII 検出）→ テーブルごとのプロファイリングと外部キー候補の発見 → テーブル横断で用語ファミリー化し、**推定した結合はデータで裏付けたものだけ残す** → Postgres に保存（Ossie YAML でインポート / エクスポート可）→ `check_answerable`・`ask_question` で試しながら人が認定。

### 回答

分類 → 埋め込み検索 → 結合（経路はオントロジーから決まり、**経路探索に LLM は関与しない**。起点の選択には使う）→ 推論モデルで SQL 生成 → 静的チェックと LLM ジャッジで検査・修復（結果が空ならフィルタ値の実在を確認）→ SQL と手順を添えて回答。有効なクエリが作れなければ「答えられない」と報告する。ROAS のようにデータにない概念は、`check_answerable` で確かめて聞き返す。

### 構成と接続先

Next.js（Web UI・認証・**公開 API ゲートウェイ**、3000）、FastAPI のバックエンド（3001）と取り込みサービス（3002）、FastMCP の MCP サーバー（3003、Compose には含まれず別途起動）、PostgreSQL 17 + pgvector、任意で Vault。推論は既定で NVIDIA NIM（Nemotron 系）、`REASONING`・`NON_REASONING`・`EMBED`・`RERANK` の 4 役割ごとに OpenAI 互換エンドポイントへ差し替えられる。データソースは PostgreSQL・MySQL・Databricks・Snowflake・ClickHouse・Trino・Apache Kyuubi・HeavyDB・DuckDB・SQLite の 10 種類。

組み込むときは画面を使わず REST API（`POST /api/chat/completions`、SSE）か MCP で呼ぶのが公式の想定。Next.js を外して FastAPI を直接呼ぶのは、`x-auto-ontology-user-id` ヘッダーを無検証で信頼する・トークンやアカウント管理が Next.js にしかない・MCP も使えない、という理由で勧められない。

### 運用上の注意

- 3001・3002 はプライベートネットワークに閉じる（取り込みの ingest・delete・reset・compile に独自認証がない）
- 既定の推論先は NVIDIA API カタログ。KumoRFM を有効にするとテーブル（既定で最大 20）がホスト型サービスに上がる
- コンパイルは外部キー確認のため DWH にクエリを出す。`PREVENT_SEMANTIC_FK_DB_QUERIES=true` で止めると裏付けなしで採用する
- Vault なしだと接続用 DB パスワードは PostgreSQL に平文で保存
- **行単位の権限制御はない**（接続ごとにスキーマ・テーブルの許可リストまで）。API トークンは持ち主の権限で動き、共通トークン 1 つで呼ぶと全員が同じ権限・同じ履歴になる
- 他の利用者の回答を使い回す仕組みはなく、1 回の回答に典型的に数十秒かかる。SQL 属性は一貫性のためで、速さのためではない
- プルリクエストは受け付けていない（Issue は歓迎）

### 業務システムでの使いどころ

権限のある業務システムでは中核に据えず、全社データを見てよい監査担当などの役割にだけ開放するハイブリッドで使う。まず PoC で実際の質問 20〜50 件の正答率と DB をまたぐ質問の扱いを測る。スタックが重ければ Ossie YAML で定義だけ持ち出し、軽量な自前実装で使う道もある。価値があるのは実行環境ではなく作り込んだ定義のほう。評価には BIRD などで差を測る [auto-ontology-eval](https://github.com/NVIDIA/auto-ontology-eval) がある。

## 関連ページ

- [オントロジー](/blogs/wiki/concepts/ontology/) — このツールが生成する知識の層
- [Text-to-SQL](/blogs/wiki/concepts/text-to-sql/) — 業務システムでの位置づけとハイブリッド運用
- [MCP](/blogs/wiki/concepts/mcp/) — エージェントへの提供手段
- [DuckDB](/blogs/wiki/tools/duckdb/) — 接続できるデータソースの 1 つ

## ソース記事

- [NVIDIA Auto Ontology とは — オントロジー自動生成で AI エージェントの Text-to-SQL 精度を上げる](/blogs/posts/2026/11/nvidia-auto-ontology/) — 2026-11-15
- [Text-to-SQL vs ツール呼び出し — 権限管理のある業務システムに AI データ照会を組み込む](/blogs/posts/2026/11/business-system-data-chatbot/) — 2026-11-15
