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

## 代替選択肢は Grafana プラグインとして追加できるのか

「Karma や Apprise を Grafana サーバーにプラグインとして組み込めばいいのでは」という疑問が出てきます。**正確な答え: 大半は Grafana プラグインではなく独立サービス**です。プラグイン化できるかどうかは、種類によってまったく違います。

### Grafana のプラグインアーキテクチャ

Grafana のプラグインは 3 種類:

1. **Panel plugin** — ダッシュボード内のカスタムパネル
2. **Data source plugin** — 新しいデータソース接続
3. **App plugin** — Grafana 内に独自ページを持つフルアプリ

OnCall 系の機能を提供できるのは **App plugin** ですが、現実にはほとんどの代替が「プラグインではなく外部サービス」です。

### 各代替選択肢のプラグイン化可否

| 選択肢 | プラグイン化 | 形態 |
|---|---|---|
| **Grafana OnCall（過去）** | ◯（App plugin） | `grafana-oncall-app` + 別エンジンの 2 層、**アーカイブ済** |
| **Grafana Cloud IRM** | ✕（Cloud 限定） | Grafana Cloud 上でのみ動作、OSS サーバーには入らない |
| **Karma** | ✕ | Alertmanager 専用 Web UI、別プロセス・別ポート |
| **Apprise** | ✕ | Python ライブラリ / CLI、Webhook 中継として配置 |
| **Signoz** | ✕ | Grafana 競合の独立 OSS プラットフォーム |
| **PagerDuty / Opsgenie / Zenduty** | ✕ | SaaS、Webhook 連携で繋ぐ |

つまり **「Grafana サーバーに何かを追加するだけで OnCall 相当が手に入る」道は、OnCall OSS のアーカイブで完全に閉じた**のが現状です。

### Grafana 標準機能だけでどこまでできるか（プラグイン不要）

Grafana 8 以降の **Unified Alerting** には、実はかなりの機能が標準装備されています。

#### 標準で使える機能

- **アラートルール定義**（PromQL / LogQL / SQL ベース）
- **Contact Points**（通知先）— 標準で 20 種類以上対応:
  - Slack / Microsoft Teams / Discord / Telegram / LINE Notify
  - Email / Webhook
  - PagerDuty / Opsgenie（SaaS と連携）
  - Pushover / Pushbullet
  - SNS（AWS）/ Google Chat
- **Notification Policies**（ルーティングツリー）— ラベルベースでチーム分け
- **Mute Timings**（時間帯ベースのミュート）
- **Silences**（一時ミュート）
- **Templates**（通知テンプレート）

これだけで「**チーム別 Slack 通知 + critical は PagerDuty + 業務時間外は別ルーティング**」までは **プラグインなしで完結**します。

#### 標準では足りない機能

- **シフト管理 / オンコールローテーション** — 「今週は田中さん、来週は佐藤さん」の時間切替
- **エスカレーションポリシー** — 「2 分応答なければ次の人へ」
- **音声通話通知** — SMS は webhook で可能だが、自動電話には専用サービスが必要
- **モバイルプッシュ通知の専用アプリ** — Grafana Mobile はあるがオンコール特化機能は薄い
- **Acknowledge / Resolve のワークフロー管理**
- **ポストインシデントタイムライン**

これらは**プラグインでは実装できない領域**で、専用サービス（IRM / PagerDuty 等）が必要になる根本理由です。シフト管理だけでも、カレンダー・タイムゾーン・休暇管理・ユーザー在不在の追跡が必要で、これを Grafana のアプリプラグインだけで完結させるのは設計上難しい。

### プラグイン形式の限界と現実解

「プラグインで済ませたい」という発想自体が、OnCall OSS が成立していたからこそ可能だったものです。アーカイブ後の現実解は **「Grafana 標準アラート + 外部サービスの Webhook 連携」のハイブリッド**:

```text
[Grafana OSS サーバー]          ← プラグインで賄う部分
   ├─ アラートルール定義
   ├─ Contact Points
   └─ Notification Policies
        ↓ webhook
[外部サービス]                   ← プラグインでは賄えない部分
   ├─ Karma（Alertmanager UI 補完、別プロセス）
   ├─ Apprise（通知ハブ、別プロセス）
   ├─ シフト管理（自作 or Zenduty 等の安価 SaaS）
   └─ 音声通話・モバイルプッシュ（Twilio / SaaS）
```

判断基準:

- **アラート発火 + ルーティング + チャット通知まで** → Grafana 標準のみで OK、プラグイン不要
- **シフト管理 + エスカレーション + 音声通話まで** → 外部サービス必須、プラグインでは足りない

中規模以上のチームで本格的なオンコール運用を組むなら、**「シフト管理は SaaS に任せ、Grafana 側はアラート発火に専念」**が最もコスト効率が良い構成です。

