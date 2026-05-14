---
title: "Claude Platform on AWS が GA — Amazon Bedrock との違いと day-one でフル機能を使える理由"
date: 2026-05-13
lastmod: 2026-05-13
draft: false
description: "Anthropic が 2026 年 5 月 11 日に GA した Claude Platform on AWS を Amazon Bedrock と比較。day-one で使える Managed Agents・Skills・MCP connector、既存 AWS コミットメントの消化など、AWS 顧客が選び分けるための判断材料をまとめる。"
summary: "Claude Platform on AWS の GA を Amazon Bedrock との比較で整理。ネイティブ API フル機能と AWS IAM・請求の両立がもたらす意味を解説。"
source_url: "https://github.com/hdknr/blogs/issues/1#issuecomment-4439456381"
categories: ["AI/LLM"]
tags: ["Claude", "AWS", "Anthropic", "Amazon Bedrock", "Managed Agents", "MCP", "Skills"]
---

Anthropic は 2026 年 5 月 11 日、**Claude Platform on AWS** の一般提供（GA）を開始した。Anthropic 公式 API のフル機能を、AWS の IAM 認証・CloudTrail 監査・単一請求書で利用できる新しいアクセス経路である。すでに展開している Amazon Bedrock 経由の Claude とは別サービスとして位置付けられている。

## 何が新しいのか

これまで AWS 顧客が Claude を使う公式の選択肢は **Amazon Bedrock** 経由が中心だった。Bedrock は AWS がデータ処理事業者となり、AWS バウンダリ内で完結する一方で、Anthropic ネイティブ API の最新機能やベータ機能は遅れて追随する形になっていた。

Claude Platform on AWS は、**ネイティブ Claude API と完全に同じ機能セット**を AWS の認証・課金レイヤーから直接呼び出せるようにしたものだ。Anthropic 公式ブログによれば、新機能やベータは **ネイティブ API と同日リリース（day-one access）** される。

