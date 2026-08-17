---
title: "EDINET XBRL を Python で扱うガイド"
description: "金融庁 EDINET から有価証券報告書の XBRL データを取得し、edinet-xbrl ライブラリで Python から解析する手順"
date: 2026-04-14
lastmod: 2026-08-05
aliases: ["EDINET API v2", "docTypeCode", "issuerEdinetCode", "EDINETコードリスト"]
related_posts:
  - "/posts/2026/04/edinet-xbrl-python/"
  - "/posts/2026/04/buffett-code-analysis/"
  - "/posts/2026/08/activist-signal-news-detection/"
tags: ["python", "XBRL", "EDINET", "金融データ", "財務分析"]
---

## 概要

EDINET（Electronic Disclosure for Investors' NETwork）は金融庁が運営する電子開示システムで、上場企業の有価証券報告書を XBRL 形式でダウンロードできる。edinet-xbrl ライブラリを使えば、複雑な XBRL 仕様を意識せずに Python でデータを抽出できる。

## 必要なもの

- EDINET API キー（[EDINET API](https://api.edinet-fsa.go.jp/) で取得）
- Python 3.x
- edinet-xbrl ライブラリ（`pip install edinet-xbrl`）

## 基本的な使い方

```python
from edinet_xbrl.edinet_xbrl_parser import EdinetXbrlParser

parser = EdinetXbrlParser()
edinet_xbrl_object = parser.parse_file("path/to/file.xbrl")

# 総資産の取得例
assets = edinet_xbrl_object.get_data_by_context_ref(
    "jppfs_cor:Assets", "CurrentYearInstant"
).get_value()
```

## 主要な財務タクソノミキー

| key | 内容 |
|-----|------|
| `jppfs_cor:Assets` | 総資産 |
| `jppfs_cor:NetSales` | 売上高 |
| `jppfs_cor:OperatingIncome` | 営業利益 |
| `jppfs_cor:OrdinaryIncome` | 経常利益 |

`jppfs_cor` は日本 GAAP 財務諸表のタクソノミ名前空間。`context_ref` の `CurrentYearInstant` は当期末時点を指す。

## EDINET API から書類を取得する

```python
import requests

url = "https://api.edinet-fsa.go.jp/api/v2/documents.json"
params = {
    "date": "2024-03-31",
    "type": 2,  # 書類メタデータ
    "Subscription-Key": "YOUR_API_KEY"
}
response = requests.get(url, params=params)
documents = response.json()
# documents["results"] から docID を取得
```

## バフェット・コードとの関係

バフェット・コードは同様のパイプライン（EDINET/TDNET → XBRL パース → RDB 格納）を活用した企業分析 SaaS。edinet-xbrl ライブラリ自体も BuffettCode 社が OSS 公開している。Web API、スプレッドシート連携、MCP サーバーなどを通じて財務データにアクセス可能。

## 書類一覧 API のメタデータだけを使う場合

XBRL 本体をパースせず、書類一覧 API（`/api/v2/documents.json`）のメタデータだけで用が足りるケースもある。大量保有報告書によるアクティビスト追跡がその例。

- **`type=2`** で提出書類一覧 + メタデータを取得する。`Subscription-Key` は必須（無いと 401）
- **書類種別コード** — 350 大量保有報告書 / 360 訂正大量保有報告書 / 240・250 公開買付届出書・訂正 / 290 意見表明報告書
- **変更報告書に独立コードはない** — 新規か変更かは `docDescription` の文字列で判別する
- **`secCode` は提出者の証券コード**（仕様書の項目 15）。大量保有報告書の提出者はファンドなので多くは `null` になり、買われている側の銘柄コードは取れない
- **対象企業は `issuerEdinetCode`**（項目 26）から引く。EDINET コードリスト（`Edinetcode.zip`）で証券コードへ変換する。CSV は cp932、1 行目がメタ行・2 行目がヘッダ、証券コードは 5 桁表記なので上 4 桁が銘柄コード
- **四半期報告書は廃止済み** — 2024 年 4 月以後の Q1/Q3 の数字を EDINET に求めてはいけない

## 関連ページ

- [DuckDB](/blogs/wiki/tools/duckdb/) — 取得した財務データの高速集計に活用可能
- [アクティビスト検知](/blogs/wiki/concepts/activist-investor-detection/) — 書類一覧 API を「開示が無いこと」の確認に使う応用
- [株式データソースの3層構造](/blogs/wiki/concepts/stock-data-source-layers/) — EDINET の位置づけ

## ソース記事

- [EDINET XBRL を Python で扱う](/blogs/posts/2026/04/edinet-xbrl-python/) — 2026-04-06
- [バフェット・コード徹底分析](/blogs/posts/2026/04/buffett-code-analysis/) — 2026-04-07
- [大量保有報告書の「前」を検知する — EDINET API とニュース見出しでアクティビストの兆候を捕まえる](/blogs/posts/2026/08/activist-signal-news-detection/) — 2026-08-05（docTypeCode 350/360 と secCode の落とし穴）
