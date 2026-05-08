---
title: "Grafana OnCall は終わった、Grafana Cloud IRM が始まった — オンコール体制の現代的選択肢を整理する"
date: 2026-05-08
lastmod: 2026-05-08
draft: false
categories: ["クラウド/インフラ"]
tags: ["Grafana OnCall", "Grafana Cloud IRM", "PagerDuty", "Opsgenie", "オンコール", "インシデント対応", "SRE", "監視", "オブザーバビリティ"]
---

[前回の記事](/blogs/posts/2026/05/2026-05-08-prometheus-loki-grafana-server-monitoring-stack/)で「サーバー監視の王道スタック」として Prometheus + Loki + Grafana + Alloy を整理しました。アラート設計のセクションで触れた **Grafana OnCall** について、改めて単独で深掘りします。

ただし重要な注意点があります — **Grafana OnCall OSS（grafana/oncall リポジトリ）は 2026 年 3 月 24 日にアーカイブされました**。後継は **Grafana Cloud IRM（Incident Response Management）**で、OnCall と Incident の両アプリが 1 つに統合されています。

「Grafana OnCall を新規導入したい」「既存環境を移行すべきか」という人に向けて、**何が終わって、何が始まったのか**を整理します。

## Grafana OnCall とは何だったのか

Grafana OnCall は **「アラートが鳴った後の対応フロー」を管理するツール**でした。

- Prometheus / Loki / Grafana が「**異常を検知する**」までを担当
- Grafana OnCall は「**鳴ったアラートを誰に・どうやって届け、どう対応するか**」を管理

PagerDuty や Opsgenie の OSS 互換ツールとして、Grafana エコシステムの中で重要なポジションを占めていました。

### 主な機能（当時）

1. **アラートの集約とルーティング** — 複数の監視システムからのアラートを統合、内容に応じてチームへ振り分け
2. **オンコールシフト管理** — 担当者のカレンダー（シフト表）に従って当番者にだけ通知
3. **エスカレーションポリシー** — 一定時間応答がなければ次の担当者へ自動エスカレーション
4. **ChatOps 連携** — Slack / Telegram 上でアラート確認・対応開始（Acknowledge）・解決（Resolve）が完結
5. **柔軟な通知手段** — Slack / Microsoft Teams / SMS / 自動音声通話（電話）/ モバイルプッシュ
6. **IaC 対応** — Terraform プロバイダで設定をコード管理可能

### 連携先（インテグレーション）

| カテゴリ | 代表的な連携先 |
|---|---|
| 監視・アラート検知 | Grafana, Prometheus (Alertmanager), Datadog, Zabbix, AWS CloudWatch, New Relic |
| 通知・コミュニケーション | Slack, Microsoft Teams, Telegram, SMS, 自動音声通話 |

OSS 版で自社サーバーに構築することも、Grafana Cloud のマネージドサービスとして利用することも可能でした。

## 「終わった」というのはどういうことか — タイムライン

| 日付 | できごと |
|---|---|
| **2025-03-11** | Grafana OnCall OSS が **read-only / メンテナンスモード** に移行 |
| **2025-03 頃** | Grafana Cloud IRM（OnCall + Incident 統合）が全 Grafana Cloud 環境にロールアウト |
| **2026-03-24** | **`grafana/oncall` リポジトリがアーカイブ** |
| **2026-03-24** | OnCall OSS の **Cloud Connection 機能（SMS / 電話 / プッシュ通知のクラウド経由配信）が停止** |
| **2026-05（現在）** | OSS 版を新規構築する選択肢は事実上なくなり、IRM か他社ツールへ |

つまり**現時点で Grafana OnCall OSS を新規導入する理由はほぼありません**。既存の OSS 環境を運用している場合は、Cloud Connection 停止で SMS / 電話通知が動かなくなっているはずなので、移行が必須です。

## 後継: Grafana Cloud IRM とは

**Grafana Cloud IRM (Incident Response Management)** は、従来の Grafana OnCall と Grafana Incident（インシデントマネジメントアプリ）を**1 つの統合アプリにまとめた**もの。

### 従来の役割分担と統合

