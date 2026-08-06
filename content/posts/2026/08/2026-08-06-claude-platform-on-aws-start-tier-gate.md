---
title: "開設したAWSアカウントで Claude Platform on AWS が使えない — サポートでは進まない理由"
date: 2026-08-06
lastmod: 2026-08-06
slug: "claude-platform-on-aws-start-tier-gate"
draft: false
description: "新規 AWS アカウントで Claude Platform on AWS が使えないのは、サインアップが AWS Marketplace の購読を経由するため。SCP・Private Marketplace・リセラー契約による阻害はいずれも AWS Support の権限外で、担当営業しか動かせない。使えた後の Start tier 固定の話と併せて整理する。"
source_url: "https://github.com/hdknr/blogs/issues/593#issuecomment-5200842187"
categories: ["AI/LLM", "クラウド/インフラ"]
tags: ["Claude", "Claude Platform on AWS", "Amazon Bedrock", "AWS", "レート制限"]
---

新しく開設した AWS アカウントで Claude Platform on AWS を使おうとしたら、使えなかった。**AWS サポートと何度もやり取りしたが進展せず、最終的に別途契約している AWS アカウントのローカルセールス担当と連絡がついて、ミーティングで依頼したことでようやく動いた。**

このとき最初に立てた仮説は「新規アカウントは不正利用（アビューズ）対策で手動ロックされていて、セールス経由でしか解放できないのだろう」というものだった。だが公式ドキュメントを「アカウント年齢によるロック」の観点で探しても、そんな記述はどこにも見つからない。

さらにこの仮説では説明できない事実がある。**同じ時期に、長期運用している別の AWS アカウント（別契約）では問題なくオンボードできた。** 一律のロックがかかっているなら、こうはならない。

結論から言うと、**探す場所が違っていた。** ゲートは「アカウントの新しさ」ではなく「**そのアカウント ID 向けに購読可能な AWS Marketplace のオファーが存在するか**」だった。そして症状も 2 つに分けて考える必要があった。

| 症状 | 原因 |
| --- | --- |
| **そもそも使えない**（サインアップが通らない） | そのアカウント ID 向けの購読可能なオファーが存在しない（調達の問題） |
| **使えるが上限が上がらない** | Anthropic の tier 設計（Start tier 固定・自動昇格なし） |

この 2 つは原因も連絡先も違う。混同すると、サポートに何往復問い合わせても進まないという状況になる。この記事では両方を切り分けて整理する。

## AWS 経由で Claude を使う 2 つの経路 — Bedrock と Claude Platform on AWS

2026 年 5 月 11 日、AWS は **Claude Platform on AWS** の一般提供開始を発表した。既存の AWS アカウントから、Anthropic のネイティブな Claude Platform（Messages API、Claude Console、ベータ機能）にアクセスできる。AWS はこれを最初に提供するクラウドプロバイダーとなった。提供リージョンは北米・南米・欧州・アジアパシフィックの 17 リージョンである。

ここで重要なのは、これが従来の Claude in Amazon Bedrock とは別物だという点だ。ドキュメントの表現を借りると、両者の役割分担はこうなっている。

| 比較軸 | Amazon Bedrock | Claude Platform on AWS |
| --- | --- | --- |
| 推論スタックの運用 | AWS | Anthropic |
| データ処理の境界 | AWS のセキュリティ境界内 | AWS の境界外（Anthropic が処理） |
| 課金 | AWS | AWS Marketplace |
| ベース URL | `bedrock-mantle.{region}.api.aws` | `aws-external-anthropic.{region}.api.aws` |
| **レート制限とクォータの管理** | **AWS** | **Anthropic** |
| 新機能・ベータ機能 | Bedrock のリリーススケジュールに従う | Claude API とほぼ同日、`anthropic-beta` ヘッダも通る |

最下段のひとつ上、「レート制限とクォータの管理」が今回の話の核心である。名前に `on AWS` と入っているので AWS Service Quotas で管理されていそうに見えるが、Claude Platform on AWS の上限は AWS のクォータシステムの管轄外だ。

