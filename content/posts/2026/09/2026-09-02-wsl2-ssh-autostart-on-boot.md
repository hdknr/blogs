---
title: "WSL2 の sshd を Windows 起動時に自動起動する — セッション 0 と 15 秒タイムアウトの罠"
date: 2026-09-02
lastmod: 2026-09-02
slug: "wsl2-ssh-autostart-on-boot"
draft: false
source_url: "https://github.com/hdknr/blogs/issues/572#issuecomment-5502273864"
description: "WSL2 の SSH 自動起動は、タスクスケジューラのセッション 0 と、instanceIdleTimeout による 15 秒でのインスタンス停止という 2 つの罠で止まる。どちらも microsoft/WSL の Issue で裏が取れる。"
categories: ["ツール/開発環境"]
tags: ["WSL2", "ssh", "Windows", "linux", "systemd", "タスクスケジューラ"]
---

前回、[Orca から WSL2 へ SSH 接続する話](/blogs/posts/2026/09/orca-wsl2-ssh-bashrc-node-not-found/)を書いた。画面は Windows のまま、開発環境だけ WSL2 側にまとめる構成だ。

その構成で次に来る不満は決まっている。**再起動のたびに Ubuntu を開いて `sudo service ssh start` を叩くのが面倒**、というやつだ。当然「Windows の起動と同時に WSL と sshd を上げてしまえばいい」という発想になる。

ところが、この用途でネット上に出回っている定番手順を裏取りしていくと、**一番目立つ設定項目が、まさに動かない組み合わせ**だった。しかもそれは公式ドキュメントには書かれておらず、microsoft/WSL の Issue を追わないと出てこない。

この記事では、定番手順のどこが詰まるのかを主な罠 2 つを軸に、周辺の前提（sudoers・systemd・ネットワーク）まで含めて整理する。

> **前置き**: 筆者の手元は macOS で、Windows + WSL2 の実機検証はしていない。ここで「確認した」と書いているのは、Microsoft Learn の WSL ドキュメントと microsoft/WSL リポジトリの Issue という、実機なしで裏が取れる範囲に限る。挙動は WSL のバージョンと Windows のビルドでかなり変わるため、最後に挙げる確認コマンドで自分の環境の実際を見てほしい。

## 先に結論

