---
title: "Agent Plugins for AWS: Claude Code から AWS アーキテクチャ設計・デプロイまで一気通貫"
date: 2026-03-25
lastmod: 2026-03-25
draft: false
source_url: "https://github.com/hdknr/blogs/issues/1#issuecomment-4126127772"
categories: ["クラウド/インフラ"]
tags: ["aws", "claude-code", "agent", "mcp"]
---

AWS が「**Agent Plugins for AWS**」を公開しました。AI コーディングエージェント（Claude Code や Cursor など）に、AWS のアーキテクチャ設計からデプロイ実行までの能力を組み込むオープンソースのプラグインライブラリです。

## Agent Plugins for AWS とは

[Agent Plugins for AWS](https://github.com/awslabs/agent-plugins) は、AWS Labs が開発・公開したオープンソースプロジェクトです。コスト見積もり、Infrastructure as Code（IaC）の生成、デプロイといった AWS 固有のスキルセットを AI エージェントに追加できます。

プラグインは以下の要素で構成されています:

- **Agent Skills**: 複雑なタスクをステップバイステップで実行するワークフロー。デプロイやアーキテクチャ設計のベストプラクティスを手順として組み込んだもの
- **MCP サーバー**: 外部サービス、ドキュメント、料金データなどへのリアルタイム接続
- **Hooks**: 開発者のアクションに対するバリデーションやガードレール

## deploy-on-aws プラグイン

現時点で提供されている主要プラグインが **deploy-on-aws** です。「deploy to AWS」と指示するだけで、以下の 5 ステップを自動実行します:

1. **コードベースの分析**: アプリケーションの構成・依存関係を解析
2. **AWS サービスの推奨**: 最適な AWS サービスを理由付きで提案
3. **コスト見積もり**: 推奨構成の月額コストを試算
4. **IaC の生成**: CDK または CloudFormation でインフラコードを生成
5. **デプロイ実行**: ユーザーの確認後にデプロイ

AWS によると、従来は数時間かかっていたデプロイフローが約 10 分で完了するとのことです。

## Claude Code へのインストール

Claude Code では、プラグインマーケットプレイス経由でインストールします:

```bash
# マーケットプレイスを追加
/plugin marketplace add awslabs/agent-plugins

# deploy-on-aws プラグインをインストール
/plugin install deploy-on-aws@awslabs-agent-plugins
```

インストール後は、Claude Code のプロンプトで「AWS にデプロイして」と指示するだけで、プラグインが自動的に起動します。

## Terraform ユーザーへの注意

現時点の deploy-on-aws プラグインが生成する IaC は **CDK または CloudFormation** のみで、**Terraform はサポートされていません**。既に Terraform でインフラを管理しているプロジェクトでは注意が必要です。

- **デプロイ機能**: CloudFormation/CDK と Terraform が混在するため、そのままでは導入しにくい
- **アーキテクチャ設計・コスト見積もり**: IaC 生成前のステップ（コードベース分析、サービス推奨、コスト試算）は Terraform プロジェクトでも参考になる
- **MCP サーバー**: ドキュメントや料金データへのアクセスは IaC ツールに依存しないため活用可能

Agent Plugins はオープンソースでプラグインを追加できる設計のため、今後 Terraform 対応のプラグインが登場する可能性はあります。

### Terraform ユーザー向けの代替手段: Terraform MCP Server

Agent Plugins とは別に、Terraform プロジェクト向けの MCP サーバーが存在します。AWS Labs が公開していた [terraform-mcp-server](https://github.com/awslabs/mcp) は現在非推奨（deprecated）となり、HashiCorp 公式の **[Terraform MCP Server](https://developer.hashicorp.com/terraform/mcp-server/deploy)** への移行が推奨されています。

HashiCorp 公式版では以下の機能が提供されています:

- **Terraform Registry の検索**: プロバイダーやモジュールのドキュメント参照
- **HCP Terraform ワークスペース管理**: ワークスペースの操作や状態確認
- **エンタープライズ対応**: 組織規模での運用に必要な機能

Terraform でインフラを管理しているプロジェクトでは、Agent Plugins の代わりに **Claude Code + HashiCorp Terraform MCP Server** の組み合わせが実用的です。

## セキュリティ上の注意点

AWS は以下のベストプラクティスを推奨しています:

- **生成コードのレビュー**: デプロイ前に、セキュリティ・コスト・耐障害性の観点で必ず確認する
- **最小権限の原則**: AWS クレデンシャルは必要最低限の権限で設定する
- **セキュリティスキャン**: 生成されたインフラコードに対してセキュリティスキャンツールを実行する

AI が生成したインフラコードをそのままデプロイすることは避け、人間によるレビューを挟むことが重要です。

## まとめ

Agent Plugins for AWS は、AI コーディングエージェントとクラウドインフラの間のギャップを埋めるプロジェクトです。コードを書くだけでなく、アーキテクチャの設計からデプロイまでを AI に任せられる時代が現実になりつつあります。ただし、インフラの変更は影響範囲が大きいため、自動生成されたコードのレビューとセキュリティ確認は欠かせません。

## 参考リンク

- [awslabs/agent-plugins（GitHub）](https://github.com/awslabs/agent-plugins)
- [Introducing Agent Plugins for AWS（AWS Developer Blog）](https://aws.amazon.com/blogs/developer/introducing-agent-plugins-for-aws/)
- [deploy-on-aws プラグイン](https://github.com/awslabs/agent-plugins/tree/main/plugins/deploy-on-aws)
