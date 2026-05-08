---
title: "Claude Code から Microsoft Teams を操作する3つの方法 — Workflows Webhook / M365 Connector / ms-365-mcp-server"
date: 2026-04-27
lastmod: 2026-04-27
draft: false
description: "Claude Code から Microsoft Teams を操作する3つの方法を初心者向けに解説。Workflows Webhook（5分セットアップ）、Microsoft 365 Connector（公式・読み取り）、ms-365-mcp-server（投稿+ファイル DL）を難易度順に比較し、2026年5月の Incoming Webhook 廃止にも対応。"
categories: ["ツール/開発環境"]
tags: ["Claude Code", "Microsoft Teams", "MCP", "Microsoft 365", "Webhook", "ms-365-mcp-server", "Anthropic", "Adaptive Card"]
---

「Claude Code から Microsoft Teams にビルド結果を投稿したい」「OneDrive のファイルを Claude に読ませて要約させたい」──こうしたニーズは、AI 駆動の開発フローで日常的に発生します。本記事では、**初心者でも今日から使える 3 つの方法**を、難易度順にセットアップから操作まで解説します。

<!--more-->

## 結論：選択肢の早見表

| 方法 | できること | 難易度 | 認証 | 用途 |
|------|-----------|--------|------|------|
| **Workflows Webhook** | チャネルへの投稿のみ | ★ | 不要 | 通知・ビルド結果投稿 |
| **Microsoft 365 Connector** | 読み取り（チャット/ファイル/メール） | ★★ | SSO | Teams の内容を Claude で要約 |
| **ms-365-mcp-server** | 投稿＋読み取り＋ファイル DL | ★★★ | デバイスコード | フル自動化 |

> **重要なお知らせ**: 旧 "Incoming Webhook" コネクタは **2026 年 5 月 18〜22 日に廃止** されます（既存の Webhook URL も同日以降は停止）。新規導入なら本記事で紹介する **Workflows Webhook**（後継）を使ってください。

---

## 方法 1：Workflows Webhook（5分でできる投稿）

最速で「Claude Code → Teams 投稿」を実現する方法です。Azure AD 設定も認証も不要です。

### ステップ 1：Teams で Workflow を作成

1. 投稿したいチャネル名の右にある「**…**」（その他のオプション）→「**ワークフロー**」をクリック
2. テンプレート一覧から「**Webhook 要求を受信したらチャネルに投稿する**」を選択
   （英語 UI: "Post to a channel when a webhook request is received"）
3. 「次へ」→ チーム名・チャネル名を確認 →「**ワークフローを追加**」
4. 表示された **Webhook URL** をコピー

> **注意**: Webhook URL は一度しか表示されません。ダイアログを閉じる前に必ずコピーして安全な場所（パスワードマネージャーや `.env` など）に保存してください。

### ステップ 2：環境変数に保存

`~/.zshrc` に追記:

```bash
export TEAMS_WEBHOOK_URL="https://prod-XX.japaneast.logic.azure.com:443/workflows/..."
```

シェルを再読み込み:

```bash
source ~/.zshrc
```

### ステップ 3：Claude Code から投稿

Claude Code のセッションで以下のように依頼すれば、curl コマンドを生成・実行してくれます。

```
Teams に「ビルド成功 ✅」とテスト投稿してください
```

実際に実行されるコマンド例:

```bash
curl -X POST -H 'Content-Type: application/json' \
  -d '{
    "type": "message",
    "attachments": [{
      "contentType": "application/vnd.microsoft.card.adaptive",
      "content": {
        "type": "AdaptiveCard",
        "version": "1.4",
        "body": [
          {"type": "TextBlock", "text": "ビルド成功 ✅", "size": "Medium", "weight": "Bolder"}
        ]
      }
    }]
  }' \
  "$TEAMS_WEBHOOK_URL"
```

> Workflows Webhook は **Adaptive Card 形式**を推奨。旧 MessageCard 形式も互換的に動作しますが、ボタンが表示されないなどの制約があります。

### ステップ 4：許可パターンを登録（auto モード対応）

毎回確認を求められないように、`.claude/settings.json` に以下を追加:

```json
{
  "permissions": {
    "allow": [
      "Bash(curl -X POST:*)"
    ]
  }
}
```

### この方法の限界

- **チャネル投稿のみ**（DM 送信不可、ファイル添付不可）
- **読み取り不可**（Teams の内容を Claude に取得させられない）
- **Bot 名・アイコンを変更不可**（"Flow bot" 固定で表示される）

→ 双方向のやり取りが必要なら次の方法へ。

---

## 方法 2：Microsoft 365 Connector for Claude（読み取り特化・公式）

Anthropic 公式の連携機能で、**現在は全 Claude プラン（Free 含む）で利用可能**です。Teams のチャット、SharePoint、OneDrive、Outlook を **読み取り専用**で参照できます。

### 何ができる？

- Teams チャネルの過去のやり取りを Claude に検索・要約させる
- OneDrive/SharePoint のドキュメントを Claude に読ませて分析する
- Outlook のメールを横断検索する

### セットアップ手順

