---
title: "AI で作った社内ツールは GAS に置く：追加コストゼロの「社内限定」アプリ基盤"
date: 2026-10-09
lastmod: 2026-10-09
slug: "gas-internal-app-platform"
draft: false
source_url: "https://github.com/hdknr/blogs/issues/572#issuecomment-6072815563"
categories: ["AI/LLM"]
tags: ["GAS", "Google Workspace", "claude-code", "Agent Skills", "MDM"]
---

## はじめに

Claude Code のようなコーディングエージェントが全社に行き渡ると、非エンジニアの社員も業務ツールを自分で作り始めます。そこで次に問題になるのは「作ったツールをどこに置くか」です。

kubell（旧 Chatwork）の山本正喜 CEO が [X で紹介](https://x.com/cwmasaki/status/2107299379992551509) していたのが、社内エンジニアの須田幹大さんによる note 記事「[Google Workspace があればどの会社でも作れる！追加コストゼロで「社内限定」アプリ基盤を整備した話](https://note.com/kubell_suda/n/nc9c577b34af6)」です。AI で作った社内アプリの公開先を **Google Apps Script（GAS）の Web アプリ** に統一し、その「安全な道」を Claude のスキルで舗装した、という事例です。

この記事では、その内容をもとに、GAS を選んだ理由、Web アプリの基本構成（doGet / google.script.run / appsscript.json）、社内スキルと MDM で全社に定着させる仕組み、そして GAS の制約を順に紹介します。

## なぜ Vercel / Netlify ではなく GAS なのか

社員が AI でツールを作るようになると、公開先として Vercel や Netlify が自然に選ばれ始めます。しかし、社内ツールの置き場所としては次のような懸念がありました。

- URL さえ分かれば社外からも開けてしまう
- Basic 認証や IP 制限は、設定漏れが起きやすい
- 個人アカウントで運用すると、作成者の退職とともにツールが消える
- 情シスが把握していない社外のデータストアに業務データが置かれる

社内ガイドラインはあっても、ツールを作る人が読みに行くとは限りません。そこで「ここに置けばよい」という標準の置き場所を用意する方針になりました。

AWS 上に社内基盤を自前で作る案も検討されました。しかし、認証・ホスティング・DB・監視を運用し続けるコストが大きくなります。また、業務データの多くは Google Workspace にあるため、別クラウドから Google API を呼ぶと認証情報の管理も増えます。結果として、**既に契約している Google Workspace に含まれる GAS** が選ばれました。

GAS の Web アプリを選んだ理由は次のとおりです。

| 観点 | GAS Web アプリでの扱い |
|------|------------------------|
| 公開範囲 | 自社ドメインのアカウントだけに限定できる |
| 利用者の識別 | 開いた人のアカウントをサーバ側で取得できる |
| データの置き場所 | 自社 Workspace のスプレッドシート |
| 費用 | 追加費用なし。個人のクレジットカードも不要 |
| 引き継ぎ | オーナー譲渡や共有ドライブで会社の管理下に残せる |

## 全体像

![作る人の PC 上で Claude Code と社内スキルを使って Vite でビルドした単一 HTML を clasp で GAS Web アプリにデプロイし、同じドメインの社員だけがブラウザから利用してスプレッドシートのデータを読み書きする構成と、スキルを GitHub Actions と MDM で全社端末に配布する流れを示した図](/blogs/images/gas-internal-app-platform-architecture.png)

大きく分けると、次の 3 つの層でできています。

1. **作る人の手元**：Claude Code に自然言語で頼むと、社内スキルが雛形作成からデプロイまでを案内する
2. **Google Workspace**：GAS Web アプリが画面とサーバ関数を提供し、データはスプレッドシートに置く
3. **配布**：スキルと全社共通の設定を MDM（Jamf や Intune などの端末管理ツール）で全社員の端末に届ける

## GAS Web アプリの基本構成

### doGet で HTML を配信する

元記事によると、Web アプリとしてデプロイすると `https://script.google.com/a/macros/<ドメイン>/s/<デプロイID>/exec` という形式の URL が発行されます。アクセスされると `doGet()` が呼ばれ、HTML を返します。

```javascript
function doGet() {
  return HtmlService.createHtmlOutputFromFile('Index').setTitle('備品予約');
}
```

### google.script.run でサーバ関数を呼ぶ

ブラウザ側からは `google.script.run` で GAS のサーバ関数を非同期に呼び出せます。API サーバを立てたり、CORS や認証トークンを管理したりする必要はありません。

```javascript
// ブラウザ側
google.script.run
  .withSuccessHandler((rows) => render(rows))
  .withFailureHandler((err) => showError(err.message))
  .listMyReservations();
```

サーバ側では `Session.getActiveUser().getEmail()` で呼び出した社員を特定できます。シートは `getDataRange().getValues()` でまとめて 1 回で読むのが基本です。

```javascript
// サーバ側（GAS）
function listMyReservations() {
  const me = Session.getActiveUser().getEmail();
  const values = SpreadsheetApp.openById(SHEET_ID)
    .getSheetByName('reservations')
    .getDataRange()
    .getValues();
  return values.filter((row) => row[1] === me); // 2 列目 = 予約者のメールアドレス
}
```

`SHEET_ID` はデータを置くスプレッドシートの ID です。スクリプトをスプレッドシートにバインドしている場合は `SpreadsheetApp.getActive()` でも構いませんが、スタンドアロンのスクリプトでは `openById()` で開きます。

### appsscript.json で公開範囲を決める

公開範囲と実行権限はマニフェスト `appsscript.json` の `webapp` で指定します。

```json
{
  "timeZone": "Asia/Tokyo",
  "runtimeVersion": "V8",
  "webapp": {
    "access": "DOMAIN",
    "executeAs": "USER_ACCESSING"
  }
}
```

- `access: "DOMAIN"`：デプロイした人と同じ Workspace ドメインのアカウントだけが開ける
- `executeAs: "USER_ACCESSING"`：開いた人の権限で実行する

`USER_ACCESSING` の場合、利用者自身にシートの編集権限が必要です。つまり、利用者がシートを直接開けば他人の行も編集できてしまいます。利用者に元データの権限を渡したくない場合は、デプロイした人の権限で動く `USER_DEPLOYING` を選びます。なお `Session.getActiveUser()` は実行設定やセキュリティポリシーによって空文字を返すことがあるため、どちらの設定でも利用者のメールアドレスが取れるかを最初に確かめておくと安心です。どちらにするかは、データの共有範囲に応じて決める必要があります。

### 単一 HTML にビルドする

GAS は HTML をファイル単位で配信するため、JS と CSS を別ファイルに分けて読み込む通常の構成はそのまま使えません。そこで、画面は Vite + React + TypeScript で書き、[vite-plugin-singlefile](https://github.com/richardtallent/vite-plugin-singlefile) で JS と CSS を 1 つの `Index.html` に埋め込みます。画像などの静的ファイルも data URI にして同じ HTML に含めます。

デプロイには Google が公開している CLI の [clasp](https://github.com/google/clasp) を使います。デプロイ ID を固定したまま更新すれば、URL を変えずに中身だけを差し替えられます。元記事では `clasp redeploy` を使っていますが、デプロイ関連のサブコマンド名は clasp のバージョンによって異なるため、手元の `clasp --help` で確認してください。開発中は `vite dev` で画面を確認し、`google.script.run` の呼び出し部分はモックに差し替えます。

## 社内スキルで「安全な道」を舗装する

この事例で特に参考になるのは、GAS という技術の選択よりも、**それを社員に使ってもらう仕組み** のほうです。

kubell では全社配布の Claude スキル集を「kube-mas（Kubell Major Skills）」と呼んでおり、GAS 関連のスキルを役割ごとに分けています。

| スキル | 役割 |
|--------|------|
| onboarding | 用途やデータの共有範囲などを 2〜3 問ヒアリングして方針を決める。Vercel への公開を希望されたときの案内もここが担う |
| scaffold | 雛形を生成する |
| deploy | 社内公開を実行する |

利用者がスキル名を覚える必要はなく、自然言語で頼めば適切なスキルが動きます。スキルの設計では、次の 3 点が重視されています。

### 1. 事故が起きやすい箇所を確認させる

- clasp でプロジェクトを作ると `appsscript.json` が既定値で上書きされ、公開範囲の設定が消えてしまいます。スキルには作成直後に設定を書き戻す手順と、タイムゾーンが `America/New_York` のままなら書き戻しに失敗したと判断する確認方法が書かれています。
- 個人の Gmail でログインしたままデプロイすると、同僚が開けなくなります。そのため、デプロイ前にアカウントのドメインを確認させます。

### 2. 体感速度を最初から確保する

GAS は 1 回の呼び出しに数百ミリ秒から 1 秒ほどかかります。「遅いから」という理由で Vercel などに流れてしまわないよう、雛形には最初から次の工夫を組み込んでいます。

- 楽観的更新（サーバの応答を待たずに画面を更新する）
- 再訪時のキャッシュ表示
- 同期中であることの表示

さらにスキルには「GAS は遅い、と先回りして言わない」とも書かれています。**体感速度もガバナンスを保つための要件** と位置づけているのが印象的です。

### 3. 既知の罠リストを育てる

たとえば、GAS の HTML は iframe の中に表示されるため、URL のハッシュ（`#/...`）が画面側に届かず、共有された URL を開くと真っ白になる、という罠があります。こうした症状・原因・対処を「罠リスト」としてスキルに持たせ、新しい罠に遭遇するたびに追記しています。その結果、同じ問題で 2 人目が詰まることはほぼなくなったとのことです。

## スキルと設定を全社に配る

スキルは、社員が自分でインストールしなくても届くようになっています。

- Claude Code には、管理者が OS の決まった場所に置いた設定やスキルを全ユーザーに読み込ませる仕組みがあります。macOS では `/Library/Application Support/ClaudeCode/` が配置先です。
- 設定一式は GitHub で管理し、main にマージされると GitHub Actions が macOS 用 pkg と Windows 用パッケージを生成します。それを Jamf（macOS）と Intune（Windows）で全社端末に配布します。
- claude.ai のデスクトップアプリには、同じスキルをプラグインにまとめて組織単位で配布しています。

さらに全社共通の `CLAUDE.md` には、外部 AI サービスの組み込みや外部クラウドへのデプロイを行おうとしたときに、社内ガイドラインの該当箇所を示して確認を促すよう書かれています。ガイドラインの原文は Confluence から自動同期されています。そのため、実際に Vercel で公開しようとすると、Claude が該当箇所を引用して確認を求めてきます。

「ガイドラインを読んでもらう」のではなく、**ツールを作る瞬間に AI がガイドラインを持ってくる** という設計になっているわけです。

## 導入後の変化

元記事では、導入後の変化として次のような例が挙げられています。

- 「Vercel に上げていいか」という問い合わせがほぼなくなり、「特定メンバーだけに見せたい」「定期実行の通知を工夫したい」といった一歩進んだ相談が増えた
- デザイナーが動くモックを作り、社内限定 URL でエンジニアに渡すようになった
- Confluence で運用していた社員紹介ページを、機能面も含めて GAS 上で作り直した
- テスト結果をスクリーンショット付きで共有する仕組みを作ったチームがあり、Google Drive 上の HTML ファイルを GAS から社内向けに配信している
- GAS スキル自体の使い方ページも、そのスキルで作って GAS から配信している

## 制約と向き不向き

もちろん GAS は万能ではありません。元記事でも次の制約が挙げられています。

- **実行時間とクォータ**：1 回の実行は最大 6 分で、API 呼び出しには 1 日あたりのクォータがある。重いバッチ処理や大量アクセスのサービスには向かない
- **テナントの壁**：`access: "DOMAIN"` のツールは同じ Workspace テナントのユーザーしか開けない。関連会社など別テナントの利用者には、画面とデータを中継する別の仕組みが必要になる
- **iframe の制約**：URL ハッシュが届かない、自動リダイレクトができない
- **データストア**：スプレッドシートは本格的な DB の代わりにはならない。同時書き込みは `LockService` で直列化している

同時書き込みの直列化は、たとえば次のような形になります。

```javascript
function reserve(item, date) {
  const lock = LockService.getScriptLock();
  lock.waitLock(10000); // 最大 10 秒待つ
  try {
    const sheet = SpreadsheetApp.openById(SHEET_ID).getSheetByName('reservations');
    sheet.appendRow([item, Session.getActiveUser().getEmail(), date]);
  } finally {
    lock.releaseLock();
  }
}
```

それでも、社内の小規模なツールであれば大半は GAS で足りる、というのが元記事の結論です。

## 自社で試すには

元記事の末尾には、Claude Code にこの記事を読ませて自社向けの GAS 社内公開スキル群を設計させるためのプロンプト例が載っています。その流れは次のとおりです。

1. まず Workspace のドメイン、別ドメインの利用者の有無、利用者層、社内ルール、配布方法、データの保存先を質問する
2. 回答をもとに、onboarding / scaffold / deploy などの役割分担を設計する
3. 設計が固まってから実装に進む

Google Workspace を契約している組織であれば、追加コストなしで同じ構成を試せます。

## まとめ

- AI で社員がツールを作れるようになると、「どこに置くか」がガバナンスの論点になる
- GAS の Web アプリは、ドメイン限定公開・利用者識別・データの社内保持・引き継ぎを追加費用なしで満たせる
- 技術選定だけでなく、**スキルで安全な道を舗装し、MDM で配り、CLAUDE.md でガイドラインを自動提示する** ことで、社員が自然にその道を選ぶようになる
- 体感速度や既知の罠への対処まで雛形に組み込んでおくことが、ルールを守ってもらうための実務的な工夫になっている

「禁止する」より「正しい置き場所を一番楽にする」というアプローチは、AI 時代の社内 IT ガバナンスの参考になります。

## 参考

- [山本正喜さんの投稿（X）](https://x.com/cwmasaki/status/2107299379992551509)
- [Google Workspace があればどの会社でも作れる！追加コストゼロで「社内限定」アプリ基盤を整備した話（note）](https://note.com/kubell_suda/n/nc9c577b34af6)
- [Web Apps | Apps Script | Google for Developers](https://developers.google.com/apps-script/guides/web)
- [google/clasp（GitHub）](https://github.com/google/clasp)