## Apprise + 自作 Web サービスで「ack URL + エスカレーション」を組む

「**メール通知に承認 URL を埋め、一定時間踏まれなかったら次の担当へ自動エスカレーション**」というシンプルなフローなら、Apprise + 軽量な Web サービスで素直に実装できます。OSS 諦めない派にとって、自作の現実的な落としどころです。

### 全体フロー

```text
[Grafana Alerting]
      ↓ webhook
[自作 Web サービス（Ack & Escalation）]
   ├─ アラート受信 → DB に登録
   ├─ ユニークな ack URL 発行
   └─ Apprise で通知送信
        ↓
[1次担当者にメール]
   "障害発生。承認するには ↓ をクリック
    https://oncall.example.com/ack/abc123"
        ↓
   ┌─ N 分以内にクリック → 解決済みに更新、終了
   └─ N 分タイムアウト  → 2次担当者にメール（新 URL）
                            → さらに N 分待つ → 3次担当 → ...
```

### 最小実装サンプル（FastAPI + Apprise + SQLite + APScheduler）

```python
# main.py（抜粋、全体で 150 行程度で動く）
import secrets
from datetime import datetime, timedelta
from fastapi import FastAPI, HTTPException
from sqlmodel import SQLModel, Field, Session, create_engine
from apscheduler.schedulers.background import BackgroundScheduler
import apprise

ESCALATION_POLICY = [
    "mailto://primary@example.com",
    "mailto://secondary@example.com",
    "mailto://manager@example.com",
]
ESCALATION_TIMEOUT_MIN = 5
BASE_URL = "https://oncall.example.com"

class Alert(SQLModel, table=True):
    id: str = Field(primary_key=True)
    title: str
    message: str
    status: str = "pending"   # pending / acknowledged / closed
    level: int = 0
    created_at: datetime = Field(default_factory=datetime.utcnow)

engine = create_engine("sqlite:///alerts.db")
SQLModel.metadata.create_all(engine)
scheduler = BackgroundScheduler()
scheduler.start()
app = FastAPI()

def send_notification(alert_id: str):
    with Session(engine) as session:
        alert = session.get(Alert, alert_id)
        if not alert or alert.status != "pending":
            return
        if alert.level >= len(ESCALATION_POLICY):
            alert.status = "closed"
            session.add(alert); session.commit()
            return

        target = ESCALATION_POLICY[alert.level]
        ack_url = f"{BASE_URL}/ack/{alert.id}"
        apobj = apprise.Apprise()
        apobj.add(target)
        apobj.notify(
            title=f"[L{alert.level + 1}] {alert.title}",
            body=(
                f"{alert.message}\n\n"
                f"承認 URL（{ESCALATION_TIMEOUT_MIN} 分以内にクリック）:\n{ack_url}\n\n"
                f"応答がなければ次の担当者へエスカレーションします。"
            ),
        )
        scheduler.add_job(
            escalate, "date",
            run_date=datetime.utcnow() + timedelta(minutes=ESCALATION_TIMEOUT_MIN),
            args=[alert_id],
            id=f"escalate-{alert_id}-{alert.level}",
            replace_existing=True,
        )

def escalate(alert_id: str):
    with Session(engine) as session:
        alert = session.get(Alert, alert_id)
        if not alert or alert.status != "pending":
            return
        alert.level += 1
        session.add(alert); session.commit()
    send_notification(alert_id)

@app.post("/webhook")
async def receive(payload: dict):
    """Grafana Alerting / Alertmanager の webhook を受ける"""
    alert_id = secrets.token_urlsafe(16)
    alert = Alert(
        id=alert_id,
        title=payload.get("title", "Alert"),
        message=payload.get("message", ""),
    )
    with Session(engine) as session:
        session.add(alert); session.commit()
    send_notification(alert_id)
    return {"alert_id": alert_id}

@app.get("/ack/{alert_id}")
async def acknowledge(alert_id: str):
    with Session(engine) as session:
        alert = session.get(Alert, alert_id)
        if not alert:
            raise HTTPException(404, "Alert not found")
        if alert.status != "pending":
            return {"message": f"Already {alert.status}"}
        alert.status = "acknowledged"
        session.add(alert); session.commit()
    for job in scheduler.get_jobs():
        if job.id.startswith(f"escalate-{alert_id}-"):
            job.remove()
    return {"message": "Acknowledged. ありがとうございます。"}
```

これだけで「webhook 受信 → メール送信 → ack URL → 5 分タイムアウト → 次担当者」が動きます。

### Grafana 側の設定

Grafana Alerting の Contact Point を **Webhook** にして、自作サービスの `/webhook` を指定:

