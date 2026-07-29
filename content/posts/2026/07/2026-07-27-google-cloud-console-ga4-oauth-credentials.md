---
title: "GA4・Search Console API 認証設定ガイド — refresh_token が 7 日で失効する罠"
date: 2026-07-27
lastmod: 2026-07-27
slug: "google-cloud-console-ga4-oauth-credentials"
draft: false
description: "GA4 と Search Console の API は API キーでは呼べず OAuth 必須。Google Cloud Console でのプロジェクト選択・API 有効化・OAuth 同意画面（Audience）設定・API キー制限までの手順と、refresh_token が 7 日で失効する原因、org_internal エラーの対処をまとめました。"
categories: ["クラウド/インフラ"]
tags: ["GA4", "Google Search Console", "OAuth", "gcp", "refresh_token", "security"]
---

GA4 / Search Console / PageSpeed Insights を**プログラムから叩きたい**とき、
最初にぶつかるのが「で、Google Cloud Console のどの画面で何を発行すればいいの？」という壁です。

実際にサイト分析の自動化を組んで運用に載せるまでに踏んだ地雷を、
**Console 上の操作**という一点に絞って 1 本にまとめます。
特に **`refresh_token` が 7 日で失効する**問題と、
**`org_internal`（組織内のユーザーのみが利用できます）でブロックされる**問題は、
知らないと原因にたどり着くのがかなり難しい部類です。

---

## まず結論: 「API キー」を使うのは PageSpeed だけ

一番大きな誤解がここです。Google の認証情報には **3 種類**あり、**呼ぶ API によって使い分けます**。

| 発行するもの | Console の画面 | 使える API | いくつ必要か |
| --- | --- | --- | --- |
| **API キー** (`AIza...`) | 認証情報 > API キー | **PageSpeed Insights だけ** | 1 本を使い回せる |
| **OAuth クライアント**<br>(`client_id` / `client_secret`) | 認証情報 > OAuth クライアント ID | GA4 Data / GA4 Admin / Search Console | **プロジェクトに 1 つ**（全部で共用） |
| **`refresh_token`** | Console では発行しない<br>（自分のアプリのブラウザ認可で取得） | 同上 | **スコープ（API 種別）ごとに 1 つ** |

つまり：

- **GA4 と Search Console は API キーでは呼べません。** OAuth 必須です。
  「GA4 の API キーを発行しよう」と Console を探し回っても、**そんなものは存在しません**。
  ユーザー個人のデータを読む API なので、「誰の権限で読むのか」を示す OAuth が要ります。
- **PageSpeed Insights（以下 PSI）は逆に OAuth 不要**です。公開 URL を外から測るだけなので、
  誰の権限も要りません。API キーは**割り当て（quota）を増やすため**だけに使います。

この非対称性が、Console のどの画面に行けばいいか分からなくなる最大の原因です。
全体の対応関係を図にすると次のようになります。

![GA4 / Search Console / PageSpeed Insights の認証情報の対応関係を示した図](/blogs/images/google-cloud-console-ga4-oauth-credentials.png)

GA4 Data API・GA4 Admin API・Search Console API の 3 つは **OAuth クライアント 1 つを共用**し、
そこからスコープごとに `refresh_token` を取得します。
PSI だけは API キー 1 本で済み、トークンは要りません。
そして OAuth 同意画面（対象 / Audience）の設定はプロジェクトに 1 回だけ、全体に効きます。

### プロジェクトは 1 つにまとめてよい

API ごとにプロジェクトを分ける必要はありません。むしろ分けると
「OAuth クライアントを作ったプロジェクトと、API を有効化したプロジェクトが違う」
という **403 の定番事故**を踏みます。1 つに集約するのが素直です。

---

## 1. プロジェクトを選ぶ（すべての作業の前に）

Console の操作は**すべて同じプロジェクトを選んだ状態**で行います。
ここを外すと「有効にしたはずなのに 403」という最も多い失敗になります。

