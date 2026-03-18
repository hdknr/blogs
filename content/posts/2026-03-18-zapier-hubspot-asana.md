---
title: "Zapier を使った HubSpot と Asana の連携：集計ロジックも追加する方法"
date: 2026-03-18
lastmod: 2026-03-18
draft: false
source_url: "https://github.com/hdknr/blogs/issues/71#issuecomment-4079051187"
categories: ["ビジネス/キャリア"]
tags: ["Zapier", "HubSpot", "Asana", "自動化", "ノーコード"]
---

Zapier を使って HubSpot と Asana を連携させる方法と、Code by Zapier で集計ロジックを追加するテクニックを紹介します。

## HubSpot × Asana 連携の基本

HubSpot（CRM・マーケティング）と Asana（プロジェクト管理）を連携させることで、営業パイプラインとタスク管理を自動化できます。Zapier を使えばノーコードで連携を構築できます。

### よくある連携パターン

| トリガー（HubSpot） | アクション（Asana） | ユースケース |
|---|---|---|
| 新規ディールが作成された | タスクを作成 | 商談ごとにプロジェクトタスクを自動生成 |
| ディールのステージが変わった | タスクを更新 | 進捗をリアルタイムに反映 |
| フォーム送信があった | タスクを作成 | 問い合わせ対応タスクを自動起票 |
| 新規チケットが作成された | タスクを作成 | サポート対応を Asana で管理 |

逆方向の連携もあります。

| トリガー（Asana） | アクション（HubSpot） | ユースケース |
|---|---|---|
| タスクが完了した | コンタクトを更新 | 納品完了を CRM に反映 |
| タスクにコメントが追加された | エンゲージメントを作成 | 活動履歴を CRM に記録 |

## Zapier での連携セットアップ

### 1. Zap の作成

Zapier にログインし、「Create Zap」から新しい Zap を作成します。

**トリガーの設定（例: HubSpot → Asana）:**

1. トリガーアプリに **HubSpot** を選択
2. トリガーイベントに「New Deal」を選択
3. HubSpot アカウントを接続
4. テストを実行して動作確認

**アクションの設定:**

1. アクションアプリに **Asana** を選択
2. アクションイベントに「Create Task」を選択
3. Asana アカウントを接続
4. フィールドをマッピング:
   - **Task Name** → HubSpot のディール名
   - **Project** → 対象の Asana プロジェクト
   - **Notes** → ディールの詳細情報
   - **Due Date** → クローズ予定日

### 2. フィールドマッピングのコツ

HubSpot のプロパティを Asana のフィールドに適切にマッピングすることが重要です。

```
HubSpot Deal Name     → Asana Task Name
HubSpot Deal Amount   → Asana Custom Field (金額)
HubSpot Deal Stage    → Asana Section
HubSpot Close Date    → Asana Due Date
HubSpot Deal Owner    → Asana Assignee
```

## 集計ロジックの追加：Code by Zapier

標準のトリガー・アクションだけでは実現できない集計や変換が必要な場合、**Code by Zapier** ステップを間に挟むことで対応できます。

### Code by Zapier とは

Zap のワークフロー内で JavaScript（Node.js 18）または Python のコードを実行できるステップです。

- **JavaScript**: 標準ライブラリ + `fetch` パッケージが利用可能
- **Python**: 標準ライブラリ + `requests` + `BeautifulSoup` が利用可能
- 外部パッケージの追加インストールは不可

### 例1: ディール金額の集計

HubSpot から取得した複数のディール金額を集計して、Asana タスクの説明に含める例です。

```javascript
// Code by Zapier (JavaScript)
// Input: dealAmounts (カンマ区切りの金額文字列)
const amounts = inputData.dealAmounts.split(',').map(Number);

const total = amounts.reduce((sum, val) => sum + val, 0);
const average = total / amounts.length;
const max = Math.max(...amounts);
const min = Math.min(...amounts);

output = {
  total: total,
  average: Math.round(average),
  count: amounts.length,
  max: max,
  min: min,
  summary: `合計: ¥${total.toLocaleString()} / 平均: ¥${Math.round(average).toLocaleString()} / 件数: ${amounts.length}`
};
```

### 例2: ステージごとのタスク振り分けロジック

ディールのステージに応じて、Asana の異なるプロジェクトやセクションにタスクを作成する分岐ロジックです。

```javascript
// Code by Zapier (JavaScript)
// Input: dealStage, dealAmount
const stage = inputData.dealStage;
const amount = Number(inputData.dealAmount);

let project = '';
let section = '';
let priority = 'medium';

if (stage === 'closedwon') {
  project = 'オンボーディング';
  section = amount >= 1000000 ? 'エンタープライズ' : 'スタンダード';
  priority = amount >= 1000000 ? 'high' : 'medium';
} else if (stage === 'contractsent') {
  project = '契約管理';
  section = '契約書送付済み';
} else {
  project = '商談進行中';
  section = stage;
}

output = {
  project: project,
  section: section,
  priority: priority
};
```

### 例3: Python で日付ベースの集計

```python
# Code by Zapier (Python)
# Input: created_dates (カンマ区切りの日付文字列)
from datetime import datetime
from collections import Counter

dates = input_data['created_dates'].split(',')
months = [datetime.strptime(d.strip(), '%Y-%m-%d').strftime('%Y-%m') for d in dates]
monthly_counts = Counter(months)

summary_lines = [f"{month}: {count}件" for month, count in sorted(monthly_counts.items())]

output = {
    'monthly_summary': '\n'.join(summary_lines),
    'total': len(dates),
    'latest_month': max(monthly_counts, key=monthly_counts.get)
}
```

## より高度な集計: Zapier Functions

標準の Code by Zapier ではライブラリの追加ができませんが、**Zapier Functions**（Python 環境）を使えば、Pandas や NumPy などのパッケージも利用できます。

```python
# Zapier Functions (Python)
import pandas as pd

# HubSpot から取得したディールデータ
deals = pd.DataFrame(input_data['deals'])

# ステージ別の集計
stage_summary = deals.groupby('stage').agg(
    count=('amount', 'count'),
    total=('amount', 'sum'),
    average=('amount', 'mean')
).round(0)

output = {
    'report': stage_summary.to_string(),
    'total_pipeline': int(deals['amount'].sum())
}
```

## ネイティブ連携との使い分け

HubSpot には Asana とのネイティブ連携（公式インテグレーション）も用意されています。

| 観点 | ネイティブ連携 | Zapier 連携 |
|---|---|---|
| セットアップ | HubSpot の設定画面から直接接続 | Zapier アカウントが必要 |
| カスタマイズ性 | 限定的 | 高い（Code ステップで自由に拡張） |
| 集計・変換 | 不可 | Code by Zapier で対応可能 |
| コスト | 無料 | Zapier のプランに依存 |
| 信頼性 | 高い（直接接続） | Zapier の稼働状況に依存 |

集計ロジックやカスタム変換が必要な場合は Zapier、シンプルな双方向同期だけであればネイティブ連携がおすすめです。

## まとめ

- Zapier を使えば HubSpot と Asana の連携をノーコードで構築できる
- Code by Zapier（JavaScript / Python）で集計・変換ロジックを追加できる
- より高度な集計には Zapier Functions（Pandas 等のライブラリ対応）が利用可能
- シンプルな同期であれば HubSpot のネイティブ連携も選択肢になる
