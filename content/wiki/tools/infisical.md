---
title: "Infisical"
description: ".env ファイルに依存しないオープンソースのシークレット・証明書・特権アクセス管理プラットフォーム"
date: 2026-04-23
lastmod: 2026-04-23
aliases: ["インフィジカル", "シークレット管理", "Vault 代替"]
related_posts:
  - "/posts/2026/04/2026-04-21-infisical-secret-management/"
tags: ["セキュリティ", "シークレット管理", "DevSecOps", "オープンソース"]
---

## 概要

Infisical はシークレット（API キー・パスワード・証明書）をランタイム時に取得する設計のオープンソースプラットフォーム。`.env` ファイルのようにディスクに保存しないため、ファイルベースの漏洩リスクを根本から排除する。GitHub 26,000 スター超（2026年4月時点）で HashiCorp Vault の OSS 代替として注目されている。

## 主な機能

- **シークレット管理**: プロジェクト・環境ごとの管理、バージョン履歴、自動ローテーション、監査ログ
- **証明書管理（PKI）**: プライベート CA 構築、ACME 対応、証明書自動更新
- **Machine Identity**: AI エージェント・CI/CD・サービスアカウント向けの非人間アクター認証
- **統合**: CLI・SDK（Node.js/Python/Go/Java）・Kubernetes・GitHub Actions・AWS/GCP/Azure

## CLI の基本操作

```bash
# インストール (macOS)
brew install infisical/get-cli/infisical

# ログイン・プロジェクト紐付け
infisical login
infisical init

# シークレットを注入してコマンド実行
infisical run -- node app.js
infisical run --env=staging -- python manage.py runserver
```

## AI エージェント時代との関連

Machine Identity により、AI エージェントや MCP サーバーが必要なシークレットだけをランタイムで動的取得できる。最小権限の原則を実装しやすく、シャドーAI・バイブコーディングで問題になる認証情報の平文保存リスクを排除する。

## デプロイ形態

| | クラウド版（infisical.com） | セルフホスト版 |
|---|---|---|
| データ管理 | Infisical 管理 | 自社管理 |
| コンプライアンス | SOC 2 / HIPAA 対応 | 自社ポリシー |
| 無料枠 | あり | 無制限 |

## 関連ページ

- [シャドーAI](/blogs/wiki/concepts/shadow-ai/)
- [AI エージェント](/blogs/wiki/concepts/ai-agent/)

## ソース記事

- [Infisical — .env に別れを告げるオープンソース・シークレット管理プラットフォーム](/blogs/posts/2026/04/2026-04-21-infisical-secret-management/) — 2026-04-21
