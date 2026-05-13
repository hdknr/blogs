---
title: "CAMPFIRE 個人情報漏洩から学ぶ — GitHub アカウント侵害が招く CI/CD セキュリティリスク"
date: 2026-04-25
lastmod: 2026-04-25
draft: false
source_url: "https://github.com/hdknr/blogs/issues/1#issuecomment-4317754599"
categories: ["セキュリティ"]
tags: ["セキュリティ", "GitHub Actions", "GitHub Secrets", "Terraform", "OIDC"]
---

クラウドファンディングプラットフォーム CAMPFIRE が、GitHub アカウントへの不正アクセスを起点に最大 22 万 5,846 件の個人情報が漏洩した可能性があると発表しました（2026 年 4 月 24 日）。単なる「パスワード流出」ではなく、**CD パイプラインを悪用してインフラを乗っ取るという、現代の DevOps が抱えるリスクを象徴するインシデント**です。本記事ではエンジニア視点で攻撃経路を分析し、再発防止策を考えます。

## インシデントの経緯

| 日時 | 出来事 |
|------|--------|
| 2026-04-02 22:50 | GitHub アカウントへの不正アクセスを検知。一部ソースコードが閲覧された可能性（初報） |
| 2026-04-14 | 第二報：社員・取引先情報の閲覧可能状態を確認 |
| 2026-04-22 | 第三報：顧客情報管理システムへの不正アクセス痕跡を確認 |
| 2026-04-24 | 個人情報漏洩の可能性を正式発表（最大 22 万 5,846 件） |

漏洩した可能性がある情報は以下のとおりです:

- **プロジェクト実行者** 12 万 929 件：氏名・住所・電話番号・口座情報など（2021 年 2 月以降）
- **支援者** 13 万 155 件：氏名・住所・口座情報など（PayPal 決済、後払い、口座送金返金ユーザー）
- うち **8 万 2,465 件**が口座情報を含む
- クレジットカード情報は対象外（CAMPFIRE 公式発表）

## 推定される攻撃経路

エンジニア向け技術解説として、@poly_soft（勝又健太）氏が X（旧 Twitter）で以下の攻撃チェーンを推察しています。この分析は公式発表を補完する形で、攻撃者が具体的にどう動いたかを示しています（以下はあくまで推定です）。

### Step 1: CD 権限を持つ GitHub アカウントの侵害（推定）

攻撃者が最初に侵害したのは、**単独で CD（継続的デプロイ）をトリガーできる権限を持つ GitHub アカウント**であったと推定されます。

問題の設定として考えられるのは:

- ブランチ保護ルールが未設定
- 複数ユーザーの approve なしでも、トリガーブランチへ PR をマージできる設定

GitHub のユーザー権限が、実質的にインフラの管理者権限と同等になっていた状態です。

### Step 2: DB スキーマ情報の取得（推定）

ソースコードにアクセスした段階で、**マイグレーションファイルから DB のスキーマ情報**を容易に把握できたと推定されます。テーブル構造・カラム名・リレーションが丸わかりになるため、後のデータ抽出計画を立てやすくなります。

### Step 3: GitHub Secrets から認証情報を取得（推定）

CI/CD ワークフローのコードを読むことで、`secrets.DB_USER` や `secrets.DB_PASSWORD` がどのように参照されているかが判明します。Secrets の値自体はワークフロー実行時に環境変数として注入されるため、**IaC（Terraform 等）のコードにその注入設定を追記することで値を横取り**できたと推定されます。

### Step 4: IaC コードを改ざんして EC2 インスタンスを不正起動（推定）

攻撃者は Terraform などの IaC コードに変更を加えたと推定されます:

```hcl
# 攻撃者が追加したと推定されるリソース（イメージ）
resource "aws_instance" "attacker_pivot" {
  ami           = "ami-xxxxxxxx"
  instance_type = "t3.micro"
  subnet_id     = aws_subnet.public.id  # パブリックサブネットに配置

  vpc_security_group_ids = [aws_security_group.attacker_access.id]

  environment = {
    DB_USER     = var.db_user      # secrets.DB_USER が流し込まれる
    DB_PASSWORD = var.db_password  # secrets.DB_PASSWORD が流し込まれる
    DB_HOST     = var.db_host
  }
}

resource "aws_security_group" "attacker_access" {
  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]  # 外部から SSH アクセス可能
  }
}
```

