---
title: "AWS DMS Serverless の OOM 障害と監視の盲点 — 検知漏れの根本原因と対策"
date: 2026-03-26
lastmod: 2026-03-26
draft: false
categories: ["クラウド/インフラ"]
tags: ["aws", "dms", "serverless", "eventbridge", "cloudwatch", "terraform", "監視"]
source_url: "https://gist.github.com/hdknr/43e385fbfa822e3ee1214a71564fd7a9"
---

AWS DMS Serverless Replication（CDC モード）が OOM（Out of Memory）で `failed` 状態になり、自動再起動の仕組みが検知できずに長期間停止していた問題について、根本原因と対策をまとめます。

## 構成

```
RDS (MySQL) → DMS Serverless (CDC) → S3 (Parquet)
```

- DMS Serverless Replication で全テーブルの CDC（Change Data Capture）を実行
- S3 に Parquet 形式で日付パーティション付きで出力
- EventBridge + Lambda で DMS 停止を検知し自動再起動する仕組みを構築済み

## 発生した事象

### 症状

- prod 環境の DMS Serverless Replication が `failed` 状態で停止
- エラーメッセージ: `Replication out of memory. Stop Reason FATAL_ERROR Error Level FATAL`
- CDC が完全に停止し、S3 へのデータ同期が止まっていた

### 発覚の経緯

手動確認で発見。自動再起動 Lambda の最終実行は約2ヶ月前で、それ以降は検知されていなかった。

## 根本原因

### 原因 1: EventBridge ルールのイベントパターンが不完全

自動再起動用の EventBridge ルールが `REPLICATION_TASK_STOPPED` のみを監視していた。

```json
{
  "source": ["aws.dms"],
  "detail-type": ["DMS Replication Task State Change"],
  "detail": {
    "eventType": ["REPLICATION_TASK_STOPPED"]
  }
}
```

DMS が OOM で異常終了した場合、イベントタイプは `REPLICATION_TASK_STOPPED` ではなく **`REPLICATION_TASK_FAILED`** として発火する。このため、EventBridge ルールがイベントをキャッチできず、Lambda による自動再起動も SNS 通知も行われなかった。

**教訓**: DMS の停止には「正常停止（stopped）」と「異常停止（failed）」の2種類がある。自動再起動を組む場合は両方を監視する必要がある。

### 原因 2: DMS Serverless の容量不足

`max_capacity_units = 2`（2 DCU）で全テーブル CDC を実行していたため、メモリが不足した。DMS Serverless はオートスケールするが、`max_capacity_units` が上限となるため、それを超えるワークロードでは OOM が発生する。

## 対策

### 1. EventBridge ルールの修正

`REPLICATION_TASK_FAILED` を追加し、異常停止も検知できるようにした。

```json
{
  "detail": {
    "eventType": ["REPLICATION_TASK_STOPPED", "REPLICATION_TASK_FAILED"]
  }
}
```

### 2. DMS 容量の引き上げ

```hcl
replication_config = {
  max_capacity_units = 4  # 2 → 4 に変更
  min_capacity_units = 2
}
```

### 3. 管理者へのメール通知（EventBridge → SNS）

DMS の停止/障害イベントを管理者にメールで通知する仕組みを追加。Lambda を経由せず、EventBridge → SNS トピック → メールの直接通知とした。

```
EventBridge Rule
  ├→ Lambda（自動再起動）
  └→ SNS Topic → Email（管理者通知）
```

Lambda を経由しない理由：

- EventBridge は1つのルールに複数ターゲットを設定可能
- SNS への通知に Lambda のコード変更や追加権限は不要
- シンプルな構成の方が障害点が少ない

### 4. CloudWatch Alarm による予兆検知

OOM が発生する前に異常を検知するため、DMS Serverless のメトリクスに CloudWatch Alarm を設定。

