---
title: "HubSpot を Claude Code から操作する 6 つの認証方式の違い — Private App / OAuth / MCP / PAK / Developer Key / Service Key"
date: 2026-05-09
lastmod: 2026-05-09
slug: "hubspot-auth-methods-claude-code"
draft: false
description: "HubSpot 認証方式 6 つ（Private App / OAuth 2.0 / 公式 MCP / Personal Access Key / Developer API Key / Service Key）の違いを Claude Code 文脈で整理。新規構築は Service Key（2026-02 Beta）、Claude Code から自然言語で操作するなら公式 MCP サーバーが推奨。"
source_url: "https://github.com/hdknr/blogs/issues/71#issuecomment-4411663173"
categories: ["クラウド/インフラ"]
tags: ["HubSpot", "claude-code", "mcp", "認証", "OAuth", "Private App", "Service Key", "REST API"]
---

HubSpot は API 認証の選択肢が多く、「**結局どれを使えばいいのか**」が混乱しがちです。特に Claude Code から HubSpot を操作したい場合、現在は **6 種類の認証手段**が併存しています:

- 非公開アプリ（Private App）
- 旧 API キー（廃止済み）
- MCP 認証アプリ（HubSpot 公式 MCP Server）
- パーソナルアクセスキー（Personal Access Key）
- 開発者 API キー（Developer API Key）
- サービスキー（Service Key、新規 Beta）

この記事では、それぞれの違い・推奨用途・Claude Code から使う場合の選び方を整理します。なお旧 API Key は廃止済みですが、参考情報として記事末尾で触れます（実質的な選択肢は **6 つ**です）。

**結論を先に言うと**: 用途で 2 軸に分かれます。

- **アドホックに自然言語で操作したい**（営業・マーケが Claude Code から HubSpot を触る等） → **公式 MCP サーバー**
- **本番運用・バッチ・Webhook など継続的なシステム統合** → **REST API 直叩き + Service Key（新規）/ Private App（既存）**

両者は競合ではなく補完関係で、実務では併用するのが現実解です。

## 早見表

| 認証方式 | 用途 | スコープ | トークン寿命 | 状態 | Claude Code から使うなら |
|---|---|---|---|---|---|
| **HubSpot MCP Server（公式）** | AI エージェントから HubSpot 操作 | アプリと同等 | OAuth ベース | ✅ 2025-2026 リリース | ✅ **最も推奨**（1 行で接続） |
| **Service Key（新）** | システム間データ連携 | アカウント単位の細かい権限 | 永続 | ✅ **2026-02-10 Public Beta** | ✅ Private App の後継、新規ならこれ |
| **Private App** | 単一アカウント向け統合 | アプリ単位で細かく設定 | 永続 | ⚠️ 維持されているが、新規は Service Key 推奨 | ✅ シンプルな REST 呼び出し |
| **OAuth 2.0（Public App）** | Marketplace アプリ・複数アカウント | scope ベース | access 30 分・refresh で更新 | ✅ 公式・現役（v3 が新版） | △ 自前で OAuth フロー実装が必要 |
| **Personal Access Key（PAK）** | HubSpot CLI 認証 | アカウントごと | 永続（rotate 可能） | ✅ 現役 | △ CLI 経由の操作のみ |
| **Developer API Key** | Developer Account 内のアプリ管理 | 開発者アカウント全体 | 永続 | ✅ 現役 | △ アプリ管理用、CRM データには不向き |
| **旧 API Key**（参考） | 単純な API 呼び出し | アカウント全体 | 永続 | ❌ **2022-11-30 廃止** | ❌ 使えない |

## 各認証方式の詳細

### ① 旧 API Key（廃止済み、参考情報）

HubSpot ポータルの「Integrations → API Key」から発行できた**アカウント単位の単一キー**。

- スコープ分離なし（持っているだけで全権限）
- セキュリティ上の問題で **2022 年 11 月 30 日に廃止**
- 既存統合は Private App / OAuth / Service Key のいずれかへ移行済みのはず
- **新規構築では使えない**

「旧アプリ」「Hub-level API Key」と呼ばれていたのはこれです。

### ② Private App（非公開アプリ）

ポータルの「Settings → Integrations → Private Apps」から作成する**単一アカウント向けの統合**。

**特徴**:

- **アクセストークンが永続**（OAuth のように 30 分で失効しない）
- **scope（権限）をアプリ単位で詳細設定可能** — `crm.objects.contacts.read` などをチェックボックスで選択
- 1 アカウントにつき複数作れる（用途別に分離可能）
- ポータルから即座に rotate（再発行）可能

**使い方**:

```bash
# Authorization ヘッダに Bearer トークンを入れて REST API を呼ぶだけ
curl -H "Authorization: Bearer pat-na1-xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx" \
     https://api.hubapi.com/crm/v3/objects/contacts
```

**Claude Code からの使い方**:

> 「HubSpot の API キーをこの環境変数に入れた。コンタクト一覧を取得する Python スクリプトを書いて」

と指示すると、Claude Code が以下のようなコードを生成します。

```python
import os, requests

HUBSPOT_TOKEN = os.environ["HUBSPOT_PRIVATE_APP_TOKEN"]
r = requests.get(
    "https://api.hubapi.com/crm/v3/objects/contacts",
    headers={"Authorization": f"Bearer {HUBSPOT_TOKEN}"},
)
```