> The Claude Platform on AWS brings the full set of Claude API features to AWS customers for the first time, with all new features and betas shipping the same day they go live on the native Claude API.
>
> （訳: Claude Platform on AWS は AWS 顧客に初めて Claude API のフル機能セットを提供する。新機能とベータはネイティブ Claude API でローンチされるのと同日にリリースされる。）
> （出典: [claude.com/blog/claude-platform-on-aws](https://claude.com/blog/claude-platform-on-aws)）

## Claude Platform on AWS と Amazon Bedrock の違い

両者は競合ではなく、**運営主体とデータ処理境界が異なる別オプション**として並列に提供される。

| 観点 | Claude Platform on AWS | Claude on Amazon Bedrock |
| --- | --- | --- |
| 運営主体 | Anthropic | AWS |
| データ処理 | AWS の信頼境界（バウンダリ）外 | AWS の信頼境界内 |
| ネイティブ API 機能 | フル（day-one） | サブセット |
| 認証 | AWS IAM | AWS IAM |
| 請求 | AWS 単一請求書（既存コミットメント消化可） | AWS 単一請求書 |
| 向いている用途 | 最新機能を最速で使いたい場合 | AWS 内でのデータ処理が必須の場合 |

つまり、**「データ処理を AWS 内に閉じ込める要件があるか」** が選び分けの軸になる。要件がなければ Claude Platform on AWS のほうが機能面で有利、要件があれば引き続き Bedrock という整理だ。関連: [Claude Managed Agents の公式ローンチ](/blogs/posts/2026/04/2026-04-10-claude-managed-agents/) も Bedrock ではなくこのプラットフォームの中核機能として整理されている。

## day-one アクセスで使える Claude ネイティブ API 機能一覧

公式ブログに列挙されている主な機能は次のとおり。多くが現時点でも `(beta)` ラベルが付くが、これらが AWS 経由でもネイティブ API と同タイミングで使えるのが今回の核心だ。

- **Claude Managed Agents (beta)** — エージェントをスケールで構築・展開
- **Advisor strategy (beta)** — アドバイザーモデルに諮問して知能をブースト
- **Web search / Web fetch** — Web から最新情報を取得
- **Code execution** — API 呼び出し内で Python を実行、可視化やデータ分析
- **Files API (beta)** — ドキュメントをアップロードして会話横断で参照
- **Skills (beta)** — ベストプラクティスを教え込み、一貫した出力を実現
- **MCP connector (beta)** — クライアントコードを書かずに任意のリモート MCP サーバーへ接続
- **Prompt caching** — 繰り返しコンテキストでコスト・レイテンシ削減
- **Citations** — ソース文書による根拠付き応答
- **Batch processing** — 大量・非同期ワークロード向けバッチ処理

加えて、Anthropic の開発者向け Web コンソールである **Claude Console**（プロンプト改善ツール、プロンプトジェネレーター、評価ツールを含む）にもアクセスできる。

利用可能なモデルは **Claude Opus 4.7 / Sonnet 4.6 / Haiku 4.5** で、Anthropic は新モデルもローンチに合わせて順次提供する予定としている。

## 既存の AWS 運用に馴染む

Claude Platform on AWS の設計は、AWS をすでに使っている組織にとって導入の摩擦を最小化することを狙っている。

- **認証**: 既存の AWS IAM クレデンシャル・ポリシーをそのまま使う。新しい認証基盤を別途構築する必要がない
- **監査ログ**: CloudTrail に記録され、既存のセキュリティ運用フローに統合できる
- **請求**: AWS の単一請求書にまとまり、**既存の AWS コミットメント（EDP: Enterprise Discount Program など）の消化に充当**される。別途 Anthropic に支払いを起こす必要がない
- **リージョン**: 多くの AWS 商用リージョンで提供、グローバルおよび米国（U.S.）の推論リージョン（inference geography）をサポート

特に「既存の AWS コミットメントを消化（retire）できる」点は、すでに大型コミットメントを抱える企業にとって価値が大きい。Anthropic への直接契約だと別予算ラインを立てる必要があったところを、AWS の枠内に収められる。

## 顧客の声から見える導入動機

公式ブログには 3 社のコメントが掲載されている。三者三様に「ネイティブ API と同等の最新機能を、AWS の運用モデルを崩さずに使える」点を強調している。

- **Jonathan Echavarria 氏（Principal Research Scientist）**: Claude へのアクセス簡素化、Claude Code エンジニアの体験向上、既存のクラウド運用モデルを維持したままサイバーセキュリティ・エンジニアリングのワークフローへ AI を統合
- **Tomas Oliva 氏（OpenRouter / AI Platform Engineer）**: ネイティブ Claude API の最新機能への直接アクセス、他の AWS サービスと同じ IAM クレデンシャルでアクセス制御
- **Avinash Vishwakarma 氏（Chief Architect）**: 「canonical Anthropic API + AWS をアクセスレイヤーとする構成」で機能パリティ（feature parity）と新モデル機能への day-one アクセスを実現

## 導入時の注意点

Anthropic は導入前に押さえておくべき点も明示している。

> If you have an existing Bedrock private offer, please contact your Anthropic or AWS account executive before getting started with Claude Platform on AWS to ensure your discounts are applied correctly. Discounts cannot be applied retroactively to usage incurred before a Claude Platform private offer is accepted.
>
> （訳: 既存の Bedrock プライベートオファーをお持ちの場合は、Claude Platform on AWS を利用開始する前に Anthropic または AWS の営業担当に連絡し、割引が正しく適用されるようにしてください。Claude Platform プライベートオファーを受諾する前に発生した利用分に対して、割引をさかのぼって適用することはできません。）

つまり、**既存の Bedrock プライベートオファーがある場合は、先に営業担当に連絡して割引を Claude Platform on AWS 側にも適用する手続きを取る必要がある**。割引はさかのぼって適用されないため、契約調整は利用開始前に済ませる必要がある。

## Claude Platform on AWS と Bedrock どちらを選ぶ？判断フロー

新規に AWS 上で Claude を採用する場合、選択は次の問いに集約される。

1. **データ処理を AWS の信頼境界内に閉じ込める法令・契約上の要件があるか？**
   - **YES** → Claude on Amazon Bedrock
   - **NO** → Claude Platform on AWS
2. **ネイティブ API のベータや最新機能を day-one で使いたいか？**
   - **YES** → Claude Platform on AWS
   - **NO（安定版のみで十分）** → どちらでも可
3. **既存の AWS コミットメントを Claude 利用で消化したいか？**
   - **YES** → どちらも AWS 請求にまとまるので可。割引の適用範囲は営業確認
   - **NO** → 通常請求でどちらも可

特に [Claude Managed Agents](/blogs/posts/2026/04/2026-04-10-claude-managed-agents/) や Skills、MCP connector、Code execution など、Claude Platform の魅力的なベータ機能を試したいエンジニアリングチームには、Claude Platform on AWS が現実的な唯一解になる。

## 開発者にとっての意味

Anthropic 視点では、これはいわゆる **「Bedrock のサブセット問題」を解消する戦略的な動き**でもある。Claude のフロンティア機能（Managed Agents、Skills、MCP connector など）はベータ段階から出荷頻度が高く、Bedrock 経由だとどうしてもラグが出ていた。

AWS 顧客にとっては「ネイティブ API を直接叩く（= AWS 外の請求・認証を別途運用する）」か「Bedrock で待つ」かの二択だった。今回そこに、**「AWS の運用そのままでネイティブ API のフル機能」** という第三の選択肢が加わった意味は大きい。

エージェント開発、特に Claude Managed Agents や Skills を中核に据えた本番システムを AWS で動かす場合、これからのデフォルトは Claude Platform on AWS になるだろう。

## セットアップとデスクトップ PC からの利用方法

ここからは、実際に Claude Platform on AWS を有効化し、デスクトップ PC から SDK や Claude Code で叩くまでの手順を詳しく解説する。出典は AWS 公式ユーザーガイド、`platform.claude.com` の API ドキュメント、Claude Code ドキュメントの 3 点。

### 前提条件

| 必須 | 内容 |
| --- | --- |
| AWS アカウント | サインアップ権限のある管理者アカウント |
| AWS CLI | バージョン 2 系をローカルにインストール |
| IAM 権限 | サインアップ・ロール引き受け・IAM ポリシー作成権限 |
| エンドポイント | `https://aws-external-anthropic.{region}.api.aws`（自動算出） |

注意: AWS Console からサインアップすると **AWS アカウント専用の新しい Anthropic 組織** がプロビジョニングされる。既存の Anthropic 直契約組織や Claude Console の API キーは引き継がれない。

### Step 1: AWS Console でサインアップ

1. AWS Console にログインし、サービス一覧から **Claude Platform on AWS** を開く
2. **Sign up** をクリック
3. 利用規約（Anthropic EULA、AWS Privacy Notice、AWS Customer Agreement）に同意して **Continue**
4. 「Sign-up in progress」バナーが出るので**そのまま待機**（数分かかる）。AWS Marketplace サブスクリプションが自動処理される
5. 既存の Bedrock プライベートオファーがある場合は、**サインアップ前**に営業担当へ連絡する（割引はさかのぼり不可）

### Step 2: Anthropic 組織を作成

サインアップ完了後、`platform.claude.com/partner-signup` にリダイレクトされる。

1. 組織オーナーのメールアドレスを入力 → **Get started**
2. 招待メールのリンクを開く（「Signed in as a different account」が出たら **Log out and continue**）
3. 組織情報（組織名、エンティティタイプ、国、利用目的）を入力 → **Complete setup**

完了すると AWS Console 側に **Home / API keys / Quickstart / Workspaces** のナビゲーションが表示される。

### Step 3: Workspace ID をメモする

- デフォルト Workspace が自動作成される
- **Workspaces** ページから `wrkspc_01AbCdEf23GhIj` 形式の ID をコピー
- Workspace は **AWS リージョンに紐づく**（`us-west-2` で作った Workspace は `us-west-2` のエンドポイントからしか使えない）

### Step 4: Claude Console にサインイン

1. IAM ロールに `aws-external-anthropic:AssumeConsole` 権限を付与
2. AWS Console の **Claude Platform on AWS** ページから **Open Claude Console**
3. AWS が JWT を発行し `platform.claude.com` にリダイレクト
4. 初回は職場メールを入力 → ユーザーが自動プロビジョニング

サイドバー左下に **Account managed by AWS** インジケーターが表示されれば成功。

### API 呼び出し前の必須準備（最重要）

**Outbound Web Identity Federation の有効化** は AWS アカウントごとに 1 回必要。これを忘れると全リクエストが失敗する（最も多いセットアップエラー）。

```bash
aws iam enable-outbound-web-identity-federation
```

すでに有効なら `[ERROR] (FeatureEnabled) ... already enabled` が返る。確認は次のコマンド。

```bash
aws iam get-outbound-web-identity-federation-info
```

環境変数を設定する。

```bash
export ANTHROPIC_AWS_WORKSPACE_ID='wrkspc_01AbCdEf23GhIj'
export AWS_REGION='us-west-2'   # Workspace の AWS リージョン
```

### 認証方式

Claude Platform on AWS は 2 種類の認証をサポートする。

**A. AWS IAM (SigV4) — エンタープライズ向けの推奨方式**

標準の AWS クレデンシャルチェーンが使える。

| ソース | 用途 |
| --- | --- |
| `AWS_ACCESS_KEY_ID` / `AWS_SECRET_ACCESS_KEY` / `AWS_SESSION_TOKEN` | 環境変数 |
| `~/.aws/credentials` / `~/.aws/config` | 共有プロファイル（SSO・`credential_process` 含む） |
| Web Identity (`AWS_WEB_IDENTITY_TOKEN_FILE`) | IRSA、GitHub Actions |
| ECS / EC2 IMDS | コンテナ・インスタンス |

動作確認:

```bash
aws sts get-caller-identity
```

SSO ログイン例:

```bash
aws sso login --profile my-profile
export AWS_PROFILE=my-profile
```

**B. API キー — 開発・スクリプト向け**

1. AWS Console → **Claude Platform on AWS → API keys → Generate a key** でキー生成
2. IAM プリンシパルに `aws-external-anthropic:CallWithBearerToken` アクションを付与
3. 環境変数にセット:

```bash
export ANTHROPIC_AWS_API_KEY='sk-ant-xxxxx'
```

注意: 通常の Claude Console で発行した API キーは Claude Platform on AWS では使えない。必ず AWS Console の API keys から発行する。

### デスクトップ PC から SDK で使う

**Python SDK の例**:

```bash
pip install anthropic
```

```python
from anthropic import AnthropicAWS

client = AnthropicAWS()  # 環境変数から自動読み込み

message = client.messages.create(
    model="claude-sonnet-4-6",
    max_tokens=1024,
    messages=[{"role": "user", "content": "Hello!"}],
)
print(message)
```

**TypeScript SDK の例**:

```bash
npm install @anthropic-ai/sdk
```

```typescript
import { AnthropicAWS } from "@anthropic-ai/sdk";

const client = new AnthropicAWS();
const message = await client.messages.create({
  model: "claude-sonnet-4-6",
  max_tokens: 1024,
  messages: [{ role: "user", content: "Hello!" }],
});
console.log(message);
```

**cURL で生 API を叩く**:

```bash
curl https://aws-external-anthropic.us-west-2.api.aws/v1/messages \
  --aws-sigv4 "aws:amz:us-west-2:aws-external-anthropic" \
  --user "$AWS_ACCESS_KEY_ID:$AWS_SECRET_ACCESS_KEY" \
  -H "x-amz-security-token: $AWS_SESSION_TOKEN" \
  -H "anthropic-workspace-id: $ANTHROPIC_AWS_WORKSPACE_ID" \
  -H "anthropic-version: 2023-06-01" \
  -H "content-type: application/json" \
  -d '{
    "model": "claude-sonnet-4-6",
    "max_tokens": 1024,
    "messages": [{"role": "user", "content": "Hello!"}]
  }'
```

- `--aws-sigv4` の形式: `aws:amz:<region>:aws-external-anthropic`
- `x-amz-security-token` は STS / SSO / IAM Role などの一時クレデンシャルのときだけ必要
- `anthropic-workspace-id` ヘッダーは**必須**

**利用可能モデル ID**（Bedrock の ARN 形式ではなくネイティブと同じ）:

| モデル | ID |
| --- | --- |
| Claude Opus 4.7 | `claude-opus-4-7` |
| Claude Opus 4.6 | `claude-opus-4-6` |
| Claude Sonnet 4.6 | `claude-sonnet-4-6` |
| Claude Haiku 4.5 | `claude-haiku-4-5` |

### デスクトップ PC から Claude Code で使う

日常のデスクトップ利用では、この Claude Code 経由のセットアップが最も実用的だ。

**Step 1: Claude Code のインストール**

```bash
npm install -g @anthropic-ai/claude-code
```

**Step 2: AWS クレデンシャルを準備**

SigV4 を使う場合（推奨）:

```bash
aws sso login --profile my-profile
export AWS_PROFILE=my-profile
```

API キーを使う場合:

```bash
export ANTHROPIC_AWS_API_KEY='sk-ant-xxxxx'
```

**Step 3: Claude Code を Claude Platform on AWS に向ける**

3 つの環境変数が必須。

```bash
export CLAUDE_CODE_USE_ANTHROPIC_AWS=1
export ANTHROPIC_AWS_WORKSPACE_ID='wrkspc_01ABCDEFGHIJKLMN'
export AWS_REGION='us-east-1'
```

- `CLAUDE_CODE_USE_ANTHROPIC_AWS=1` がないと従来通り `api.anthropic.com` に行ってしまう
- `CLAUDE_CODE_USE_BEDROCK` や `CLAUDE_CODE_USE_FOUNDRY` がセットされていると**そちらが優先**されるので `unset` する

**Step 4: モデルバージョンの固定（チーム展開向け推奨）**

```bash
export ANTHROPIC_DEFAULT_OPUS_MODEL=claude-opus-4-7
export ANTHROPIC_DEFAULT_SONNET_MODEL=claude-sonnet-4-6
export ANTHROPIC_DEFAULT_HAIKU_MODEL=claude-haiku-4-5
```

**Step 5: SSO セッション自動更新（任意）**

`~/.claude/settings.json` に追記すると SSO 期限切れ時に自動再ログイン:

```json
{
  "awsAuthRefresh": "aws sso login --profile my-profile"
}
```

**Step 6: 起動確認**

```bash
claude
```

起動後にプロンプトで `/status` を実行し、`Provider: Claude Platform on AWS` になっていれば成功。

**OS 別の永続設定例**

macOS / Linux（zsh / bash）:

```bash
# ~/.zshrc
export CLAUDE_CODE_USE_ANTHROPIC_AWS=1
export ANTHROPIC_AWS_WORKSPACE_ID='wrkspc_01ABCDEFGHIJKLMN'
export AWS_REGION='us-east-1'
export AWS_PROFILE='my-profile'
```

Windows PowerShell:

```powershell
# $PROFILE
$env:CLAUDE_CODE_USE_ANTHROPIC_AWS = "1"
$env:ANTHROPIC_AWS_WORKSPACE_ID = "wrkspc_01ABCDEFGHIJKLMN"
$env:AWS_REGION = "us-east-1"
$env:AWS_PROFILE = "my-profile"
```

**企業プロキシ / LLM ゲートウェイ経由**:

```bash
export CLAUDE_CODE_USE_ANTHROPIC_AWS=1
export ANTHROPIC_AWS_WORKSPACE_ID='wrkspc_01ABCDEFGHIJKLMN'
export ANTHROPIC_AWS_BASE_URL='https://anthropic-proxy.example.com'
# ゲートウェイ側で SigV4 を付けるなら Claude Code 側はスキップ
export CLAUDE_CODE_SKIP_ANTHROPIC_AWS_AUTH=1
```

### データレジデンシー（推論リージョン指定）

リクエストごとに `inference_geo` を指定可能（Opus 4.6 / Sonnet 4.6 以降のみ対応）:

```python
client.messages.create(
    model="claude-sonnet-4-6",
    inference_geo="us",  # "us" or "global"
    ...
)
```

- `us`: 米国内データセンターに固定（**1.1 倍課金**）
- `global`: 全世界（デフォルト、標準価格）

AWS リージョンは IAM / CloudTrail / 課金のスコープにすぎず、**推論経路は別軸**で制御する。

### トラブルシューティング

| 症状 | 原因と対処 |
| --- | --- |
| `Outbound web identity federation is disabled` | `aws iam enable-outbound-web-identity-federation` を実行 |
| `403 Forbidden / AccessDenied` | IAM ロールに `aws-external-anthropic:*` 権限がない、または API キーが古い |
| `missing-workspace error` | `ANTHROPIC_AWS_WORKSPACE_ID` が未設定 |
| Claude Code が `api.anthropic.com` に行く | `CLAUDE_CODE_USE_ANTHROPIC_AWS=1` 未設定、または `CLAUDE_CODE_USE_BEDROCK` が干渉 |
| 署名拒否エラー | `--aws-sigv4` の region と URL の region が不一致 |
| Usage ページにデータが出ない | 数分のラグ。通常は自然に解消 |

### デスクトップ利用の最短経路まとめ

1. AWS Console から Claude Platform on AWS にサインアップ
2. `aws iam enable-outbound-web-identity-federation` を 1 回実行
3. Workspace ID をメモ
4. `aws sso login --profile <name>` で AWS 認証
5. シェル設定に 3 つの環境変数を追記:
   ```bash
   export CLAUDE_CODE_USE_ANTHROPIC_AWS=1
   export ANTHROPIC_AWS_WORKSPACE_ID='wrkspc_xxx'
   export AWS_REGION='us-east-1'
   ```
6. `claude` を起動して `/status` で Provider 確認 → 完了

これで日常の Claude Code 利用が、AWS の IAM / CloudTrail / 単一請求書のフレームの中で完結する。

## 参考リンク

- [Introducing the Claude Platform on AWS（Anthropic 公式ブログ）](https://claude.com/blog/claude-platform-on-aws)
- [Claude Platform on AWS（AWS ランディングページ）](https://aws.amazon.com/jp/claude-platform/)
- [Set up your account - Claude Platform on AWS（AWS 公式ユーザーガイド）](https://docs.aws.amazon.com/claude-platform/latest/userguide/setup.html)
- [Claude Platform on AWS - Claude API Docs](https://platform.claude.com/docs/en/build-with-claude/claude-platform-on-aws)
- [Claude Code on Claude Platform on AWS（Claude Code 公式ドキュメント）](https://code.claude.com/docs/en/claude-platform-on-aws)
- [Actions, resources, and condition keys for Claude Platform on AWS（IAM リファレンス）](https://docs.aws.amazon.com/service-authorization/latest/reference/list_claudeplatformonaws.html)
- [元ポスト（X / @hata_AI_master）](https://x.com/hata_AI_master/status/2053968293283979694)
