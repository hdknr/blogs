---
title: "kabu ステーション API"
description: "三菱UFJ eスマート証券が提供する個人向け自動発注 API。Windows GUI アプリが localhost に立てる REST + WebSocket のサイドカー型で、PUSH は時価のみ"
date: 2026-05-20
lastmod: 2026-09-02
aliases: ["kabuS API", "kabusapi", "auカブコム API", "kabuステーションAPI", "kabu STATION API"]
related_posts:
  - "/posts/2026/05/nikkei225-micro-monte-carlo-claude/"
  - "/posts/2026/09/kabu-station-api-localhost-sidecar/"
tags: ["kabuステーション", "三菱UFJ eスマート証券", "自動売買", "API", "WebSocket", "kabu Station API"]
---

## 概要

kabu ステーション API は **三菱UFJ eスマート証券（旧 auカブコム証券）** が提供する個人向けの自動発注 API である。日本国内で個人が利用できる主要な自動発注 API のひとつ。

重要な前提として、**これはクラウド API ではない**。Windows の GUI アプリ「kabuステーション」を起動して API を有効化すると、そのプロセスがローカルに HTTP サーバを立て、自作プログラムはそこへリクエストを投げる。アプリが証券基幹システムへ中継する**サイドカー型**の構造である。

- リファレンス: <https://kabucom.github.io/kabusapi/reference/index.html>
- PUSH API: <https://kabucom.github.io/kabusapi/ptal/push.html>
- 開発者ポータル: <https://kabucom.github.io/kabusapi/ptal/>
- サポート窓口（GitHub Issues）: <https://github.com/kabucom/kabusapi>

## 法人向け API との区別

同社は同じブランド下に**別系統の API を 2 つ**持っている。混同しやすいので先に切り分けておく。

| | 三菱UFJ eスマート証券のAPI（法人向け） | kabu ステーション API（個人向け） |
| --- | --- | --- |
| 契約主体 | 法人口座が必須。個人口座は申込不可 | 個人口座で可 |
| 手続き | メール申請 → 一次審査 → 来社面談 → 契約 | ログイン後の電子契約のみ |
| 接続形態 | サーバ間接続（OAuth 2.0） | 同一 PC の `localhost:18080` |
| 発注操作 | 発注・**訂正**・取消 | 発注・取消（**訂正なし**） |
| PUSH 配信 | 時価・注文状態変更・建玉状態変更 | **時価のみ** |
| 対象商品 | 株式、先物・オプション、投資信託、FX、プチ株® | 株式、先物、オプション |

法人向けページは個人に対して明示的に「kabu STATION API をご利用ください」と案内している。自作ツールを第三者に提供する段階になったら法人向けの審査を受ける、という線引きになっている。

## エンドポイント

```text
本番環境  http://localhost:18080/kabusapi
検証環境  http://localhost:18081/kabusapi
PUSH     ws://localhost:18080/kabusapi/websocket
```

認証は API パスワードをトークンに交換する方式。`POST /token` で得たトークンを、以降のリクエストの `X-API-KEY` ヘッダに載せる。

## 主要機能

- **REST API**: 発注（`POST /sendorder`）・取消（`PUT /cancelorder`）・注文約定照会（`GET /orders`）・建玉照会（`GET /positions`）・取引余力（`GET /wallet/*`）・時価と板情報（`GET /board/{symbol}`）・歩み値（`GET /timeandsales/{symbol}`）
- **WebSocket Push**: **時価・板情報のストリーミングのみ**
- 対応商品は現物株・信用取引・先物・オプション（投資信託と FX の発注は非対応）

> `DELETE` メソッドのエンドポイントは仕様書に 1 つも存在しない。銘柄登録の解除も `PUT /unregister` / `PUT /unregister/all` である。

## PUSH 配信は時価のみ

**最も誤解されやすい点。** WebSocket で流れてくるのは時価・板情報だけで、**約定通知は来ない**。PUSH API リファレンスが定義する 63 フィールドは、銘柄識別子を除けばすべて価格情報である。注文状態変更・建玉状態変更の PUSH は法人向け API の機能。

したがって約定・失効・拒否の検知は `GET /orders` のポーリングで自作することになる。

- 登録できる銘柄は最大 **50 銘柄**（REST/PUSH 合わせて）
- 間引き間隔は **400ms**
- **WebSocket の同時接続は 1 本のみ**。自動再接続の公式ガイドラインはない
- 場間（昼休み）と引け後は配信されない
- `/board` や `/symbol` を叩くと**その銘柄が自動で登録枠を消費する**。スクリーニング用途で多数の銘柄に問い合わせると PUSH 対象が枠から溢れる

## 利用条件