シンプルで強力ですが、**新規構築なら後述の Service Key の方が将来性がある**という位置付けに変わってきています。

### ③ OAuth 2.0（Public App）

HubSpot App Marketplace に公開するアプリや、**複数の HubSpot アカウントを横断して動く統合**で使う標準的な OAuth フロー。

**特徴**:

- 各アカウントのユーザーが **OAuth 同意画面**でアプリにアクセスを許可
- **access token は 30 分で失効**、refresh token で更新
- scope ベースで権限を細かく制御
- v1 は deprecated、**v3 が現役**（強化されたセキュリティ）

Claude Code から直接使うには OAuth フロー（リダイレクト・コールバック・トークン交換）の実装が必要です。**通常は MCP サーバーや Private App / Service Key の方が手軽**になります。

### ④ HubSpot MCP Server（公式、Claude Code に最適）

2025 年に HubSpot が公式リリースした **Model Context Protocol サーバー**。Claude Code から **1 行のコマンド**で接続できます。

```bash
claude mcp add --transport http hubspot --scope user https://mcp.hubspot.com/anthropic
```

**特徴**:

- **OAuth ベースで認証** — 初回接続時にブラウザでログインして同意
- Claude Code が「HubSpot のコンタクトを検索して」「この見込み客にメモを追加して」を自然言語で実行
- HubSpot 公式メンテナンスなので**安定性・追従性が高い**
- 単一アカウントでも複数アカウントでも動く

**前提**:

- 有効な HubSpot ユーザーアカウント
- 有効な Claude アカウント
- **Anthropic の有料サブスクリプション**（Pro / Max / Team / Enterprise のいずれか）

Claude / Claude.ai 側の **HubSpot Connector**（Settings から有効化する公式コネクタ）と背後の仕組みは同じです。**Claude Code から触る場合は MCP サーバー経由**になります。

### ⑤ Personal Access Key（パーソナルアクセスキー、PAK）

**HubSpot CLI** （`hubspot` コマンド）で使う認証用のキー。

```bash
# CLI 認証
hubspot auth personal-access-key

# UI extension のローカル開発・デプロイ
hubspot project upload
```

**特徴**:

- **CLI 操作と UI Extensions / Project ベースアプリの開発専用**
- アカウント単位で発行
- GitHub のシークレットスキャン対象（漏洩したら自動検知）
- API 呼び出しの汎用認証ではない

Claude Code から CLI を経由してプロジェクト操作・デプロイするなら使いますが、**CRM データ取得・更新が目的なら PAK は適切ではありません**。

### ⑥ Developer API Key（開発者 API キー）

**Developer Account**（HubSpot アプリ開発者用の親アカウント）内で発行するキー。

**用途**:

- アプリのインストール統計・メトリクスの取得
- アプリの設定や Webhook 管理
- 顧客アカウント（Customer Account）の管理

**重要な制限**:

- **顧客 HubSpot アカウントの CRM データにはアクセスできない**
- アプリ自体の管理用 API のみ

「開発者アカウントを持っている」場合に発行するもので、通常の業務統合では出番がありません。

### ⑦ Service Key（サービスキー、Beta）

**2026 年 2 月 10 日に Public Beta に入った新しい認証方式**。Private App の後継として位置付けられています。

**特徴**:

- **アカウント単位の API クレデンシャル** — system-to-system 統合専用
- **scope が Private App より細かく制御可能**
- HubSpot の最新 Developer Platform インフラに基づいて設計
- Private App と同じく**永続トークン**

**作成方法**:

ポータルで `Development → Keys → Service keys → Create service key`

```bash
# 使い方は Private App と同じ（Bearer トークン）
curl -H "Authorization: Bearer hsk-xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx" \
     https://api.hubapi.com/crm/v3/objects/contacts
```

**制限事項**:

- Webhook の認証には使えない（Webhook が必要なら Project ベースアプリ + CLI、または Private App を引き続き使用）
- UI Extension 内の API 呼び出しには使えない
- REST API 呼び出し専用

**Private App との使い分け**:

- **新規構築 + 純粋な REST API 連携** → **Service Key 推奨**
- **Webhook も使う / UI Extension も使う** → Private App か Project App
- **既存の Private App** → 当面は維持。強い理由がなければ移行不要

## Claude Code から HubSpot を操作する 3 通りの方法

3 つの方法は競合ではなく、**用途が違います**。「人間がアドホックに触る」なら方法 1、「システムが本番で継続的に動かす」なら方法 2、「Project / UI Extension の開発」なら方法 3、と棲み分けるのが正しい理解です。

### 方法 1 vs 方法 2 の比較

| 観点 | 方法 1: 公式 MCP | 方法 2: REST API 直叩き |
|---|---|---|
| セットアップ | ◎ 1 行で接続 | ○ 環境変数 + コード |
| 自然言語操作 | ◎ そのまま指示 | △ コード生成は可だが実行は手動 |
| **本番運用（バッチ・cron）** | △ Claude Code を都度起動は非現実的 | ◎ 純粋な Python スクリプトとして安定動作 |
| **ランタイムコスト** | ✕ Claude API トークンが毎回かかる | ◎ HubSpot API のレート制限のみ |
| **外部依存** | ✕ Anthropic + HubSpot MCP インフラ | ◎ HubSpot だけ |
| **エラー処理・リトライ** | △ Claude 任せ、細かい制御が難しい | ◎ コードで完全制御 |
| **可能な操作の範囲** | △ MCP サーバーが提供する範囲 | ◎ HubSpot API 全エンドポイント |
| **デバッグ容易性** | △ Claude 経由でブラックボックス気味 | ◎ ログ・スタックトレースが普通に取れる |
| **CI/CD 組み込み** | △ non-interactive 実行が要る | ◎ そのまま組み込める |
| **必要なサブスク** | ✕ Anthropic 有料プラン必須 | ◎ なし |

