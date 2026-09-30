---
title: "ProxyJump による多段 SSH"
description: "踏み台（bastion）経由の SSH を ProxyJump と -J で短く書き、Match host でプライベート IP 帯にまとめて適用し、ControlMaster で接続を多重化する。ssh -G で解決結果を確かめる"
date: 2026-09-30
lastmod: 2026-09-30
aliases: ["ProxyJump", "ssh -J", "多段 SSH", "踏み台 SSH", "bastion", "Match host", "ControlMaster", "ssh -G"]
related_posts:
  - "/posts/2026/09/ssh-proxyjump/"
tags: ["ssh", "OpenSSH", "aws", "ec2", "ネットワーク"]
---

## 概要

VPC のプライベートサブネットにあるサーバーへ踏み台経由で SSH する設定は、`ProxyCommand ssh -W %h:%p bastion` や踏み台上の `nc` を使う古い書き方より、OpenSSH 7.3 で入った **`ProxyJump`**（コマンドラインでは `-J`）で短く書ける。`Match host` でアドレス帯にまとめて適用すれば、IP が変わる EC2 でも設定を書き換えずに済む。

## 詳細

### 完成形

```ssh-config
Host bastion
    Hostname 203.0.113.10
    User ec2-user
    # 次の 3 行は Windows ネイティブの OpenSSH では使えない
    ControlMaster auto
    ControlPath ~/.ssh/cp-%C
    ControlPersist 10m

Host app1
    Hostname 172.16.1.10
    User ubuntu

# 接続先エントリより後ろに書く
Match host 172.16.*,!172.16.0.5
    ProxyJump bastion
```

これで `ssh app1` でも `ssh 172.16.1.20` でも bastion 経由になる。

### ProxyJump と -J

- `ProxyJump <user>@<host>:<port>`。ユーザーとポートは省略でき、踏み台を config に定義してあれば `ProxyJump bastion` だけで済む
- 一時的な接続は `ssh -J bastion 172.16.1.10`。プライベート IP を解釈するのは手元ではなく踏み台なので、これで正しい
- 踏み台はカンマ区切りで複数並べられるが、2 段以上なら各踏み台のエントリに `ProxyJump` を書いて連鎖させるほうが見通しがよい

### Host ではなく Match host を使う理由

`Host` はコマンドラインで指定した名前（`app1`）とだけ照合し、`Match host` は先に読んだ `Hostname` で置き換えた後の名前（`172.16.1.10`）と照合する。

| 書き方と位置 | `ssh -G app1` | `ssh -G 172.16.1.10` |
|---|---|---|
| `Host 172.16.*` | ProxyJump なし | `proxyjump bastion` |
| `Match host 172.16.*`（接続先エントリより後） | `proxyjump bastion` | `proxyjump bastion` |
| `Match host 172.16.*`（接続先エントリより前） | ProxyJump なし | `proxyjump bastion` |
| `Match final host 172.16.*`（前） | `proxyjump bastion` | — |

ssh は設定を上から読むので、`Match host` の行に来た時点で `Hostname` がまだ読まれていないと `app1` のまま照合されて外れる。共通設定を上に書きたいなら、設定をもう一度読み直させる `Match final host` を使う。

### ControlMaster で接続を多重化する

| 設定 | 意味 |
|---|---|
| `ControlMaster auto` | 既存の接続があれば使い回し、なければ新しく張る |
| `ControlPath` | 共有する Unix ドメインソケットのパス。`%r@%h:%p` だとファイル名に接続先が出るので、見せたくなければハッシュの `%C` |
| `ControlPersist 10m` | 最後のセッションを閉じても 10 分は接続を保持 |

2 回目以降は TCP 確立と認証を省けて速くなり、踏み台の TCP 接続本数も減る。Windows ネイティブの OpenSSH は Unix ドメインソケット非対応で使えないが、WSL2 の中なら使える。

### ハマりどころ

- **ssh_config は最初に得た値が優先** — `Host *` を先頭に置くと、後ろの `Host` で同じ項目を上書きしても効かない（`ControlPersist no` を書いても `controlpersist 600` のまま）。個別エントリを先頭、`Host *` を末尾に置く
- **踏み台自身が Match の範囲に入る** — bastion の `Hostname` が `172.16.0.5` で `Match host 172.16.*` だと、bastion に入るのに bastion を経由しようとする。否定パターン（`!172.16.0.5`）で外すか範囲を絞る。VPN 経由でプライベート IP の踏み台に入る構成で起こりやすい

### 設定は ssh -G で確かめる

```bash
ssh -G app1 | grep -i '^proxyjump'
```

`ssh -G` は設定を解決して表示するだけで接続しない。ssh_config は記載順序と照合する名前で結果が変わるので、変えたら接続する前にこれで見る。

## 関連ページ

- [WSL2 に SSH で入る設定と罠](/blogs/wiki/guides/wsl2-ssh-setup/) — 接続先側（sshd）の設定
- [WireGuard](/blogs/wiki/tools/wireguard/) — SSH を開けずに SSM で管理する VPN ハブ
- [CloudFront + ALB で HTTPS](/blogs/wiki/guides/cloudfront-alb-https/) — AWS 上の別の到達経路

## ソース記事

- [多段 SSH は ProxyJump で — Match host と ControlMaster で踏み台設定を短くする](/blogs/posts/2026/09/ssh-proxyjump/) — 2026-09-29
