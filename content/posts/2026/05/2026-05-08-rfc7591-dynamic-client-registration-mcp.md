---
title: "Claude Code はなぜ事前登録なしで MCP に繋がるのか — RFC 7591 Dynamic Client Registration と連動 RFC 群"
date: 2026-05-08
lastmod: 2026-05-08
draft: false
description: "MCP クライアントが事前登録なしで認可サーバーに繋がる仕組みを RFC 7591（Dynamic Client Registration）と RFC 9728 / 8414 / 9068 / 8707 / 7636 の連動から解説。Claude Code の自動ログインフローと JWT audience 検証でハマる構造を仕様レベルで追える。"
categories: ["セキュリティ"]
tags: ["mcp", "oauth2", "dcr", "claude-code", "jwt", "pkce"]
---

[個人開発アプリの認証は「絶対に」WorkOS を使え — MCP 化で知った最強の選択肢]({{< ref "/posts/2026/04/2026-04-27-workos-authkit-mcp-authentication" >}}) では、WorkOS AuthKit の Dynamic Client Registration（DCR）対応が MCP 認証の決め手になる、という話を書いた。

MCP × OAuth 2.1 の全体像は [MCP のセキュリティが OAuth 2.1 で大幅進化]({{< ref "/posts/2026/03/2026-03-22-mcp-oauth21-security" >}}) で扱った。本記事はその中で SHOULD/MAY 扱いされている DCR を仕様レベルで深掘りする補足記事だ。

具体的には、**DCR を定義する RFC 7591 そのものの仕様と、MCP 認証で必ず連動する周辺 RFC 群（9728 / 8414 / 9068 / 8707 / 7636）の関係** を、Claude Code の自動ログインフローを追いながら整理する。

この記事でわかること:

- なぜ事前登録なしにクライアントが認可サーバーに繋がってくるのか（RFC 7591 / 9728 / 8414 の連動）
- Claude Code の自動ログインフローを HTTP リクエスト単位で何が起きているか
- なぜ JWT の audience 検証で詰まるのか（RFC 9068 / 8707 と DCR の構造的な相性問題）

## なぜ MCP では Dynamic Client Registration（DCR）が必要なのか

従来の OAuth 2.0（RFC 6749）は、**クライアント（アプリ）を事前に手動登録する** 前提だった。Google や GitHub の OAuth を使うときに、開発者が「アプリを登録 → `client_id` と `client_secret` を発行 → コードに埋め込み」という流れだ。

これは「クライアント側の開発者が事前にサーバー管理者に挨拶できる」前提が成り立つ場合は問題ない。しかし MCP の世界ではこの前提が崩れる。

- MCP サーバーから見ると、**繋ぎに来るクライアントが誰か事前にわからない**（Claude Code、Cursor、これから出る MCP クライアント、ユーザーが書いた野良クライアント…）
- MCP クライアントから見ると、**繋ぎに行くサーバーは無数にある**（Notion、Linear、Stripe、個人開発の小さなサーバー…）

ここで「サーバー管理者が事前に全クライアントを登録しておく」のは不可能だ。

RFC 7591（2015 年策定）は、この **クライアントが自分自身をプログラムで登録するためのプロトコル** を定義する。

## RFC 7591 の核 — Registration Endpoint と client_id の動的発行

認可サーバーは `registration_endpoint` という URL を公開する。クライアントはここに JSON で POST するだけで、`client_id` を入手できる。

### リクエスト例

```http
POST /register HTTP/1.1
Content-Type: application/json
Host: server.example.com

{
  "redirect_uris": ["https://client.example.org/callback"],
  "client_name": "My MCP Client",
  "client_uri": "https://client.example.org",
  "grant_types": ["authorization_code", "refresh_token"],
  "response_types": ["code"],
  "scope": "openid profile email",
  "token_endpoint_auth_method": "none"
}
```

### レスポンス例

```http
HTTP/1.1 201 Created
Content-Type: application/json

{
  "client_id": "s6BhdRkqt3",
  "client_secret": "cf136dc3c1fc93f31185e5885805d",
  "client_id_issued_at": 1571276473,
  "client_secret_expires_at": 0,
  "redirect_uris": ["https://client.example.org/callback"],
  "client_name": "My MCP Client",
  "registration_access_token": "this.is.an.access.token",
  "registration_client_uri": "https://server.example.com/register/s6BhdRkqt3"
}
```

