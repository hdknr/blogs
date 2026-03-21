---
title: "Claude Code Channels で変わる AI 開発ワークフロー：OpenClaw との組み合わせが最適解か"
date: 2026-03-21
lastmod: 2026-03-21
draft: false
source_url: "https://github.com/hdknr/blogs/issues/1#issuecomment-4102565274"
categories: ["AI/LLM"]
tags: ["claude-code", "claude", "agent", "OpenClaw", "MCP"]
---

2026 年 3 月 20 日、Anthropic が Claude Code の新機能「Channels」をリサーチプレビューとしてリリースしました。Telegram や Discord から Claude Code セッションにメッセージを送り、PC 上で開発タスクを実行させることができる機能です。この記事では Claude Code Channels の概要と、OpenClaw と組み合わせた AI 開発ワークフローの可能性について紹介します。

## Claude Code Channels とは

Claude Code Channels は、MCP（Model Context Protocol）サーバーを通じて外部のメッセージングプラットフォームから Claude Code のセッションにイベントをプッシュする仕組みです。従来の「ターミナルの前に座って対話する」同期的なモデルから、**非同期的にどこからでも AI エージェントに指示を出せる**モデルへの転換を実現します。

### 主な特徴

- **双方向チャットブリッジ**: Telegram や Discord からメッセージを送ると、Claude Code が読み取って処理し、同じチャネルに返信を返す
- **ローカル実行**: 開発作業は自分の PC 上で実行される。ファイルアクセスやコマンド実行はすべてローカル
- **MCP ベース**: Anthropic が推進するオープンプロトコル MCP 上に構築
- **プラグイン方式**: Telegram・Discord が公式プラグインとして提供され、カスタムチャンネルの自作も可能

### セットアップの流れ（Telegram の場合）

1. Telegram の BotFather で新しいボットを作成しトークンを取得
2. Claude Code でプラグインをインストール:
   ```
   /plugin install telegram@claude-plugins-official
   ```
3. トークンを設定:
   ```
   /telegram:configure <token>
   ```
4. Channels を有効にして Claude Code を起動:
   ```bash
   claude --channels plugin:telegram@claude-plugins-official
   ```
5. Telegram でボットにメッセージを送りペアリングコードを取得、Claude Code で承認

### 動作要件

- Claude Code v2.1.80 以上
- Bun ランタイム（Node.js では動作しない点に注意）
- claude.ai ログイン認証（API キー認証は未対応）
- Team/Enterprise プランでは管理者による有効化が必要

## OpenClaw とは

OpenClaw はオーストリアの開発者 Peter Steinberger が開発した、オープンソースの自律型 AI エージェントです。2026 年初頭に 72 時間で GitHub スター 60,000 を獲得するなど爆発的に普及しました。

- **ローカル実行**: データが外部に送信されない設計
- **100 以上のスキル**: ファイル操作、ブラウザ操作、メール送信、API 制御など
- **メッセージング連携**: Signal、Telegram、Discord、WhatsApp 経由でチャットボットとして操作可能
- **コンテキスト管理**: 会話をまたいだ記憶保持が可能

## OpenClaw × Claude Code Channels の分業構造

ツイート元の提案する構成が注目に値します:

```
スマホ
  ↓
OpenClaw（記憶 / ナレッジ / コンテキスト管理）
  ↓
Claude Code Channels（ナレッジ資産を活かした開発実行）
```

つまり:

| 役割 | ツール | 比喩 |
|------|--------|------|
| コンテキスト管理・ワークフロー保持 | OpenClaw | 脳 |
| 開発タスクの実行 | Claude Code | 手 |

### この構成のメリット

1. **API コスト最適化**: OpenClaw 側で軽量〜中量のタスクを処理し、本格的な開発だけ Claude Code（Opus）に回すことでコストを抑えられる
2. **スマホからの指示**: 外出先からスマホで OpenClaw に指示 → PC の Claude Code が開発を実行
3. **記憶の分離**: OpenClaw がナレッジとワークフローを保持し、Claude Code は開発実行に集中
4. **認証問題の回避**: OpenClaw から直接 Claude API を呼ぶ際の認証制約を、Channels 経由で迂回できる

### 従来の使い分けとの違い

これまでは:
- 軽量〜中量の自動化 → OpenClaw
- 本格的な開発 → Claude Code

と**別々に**使い分けていたものが、Channels によって**連携した一つのシステム**として機能するようになります。

## セキュリティ上の注意点

Claude Code Channels を使う際のセキュリティ面での注意:

- **allowlist の設定**: ペアリング後すぐに `access policy allowlist` でアクセスを制限する。デフォルトではボットにメッセージを送った誰にでもペアリングコードが返される
- **`--channels` フラグの明示**: `.mcp.json` に設定するだけでは有効にならず、起動時に `--channels` フラグで明示的に指定が必要
- **権限プロンプト**: 不在時に権限プロンプトが出るとセッションが一時停止する。`--dangerously-skip-permissions` は信頼できる環境でのみ使用すること
- **OpenClaw のスキルリスク**: サードパーティの OpenClaw スキルにはデータ流出やプロンプトインジェクションのリスクが報告されている

## まとめ

Claude Code Channels は、AI コーディングエージェントを「ターミナルに縛られた存在」から「どこからでもアクセスできるサービス」へと進化させる機能です。OpenClaw のようなコンテキスト管理ツールと組み合わせることで、AI の「脳」と「手」を分離した効率的な開発ワークフローが実現できる可能性があります。まだリサーチプレビュー段階ですが、AI エージェント設計の新しい方向性を示す注目の機能です。
