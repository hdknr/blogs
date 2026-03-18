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

## データモデル詳細

Line Item の全プロパティは `GET /crm/v3/properties/line_item` で取得できます。以下はカテゴリ別の主要プロパティです。

### 基本情報

| 内部名 | 表示名 | 説明 | 備考 |
|--------|--------|------|------|
| `name` | 名前 | 商品項目の名前 | 必須 |
| `description` | 説明 | 製品の詳細な説明 | |
| `hs_sku` | SKU | 製品の固有識別子 | |
| `hs_product_id` | 製品 ID | 関連する製品ライブラリの ID | 製品から作成時に指定 |
| `hs_object_id` | レコード ID | Line Item の一意な ID | 自動設定・読み取り専用 |
| `hs_product_type` | 製品タイプ | `INVENTORY`（在庫）/ `NON_INVENTORY`（非在庫）/ `SERVICE`（サービス） | |
| `hs_url` | URL | 製品の Web ページ URL | |
| `hs_images` | 画像 URL | 製品画像の URL | |

### 価格・数量

| 内部名 | 表示名 | 説明 | 備考 |
|--------|--------|------|------|
| `quantity` | 数量 | 含まれる製品の単位数 | |
| `price` | 単価 | 購入者向けの製品単価 | 負の値は不可 |
| `amount` | 正価（Net price） | 合計金額（数量 × 単価） | 計算フィールド |
| `hs_cost_of_goods_sold` | 売上原価 | 製品の原価 | |
| `hs_line_item_currency_code` | 通貨 | 通貨コード（例: `JPY`, `USD`） | |
| `hs_pricing_model` | 価格モデル | `FLAT`（定額）または `TIERED`（段階制） | |
| `hs_effective_unit_price` | 有効単価 | 段階制価格の場合に適用される実効単価 | |

### 割引

| 内部名 | 表示名 | 説明 | 備考 |
|--------|--------|------|------|
| `hs_discount_percentage` | 割引率 | 適用される割引の割合（%） | |
| `discount` | 単位割引額 | 単位あたりの割引金額 | |
| `hs_total_discount` | 合計割引額 | 割引率と割引金額を考慮した総割引額 | 計算フィールド |
| `hs_pre_discount_amount` | 割引前金額 | 割引適用前の金額 | 計算フィールド |

### 税金

| 内部名 | 表示名 | 説明 | 備考 |
|--------|--------|------|------|
| `hs_tax_rate_group_id` | 税率グループ ID | 適用する税率の識別子 | |
| `tax` | 税額 | 適用される税金額 | |
| `hs_tax_amount` | 計算税額 | 税率から自動計算された税額 | 計算フィールド |
| `hs_tax_rate` | 税率 | 適用される税率（%） | |
| `hs_after_tax_amount` | 税込金額 | 税額適用後の金額 | 計算フィールド |

### 定期請求（Recurring Billing）

| 内部名 | 表示名 | 説明 | 備考 |
|--------|--------|------|------|
| `recurringbillingfrequency` | 請求頻度 | 定期請求の頻度（`monthly`, `quarterly`, `annually` など） | |
| `hs_recurring_billing_period` | 請求期間 | ISO-8601 期間形式（例: `P12M` = 12ヶ月, `P1Y` = 1年） | PnYnMnD / PnW 形式 |
| `hs_recurring_billing_start_date` | 請求開始日 | 定期請求の開始日 | |
| `hs_recurring_billing_end_date` | 請求終了日 | 定期請求の終了日 | |
| `hs_recurring_billing_terms` | 請求条件 | `FIXED`（固定回数）または `AUTO_RENEW`（自動更新） | |
| `hs_recurring_billing_number_of_payments` | 支払い回数 | 固定回数請求の場合の支払い総数 | |
| `hs_billing_start_delay_days` | 請求開始遅延（日） | 請求開始を遅延させる日数 | |
| `hs_billing_start_delay_months` | 請求開始遅延（月） | 請求開始を遅延させる月数 | |
| `hs_billing_start_delay_type` | 請求遅延タイプ | `FIXED_DATE`（固定日）または `DELAYED_PERIOD`（遅延期間） | |
| `hs_term_in_months` | 期間（月） | 契約期間の月数 | |

### 収益指標（計算フィールド）

| 内部名 | 表示名 | 説明 |
|--------|--------|------|
| `hs_tcv` | 総契約額（TCV） | Total Contract Value |
| `hs_acv` | 年間契約額（ACV） | Annual Contract Value |
| `hs_arr` | 年間経常収益（ARR） | Annual Recurring Revenue |
| `hs_mrr` | 月間経常収益（MRR） | Monthly Recurring Revenue |
| `hs_margin` | マージン | 売上 − 売上原価 |
| `hs_margin_tcv` | マージン TCV | TCV − 売上原価合計 |
| `hs_margin_acv` | マージン ACV | ACV − 売上原価（年間） |
| `hs_margin_arr` | マージン ARR | ARR − 売上原価（年間） |
| `hs_margin_mrr` | マージン MRR | MRR − 売上原価（月間） |

### システムプロパティ（読み取り専用）

| 内部名 | 表示名 | 説明 |
|--------|--------|------|
| `createdate` | 作成日時 | レコード作成日時 |
| `hs_lastmodifieddate` | 最終更新日時 | プロパティが最後に変更された日時 |
| `hs_created_by_user_id` | 作成者ユーザー ID | レコードを作成したユーザー |
| `hs_updated_by_user_id` | 更新者ユーザー ID | 最後に更新したユーザー |
| `hs_object_source` | レコードソース | レコードの作成方法 |
| `hs_was_imported` | インポートフラグ | インポートによって作成されたかどうか |

### プロパティの種別

- **必須**: `name` のみが作成時に必須。ただし `price` と `quantity` も通常は指定する
- **計算フィールド**: `amount`, `hs_total_discount`, `hs_pre_discount_amount`, `hs_after_tax_amount`, `hs_tax_amount`, 収益指標（TCV/ACV/ARR/MRR）は HubSpot が自動計算する。API から直接設定はできない
- **読み取り専用**: システムプロパティ（作成日時、更新日時、ユーザー ID 等）は自動設定される
- **price の制約**: 負の値を設定できない

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
