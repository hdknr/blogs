---
title: "Claude Code Remote Control で iPhone から遠隔操作する"
description: "Mac で走る Claude Code のセッションを iPhone からミラーして答える設定、プッシュ通知の切り分け、不在中に止まらないための設定"
date: 2026-10-30
lastmod: 2026-10-30
aliases: ["Remote Control", "/remote-control", "/rc", "claude rc", "Claude Code モバイル通知"]
related_posts:
  - "/posts/2026/10/claude-code-remote-control-iphone/"
tags: ["claude-code", "Remote Control", "プッシュ通知", "macOS"]
---

## 概要

Remote Control は、手元の Mac で動いている Claude Code のセッションを iPhone の Claude アプリ（Code タブ）にミラーし、外出先から状況確認や権限確認・質問への回答をできるようにする機能。**ミラーとプッシュ通知は別の仕組み**で、ミラーできていても通知が届くとは限らない。長時間の自律実行では、通知より「そもそも止まらない設定」のほうが効く。

## 詳細

### ミラーの手順

1. Mac の Claude Code の入力欄で `/remote-control`（短縮 `/rc`）を打ち、「Enable Remote Control」を選ぶ。**先頭に空白を入れるとただのメッセージとして送られる**。Claude 自身はこのコマンドを実行できない
2. 実行中の作業を止めずに有効にでき、再起動は不要
3. iPhone の Claude アプリに **Mac と同じアカウント・同じ組織**でサインインし、Code タブからセッションを開くか、`/remote-control` を再度打って出る QR コードを読む

前提条件:

- Team / Enterprise プランでは組織の Owner が管理画面で Remote Control を有効にする（既定オフ）
- Mac 側の `claude` プロセスが動き続けていること
- API キー認証や `ANTHROPIC_BASE_URL`、`CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC` の設定下では使えないことがある
- Mac 側のアカウントを切り替えると切れるので、つなぎ直す

### `claude rc` と `/remote-control` は別物

| コマンド | 何につながるか |
|---|---|
| `/remote-control`（セッション内） | いま作業中のセッションのミラー |
| `claude rc`（別ターミナル） | 新しいセッションの待ち受け（アプリの「デバイスを追加」用） |

iPhone で開いたセッション名が `claude rc` の画面に出た名前と同じなら、待ち受けのほうにつながっている。そこから送ったメッセージは作業中のセッションに届かない。

### プッシュ通知

| 場所 | 設定 |
|---|---|
| Mac の `/config` | 「Push when actions required」（権限確認・質問で止まったとき）、任意で「Push when Claude decides」 |
| iPhone | 設定 → 通知 → Claude を許可。夜間も受けるなら集中モードの許可アプリに追加 |

切り分けのコツ:

- `/config` に **「No mobile registered」** と出ていれば届かない。Mac と iPhone のアカウント・組織の食い違いを疑い、両方を同じアカウントで入り直す
- Claude に試しの通知を送らせると、送れなかった理由が返る（`mobile push is disabled in /config`、`this terminal is active` など）
- **Mac のターミナルを操作中、または iPhone から操作中は「使用中」と判定されて通知が省かれる**。試験は `sleep 120` などで遅らせ、その間に画面をロックしアプリを閉じて行う
- それでも駄目なら `claude doctor` か、Owner に管理画面を確認してもらう

### 不在中に止まらないための設定

`~/.claude/settings.json` の例:

```json
{
  "autoContinueAtUsageLimit": true,
  "inputNeededNotifEnabled": true,
  "askUserQuestionTimeout": "5m"
}
```

- `autoContinueAtUsageLimit`: 利用上限から回復したら自動で続行
- `askUserQuestionTimeout`: 質問が出ても一定時間で先へ進む
- 機械側は `caffeinate -dims` でスリープを防ぎ、ネットワークを切らない
- よく使う読み取り系コマンドは `permissions.allow` に入れ、権限確認で止まりにくくする

PC を閉じても動かしたいなら、Anthropic のクラウドで動く scheduled tasks（旧 Routines）が選択肢になる（[Claude Code](/blogs/wiki/tools/claude-code/) 参照）。

## 関連ページ

- [Claude Code](/blogs/wiki/tools/claude-code/) — 本体と Routines（scheduled tasks）
- [claude -p によるヘッドレス実行](/blogs/wiki/guides/claude-p-headless/) — 対話画面を持たない自動化の別ルート
- [エージェントループ設計](/blogs/wiki/concepts/agent-loop-design/) — 長時間の自律実行の設計

## ソース記事

- [Claude Code を iPhone から遠隔操作する — Remote Control の設定と、通知でつまずいた話](/blogs/posts/2026/10/claude-code-remote-control-iphone/) — 2026-10-25
