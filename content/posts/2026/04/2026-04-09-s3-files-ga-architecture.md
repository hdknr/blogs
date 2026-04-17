---
title: "Amazon S3 Files GA：消えるアーキテクチャ層と生まれるアーキテクチャ"
date: 2026-04-09
lastmod: 2026-04-17
draft: false
source_url: "https://github.com/hdknr/blogs/issues/1#issuecomment-4217192632"
categories: ["クラウド/インフラ"]
tags: ["AWS", "S3", "アーキテクチャ", "クラウド", "NFS", "Django", "Terraform"]
---

2026年4月7日、AWSがAmazon S3 Filesを一般提供（GA）しました。S3バケットをNFS v4.1/v4.2のファイルシステムとしてマウントできる機能で、EC2・EKS・ECS・Lambdaのいずれからでも利用できます。

本記事は、ikenyal氏のZenn記事「[S3 Filesで消えるアーキテクチャ層、生まれるアーキテクチャ](https://zenn.dev/genda_jp/articles/b6ff5ea33c7a71)」を参照しながら、S3 Filesが既存のアーキテクチャにどう影響するかを整理します。「何が設定できるか」ではなく「**何が不要になり、何が可能になるか**」にフォーカスします。

## S3 Filesが解こうとしている問題

たとえば、MLチームが学習データの前処理をする場面を考えましょう。元データはS3に置いてあり、pandasで読み込んで加工したい場面です。

`pd.read_csv("s3://my-bucket/data.csv")` と書けますが、内部ではboto3がGETリクエストを発行してメモリに読み込んでいます。手元の `open("./data.csv")` とは根本的に異なるI/Oモデルです。

規模が大きくなると、これは「パイプラインのアーキテクチャ課題」になります。

```
S3からEFS/EBSにコピー → 処理 → 結果をS3に書き戻す
```

この「中間のコピー層」は本来やりたい処理ではなく、ストレージのI/Oモデルの違いを埋めるためだけに存在しています。

S3 Filesはこのギャップそのものを解消します。アプリケーションからS3のデータはローカルのディレクトリに見えます。

```python
# S3 Filesを使うと
pd.read_csv("/mnt/s3files/data.csv")   # S3のオブジェクトが読まれる
df.to_csv("/mnt/s3files/result.csv")   # 変更が自動的にS3にコミットされる
```

## FUSEベースのツールとの違い

「S3をマウントできる」と聞いて、Mountpoint for Amazon S3やgcsfuseを思い浮かべる方も多いでしょう。S3 Filesは内部構造がまったく異なります。

**FUSEベースのツール**は、S3 APIの上にファイルシステムの振る舞いを「エミュレーション」するアプローチです。ファイルの一部だけを書き換えるような操作がサポートされず、空ディレクトリの扱いに不整合が出ることもあります。

**S3 Files**はエミュレーションではなく、EFS（Elastic File System）という本物のNFSファイルシステムをS3に接続しています。二つの異なるシステムが共存し、その間に明示的な同期レイヤーがある構造です。

### 「stage and commit」モデル

ファイルシステム上での変更は即座にS3に反映されるのではなく、**約60秒ごとにまとめてS3へPUT**されます（「commit」）。逆に、S3側でオブジェクトが更新された場合は通常数十秒以内にファイルシステム側に反映されます。

これは明確なトレードオフです。「リアルタイムに同期される共有ファイルシステム」ではなく、「数十秒の遅延を許容する代わりに、ファイルとオブジェクトの両方のセマンティクスを壊さない」設計です。

## 消えるアーキテクチャ層

### 1. S3 → EFS/EBSのステージングパイプライン

100GBの学習データを処理する場合、従来の手順は：

1. S3からEBSにダウンロード（数分かかる）
2. データを処理する
3. 結果をS3にアップロード
4. EBSボリュームをクリーンアップ

やりたい処理は2番だけです。S3 Filesでは、S3プレフィックスをマウントするだけで処理スクリプトはそのまま `/mnt/s3files/` のファイルを読み書きします。ダウンロード・アップロード・クリーンアップのステップが消えます。

### 2. Lambdaの「/tmp にダウンロードしてから処理」パターン

画像サムネイル生成のLambda関数を例にすると、従来の実装はこうです：

```python
# 従来: S3からダウンロード → 処理 → アップロード
def handler(event, context):
    key = event['Records'][0]['s3']['object']['key']
    bucket = event['Records'][0]['s3']['bucket']['name']

    s3 = boto3.client('s3')
    download_path = f'/tmp/{key.split("/")[-1]}'
    s3.download_file(bucket, key, download_path)   # /tmp にダウンロード

    img = Image.open(download_path)
    img.thumbnail((128, 128))
    thumb_path = f'/tmp/thumb_{key.split("/")[-1]}'
    img.save(thumb_path)

    s3.upload_file(thumb_path, bucket, f'thumbnails/{key}')  # S3にアップロード
```

S3 Filesを使うと：

```python
# S3 Files: マウントされたパスで直接操作
from PIL import Image

def handler(event, context):
    key = event['Records'][0]['s3']['object']['key']

    img = Image.open(f'/mnt/s3files/{key}')
    img.thumbnail((128, 128))
    img.save(f'/mnt/s3files/thumbnails/{key}')
```

boto3のインポートすら不要になります。より重要なのは、Lambda関数が **`/tmp` の容量制約（デフォルト512MB、最大10GB）から解放される**ことです。大きな機械学習モデルを参照する関数でも、コールドスタート時のダウンロード待機が不要になります。

### 3. EFS＋S3同期の自前運用

「データレイクはS3だが、リアルタイム処理にはEFSが必要」という理由でS3とEFSの両方を使い、DataSyncやcronで同期スクリプトを走らせている構成があります。

この構成の苦しさは同期ロジックの維持にあります。新しいオブジェクトの検出、差分の特定、同期失敗時のリトライ、データ一貫性の保証など、すべてを自前で管理する必要があります。

S3 Filesでは、この同期レイヤーがマネージドに置き換わります：
- S3からファイルシステムへの反映（import）：最大2,400オブジェクト/秒
- ファイルシステムからS3へのコミット（export）：約60秒のバッチウィンドウ
- eviction期間：1日〜365日（デフォルト30日）

### 4. レガシーアプリのためのアダプタ層

`open()` / `read()` / `write()` を前提にしたアプリケーション（ログ集約ツール、ビルドシステムなど）は、S3 SDKへの書き換えが現実的でないことが多いです。

S3 Filesでは、S3をプライマリストレージとしたままアプリケーションからNFSマウント経由でアクセスできます。POSIXパーミッションやファイルロック（flock）にも対応しているため、コード変更なしにマウントポイントを切り替えるだけで移行できる可能性があります。

## 生まれるアーキテクチャ

### 1. 二層構造による読み込みの自動最適化

S3 Filesの内部は二層構造になっています：

- **high-performance storage層**：頻繁にアクセスされる小さなファイルをキャッシュ。1ミリ秒未満〜1桁ミリ秒のレイテンシ
- **S3層**：1MB以上のリードはS3から直接ストリーミング。しかもファイルシステムのアクセス料金が発生しない（S3のGET料金のみ）

公式ドキュメントに記載された性能仕様：

| 指標 | 値 |
|------|-----|
| 1クライアントあたり最大リードスループット | 3 GiB/s |
| ファイルシステムあたり合計リードスループット | テラバイト/秒級 |
| ファイルシステムあたり最大リードIOPS | 250,000 |
| ファイルシステムあたり合計ライトスループット | 1〜5 GiB/s（リージョンによる） |
| ファイルシステムあたり最大ライトIOPS | 50,000 |

EBSのgp3デフォルトスループット（125MiB/s）と比べると、100GBデータのシーケンシャルリードで約33秒 vs 約13分という差になります。ボリュームのプロビジョニングなしで、使った分だけの課金です。

### 2. Lambdaでの大規模参照データの直接利用

従来、Lambda関数が大きな参照データを使う選択肢は：

1. コンテナイメージにモデルファイルを含める（最大10GB、デプロイのたびに再ビルド）
2. EFSをマウントする（VPC設定が必要、コールドスタートが長くなる傾向）
3. `/tmp` にS3からダウンロードする（最大10GB、コールドスタートにダウンロード時間が加算）

S3 Filesが4番目の選択肢になります。S3にモデルファイルを置いたまま、Lambda関数からファイルシステム経由で直接読み込めます。モデルの更新はS3側へのアップロードだけで完了し、Lambda関数の設定変更が不要です。

「lazy hydration」と呼ばれるプリフェッチ機能により、設定可能なサイズ閾値（デフォルト128KB）以下のファイルはメタデータと一緒にプリフェッチされ、数百万オブジェクトのバケットでもマウント直後から作業を開始できます。

## Django Web アプリでの活用例

S3 Files の最大のメリットは、既存のファイルシステム前提のコードをそのまま使える点だ。Django では `django-storages` + boto3 を使った S3 連携が一般的だが、S3 Files を使えばその依存を丸ごと外せる。

### 従来: django-storages を使う構成

```python
# settings.py（従来）
DEFAULT_FILE_STORAGE = "storages.backends.s3boto3.S3Boto3Storage"
AWS_STORAGE_BUCKET_NAME = "my-app-uploads"
AWS_S3_REGION_NAME = "ap-northeast-1"
MEDIA_URL = "https://my-app-uploads.s3.amazonaws.com/"
```

この構成では、ファイルのアップロード・ダウンロードのたびに boto3 が S3 API を叩く。サムネイル生成やCSVエクスポートなど、ファイルを一時的にローカルで処理する場面では「S3からダウンロード → 処理 → S3にアップロード」の往復が発生する。

### S3 Files を使う構成

EC2 や ECS 上で S3 バケットを `/mnt/s3files` にマウントしている前提:

```python
# settings.py（S3 Files）
MEDIA_ROOT = "/mnt/s3files/media/"
MEDIA_URL = "/media/"
```

これだけで Django の `FileField` / `ImageField` は S3 上のオブジェクトを直接読み書きする。`django-storages` は不要だ。

### モデルの例

```python
# models.py — コード変更なし
from django.db import models

class Report(models.Model):
    title = models.CharField(max_length=200)
    attachment = models.FileField(upload_to="reports/%Y/%m/")
    created_at = models.DateTimeField(auto_now_add=True)
```

`attachment` フィールドにアップロードされたファイルは `/mnt/s3files/media/reports/2026/04/` に保存され、約 60 秒後に S3 バケットへ自動コミットされる。

### ファイル処理もシンプルに

```python
# views.py — CSV エクスポートの例
import csv
from django.http import FileResponse

def export_csv(request):
    path = "/mnt/s3files/media/exports/report.csv"
    with open(path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["ID", "Title", "Date"])
        for r in Report.objects.all():
            writer.writerow([r.id, r.title, r.created_at])
    return FileResponse(open(path, "rb"), as_attachment=True)
```

boto3 のインポートも一時ファイルへのコピーも不要。通常のファイル操作だけで S3 上にデータが永続化される。

### 注意点

- **約 60 秒のコミット遅延**: アップロード直後に S3 API 経由（CloudFront 等）でファイルを配信する場合、反映までのラグを考慮する必要がある
- **静的ファイル配信**: `MEDIA_URL` を CloudFront 経由にする場合は、S3 側のオブジェクトパスとの整合性を確認する
- **マルチサーバー構成**: 複数の EC2 インスタンスから同じ S3 Files マウントに書き込む場合、NFS のファイルロック（flock）が利用できる

## セットアップ: 既存バケットの有効化

S3 Files は**既存の汎用バケット（general purpose bucket）をそのまま使える**。新しいバケットを作り直す必要はない。既存のオブジェクトはマウント後にファイルとして見える。

### AWS CLI での手順

```bash
# 1. ファイルシステムを作成（既存バケットを指定）
aws s3files create-file-system --bucket-name my-existing-bucket

# 2. マウントターゲットを作成（VPC のサブネットを指定）
aws s3files create-mount-target \
  --file-system-id fs-0123456789abcdef0 \
  --subnet-id subnet-abcdef01 \
  --security-groups sg-12345678

# 3. EC2 からマウント
sudo mount -t s3files fs-0123456789abcdef0:/ /mnt/s3files
```

### Terraform での構成

Terraform AWS Provider **v6.40.0**（2026年4月リリース）で S3 Files の正式サポートが追加された。以下の 5 リソースが利用できる。

| リソース | 役割 |
|----------|------|
| `aws_s3files_file_system` | ファイルシステムの作成・管理 |
| `aws_s3files_mount_target` | VPC 内のマウントターゲット |
| `aws_s3files_access_point` | アクセスポイント |
| `aws_s3files_synchronization_configuration` | S3 との同期設定 |
| `aws_s3files_file_system_policy` | ファイルシステムポリシー |

```hcl
terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = ">= 6.40.0"
    }
  }
}

# 既存バケットに S3 Files を有効化
resource "aws_s3files_file_system" "main" {
  bucket_name = "my-existing-bucket"
}

# マウントターゲット（AZ ごとに作成）
resource "aws_s3files_mount_target" "az1" {
  file_system_id = aws_s3files_file_system.main.id
  subnet_id      = aws_subnet.private_a.id
  security_groups = [aws_security_group.s3files.id]
}

resource "aws_s3files_mount_target" "az2" {
  file_system_id = aws_s3files_file_system.main.id
  subnet_id      = aws_subnet.private_c.id
  security_groups = [aws_security_group.s3files.id]
}

# NFS 用のセキュリティグループ
resource "aws_security_group" "s3files" {
  name_prefix = "s3files-"
  vpc_id      = aws_vpc.main.id

  ingress {
    from_port   = 2049
    to_port     = 2049
    protocol    = "tcp"
    cidr_blocks = [aws_vpc.main.cidr_block]
  }
}

# 同期設定（オプション）
resource "aws_s3files_synchronization_configuration" "main" {
  file_system_id = aws_s3files_file_system.main.id
  # eviction 期間やコミット間隔の調整が可能
}
```

EC2 インスタンスの user_data でマウントを自動化する例:

```hcl
resource "aws_instance" "app" {
  ami           = "ami-xxxxxxxxx"
  instance_type = "m7i.large"
  subnet_id     = aws_subnet.private_a.id

  user_data = <<-EOF
    #!/bin/bash
    mkdir -p /mnt/s3files
    mount -t s3files ${aws_s3files_file_system.main.id}:/ /mnt/s3files
    echo "${aws_s3files_file_system.main.id}:/ /mnt/s3files s3files defaults,_netdev 0 0" >> /etc/fstab
  EOF
}
```

## リージョン対応

S3 Files は GA と同時に**すべての商用 AWS リージョン**で利用可能になっている。東京リージョン（ap-northeast-1）を含む日本国内からの利用にも対応済みだ。リージョン固有の制約としては、ライトスループットが 1〜5 GiB/s とリージョンによって異なる点がある。

## まとめ

S3 FilesのGAは、「S3はオブジェクトストレージ、ファイルシステムはEFS」という二分法を変えるものです。

**消えるもの**: S3↔EFS間の自前同期レイヤー、Lambdaの`/tmp`ダウンロードパターン、レガシーアプリ向けのアダプタ層

**生まれるもの**: ボリューム設計不要の高スループットストレージ、Lambdaでの大規模参照データへの直接アクセス

約60秒のコミット遅延というトレードオフは理解したうえで、既存のアーキテクチャのどの部分をS3 Filesで置き換えられるかを検討する価値があります。

## 参考リンク

- [Launching S3 Files: Making S3 buckets accessible as file systems - AWS Blog](https://aws.amazon.com/blogs/aws/launching-s3-files-making-s3-buckets-accessible-as-file-systems/)
- [Amazon S3 Files User Guide](https://docs.aws.amazon.com/AmazonS3/latest/userguide/s3-files.html)
- [S3 Filesで消えるアーキテクチャ層、生まれるアーキテクチャ - Zenn（ikenyal）](https://zenn.dev/genda_jp/articles/b6ff5ea33c7a71)
- [S3 Files and the changing face of S3 - All Things Distributed](https://www.allthingsdistributed.com/2026/04/s3-files-and-the-changing-face-of-s3.html)
