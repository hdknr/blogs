---
title: "WSL2 への SSH 接続と sshd 自動起動"
description: "Windows から WSL2 へ SSH する構成の実務。~/.bashrc の早期 return で node が見つからない罠、セッション 0 で動かないタスク、15 秒でインスタンスが止まる instanceIdleTimeout"
date: 2026-09-02
lastmod: 2026-09-02
aliases: ["WSL2 SSH", "sshd 自動起動", "instanceIdleTimeout", "セッション 0", "ミラーモード", "Node.js not found on remote host"]
related_posts:
  - "/posts/2026/09/orca-wsl2-ssh-bashrc-node-not-found/"
  - "/posts/2026/09/wsl2-ssh-autostart-on-boot/"
tags: ["WSL2", "ssh", "Windows", "linux", "systemd", "nvm"]
---

## 概要

画面は Windows のまま、開発環境だけ WSL2（Ubuntu）側にまとめる構成。GUI クライアント（Orca など）から SSH でリモート接続する使い方が前提。

素直に見えて、実際には**シェル初期化・Windows のセッション分離・WSL のアイドル停止**という3つの独立した罠が待っている。いずれもエラーメッセージが原因を指さないため、知らないと詰まる。

## 罠1: `Node.js not found on remote host` — `~/.bashrc` の早期 return

SSH の失敗ではない。噛み合っているのは次の2つの設計判断である。

1. **nvm は読み込み行を `~/.bashrc` の末尾に追記する** — インストーラは `>>` で追記し、`nvm_detect_profile` は bash 環境でまず `~/.bashrc` を選ぶ
2. **Ubuntu の `~/.bashrc` は冒頭で非対話シェルを弾く**

```bash
# If not running interactively, don't do anything
case $- in
    *i*) ;;
      *) return;;
esac
```

`ssh host 'node -v'` のようにコマンドを直接指定した実行は非対話シェルを起動する。bash は標準入力がネットワーク接続に繋がっていること（＝ sshd 経由）を検出して `~/.bashrc` を読むが、**冒頭のガードで `return` するため末尾の nvm 行に永遠に到達しない**。

### 症状の非対称性

| 接続のしかた | `~/.bashrc` の扱い | 結果 |
| --- | --- | --- |
| `ssh user@localhost` でログイン（対話シェル） | 冒頭のガードを素通り | `node -v` が動く |
| コマンドを直接指定した実行（非対話シェル） | 冒頭で `return` | node が見つからない |

**「PowerShell から手で ssh すると動くのに、GUI クライアントからだと動かない」**という一見不可解な状況は、この構造の当然の帰結。**疎通確認が通ってもクライアント側では失敗しうる**（確認に使ったシェルの種類が違う）。

> この壊れ方はディストリビューション依存。Fedora/RHEL の既定 `.bashrc` にはこのガードが無いため最後まで読み進む。Debian/Ubuntu だけが冒頭で返る。

### 切り分け

```powershell
ssh <Ubuntuのユーザー名>@localhost "node -v; which node; echo $-"
```

### 対処

- **A（推奨）**: nvm の読み込みをガードより前に置く
- **B**: `~/.profile` に書く
- **C**: シェル初期化に依存させない

```bash
sudo ln -s "$(nvm which default)" /usr/local/bin/node
sudo ln -s "$(dirname "$(nvm which default)")/npm" /usr/local/bin/npm
```

C はどのシェルからでも同じ node を引ける。`nvm use` で切り替えてもリンク先は追随しないので張り直しが要るが、**エージェントに使わせる Node.js のバージョンを固定したい**なら欠点ではなく利点になる。

### 逆パターン: Windows 版 Node.js を掴んでいる

`which npm` が `/mnt/c/Users/...` を指す場合。WSL は既定で Windows 側の PATH を引き継ぐため、Windows の `node.exe` / `npm` を掴むことがある。切るなら `/etc/wsl.conf` に書く。

```ini
[interop]
appendWindowsPath=false
```

ただし `notepad.exe` のような Windows コマンドを名前だけで呼べなくなる。

## 罠2: タスクスケジューラの「ログオン不問」はセッション 0 で走る

Windows はログオンユーザーの対話セッションと、サービスが動く**セッション 0** を分離している。タスクスケジューラの「**ユーザーがログオンしているかどうかにかかわらず実行する**」は必然的にセッション 0 側で実行される。

