---
title: "HubSpot + LINE でリードを統合管理する — LIFF でアンケート回答者と LINE 友だちを紐づける"
date: 2026-06-04
lastmod: 2026-06-04
slug: "hubspot-line-lead-linking"
draft: false
description: "LINE 友だちと HubSpot リードを LIFF で紐づける実装ガイド。LIFF SDK で取得した userId をフォームの hidden フィールドに同送し、追加サーバーなしで名寄せ。LINE Login チャネル作成・LIFF Server API 自動化・CMS モジュール実装まで解説。"
source_url: "https://gist.github.com/hdknr/f88d85a752b3e9892d5c98a283209bec"
categories: ["Web開発"]
tags: ["line", "liff", "HubSpot", "javascript", "crm"]
---

LINE 公式アカウントで集客し、HubSpot でリード管理する——この組み合わせを使っている企業は多いはずです。しかし両者のユーザーデータは放っておくと分断されたままです。本記事では、**LINE で配布したアンケート LP の回答者（HubSpot リード）と、LINE 友だち（userId）を自動で紐づける仕組み**を、追加サーバーなし・HubSpot ネイティブ機能 + LIFF だけで構築する方法を解説します。

## 課題: LINE 友だちとリードは「別人」のまま

LINE 公式アカウントの友だちは LINE 上の `userId` でしか識別できず、HubSpot のコンタクトはメールアドレスをキーに管理されます。アンケート LP の URL を LINE で配って回答を集めても、そのままでは

- 「この回答者は LINE のどの友だちなのか」が分からない
- 「友だちのうち誰が回答済み/未回答か」のセグメントが作れない
- HubSpot のリスト起点で LINE Push 配信ができない

という状態になります。紐づけの鍵は、**フォーム送信時に LINE の userId を一緒に HubSpot へ渡すこと**です。

## 方式比較

userId をフォームに同乗させる方法は主に 3 つあります。

| 方式 | 仕組み | 配信方法 | 確実性 |
|---|---|---|---|
| **① LIFF（推奨）** | LP を LIFF アプリとして開き、SDK で userId を取得 → hidden フィールドで同送 | ブロードキャスト可（全員同じ URL） | 高 |
| ② パーソナライズ URL | ユーザーごとに `?t=<トークン>` 付き URL を Push 送信。トークン↔userId の対応表をサーバーで保持 | Push のみ（個別配信・通数コスト増） | 中（URL 転送リスク） |
| ③ LINE Login | LP に「LINE でログイン」ボタンを設置 | 自由 | 高（ただし回答前に同意画面が挟まり離脱要因） |

「全員に同じ URL をブロードキャストで配れて、ユーザー操作ゼロで userId が付いてくる」のは LIFF だけです。アンケート用途なら実務上ほぼ一択と言えます。

### なぜ liff.line.me 経由だと userId が取れるのか

1. ユーザーが `https://liff.line.me/{liffId}` をタップする
2. LINE アプリが「LIFF アプリだ」と認識し、LIFF ブラウザでエンドポイント URL を開く
3. このとき LINE アプリ内のログインセッションからアクセストークンをページに自動で引き渡す
4. `liff.init()` がそれを受け取り、`liff.getProfile()` で userId が取得できる

つまり liff.line.me は「LINE が持つ本人情報を、Web ページ側に**ノータップ・無摩擦で**引き渡す入り口」です。LP の URL を直接配った場合は `liff.login()` のリダイレクト（初回は同意画面）が必要になり、回答率を下げる要因になります。

## アーキテクチャ

LP もフォームも HubSpot ネイティブで作り、CMS テーマ側のモジュールで LIFF SDK を組み込みます。中継サーバー（Lambda 等）は不要です。

![LINE 配信から liff.line.me を経由して HubSpot LP が LIFF ブラウザで開かれ、LIFF SDK が取得した userId をフォームの hidden フィールドに注入し、送信後に HubSpot コンタクトへ email で自動名寄せされる流れを示したアーキテクチャ図](/blogs/images/hubspot-line-lead-linking-architecture.png)