```text
[従来]
 Grafana OnCall  : アラート → 通知 → エスカレーション
 Grafana Incident: インシデントが発生した後のドキュメント・タイムライン・ポストモーテム

[統合後]
 Grafana Cloud IRM: アラート → オンコール → インシデント対応 → 振り返りまで一気通貫
```

### 主な特徴

- **Grafana オブザーバビリティスタックとの深い統合** — Prometheus / Loki / Tempo のデータが標準でインシデントに紐付く
- **モバイル・チャットファースト** — Slack / Microsoft Teams 内で完結
- **ポストインシデントプロセス内蔵** — タイムライン自動記録、振り返りテンプレート、SLO 連動
- **統一されたインテグレーション** — OnCall と Incident で別々だった webhook / 連携が 1 つに

### 価格

Grafana Cloud IRM は **Grafana Cloud 上の有料アドオン**:

- **$20 / IRM ユーザー / 月**（月次アクティブユーザーベース）
- 加えて **$19 の Platform fee**
- 例: 20 人体制 = $20 × 20 + $19 = **$419/月**
- 別途 Grafana Cloud 本体の料金

PagerDuty が $21〜/ユーザー/月 程度なので、**1 ユーザーあたりの単価はほぼ同等**。Grafana スタックを既に使っているなら統合の利便性で IRM が有利。Grafana を使っていない組織には PagerDuty / Opsgenie の方が中立的。

## 主要競合との比較

| ツール | 価格 | 特徴 | 向いている組織 |
|---|---|---|---|
| **Grafana Cloud IRM** | $20〜/ユーザー/月 + Platform fee | Grafana スタックと統合、ポストインシデントまで | Grafana / Prometheus / Loki ユーザー |
| **PagerDuty** | $21〜/ユーザー/月 | 業界標準、エスカレーション・自動化が豊富、AIOps 充実 | エンタープライズ全般 |
| **Opsgenie**（Atlassian） | $9〜/ユーザー/月 | Jira / Confluence と統合、コスト優位 | Atlassian エコシステム |
| **AWS Incident Manager** | 従量課金 | AWS ネイティブ、CloudWatch 統合 | AWS 中心の組織 |
| **OnPage** | $13.99〜/ユーザー/月 | 医療系で実績、確実な配信 | 医療・ミッションクリティカル |
| **Zenduty** | $7〜/ユーザー/月 | 安価で機能十分、新興プレイヤー | コスト重視 |

## OSS 版を諦めない場合の代替選択肢

「OSS 縛り」「自前運用したい」「コストを最小化したい」という要件なら、以下が現実的な選択肢:

### 1. Karma（Alertmanager UI）+ 自前運用

