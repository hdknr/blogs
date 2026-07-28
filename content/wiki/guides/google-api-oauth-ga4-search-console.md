---
title: "GA4 / Search Console API の認証設定"
description: "GA4 と Search Console は API キーでは呼べず OAuth 必須。Google Cloud Console での発行手順と、refresh_token が 7 日で失効する原因・org_internal エラーの対処"
date: 2026-07-28
lastmod: 2026-07-28
aliases: ["GA4 API 認証", "Search Console API", "PageSpeed Insights API", "refresh_token 失効", "org_internal", "OAuth 同意画面", "Audience"]
related_posts:
  - "/posts/2026/07/google-cloud-console-ga4-oauth-credentials/"
tags: ["GA4", "Google Search Console", "OAuth", "gcp", "security"]
---

## 概要

GA4 / Search Console / PageSpeed Insights をプログラムから叩くとき、最初にぶつかるのが「Google Cloud Console のどの画面で何を発行するのか」という壁。**認証情報は 3 種類あり、呼ぶ API によって使い分ける**という非対称性が混乱の元になる。

## まず結論: API キーを使うのは PageSpeed だけ

| 発行するもの | Console の画面 | 使える API | いくつ必要か |
|---|---|---|---|
| **API キー**（`AIza...`） | 認証情報 > API キー | **PageSpeed Insights だけ** | 1 本を使い回せる |
| **OAuth クライアント**（`client_id` / `client_secret`） | 認証情報 > OAuth クライアント ID | GA4 Data / GA4 Admin / Search Console | **プロジェクトに 1 つ**（全部で共用） |
| **`refresh_token`** | Console では発行しない（自分のアプリのブラウザ認可で取得） | 同上 | **スコープごとに 1 つ** |

- **GA4 と Search Console は API キーでは呼べない。** OAuth 必須。「GA4 の API キー」を Console で探し回っても存在しない。ユーザー個人のデータを読む API なので「誰の権限で読むのか」を示す OAuth が要る
- **PageSpeed Insights は逆に OAuth 不要。** 公開 URL を外から測るだけなので誰の権限も要らない。API キーは**割り当て（quota）を増やすため**だけに使う

GA4 Data API・GA4 Admin API・Search Console API の 3 つは OAuth クライアント 1 つを共用し、そこからスコープごとに `refresh_token` を取得する。OAuth 同意画面（対象 / Audience）の設定はプロジェクトに 1 回だけで全体に効く。

## プロジェクトは 1 つにまとめる

API ごとにプロジェクトを分ける必要はない。むしろ分けると「OAuth クライアントを作ったプロジェクトと、API を有効化したプロジェクトが違う」という **403 の定番事故**を踏む。

## 手順

### 1. プロジェクトを選ぶ（すべての作業の前に）

Console の操作は**すべて同じプロジェクトを選んだ状態**で行う。ここを外すと「有効にしたはずなのに 403」という最も多い失敗になる。

1. 画面上部の**プロジェクトセレクタ**が対象プロジェクトになっているか確認
2. 右上アバターの**メールアドレス**が、対象の GA4 プロパティ / Search Console サイトを管理しているアカウントと同じか確認

2 番目は地味だが重要。複数の Google アカウントにログインしていると、URL の `authuser=` の違いだけで別人として操作していることがある。

### 2. API を有効化する

使う API（GA4 Data / GA4 Admin / Search Console / PageSpeed Insights）を、選んだプロジェクトで有効化する。

### 3. OAuth 認証情報を発行する

認証情報 > OAuth クライアント ID から発行し、`client_id` / `client_secret` を取得する。あわせて OAuth 同意画面（対象 / Audience）を設定する。

### 4. API キーを発行する（PageSpeed 専用）

PageSpeed Insights だけは API キーを発行し、必要に応じて利用制限をかける。

## 主要な落とし穴

### refresh_token が 7 日で失効する

OAuth 同意画面の公開ステータスが**テスト（Testing）のままだと、発行された `refresh_token` は 7 日で失効する**。運用に載せるなら同意画面を本番公開の状態にする必要がある。「動いていたのに 1 週間後に必ず落ちる」症状の原因はほぼこれ。

### org_internal でブロックされる

同意画面の対象（Audience）が組織内部（internal）に設定されていると、「組織内のユーザーのみが利用できます」という `org_internal` エラーでブロックされる。組織外のアカウントで認可する場合は対象を外部（external）にする必要がある。

### 403 の切り分け

- 有効化したプロジェクトと OAuth クライアントのプロジェクトが違う
- ログイン中の Google アカウントが対象プロパティ／サイトの管理者ではない
- 必要なスコープを含めずに `refresh_token` を取得している（スコープごとにトークンが要る）

## 運用に載せるときのチェックリスト

- OAuth 同意画面は本番公開状態か（テストのままなら 7 日で死ぬ）
- 対象（Audience）は internal / external のどちらが正しいか
- `refresh_token` はスコープごとに取得・保管されているか
- API キーは PageSpeed 専用として制限がかかっているか
- すべての操作が同一プロジェクト・同一アカウントで行われているか

## 関連ページ

- [claude-seo](/blogs/wiki/tools/claude-seo/) — GA4 / Search Console データを使う分析自動化
- [AI エージェントのシークレット管理](/blogs/wiki/guides/ai-agent-secret-management/) — client_secret / refresh_token の保管
- [JWT Bearer Grant](/blogs/wiki/concepts/jwt-bearer-grant/) — サービスアカウント方式との比較

## ソース記事

- [GA4・Search Console API 認証設定ガイド — refresh_token が 7 日で失効する罠](/blogs/posts/2026/07/google-cloud-console-ga4-oauth-credentials/) — 2026-07-27