つまり**「人間が触る入口は MCP、システムが動かす中核は REST API」**が補完関係です。

### 方法 1: HubSpot 公式 MCP サーバー（アドホック操作・対話的な作業向け）

```bash
claude mcp add --transport http hubspot --scope user https://mcp.hubspot.com/anthropic
```

接続後は Claude Code に自然言語で指示するだけ:

```
「HubSpot で『ABC 商事』のディール一覧を取得して」
「直近 7 日間に作成されたコンタクトを Markdown でまとめて」
「このメールを読んで HubSpot のコンタクトにメモを追加して」
```

**向いている場面**:

- アドホックな調査・分析（営業・マーケが「直近 30 日の新規コンタクトを業界別に集計」）
- 対話的な仮説検証
- コードを書きたくないユーザー
- 1 回限りで再現性不要なタスク

**メリット**:

- 認証が OAuth で安全
- 公式メンテナンスで API 変更に追従
- スキーマやエンドポイントを Claude が把握しているので質問するだけで動く

**前提**: Anthropic 有料サブスクリプション

### 方法 2: REST API 直叩き（Private App / Service Key）— 本番運用の本命

```bash
# Claude Code に「このトークンを使って ... する Python スクリプトを書いて」と指示
export HUBSPOT_TOKEN=pat-na1-...

# Claude Code が requests / httpx ベースのコードを生成
# 必要に応じて HubSpot Python SDK (hubspot-api-client) も使う
```

**向いている場面（本番運用ではこちらが最有力）**:

- **定期バッチ**: 毎朝 9 時に新規リードを別 DB に同期
- **Webhook 受信処理**: HubSpot からのイベントに反応
- **大量データ処理**: 100 万件のコンタクトをスクリプトで一気に更新
- **本番アプリケーション**: SaaS の HubSpot 連携機能
- **コスト最適化**: Claude API トークンを毎回消費したくない
- **再現性・監査が必要**: コード化された手続きが必要

**メリット**:

- HubSpot API の全エンドポイントにアクセス可能（MCP の範囲外も含む）
- 自社内で完結（外部 SaaS 経由しない）
- バッチ処理・定期実行に組み込みやすい
- Anthropic 有料プラン不要、ランタイムコストが極小

**Private App or Service Key**:

- **新規構築** → Service Key
- **Webhook も併用** → Private App

Claude Code は**コード生成器**として使い、生成されたスクリプトは Claude を介さず単独で動かす — このパターンが本番運用では最も実用的です。

### 方法 3: HubSpot CLI 経由（Personal Access Key）

```bash
# UI Extension 開発・デプロイ
hubspot auth personal-access-key
hubspot project upload
```

CRM データ操作には不向きで、**Project App / UI Extension のローカル開発・デプロイ**で使います。

## セットアップフローの内部動作 — MCP と Service Key の比較

それぞれの認証方式が「**初回セットアップ時に何が起きているか**」を理解しておくと、トラブル時のデバッグや、運用の判断（ローテーション戦略・失効対応）がしやすくなります。

### MCP サーバー登録時の OAuth フロー

ユーザーは `claude mcp add` を 1 行打つだけですが、内部では複数のステップが順に走っています。

```text
┌─────────────────────────────────────────────────┐
│ 1. claude mcp add --transport http hubspot ...  │
│    → Claude Code の設定ファイルに URL を登録するだけ │
│    → この時点では OAuth は開始しない             │
└─────────────────────────────────────────────────┘
                      ↓
┌─────────────────────────────────────────────────┐
│ 2. Claude Code を起動 / 初めて MCP を呼び出す   │
│    → MCP サーバーへ HTTP リクエスト              │
│    → 401 Unauthorized + OAuth メタデータの場所   │
└─────────────────────────────────────────────────┘
                      ↓
┌─────────────────────────────────────────────────┐
│ 3. Claude Code が OAuth メタデータを取得         │
│    /.well-known/oauth-authorization-server      │
│    → HubSpot の authorize / token エンドポイント │
└─────────────────────────────────────────────────┘
                      ↓
┌─────────────────────────────────────────────────┐
│ 4. Dynamic Client Registration (RFC 7591)       │
│    → Claude Code が自身をクライアントとして登録  │
│    → client_id を取得（pre-registered の場合あり）│
└─────────────────────────────────────────────────┘
                      ↓
┌─────────────────────────────────────────────────┐
│ 5. ブラウザが開いて HubSpot ログイン画面へ      │
│    PKCE 付き Authorization Code フロー          │
│    → ユーザーがログイン + 同意                   │
└─────────────────────────────────────────────────┘
                      ↓
┌─────────────────────────────────────────────────┐
│ 6. HubSpot がコールバック URL に                │
│    authorization_code を返す                    │
└─────────────────────────────────────────────────┘
                      ↓
┌─────────────────────────────────────────────────┐
│ 7. Claude Code が token エンドポイントへ        │
│    code → access_token + refresh_token に交換   │
└─────────────────────────────────────────────────┘
                      ↓
┌─────────────────────────────────────────────────┐
│ 8. トークンをローカル保存                        │
│    ~/.claude/ の設定ファイル or 各 OS の keychain│
│    （実装依存）                                   │
└─────────────────────────────────────────────────┘
                      ↓
┌─────────────────────────────────────────────────┐
│ 9. 以降、access_token で API 呼び出し           │
│    30 分で失効したら refresh_token で自動更新    │
└─────────────────────────────────────────────────┘
```

