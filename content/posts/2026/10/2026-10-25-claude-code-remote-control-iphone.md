---
title: "Claude Code を iPhone から遠隔操作する — Remote Control の設定と、通知でつまずいた話"
date: 2026-10-25
lastmod: 2026-10-25
slug: "claude-code-remote-control-iphone"
description: "Mac で走らせている Claude Code のセッションを、外出先の iPhone から見て答えるために Remote Control を設定した手順と、プッシュ通知が届かなかった原因（No mobile registered・使用中判定・claude rc の待ち受けへの誤接続）の切り分け、そして不在中に止まらないための設定をまとめる。"
draft: false
categories: ["AI/LLM"]
tags: ["claude-code", "claude", "Remote Control", "プッシュ通知", "ios", "macOS"]
---

Mac で長時間走らせている Claude Code のセッションを、外出先の iPhone から見て、質問や権限確認にも答えたい。そのために Remote Control を設定しました。この記事はその手順と、つまずいた点のまとめです。

前提として、Mac では Claude Code に大量の課題を一晩かけて自律実行させていました。利用上限や権限確認で止まったら、帰宅途中に iPhone から状況を見て、必要なら答えたいという用途です。

- 確認した環境：Claude Code 2.1.310（macOS）、iPhone の Claude アプリ、Team プラン
- 一次資料：<https://code.claude.com/docs/en/remote-control.md>

---

## 結論（先に要点）

| やりたいこと | 結果 | 必要なこと |
| --- | --- | --- |
| iPhone からセッションを見る・答える（ミラー） | **できた** | Mac で `/remote-control`。iPhone の Claude アプリで**同じアカウント・同じ組織**にサインイン |
| 止まったときに iPhone へプッシュ通知 | **後日、届いた**（2 章の「解決」） | `/config` の通知設定。Mac と iPhone を同じアカウントにそろえる。試験は、どちらの端末でも操作していないときに行う |
| 不在中に止まらないようにする | **設定済み** | `autoContinueAtUsageLimit` などの設定（後述） |

**ミラーと通知は別の仕組みです。** ミラーがつながっていても、`/config` に「No mobile registered」と出ていれば通知は届きません。

---

## 1. Remote Control でミラーする

### Mac 側

1. 動いている Claude Code の入力欄で、`/remote-control`（短縮形は `/rc`）と打ちます。
   - **先頭に空白を入れないこと。** 空白があるとコマンドではなく、ただのメッセージとして Claude に送られます（実際に一度やりました）。
   - Claude 自身はこのコマンドを実行できません。人間が打つ必要があります。
2. 「Enable Remote Control」を選びます。会話はそのまま引き継がれ、`/rc active` と出れば接続済みです。
3. もう一度 `/remote-control` と打つと、セッションの URL と QR コードが出ます。

**セッションを再起動する必要はありません。** 動いている作業を止めずに有効にできます。

### iPhone 側

1. Claude アプリ（iOS）を入れます。Mac で `/mobile` と打つと、App Store への QR コードが出ます。
2. Mac の Claude Code と**同じアカウント**でサインインします。Team / Enterprise プランなら**同じ組織**を選んでいることも確かめます。
3. 次のどちらかでセッションを開きます。
   - Mac に出た QR コードを読み取る。
   - アプリの **Code タブ**から、そのセッションを選ぶ。

**別ルート：アプリの「デバイスを追加」から組む。** アプリの「デバイスを追加」を使う場合は、Mac で**別のターミナルタブ**を開き、`claude rc` を実行します（初回は `Enable Remote Control? (y/n)` に `y`）。表示されたコードを iPhone で読み取ります。

- 作業中のセッションのタブは閉じないこと。閉じると作業も止まります。
- `claude rc` は別プロセスなので、組み終わったら `Ctrl-C` で止めてかまいません。

今回はこのルートで「このセッションが iPhone の Claude Code にミラーされた」状態になりました。

### アカウントを切り替えたら、つなぎ直す

Mac 側のログインアカウントを切り替えると、Remote Control は切れます。iPhone 側も同じアカウントでログインし直したうえで、次の手順でつなぎ直します。

1. Mac で `/remote-control` を打ち、「Enable Remote Control」を選ぶ。
2. iPhone の Code タブからセッションを選ぶ。一覧に出なければ、`/remote-control` を打って出る QR コードを読む。

これで iPhone からのメッセージが Mac のセッションに届くことを確認しました。

### 注意点

- **Team / Enterprise プラン**では、組織の Owner が <https://claude.ai/admin-settings/claude-code> で Remote Control を有効にしておく必要があります（既定はオフ）。
- Mac のターミナルで `claude` が動き続けている必要があります。閉じると切れます。
- API キーでの認証をしている場合や、`ANTHROPIC_BASE_URL`・`CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC` を設定している場合は、Remote Control を使えないことがあります。事前に環境変数を確かめておくと安心です。

---

## 2. プッシュ通知（一度つまずき、後日届いた）

### 設定の場所

| どこで | 何を |
| --- | --- |
| **Mac**（`/config`） | 「**Push when actions required**」をオン。権限確認や質問で止まったときに通知します。 |
| **Mac**（`/config`・任意） | 「**Push when Claude decides**」をオン。Claude が自分の判断で通知を送れるようになります（例：全課題が終わった）。 |
| **iPhone**（設定 → 通知 → Claude） | 「通知を許可」、ロック画面、通知センターをオン |
| **iPhone**（設定 → 集中モード） | 夜間にも気づきたいなら、Claude を「通知を許可するアプリ」に追加 |

`/config` は Mac のターミナル専用のコマンドで、iPhone のアプリからは実行できません。

