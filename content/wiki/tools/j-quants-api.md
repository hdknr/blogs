---
title: "J-Quants API"
description: "JPX（日本取引所グループ）公式の日本株データ API。上場銘柄一覧・株価四本値・財務情報・信用残などを提供する個人〜法人向けマーケットデータサービス"
date: 2026-05-20
lastmod: 2026-08-05
aliases: ["JQuants", "J-Quants", "JPX API", "TDnetアドオン"]
related_posts:
  - "/posts/2026/05/nikkei225-micro-monte-carlo-claude/"
  - "/posts/2026/07/fable-stock-factor-analysis-jquants/"
  - "/posts/2026/07/claude-code-stock-news-automation/"
  - "/posts/2026/08/stock-turnaround-signals/"
  - "/posts/2026/08/activist-signal-news-detection/"
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

## データ品質の落とし穴

ファクター分析のようにデータの質で結果が変わる用途では、API を使っても前処理側に難所が残る。実際に報告されている課題は次の 4 つ。

- **財務データの時系列が揃っていない** — 財務データと株価データをマージすると実態と乖離するケースがある
- **XBRL 由来の数値ミス** — 開示書類そのものに数値の誤りが含まれることがある
- **株式分割の調整値が怪しいことがある** — 調整値がずれると過去リターンの計算が狂う
- **自力で抽出したデータの品質が低い** — 受注情報やセグメント情報など API に無い情報を独自にスクレイピングした分は、公式データより品質が落ちる

> 教訓: **ファクター分析ツールの難所は、計算式でもバックテストのロジックでもなく、その手前のデータ整備にある。** バリューやモメンタムの計算は定義が確立していて AI でも安定して書けるが、「時系列の整合」「分割調整」「欠損補完」はドメイン知識と地道な検証を要する。AI に丸投げできる部分（設計・実装）と、人間が責任を持つべき部分（データの正しさ）を切り分ける視点が必要。

## 適時開示（TDnet）アドオン

2026 年 5 月 18 日から**適時開示書類（TDnet）アドオン**が提供されている。過去 5 年分の適時開示インデックス情報と、全文 PDF・サマリ PDF・XBRL を**開示同日に**取得できる。CSV での一括ダウンロードにも対応。

- 料金: 月額 **11,000 円**（税込）
- 条件: **ライトプラン以上**の契約者向けアドオン（フリープランでは利用できない）

カタリスト検知の本体は TDnet 側にあるため、速報性を求める用途ではこのアドオンが実質的な要件になる。逆に**フリープランの 12 週遅延はニュース分析や兆候検知には使えない**ので、組み込む前に必ず確認する。

## 関連ページ

- [モンテカルロ法による売買判定](/blogs/wiki/concepts/monte-carlo-trading/) — 本 API のユースケース
- [kabu ステーション API](/blogs/wiki/tools/kabu-station-api/) — 発注層
- [株式投資の売買スタイル](/blogs/wiki/concepts/stock-trading-styles/) — 取引スタイル
- [セクターローテーション](/blogs/wiki/concepts/sector-rotation/) — RS比・出来高データの用途
- [グラフエンジニアリング](/blogs/wiki/concepts/graph-engineering/) — 多因子アルファモデルをグラフで組む設計
- [株式の銘柄分類](/blogs/wiki/concepts/stock-style-classification/) — 分類別の先行指標の取得元
- [株式データソースの3層構造](/blogs/wiki/concepts/stock-data-source-layers/) — 第1層の中心としての位置づけ
- [分類別の先行指標](/blogs/wiki/concepts/stock-leading-indicators/) — J-Quants / TDnet / EDINET の役割分担

## ソース記事

- [日経225マイクロ先物 × Monte Carlo 自動売買判定 — Claude + 1万通りシミュレーションで勝率55%超のときだけ発注する実装](/blogs/posts/2026/05/nikkei225-micro-monte-carlo-claude/) — 2026-05-20
- [AIに設計から任せて株式ファクター分析ツールを作る──Claude Fable 5 × J-Quants API のプロンプト実例](/blogs/posts/2026/07/fable-stock-factor-analysis-jquants/) — 2026-07-17
- [Claude Code で株式ニュース分析を自動化する — EDINET・J-Quants・RSS の 3 層構成](/blogs/posts/2026/07/claude-code-stock-news-automation/) — 2026-07-31（無料プランの12週遅延に注意）
- [株価が上昇に転じる兆候 — 銘柄分類別に見る先行指標](/blogs/posts/2026/08/stock-turnaround-signals/) — 2026-08-03
- [大量保有報告書の「前」を検知する](/blogs/posts/2026/08/activist-signal-news-detection/) — 2026-08-05（出来高 z-score による裏付け）
