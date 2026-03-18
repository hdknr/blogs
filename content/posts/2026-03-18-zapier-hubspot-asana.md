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

標準の Code by Zapier ではライブラリの追加ができませんが、**Zapier Functions** を使えば、外部パッケージを含む本格的な Python コードを実行できます。

### Zapier Functions とは

Zapier Functions は、Zapier 内でサーバーレス Python 関数を作成・実行できるサービスです。概念的には **AWS Lambda に近い**ですが、Zapier のエコシステムに統合されている点が異なります。

| 観点 | Zapier Functions | AWS Lambda |
|---|---|---|
| 位置づけ | Zapier 内のサーバーレス関数 | AWS のサーバーレスコンピューティング |
| 言語 | Python | Python, Node.js, Go, Java 他多数 |
| 外部パッケージ | Pandas, NumPy, TensorFlow 等の主要パッケージ | pip/npm 等で自由にインストール可能 |
| 実行時間制限 | 5 分 | 最大 15 分 |
| トリガー | Zap のステップ、Agent、MCP サーバー | API Gateway, S3, SQS 等多数 |
| シークレット管理 | 組み込みの Secrets 機能 | AWS Secrets Manager / Parameter Store |
| デプロイ | Zapier UI 上で直接編集・保存 | ZIP アップロード、SAM、CDK 等 |
| 再利用性 | 複数の Zap / Agent から呼び出し可能 | API Gateway 等経由で任意に呼び出し可能 |
| インフラ管理 | 不要（フルマネージド） | 不要（フルマネージド） |
| 料金 | Zapier プランに含まれる（オープンベータ） | 実行回数・時間による従量課金 |

### Code by Zapier との違い

Zapier Functions は Code by Zapier の上位互換ではなく、**別のサービス**として提供されています。

| 観点 | Code by Zapier | Zapier Functions |
|---|---|---|
| 用途 | Zap 内のインラインスクリプト | 独立した再利用可能な関数 |
| 言語 | JavaScript (Node.js 18) / Python | Python |
| 外部パッケージ | 不可（標準ライブラリ + fetch/requests のみ） | Pandas, NumPy, TensorFlow 等が利用可能 |
| 実行時間 | 30 秒（プランにより延長あり） | 5 分 |
| メモリ | 256 MB | 非公開（より大きいと推定） |
| シークレット管理 | なし（Input Data に直接入力） | 組み込みの Secrets 機能で安全に管理 |
| 再利用 | Zap ごとにコードを記述 | 1 つの関数を複数の Zap / Agent から呼び出し可能 |
| 開発環境 | Zapier エディタ内のテキストエリア | 専用の開発環境（ファイル分割可能） |
| ステータス | GA（正式リリース） | オープンベータ |

### Zapier Functions のアーキテクチャ

Zapier Functions は以下の構成要素で動作します。

```
[Zap / Agent / MCP サーバー]
    ↓ Call a Function アクション
[Zapier Functions]
    ├── Start a Function トリガー（入力フィールド定義）
    ├── Python コード（外部パッケージ + Secrets 利用可能）
    └── Return from Function アクション（結果を呼び出し元に返却）
    ↓
[呼び出し元に結果を返す]
```

1. **Start a Function トリガー**: 入力パラメータを定義する。Zap から渡されるデータのスキーマを設定
2. **Python コード**: メインのロジックを記述。外部パッケージのインポートや Secrets の参照が可能
3. **Return from Function アクション**: 処理結果を呼び出し元（Zap / Agent）に返す。これにより呼び出し元は結果を待ってから次のステップに進める

### Secrets 管理

Zapier Functions には組み込みのシークレット管理機能があり、API キーやトークンを安全に保存できます。

```python
# Zapier Functions (Python)
# シークレットは環境変数のように参照可能
import os

hubspot_token = os.environ['HUBSPOT_API_KEY']  # Secrets に登録した値
```

Code by Zapier では Input Data にトークンを直接入力する必要がありましたが、Functions ではシークレットとして暗号化管理されるため、よりセキュアです。

### 利用例: Pandas でディールデータを集計

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

### どちらを使うべきか

- **Code by Zapier**: 簡単なデータ変換、フォーマット処理、単純な API コールなど、数行で済む処理
- **Zapier Functions**: 外部パッケージが必要な処理、複数の Zap で共有したいロジック、API キーを安全に管理したい場合、30 秒以上かかる処理
- **AWS Lambda**: Zapier のエコシステム外で動かしたい場合、Python 以外の言語を使いたい場合、15 分以上の処理、完全なカスタマイズが必要な場合

## 実践例: Asana タスクを集計して HubSpot Deal に Line Item を追加する