ポイントは 4 つある。

- **`client_id` がその場で発行される**（事前登録なし）
- **`token_endpoint_auth_method: "none"`** にすれば public client として登録できる（client secret なしでも動く。MCP クライアントは典型的にこちら）
- **`registration_access_token`** と **`registration_client_uri`** は RFC 7592（Dynamic Client Registration Management Protocol）で使う、後からクライアント情報を更新・削除するための鍵
- **`client_secret_expires_at: 0`** は「無期限」を意味する（RFC 7591 §3.2.1）

## 標準化されたクライアントメタデータ

RFC 7591 のもう一つの貢献は、**クライアントメタデータの語彙を標準化したこと**。代表的なフィールドだけ抜き出す（§2 より）。

| フィールド | 意味 |
|---|---|
| `redirect_uris` | コールバック URL（必須） |
| `token_endpoint_auth_method` | クライアント認証方式（`none` / `client_secret_basic` / `client_secret_post` / `private_key_jwt`） |
| `grant_types` | 使う grant（`authorization_code`, `refresh_token`, `client_credentials` 等） |
| `response_types` | `code` / `token` |
| `scope` | スペース区切りのスコープ |
| `client_name`, `client_uri`, `logo_uri`, `tos_uri`, `policy_uri` | 同意画面で表示する UI 用メタ |
| `jwks_uri`, `jwks` | クライアント側公開鍵（`private_key_jwt` 用） |
| `software_id`, `software_version` | クライアントソフトウェアの識別 |
| `software_statement` | 信頼できる発行元が署名した JWT 形式の自己宣言 |

OIDC・SCIM・UMA など他の仕様もこの語彙を再利用していて、OAuth まわりの「クライアント情報の共通語」になっている。

## Open Registration vs Protected Registration

RFC 7591 §3 では、登録エンドポイント自体の保護方式を 2 つ示している。

- **Open Registration**: 誰でも登録できる（認証不要）。MCP / 一般公開サーバー向け
- **Protected Registration**: `Initial Access Token` を持つクライアントだけ登録できる。社内・パートナー向け

WorkOS AuthKit を含む MCP 対応の認可サーバーは、Open Registration を採用するのが普通。これがないと「Claude Code がいきなり来て勝手にクライアント登録する」が成立しない。

## MCP 認証で連動する RFC 群

ここからが本題。MCP の認可フローでは、RFC 7591 単体では足りず、複数の RFC が組み合わさって動く。

| RFC | 役割 |
|---|---|
| **RFC 9728**（2025-04 発行） | Protected Resource Metadata。`/.well-known/oauth-protected-resource` で「このリソースサーバー（= MCP サーバー）の認可サーバーはどれか」を公開 |
| **RFC 8414** | Authorization Server Metadata。`/.well-known/oauth-authorization-server` で `registration_endpoint` を含むサーバー機能を公開 |
| **RFC 7591** | Dynamic Client Registration。クライアントが自分自身を登録する |
| **RFC 7636** | PKCE。public client が安全に code 交換するために必須 |
| **RFC 9068** | JWT Profile for OAuth 2.0 Access Tokens。アクセストークンが JWT のときの形式 |
| **RFC 8707** | Resource Indicators。トークンを「どのリソース向けか」絞り込む |
| **RFC 6749** | OAuth 2.0 Framework（コア） |

特に押さえるべきは、**MCP の認可仕様（2025-06-18 / 2025-11-25 版）が RFC 9728 と RFC 8414 を MUST、RFC 7591 を SHOULD/MAY としている** 点だ。MCP サーバー実装者は、この 2 つの `.well-known` エンドポイントが必須と思っていい。

## Claude Code の自動ログインを仕様レベルで追う

WorkOS AuthKit 記事の「Claude Code が勝手にログインする仕組み」を、上の RFC 群にマッピングしてみる。全体像をシーケンス図にすると以下のとおり。