#### 押さえておくべき点

- **OAuth が始まるのは `add` ではなく初回呼び出し時**: `claude mcp add` は設定ファイル更新だけのオフライン操作。
- **保存されるトークンは 2 種類**: 短命の `access_token`（30 分）と長期の `refresh_token`。後者がある限り自動更新で再ログイン不要。
- **保存先は OS 依存**: macOS は Keychain、Linux は libsecret（Secret Service）、Windows は Credential Manager。実装によっては `~/.claude/` 内の設定ファイルに直書きされる場合もあるので、機密性が気になるなら実際の保存先を確認するのが確実。
- **Dynamic Client Registration (RFC 7591)** で Claude Code が動的に自身をクライアントとして登録。事前のアプリ登録不要で接続できるのが MCP HTTP transport の大きな利点。詳しくは [RFC 7591 Dynamic Client Registration を MCP で活用する記事](/blogs/posts/2026/05/rfc7591-dynamic-client-registration-mcp/)。

#### トークンを失効させるには

```bash
# Claude Code 側から MCP を削除（ローカルトークンも削除）
claude mcp remove hubspot

# HubSpot 側からアプリのアクセスを取り消す
# Settings → Integrations → Connected Apps → 該当アプリを Revoke
```

両側からトークン無効化できるのが OAuth ベースの利点です。

### Service Key 取得から REST API デプロイまでのフロー

Service Key は OAuth を伴わない**ハンドアウト型のクレデンシャル**です。発行・配布・運用の主導権がアプリケーション開発者側にあるのが特徴で、フローはシンプルですが**機密情報の保管責任は自分側に来ます**。

```text
┌─────────────────────────────────────────────────┐
│ 1. HubSpot ポータルにログイン                    │
│    （Super Admin または相当のロールが必要）      │
└─────────────────────────────────────────────────┘
                      ↓
┌─────────────────────────────────────────────────┐
│ 2. Development → Keys → Service keys           │
│    → Create service key                         │
└─────────────────────────────────────────────────┘
                      ↓
┌─────────────────────────────────────────────────┐
│ 3. 名前と scope（権限）を設定                   │
│    crm.objects.contacts.read                    │
│    crm.objects.contacts.write                   │
│    crm.objects.deals.read … 必要なものだけ      │
└─────────────────────────────────────────────────┘
                      ↓
┌─────────────────────────────────────────────────┐
│ 4. Create を押すと Service Key が表示される    │
│    例: hsk-na1-xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxx │
│    ⚠️ 1 度しか表示されない → 必ずコピーして保管  │
└─────────────────────────────────────────────────┘
                      ↓
┌─────────────────────────────────────────────────┐
│ 5. シークレットストレージに保存                  │
│    .env + .gitignore（ローカル開発）            │
│    AWS Secrets Manager / GCP Secret Manager     │
│    Kubernetes Secret                            │
│    GitHub Actions Secret（CI/CD 用）            │
└─────────────────────────────────────────────────┘
                      ↓
┌─────────────────────────────────────────────────┐
│ 6. アプリケーションが環境変数から読み込み        │
│    export HUBSPOT_SERVICE_KEY=hsk-na1-...       │
└─────────────────────────────────────────────────┘
                      ↓
┌─────────────────────────────────────────────────┐
│ 7. REST API 呼び出し                            │
│    Authorization: Bearer $HUBSPOT_SERVICE_KEY   │
│    https://api.hubapi.com/crm/v3/...            │
└─────────────────────────────────────────────────┘
                      ↓
┌─────────────────────────────────────────────────┐
│ 8. 定期ローテーション（推奨 90 日ごと）          │
│    新 Key 発行 → secret store 更新              │
│    → アプリ再デプロイ → 旧 Key を revoke        │
└─────────────────────────────────────────────────┘
```

実際のコード例:

```python
import os
import requests

HUBSPOT_SERVICE_KEY = os.environ["HUBSPOT_SERVICE_KEY"]

r = requests.get(
    "https://api.hubapi.com/crm/v3/objects/contacts",
    headers={"Authorization": f"Bearer {HUBSPOT_SERVICE_KEY}"},
    params={"limit": 10},
)
r.raise_for_status()
contacts = r.json()["results"]
```

#### 押さえておくべき点

