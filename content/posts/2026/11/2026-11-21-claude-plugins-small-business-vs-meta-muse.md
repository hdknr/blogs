---
title: "「Claude プラグイン 532 個で月 3.8 万ドルのチームが不要」を検証する — Claude for Small Business と Meta Muse の比較"
date: 2026-11-21
lastmod: 2026-11-21
slug: "claude-plugins-small-business-vs-meta-muse"
draft: false
source_url: "https://github.com/hdknr/blogs/issues/572#issuecomment-7057590137"
categories: ["AI/LLM"]
tags: ["claude-code", "プラグイン", "Claude Cowork", "スモールビジネス", "Muse"]
---

## はじめに

2026 年 11 月 20 日、X で次のような投稿が拡散した。

> Anthropic が Claude の無料プラグインを 532 個出した。Stripe、Shopify、Canva、BlackRock、HubSpot が自分たちで作ったものだ。Dario Amodei（Anthropic の CEO）が、小さな会社のチームをまるごと置き換える 7 つを選んだ。そのチームは月 38,400 ドルかかるが、プラグインは 0 ドル。
> （[@PaulYoungX の投稿](https://x.com/PaulYoungX/status/2123710181032747325)（フランス語）を要約・翻訳。ほぼ同じ文面の[英語の投稿](https://x.com/mika_systems/status/2123133007208812915)もある）

投稿が挙げる 7 つは、経理（QuickBooks）、決済開発（Stripe）、EC 運営（Shopify）、デザイン（Canva）、営業（HubSpot）、法務（LegalZoom）、業務連携（Zapier）。BlackRock は 7 つに入っていない。「Claude Code を開いて `/plugin` と打てば 5 分で入る」「まず 1 つ、毎朝開いているツールのものから」と締めくくっている。

この記事では、投稿の主張を Claude の公式マーケットプレイスと公式リポジトリで 1 つずつ確かめる。そのうえで、以前取り上げた Meta の Muse と比べる。どちらも「AI に仕事を任せる」製品だが、作りが大きく違う。

先に結論を書くと、**「532 個の無料プラグイン」はおおむね本当だが、「CEO が選んだ 7 つで月 3.8 万ドルのチームが不要」には根拠がない**。小さな会社向けの本命は、別にある「Claude for Small Business」というプラグインだ。

## 登場するプロダクトと用語

| 名前 | 何か |
|---|---|
| プラグイン | スキル・コネクタ・スラッシュコマンド・サブエージェント・フックをまとめて、1 回でインストールできるようにした Claude の拡張パッケージ |
| コネクタ | Claude を外部サービス（QuickBooks、HubSpot など）につなぐ部品。中身は MCP（Model Context Protocol）サーバー |
| スキル | 特定の作業の手順や知識をまとめたもの。Claude が必要なときに読み込む |
| Claude Code | 開発者向けのエージェント型コーディングツール（CLI・デスクトップ・IDE 拡張） |
| Claude Cowork | 開発者でない人向けに、デスクトップアプリ上でファイル操作や業務を任せる Claude の作業スペース |
| Claude Marketplace | プラグイン・コネクタ・パートナーの製品をまとめて探せる Web の公式ディレクトリ（[claude.com/marketplace](https://claude.com/marketplace)） |
| claude-plugins-official | Claude Code の `/plugin` が参照する公式マーケットプレイスの定義（[GitHub](https://github.com/anthropics/claude-plugins-official)）。各プラグインの作者や配布元が書かれている |
| Claude for Small Business | Anthropic が 2026 年 5 月 13 日に発表した、小規模事業者向けのプラグイン（Cowork 用） |
| Meta Muse | Meta が 2026 年 9 月に発表したパーソナル AI エージェント。専用のクラウド VM 上でブラウザを操作して作業する |

## 投稿の主張を 1 つずつ確かめる

2026 年 11 月 21 日時点で、Web の Claude Marketplace と claude-plugins-official を見た結果をまとめる。

| 投稿の主張 | 確認できたこと | 判定 |
|---|---|---|
| 無料のプラグインが 532 個 | [プラグイン一覧](https://claude.com/marketplace/plugins) の表示は 539 個。数は日々変わるので、投稿時点で 532 個だった可能性はある | おおむね正しい |
| Stripe・Shopify・Canva・BlackRock・HubSpot が自分で作った | claude-plugins-official で、Canva・Shopify・HubSpot は作者が各社になっている。Stripe は作者欄がないが、配布元は Stripe のリポジトリ。BlackRock のプラグイン（`blackrock-advisor-center-plugin`）もあるが、金融アドバイザー向けで小さな会社の業務とは関係がない | おおむね正しい |
| Dario Amodei が 7 つを選んだ | 出典が見当たらない。7 つは別々のプラグインで、Anthropic がこの 7 つをセットで紹介した事実も見つからなかった | 根拠なし |
| チームは月 38,400 ドル、プラグインは 0 ドル | 月 38,400 ドルの根拠は示されていない。プラグイン自体は無料だが、Claude の有料プランと、各サービスの契約は別に要る（後述） | 誇張 |
| `/plugin` で 5 分でインストール | 開発者向けの一部は Claude Code の `/plugin` で入る。ただし小規模事業者向けの本命は Cowork 用で、Claude Code ではない | 一部正しい |

### QuickBooks・Stripe・Shopify など 7 つのプラグインの中身

投稿の「役割」と、プラグインの説明に書かれている実際の機能を並べる。

| 投稿の役割 | 実際のプラグイン | 説明に書かれている機能 |
|---|---|---|
| 経理 | Intuit QuickBooks（`intuit-quickbooks`） | 損益・キャッシュフローの財務状況のまとめ、業界との比較、請求書、給与、融資 |
| 決済の開発者 | Stripe（`stripe`） | **開発者向け**。Stripe の MCP サーバーにつなぎ、Checkout やサブスクリプションの実装を手伝う。`/explain-error`（エラーの説明）と `/test-cards`（テスト用カード番号）がある |
| EC 店長 | Shopify AI Toolkit（`shopify-ai-toolkit`） | **開発向けが中心のスキル 18 個**。ドキュメント検索、GraphQL・Liquid のコード検証、Hydrogen、Polaris など。CLI でのストア管理や、店舗運営者向けの導入案内も含む |
| デザイナー | Canva（`canva`） | デザインの作成・編集・リサイズ・ブランドチェック。変更はプレビューして承認してから反映される。スプレッドシートからの一括作成は Canva Enterprise プランが必要 |
| 営業 | HubSpot Sales（`hubspot-sales`） | 朝のブリーフ、商談前の準備、フォローアップの下書き、通話記録、パイプライン（進行中の商談一覧）の見直し。結果は HubSpot に書き戻される |
| 弁護士 | LegalZoom（`legalzoom`） | `/review-contract` で契約書のリスクを赤・黄・緑で分類する。**法的助言ではない**と明記されている。弁護士への相談は LegalZoom の Business Attorney Plan が必要 |
| 業務連携 | Zapier（`zapier`） | 8,000 以上のアプリの Zapier アクションを Claude から呼び出す |

注意したいのは Stripe と Shopify だ。どちらも中心は**自社のサービスの上でアプリを作る開発者**向けの機能で、店の運営や返金処理を丸ごと任せるものではない。「人を置き換える」という並べ方は、ここで実態からずれている。

## 小さな会社向けの本命は「Claude for Small Business」

投稿の 7 つはばらばらのプラグインだが、Anthropic は小規模事業者向けに 1 つにまとめたプラグインを出している。2026 年 5 月 13 日に発表された [Claude for Small Business](https://www.anthropic.com/news/claude-for-small-business) だ。中身は [anthropics/knowledge-work-plugins](https://github.com/anthropics/knowledge-work-plugins) の `small-business` で公開されている。

発表時は「15 のワークフローと 15 のスキル」だったが、現在の[マーケットプレイスの説明](https://claude.com/marketplace/plugins/small-business)では 43 個の業務ワークフローに増えている。主なコマンドは次のとおり。

| コマンド | やること |
|---|---|
| `/monday-brief` | 現金・売上・パイプライン・予定と、いちばん手を打つべきことを 1 ページにまとめる |
| `/close-month` | 帳簿と決済サービスの記録を突き合わせ、税理士向けの月次資料を作る |
| `/plan-payroll` | 給与を払う現金があるか確かめ、未払いの請求を催促し、給与計算の準備をする |
| `/pay-the-bills`・`/restock`・`/tax-prep` | 支払い、在庫の補充、四半期の納税や 1099（米国の支払調書） |
| `/speed-to-lead` | 夜間・週末の問い合わせに、空いている面談の日時を添えて返信し、CRM（顧客管理システム）に記録する |
| `/grow-pipeline`・`/call-list` | 優良顧客に似た見込み客を探し、営業文を書き、今日電話すべき相手を示す |
| `/smb-onboard` | 事業の内容を聞き取り、ツールの接続を手伝う |

接続できるパートナーのコネクタは 37 個ある。主なものは次のとおり。

- 会計・給与: QuickBooks、Xero、Gusto
- 決済・EC: Stripe、Square、PayPal、Shopify
- 営業: HubSpot、Salesforce
- その他: Canva、Docusign、Google Workspace、Microsoft 365、Slack、Zapier

投稿の 7 つのうち、開発者向けの Stripe・Shopify のプラグインを除いた「業務」の部分は、だいたいこのプラグイン 1 つでカバーされる。

大事なのは**承認モード**だ。どのワークフローも最初は承認モードで動き、Claude は下書きと準備までを行う。送信・投稿・支払いは、利用者が許可するまで実行されない。信頼できたワークフローだけ、スケジュールで自動実行に切り替えられる。

ただし `/tax-prep` の 1099 や Gusto（米国の給与計算サービス）のように、**米国の商習慣を前提にした部分**が多い。日本の会社がそのまま使えるのは、営業・マーケティング・デザインまわりが中心になるだろう。

## 導入方法と費用

### インストール

開発者向けのプラグインは、Claude Code の入力欄で 1 行ずつ実行して公式マーケットプレイスから入れる。

```text
/plugin install stripe@claude-plugins-official
/plugin install shopify-ai-toolkit@claude-plugins-official
/plugin install hubspot-sales@claude-plugins-official
```

Claude for Small Business は Cowork 用なので、Claude デスクトップアプリの Cowork から追加する。[マーケットプレイスのページ](https://claude.com/marketplace/plugins/small-business) の「Install in Cowork」からも入れられる。

### 「0 ドル」ではない

プラグイン自体に料金はかからないが、次の費用は別にかかる。

- **Claude の有料プラン**: The Register の報道では、Claude for Small Business は Pro・Max・Team プランの利用者が Cowork から追加できる
- **各サービスの契約**: QuickBooks や HubSpot などを使うには、それぞれの契約が要る。LegalZoom の弁護士相談や Canva の一括作成のように、上位プランが前提の機能もある
- **データの扱い**: Anthropic は Team・Enterprise プランのデータを、既定では学習に使わないとしている。個人向けの Pro・Max で業務データを扱う場合は、学習の設定を確認しておきたい

## Meta Muse との比較

[Meta Muse](/blogs/wiki/tools/meta-muse/) も「仕事を AI に任せる」製品だが、作りは大きく違う。

| 項目 | Claude のプラグイン（Small Business ほか） | Meta Muse |
|---|---|---|
| 何を任せるか | ベンダーが用意したワークフロー（月次決算、給与準備、営業など） | 何でも。ブラウザでできることはほぼ全部 |
| 使い方を考えるのは誰か | プラグインを作った側（Anthropic・パートナー各社） | 利用者 |
| 外部サービスとのつなぎ方 | 公式のコネクタ（MCP）で API につなぐ | クラウド VM 上のブラウザで画面を操作する |
| 承認 | 承認モードが標準。送信・投稿・支払いの前に止まる | 送信や購入の前に知らせる。外部送信は別エージェントの Sentinel が承認する |
| モデル | Claude | Meta のモデル（Muse Spark）。他のモデルを選べるかは公表されていない |
| 動く場所 | Claude のアプリ（Cowork はデスクトップ） | Meta のクラウド VM。アプリを閉じても続く |
| 費用 | プラグインは無料。Claude の有料プランと各サービスの契約が要る | ほとんどの用途は無料。多く使う人向けにサブスクリプション |
| 向いている人 | 会計・CRM・EC のツールをすでに契約している事業者 | 買い物・予約・リサーチなどの雑務をすぐ任せたい個人 |

### 違いは「使い方を見つける手間」を誰が持つか

Muse の記事では、汎用エージェントは何でもできるぶん、**使い方を見つける手間が利用者に移る**ことを見た。活用例を集めたら 388 通りになった、という話だ（[Meta の AI エージェント Muse は「使い方の凡例が 388 通り」](/blogs/posts/2026/11/meta-muse-use-case-inventory/)）。

Claude のプラグインはその反対で、使い方をパートナー各社が先に決めてパッケージにしている。何を任せられるかが、最初からコマンド名やスキル名になっている。たとえば HubSpot なら「朝のブリーフ」「商談前の準備」、Small Business なら「月次決算」「給与の準備」だ。そのかわり、用意されていない作業はできないか、自分でスキルを足すことになる。Small Business には、毎週手でやっている作業をワークフローにする `build-agent` も入っている。

つなぎ方の違いも効いてくる。Muse はブラウザで画面を操作するので、API のないサイトでも使える。そのぶん、画面が変わると止まりやすいと考えられる。Claude のプラグインは各社の公式コネクタを通すので、画面の変更には左右されにくい。コネクタのないサービスは Zapier 経由になる。

### 併用するなら

- **会計・CRM・EC の定型業務**: Claude のプラグインに任せる。データはすでに契約しているサービスの中にあり、公式コネクタで読み書きできる
- **API のないサイトでの雑務**（予約・買い物・フォーム入力）: Muse に任せる
- **どちらも**: 最初は承認付きで動かし、手戻りのない作業から自動実行に切り替える

## GTD の視点：投稿でいちばん役立つ助言

投稿の数字は割り引いて読むべきだが、最後の助言は的を射ている。「**まず 1 つだけ。毎朝開いているツールのプラグインがいちばん効く**」。

これは GTD（Getting Things Done。やることを書き出し、週次レビューで見直す仕事術）の考え方に重なる。[Muse の記事](/blogs/posts/2026/11/meta-muse-use-case-inventory/)で書いた「自分の繰り返し作業の表から、任せられるものを逆引きする」と同じだ。539 個のプラグインを眺めて選ぶのではなく、向きを逆にする。

1. 毎週やっている作業と、そのとき開いているツールを書き出す
2. そのツールのプラグインがマーケットプレイスにあるか探す
3. あれば承認付きで 1 つ入れて、1 週間使う
4. 週次レビューで「手戻りがなかったか」「承認待ちで止まっていないか」を見て、次の 1 つを決める

## まとめ

- 「532 個の無料プラグイン」はおおむね本当だが、「CEO が選んだ 7 つ」「月 38,400 ドルのチームが不要」には根拠がない
- 7 つのうち Stripe と Shopify は開発向けが中心で、店を運営する人の代わりにはならない
- 小規模事業者向けの本命は Claude for Small Business（Cowork 用）。現在は 43 のワークフローと 37 のコネクタを備えるが、米国の商習慣が前提の部分が多い
- Meta Muse との違いは「使い方を見つける手間」を誰が持つか。プラグインはベンダーが、汎用エージェントは利用者が持つ
- 始めるなら、毎朝開くツールのプラグインを 1 つ、承認付きで
