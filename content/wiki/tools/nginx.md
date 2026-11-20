---
title: "nginx"
description: "Web サーバー・リバースプロキシの nginx。stable と mainline の 2 系統で配布される。2026 年 11 月の脆弱性 10 件（HTTP/2 の未認証 RCE のおそれを含む）への対応手順、HTTP/2 の無効化による暫定対策、更新後に古いワーカーが残っていないかの確認、証明書更新後の reload"
date: 2026-11-20
lastmod: 2026-11-20
aliases: ["Nginx", "NGINX", "NGINX Plus", "エンジンエックス"]
related_posts:
  - "/posts/2026/11/nginx-vulnerabilities-november-2026/"
  - "/posts/2026/03/letsencrypt-certbot-dns-route53/"
tags: ["nginx", "脆弱性", "HTTP/2", "security"]
---

## 概要

**nginx** は Web サーバー兼リバースプロキシで、HTTPS の終端やアプリケーションサーバーの前段として広く使われる。オープンソース版は **stable**（安定版）と **mainline**（新機能を含む開発版）の 2 系統で配布され、F5 が商用版の NGINX Plus を提供している。公開サーバーの前面に立つことが多いため、脆弱性が出たときの更新の速さがそのまま攻撃面の広さを決める。

## 詳細

### 2026 年 11 月の脆弱性 10 件

2026 年 11 月 18 日に F5 が 10 件を公表し、修正版 1.30.7（stable）と 1.31.9（mainline）を出した。影響範囲は 0.5.33 などの古い版からに及ぶため、**修正版より前の nginx はほぼすべて対象**と考える。

| 対象機能 | 主な内容 |
|---|---|
| HTTP/2 | フロー制御のメモリ破壊、use-after-free。未認証 RCE のおそれ |
| TLS 1.3 | リクエストボディ読み込み時の無限ループ（サービス停止） |
| HTTP/3・メールプロキシ・resolver | それぞれ use-after-free |
| stream | クライアント証明書検証の SNI バイパス、ssl_preread の検証不足 |
| その他 | PROXY プロトコル v2 の NULL 参照、alias と try_files 併用時のバッファオーバーフロー |

**重要度の評価は情報源で食い違う**。nginx.org で medium の 3 件を IPA は CVSS v4.0 で 9.2（Critical）としている。片方の重要度だけで後回しにしない。

### 対応の手順

1. **対象か確かめる**：`nginx -v` と `sudo nginx -T | grep -nE 'http2|listen'`。ディストリビューションのパッケージは番号が上流と違ったり修正がバックポートされていたりするので、各ディストリのセキュリティ情報も見る
2. **修正版へ更新する**：コンテナはベースイメージを更新して再ビルド・再デプロイする
3. **すぐ更新できないときの暫定策**：HTTP/2 を無効にする。`http2` ディレクティブ（1.25.1 以降）なら `http2 off;`、古い書き方なら `listen 443 ssl http2;` から `http2` を外す。塞がるのは HTTP/2 の 2 件だけで、**gRPC は HTTP/2 必須なので止まる**。更新後は元に戻す
4. **更新後に再起動し、古いプロセスを確かめる**：`ps -o pid,lstart,cmd -C nginx` でマスターとワーカーの起動時刻を見る

### reload と再起動の違い

`nginx -s reload`（`systemctl reload nginx`）は**設定と証明書を読み直す**が、**新しいバイナリは読み込まない**。

- 証明書を更新したとき（certbot の自動更新後のフックなど）は、`nginx -t` で設定を検査してから reload で足りる
- パッケージを更新したときは再起動が要る。reload 後も古いワーカーは長い接続を処理し終えるまで残るので、脆弱なコードが動き続けることがある

## 関連ページ

- [GitHub Actions のセキュリティ](/blogs/wiki/guides/github-actions-security/) — 依存の更新を速く回すための CI 側の備え
- [インシデント対応](/blogs/wiki/guides/incident-response/) — 公開サーバーの脆弱性が見つかったときの初動
- [CloudFront + ALB で HTTPS](/blogs/wiki/guides/cloudfront-alb-https/) — nginx の代わりにマネージドサービスで TLS を終端する構成

## ソース記事

- [nginx 脆弱性 10 件（2026年11月）：HTTP/2 で未認証 RCE のおそれ、1.30.7 / 1.31.9 へ更新を](/blogs/posts/2026/11/nginx-vulnerabilities-november-2026/) — 2026-11-19
- [開発サーバーの Let's Encrypt 証明書が切れたので自動更新できるようにした](/blogs/posts/2026/03/letsencrypt-certbot-dns-route53/) — 2026-03-17
