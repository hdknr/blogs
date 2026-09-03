---
title: "Mac から Windows の共有に繋がらない — WFP まで降りて犯人（ノートンのスマートファイアウォール）を特定した話"
date: 2026-09-03
lastmod: 2026-09-03
slug: "smb-norton-wfp"
draft: false
description: "Windows 11 の共有フォルダに Mac から繋がらない。共有もファイアウォールも正しいのに Finder は「サーバが存在しない」としか言わない。pktmon と netsh wfp show netevents で WFP の受信認可層まで降り、拒否したフィルタを filterId から名指しでノートン 360 と特定するまでの手順と、分類を緩めた代償として意図しないポートまで開いていた話。"
categories: ["セキュリティ"]
tags: ["Windows", "macOS", "SMB", "ファイアウォール", "ネットワーク"]
---

Windows 11 の共有フォルダに、同じ LAN の MacBook から接続できない。共有もファイアウォールも正しく設定したのに、Finder は「サーバが存在しないか、現在利用できません」としか言わない。

結論から書くと、犯人は **ノートン 360 のスマートファイアウォール**だった。Windows のファイアウォールより手前（WFP の受信認可層）で、445 番への受信接続を拒否していた。

そこに辿り着くまでに踏んだ手順と、途中で 3 回も引っかかった「コマンドは成功と言うのに効いていない」という罠を残しておく。さらに後半では、共有を通すために設定を緩めた結果、**意図していないポートまで同時に開いていた**という代償の話を書く。個人的には、後半のほうが実務に効いた。

## 環境

| | |
| --- | --- |
| 共有する側 | Windows 11 25H2（Entra ID 参加・ノートン 360 導入済み）。WSL2 を `networkingMode=mirrored` で運用 |
| 繋ぐ側 | macOS（同一 LAN・同一サブネット） |
| やりたいこと | Mac から Windows のフォルダへファイルを置く |

## 症状

- Finder の `⌘K` → `smb://<WindowsのIP>/<共有名>` が「サーバが存在しないか、現在利用できません」
- `nc -z -w 3 <WindowsのIP> 445` は **タイムアウト**（`refused` ではない＝黙って捨てられている）
- 一方、**Windows → Mac 方向の ping は成功**する

## 最初に潰した「思い込み」

ここで一番やってはいけないのは、想像で設定をいじり続けることだと思う。ひとつずつ潰した。

### 1. 共有は本当に存在するか

```powershell
Get-SmbShare -Name <共有名> | Format-List Name, Path
Get-SmbShareAccess -Name <共有名>
```

存在した。アクセス許可も対象アカウントに付いていた。

### 2. SMB サーバは動いているか

```powershell
Get-Service LanmanServer, LanmanWorkstation
Get-SmbServerConfiguration | Select-Object EnableSMB2Protocol
netstat -ano | findstr ":445"
```

`LanmanServer` は Running、SMB2 有効、`0.0.0.0:445` と `[::]:445` で待ち受け。**ホスト自身から** `Test-NetConnection -ComputerName <自分のIP> -Port 445` も `True`。

### 3. ファイアウォールの許可規則はあるか

```powershell
New-NetFirewallRule -Name 'SMB-In-LAN' -DisplayName 'SMB 445 inbound from LAN' `
  -Direction Inbound -Protocol TCP -LocalPort 445 `
  -RemoteAddress '10.0.0.0/24' -Action Allow -Profile Any -Enabled True
```

作った。**ActiveStore にも載っている**ことを確認した（＝実際に適用されている）。

```powershell
Get-NetFirewallRule -PolicyStore ActiveStore -Name 'SMB-In-LAN' |
  Select-Object Name, Enabled, Profile, Action
```

それでも通らない。

### 4. Wi-Fi のクライアント分離（AP 隔離）ではないか

ここで一度これを疑ったが、**同じ LAN の別の Windows 機には Mac から繋がっていた**。つまりネットワークは端末間通信を通している。犯人はこの PC の中にいる。

さらに念のため、この Windows から**別の Windows 機の 445 へ出られるか**を確認した。