Asana のタスクデータを集計し、その結果を HubSpot の Deal に Line Item として追加するケースを考えます。Zapier の標準 HubSpot アクションには「Line Item を作成して Deal に紐付ける」アクションが直接用意されていないため、**Code by Zapier から HubSpot API を直接呼び出す**方法で実現します。

### Zap の全体構成

```
[トリガー] Asana: タスク完了
    ↓
[アクション] Code by Zapier: Asana データ集計 + HubSpot API 呼び出し
```

### 前提条件

- HubSpot の Private App を作成し、以下のスコープを付与しておく:
  - `crm.objects.line_items.write`（Line Item の作成）
  - `crm.objects.line_items.read`（Line Item の読み取り）
  - `crm.objects.deals.read`（Deal の読み取り）
- Private App のアクセストークンを Zapier の Input Data に設定する

### Code by Zapier の実装

```javascript
// Code by Zapier (JavaScript)
// Input Data:
//   hubspotToken - HubSpot Private App のアクセストークン
//   dealId       - 対象の HubSpot Deal ID
//   taskName     - Asana タスク名（Line Item の名前に使用）
//   hours        - Asana タスクの作業時間（カスタムフィールド等から取得）
//   hourlyRate   - 時間単価

const dealId = inputData.dealId;
const taskName = inputData.taskName;
const hours = Number(inputData.hours);
const hourlyRate = Number(inputData.hourlyRate || 5000);
const amount = hours * hourlyRate;

// HubSpot API で Line Item を作成し、Deal に紐付ける
const response = await fetch(
  'https://api.hubapi.com/crm/v3/objects/line_items',
  {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${inputData.hubspotToken}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      properties: {
        name: taskName,
        price: amount,
        quantity: 1,
        description: `Asana タスク「${taskName}」: ${hours}時間 × ¥${hourlyRate.toLocaleString()}`
      },
      associations: [
        {
          to: { id: dealId },
          types: [
            {
              associationCategory: 'HUBSPOT_DEFINED',
              associationTypeId: 20
            }
          ]
        }
      ]
    })
  }
);

const result = await response.json();

if (!response.ok) {
  throw new Error(`HubSpot API error: ${JSON.stringify(result)}`);
}

output = {
  lineItemId: result.id,
  lineItemName: taskName,
  amount: amount,
  status: 'created'
};
```

### 既存の Product を使う場合

HubSpot に登録済みの Product（商品）から Line Item を作成する場合は、`hs_product_id` プロパティを指定します。

```javascript
// 既存の Product ID を指定して Line Item を作成
body: JSON.stringify({
  properties: {
    hs_product_id: inputData.productId,  // HubSpot の Product ID
    quantity: Number(inputData.hours),
    // price は Product のデフォルト価格が使われる（上書きも可能）
  },
  associations: [
    {
      to: { id: dealId },
      types: [
        { associationCategory: 'HUBSPOT_DEFINED', associationTypeId: 20 }
      ]
    }
  ]
})
```

### 複数タスクを一括で Line Item にする場合

Asana の複数タスクをまとめて処理する場合、Zapier の **Looping by Zapier** と組み合わせるか、Code ステップ内で一括処理します。

```javascript
// Code by Zapier (JavaScript)
// Input Data:
//   tasks - JSON 文字列（Asana タスクの配列）
//   hubspotToken, dealId

const tasks = JSON.parse(inputData.tasks);
const results = [];

for (const task of tasks) {
  const res = await fetch(
    'https://api.hubapi.com/crm/v3/objects/line_items',
    {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${inputData.hubspotToken}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        properties: {
          name: task.name,
          price: task.amount,
          quantity: 1
        },
        associations: [
          {
            to: { id: inputData.dealId },
            types: [
              { associationCategory: 'HUBSPOT_DEFINED', associationTypeId: 20 }
            ]
          }
        ]
      })
    }
  );

  const data = await res.json();
  results.push({ id: data.id, name: task.name, status: res.ok ? 'ok' : 'error' });
}

output = {
  created: results.filter(r => r.status === 'ok').length,
  errors: results.filter(r => r.status === 'error').length,
  details: JSON.stringify(results)
};
```

### 注意点

- **API レート制限**: HubSpot API は Private App の場合、秒間 100 リクエストまで。大量のタスクを処理する場合は注意が必要
- **トークン管理**: Private App のアクセストークンは Zapier の Input Data に直接入力するため、チーム内での共有・管理方法を検討すること
- **代替手段**: API を直接叩く代わりに **Webhooks by Zapier**（Custom Request アクション）でも同様のことが可能。集計ロジックが不要な場合はこちらの方がシンプル

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
- Code by Zapier から HubSpot API を直接呼び出すことで、Line Item の作成・Deal への紐付けも自動化できる
- より高度な集計には Zapier Functions（Pandas 等のライブラリ対応）が利用可能
- シンプルな同期であれば HubSpot のネイティブ連携も選択肢になる