- **発行時のみ表示される**: 一度ポータルを閉じると元の Key は二度と表示されない。コピーを忘れたら**新しい Key を発行**して旧 Key を revoke する。
- **scope は最小権限で**: 「全部許可」ではなく必要な権限だけチェック。インシデント時の被害を限定。
- **シークレットストレージで管理**: コード直書きや `.env` の Git コミットは厳禁。チームで共有するなら Vault / AWS Secrets Manager / 1Password CLI 等を使う。
- **ローテーション戦略**: 期限なしの永続キーなので、定期ローテーション（90 日 / 半年 / 退職時）の運用ルールを明文化しておく。HubSpot ポータルから新規発行・古いものの revoke が即可能。
- **Webhook には使えない**: Webhook を受け取るなら Private App か Project App を別途用意。
- **`hsk-` プレフィクス**: Bearer トークンとして使う際に分かりやすいよう、Service Key は `hsk-` 始まり（Private App は `pat-` 始まり）。漏洩検出ツール（GitHub Secret Scanning 等）でもパターンマッチしやすい。

#### Key を失効させるには

```text
HubSpot ポータル → Development → Keys → Service keys
→ 該当 Key の「…」メニュー → Delete
```

削除と同時に該当 Key での認証は即座に拒否されます。アプリ側のシークレットストレージも忘れずに更新すること。

### MCP OAuth と Service Key の決定的な違い

| 観点 | MCP（OAuth） | Service Key |
|---|---|---|
| 認証主体 | **ユーザー個人** | **アプリケーション（system）** |
| 権限スコープ | ユーザーが持つ権限 + 同意した範囲 | Key 発行時に設定した scope（固定） |
| トークン寿命 | access 30 分 + refresh で自動更新 | 永続（手動 rotate） |
| 失効方法 | 両側から可能（Claude Code 側 / HubSpot 側） | HubSpot ポータルから削除 |
| 配布 | 各ユーザーが各自で OAuth を通す | 1 つの Key を secret store で集中管理 |
| ブラウザ依存 | あり（初回ログイン時） | なし（ヘッドレスで完結） |
| バッチ・cron 適性 | △（ユーザートークンが必要） | ◎（system-to-system 設計） |
| 監査ログ | 各ユーザー単位で記録 | アプリ単位で記録 |

「**人間が触る = OAuth、システムが動かす = Service Key**」という棲み分けは、こうした内部動作の違いから来ています。

## 利用者への権限設定 — 2 つのフローでの設計の違い

OAuth と Service Key では「誰が何にアクセスできるか」を制御する仕組みが根本的に違います。**OAuth は HubSpot のユーザー権限管理がそのまま効く**のに対し、**Service Key は Key 単位で固定された権限**を持つだけで、ユーザー概念がありません。

### OAuth（MCP）フローの権限が決まる 3 レイヤー

実際にユーザーが操作できる範囲は、以下の **3 つの交差点** で決まります。

```text
┌──────────────────────────────┐
│ ① アプリ（MCP サーバー）の   │
│    declared scope            │ ← HubSpot にアプリ登録時に宣言
│    例: contacts.read,        │
│        contacts.write,       │
│        deals.read            │
└──────────────────────────────┘
              ∩
┌──────────────────────────────┐
│ ② ユーザーが OAuth 画面で    │
│    同意した scope            │ ← ログイン時に granted
│    （減らせるが、増やせない）│
└──────────────────────────────┘
              ∩
┌──────────────────────────────┐
│ ③ ユーザー本人の HubSpot     │
│    ロール / 権限             │ ← HubSpot 管理者が設定
│    例: Super Admin /         │
│        Sales / View-only     │
└──────────────────────────────┘
              ↓
       実際の API アクセス権
```

**① アプリ側の declared scope** — MCP サーバー提供者の設計に依存:

- 公式 MCP（`https://mcp.hubspot.com/anthropic`）は CRM 操作に必要な汎用 scope セットを要求
- ユーザー側でアプリの scope を変更することはできない
- 「このアプリは何を要求しているか」は同意画面で確認できる

**② ユーザーが同意する scope** — OAuth 同意画面で:

```
このアプリは以下のアクセスを要求しています:
✅ コンタクトの読み取り
✅ コンタクトの書き込み
✅ ディールの読み取り
☐  ディールの書き込み（任意）
```

任意 scope は外せる場合がある（HubSpot Public App の設計次第）。同意しなければ認証は完了しない。

**③ ユーザー本人のロール** — HubSpot 管理者が事前に設定:

```text
HubSpot ポータル → Settings → Users & Teams
  → 個別ユーザーの Permissions タブ
  - CRM access (Contacts/Companies/Deals/Tickets) を細かく
  - Marketing access
  - Sales access
  - Reports access
  - Account access (Settings 操作可否)
  → Permission Sets でテンプレ化して使い回し
```

#### OAuth フローの重要な特性

- **同じ MCP 接続でもユーザーごとに操作可能範囲が違う** — Aさん（Super Admin）は全部、Bさん（Sales）はコンタクトのみ、というのが自動で実現
- **ユーザー追加・削除・ロール変更が即座に反映** — HubSpot 側で View-only に降格したら、その瞬間から書き込み API が 403 を返すようになる
- **監査ログがユーザー単位** — 「誰がどのコンタクトを更新したか」を HubSpot 側で追跡できる
- **退職者のアクセスは HubSpot ユーザー削除で即無効化** — 個別 Key 管理が不要

### Service Key フローの権限設定