- Alertmanager は OSS で生きている — ルーティング・サイレンス・抑制は変わらず使える
- **[Karma](https://github.com/prymitive/karma)** で Alertmanager の UI を補完
- ただし**シフト管理・エスカレーション・電話通知は別途実装が必要**

### 2. Apprise + cron でシフト管理を自前

- [Apprise](https://github.com/caronc/apprise) で 70 種類以上の通知先に統一インタフェース
- シフト表を YAML or DB で管理し、cron / Argo CronJob で「今のオンコール担当者は誰か」を webhook で発信
- 簡素だが、**フル機能の OnCall 系には及ばない**

### 3. Signoz / Uptrace 系の OSS 監視に内蔵

- **[Signoz](https://signoz.io/)** — OpenTelemetry ベースの OSS オブザーバビリティ、アラート機能内蔵
- アラートのルーティングは可能だがシフト管理は弱い

### 4. OnPage 等のリーズナブルな商用 SaaS

- フル機能を欲しいが Grafana Cloud IRM の価格は高すぎる場合の中間解
- Zenduty（$7〜）が新興だが機能十分

## アーキテクチャ的な位置付け

[前回の記事](/blogs/posts/2026/05/2026-05-08-prometheus-loki-grafana-server-monitoring-stack/)のスタックに IRM（または代替）を組み込んだ全体像:

```text
[アプリ・サーバー]
      ↓
   Alloy（収集）
      ↓
[Prometheus / Loki / Tempo]
      ↓
   アラートルール（PromQL / LogQL）
      ↓ 発火
[Alertmanager または Grafana Alerting]
      ↓ webhook
   ┌─────────────────────────┐
   │   Grafana Cloud IRM     │ ← ここを担当
   │  ・シフト管理            │
   │  ・エスカレーション      │
   │  ・ChatOps 連携          │
   │  ・ポストインシデント    │
   └─────────────────────────┘
      ↓
[担当者のスマホ / Slack / 電話]
```

「アラートが鳴る」までと「鳴ってから人が動く」のは別のレイヤーであり、**IRM はその「人が動く」部分の OS** に相当します。

## 移行ガイド: OnCall OSS → Grafana Cloud IRM

既存の Grafana OnCall OSS 環境がある場合、以下が公式の移行手順:

1. **Grafana Cloud アカウント作成** — Free tier から始められる
2. **IRM アプリを有効化** — Cloud Stack のインストール画面から
3. **OnCall OSS の設定をエクスポート** — Terraform で管理していた場合は最小の変更で移行可能
4. **Webhook 連携の付け替え** — Alertmanager の receiver URL を IRM のエンドポイントへ
5. **ユーザー・スケジュール・統合の再作成** — 公式ドキュメントの[移行ガイド](https://grafana.com/docs/grafana-cloud/alerting-and-irm/irm/set-up/migrate/oncall-oss/) に従う
6. **動作確認後、OSS 環境を停止**

OSS の Cloud Connection（SMS / 電話通知）は既に止まっているので、**音声通話やモバイル通知が動かなくなった**時点で移行は実質必須です。

## 当該プロジェクトでの導入判断

「Grafana OnCall を導入したい」と思った時点で、選択肢は以下のいずれかです:

| 状況 | 推奨 |
|---|---|
| **Grafana Cloud を既に使っている / 使う予定** | **Grafana Cloud IRM** — エコシステム統合最強 |
| **AWS 中心、コスト最小化したい** | **AWS Incident Manager** — 従量課金、CloudWatch 統合 |
| **Atlassian エコシステム** | **Opsgenie** — Jira 連携が深い |
| **エンタープライズ標準準拠が必要** | **PagerDuty** — 業界標準、監査・コンプライアンス対応強い |
| **コスト最優先 + OSS 寄り** | **Zenduty** or **OnPage** + Alertmanager + Karma |
| **完全自前 OSS 運用** | Alertmanager + Apprise + 自作シフト管理（フル機能は諦める） |

純粋な OSS で OnCall を完全代替する選択肢は弱く、**「重要なオンコール機能はマネージド SaaS に任せる」のが現実解**になっています。

## まとめ

- **Grafana OnCall OSS は 2026-03-24 にアーカイブされた** — 新規導入の選択肢ではない
- 後継は **Grafana Cloud IRM** — OnCall + Incident を統合した有料アドオン
- 価格は $20/ユーザー/月 + Platform fee で、**PagerDuty とほぼ同等**
- Grafana スタックを使っているなら IRM が最有力、そうでなければ PagerDuty / Opsgenie / Zenduty
- 「アラート発火」と「人が動く」は別レイヤーで、後者の管理を専用ツールに任せるのが現代の SRE プラクティス

OnCall OSS の終了は寂しいニュースですが、Grafana Cloud IRM は OSS 版より機能的に明確に進化しています。Grafana オブザーバビリティスタックを既に使っているチームには、自然な拡張として導入を検討する価値があります。

## 参考リンク

- [Grafana Cloud IRM 製品ページ](https://grafana.com/products/cloud/irm/)
- [Grafana Cloud IRM 紹介ブログ（OnCall + Incident 統合）](https://grafana.com/blog/oncall-management-incident-response-grafana-cloud-irm/)
- [Grafana OnCall OSS アーカイブ告知](https://grafana.com/docs/oncall/latest/set-up/open-source/)
- [OnCall OSS から Grafana Cloud IRM への移行ガイド](https://grafana.com/docs/grafana-cloud/alerting-and-irm/irm/set-up/migrate/oncall-oss/)
- [Grafana Cloud 価格表](https://grafana.com/pricing/)
- [grafana/oncall（アーカイブ済みリポジトリ）](https://github.com/grafana/oncall)
