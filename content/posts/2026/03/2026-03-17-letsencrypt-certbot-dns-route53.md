---
title: "開発サーバーの Let's Encrypt 証明書が切れたので自動更新できるようにした"
date: 2026-03-17
lastmod: 2026-03-17
draft: false
categories: ["クラウド/インフラ"]
tags: ["aws", "nginx"]
source_url: "https://gist.github.com/hdknr/dc0d7b4fd7308222ef4b981c9270a7a4"
---

## きっかけ

ある日、開発環境の Web アプリにアクセスしたら証明書の期限切れ警告が表示された。

確認してみると、ワイルドカード証明書 (`*.dev.example.com`) がちょうどその日に期限切れになっていた。さらにもう1つ古い証明書も半年前に失効済み。

```
Certificate Name: dev.example.com-0001
    Domains: *.dev.example.com
    Expiry Date: 2026-03-17 (INVALID: EXPIRED)

Certificate Name: dev.example.com
    Domains: *.dev.example.com dev.example.com
    Expiry Date: 2025-09-17 (INVALID: EXPIRED)
```

## 原因

certbot の renewal 設定を確認したところ、問題が見えた。

```ini
[renewalparams]
authenticator = manual
pref_challs = dns-01,
```

**authenticator が `manual`** になっていた。

ワイルドカード証明書は DNS-01 チャレンジが必須だが、`manual` モードでは certbot が更新のたびに「この TXT レコードを DNS に追加してください」と対話的に聞いてくる。つまり **自動更新が不可能** な状態だった。

systemd timer (`certbot.timer`) は1日2回動いていたが、`manual` モードの証明書は自動更新をスキップされるため、期限切れまで放置されていた。

## 対応方針

2つの選択肢を検討した。

| 方法 | 内容 | メリット | デメリット |
|------|------|----------|-----------|
| A. 手動更新 | SSH して certbot を手動実行、DNS レコードを手動追加 | 即時対応可能 | 90日後にまた同じ作業が必要 |
| B. dns-route53 プラグイン | IAM ロールで Route53 権限を付与、certbot が自動で DNS チャレンジ | 恒久的に自動更新 | Terraform 変更 + EC2 設定が必要 |

**方法 B** を採用した。少し手間はかかるが、二度と手動対応しなくて済む。

## 実施手順

### Step 1: IAM ロールの作成 (Terraform)

EC2 に Route53 の変更権限を持つ IAM ロールを付与した。

```hcl
# iam.tf
resource "aws_iam_role" "ec2" {
  name               = "${var.symbol.prefix}-devel-ec2"
  assume_role_policy = data.aws_iam_policy_document.ec2_assume_role.json
}

data "aws_iam_policy_document" "route53_certbot" {
  statement {
    actions   = ["route53:ListHostedZones", "route53:GetChange"]
    resources = ["*"]
  }
  statement {
    actions   = ["route53:ChangeResourceRecordSets"]
    resources = ["arn:aws:route53:::hostedzone/${var.zone.zone_id}"]
  }
}
```

ポイントは `ChangeResourceRecordSets` を対象ゾーンのみに制限していること。最小権限の原則に従った。

EC2 インスタンスにインスタンスプロファイルを紐付け:

```hcl
resource "aws_instance" "devel" {
  # ...
  iam_instance_profile = aws_iam_instance_profile.ec2.name
}
```

`terraform apply` の結果は 3 to add, 2 to change, 0 to destroy。EC2 はインスタンスプロファイルの付与のみで **再起動不要** (in-place 更新)。

### Step 2: certbot-dns-route53 プラグインのインストール

```bash
sudo apt-get install -y python3-certbot-dns-route53
```

### Step 3: renewal 設定の変更

```bash
sudo sed -i 's/authenticator = manual/authenticator = dns-route53/' \
  /etc/letsencrypt/renewal/dev.example.com-0001.conf
```

変更前:

```ini
authenticator = manual
```

変更後:

```ini
authenticator = dns-route53
```

### Step 4: 証明書の更新

```bash
sudo certbot renew --cert-name dev.example.com-0001
```

certbot が自動的に以下を実行:

1. Route53 に `_acme-challenge.dev.example.com` の TXT レコードを作成
2. Let's Encrypt が DNS を検証
3. 新しい証明書を取得
4. TXT レコードを削除

DNS 伝播の待ち時間を含めて約10分で完了。

### Step 5: nginx リロード

```bash
sudo nginx -t && sudo systemctl reload nginx
```

## 結果

```
Certificate Name: dev.example.com-0001
    Domains: *.dev.example.com
    Expiry Date: 2026-06-15 (VALID: 89 days)
```

HTTPS アクセスも正常に復旧:

```
$ curl -sI https://app.dev.example.com/login
HTTP/1.1 200 OK
```

## 自動更新の仕組み

今後は以下のフローで自動更新される:

```
certbot.timer (systemd, 1日2回)
  → certbot renew
    → certbot-dns-route53 プラグイン
      → EC2 IAM ロール
        → Route53 に TXT レコード作成
          → Let's Encrypt が DNS-01 チャレンジを検証
            → 証明書更新完了
```

期限の30日前から更新が試行されるため、次回は自動的に更新される。

## 学び

### manual authenticator の罠

Let's Encrypt のワイルドカード証明書を初回発行する際、手っ取り早く `--manual` オプションを使いがち。発行自体はうまくいくが、renewal 設定に `authenticator = manual` が書き込まれるため、**自動更新ができなくなる**。

systemd timer が動いていても `manual` モードの証明書はスキップされるので、一見自動更新が設定されているように見えて実は機能していない。

### 対策

AWS 環境であれば、最初から `certbot-dns-route53` プラグインを使うべき。初回発行時に:

```bash
sudo certbot certonly --dns-route53 -d "*.dev.example.com" --key-type ecdsa
```

とすれば、renewal 設定にも `authenticator = dns-route53` が記録され、以後は自動更新が機能する。

### EC2 + Route53 の構成

必要なものは3つだけ:

1. **IAM ロール**: Route53 の変更権限 (対象ゾーンのみ)
2. **インスタンスプロファイル**: EC2 に IAM ロールを紐付け
3. **certbot-dns-route53**: apt でインストール

Terraform で IAM を管理すれば、インフラのコード化も維持できる。