### Step 5: CD を実行して EC2 を起動・外部からアクセス（推定）

改ざんした IaC コードで CD を実行し、EC2 インスタンスが起動して外部からアクセスできる状態になったと推定されます。

### Step 6: EC2 を踏み台に DB へアクセスしてデータ抽出（推定）

起動した EC2 には DB の接続情報が環境変数として渡されているため、そこから直接 DB に接続してデータを抽出・外部送信することが可能であったと推定されます。

![攻撃者がGitHubアカウントを侵害し、IaCコード改ざんとCD実行でEC2インスタンスを踏み台にDBデータを抽出するまでの全攻撃チェーン図](/blogs/images/campfire-attack-chain.png)

## 今回の教訓

今回のインシデントが示す本質的な問題は、「**GitHub のユーザー権限が実質的にインフラの管理者権限になっていた**」点です。

クラウドインフラの IaC 化・CD 自動化が進む現代では、GitHub アカウントの侵害が直接インフラ侵害につながるリスクがあります。以下の 3 点を今すぐ確認することをお勧めします:

1. **CD を単独トリガーできるアカウントはないか** → ブランチ保護・CODEOWNERS を設定
2. **GitHub Secrets に長期的な DB/AWS 認証情報を置いていないか** → OIDC + IAM Role に移行
3. **IaC の変更が無審査でデプロイされる設定になっていないか** → 変更レビューフローを必須化

GitHub を使う組織が増えた今、アカウントセキュリティ（MFA 必須化、不要な権限の削除）と CI/CD パイプラインのセキュリティを一体で考えることが不可欠です。

## 問題のある設定と推奨される対策

### 1. GitHub ブランチ保護と CODEOWNERS

| 現状（推定） | 対策 |
|-------------|------|
| ブランチ保護なし / 単独マージ可能 | `main` / `production` ブランチへのマージに **複数 reviewer の approve** を必須化 |
| CD トリガーブランチへの直接プッシュ可能 | `CODEOWNERS` で IaC・Secrets 関連ファイルの変更に特定チームの承認を要求 |

```yaml
# .github/CODEOWNERS の例
/terraform/         @security-team @infra-team
/.github/workflows/ @security-team
```

### 2. GitHub Actions の権限を最小化

```yaml
# .github/workflows/deploy.yml
permissions:
  contents: read   # write は不要なら read のみ
  id-token: write  # OIDC トークン取得に必要な場合のみ
```

Secrets に直接 DB 認証情報を置くのではなく、**AWS IAM Role を OIDC で一時取得**する方式が推奨です。

### 3. Secrets に DB 認証情報を置かない

```yaml
# NG: Secrets に長期認証情報を保存
env:
  DB_PASSWORD: ${{ secrets.DB_PASSWORD }}

# OK: AWS Secrets Manager + OIDC で一時取得
- uses: aws-actions/configure-aws-credentials@v4
  with:
    role-to-assume: arn:aws:iam::123456789:role/github-actions-role
    aws-region: ap-northeast-1
- name: Get DB credentials
  run: |
    aws secretsmanager get-secret-value \
      --secret-id prod/db/credentials \
      --query SecretString --output text
```

### 4. CD 実行ログの監視・異常検知

CloudTrail と EventBridge を組み合わせ、通常とは異なる時間帯・変更内容の CD 実行に対して Slack アラートを設定します。Terraform apply の実行ログを集中管理し、IaC の変更内容を自動レビューに組み込む仕組みが有効です。

### 5. インフラのネットワーク設計

- **踏み台サーバーはパブリックサブネットに置かない**（SSM Session Manager を使用）
- DB はプライベートサブネットに配置し、セキュリティグループで接続元を限定

## まとめ

CAMPFIRE のインシデントは、GitHub アカウント 1 つの侵害が DB への不正アクセスにつながるという、現代の DevOps インフラが持つリスクを実証しました。22 万件超の個人情報漏洩という深刻な被害を教訓に、自社の CI/CD パイプラインのセキュリティを見直すきっかけにしてください。

---

- 出典: [【重要】弊社システムへの不正アクセスによる個人情報漏えいの可能性に関するお詫びとご報告（CAMPFIRE 公式）](https://campfire.co.jp/press/2026/04/24/campfire/)
- 攻撃経路分析: [@poly_soft (勝又健太) の X ポスト](https://x.com/poly_soft/status/2047676004211265657)
