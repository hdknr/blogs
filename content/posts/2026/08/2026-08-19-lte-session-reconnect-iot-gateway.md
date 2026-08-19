---
title: "SORACOM のセッションが Deleted → Created を繰り返す — LTE-M の PSM と無通信タイマーで切り分ける"
date: 2026-08-19
lastmod: 2026-08-19
slug: "lte-session-reconnect-iot-gateway"
description: "SORACOM のセッション履歴に Deleted → Created が繰り返し記録される原因を、デバイス・無線区間・コア網・プラットフォームの 4 層で切り分ける。ハンドオーバーは Modified、PSM は張り直しを増やさない、オンライン表示は証拠にならない——3 つの誤解も訂正し、soracom sims session-events での確認手順まで。"
draft: false
source_url: "https://github.com/hdknr/blogs/issues/558#issuecomment-5341450437"
categories: ["クラウド/インフラ"]
tags: ["IoT", "SORACOM", "LTE-M", "遠隔監視", "トラブルシューティング"]
---

LTE-M 対応の IoT ゲートウェイ **SmartFitPRO**（旭光電機）を、ドコモ回線で長時間稼働させる。すると、セッション履歴に `Deleted` が記録され、その後 `Created` が続く——という現象に出会う。数日〜数週間動かしていれば、まず間違いなく何度か出る。デバイス選定の全体像は[SORACOM IoT ストアの製品をソリューション軸で分類した記事](/blogs/posts/2026/07/soracom-iot-store-solution-map/)にまとめたが、この記事はその一段下、選んだ後に現場で出てくる話だ。

結論を先に書くと、**この `Deleted` → `Created` の多くは仕様の範囲内の正常動作**である。ただし「よくある現象なので気にしなくていい」で止めてしまうと、本当に実害が出ているケースを同じ形の中に埋めてしまう。正常な張り直しと、調査すべき張り直しは、ログの形で区別できる。

この記事では、その区別のつけ方を整理する。あわせて、この現象の説明としてよく流布している 3 つの誤解も訂正しておく。どれも「もっともらしいが因果が逆」というタイプで、切り分けの順番を狂わせる。「LTE の瞬断」という一言で片付けてしまうと、この 3 つはまとめて見えなくなる。

なお以降、セッションの再確立・再接続はすべて「張り直し」と呼ぶ。

## SORACOM の「セッションが切れた」は 4 つの層を指す

切り分けが難しくなる最大の理由は、「セッションが切れた」という一言が指す対象が、実は 4 つの別々の層にあることだ。以下では「コアネットワーク（MME）」を単にコア網と呼ぶ。

![IoT ゲートウェイのセッション切断が起きうる 4 つの層を、デバイス・無線区間・コアネットワーク・PGW/SORACOM プラットフォームに分け、それぞれの典型的な原因と観測できる痕跡を対応させた一覧図](/blogs/images/lte-session-reconnect-layers.png)

重要なのは、**手元で観測できるのは一番下の層（プラットフォームのセッション履歴）だけ**という点だ。デバイスが自発的に張り直したのか、無線区間が一瞬揺れただけなのか、コア網がデタッチしたのか、無通信タイマーが満了したのか。原因は上の 3 層のどこかにあるのに、証拠は一番下の層のログにしか出てこない。

だからこそ、ログの「形」から上の層を推定する必要がある。

## 誤解 1：ハンドオーバーはセッションの張り直しではない

「電波状況が変動して別の基地局に切り替わるタイミングでセッションが再作成される」という説明をよく見る。これは半分だけ正しい。