- タスクスケジューラの「**ユーザーがログオンしているかどうかにかかわらず実行する**」を選ぶと、タスクは**セッション 0** で走る。ストア版 WSL はセッション 0 から起動できず、これは 2026 年 9 月時点で[未解決の Issue](https://github.com/microsoft/WSL/issues/9231) のままだ。選ぶべきは「ユーザーがログオンしているときのみ実行する」。

  > ここで言う「ストア版」は、Microsoft Store から入る現行の WSL のこと。Windows のオプション機能として最初から入っている旧来の**インボックス版**とは別物で、`wsl --version` がバージョンを返せばストア版だ。以下の話はストア版が前提になる。

- sshd をデーモンとして上げても、**WSL のインスタンスは追跡対象プロセスが尽きると既定 15 秒で停止する**。止めないためには `.wslconfig` の `instanceIdleTimeout=-1` が要るが、この設定は Microsoft Learn の `.wslconfig` の表に載っていない。
- 定番手順に含まれる `sudoers` の NOPASSWD 行は、バッチが `wsl -u root` で走る限り**使われない**。要らない権限付与を残さないほうがいい。

![WSL2 の sshd 自動起動の 2 経路を比較した図。ログオン時トリガーはアイドル停止を .wslconfig で回避して接続に到達するが、ログオン不問トリガーはセッション 0 で行き止まりになる](/blogs/images/wsl2-ssh-autostart-on-boot.png)

## 出回っている定番手順

まず、検証の対象にした手順を整理しておく。おおむねこの 4 ステップで説明されることが多い。

**1. WSL 側に SSH サーバーを入れる**

```bash
sudo apt update
sudo apt install openssh-server -y
```

**2. パスワードなしで SSH サービスを起動できるようにする**

```bash
echo 'your-username ALL=(root) NOPASSWD: /usr/sbin/service ssh start' | sudo tee /etc/sudoers.d/service-ssh-start
```

**3. Windows 側にバッチファイルを置く**

```bat
@echo off
wsl -u root -- service ssh start
```

**4. タスクスケジューラに登録する**

- トリガー: **スタートアップ時**
- セキュリティオプション: **ユーザーがログオンしているかどうかにかかわらず実行する**
- 操作: 手順 3 のバッチファイル

手順 1 と 3 は問題ない。`wsl -u root -- <コマンド>` は正しい書き方で、`--` 以降が Linux 側に渡る。手順 2 は後述するとおり、この経路では使われない。詰まるのは 4 と、その先だ。

## 罠 1: 「ログオンしているかどうかにかかわらず実行する」はセッション 0 で走る

Windows は、ログオンしたユーザーの対話セッションと、サービスが動く**セッション 0** を分離している。Windows Vista 以降、サービスは常にセッション 0 に置かれ、ユーザーの画面とは切り離される。

タスクスケジューラの「ユーザーがログオンしているかどうかにかかわらず実行する」は、**ログオンしていなくても走らせる**という指定なので、必然的にセッション 0 側で実行される。「スタートアップ時」トリガーと組み合わせれば、なおさら誰もログオンしていない状態で走ることになる。

そして、ここがこの記事の本題だ。**ストア版の WSL はセッション 0 からアクセスできない。**

microsoft/WSL の [Issue #9231「Store WSL isn't accessible from Session 0」](https://github.com/microsoft/WSL/issues/9231)がその報告だ。2022 年 11 月に立ってから **2026 年 9 月現在も open** で、コメントは 160 件を数える。同じ症状を「スケジュールされたタスクに影響する」と報告した [Issue #9271](https://github.com/microsoft/WSL/issues/9271) は、この #9231 の重複として閉じられた。

症状がたちが悪いのは、**エラーが表に出ない**ことだ。#9271 の報告によれば、WSL 側にはコマンドが実行された形跡が残らず、セッション 0 に `conhost.exe` のプロセスだけが作られる。タスクスケジューラの履歴上はタスクが「実行された」ように見えるのに、sshd は上がっていない。「設定したのに繋がらない」という一番デバッグしづらい形で失敗する。

### どうするか: トリガーは「ログオン時」にする

デスクトップ機なら、**素直にログオンを前提にする**のが一番はっきりしている。

- **トリガー**: 「ログオン時」
- **セキュリティオプション**: 「ユーザーがログオンしているときのみ実行する」

自分のマシンで自分がログオンして使う分には、これで実用上まったく困らない。開発機の WSL に SSH したいという動機なら、そもそもログオンしているはずだ。

なお、バッチファイルを別途作らなくても、タスクの「操作」に直接こう書けば済む。

- プログラム/スクリプト: `wsl.exe`
- 引数の追加: `-u root -- service ssh start`

この設定ではタスク実行時にコンソールウィンドウが一瞬開くので、気になるなら [全般] タブの「**表示しない**」にチェックを入れておく。

**ログオンせずに動かす必要がある場合**（サーバー機に RDP で入るだけ、といった用途）は、#9231 のスレッドに回避策の報告がある。NSSM でサービス化する方法と、MSI 版 WSL を追加インストールして `C:\Program Files\WSL\wsl.exe` を明示的に叩く方法だ。ただしこれらは**有志のワークアラウンドであって公式手順ではない**し、スレッドを読むと Windows のエディションやバージョンによって効いたり効かなかったりしている。恒久的な解決を当てにする対象ではない。

## 罠 2: sshd を上げてもインスタンスが 15 秒で止まる — instanceIdleTimeout

罠 1 を避けてログオン時トリガーにしたとして、次に来るのがこちらだ。

WSL のアイドル停止には、**VM のタイムアウトとインスタンスのタイムアウトという別々の 2 つ**がある。ここを混同すると、いくら設定しても止まる。

| 設定 | 対象 | 既定値 | Learn 記載 |
| --- | --- | --- | --- |
| `vmIdleTimeout`（`[wsl2]`） | WSL2 を動かしている VM | 60000 ミリ秒 | あり |
| `instanceIdleTimeout`（`[general]`） | ディストリビューションのインスタンス | 15000 ミリ秒 | **なし** |

`vmIdleTimeout` のほうは [Microsoft Learn の `.wslconfig` の表](https://learn.microsoft.com/ja-jp/windows/wsl/wsl-config)に載っている。しかし**止まっているのは VM ではなくインスタンスのほう**で、そちらを制御する `instanceIdleTimeout` は、同じページの表に存在しない。

この挙動そのものは古くから報告がある。[Issue #8661](https://github.com/microsoft/WSL/issues/8661) の再現手順はこうだ。`/etc/wsl.conf` の `[boot] command` で `cron` を起動し、シェルを抜ける。すると `cron` が動いているにもかかわらず、15 秒後にインスタンスが `STOPPED` になる。この Issue は「systemd の挙動から見て仕様」として 2022 年 10 月にクローズされた。

そして 2025 年、[Issue #13291](https://github.com/microsoft/WSL/issues/13291) で「`vmIdleTimeout=-1` を設定しているのに ollama や sshd が落ちる」という報告が上がる。

### どうするか: .wslconfig に instanceIdleTimeout=-1 を書く

ここで WSL のメンテナ（OneBlue 氏）が回答しているのが、次の設定だ。

```ini
# %UserProfile%\.wslconfig
[general]
instanceIdleTimeout=-1

[wsl2]
vmIdleTimeout=-1
```

`[general]` セクションと `[wsl2]` セクションの**両方**が要る。片方だけでは、VM は生きたままインスタンスが落ちる、あるいはその逆になる。同じスレッドでメンテナが「これはドキュメント化すべきだ」と書いており、実際 2026 年 6 月更新版の Learn のページを見てもまだ載っていない。

`instanceIdleTimeout` はミリ秒でも指定できるので、常時起動まではしたくないなら `instanceIdleTimeout=300000`（5 分）のような妥協点も取れる。

### 常時起動のコスト: メモリと autoMemoryReclaim

`-1` はつまり「勝手に落とすな」という指定なので、**WSL2 の VM が常駐してメモリを保持し続ける**。ノート PC で気になるなら、メモリ回収を併用する手がある。

```ini
[wsl2]
memory=4GB

[experimental]
autoMemoryReclaim=gradual
```

`autoMemoryReclaim` は Learn の `[experimental]` セクションに載っている設定で、`gradual` はキャッシュメモリをゆっくり回収する。ただし実験的機能という位置づけなので、そのつもりで使う。

## sudoers の行は、この手順では使われない

定番手順の 2 番目、`/etc/sudoers.d/service-ssh-start` を置くステップについて。

```bash
echo 'your-username ALL=(root) NOPASSWD: /usr/sbin/service ssh start' | sudo tee /etc/sudoers.d/service-ssh-start
```

これは「一般ユーザーがパスワードなしで `sudo service ssh start` を実行できるようにする」設定だ。だが手順 3 のバッチは `wsl -u root` で、**最初から root として実行している**。sudo は一度も介在しない。

つまりこの行は、この手順の中では使われないまま `/etc/sudoers.d/` に残る。害が大きいわけではないが、`sudoers` に不要なエントリを残すのは避けたい。**WSL の中から一般ユーザーとして手で `sudo service ssh start` を叩く運用も併用する**なら意味があるので、そこは自分の使い方次第で判断すればいい。

## systemd を使うなら service コマンド自体が不要になる

もう一つ、そもそも論として。WSL は systemd をサポートしている。前回の記事では systemd 有効を前提に `systemctl enable --now ssh` で導入したが、ここでは systemd を切ったままの環境も含めて整理しておく。

```ini
# /etc/wsl.conf
[boot]
systemd=true
```

これはストア版 WSL の **0.67.6 以降**で使える。`wsl --version` が認識されないなら古いインボックス版なので、先に更新が要る。設定後は PowerShell から `wsl --shutdown` して入れ直す。

systemd が動いていれば、SSH の自動起動は Linux 側の作法で済む。

```bash
sudo systemctl enable ssh
sudo systemctl start ssh
```

これで **WSL インスタンスが起動するたびに** sshd が上がるので、Windows 側のバッチから `service ssh start` を叩く必要がなくなる。

ただし勘違いしないでほしいのは、これが解決するのは「インスタンス起動後に sshd を上げる」部分だけだということだ。**WSL インスタンスそのものを起動するトリガーは、依然として Windows 側に要る**。つまりタスクスケジューラの出番は消えない。変わるのはバッチの中身だけだ。`wsl -u root -- service ssh start` が `wsl -d Ubuntu -e true` のような「起動するだけ」の呼び出しになる。罠 1 と罠 2 はそのまま残る。

なお `wsl.conf` の `[boot] command` にコマンドを書く手もあるが、Learn には「Boot 設定は **Windows 11 と Server 2022 でのみ利用可能**」と明記されている。加えて #8661 の通り、`[boot] command` で起動したデーモンはインスタンスの延命に寄与しない。

## ネットワークの前提: NAT とミラーモード

sshd が上がっても、そこに届かなければ意味がない。WSL2 は既定で NAT の下にいるため、接続経路の話は別途ついて回る。

- **NAT（既定）**: `localhostForwarding` により、Windows から WSL2 の `localhost:22` へ届く場合がある
- **ミラーモード**: Windows のインターフェイスを WSL2 に見せる方式。Windows 11 22H2 以降

このあたりは前回の記事の[ミラーモードの副作用](/blogs/posts/2026/09/orca-wsl2-ssh-bashrc-node-not-found/#ミラーモードの副作用)で詳しく書いた。要点だけ再掲すると、ミラーモードは NAT の上位互換ではない。**Windows とポートが競合するようになり、`localhostForwarding` は設定ごと無視され、LAN から WSL に直接届くようになる。**

最後の点は、自動起動と組み合わせると意味が変わる。手で `service ssh start` していた頃は「使うときだけ開くポート」だったものが、自動起動にした瞬間**起動のたびに開きっぱなしのポート**になる。ミラーモードなら、それが LAN から見える。

## セキュリティは自動起動で前提が変わる

というわけで、自動起動を入れるなら最低限これは押さえておきたい。

**パスワード認証を切る。** `openssh-server` を入れた直後の Ubuntu はパスワード認証が有効だ。常時上がっているポートをパスワードで守るのは無理がある。公開鍵を置いたうえで `/etc/ssh/sshd_config` を絞る。

```text
PasswordAuthentication no
PubkeyAuthentication yes
```

**ポート競合を確認する。** Windows 側に OpenSSH サーバーが入っていると、ミラーモードでは 22 番が競合する。WSL 側を 2222 番などにずらすか、`.wslconfig` の `[experimental] ignoredPorts` で逃がす。

**待ち受け範囲を確認する。** `sudo ss -tlnp | grep sshd` で、`0.0.0.0:22` なのか `127.0.0.1:22` なのかを見ておく。

## 直した手順: タスクスケジューラと .wslconfig の最終形

以上を反映した最終形はこうなる。

**1. WSL 側**

```bash
sudo apt update
sudo apt install openssh-server -y
```

公開鍵を `~/.ssh/authorized_keys` に置き、`/etc/ssh/sshd_config` で `PasswordAuthentication no` にする。systemd を有効にしているなら、あわせて `sudo systemctl enable ssh`。

**2. Windows 側 — `%UserProfile%\.wslconfig`**

```ini
[general]
instanceIdleTimeout=-1

[wsl2]
vmIdleTimeout=-1
```

**3. Windows 側 — タスクスケジューラ**

- [全般] セキュリティオプション: **ユーザーがログオンしているときのみ実行する**
- [全般] **「表示しない」にチェック**
- [トリガー] **ログオン時**
- [操作] プログラム: `wsl.exe` / 引数: `-u root -- service ssh start`
  （systemd を有効にしているなら引数は `-d Ubuntu -e true` でよい）

**4. 確認**

再起動後、PowerShell から次を確認する。

```powershell
wsl -l -v
```

`STATE` が `Running` のままかどうか。ここで 15 秒待って `Stopped` になるなら、罠 2 の設定が効いていない。`.wslconfig` を書き換えたら `wsl --shutdown` が必要な点にも注意（Learn の言う「8 秒ルール」で、完全に停止するまで設定は反映されない）。

sshd 側は WSL に入って確認する。

```bash
sudo ss -tlnp | grep sshd
```

## まとめ

- タスクスケジューラの「**ユーザーがログオンしているかどうかにかかわらず実行する**」はセッション 0 で走り、ストア版 WSL はそこから起動できない。[microsoft/WSL#9231](https://github.com/microsoft/WSL/issues/9231) は 2026 年 9 月現在も open。**エラーが出ないまま sshd が上がらない**ので、一番デバッグしづらい形で失敗する。
- WSL のアイドル停止は VM とインスタンスで別々。`vmIdleTimeout` だけでは足りず、`[general] instanceIdleTimeout=-1` が要る。**この設定は Microsoft Learn に載っていない**。
- `sudoers` の NOPASSWD 行は `wsl -u root` の経路では使われない。
- systemd を有効にすれば sshd の起動は Linux 側の作法で済むが、**WSL インスタンスを起こすトリガーは Windows 側に残る**。
- 自動起動は「使うときだけ開くポート」を「常時開いているポート」に変える。ミラーモードならそれが LAN から見える。公開鍵認証への切り替えはセットで考える。

「公式ドキュメントに書いてあることだけでは足りず、Issue のスレッドを読まないと動かない」というのは、前回の `~/.bashrc` の話と同じ形をしている。**動かない理由が仕様として決まっているのに、その仕様がドキュメントの表に無い**、というタイプの詰まり方だ。この手の構成を組むときは、`wsl -l -v` の `STATE` のような**中間状態を直接見られるコマンド**を先に手に入れておくと、切り分けが一気に楽になる。

## 参考

- [Advanced settings configuration in WSL](https://learn.microsoft.com/ja-jp/windows/wsl/wsl-config) — Microsoft Learn（`.wslconfig` / `wsl.conf` の設定一覧、`vmIdleTimeout`、`[boot]` の Windows 11 制限、8 秒ルール）
- [Store WSL isn't accessible from Session 0 · Issue #9231](https://github.com/microsoft/WSL/issues/9231) — microsoft/WSL
- [(regression) No WSL access from session 0, affects scheduled tasks · Issue #9271](https://github.com/microsoft/WSL/issues/9271) — microsoft/WSL
- [Instance self-terminates prematurely when started with a background process in boot.command · Issue #8661](https://github.com/microsoft/WSL/issues/8661) — microsoft/WSL
- [WSL Services (e.g., Ollama, SSHD) Are Being Suspended Despite `vmIdleTimeout=-1` · Issue #13291](https://github.com/microsoft/WSL/issues/13291) — microsoft/WSL
- [Systemd support is now available in WSL!](https://devblogs.microsoft.com/commandline/systemd-support-is-now-available-in-wsl/) — Windows Command Line Blog