```text
┌──────────────────────────────┐
│ ① Key 発行時に選択した scope │ ← Key 作成者（HubSpot 管理者）が設定
│    例:                        │
│    crm.objects.contacts.read  │
│    crm.objects.contacts.write │
│    crm.objects.deals.read     │
└──────────────────────────────┘
              ↓
┌──────────────────────────────┐
│ ② ユーザー概念が「ない」     │
│    Key 自体が API クライアント│
│    どのユーザーが叩いても同じ │
│    権限                       │
└──────────────────────────────┘
              ↓
       実際の API アクセス権
```

OAuth と違って **「ユーザーロールでの絞り込み」が機能しない**。Key の scope = そのまま実権限になる。

#### 設定手順

```text
1. HubSpot ポータル → Development → Keys → Service keys
2. Create service key
3. Name を入力（例: "Nightly Lead Sync Job"）
4. Permissions（scope）を選択:
   - CRM
     ☐ crm.objects.contacts.read
     ☐ crm.objects.contacts.write
     ☐ crm.objects.companies.read
     ☐ crm.objects.deals.read
     ☐ ... 必要なものだけチェック
   - Marketing
     ☐ marketing.campaigns.read
     ☐ marketing.emails.read
   - Settings / Schemas / etc.
5. Create を押すと Key が生成される（1 度しか表示されない）
```

#### 「ユーザーごとに違う権限」を実現するパターン

Service Key はそのままでは **全ユーザー共通の権限** になる。「Aさんはコンタクトのみ、Bさんは全データ」のような分離をしたい場合は、**Key を複数発行して配り分ける** のが基本パターン:

| パターン | 設計 |
|---|---|
| **全社共通の単一 Key** | 1 Key、最小権限。全ジョブが共有 |
| **チーム / 用途別** | Sales 用 / Marketing 用 / 分析用と複数 Key |
| **マルチテナント SaaS** | テナントごとに別 Key を発行・管理 |
| **環境別** | Dev / Staging / Prod でそれぞれ別 Key |

それぞれの Key を**シークレットストレージで分離管理**し、アプリ起動時に環境変数で必要な Key だけ読み込む。

#### アプリ層で「ユーザー権限」を独自実装するパターン

Service Key 経由で動く SaaS が「エンドユーザーごとに違う HubSpot データを見せたい」場合は、**アプリ側で独自の権限管理層を実装**します:

```python
# 例: SaaS のユーザー A はコンタクト 1〜100 だけ見られる
def get_contacts_for_user(user_id: str):
    # アプリ側の認可ロジック
    allowed_contact_ids = check_user_permissions(user_id)
    # Service Key で全データにアクセス可能だが、フィルタしてから返す
    return hubspot_api.fetch_contacts(ids=allowed_contact_ids)
```

これは HubSpot 側の権限ではなく、**アプリ側の責任**で実装する点が OAuth と決定的に違う。

#### Service Key の運用上の注意

- **権限変更 = Key を新しく発行** — 既存 Key の scope は後から変更できない。要件が変わったら新規発行 → 旧 Key を revoke
- **退職対応** — Key を revoke するだけ（HubSpot ユーザーアカウントとは独立）
- **監査ログは Key 単位** — 「どの Key が叩いたか」は分かるが「実際に裏で誰が指示したか」はアプリ側のログで補完が必要
- **共有される秘密** — 1 つの Key を複数のチームメンバーが使うと「漏洩したら誰の責任か」が曖昧になる。可能ならユーザー / 用途ごとに Key を分離

### 設計判断のポイント

| 観点 | OAuth（MCP） | Service Key |
|---|---|---|
| 権限の単位 | **ユーザー単位**（HubSpot ロール経由） | **Key 単位**（発行時に固定） |
| 権限変更 | HubSpot 管理者がユーザーロールを変えるだけ | 新 Key 発行 + 旧 Key revoke + アプリ更新 |
| 退職対応 | HubSpot ユーザー削除で即無効 | Key を revoke |
| 監査ログ | ユーザー個人に紐づく | Key（アプリ）に紐づく |
| 「ユーザーごとに違う権限」の実現 | ◎ 自動 | △ Key を分けるか、アプリ層で独自実装 |
| 利用者が増えた時の管理 | ◎ HubSpot 側の管理に集約 | △ Key の数が増えて管理コスト増 |
| 適合シナリオ | 多数のユーザーが個別に HubSpot を触る | システムがバックグラウンドで動く |

判断基準を簡潔にまとめると:

- **「人間がそれぞれ違う権限で触る」なら OAuth（MCP）** — HubSpot のユーザー権限管理がそのまま効く
- **「システムが裏で動く、権限はアプリ単位で固定」なら Service Key** — Key 単位の最小権限管理 + ローテーション運用
- **「SaaS のエンドユーザーに見せる範囲を制御したい」なら Service Key + アプリ層認可** — HubSpot の権限機能は使えないので自前で

## 制約と前提条件 — MCP / OAuth が使えないケース

ここまで「OAuth は 3 レイヤー」「Service Key は 2 レイヤー」と説明しましたが、実運用では**さらに上のレイヤー**が制約として効いてきます。「同意画面で `contents` scope を追加できない」「MCP に接続できない」といった現象の多くは、ユーザー権限ではなく**契約・組織レベルの設定**で弾かれているケースです。

### 真の権限階層は 5 レイヤー