![Claude Code が MCP サーバーに認証付きで繋がるまでの OAuth プロトコルフロー。Phase 1（RFC 9728 でリソース発見）、Phase 2（RFC 8414 で認可サーバーメタデータ取得）、Phase 3（RFC 7591 DCR で client_id を動的発行）、Phase 4（RFC 6749 + 7636 PKCE で認可コードフロー）、Phase 5（RFC 9068 JWT で MCP を Bearer 認証）の 5 フェーズと、audience 検証の罠を含む詳細シーケンス図](/blogs/images/rfc7591-mcp-oauth-flow.png)

5 つのフェーズに分けて読むと整理しやすい。Phase 3（紫枠）が本記事の主役 RFC 7591 だ。以下、各ステップを順に追う。

### Step 1: 401 + リソースメタデータ URL

Claude Code が MCP エンドポイント（典型的には `/mcp` への POST で `initialize` リクエスト）にアクセスすると、サーバーは `401` で `WWW-Authenticate` ヘッダーを返す。**RFC 9728 §5.1** がこの形式を規定している。

```http
HTTP/1.1 401 Unauthorized
WWW-Authenticate: Bearer resource_metadata="https://mcp.example.com/.well-known/oauth-protected-resource"
```

### Step 2: Protected Resource Metadata（RFC 9728）

Claude Code が `resource_metadata` URL を GET する。

```http
GET /.well-known/oauth-protected-resource HTTP/1.1
Host: mcp.example.com
```

```json
{
  "resource": "https://mcp.example.com/mcp",
  "authorization_servers": ["https://your-tenant.authkit.app"],
  "bearer_methods_supported": ["header"],
  "scopes_supported": ["openid", "profile", "email", "offline_access"],
  "resource_name": "My MCP Server"
}
```

ここで初めて、**「この MCP サーバーの認可サーバーは `https://your-tenant.authkit.app` だ」** とクライアントが知る。`authorization_servers` は配列なので、複数の認可サーバーをサポートする MCP サーバーも仕様上は許される。

### Step 3: Authorization Server Metadata（RFC 8414）

次に Claude Code は、認可サーバーのメタデータを取りに行く。

```http
GET /.well-known/oauth-authorization-server HTTP/1.1
Host: your-tenant.authkit.app
```

レスポンスには、これから使う各種エンドポイントが全部入っている。

```json
{
  "issuer": "https://your-tenant.authkit.app",
  "authorization_endpoint": "https://your-tenant.authkit.app/oauth2/authorize",
  "token_endpoint": "https://your-tenant.authkit.app/oauth2/token",
  "registration_endpoint": "https://your-tenant.authkit.app/oauth2/register",
  "jwks_uri": "https://your-tenant.authkit.app/oauth2/jwks",
  "code_challenge_methods_supported": ["S256"],
  "grant_types_supported": ["authorization_code", "refresh_token"],
  "response_types_supported": ["code"]
}
```

`registration_endpoint` は RFC 8414 §2 で OPTIONAL と規定されている。**このフィールドが存在することが、認可サーバーが DCR をサポートしているシグナル** になる。

### Step 4: Dynamic Client Registration で client_id を動的取得（RFC 7591）

ここが本記事の主役。Claude Code は `registration_endpoint` に POST して、自分用の `client_id` を取得する。

```http
POST /oauth2/register HTTP/1.1
Host: your-tenant.authkit.app
Content-Type: application/json

{
  "client_name": "Claude Code",
  "redirect_uris": ["http://localhost:33418/callback"],
  "grant_types": ["authorization_code", "refresh_token"],
  "response_types": ["code"],
  "token_endpoint_auth_method": "none"
}
```

Claude Code は登録結果（`client_id` など）をローカルに保存する。そのため、別 PC の Claude Code は最初のアクセスで再度 DCR を走らせ、また別の `client_id` を取得することになる（RFC 7591 自身は「同一クライアントが何度登録してよいか」を規定していない。これは Claude Code 側の実装方針）。

### Step 5: 認可リクエスト + PKCE（RFC 7636）

Claude Code はブラウザを起動し、`authorization_endpoint` に飛ばす。public client なので PKCE は必須だ（RFC 7636）。

