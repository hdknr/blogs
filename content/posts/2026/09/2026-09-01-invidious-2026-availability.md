---
title: "Invidious は2026年も YouTube の代替になるか — 稼働率100%の裏で到達できたのは5件中0件"
date: 2026-09-01
lastmod: 2026-09-01
slug: "invidious-2026-availability"
draft: false
description: "Invidious の公開インスタンスを2026年9月に実測。監視サイトの稼働率は97〜100%なのに、素の HTTP クライアントが動画ページに到達できたのは5件中0件。HTTPS は32件から7件に減り公開 REST API は0件。Anubis と Cloudflare、YouTube の IP ブロックという二層のゲートと、セルフホストの前提条件を整理する。"
source_url: "https://github.com/hdknr/blogs/issues/1#issuecomment-5490095176"
categories: ["セキュリティ"]
tags: ["Invidious", "YouTube", "セルフホスト", "プライバシー", "監視"]
---

「YouTube Premium を解約した。無料でオープンソースの代替を見つけたので、もう戻らない」——
そんな X のスペイン語ポストが320万表示を集めていた。紹介されているのは
[Invidious](https://invidious.io/)、YouTube のプライバシー重視フロントエンドだ。

主張されている機能は魅力的だ。

- 広告なし / ログイン不要 / Google の追跡なし
- モバイルでのバックグラウンド再生
- Google アカウントなしでのチャンネル購読と、YouTube の購読リストの一括インポート
- 新着動画の通知
- 拡張機能で YouTube のリンクを自動リダイレクト
- 「完全な制御が欲しいなら自分でホストできる」

締めは「100% オープンソース、月 0 円」。

元ポストは正直な注意書きも添えている。「Google は2024年からインスタンスをブロックし続けているので、
公開インスタンスは波がある。自己ホストの方がずっと良い」（以下、本記事では引用を除いて
「セルフホスト」と表記する）。

この注意書きが、実は記事の主役だった。2026年9月1日時点で公開インスタンスを実際に叩いてみると、
**監視サイトが報告する稼働率は 97〜100% なのに、素の HTTP クライアントが到達できたのは5件中0件**
だった。稼働率 100.0% と報告されているインスタンスすら例外ではない。
そして「自己ホストの方がずっと良い」という部分は、公式ドキュメントを読む限り
条件付きでしか成立しない。

この記事では元ポストの主張を項目ごとに実測・検証し、Invidious の可用性が
実際には何によって決まっているのかを整理する。ついでに、
**稼働率という指標が何を測っていないのか**も見えてくる。

## Invidious 本体は生きている — AGPL-3.0、star 23,597

疑う前に、確かめられることを確かめておく。元ポストの「オープンソース」「ボランティアが GitHub で維持」
という部分は事実だ。

```bash
gh api /repos/iv-org/invidious --jq '{full_name, stargazers_count, archived, pushed_at, license: .license.spdx_id}'
```

```json
{
  "full_name": "iv-org/invidious",
  "stargazers_count": 23597,
  "archived": false,
  "pushed_at": "2026-08-28T21:50:40Z",
  "license": "AGPL-3.0"
}
```

AGPL-3.0、star 23,597、直近のプッシュは3日前。プロジェクトは生きている。

機能面もソースで裏が取れる。購読の一括インポートは
`src/invidious/views/user/data_control.ecr` に対応形式が並んでいる。
取り込めるのは、YouTube の購読（Google Takeout 経由）、YouTube プレイリスト（.csv）、
視聴履歴（.json）、FreeTube（.db）、NewPipe（.json / .zip）だ。
エクスポートは OPML と JSON。

新着通知に使える RSS も実装がある。`src/invidious/routes/feeds.cr` に `rss_channel` と
`rss_private` があり、`Content-Type` は `application/atom+xml` を返す。
モバイルのバックグラウンド再生に相当する音声のみモードも、`listen` 設定として
`src/invidious/user/preferences.cr` に存在する。

つまり**機能の実在について元ポストは嘘をついていない**。問題は、その機能に到達できるかどうかだ。

## 公開インスタンスは 32 件から 7 件へ

Invidious は公式にインスタンス一覧を JSON で公開している。まず現在の分を取る。

```bash
curl -s "https://api.invidious.io/instances.json?pretty=1&sort_by=type,users" -o inv-instances.json
```

比較対象として、Wayback Machine から2023年12月10日のスナップショットを取る。

```bash
curl -sL "http://web.archive.org/web/20231210202844/https://api.invidious.io/instances.json" -o inv-2023.json
```

一覧は `[名前, 詳細オブジェクト]` の配列なので、同じ一行を両方に当てて種別ごとに数える。

```bash
jq -r '.[] | .[1].type' inv-instances.json | sort | uniq -c
jq -r '.[] | .[1].type' inv-2023.json | sort | uniq -c
```

結果はこうなった。

| 項目 | 2023年12月10日 | 2026年9月1日 |
|---|---|---|
| 登録の総数 | 49 | 11 |
| HTTPS | 32 | 7 |
| Tor（onion） | 14 | 2 |
| I2P | 3 | 2 |
| 公開 REST API が有効なインスタンス | 27 / 32 | **0 / 7** |

元ポストの「公開インスタンスは波がある」は、規模で言えば HTTPS が32件から7件に減ったという話だ。
そして見落としやすいのが最後の行で、**公開 REST API を有効にしているインスタンスは1件も残っていない**。
2023年12月には32件中27件が有効だった。

これは機能一覧には出てこない種類の劣化だ。Invidious 公式サイトは
「Invidious has a fully featured and documented REST API for developers」と謳っているが、
その API を叩ける公開インスタンスは現在ゼロである。FreeTube のように Invidious API を
バックエンドに使えるクライアントから見ると、公開インスタンスは選択肢として消えている。

## 「稼働率 97〜100%」の中身を自分で叩く

一覧には監視データも入っている。HTTPS 7件のうち監視が付いている5件を、稼働率の高い順に並べる。
以降の実測もすべてこの順序で示す。

| インスタンス | 地域 | 稼働率（30日） | 登録受付 | ユーザー数 |
|---|---|---|---|---|
| invidious.nerdvpn.de | UA | 100.0% | 可 | 5,689 |
| invidious.f5.si | JP | 99.9% | 可 | 4,853 |
| inv.nadeko.net | CL | 98.9% | 可 | 41,764 |
| invidious.tiekoetter.com | DE | 97.9% | 不可 | — |
| yt.chocolatemoo53.com | US | 97.4% | 可 | 2,320 |

数字だけ見れば健康そのものだ。日本国内のインスタンスも1件ある。

では実際に動画ページを取ってみる。YouTube 最初の動画（`jNQXAC9IVRw`）を使う。

```bash
for h in invidious.nerdvpn.de invidious.f5.si inv.nadeko.net invidious.tiekoetter.com yt.chocolatemoo53.com; do
  curl -s -o "w-$h.html" -w "%{http_code} " -m 25 -A "Mozilla/5.0" "https://$h/watch?v=jNQXAC9IVRw"
  echo "$h"
done
```

プレイヤーが埋まっているかどうかは、動画ストリームの URL か `<video>` 要素の有無で判定する。

```bash
for h in invidious.nerdvpn.de invidious.f5.si inv.nadeko.net invidious.tiekoetter.com yt.chocolatemoo53.com; do
  echo "$h $(grep -c 'videoplayback\|<video' w-$h.html)"
done
```

5件すべて 0 件だった。返ってきたものの内訳はこうなる。

| インスタンス | HTTP | 返ってきたもの | プレイヤー |
|---|---|---|---|
| invidious.nerdvpn.de | 200 | 「503 - Service Unavailable」ページ（nginx） | 0 |
| invidious.f5.si | 200 | Anubis の PoW チャレンジ | 0 |
| inv.nadeko.net | 418 | Anubis の PoW チャレンジ | 0 |
| invidious.tiekoetter.com | 200 | Anubis の PoW チャレンジ | 0 |
| yt.chocolatemoo53.com | 200 | Cloudflare のチャレンジ | 0 |

3種類に分かれるが、原因は大きく2つだ。

### 1. HTTP 200 で「503」と書かれたページ（1件）

稼働率 100.0% の `invidious.nerdvpn.de` が返したものを見てみる。

```bash
curl -s -o /dev/null -D - -m 20 -A "Mozilla/5.0" "https://invidious.nerdvpn.de/watch?v=jNQXAC9IVRw" | grep -iE "^HTTP|^server"
```

```
HTTP/2 200
server: nginx
```

ステータスは 200。ところが本文の `<h1>` はこうだ。

```
503 - Service Unavailable
```

nginx が **HTTP 200 のステータスラインで 503 のエラーページを配っている**。
監視側から見ればレスポンスは 200 なので、稼働率は 100.0% と記録される。
稼働率が測っているのは「何かが 200 で返ってくること」であって、
Invidious が動いていることではない。

これはデッドリンク調査でよく踏む罠と同じ構造だ。ドメインを失ったサイトのパーキングページも
200 を返す。HTTP 200 は生存の証明にならない。

### 2. 運営者が置くボットゲート（Anubis 3件 / Cloudflare 1件）

残る4件のうち3件が返したのは、`<h1>Making sure you're not a bot!</h1>` というページだった
（`inv.nadeko.net` だけはこれをステータス 418 で返してくる）。

最初はこれを YouTube 側のブロック（「Sign in to confirm you are not a bot」）だと思ったが、
文字列が違う。中身を確認する。

```bash
grep -ioE "anubis|proof.of.work|\"difficulty\":[0-9]*" w-invidious.f5.si.html | sort -u
```

```
anubis
proof of work
proof-of-work
"difficulty":2
```

[Anubis](https://anubis.techaro.lol/) だった。これはインスタンス運営者が自分で設置する
Proof-of-Work 型の対ボットゲートで、AI スクレイパーの負荷からサーバを守る目的のものだ。
つまり**このゲートは Google が置いたものではなく、インスタンス運営者が置いたもの**である。

難易度は 2 と控えめで、JavaScript が動くブラウザなら一瞬で通過する程度の負荷だ。

残る1件、`yt.chocolatemoo53.com` は Cloudflare のチャレンジページだった。これも運営者側の設定である。

### ここで測れたこと・測れていないこと

正確に書いておくと、この結果は「人間がブラウザで見られない」ことを意味しない。
Anubis も Cloudflare も、JavaScript が動くブラウザなら通過することを前提にした仕組みで、
難易度2の PoW はブラウザにとって軽い。確認できたのは
**JavaScript を実行しないクライアントが1件も通れない**ということだけであり、
ブラウザで実際に再生まで到達するかは別途検証していない。

それでも、この区別自体が実用上の意味を持つ。RSS リーダー、API クライアント、
自動化スクリプト、他アプリからの利用——JavaScript を実行しない経路は、
公開インスタンス経由では原則として通らなくなっている。
公開 API が 0 / 7 という数字と、方向は一致している。

なお2025年前後の記事では「公開インスタンスはどこも新規登録を締めている」という記述を見かけるが、
少なくとも上の5件のうち4件は登録を受け付けていた。ここは当時より緩んでいる。

## Invidious の RSS フィードだけは通る — 5件中2件

ただし例外があった。RSS は元ポストが挙げた機能のひとつなので、フィードも叩いてみる。

```bash
UC="UC_x5XG1OV2P6uZZ5FSM9Ttw"
for h in invidious.nerdvpn.de invidious.f5.si inv.nadeko.net invidious.tiekoetter.com yt.chocolatemoo53.com; do
  curl -s -m 25 -A "Mozilla/5.0" -o "rss-$h.xml" -w "%{http_code} %{content_type} " "https://$h/feed/channel/$UC"
  echo "$h"
done
```

結果は分かれた。

| インスタンス | Content-Type | Atom エントリ |
|---|---|---|
| invidious.nerdvpn.de | `text/html`（503 ページ） | 0 |
| invidious.f5.si | `text/html`（ゲート） | 0 |
| inv.nadeko.net | `application/atom+xml` | 16件 |
| invidious.tiekoetter.com | `application/atom+xml` | 16件 |
| yt.chocolatemoo53.com | `text/html`（ゲート） | 0 |

2件は正しい Atom フィードを返した。動画ページでは Anubis のゲートに阻まれた
`inv.nadeko.net` と `invidious.tiekoetter.com` が、`/feed/` では素通しになっている。
運営者がフィードのパスだけゲートから除外しているということだ。

中身も生きている。

```bash
grep -oE "<title>[^<]*</title>|<published>[^<]*" rss-inv.nadeko.net.xml | head -4
```

```
<title>Google for Developers</title>
<title>Build voice-first apps with Gemini 3.5 Transcribe</title>
<published>2026-08-27T01:00:08+00:00
```

数日前の動画が入っている。フィード生成のために YouTube からメタデータを取る経路は、
このインスタンスでは機能している。元ポストの「新着動画の通知を受け取れる」は、
インスタンスを選べば今でも成立する。

## 可用性を決めているのは二層のゲート

ここまでの実測を整理すると、Invidious の可用性は独立した二つのゲートの積で決まっている。

![Invidious の可用性を決める二層のゲート構造の図。閲覧者から YouTube までの経路に、運営者が置くゲート①（Anubis や Cloudflare）と、Google が送信元 IP の出自で判定するゲート②が直列に並ぶ。下部にセルフホストの前提条件を3点併記](/blogs/images/invidious-2026-two-layer-gate.png)

**ゲート①は運営者が置く。** Anubis や Cloudflare で、スクレイパーの負荷から自分のサーバを守るためだ。
これは Google とは無関係の、運営コスト側の問題である。

**ゲート②は Google が置く。** 判定材料は送信元 IP の出自だ。公式ドキュメントの
[YouTube エラー解説](https://docs.invidious.io/youtube-errors-explained/)は、
「Sign in to confirm you are not a bot」と PO Token のタイムアウトの両方について、
同じ一文を置いている。

> It is known that YouTube block datacenter and VPN IP addresses.

ここが元ポストの「自己ホストの方がずっと良い」に直接刺さる。

## Invidious のセルフホストは「ずっと良い」のか — 家庭回線 IP と invidious-companion

「完全な制御が欲しいなら自分でホストできる」「月 0 円」という部分を、公式ドキュメントで確認する。
[インストール手順](https://docs.invidious.io/installation/)は docker-compose を推奨していて、
手順自体は素直だ。

```bash
git clone https://github.com/iv-org/invidious.git
cd invidious
docker compose up -d
```

ただし、周辺に書かれている条件が3つある。

**1つ目。データセンターの IP では通らない。** 上に引用したとおり、YouTube は
データセンターと VPN の IP をブロックする。つまり VPS やクラウドに立てるという
最も普通のセルフホストは、そのままでは成立しない。残るのは家庭回線の IP、
つまり自宅のマシンだ。元ポストの「自己ホストの方がずっと良い」は、
**「自宅の回線から出るなら」という条件が省略された主張**である。
その条件を満たせないと、セルフホストは公開インスタンスと同じ壁にぶつかる。

**2つ目。`invidious-companion` が必須になった。** ドキュメントは明言している。

> Playback won't work without Invidious companion configured.

ここで検索に頼ると古い情報を拾う。多くの記事が「`inv_sig_helper` と po_token と
visitor_data を組み合わせる」と書いているが、確認するとこうなっている。

```bash
gh api /repos/iv-org/inv_sig_helper --jq '{full_name, archived, pushed_at}'
```

```json
{
  "full_name": "iv-org/inv_sig_helper",
  "archived": true,
  "pushed_at": "2025-07-23T16:36:59Z"
}
```

`inv_sig_helper` は**アーカイブ済み**だ。現在は
[iv-org/invidious-companion](https://github.com/iv-org/invidious-companion)（Deno 製、
youtube.js ベース）が `inv_sig_helper` と `youtube-trusted-session-generator` の両方を
置き換えている。この領域は情報の陳腐化が速く、2025年の記事の手順をそのまま踏むと
アーカイブされたリポジトリを追うことになる。

**3つ目。頻繁な再起動が要る。** ドキュメントの注意書きはこうだ。

> Invidious must be restarted often, at least once a day, ideally every hour

1時間ごとの再起動が理想、という運用対象である。

3つ合わせると、「月 0 円」の中身は「サブスク料金が 0 円」であって、
自宅マシンの電気代・回線・そして定期再起動を含む運用の手間はその外側に残る。
YouTube Premium の月額と釣り合うかは、この運用を趣味として楽しめるかどうかで決まる。

なお「ページがミリ秒で読み込まれる」という体感の話も、公開インスタンス経由では
PoW チャレンジの通過がその前に挟まる。セルフホストすればゲート①は自分で外せるので、
この主張が成立するのはむしろセルフホスト側だ。

## 元ポストの主張を項目別に検証

| 主張 | 判定 | 根拠 |
|---|---|---|
| 無料・OSS・GitHub のコミュニティが維持 | ✅ | AGPL-3.0、star 23,597、2026-08-28 プッシュ |
| 広告なし | ✅ | 公式サイトに明記 |
| ログインなしで視聴できる | ✅ | 公式サイトに明記 |
| Google アカウントなしでチャンネル購読 | ✅ | 公式サイトに明記。ただしインスタンス側のアカウントが必要 |
| 新着動画の通知を受け取れる | ✅ | Atom フィード。5件中2件で実到達 |
| YouTube の購読を一括インポート | ✅ | Takeout / NewPipe / FreeTube 形式に対応（ソース確認） |
| モバイルでバックグラウンド音声 | ✅ | `listen` 設定がソースに存在 |
| Google の追跡がない | ✅ | ただし公開インスタンスの運営者からは見える |
| 拡張機能で YouTube リンクを自動リダイレクト | ✅ | [LibRedirect](https://github.com/libredirect/browser_extension) が現役（2026-08-12 プッシュ） |
| ページがミリ秒で読み込まれる | ⚠️ | 公開インスタンスでは PoW 通過が先に乗る |
| 公開インスタンスは「波がある」 | ⚠️ | 実態はより厳しい。HTTPS 32件→7件、公開 API 27件→0件 |
| 自己ホストの方がずっと良い | ⚠️ | 家庭回線の IP が前提。VPS では通らない |
| 月 0 円 | ⚠️ | サブスク料金は 0 円。電気代・回線・1時間ごとの再起動は別 |

意図的な誇張というより、**「動く条件」が省略されている**という形の不正確さだ。
機能はどれも実在する。実在しないのは「誰でもすぐ、無条件に使える」という前提のほうだ。

## 補足: YouTube 法務からの停止要求（2023年）

触れておく必要がある点として、YouTube の法務チームは2023年6月、Invidious に対して
7日以内のサービス停止を求める通知を送っている。YouTube API サービス利用規約と
デベロッパーポリシーへの違反という主張だった。

iv-org 側の回答は、自分たちは YouTube の利用規約に同意したことは一度もなく、
動画の取得と表示に YouTube の API を使っていない、というものだった。
プロジェクトは停止せず、現在も継続している。

法的な評価はこの記事の範囲を超えるが、**利用にあたって前提として知っておくべき経緯**ではある。
少なくとも「Google と揉めていない、安定した無料サービス」ではない。

## まとめ — いま Invidious を使うなら

- 元ポストが挙げた Invidious の機能は、ほぼすべてソースと公式ドキュメントで実在を確認できた
- 一方で公開インスタンスは HTTPS 32件（2023年12月）から7件に減り、公開 REST API を
  有効にしているインスタンスは1件も残っていない
- 監視サイトの稼働率 97〜100% に対し、素の HTTP クライアントが到達できたのは5件中0件。
  稼働率 100.0% のインスタンスは **HTTP 200 で「503」と書かれたページ**を返していた
- 到達を阻んでいるゲートは二層ある。運営者が置く対スクレイパー防御（Anubis / Cloudflare）と、
  Google が送信元 IP の出自で判定するブロックで、前者は Google と無関係
- `/feed/` をゲートから除外している運営者もいて、RSS は5件中2件で今も生きている
- 「自己ホストの方がずっと良い」は、家庭回線の IP から出る場合に限る。
  データセンター IP は公式ドキュメントがブロック対象と明記している
- `invidious-companion` が必須で、`inv_sig_helper` はアーカイブ済み。
  この領域の記事は1年で陳腐化するので、手順は必ず公式ドキュメントで確認する

一番持ち帰る価値があるのは、稼働率の読み方だと思う。**稼働率 97〜100% と
到達 5件中0件が同時に成り立つ**のは、監視が「200 が返ること」を測っていて、
「目的を果たせること」を測っていないからだ。監視の対象が実際のユースケースから
一段ずれていると、ダッシュボードは緑のまま壊れる。

## 参考リンク

- [Invidious 公式サイト](https://invidious.io/)
- [iv-org/invidious（GitHub）](https://github.com/iv-org/invidious)
- [iv-org/invidious-companion（GitHub）](https://github.com/iv-org/invidious-companion)
- [Invidious インストールドキュメント](https://docs.invidious.io/installation/)
- [YouTube エラーメッセージの解説（公式）](https://docs.invidious.io/youtube-errors-explained/)
- [公開インスタンス一覧（JSON）](https://api.invidious.io/instances.json)
- [LibRedirect](https://github.com/libredirect/browser_extension)
- [Anubis](https://anubis.techaro.lol/)
- [YouTube Orders 'Invidious' Privacy Software to Shut Down in 7 Days（TorrentFreak, 2023）](https://torrentfreak.com/youtube-orders-invidious-privacy-software-to-shut-down-in-7-days-230609/)
