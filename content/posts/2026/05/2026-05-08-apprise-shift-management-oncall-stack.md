---
title: "Apprise + シフト管理ツールで OnCall 自作スタックを組む — PyShift・OR-Tools・GoAlert の役割と選び方"
date: 2026-05-08
lastmod: 2026-05-08
slug: "apprise-shift-management-oncall-stack"
draft: false
categories: ["クラウド/インフラ"]
tags: ["Apprise", "シフト管理", "オンコール", "PyShift", "GoAlert", "OR-Tools", "PuLP", "Python", "OSS", "オブザーバビリティ", "Microsoft Teams", "Microsoft Graph", "Outlook", "Microsoft Shifts"]
---

[前回の記事](/blogs/posts/2026/05/grafana-oncall-irm-incident-response/)で「Apprise + 自作 Web サービスで OnCall 相当を組む」例を示しました。この記事ではよくある誤解を整理し、**シフト管理を含めた自作 OnCall スタックの現実的な選択肢**を深掘りします。

## まずは Apprise の正しい位置付けを確認

[Apprise](https://github.com/caronc/apprise) は名前から「シフト管理ができそう」と誤解されがちですが、実際の役割は明確に分かれています。

**正しい位置付け**:

- Apprise は **「通知の超便利ハブ」** — 1 つのコードで Slack / メール / SMS / LINE / Telegram など 100 種類以上の通知先に統一インタフェースで送る
- **シフト管理機能（カレンダー、ローテーション、当番判定）は持たない**
- 「シフト管理に Apprise を使う」とは、**シフトロジックは別のライブラリ / DB / カレンダーで持ち、通知配信だけ Apprise に任せる**という意味

つまり Apprise は「**組んだシフトを確実に届ける道具**」であり、「シフトを組む道具」ではありません。前回記事のコード例で `get_policy_for_now()` を Python で書いていたのは、まさにこの「シフト判定ロジックを自作」の実装です。

## シフト管理を「自作する場合」に組み合わせる Python ライブラリ

シフトロジックを自分で書くなら、以下のライブラリが Apprise と相性が良い。

### 1. PyShift（point85/PyShift） — 古典的なシフトローテ

[point85/PyShift](https://github.com/point85/PyShift) は、Java 版の Shift ライブラリを Python に移植したもの。PyPI では `PyWorkShift` として配布されています。

```python
from PyShift.workschedule.work_schedule import WorkSchedule
from PyShift.workschedule.shift import Shift
from datetime import time, timedelta, date

# 8 時間 3 交代制
schedule = WorkSchedule("3 Shift Rotation", "Day-Swing-Night")
day_shift   = schedule.create_shift("Day",   "Day shift",   time(7, 0),  timedelta(hours=8))
swing_shift = schedule.create_shift("Swing", "Swing shift", time(15, 0), timedelta(hours=8))
night_shift = schedule.create_shift("Night", "Night shift", time(23, 0), timedelta(hours=8))

# ローテーション: 5 日勤 → 2 休 → 5 夕勤 → 2 休 → 5 夜勤 → 2 休
rotation = schedule.create_rotation("28-day cycle", "")
rotation.add_segment(day_shift,   5, 2)
rotation.add_segment(swing_shift, 5, 2)
rotation.add_segment(night_shift, 5, 2)

# A チームは 2026-01-01 開始でこのローテに従う
team_a = schedule.create_team("A team", "", rotation, date(2026, 1, 1))

# 「今日、A チームは何のシフト？」を判定
shift_today = team_a.get_shift_instance_for_day(date.today())
print(shift_today)
```

**Apprise との連携イメージ**:

```python
import apprise
# 当番者を PyShift で判定
on_call_team = team_a if team_a.is_working(now) else team_b
# Apprise で通知
apobj = apprise.Apprise()
apobj.add(f"mailto://{on_call_team.email}")
apobj.notify(title="Alert", body="...")
```

工場・病院・ホテルなどの**規則的なローテーション**には強いが、IT のオンコールのように「毎週 1 人ずつ持ち回り」「祝日避けて再配置」といった柔軟性は弱め。

### 2. PuLP / Google OR-Tools — 最適化ベースのシフト生成

複雑な制約があるシフト割当（「夜勤明けの日勤禁止」「週 40 時間以内」「全員平等にカバー」）を**最適化問題として解く**ライブラリ。

- **[PuLP](https://github.com/coin-or/pulp)** — 線形計画法、シンプル
- **[Google OR-Tools](https://developers.google.com/optimization)** — より高性能、CP-SAT ソルバ搭載

シフト表は **生成して DB / YAML に保存**し、運用時はそれを読んで Apprise で通知、という構成が一般的。

```python
# OR-Tools の例（簡略化）
from ortools.sat.python import cp_model

model = cp_model.CpModel()
# 変数: shifts[(emp, day, shift_type)] = 0 or 1
# 制約: 1 日 1 シフトまで、夜勤明けは休、最低人数確保 ...
# 目的関数: 不公平最小化
solver = cp_model.CpSolver()
solver.Solve(model)
# 結果を schedule.yaml に出力
```

「シフト表を毎月自動生成 → DB に投入 → 運用中は Apprise で通知」が王道パターン。

### 3. Google Calendar + Python + Apprise（最も実用的）

実は**最も手軽で広く使われている**のはこの組み合わせ。「ガチガチのシフトソフト」より、Google Calendar を共有してそこで運用する方が圧倒的に現場で機能します。

#### 「個別予定の共有」ではなく「1 つの共有カレンダー」が基本

よくある誤解として「担当者ごとに予定を作って共有するのか？」がありますが違います。**「OnCall シフト」という 1 つの専用カレンダーを作り、シフトイベントを並べて、チーム全員に閲覧権限で共有する**のが標準パターンです。

```text
[「Engineering OnCall」というカレンダー（1 つだけ）]
   ├─ 2026-05-08 09:00 〜 2026-05-15 09:00  「[Primary] 田中」
   ├─ 2026-05-15 09:00 〜 2026-05-22 09:00  「[Primary] 佐藤」
   ├─ 2026-05-22 09:00 〜 2026-05-29 09:00  「[Primary] 鈴木」
   ├─ 2026-05-08 09:00 〜 2026-05-15 09:00  「[Secondary] 山田」 ← 別イベント
   └─ ...

   ↓ チーム全員に「閲覧権限」で共有
   ↓ 編集権限は管理者のみ

[Web サービス（Apprise + 自作）]
   API で「今この時刻に該当するイベント」を取得
   → イベントから担当者メールを抽出
   → Apprise で通知
```

| やり方 | 特徴 |
|---|---|
| ❌ **個別の予定を各担当者と共有** | 1 件ずつ招待を送る運用、シフト変更が面倒、全体像が見えない |
| ✅ **1 つの共有カレンダーに当番イベントを並べる** | カレンダー全体を見れば全シフトが俯瞰、編集も 1 箇所 |

#### セットアップ手順

1. **専用カレンダーを作成** — `Engineering OnCall` などの名前で、個人予定とは分離
2. **権限を設定** — チーム全員は閲覧、シフト管理者のみ編集、API 連携用にサービスアカウントを読み取り権限で追加
3. **シフトイベントを作成** — タイトルや説明欄に担当者のメールアドレスを入れる
4. **階層分けは「カレンダーを分ける」のが最も実装が楽** — `OnCall-Primary`、`OnCall-Secondary` の 2 つに分けると API も読みやすい

#### 「今の当番」を取得する Python コード

```python
from googleapiclient.discovery import build
from google.oauth2 import service_account
from datetime import datetime, timezone

# サービスアカウントで認証
creds = service_account.Credentials.from_service_account_file(
    "sa-key.json",
    scopes=["https://www.googleapis.com/auth/calendar.readonly"],
)
calendar = build("calendar", "v3", credentials=creds)

def get_current_oncall(calendar_id: str) -> str | None:
    """カレンダーから「今この時刻の当番者」のメールを返す"""
    now = datetime.now(timezone.utc)
    events = calendar.events().list(
        calendarId=calendar_id,
        timeMin=now.isoformat(),
        timeMax=now.isoformat(),  # 開始 ≤ now < 終了 が拾える
        singleEvents=True,
    ).execute()

    for event in events.get("items", []):
        summary = event.get("summary", "")
        if "@" in summary:
            return summary.split()[-1]  # "[Primary] tanaka@example.com" → "tanaka@example.com"
    return None

primary   = get_current_oncall("primary-oncall@group.calendar.google.com")
secondary = get_current_oncall("secondary-oncall@group.calendar.google.com")

# Apprise で通知
import apprise
apobj = apprise.Apprise()
apobj.add(f"mailto://{primary}")
apobj.notify(title="Alert", body="...")
```

#### メリット

1. **担当者がカレンダーを「自分の予定」として確認できる** — 「来週は当番だ」を Calendar アプリが通知してくれる
2. **シフト変更がドラッグ&ドロップ** — 「来週入院するから誰か変わって」を 30 秒で対応
3. **休暇・代理対応**もカレンダーで普通に編集
4. **過去ログが残る** — 「あのインシデント時の当番は誰だったか」が後から正確にわかる
5. **モバイルで全員が見られる** — Calendar アプリを入れればすぐ
6. **API 連携が簡単** — Google 公式
7. **追加コストゼロ** — Workspace に既に含まれている

#### 落とし穴

- **タイトルから担当者を抽出するのは脆弱** — 表記ゆれで失敗する。説明欄や `attendees` フィールドに正規化して入れるか、Extended Properties を使うと堅牢
- **タイムゾーンの扱い** — UTC と JST が混ざるので API では明示的に指定（`datetime.now(timezone.utc)`）
- **「終日」イベントは避ける** — 時刻判定が曖昧になるので必ず時刻付きイベント
- **シフト境界の瞬間** — 月曜 09:00:00 ぴったりは前後どちらか、`timeMin = now - 1秒` などで安全側に倒す
- **「今の」イベントが複数返る** — 階層別カレンダーで分けるか、優先度ルールを決める

#### 代理対応のパターン

「田中さんが来週休みなので佐藤さんに代わる」場合:

- **カレンダーで田中のイベントを佐藤に書き換える** — 最も簡単
- **田中のイベントを「OOO」に変更し、佐藤の代理イベントを追加** — 履歴を残したい場合
- **`OnCall-Override` 専用カレンダーを別に持つ** — そちらに該当者がいればそちらを優先

「予定をひとりずつに送る」のではなく、**「全員が見られる単一のシフト表 = カレンダー」**がポイントです。

### 4. Microsoft 365 / Teams 環境で同じ運用を行う

「Google Calendar 運用」を Microsoft 365 / Teams 環境でやりたい場合、**完全に同じパターンが成立**します。コンポーネントを差し替えるだけで思想は同じです。

#### コンポーネントの対応関係

| 役割 | Google Workspace | Microsoft 365 / Teams |
|---|---|---|
| シフト表 | Google Calendar 共有カレンダー | **Outlook/Exchange 共有カレンダー** |
| API | Google Calendar API | **Microsoft Graph API**（統一 API） |
| 認証 | サービスアカウント | **Azure AD アプリ登録 + クライアント資格情報フロー（msal）** |
| チャット通知 | Google Chat / Slack | **Teams Incoming Webhook** |
| 専用シフト管理アプリ | — | **Microsoft Shifts**（Teams 内蔵、別パターン） |

#### パターン A: Outlook 共有カレンダー（最も直接的な移植）

Google Calendar 版とほぼ同じ構造。

セットアップ:

1. **Outlook で「Engineering OnCall」共有カレンダーを作成** — Microsoft 365 グループに紐付けるのが一般的
2. **チームに閲覧権限で共有**
3. **Azure AD でアプリ登録** — `Calendars.Read.Shared` または `Calendars.Read` の **Application permission** を付与
4. **管理者同意（admin consent）** を取得 — テナント全体への読み取り権限

Microsoft Graph API での実装:

```python
from msal import ConfidentialClientApplication
import requests
from datetime import datetime, timezone, timedelta
import apprise

TENANT_ID     = "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
CLIENT_ID     = "yyyyyyyy-yyyy-yyyy-yyyy-yyyyyyyyyyyy"
CLIENT_SECRET = "zzzzzzzzzzzzzzzzzzzzzzzz"
GROUP_ID      = "engineering-oncall@example.onmicrosoft.com"

# クライアント資格情報フローでトークン取得
app = ConfidentialClientApplication(
    CLIENT_ID,
    authority=f"https://login.microsoftonline.com/{TENANT_ID}",
    client_credential=CLIENT_SECRET,
)
result = app.acquire_token_for_client(scopes=["https://graph.microsoft.com/.default"])
token = result["access_token"]

def get_current_oncall(group_email: str) -> str | None:
    """グループカレンダーから「今の当番」のメールを返す"""
    now = datetime.now(timezone.utc)
    end = now + timedelta(seconds=1)
    url = (
        f"https://graph.microsoft.com/v1.0/groups/{group_email}/calendarView"
        f"?startDateTime={now.isoformat()}&endDateTime={end.isoformat()}"
    )
    r = requests.get(url, headers={"Authorization": f"Bearer {token}"})
    r.raise_for_status()
    for event in r.json().get("value", []):
        subject = event.get("subject", "")
        if "@" in subject:
            return subject.split()[-1]
        for a in event.get("attendees", []):
            return a["emailAddress"]["address"]
    return None

# Apprise で通知（メール + Teams 同時送信）
oncall = get_current_oncall(GROUP_ID)
apobj = apprise.Apprise()
apobj.add(f"mailto://{oncall}")
apobj.add("msteams://TOKEN_A/TOKEN_B/TOKEN_C/")  # Teams Incoming Webhook
apobj.notify(title="Alert", body=f"On-call: {oncall}")
```

#### パターン B: Microsoft Shifts（Teams 内蔵のシフト管理）

Teams には **Shifts** というシフト管理専用アプリが標準で組み込まれています。

特徴:

- **Teams の左サイドバーに常駐** — 担当者は Teams を開くたびに自分のシフトが見える
- **シフト交換・申請・承認**のワークフロー内蔵
- **タイムクロック機能**（出退勤打刻）
- **Power Automate** 連携可能
- **Microsoft Graph API（`/teams/{id}/schedule`）** でシフトデータ取得可能

```python
url = f"https://graph.microsoft.com/v1.0/teams/{TEAM_ID}/schedule/shifts"
r = requests.get(url, headers={"Authorization": f"Bearer {token}"})
shifts = r.json()["value"]
current = next(
    s for s in shifts
    if s["sharedShift"]["startDateTime"] <= now.isoformat() <= s["sharedShift"]["endDateTime"]
)
user_id = current["userId"]
```

要求権限: `Schedule.Read.All`（管理者同意必要）

#### A vs B の使い分け

| 用途 | Outlook 共有カレンダー（A） | Microsoft Shifts（B） |
|---|---|---|
| シフト表の編集 UI | カレンダーアプリ | 専用 UI（直感的） |
| シフト交換ワークフロー | なし（手動編集） | あり（依頼・承認） |
| タイムクロック | なし | あり |
| API の単純さ | 簡単（Calendar API） | やや複雑（Schedule API） |
| 適合用途 | **IT オンコール、軽量運用** | フロントライン勤務（小売・医療等） |

**IT のオンコール用途**なら Outlook 共有カレンダー（A）で十分。**交代制勤務の本格運用**なら Shifts（B）。

#### Apprise の Teams 通知連携

```python
apobj.add("msteams://TokenA/TokenB/TokenC/")
```

Teams チャネルの設定で Incoming Webhook コネクタを有効化し、生成された URL の token 部分を Apprise URL に変換するだけ。

> ⚠️ **注意**: Microsoft は Connector ベースの Incoming Webhook を **Power Automate Workflow** に段階的に移行しています。最新環境では Workflow 用 Webhook を使う必要がある場合あり。Apprise 側も `msteamswrapper` プラグインで対応中。

#### Azure AD アプリ登録時の落とし穴

- **Application permission を選ぶ**（Delegated ではない） — サービスとして動かすため
- 必要スコープ: `Calendars.Read.Shared`（A）or `Schedule.Read.All`（B）
- **管理者同意（admin consent）が必須** — テナント管理者にお願いして承認
- Client secret は Azure Key Vault などで管理、コード直書きは厳禁
- **タイムゾーン**は `Prefer: outlook.timezone="Tokyo Standard Time"` ヘッダで指定可能
- Microsoft Graph はレート制限が厳しめ — `429 Too Many Requests` のリトライ実装必須

#### 選択指針

| 状況 | 推奨 |
|---|---|
| Google Workspace 中心 | Google Calendar + Calendar API + Apprise |
| **Microsoft 365 / Teams 中心** | **Outlook 共有カレンダー + Graph API + Apprise（msteams 通知）** |
| シフト交換ワークフローも本格運用したい | **Microsoft Shifts** + Graph API + Apprise |
| シフト管理 UI を Teams に統合したい | **Channel Calendar アプリ**（バックエンドは Outlook と同じ）+ Graph API |

エンタープライズで M365 を既に契約している場合、追加コストゼロでこの構成が組めるのが大きな利点です。

## シフト管理 + 通知が「最初から統合された」OSS

「自作ではなく既製品で」という選択肢:

### GoAlert（Target 社 OSS）— OnCall OSS アーカイブ後の有力代替

[GoAlert](https://github.com/target/goalert)（Apache 2.0）は、Target 社が OSS 公開しているオンコール管理ツール。**Grafana OnCall OSS のアーカイブを受けて注目度が急上昇**しています。

**機能**:

- ブラウザ UI でドラッグ＆ドロップのシフト編集
- エスカレーションポリシー（一定時間応答なしで次の人へ）
- ローテーション + Override（一時的な交代）
- API + GraphQL での連携

**通知手段**:

- **Twilio** で SMS / 音声通話（**唯一サポートされているプロバイダ**）
- **SMTP** でメール
- **Slack** チャンネル統合

GoAlert は Twilio + SMTP + Slack を直接統合する設計で、Apprise は使っていません。Apprise の 100 種類超の通知先を活かしたい場合は、別途自作ハブを挟むか、Apprise の Webhook を GoAlert の通知ターゲットに据える形になります。

GoAlert の標準範囲で足りる組織なら、自作よりずっと楽。

### その他の OSS

- **[Alerta](https://github.com/alerta/alerta)** — アラート集約 + ack / シェルブ機能、シフト管理は弱い
- **[OneUptime](https://oneuptime.com/)** — オンコール + インシデント + ステータスページの全部入り OSS
- **[Karma](https://github.com/prymitive/karma)** — Alertmanager 専用 UI、通知ではなく可視化

## 自作スタックの完成形

[前回記事](/blogs/posts/2026/05/grafana-oncall-irm-incident-response/)の Apprise + FastAPI 自作サービスに、シフト管理を組み込んだ完成形:

```text
[Grafana Alerting]
      ↓ webhook
[自作 Web サービス（FastAPI）]
      ↓
   ┌─ 当番判定: Google Calendar API or PyShift で「今の担当者は誰か」
   ├─ ack URL 発行
   └─ Apprise で通知（メール + Slack + Pushover）
        ↓
   N 分タイムアウトでエスカレーション
        ↓
[次の当番者]（同様にカレンダーから取得）
```

実装の最小増分:

```python
# ESCALATION_POLICY を時間帯別に動的取得
def get_escalation_policy_now():
    now = datetime.now()
    # Google Calendar から取得 or PyShift で計算
    primary = get_oncall_from_calendar(now)
    secondary = get_oncall_from_calendar(now + timedelta(hours=1))
    manager = "manager@example.com"
    return [
        f"mailto://{primary}",
        f"mailto://{secondary}",
        f"mailto://{manager}",
    ]
```

これで「カレンダーで誰でも編集できるシフト表 + Apprise の通知柔軟性 + 自作の細かい制御」を全部手に入れられます。

## 規模別の推奨構成（再整理）

| 規模 | 推奨構成 |
|---|---|
| **個人 / 1〜3 人体制** | 自作 FastAPI + Apprise + Google Calendar（シフト表として）|
| **5〜10 人、IT オンコール中心** | **GoAlert** + Twilio + Slack(自前運用が前提)|
| **5〜10 人、シフト規則が複雑** | OR-Tools でシフト生成 + 自作 + Apprise |
| **10 人超、24/7 + 音声通話必須** | Zenduty / OnPage / PagerDuty SaaS |
| **エンタープライズ + Grafana スタック** | Grafana Cloud IRM |

**Apprise はシフト管理しない**こと、**Grafana OnCall や GoAlert は Apprise ではなく独自の通知統合**で動いていることを理解した上で、自分の環境に合うレイヤーを選ぶのが正解です。

## まとめ

- **Apprise = 通知ハブ**。シフト管理機能はない
- シフト管理を**自作する**なら: PyShift（規則的）、OR-Tools（最適化）、Google Calendar / Outlook 共有カレンダー（実用最強）
- **既製品で済ませる**なら: GoAlert（OSS）、または有料 SaaS（Zenduty / IRM / PagerDuty）
- Microsoft 365 環境なら Outlook 共有カレンダー + Graph API で同じ思想がそのまま動く

OnCall OSS 後の OSS 自作の現実解として、**Apprise + 共有カレンダー + 自作 Web サービス**が最もシンプルかつ実用的、というのが筆者の結論です。

## 参考リンク

- [Apprise（GitHub）](https://github.com/caronc/apprise)
- [point85/PyShift（GitHub）](https://github.com/point85/PyShift)
- [PyWorkShift（PyPI）](https://pypi.org/project/PyWorkShift/)
- [PuLP（GitHub）](https://github.com/coin-or/pulp)
- [Google OR-Tools](https://developers.google.com/optimization)
- [GoAlert（target/goalert）](https://github.com/target/goalert)
- [Alerta](https://github.com/alerta/alerta)
- [OneUptime](https://oneuptime.com/)
- [Google Calendar API](https://developers.google.com/calendar)