```
https://your-tenant.authkit.app/oauth2/authorize
  ?response_type=code
  &client_id=<Step 4 で取得した client_id>
  &redirect_uri=http://localhost:33418/callback
  &scope=openid+profile+email+offline_access
  &code_challenge=<S256 ハッシュ>
  &code_challenge_method=S256
  &state=<csrf token>
```

ユーザーがブラウザでログインボタンを押すと、`redirect_uri` に code が返ってくる。

### Step 6: Token 交換

Claude Code は `token_endpoint` に code と PKCE verifier を投げて、access token を入手する。

```http
POST /oauth2/token HTTP/1.1
Host: your-tenant.authkit.app
Content-Type: application/x-www-form-urlencoded

grant_type=authorization_code
&code=<step 5 の code>
&redirect_uri=http://localhost:33418/callback
&client_id=<step 4 の client_id>
&code_verifier=<S256 の元>
```

返ってくるアクセストークンは、RFC 9068（JWT Profile）に従った JWT 形式が多い（不透明トークンを返す認可サーバーもある）。

### Step 7: 認証付きで MCP を叩く

Claude Code は手に入れた JWT を Bearer に付けて、MCP サーバーに再リクエストする。

```http
POST /mcp HTTP/1.1
Host: mcp.example.com
Authorization: Bearer eyJhbGciOiJSUzI1NiIs...
```

MCP サーバー側は、認可サーバーの JWKS で JWT 署名を検証し、`sub` を見てユーザーを特定する。

## なぜ audience 検証でハマるのか

WorkOS AuthKit 記事で「JWT の `aud` 検証はスキップした」と書いた件を、ここまでの仕様で説明できる。

RFC 9068（JWT Access Token Profile, 2021 年）§2.2 では、`aud` クレームは必須で、RFC 8707 の resource indicator（つまり `https://mcp.example.com/mcp` のような URL）が利用可能な場合はその値が入ると規定される。

ところが、多くの認可サーバーは歴史的に `aud` に **「リクエストした client_id」** を入れる実装を残している。これは RFC 9068 制定（2021 年）以前の OIDC ID Token の慣習が引き継がれたもので、9068 の本来の意図からは外れる。

ここで DCR と組み合わさると問題が起きる。

- MCP サーバーから見れば、信頼したい `aud` は **リソース URL**（自分の MCP エンドポイント）
- 一方、JWT に乗ってくる `aud` は **動的に発行された client_id**（Claude Code が Step 4 で取得したやつ）
- この `client_id` は MCP サーバー側が事前に知らない値なので、検証式に書きようがない

正しい対処は二択。

1. **認可サーバーが `audience` / `resource` パラメータをサポートしている場合**: トークン要求時に `resource=https://mcp.example.com/mcp` を渡し、JWT の `aud` をリソース URL にしてもらう。MCP サーバー側はこの URL で `aud` 検証する
2. **サポートしていない場合**: `aud` 検証は実質スキップし、`issuer` + JWKS 署名検証で足りるとみなす（必要なら resource indicator を実装依存のクレーム名で別途確認する）

WorkOS AuthKit 記事の「`skipAudience: true`」は後者のパターン。RFC 8707 の resource indicator が普及してくると、徐々に前者のパターンに寄っていくはずだ。

## DCR の限界（RFC 7591 §5 + 7592）

DCR は強力だが、Open Registration を素直に実装するといくつかの構造的な問題に当たる。RFC 7591 §5 自身が以下のリスクを挙げている。

- **`redirect_uris` の検証不足** → オープンリダイレクトで認可コード横取り
- **`client_name` / `logo_uri` の偽装** → 同意画面でのフィッシング。動的に作られたクライアントが「正規アプリ」を装って同意画面に出てくる、という事故が起きやすい
- **登録の濫用** → 大量の不要クライアントが登録される DoS

加えて、**RFC 7592（Dynamic Client Registration Management Protocol）** で定義される後続管理（クライアント情報の取得・更新・削除）は、`registration_access_token` を使う仕組みが用意されているものの、現状ほとんど実装されていない。Claude Code がアンインストール時に自分の登録を綺麗に消す、といった「片付け」が標準では起きない。