1. [Google Cloud Console](https://console.cloud.google.com/) を開く
2. 画面上部の**プロジェクトセレクタ**が対象プロジェクトになっているか確認する
3. 右上アバターの**メールアドレス**が、
   対象の GA4 プロパティ / Search Console サイトを**管理しているアカウントと同じ**か確認する

3 番は地味ですが重要です。複数の Google アカウントにログインしていると、
URL の `authuser=` の違いだけで別人として操作していることがあります。
Cloud Console / Analytics / Search Console の**3 つとも右上のアドレスを見比べてください**。

> **どのプロジェクトか分からなくなったら**
> 403 のエラーメッセージに含まれる `project 123456789012` のような数字がプロジェクト番号です。
> エラー文中に出てくる URL をそのまま開けば、正しいプロジェクトの有効化画面に着きます。

---

## 2. API を有効化する

**API とサービス > ライブラリ**で、使う API を有効化します。
下表の直リンクを**プロジェクトを選んだ状態で**開いて「**有効にする**」を押すだけです。
ここで認証情報を作る必要はありません（作成は次の手順）。

| API | 何に使うか | 直リンク |
| --- | --- | --- |
| **Google Analytics Data API** | GA4 のレポート取得（`runReport`） | [ライブラリ](https://console.cloud.google.com/apis/library/analyticsdata.googleapis.com) |
| **Google Analytics Admin API** | プロパティ ID の一覧取得・自動解決 | [ライブラリ](https://console.cloud.google.com/apis/library/analyticsadmin.googleapis.com) |
| **Google Search Console API** | 検索パフォーマンス（Search Analytics）の取得 | [ライブラリ](https://console.cloud.google.com/apis/library/searchconsole.googleapis.com) |
| **PageSpeed Insights API** | Lighthouse スコア / CrUX 実測値の取得 | [ライブラリ](https://console.cloud.google.com/apis/library/pagespeedonline.googleapis.com) |

注意点が 3 つあります。

- **旧 UA 用の API と混同しない。** GA4 は *Google Analytics **Data** API* です。
  *Analytics Reporting API*（v4）は Universal Analytics 用で、GA4 では使えません。
- **Analytics Admin API は必須ではないが強く推奨。**
  プロパティ ID を手入力せずに一覧から選べるようになるので、
  ID の取り違えによる 403 を未然に潰せます。
- **反映まで数分かかることがある。**
  有効化直後に `... API has not been used in project ... or it is disabled`（403）が出たら、
  設定ミスではなく単に反映待ちのことがあります。少し待って再実行してください。

有効化済みかどうかは
[**API とサービス > 有効な API とサービス**](https://console.cloud.google.com/apis/dashboard) で一覧できます。

---

## 3. OAuth 認証情報を発行する（GA4 / Search Console）

**プロジェクトに 1 回だけ**でよく、GA4 と Search Console で共用できます。

### 3-1. 同意画面の「対象（Audience）」を設定して**公開する**

場所: <https://console.cloud.google.com/auth/audience>
（未設定なら <https://console.cloud.google.com/auth/overview> の「始める」ウィザードから）

> 新しい Console（Google Auth Platform）では、旧「OAuth 同意画面」の設定が
> **「対象（Audience）」** ページに移動しています。
> 「ユーザーの種類（User type）」と「公開ステータス」はこのページ内の項目です。
> 古い記事の画面と違って見えるのはこのためです。

選択肢は「内部（Internal）」と「外部（External）」の 2 つです。

#### 「内部（Internal）」が選べるなら最も簡単

テストユーザー不要・警告画面なし・`refresh_token` は長期有効。いいことずくめですが、**条件が 2 つ**あります。

1. Cloud プロジェクトが **Google Cloud 組織（Google Workspace または Cloud Identity）の配下**にあること
2. **認可に使う Google アカウントも、その組織のメンバーであること** ← ここが抜けがち

**2 番目が最大の落とし穴**です。プロジェクトが組織配下にあっても、
対象の GA4 プロパティや Search Console サイトを管理しているのが**組織外のアカウント**だと通りません。
担当者の個人アカウントや、クライアント側のアカウントが典型です。
この場合、認可の瞬間にこう出て止まります。

```text
アクセスをブロック: <アプリ名> は組織内のユーザーのみが利用できます
```

このときのエラーコードは **`403 org_internal`** です
（英語版の文言は "This client is restricted to users within its organization."）。
画面文言は Google 側で変わることがあるので、**エラーコードで判断する**のが確実です。

**まず疑うべきはアカウントの選び間違いです。** 複数ログインしていると認可画面で違うアカウントを
選んでいることがあり、プロパティ管理者が組織内アカウントなら選び直すだけで通ります。
本当に組織外のアカウントが管理している場合は Internal では原理的に通らないので、
「外部（External）」に切り替えます。

#### 「外部（External）」の場合 —— **必ず「公開」まで行う**

対象プロパティを管理しているのが個人 Google アカウント（Workspace ユーザーでない）なら、
External 一択です。このとき、**絶対に忘れてはいけないのが「公開（Publish app）」**です。

> **⚠️ External + 「テスト中」だと `refresh_token` が 7 日で失効する**
>
> 公開ステータスが「**テスト中（Testing）**」のまま発行された `refresh_token` は、
> **7 日で無効になります**（Google の仕様）。
> `refresh_token` を保存して定期実行する作りだと、**毎週きっかり止まる**バッチができあがります。
> しかも 7 日後なので、動作確認した当日には絶対に気づけません。
>
> Audience ページで、次の 2 つを行ってください。
>
> 1. **テストユーザーに自分を追加** — 「Test users」に認可で使う Google アカウントを追加する
>    （無いと認可時に `access_denied`）
> 2. **アプリを公開（Publish app）** — 公開ステータスを **「本番（In production）」** にする
>
> 2 番で 7 日失効が解消され、`refresh_token` が長期有効になります。
> **公開はプロジェクト単位**なので、一度公開すれば GA4・Search Console 両方のトークンに効きます。

#### 「Google で確認されていません」の警告は通過してよい

要求したスコープが Google の分類で「**機密（sensitive）**」に当たると、
External で本番公開しても、未審査のうちは認可時にこの警告が出ます。
自分が使うスコープがどの分類かは Console の「**データアクセス**」画面に表示されます
（Google は個別スコープの機密判定を一覧では公開しておらず、分類は変更されることがあります。
`webmasters.readonly` のように後から非機密へ再分類された例もあります）。

**「詳細」→「（アプリ名）に移動（安全ではない）」** で進んで問題ありません。
Google の審査（verification）が必要なのは、不特定多数に配布する一般公開アプリの場合です。
ただし未審査アプリには「**警告画面を経て許可したユーザーが累計 100 人まで**」という上限があります。
自分ひとりや少人数の運用なら、実質的に問題になりません。

### 3-2. 「デスクトップ アプリ」型の OAuth クライアントを作る

1. **API とサービス > 認証情報 > 認証情報を作成 > OAuth クライアント ID**
   （直リンク: <https://console.cloud.google.com/auth/clients>）
2. アプリケーションの種類: **デスクトップ アプリ**
3. 作成後、**JSON をダウンロード**（`client_secret_xxx.json`）
   —— これは「アプリの身分証」です。**リポジトリにコミットしないこと。**

**なぜ「デスクトップ アプリ」なのか**：手元で認可を完結させるツールでは、
Web アプリ型ではなくデスクトップ型を使います。
ローカルにワンタイムのループバックサーバーを立ててブラウザ認可する、いわゆる Installed App フローです。
Web アプリ型はリダイレクト URI の登録が必要で、ローカル実行には向きません。

覚えておくと得をする性質が 2 つあります。

- **OAuth クライアントはスコープに依存しない。**
  スコープを指定するのは実行時のコード側なので、
  **GA4 用に作ったクライアント JSON が Search Console でもそのまま使えます。**
- **`refresh_token` はスコープに紐づく。**
  なので、GA4 用と Search Console 用で**ブラウザ認可はそれぞれ 1 回ずつ**必要です。
  クライアントは共用、トークンは別、と覚えてください。

### 3-3. 認可は「プロパティを管理している本人のアカウント」で

OAuth ユーザー認可は、**認可した人の権限で API を叩く**方式です。
ブラウザ認可で使った Google アカウントが、対象プロパティを管理しているアカウントと
**同一でないと、後でレポート取得が `403 PERMISSION_DENIED` になります**。

必要な権限は次のとおりです。

- **GA4**: 対象プロパティの「閲覧者」以上
- **Search Console**: 対象サイトが
  [Search Console](https://search.google.com/search-console) に**登録・所有権確認済み**で、
  そのアカウントが「制限付き」以上の権限を持つこと

### 補足: なぜ「サービスアカウント」ではないのか

自動化と聞くとサービスアカウント（`...@....iam.gserviceaccount.com`）を思い浮かべます。
しかし**組織ポリシーで外部ドメインのメンバー追加が禁止されていると、
サービスアカウントを GA4 プロパティに招待できずに詰みます。**

Google Workspace 環境ではこの制限がデフォルトで有効なことがよくあり、
その場合は**「すでにプロパティを閲覧できる本人として OAuth 認可する」**方式を選ぶのが現実的です。
Search Console も同様です。

---

## 4. API キーを発行する（PageSpeed Insights 専用）

PSI は API キーなしでも呼べますが、**割り当てが極端に小さく、実運用ではすぐ 429 になります**。
1 本発行しておきましょう。

1. **PageSpeed Insights API を有効化済み**であることを確認（手順 2）
2. **API とサービス > 認証情報 > 認証情報を作成 > API キー**
   （直リンク: <https://console.cloud.google.com/apis/credentials>）
3. 作成したキーを**必ず制限する**（キー名の編集画面で）
    - **API の制限**: 「キーを制限」→ **PageSpeed Insights API** のみ選択
    - **アプリケーションの制限**: 呼び出し元の IP が固定できない構成（Lambda 等）なら「なし」でよい。
      API 制限だけかけておけば、漏えいしても影響は PSI の quota 消費に限られる

キーありの既定 quota は、一般に **25,000 リクエスト/日**程度とされています。
分あたりのレートは公式ドキュメントに明記がなく、情報源によって食い違うので、
正確な値は Cloud Console の
「**有効な API とサービス > PageSpeed Insights API > 割り当て**」で確認してください。
数十サイト規模の定期監査なら十分すぎる量です。

**API キーの機密度は OAuth クライアントより低い**という点は運用設計で効いてきます。
PSI 専用に制限したキーは、漏えいしても他人のデータを読まれる心配がなく、
被害は quota 消費に限られます。Secrets Manager のような重い保管庫は不要で、
CI の変数程度の扱いでも許容できます。

---

## 5. 「今どうなっているか」を確認する画面

設定が積み重なると、どこを見ればいいか分からなくなります。確認先の一覧です。

| 知りたいこと | 確認先 |
| --- | --- |
| どの API が有効か | [API とサービス > 有効な API とサービス](https://console.cloud.google.com/apis/dashboard) |
| OAuth クライアント / API キーの一覧 | [認証情報](https://console.cloud.google.com/apis/credentials) |
| 同意画面の対象と**公開ステータス** | [対象（Audience）](https://console.cloud.google.com/auth/audience) |
| API の呼び出し回数 / エラー率 / quota | [有効な API とサービス](https://console.cloud.google.com/apis/dashboard) → 対象 API |
| 認可済みアプリの取り消し（アカウント側） | [Google アカウント > アプリ連携](https://myaccount.google.com/permissions) |

---

## トラブルシュート早見表

### Console 設定が原因のもの

| 症状 | 原因と対処 |
| --- | --- |
| `... API has not been used in project ... or it is disabled`（403） | 対象 API が未有効、または**別プロジェクトで**有効化した。エラー文中の URL を開いて有効化する。有効化直後なら数分待って再実行 |
| 有効にしたはずなのに 403 が続く | プロジェクトセレクタが、OAuth クライアントを作ったプロジェクトと違う。エラー内のプロジェクト番号で照合する |
| プロパティ ID が一覧で取れない | Google Analytics **Admin** API が未有効 |

### 認可時（ブラウザで許可する場面）に起きるもの

| 症状 | 原因と対処 |
| --- | --- |
| `access_denied`（アクセスがブロックされました） | 同意画面が External + テスト中で、Test users に入っていない。**アプリを公開（本番）にする**のが本筋（`access_denied` と 7 日失効を同時に解消）。Test users 追加は応急処置で、**7 日失効が残る**ので非推奨 |
| `アクセスをブロック: <アプリ名> は組織内でのみ利用可能です`（`org_internal`） | 同意画面が**「内部」**で、認可アカウントが**組織の外**。まず**アカウントの選び間違い**を疑う（`authuser=` を確認）。本当に組織外の管理者なら、**External に変更 → Test users 追加 → 公開（本番）**まで行う。**公開を省くと 7 日失効に化ける** |
| 数日後にトークンが失効する / 毎週バッチが止まる | External 同意画面が「テスト中」のまま（7 日失効）。「アプリを公開」で本番にする |
| 「Google で確認されていません」警告 | 機密スコープ + 未審査なので**正常**。「詳細」→「（アプリ名）に移動」で通過 |
| ブラウザが認可画面を開かない | ツールが表示した認可 URL を手動でブラウザに貼る（WSL2 などで自動起動が効かないケース） |
| `refresh_token` が返ってこない | デスクトップ アプリ型では通常毎回返る。Web アプリ型や `access_type=offline` の Web サーバーフローでは 2 回目以降返らないことがある。[アプリ連携](https://myaccount.google.com/permissions) から当該アプリのアクセスを一度削除して再実行する（コード側で `prompt=consent` を付けるのも有効） |

### API 呼び出し時に起きるもの

| 症状 | 原因と対処 |
| --- | --- |
| `403 PERMISSION_DENIED` | 認可に使ったアカウントが、対象プロパティ / サイトの権限を持っていない |
| Search Console のレスポンスが空 | `siteUrl` が Search Console 登録文字列と**完全一致**していない |
| PageSpeed が `429` | API キー未設定、またはキーが実行環境に反映されていない |

> **Search Console のサイト指定**には 2 種類あります。
> **ドメイン プロパティ**（`sc-domain:example.com`）はサブドメインと http/https をまとめて計測、
> **URL プレフィックス プロパティ**（`https://example.com/`）はその URL 配下のみ。
> 両方登録されているなら、通常は**ドメイン プロパティ**を選ぶのが無難です。
> なお API 側から `sites.list` で登録済みの文字列を取得できるので、
> **手入力せず一覧から選ばせる**実装にすると事故が激減します。

---

## 運用に載せるときのチェックリスト

- [ ] Cloud プロジェクトを 1 つに決め、**すべての操作をそのプロジェクトで行った**
- [ ] 使う API を有効化した（GA4 は **Data API**。Admin API も入れておくと楽）
- [ ] 同意画面の対象を設定し、**External なら「本番」に公開した**（← 7 日失効の唯一の対策）
- [ ] 認可に使ったアカウント = **対象プロパティを管理しているアカウント**である
- [ ] OAuth クライアント（デスクトップ型）の JSON を取得し、**リポジトリに入れていない**
- [ ] PageSpeed を使うなら API キーを発行し、**PSI API のみに制限した**
- [ ] `refresh_token` の**鮮度監視**を入れた（失効は静かに起きるので、気づく仕組みが要る）

最後の 1 行が実は一番大事です。
`refresh_token` の失効は**エラーが出るまで誰も気づきません**。
「取得できた」で終わりにせず、**何日更新されていないかを監視する**ところまで作ってようやく運用です。

---

## まとめ

- **API キーを使うのは PageSpeed だけ。** GA4 / Search Console は OAuth 必須
- **OAuth クライアントは共用、`refresh_token` はスコープごと**
- **External の同意画面は「公開」まで行う。** テスト中のままだと **7 日で死ぬ**
- **`org_internal` はまずアカウントの選び間違いを疑う。** 本当に組織外なら External へ
- **プロジェクトの取り違えが 403 の最頻原因。** エラー文のプロジェクト番号で照合する
