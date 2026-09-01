---
title: "Orca から WSL2 へ SSH — Node.js not found on remote host の原因は ~/.bashrc の早期 return"
date: 2026-09-01
lastmod: 2026-09-01
slug: "orca-wsl2-ssh-bashrc-node-not-found"
draft: false
source_url: "https://github.com/hdknr/blogs/issues/572#issuecomment-5492331608"
description: "Orca などの SSH クライアントで WSL2 に繋ぐと出る Node.js not found on remote host は SSH の失敗ではない。nvm が ~/.bashrc の末尾に書き、Ubuntu がその冒頭で非対話シェルを return するのが原因だと、公開情報の範囲で整理した。"
categories: ["ツール/開発環境"]
tags: ["Orca", "WSL2", "nvm", "ssh", "Node.js"]
---

Windows 版の [Orca](https://onorca.dev) から WSL2（Ubuntu）へ SSH 接続して、画面は Windows のまま開発環境だけ Linux 側にまとめる、という構成の解説記事を読んだ。

- [Windows版OrcaからWSL2（Ubuntu）へSSH接続する](https://zenn.dev/festiva1300/articles/orca-windows-wsl-ssh)（festiva1300 氏、2026-07-25）

手順そのものは元記事がよくまとまっている。ここで掘るのは次の 2 点に絞る。

- 元記事には書かれていない、Orca 公式ドキュメント側にだけある**前提条件**
- 元記事がトラブルシューティングとして挙げている **`Node.js not found on remote host` がなぜ起きるのか**

後者は Orca 固有の不具合ではなく、SSH とシェル初期化が噛み合ったときに出る、汎用的な罠だった。

> **前置き**: 筆者の手元は macOS で、Windows + WSL2 の実機検証はしていない。この記事で「確認した」と書いているのは、Orca 公式ドキュメント・nvm のインストーラのソース・bash と Ubuntu の既定 `~/.bashrc` の挙動といった、実機なしで裏が取れる範囲に限る。Orca の UI ラベルや接続の可否そのものは元記事の記述に依っている。**Orca が実際にどの形でリモートのコマンドを起動しているか（対話シェルなのか否か）も未検証**で、以下では「非対話シェルでコマンドを叩く一般的な SSH クライアント」としてモデル化している。

## 先に結論

`Node.js not found on remote host` は SSH の失敗ではない。噛み合っているのは次の 2 つだ。

- nvm は読み込み行を `~/.bashrc` の**末尾**に追記する
- Ubuntu の `~/.bashrc` は**冒頭**で非対話シェルを `return` する

結果、非対話シェルでは末尾の nvm 行に到達せず、PATH に node が入らない。対処は「nvm の読み込みをガードより前に移す」。根拠と手順は後述する。

## Orca の SSH worktrees は何をリモートに置くのか

まず前提の整理から。Orca は Stably 社が開発している ADE（Agent Development Environment）だ。Claude Code や Codex CLI といった CLI エージェントを [git worktree ごとに並列実行](/blogs/posts/2026/04/dmux-parallel-ai-agents/)するデスクトップアプリで、[GitHub 上では MIT ライセンス](https://github.com/stablyai/orca)で公開されている。ターミナルから同じ方向に進化した [Warp の ADE 化](/blogs/posts/2026/04/warp-agentic-development-environment/)と並ぶ、いわば同世代の道具立てになる。

その機能のひとつに SSH 接続があり、これを WSL2 に向ける、というのが今回の構成だ。

Orca の [SSH worktrees のドキュメント](https://www.onorca.dev/docs/ssh)によると、SSH ターゲットを使ったときの役割分担はこうなっている。

- git worktree は**リモート側に**作られる
- エージェントは**リモート側で**実行される
- エディタ・差分・ブラウザは**手元のまま**（ファイルイベントを同期している）

つまり「Windows のアプリから Linux のファイルを開く」のではなく、作業の実体を丸ごと Ubuntu 側に置いて、UI だけ Windows に残す構成になる。

![Windows 上の Orca が localhost:22 経由で WSL2 の Ubuntu へ SSH 接続する構成図。Windows 側に Orca と .wslconfig、WSL2 側に OpenSSH Server・Orca のリレー・nvm 配下の Node.js とエージェント群が並ぶ](/blogs/images/orca-wsl2-ssh-architecture.png)

## Orca × WSL2 の SSH 接続セットアップ

元記事の手順を、意味のある単位に圧縮するとこうなる。

### WSL2 をミラーモードにする（任意）

`C:\Users\<Windowsのユーザー名>\.wslconfig` を作る。

```ini
[wsl2]
networkingMode=mirrored
dnsTunneling=true
autoProxy=true
```

反映には WSL の完全停止が要る。

```powershell
wsl --shutdown
```

ミラーモードは、Windows のネットワークインターフェイスをそのまま WSL2 側に見せる方式だ。[Microsoft Learn の WSL ネットワークのドキュメント](https://learn.microsoft.com/ja-jp/windows/wsl/networking)によれば **Windows 11 22H2 以降**が要件になる。これで Windows と WSL2 が `localhost` で相互に通信できるようになり、接続先を `localhost:22` に固定できる。

なお、これは必須条件ではない。既定の NAT 方式でも `localhostForwarding` で Windows から WSL2 へ届く場合がある。ミラーモードを使うのは、接続先の書き方を `localhost` に統一して構成を単純に保つためだ。

### ミラーモードの副作用

ミラーモードは NAT の上位互換ではない。**分離をやめる代わりに、分離が生んでいた便利さも失う**トレードオフなので、既存環境に後から入れるなら以下は把握しておきたい。

**ポートが Windows と衝突するようになる。** これが一番効く。NAT では Windows と Linux が別ネットワークだったため、**両方が同じポート番号を使えた**。ミラーモードではそれが競合し、Windows 側で使用中のポートに Linux のアプリがバインドできなくなる。逃がし弁として、ミラーモード専用の設定が用意されている。

```ini
[experimental]
ignoredPorts=3000,9000,9090
```

`ignoredPorts` は「Windows で使用中でも Linux がバインドしてよいポート」の指定で、公式は Docker Desktop の 53 番を例に挙げている。Linux 内部だけで完結する通信なら衝突させる必要がない、という理屈だ。

**`localhostForwarding` が無視される。** NAT 時代に `localhost` 転送を担っていたこの設定は、ミラーモードでは設定ごと無視される（公式の `.wslconfig` サンプルにその旨が明記されている）。同様に `dnsProxy` も NAT 専用なので効かない。

**LAN から WSL に直接届くようになる。** 公式が利点として挙げている項目だが、裏返せば露出面が増えるということでもある。NAT の頃は WSL 内のサービスが事実上隠れていた。ここは Hyper-V ファイアウォールが既定で守っている（`firewall=true` が既定）ので、インバウンドを通したい場合はむしろ明示的に開ける必要がある。

```powershell
New-NetFirewallHyperVRule -Name "MyWebServer" -DisplayName "My Web Server" -Direction Inbound -VMCreatorId '{40E0AC32-46A5-438A-A0B2-2B479E8F2E90}' -Protocol TCP -LocalPorts 80
```

**IPv6 の `::1` は使えない。** `localhost` で繋がるのは IPv4 の `127.0.0.1` だけで、IPv6 の localhost は非対応と明記されている。IPv6 自体には対応しているのに localhost だけ穴がある形なので、踏むと原因が分かりにくい。なお `127.0.0.1` 以外のホスト割り当て IP を使いたい場合は、`[experimental]` の `hostAddressLoopback=true`（既定 `false`、IPv4 のみ）が要る。

**WSL 固有 IP の前提が崩れる。** ミラーモードは定義上 Windows のインターフェイスを Linux に複製するので、Linux 側から見える IP は Windows のものになる。`ip addr` や `hostname -I` から `172.x` 系の WSL 固有 IP を拾っていたスクリプトは、そのまま壊れる。

今回の用途（Windows から `localhost:22` へ繋ぐだけ）では、これらの副作用はほぼ表に出ない。ただし **3 点目は次節で立てる sshd と直結する**ので、22 番を上げる以上は意識しておく価値がある。

### Ubuntu 側に OpenSSH Server を入れる

```bash
sudo apt update
sudo apt install -y openssh-server
sudo systemctl enable --now ssh
```

起動と待ち受けまで確認する。

```bash
sudo systemctl status ssh --no-pager
ss -tln | grep ':22'
```

ここで一点、元記事も注意しているが繰り返す価値がある。**sshd は設定と Windows Defender ファイアウォールの状態次第で、同じネットワーク上の別端末から到達できる**。今回の用途は「同一マシン内の Windows から localhost へ」だけなので、外から触れる必要はない。外部公開する構成にするなら、公開鍵認証とパスワード認証の無効化はセットで考えることになる。

### Node.js は nvm で入れる

```bash
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.7/install.sh | bash
source ~/.bashrc
nvm install --lts
nvm alias default 'lts/*'
```

バージョン番号は執筆時点の最新（v0.40.7）。[nvm のリリース一覧](https://github.com/nvm-sh/nvm/releases)で最新を確認してから叩くこと。

確認は `which nvm` ではなく `command -v nvm` を使う。nvm はシェル関数として読み込まれるので、`which` では引っかからない。

```bash
command -v nvm
which node
```

`which node` が `/home/<ユーザー名>/.nvm/versions/node/vXX.XX.X/bin/node` を指していれば期待どおり。**この「nvm 配下を指している」という状態が、後述する `Node.js not found on remote host` の火種**になる。

## 元記事にない前提: build-essential と python3

Orca 公式ドキュメントの「[Linux hosts without a C/C++ toolchain](https://www.onorca.dev/docs/ssh)」には、手順記事の側では触れられていない前提が書かれている。

> On first connect, Orca installs a small relay on the remote. Remote terminals need a native `node-pty` module. Linux packages often compile on the host; macOS/Windows relays use prebuilds.

Orca は初回接続時にリモートへ小さなリレーを入れる。リモートのターミナルはネイティブモジュールの `node-pty` を必要とし、**Linux ではそれがホスト上でコンパイルされることが多い**。

同ページはさらに、`make` / C++ コンパイラ / `python3` が無い場合の症状まで明示している。接続自体は完了し、**ファイル・git・エディタは動く。リモートターミナルだけが動かない**。

これは厄介な壊れ方だ。「繋がっているのに一部だけ動かない」ので、SSH の設定を疑って延々ハマる余地がある。Debian/Ubuntu 系なら先に入れておくのが早い。

```bash
sudo apt-get install -y build-essential python3
```

入れたあとは**再接続**する。リレーがネイティブモジュールを入れ直すのはそのタイミングになる。

## 本題: Node.js not found on remote host の正体

ここからが本記事の主題。元記事はこのエラーに対して「NVM はシェルの起動時に読み込まれる仕組み」「SSH クライアントが起動するシェルの種類によっては PATH へ反映されない場合がある」と書いている。正しいが、もう一段だけ具体化できる。

原因は、**2 つの独立した設計判断が噛み合った結果**だ。

### 事実 1: nvm はファイルの「末尾」に追記する

nvm のインストーラ（`install.sh`）の該当部分はこうなっている。

```sh
SOURCE_STR="\\nexport NVM_DIR=\"${PROFILE_INSTALL_DIR}\"\\n[ -s \"\$NVM_DIR/nvm.sh\" ] && \\. \"\$NVM_DIR/nvm.sh\"\\n"
...
command printf '%b' "${SOURCE_STR}" >> "$NVM_PROFILE"
```

`>>` による**追記**、つまりファイルの末尾に書かれる。そして書き込み先を決める `nvm_detect_profile` は、bash 環境ではまず `~/.bashrc` を選ぶ。

### 事実 2: Ubuntu の ~/.bashrc は「冒頭」で非対話シェルを弾く

Ubuntu の既定の `~/.bashrc` は、ファイルのほぼ先頭にこの 5 行を持っている。

```bash
# If not running interactively, don't do anything
case $- in
    *i*) ;;
      *) return;;
esac
```

`$-` はシェルのオプションフラグで、対話シェルなら `i` を含む。含まなければ、**そこで `return` して以降を一切読まない**。

### 噛み合うと何が起きるか

`ssh host 'node -v'` のようにコマンドを直接指定した実行は、非対話シェルを起動する。このとき bash は、標準入力がネットワーク接続に繋がっていること（＝ sshd 経由で起動されたこと）を検出して `~/.bashrc` を読みにいく（[Bash Startup Files](https://www.gnu.org/software/bash/manual/html_node/Bash-Startup-Files.html)）。

そこで冒頭のガードに突き当たる。結果、**`return` してしまい、末尾に追記された nvm の 2 行には永遠に到達しない**。PATH に node が入らないまま、コマンドが「無い」と判定される。

なお、この壊れ方はディストリビューション依存だ。Fedora/RHEL の既定 `.bashrc` にはこのガードが無いため最後まで読み進む。Debian/Ubuntu だけが冒頭で返る。

![nvm の読み込み行が ~/.bashrc の末尾、Ubuntu 既定のガードが冒頭にあるため、対話シェルは末尾まで到達して node が使えるのに対し、非対話シェルは冒頭の return で終了して node が PATH に入らないことを示す図](/blogs/images/orca-wsl2-bashrc-guard.png)

この構造から、**症状の非対称性**が説明できる。

| 接続のしかた | `~/.bashrc` の扱い | 結果 |
| --- | --- | --- |
| ターミナルで `ssh user@localhost` してログイン（対話シェル） | 冒頭のガードを素通り | `node -v` が動く |
| コマンドを直接指定した実行（非対話シェル） | 冒頭で `return` | node が見つからない |

つまり「**PowerShell から手で ssh すると動くのに、GUI クライアントからだと動かない**」という一見不可解な状況は、この構造の当然の帰結になる。元記事の手順が「7. Windows から SSH 接続を確認する」で疎通確認を挟んでいるのは正しい。ただし**その確認が通っても、クライアント側では失敗しうる**。確認に使ったシェルの種類が違うからだ。

> Orca がリモートのコマンドを実際にどの形（対話シェルかどうか、ログインシェルかどうか）で起動しているかは、前述のとおり未検証である。ここでは非対話シェルを使う一般的なクライアントとしてモデル化して説明している。自分の環境で切り分けるなら、次節の検証コマンドで「非対話だと落ちるか」を先に確かめるのが早い。

### まず切り分ける

直す前に、これが本当にシェル初期化の問題なのかを確かめる。Windows の PowerShell から、**対話ログインと非対話実行を別々に**叩き比べればいい。

```powershell
ssh <Ubuntuのユーザー名>@localhost "node -v; which node; echo $-"
```

対話ログイン（引数なしの `ssh`）では `node -v` が出るのに、この一発実行では出ない、あるいは `$-` に `i` が含まれない——そうなっていれば、原因はこの記事の話で確定する。この 1 行がそのまま、以下の対処の受け入れテストにもなる。

### 対処 A: nvm の読み込みをガードより前に置く（推奨）

`~/.bashrc` の冒頭、`case $- in` の**上**に nvm の 2 行を移す。ファイル先頭がこの形になればいい。

```bash
export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"

# If not running interactively, don't do anything
case $- in
    *i*) ;;
      *) return;;
esac
```

シェルの種類に関係なく評価されるので、これが一番素直に効く。

ただし副作用がある。**あらゆる非対話シェルで `nvm.sh` を読むことになる**ので、`scp` / `rsync` や大量の `ssh` 実行が目に見えて重くなりうる。`nvm.sh` は決して小さくない。頻度が高い環境では次の対処 C のほうが向く。

### 対処 B: ~/.profile に書く（元記事の方法）

```bash
export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"
```

クライアントが**ログインシェル**を起動する場合はこれで効く。ただし `~/.profile` を読むのはログインシェルなので、**非ログインかつ非対話の実行では、これもまた読まれない**。クライアントの挙動に依存する対処である点は意識しておきたい。

### 対処 C: シェル初期化に依存させない

そもそもシェルの初期化ファイルを経由しない形にしてしまう手もある。nvm が選んだバージョンへのシンボリックリンクを、PATH の通った場所に置く。

```bash
sudo ln -s "$(nvm which default)" /usr/local/bin/node
sudo ln -s "$(dirname "$(nvm which default)")/npm" /usr/local/bin/npm
```

どのシェルからでも同じ node を引けるようになり、起動コストも増えない。代わりに `nvm use` でバージョンを切り替えてもリンク先は追随しないので、張り直しが要る。**エージェントに使わせる Node.js のバージョンをむしろ固定したい**のなら、この性質は欠点ではなく利点になる。

### 補足: Windows 版 Node.js を掴んでいるケース

同じ「node が見つからない／挙動がおかしい」でも、原因が逆のパターンがある。`which npm` の結果が `/mnt/c/Users/...` を指している場合だ。

WSL は既定で Windows 側の PATH を Linux 側に引き継ぐので、Windows に Node.js を入れていると、そちらの `node.exe` / `npm` を掴むことがある。切りたければ Ubuntu 側の `/etc/wsl.conf` に書く。

```ini
[interop]
appendWindowsPath=false
```

ただしこれを入れると、WSL から `notepad.exe` のような Windows コマンドを名前だけで呼べなくなる。相互運用を残したいなら、PATH の順序だけを整える方向で調整することになる。

## まとめ

- Orca の SSH ターゲットは「UI だけ手元、worktree もエージェントもリモート」という分担になる。WSL2 をそこに置くと、Windows の画面のまま実行環境を Linux に寄せられる。
- ミラーモード（Windows 11 22H2 以降）は必須ではないが、接続先を `localhost:22` に統一できるぶん構成が単純になる。ただし NAT の上位互換ではない。**Windows とポートが競合するようになり、`localhostForwarding` は無視され、LAN から WSL に直接届くようになる。**
- **公式ドキュメントにしか書かれていない前提**として、Linux リモートには `build-essential` と `python3` が要る。無いと「接続は成功するのにリモートターミナルだけ動かない」という切り分けにくい壊れ方をする。
- **`Node.js not found on remote host` は SSH の失敗ではない。** nvm が `~/.bashrc` の末尾に書き、Ubuntu の `~/.bashrc` が冒頭で非対話シェルを `return` する——この 2 つが噛み合った結果、末尾の nvm に到達しないだけだ。
- だから「手で ssh すると動くのに GUI からは動かない」という非対称が出る。**手動の疎通確認が通ったことは、GUI クライアントからの疎通を保証しない。** 確認するなら `ssh host 'node -v'` のように、非対話シェルの形で叩くほうが実態に近い。

シェル初期化ファイルの「どこに書くか」は、普段は気に留めない。リモート実行を挟んだ途端に、ファイル内の行の位置がそのまま不具合の有無になる。

対話を前提に組まれた仕組みが、非対話環境で黙って壊れる——という形自体は、[gh コマンドでトークン認証して非対話的にクローンする](/blogs/posts/2026/05/gh-cli-token-noninteractive-clone/)ときの詰まり方とよく似ている。エージェントに作業させる環境は基本的に非対話側なので、この手の罠は今後も踏むことになりそうだ。

## 参考

- [Windows版OrcaからWSL2（Ubuntu）へSSH接続する](https://zenn.dev/festiva1300/articles/orca-windows-wsl-ssh) — 本記事の元にした手順記事
- [Orca 公式サイト](https://onorca.dev)
- [Orca Docs: SSH worktrees](https://www.onorca.dev/docs/ssh)
- [stablyai/orca (GitHub)](https://github.com/stablyai/orca)
- [WSL でのネットワーク アプリケーションへのアクセス (Microsoft Learn)](https://learn.microsoft.com/ja-jp/windows/wsl/networking)
- [WSL の詳細設定の構成 (Microsoft Learn)](https://learn.microsoft.com/ja-jp/windows/wsl/wsl-config) — `ignoredPorts` / `hostAddressLoopback` / `firewall` の定義
- [Windows および Linux ファイル システム間での作業 (Microsoft Learn)](https://learn.microsoft.com/ja-jp/windows/wsl/filesystems)
- [nvm-sh/nvm (GitHub)](https://github.com/nvm-sh/nvm)
- [Bash Reference Manual: Bash Startup Files](https://www.gnu.org/software/bash/manual/html_node/Bash-Startup-Files.html)
