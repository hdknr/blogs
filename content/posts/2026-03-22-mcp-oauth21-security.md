---
title: "MCP のセキュリティが OAuth 2.1 で大幅進化：AI エージェントと社内データを安全に接続する仕組み"
date: 2026-03-22
lastmod: 2026-03-22
draft: false
source_url: "https://github.com/hdknr/blogs/issues/1#issuecomment-4106918372"
categories: ["AI/LLM"]
tags: ["mcp", "agent", "security"]
---

AI エージェントが外部ツールやデータソースに安全にアクセスするための標準プロトコル「MCP（Model Context Protocol）」が、OAuth 2.1 ベースの認証・認可フレームワークを導入し、エンタープライズ環境での採用が加速しています。本記事では、MCP の認可仕様の仕組みと、企業導入における設計ポイントを解説します。

## MCP とは

MCP（Model Context Protocol）は、AI アシスタントがツール、データソース、サービスといった外部リソースに接続するための標準プロトコルです。Anthropic が提唱し、オープンな仕様として公開されています。

MCP を使うことで、AI エージェントは以下のようなことが可能になります：

- 社内データベースへのクエリ実行
- 外部 API の呼び出し
- ファイルシステムの操作
- 各種 SaaS サービスとの連携

## OAuth 2.1 による認可フレームワーク

MCP の認可仕様では、以下の役割分担が定義されています：

| 役割 | OAuth 2.1 での対応 |
|------|-------------------|
| MCP サーバー | リソースサーバー |
| MCP クライアント | OAuth クライアント |
| ユーザー | リソースオーナー |

### 認可フローの概要

1. MCP クライアントが保護されたサーバーに初回アクセスを試みる
2. サーバーが `401 Unauthorized` を返し、`WWW-Authenticate` ヘッダーで Protected Resource Metadata（PRM）ドキュメントへのリンクを提供する
3. クライアントは PRM から認可サーバーの情報を取得する
4. OAuth 2.1 の認可コードフロー + PKCE で認可を取得する
5. 取得したアクセストークンを使って MCP リソースにアクセスする

### PKCE の必須化

OAuth 2.1 では PKCE（Proof Key for Code Exchange）がすべてのクライアント（パブリック・コンフィデンシャル両方）で必須となっています。これにより、悪意ある MCP サーバーがインストールされた場合でも、認可コードの奪取による被害を防止できます。

```
# PKCE フローの概要
1. クライアントが code_verifier（ランダム文字列）を生成
2. code_verifier から code_challenge を算出（SHA-256）
3. 認可リクエスト時に code_challenge を送信
4. トークンリクエスト時に code_verifier で検証
```

### 動的クライアント登録

MCP の認証実装では、OAuth 2.0 Dynamic Client Registration Protocol（RFC 7591）のサポートがオプションとして定義されています（MAY）。これにより、新しい MCP クライアントが自動的に認可サーバーに登録でき、管理者の手動設定なしにクライアントを追加できます。なお、MCP では Client ID Metadata Documents による登録が推奨（SHOULD）されており、動的クライアント登録は後方互換性のための選択肢として位置づけられています。

## エンタープライズ環境での導入パターン

### 段階的なツール公開

Bloomberg や AWS などの企業が採用している段階的導入アプローチでは：

1. **フェーズ 1**: 読み取り専用のツールのみを公開
2. **フェーズ 2**: 運用実績を積んだ後、データ変更系のツールを段階的に解放
3. **フェーズ 3**: 権限の細粒度制御を導入

### ネットワーク設計

MCP サーバーの配置に関する推奨事項：

- MCP サーバーはプライベートネットワーク内に配置する
- VPN またはゼロトラストネットワーク経由でのみアクセスを許可する
- トランスポート層での暗号化（TLS）を必須とする

### 権限管理の設計

```yaml
# MCP サーバーの権限設計例
tools:
  - name: database-query
    permissions:
      - read:database
    description: "データベースへの読み取りクエリ"

  - name: database-write
    permissions:
      - read:database
      - write:database
    description: "データベースへの書き込み操作"
```

## まとめ

MCP の OAuth 2.1 対応は、AI エージェントのエンタープライズ採用における重要なマイルストーンです。PKCE の必須化、動的クライアント登録、Protected Resource Metadata といった標準的なセキュリティメカニズムの採用により、企業のセキュリティ基準を満たしながら、AI エージェントの業務活用を安全に進められるようになっています。

## 参考リンク

- [MCP Authorization Specification](https://modelcontextprotocol.io/specification/draft/basic/authorization)
- [MCP, OAuth 2.1, PKCE, and the Future of AI Authorization - Aembit](https://aembit.io/blog/mcp-oauth-2-1-pkce-and-the-future-of-ai-authorization/)
- [MCP 入門と認可 - Auth0](https://auth0.com/blog/jp-an-introduction-to-mcp-and-authorization/)
- [安全な MCP への第一歩：Authorization の仕様を理解する - Qiita](https://qiita.com/icoxfog417/items/ef2c3382056968032dd5)