```powershell
Test-NetConnection -ComputerName <別PCのIP> -Port 445   # TcpTestSucceeded : True
net view \\<別PCのIP>                                    # System error 5（＝SMB は喋れている）
```

**送信は正常。受信だけが落ちている。**

## 罠その 1: 「コマンドは成功したのに効いていない」

途中、3 回これを踏んだ。どれもエラーを出さない。

```powershell
# ネットワークをプライベートにする → エラーなし。しかし読み直すと Public のまま
Set-NetConnectionProfile -InterfaceAlias 'Wi-Fi' -NetworkCategory Private
Get-NetConnectionProfile | Select-Object Name, NetworkCategory   # → Public

# 規則の RemoteAddress を書き換える → エラーなし。しかし値は変わっていない
Set-NetFirewallRule -Name 'SMB-In-LAN' -RemoteAddress '10.0.0.0/24'
(Get-NetFirewallRule -Name 'SMB-In-LAN' | Get-NetFirewallAddressFilter).RemoteAddress  # → LocalSubnet

# ファイアウォールのログを止める → エラーなし。しかし True のまま
Set-NetFirewallProfile -Profile Public -LogBlocked False -LogAllowed False
```

**設定したら必ず読み直す。**「成功した」は「効いた」ではない。あとで分かるが、これも同じ犯人の仕業だった（セキュリティ製品が Windows 側の設定を握っている）。

## 罠その 2: 「ファイアウォールのログが空」という手がかり

破棄も許可も両方ログするようにしたのに、`pfirewall.log` がヘッダ 4 行のまま増えなかった。

```powershell
Set-NetFirewallProfile -Profile Domain,Private,Public -LogBlocked True -LogAllowed True `
  -LogFileName "$env:SystemRoot\System32\LogFiles\Firewall\pfirewall.log"
```

稼働中のマシンで許可ログが 1 行も出ないのは異常で、これは **「Windows ファイアウォールがこの経路を処理していない」＝別のフィルタが先にいる**というシグナルだった。当時は気づかず、`networkingMode=mirrored` な WSL の Hyper-V ファイアウォールを疑って回り道をした。

## 決定打 1: pktmon でパケットが届いているか見る

推測を止めて、パケットを直接見る。Windows 10/11 には `pktmon` が標準で入っている。

```powershell
pktmon filter remove
pktmon filter add MyFilter -p 445
pktmon start --capture --comp all --pkt-size 128 --file C:\Temp\cap.etl --file-size 50
# ここで Mac から接続を試みる
pktmon stop
pktmon etl2txt C:\Temp\cap.etl -o C:\Temp\cap.txt
```

結果はこうだった。

```
10.0.0.26.55847 > 10.0.0.8.445: Flags [S], seq ..., length 0     ← Wi-Fi 層で観測
10.0.0.26.55847 > 10.0.0.8.445: Flags [S], seq ..., length 0     ← イーサネット層で観測
ドロップ: 方向 Rx、種類 IP、コンポーネント 119、フィルター 1、
         INET: accept inspection 、DropLocation 0xE0004503
