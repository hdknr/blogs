---
title: "Windows の受信ブロックを WFP で切り分ける"
description: "Windows で受信だけが黙って落ちるとき、pktmon と netsh wfp で WFP の受信認可層まで降り、拒否したフィルタを filterId から名指しする手順。セキュリティ製品が Windows ファイアウォールより手前にいるケースの対処"
date: 2026-09-30
lastmod: 2026-09-30
aliases: ["WFP", "Windows Filtering Platform", "pktmon", "netsh wfp", "SMB 接続できない", "ノートン スマートファイアウォール"]
related_posts:
  - "/posts/2026/09/smb-norton-wfp/"
tags: ["Windows", "ファイアウォール", "SMB", "ネットワーク", "macOS"]
---

## 概要

Windows 11 の共有フォルダに同じ LAN の Mac から繋がらない、という症状から、**Windows Defender ファイアウォールより手前の WFP（Windows Filtering Platform）受信認可層で、セキュリティ製品（ノートン 360）が 445 番を拒否していた**ことを特定した手順。推測で設定をいじり続けず、パケットが届いているか → どの層で落ちたか → どのフィルタが落としたか、を順に確定させる。

## 詳細

### 1. 症状から疑う範囲を絞る

- `nc -z -w 3 <IP> 445` が **refused ではなくタイムアウト** → 相手まで届いていないか、黙って捨てられている
- 同じ LAN の別の Windows 機には繋がる → AP のクライアント分離ではない。犯人はこの PC の中
- この PC から他機の 445 へは出られる（`net view` が System error 5 を返す＝SMB は喋れている）→ **送信は正常、受信だけが落ちる**

共有（`Get-SmbShare` / `Get-SmbShareAccess`）、SMB サーバ（`Get-Service LanmanServer`、`netstat -ano | findstr ":445"`）、許可規則（`Get-NetFirewallRule -PolicyStore ActiveStore`）はすべて正しかった。

### 2. 「成功したのに効いていない」を疑う

次の 3 つはどれもエラーを出さず、読み直すと値が変わっていなかった。

- `Set-NetConnectionProfile -NetworkCategory Private` → `Public` のまま
- `Set-NetFirewallRule -RemoteAddress ...` → 元の `LocalSubnet` のまま
- `Set-NetFirewallProfile -LogBlocked False` → `True` のまま

**設定したら必ず読み直す。** セキュリティ製品が Windows 側の設定を握っていると、変更が黙って無視される。

もう一つの手がかりは、破棄も許可もログする設定にしたのに `pfirewall.log` が 1 行も増えないこと。**ログが空なのも情報**で、Windows ファイアウォールがこの経路を処理していない＝別のフィルタが先にいる、というシグナルになる。

### 3. pktmon でパケットが届いているかを見る

```powershell
pktmon filter remove
pktmon filter add MyFilter -p 445
pktmon start --capture --comp all --pkt-size 128 --file C:\Temp\cap.etl --file-size 50
# 別の機器から接続を試みる
pktmon stop
pktmon etl2txt C:\Temp\cap.etl -o C:\Temp\cap.txt
```

SYN が Wi-Fi 層とイーサネット層で観測されたうえで、`INET: accept inspection` でドロップされていた。WFP の接続認可層で落ちたことが確定し、ネットワークではなくこの PC 上のフィルタの問題に絞れる。

### 4. 落としたフィルタを名指しする

```powershell
netsh wfp show netevents file=netevents.xml   # FWPM_NET_EVENT_TYPE_*_DROP の filterId と layerId
netsh wfp show filters file=filters.xml       # filterId からフィルタ名・providerKey を引く
netsh wfp show state file=wfpstate.xml        # providerKey の GUID から提供元を引く
Get-CimInstance -Namespace root/SecurityCenter2 -ClassName FirewallProduct | Select-Object displayName
```

イベントは `layerId 44`（`ALE_AUTH_RECV_ACCEPT_V4`）、フィルタ名は `"Windows Networking In Public" rule, result=Deny`、提供元は `NLOK`（NortonLifeLock）。ノートンがネットワークを「パブリック」と判定しているあいだ 445 の受信を拒否していた。

**`netevents` → `filterId` → `filters` の 3 手で、拒否したフィルタを名前で特定できる。**

### 5. 直し方と効果の確認

ノートン 360 の スマートファイアウォール → ネットワーク タブで、接続中のネットワークを「パブリック」から「プライベート」へ。効いたかどうかは画面ではなく `netsh wfp show filters` の該当フィルタ数（4 本 → 0 本）で確かめる。

Entra ID 参加のみの端末は SMB のパスワード認証を通せないことがあるので、受け取り用フォルダだけを共有し、管理者権限のない共有専用ローカルアカウントを作ると手早い。

### 6. 分類を緩めた代償を外から測る

「プライベートにする」は 445 だけを開ける操作ではなかった。全ポートを Mac から測り直すと、`0.0.0.0:18080` で待ち受けていたローカル API サーバ（18080 / 18081）まで LAN に露出していた。**セキュリティ製品のネットワーク分類はポート単位のスイッチではない。**

- Windows の `New-NetFirewallRule -Action Block` は ActiveStore に載っても効かなかった。関門はノートンなので、許可も拒否も素通りする
- ノートンの トラフィックルール でポート単位のブロックを入れる。対象は分類に依存しない「すべて」にし、既定の許可ルールより上に置く（上から評価される）
- 「たまたま閉じていた」ポートと「分類に守られていた」ポートを区別する。後者は次に分類が変わると同じことが起きる

効果は両側から測る。

```bash
curl -o /dev/null -w "%{http_code}\n" http://localhost:18080/...   # 本来の利用経路は生きているか
nc -z -G 3 -w 3 <WindowsのIP> 18080 && echo OPEN || echo CLOSED    # LAN からは塞がったか
nc -z -G 3 -w 3 <WindowsのIP> 445   && echo OPEN || echo CLOSED    # 共有は維持されているか
```

**「規則を作った」を「効いた」の証拠にしない。** 塞いだら外から測り、壊していないことも測る。

### WSL2 ミラーモードとの関係

WSL2 を `networkingMode=mirrored` で動かすとホストと WSL がアドレスを共有するので、自分からの疎通テストが LAN の疎通テストになっていないことがある。**別の実機から測るまでは「未測定」であって「不通」ではない。**

## 関連ページ

- [WSL2 に SSH で入る設定と罠](/blogs/wiki/guides/wsl2-ssh-setup/) — ミラーモードで LAN から見えるポート
- [沈黙する失敗](/blogs/wiki/concepts/silent-failure/) — 「コマンドは成功したのに効いていない」
- [インシデント対応](/blogs/wiki/guides/incident-response/) — 推測より観測で切り分ける
- [kabu ステーション API](/blogs/wiki/tools/kabu-station-api/) — localhost:18080 で待ち受けるローカル API の例

## ソース記事

- [Mac から Windows の共有に繋がらない — WFP まで降りて犯人（ノートンのスマートファイアウォール）を特定した話](/blogs/posts/2026/09/smb-norton-wfp/) — 2026-09-03
