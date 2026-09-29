---
title: "多段 SSH は ProxyJump で — Match host と ControlMaster で踏み台設定を短くする"
date: 2026-09-29
lastmod: 2026-09-29
slug: "ssh-proxyjump"
draft: false
source_url: "https://github.com/hdknr/blogs/issues/694#issuecomment-5886642721"
description: "踏み台（bastion）経由の多段 SSH は ProxyJump と -J で書ける。Match host でプライベート IP 帯にまとめて適用し、ControlMaster で接続を多重化する設定を、ssh -G で挙動を確かめながら整理する。"
categories: ["クラウド/インフラ"]
tags: ["ssh", "aws", "ec2", "ネットワーク", "OpenSSH"]
---

AWS の VPC などで、踏み台ホスト（bastion）を経由してプライベートサブネットのサーバーに SSH する場面は多い。「多段 ssh」で検索すると `ProxyCommand` を使った設定例がたくさん出てくる。だが今の OpenSSH なら、`ProxyJump` を使うほうがずっと短く書ける。

この記事は、かりやみつるさんの Zenn 記事「[多段 ssh するなら ProxyCommand じゃなくて ProxyJump を使おう](https://zenn.dev/kariya_mitsuru/articles/ed76b4b27ac0fc)」の内容を整理したものだ。設定の挙動は手元の OpenSSH 10.3p1 で `ssh -G`（設定を解決して表示するだけで、接続はしない）を使って確かめた。

## 結論：この設定を書いておく

まず完成形を示す。

```ssh-config
Host bastion
    Hostname 203.0.113.10
    User ec2-user
    # 既定の鍵ファイルや ssh-agent を使うなら不要
    IdentityFile ~/.ssh/bastion.pem
    # 次の 3 行は Windows ネイティブの OpenSSH では使えない
    ControlMaster auto
    ControlPath ~/.ssh/cp-%r@%h:%p
    ControlPersist 10m

Host app1
    Hostname 172.16.1.10
    User ubuntu
    IdentityFile ~/.ssh/app.pem

# 接続先エントリより後ろに書く
Match host 172.16.*
    ProxyJump bastion
```

要点は 3 つある。

- `ProxyJump` で踏み台を経由する
- `Match host` で、プライベート IP の範囲にまとめて `ProxyJump` を適用する
- bastion に書いた `ControlMaster` / `ControlPath` / `ControlPersist` の 3 行で接続を多重化する

これで `ssh app1` とも `ssh 172.16.1.20` とも打つだけで、bastion 経由でつながる。以降の節で 1 つずつ見ていく。

## ProxyCommand は古い書き方

多段 SSH の解説でよく見かけるのは、次の 2 通りの書き方だ。

```ssh-config
# パターン 1: ssh -W を使う
Host app1
    ProxyCommand ssh -W %h:%p bastion

# パターン 2: 踏み台上の nc を使う（さらに古い）
Host app1
    ProxyCommand ssh bastion nc %h %p
```

どちらも動くが書き方は古い。パターン 2 は踏み台ホストに `nc` が入っている必要がある。

OpenSSH 7.3 で追加された `ProxyJump` を使えば、同じことを 1 行で書ける。

```ssh-config
    ProxyJump <user>@<bastion-host>:<port>

# 例
    ProxyJump ec2-user@203.0.113.10:22
```

`<user>@` と `:<port>` は省略でき、省略すると現在のユーザー名とポート 22 が使われる。踏み台ホストを `~/.ssh/config` に定義してあれば、冒頭の例のように `ProxyJump bastion` だけで済む。

踏み台はカンマ区切りで複数並べられる（`ProxyJump bastion1,bastion2`）。ただし、踏み台を 2 段以上経由するなら、それぞれの踏み台のエントリに `ProxyJump` を書いて連鎖させるほうが見通しがよい。

## コマンドラインなら -J オプション

`~/.ssh/config` にエントリを足すほどでもないときは、`-J` オプションで指定する。

```bash
ssh -J <user>@<bastion-host>:<port> <接続先IPアドレス>

# bastion を config に定義済みなら
ssh -J bastion 172.16.1.10
```

`-o ProxyJump=bastion` や `-o ProxyCommand="ssh -W %h:%p bastion"` と書くよりずっと短い。接続先のユーザー名やポート番号は、必要に応じて `-l` や `-p` で渡す。

接続先にプライベート IP アドレスを直接渡すのは奇妙に見えるかもしれない。だがこのアドレスを解釈するのは手元の PC ではなく踏み台ホストなので、これで正しい。

## Match host で -J すら省略する

bastion さえ定義してあれば `ssh -J bastion <IP>` でつながるが、毎回 `-J bastion` を打つのも面倒だ。そこで `Match host` を使う。

```ssh-config
Host bastion
    Hostname 203.0.113.10
    User ec2-user
    ControlMaster auto
    ControlPath ~/.ssh/cp-%r@%h:%p
    ControlPersist 10m

Match host 172.16.*,172.17.*
    ProxyJump bastion
```

これで `ssh 172.16.9.9` と打つだけで、自動的に bastion を経由する。`172.16.*` か `172.17.*` に当てはまる宛先には `ProxyJump bastion` が適用される、という意味だ。

AWS のインスタンスは作り直すたびに IP アドレスが変わる。そのたびに `~/.ssh/config` を書き換えるのは手間だが、割り当てるアドレス範囲（サブネット）はそうそう変わらない。範囲で書いておけば、IP アドレスが変わっても設定はそのまま使える。

## Host ではなく Match host を使う理由

複数の接続先に名前を付けて管理する場合も、`Match host` にまとめておけば各エントリに `ProxyJump` を書かずに済む。

```ssh-config
Host bastion
    Hostname 203.0.113.10
    User ec2-user

Host app1
    Hostname 172.16.1.10
    User ubuntu

Host app2
    Hostname 172.16.1.20
    User ubuntu

# ここに接続先をいくらでも追加できる

Match host 172.16.*
    ProxyJump bastion
```

`Match host` のブロックには `ProxyJump` 以外の共通設定も書ける。ここを `Host 172.16.*` にすると、`ssh app1` には効かない。`Host` はコマンドラインで指定した名前（ここでは `app1`）とだけ照合するためだ。`Match host` のほうは、先に読んだ `Hostname` で置き換えた後の名前（`172.16.1.10`）と照合する。`ssh -G` で確かめると次のようになる。

| 設定 | `ssh -G app1` | `ssh -G 172.16.1.10` |
|---|---|---|
| `Host 172.16.*` | ProxyJump なし | `proxyjump bastion` |
| `Match host 172.16.*`（接続先エントリより後） | `proxyjump bastion` | `proxyjump bastion` |

`Match host` を置く位置が結果を左右する理由は、次の節で説明する。

コマンドラインで IP アドレスしか指定しないなら `Host` でも足りる。ただ、せっかく `~/.ssh/config` に書くなら `app1` のような分かりやすい名前で接続したい。その場合は `Match host` が必要になる。

## Match の記載順序に注意する

`Match host` は、接続先のエントリより**後ろ**に書く必要がある。共通設定だからと先頭に書くと、名前で接続したときに効かない。

`ssh` コマンドは設定ファイルを上から順に読む。`Match host` の行に来た時点では、まだ `Hostname` が読まれていない。そのため照合相手は `app1` のままで、`172.16.*` とは一致しない。コマンドラインに IP アドレスを直接渡した場合は、最初から照合相手が IP アドレスなので一致する。

どうしても共通設定を上に書きたいなら、`Match final host` を使う。

```ssh-config
Host bastion
    Hostname 203.0.113.10
    User ec2-user

Match final host 172.16.*
    ProxyJump bastion

Host app1
    Hostname 172.16.1.10
    User ubuntu
```

`final` を付けると、`ssh` コマンドは設定ファイルをもう一度読み直す。1 回目の読み込みで `Hostname` が確定し、2 回目で `Match final host` がその値と照合される。3 通りの書き方を `ssh -G` で比べた結果は次のとおりだ。

| `Match` の書き方と位置 | `ssh -G app1` |
|---|---|
| `Match host`（接続先エントリより後） | `proxyjump bastion` |
| `Match host`（接続先エントリより前） | ProxyJump なし |
| `Match final host`（接続先エントリより前） | `proxyjump bastion` |

## ControlMaster で接続を多重化する

bastion に書いた `ControlMaster` / `ControlPath` / `ControlPersist` の 3 行は、接続の多重化の設定だ。多重化すると、1 本の TCP 接続の上で複数の SSH セッションを扱える。

![複数の ssh コマンドが bastion 向けの同じ ControlPath ソケットを共有し、1 本の TCP 接続で踏み台を経由してプライベートネットワーク内の各サーバーにつながる図](/blogs/images/ssh-proxyjump-multiplex.png)

多重化しないと、踏み台ホストへの TCP 接続がセッションの数だけ張られる。多重化すれば、手元の PC から踏み台までは 1 本の接続で済む。

| 設定 | 意味 |
|---|---|
| `ControlMaster auto` | 既存の接続があれば使い回し、なければ新しく接続する |
| `ControlPath ~/.ssh/cp-%r@%h:%p` | 既存接続を共有する Unix ドメインソケットのパス（`%r` はリモートのユーザー名、`%h` はホスト名、`%p` はポート番号） |
| `ControlPersist 10m` | 最後のセッションを閉じても、10 分間は接続を保持する |

効果は 2 つある。まず、2 回目以降の接続が速くなる。TCP の確立と認証を省けるので、待ち時間がほぼなくなる。次に、踏み台ホストから見ると TCP 接続の本数が減り、負荷が下がる。

注意点も 2 つある。

- **Windows ネイティブの OpenSSH では使えない。** 元記事によれば、Windows 標準の ssh が Unix ドメインソケットに対応していないためだ。WSL2 の中なら使える。
- **ソケットのパスにホスト名とユーザー名が出る。** 上の `ControlPath` だと、どこにつないでいるかがファイル名で分かる。見られたくなければ、接続情報のハッシュ値に展開される `%C` を使い、`~/.ssh/cp-%C` とする。

## Host * で全接続先に多重化を効かせる

多重化は踏み台に限らず使える。元記事の著者は、次のように `Host *` で全接続先に設定している。

```ssh-config
Host *
    ControlMaster auto
    ControlPath ~/.ssh/cp-%r@%h:%p
    ControlPersist 10m
    ServerAliveInterval 10
    ServerAliveCountMax 6

Host bastion
    Hostname 203.0.113.10
    User ec2-user

Host app1
    Hostname 172.16.1.10
    User ubuntu

Match host 172.16.*
    ProxyJump bastion
```

ここで 1 つ気を付けたい。`ssh_config` では**最初に得た値が優先**される。`Host *` を先頭に置くと、後ろの `Host` で同じ項目を上書きしようとしても効かない。

```ssh-config
Host *
    ControlPersist 10m

Host bastion
    # 次の行は効かない
    ControlPersist no
```

この設定で `ssh -G bastion` を実行すると、`controlpersist 600`（10 分）と表示される。個別に変えたい項目があるなら、`Host *` をファイルの末尾に移し、先頭には個別のエントリを置く。

## 落とし穴：踏み台自身が Match の範囲に入る場合

`Match host` の範囲に、踏み台ホスト自身の IP アドレスが含まれていないかも確認しておきたい。たとえば bastion の `Hostname` が `172.16.0.5` で、`Match host 172.16.*` と書くと、bastion への接続にも `ProxyJump bastion` が適用されてしまう。

```ssh-config
Host bastion
    Hostname 172.16.0.5

Match host 172.16.*
    ProxyJump bastion
```

`ssh -G bastion` の出力にも `proxyjump bastion` が現れる。つまり、bastion に入るのに bastion を経由しようとする設定になる。VPN 経由でプライベート IP の踏み台に入る構成では起こりやすい。対策は 2 つある。

- 否定パターンで踏み台を範囲から外す（`Match host 172.16.*,!172.16.0.5`）
- `Match host` の範囲を、踏み台を含まないように絞る

## 設定は ssh -G で確かめる

ここまで見てきたように、`~/.ssh/config`（ssh_config）は記載順序や照合する名前によって結果が変わる。書いた設定が意図どおりに効いているかは、`ssh -G` で確かめられる。

```bash
# app1 に接続するときの最終的な設定を表示する（接続はしない）
ssh -G app1

# ProxyJump だけ確認する
ssh -G app1 | grep -i '^proxyjump'
```

`ssh -G` は設定ファイルを解決して結果を表示するだけで、実際には接続しない。設定を変えたら、接続する前にこれで確かめる習慣をつけておくとよい。

## まとめ

- 多段 SSH は `ProxyCommand` ではなく `ProxyJump`（コマンドラインでは `-J`）で書く。
- `Match host` を使うと、プライベート IP の範囲にまとめて `ProxyJump` を適用できる。名前で接続する場合、`Host` では一致しない。
- `Match host` は接続先エントリの後ろに書く。前に書きたいなら `Match final host` を使う。
- `ControlMaster` / `ControlPath` / `ControlPersist` で接続を多重化すると、2 回目以降の接続が速くなる。
- `Match host` の範囲に踏み台自身の IP を含めない。含むなら否定パターンで除外する。
- ホスト名を見せたくなければ、`ControlPath` に `%C` を使う。
- `ssh_config` では最初に得た値が優先される。挙動は `ssh -G` で確かめる。

## 参考

- [多段 ssh するなら ProxyCommand じゃなくて ProxyJump を使おう（Zenn）](https://zenn.dev/kariya_mitsuru/articles/ed76b4b27ac0fc)
- [ssh_config(5) — OpenBSD manual pages](https://man.openbsd.org/ssh_config)
- [OpenSSH 7.3 リリースノート](https://www.openssh.com/txt/release-7.3)
