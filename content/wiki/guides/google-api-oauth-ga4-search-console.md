---
title: "GA4・Search Console API の OAuth 設定"
description: "Google Cloud Console での認証情報の使い分けと、refresh_token が 7 日で失効する罠の回避"
date: 2026-07-28
lastmod: 2026-07-28
aliases: ["refresh_token 7日", "org_internal", "OAuth 同意画面", "GA4 API 認証"]
related_posts:
  - "/posts/2026/07/google-cloud-console-ga4-oauth-credentials/"
tags: ["GA4", "Google Search Console", "OAuth", "gcp", "refresh_token"]
---

## 概要

GA4 / Search Console を API から叩く場合、**API キーでは呼べず OAuth が必須**である。Google Cloud Console のどの画面で何を発行するかが分かりにくく、さらに `refresh_token` が 7 日で失効する罠がある。

## 認証情報は3種類

呼ぶ API によって使い分ける。

| 発行するもの | Console の画面 | 使える API | 必要数 |
|---|---|---|---|
| **API キー**（`AIza...`） | 認証情報 > API キー | **PageSpeed Insights だけ** | 1 本を使い回せる |
| **OAuth クライアント**（`client_id` / `client_secret`） | 認証情報 > OAuth クライアント ID | GA4 Data / GA4 Admin / Search Console | プロジェクトに 1 つ（共用） |
| **`refresh_token`** | Console では発行しない（自アプリのブラウザ認可で取得） | 同上 | **スコープごとに 1 つ** |

最大の誤解は「API キーがあれば GA4 も呼べる」と思い込むこと。**API キーの出番は PageSpeed Insights だけ**である。

## 設定手順

1. **プロジェクトを選ぶ** — すべての作業の前に。プロジェクト取り違えが後続の全エラーの原因になる
2. **API を有効化する** — GA4 Data API / GA4 Admin API / Search Console API を個別に有効化
3. **OAuth 認証情報を発行する** — OAuth 同意画面（Audience）の設定を含む
4. **API キーを発行する** — PageSpeed Insights 専用。キー制限をかけておく

## 罠1: `refresh_token` が 7 日で失効する

OAuth 同意画面の User type を **External** にしたうえで、公開ステータスが**「テスト中」のままだと `refresh_token` の有効期限が 7 日**になる。

自動化バッチを組んで運用に載せた 1 週間後に突然すべて 401 で落ちる、という形で顕在化するため、原因にたどり着きにくい。

**対処**: OAuth 同意画面で **「公開（Publish app）」を実行する**。External を選んだら公開までがワンセットだと覚えておく。

## 罠2: `org_internal` でブロックされる

「組織内のユーザーのみが利用できます」というエラー。User type が Internal になっていると、組織外アカウント（個人 Google アカウントなど）で認可できない。

**対処**: User type を External に変更する。

## 運用チェックリスト

- プロジェクトは意図したものを選んでいるか
- 使う API がすべて有効化されているか
- OAuth 同意画面は External かつ**公開済み**か
- `refresh_token` はスコープごとに取得・保管されているか
- API キーには適切な制限（リファラ／IP／API 種別）がかかっているか

## 関連ページ

- [AI エージェントのシークレット管理](/blogs/wiki/guides/ai-agent-secret-management/) — 取得した認証情報の保管
- [JWT Bearer Grant](/blogs/wiki/concepts/jwt-bearer-grant/) — サーバー間認証の別方式

## ソース記事

- [GA4・Search Console API 認証設定ガイド — refresh_token が 7 日で失効する罠](/blogs/posts/2026/07/google-cloud-console-ga4-oauth-credentials/) — 2026-07-27
