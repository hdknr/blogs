---
title: "Mozilla Hubs の代替は？Hubs CE を AWS でセルフホストする構成と独自構築の比較"
date: 2026-11-19
lastmod: 2026-11-19
slug: "mozilla-hubs-ce-aws-self-hosting"
draft: false
source_url: "https://github.com/hdknr/blogs/issues/694#issuecomment-6999838912"
categories: ["クラウド/インフラ"]
tags: ["aws", "WebRTC", "WebXR", "セルフホスト", "kubernetes"]
---

## はじめに

ブラウザだけで入れる 3D 空間をみんなで共有できる **Mozilla Hubs** は、社内イベントやオンライン勉強会の会場として重宝されてきました。ところが Mozilla は 2024 年 2 月に Hubs の終了を発表し、公式ホスティング（hubs.mozilla.com）とマネージド提供は 2024 年 5 月 31 日に停止しました。自分の AWS アカウントに Hubs を立てる **Hubs Cloud**（AWS Marketplace 版）も、それより早く 2024 年初頭に AWS 上でのサポートと新規提供を終えています。

一方で、ソースコードはオープンソースのまま残っています。Mozilla が 2023 年に公開したセルフホスト向けの **Hubs Community Edition（Hubs CE）** は、現在 Hubs Foundation のもとでコミュニティが開発を続けています。そのため、いま「Hubs と同じようなサービスを使いたい」となったときの現実的な選択肢は次の 2 つです。

1. **Hubs CE を AWS にセルフホストする** — 既存の Hubs の機能をそのまま使う
2. **AWS のサービスと OSS を組み合わせて独自に構築する** — 必要な機能だけを選んで作る

この記事では、それぞれの構成とコスト面の注意点を整理し、どちらを選ぶかの目安を示します。具体的なデプロイ手順は参考リンクを参照してください。

## 登場するプロダクトと用語

| 名前 | 何か |
|---|---|
| Mozilla Hubs | Mozilla が開発したブラウザ向けのソーシャル VR 空間サービス。公式提供は 2024 年 5 月 31 日に終了 |
| Hubs Cloud | Hubs を自分の AWS アカウントに立てるための公式パッケージ（AWS Marketplace で提供）。2024 年初頭に提供終了 |
| Hubs Community Edition（Hubs CE） | 自分で Hubs を立てるためのコミュニティ版。Kubernetes 上で動かす前提 |
| Spoke | Hubs 用の 3D シーンエディタ。Hubs CE にも含まれる |

| 用語 | 意味 |
|---|---|
| WebXR | ブラウザから VR/AR デバイスを扱うための Web 標準 API |
| WebRTC | ブラウザ同士で音声・映像・データをリアルタイムにやり取りする仕組み |
| SFU（Selective Forwarding Unit） | 各参加者の音声・映像を受け取り、他の参加者へ転送するメディアサーバー。全員が全員と直接つながるより通信量を抑えられる |
| STUN / TURN | NAT やファイアウォールの内側にいる端末同士の WebRTC 接続を助けるサーバー。TURN は直接つながらない場合に通信を中継する |
| mediasoup | Node.js から使う SFU ライブラリ |
| Helm / k3s | Helm は Kubernetes 向けのパッケージマネージャー、k3s は 1 台のマシンでも動かせる軽量な Kubernetes |

## 選択肢 1: Hubs CE を AWS にセルフホストする

Hubs の空間共有、アバター、音声チャット、Spoke によるシーン編集といった既存の仕組みをそのまま活かしたいなら、Hubs CE を AWS に立てるのが近道です。

### 事前に用意するもの

- **管理者権限のある AWS アカウント**
- **独自ドメイン**（Hubs CE はドメイン単位で動くため必須）
- **メール送信の設定**（ログインはパスワードではなく、メールに届くリンクを開いて行うため、SMTP サーバーまたは Amazon SES などが必要）

### デプロイ構成

Hubs CE は複数のコンポーネントをコンテナとして動かします。主なものは次のとおりです。

- **Hubs クライアント / Spoke** — ブラウザに配信されるフロントエンド
- **Reticulum** — ルーム内のメッセージを中継するバックエンド（Elixir 製）
- **Dialog** — 音声・映像を中継する SFU（mediasoup ベース）
- **coturn** — TURN サーバー
- **PostgreSQL** — データベース

