---
title: "個人開発アプリの認証は「絶対に」WorkOS を使え — MCP 化で知った最強の選択肢"
date: 2026-04-27
lastmod: 2026-04-27
draft: false
description: "個人開発アプリの MCP 化で避けられない認証問題を WorkOS AuthKit で解決する方法を解説。Dynamic Client Registration（RFC 7591）対応・月間 100 万 MAU 無料。Next.js App Router での実装を 4 ステップ・50 行以内で完成させる手順と、JWT audience / issuer のハマりポイントも紹介。"
source_url: "https://github.com/hdknr/blogs/issues/1#issuecomment-4326314467"
categories: ["AI/LLM"]
tags: ["WorkOS", "MCP", "Claude Code", "OAuth2", "JWT"]
---

個人開発アプリを MCP 化しようとして、認証の壁に阻まれた経験はないだろうか。
大手 SaaS が次々と MCP を公開する今、個人開発者も「自分のアプリを MCP で叩けるようにしたい」と思うのは自然な流れだ。
しかし認証の設計は想像以上に重い。

この記事では、WorkOS AuthKit を使えば MCP 認証（OAuth 2.0 Dynamic Client Registration 対応）を Next.js で 30 分・50 行以内に実装できる理由と具体的な手順を紹介する。

## MCP 化の波が押し寄せている

ここ数ヶ月で、Notion・Linear・Stripe・Vercel・Cloudflare など、ちょっと触っているサービスはほぼ間違いなく MCP を出している印象だ。

Claude Code や Cursor に登録すれば、「自分の Notion を読んで」「Linear に issue を立てて」が自然言語で動く。  
**個人開発者にとっても無視できない流れだ。** 自分の作ったアプリも、CLI だけじゃなく MCP で叩けるようにしておくと、ユーザー体験が一段別物になる。

## 認証の壁

いざ自作アプリを MCP 化しようとすると、ほぼ全員がここで止まる。

「Bearer トークンを受け取って検証する」と書くと一行だが、実際には：

- ユーザーごとにアクセストークンを発行する仕組み
- Claude Code などのクライアント側がトークンをどう取得するか（OAuth？API キー手動コピペ？）
- トークンをどう保存・更新するか（リフレッシュトークン、有効期限...）
- 複数クライアントから同じユーザーが繋ぐ場合の扱い

これを真面目に作ると、週末が溶ける。筆者（html-to-pptx 作者）も最初は自前で API キー方式を実装していたが、「MCP クライアントから自動でログインさせたい」と思った瞬間、設計が一気に重くなることに気づいた。

## 結論：WorkOS（AuthKit）を使え

タイトルにも書いたが、もう一度言う。**個人開発者が MCP 化するなら、WorkOS の AuthKit 一択だ。** B2B 向けのサービス展開を考えている場合も、その場合も WorkOS が特におすすめだ。

理由は3つある。

### 1. Dynamic Client Registration（RFC 7591）に標準対応

これが最大のポイントだ。

Claude Code・Cursor・その他の MCP クライアントは、サーバーごとに事前にクライアント登録などしない。代わりに MCP サーバーに繋ぎに行ったとき、その場で自分用の OAuth クライアントを登録する仕組み（Dynamic Client Registration）を使う。

WorkOS AuthKit は、これに最初から対応している。あなたが何もしなくても、Claude Code が勝手にクライアント登録 → OAuth フロー開始 → トークン取得まで全部やってくれる。

Auth0 や Clerk でも頑張れば対応できるが、設定や有料プランが必要だったり、ドキュメントを掘る時間がかかったりする。WorkOS はここが標準装備だ。

### 2. 「個人開発者のためにある」無料枠

WorkOS は AuthKit に関して、**月間アクティブユーザー 1,000,000 人まで無料**だ。

事実上、個人開発者は課金を心配する必要がない。プロダクトが伸び始めても、認証コストはゼロ。Stripe 連携を入れて売上が立ち始めてから考えればいい話だ。

### 3. Next.js（特に App Router）との統合がおそろしく綺麗

`@workos-inc/authkit-nextjs` という SDK があり、ログインボタン・コールバック・セッション管理まで、本当に数十行で完成する。

## Claude Code が「勝手にログイン」する仕組み

Claude Code と MCP サーバーの間でどのようなやり取りが起きるか、フローを整理する。

ユーザーが Claude Code で `claude mcp add https://your-app.com/mcp` のように追加した瞬間、こんな流れが走る：

1. **Claude Code があなたの MCP エンドポイント（/mcp）に最初のリクエストを投げる**
2. **サーバーは「認証必要だよ」と `WWW-Authenticate` ヘッダーで返す**（リソースメタデータの URL 付き）
3. **Claude Code が `/.well-known/oauth-protected-resource` を読んで、AuthKit の URL を発見する**
4. **Claude Code がブラウザを自動で起動して、AuthKit のログイン画面に飛ばす**
5. **ユーザーはブラウザでログインボタンをクリックするだけ**
6. **リダイレクトでアクセストークンが発行され、Claude Code のローカルストレージに自動保存**
7. **以降、Claude Code は保存したトークンを Bearer に付けて MCP を叩く**