そして**ストア版の WSL はセッション 0 からアクセスできない**（[microsoft/WSL Issue #9231](https://github.com/microsoft/WSL/issues/9231)、2022年11月に立ってから2026年9月現在も open）。

症状がたちが悪いのは**エラーが表に出ない**こと。WSL 側にコマンド実行の形跡が残らず、セッション 0 に `conhost.exe` のプロセスだけが作られる。タスクスケジューラの履歴上は「実行された」ように見えるのに sshd は上がっていない。

> **見分け方: タスク保存時にパスワードを聞かれたら、間違ったほうを選んでいる。** Entra ID 参加機では、そのパスワードはそもそも受け付けられない。

### 対処: トリガーは「ログオン時」

- **トリガー**: 「ログオン時」
- **セキュリティオプション**: 「ユーザーがログオンしているときのみ実行する」
- **プログラム/スクリプト**: `wsl.exe`
- **引数**: `-u root -- service ssh start`

コンソールウィンドウが一瞬開くのが気になるなら［全般］タブの「表示しない」にチェック。

ログオンせずに動かす必要がある場合は #9231 に NSSM でサービス化する方法と MSI 版 WSL を明示的に叩く方法の報告があるが、**有志のワークアラウンドであって公式手順ではない**。Windows のエディションやバージョンによって効いたり効かなかったりする。

## 罠3: sshd を上げてもインスタンスが 15 秒で止まる

WSL のアイドル停止には **VM のタイムアウトとインスタンスのタイムアウトという別々の2つ**がある。ここを混同すると、いくら設定しても止まる。

| 設定 | 対象 | 既定値 | Learn 記載 |
| --- | --- | --- | --- |
| `vmIdleTimeout`（`[wsl2]`） | WSL2 を動かしている VM | 60000 ms | あり |
| `instanceIdleTimeout`（`[general]`） | ディストリビューションのインスタンス | 15000 ms | **なし** |

**止まっているのは VM ではなくインスタンスのほう**で、それを制御する `instanceIdleTimeout` は Microsoft Learn の `.wslconfig` の表に存在しない。

### 対処

```ini
# %UserProfile%\.wslconfig
[general]
instanceIdleTimeout=-1

[wsl2]
vmIdleTimeout=-1
```

**`[general]` と `[wsl2]` の両方が要る。** 片方だけでは VM は生きたままインスタンスが落ちる、あるいはその逆になる。`instanceIdleTimeout` はミリ秒指定もできるので `300000`（5分）のような妥協点も取れる。

### 常時起動のコスト

`-1` は「勝手に落とすな」なので **WSL2 の VM が常駐してメモリを保持し続ける**。ノート PC で気になるならメモリ回収を併用する。

```ini
[wsl2]
memory=4GB

[experimental]
autoMemoryReclaim=gradual
```

## sudoers の NOPASSWD 行は使われない

定番手順に含まれる `sudoers` の NOPASSWD 行は、バッチが `wsl -u root` で走る限り**使われない**。要らない権限付与を残さないほうがいい。なお systemd を有効にするなら `service` コマンド自体が不要になる。

## ネットワーク: NAT とミラーモード

- **NAT（既定）**: `localhostForwarding` により Windows から WSL2 の `localhost:22` へ届く場合がある
- **ミラーモード**（Windows 11 22H2 以降）: Windows のインターフェイスを WSL2 に見せる

**ミラーモードは NAT の上位互換ではない。** Windows とポートが競合するようになり、`localhostForwarding` は設定ごと無視され、**LAN から WSL に直接届くようになる**。

## セキュリティ — 自動起動で前提が変わる

手で `service ssh start` していた頃は「使うときだけ開くポート」だったものが、自動起動にした瞬間**起動のたびに開きっぱなしのポート**になる。ミラーモードならそれが LAN から見える。

- **パスワード認証を切る** — `openssh-server` 導入直後の Ubuntu はパスワード認証が有効。公開鍵を置いて絞る

```text
PasswordAuthentication no
PubkeyAuthentication yes
```

- **ポート競合を確認する** — Windows 側に OpenSSH サーバーがあるとミラーモードで 22 番が競合する。WSL 側を 2222 番にずらすか `[experimental] ignoredPorts` で逃がす
- **待ち受け範囲を確認する** — `sudo ss -tlnp | grep sshd` で `0.0.0.0:22` か `127.0.0.1:22` かを見る

## 関連ページ

- [GitHub Actions のセキュリティ](/blogs/wiki/guides/github-actions-security/)
- [AI エージェントのシークレット管理](/blogs/wiki/guides/ai-agent-secret-management/)

## ソース記事

- [Orca から WSL2 へ SSH — Node.js not found on remote host の原因は ~/.bashrc の早期 return](/blogs/posts/2026/09/orca-wsl2-ssh-bashrc-node-not-found/) — 2026-09-01
- [WSL2 の sshd を Windows 起動時に自動起動する — セッション 0 と 15 秒タイムアウトの罠](/blogs/posts/2026/09/wsl2-ssh-autostart-on-boot/) — 2026-09-02
