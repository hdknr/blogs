---
title: "Airtable"
description: "スプレッドシート型のノーコードデータベース。料金プランと上限は2026年8月時点で確認済み"
date: 2026-08-23
lastmod: 2026-08-23
aliases: ["エアテーブル"]
related_posts:
  - "/posts/2026/08/airtable-plans-limits-2026/"
  - "/posts/2026/08/airtable-vs-hubspot-ma-cost/"
tags: ["Airtable", "ノーコード", "SaaS", "料金プラン"]
---

## 概要

スプレッドシートの操作感でリレーショナルなデータを扱えるノーコードデータベース。日本語の解説記事は情報が古いものが多く、そのまま見積もると外れる。

## 古い日本語記事のまま見積もると外れる4点

2026 年 8 月時点の公式ドキュメントで引き直した結果、次の 4 点が要注意。

1. **Plus / Pro は 2023 年 9 月に Team へ統合済み** — 現行プラン名で書かれていない記事は世代が古い
2. **レコード上限 1,000 件は table 単位ではなく base 単位** — 見積もりが桁で変わる
3. **課金座席の定義が Team と Business で異なり、総額が逆転することがある**
4. **API のレート制限は全プラン共通で 5 リクエスト/秒** — 上位プランでも緩和されない

4 番目は連携設計に直接効く。プランを上げても API スループットは買えない。

## HubSpot との MA 運営コスト比較

| | 初年度コスト（2026年8月・年契約） |
|---|---|
| HubSpot Marketing Hub Professional | $12,600（オンボーディング $3,000 必須） |
| Airtable Team 20席 | $4,800 |

約 2.6 倍の差。ただし課金軸が違う（HubSpot はコンタクト数、Airtable は座席数）ため、規模によって損益分岐が動く。**カスタムオブジェクトは HubSpot では Enterprise 限定**である点も比較時の注意。

## 関連ページ

- [HubSpot](/blogs/wiki/tools/hubspot/) — MA / CRM の比較対象

## ソース記事

- [Airtable の料金プランと上限まとめ 2026年8月版](/blogs/posts/2026/08/airtable-plans-limits-2026/) — 2026-08-15
- [Airtable と HubSpot、MA 運営コストはどちらが安いか](/blogs/posts/2026/08/airtable-vs-hubspot-ma-cost/) — 2026-08-15