| アラーム | メトリクス | 閾値 | 目的 |
|---------|-----------|------|------|
| `*-dms-capacity-utilization` | `CapacityUtilization` | > 80%（15分間） | **OOM 予兆検知** |
| `*-dms-cdc-latency-source` | `CDCLatencySource` | > 300秒（15分間） | ソース遅延検知 |
| `*-dms-cdc-latency-target` | `CDCLatencyTarget` | > 300秒（15分間） | ターゲット遅延検知 |
| `*-dms-cpu-utilization` | `CPUUtilization` | > 90%（15分間） | CPU 高負荷検知 |

DMS Serverless の CloudWatch メトリクスでは `MemoryUsage` は提供されていないが、`CapacityUtilization` が全体的なリソース使用率を示すため、OOM の予兆検知に利用できる。

**注意点**: DMS Serverless の Dimension は `ReplicationConfigId` で、値の形式が `{account_id}:{replication_config_identifier}` となる（例: `726533500144:example-prod-dms`）。通常の DMS のように `ReplicationInstanceIdentifier` や `ReplicationTaskIdentifier` ではないため、Terraform で動的に構成する場合は `data.aws_caller_identity` でアカウント ID を取得する必要がある。

## Terraform 実装のポイント

### SNS トピックポリシー

EventBridge と CloudWatch Alarms の両方から SNS に publish するため、トピックポリシーで両サービスを許可する。

```hcl
data "aws_iam_policy_document" "sns_topic_policy" {
  # EventBridge からの publish
  statement {
    sid     = "AllowEventBridge"
    actions = ["sns:Publish"]
    principals {
      type        = "Service"
      identifiers = ["events.amazonaws.com"]
    }
    resources = [aws_sns_topic.dms_alert[0].arn]
    condition {
      test     = "ArnEquals"
      variable = "aws:SourceArn"
      values   = [aws_cloudwatch_event_rule.dms_stopped[0].arn]
    }
  }

  # CloudWatch Alarms からの publish
  statement {
    sid     = "AllowCloudWatchAlarms"
    actions = ["sns:Publish"]
    principals {
      type        = "Service"
      identifiers = ["cloudwatch.amazonaws.com"]
    }
    resources = [aws_sns_topic.dms_alert[0].arn]
    condition {
      test     = "StringEquals"
      variable = "aws:SourceAccount"
      values   = [data.aws_caller_identity.current[0].account_id]
    }
  }
}
```

### 条件付きリソース作成

通知機能はオプションのため、`notification.enabled` フラグで制御。

```hcl
variable "notification" {
  type = object({
    enabled = bool
    email   = string
  })
  default = {
    enabled = false
    email   = ""
  }
}
```

## 監視体制の全体像（対策後）

```
DMS Serverless Replication
  │
  ├─ [異常停止] EventBridge (STOPPED/FAILED)
  │    ├→ Lambda: 自動再起動（resume-processing）
  │    └→ SNS → Email: 管理者通知
  │
  └─ [予兆検知] CloudWatch Alarms
       ├─ CapacityUtilization > 80%  → SNS → Email
       ├─ CDCLatencySource > 300s    → SNS → Email
       ├─ CDCLatencyTarget > 300s    → SNS → Email
       └─ CPUUtilization > 90%      → SNS → Email
```

## まとめ

| 観点 | 対策前 | 対策後 |
|------|--------|--------|
| 異常停止の検知 | `stopped` のみ | `stopped` + `failed` |
| 容量 | 2 DCU（固定） | 2〜4 DCU（スケール可能） |
| 管理者通知 | なし | SNS メール通知 |
| 予兆検知 | なし | CloudWatch Alarm（4メトリクス） |

自動再起動の仕組みを作っても、**検知するイベントが不完全だと意味がない**。特に DMS のように `stopped` と `failed` でイベントタイプが異なるサービスでは、障害パターンを網羅的にカバーすることが重要。また、障害発生後の対応だけでなく、CloudWatch Alarm による予兆検知を組み合わせることで、OOM のような致命的な障害を未然に防ぐことができる。
