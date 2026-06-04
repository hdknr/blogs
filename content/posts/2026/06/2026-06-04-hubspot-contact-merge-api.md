---
title: "HubSpot 重複コンタクトを API でマージする方法 — AI 検知 × 人間承認の 3 ステップ設計"
date: 2026-06-04
lastmod: 2026-06-04
slug: "hubspot-contact-merge-api"
draft: false
description: "HubSpot の重複コンタクトを CRM API v3 のマージエンドポイントで統合する方法を解説。マージは取り消し不可のため、AI に重複検知させて人間が承認し API で実行する 3 ステップ設計が現実的。マージ回数上限や Koalify / Insycle などの外部ツールにも触れる。"
source_url: "https://github.com/hdknr/blogs/issues/71#issuecomment-4620334665"
categories: ["Web開発"]
tags: ["hubspot", "crm", "api", "dedup", "marketing-automation"]
---

HubSpot を運用していると必ず直面するのが**重複リード（コンタクト）の問題**です。同じ人がフォーム経由とインポート経由で別レコードになっている、表記揺れで名寄せされていない——こうした重複を放置するとメール配信もスコアリングも狂います。

結論から言うと、**API を使って 2 つのコンタクトをマージすることは可能**です。HubSpot の API にはコンタクトのマージ用エンドポイントが用意されており、マージ機能自体は Starter プランでも利用できます（API 実行には Private App の作成権限 = Super Admin が必要）。

ただし、**「AI エージェントだけで全自動で重複を検知・マージまで完結させる」のは、安全性の観点から少しハードルが高い**です。マージは一発勝負でやり直しが効かないからです。

現実的かつ賢いやり方は、「AI に重複を見つけさせてリスト化させ、マージ自体は API で行う（または人間が承認する）」というシステムを組むことです。本記事では具体的な仕組みと API の実装方法を解説します。

## AI × API で実現する「自動重複マージ」の設計図

全自動で裏でマージしてしまうと、同姓同名の別人（例:「佐藤一郎」さんという別の会社の人）をマージしてしまうリスクがあります。そのため、以下のような 3 ステップの仕組みを作るのが一般的です。

![AI が重複候補を検知してリスト化し、Slack 等で人間に確認を求め、承認されたペアだけ HubSpot API でマージを実行する 3 ステップのフロー図。全自動にしない理由としてマージが取り消し不可である点を注記](/blogs/images/hubspot-contact-merge-api-flow.png)

1. **Step 1: AI が検知** — AI（またはスクリプト）が「名前が一致、かつ会社名や電話番号が類似」しているリードを抽出
2. **Step 2: 人間が確認** — Slack や社内ツール、Google スプレッドシート等に「この 2 人、マージして大丈夫ですか?」と AI が通知
3. **Step 3: API で実行** — 人間が「承認（OK）」ボタンを押したら、システムが HubSpot API を叩いて安全にマージを実行

## Step 1「AI が検知」を分解する

「AI が検知」は実際には 4 つの工程に分かれます。すべてを LLM にやらせるのではなく、**機械的に絞り込めるところはスクリプトで処理し、あいまいな判断だけを LLM に渡す**のがコストと精度のバランスを取るコツです。

### 1-1. コンタクトデータの取得

CRM API でコンタクトを比較対象プロパティ付きで取得します（ページネーション必須。また 1 クエリあたり 10,000 件の取得上限があるため、それを超える規模では `createdate` 等でのセグメント分割が必要です）。

```bash
curl --request GET \
  --url 'https://api.hubapi.com/crm/v3/objects/contacts?limit=100&properties=email,firstname,lastname,company,phone,hs_object_id' \
  --header 'authorization: Bearer YOUR_ACCESS_TOKEN'
```

前提として、HubSpot はコンタクトを**メールアドレスで重複排除**します（フォーム送信などはメール完全一致で自動名寄せ）。つまり AI が探すべきは「メールは違う（または片方欠損）が同一人物らしい」**あいまい重複**だけです。

### 1-2. 正規化と候補ペアの絞り込み（ブロッキング）

全組み合わせを比較すると 1 万件で約 5,000 万ペアになり破綻するため、先に決定的ルールで候補を絞ります。

- **正規化**: 全角/半角・大文字小文字・カナ/かなの統一、電話番号の記号除去（`03-1234-5678` → `0312345678`）、会社名の「株式会社/(株)」除去
- **ブロッキングキー**: 「姓 + 会社名」「電話番号下 8 桁」「メールのドメイン + 名」などが一致するペアだけを候補に残す

ここまでは AI ではなく普通のスクリプト（Python の `pandas` + `rapidfuzz` 等）で十分かつ高速です。

### 1-3. LLM による同一人物判定

絞り込んだ候補ペアだけを LLM に渡し、構造化された判定をさせます。ここが「AI が検知」の核心です。