サービス自体の概要と Bedrock との選び分けの軸は、GA 時点で書いた [Claude Platform on AWS が GA — Amazon Bedrock との違いと day-one でフル機能を使える理由](/blogs/posts/2026/05/claude-platform-on-aws-ga/) に詳しい。この記事は上限管理の一点に絞る。

![Amazon Bedrock と Claude Platform on AWS の初期セットアップの流れと、レート制限引き上げのエスカレーション窓口の違いを左右に並べた比較図。Bedrock 側は AWS Service Quotas と AWS Support、Claude Platform on AWS 側は Anthropic 管理の Start tier と Anthropic の担当者が窓口になる](/blogs/images/claude-platform-on-aws-start-tier-gate.png)

## Claude Platform on AWS は Start tier に固定される

先に用語を押さえておく。**tier（usage tier）** は Claude API の利用段階で、レート制限と月間支出上限がセットで決まる。レート制限の単位は RPM（1 分あたりリクエスト数）と TPM（1 分あたりトークン数）で、入力側は ITPM、出力側は OTPM とも表記される。

そのうえで、ドキュメントの「Rate limits and quotas」節に探していた答えがそのまま書かれていた。要点は 3 つある。

1. **Claude Platform on AWS の組織は Start tier に置かれる。** レート制限は Anthropic が直接管理し、AWS のクォータシステムは経由しない。
2. **tier の自動昇格がない。** 利用実績にもとづく tier の昇格は「ファーストパーティの Claude API の組織」に適用される仕組みで、AWS Marketplace 経由で課金される組織には適用されない。
3. **Claude Console のセルフサービス導線が存在しない。** 通常なら Claude Console の Limits ページから「Request rate limit increase」を実行できるが、Claude Platform on AWS ではこのフローが使えず、Limits ページは代わりに Anthropic の account representative（以下、担当者）に連絡するよう案内する。

つまり「担当者経由になる」のはアビューズ判定の結果ではなく、セルフサービスの引き上げ導線がそもそも用意されていないという設計上の帰結である。

ただしこれは「**使えてはいるが上限が上げられない**」場合の説明である。「アカウントを開設したのに、そもそも使えない」という症状はこれとは別で、原因も窓口も違う。次節で扱う。

## なぜ開設したアカウントで「そもそも使えない」ことがあるのか

ここが本題である。**サポートに何度問い合わせても進まず、AWS のローカルセールス担当と連絡がついてミーティングで依頼したら進んだ** — 筆者が実際に踏んだ経路がこれだった。

決定的な手がかりは、**同じ人間が管理している別の AWS アカウント（長期運用・別契約）では、同じ時期に問題なくオンボードできた**という事実だった。もし「新規アカウントはアビューズ対策で一律ロックされる」なら、それは説明できる。だが実際に開通したときに行った操作は、**AWS Marketplace の private offer を承諾すること**だった。ここから逆算すると答えが出る。

### サインアップは Marketplace の購読を経由する

Claude Platform on AWS のサインアップは AWS Marketplace のサブスクリプションを経由する。AWS コンソールで Sign up を押すと、AWS が裏で Marketplace の購読処理を行う。**つまり Marketplace で購読できないアカウントは、この時点で先に進めない。** サービスの技術的な可否ではなく、調達（procurement）の問題である。

### 購読可能なオファーはアカウント ID 単位で決まる

ここが核心である。AWS Marketplace の **resale authorization** のドキュメントを読むと、必須フィールドにこうある。

> **Buyer Accounts** — A comma-separated list of target buyer accounts for offer.
>
> （オファーの対象となる買い手アカウントのカンマ区切りリスト）
>
> （Managing AWS Marketplace resale authorizations — AWS Partner Central より）

ISV（この場合 Anthropic）が Channel Partner に再販を認可する際、**対象の買い手アカウントを個別に列挙し、リセラーの 12 桁の AWS アカウント番号を指定**する。そのうえで Channel Partner が買い手向けの private offer を発行する。