- **Professional プランまたは Premium プラン**が必要。申込が完了しても条件を満たさなければ「利用不可」と表示される
- Professional プランの条件: 信用取引口座または先物オプション取引口座を開設済み、かつ前々々月〜前営業日・前々営業日で当社全取引の約定回数が 1 回以上
- 初回ログイン時は Professional が自動適用され、翌々月第 1 営業日まで有効
- 設定は 2 段階。マイページの「らくらく電子契約」→ 取引ツール → kabuステーションAPI利用設定と、kabuステーション側の「APIシステム設定」（`</>` アイコン右クリック）。後者は API パスワード（英数字 6〜16 桁）を設定してアプリ再起動が必要で、右上アイコンが緑になれば利用可能

## 設計を縛る制約

サイドカー型ゆえの制約が強く、いずれも回避策を探すべきバグではなく設計に織り込むべき仕様である。

- **同一 IP からのリクエストのみ受付**。Linux サーバや Docker コンテナからは叩けず、アプリと同じ Windows マシンにプログラムを置くしかない
- **GUI アプリの常時起動が前提**。Windows Server OS は動作保証対象外。クラウド／仮想 Windows は制限されないが、ディスクイメージの複製は禁止
- **毎朝 6:00〜6:30 頃に強制ログアウト**され、トークンが失効する。利用可能時間は 6:30 から翌早朝 6:15 まで。連続運転はできず「1 日 1 サイクル」の運用になる
- トークンは他にも「アプリ終了時」「ログアウト時」「**別のトークンを新たに発行した時**」で失効する。二重起動すると後発のトークンが先のものを黙って無効化する
- **訂正 API が存在しない**。取消して再発注するしかなく、その 2 リクエストは完全に独立に扱われるため 100〜200ms 空けるか `/orders` で取消確認が必要
- **Idempotency-Key 相当の仕組みがない**。タイムアウト時は `/orders` で照会して確認する

## 実装上の落とし穴

- **`Bid` と `Ask` が逆**。`/board` のレスポンスは仕様書自身が謝罪付きで告知しており、`BidPrice` が最良**売**気配、`AskPrice` が最良**買**気配を返す。影響するのは `BidQty`/`BidPrice`/`BidTime`/`BidSign` と `AskQty`/`AskPrice`/`AskTime`/`AskSign`
- **市場コードが情報系と発注系でズレる**。現物の新規発注は通常時に東証（`1`）を指定できず SOR（`9`）か東証+（`27`）を使うが、`/board` と `/timeandsales` のパスパラメータは SOR を扱わない。板は `@1`、発注は `9` という使い分けになる
- **型が混在**。ほとんどのコード値は整数だが `Side` と `FundType` は文字列型
- **流量制限**: 発注 5 件/秒、取引余力・情報・銘柄登録 10 件/秒、歩み値 2 件/秒。仕様書のタグ説明には発注「秒間10件」とあるが、公式回答は 5 件/秒なので保守的に設計する
- **reject 判定**は `State=5` だけでは不可（発注エラー・取消済・全約定・失効・期限切れが混ざる）。`Details[]` の `SeqNum` が最大のレコードの `Details[].State=4` を見る
- 証券会社側での発注エラー（余力不足・銘柄停止など）は注文が成立しないため `/orders` に載らず、発注レスポンスで判断する

## 自動売買での位置づけ

Monte Carlo + Claude 系の自動売買アーキテクチャでは「発注層」を担当する。

- 判定層が `LONG / SHORT / FLAT` のシグナルを出した直後、kabu API で実発注
- 約定確認は `GET /orders` のポーリングで行う（PUSH では通知されない）
- 日次のプロセス再起動を前提に、ポジションや注文の状態は外部ストアへ退避する
- 401 は異常系ではなく「日課」として扱い、トークンを再発行して再試行する

## 注意点

- 2024 年に **auカブコム証券 → 三菱UFJ eスマート証券** に社名変更されている
- 旧名（auカブコム証券）で書かれた古いドキュメント・記事も残っているため検索時は要注意
- 仕様書に書かれていない挙動は [GitHub Issues](https://github.com/kabucom/kabusapi) に過去の質問が蓄積されており、実装前に検索する価値が高い。ログは `%appdata%\KabuS\Log` と `%appdata%\KabuS\Log\APILog`

## 関連ページ

- [J-Quants API](/blogs/wiki/tools/j-quants-api/) — データ取得層
- [モンテカルロ法による売買判定](/blogs/wiki/concepts/monte-carlo-trading/) — 本 API の主要ユースケース

## ソース記事

- [kabuステーションAPI はクラウド API ではない — localhost:18080 に立つサイドカー型の正体](/blogs/posts/2026/09/kabu-station-api-localhost-sidecar/) — 2026-09-02
- [日経225マイクロ先物 × Monte Carlo 自動売買判定 — Claude + 1万通りシミュレーションで勝率55%超のときだけ発注する実装](/blogs/posts/2026/05/nikkei225-micro-monte-carlo-claude/) — 2026-05-20
