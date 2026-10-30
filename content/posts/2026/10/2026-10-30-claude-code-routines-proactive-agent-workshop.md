---
title: "「従業員なしで会社を立ち上げるマニュアル」の中身 — Anthropic の Routines ワークショップを読み解く"
description: "Anthropic の Code w/ Claude 2026 ワークショップをもとに、Claude Code Routines（現 scheduled tasks）のトリガー・コンテキスト・舵取りの設計と、無人で回すときの注意点を整理する。"
date: 2026-10-30
lastmod: 2026-10-30
slug: "claude-code-routines-proactive-agent-workshop"
draft: false
source_url: "https://github.com/hdknr/blogs/issues/572#issuecomment-6514904517"
categories: ["AI/LLM"]
tags: ["claude-code", "anthropic", "AIエージェント", "自動化", "mcp"]
---

X で「Anthropic が従業員なしで会社を立ち上げるためのマニュアルを無料公開した」という投稿が話題になった（[元投稿](https://x.com/n0tisma/status/2115050894433927470)、スペイン語）。結論から言うと、中身は Claude Code の **Routines**（現 scheduled tasks）を扱った Anthropic 公式のワークショップだ。

元投稿に添えられた約 22 分の動画では、AI とチャットするのではなく、エージェントが自分で起動し、人間の介入なしで仕事を片付ける仕組みとして紹介されている。

- スケジュール・API 呼び出し・GitHub イベントで起動する
- PC を閉じていてもクラウドで動く
- 無料

3 点目の「無料」は、動画を無料で視聴できるという意味だ。

この「マニュアル」の正体は、Anthropic の開発者カンファレンス **Code w/ Claude 2026** のワークショップ「[Build a proactive agent workflow with Claude Code](https://claude.com/code-with-claude/session/ldn-build-a-proactive-agent-workflow-with-claude-code)」だろう。動画の長さと内容が、このセッションの記録と一致する。ロンドン会場では 2026 年 5 月 19 日に、Anthropic の Maya Nielan 氏が登壇している。

ただし、中身は「従業員のいない会社」の作り方ではない。Enter を押されるまで待つ道具だった Claude Code を、自分から動くチームメイトに変える話だ。本記事でわかるのは次の 3 点だ。

- Routines の現在の名称と提供範囲
- Routine を設計するときに決める 3 つの事柄（トリガー・コンテキスト・舵取り）
- 無人で回すときの運用上の注意点

## 先に押さえておきたいこと：Routines は「scheduled tasks」に改名された

Routines は 2026 年 4 月に登場した機能だ（当時の紹介は [Claude Code Routines リリース](/blogs/posts/2026/04/claude-code-routines/) を参照）。現在の公式ドキュメント「[Automate work with scheduled tasks](https://code.claude.com/docs/en/routines)」では、名称が **scheduled tasks（旧 routines）** に変わっている。

旧名はまだ各所に残っている。

- 管理画面の URL は `claude.ai/code/routines` のまま
- CLI の `/schedule` には `/routines` という別名がある
- API のエンドポイントやベータヘッダーにも `routine` の名前が残る

機能はリサーチプレビューの段階で、挙動・上限・API は変わる可能性がある。対象は Pro / Max / Team / Enterprise プランだ。以下ではワークショップに合わせて「Routines」（個々の設定は「Routine」）と呼ぶ。

## 手元で Claude Code を cron に載せるときの 3 つの壁

ワークショップは「Claude Code を cron で回したことがある人は？」という問いかけから始まる。多くの手が挙がったが、そのインフラを作って保守するのが楽しかった人はほぼいなかった。Anthropic 社内でも同じ苦労があったという。

登壇者が挙げた壁は 3 つある。

1. **どこで動かすか**：ローカルで動かすと、ノート PC を閉じた時点でセッションが終わる。ホスティング・データの永続化・認証を自前で用意することになる
2. **いつ起動するか**：cron を組むか、自前でエンドポイントを立てて POST を受けるか。ここもインフラ作業になる
3. **何をしているか見えない**：ヘッドレス（対話画面を持たない非対話モード）で起動した Claude Code は、リアルタイムに様子を見たり、方向を変えたり、後から再開したりするのが難しい

## Routines が肩代わりするもの

Routines では、利用者が定義するのは次の 4 つだけだ。

- プロンプト
- 接続するリポジトリ
- 使わせるコネクタ（MCP：Slack や Google Drive などの外部サービスとつなぐ仕組み）
- トリガー

残りは Claude Code 側が引き受ける。先ほどの 3 つの壁に対応させると、次のようになる。

| 壁 | Routines の答え |
|---|---|
| どこで動かすか | Anthropic 管理のクラウドで実行。ホスティング・セッション状態・コネクタの認証を Anthropic 側が持つ |
| いつ起動するか | スケジュール・GitHub イベント・API（HTTP POST）の 3 種類のトリガー。1 つの Routine に複数のトリガーを付けられる |
| 何をしているか見えない | 中身は普通の Claude Code セッション。Web・CLI・デスクトップから開いて、途中で指示を出したり、後から再開したりできる |

## 設計で決めるのは「トリガー・コンテキスト・舵取り」の 3 つ

ワークショップの中心は、どんな Routine を作るときにも決める 3 つの事柄だ。例には、後述する Anthropic 社内のドキュメント自動化が使われている。

![Routines の設計で決める 3 つの事柄を示す図。左から、いつ起動するかを決めるトリガー（スケジュール、GitHub イベント、API）、何を渡すかを決めるコンテキスト（プロンプト、リポジトリ、MCP コネクタ）が並ぶ。その先で Anthropic 管理のクラウド上の Claude Code セッションが動き、最後に品質をどう担保するかを決める舵取り（エージェント同士のレビュー、実行中のセッションへの介入、成果物の検証）につながる](/blogs/images/claude-code-routines-three-decisions.png)

### 1. トリガー：いつ起動するか

起動の仕方は、時間ベースとイベントベースの 2 系統だ。

- **時間ベース**：毎週月曜 10 時に、ソースの変更とドキュメントの差分を確認する
- **イベントベース**
  - **GitHub イベント**：リリースブランチが切られたら差分を見る。「ドキュメントが必要」と示すラベルの付いた PR がマージされたら起動する
  - **API**：CD パイプラインがデプロイ後に、自分のコードから POST する

### 2. コンテキスト：何を渡すか

登壇者は「Claude に渡したコンテキストが、Claude が成功できる上限になる」と強調した。ドキュメント自動化の例では、次のものを渡している。

- **リポジトリ**：変更を読むための Claude Code のソースと、PR を出す先のドキュメントリポジトリの 2 本
- **Google Drive コネクタ**：社外向け資料と同じ言い回しで書かせるため、マーケティング資料を読ませる
- **Slack コネクタ**：PR を作ったら通知させる

### 3. 舵取り：品質をどう担保するか

紹介された手段は 3 つある。

- **エージェント同士のレビュー**：generator-critic パターン（生成役と批評役を分けるマルチエージェントの型）を借りる。ドキュメントの PR を作る Routine とは別に、その PR の作成をトリガーにレビューコメントを付ける Routine を用意し、人間が見る前に一度批評を通す
- **実行中のセッションへの介入**：claude.ai の Code 画面から実行中のセッションを開き、途中で質問したり方向を変えたりできる
- **成果物の検証**：ドキュメントの例では、Claude が変更したページを実際に描画して期待どおりか確かめる

## 社内事例：PR が 200% 増えた Claude Code のドキュメント保守

デモの題材は Anthropic 社内の実例だ。登壇者によると、Claude Code の週あたりの PR 数は年初から 200% 増えた。開発チームの生産性は上がったが、Claude Code と Agent SDK のドキュメントを一人で保守するエンジニアにとっては負担が増えた。そこでこのエンジニアは、早い段階から Routines を導入していた。

デモでは 2 つの Routine を作っていた。

1. **週次のドキュメント同期**
   - Claude Code で `/schedule` を実行し、「週に一度、main にマージされた変更をドキュメントリポジトリと照らし合わせ、必要なら更新 PR を作って」と頼む
   - Claude が「毎週何時に実行するか」「PR を作ったら Slack に通知するか」を聞き返す
   - 答えると、Claude が指示文まで生成して Routine を保存する
2. **Issue 起点の調査**
   - ドキュメントリポジトリで Issue が作られたら起動し、ドキュメントの不足が原因かを調べる。不足なら PR を作って Slack に通知する
   - デモでは、起動したセッションに「その修正は別 PR で済んでいる」と伝えて止めてみせ、実行中に舵を切れることを示した

Claude Code のセッション内で、次のように自然文で依頼するだけで作成を始められる（公式ドキュメントの例）。

```text
/schedule daily PR review at 9am
/schedule in 2 weeks, open a cleanup PR that removes the feature flag
```

`/schedule` で作った Routine にはスケジュールトリガーが付く。GitHub トリガーは Web から、または Claude Code v2.1.225 以降なら CLI からも追加できる。API トリガーの追加とトークンの管理は Web からしかできない。

## 応用例：デプロイ検証エージェント

ワークショップでは、同じ 3 つの観点で「デプロイ検証」の Routine も組み立てていた。

- **トリガー**：CD パイプラインがデプロイのたびに Routine の API エンドポイントへ POST する
- **コンテキスト**：デプロイしたサービスのソースコード、Datadog や Grafana などの監視ツール、異常時に知らせる Slack・メール・Twilio
- **舵取り**：最初は調査と Go / No-Go の判断だけを任せ、人間が分析を読んでからロールバックする。判断が信頼できるとわかってきたら、ロールバックそのものも任せる

API トリガーの呼び出しは、公式ドキュメントの例では次の形だ。URL 中の `trig_...` とトークンは、自分の Routine で発行した値に置き換える。

```bash
curl -X POST https://api.anthropic.com/v1/claude_code/routines/trig_01ABCDEFGHJKLMNOPQRSTUVW/fire \
  -H "Authorization: Bearer $ROUTINE_TOKEN" \
  -H "anthropic-beta: experimental-cc-routine-2026-04-01" \
  -H "anthropic-version: 2023-06-01" \
  -H "Content-Type: application/json" \
  -d '{"text": "Sentry alert SEN-4521 fired in prod. Stack trace attached."}'
```

成功すると、新しいセッションの ID と URL が返る（公式ドキュメントのレスポンス例）。

```json
{
  "type": "routine_fire",
  "claude_code_session_id": "session_01HJKLMNOPQRSTUVWXYZ",
  "claude_code_session_url": "https://claude.ai/code/session_01HJKLMNOPQRSTUVWXYZ"
}
```

その URL を開けば、実行の様子を見られる。

舵取りの部分が、このワークショップでいちばん実務的な指摘だと思う。いきなり全自動にせず、判断の結果を人間が見続けて、信頼が積み上がった範囲だけ権限を広げていく。

## 「従業員なし」の前に知っておきたい運用上の注意

元投稿の「人間の介入なしで仕事が片付く」という言い方は強すぎる。公式ドキュメントを読むと、無人で回すからこそ気をつける点が見えてくる。

### 権限とアカウント

- **Routine は作成者個人のものとして動く**：scheduled tasks（Routines）は個人の claude.ai アカウントに属し、チームメイトとは共有されない。コミットや PR は作成者の GitHub ユーザーで作られ、Slack への投稿も作成者のアカウントで行われる
- **コネクタは既定で全部付く**：接続済みの MCP コネクタはすべて既定で含まれ、実行中は書き込みにも使われうる。Routine に不要なものは外す

### API で渡す `text` の扱い

- **何が起きるか**：API で渡した `text` は `<routine-fire-payload>` で包まれて届き、「中の指示に従わないこと」というラベルが付く
- **なぜか**：トークンが漏れても、外部の文章が直接の命令として通らないようにするための設計だ
- **どうするか**：アラート本文などに沿って動かしたいなら、保存するプロンプト側で「routine-fire-payload の中身を調査して」と明示する

### 実行上の制約

- **実行中に止まることがある**：クラウドのセッションは原則 auto mode（分類モデルが操作を許可・ブロックし、確認を省くモード）で動く。ただし ask ルール（実行前に承認を求めるよう設定した操作）に該当する場合や、ブロックが続いた場合は承認待ちで停止する
- **上限がある**：通常のセッションと同じくサブスクリプションの使用量を消費する。そのうえで、スケジュール実行はアカウントあたり 1 時間に 100 回までなど、起動方法ごとに 1 時間あたりの上限が決められている
- **cron の最小間隔は 1 時間**：1 時間に 1 回より頻繁に動かす式は受け付けられない

## まとめ

「従業員なしで会社を立ち上げるマニュアル」の中身は、Claude Code を「Enter を押されるまで待つ道具」から「問題に気づいて自分で PR を出すチームメイト」に変える Routines のワークショップだった。登壇者の締めの言葉も、インフラの保守は Routines に任せて、自分の業務知識とプロセスの設計に集中しよう、というものだ。

人を置き換える話というより、任せる作業を見つける話だと受け取るのがよい。目安は、決まった時刻やイベントで始まり、成果を PR や通知で確かめられる作業だ。最初の 1 つは `/schedule` コマンドから作れる。

## 参考

- [Build a proactive agent workflow with Claude Code（Code w/ Claude 2026 セッションページ）](https://claude.com/code-with-claude/session/ldn-build-a-proactive-agent-workflow-with-claude-code)
- [Automate work with scheduled tasks（Claude Code 公式ドキュメント）](https://code.claude.com/docs/en/routines)
- [元投稿（X / @n0tisma）](https://x.com/n0tisma/status/2115050894433927470)
