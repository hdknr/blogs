---
title: "HubSpot を Claude Code から操作する 6 つの認証方式の違い — Private App / OAuth / MCP / PAK / Developer Key / Service Key"
date: 2026-05-09
lastmod: 2026-05-09
draft: false
description: "HubSpot 認証方式 6 つ（Private App / OAuth 2.0 / 公式 MCP / Personal Access Key / Developer API Key / Service Key）の違いを Claude Code 文脈で整理。新規構築は Service Key（2026-02 Beta）、Claude Code から自然言語で操作するなら公式 MCP サーバーが推奨。"
source_url: "https://github.com/hdknr/blogs/issues/71#issuecomment-4411663173"
categories: ["クラウド/インフラ"]
tags: ["HubSpot", "Claude Code", "MCP", "認証", "OAuth", "Private App", "Service Key", "REST API"]
---

HubSpot は API 認証の選択肢が多く、「**結局どれを使えばいいのか**」が混乱しがちです。特に Claude Code から HubSpot を操作したい場合、現在は **6 種類の認証手段**が併存しています:

- 非公開アプリ（Private App）
- 旧 API キー（廃止済み）
- MCP 認証アプリ（HubSpot 公式 MCP Server）
- パーソナルアクセスキー（Personal Access Key）
- 開発者 API キー（Developer API Key）
- サービスキー（Service Key、新規 Beta）

この記事では、それぞれの違い・推奨用途・Claude Code から使う場合の選び方を整理します。なお旧 API Key は廃止済みですが、参考情報として記事末尾で触れます（実質的な選択肢は **6 つ**です）。

**結論を先に言うと**: Claude Code から自然言語で HubSpot 操作したいなら**公式 MCP サーバー**、自前スクリプトを書くなら**新登場の Service Key**（既存は **Private App** を継続）、の 2 択でほぼ十分です。

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

### 方法 1: HubSpot 公式 MCP サーバー（最推奨）

```bash
claude mcp add --transport http hubspot --scope user https://mcp.hubspot.com/anthropic
```

接続後は Claude Code に自然言語で指示するだけ:

```
「HubSpot で『ABC 商事』のディール一覧を取得して」
「直近 7 日間に作成されたコンタクトを Markdown でまとめて」
「このメールを読んで HubSpot のコンタクトにメモを追加して」
```

**メリット**:

- 認証が OAuth で安全
- 公式メンテナンスで API 変更に追従
- スキーマやエンドポイントを Claude が把握しているので質問するだけで動く

**前提**: Anthropic 有料サブスクリプション

### 方法 2: REST API 直叩き（Private App / Service Key）

```bash
# Claude Code に「このトークンを使って ... する Python スクリプトを書いて」と指示
export HUBSPOT_TOKEN=pat-na1-...

# Claude Code が requests / httpx ベースのコードを生成
# 必要に応じて HubSpot Python SDK (hubspot-api-client) も使う
```

**メリット**:

- MCP サーバーが対応していない細かい操作も可能
- 自社内で完結（外部 SaaS 経由しない）
- バッチ処理・定期実行に組み込みやすい

**Private App or Service Key**:

- **新規** → Service Key
- **Webhook も併用** → Private App

### 方法 3: HubSpot CLI 経由（Personal Access Key）

```bash
# UI Extension 開発・デプロイ
hubspot auth personal-access-key
hubspot project upload
```

CRM データ操作には不向きで、**Project App / UI Extension のローカル開発・デプロイ**で使う。

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
- **Claude Code から最も簡単に使えるのは公式 MCP Server** — 1 行で接続、自然言語で操作
- **旧 API Key は廃止済み** — 残っていれば即移行
- **OAuth は Marketplace アプリと複数アカウント連携の標準**
- **Personal Access Key と Developer API Key は特定用途専用**

「6 つもある」と聞くと混乱しますが、実際の選択は「**Claude Code から使うなら MCP、自前スクリプトなら Service Key（新規）/ Private App（既存）**」の 2 択でほぼ十分です。

## 参考リンク

- [HubSpot Authentication methods](https://developers.hubspot.com/docs/apps/legacy-apps/authentication/intro-to-auth)
- [HubSpot MCP Server 公式ドキュメント](https://developers.hubspot.com/mcp)
- [HubSpot Connector for Claude](https://knowledge.hubspot.com/integrations/set-up-and-use-the-hubspot-connector-for-claude)
- [Service Keys（Public Beta 告知、2026-02-10）](https://developers.hubspot.com/changelog/service-keys)
- [Service Keys ドキュメント](https://developers.hubspot.com/docs/apps/developer-platform/build-apps/authentication/account-service-keys)
- [Choosing Private vs. Public HubSpot Apps](https://developers.hubspot.com/blog/hubspot-integration-choosing-private-public-hubspot-apps)
- [Upcoming: API Key Sunset（廃止告知）](https://developers.hubspot.com/changelog/upcoming-api-key-sunset)
- [Connect Claude Code to tools via MCP](https://code.claude.com/docs/en/mcp)
