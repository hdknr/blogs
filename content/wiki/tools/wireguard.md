---
title: "WireGuard"
description: "カーネル実装の軽量 VPN。AllowedIPs による cryptokey routing で経路を表現する。AWS 上に中継ハブを置き、IP 制限された SaaS へ社外からオフィスの固定 IP で出る構成と、その運用上の落とし穴"
date: 2026-09-30
lastmod: 2026-09-30
aliases: ["wg", "wg-quick", "WireGuard 中継ハブ", "cryptokey routing", "TCP MSS クランプ"]
related_posts:
  - "/posts/2026/09/wireguard-relay-hub/"
tags: ["WireGuard", "VPN", "ネットワーク", "MTU", "aws"]
---

## 概要

WireGuard は公開鍵で peer を識別する軽量な VPN。各 peer の `AllowedIPs` が「その peer へ送る宛先」と「その peer から受け入れる送信元」を兼ねる **cryptokey routing** で、最長一致で振り分けられる。`AllowedIPs = 0.0.0.0/0` の peer を 1 つ置けば、それが事実上のデフォルトルートになる。

IP 制限のある SaaS へ社外から接続するため、AWS の EC2 に中継ハブを置き、オフィスの社内ノードで NAT してオフィスの固定 IP から出す構成を組んだ記録から、設計判断と落とし穴をまとめる。

## 詳細

### 中継ハブ構成

- 社内ノードは固定のグローバル IP を持てないので、EIP を持つハブへ**社内ノードからアウトバウンドで張る**（`PersistentKeepalive = 25`）
- 社外の端末もハブへ張る。ハブは中継だけで、**自分では NAT しない**（NAT すると出口が AWS の IP になり制限を通らない）
- 社内ノードは peer として `AllowedIPs = 0.0.0.0/0`、クライアントには `/32` を払い出す
- 社内ノードで RFC 1918 宛を REJECT し、社外端末から社内 LAN へは到達させない

ハブの `wg0.conf` では **`Table = off` が必須**。`AllowedIPs = 0.0.0.0/0` を素直に書くと `wg-quick` がハブ自身の通信までトンネルへ吸い込み、SSM が切れて管理経路を失う。クライアント由来のパケットだけを `ip rule add from <client-cidr> table 200` のポリシールーティングで別テーブルへ振る。初回構築時は `systemd-run --on-active=30min ... stop wg-quick@wg0` のデッドマンタイマーを保険に置く。

### 設計判断

- **ハブの秘密鍵はインスタンス上で `wg genkey` し、公開鍵だけを Parameter Store に載せる** — Terraform の state に秘密鍵が入らない代わりに、作り直すと全クライアントの設定変更が要るので EC2 と EIP に `prevent_destroy`
- **peer 定義は台帳（`peers.json`）・Parameter Store・稼働中の `wg0` の 3 層** — 反映は `wg syncconf` で無停止。既存 peer の転送カウンタを前後で比べて巻き戻りがないことを確認する
- **スクリプトが機械編集するものを HCL で持たない** — `*.tfvars` を正規表現で編集して peer 2 件を消すバグを踏んだ。JSON なら構造ごと扱える。`file()` 由来だと variable の `validation` が使えないので `lifecycle.precondition` で検査する
- **利用者の秘密鍵は受け取らない** — アプリで空のトンネルを作らせ、公開鍵だけを送ってもらう

### 運用上の落とし穴

| 落とし穴 | 何が起きるか | 対処 |
|---|---|---|
| `systemd-networkd` の `ManageForeignRoutingPolicyRules=yes` | networkd の再起動で `ip rule` が消え、トンネルは繋がるのに出口へ行けない半壊状態。再起動テストでは `PostUp` が後勝ちするので再現しない。`unattended-upgrades` の systemd re-exec で起きる | `ManageForeignRoutingPolicyRules=no` |
| EC2 のステータスチェック | OS が生きていれば半壊でも正常に見え、1 日気づかれなかった | 5 分ごとの自前ヘルスチェックをカスタムメトリクスへ |
| `user_data` の変更 | plan は `updated in-place` と出るが、実際は stop → 変更 → start | 想定外のリソースが動く plan で中断するガード |
| 保存された新しい `user_data` | cloud-init は再実行されないので実機は変わらない | 反映は SSM で別途配布 |
| 稼働中の `wg0.conf` | `[Interface]` は初回に一度書かれただけの唯一のコピー | バックアップ + `wg-quick strip` でパース検証 |
| AMI を最新パラメータで追う | replace が計画され `prevent_destroy` で plan ごと落ち、peer の失効もできなくなる | `ignore_changes = [ami]` |