つまり private offer や再販認可は**組織単位ではなく、特定のアカウント ID にスコープされる。** 新しく作ったアカウントは当然そのリストに載っていないので、購読できるオファーが存在しない状態になる。

これで冒頭の非対称性が説明できる。

| | 長期運用アカウント（別契約） | 新規アカウント |
| --- | --- | --- |
| 購読可能なオファー | 既に存在した | **存在しない** |
| サインアップ | 通る | 止まる |
| 必要な操作 | なし | private offer の発行と承諾 |

**「アカウントが新しいから」ではなく「そのアカウント ID 向けのオファーがまだ無いから」である。** 新規アカウントは必然的にオファー未整備なので、結果として「作りたてだと使えない」という症状に見える。相関はするが、因果はアカウント年齢ではない。

### なぜ AWS サポートでは進まないのか

private offer と resale authorization を作れるのは、**ISV（Anthropic）と Channel Partner／担当営業だけ**である。AWS サポートには構造的に実行できない操作なので、ここに問い合わせ続けても進展しない。何往復しても動かなかったのはこれが理由だと考えられる。

Claude Platform on AWS のドキュメントも、この前提で書かれている。

- 「組織が Anthropic の private offer を持っている場合、コンソールがそれを検索し、AWS Marketplace で承諾するよう促す」
- 「既存の Amazon Bedrock private offer がある場合は、Sign up する前に Anthropic か AWS の **account executive**（サポートではない）に連絡すること」

サインアップのフロー自体が private offer を前提に組まれている。**そして案内されている連絡先は一貫して account executive で、サポートではない。**

### 併せて確認すべき別の阻害要因

今回の原因ではなかったが、Marketplace の購読を止める要因は他にもある。症状が似ているので切り分けの対象にはなる。

- **SCP による `aws-marketplace:Subscribe` の明示的拒否** — AWS Organizations 配下のメンバーアカウントで発生する。エラーメッセージは明示的なので判別しやすい。変更できるのは組織の管理アカウントだけで、これも AWS サポートの管轄外（顧客自身が所有するポリシーだから）

  ```text
  User is not authorized to perform: aws-marketplace:Subscribe on resource: *
  with an explicit deny in a service control policy
  ```

- **Private Marketplace による catalog 制限** — 組織が Private Marketplace を有効にしている場合、承認済み catalog に載っていない製品は購読できない。追加には管理アカウントまたは委任された管理者の操作が必要
- **支払い方法が Marketplace 非対応** — 既定の支払い方法がクレジットカードである必要がある。SEPA 銀行口座は非対応で、AISPL（インド）ではカードでの Marketplace 利用が制限される

### 結局どこに連絡すべきか

症状ごとに窓口が違う。ここを間違えると、筆者のように何往復も無駄にする。

| 症状 | 原因の所在 | 連絡先 |
| --- | --- | --- |
| **購読できるオファーが存在しない**（今回のケース） | 契約・調達形態（アカウント ID 単位） | **AWS / Anthropic の担当営業（account executive）** |
| Sign up が SCP エラーで失敗する | 自社の AWS Organizations | 自社の組織管理者 |
| 製品が Marketplace に出てこない | 自社の Private Marketplace | 自社の Private Marketplace 管理者 |
| 支払い方法が Marketplace 非対応 | 自社の請求設定 | 自社で変更（AWS Billing） |
| 使えるが tier を上げられない | Anthropic の tier 設計 | **Anthropic の account representative** |
| Service Quotas の値が異常（Bedrock） | AWS のクォータ | AWS Support |

**AWS Support に持っていって解決するのは最下段だけである。** 上 4 つはいずれもサポートの権限外なので、粘っても進まない。これが「サポートとは何度もやり取りしたが進展せず」の正体だと考えられる。

