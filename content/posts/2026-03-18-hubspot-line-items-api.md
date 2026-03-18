---
title: "HubSpot Line Items API：取引・見積もりに紐づく商品項目を管理する"
date: 2026-03-18
lastmod: 2026-03-18
draft: false
source_url: "https://github.com/hdknr/blogs/issues/71#issuecomment-4078866649"
categories: ["Web開発"]
tags: ["hubspot", "api", "crm"]
---

HubSpot CRM の Line Items（商品項目）API について整理します。Line Items は製品（Product）が取引（Deal）や見積もり（Quote）に紐付けられたときに生成される個別のインスタンスです。

## Line Items とは

HubSpot における Line Items は、製品カタログ（Products）とは異なる概念です。

- **Product**: 製品カタログ上のマスターデータ
- **Line Item**: Product が取引・見積もりなどに追加された際の個別インスタンス

Line Items への変更は元の Product には影響しません。取引ごとに価格や数量をカスタマイズできます。

## API エンドポイント

ベース URL: `/crm/v3/objects/line_items`

| 操作 | メソッド | エンドポイント |
|------|----------|---------------|
| 作成 | POST | `/crm/v3/objects/line_items` |
| 個別取得 | GET | `/crm/v3/objects/line_items/{lineItemId}` |
| 一覧取得 | GET | `/crm/v3/objects/line_items` |
| 更新 | PATCH | `/crm/v3/objects/line_items/{lineItemId}` |
| 削除 | DELETE | `/crm/v3/objects/line_items/{lineItemId}` |

## 必要なスコープ

| スコープ | 用途 |
|----------|------|
| `crm.objects.line_items.read` | データ取得 |
| `crm.objects.line_items.write` | 作成・更新 |
| `tax_rates.read` | 税率情報の取得 |

## 主要プロパティ

| プロパティ | 説明 |
|-----------|------|
| `name` | 商品項目の名前 |
| `quantity` | 数量 |
| `price` | 単価 |
| `amount` | 合計金額（数量 × 単価） |
| `hs_product_id` | 関連する製品の ID |
| `hs_tax_rate_group_id` | 適用する税率グループ ID |

## Line Item の作成例

製品から Line Item を作成し、取引に関連付ける例です。

```json
POST /crm/v3/objects/line_items

{
  "properties": {
    "name": "Web開発サービス",
    "hs_product_id": "12345",
    "quantity": "1",
    "price": "500000"
  },
  "associations": [
    {
      "to": {
        "id": "67890"
      },
      "types": [
        {
          "associationCategory": "HUBSPOT_DEFINED",
          "associationTypeId": 20
        }
      ]
    }
  ]
}
```

## 関連付け（Associations）

Line Items は以下のオブジェクトと関連付けできます。

- 取引（Deals）
- 見積もり（Quotes）
- 請求書（Invoices）
- 支払いリンク（Payment Links）
- サブスクリプション（Subscriptions）

### 重要な制限

**Line Items は 1 つの親オブジェクトにのみ属します。** 同じ Line Item を複数の取引や見積もりに共有することはできません。複数のオブジェクトに同じ製品を紐付けたい場合は、オブジェクトごとに別々の Line Item を作成する必要があります。

## 参考リンク

- [HubSpot Line Items API リファレンス（日本語）](https://developers.hubspot.jp/docs/api-reference/crm-line-items-v3/guide)
- [HubSpot Line Items API Reference（英語）](https://developers.hubspot.com/docs/api-reference/crm-line-items-v3/guide)
