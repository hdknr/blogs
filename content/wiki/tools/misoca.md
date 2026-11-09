---
title: "Misoca"
description: "弥生のクラウド請求書サービス。Misoca API v3 では OAuth2 で請求書・見積書・納品書・取引先・品目を操作できる。弥生で公開されている外部 API は調べた範囲で Misoca のみ"
date: 2026-11-09
lastmod: 2026-11-09
aliases: ["ミソカ", "Misoca API", "Misoca API v3", "弥生 API", "請求書 API"]
related_posts:
  - "/posts/2026/11/misoca-api-v3/"
tags: ["Misoca", "弥生", "API", "OAuth", "請求書"]
---

## 概要

Misoca（ミソカ）は、弥生株式会社が提供するクラウド請求書サービス。外部 API の仕様が [doc.misoca.jp](https://doc.misoca.jp/) で公開されており、販売管理システムや CRM から請求書・見積書・納品書を自動で起こす用途に使える。

弥生会計そのものには外部開発者向けの公開 API が見当たらないため、弥生を使う場合に API で自動化できるのは**請求（Misoca）まで**というのが実務上の線になる。

## 詳細

### Misoca API v3 の基本

| 項目 | 内容 |
|---|---|
| 現行バージョン | v3（2016 年 12 月 1 日公開。2024 年 1 月に納品書・品目 API を追加） |
| エンドポイント | `https://app.misoca.jp/api/v3/` |
| 認証 | OAuth2 認可コードフロー（スコープ `read` / `write`、`write` は `read` を含む） |
| 仕様書 | Swagger 2.0（`/api/v3/swagger_doc`） |
| 旧版 | v1 は 2021 年 4 月 1 日に提供終了 |

### リソースと設計の癖

- 請求書・見積書・納品書・取引先（`contact_group`）・送り先（`contact`）・品目（`dealing_item`）・ユーザー（`/user/me`）を扱える
- 一覧は**複数形**（`/invoices`）、1 件の取得・作成は**単数形**（`/invoice/{id}`）。Rails 系でよく見る `/invoices/{id}` と違うので間違えやすい
- 支払済み・送付済み・ゴミ箱などの**状態はサブリソースへの `PUT`（オン）と `DELETE`（オフ）の組**で切り替える（例: `PUT /invoice/{id}/paid`）。本体を `DELETE` で消すのではなくフラグを立て倒しする設計
- PDF 取得に加え、請求書の郵送（`send_by_postal_mail`）や見積書のメール送付（`distribute`）も API で指示できる

### 認証の流れ

1. `https://app.misoca.jp/oauth2/applications` でアプリ名とコールバック URL を登録し、アプリケーション ID とシークレットを得る
2. `/oauth2/authorize` で認可、`/oauth2/token` でトークン取得
3. `Authorization` ヘッダーにトークンを載せて呼ぶ（書式は明記されておらず、一般的な `Bearer` 形式で試す）。疎通確認は `GET /user/me` が手堅い

アクセストークンの有効期限は **1 日**（2019 年 6 月に 90 日から短縮）。夜間バッチは毎回リフレッシュする前提で作る。

### ページングと差分同期

- `page`（既定 1）と `per_page`（既定 25、最大 100）。次・最後のページは `Link` ヘッダーの `rel="next"` / `rel="last"` に入るので、全件取得はこれをたどる
- `GET /invoices` は請求日・支払期限・更新日の範囲、`payment_status`、`invoice_status`、`contact_group_id` で絞り込める
- `updated_at_from` で差分同期が書けるが日付単位なので、同じ請求書を再取得しうる。ID で重複除去を入れる

### 使う前の制約

ドキュメントは「現状有姿」での提供、予告なしの仕様変更あり、サポートなし、損害について弥生は責任を負わない、と明記している。レート制限の記載もない。基幹に組み込むなら、リトライとバックオフ、レスポンスのスキーマ検証、Swagger JSON の定期的な差分取得などを自前で入れる。

### freee との比較

| 観点 | freee | 弥生 |
|---|---|---|
| 会計 API | freee会計 API で取引・振替伝票を登録できる | 公開 API は見当たらない |
| 請求書 API | freee請求書 API | Misoca API v3 |
| アクセストークン | 6 時間（リフレッシュトークン 90 日） | 1 日（リフレッシュトークンの期限は記載なし） |
| サポート | リファレンス・チュートリアル・リリースノートあり | 現状有姿・サポートなし |

弥生会計へのデータ投入は、口座連携（金融機関 1,100 件以上）、スマート取引取込（ScanSnap Cloud や POS レジアプリ等）、CSV 取込で行い、自社システムから仕訳を直接書き込む公開経路はない。基幹から会計まで API で自動化したいなら freee が向く。

## 関連ページ

- [JWT Bearer Grant](/blogs/wiki/concepts/jwt-bearer-grant/) — OAuth のトークン発行方式の一つ
- [Google API の OAuth 設定](/blogs/wiki/guides/google-api-oauth-ga4-search-console/) — OAuth 必須の API で refresh_token の失効に対処する例

## ソース記事

- [弥生の Misoca API v3 を読む — OAuth2 で請求書・見積書・納品書を操作する](/blogs/posts/2026/11/misoca-api-v3/) — 2026-11-06