ヘルスチェックは設定値の羅列より、**カーネルの経路選択そのものを問う**のが確実。

```bash
ip route get 1.1.1.1 from "$CLIENT_IP" iif wg0 | grep -q 'dev wg0' || note route-via-wg0
```

「無いべきものが在る」（POSTROUTING に MASQUERADE が生えた）も見る。自動修復はせず、検出してアラームを上げるところまでに留める。

### 利用者側の 2 つの障害

**症状はどちらも「繋がっているのに何も開けない」だった。**

1. **`DNS` の欠落** — `AllowedIPs = 0.0.0.0/0` は DNS もトンネルへ送る。`DNS` を書かないと端末は自宅ルータ（`192.168.x.1`）へ問い合わせ、社内ノードが RFC 1918 宛として REJECT し名前解決が全滅する。`DNS = 1.1.1.1, 8.8.8.8` を必須にした（社内ホスト名が引けないのは要件の帰結）。SaaS の IP はリゾルバで違う値が返るので、`AllowedIPs` を絞る split tunnel は成立しない
2. **`MTU` の過大** — WireGuard は内側のパケットに 60 バイト（IPv4 20 + UDP 8 + WG ヘッダ 16 + 認証タグ 16）を足す。`MTU = 1420` は回線上 1480 バイトになり、フレッツ系 PPPoE（IPv4 上限 1454）を超える。ハンドシェイクや DNS や 350 バイトの応答は通り、TLS 証明書の数 KB で止まる。`MTU = 1280`（IPv6 の最小 MTU）で解消

MTU は DF ビットを立てた ping で測る（macOS なら `ping -D -s <size>`、内側のサイズは `-s` + 28）。

### 恒久対処: ハブで TCP MSS をクランプ

```bash
iptables -t mangle -A FORWARD -i wg0 -o wg0 -p tcp --tcp-flags SYN,RST SYN \
  -j TCPMSS --set-mss 1240
```

- 1240 = 配布 MTU 1280 − IPv4 20 − TCP 20。利用者が MTU を大きめにしていても TCP は成立する。効くのは主に下り
- `--clamp-mss-to-pmtu` は送出インターフェース（`wg0` = 1420）しか見ないので、その先の細い回線は知りようがない
- QUIC / HTTP3 は UDP なので効かない（ブラウザの TCP フォールバックで実用上は足りる）
- クランプ値を配布 MTU から算出しない。クランプ値は user_data に埋まるので、derive すると配布 MTU を触るだけで実機が止まる
- ルールが消えると細い回線の利用者だけが壊れるので、ヘルスチェックにも項目を足し、**ルールを外して検出されることを対照実験で確かめてから戻す**

### トラブルシュートの切り分け表

| `curl https://1.1.1.1/cdn-cgi/trace` | `nslookup <host>` | 原因 |
|---|---|---|
| 出ない | — | 通信自体が通っていない |
| 出る | 答えが返らない | `DNS` 行の欠落 |
| 出る | 答えが返る | `MTU` が大きすぎる |

「名前を使わない疎通」だけでは足りない。**名前解決の可否とパケットの大きさの 2 軸**を、小さい応答と大きい応答の両方で測る。接続確認は IP 制限が可視化される API エンドポイントで行う（HTML パスは送信元に関係なく 200 を返すことがある）。

## 関連ページ

- [沈黙する失敗](/blogs/wiki/concepts/silent-failure/) — ステータスチェックで見えない半壊と対照実験
- [Terraform による IaC](/blogs/wiki/guides/terraform-iac/) — `prevent_destroy`・`ignore_changes`・`precondition`
- [ProxyJump による多段 SSH](/blogs/wiki/guides/ssh-proxyjump/) — 踏み台経由の別の接続経路
- [インシデント対応](/blogs/wiki/guides/incident-response/) — 切り分けの進め方

## ソース記事

- [社外から「許可された IP」で出るための WireGuard 中継ハブ — 構成と、4 日かかった障害の話](/blogs/posts/2026/09/wireguard-relay-hub/) — 2026-09-07
