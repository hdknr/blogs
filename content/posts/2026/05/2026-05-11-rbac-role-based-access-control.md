---
title: "RBAC 入門 — ロールベースアクセス制御の仕組み・ABAC との違い・実装例（AWS / Kubernetes）"
date: 2026-05-11
lastmod: 2026-05-11
draft: false
source_url: "https://github.com/hdknr/blogs/issues/93#issuecomment-4417016793"
categories: ["セキュリティ"]
tags: ["RBAC", "アクセス制御", "Kubernetes", "AWS IAM", "ABAC"]
---

**RBAC（Role-Based Access Control：ロールベースアクセス制御）とは、ユーザーに直接権限を与えず、ロールを介して権限を管理する仕組みです。** AWS の IAM、Kubernetes、GitHub、Microsoft 365 など、現代のほとんどのプラットフォームがこの考え方を基盤にしています。

一言で言うと、「社員一人ひとりに鍵を渡すのではなく、役職ごとのマスターキーを管理する」仕組みです。本記事では RBAC の基本構造、必要性、ABAC との違い、AWS IAM・Kubernetes での実装例までをまとめます。

## RBAC の基本構造

RBAC は主に 3 つの要素の組み合わせで成り立っています。

- **ユーザー (User)** — システムを利用する個人
- **ロール (Role)** — 「管理者」「編集者」「閲覧者」といった役割。権限の集合体
- **パーミッション (Permission)** — 「ファイルの読み取り」「データの削除」といった具体的な操作権限

ユーザーは直接パーミッションを持つのではなく、ロールを介して権限を獲得します。この「間接化」が RBAC の本質です。

![ユーザーがロールに割り当てられ、ロールがパーミッションを付与する RBAC の3階層モデル](/blogs/images/rbac-structure.png)

## なぜ RBAC が必要なのか

従来の ACL ベースの管理（ユーザーごとにリソースの権限を個別に設定する方式）では、組織が大きくなるにつれて管理が破綻します。RBAC を導入することで、以下のメリットが得られます。

### 1. 管理の効率化

異動や入社があった際、個別に何十もの設定を変更する必要がなく、適切な「ロール」を割り当てるだけで済みます。退職時もロールを外せば一括で権限が剥奪されます。

### 2. セキュリティの向上（最小権限の原則）

業務に必要な権限だけをセットにしたロールを作成することで、過剰な権限付与によるリスクを防げます。最小権限の原則（Principle of Least Privilege）を組織的に実現する手段として最も普及しているのが RBAC です。

### 3. コンプライアンスの強化

「誰がどのような権限を持っているのか」をロール単位で把握できるため、監査が容易になります。SOC 2、ISO 27001、PCI DSS などのコンプライアンス監査では、アクセス権限のレビューが必須項目になっており、RBAC ベースの設計だとレポート作成が圧倒的に楽になります。

## 具体例：ドキュメント管理システム

| ユーザー | 割り当てられたロール | 実行できる操作 (パーミッション) |
| --- | --- | --- |
| **佐藤さん** | **管理者 (Admin)** | 作成、編集、削除、ユーザー追加 |
| **鈴木さん** | **編集者 (Editor)** | 作成、編集 |
| **高橋さん** | **閲覧者 (Viewer)** | 閲覧のみ |

もし鈴木さんが管理者に昇進した場合、鈴木さんの設定を一つずつ変えるのではなく、付与するロールを「編集者」から「管理者」へ切り替えるだけで、すべての権限が更新されます。

## 実装例：Kubernetes と AWS IAM

### Kubernetes RBAC

Kubernetes は RBAC を標準サポートしており、`Role`/`ClusterRole` と `RoleBinding`/`ClusterRoleBinding` でアクセス制御を行います。

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  namespace: default
  name: pod-reader
rules:
  - apiGroups: [""]
    resources: ["pods"]
    verbs: ["get", "watch", "list"]
---
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: read-pods
  namespace: default
subjects:
  - kind: User
    name: alice
    apiGroup: rbac.authorization.k8s.io
roleRef:
  kind: Role
  name: pod-reader
  apiGroup: rbac.authorization.k8s.io
```

「`default` 名前空間の Pod を読み取る権限」をロールとして定義し、それをユーザー `alice` に紐付けています。

### AWS IAM ロール

AWS の IAM ロールも RBAC の典型例です。EC2 インスタンスに「S3 の読み取り専用ロール」を割り当てれば、そのインスタンスから動くアプリケーションは S3 の読み取りは可能だが書き込みは不可、という制御が実現できます。アプリケーションのコードに認証情報を埋め込む必要がなくなる点も大きな利点です。

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": ["s3:GetObject", "s3:ListBucket"],
      "Resource": ["arn:aws:s3:::my-bucket", "arn:aws:s3:::my-bucket/*"]
    }
  ]
}
```

このポリシーをロールにアタッチし、ロールを EC2/Lambda/コンテナタスクなどに割り当てます。

## RBAC と ABAC の違い

RBAC とよく比較されるものに **ABAC (Attribute-Based Access Control)** があります。

- **RBAC**: 「役職」で判断（例: マネージャーなら OK）
- **ABAC**: 「属性（場所、時間、デバイス、リソースのタグなど）」で判断（例: マネージャーで、かつ社内 Wi-Fi からのアクセスなら OK）

ABAC はより細かい制御ができる反面、ポリシー設計が複雑になります。一方 RBAC はシンプルで導入しやすく、運用も理解しやすいのが特長です。

実務では「RBAC をベースに、必要な箇所だけ ABAC で属性ベースの条件を加える」ハイブリッドな設計が一般的です。AWS IAM も基本は RBAC ですが、`Condition` 句で IP アドレスや MFA 有無などの属性を加味できるため、実質的に ABAC の要素を取り込んでいます。

## ロール設計のアンチパターン

RBAC を導入しても、設計を誤ると逆に管理コストが増えることがあります。代表的なアンチパターン:

- **ロール爆発（Role Explosion）**: 業務ごとに細かくロールを切りすぎて、結局ユーザー数に近いロール数になってしまう
- **すべてを管理者ロール**: 面倒だからと全員に Admin を付与し、最小権限の原則が崩壊する
- **役割ではなく個人名のロール**: 「田中ロール」のような個人前提のロールを作ると、異動・退職で破綻する

ロールは「業務上の役割」を単位として設計し、ユーザー数より大幅に少ない数に収めるのが基本です。

## まとめ

- RBAC は「ユーザー → ロール → パーミッション」の 3 階層で権限を管理する設計パターン
- 管理効率、セキュリティ、コンプライアンスの 3 つで大きな利点がある
- AWS、Azure、Google Cloud、Kubernetes、GitHub など主要プラットフォームの基盤として採用されている
- 細かい条件が必要な場合は ABAC を組み合わせるハイブリッド設計が現実解
- ロール設計のアンチパターン（ロール爆発、個人名ロール）に注意

シンプルで理解しやすく、それでいて組織のセキュリティ統制を大きく前進させられる点が、RBAC が長年デファクトであり続ける理由です。