公式の手順は Kubernetes クラスターへのデプロイを前提にしています。AWS では Amazon EKS を使うか、EC2 上に k3s などを立てて動かすことになります。コミュニティメンバーの Alex Griggs 氏は Hubs CE 向けの Helm チャートを公開しており、小規模向けの「Personal Edition」と、EKS や RDS を使う大規模向けの「Scale Edition」のガイドがあります（[Personal Edition の解説記事](https://medium.com/@alexgriggs/deploying-mozilla-hubs-ce-on-aws-with-ease-a-guide-to-the-personal-edition-helm-chart-fb7328edbdea)）。

### コストに注意する

Hubs CE の運用でいちばん効いてくるのはコストです。

- **常時稼働のインスタンス代**: 誰も入っていない時間もクラスターは動き続ける
- **データ転送量**: 音声・映像（WebRTC）の通信は参加者数に比例して増え、AWS から外向きのデータ転送は従量課金

イベントのときだけ使うのであれば、使わない時間のインスタンス停止や、利用時間に合わせたノード数の増減を前提に設計しておくと安心です。

## 選択肢 2: AWS のサービスと OSS で独自に構築する

「Hubs の機能をすべては使わない」「コストや拡張性を細かく制御したい」という場合は、機能ごとに部品を選んで組み上げる方法があります。構成は大きく 3 つの層に分かれます。

![AWS 上に WebXR の共有空間を独自構築する構成例。ブラウザや VR 機器のクライアントが、CloudFront 経由で S3 から HTML と 3D アセットを取得し、WebSocket で ALB または API Gateway を通して ECS・EKS・Lambda 上の同期サーバーにつながり、ユーザーやルームの設定は RDS または DynamoDB に保存する。音声と映像は WebRTC で EC2 や ECS 上の mediasoup などの SFU に送られ、NAT 越えには STUN/TURN サーバーを使う。](/blogs/images/webxr-aws-self-built-architecture.png)

### ① 3D / WebXR クライアントと配信

- **Three.js** や **A-Frame** でブラウザ向けの 3D 空間を作る
- ビルドした HTML/JS と、3D モデル（glTF など）・テクスチャを **Amazon S3** に置き、**Amazon CloudFront** で配信する

3D アセットはファイルサイズが大きくなりがちなので、CDN でキャッシュさせる効果が大きい部分です。

### ② リアルタイム同期と API

- アバターの位置同期やルームの入退室管理には **WebSocket** を使う
- サーバーは **Amazon ECS** / **Amazon EKS** 上のコンテナ、あるいは **AWS Lambda** と **API Gateway の WebSocket API** の組み合わせで動かす
- ユーザーやルームの設定データは **Amazon RDS** や **Amazon DynamoDB** に保存する

位置同期のように更新頻度が高い処理は、ルームの状態をメモリに持ったまま処理できる常駐コンテナで受けたほうが扱いやすいことが多いです。

### ③ 音声・映像（WebRTC）

- 複数人での音声通話や画面共有には、**mediasoup** などの SFU を EC2 / ECS で運用する
- NAT の内側にいる参加者のために **STUN / TURN サーバー**（coturn など）も用意する

この層は UDP の通信とポート開放が絡むため、ロードバランサーの選び方やセキュリティグループの設定に、通常の Web アプリとは違う注意が必要です。Hubs CE でも同じ構成（Dialog + coturn）をとっているので、仕組みを理解するための参考になります。

なお、SFU と TURN を自分で置く以上、選択肢 1 と同じくデータ転送量と常時稼働のコストはかかります。音声・映像を使わない（テキストチャットだけにする、外部の通話サービスに任せる）と割り切れるなら、この層を丸ごと省けるのが独自構築の大きな利点です。

## Hubs CE と独自構築のどちらを選ぶか

次の 3 つの観点をはっきりさせておくと判断しやすくなります。

| 観点 | Hubs CE に向くケース | 独自構築に向くケース |
|---|---|---|
| 利用形態 | 社内会議・イベントなど、Hubs と同じ使い方で足りる | 常時開放のコミュニティを運営したい、または独自の体験を作り込みたい |
| 規模と音声・映像の要否 | 小〜中規模で、音声チャットを含めて一式ほしい | 規模が大きい、または音声・映像が不要でコストを削りたい |
| 開発の優先度 | 既存コードを活かして早く立ち上げたい | 開発工数をかけてでも、機能とコストを自分で制御したい |

短期間で「Hubs 相当」を用意したいなら Hubs CE、長く運用するサービスとして独自性やコスト最適化を突き詰めたいなら独自構築、というのが大まかな目安です。

## まとめ

- Mozilla Hubs の公式ホスティングと Hubs Cloud は 2024 年に終了したが、ソースは Hubs Community Edition として引き継がれている
- Hubs CE を AWS（Kubernetes）にセルフホストすれば、既存の Hubs の機能をそのまま使える。ただし常時稼働と WebRTC の通信量でコストが膨らみやすい
- 独自構築なら、配信（S3 + CloudFront）・同期（WebSocket + ECS/EKS/Lambda）・音声映像（SFU + TURN）の 3 層を必要な分だけ選べる
- どちらにするかは、利用形態・規模と音声・映像の要否・開発の優先度で決める

## 参考

- [Mozilla Hubs のサポート終了（Mozilla サポート）](https://support.mozilla.org/ja/kb/end-support-mozilla-hubs)
- [Hubs CE のソースとデプロイ手順（Hubs-Foundation/hubs-cloud）](https://github.com/Hubs-Foundation/hubs-cloud/tree/master/community-edition)
- [Mozilla Ceases Support for Mozilla Hubs, But the Open-Source Hubs Community Edition Continues（Ryan Schultz）](https://ryanschultz.com/2024/02/26/mozilla-ceases-support-for-mozilla-hubs-but-the-open-source-hubs-community-edition-continues/)
- [Deploying Mozilla Hubs CE on AWS with Ease: A Guide to the Personal Edition Helm Chart（Alex Griggs）](https://medium.com/@alexgriggs/deploying-mozilla-hubs-ce-on-aws-with-ease-a-guide-to-the-personal-edition-helm-chart-fb7328edbdea)
- [Hubs の構成と導入メモ（フレームシンセシス）](https://tech.framesynthesis.co.jp/hubs/)
- [AWS で実現するメタバース（AWS 資料・PDF）](https://pages.awscloud.com/rs/112-TZM-766/images/20220707-Game-2_AWS_Metaverse.pdf)