HubSpot フォームは送信時にメールアドレスで既存コンタクトと自動マージされるため、以後は「LINE 友だち ⇔ リード」が 1 レコードに統合されます。

## 実装手順

### 1. LINE Login チャネルを作成する（コンソール・1 回だけ）

LIFF アプリは **LINE Login チャネル**にしか作れません（Messaging API チャネルへの LIFF 追加は廃止済み）。チャネル作成用の API は提供されておらず、コンソールでの手作業になります。

1. [LINE Developers コンソール](https://developers.line.biz/console/)で、**既存の Messaging API チャネルと同じプロバイダー**を選択
2. 「新規チャネル作成」→「LINE ログイン」、アプリタイプは「ウェブアプリ」
3. 作成後、チャネルステータスを「開発中」→「**公開済み**」に切り替える

> **⚠️ 最重要の注意点が 2 つ:**
> 1. **必ず同一プロバイダー配下に作成すること。** プロバイダーが異なると Messaging API 側と userId が一致せず、紐づけが成立しません。プロバイダー間の移動は不可なので作り直しになります。
> 2. **チャネルを「公開済み」にすること。** 開発中のままだと、チャネルの管理者/テスター以外は LIFF アプリを開けません。

「チャネル基本設定」のチャネル ID とチャネルシークレットを控えておきます。

### 2. LIFF アプリを作成する（API で自動化可能）

チャネル作成後は [LIFF Server API](https://developers.line.biz/ja/reference/liff-server/) ですべて自動化できます。

```bash
# Login チャネルのアクセストークン発行(client_credentials)
curl -s -X POST https://api.line.me/oauth2/v3/token \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  -d 'grant_type=client_credentials' \
  -d 'client_id={LoginチャネルID}' \
  -d 'client_secret={Loginチャネルシークレット}'

# LIFF アプリ作成 → liffId が返る
curl -s -X POST https://api.line.me/liff/v1/apps \
  -H "Authorization: Bearer {上のトークン}" \
  -H 'Content-Type: application/json' \
  -d '{
    "view": { "type": "full", "url": "https://<HubSpot LPのURL>" },
    "scope": ["profile", "openid"],
    "botPrompt": "normal"
  }'
```

返ってきた `liffId` で配布 URL `https://liff.line.me/{liffId}` が確定します。LP の URL 変更は `PUT /liff/v1/apps/{liffId}` で追従できるので、ステージング → 本番の切替も自動化できます。

`botPrompt: "normal"` を指定すると、未フォローのユーザーが LIFF を開いた際に友だち追加を促せます（Login チャネルと公式アカウントの[リンク設定](https://developers.line.biz/ja/docs/line-login/link-a-bot/)が別途必要）。

### 3. HubSpot 側の準備

- コンタクトのカスタムプロパティ **`line_user_id`**（単一行テキスト）を作成
- アンケートフォームに同プロパティのフィールドを追加し「**非表示（hidden）**」に設定
- **email は必須**にする（名寄せキーがなくなるため）

### 4. LP モジュールの実装（CMS テーマ）

HubSpot フォームの埋め込みは非同期なので、`onFormReady` コールバックで userId を注入します。

```html
<script src="https://static.line-scdn.net/liff/edge/2/sdk.js"></script>
<div id="survey-form"></div>
<script>
hbspt.forms.create({
  portalId: "XXXXX",
  formId: "XXXXX",
  target: "#survey-form",
  onFormReady: function(form) {
    // 旧 (jQuery 版) フォームでは form が jQuery コレクションで渡るため型を吸収する
    var formEl = form && form.jquery ? form[0] : form;
    liff.init({ liffId: "XXXX-XXXXXXXX" }).then(function() {
      if (!liff.isLoggedIn()) return; // LINE 外ブラウザ → 紐づけなしで回答は受ける
      liff.getProfile().then(function(profile) {
        var input = formEl.querySelector('input[name="line_user_id"]');
        input.value = profile.userId;
        input.dispatchEvent(new Event('input', { bubbles: true }));
      });
    });
  }
});
</script>
```

ポイントは 3 つ:

- `onFormReady` の引数は **HubSpot フォームの版によって型が異なる**。旧来の jQuery 依存版では jQuery コレクション、新しい jQuery 非依存版では DOM 要素が渡るため、上記のように型を吸収してから `querySelector` する
- `dispatchEvent(new Event('input', ...))` を忘れると HubSpot フォームが値の変更を認識しないことがある
- `liff.isLoggedIn()` が false（LINE 外ブラウザで開かれた場合）は **userId なしのまま回答を受ける**。リードは取れるが紐づけはされない、という graceful degradation にしておく

テーマのモジュールとして実装する場合は、`liffId` / `formId` をモジュールフィールドにしておくと、アンケートを増やすたびにコードを触らずに済みます。

### 5. 設定の順序 — 循環依存に注意

「LIFF 作成には LP の URL が必要」「LP のモジュールには liffId が必要」という相互依存があるため、次の順で進めます。

1. プロパティ + フォーム作成
2. LP を作成・公開（liffId は空のまま → 普通のフォームとして動く）
3. 手順 2 の URL で LIFF アプリ作成 → liffId 取得
4. LP のモジュール設定に liffId を入力して再公開
5. `https://liff.line.me/{liffId}` から E2E 確認

モジュール側を「liffId が空なら LIFF 初期化をスキップ」と実装しておくのは、この手順 2 の状態を成立させるためです。

## HubSpot ページ側の細かい設定

| 設定 | 内容 |
|---|---|
| 公開 URL | 接続済みドメインで公開し、スラッグを確定（LIFF エンドポイントになるため後から変えない） |
| 検索エンジン | 「インデックスさせない」を推奨（LINE 限定配布のため）。sitemap からも除外 |
| Cookie 同意バナー | LIFF ブラウザ内でも表示される。回答の妨げになる場合は調整 |
| 流入計測 | `https://liff.line.me/{liffId}?utm_source=line&utm_medium=broadcast` のようにクエリを付けると LIFF がエンドポイント URL に引き継ぐため、UTM 計測がそのまま効く（[LIFF アプリを開く](https://developers.line.biz/ja/docs/liff/opening-liff-app/)の 2 次リダイレクト仕様） |

## 運用: アンケート LP を追加するときの作業

2 本目以降の LP を追加する際は、初回構築時の資産の大半をそのまま再利用できます。

| 資産 | 再利用できる理由 |
|---|---|
| LINE Login チャネル | チャネル 1 つに複数の LIFF アプリを登録できる |
| `line_user_id` カスタムプロパティ | コンタクト共通のプロパティなので 1 回作れば終わり |
| CMS テーマのモジュール | `liffId` / `formId` をモジュールフィールドにしてあればコード変更ゼロ |

LP 追加ごとの作業は「実装手順」の縮小版になります。

1. フォーム作成（`line_user_id` hidden + email 必須）
2. LP 作成・公開（モジュールの `liffId` は空のまま → URL を確定）
3. `POST /liff/v1/apps` に手順 2 の URL を渡して新しい `liffId` を取得
4. モジュールに `liffId` / `formId` を設定して再公開
5. `https://liff.line.me/{liffId}` から E2E 確認

手動が必須なのは HubSpot 上のフォーム・LP 作成くらいで、手順 3 はトークン発行 → アプリ作成のスクリプトを 1 本用意しておけばワンコマンド化できます。

### 共有 LIFF アプリ方式 — LIFF を LP ごとに増やさない選択肢

LIFF URL には追加のパスやクエリを付けられ、[2 次リダイレクト先 URL](https://developers.line.biz/ja/docs/liff/opening-liff-app/) は「エンドポイント URL のドメイン + エンドポイント URL のパス/クエリ + LIFF URL の追加情報」を連結した URL になります。たとえばエンドポイント URL が `https://example.com` なら、`https://liff.line.me/{liffId}/lp-2/` は `https://example.com/lp-2/` を開きます。

これを使うと、エンドポイント URL を LP 共通のベースパスにした **共有 LIFF アプリを 1 つ**だけ作り、LP 追加時は手順 3〜4 を丸ごと省略して「フォーム + LP を作って配布 URL のパスを変えるだけ」にできます。

ただしトレードオフもあります。

- **エンドポイント URL のページにも LIFF SDK + `liff.init()` が必要** — 追加パスは一旦 `liff.state` クエリとしてエンドポイント URL に渡り、`liff.init()` が 2 次リダイレクトを実行する仕組みのため、エンドポイント直下のページが LIFF 初期化を行わないと LP まで到達しない
- `scope` や `botPrompt` などの設定が全 LP で共通になる
- LIFF 単位での出し分け・差し替え（特定アンケートだけ URL を無効化する等）ができなくなる

アンケートを頻繁に増やす運用なら共有 LIFF 方式、LP ごとに挙動を変えたいなら「1 LP = 1 LIFF」が向いています。

## この方式の制約

| 項目 | 内容 |
|---|---|
| **トークン検証なし** | userId はクライアント JS から hidden に入るだけなので、理論上は改ざん可能。アンケート用途なら通常許容範囲。厳密化するなら、送信後にサーバーサイド（ワークフロー + 外部 API 等）で LINE Profile API による実在チェックを追加するか、`liff.getIDToken()` を送って LINE の verify API で検証する構成に発展させる |
| **LINE 外で開かれた場合** | userId が空のまま送信され、紐づけ不可。トーク/リッチメニューからの導線なら実質問題なし |

まず「LIFF + クライアント直送」のシンプル構成で運用を始め、必要になったら検証レイヤーを足す、という段階導入が現実的です。

## 紐づけ後にできること

`line_user_id` がコンタクトに入ると、HubSpot を起点とした LINE 施策が一気に開きます。

- **セグメント作成** — 「友だちだが未回答」「回答済み」「特定の回答をした人」などのリスト
- **HubSpot 起点の Push 配信** — リストから userId を取り出して Messaging API の Push/マルチキャストで個別配信（ブロードキャストからの脱却）
- **スコアリング・ワークフロー連携** — LINE 経由の行動を HubSpot のリードスコアやナーチャリングフローに組み込む

## まとめ

- LINE 友だちと HubSpot リードの紐づけは、**LIFF で userId をフォームの hidden フィールドに同乗させる**のが最小構成
- LP・フォームとも HubSpot ネイティブで完結し、**追加サーバー不要**
- 手動作業は LINE Login チャネル作成の 1 回だけ。LIFF の作成・管理は API で自動化できる
- LP の追加はフォーム + LP の作成だけ。LIFF は API でワンコマンド追加するか、共有 LIFF + パス連結で省略できる
- **同一プロバイダー**と**チャネル公開**の 2 点だけは絶対に外さないこと

## 参考リンク

- [LIFF ドキュメント | LINE Developers](https://developers.line.biz/ja/docs/liff/)
- [LIFF Server API リファレンス | LINE Developers](https://developers.line.biz/ja/reference/liff-server/)
- [LINE ログインを始めよう | LINE Developers](https://developers.line.biz/ja/docs/line-login/getting-started/)
- [友だち追加オプション（ボットリンク） | LINE Developers](https://developers.line.biz/ja/docs/line-login/link-a-bot/)
- [HubSpot Forms API](https://developers.hubspot.com/docs/guides/api/marketing/forms)
