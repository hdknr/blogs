---
title: "Mozilla Hubs / Hubs Community Edition"
description: "ブラウザで入れる共有 3D 空間サービス。Mozilla の公式提供は 2024 年に終了し、セルフホスト向けの Hubs CE がコミュニティで継続。AWS へのセルフホスト構成と、AWS サービス＋OSS による独自構築の比較"
date: 2026-11-19
lastmod: 2026-11-19
aliases: ["Hubs CE", "Hubs Cloud", "Mozilla Hubs 代替", "ソーシャル VR"]
related_posts:
  - "/posts/2026/11/mozilla-hubs-ce-aws-self-hosting/"
tags: ["aws", "WebRTC", "WebXR", "セルフホスト", "kubernetes"]
---

## 概要

Mozilla Hubs はブラウザだけで入れる 3D 空間を複数人で共有できるソーシャル VR サービス。Mozilla は 2024 年 2 月に終了を発表し、公式ホスティングとマネージド提供は 2024 年 5 月 31 日に停止した。自分の AWS アカウントに立てる Hubs Cloud（AWS Marketplace 版）も 2024 年初頭に提供を終えている。

ソースは OSS のまま残り、Mozilla が 2023 年に公開したセルフホスト向けの **Hubs Community Edition（Hubs CE）** を Hubs Foundation のもとでコミュニティが開発している。現実的な選択肢は「Hubs CE をセルフホスト」か「AWS のサービスと OSS で独自構築」の 2 つ。

## 詳細

### Hubs CE の構成

| コンポーネント | 役割 |
|---|---|
| Hubs クライアント / Spoke | ブラウザに配信するフロントエンドと 3D シーンエディタ |
| Reticulum | ルーム内メッセージを中継するバックエンド（Elixir 製） |
| Dialog | 音声・映像を中継する SFU（mediasoup ベース） |
| coturn | TURN サーバー（NAT 越え） |
| PostgreSQL | データベース |

公式手順は Kubernetes へのデプロイが前提で、AWS では EKS か EC2 上の k3s などで動かす。コミュニティの Helm チャートには小規模向け「Personal Edition」と、EKS・RDS を使う「Scale Edition」がある。

事前に必要なもの：

- 管理者権限のある AWS アカウント
- 独自ドメイン（ドメイン単位で動くため必須）
- メール送信（ログインはメールのリンク方式なので SMTP か Amazon SES）

### コストの注意点

- **常時稼働**：誰もいない時間もクラスターは動き続ける
- **データ転送量**：WebRTC の通信量は参加者数に比例し、AWS からの外向き転送は従量課金

イベント時だけ使うなら、インスタンス停止やノード数の増減を前提に設計しておく。

### 独自構築する場合の 3 層

| 層 | 主な部品 |
|---|---|
| ① 3D / WebXR クライアントと配信 | Three.js / A-Frame。HTML/JS と glTF などのアセットを S3 に置き CloudFront で配信（大きいアセットは CDN の効果が大きい） |
| ② リアルタイム同期と API | WebSocket。ECS / EKS の常駐コンテナ、または Lambda＋API Gateway WebSocket API。設定は RDS / DynamoDB。位置同期のような高頻度処理は状態をメモリに持つ常駐コンテナが扱いやすい |
| ③ 音声・映像 | mediasoup などの SFU を EC2 / ECS で運用し、STUN / TURN（coturn）を用意。UDP とポート開放が絡むため LB やセキュリティグループに注意 |

SFU と TURN を置く以上、③のコストは Hubs CE と変わらない。音声・映像を不要（テキストのみ、外部通話サービスに任せる）と割り切れるなら③を丸ごと省けるのが独自構築の最大の利点。

### 選び方

| 観点 | Hubs CE | 独自構築 |
|---|---|---|
| 利用形態 | 社内会議・イベントなど Hubs と同じ使い方 | 常時開放のコミュニティ、独自体験の作り込み |
| 規模・音声映像 | 小〜中規模で音声チャット込みの一式 | 大規模、または音声映像不要でコスト削減 |
| 開発の優先度 | 既存コードで早く立ち上げる | 工数をかけて機能とコストを制御する |

短期間で「Hubs 相当」を用意するなら Hubs CE、長期運用で独自性やコスト最適化を突き詰めるなら独自構築が目安。

### 用語

- **SFU**：参加者の音声・映像を受けて他の参加者へ転送するメディアサーバー。全員が全員と直接つなぐより通信量を抑えられる
- **STUN / TURN**：NAT 内の端末同士の WebRTC 接続を助けるサーバー。TURN は直接つながらないときに中継する

## 関連ページ

- [CloudFront + ALB で HTTPS 化](/blogs/wiki/guides/cloudfront-alb-https/) — 配信層の構成で参考になる AWS ガイド
- [AFFiNE](/blogs/wiki/tools/affine/) — 同じくセルフホストで公式サービスの代替にするツール

## ソース記事

- [Mozilla Hubs の代替は？Hubs CE を AWS でセルフホストする構成と独自構築の比較](/blogs/posts/2026/11/mozilla-hubs-ce-aws-self-hosting/) — 2026-11-19