> 注記: 事実と推論の切り分けを明示しておく。**事実**は、(1) サインアップが Marketplace の購読を経由すること、(2) resale authorization が買い手アカウントを個別に列挙する仕組みであること、(3) ドキュメントの案内先が一貫して account executive であること、(4) 筆者のケースでは private offer の承諾によって開通し、別契約の長期運用アカウントでは何もせず通ったこと — ここまでは公式ドキュメントと実際の経過で確認できる。**推論**は、この 4 点から「新規アカウントで詰まる原因はオファーの不在である」と結論している部分である。「新規に開設した AWS アカウントでは使えない」という形の記述自体は、AWS・Anthropic のドキュメントには存在しない。

## Start tier の枠と月間支出上限

Start tier の実際のレート制限は決して小さくない。

| モデル | RPM | 入力 TPM | 出力 TPM |
| --- | --- | --- | --- |
| Claude Opus 5 | 1,000 | 2,000,000 | 400,000 |
| Claude Sonnet 5 | 1,000 | 2,000,000 | 400,000 |
| Claude Haiku 4.5 | 1,000 | 2,000,000 | 400,000 |
| Claude Fable 5 | 1,000 | 500,000 | 100,000 |

上位 3 モデルは同じ枠を持ち、Fable 5 だけトークン枠が低い。

一方で、実務上先に効いてくるのは月間の支出上限のほうだ。tier とレート制限と支出上限はセットになっている。

| Usage tier | 月間支出上限 |
| --- | --- |
| Start | 500 USD |
| Build | 1,000 USD |
| Scale | 200,000 USD |
| Custom | 上限なし（アカウントチームと個別調整） |

Build と Scale の間が 200 倍開いているが、これは誤植ではない。そして Start tier の上限は月 500 USD である。エージェント的なワークロードを Opus 系で回すと、この額はレート制限より先に到達しうる。支出上限とレート制限は同じ tier に属しているため、**支出上限だけを上げることはできない**。上げるには tier ごと引き上げを依頼することになる。

なお、自分でさらに低い上限を設定することは可能で、Claude Platform on AWS ではこれを Limits ページではなく **Settings > Billing** で行う。これはソフトリミットで、設定した上限に対する使用量の集計反映には約 2 時間の遅延がある。

### 注意: 支出上限について 2 つの公式ドキュメントが食い違っている

ここまで書いた支出上限の話には、確認しておくべき前提がある。**AWS 側のユーザーガイドと Anthropic 側のドキュメントで、記述が食い違っている。**

| ドキュメント | 支出上限 | tier の呼称 |
| --- | --- | --- |
| AWS ユーザーガイド（`docs.aws.amazon.com`） | `Spend limits: Not available. Rely on AWS billing controls instead.` | Tier 1 |
| Anthropic ドキュメント（`platform.claude.com`） | Start / Build / Scale に月間支出上限あり。Settings > Billing で設定可 | Start |

この記事が前掲の表で示した「Start tier = 月 500 USD」は Anthropic 側の記述である。AWS 側のユーザーガイドは、今日時点でも機能非対応リストに spend limits を挙げたままだ。

どちらを取るべきかについては、AWS 側の「Rate limits and quotas」ページ自身が答えを書いている。

> The Anthropic page is the source of truth and is updated when limits change.
>
> （Anthropic のページが source of truth であり、上限が変わったときに更新される。）
>
> （Rate limits and quotas — Claude Platform on AWS User Guide より、筆者訳）

つまり上限に関しては Anthropic 側の記述が優先され、AWS 側のユーザーガイドが追随していない状態と読むのが妥当だ。ただし実運用では、どちらの記述が自分の組織に適用されているかを Claude Console の Limits / Billing ページで現物確認するのが確実である。

このブログでは 6 月に [Claude Platform on AWS には Spend Limit がない — AWS Budgets と Rate Limit で課金暴走を防ぐ](/blogs/posts/2026/06/claude-platform-on-aws-no-spend-limit/) を書いており、そちらは AWS 側の記述を引用している。当該記事にも追記を入れた。なお 6 月の記事の「Rate Limit を低く保つことが事故時の被害上限になる」「上限引き上げは事故時の最大被害額を引き上げる行為でもある」という論点は、Start tier 固定と自動昇格なしが続いている今もそのまま有効である。

