---
title: "バフェット・コード徹底分析 — EDINET XBRLを活用した企業分析SaaSの全貌"
date: 2026-04-07
lastmod: 2026-04-07
draft: false
categories: ["Web開発"]
description: "EDINETのXBRLデータを基盤にした企業分析SaaS「バフェット・コード」を徹底分析。Web API、スプレッドシート連携、MCP Server、OSSライブラリなど、無料プランの範囲からPython実装例まで解説"
tags: ["バフェット・コード", "EDINET", "Python", "財務分析", "MCP"]
---

[前回の記事](/posts/2026/04/2026-04-06-edinet-xbrl-python/)で EDINET の XBRL データを Python で扱う方法を紹介した。今回は、その仕組みを活用して構築されている企業分析サービス「[バフェット・コード](https://www.buffett-code.com/)」を分析し、何ができるのかを網羅的にまとめる。

## バフェット・コードとは

バフェット・コードは、EDINET（有価証券報告書）と TDNET（適時開示）の XBRL データをパースし、企業の財務情報をワンストップで分析できる SaaS サービスだ。バフェットコード株式会社が開発・運営している。

データパイプラインの流れは以下の通り:

1. EDINET / TDNET から XBRL ファイルを取得
2. XBRL をパースして RDB に格納
3. 過去データと株価を組み合わせて財務指標を算出
4. スクリーニング・比較用のデータセットを更新

このパイプラインの XBRL パース部分に、前回紹介した [edinet_xbrl](https://github.com/BuffettCode/edinet_xbrl) ライブラリが使われている。

## Web アプリケーションでできること

バフェット・コードの Web アプリ（[buffett-code.com](https://www.buffett-code.com/)）では以下の機能が利用できる。

### 企業分析

- **財務データの閲覧**: B/S（貸借対照表）、P/L（損益計算書）、C/S（キャッシュフロー計算書）を一覧表示
- **企業概況**: 設立日、上場日、事業内容などの基本情報
- **役員一覧**: 取締役・監査役の情報
- **大株主情報**: 四半期ごとの大株主構成
- **セグメント情報**: 事業セグメント別の業績データ
- **類似企業の表示**: 同業他社の自動提案

### スクリーニング・比較

- **条件検索**: 財務指標（PER、PBR、ROE 等）でフィルタリング
- **企業比較**: 複数企業の財務データを横並びで比較
- **株主検索**: 特定の株主が保有する企業を検索

### 資料検索

- **横断検索**: EDINET・TDNET の資料に加え、各社の決算説明資料や統合報告書も横断的に検索
- **CSV ダウンロード**: 年間業績や各種指標のダウンロード

## Web API でできること

バフェット・コードは REST API（v4）を提供しており、プログラムから財務データにアクセスできる。API の利用には有償契約が必要だが、テスト用 API キーも用意されている。

### API のカテゴリ

#### 1. 企業・銘柄系 API

```bash
# 企業情報の取得（company_id には銘柄コード、例: 2801 を指定）
curl "https://api.buffett-code.com/api/v4/jp/companies/{company_id}" \
  -H "x-api-key: YOUR_API_KEY"
```

- 企業・銘柄情報の取得
- 企業概況の取得
- 類似企業一覧の取得
- 役員一覧の取得
- 米国企業の情報取得にも対応

#### 2. 財務数値・株価指標系 API

期間の粒度に応じて異なるデータを取得できる:

| 粒度 | 取得できるデータ |
|------|-----------------|
| 日次 | 株価指標、予想値関連指標 |
| 週次 | β（ベータ）などの統計値 |
| 月次 | β（ベータ）などの統計値、KPI |
| 四半期 | 有報・四半期報告書の財務数値、テキスト情報、大株主、セグメント |
| 決算年度 | 業績予想の修正履歴 |

```bash
# 四半期財務データの取得
curl "https://api.buffett-code.com/api/v4/jp/companies/{company_id}/quarterly/2025Q1" \
  -H "x-api-key: YOUR_API_KEY"
```

#### 3. 資料系 API

- 有価証券報告書や適時開示の検索
- 資料のダウンロードリンク生成
- EDINET・TDNET の資料に加え、決算説明資料・統合報告書も対象

#### 4. メタデータ API / データセット API

- 全企業・銘柄の一覧と更新日の取得
- 大規模なファイルベースのデータ一括ダウンロード（機械学習用途に最適）

### テスト用 API キー

契約不要で試せるテスト用 API キーが公開されている:

```
sAJGq9JH193KiwnF947v74KnDYkO7z634LWQQfPY
```

このキーはテスト専用で、レートリミットが適用される。制限事項:

- 日本企業: 銘柄コード末尾が `01` の企業のみアクセス可能
- 米国企業: Alphabet Inc.（CIK: `0001652044`）のみ
- 資料系 API: アクセス不可

## スプレッドシート連携

### Google スプレッドシートアドオン

[Google Workspace Marketplace](https://workspace.google.com/marketplace/app/%E3%83%90%E3%83%95%E3%82%A7%E3%83%83%E3%83%88%E3%83%BB%E3%82%B3%E3%83%BC%E3%83%89/671399271704) からインストールでき、`BCODE` 関数を使ってセルに直接財務データを呼び出せる。

### Excel アドイン

Excel 向けのアドイン（[buffett-code-api-client-excel](https://github.com/BuffettCode/buffett-code-api-client-excel)）も提供されている。

## MCP Server — AI との連携

バフェット・コードは [MCP（Model Context Protocol）サーバー](https://github.com/BuffettCode/buffett-code-mcp-server) を公開している。これにより、Claude Desktop などの AI アシスタントからバフェット・コードの API に直接アクセスし、対話的に企業分析を行える。

### セットアップ

```json
{
  "mcpServers": {
    "buffett-code": {
      "command": "node",
      "args": ["/path/to/buffett-code-mcp-server/dist/index.js"],
      "env": {
        "BUFFETT_CODE_API_KEY": "YOUR_API_KEY"
      }
    }
  }
}
```

### できること

- 「トヨタの直近の営業利益率を教えて」のような自然言語での企業分析
- 複数企業の財務データを比較し、表やグラフで整理
- 決算データに基づいた投資判断の材料提示

AI と財務データの組み合わせにより、従来はアナリストが手作業で行っていた分析作業を効率化できる。

## OSS ライブラリ群

バフェット・コードは GitHub（[BuffettCode](https://github.com/BuffettCode)）で複数のオープンソースプロジェクトを公開している:

| リポジトリ | 言語 | 説明 |
|-----------|------|------|
| [edinet_xbrl](https://github.com/BuffettCode/edinet_xbrl) | Python | EDINET XBRL ファイルのダウンロード・パーサー |
| [buffett-code-api-client-python](https://github.com/BuffettCode/buffett-code-api-client-python) | Python | API クライアント（Python） |
| [buffett-code-api-client-excel](https://github.com/BuffettCode/buffett-code-api-client-excel) | — | Excel アドイン |
| [buffett-code-api-client-google-spreadsheet](https://github.com/BuffettCode/buffett-code-api-client-google-spreadsheet) | — | Google スプレッドシートアドオン |
| [buffett-code-mcp-server](https://github.com/BuffettCode/buffett-code-mcp-server) | TypeScript | MCP Server（Claude Desktop 連携） |

## 料金プラン

バフェット・コードは無料プランから有料プランまで複数のプランを提供している:

| プラン | 月額 | データ範囲 |
|--------|------|-----------|
| 無料 | 0円 | 3年分の業績データ |
| ライト | 990円 | 5年分 |
| スタンダード | 5,500円 | 17期分 |
| プレミアム | 22,000円 | 全データ + Web API |

Web API の利用には別途 API 利用契約が必要。個人・法人それぞれの問い合わせフォームから申し込みできる。

## Python での活用例

API を使って四半期データを取得する例:

```python
import requests
import pandas as pd

API_KEY = "YOUR_API_KEY"
BASE_URL = "https://api.buffett-code.com/api/v4"

def get_quarterly_data(company_id: str, quarter: str) -> dict:
    """四半期財務データを取得する"""
    url = f"{BASE_URL}/jp/companies/{company_id}/quarterly/{quarter}"
    headers = {"x-api-key": API_KEY}
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()

# テスト用APIキーで銘柄コード末尾01の企業を取得
data = get_quarterly_data("2801", "2024Q4")
```

## まとめ

バフェット・コードは、EDINET / TDNET の XBRL データを基盤に、以下の多層的なアクセス手段を提供している:

| 用途 | 手段 |
|------|------|
| ブラウザで手軽に分析 | Web アプリ |
| スプレッドシートに組み込み | Google / Excel アドイン |
| プログラムから自動取得 | REST API (v4) |
| AI で対話的に分析 | MCP Server |
| 自前パイプライン構築 | OSS ライブラリ（edinet_xbrl） |

単なるデータ閲覧サービスではなく、API・アドイン・MCP・OSS を組み合わせた **企業財務データのプラットフォーム** として設計されている点が特徴だ。特に MCP Server の公開は、AI 時代の財務分析ワークフローを先取りした取り組みとして注目に値する。

## 参考リンク

- [バフェット・コード公式サイト](https://www.buffett-code.com/)
- [バフェット・コード Web API ドキュメント](https://docs.buffett-code.com/api/)
- [BuffettCode - GitHub](https://github.com/BuffettCode)
- [バフェット・コードのブログ](https://blog.buffett-code.com/)
- [バフェット・コード - Google Workspace Marketplace](https://workspace.google.com/marketplace/app/%E3%83%90%E3%83%95%E3%82%A7%E3%83%83%E3%83%88%E3%83%BB%E3%82%B3%E3%83%BC%E3%83%89/671399271704)