```yaml
# Grafana Alerting Contact Point
type: webhook
settings:
  url: https://oncall.example.com/webhook
  httpMethod: POST
  username: oncall-webhook   # オプション: Basic 認証
  password: <secret>
```

通知ペイロードのテンプレートを Grafana 側で整形して、`title` と `message` を送れば自作サービス側で扱いやすくなります。

### 設計上のポイントと落とし穴

#### 1. ack URL は「推測不能 + 単発 + 期限付き」に

- `secrets.token_urlsafe(32)` で推測困難なトークン
- 1 回 ack されたら無効化
- 24 時間で自動失効
- HTTPS 必須、メール件名には書かない（プレビューでバレるため）

#### 2. SPOF（単一障害点）対策

「監視通知を司るサービス自身が落ちたら気づけない」という致命的な問題:

- **dead man's switch** — 別の監視（Grafana や UptimeRobot など）でこのサービス自体の死活監視
- 落ちたら Slack に直接投げる別経路を用意
- 可能なら 2 インスタンス冗長 + Postgres / Redis 共有

#### 3. メール配信遅延

メールは平均 10〜30 秒、最大数分の遅延があります。

- タイムアウトは「メール到達」ではなく「ack 受信」基準
- エスカレーション間隔は **最低 3〜5 分推奨**（短すぎると誤エスカレーション増）
- 急ぎなら Slack や Telegram も併用（Apprise なら多重送信が容易）

#### 4. シフト管理を組み込むなら

`ESCALATION_POLICY` を時間帯で動的に切り替える:

```python
def get_policy_for_now():
    now = datetime.now()
    if now.weekday() < 5 and 9 <= now.hour < 18:
        return ["mailto://team-a@example.com", "mailto://manager@example.com"]
    else:
        return ["mailto://oncall-tonight@example.com", "mailto://manager@example.com"]
```

カレンダー連携が必要なら Google Calendar API でシフト表を読むのが現実的。

#### 5. 永続化と再起動耐性

`APScheduler` のデフォルトはメモリベース。プロセス再起動でジョブが消えるので、本番では DB に永続化:

```python
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
scheduler = BackgroundScheduler(jobstores={
    "default": SQLAlchemyJobStore(url="sqlite:///jobs.db")
})
```

または Celery + Redis で別プロセス化。

#### 6. 監査ログ

「誰がいつ ack したか」を残しておくと、ポストインシデント分析や運用改善で役立ちます。`Alert` テーブルに `acknowledged_by_ip`, `acknowledged_at`, `user_agent` を追加。

### メリット・デメリット

#### メリット

- **超軽量** — 1 VM / Docker で動く、月 $5 程度の VPS で十分
- **完全に自分の支配下** — 外部 SaaS 依存ゼロ、データ主権
- **柔軟** — 業務固有のルール（特定 alert は別ルート、お盆休みは特別ローテ）を素直に書ける
- **Apprise で 70 種類の通知先に対応可能** — 後から Slack / LINE / Pushover 追加も容易

#### デメリット・限界

- **モバイルプッシュ通知**はメール頼みなので深夜の確実な起床は弱い → Pushover / Pushbullet を Apprise 経由で組み合わせると改善
- **音声通話**はできない → Twilio API を組み込めば可能だがコード追加必要
- **GUI でのシフト管理**はない — 設定は YAML / コード管理になる
- **ポストインシデントテンプレート**などは無い
- **SPOF リスク**が大きい — マネージド SaaS と違い自分で可用性を確保する必要

### 規模別の判断

| 規模 | 推奨 |
|---|---|
| **1〜3 人体制、週数件のアラート** | この自作サービスで十分 |
| **5〜10 人、エスカレーション + 簡易シフト** | 自作 + シフト管理を YAML / Calendar 連携で拡張 |
| **10 人超、24/7 シフト + 電話通知** | Zenduty（$7〜）など安価 SaaS の方がトータルコスト低 |
| **エンタープライズ、コンプライアンス必須** | PagerDuty / Grafana Cloud IRM |

### 既存 OSS で似たアプローチ

ゼロから作るのが面倒なら、近い思想の OSS:

- **[Alerta](https://github.com/alerta/alerta)** — アラート集約 + ack / 手動シェルブ機能
- **[OneUptime](https://oneuptime.com/)** — オンコール + インシデント + ステータスページの OSS
- **[Cabot](https://github.com/cabotapp/cabot)** — シンプルな OSS 監視 + 通知（やや古い）

これらは「自作」と「フル SaaS」の中間に位置します。

「**Apprise + FastAPI 150 行で OnCall の核を再現**」できることが分かると、OnCall OSS のアーカイブ後の心理的インパクトはかなり下がります。中身をブラックボックスにせず、自分の手で組める範囲で済ませる選択肢が現実的に存在します。

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