### 引き上げ依頼に何を書くか

ドキュメントは依頼時に含める情報を明示している。ここを埋めずに投げると往復が増えるので、先に用意しておくとよい。

1. 引き上げが必要なモデル
2. モデルごとの**ピーク時**の入力トークン/分と出力トークン/分（日次の合計値ではない）
3. 入力のうちキャッシュまたは繰り返しコンテキストが占める概算の割合

3 番目が効くのは、多くの Claude モデルで `cache_read_input_tokens` が ITPM にカウントされないからだ。`input_tokens` と `cache_creation_input_tokens` だけが対象になる。したがって 200 万 ITPM の枠でキャッシュヒット率が 80% なら、実効で毎分 1,000 万トークン程度の入力を処理できる。tier を上げる前に、[プロンプトキャッシュ](/blogs/posts/2026/05/claude-md-english-prompt-caching/)で実効スループットを稼げないか確認する価値がある。

## 担当者に連絡が必要な項目

「Claude Platform on AWS では担当者に連絡してください」と案内される項目を、ドキュメントから拾って並べておく。tier 引き上げ以外にもいくつかある。

- **レート制限と支出上限の引き上げ**（tier の引き上げ）
- **Zero Data Retention（ZDR）の有効化** — Claude Platform on AWS ではオプトイン。Bedrock では AWS がデータ処理者となり、Anthropic は推論の入出力を保持しない。そのため Bedrock はそもそも ZDR プログラムの対象外だ
- **Claude Console のロール割り当て** — Admin / Developer をプリンシパルに割り当てる操作
- **Private offer（個別の割引条件）** — 既存の Bedrock private offer がある場合は、Sign up する**前に** Anthropic か AWS の販売担当（account executive）に連絡する必要がある。割引は遡及適用されないため、順序を間違えると最初の請求分を取り逃す

最後の項目は地味に効く。既存の Bedrock 割引を持っている組織が「とりあえず試そう」で Sign up してしまうと、その分の利用は定価で計上される。

## 新規 AWS アカウントで Claude Platform on AWS を立ち上げる手順

新規アカウントで立ち上げるなら、この順序になる。

1. **既存の private offer や商用条件があるかを先に確認する。** ある場合は Sign up 前に Anthropic / AWS の販売担当に連絡する。
2. AWS コンソールの Claude Platform on AWS サービスページから **Sign up** する。Marketplace のサブスクリプションは AWS が処理し、数分かかる。
3. `platform.claude.com/partner-signup` で組織のオーナーのメールアドレスを入力し、届いたリンクから組織情報フォーム（組織名・法人種別・国・用途）を埋めて組織を作成する。
4. ワークスペース ID を確認する。`wrkspc_` に英数字が続く形式で、単一の AWS リージョンに紐づく。
5. `aws-external-anthropic:AssumeConsole` 権限を持つ IAM ロールを引き受けて Claude Console にサインインする。サイドバーに **Account managed by AWS** の表示が出れば正しい組織を見ている。
6. **Claude Console の Limits ページで tier と現在の上限を確認する。** ここが「Service Quotas を見に行く」との分岐点である。Start tier の月 500 USD が想定ワークロードに足りるかを、本番トラフィックを流す前に見積もる。
7. 足りないなら担当者か support に、前掲の 3 点（モデル、ピーク時の入出力 TPM、キャッシュ比率）を添えて依頼する。

ステップ 2 で以下の赤いバナーが出ることがある。IAM の反映待ちなので、**Continue** をもう一度押せばよい。

```text
Sign-up failed: Failed to enable OutboundWebIdentityFederation
```

### 最初のリクエスト

認証には IAM の SigV4 署名（推奨）と API キーの 2 方式があり、どちらも同じベース URL とリクエスト形式を使う。リクエストとレスポンスの形はファーストパーティの Claude API と同じで、変わるのはベース URL、認証方式、そして必須の `anthropic-workspace-id` ヘッダである。

