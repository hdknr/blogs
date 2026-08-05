---
title: "GoogleビジネスプロフィールをAPIで管理する — 分割された8つのAPIと、v4に残る口コミ・投稿"
date: 2026-08-05
lastmod: 2026-08-05
slug: "google-business-profile-api"
draft: false
description: "Googleビジネスプロフィール（GBP）をAPIで管理する方法。旧 Google My Business API から分割された8つの API の役割分担、口コミ・投稿が残るレガシー v4、利用申請と 0/300 QPM の承認判定、Python 実装例、reportInsights からの移行対応表まで。"
source_url: "https://github.com/hdknr/blogs/issues/71#issuecomment-5185965831"
categories: ["Web開発"]
tags: ["Google Business Profile", "Google My Business API", "MEO", "ローカルビジネス", "python"]
---

Google ビジネスプロフィール（GBP）は、Google 検索や Google マップに表示される店舗情報を無料で管理できるサービスだ。住所・電話番号・営業時間を登録すると「渋谷 カフェ」のような検索でローカルパックに載る。店舗ビジネスにとっては、広告費をかけずに来店導線を確保できる基幹チャネルになっている。

問題は**運用が手作業だと破綻すること**にある。[STORES の解説記事](https://stores.fun/magazine/articles/google-business-profile-stores)も、GBP の課題として「営業時間や写真の更新を忘れがち」「口コミ返信の時間を確保できない」「チェーン展開では店舗ごとの更新が追いつかない」を挙げている。10店舗を超えたあたりから、管理画面をポチポチする運用は現実的でなくなる。

そこで API である。ただし GBP の API は、他の Google API と比べてかなり癖が強い。この記事ではその構造と、実際に何をどう叩くのかを整理する。先に結論だけ並べると次のようになる。

- API は1つではなく、用途ごとに **8つに分割**されている
- それでも**口コミ・投稿・メディアはレガシーの v4 にしかない**。新旧2系統の併用が前提
- 使い始めるには**利用申請と承認**が要る。承認済みかは**クォータが 0 QPM か 300 QPM か**で分かる
- **サンドボックス環境がない**。書き込みのテストは本番データに当たる

前提として Python 3.10 以上と `requests`、OAuth 2.0 の基礎知識を想定している。Place Actions（予約リンク）と Lodging（宿泊施設属性）は扱わない。

## Business Profile API は1つではない — 8つに分割された構成

かつて Google My Business API（v4.9、以下 **v4**）という単一の API がすべてを担っていたが、Google は 2021年に**用途ごとの分割**へ舵を切った。現在は機能領域ごとに独立したホスト名を持つ。

![Google ビジネスプロフィール API の構成図。左側に Account Management、Business Information、Performance、Verifications、Q&A、Place Actions、Notifications、Lodging という現行の分割APIが並び、右側にレガシーの Google My Business API v4.9 が口コミ・投稿・メディア・メニューを抱えている様子を示している](/blogs/images/google-business-profile-api-map.png)

現行の分割 API はおおむね次の役割分担になっている。

| API | ホスト名の接頭辞 | 主な守備範囲 |
| --- | --- | --- |
| Account Management | `mybusinessaccountmanagement` | アカウント、管理者、招待、ロケーション（＝店舗の API 上の呼称）の移管 |
| Business Information | `mybusinessbusinessinformation` | 店舗情報、営業時間、属性、カテゴリ、チェーン |
| Performance | `businessprofileperformance` | 表示回数、電話、経路リクエスト、検索キーワード |
| Verifications | `mybusinessverifications` | オーナー確認、Voice of Merchant 状態 |
| Q&A | `mybusinessqanda` | 質問と回答 |
| Place Actions | `mybusinessplaceactions` | 予約・注文などの行動リンク |
| Notifications | `mybusinessnotifications` | Pub/Sub 通知設定 |
| Lodging | `mybusinesslodging` | 宿泊施設向けの属性 |

ホスト名はいずれも `<接頭辞>.googleapis.com` の形になる。**Performance API だけが `mybusiness` ではなく `businessprofile` 始まり**で、ここは実装時に一度は踏む落とし穴だ。

もうひとつ紛らわしいのがバージョン表記で、ドキュメントの目次では Account Management が v1.1、Notifications と Lodging が v1.2 と書かれている。しかし**これは URL のパスに入るバージョンではない**。各 API の discovery document を引くと、いずれも `version: v1` を返す。

```bash
curl -s 'https://mybusinessaccountmanagement.googleapis.com/$discovery/rest?version=v1'
```

```json
{
  "version": "v1",
  "baseUrl": "https://mybusinessaccountmanagement.googleapis.com/"
}
```

つまりリクエストのパスは全 API で `/v1/...` に揃う。`/v1.1/` と書いて 404 に悩まないようにしたい。

### 口コミ・投稿はレガシー v4（Google My Business API）にしかない

分割で完全に置き換わったわけではない。**口コミ・投稿・メディア・メニューは、いまも `mybusiness.googleapis.com/v4` にしか存在しない**。

- `accounts.locations.reviews` — 口コミの取得、返信、返信削除
- `accounts.locations.localPosts` — イベントや特典の投稿
- `accounts.locations.media` — 写真・動画のアップロード
- `accounts.locations.updateFoodMenus` / `accounts.locations.updateServiceList` — メニューとサービスを更新するメソッド

つまり「MEO で最も効く機能」がレガシー側に固まっている。実装では、新旧2系統のクライアントを併用する前提で設計することになる。

## GBP API の利用申請と承認 — 最初の関門はコードではなく審査

GBP API は Cloud コンソールで有効化すれば使える、という類のものではない。**利用申請を出して承認されるまで、クォータが 0 QPM に固定されている**。

![Google ビジネスプロフィール API を使い始めるまでの6ステップのフロー図。申請条件の確認、Cloud プロジェクト作成、申請フォーム送信、クォータ0または300QPMによる承認判定、8つのAPIの有効化、OAuthクライアントIDでの疎通確認までを順に示している](/blogs/images/google-business-profile-api-access-flow.png)

### 申請条件

公式ドキュメントが挙げている必須要件は2つ。

1. **検証済みかつ 60日以上アクティブな GBP を管理していること**。自社のオフィスや本社のプロフィールでもよいし、代理で管理しているクライアントのものでもよい
2. **その事業を表すウェブサイトがあること**

審査をスムーズに通すため、GBP の情報（公式サイトを含む）を完全かつ最新の状態にしておくことが推奨されている。

申請は Cloud コンソールで作成したプロジェクトの **Project number** を控えたうえで、GBP API contact form から「Application for Basic API Access」を選んで送る。このとき**送信元メールアドレスが、その GBP のオーナーまたは管理者として登録されている必要がある**。

### 承認されたかは 0 QPM / 300 QPM で分かる

審査結果はメールで来るが、待たずに確認する方法がある。Cloud コンソールで Business Profile APIs のクォータを見ればよい。

- **0 QPM** — まだ承認されていない
- **300 QPM** — 承認済み

この 300 QPM が、そのまま本番のレート制限になる。全店舗を毎分同期するような設計は最初から成立しないので、差分同期や夜間バッチを前提に組む。

### 有効化するのは公式リストの8つ ＋ Performance API

承認後、Cloud コンソールで API を有効化する。ここで**「8つ」という数が2通り出てくる**ので整理しておきたい。先の表に挙げた分割 API も8つだが、**両者は同じ8つではない**。

公式ドキュメントの Basic setup が「有効化が必要」として列挙しているのはこの8つだ。

- **Google My Business API** — v4。口コミ・投稿・メディアを使うならこれが要る
- My Business Account Management API
- My Business Business Information API
- My Business Verifications API
- My Business Q&A API
- My Business Place Actions API
- My Business Notifications API
- My Business Lodging API

つまり公式リストの8つは「分割 API のうち Performance を除く7つ ＋ レガシー v4」という構成になっている。**Business Profile Performance API はこのリストに含まれていない**が、`businessprofileperformance.googleapis.com` という独立したサービスとして存在する。インサイトを取得するなら、この分も別途有効化しておくのが確実だ。

なお Google Workspace アカウントで使う場合、組織側で Google ビジネス プロフィールが無効になっていると `403 PERMISSION_DENIED` になる。これは API 側では解決できないので、管理コンソールを確認する。

## OAuth 認証（business.manage スコープ）と疎通確認

OAuth スコープは分割されておらず、**すべての API が同じ1本**を使う。

```text
https://www.googleapis.com/auth/business.manage
```

OAuth 2.0 クライアント ID を作ったら、まずアカウント一覧で疎通を確認するのが定石だ。ここが 200 で返れば、審査・有効化・認証がすべて通っている。

```bash
curl -s -H "Authorization: Bearer ${ACCESS_TOKEN}" \
  https://mybusinessaccountmanagement.googleapis.com/v1/accounts
```

Python から扱う場合は `google-auth` に認証を任せ、あとは素の HTTP で叩くのが分かりやすい。分割 API はそれぞれ discovery document を持つが、2系統を併用する都合上、薄いラッパーを自分で書いたほうが見通しがよくなる。

```bash
pip install requests google-auth google-auth-oauthlib
```

リフレッシュトークンは `google-auth-oauthlib` の `InstalledAppFlow` で一度だけ取得しておく。このとき `access_type="offline"` を指定しないとリフレッシュトークンが返らない。

```python
from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = ["https://www.googleapis.com/auth/business.manage"]

flow = InstalledAppFlow.from_client_secrets_file("client_secret.json", SCOPES)
creds = flow.run_local_server(port=0, access_type="offline", prompt="consent")
print(creds.refresh_token)   # 控えて環境変数などに保存する
```

以降のリクエストでは `AuthorizedSession` を使う。**アクセストークンは約1時間で失効する**ため、全店舗をページングで舐めるような長時間バッチでは、自前でヘッダに焼き付けると途中で 401 になる。`AuthorizedSession` はトークンを自動更新してくれる。

```python
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import AuthorizedSession

SCOPES = ["https://www.googleapis.com/auth/business.manage"]


def build_session(client_id: str, client_secret: str, refresh_token: str) -> AuthorizedSession:
    creds = Credentials(
        token=None,
        refresh_token=refresh_token,
        client_id=client_id,
        client_secret=client_secret,
        token_uri="https://oauth2.googleapis.com/token",
        scopes=SCOPES,
    )
    return AuthorizedSession(creds)
```

Google の OAuth 同意画面まわりの落とし穴（テスト状態だとリフレッシュトークンが7日で失効する等）は、[GA4・Search Console API の認証情報を設定する記事](/blogs/posts/2026/07/google-cloud-console-ga4-oauth-credentials/)にまとめてある。GBP API でもそのまま踏むので、認証で詰まったら先にそちらを確認してほしい。

## Python 実装例 — 店舗一覧・営業時間更新・口コミ返信・インサイト取得

### 1. アカウントと店舗の一覧を取る（初期同期）

店舗一覧は Account Management でアカウントを引いてから、Business Information で配下のロケーションを取る、という2段構えになる。`readMask` が**必須**な点に注意（省略すると 400 になる）。

```python
ACCOUNTS = "https://mybusinessaccountmanagement.googleapis.com/v1/accounts"
INFO = "https://mybusinessbusinessinformation.googleapis.com/v1"


def get_json(session, url: str, **kwargs) -> dict:
    """403 PERMISSION_DENIED や 429 を握り潰さないよう、必ず status を見る"""
    response = session.get(url, **kwargs)
    response.raise_for_status()
    return response.json()


def list_accounts(session) -> list[dict]:
    return get_json(session, ACCOUNTS).get("accounts", [])


def list_locations(session, account_name: str) -> list[dict]:
    """account_name は 'accounts/123456789' 形式"""
    locations, page_token = [], None
    while True:
        params = {
            "readMask": "name,title,storefrontAddress,phoneNumbers,regularHours,websiteUri",
            "pageSize": 100,          # 上限は 100。未指定だと 10 件しか返らない
        }
        if page_token:
            params["pageToken"] = page_token

        payload = get_json(session, f"{INFO}/{account_name}/locations", params=params)
        locations.extend(payload.get("locations", []))

        page_token = payload.get("nextPageToken")
        if not page_token:
            return locations
```

`raise_for_status()` を挟んでいるのには理由がある。素直に `.json().get("accounts", [])` と書くと、承認前の 0 QPM で弾かれても `403` の本文をパースして**空リストを返し、正常終了してしまう**。「店舗が0件だった」のか「そもそも権限がない」のかが区別できなくなるので、読み取り系こそ status を見る。

### 2. 営業時間を更新する

更新は `PATCH` で、**`updateMask` に変更するフィールドを明示する**。マスクに載せなかったフィールドは触られない。年末年始のような特別営業日は `regularHours` ではなく `specialHours` 側で表現する。

```python
def update_regular_hours(
    session, location_name: str, periods: list[dict], dry_run: bool = False
) -> dict:
    """location_name は 'locations/12345678901234567890' 形式"""
    params = {"updateMask": "regularHours"}
    if dry_run:
        params["validateOnly"] = "true"     # 本番データを変えずに検証だけ行う

    response = session.patch(
        f"{INFO}/{location_name}",
        params=params,
        json={"regularHours": {"periods": periods}},
    )
    response.raise_for_status()
    return response.json()


PERIODS = [
    {
        "openDay": day,
        "openTime": {"hours": 11, "minutes": 0},
        "closeDay": day,
        "closeTime": {"hours": 22, "minutes": 0},
    }
    for day in ["MONDAY", "TUESDAY", "WEDNESDAY", "THURSDAY", "FRIDAY"]
]

update_regular_hours(session, "locations/12345678901234567890", PERIODS, dry_run=True)
```

`locations.patch` は `validateOnly` に対応している数少ないメソッドのひとつだ。指定すると更新は行われず、エラーがあった場合だけ検証エラーが返る（問題がなければレスポンスは空になる）。

### 3. 口コミを取得して返信する（v4 Reviews API）

ここだけレガシー v4 を使う。パスが `accounts/*/locations/*` の**2階層**である点が、分割 API 側の `locations/*` と食い違うので混同しやすい。

```python
V4 = "https://mybusiness.googleapis.com/v4"


def list_reviews(session, account_id: str, location_id: str) -> list[dict]:
    """1ページあたり最大 50 件"""
    url = f"{V4}/accounts/{account_id}/locations/{location_id}/reviews"
    reviews, page_token = [], None
    while True:
        params = {"pageSize": 50, "orderBy": "updateTime desc"}
        if page_token:
            params["pageToken"] = page_token

        payload = get_json(session, url, params=params)
        reviews.extend(payload.get("reviews", []))

        page_token = payload.get("nextPageToken")
        if not page_token:
            return reviews


def reply_to_review(
    session, account_id: str, location_id: str, review_id: str, comment: str
) -> dict:
    """返信が無ければ作成、あれば上書きされる（PUT）"""
    url = f"{V4}/accounts/{account_id}/locations/{location_id}/reviews/{review_id}/reply"
    response = session.put(url, json={"comment": comment})
    response.raise_for_status()
    return response.json()
```

`reviews.list` のレスポンスには `averageRating` と `totalReviewCount` も含まれるので、店舗別の評価推移を貯めるだけならページングせず1回叩けば足りる。`orderBy` に指定できるのは `rating` / `rating desc` / `updateTime desc` の3つで、既定は `updateTime desc`。**この API はロケーションが検証済みでないと使えない**。

なお口コミ返信の自動生成を LLM に任せる構成は相性がよい。ただし返信は即座に公開される。ポリシー違反で却下されることもある（却下理由は v4 の Reviews API から確認できる）。下書き生成までを自動化し、公開は人間が承認する形が無難だ。ローカルビジネス側の運用に落とし込む話は[Google マップ × AI でローカルビジネスを回す記事](/blogs/posts/2026/05/google-map-ai-local-business/)でも触れている。

### 4. インサイトを取得する（Performance API・週次レポート向け）

表示回数やアクションは Performance API から日次時系列で取得する。日付は `year` / `month` / `day` をそれぞれ独立したクエリパラメータとして渡す、やや珍しい形式になっている。

```python
from datetime import date

PERF = "https://businessprofileperformance.googleapis.com/v1"


def daily_metric(session, location_id: str, metric: str, start: date, end: date) -> dict:
    params = {
        "dailyMetric": metric,
        "dailyRange.start_date.year": start.year,
        "dailyRange.start_date.month": start.month,
        "dailyRange.start_date.day": start.day,
        "dailyRange.end_date.year": end.year,
        "dailyRange.end_date.month": end.month,
        "dailyRange.end_date.day": end.day,
    }
    url = f"{PERF}/locations/{location_id}:getDailyMetricsTimeSeries"
    return get_json(session, url, params=params)


daily_metric(session, "12345678901234567890", "WEBSITE_CLICKS", date(2026, 7, 1), date(2026, 7, 31))
```

指標を複数まとめて取りたい場合は `locations.fetchMultiDailyMetricsTimeSeries` を使うと1リクエストで済む。300 QPM の制約下では、こちらを基本にしたほうがよい。

## reportInsights 廃止後の移行 — Performance API 指標対応表

旧 `accounts.locations.reportInsights` は 2023年3月30日に廃止済みで、Performance API への移行が必要になっている。指標名がそのまま対応しているわけではないので、対応表を置いておく。

| v4 の Metric | Performance API v1 での代替 |
| --- | --- |
| `VIEWS_MAPS` | `BUSINESS_IMPRESSIONS_DESKTOP_MAPS` ＋ `BUSINESS_IMPRESSIONS_MOBILE_MAPS` |
| `VIEWS_SEARCH` | `BUSINESS_IMPRESSIONS_DESKTOP_SEARCH` ＋ `BUSINESS_IMPRESSIONS_MOBILE_SEARCH` |
| `ACTIONS_WEBSITE` | `WEBSITE_CLICKS` |
| `ACTIONS_PHONE` | `CALL_CLICKS` |
| `ACTIONS_DRIVING_DIRECTIONS` | `BUSINESS_DIRECTION_REQUESTS` |
| `PHOTOS_VIEWS_MERCHANT` / `PHOTOS_VIEWS_CUSTOMERS` | 代替なし（廃止） |
| `QUERIES_DIRECT` / `QUERIES_INDIRECT` / `QUERIES_CHAIN` | 代替なし（廃止） |
| `DrivingDirectionMetrics` | 代替なし（廃止） |

要点は2つある。ひとつは、**表示回数がデスクトップとモバイルに分割された**こと。旧指標と同じ数字を出すには2本取って合算する必要がある。もうひとつは、**写真の閲覧数と検索クエリ種別の内訳が完全に消えた**こと。これらをレポートに載せていた場合、代替指標はないので指標定義そのものを見直すことになる。

同時期に廃止されたものとして、My Business Business Calls API（2023年5月30日）、Business Information API の `locations.associate` と `locations.clearLocationAssociation`（同日）、v4 の `InsuranceNetworks` と `HealthProviderAttributes`（2024年6月17日）がある。古い実装を引き継いだ場合は、この4点も確認しておきたい。

## GBP API の運用設計 — サンドボックスなし・ID 形式・300 QPM の配分

**サンドボックス環境が存在しない。** これが GBP API の最も厄介な性質だ。書き込み系のテストは本番の店舗情報に直接当たる。対応しているメソッドには `validateOnly` クエリパラメータがある。データを変更せずに検証だけを行えるので、CI ではこれを使う。検証用に捨ててよい GBP を1つ確保しておくのも有効だが、その場合も「検証済み・60日以上」の条件は満たしておく必要がある。

**ID の前置きが API 系統で揃っていない。** 店舗を指す数値 ID（listing ID）自体は共通で、違うのは前に何が付くかだけだ。分割 API と Performance API は `locations/{locationId}`、レガシー v4 は `accounts/{accountId}/locations/{locationId}` を要求する。内部では数値 ID を持つ店舗マスタを1つだけ持ち、API 呼び出しの直前に各系統の形式へ組み立てる層を挟むと事故が減る。

**300 QPM をどう配分するか。** 全 API 合算のクォータなので、口コミポーリングでこれを食い潰すとインサイト取得が止まる。更新頻度の異なるデータ（店舗情報は日次、口コミは時間ごと、インサイトは日次バッチ）を分けてスケジュールし、`fetchMultiDailyMetricsTimeSeries` のようなまとめ取得を優先する。指数バックオフやサーキットブレーカーの組み方は[レートリミット対策の記事](/blogs/posts/2026/07/ai-agent-rate-limit-circuit-breaker/)にまとめてある。

**Google 側からの変更を検知する。** ユーザーや Google 自身がプロフィールを書き換えることがある。Business Information API の `locations.getGoogleUpdated` で Google 側の更新版を取得できる。自社マスタとの差分を定期的に突き合わせる運用が要る。リアルタイムに寄せたい場合は Notifications API で Pub/Sub 通知を受ける。

### よく踏むエラーと原因

| 症状 | 原因 |
| --- | --- |
| 全リクエストが弾かれる | 利用申請が未承認。クォータが 0 QPM のままになっている |
| `403 PERMISSION_DENIED` | Workspace 組織側で Google ビジネス プロフィールが無効 |
| `locations.list` が 400 | `readMask` を指定していない（必須） |
| `locations.patch` が意図しない項目を消す | `updateMask` の指定漏れ |
| `/v1.1/` や `/v1.2/` で 404 | ドキュメントの版表記であってパスの版ではない。パスは `/v1` |
| 店舗が10件しか返らない | `pageSize` 未指定（既定10、上限100）。`nextPageToken` も見る |
| 長時間バッチの途中で 401 | アクセストークンの失効。`AuthorizedSession` で自動更新する |

## まとめ

- GBP API は用途ごとに分割された8つの API 群。OAuth スコープは `business.manage` の1本で共通。パスの版はいずれも `/v1`
- **口コミ・投稿・メディアはレガシーの v4 にしか存在しない**。MEO で効く機能ほど古い側に残っているので、新旧2系統の併用が前提になる
- 使い始めるには申請と承認が要る。条件は「検証済みかつ 60日以上アクティブな GBP」と「事業のウェブサイト」。承認状況は**クォータが 0 QPM か 300 QPM か**で判別できる
- Cloud コンソールで有効化する公式リストの8つには **Performance API が含まれていない**。インサイトを使うなら別途有効化する
- サンドボックスがないので、書き込みは `validateOnly` と捨ててよい検証用プロフィールで守る
- 旧 `reportInsights` からの移行では、表示回数がデスクトップ／モバイルに分割され、写真閲覧数とクエリ種別の内訳は代替なしで消えている

店舗数がひと桁のうちは管理画面で足りる。API を入れる価値が出るのは、更新の抜け漏れが実際の機会損失になり始めてからだ。逆に言えば、その時点で申請から始めると 60日条件で詰むことがあるので、**GBP の検証だけは早めに済ませておく**のが実務上のコツになる。

## 参考リンク

- [Business Profile APIs — Prerequisites｜Google for Developers](https://developers.google.com/my-business/content/prereqs)
- [Business Profile APIs — Basic setup｜Google for Developers](https://developers.google.com/my-business/content/basic-setup)
- [Business Profile APIs — Deprecation schedule｜Google for Developers](https://developers.google.com/my-business/content/sunset-dates)
- [Method: accounts.locations.reviews.list（v4）｜Google for Developers](https://developers.google.com/my-business/reference/rest/v4/accounts.locations.reviews/list)
- [Method: locations.getDailyMetricsTimeSeries（Performance API v1）｜Google for Developers](https://developers.google.com/my-business/reference/performance/rest/v1/locations/getDailyMetricsTimeSeries)
- [Googleビジネスプロフィールとは？設定方法・最適化・活用事例を完全解説｜STORES Magazine](https://stores.fun/magazine/articles/google-business-profile-stores)
