---
title: "OpenClawスキルの厳選コレクション — AIエージェントを即戦力にするスキル集"
date: 2026-03-15
lastmod: 2026-03-15
draft: false
source_url: "https://github.com/hdknr/blogs/issues/1#issuecomment-4062012721"
categories: ["AI/LLM"]
tags: ["openclaw", "claude-code", "agent", "github"]
---

OpenClawのスキルエコシステムが急速に拡大しています。公式レジストリ「ClawHub」には13,000以上のコミュニティ製スキルが登録されていますが、その中から厳選・カテゴリ整理されたコレクションが公開され、注目を集めています。

## OpenClawスキルとは

OpenClawはローカルで動作するAIアシスタントです。「スキル」は外部サービスとの連携やワークフローの自動化を実現する拡張機能で、インストールするだけでエージェントの能力を大幅に拡張できます。

## 注目のスキルコレクション

### awesome-openclaw-skills（VoltAgent）

[VoltAgent/awesome-openclaw-skills](https://github.com/VoltAgent/awesome-openclaw-skills) は、ClawHubの13,729スキルからスパム・重複・低品質なものを除外し、**5,366スキル**を厳選したAwesomeリストです。GitHub スター数は37,000超。

主なカテゴリ:

| カテゴリ | スキル数 |
|----------|---------|
| Coding Agents & IDEs | 1,222 |
| Web & Frontend Development | 938 |
| DevOps & Cloud | 409 |
| Search & Research | 352 |
| Browser & Automation | 335 |
| Productivity & Tasks | 206 |
| AI & LLMs | 197 |
| Git & GitHub | 170 |

### openclaw-master-skills（LeoYeAI）

[LeoYeAI/openclaw-master-skills](https://github.com/LeoYeAI/openclaw-master-skills) は、MyClaw.aiが毎週更新する**339+スキル**の厳選コレクションです。AI、生産性、開発、マーケティング、金融など幅広いカテゴリをカバーしています。

## カテゴリ別おすすめスキル

### AIツール連携

- **Slack**: リアルタイムメッセージの送受信、チャンネル管理
- **Notion**: ページの同期・ナレッジ管理
- **Outlook**: メール操作・カレンダー連携
- **Linear / Trello**: タスク管理・プロジェクト進捗の追跡
- **1Password**: シークレット管理・セキュリティ連携

### DevOps自動化

- **Docker**: コンテナのビルド・管理・デプロイ
- **Git**: ブランチ管理、コミット履歴の操作
- **GitHub CLI**: Issue・PR の操作、リリース管理
- **n8n**: ワークフロー自動化
- **Expo CI/CD**: モバイルアプリのビルド・デプロイ

### Web自動化

- **Playwright**: フォーム入力、データ抽出、ブラウザ操作
- AIによるWebタスクの自動化

### 生産性向上

- **Todoist / Things 3**: タスク管理
- カレンダー同期
- ドキュメント処理

### 開発パターン

- **Next.js**: 実装パターン
- **React**: 状態管理
- **Node.js**: バックエンドパターン
- **REST / GraphQL**: API設計
- **SQL**: データベース操作

## スキルのインストール方法

ClawHub CLIを使ったインストール:

```bash
openclaw skills install <スキル名>
```

手動インストールの場合は、スキルファイルを `~/.openclaw/skills/` ディレクトリに配置します。

## セキュリティに関する注意

スキルはコードを直接実行する仕組みのため、インストール前に以下を確認することが推奨されます:

- **ソースコードの確認**: スキルの内容を事前にレビューする
- **信頼できるソースから取得**: ClawHubの公式レジストリや、Awesomeリストで厳選されたスキルを利用する
- **権限の確認**: スキルがアクセスするリソース（ファイルシステム、ネットワーク、外部API）を把握する

VirusTotalとの連携によるセキュリティスキャンも統合されていますが、最終的な判断はユーザー自身が行う必要があります。

## まとめ

OpenClawのスキルエコシステムは、単体のAIツールから「拡張可能なAIプラットフォーム」へと進化しています。厳選コレクションを活用すれば、スキルをゼロから作る必要なく、すぐにエージェントの能力を拡張できます。まずは自分のワークフローに合ったカテゴリからスキルを試してみることをおすすめします。
