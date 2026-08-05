---
title: "Google Business Profile API"
description: "Googleビジネスプロフィールを機械的に管理するための API 群。用途ごとに8つに分割されているが、口コミ・投稿はレガシー v4 にしか存在しない"
date: 2026-08-05
lastmod: 2026-08-05
aliases: ["GBP API", "Googleビジネスプロフィール API", "Google My Business API", "GMB API", "MEO API", "businessprofileperformance"]
related_posts:
  - "/posts/2026/08/google-business-profile-api/"
tags: ["Google Business Profile", "Google My Business API", "MEO", "ローカルビジネス", "python"]
---

## 概要

Google ビジネスプロフィール（GBP）を API から管理するための API 群。かつては Google My Business API（v4.9）という単一 API だったが、2021年に**用途ごとの分割**が行われ、現在は機能領域ごとに独立したホスト名を持つ。OAuth スコープは全 API 共通で `https://www.googleapis.com/auth/business.manage` の1本。

## API の構成

| API | ホスト名の接頭辞 | 守備範囲 |
| --- | --- | --- |
| Account Management | `mybusinessaccountmanagement` | アカウント、管理者、招待、ロケーション移管 |
| Business Information | `mybusinessbusinessinformation` | 店舗情報、営業時間、属性、カテゴリ |
| Performance | `businessprofileperformance` | 表示回数、電話、経路リクエスト |
| Verifications | `mybusinessverifications` | オーナー確認、Voice of Merchant 状態 |
| Q&A | `mybusinessqanda` | 質問と回答 |
| Place Actions | `mybusinessplaceactions` | 予約・注文などの導線リンク |
| Notifications | `mybusinessnotifications` | Pub/Sub 通知設定 |
| Lodging | `mybusinesslodging` | 宿泊施設向け属性 |

ホスト名は `<接頭辞>.googleapis.com`。**Performance API だけ `businessprofile` 始まり**である点が実装時の落とし穴になる。

ドキュメントの目次には v1.1 / v1.2 という表記があるが、これは URL パスの版ではない。discovery document はいずれも `version: v1` を返すため、**パスは全 API で `/v1`** に揃う。

## 口コミ・投稿はレガシー v4 にしかない

分割は完全な置き換えではなく、**集客に直結する機能ほど v4（`mybusiness.googleapis.com/v4`）に残っている**。

- `accounts.locations.reviews` — 口コミの取得・返信
- `accounts.locations.localPosts` — 投稿
- `accounts.locations.media` — 写真・動画
- `accounts.locations.updateFoodMenus` / `updateServiceList` — メニューとサービス

したがって実装は新旧2系統の併用が前提になる。パス構造も分割 API が `locations/*`、v4 が `accounts/*/locations/*` と異なる（数値 ID 自体は共通）。

## 利用には申請と承認が要る

Cloud コンソールで有効化すれば使える類の API ではない。承認されるまで**クォータが 0 QPM に固定**される。

- 申請条件: 検証済みかつ **60日以上アクティブ**な GBP を管理していること、事業を表すウェブサイトがあること
- 申請は GBP API contact form から「Application for Basic API Access」を選択。送信元は GBP のオーナー／管理者メールアドレス
- 承認判定: クォータが **0 QPM なら未承認、300 QPM なら承認済み**。この 300 QPM が全 API 合算の本番レート制限になる

公式の Basic setup が有効化対象として挙げるのは8つ（分割 API のうち Performance を除く7つ ＋ レガシー v4）で、**Performance API は含まれていない**。インサイトを使うなら別途有効化する。

## 実装上の注意

- **サンドボックス環境がない**。書き込みのテストは本番データに当たる。`locations.patch` などは `validateOnly` に対応している
- `locations.list` は `readMask` が必須（省略で 400）。`pageSize` は既定10・上限100
- `locations.patch` は `updateMask` が必須。マスクに載せない項目は変更されない
- アクセストークンは約1時間で失効するため、長時間バッチでは `AuthorizedSession` などで自動更新する
- 旧 `reportInsights` は 2023-03-30 に廃止。表示回数はデスクトップ／モバイルに分割され、写真閲覧数とクエリ種別内訳は代替なしで消滅した

## 関連ページ

- [Google API の OAuth 設定（GA4・Search Console）](/blogs/wiki/guides/google-api-oauth-ga4-search-console/) — 認証まわりの落とし穴
- [サーキットブレーカー](/blogs/wiki/concepts/circuit-breaker/) — レート制限への対処

## ソース記事

- [GoogleビジネスプロフィールをAPIで管理する — 分割された8つのAPIと、v4に残る口コミ・投稿](/blogs/posts/2026/08/google-business-profile-api/) — 2026-08-05
