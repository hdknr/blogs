---
title: "J-Quants API"
description: "JPX（日本取引所グループ）公式の日本株データ API。上場銘柄一覧・株価四本値・財務情報・信用残などを提供する個人〜法人向けマーケットデータサービス"
date: 2026-05-20
lastmod: 2026-07-28
aliases: ["JQuants", "J-Quants", "JPX API"]
related_posts:
  - "/posts/2026/05/nikkei225-micro-monte-carlo-claude/"
  - "/posts/2026/07/fable-stock-factor-analysis-jquants/"
tags: ["J-Quants", "JPX", "日本株", "API", "市場データ"]
---

## 概要

J-Quants API は **JPX（日本取引所グループ）公式** が提供する日本株マーケットデータ API である。上場銘柄一覧、株価四本値、財務情報、信用残などを REST 経由で取得でき、個人投資家・FinTech 企業の双方が利用できる。公式サイトは [jpx-jquants.com](https://jpx-jquants.com/)。

## 料金プラン

- **フリープラン**: 12 週間遅延データのみ。バックテスト・教育用途には十分
- **ライト以上の有料プラン**: リアルタイム化・分足対応・上位データセット
- 月額課金で個人でも利用可能

## 提供データ

- 上場銘柄一覧
- 株価四本値（日足）
- 上位プランでは分足
- 財務情報（決算ベース）
- 信用残（買い残・売り残）
- 投資部門別売買状況

## 自動売買での位置づけ

Monte Carlo + Claude 系の自動売買アーキテクチャでは「データ取得層」を担当する。MVP では `yfinance` で代用できるが、本番投入時には次の理由で J-Quants API に置き換える必要がある。

- リアルタイム性: ザラ場運用には遅延データでは不十分
- データ正確性: 配当落ち調整・分割調整など、JPX 公式の整合された数値が手に入る
- 銘柄カバレッジ: 日本市場全銘柄を網羅的に扱える

## ファクター分析でのデータ品質の落とし穴

ファクター分析は入力データの質で結果がまったく変わるため、API から取れたデータをそのまま信じると危険である。実務で挙がっている主な論点は次のとおり。

- **財務データの時系列が揃っていない** — 財務データと株価データを単純にマージすると、実態と乖離するケースがある（開示タイミングのズレ）
- **XBRL 由来の数値ミス** — 開示書類（XBRL）そのものに数値の誤りが含まれることがある
- **分割調整** — 株式分割の遡及調整が意図どおりか要確認
- **自力抽出データ** — 独自にパースした項目は特に検証が必要

## 関連ページ

- [モンテカルロ法による売買判定](/blogs/wiki/concepts/monte-carlo-trading/) — 本 API のユースケース
- [kabu ステーション API](/blogs/wiki/tools/kabu-station-api/) — 発注層
- [株式投資の売買スタイル](/blogs/wiki/concepts/stock-trading-styles/) — 取引スタイル
- [セクターローテーション](/blogs/wiki/concepts/sector-rotation/) — RS比・出来高データの活用先
- [グラフエンジニアリング](/blogs/wiki/concepts/graph-engineering/) — 多因子アルファモデルの組み方

## ソース記事

- [日経225マイクロ先物 × Monte Carlo 自動売買判定 — Claude + 1万通りシミュレーションで勝率55%超のときだけ発注する実装](/blogs/posts/2026/05/nikkei225-micro-monte-carlo-claude/) — 2026-05-20
- [AIに設計から任せて株式ファクター分析ツールを作る──Claude Fable 5 × J-Quants API のプロンプト実例](/blogs/posts/2026/07/fable-stock-factor-analysis-jquants/) — 2026-07-17