1. **claude.ai にログイン** → 右下の「**Settings**」→「**Connectors**」
2. **Microsoft 365** を検索して「**Connect**」をクリック
3. Microsoft アカウントで OAuth 同意（職場・学校アカウントの場合は管理者承認が必要な場合があります）
4. 接続完了後、Claude Code を再起動すれば Connector が自動的に認識され、自然言語で Microsoft 365 の情報を参照できるようになります

### 組織アカウントの場合の注意

職場・学校アカウントでは、初回接続時に **テナント管理者の同意**が必要になることがあります。同意ダイアログが「管理者の承認が必要」と表示されたら、IT 管理者に Microsoft Entra 管理センターから承認してもらってください。

### Claude Code での使い方

Claude Code 起動後、自然言語で指示するだけ:

```
Teams の "開発" チャネルから昨日の議論をまとめて、
決まったことと次のアクションを箇条書きで出して
```

```
OneDrive の Q1-売上.xlsx を読み込んで、月次推移をグラフ化したい
```

### この方法の限界

- **読み取り専用**（投稿・編集・削除はできない）
- 投稿が必要なら方法 1 か方法 3 と組み合わせる

---

## 方法 3：ms-365-mcp-server（投稿＋読み取り＋ファイル DL）

[Softeria/ms-365-mcp-server](https://github.com/softeria/ms-365-mcp-server) は **200 種類超のツールを提供する MCP サーバー**で、投稿・読み取り・ファイルダウンロードを全部こなせます。

### 前提条件

- **Node.js 20 以上**
- 個人 Microsoft アカウント（@outlook.com 等）または職場/学校アカウント
- Teams/SharePoint を使うなら職場/学校アカウントが必須

### ステップ 1：Claude Code に MCP サーバーを登録

#### 個人アカウントの場合（OneDrive、Outlook、Calendar のみ）

```bash
claude mcp add ms365 -- npx -y @softeria/ms-365-mcp-server
```

#### 職場/学校アカウントの場合（Teams、SharePoint を使うならこちら）

```bash
claude mcp add ms365 -- npx -y @softeria/ms-365-mcp-server --org-mode
```

`--org-mode` フラグを付けることで Teams・SharePoint・オンライン会議関連のツールが有効化されます。

### ステップ 2：初回認証（デバイスコードフロー）

Claude Code を起動し、最初に以下を依頼:

```
ms365 MCP の login ツールを実行して
```

すると以下のような出力が表示されます:

```
To sign in, use a web browser to open the page
https://microsoft.com/devicelogin
and enter the code ABC123XYZ to authenticate.
```

表示された URL（`microsoft.com/devicelogin`）をブラウザで開き、コードを入力します。続いて Microsoft アカウントでサインインして承認すれば認証完了です。

トークンは **OS のキーチェーン** に安全に保存されるため、次回以降は再認証不要です。

> **重要**: Azure AD アプリ登録は **不要**です。組み込みのパブリッククライアントアプリが使われます。本番運用や独自スコープ制御が必要な場合のみ、自分の Azure AD アプリを `MS365_MCP_CLIENT_ID` 環境変数で指定できます。

### ステップ 3：使ってみる

Claude Code のセッションで自然言語で指示:

```
Teams の "general" チャネルに
"Claude Code からの自動投稿テスト" と投稿して
```

```
OneDrive の /Documents/report.xlsx をダウンロードして、
売上シートの合計を計算して
```

```
今週の Outlook 受信メールから、
"請求書" と件名に含むものを一覧表示して
```

### よく使うツール例

`--org-mode` で有効化される代表的なツール:

| ツール | 機能 |
|--------|------|
| `send-channel-message` | Teams チャネルへの投稿 |
| `send-chat-message` | DM・グループチャットへの投稿 |
| `list-channel-messages` | チャネルメッセージ一覧取得 |
| `download-onedrive-file` | OneDrive ファイルのダウンロード |
| `list-sharepoint-sites` | SharePoint サイト一覧 |
| `create-online-meeting` | Teams 会議の作成 |

有効なツールが要求する権限スコープ一覧は `--list-permissions` で確認できます:

```bash
npx @softeria/ms-365-mcp-server --org-mode --list-permissions
```

組織で事前に管理者承認が必要な場合、このコマンドで Graph API スコープを把握してから IT 管理者に依頼するとスムーズです。

### ステップ 4：許可パターンを登録

`.claude/settings.json` に MCP ツールの許可を追加:

```json
{
  "permissions": {
    "allow": [
      "mcp__ms365__send-channel-message",
      "mcp__ms365__list-channel-messages",
      "mcp__ms365__download-onedrive-file"
    ]
  }
}
```

頻繁に使うツールだけ allowlist に入れておくと、auto モードでも止まらず動きます。

---

## ユースケース別おすすめ

### 通知だけしたい（個人開発・CI から呼び出す）

**→ 方法 1：Workflows Webhook**

セットアップ 5 分。`curl` で十分。

### Teams の議論を要約させたい

**→ 方法 2：Microsoft 365 Connector**

公式・無料・読み取り専用で安全。

### 投稿もファイル DL も全部やりたい

**→ 方法 3：ms-365-mcp-server**

組織アカウントで `--org-mode` を使う。Azure AD 設定は **デフォルト不要**。

### ハイブリッド構成（おすすめ）

実は **方法 2 と方法 3 を併用する**のが最強です:

- 読み取りは Microsoft 365 Connector（公式、安全、監査ログあり）
- 投稿は ms-365-mcp-server（書き込みが必要なときだけ）

両方を Claude Code に登録しておけば、Claude が文脈に応じて適切なほうを選びます。

---

## セキュリティのベストプラクティス

### 1. Webhook URL の保護

Webhook URL を `.env` ファイルに書く運用にする場合は、必ず `.gitignore` に追加してリポジトリにコミットしないようにします:

```bash
echo ".env*" >> .gitignore
```

Workflows Webhook URL は **コピー後に再表示できない**ため、紛失したら再生成が必要です。

### 2. 権限の最小化

ms-365-mcp-server の `--org-mode` は便利ですが、Teams 不要なら付けないほうが安全です。`--preset` フラグで機能を絞り込むこともできます:

```bash
npx @softeria/ms-365-mcp-server --preset mail --list-permissions
```

`mail`、`calendar`、`files` などのプリセットが用意されており、必要な機能だけ有効化することで権限スコープを最小化できます。

### 3. 読み取り専用モード

ms-365-mcp-server には `--read-only` フラグがあります。投稿系の事故を防ぎたいときに使えます:

```bash
claude mcp add ms365-readonly -- npx -y @softeria/ms-365-mcp-server --read-only
```

### 4. 監査ログ

Microsoft 365 Connector 経由のアクセスは **すべて Microsoft 365 監査ログに記録**されます。組織管理者は M365 Compliance Center から確認できます。ms-365-mcp-server も Graph API 経由なので同様に記録されます。

---

## トラブルシューティング

### Q. Workflows Webhook で 400 エラー

**よくある原因**: ペイロードの JSON 形式が古い MessageCard のまま

**対処**: Adaptive Card 形式（`type: "message"` + `attachments[]`）に書き換える

### Q. ms-365-mcp-server で「テナント管理者の承認が必要」

**原因**: 組織テナントが管理者承認なしの個人アプリ利用を制限している

**対処**: 管理者に対し、ms-365-mcp-server に組み込まれている Azure AD アプリの ID（GitHub README に記載）の同意を Microsoft Entra 管理センターから付与してもらうか、自前の Azure AD アプリを登録して `MS365_MCP_CLIENT_ID` 環境変数で指定する

### Q. Teams のツールが見えない

**原因**: `--org-mode` フラグが付いていない

**対処**:

```bash
claude mcp remove ms365
claude mcp add ms365 -- npx -y @softeria/ms-365-mcp-server --org-mode
```

### Q. デバイスコードフローでブラウザが開かない

**原因**: ターミナル環境からブラウザを起動できない（リモート SSH など）

**対処**: 表示された URL（`microsoft.com/devicelogin`）を手動でローカル PC のブラウザに貼り付けて、表示されたコードを入力すれば認証できます。

---

## まとめ

Claude Code から Microsoft Teams を操作する方法は、用途別に 3 つに整理できます。



1. **通知だけなら Workflows Webhook**（5分セットアップ）
2. **読み取りは Microsoft 365 Connector**（公式・無料・全プラン）
3. **フル機能は ms-365-mcp-server**（Azure AD 登録不要、デバイスコードで簡単）

旧 Incoming Webhook の廃止が 2026 年 5 月に迫っているため、これから始めるなら **Workflows Webhook** か **MCP サーバー**を選んでください。

最初の一歩としては、まず方法 1 でビルド通知を Teams に流してみる → 慣れたら方法 3 で双方向自動化、の順がおすすめです。

## 関連記事

- [Claude Code Wiki](/blogs/wiki/tools/claude-code/) — Claude Code 全般の概要と機能まとめ
- [MCP（Model Context Protocol）Wiki](/blogs/wiki/concepts/mcp/) — MCP サーバーの仕組みと活用パターン

## 参考リンク

- [ms-365-mcp-server (Softeria) - GitHub](https://github.com/softeria/ms-365-mcp-server)
- [Microsoft 365 connector for Claude - 公式ドキュメント](https://support.claude.com/en/articles/12542951-enable-and-use-the-microsoft-365-connector)
- [Microsoft 365 Connector: Security Guide](https://support.claude.com/en/articles/12684923-microsoft-365-connector-security-guide)
- [Office 365 Connectors retirement - Microsoft 365 Developer Blog](https://devblogs.microsoft.com/microsoft365dev/retirement-of-office-365-connectors-within-microsoft-teams/)
- [Workflows in Microsoft Teams - 公式ガイド](https://support.microsoft.com/en-us/office/post-a-workflow-when-a-webhook-request-is-received-in-microsoft-teams-8ae491c7-0394-4861-ba59-055e33f75498)
- [Connect Claude Code to tools via MCP](https://docs.claude.com/en/docs/claude-code/mcp)
