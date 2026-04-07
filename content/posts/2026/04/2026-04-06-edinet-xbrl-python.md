---
title: "EDINET XBRLをPythonで扱う — edinet-xbrlライブラリの使い方"
date: 2026-04-06
lastmod: 2026-04-06
draft: false
source_url: "https://github.com/hdknr/blogs/issues/1#issuecomment-4195639252"
categories: ["プログラミング言語"]
description: "EDINETのXBRLファイルをPythonで解析する方法を解説。edinet-xbrlライブラリのインストールからXBRLパース、EDINET APIでの書類取得まで、サンプルコード付きで紹介"
tags: ["Python", "XBRL", "EDINET", "金融データ", "有価証券報告書"]
---

EDINETで公開されている有価証券報告書のXBRLファイルを、Pythonで効率的にパース・活用する方法を紹介する。[edinet-xbrl](https://github.com/BuffettCode/edinet_xbrl) ライブラリを使えば、複雑なXBRL仕様を意識せずにデータを抽出できる。

## EDINETとXBRLとは

**EDINET**（Electronic Disclosure for Investors' NETwork）は、金融商品取引法に基づく有価証券報告書等の開示書類を電子的に提出・閲覧するためのシステムだ。金融庁が運営しており、上場企業の決算書データをXBRL形式でダウンロードできる。

**XBRL**（eXtensible Business Reporting Language）は、財務・経営・投資情報を標準化されたXMLベースで記述するための言語だ。構造化されたデータとしてマシンリーダブルだが、仕様が複雑で、そのまま扱うのは難易度が高い。

## edinet-xbrl ライブラリ

[BuffettCode/edinet_xbrl](https://github.com/BuffettCode/edinet_xbrl) は、EDINETのXBRLファイルをPythonオブジェクトとして扱えるようにするライブラリだ。

### インストール

```bash
pip install edinet-xbrl
```

### 基本的な使い方

```python
from edinet_xbrl.edinet_xbrl_parser import EdinetXbrlParser

# パーサーの初期化
parser = EdinetXbrlParser()

# XBRLファイルをパースしてデータコンテナを取得
xbrl_file_path = "path/to/your/xbrl/file.xbrl"
edinet_xbrl_object = parser.parse_file(xbrl_file_path)

# 例: 該当年度の総資産を取得
key = "jppfs_cor:Assets"
context_ref = "CurrentYearInstant"
current_year_assets = edinet_xbrl_object.get_data_by_context_ref(key, context_ref).get_value()
```

### key と context_ref の特定

XBRLでは、取得したいデータ項目を `key`（タクソノミ要素 = データ項目の識別子）と `context_ref`（コンテキスト参照 = 期間や連結/単体などの条件）の組み合わせで指定する。`jppfs_cor` は日本GAAP財務諸表のタクソノミ名前空間だ。これらを特定するには：

- 有価証券報告書のPDFとXBRLファイルを並べて対照する
- EDINETタクソノミの「タクソノミ要素リスト」（Excelファイル）を参照する

主要な key の例：

| key | 内容 |
|-----|------|
| `jppfs_cor:Assets` | 総資産 |
| `jppfs_cor:NetSales` | 売上高 |
| `jppfs_cor:OperatingIncome` | 営業利益 |
| `jppfs_cor:OrdinaryIncome` | 経常利益 |

## XBRLファイルのダウンロード

EDINETからXBRLファイルを取得するには、[EDINET API](https://api.edinet-fsa.go.jp/) を利用する。書類一覧の取得と書類のダウンロードが可能だ。

```python
import requests

# 書類一覧の取得（例: 2024年3月31日提出分）
url = "https://api.edinet-fsa.go.jp/api/v2/documents.json"
params = {
    "date": "2024-03-31",
    "type": 2,  # 書類メタデータ
    "Subscription-Key": "YOUR_API_KEY"
}
response = requests.get(url, params=params)
documents = response.json()
# documents["results"] から docID を取得し、書類取得APIでXBRLをダウンロード
```

2024年4月以降、EDINET API v2 の利用には Subscription Key（APIキー）の取得が必要となった。[EDINET](https://disclosure.edinet-fsa.go.jp/) のサイトからアカウントを作成して申請できる。

## 活用事例

edinet-xbrl ライブラリは、[バフェット・コード](https://www.buffett-code.com/)という企業分析サービスの開発で実際に活用されている。大量のXBRLデータを自動処理し、企業の財務データを整理・可視化する基盤として機能している。

## まとめ

- EDINETのXBRLは構造化されたデータだが、仕様が複雑で直接扱うのは大変
- `edinet-xbrl` ライブラリを使えば、Pythonオブジェクトとして簡単にデータを抽出できる
- 財務データの自動収集・分析を行うデータパイプラインの構築に活用できる

## 参考リンク

- [BuffettCode/edinet_xbrl - GitHub](https://github.com/BuffettCode/edinet_xbrl)
- [EDINETのXBRL用のPythonライブラリを作った - Parser編（Qiita）](https://qiita.com/shoe116/items/dd362ad880f2b6baa96f)
- [EDINETのXBRL用のPythonライブラリを作った - ダウンロード編（Qiita）](https://qiita.com/shoe116/items/a7b688d05b699cf403a1)
- [EDINET](https://disclosure.edinet-fsa.go.jp/)