SORACOM のセッションイベントは 3 種類あり、[用語集](https://users.soracom.io/ja-jp/resources/glossary/session/)では明確に区別されている。

| イベント | 意味 |
| --- | --- |
| `Created` | セッションが確立された |
| `Deleted` | セッションが切断された |
| `Modified` | デバイスの移動や電波強度の問題などの理由で、基地局からセッションの更新（ハンドオーバー）が通知された |

つまり**ハンドオーバーは `Modified` として記録され、`Deleted` にはならない**。PDN セッションは維持されたままで、IP アドレスも変わらない。

同じドキュメントには「デバイスと基地局間の通信状態が不安定な場合は、Created / Deleted が短い間隔で頻繁に記録されたり、Modified が多く記録されることがあります」とある。裏を返せば、**`Modified` だけが多発しているなら無線区間の話であり、セッションは一度も張り直されていない**。この場合にゲートウェイのキープアライブ設定をいじり始めるのは、見当違いの層を触っていることになる。

逆に `Deleted` が出ているなら、無線区間より下——コア網かプラットフォームで、セッションそのものが落ちている。

## 誤解 2：PSM / eDRX は「張り直しを増やす」機能ではない

これが一番よく見る、そして一番厄介な誤解だ。「LTE-M では省電力機能（eDRX や PSM）との兼ね合いで定期的にセッションの再確立が行われる」という説明——**因果が逆**である。

LTE-M は LPWA（省電力広域通信）の一種で、電池運用を成立させるための省電力機能を持つ——という前提は[IoT センサーの種類と入手先を整理した記事](/blogs/posts/2026/07/iot-sensor-categories-and-shops/)でも通信規格の比較として触れた。その省電力機能の中身が、ここで問題になっている PSM と eDRX である。

PSM（Power Saving Mode）と eDRX（extended Discontinuous Reception）の設計目的は、まさに**再アタッチを避けること**だ。モデムの電源を切ってしまうのではなく無線だけを止め、ネットワークへの登録状態は維持したまま眠る。アタッチ手続きは電力を食うので、それをやり直させないためにこの仕組みがある。PSM は「セッションを張り直す機能」ではなく「張り直さずに済ませる機能」だ。

では、なぜ実際に `Deleted` → `Created` が出るのか。競合しているのはタイマーである。

### PSM が交渉する 2 つのタイマー

PSM は、アタッチまたは TAU（Tracking Area Update）の手続きの中で 2 つのタイマーをネットワークと交渉して有効になる。

- **T3324（Active Timer）**：接続状態からアイドルに移った後、着信を受けられる時間。3GPP 上の最大値は 11,160 秒（186 分）。
- **T3412 extended（周期 TAU タイマー）**：端末がネットワークに存在を知らせる周期。3GPP TS 24.008 での最大値は 413 日。

**スリープできる長さは T3412 − T3324** になる。そしてネットワーク側には、TAU が来なかったときのための保険がある。**Implicit Detach Timer は T3412 extended ＋ 4 分**に設定され、これが満了すると MME は端末の登録を破棄する。Mobile Reachability Timer は T3324 と同値だ。

### 無通信タイマーとの競合

ここに、もう 1 本別のタイマーが絡む。**プラットフォーム側の無通信タイマー**である。SORACOM には無通信が一定時間続くとセッションを切断（タイムアウト）する仕様があり、その時間は[サブスクリプションごとに異なる](https://users.soracom.io/ja-jp/resources/glossary/session/)。

![PSM のスリープ期間と無通信タイマーの関係を時系列で示した図。T3324 の Active Time、T3412 extended の周期 TAU 間隔、T3412 + 4 分の Implicit Detach タイマーと、それより短いプラットフォーム側の無通信タイマーが満了して Deleted が記録される様子を対比している](/blogs/images/lte-session-reconnect-psm-timers.png)

つまり、こういう順序になる。

1. デバイスが PSM で眠る（ネットワーク登録は維持されている）
2. 眠っている間に**無通信タイマーが先に満了する**
3. プラットフォーム側でセッションが切られ、履歴に `Deleted` が記録される
4. 次の送信タイミングで起きたデバイスがセッションを張り直し、`Created` が記録される

**端末は寝ていただけなのに、ログには「切断 → 再接続」として残る。** これが「よくある現象」の実体だ。PSM が張り直しを引き起こしているのではなく、PSM のスリープが無通信タイマーより長いから、その間セッションが維持されないだけである。

この理解が実務で効くのは、**打つ手が変わる**からだ。「PSM のせい」だと思うと省電力設定を切りたくなるが、切ったところで無通信タイマーの方が短ければ結果は同じで、電池だけが減る。見るべきは送信周期と無通信タイマーの大小関係だ。そしてこの経路の `Deleted` は「送信が終わってから無通信タイマー分だけ後」に出るという規則性を持つ。

## 誤解 3：「オンライン表示」はセッションがある証拠にならない

3 つめ。コンソールがオンラインと表示していても、実際にはセッションが確立されていない状態がありうる。

SORACOM の[診断ガイド](https://users.soracom.io/ja-jp/guides/diagnostic/air-for-cellular/)には、「デバイスの予期せぬ電源断や予期せぬ停止などが原因で、デバイスだけがセッションを破棄してしまう」ことがあり、この場合「ユーザーコンソールでの表示とは異なり、実際にはセッションが確立されていません」と明記されている。

接点入出力の監視用途では、これが地味に痛い。ゲートウェイは電池や USB で駆動していることが多く、電源が不安定な現場では片側だけセッションが消える状況が起こりうる。**「オンラインだから届いているはず」ではなく、直近の通信実績で判断する。**

これは「監視が正常を示しているのに実際は死んでいる」という失敗の典型で、層もサービスも違うが構造は同じだ。[RDS の Blue/Green 切替で DMS が静かに死んだ話](/blogs/posts/2026/08/rds-blue-green-dms-cdc-incident/)も、まさにこの形で 18 日間気付かれなかった。ステータス表示ではなく処理実績を指標に置くべきという話は、[SLI/SLO の設計](/blogs/posts/2026/05/sli-slo-sla-proposal/)と同じ論点である。

通信実績はデータ通信量の集計から取れる。5 分単位まで刻めるので、「オンライン表示のまま実は無通信」を検出できる。

```bash
# 直近の通信量を約 5 分単位で見る（--from / --to は UNIX time の「秒」）
soracom stats air sims get \
  --sim-id 8981100000000000000 \
  --period minutes \
  --from 1755561600 \
  --to 1755648000
```

セッションイベントの `--from` / `--to` はミリ秒、この通信量 API は秒である。単位が違うので使い回すと静かに 1970 年を見ることになる。

## データ欠損が出ているときの切り分け手順

判定の軸は「回数」ではなく「**周期性と送信タイミングの一致**」だ。1 日に 20 回出ていても送信周期と揃っていれば設計どおりで、1 日に 3 回でも送信と無関係なタイミングなら何か起きている。

実害——「クラウドへのデータ送信が欠損する」「張り直しのあと復帰しない」——が出ているときは、この順で見ると層を素早く絞れる。

1. **`Modified` だけか、`Deleted` を伴うか**
   `Modified` のみなら無線区間の問題で、セッションは切れていない。→ アンテナ設置場所の変更や電波強度の改善に向かう。ゲートウェイ側の設定は触らない。機械室や地下ピットのような閉所での設置とアンテナ選定は、[建築設備メンテナンスの視点で SORACOM の IoT を分類した記事](/blogs/posts/2026/07/soracom-iot-building-maintenance-classification/)でも扱った論点だ。
2. **`Deleted` の発生間隔が送信周期・スリープ周期と一致するか**
   一致するなら無通信タイマー満了で、正常動作。→ 送信周期を短くするか、欠損しない送信リトライをアプリ側に入れる。省電力設定を切っても解決しない。
3. **一致しないなら、前後でセル ID が変わっているか**
   変わっていれば基地局をまたいでいる。変わっていなければコア網かデバイス側。
4. **`Deleted` から `Created` までの復帰時間はどれくらいか**
   直後に `Created` が続き、データ欠損もないなら問題なし。数分以上かかる、あるいは戻らないなら、デバイス側の自動復旧が働いていない。→ ファームウェア更新やキープアライブ設定の調整に向かう。
5. **オンライン表示を信じない**
   通信実績で確認する。片側だけセッションが消えている可能性がある（誤解 3）。

## `soracom sims session-events` で履歴を取り周期性を見る

周期性の確認は、コンソールを目視するより CLI で引いた方が速い。[SORACOM CLI](https://users.soracom.io/ja-jp/tools/cli/) のセッションイベント取得コマンドを使う。

```bash
# --sim-id は自分の SIM の ID に置き換える
soracom sims session-events --sim-id 8981100000000000000

# 期間を絞る（--from / --to は UNIX time の「ミリ秒」）
# 例: 2026-08-19 00:00 〜 2026-08-20 00:00 (JST)
soracom sims session-events \
  --sim-id 8981100000000000000 \
  --from 1755561600000 \
  --to 1755648000000 \
  --fetch-all

# 1 行 1 JSON で吐いて、そのまま集計に流す
soracom sims session-events --sim-id 8981100000000000000 --fetch-all --jsonl
```

対応する API は `Sim:listSimSessionEvents` である。

1 件のイベントはこういう形をしている（値は伏せてある）。

```json
{
  "time": 1755594000000,
  "event": "Deleted",
  "imsi": "44010xxxxxxxxxx",
  "imei": "35xxxxxxxxxxxxx",
  "ueIpAddress": "10.xxx.xxx.xxx",
  "apn": "soracom.io",
  "cell": { "radioType": "lte", "mcc": 440, "mnc": 10, "tac": 1234, "eci": 56789012 }
}
```

切り分けに効くのは `cell.eci`（E-UTRAN Cell Identifier）と `ueIpAddress` の 2 つだ。

- **`cell.eci`** — `Deleted` → `Created` の前後で変わっているなら基地局をまたいでいる（＝無線区間側の事情）。変わっていないなら、同じセルに居たままセッションだけが落ちている（＝タイマー満了かデバイス側の張り直し）。層を絞り込む材料が、同じログの中に入っている。
- **`ueIpAddress`** — 張り直しで IP が変わったかどうかを、推測ではなくログで確認できる。固定 IP 前提のシステムを組んでいるなら、ここは必ず見る。

周期性の確認は `--jsonl` の出力を `jq` に流すだけでよい。`Deleted` の発生間隔（秒）を並べる:

```bash
soracom sims session-events --sim-id 8981100000000000000 --fetch-all --jsonl \
  | jq -s '[.[] | select(.event == "Deleted") | .time] | sort
           | . as $t | [range(1; length)] | map(($t[.] - $t[.-1]) / 1000)'
```

この間隔が送信周期にきれいに揃うなら、それはもう答えが出ている。ばらついていたら、次はセル ID を見る。

## `soracom sims delete-session` で自動復旧能力を事前検証する

「切れたあと自動で復旧するか」は、障害が起きてから確認するものではない。**わざと切って試せる。**

> ⚠️ 以下は対象 SIM の通信を実際に落とすコマンドである。稼働中の監視系では、実施タイミングを関係者と合意してから叩くこと。

```bash
# 対象 SIM のセッションを切断する
soracom sims delete-session --sim-id 8981100000000000000
```

API は `Sim:deleteSimSession`。コンソールからは [SIM 管理] → 対象 SIM を選択 → [操作] → [セッションを切断] でも実行できる。

このあとの挙動が、そのまま自動復旧能力の答えになる。

- **自動セッション確立機能があるデバイス**：自動的に「オンライン」に戻る
- **ない場合**：機内モードの切り替え、PPP の再起動、あるいは本体の再起動といったデバイス操作が必要になる

後者だった場合、現場で `Deleted` が出たときに誰かが行って再起動しなければならないと判明する。遠隔監視のシステムとしては、そこが本当の弱点である。人が行かずに復旧させる手段まで含めた設計は[建設・工事現場の遠隔監視ニーズを整理した記事](/blogs/posts/2026/07/soracom-iot-construction-site-demand/)や、OTA での遠隔管理を扱った[balenaCloud で Raspberry Pi を管理する記事](/blogs/posts/2026/05/balenacloud-raspberry-pi-iot-management/)の領域に入る。

なおこのセッション切断は、VPG の変更など一部の設定を反映させる正規の手順としても使われる。運用手順に組み込んでおいて損はない。

## まとめ

- 長時間稼働中の `Deleted` → `Created` は、多くは仕様の範囲内。ただし「よくあること」で止めると実害を見逃す
- 「セッション」は 4 層にまたがる言葉で、観測できるのは一番下の層だけ。ログの形から上の層を推定する
- ハンドオーバーは `Modified`。`Deleted` ではない
- PSM / eDRX は再アタッチを**避ける**ための仕組み。`Deleted` が出るのは、スリープが無通信タイマーより長いから
- 判定軸は回数ではなく、**送信周期との一致**
- `soracom sims session-events` で履歴を引き、`cell.eci` と `ueIpAddress` の変化まで見る。`soracom sims delete-session` で復旧能力を事前に検証する

「よくある現象です」は正しい。だが、それを言えるようになるまでに確認すべきことは、思っているより具体的だ。

## 参考リンク

- [詳細: セッション | SORACOM Users 用語集](https://users.soracom.io/ja-jp/resources/glossary/session/)
- [IoT SIM の通信状況 (セッション) を確認する | SORACOM Users](https://users.soracom.io/ja-jp/docs/air/view-stats/)
- [IoT SIM のセッションを再確立する | SORACOM Users](https://users.soracom.io/ja-jp/docs/air/delete-session/)
- [SORACOM Air for セルラーの診断 | SORACOM Users](https://users.soracom.io/ja-jp/guides/diagnostic/air-for-cellular/)
- [SORACOM CLI 利用ガイド | SORACOM Users](https://users.soracom.io/ja-jp/tools/cli/)
- [接点入出力搭載 LTE-M 対応 IoT ゲートウェイ「SmartFitPRO シリーズ」| SORACOM 公式ブログ](https://blog.soracom.com/ja-jp/2023/07/14/smartfitpro-overview-with-soracom/)
- [Power Saving Mode (PSM) in UEs | Cisco MME Administration Guide](https://www.cisco.com/c/en/us/td/docs/wireless/asr_5000/21-27/mme-admin/21-27-mme-admin/21-17-MME-Admin_chapter_01000110.html)
- [PSM and eDRX features in LTE-M and NB-IoT | IoT For All](https://www.iotforall.com/what-are-psm-and-edrx-features-in-lte-m-and-nb-iot)