```bash
# us-west-2 は URL と --aws-sigv4 の両方で自分のリージョンに置き換える
# 長期の IAM ユーザー資格情報を使う場合は x-amz-security-token ヘッダを省く
curl "https://aws-external-anthropic.us-west-2.api.aws/v1/messages" \
  --aws-sigv4 "aws:amz:us-west-2:aws-external-anthropic" \
  --user "$AWS_ACCESS_KEY_ID:$AWS_SECRET_ACCESS_KEY" \
  -H "x-amz-security-token: $AWS_SESSION_TOKEN" \
  -H "content-type: application/json" \
  -H "anthropic-version: 2023-06-01" \
  -H "anthropic-workspace-id: $ANTHROPIC_AWS_WORKSPACE_ID" \
  -d '{
    "model": "claude-sonnet-5",
    "max_tokens": 1024,
    "messages": [
      {"role": "user", "content": "Hello!"}
    ]
  }'
```

SigV4 を扱えないプロセス（LLM ゲートウェイやサーバーレス関数など）に資格情報を渡したい場合もある。この場合は AWS コンソールで長期キーを発行せず、AWS の資格情報から短期の API キーを生成する方法が案内されている。

セットアップと API 呼び出しの実機ログは [Claude Platform on AWS セットアップと API 呼び出し実録](/blogs/posts/2026/05/claude-platform-on-aws-ga-setup/) にまとめてある。

## よくある誤解を公式ドキュメントで検証する

冒頭の仮説を項目ごとに突き合わせておく。ここが今回いちばん学びのあった部分だ。

| 当初の仮説 | 検証結果 |
| --- | --- |
| 利用目的（Use Case Details）の提出と承認が必要 | **誤り** — Bedrock 側の仕組み |
| 初期クォータが 0 に設定されている | **半分正しい** — サービスによって意味が変わる |
| アビューズ対策で新規アカウントは自動承認をスキップされる | **部分的に正しい** — 仕組みは実在するが場所が違う |
| 支払い実績・クレジットリスクの確認 | **未確認** — 裏を取れなかった |

### 誤り: 利用目的の承認は Bedrock 側の仕組み

Anthropic モデルの初回利用フォームは実在する。Bedrock の API に `GetUseCaseForModelAccess` というオペレーションがあり、「Anthropic モデルへのアクセス要求に使うユースケースを返す」「Anthropic の初回利用リクエストのフォームデータを返す」と説明されている。

ただしこれは Bedrock 固有の仕組みで、Claude Platform on AWS には存在しない。Claude Platform on AWS 側の相当物は `platform.claude.com/partner-signup` の組織情報フォームだ。AWS コンソールで Sign up した後（Marketplace のサブスクリプションは AWS が自動処理する）に表示され、組織名・法人種別・国・用途を入力する。「用途を書かされる」という体験が似ているので混ざりやすいが、別のフォームである。

さらに現在の Bedrock では、主要な Claude モデルは全 Bedrock 顧客に開放されている。Claude Fable 5、Opus 4.8、Sonnet 5、Opus 4.7、Haiku 4.5 が「Open」で、モデル個別にアクセス基準が設定される形になっている。「Anthropic モデルは一律で承認待ち」という理解は現状に合っていない。

例外は招待制のモデルだ。Claude Mythos Preview は Bedrock Marketplace チームによって許可リストに登録された専用の AWS アカウントを必要とする。Anthropic の販売担当がアカウント ID を提出する。通常 24 時間程度で処理され、完了すると AWS からウェルカムメールが届く。ここは正当に「担当者経由」のフローである。

### 半分正しい: 「初期クォータ 0」はサービスによって意味が変わる

Bedrock には確かに AWS Service Quotas ベースの上限があり、既定は 200 万入力 TPM である。400 万入力 TPM までは Anthropic の追加承認なしで引き上げを要求できる。RPM 側の調整は AWS Support の担当となる。

