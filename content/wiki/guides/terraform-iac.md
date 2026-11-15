---
title: "Terraform IaC ベストプラクティス"
description: "大規模 Terraform プロジェクトの設計・運用：モジュール化・ファイル分割・state 管理と、Terraform のコード構造に対応させた AWS 設計指示書（パラメータシート）の書き方、環境分割、運用時の事故防止"
date: 2026-04-06
lastmod: 2026-11-15
aliases: ["Terraform 設計書", "パラメータシート", "設計指示書", "terraform_remote_state", "default_tags", "terraform test"]
related_posts:
  - "/posts/2026/11/terraform-aws-design-spec/"
tags: ["Terraform", "IaC", "DevOps", "aws"]
---

## 概要

`main.tf`（リソース）/ `variables.tf`（入力）/ `outputs.tf`（出力）に分割し、大規模化したら `modules/` 配下でコンポーネント化する。環境ごと（dev / stg / prod）に変数の値を分け、State はリモートに置いてロックで同時実行を防ぐ。設計工程から渡す設計指示書は、**Terraform のコード構造（ディレクトリ・変数・リソース）にそのまま対応づけられる形**で書くと、実装の速さとミスの量が大きく変わる。

## 詳細

### 設計指示書の 5 要素と対応先

| 要素 | Terraform 側の対応先 | 書くこと |
| --- | --- | --- |
| ① 全体像と State 分割方針 | ディレクトリ・backend | 構成図、変更頻度による分割（`01_network` / `02_database` / `03_app`）、別 State の参照方法と公開する `output` |
| ② リソース一覧と命名規則 | `locals`・provider の `default_tags` | 論理名（`aws_vpc.main`）と物理名（`${var.project}-${var.env}-vpc`）、共通タグのキーと値 |
| ③ パラメータシート | `variables.tf`・`.tfvars`・`validation` | 列を「リソース種別・変数名・型・環境ごとの値・制約」にする |
| ④ 機密情報と手動作業の境界 | `data` ソース・Bootstrap 手順 | シークレットの渡し方、State バケット作成などの手動手順 |
| ⑤ 環境の分割方針 | 環境ごとのルートと backend | アカウント・State の置き場・apply の権限 |

### State の参照と機密値

- `terraform_remote_state` は参照先の outputs しか読まないが、読む側には **State ファイル全体の読み取り権限**が要る。State には機密値も平文で入るので、別チーム・別リポジトリには ID やエンドポイントだけを SSM Parameter Store に公開し、パス単位の IAM で `data "aws_ssm_parameter"` から読ませる
- 機密値の受け渡しに SSM の `SecureString` を使わない。data ソースで読めば復号値が読む側の State に残る
- シークレットは Secrets Manager に置き、Terraform では `data "aws_secretsmanager_secret"` で **ARN だけ**を参照する。値を読む data ソースを使うと tfstate に平文で残る
- ある環境に無い値はパラメータ自体を作らない。読む側がエラーになることで「その環境には無い」と気付ける

### パラメータシートの書き方

- 環境ごとに違う値だけを変数に切り出し、共通の固定値はリソースブロックか `locals` に直接書く
- 画面の項目名（「削除保護の有効化」）ではなく Terraform Registry の引数名（`deletion_protection`）で書く
- デフォルト値のままの項目は書かない
- 「備考・制約」は `validation` に、組み合わせで決まる制約は `terraform test`（`.tftest.hcl` + `mock_provider` で AWS 非接続の plan を検証、`expect_failures`）に落とすと、設計書の制約がそのまま受入テストになる
- 設計書は `docs/` に Markdown で置き、コードと同じ Pull Request で更新する

### 環境の分け方

| 方式 | 特徴 |
| --- | --- |
| 環境ごとのディレクトリ（`envs/prod/01_network/`） | backend と assume する IAM ロールがファイルに書かれ、どこに apply するかが一目で分かる |
| 共通コード + 環境ごとの設定ファイル | `-backend-config=envs/prod.s3.tfbackend` と `-var-file=envs/prod.tfvars` を毎回正しく指定する運用ルールが要る |
| CLI workspace | 全 workspace が backend とコードを共有する。認証情報やアクセス制御を分けたい本番隔離には向かない |

- アカウントを分けるなら「ルートディレクトリ → アカウント → backend」の対応表を必ず作る。別アカウント用のリソースを違うルートに書くとエラーなしで別アカウントに作られる
- CI・コンテナレジストリ・DNS など環境をまたぐリソースは専用のルートに分ける
- State バケットのバージョニングを明示的に有効にする。S3 だけでロックする `use_lockfile` は Terraform 1.11 以降で正式機能
- ルートごとに `.terraform.lock.hcl` をコミットし、Terraform と provider のバージョンを固定する
- `backend` ブロックは変数を使えないが、`terraform_remote_state` の `config` には変数を書けるので参照先を環境に追従させる

### 運用で事故を防ぐ指示

- **誰が値を持つか**：Auto Scaling や夜間停止が変える属性（ECS の `desired_count` など）は `lifecycle { ignore_changes }` に入れる
- **共有モジュールの変更は全ルートで plan**：`-target` 運用が続いたルートには他人の変更が取り残される。`-target` も依存先を plan に含めるので「絞ったから安全」ではない
- **plan の期待値を先に書く**：`3 to add, 0 to change, 0 to destroy` のように書いておき、一致したときだけ apply する
- **replace は下流を棚卸し**：RDS の Blue/Green 切り替えで binlog 位置を覚えた DMS の CDC が再開できなくなる例がある（[RDS Blue/Green 移行](/blogs/wiki/guides/rds-blue-green-migration/)）

### AI に実装させる場合

- パラメータシートを YAML / JSON の構造化データで書くと、設計書をそのままプロンプトに渡せる。人が読む表と AI が読む定義は、どちらか一方を正本にする
- `CLAUDE.md` / `AGENTS.md` に「`validate` と `plan` は自由、`apply` と State を書き換える操作（`state mv`・`import`・backend 移行）は人間の承認なしに実行しない」と書く

### 構成図ツール

| ツール | 向いているケース |
| --- | --- |
| draw.io（`.drawio.svg` で保存） | 迷ったらこれ。GitHub でプレビューでき再編集もできる。ネットワーク境界を正確に描ける |
| Mermaid | State 間の参照関係やデータフローなどテキスト差分で管理したい図。入れ子の深い配置図は崩れやすい |
| Diagrams（Python） | 公式アイコン付きの配置図をコードで管理。Graphviz が要る |
| Eraser / Lucidchart | デザイン性・同時編集重視の SaaS。構成情報を外部に上げてよいかの確認が要る |
| Inframap / Rover / `terraform graph` | 実装後にコードや State から逆生成して設計図と突き合わせる |

## 関連ページ

- [RDS Blue/Green 移行](/blogs/wiki/guides/rds-blue-green-migration/) — replace が下流を壊す実例
- [NAT Gateway](/blogs/wiki/tools/nat-gateway/) — VPC 設計で出てくる構成要素
- [AI エージェント時代のシークレット管理](/blogs/wiki/guides/ai-agent-secret-management/) — 機密値の置き場所

## ソース記事

- [Terraform 向け AWS 設計書の書き方 — パラメータシートを variables.tf に対応させる5要素と構成図ツール比較](/blogs/posts/2026/11/terraform-aws-design-spec/) — 2026-11-14
