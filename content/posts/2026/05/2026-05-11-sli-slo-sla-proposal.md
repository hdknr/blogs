---
title: "SLI / SLO / SLA の違いと使い分け — 提案書で失敗しないサービスレベル設計入門"
date: 2026-05-11
lastmod: 2026-05-11
draft: false
source_url: "https://gist.github.com/hdknr/f23c06b2006ce70df78d6702ddc9f3db"
categories: ["クラウド/インフラ", "ビジネス/キャリア"]
tags: ["SRE", "SLO", "SLA", "提案書", "エラーバジェット"]
---

IoT システムや SaaS の提案書を書いていると、お客様から「このシステム、ちゃんと動くんですか?」と聞かれます。**この質問にどう答えるか** で、契約交渉の主導権が決まります。

「99.9% 動きます」と言い切れば SLA（契約）になり、下回ったら違約金。「目標値です」と言えば SLO（内部目標）で、未達でも返金義務はない。**この 1 文字違いで法的拘束力が変わります**。

本記事では、SRE（Site Reliability Engineering）業界で標準となっている **SLI / SLO / SLA** の 3 用語の **違いと使い分け** を、提案書を書く立場から整理します。

## 3 用語の違い（要点）

| 略語 | 正式名 | 一言で | 性格 |
| --- | --- | --- | --- |
| **SLI** | Service Level **Indicator** | 計測する指標 | データ |
| **SLO** | Service Level **Objective** | 目指す目標 | **内部約束** |
| **SLA** | Service Level **Agreement** | 契約上の保証 | **対外契約** |

順序は **SLI → SLO → SLA** で考えます。

1. **SLI** で「何を測るか」を決める（例: イベント検知から通知メール送信までの遅延時間）
2. **SLO** で「目標値」を内部で握る（例: 95%ile が 60 秒以内）
3. **SLA** で「契約条項」に格上げする（例: SLO 違反が月 3 件超えたら月額の 10% 返金）

## なぜ 3 つに分かれているのか

**Google SRE Book** が提唱した「エラーバジェット」の考え方が背景にあります。

> 100% を目指すと、**新機能が出せなくなる**。99.9% を許容することで、0.1% の失敗を「許される予算」として、新規開発・実験・障害対応の余地を作る。

つまり SLO は **「これより悪くなったら開発を止めて運用に集中する」** という運用判断のトリガーです。SLA より緩めに設定し、超過分のバッファを意図的に残します。

### 典型的な数値関係

![SLA（契約）99.0% は SLO（内部目標）99.5% より緩く設定し、実測（SLI 集計）99.7% との間にバッファを確保する3段階の関係図](/blogs/images/sli-slo-sla-relationship.png)

顧客と交わす SLA は最も緩く、SLO で内部目標を握り、実測（SLI）はそれを上回るように運用する。3 段階のバッファが「予期せぬ障害でも SLA を割らない」マージンを生みます。

## 実例: IoT 設備異常通知システム

ある SaaS 提案書での書き分け例（顧客名・サービス名は匿名化）:

| 指標（SLI） | SLO（Phase 1 内部目標） | SLA（Phase 2 契約格上げ案） |
| --- | --- | --- |
| イベント検知 → メール送信遅延 | 95%ile **< 60 秒** | 95%ile < 120 秒 |
| メール到達率 | **99.0%**（バウンス除く） | 98.5% |
| 拠点ゲートウェイ稼働率 | **99.0% / 月** | 98.0% / 月 |
| 配信ルール変更反映時間 | **< 30 秒** | < 5 分 |

SLO（Phase 1）は社内で厳しめに握る目標値、SLA（Phase 2）は契約として顧客と約束する数値です。**SLA を SLO より緩く設定する** ことで、突発障害があっても契約違反にならないバッファを確保します。

→ Phase 1 PoC で **SLI を 1 ヶ月実測** し、現実的な達成率を把握してから SLA に格上げ。「100% 60 秒以内」と契約書に書くと、LTE 回線の一時不調 1 件で SLA 違反になるため、**95%ile（遅い方から 5% を除外した値）** を使うのが運用業界の標準です。

## よくある誤解

### 誤解 1: 「SLA = SLO の数値そのまま」と思い込む

SLA は **法的拘束力** があるので、SLO より **必ず緩く** 設定します。SLO 99.5% に対し SLA 99.0%、のように 0.5%〜1% のバッファを取るのが定石です。

### 誤解 2: SLI を決めずに SLO を語る

「稼働率 99%」と言われても、**何が「稼働」なのか** が曖昧だと意味がありません。

- ping が通れば稼働? → SLI = ping 応答率
- メールが実際に届けば稼働? → SLI = end-to-end 到達率

**SLI の定義（測定境界・カウント方法）を先に握る** のが鉄則です。

### 誤解 3: 100% を目指す

100% SLA は **コストが指数関数的に増える** だけでなく、わずかな障害で違反になるため、**営業上のリスクが高すぎる**。99.9% でも年間 **約 8.76 時間** のダウンタイム余地があり、これが障害対応・メンテナンス窓口になります。

## 提案書での実務的な書き方

1. **PoC 段階では SLO のみ提示** — 「目標値です、Phase 2 で SLA に格上げ判断」と前置きする
2. **PoC で SLI を 1 ヶ月実測** — 達成困難な数値を最初から契約しない
3. **SLA 違反時の返金条項を分離** — 「SLO 達成義務」と「違反時返金」は別条項に
4. **エラーバジェット消費を可視化** — 「今月は SLO 99.5% に対し 99.7%、余裕 0.2pt」のような月次レポート

## まとめ

| やってはいけない | 推奨 |
| --- | --- |
| 「99.9% 動きます」と口頭で約束 | SLI / SLO / SLA を文書で分ける |
| SLO と SLA を同じ数値にする | SLA は SLO より緩く（バッファ確保） |
| 100% を約束する | 99.X% に止めてエラーバジェットを残す |
| 実測なしで SLA を切る | PoC で 1 ヶ月実測してから SLA 化 |

提案書に「**SLO（Service Level Objective）: 内部目標。Phase 2 で SLA に格上げ判断**」の 1 行があるだけで、客先との期待値ギャップが大きく縮まります。

## 関連記事

- [現代的サーバー監視の王道スタック — Prometheus + Loki + Grafana + Alloy](/blogs/posts/2026/05/2026-05-08-prometheus-loki-grafana-server-monitoring-stack/) — SLI の実測手段（Prometheus / PromQL）
- [Grafana OnCall は終わった、Grafana Cloud IRM が始まった](/blogs/posts/2026/05/2026-05-08-grafana-oncall-irm-incident-response/) — SLO 違反時のオンコール体制
- [Google シニア SRE 面接 2026 — Coding/System Design/Behavioral 対策](/blogs/posts/2026/04/2026-04-30-google-senior-sre-interview-2026/) — SRE の体系的な知識を問う面接

## 参考

- [Google SRE Book — Service Level Objectives](https://sre.google/sre-book/service-level-objectives/)（公開無料）
- [Google SRE Workbook — Implementing SLOs](https://sre.google/workbook/implementing-slos/)
- [Atlassian SRE Handbook — SLA vs SLO vs SLI](https://www.atlassian.com/incident-management/kpis/sla-vs-slo-vs-sli)
