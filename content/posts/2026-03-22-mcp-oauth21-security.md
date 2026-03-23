---
title: "MCP のセキュリティが OAuth 2.1 で大幅進化：AI エージェントと社内データを安全に接続する仕組み"
date: 2026-03-22
lastmod: 2026-03-22
draft: false
source_url: "https://github.com/hdknr/blogs/issues/1#issuecomment-4106918372"
categories: ["AI/LLM"]
tags: ["mcp", "agent", "security", "oauth2"]
---

AI エージェントが外部ツールやデータソースに安全にアクセスするための標準プロトコル「MCP（Model Context Protocol）」が、OAuth 2.1 ベースの認証・認可フレームワークを導入し、エンタープライズ環境での採用が加速しています。本記事では、MCP の認可仕様の仕組みと、企業導入における設計ポイントを解説します。

## MCP とは

MCP（Model Context Protocol）は、AI アシスタントがツール、データソース、サービスといった外部リソースに接続するための標準プロトコルです。Anthropic が提唱し、オープンな仕様として公開されています。

MCP を使うことで、AI エージェントは以下のようなことが可能になります：

- 社内データベースへのクエリ実行
- 外部 API の呼び出し
- ファイルシステムの操作
- 各種 SaaS サービスとの連携

## OAuth 2.0 から 2.1 へ：何が変わったのか

OAuth 2.1 は OAuth 2.0 の後継仕様であり、これまで個別の RFC やベストプラクティスとして散在していたセキュリティ強化策を統合したものです。MCP がベースとする OAuth 2.1 では、以下の重要な変更が含まれています：

| 変更点 | 内容 |
|--------|------|
| **PKCE 必須化** | 全クライアント（パブリック・コンフィデンシャル両方）で必須に |
| **Implicit フロー廃止** | アクセストークンが URL フラグメントに露出するリスクを排除 |
| **リフレッシュトークンのローテーション** | パブリッククライアントでのトークン漏洩時の影響を軽減 |
| **リダイレクト URI の厳密一致** | ワイルドカードによるオープンリダイレクト攻撃を防止 |

つまり、OAuth 2.1 は「新機能の追加」というより、**OAuth 2.0 時代に発見された攻撃手法への対策を標準に組み込んだもの**です。

## MCP の認可アーキテクチャ

MCP の認可仕様では、OAuth 2.1 をベースに、AI エージェント特有の要件に対応した複数の仕組みを組み合わせています。

### 役割の定義

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

### PKCE：認可コードの横取りを防ぐ

PKCE（Proof Key for Code Exchange）は、認可コードの横取り攻撃を防ぐ仕組みです。OAuth 2.1 では全クライアントで必須化されました。

```
# PKCE フローの概要
1. クライアントが code_verifier（ランダム文字列）を生成
2. code_verifier から code_challenge を算出（SHA-256）
3. 認可リクエスト時に code_challenge を送信
4. トークンリクエスト時に code_verifier で検証
→ 認可コードを傍受しても code_verifier がなければトークン取得不可
```

### Resource Indicators：トークンの流用を防ぐ

MCP では Resource Indicators（RFC 8707）の実装が必須（MUST）です。これにより、アクセストークンが**特定の MCP サーバー専用**にバインドされ、別のサーバーでの流用が防止されます。

```http
# 認可リクエストに resource パラメータを含める
GET /authorize?
  response_type=code&
  client_id=example-client&
  resource=https://mcp.example.com&
  code_challenge=E9Melhoa2OwvFrEMTJguCHaoeK1t8URWbuGJSstw-cM&
  code_challenge_method=S256
```

これは PKCE とは異なるレイヤーの保護です。PKCE が「認可コードの横取り」を防ぐのに対し、Resource Indicators は「正規に取得したトークンの別サービスでの悪用」を防ぎます。

### Protected Resource Metadata：認可サーバーの安全な発見

MCP サーバーは OAuth 2.0 Protected Resource Metadata（RFC 9728）の実装が必須です。これにより、クライアントは MCP サーバーがどの認可サーバーを使っているかを標準的な方法で発見できます。

```http
# MCP サーバーが返す 401 レスポンス例
HTTP/1.1 401 Unauthorized
WWW-Authenticate: Bearer resource_metadata="https://mcp.example.com/.well-known/oauth-protected-resource",
                         scope="files:read"
```

手動でエンドポイントを設定する必要がなくなり、MCP クライアントとサーバーの接続がセキュアかつ自動的に行われます。

### クライアント登録：事前関係なしでの安全な接続

MCP では 3 つのクライアント登録方式をサポートしています：

1. **Client ID Metadata Documents**（推奨）— HTTPS URL をクライアント ID として使用し、事前登録なしで安全に識別
2. **事前登録** — 従来の OAuth のように事前にクライアント ID を取得
3. **動的クライアント登録（RFC 7591）**（オプション）— 後方互換性のための選択肢

AI エージェントのエコシステムでは、MCP クライアントとサーバーが事前の関係なしに接続するケースが多いため、Client ID Metadata Documents が推奨されています。

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

MCP の OAuth 2.1 対応は、単に PKCE を導入しただけではありません。OAuth 2.1 による安全なフロー（PKCE 必須化、Implicit フロー廃止）をベースに、Resource Indicators によるトークンのサーバーバインド、Protected Resource Metadata による認可サーバーの自動発見、Client ID Metadata Documents による事前関係なしの安全な接続といった、AI エージェント特有の要件に対応した複数のセキュリティレイヤーを組み合わせています。

これらの標準仕様の採用により、独自のセキュリティ実装に頼ることなく、企業のセキュリティ基準を満たしながら AI エージェントの業務活用を安全に進められるようになっています。

## 参考リンク

- [MCP Authorization Specification](https://modelcontextprotocol.io/specification/draft/basic/authorization)
- [MCP, OAuth 2.1, PKCE, and the Future of AI Authorization - Aembit](https://aembit.io/blog/mcp-oauth-2-1-pkce-and-the-future-of-ai-authorization/)
- [MCP 入門と認可 - Auth0](https://auth0.com/blog/jp-an-introduction-to-mcp-and-authorization/)
- [安全な MCP への第一歩：Authorization の仕様を理解する - Qiita](https://qiita.com/icoxfog417/items/ef2c3382056968032dd5)