```

**パケットは届いている。届いたうえで、受信の「接続受け入れ検査」で捨てられている。**`accept inspection` は WFP（Windows Filtering Platform）の接続認可層で落ちたことを示す。つまりネットワークの問題ではなく、この PC 上のフィルタの問題だと確定した。

ここまでで、どの層まで生きていてどこで死んだかがはっきりした。

![Mac から Windows の 445 番宛パケットが、NIC/IP 層と WFP の受信 IP パケット層は通過し、WFP の ALE_AUTH_RECV_ACCEPT_V4 層でノートン 360 のフィルタに拒否されて、Windows Defender ファイアウォールと LanmanServer には到達していないことを示す層構造の図](/blogs/images/smb-norton-wfp-layers.png)

この図の要点は、**関門が Windows Defender ファイアウォールより手前にある**ことだ。だから Windows 側で規則を足しても引いても効かず、許可ログも 1 行も出なかった。罠その 2 の「ログが空」は、この構造の裏返しにすぎなかった。

## 決定打 2: どのフィルタが落としたのかを名指しする

WFP は「どのフィルタが落としたか」を ID 付きで記録している。

```powershell
netsh wfp show netevents file=netevents.xml
```

出てきた XML から該当イベントを拾う。

```xml
<type>FWPM_NET_EVENT_TYPE_PUBLIC_CLASSIFY_DROP</type>
<localPort>445</localPort>
<remoteAddrV4>10.0.0.26</remoteAddrV4>
<filterId>651964</filterId>
<layerId>44</layerId>            <!-- ALE_AUTH_RECV_ACCEPT_V4 -->
```

`filterId` が分かれば、フィルタ一覧から正体を引ける。

```powershell
netsh wfp show filters file=filters.xml
```

```
name: "Windows Networking In Public" rule, result=Deny
layerKey: FWPM_LAYER_ALE_AUTH_RECV_ACCEPT_V4
providerKey: {b0689775-...}
条件: FWPM_CONDITION_IP_LOCAL_PORT = 445
```

提供元 GUID を状態ダンプで引くと、記述に **`NLOK`**（NortonLifeLock）と出た。

```powershell
netsh wfp show state file=wfpstate.xml
# → "NLOK FWPM_LAYER_INBOUND_IPPACKET_V4 callout"
```

登録セキュリティ製品も確認。

```powershell
Get-CimInstance -Namespace root/SecurityCenter2 -ClassName FirewallProduct |
  Select-Object displayName        # → ノートン 360
```

**犯人はノートン 360 のスマートファイアウォール**。ネットワークを「パブリック」と判定しているあいだ、Windows ネットワーキング（445）の受信を拒否する規則が効いていた。

## 直し方

ノートン 360 → **設定 → 機能 → スマートファイアウォール → 「ネットワーク」タブ** → 接続中のネットワークを **「パブリック」から「プライベート」へ**。

効いたかどうかは画面ではなくフィルタの実体で確認した。

```powershell
netsh wfp show filters file=filters2.xml
# 変更前: "Windows Networking In Public" rule, result=Deny  → 4 本
# 変更後: 0 本
```

この直後、Mac の Finder は**ログインダイアログを出した**。＝ TCP も SMB ネゴシエーションも通ったということ。

## おまけ: Entra ID 参加の端末は SMB 認証で詰まる

繋がったあと、今度は認証で弾かれた。`ドメイン\ユーザー名` でも UPN（メールアドレス形式）でも通らない。

```powershell
whoami /upn
dsregcmd /status | findstr "AzureAdJoined DomainJoined"
# AzureAdJoined : YES / DomainJoined : NO
```

Entra ID 参加のみ（オンプレ AD 非参加）の端末は、SMB のパスワード認証を通せないことがある。共有専用の**ローカル標準アカウント**を作るのが手っ取り早い。

```powershell
$sec = Read-Host "共有用パスワード" -AsSecureString
New-LocalUser -Name shareuser -Password $sec -PasswordNeverExpires -UserMayNotChangePassword
Add-LocalGroupMember -Group (Get-LocalGroup -SID S-1-5-32-545).Name -Member shareuser  # Users のみ

$dir = 'C:\Users\<user>\FromMac'
New-Item -ItemType Directory -Path $dir -Force | Out-Null
icacls $dir /grant "shareuser:(OI)(CI)M"
New-SmbShare -Name frommac -Path $dir -FullAccess "$env:COMPUTERNAME\shareuser"
```

ユーザープロファイル全体ではなく**受け取り用フォルダだけ**を共有し、そのアカウントには管理者権限を与えない。これで Mac の Finder から `smb://<WindowsのIP>/frommac` に繋がった。

なお WSL を `networkingMode=mirrored` で動かしている環境では、ホストと WSL がアドレスを共有するため、こうした疎通確認の解釈がずれやすい。WSL 絡みで「動くはずのものが動かない」ときの切り分けについては [Orca から WSL2 へ SSH — Node.js not found on remote host の原因は ~/.bashrc の早期 return](/blogs/posts/2026/09/orca-wsl2-ssh-bashrc-node-not-found/) にも別のパターンを書いた。