ユーザーがやるのはブラウザでボタンをクリックするだけ。トークンのコピペも、設定ファイル編集も不要。これが MCP の理想体験だ。

## 実装は本当に数十行で終わる

html-to-pptx で実際に動いているコードをベースに、最小構成を見せる。

### Step 1: AuthKit のセットアップ

```bash
npm i @workos-inc/authkit-nextjs
```

`.env.local` に環境変数を入れる：

```env
WORKOS_API_KEY=sk_live_xxx
WORKOS_CLIENT_ID=client_xxx
# 32文字以上のランダム文字列（openssl rand -base64 32 等で生成）
WORKOS_COOKIE_PASSWORD=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
WORKOS_AUTHKIT_DOMAIN=yourcompany.authkit.app
NEXT_PUBLIC_WORKOS_REDIRECT_URI=https://your-app.com/callback
```

### Step 2: コールバックルートを書く（これだけ）

`app/callback/route.js`:

```js
import { handleAuth } from '@workos-inc/authkit-nextjs';

export const GET = handleAuth({
  returnPathname: '/dashboard',
});
```

これでブラウザログインの折り返しは完成だ。1分。

### Step 3: MCP エンドポイントで Bearer JWT を検証

`/mcp` ルートで、Authorization ヘッダーから取り出した JWT を WorkOS の JWKS で検証する：

```js
import { createRemoteJWKSet, jwtVerify } from 'jose';

const jwks = createRemoteJWKSet(
  new URL(`https://${process.env.WORKOS_AUTHKIT_DOMAIN}/oauth2/jwks`)
);

async function verifyWorkOSToken(accessToken) {
  const issuerBase = `https://${process.env.WORKOS_AUTHKIT_DOMAIN}`;
  const { payload } = await jwtVerify(accessToken, jwks, {
    issuer: [issuerBase, `${issuerBase}/`],
    // 注: audience チェックはスキップ（後述）
  });
  return payload;
}
```

検証 OK なら、`payload.sub` がユーザー ID だ。あとは自分の DB で `sub` をユーザーに紐付ければ、認証付き MCP の完成だ。

### Step 4: Protected Resource Metadata を返す

これが Dynamic Client Registration を成立させる鍵だ。  
`app/.well-known/oauth-protected-resource/route.js`:

```js
import { NextResponse } from 'next/server';

export async function GET(request) {
  const origin = new URL(request.url).origin;
  return NextResponse.json({
    resource: `${origin}/mcp`,
    authorization_servers: [`https://${process.env.WORKOS_AUTHKIT_DOMAIN}`],
    bearer_methods_supported: ['header'],
    scopes_supported: ['openid', 'profile', 'email', 'offline_access'],
    resource_name: 'My MCP Server',
  });
}
```

ここまで書けば、Claude Code からの自動ログインが動く。全部で 50 行いかないはずだ。

## ハマりポイント（これ大事）

理屈は綺麗だが、実装中に2回詰まった。同じ穴に落ちないでほしいので共有する。

### ハマりポイント1: audience の罠

JWT を検証するとき、普通は `audience: WORKOS_CLIENT_ID` を指定する。でも MCP クライアントが発行する JWT の audience は、あなたのアプリの CLIENT_ID ではない。

なぜか。Dynamic Client Registration では、Claude Code が自分用に新しい `client_id` を動的に発行するからだ。発行された JWT の audience は「その動的に作られた client_id」になっている。あなたのアプリの CLIENT_ID ではマッチしないので、必ず失敗する。

**回避策: audience チェックをスキップする。** issuer + JWKS 署名検証で十分だ。html-to-pptx の実装でも `skipAudience: true` フラグを入れている。

### ハマりポイント2: issuer 末尾スラッシュ問題

WorkOS が発行する JWT の `iss` クレームは、設定によって末尾スラッシュが付いたり付かなかったりする。`jwtVerify` の `issuer` オプションは厳密一致なので、片方だけ書くとランダムに失敗する地獄が始まる。

```js
issuer: [issuerBase, `${issuerBase}/`]  // 両方を許可
```

これ、ドキュメントには書いていないので踏まないと気づかない。

## まとめ：MCP 化のハードルは認証じゃなくなった

ちょっと前まで、個人開発アプリの MCP 化は「やりたいけど認証が重すぎて止まる」案件だった。

WorkOS が出てきて、その壁は実質消えたと思っている。

- セットアップ30分
- コードは50行未満
- 月間100万MAUまで無料
- Claude Code からの自動ログイン → トークン保存まで全部勝手にやってくれる

「MCP 化は SaaS の仕事」という時代は終わりつつある。先週末に作ったあの小さなアプリも、この週末に MCP 化できる。

WorkOS AuthKit は、個人開発者が MCP 認証を実装するうえで現時点で最良の選択肢だ。

## 参考リンク

- [WorkOS AuthKit ドキュメント](https://workos.com/docs/authkit)
- [Model Context Protocol（MCP 公式）](https://modelcontextprotocol.io/)
- [RFC 7591: OAuth 2.0 Dynamic Client Registration Protocol](https://datatracker.ietf.org/doc/html/rfc7591)
- [元ツイート（@taiyo_ai_gakuse）](https://x.com/taiyo_ai_gakuse/status/2048608961428087111)