```text
以下の 2 つの CRM コンタクトが同一人物か判定してください。

レコードA: {"id":"101","name":"佐藤 一郎","company":"株式会社ABC","email":"i.sato@abc.co.jp","phone":"03-1234-5678"}
レコードB: {"id":"202","name":"サトウ イチロウ","company":"ABC(株)","email":null,"phone":"0312345678"}

JSON で回答: {"is_duplicate": true/false, "confidence": 0-100,
"reason": "判定根拠", "suggested_primary": "残すべき ID と理由"}
```

LLM が効くのは、表記揺れ（漢字/カナ）、旧姓・転職、会社名の略記など**ルールで書き切れない判断**です。逆に「同姓同名だが会社が違う」ペアに `is_duplicate: false` と根拠付きで答えられるのも利点です。コストは 1-2 の絞り込みで候補が数百ペア程度になっていれば現実的な範囲に収まります。

### 1-4. primary の提案とリスト化

マージは「どちらを残すか」の判断も必要なので、AI に **`primaryObjectId` の提案**までさせます。判断基準の例:

- プロパティの充足度が高い方（メール・電話が埋まっている）
- ライフサイクルステージが進んでいる方（商談あり > リード）
- 直近のアクティビティがある方

最終出力は「ペア + confidence + 根拠 + primary 案」の表で、これがそのまま Step 2 の承認依頼（Slack 通知やスプレッドシートの行）になります。confidence でしきい値を切り、**高確信のみ通知・低確信は無視**とするとノイズが減ります。

なお、コードを書かずに済ませたい場合は HubSpot 標準の「重複管理ツール」も類似レコードのサジェストを行います（個別の重複管理は Professional 以上、一括処理は Data Hub Professional 以上）。ただし判定根拠の説明・primary の自動提案・Slack 承認フローまで組めるのが自作 AI パイプラインの利点です。

## 開発者向け: マージを実行する HubSpot API

HubSpot の最新の CRM API（v3）には、コンタクトをマージするための[専用エンドポイント](https://developers.hubspot.com/docs/api-reference/crm-contacts-v3/basic/post-crm-v3-objects-contacts-merge)があります。これを使うと、管理画面で手動マージしたときとほぼ同等の処理（プロパティ・アクティビティ履歴の統合など）が行われます。なおマージは非同期処理で、200 応答は「受理」を意味し、完了まで数秒かかる場合があります。

### エンドポイント（POST）

```text
https://api.hubapi.com/crm/v3/objects/contacts/merge
```

### リクエストボディ（JSON データ）

システムから HubSpot に送るデータ（ペイロード）の形式です。

```json
{
  "primaryObjectId": "101",
  "objectIdToMerge": "202"
}
```

- **`primaryObjectId`**: 最終的に「メインとして残す側」のコンタクト ID
- **`objectIdToMerge`**: メインに吸収されて「消える側（重複側）」のコンタクト ID

### cURL での実行例

```bash
curl --request POST \
  --url https://api.hubapi.com/crm/v3/objects/contacts/merge \
  --header 'authorization: Bearer YOUR_ACCESS_TOKEN' \
  --header 'content-type: application/json' \
  --data '{
    "primaryObjectId": "101",
    "objectIdToMerge": "202"
  }'
```

## API や外部ツールを使う際の注意点

1. **マージ制限（上限）に注意**
   HubSpot の仕様上、マージしようとする **2 つのレコードの合算マージ回数が 250 回以上**になるとエラーになります（例: 双方が 130 回ずつマージに関与していると合算 260 回で上限超過）。通常の運用では滅多に引っかかりませんが、テスト等で同じレコードを何度も使い回す際は注意してください。

2. **サードパーティツールの検討（ノーコード派向け）**
   自社で API を組むのが難しい場合、HubSpot のアプリマーケットプレイスにある『[Koalify](https://ecosystem.hubspot.com/marketplace/listing/koalify-io)』（無料枠あり）や『[Insycle](https://ecosystem.hubspot.com/marketplace/listing/dedup)』（有料）といった、重複管理に特化した外部アプリを連携させるのも一つの手です。柔軟な重複ルールを設定できます（対応する HubSpot プランは各アプリのマーケットプレイス掲載を確認してください）。

## まとめ

- HubSpot の重複コンタクトは **CRM API v3 のマージエンドポイント**でプログラムから統合できる（Starter プランでも利用可）
- マージは**取り消し不可の一発勝負**なので、全自動化はリスクが高い
- 「**AI が検知 → 人間が承認 → API が実行**」の 3 ステップ設計が安全性と効率のバランスが良い
- マージ回数の合算上限（250 回）に注意。ノーコードで済ませたい場合は Koalify / Insycle などの専用アプリも選択肢

Python や Node.js での重複検知の実装、Zapier などの iPaaS での構成など、具体的な組み方はニーズに応じて発展させていけます。

## 参考リンク

- [Merge two contacts — HubSpot CRM API v3 | HubSpot Developers](https://developers.hubspot.com/docs/api-reference/crm-contacts-v3/basic/post-crm-v3-objects-contacts-merge)
- [Merge records | HubSpot Knowledge Base](https://knowledge.hubspot.com/records/merge-records)
