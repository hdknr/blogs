---
title: "Apprise + シフト管理ツールで OnCall 自作スタックを組む — PyShift・OR-Tools・GoAlert の役割と選び方"
date: 2026-05-08
lastmod: 2026-05-08
draft: false
categories: ["クラウド/インフラ"]
tags: ["Apprise", "シフト管理", "オンコール", "PyShift", "GoAlert", "OR-Tools", "PuLP", "Python", "OSS", "オブザーバビリティ"]
---

[前回の記事](/blogs/posts/2026/05/2026-05-08-grafana-oncall-irm-incident-response/)で「Apprise + 自作 Web サービスで OnCall 相当を組む」例を示しました。この記事ではよくある誤解を整理し、**シフト管理を含めた自作 OnCall スタックの現実的な選択肢**を深掘りします。

## まずは Apprise の正しい位置付けを確認

[Apprise](https://github.com/caronc/apprise) を「**シフト管理ができる Python ライブラリ**」と紹介する記事や AI の回答を見かけますが、これは誤りです。

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

実は**最も手軽で広く使われている**のはこの組み合わせ:

```python
from googleapiclient.discovery import build
import apprise

calendar = build("calendar", "v3", credentials=creds)
# 「今この時刻のオンコール担当者」をカレンダーから取得
events = calendar.events().list(
    calendarId="oncall@example.com",
    timeMin=now.isoformat(),
    timeMax=(now + timedelta(minutes=1)).isoformat(),
).execute()
oncall_email = events["items"][0]["summary"]  # 例: "tanaka@example.com"

apobj = apprise.Apprise()
apobj.add(f"mailto://{oncall_email}")
apobj.notify(title="Alert", body="...")
```

メリット:

- **シフト管理 UI が Google Calendar そのもの** — 全員が使い慣れている
- **休暇・代理対応**もカレンダーで普通に編集できる
- **モバイル / Web の確認**も Calendar アプリで完結
- API 連携が簡単

「ガチガチのシフトソフト」より、Google Calendar を共有してそこで運用する方が圧倒的に現場で機能するパターンは多いです。

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

> ⚠️ **注意**: 一部の解説記事や AI 回答で「GoAlert は Apprise 思想で連携」「Apprise を内蔵」と紹介されているのを見かけますが、**事実誤認**です。GoAlert は Twilio + SMTP + Slack を直接統合しており、Apprise は使っていません。Apprise の 100 種類超の通知先を活かしたい場合は、自作ハブが必要になります。

GoAlert の標準範囲で足りる組織なら、自作よりずっと楽。

### その他の OSS

- **[Alerta](https://github.com/alerta/alerta)** — アラート集約 + ack / シェルブ機能、シフト管理は弱い
- **[OneUptime](https://oneuptime.com/)** — オンコール + インシデント + ステータスページの全部入り OSS
- **[Karma](https://github.com/prymitive/karma)** — Alertmanager 専用 UI、通知ではなく可視化

## 自作スタックの完成形

[前回記事](/blogs/posts/2026/05/2026-05-08-grafana-oncall-irm-incident-response/)の Apprise + FastAPI 自作サービスに、シフト管理を組み込んだ完成形:

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

「**Apprise はシフト管理しない**」と「**Grafana OnCall や GoAlert も Apprise を使っていない**」を理解した上で、自分の環境に合うレイヤーを選ぶのが正解です。

## ファクトチェック注釈 — AI 回答の鵜呑みは危険

この記事は、AI（Gemini）の回答をきっかけに書きましたが、Gemini の主張のうち以下は**事実誤認**でした:

| Gemini の主張 | 実態 |
|---|---|
| 「Grafana Cloud IRM の通知機能の裏側で実際に Apprise が動いている」 | ❌ Grafana OnCall / IRM は **Django + Celery + 独自 Notification Managers**。Apprise は使っていない |
| 「GoAlert は Apprise 的思想で連携可能」 | ❌ GoAlert は **Twilio + SMTP + Slack の直接統合**。Apprise は使っていない |

PyShift・PuLP・OR-Tools の存在と GoAlert の存在は事実ですが、「Apprise との関係」はかなり盛られていました。**新興技術領域では、AI の回答に出典が示されていない場合、必ず一次資料（GitHub README / 公式ドキュメント）で確認**するのが鉄則です。

## まとめ

- **Apprise = 通知ハブ**。シフト管理機能はない
- シフト管理を**自作する**なら: PyShift（規則的）、OR-Tools（最適化）、Google Calendar（実用最強）
- **既製品で済ませる**なら: GoAlert（OSS）、または有料 SaaS（Zenduty / IRM / PagerDuty）
- 「Apprise + シフト管理」と書かれた記事や AI 回答を見たら、**実際は Apprise + 他のシフト管理ライブラリ / カレンダー**の組み合わせのことを指していると読み替える
- AI の回答は出典のない技術主張ほどハルシネーションが混じる。**GitHub の README で必ず一次確認**

OnCall OSS 後の OSS 自作の現実解として、**Apprise + Google Calendar + 自作 Web サービス**が最もシンプルかつ実用的、というのが筆者の結論です。

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
