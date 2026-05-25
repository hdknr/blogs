---
title: "Claude Code でMacをセキュリティ監査する — Pieter Levels流、一言頼むだけで未設定項目を洗い出す方法"
date: 2026-05-21
lastmod: 2026-05-21
slug: "pieter-levels-claude-code-security-audit-mac"
draft: false
source_url: "https://github.com/hdknr/blogs/issues/1#issuecomment-4504067702"
categories: ["セキュリティ"]
tags: ["claude-code", "security", "macOS", "FileVault", "セキュリティ監査"]
---

Pieter Levels（@levelsio）は Claude Code を使って自分の MacBook Pro をセキュリティ監査した。すると、設定していなかった項目が次々と見つかったという。その方法はシンプルで、Claude Code に「このコンピューターをセキュリティ監査して」と頼むだけだ。

## Pieter Levels のツイート

Pieter Levels は PhotoAI（月間収益 $100K）や RemoteOK（同 $44K）など複数のプロダクトを一人で運営するインディー開発者で、VPS サーバーの管理にも Claude Code を活用している。

彼のツイートの要点は以下のとおり：

> A nice way to stay safe is to ask Claude Code to audit your devices
>
> I do same on my VPS servers, so today I tried it on my MacBook Pro and it's pretty good at it too
>
> It founds lots of stuff that was not secured, I actually forgot to enable FileVault when I got this new MBP in

（要訳：デバイスの安全を保つ手軽な方法は、Claude Code に監査を頼むことだ。VPS サーバーでも同じことをやっていたが、今日は MacBook Pro で試してみた。かなりうまくいった。保護されていない項目がたくさん見つかり、新しい MacBook Pro を入手してから FileVault を有効にし忘れていたことにも気づいた。）

新しい MacBook Pro を入手してから **FileVault（ディスク暗号化）を有効にし忘れていた**という事実が、監査で発覚した典型例だ。これは見落としがちながら、端末を紛失・盗難された際に致命的になるリスクがある。

## なぜ Claude Code が使えるのか

Claude Code は通常、コード生成やリファクタリングに使うツールだが、macOS には豊富なシステム状態の確認コマンドが存在する。Claude Code はこれらのコマンドを組み合わせて実行できるため、セキュリティチェックリストを自動的に網羅できる。

たとえば以下のような macOS コマンドを Claude Code は活用できる：

```bash
# FileVault の状態確認
fdesetup status

# ファイアウォールの状態確認
/usr/libexec/ApplicationFirewall/socketfilterfw --getglobalstate

# SIP（System Integrity Protection）の確認
csrutil status

# Gatekeeper の確認
spctl --status

# SSH の設定確認
sudo launchctl list | grep ssh

# 自動ログインの確認
defaults read /Library/Preferences/com.apple.loginwindow autoLoginUser 2>/dev/null

# スクリーンロックの確認
pmset -g | grep displaysleep
```

Claude Code はこれらを自動的に実行し、問題のある設定を日本語でわかりやすく報告してくれる。

## 実際の使い方

Claude Code を開き、以下のように頼むだけだ：

```
このコンピューターをセキュリティ監査してください。
macOS のセキュリティ設定を確認して、問題があれば指摘してください。
```

より詳細な監査を求める場合は以下のように指示する：

```
macOS のセキュリティ設定を包括的に監査してください。
以下の項目を確認してください：
- FileVault（ディスク暗号化）
- ファイアウォール
- SIP（System Integrity Protection）
- Gatekeeper
- SSH の設定
- 自動ログインの設定
- スクリーンロックのタイムアウト
- インストール済みアプリのアクセス権（カメラ、マイク、位置情報など）
- ネットワーク共有の設定
結果を重大度別に整理して報告してください。
```

VPS サーバーに対しては：

```
このサーバーをセキュリティ監査してください。
SSH、ファイアウォール、未使用ポート、sudoers 設定、
不審なプロセスや cron ジョブを確認してください。
```

## よく見つかる問題

実際に試してみると、以下のような項目が見落とされていることが多い：

### 1. FileVault が無効
新しい Mac に移行した直後や、クリーンインストール後に忘れがち。有効にしないと端末盗難時にデータがそのまま読まれる。

```bash
# 有効化
sudo fdesetup enable
```

### 2. ファイアウォールが無効
macOS のファイアウォールはデフォルトで無効の場合がある。

システム設定 → ネットワーク → ファイアウォール から有効化できる。

### 3. SSH が開きっぱなし
リモートログイン機能を以前に有効にしてそのままにしている場合がある。

```bash
# SSH サービスを無効化（macOS Ventura 以降の推奨コマンド）
sudo launchctl disable system/com.openssh.sshd

# 旧バージョン向け（Monterey 以前）
# sudo launchctl unload -w /System/Library/LaunchDaemons/ssh.plist
```

### 4. スクリーンロックまでの時間が長すぎる
席を離れた際のリスクを減らすため、1〜5分程度に設定するのが望ましい。

### 5. アプリへの過剰な権限付与
カメラ、マイク、位置情報へのアクセス権が不要なアプリに付与されたままになっている。

## 注意点と限界

この件についてリツイートした @L_go_mrk（X でマーケティング戦略と Claude Code 導入事例を発信しているアカウント）が指摘しているように、「Claude Code に全任せするだけでもだめ」という点は重要だ。

- Claude Code はコマンドを実行して結果を解釈するが、**すべての脆弱性を網羅するわけではない**
- マルウェアの検出や高度な侵入検知は、専用のセキュリティツール（Malwarebytes、LittleSnitch など）が必要
- 報告された問題の修正は人間が判断・実行する必要がある
- 定期的なセキュリティアップデートの適用は別途管理が必要

それでも、@L_go_mrk が言うように「人間が全部管理するよりは遥かに簡単」であることは確かで、定期的にこの監査を習慣にするだけで、基本的なセキュリティホールを防げる。

## まとめ

| 方法 | コスト | 効果 |
|------|--------|------|
| 専門家によるペネトレーションテスト | 高（数十〜数百万円） | 高 |
| Claude Code による自動監査 | 低（Claude Code 利用料のみ） | 中 |
| 手動チェックリスト | 中（作業時間） | 中〜低（見落としあり） |
| 放置 | ゼロ | リスク大 |

インディー開発者として一人でサービスを運営する Pieter Levels が実践しているこの方法は、コストと効果のバランスが優れている。完全ではないが、「やっていない」よりは圧倒的に安全だ。

まず Claude Code に「このコンピューターをセキュリティ監査して」と頼んでみよう。新しい Mac に乗り換えたばかりの人、しばらくセキュリティ設定を見直していない人には特におすすめだ。