WorkOS のような商用認可サーバーは、これらの罠に対処している（rate limit、redirect URI の HTTPS 強制、`localhost` 例外の扱いなど）。自前で DCR エンドポイントを実装するなら、ここの作り込みコストが高いので「素直にマネージドサービスを使え」という結論になる。

## DCR の代替：CIMD（Client ID Metadata Document）

DCR の限界を踏まえ、**MCP 認可仕様は DCR を将来的に置き換える方向で検討中** だ。

新しいアプローチは **Client ID Metadata Documents（CIMD）** と呼ばれ、クライアントが自分のメタデータ JSON を URL で公開し、`client_id` としてその URL 自体を使う、という方式。サーバー側は登録ステップなしに、その URL を fetch するだけでクライアントを認識できる。すでに ATProto / Bluesky の OAuth で先行採用されており、絵空事ではない。

CIMD は DCR の問題点を以下のように解決する。

- 同意画面に出るクライアントメタデータが **URL の所有者によって署名・公開された値** なので、信頼判定がしやすい
- 登録ステップが消えるので **濫用 DoS のリスクが下がる**
- 認可サーバー側も **registration エンドポイントを持たなくて良い**

MCP 2025-11-25 版以降の仕様改訂で DCR の位置づけが SHOULD から MAY に下がったのは、この移行を見据えたもの（CIMD 自体は 2026 年 5 月時点でまだ正式採択されていない）。

ただし当面、本番運用に乗っているのは DCR が中心。WorkOS AuthKit のような既存サーバーが DCR で動く以上、しばらくは RFC 7591 を理解しておく価値がある。

## まとめ

MCP の認証フローは、表面的には「Claude Code が勝手にログインしてくれる魔法」に見える。が、その裏では複数の RFC が連携している。

- **RFC 9728** がリソースサーバーの認可サーバーを指す
- **RFC 8414** が認可サーバーの機能（特に `registration_endpoint`）を公開する
- **RFC 7591**（DCR）でクライアントが自分を登録する
- **RFC 7636**（PKCE）+ **RFC 6749**（OAuth Core）で認可フローを実行
- **RFC 9068** で JWT 化、**RFC 8707** で resource indicator が乗る

これが揃って初めて、「事前登録なしで未知のクライアントがサーバーに繋がる」が成立する。RFC 7591 だけでは足りないし、RFC 9728 だけでも足りない。

将来的に CIMD が普及して DCR が脇役になる可能性はあるものの、現状の MCP エコシステムを理解する上で、この RFC 群の関係を押さえておくと「なぜここでハマるのか」「なぜこのエンドポイントが必要なのか」が一気に腑に落ちるはずだ。

## 参考リンク

- [RFC 7591: OAuth 2.0 Dynamic Client Registration Protocol](https://datatracker.ietf.org/doc/html/rfc7591)
- [RFC 7592: OAuth 2.0 Dynamic Client Registration Management Protocol](https://datatracker.ietf.org/doc/html/rfc7592)
- [RFC 8414: OAuth 2.0 Authorization Server Metadata](https://datatracker.ietf.org/doc/html/rfc8414)
- [RFC 9728: OAuth 2.0 Protected Resource Metadata](https://datatracker.ietf.org/doc/html/rfc9728)
- [RFC 9068: JWT Profile for OAuth 2.0 Access Tokens](https://datatracker.ietf.org/doc/html/rfc9068)
- [RFC 8707: Resource Indicators for OAuth 2.0](https://datatracker.ietf.org/doc/html/rfc8707)
- [RFC 7636: Proof Key for Code Exchange (PKCE)](https://datatracker.ietf.org/doc/html/rfc7636)
- [Model Context Protocol Authorization Specification](https://modelcontextprotocol.io/specification/2025-06-18/basic/authorization)
- [Let's fix OAuth in MCP（Aaron Parecki）](https://aaronparecki.com/2025/04/03/15/oauth-for-model-context-protocol)
- [MCP のセキュリティが OAuth 2.1 で大幅進化]({{< ref "/posts/2026/03/2026-03-22-mcp-oauth21-security" >}})
- [個人開発アプリの認証は「絶対に」WorkOS を使え — MCP 化で知った最強の選択肢]({{< ref "/posts/2026/04/2026-04-27-workos-authkit-mcp-authentication" >}})
