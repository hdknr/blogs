---
title: "LOGILESS（ロジレス）"
description: "OMS(受注管理)と WMS(倉庫管理)を一体化した EC 自動出荷システム。Shopify 等と API 連携し受注取込・在庫連動・出荷通知を自動化、全注文の90%以上を自動出荷する"
date: 2026-07-15
lastmod: 2026-07-15
aliases: ["LOGILESS", "ロジレス", "logiless"]
related_posts:
  - "/posts/2026/07/logiless-shopify-integration/"
  - "/posts/2026/07/ec-oms-wms-comparison-japan/"
tags: ["LOGILESS", "EC", "OMS", "WMS", "Shopify", "API連携", "在庫管理"]
---

## 概要

LOGILESS（ロジレス社）は、OMS（Order Management System / 受注管理）と WMS（Warehouse Management System / 倉庫管理）を1つのシステムに統合した EC 自動出荷 SaaS。受注情報と倉庫の実在庫を同じデータ基盤で扱うため、出荷までの **90%以上を自動化**できる。約1,700社（2026年4月時点）が利用する。Shopify・BASE・makeshop・ecforce・futureshop・EC-CUBE など主要カートに専用 API 連携を用意する。

## 詳細

### Shopify 連携で自動化される3つのこと

1. **受注取込（Shopify → LOGILESS）**: 注文を自動取込し、引き当て可能な**フリー在庫数**を自動計算
2. **在庫の双方向連動（Shopify ⇄ LOGILESS）**: 倉庫の実在庫を **約10分ごと** に反映し、欠品・オーバーセルを抑える
3. **出荷通知（LOGILESS → Shopify）**: 出荷完了で配送会社名と追跡番号を自動書き戻し

設定は公式アプリのインストールと「受注取込を自動実行」「出荷通知を自動実行」のチェックだけで完了する。

### 運用でハマりやすい点

- **Shopify Lite プランは連携不可**
- **商品対応表が必須**（SKU が異なると引き当て不可。在庫連動の前提条件）
- **31日ルール**: 自動取込は直近31日以内・未発送・オープンの注文のみ（オプションで最大6ヶ月遡及）
- **待機とオーバーセル**: 受注取込の待機を在庫連動と併用するとズレでオーバーセルが起きうる。待機短縮・在庫連動オフ・安全在庫設定で対策

### Shopify 以外・独自 EC との連携

WooCommerce や独自 EC は公式アプリ対象外だが、**開発者向け API「LOGILESS Developers」**（OAuth 2.0、ベース URL `https://app2.logiless.com/api/`、レート制限 約1 req/秒）で自作ミドルウェアを介して連携できる。リソースを割けない場合は **CSV レイアウト機能**でのバッチ連携も可能。

### 料金

基本料金＋月間出荷数の従量課金。無料枠はライトプラン月300件・スタンダードプラン月500件が目安で、立ち上げ期に優しい。

## 関連ページ

- [EC 一元管理（OMS/WMS）](/blogs/wiki/concepts/ec-order-management/) — LOGILESS が属する OMS/WMS 一体型の位置づけと他サービス比較
- [ソーシャルコマース](/blogs/wiki/concepts/social-commerce/) — SNS 経由の受注を一元管理する必要性
- [オープンロジ](/blogs/wiki/tools/openlogi/) — 倉庫を借りる物流アウトソース型（役割が異なる）

## ソース記事

- [LOGILESS × Shopify 連携を理解する：受注・在庫・出荷を自動化する OMS/WMS 一体型システム](/blogs/posts/2026/07/logiless-shopify-integration/) — 2026-07-02
- [EC 一元管理システム徹底比較｜ネクストエンジン・LOGILESS・コマースロボなど6サービス](/blogs/posts/2026/07/ec-oms-wms-comparison-japan/) — 2026-07-02
