---
title: "Infisical — .env に別れを告げるオープンソース・シークレット管理プラットフォーム"
date: 2026-04-21
lastmod: 2026-04-23
draft: false
source_url: "https://github.com/hdknr/blogs/issues/1#issuecomment-4287249404"
categories: ["セキュリティ"]
tags: ["Infisical", "シークレット管理", "security", "agent", "docker"]
description: "Infisical は .env ファイルに依存しないオープンソースのシークレット管理プラットフォーム。チーム開発・Kubernetes・GitHub Actions・AI エージェントと統合でき、シークレットをランタイム取得することでディスク上の漏洩リスクを排除します。"
---

`.env` よ、安らかに眠れ——。

AI 時代の開発現場では、シークレット（API キー・データベースパスワード・証明書など）の扱い方が大きな課題になっています。従来は `.env` ファイルに書いておけばなんとかなっていました。しかしチーム規模が拡大したり、AI エージェントが複数のサービスを横断して動くようになると、`.env` ベースの管理はほころびを見せてきます。

**Infisical** は、そんな `.env` の時代を終わらせるべく登場したオープンソースのシークレット管理プラットフォームです。

## .env の何が問題なのか

`.env` ファイルによるシークレット管理には以下のような問題があります。

- **ディスクに残る**: 誤って `git add .env` してしまうリスクが常に存在する
- **同期が難しい**: 複数人・複数環境での値の一元管理が困難
- **ローテーションが手動**: シークレットを更新するたびに全メンバーへの周知が必要
- **監査ログがない**: いつ誰がどの値を変更したか追跡できない
- **AI エージェントとの相性が悪い**: エージェントが環境変数ファイルを読み書きすると漏洩リスクが増大する

## Infisical とは

[Infisical](https://github.com/Infisical/infisical) は、シークレット・証明書・特権アクセスを一元管理するオープンソースプラットフォームです。2026年4月時点で GitHub 26,000 スター超を獲得しており、Vault の OSS 代替として注目されています。

最大の特徴は、**シークレットをランタイム時に取得する**設計にあります。`.env` ファイルのようにディスクに値を保存しないため、ファイルベースの漏洩リスクを根本から排除します。

## 主な機能

### シークレット管理

- プロジェクト・環境（dev / staging / prod）ごとのシークレット管理
- シークレットのバージョン履歴と自動ローテーション
- 変更の監査ログ
- シークレット参照（他のシークレットの値を参照する変数展開）

### 証明書管理（PKI）

- プライベート CA の構築と証明書の発行
- ACME プロトコル対応で Let's Encrypt 互換のワークフロー
- 証明書の有効期限監視と自動更新

### 統合機能

- **CLI**: あらゆる言語・フレームワークのコマンドをシークレット付きで実行
- **SDK**: Node.js、Python、Go、Java など主要言語のネイティブ SDK
- **インフラ統合**: Kubernetes、GitHub Actions、AWS、GCP、Azure など

## 基本的な使い方

### インストール

```bash
# macOS (Homebrew)
brew install infisical/get-cli/infisical

# npm
npm install -g @infisical/cli
```

### ログインとプロジェクト初期化

```bash
# Infisical にログイン
infisical login

# プロジェクトに紐付け
infisical init
```

### シークレットを注入してコマンドを実行

```bash
# .env の代わりに Infisical からシークレットを取得してアプリを起動
infisical run -- node app.js

# 環境を指定
infisical run --env=staging -- python manage.py runserver
```

### SDK から直接取得（Node.js の例）

```javascript
import { InfisicalSDK } from "@infisical/sdk";

const client = new InfisicalSDK();

await client.auth().universalAuth.login({
  clientId: process.env.INFISICAL_CLIENT_ID,
  clientSecret: process.env.INFISICAL_CLIENT_SECRET,
});

const secret = await client.secrets().getSecret({
  secretName: "DATABASE_URL",
  projectId: "my-project-id",
  environment: "production",
});
```

## AI 時代のシークレット管理

AI エージェントや MCP サーバーが普及した今、シークレット管理の重要性はさらに高まっています。

- **エージェントの認証情報を動的取得**: 各エージェントが必要なシークレットだけをランタイムで取得し、不要な権限を持たせない
- **最小権限の原則**: プロジェクトや環境単位でアクセス制御を細かく設定
- **自動ローテーションでリスク最小化**: 漏洩が疑われるシークレットをすばやく無効化・交換

Infisical は、マシン ID（Machine Identity）という概念でエージェント・CI/CD・サービスアカウントを管理します。人間のユーザーと同じ認証基盤で非人間アクター（AI エージェントを含む）を制御できる点が現代的な設計です。

## セルフホストとクラウド

Infisical はクラウド版（[infisical.com](https://infisical.com)）とセルフホスト版の両方を提供しています。

| | クラウド版 | セルフホスト版 |
|---|---|---|
| 運用コスト | 低 | 要インフラ整備 |
| データ管理 | Infisical 管理 | 自社管理 |
| コンプライアンス | SOC 2 対応 | 自社ポリシー対応 |
| 無料枠 | あり | 無制限 |

Docker Compose を使ってセルフホストを始めることもできます。

```bash
curl -o docker-compose.prod.yml https://raw.githubusercontent.com/Infisical/infisical/main/docker-compose.prod.yml
curl -o .env https://raw.githubusercontent.com/Infisical/infisical/main/.env.example
docker compose -f docker-compose.prod.yml up -d
```

## まとめ

`.env` ファイルは長年の功労者ですが、現代の開発・運用スタイルには限界があります。Infisical は以下を提供します。

- **ディスクに残らない**シークレット取得
- **チーム全体**での一元管理と監査ログ
- **あらゆる言語・インフラ**との統合
- **AI エージェント時代**に対応した非人間アクター管理

オープンソースで始められる点も魅力で、まずは小規模プロジェクトから導入を試みるとよい。

- GitHub: [Infisical/infisical](https://github.com/Infisical/infisical)
- 公式サイト: [infisical.com](https://infisical.com)
- ドキュメント: [infisical.com/docs](https://infisical.com/docs)