## 続き: 共有を通した代償 — 別のポートの防御まで同時に外れていた

ここからが、この一件でいちばん実務的に効いた話。

### 「プライベートにする」は 445 だけを開ける操作ではない

上で、ノートンのネットワーク分類を **パブリック → プライベート** に変えて共有を通した。その直後、同じ LAN の Mac から**全ポートを一通り測り直した**ところ、こうなっていた。

![ノートンのネットワーク分類をパブリックからプライベートに変えた結果、445 と 139 に加えて意図していなかった 18080 と 18081 も同時に OPEN になり、トラフィックルールでポート単位に遮断して初めて 18080 と 18081 が CLOSED に戻ったことを 3 段階で比較した表の図](/blogs/images/smb-norton-port-exposure.png)

このマシンには、`0.0.0.0:18080` で待ち受けるローカル API サーバが常駐していた。**ノートンが「パブリック」として受信を拒否していたあいだ、それも一緒に守られていた。**分類を緩めた瞬間、守られていたのは 445 だけではなかったことが分かった。

⚠️ **セキュリティ製品のネットワーク分類は、ポート単位のスイッチではない。**1 つのアプリを通すために分類を緩めると、**そのマシンで待ち受けている全部**が同時に露出する。「何を開けたか」ではなく「**何が開いたか**」を、外から測って確認する必要がある。

なお図の ② で 22 と 3389 が CLOSED なのは、分類のおかげではない。そもそも LAN から到達できる待ち受けが無かっただけだ。分類に守られていたのは 18080 / 18081 のほうだった。**「たまたま閉じていた」と「守られていた」を区別しないと、次に分類が変わったときに同じことが起きる。**

### Windows のブロック規則は効かなかった

まず Windows ファイアウォールで塞ごうとした。

```powershell
New-NetFirewallRule -Name 'Block-App-In' -Direction Inbound -Protocol TCP `
  -LocalPort 18080,18081 -RemoteAddress LocalSubnet -Action Block -Profile Any -Enabled True
