---
title: "Claude Platform on AWS の上限は Start tier 固定 — 引き上げが担当者経由になる理由"
date: 2026-08-06
lastmod: 2026-08-06
slug: "claude-platform-on-aws-start-tier-gate"
draft: false
description: "Claude Platform on AWS のレート制限と月 500 USD の支出上限は Anthropic 管理の Start tier に固定され、自動昇格も Console からのセルフサービス引き上げもない。Amazon Bedrock の Service Quotas との管轄の違いと、引き上げ依頼に必要な情報を整理する。"
source_url: "https://github.com/hdknr/blogs/issues/593#issuecomment-5200842187"
categories: ["AI/LLM", "クラウド/インフラ"]
tags: ["Claude", "Claude Platform on AWS", "Amazon Bedrock", "AWS", "レート制限"]
---

新しく開設した AWS アカウントで Claude を使おうとして、「上限が上がらない」「結局『担当営業に連絡してほしい』と案内された」という状況に出くわすことがある。

このとき最初に立てがちな仮説は「新規アカウントは不正利用（アビューズ）対策で手動ロックされていて、セールス経由でしか解放できないのだろう」というものだ。筆者も当初そう整理していた。しかし公式ドキュメントを読み直すと、症状としての結論（担当者経由になる）は当たっているが、**原因の説明はほぼ入れ替えが必要**だった。

原因は「新規アカウントだからロックされている」ことではなく、Claude Platform on AWS と Amazon Bedrock が別サービスで、上限を管理している主体も引き上げの窓口も違うことにある。しかもその窓口は AWS ではなく Anthropic 側だ。この記事はその整理である。

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

つまり「担当者経由になる」のはアビューズ判定の結果ではなく、セルフサービスの引き上げ導線がそもそも用意されていないという設計上の帰結である。新規アカウントであってもなくても同じ扱いになる。

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

### 6 月の記事から変わった点

このブログでは 6 月に [Claude Platform on AWS には Spend Limit がない — AWS Budgets と Rate Limit で課金暴走を防ぐ](/blogs/posts/2026/06/claude-platform-on-aws-no-spend-limit/) を書いた。当時の公式ドキュメントは機能非対応リストに「Spend limits: Not available. Rely on AWS billing controls instead.」と明記しており、記事はそれを引用している。

**この点は現在のドキュメントでは変わっている。** 今日時点の Claude Platform on AWS のドキュメントを確認すると、機能非対応リストから spend limits の項目は消えており、代わりに「Spend limits」という独立した節が追加されて、Settings > Billing から組織およびワークスペース単位の月間支出上限を設定できると説明されている。tier の呼称も当時の「Tier 1」から「Start」に変わった。

したがって 6 月の記事の結論のうち「金額上限をかける機能が存在しない」という部分は現在は成り立たない。一方で「Rate Limit を低く保つことが事故時の被害上限になる」「上限引き上げは事故時の最大被害額を引き上げる行為でもある」という論点は、Start tier 固定が続いている今もそのまま有効である。AWS Budgets によるアラートの組み方も引き続き有用だ。

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

- Claude Platform on AWS（2026 年 5 月 11 日 GA）と Claude in Amazon Bedrock は別サービスで、上限を管理する主体が違う。前者は Anthropic、後者は AWS。
- Claude Platform on AWS の組織は **Start tier に固定**され、自動昇格せず、Claude Console のセルフサービス引き上げ導線も提供されない。だから結果として担当者経由になる。新規アカウントだからロックされているわけではない。
- Bedrock 側は AWS Service Quotas の世界だ。既定は 200 万入力 TPM で、400 万までは Anthropic の追加承認なしに引き上げを要求できる。RPM の調整は AWS Support が窓口になる。
- 「新規はアビューズ対策で絞られる」仕組みは Anthropic の Evaluation tier として実在するが、こちらは自動で解消する。同じ症状に見えて対処法が逆なので、区別しておく価値がある。
- Start tier の月 500 USD の支出上限は、レート制限より先に当たりやすい。本番投入前に Limits ページで確認し、必要ならプロンプトキャッシュで実効スループットを稼ぐか、tier 引き上げを依頼する。
- 既存の private offer があるなら Sign up より先に販売担当に連絡する。割引は遡及適用されない。

「規約に明記されているか」を探しに行くと空振りするが、「どちらのサービスの、どのページに書かれているか」を切り分けると、今回の件はほぼ全部が公開ドキュメントの範囲で説明できた。上限の話で詰まったときは、まず自分がどちらの経路にいるのかを確認するのが早い。

## 参考

- [Claude Platform on AWS is now generally available — AWS What's New](https://aws.amazon.com/about-aws/whats-new/2026/05/claude-platform-aws/)
- [Claude Platform on AWS — Claude Platform Docs](https://platform.claude.com/docs/en/build-with-claude/claude-platform-on-aws)
- [Set up your account — Claude Platform on AWS User Guide](https://docs.aws.amazon.com/claude-platform/latest/userguide/setup.html)
- [Claude in Amazon Bedrock (Opus 4.7 and later) — Claude Platform Docs](https://platform.claude.com/docs/en/build-with-claude/claude-in-amazon-bedrock)
- [Rate limits — Claude Platform Docs](https://platform.claude.com/docs/en/api/rate-limits)
- [GetUseCaseForModelAccess — Amazon Bedrock API Reference](https://docs.aws.amazon.com/bedrock/latest/APIReference/API_GetUseCaseForModelAccess.html)
