---
title: "RFC 7523 / JWT Bearer Grant"
description: "署名付き JWT（アサーション）を提示してトークンを発行してもらう OAuth のアサーション認可。モバイルの『1回ログイン → サービスごとのトークン』を支える"
date: 2026-06-24
lastmod: 2026-06-24
aliases: ["RFC 7523", "JWT Bearer Grant", "jwt-bearer", "JWTアサーション", "トークン交換"]
related_posts:
  - "/posts/2026/06/mobile-token-exchange-rfc-7523/"
tags: ["OAuth", "JWT", "RFC7523", "認証認可", "モバイル"]
---

## 概要

RFC 7523（JWT Profile for OAuth 2.0 / JWT Bearer Grant）は、署名付き JWT を「アサーション」として提示し、受け取った側にアクセストークンを発行してもらう OAuth のアサーション認可。`grant_type=urn:ietf:params:oauth:grant-type:jwt-bearer` を使う。モバイルアプリのように「ログインは1回だけ、トークンはサービスごとに分けたい」という要件を、IdP・RP の連携で実現する基盤になる。

## 詳細

### 登場人物と構図

- **IdP**（統合認証サーバー）— 身分証となる署名付き JWT を発行し、ユーザー照会に応える。トークンを発行するのは IdP ではない
- **RP**（各サービス）— IdP の身分証を信頼し、**自分専用のトークンを自分で発行**する（各 RP が小さな認可サーバーを兼ねる）
- **モバイルアプリ**（public client）— クライアントシークレットを安全に持てない。JWT を中継する役

ユーザーは IdP に1回ログインして JWT を1枚受け取り、その**同じ JWT** を各 RP に提示して、サービスごとのトークンを発行してもらう。

### 関連 RFC の役割分担

- **RFC 7521** — アサーションフレームワーク（土台の一般ルール）
- **RFC 7523** — JWT を1枚提示 → 受け取った側がトークン発行（このパターンに最も近い）
- **RFC 8693** — Token Exchange。中央の認可サーバーがトークンをトークンに交換する中央集約型で、7523 とは形が違う
- **RFC 7636 (PKCE)** — public client のログイン時に認可コード横取りを防ぐ

### 「2段の 7523」と `aud`

ユーザー確認を別プロトコルではなく 7523 で表現する設計では、JWT Bearer Grant を **client→RP** と **RP→IdP** の2段で使う。`aud`（audience）の扱いが要点：

- 1枚の JWT を複数 RP で使い回す設計では `aud` は特定 RP ではなく **IdP（または共通値）**
- `RP→IdP`（確定）が `aud=IdP` の教科書どおりの 7523。IdP は自己発行 JWT を検証してユーザーを確定する
- `app→RP` では RP は `aud` ではなく「IdP 発行の身分証を IdP に取り次ぐブローカー」として振る舞う
- RP→IdP では RP は confidential client として `client_id`/`client_secret` でも認証する（登録済み RP に限定。アサーションとは別レイヤー＝RFC 6749 のクライアント認証）

### なぜランダム文字列でなく署名付き JWT か

JWT は署名により**発行元（IdP）を公開鍵（JWKS）で検証できる**。不透明なランダム文字列は発行元への問い合わせなしには出所も完全性も検証できない。中継経路に信頼できない public client が挟まっても、改ざんは署名検証で検知できる。

### 標準化のための現実解

独自の grant_type 名（例: `urn:ietf:params:oauth:grant-type:assertion-grant`）を使うシステムは、**既存の認可サーバーにカスタムグラントを足して標準名 `jwt-bearer` へ寄せる**最小移行が現実的。Django なら django-allauth（認証）+ django-oauth-toolkit（AS）を活かしたまま拡張でき、Authlib への全面差し替えは RFC 8693 級の要件が出てから検討すれば足りる。

## 関連ページ

- [FIDO2/パスキー認証](/blogs/wiki/concepts/fido2-passkey/)
- [メール認証（SPF/DKIM/DMARC）](/blogs/wiki/concepts/email-authentication/)

## ソース記事

- [モバイルアプリの「1回ログイン → サービスごとのトークン」を支える仕組み — OAuth RFC 7523 入門](/blogs/posts/2026/06/mobile-token-exchange-rfc-7523/) — 2026-06-24