```

規則は `ActiveStore` にも載った。**それでも Mac からは OPEN のままだった。**

前半で分かっていたこと（許可ログを有効にしても `pfirewall.log` が 1 行も増えない ＝ Windows ファイアウォールがこの経路にいない）が、ここで**遮断側でも**裏付けられた形になる。**このマシンの関門はノートンであり、Windows 側の規則は許可も拒否も素通りする。**

### 遮断もノートン側で入れる

ノートン 360 → 設定 → スマートファイアウォール → **「トラフィックルール」タブ** → ルールを 2 本追加（ポートごとに 1 本）。

| 項目 | 選択 |
| --- | --- |
| 処理 | ブロック |
| 方向 | インバウンド（受信） |
| 対象 | **すべて** |
| プロトコル / ポート | TCP / 18080、18081 |

⚠️ 対象を「ローカル」「プライベート」に絞らず**「すべて」**にした。理由は単純で、**この一件そのものが「分類が変わった瞬間に防御が外れる」実例**だったから。分類に依存しない指定にしておく。

⚠️ ノートンのトラフィックルールは**上から順に評価される**ので、追加したルールが既定の許可ルールより上にある必要がある。

### 効果は必ず両側から測る

塞いだあと、**壊していないこと**と**塞げたこと**を別々に測った。

```bash
# 1) 本来の利用経路（このマシン自身から）が生きているか
curl -o /dev/null -w "%{http_code}\n" http://localhost:18080/...   # → 401（＝応答している）
```

```bash
# 2) LAN の他機からは塞がったか（Mac 側で実行）
nc -z -G 3 -w 3 <WindowsのIP> 18080 && echo OPEN || echo CLOSED    # → CLOSED
nc -z -G 3 -w 3 <WindowsのIP> 445   && echo OPEN || echo CLOSED    # → OPEN（共有は維持）
```

結果:

| ポート | 対処前 | 対処後 |
| --- | --- | --- |
| 18080 / 18081 | OPEN | **CLOSED** |
| 445 / 139 | OPEN | OPEN（意図どおり維持） |
| ローカルからの API 利用 | 401 応答 | **401 応答（無傷）** |

⚠️ **「規則を作った」を「効いた」の証拠にしない。** 今回まさに、規則が正しく登録されたのに 1 ミリも効いていないケースを踏んでいる。**塞いだら外から測る。壊していないかも測る。**

### Mac 側のチェックを共有フォルダに置いておくと楽

共有が通ったあとは、チェック用のスクリプトを**共有フォルダそのものに置く**のが手っ取り早かった。Mac で実行 → 結果を同じフォルダに書き出す → Windows 側からそのまま読める。

```bash
#!/usr/bin/env bash
WIN_IP="${WIN_IP:-<WindowsのIP>}"
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
{
  for i in en0 en1; do ip="$(ipconfig getifaddr "$i" 2>/dev/null)"; [ -n "$ip" ] && echo "$i : $ip"; done
  for p in 445 139 18080 18081 22 3389; do
    if nc -z -G 3 -w 3 "$WIN_IP" "$p" >/dev/null 2>&1; then echo "$p : OPEN"; else echo "$p : CLOSED"; fi
  done
  smbutil view "//<user>@$WIN_IP" 2>&1
} | tee "$DIR/result-from-mac.txt"
```

## 学んだこと

1. **「コマンドが成功した」と「設定が効いた」は別。** 変更したら必ず読み直す。セキュリティ製品が入っていると、Windows 側の設定変更が黙って無視されることがある。
2. **タイムアウトと接続拒否は違う。** `refused` なら相手まで届いている。タイムアウトは「届いていない」か「黙って捨てられた」のどちらかで、そこを先に切り分ける。
3. **ログが空なのも情報。** 許可ログまで有効にして 1 行も出ないなら、そのファイアウォールは経路にいない。
4. **推測を重ねる前に `pktmon`。** パケットが届いているかどうかで、疑う範囲が半分に減る。
5. **WFP は「誰が落としたか」を教えてくれる。** `netsh wfp show netevents` → `filterId` → `netsh wfp show filters` の 3 手で、拒否したフィルタを名前で特定できる。
6. **「自分から見えない」を「誰からも見えない」と書かない。** WSL のミラーモードのようにアドレスを共有している環境では、自分からの疎通テストが LAN の疎通テストになっていないことがある。別の実機から測るまでは「未測定」であって「不通」ではない。
7. **分類を緩めるときは、緩めた後に外から全ポートを測る。** 開けたかったポート以外に何が開いたかは、設定画面には書いていない。
8. **セキュリティ製品が入っている Windows では、`New-NetFirewallRule` は「効くとは限らない」。** 許可も拒否も素通りすることがある。**効果は必ず別マシンから確認する。**
9. **遮断を入れたら「壊していないこと」も測る。** 塞ぐ側だけ確認して、本来の利用経路を切ってしまうのが最悪の結末。両方測って初めて完了と言える。

## 使ったコマンドまとめ

| 目的 | コマンド |
| --- | --- |
| 共有の確認 | `Get-SmbShare` / `Get-SmbShareAccess` |
| SMB サーバの確認 | `Get-Service LanmanServer` / `Get-SmbServerConfiguration` |
| 待ち受けの確認 | `netstat -ano \| findstr ":445"` |
| 規則が実適用か | `Get-NetFirewallRule -PolicyStore ActiveStore` |
| パケットを見る | `pktmon filter add -p 445` → `pktmon start --capture --comp all` → `pktmon etl2txt` |
| 落としたフィルタの ID | `netsh wfp show netevents` |
| フィルタの正体 | `netsh wfp show filters` / `netsh wfp show state` |
| 導入製品 | `Get-CimInstance -Namespace root/SecurityCenter2 -ClassName FirewallProduct` |
| 参加状態 | `dsregcmd /status` / `whoami /upn` |
| 外からポートを測る | `nc -z -G 3 -w 3 <IP> <port>` / `smbutil view` |
