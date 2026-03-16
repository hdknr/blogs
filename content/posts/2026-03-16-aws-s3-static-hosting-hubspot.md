---
title: "AWS S3 静的ホスティングで HubSpot テーマのデザイン HTML をプレビューする"
date: 2026-03-16
lastmod: 2026-03-16
draft: false
source_url: "https://github.com/spin-dd/taihei-hubspot-theme/pull/8#issuecomment-4064528731"
categories: ["クラウド/インフラ"]
tags: ["aws"]
---

HubSpot テーマのデザイン HTML を関係者に共有する際、ローカルファイルを直接送るのは手間がかかります。AWS S3 の静的ウェブサイトホスティングを使えば、HTML ファイルをアップロードするだけで即座にブラウザから確認できる URL を発行できます。

本記事では、S3 バケットの作成からデプロイまでの手順をまとめます。

## S3 バケットの作成と設定

### 1. バケット作成

AWS マネジメントコンソールまたは CLI でバケットを作成します。

```bash
aws s3 mb s3://hubspot-tec --region ap-northeast-1
```

設定項目:

| 項目 | 値 |
|---|---|
| バケット名 | `hubspot-tec` |
| リージョン | `ap-northeast-1`（東京） |

### 2. 静的ウェブサイトホスティングの有効化

```bash
aws s3 website s3://hubspot-tec/ \
  --index-document home.html
```

### 3. パブリックアクセスの許可

S3 のデフォルトではパブリックアクセスがブロックされています。静的ホスティングで外部公開するには、以下の 2 つの設定が必要です。

**パブリックアクセスブロックの解除:**

```bash
aws s3api put-public-access-block \
  --bucket hubspot-tec \
  --public-access-block-configuration \
  BlockPublicAcls=false,IgnorePublicAcls=false,BlockPublicPolicy=false,RestrictPublicBuckets=false
```

**バケットポリシーの設定（パブリック読み取り許可）:**

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "PublicReadGetObject",
      "Effect": "Allow",
      "Principal": "*",
      "Action": "s3:GetObject",
      "Resource": "arn:aws:s3:::hubspot-tec/*"
    }
  ]
}
```

```bash
aws s3api put-bucket-policy \
  --bucket hubspot-tec \
  --policy file://bucket-policy.json
```

### 4. 公開 URL

設定完了後、以下の URL でアクセスできます。

```
http://<バケット名>.s3-website-<リージョン>.amazonaws.com
```

例: `http://hubspot-tec.s3-website-ap-northeast-1.amazonaws.com`

## IAM 権限設定

チームメンバーがデプロイできるよう、必要最小限の S3 権限を IAM ポリシーとして設定します。

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "s3:ListBucket",
        "s3:GetObject",
        "s3:PutObject",
        "s3:DeleteObject"
      ],
      "Resource": [
        "arn:aws:s3:::hubspot-tec",
        "arn:aws:s3:::hubspot-tec/*"
      ]
    }
  ]
}
```

各権限の用途:

| アクション | 用途 |
|---|---|
| `s3:ListBucket` | バケット内のファイル一覧取得 |
| `s3:GetObject` | ファイルのダウンロード |
| `s3:PutObject` | ファイルのアップロード |
| `s3:DeleteObject` | `sync --delete` での不要ファイル削除 |

## デプロイ

`aws s3 sync` コマンドでローカルの HTML ディレクトリを S3 に同期します。

```bash
aws s3 sync ./html/ s3://hubspot-tec/
```

`--delete` オプションを付けると、ローカルに存在しないファイルを S3 からも削除します。

```bash
aws s3 sync ./html/ s3://hubspot-tec/ --delete
```

## 注意点

- S3 静的ホスティングの URL は **HTTP のみ**（HTTPS 非対応）です。HTTPS が必要な場合は CloudFront を前段に配置してください
- パブリック公開するため、機密情報を含むファイルはアップロードしないよう注意してください
- 本番環境ではなくデザインプレビュー用途での利用を想定しています