一方 Claude Platform on AWS では、そもそも上限が Service Quotas の管轄外なので「Service Quotas が 0 になっている」という現象は起こらない。Claude Console の Limits ページで tier と現在の上限を確認するのが正しい確認手順になる。

なお「新規アカウントで実効クォータが 0 相当になる」という現象について、筆者が確認した範囲では一次情報の裏付けが取れていない。遭遇した場合は仕様ではなく異常として、Service Quotas コンソールの値を添えて AWS Support に上げるのが筋だろう。

### 部分的に正しい: アビューズ対策の仕組みは実在するが、別の場所にある

これに対応する文書化された仕組みは存在する。ただし AWS の手動ロックではなく、Anthropic 側の **Evaluation tier** だ。先の表に挙げた 4 段とは別に、入り口としてこの tier がある。

> 新規の組織や利用履歴の限られた組織は Evaluation tier から始まることがあり、アカウントの履歴が確立されるまでは標準の上限を下回る制限が適用される。この開始時の制限は Anthropic が不正利用や乱用を防ぐ仕組みの一部であり、組織が利用履歴を積むにつれて自動的に引き上げられる。
>
> （Rate limits — Claude Platform Docs より、筆者訳）

重要なのは「自動的に引き上げられる」という点である。アビューズ対策の初期制限は待てば解消する類のもので、担当者に連絡する必要はない。そしてこれはファーストパーティの Claude API 組織の話であり、Claude Platform on AWS の組織は Start tier に置かれ自動昇格しない。

同じ「新規は制限される」という見た目でも、**片方は自動で解消し、もう片方は依頼しないと動かない。** 対処法が逆になるので、区別する実益は大きい。

### 未確認: 支払い実績・クレジットリスク

高額な AI インフラの未払いリスクを理由に制限がかかるという説明は、公開ドキュメントに根拠を見つけられなかった。Claude Platform on AWS の課金は AWS Marketplace 経由で、Claude Consumption Units（CCU）建て・毎時計測・翌月請求であり、前払いクレジットではなく残高やコミットメントの概念もない。ここは推測として扱い、記事の結論には使わないでおく。

## 補足: Claude Platform on AWS で使えない機能

tier の話と同じく「AWS 経由だから」の制約として把握しておきたい項目がある。ファーストパーティの Claude API とほぼ同等の機能パリティがある一方で、以下は現時点で利用できない。

- **ワークスペース単位のレート制限設定**（組織単位の tier のみ）
- **fast mode**
- **OpenAI 互換の API エンドポイント**
- **OAuth 認証**（SigV4 か API キーを使う）
- **Admin API の大半**
  - 使える: ワークスペース系エンドポイント（作成・取得・一覧・更新・アーカイブ）
  - 使えない: 組織メンバー、ワークスペースメンバー、招待、API キー、レポート系（使用状況・コスト・レート制限）、外部キー
  - 代替: 組織メンバーシップは AWS IAM が管理し、使用状況とコストは Claude Console で確認する
- **Claude Code 専用ワークスペースと Analytics API** — Claude Code の利用は専用画面ではなく一般の使用状況ビューに合算される
- **MCP tunnels** — 公開インターネット上に露出した MCP サーバーのみサポート
- **HIPAA readiness プログラム**

また、Claude Platform on AWS では Claude Console の組織切り替えができない。別の組織にアクセスするには、いったんサインアウトして、その組織の AWS アカウントの IAM ロールで AWS コンソールから再認証する必要がある。

## まとめ