```text
┌───────────────────────────────────────┐
│ ⓪ HubSpot サブスクリプション層        │ ← 契約プランで使える機能が決まる
│    Free / Starter / Pro / Enterprise │
│    + 各 Hub (CMS Hub, Sales Hub …)   │
└───────────────────────────────────────┘
              ↓
┌───────────────────────────────────────┐
│ ① アプリの declared scope             │ ← アプリ登録時に「契約上利用可能な
│    （契約していない scope は         │    scope のみ」が選択肢に出る
│    そもそも UI に出てこない）         │
└───────────────────────────────────────┘
              ↓
┌───────────────────────────────────────┐
│ ② アカウント管理者のマーケットプレイス │ ← 「ユーザーが任意のアプリを
│    制限                               │    入れていいか」を Super Admin が
│    （App approval setting）          │    制御可能
└───────────────────────────────────────┘
              ↓
┌───────────────────────────────────────┐
│ ③ ユーザーが OAuth 画面で同意         │
└───────────────────────────────────────┘
              ↓
┌───────────────────────────────────────┐
│ ④ ユーザー本人の HubSpot ロール       │
└───────────────────────────────────────┘
              ↓
       実際の API アクセス権
```

### 「`contents` scope を追加できない」はなぜ起きるか

`contents` 系の scope（`content`、`hubdb`、`files` など）は **CMS Hub の機能** に紐づいています。アプリ登録画面で追加できない原因として考えられるのは:

1. **CMS Hub を契約していない** — Marketing Hub だけ契約している場合、CMS 側の scope はそもそもアプリ登録画面に出てこない
2. **CMS Hub Free しかない** — 一部 scope は Pro 以上で開放される
3. **アプリ登録画面でのリスト不足** — Public App と Private App で利用可能な scope セットが違う
4. **「旧アプリ」だから** — 古いアプリ登録形式で、新規 scope の追加が deprecated path にある可能性

確認方法:

```text
HubSpot Developer ポータル
  → 該当アプリ → Auth タブ
  → "Scopes" セクションで利用可能 scope の一覧
  → grayed out / 表示されないものは契約 or 設定で制限されている
```

ポータルで `contents` が灰色表示 / 表示されない場合は、**ユーザーレベルの権限ではなくアカウント契約レベルの問題**です。アカウントの Super Admin に問い合わせて:

- CMS Hub を契約に追加するか
- アカウント設定で対象機能を有効化するか
- 別のアプリ形式（Private App、Project App、Service Key）で代替するか

を判断する必要があります。

### MCP がそもそも使えないケース

公式 HubSpot MCP も**同じ階層の制約を受けます**。

#### ⓪ HubSpot サブスクリプション層

- **HubSpot Free** ではマーケットプレイスアプリの一部機能が制限される
- 公式 MCP がアクセスする CRM オブジェクトの一部（Custom Objects、Workflows など）は **Pro / Enterprise** が前提
- HubSpot 側が「MCP は Free / Starter では非対応」とした場合、API 呼び出しが 403 で失敗

#### ① アプリのインストール権限

- 公式 MCP（`https://mcp.hubspot.com/anthropic`）は HubSpot アカウントに「アプリ」としてインストールされる
- HubSpot のアカウント設定で **「Marketplace アプリの追加」** が制限されている場合、Super Admin の承認が必要
- ユーザーが OAuth 同意画面まで進めても、最終的に「Admin Approval Required」で止まる

確認:

```text
HubSpot ポータル → Settings → Account Setup → Permissions
→ "App Marketplace install requests" の設定
- 全ユーザー OK
- Super Admin 承認が必要
- Super Admin のみインストール可能
```

#### ② Anthropic 側のサブスクリプション

- 公式 MCP の利用には **Anthropic Pro / Max / Team / Enterprise** の有料プランが必要
- Free プランでは公式 MCP は接続できない

#### ③ Claude Code の MCP scope 制限

- `claude mcp add ... --scope user` はユーザー単位、`--scope project` はプロジェクト単位
- 共有マシン / チーム環境で「project scope」の MCP を入れたい場合、リポジトリオーナー / 管理者の承認が必要なことがある

#### ④ ネットワーク / セキュリティポリシー

- 企業ネットワークで `mcp.hubspot.com` への外向き通信が遮断されている
- 認証時のリダイレクト URL（OAuth コールバック）が localhost だが、企業プロキシで弾かれる
- ZTNA / SASE 製品が MCP のトラフィックを未知のものとして遮断

### 使えないときの判断フロー

```text
MCP に接続できない / scope が足りない
            ↓
[ Super Admin に確認 ]
   - HubSpot 契約プランは何か？
   - 必要な Hub（CMS / Sales / Marketing）を契約しているか？
   - Marketplace アプリのインストール制限はあるか？
            ↓
   ┌────────┴────────┐
契約・制限あり        契約・制限なし
   ↓                       ↓
[ 代替案 ]              [ Anthropic プラン確認 ]
- 契約アップグレード     - Pro 以上を契約済みか
- Private App 利用       ↓
  （既存契約内で         [ ネットワーク確認 ]
   発行可能）            - mcp.hubspot.com に到達可能か
- Service Key 利用       - OAuth コールバック OK か
  （Super Admin に
   依頼して発行）
```

### 実用的な対処パターン

#### パターン A: Super Admin と相談できる

