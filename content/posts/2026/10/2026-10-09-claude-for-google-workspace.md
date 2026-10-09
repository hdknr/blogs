---
title: "Claude for Google Workspace 公開ベータ — Docs・Sheets・Slides でできることと Gemini との使い分け"
date: 2026-10-09
lastmod: 2026-10-09
slug: "claude-for-google-workspace"
draft: false
source_url: "https://github.com/hdknr/blogs/issues/572#issuecomment-6077919594"
categories: ["AI/LLM"]
tags: ["claude", "anthropic", "Google Workspace", "gemini", "Google Sheets"]
---

Anthropic は 2026 年 10 月 6 日（米国時間）、Google Docs（Google ドキュメント）・Google Sheets（スプレッドシート）・Google Slides（スライド）の中で Claude を使える「Claude for Google Workspace」を公開ベータとして発表しました。対象は Pro・Max・Team・Enterprise の有料プランです。X でも「Gemini Spark や Workspace Studio ではできなかった」と評価する投稿が見られ、日本語の解説記事（[@ai_ai_ailover 氏の X 記事](https://x.com/ai_ai_ailover/status/2108006884934598768)、以下「解説記事」）も出ています。

これまでは、ドキュメントの文章をコピーして Claude に貼り付け、直してもらった文章をまたドキュメントに戻す、という往復が必要でした。今回の統合で、Claude が開いているファイルを読み、その場で文章・表・スライドを編集できるようになります。

この記事では、Anthropic の公式情報と解説記事をもとに、できること・Gemini との使い分け・導入時の注意点を整理します。

## 2 つの入口：サイドバーとコネクター

今回の統合には、Google ファイルの側から使う入口と、Claude のチャットの側から使う入口の 2 つがあります。

![Claude for Google Workspace の 2 つの入口を示す図。Google ファイル内の Claude サイドバーと、Claude のチャットからのコネクターがあり、モデル選択・Skills・コネクターの設定を両方で共有する](/blogs/images/claude-for-google-workspace-two-paths.png)

### ① Google ファイルの中から呼び出す（サイドバー）

Google Workspace Marketplace から Claude のアドオンをインストールし、ファイルを開いて「拡張機能」メニューから起動します。画面右側にサイドバーが表示され、1 回のインストールで Docs・Sheets・Slides の 3 つに対応します。

サイドバーの Claude は開いているファイルの内容を読み取ります。文章・セル範囲・スライドを選択して、その部分だけを処理させることもできます。

### ② Claude のチャットから Google ファイルを操作する（コネクター）

Claude のチャット画面に Google ファイルのリンクを貼ったり、「この内容から Google スライドを作って」と頼んだりすると、Claude 側からファイルを作成・編集できます。Docs・Sheets・Slides 用のコネクターがベータとして用意されています。

複数の資料を読みながら新しい企画書を作るような作業は、こちらの方が向いています。アクセスできる範囲は Google 側の共有権限に従います。Team / Enterprise プランでは、メンバーが使う前にオーナーがコネクターを有効化する必要があります。

## アプリごとにできること

### Google Docs：書式を保ったまま構成から直す

文章の書き直しや見出しスタイルの変更を、周囲の書式を維持したまま行えます。書き換えを提案カードとして出させることもでき、カードごとに採用・却下を選べます。なお、既定の編集モードではどの変更も反映前に承認を求められます（後述）。

たとえば長い企画書に対して、次のような指示が考えられます。

```text
この資料を 6 ページに圧縮してください。
ただし、要件番号、金額、納期、責任範囲は残してください。
結論、理由、実行手順の順番に再構成してください。
```

### Google Sheets：数式から Python によるデータ整形まで

数式の作成・修正、ピボットテーブル、ネイティブのグラフ、新しいタブの追加に対応しています。データの結合やクリーニングでは、選択範囲を Python に渡して処理し、その結果をシートへ書き戻せます。

日付表記が混在している、全角と半角が混じっている、同じ顧客が別名で登録されている、といった現場のデータは関数だけでは扱いにくいものです。こうした整形を、手順を説明させながら進められます。

```text
広告費データと売上データを顧客 ID で結合してください。
顧客名の全角・半角と余分な空白を統一してください。
日付を月単位にそろえ、月別の売上と広告費を集計してください。
```

### Google Slides：既存テーマで作り、崩れを点検する

既存デッキのレイアウトとテーマを使って新しいスライドを作れます。作成後には、要素の重なり・スライド外へのはみ出し・読みにくい文字といった問題を指摘できます。

AI にスライドを作らせると、内容は正しくても図形が重なったり文字が枠からはみ出したりしがちです。生成だけでなく最後の点検まで任せられる点が、資料作成では効いてきます。

## 編集の承認と履歴

サイドバーには編集モードが 2 つあります。

| モード | 動き |
| --- | --- |
| Ask before edits（既定） | 変更内容を提示し、ユーザーの承認後に反映する |
| Accept all edits | 通常の編集は確認を挟まずにまとめて処理する |

Accept all edits でも、リンクの追加、外部画像の挿入、Web アドレスの扱い、共有権限の変更に関わる操作は、引き続き承認を求められます。

Claude が行った変更は Google ファイルのバージョン履歴に残るため、通常の編集と同じ手順で元に戻せます。契約書や社外向け資料のように変更理由を確認したいファイルは Ask before edits、定型的な整形は Accept all edits、と使い分けられます。

## Claude 側の設定をそのまま持ち込める

解説記事が Gemini との大きな違いとして挙げているのが、ここです。サイドバーではモデルを選択でき、組織で許可されたモデル・コネクター・Skills の設定がそのまま反映されます。

すでに Claude Code や Claude Desktop、Projects などで、自分の仕事向けに Skills やコネクターを整えている人もいるでしょう。そうした人は、Google Workspace 用に別の AI の設定を一から作り直す必要がありません。たとえば次のような流れを Skills として標準化しておけば、毎回同じ品質で報告資料を作れます。

1. 外部の CRM から顧客情報を取得する
2. Google Drive から直近の商談メモを読む
3. 自社の報告フォーマットに当てはめる
4. Google Slides で資料を作り、Google Sheets で数値を集計する

## サイドバーが見る範囲は限定されている

誤解されやすい点ですが、サイドバーの Claude が Google Workspace 全体を見るわけではありません。アドオンが扱うのは、開いている 1 ファイルだけです。Google 側に求める権限も、サイドバーの表示とそのファイルの読み書きに必要な範囲に限られます。

Drive 内の他ファイルや Gmail・Calendar まで Claude から検索したい場合は、別途 Google Workspace のコネクターを有効にします。必要な範囲だけを Claude に見せる運用ができるわけです。Claude Desktop や Gemini CLI などから MCP 経由で Workspace データを扱う方法は、[Google Workspace 公式 MCP サーバー](/blogs/posts/2026/04/google-workspace-mcp-server/) の記事で紹介しています。

組織で導入する場合は、Google Workspace 管理者がドメイン・グループ・組織部門の単位で利用者を指定できます。Team / Enterprise では、Claude 側の管理者がコネクター・Skills・モデルの利用範囲を管理します。

## Gemini との使い分け

Gemini は Gmail・Drive・Calendar・Meet・Chat など Google のサービスに深く組み込まれており、Google の権限体系の中で情報を横断して扱うのが得意です。Gmail・カレンダー・Drive をまたぐ作業を 1 つのプロンプトで連続処理する [Gemini Agent モード](/blogs/posts/2026/04/gemini-agent-mode/) は、その方向を突き詰めた機能です。Gemini in Docs や Gemini in Sheets も、下書きの作成、表やグラフの作成、ピボットテーブルなどに対応しています。

解説記事の整理を借りると、使い分けは次のようになります。この表は公式の比較ではなく解説記事の評価にもとづくもので、Gemini 側の機能も継続的に更新されている点に注意してください（◎ = 得意、○ = 対応、△ = 限定的）。

| 向いている作業 | Gemini | Claude |
| --- | --- | --- |
| メール要約・予定調整・Drive 横断検索 | ◎ | コネクター次第 |
| Sheets の標準操作をすばやく実行 | ◎ | ○ |
| 長文を構造から作り直す | ○ | ◎ |
| 汚れたデータの結合・クリーニング（Python） | ○ | ◎ |
| 自社の Skills・外部コネクターを使った資料作成 | △ | ◎ |
| スライドのレイアウト崩れの点検 | △ | ◎ |

Google の中の情報を集める・予定を回すのは Gemini、成果物の品質を上げる編集や分析は Claude、という分担が現実的でしょう。

## 導入手順

利用できるのは有料プラン（Pro・Max・Team・Enterprise）です。

1. Google Workspace Marketplace で Claude のアドオンをインストールする
2. Google Docs・Sheets・Slides のいずれかのファイルを開く
3. 「拡張機能」メニューから Claude を起動する
4. サイドバーで Claude アカウントにログインする
5. Drive・Gmail・Calendar なども扱いたい場合は、Claude 側で Google Workspace のコネクターを有効にする

管理者が Marketplace のアドオンを制限している組織では、管理者による許可やインストールが必要です。

## ベータ版の制約

公開ベータのため、次のような制約があります。

- アドオン単体では、開いているファイル以外の Google ファイルの作成・コピーや、PDF への書き出しはできない
- 処理中にサイドバーを閉じると作業が止まる
- Firefox はサポート対象外
- 1 回の長い処理には最大 6 分の制限がある
- Slides で Claude が作るグラフは画像として挿入されるため、元データが変わっても自動更新されない（データが変わったら Claude にグラフを作り直させる）

Enterprise 向けの統制機能は一部のみ対応です。公式ヘルプによると、Compliance API・CMEK・OpenTelemetry には対応する一方、Bedrock・Vertex AI・Azure 経由の推論、ゼロデータ保持（ZDR）、HIPAA には対応しておらず、組織独自のデータ保持設定も引き継がれません。導入前に管理者が確認しておくと安全です。

## まとめ

Claude for Google Workspace は、「Claude に文章を作らせてコピペで戻す」作業をなくし、Google ファイルそのものを Claude に仕上げさせるための統合です。

- サイドバーは開いている 1 ファイルを読み取って直接編集し、変更は承認制にもできる
- コネクターを使えば、Claude のチャットから Google ファイルを作成・編集できる
- モデル選択・Skills・コネクターといった Claude 側の設定がそのまま使える
- Google 全体の情報を横断するなら Gemini、成果物の仕上げなら Claude という使い分けが現実的
- 公開ベータのため、Firefox 非対応や 1 回の処理が最大 6 分といった制約がある

すでに Claude を日常的に使い込んでいる人ほど、恩恵が大きいアップデートだと言えます。

## 参考

- [Use Claude in Google Docs, Sheets, and Slides（Claude Help Center）](https://support.claude.com/en/articles/16951679-use-claude-in-google-docs-sheets-and-slides)
- [Claude now works with Google Docs, Sheets, and Slides（claude.com）](https://claude.com/blog/claude-now-works-in-google-docs-sheets-and-slides)
- [Claude Now Works Directly in Google Docs, Sheets and Slides（iPhone in Canada）](https://www.iphoneincanada.ca/2026/10/06/claude-now-works-directly-in-google-docs-sheets-and-slides/)
- [Claude for Google Workspace in public beta（Reworked）](https://www.reworked.co/digital-workplace/anthropic-opens-claude-for-google-workspace-in-beta/)
- [Claude × Google Workspace完全解説（X / @ai_ai_ailover）](https://x.com/ai_ai_ailover/status/2108006884934598768)
- [解説記事を引用した投稿（X / @MakeAI_CEO）](https://x.com/MakeAI_CEO/status/2108161645470212408)
