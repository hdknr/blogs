---
title: "弥生の Misoca API v3 を読む — OAuth2 で請求書・見積書・納品書を操作する"
date: 2026-11-06
lastmod: 2026-11-06
slug: "misoca-api-v3"
draft: false
source_url: "https://github.com/hdknr/blogs/issues/572#issuecomment-6678318673"
categories: ["Web開発"]
tags: ["Misoca", "弥生", "API", "OAuth", "請求書"]
---

弥生（弥生株式会社）は会計ソフト「弥生会計」の会社ですが、クラウド請求書サービス **Misoca（ミソカ）** も提供しています。Misoca には外部 API があり、仕様は [doc.misoca.jp](https://doc.misoca.jp/) で公開されています。

この記事では、Misoca API v3 のドキュメントを読んで、次の 4 点を整理します。

- 何ができるか（扱えるリソース）
- どう認証するか（OAuth2 の流れ）
- 一覧取得のページングと絞り込み
- 使う前に知っておくべき制約

社内の販売管理システムや CRM から請求書を自動で起こしたい、と考えている人向けのメモです。

## Misoca API の概要

| 項目 | 内容 |
|---|---|
| 現行バージョン | v3（2016 年 12 月 1 日公開） |
| エンドポイント | `https://app.misoca.jp/api/v3/` |
| 認証 | OAuth2（スコープは `read` / `write`） |
| 仕様書 | Swagger 2.0（`https://app.misoca.jp/api/v3/swagger_doc`） |
| 旧版 | v1 は 2021 年 4 月 1 日に提供終了 |

ドキュメントの更新履歴を見ると、2024 年 1 月に納品書 API と品目 API が追加されています。2016 年公開の API ですが、今も機能追加が続いています。

## 扱えるリソース

Swagger の定義から、主なエンドポイントを表にまとめました。

| リソース | 主なエンドポイント |
|---|---|
| 請求書 | `GET /invoices`, `POST /invoice`, `GET /invoice/{id}`, `GET /invoice/{id}/pdf` |
| 見積書 | `GET /estimates`, `POST /estimate`, `GET /estimate/{id}/pdf`, `POST /estimate/{id}/distribute` |
| 納品書 | `GET /delivery_slips`, `POST /delivery_slip`, `GET /delivery_slip/{id}/pdf` |
| 取引先 | `GET /contact_groups`, `POST /contact_group` |
| 送り先 | `GET /contacts`, `POST /contact` |
| 品目 | `GET /dealing_items`, `POST /dealing_item` |
| ユーザー | `GET /user/me` |

一覧の取得は複数形のパス（`/invoices`）、1 件の取得や作成は単数形のパス（`/invoice`）です。Rails 系 API でよく見る `/invoices/{id}` 形式とは違うので、クライアントを書くときに間違えやすいところです。

### 状態の変更は PUT / DELETE の組で表す

請求書の「支払済み」「送付済み」「ゴミ箱」は、専用のサブリソースに対する `PUT`（オン）と `DELETE`（オフ）の組で切り替えます。

```text
PUT    /invoice/{id}/paid        # 支払済みにする
DELETE /invoice/{id}/paid        # 支払済みを取り消す
PUT    /invoice/{id}/submitted   # 送付済みにする
DELETE /invoice/{id}/submitted   # 送付済みを取り消す
PUT    /invoice/{id}/trashed     # ゴミ箱に入れる
DELETE /invoice/{id}/trashed     # ゴミ箱から戻す
```

取引先と送り先も同じく `trashed` で非表示（`PUT`）と再表示（`DELETE`）を切り替えます。リソース本体の `DELETE` で消すのではなく、フラグを立てたり倒したりする設計です。

### 郵送とメール送付も API から

`POST /invoice/{id}/send_by_postal_mail` で請求書の郵送を、`POST /estimate/{id}/distribute` で見積書のメール送付を指示できます。PDF を作るだけでなく、送付まで API で完結させられます。

## 認証: OAuth2 の流れ

Misoca API はユーザーの代わりに操作する API なので、API キー方式ではなく OAuth2 の認可コードフローを使います。

### 1. アプリケーションを登録する

Misoca にログインした状態で `https://app.misoca.jp/oauth2/applications` を開き、次の 2 つを登録します。

- 名称
- コールバック URL（1 行に 1 つ。登録した URL 以外へはリダイレクトされない）

登録後の画面に **アプリケーション ID** と **シークレット** が表示されます。

### 2. 認可とトークン取得

OAuth2 のエンドポイントは `https://app.misoca.jp/oauth2/` 配下です。

| 用途 | URL |
|---|---|
| 認可 | `https://app.misoca.jp/oauth2/authorize` |
| トークン | `https://app.misoca.jp/oauth2/token` |

スコープは `read` と `write` の 2 つです。`write` は `read` を含むので、作成や更新をするなら `write` だけを要求すれば足ります。

### 3. API を呼ぶ

取得したアクセストークンを `Authorization` ヘッダーに載せます。ドキュメントにはヘッダーの書式までは明記されていないため、以下の例では OAuth2 で一般的な `Bearer` 形式を使っています。まずは自分のユーザー情報で疎通を確認するのが手堅いです。

```bash
curl -H "Authorization: Bearer $MISOCA_ACCESS_TOKEN" \
  https://app.misoca.jp/api/v3/user/me
```

未払いの請求書を 100 件ずつ取得する例です。

```bash
curl -H "Authorization: Bearer $MISOCA_ACCESS_TOKEN" \
  "https://app.misoca.jp/api/v3/invoices?payment_status=unpaid&per_page=100&page=1"
```

### 補足: トークンの有効期限は 1 日

アクセストークンの有効期限は **1 日** です。以前は 90 日でしたが、2019 年 6 月に短くなりました。夜間バッチなどで使う場合は、毎回リフレッシュする前提で作る必要があります。

## ページングと検索条件

一覧 API のページングは `page` と `per_page` で指定します。

- `page` の既定値は 1
- `per_page` の既定値は 25、指定できる範囲は 1〜100
- 次のページと最後のページは、レスポンスの `Link` ヘッダー（Web Linking の仕様）に `rel="next"` / `rel="last"` として入る

全件を取るときは、ページ番号を自分で数えるより `Link` ヘッダーの `next` をたどるほうが確実です。

`GET /invoices` には絞り込み用のパラメータも揃っています。

| パラメータ | 意味 |
|---|---|
| `from` / `to` | 請求日の範囲 |
| `due_date_from` / `due_date_to` | 支払期限の範囲 |
| `updated_at_from` / `updated_at_to` | 更新日の範囲（`YYYY/MM/DD` の日付単位） |
| `payment_status` | `paid` / `unpaid` |
| `invoice_status` | `submitted` / `unsubmitted` |
| `contact_group_id` | 取引先で絞り込み |

`updated_at_from` があるので、前回の同期以降に変わった請求書だけを取る差分同期が書けます。ただし指定は日付単位です。前回と同じ日を起点に取り直すと同じ請求書を再び受け取りうるので、ID で重複を除く処理を入れておくと安全です。

## 使う前に知っておくべき制約

ドキュメントの冒頭には、次の注意書きがあります。

- API は「現状有姿」（動作を保証しない、の意味）で提供される
- 継続開発中で、予告なく仕様が変わることがある
- サポートは提供されない
- 仕様変更による損害について弥生は責任を負わない

レート制限の記載も見当たりません。業務の基幹に組み込むなら、次の対策を自前で入れておくのが無難です。

- リトライとバックオフ
- レスポンスのスキーマ検証
- 仕様変更を早めに検知する仕組み（Swagger JSON の差分を定期的に取るなど）

## freee と並べて比べる

請求書の API を検討するとき、比較対象になりやすいのが freee です。freee は請求書だけでなく会計そのものの API も公開しているので、「どこまで API で自動化できるか」が弥生と大きく違います。

### API の比較

| 観点 | freee | 弥生 |
|---|---|---|
| 会計 API | freee会計 API（取引や振替伝票を API で登録できる） | 外部開発者向けの公開 API は見当たらない |
| 請求書 API | freee請求書 API（`/invoices`・`/quotations`・`/delivery_slips`） | Misoca API v3（`/invoices`・`/estimates`・`/delivery_slips`） |
| 請求書と会計のつながり | 同じ freee の中で帳票と会計データを管理できる | Misoca と弥生会計は別の製品 |
| 認証 | OAuth 2.0 | OAuth2（Misoca） |
| アクセストークンの有効期限 | 6 時間（2022 年 7 月に 24 時間から短縮） | 1 日（Misoca） |
| リフレッシュトークンの有効期限 | 90 日 | ドキュメントに記載なし |
| サポート | 開発者サイトにリファレンス・チュートリアル・リリースノートがある | 現状有姿・サポートなし |

freee会計 API で取引を登録するには、事業所 ID（`company_id`）や勘定科目 ID（`account_item_id`）が必要です。これらは先に GET で取得しておきます。

### 弥生会計にデータを入れる手段

弥生も外部とのデータ連携はしていますが、手段は公開 API ではありません。

- **口座連携**: 銀行やカード会社と個別に API 連携し、明細を取り込む。2025 年 12 月時点で、データ連携できる金融機関は全国 1,100 件以上
- **スマート取引取込**: ScanSnap Cloud や POS レジアプリなどの外部サービスと連携し、取引を弥生会計に取り込む
- **CSV ファイル取込**: CSV 形式の明細ファイルを取り込む

つまり、自社のシステムから弥生会計へ仕訳を直接書き込む経路は、少なくとも公開情報の範囲では見当たりません。

### どちらを選ぶか

- 基幹システムや CRM から会計まで API で自動化したい → freee が向く
- 弥生を使い続ける → API で自動化できるのは請求（Misoca）まで。会計への取り込みは口座連携・スマート取引取込・CSV で補う

## まとめ

- Misoca API v3 では、請求書・見積書・納品書・取引先・品目を OAuth2 経由で操作できる
- 状態の変更は `PUT` / `DELETE` の組で表し、郵送やメール送付も API から指示できる
- トークンの有効期限は 1 日、一覧は最大 100 件ずつで `Link` ヘッダーをたどって取得する
- サポートなし・予告なしの仕様変更あり、という前提で、防御的にクライアントを作る
- freee は会計 API まで公開している。弥生については、調べた範囲で見つかった公開 API は Misoca だけ

弥生会計そのものではなく、その手前の請求業務を自動化したいなら、まず Misoca API を検討するとよいでしょう。