- 「そもそも使えない」と「上限が上がらない」は別の症状で、原因も連絡先も違う。前者は AWS Marketplace で購読可能なオファーが存在しないという**調達の問題**、後者は Anthropic の tier 設計の問題。
- サインアップは Marketplace の購読を経由するため、**そのアカウント ID 向けに購読可能なオファーが無いと止まる。** private offer / resale authorization は組織単位ではなく買い手アカウントを個別に列挙する仕組みなので、新しく作ったアカウントは必然的にオファー未整備になる。
- **オファーを作れるのは ISV と担当営業だけで、AWS Support には構造的に実行できない。** だからサポートに粘っても進まない。ドキュメントの案内先も一貫して account executive であってサポートではない。
- 「アカウントが新しいから使えない」ではなく「そのアカウント ID 向けのオファーがまだ無いから使えない」。相関はするが因果は違う。別契約の長期運用アカウントが問題なく通ったことがその証拠になる。
- 併せて切り分けるべき阻害要因として、SCP による `aws-marketplace:Subscribe` の拒否、Private Marketplace の catalog 制限、Marketplace 非対応の支払い方法がある。前 2 つは自社の組織管理側の話で、これも AWS Support の管轄外。
- Claude Platform on AWS（2026 年 5 月 11 日 GA）と Claude in Amazon Bedrock は別サービスで、上限を管理する主体が違う。前者は Anthropic、後者は AWS。
- Claude Platform on AWS の組織は **Start tier に固定**され、自動昇格せず、Claude Console のセルフサービス引き上げ導線も提供されない。だから結果として担当者経由になる。新規アカウントだからロックされているわけではない。
- Bedrock 側は AWS Service Quotas の世界だ。既定は 200 万入力 TPM で、400 万までは Anthropic の追加承認なしに引き上げを要求できる。RPM の調整は AWS Support が窓口になる。
- 「新規はアビューズ対策で絞られる」仕組みは Anthropic の Evaluation tier として実在するが、こちらは自動で解消する。同じ症状に見えて対処法が逆なので、区別しておく価値がある。
- Start tier の月 500 USD の支出上限は、レート制限より先に当たりやすい。本番投入前に Limits ページで確認し、必要ならプロンプトキャッシュで実効スループットを稼ぐか、tier 引き上げを依頼する。ただし支出上限については AWS 側のユーザーガイドと Anthropic 側の記述が食い違っているため、Claude Console で現物を確認すること。
- 既存の private offer があるなら Sign up より先に販売担当に連絡する。割引は遡及適用されない。

「規約に明記されているか」を探しに行くと空振りするが、「どちらのサービスの、どのページに書かれているか」を切り分けると、今回の件はほぼ全部が公開ドキュメントの範囲で説明できた。上限の話で詰まったときは、まず自分がどちらの経路にいるのかを確認するのが早い。

## 参考

- [Claude Platform on AWS is now generally available — AWS What's New](https://aws.amazon.com/about-aws/whats-new/2026/05/claude-platform-aws/)
- [Claude Platform on AWS — Claude Platform Docs](https://platform.claude.com/docs/en/build-with-claude/claude-platform-on-aws)
- [Set up your account — Claude Platform on AWS User Guide](https://docs.aws.amazon.com/claude-platform/latest/userguide/setup.html)
- [Feature support — Claude Platform on AWS User Guide](https://docs.aws.amazon.com/claude-platform/latest/userguide/feature-support.html)
- [Rate limits and quotas — Claude Platform on AWS User Guide](https://docs.aws.amazon.com/claude-platform/latest/userguide/rate-limits.html)
- [Claude in Amazon Bedrock (Opus 4.7 and later) — Claude Platform Docs](https://platform.claude.com/docs/en/build-with-claude/claude-in-amazon-bedrock)
- [Rate limits — Claude Platform Docs](https://platform.claude.com/docs/en/api/rate-limits)
- [GetUseCaseForModelAccess — Amazon Bedrock API Reference](https://docs.aws.amazon.com/bedrock/latest/APIReference/API_GetUseCaseForModelAccess.html)
- [Managing AWS Marketplace resale authorizations — AWS Partner Central](https://docs.aws.amazon.com/partner-central/latest/crm/crm-resale-authorizations.html)
- [AWS Marketplace で製品を購入する — 購入者ガイド](https://docs.aws.amazon.com/ja_jp/marketplace/latest/buyerguide/buyer-subscribing-to-products.html)