`~/.claude/settings.json` に直接書く場合、「Push when actions required」は `inputNeededNotifEnabled` に当たるようです。`/config` のツール結果に `inputNeededNotifEnabled` と `agentPushNotifEnabled` が並んで返ってきたためで、ドキュメントで確かめたわけではありません。

### 切り分けの方法：Claude に試しの通知を送らせる

Claude Code の通知ツールは、送れなかったときに理由を返します。これがいちばん早い切り分けでした。

- `Push not sent — mobile push is disabled in /config.`：「Push when Claude decides」がオフ
- ターミナルを使用中なので送らない：Mac の画面をロックしてから、もう一度送らせる
- 「送れた」のに届かない：原因は iPhone 側（通知の許可・集中モード・サインインしているアカウント）

**ターミナルに打鍵中か、ターミナルが前面にあるあいだは、通知は送られません。** 「通知が来ない」と思ったら、まずこれを疑います。

### 今回つまずいた点：「No mobile registered」

`/config` に **「No mobile registered」** と出ていました。iPhone がこのアカウントの通知先として 1 台も登録されていない、という意味です。

試したこと：

1. iPhone の「設定 → 通知」に Claude があり、「許可・即時通知」になっていることを確かめた。ここは問題なし。
2. アプリを開き直しても、通知の許可を求める画面は出なかった。
3. Remote Control のミラーは成功した。それでも警告は消えなかった。

ここから分かることは次のとおりです。

- **Remote Control が組織で有効になっていることは確か**です（ミラーできているため）。組織設定で通知そのものを止められるかは、ドキュメントでは確かめられませんでした。
- いちばん疑わしいのは **iPhone のアプリと Mac で、アカウントか組織が食い違っていること**です。Code タブにセッションが出れば、両方とも合っています。
- 起動中のセッションは、起動時の登録情報を持ったままになっている可能性があります。**新しく起動したプロセス**（別タブの `claude rc` など）で `/config` を開くと、どちらなのかを切り分けられます。

### 解決：同じアカウントで入り直し、「使用中」を外して試したら届いた

後日、次の手順で iPhone に通知が届きました。

1. **Mac と iPhone を同じアカウントでログインし直した。** これで「mobile push is disabled」や「No mobile registered」では止まらなくなりました。
2. **iPhone が `claude rc` の待ち受けではなく、このセッションにつながっていることを確かめた。**
   - iPhone のセッション名が `macstudio-local-agile-tide` になっていました。これは `claude rc` の画面に出ていた名前と同じで、iPhone は待ち受けのほうにつながっていたことになります。そこから送ったメッセージは、作業中のセッションに届きません。
   - `claude rc` を止め、作業中のセッションで `/remote-control` を打ちました。2 回目以降は `/rc active` ではなく QR コードを出す選択肢が出るので、それで出した QR コードを iPhone で読み直しました。
   - iPhone から 1 行送り、それが作業中のセッションに届くことを確かめました。
3. **「使用中」を外してから送らせた。** iPhone から操作しているあいだも、Mac のターミナルを使っているあいだと同じく「使用中」と判定され、通知は省かれました（`Not sent — this terminal is active`）。そこで Claude に `sleep 120` のバックグラウンドタイマーを動かしてもらい、そのあいだに Mac の画面をロックし、iPhone のアプリを閉じました。2 分後に送らせた通知は `Terminal notification sent. Mobile push requested.` と返り、iPhone に届きました。

**教訓：通知の試験は、Mac でも iPhone でもセッションを操作していないときに行う。** 操作中に「通知を送って」と頼むと、毎回「使用中」で省かれます。

**それでも駄目なら：** `claude doctor` を実行するか、組織の Owner に管理画面の設定を見てもらうのが次の手です。

---

## 3. 通知が無くても止まらないようにする設定

通知はあくまで「止まったことに気づく」ための手段です。そもそも止まらないようにする設定のほうが効きます。`~/.claude/settings.json` に次を入れました。

```json
{
  "autoContinueAtUsageLimit": true,
  "inputNeededNotifEnabled": true,
  "askUserQuestionTimeout": "5m"
}
```

- `autoContinueAtUsageLimit`：利用上限で止まったら、上限が戻るのを待って自動で続けます。
- `inputNeededNotifEnabled`：権限確認や質問で止まったときに通知します（端末の登録が済んでいる場合）。
- `askUserQuestionTimeout`：質問が出ても、5 分で自動的に先へ進みます。

機械の側では、次の 2 つも必要です。

- **スリープさせない。** 別のターミナルで `caffeinate -dims` を動かし、電源につないで蓋を開けたままにします。
- **ネットワークを切らない。**

よく使う読み取り系のコマンドは、許可ルール（`permissions.allow`）に入れておくと権限確認で止まりにくくなります。

---

## まとめ

1. ミラーは簡単です。Mac で `/remote-control` を打ち、iPhone の Claude アプリを**同じアカウント・同じ組織**にして Code タブから開くだけです。
2. 通知は別の仕組みです。`/config` に「No mobile registered」が出ていないことを、まず確かめます。
3. 通知の切り分けは、Claude に試しの通知を送らせて、返ってきた理由を見るのが早道です。試験は、Mac でも iPhone でも操作していないときに行います（タイマーで遅らせて送らせる）。
4. `claude rc`（新しいセッションの待ち受け）と `/remote-control`（いまのセッションのミラー）は別物です。iPhone で開いたセッション名で、どちらにつながっているかを確かめます。
5. 不在中の運用では、通知よりも「止まらない設定」（自動継続・質問のタイムアウト・スリープ防止）のほうが効きます。