- 必要な scope / Hub を伝えて契約 or 設定変更を依頼
- 一時的なものなら Super Admin に **Service Key を発行してもらう**（必要な scope だけチェック）→ そのキーを使って自分の用途を実装

#### パターン B: Super Admin に依頼できない / 即座にやりたい

- 自分のロールで作れる **Private App**（Settings → Integrations → Private Apps）を使う
- Private App は通常 Super Admin / Admin ロールでないと作れないが、組織によっては緩いことも
- 利用できる scope は自分のロール権限の範囲内に限定される

#### パターン C: 個人でテストしたい / 検証用

- **無料の HubSpot Developer Account** で Test Account を作成
- そこで Super Admin として全 scope を試せる
- 本番アカウントへの切替時に同じ scope が利用可能かを別途確認

#### パターン D: MCP がブロックされて使えない

- **方法 2（REST API 直叩き + Private App / Service Key）に切り替える**
- ヘッドレス環境で完結するので OAuth リダイレクトの問題は出ない
- ネットワーク的には `api.hubapi.com` への HTTPS 通信のみ必要
- 自社マシン内で完結するので情シスの承認も得やすい

### なぜ「2 択でほぼ十分」が現実的なのか — 改めて

冒頭で「MCP と Service Key の 2 択でほぼ十分」と書きましたが、**MCP 経由は契約・組織・ネットワーク・サブスクリプションの全レイヤーをクリアする必要があり**、企業環境では実は使えないことが珍しくありません。「アドホック調査用に MCP も使える」と読み替えるのが現実的で、**業務統合の本命は方法 2（REST API + Service Key / Private App）になりがち**です。

つまり「MCP は使えれば便利だが、組織条件次第で使えないことも多い」という事実が、**方法 2 を実質的な本命**にしている根拠です。MCP に接続できない場合の Plan B として、必ず Service Key / Private App の運用ルートも準備しておくのが安全です。

## 用途別の推奨

| やりたいこと | 推奨認証 |
|---|---|
| Claude Code から自然言語で HubSpot 操作（CRUD） | **MCP サーバー** |
| 自社の独自スクリプトで CRM データ連携 | **Service Key**（新規）/ Private App（既存） |
| Marketplace 公開アプリ・複数アカウント連携 | **OAuth 2.0** |
| Webhook を受け取る統合 | **Private App** または **Project App** |
| HubSpot CLI で UI Extension 開発 | **Personal Access Key** |
| 顧客アカウントの管理（開発者ロール） | **Developer API Key** |
| 旧 API Key で動いている古いコード | **即移行**（廃止済み） |

## セキュリティ上の注意

### 共通の鉄則

- **トークンを Git に commit しない** — `.env` で管理、`.gitignore` に追加
- **環境変数 or シークレットマネージャーで管理**
- **定期的に rotate** — Private App / Service Key は UI から即座に rotate 可能
- **scope は最小限** — 必要な権限だけ付与

### Claude Code 利用時の追加注意

- MCP サーバー経由なら**トークンが Claude Code に直接渡らない**ので最も安全
- REST API 直叩きの場合、Claude Code が出力したコードに**トークンが直書きされていないか**を必ず確認
- 作業用の一時ディレクトリやログファイルにトークンを書き出さない（誤って Git に push される可能性）

## まとめ

- 現時点で**最も将来性があるのは Service Key**（新規 system-to-system 統合）
- **Webhook が必要なら Private App / Project App** を引き続き使用
- **Claude Code でアドホックに自然言語操作するなら公式 MCP Server** — 1 行で接続して即座に使える
- **本番運用（バッチ・Webhook・大量処理）は REST API 直叩き（Service Key / Private App）が最有力** — Claude Code はコード生成器として使い、生成されたスクリプトは Claude を介さず単独で動かす
- **旧 API Key は廃止済み** — 残っていれば即移行
- **OAuth は Marketplace アプリと複数アカウント連携の標準**
- **Personal Access Key と Developer API Key は特定用途専用**

「6 つもある」と聞くと混乱しますが、用途で割り切ると 2 軸で済みます:

- **人間が触る入口（探索・対話）** → **MCP サーバー**
- **システムが動かす中核（本番・バッチ）** → **REST API + Service Key（新規）/ Private App（既存）**

両者は**競合ではなく補完関係**で、多くの組織では併用するのが現実解です。

## 参考リンク

- [HubSpot Authentication methods](https://developers.hubspot.com/docs/apps/legacy-apps/authentication/intro-to-auth)
- [HubSpot MCP Server 公式ドキュメント](https://developers.hubspot.com/mcp)
- [HubSpot Connector for Claude](https://knowledge.hubspot.com/integrations/set-up-and-use-the-hubspot-connector-for-claude)
- [Service Keys（Public Beta 告知、2026-02-10）](https://developers.hubspot.com/changelog/service-keys)
- [Service Keys ドキュメント](https://developers.hubspot.com/docs/apps/developer-platform/build-apps/authentication/account-service-keys)
- [Choosing Private vs. Public HubSpot Apps](https://developers.hubspot.com/blog/hubspot-integration-choosing-private-public-hubspot-apps)
- [Upcoming: API Key Sunset（廃止告知）](https://developers.hubspot.com/changelog/upcoming-api-key-sunset)
- [Connect Claude Code to tools via MCP](https://code.claude.com/docs/en/mcp)
