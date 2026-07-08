---
title: "Claude Platform on AWS セットアップと API 呼び出し実録 — API key/SigV4 認証と inference_geo の挙動"
date: 2026-05-22
lastmod: 2026-05-22
slug: "claude-platform-on-aws-ga-setup"
draft: false
source_url: "https://github.com/hdknr/blogs/issues/1#issuecomment-4514469915"
categories: ["AI/LLM"]
tags: ["claude", "aws", "anthropic", "bedrock", "messages-api", "sigv4"]
---

2026年5月11日に一般提供（GA）となった **Claude Platform on AWS** のセットアップ手順・API 呼び出し・`inference_geo` の挙動を実機で検証した記録です。

概念的な概要や Amazon Bedrock との比較については[こちらの記事](/blogs/posts/2026/05/claude-platform-on-aws-ga/)をご参照ください。本記事では hands-on のセットアップと API 呼び出しに絞って解説します。

参考: [Claude Platform on AWS がGA。セットアップとAPI呼び出しを試してみた | DevelopersIO](https://dev.classmethod.jp/articles/claude-platform-on-aws-ga-setup/)

## Claude Platform on AWS とは（概要）

AWS アカウントを通じて Anthropic のネイティブ Claude Platform に直接アクセスできるサービスです。Amazon Bedrock とは別サービスで、**推論は Anthropic のインフラ上で実行**されます。

| 項目 | Claude Platform on AWS | Claude on Bedrock |
|------|----------------------|-------------------|
| 推論の実行 | Anthropic | AWS |
| 利用可能な機能 | 全ネイティブ機能（Skills, Code Execution, Files API, MCP 等） | Bedrock が提供する機能（Guardrails, KB, Converse API 等） |
| 新機能の利用 | Anthropic と同日 | AWS が対応したとき |
| 認証 | AWS IAM | AWS IAM |
| 監査ログ | CloudTrail | CloudTrail |
| 課金 | AWS 請求に統合 | AWS 請求に統合 |
| 向いているケース | 最新機能・エージェント・スキル | データ所在地優先・FedRAMP/HIPAA 等のコンプライアンス対応・AWS 単独データ処理要件 |

## セットアップ手順

### 1. AWS コンソールで開始

AWS マネジメントコンソールで「Claude Platform on AWS」を開き「Get Started」をクリックします。確認画面で「Continue」を選択します。

メールアドレスを入力して「Start」をクリックすると、Anthropic から "Set up your Claude organization" という件名のメールが届きます。メール内のリンクをクリックし、組織情報を入力して「Complete setup」を実行します。

### 2. ワークスペースの作成

セットアップ完了後、「Create Workspace」からワークスペースを作成します。**ワークスペース ID（`wrkspc_xxxxx` 形式）は後で必要になるので控えておきます。** ワークスペースは単一の AWS リージョンに紐付けられます。

### 3. Claude Console にサインイン

Admin ロールを選択してサインインすると Claude Console が開きます。Console では以下の操作が行えます。

- エージェントスキルの登録・管理
- エージェントの作成・管理
- トークン使用量とコストのモニタリング
- レートリミット確認
- データレジデンシー管理

### 4. API キーの生成

ダッシュボードから API キーを生成します（有効期限を設定可能）。生成された API キーは一度しか表示されないため、必ず保存してください。

AWS コンソールの「Claude Platform on AWS」→「API Keys」でも API キーの作成・管理ができます。

## API 呼び出し

### 環境変数の設定

```bash
export AWS_REGION="us-east-1"
export ANTHROPIC_AWS_WORKSPACE_ID="wrkspc_xxxxx"
export ANTHROPIC_API_KEY="xxxxx"
```

ベース URL は `https://aws-external-anthropic.{リージョン}.api.aws` の形式です。

### API key 認証での呼び出し

Anthropic Messages API と同じエンドポイント（`/v1/messages`）を使用します。**`anthropic-workspace-id` ヘッダーが必須**です。

```bash
curl "https://aws-external-anthropic.us-east-1.api.aws/v1/messages" \
  -H "x-api-key: $ANTHROPIC_API_KEY" \
  -H "content-type: application/json" \
  -H "anthropic-version: 2023-06-01" \
  -H "anthropic-workspace-id: $ANTHROPIC_AWS_WORKSPACE_ID" \
  -d '{
    "model": "claude-sonnet-4-6",
    "max_tokens": 1024,
    "messages": [
      {"role": "user", "content": "What is Amazon Bedrock?"}
    ]
  }'
```

### SigV4 認証での呼び出し

API キーの代わりに AWS SigV4 認証も使用できます。curl では `--aws-sigv4` フラグで SigV4 署名を行い、`--user` で ACCESS_KEY_ID と SECRET_ACCESS_KEY を渡します。

```bash
curl "https://aws-external-anthropic.us-east-1.api.aws/v1/messages" \
  --aws-sigv4 "aws:amz:us-east-1:aws-external-anthropic" \
  --user "$AWS_ACCESS_KEY_ID:$AWS_SECRET_ACCESS_KEY" \
  -H "x-amz-security-token: $AWS_SESSION_TOKEN" \
  -H "content-type: application/json" \
  -H "anthropic-version: 2023-06-01" \
  -H "anthropic-workspace-id: $ANTHROPIC_AWS_WORKSPACE_ID" \
  -d '{
    "model": "claude-sonnet-4-6",
    "max_tokens": 1024,
    "messages": [
      {"role": "user", "content": "What is Amazon Bedrock?"}
    ]
  }'
```

API キー認証と SigV4 認証は排他的です。`x-api-key` ヘッダーがある場合は API キー認証として処理されます。

### レスポンスの確認

リクエストが成功すると、通常の Anthropic Messages API レスポンスに加えて、`usage` フィールドの中に `inference_geo` が含まれます。

```json
{
  "model": "claude-sonnet-4-6",
  "id": "msg_xxxxx",
  "type": "message",
  "role": "assistant",
  "content": [...],
  "stop_reason": "end_turn",
  "usage": {
    "input_tokens": 18,
    "cache_creation_input_tokens": 0,
    "cache_read_input_tokens": 0,
    "output_tokens": 527,
    "service_tier": "standard",
    "inference_geo": "global"
  }
}
```

**`inference_geo`** フィールドは推論が実行された地理的なロケーションを示します。`"global"` はグローバルの推論リソースが使われたことを意味します。データ所在地を特定リージョンに固定したい場合は、ワークスペース設定またはリクエストごとに `inference_geo` パラメータで制御できます。

## Anthropic SDK での利用

Claude Platform on AWS 専用の SDK クライアントは **`AnthropicAWS`** です（Amazon Bedrock 用の `AnthropicBedrock` とは別クラスです）。

```python
from anthropic import AnthropicAWS

client = AnthropicAWS()

message = client.messages.create(
    model="claude-sonnet-4-6",
    max_tokens=1024,
    messages=[
        {"role": "user", "content": "What is Amazon Bedrock?"}
    ]
)
print(message.content)
```

SDK が使う環境変数は `ANTHROPIC_AWS_WORKSPACE_ID`（API キー認証なら `ANTHROPIC_API_KEY` も必要）と `AWS_REGION` です。

## まとめ

Claude Platform on AWS のセットアップは非常にシンプルで、AWS コンソールからの数ステップで完了します。API 呼び出しは Anthropic Messages API と同一のインターフェース（`/v1/messages`）で、`anthropic-workspace-id` ヘッダーを追加するだけです。

使い分けの判断軸は**データ所在地・コンプライアンス要件**です。FedRAMP High、HIPAA 対応など AWS のセキュリティ境界内で推論を行う必要がある場合は Bedrock を選択します。最新の Anthropic 機能（Skills、Files API、MCP 等）を即日使いたい場合は Claude Platform on AWS が適しています。
