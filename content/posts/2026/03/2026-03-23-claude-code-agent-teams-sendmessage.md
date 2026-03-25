---
title: "Claude Code Agent Teams: セッション間でメッセージをやり取りできるマルチエージェント機能"
date: 2026-03-23
lastmod: 2026-03-23
draft: false
source_url: "https://github.com/hdknr/blogs/issues/1#issuecomment-4113381313"
categories: ["AI/LLM"]
tags: ["claude-code", "claude", "anthropic", "agent", "マルチエージェント"]
---

Claude Code に「Agent Teams」機能が追加されました。複数のセッションがメッセージをやり取りしながら協調作業できる機能です。

従来のサブエージェントは親セッションに結果を返すだけでしたが、Agent Teams ではエージェント同士が直接コミュニケーションを取りながらタスクを進められます。

## Agent Teams とは

Agent Teams は Claude Code v2.1.32 以降で利用できる実験的機能です。1つのセッションがチームリーダーとなり、複数のチームメイト（それぞれ独立した Claude Code インスタンス）を起動して並列に作業を進めます。

各チームメイトは独自のコンテキストウィンドウを持ち、共有タスクリストを通じて自律的に連携します。

## サブエージェントとの違い

| 比較項目 | サブエージェント | Agent Teams |
|---|---|---|
| コンテキスト | 独自のコンテキスト、結果を呼び出し元に返却 | 独自のコンテキスト、完全に独立 |
| コミュニケーション | 親エージェントへの一方向のみ | チームメイト同士で直接メッセージ送受信 |
| 調整方法 | 親エージェントが全体を管理 | 共有タスクリストで自己調整 |
| 適した用途 | 結果だけが必要な集中タスク | 議論・協調が必要な複雑な作業 |
| トークンコスト | 低い（結果が親コンテキストに要約される） | 高い（各チームメイトが個別の Claude インスタンス） |

## SendMessage によるエージェント間通信

Agent Teams の中核となるのが `SendMessage` ツールです。2つの通信方式が用意されています。

- **directed message**: 特定のチームメイトにメッセージを送信
- **broadcast**: 全チームメイトにメッセージを一斉送信

メッセージは各チームメイトの受信ボックスに JSON として追記されます。受信ボックスのパスは `~/.claude/teams/<project>/inboxes/<name>.json` です。メッセージは次のターンで読み取られ、会話履歴に新しいユーザーターンとして注入されます。

## 有効化と使い方

Agent Teams はデフォルトで無効です。`~/.claude/settings.json` で環境変数を設定して有効化します。

```json
{
  "env": {
    "CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS": "1"
  }
}
```

有効化後は、自然言語でチーム構成を指示するだけで起動できます。

```text
CLI ツールの設計を検討したい。UX担当、技術アーキテクチャ担当、
批判的レビュー担当の3人チームを作って、それぞれの視点から探ってほしい。
```

Claude がチームを作成し、タスクを割り振り、各チームメイトを起動します。

## 表示モード

チームメイトの作業状況を確認する方法は2つあります。

- **In-process モード**: メインのターミナル内で動作。`Shift+Down` でチームメイトを順に切り替え
- **Split panes モード**: tmux または iTerm2 を使い、各チームメイトが独立したペインで動作

```json
{
  "teammateMode": "tmux"
}
```

## 効果的なユースケース

- **リサーチ・レビュー**: 複数のチームメイトが問題の異なる側面を同時に調査し、発見を共有・検証
- **クロスレイヤー開発**: フロントエンド、バックエンド、テストにまたがる変更をそれぞれ別のチームメイトが担当
- **デバッグ**: 複数の仮説を並行して検証し、素早く原因を特定

## 注意点

- Agent Teams は実験的機能であり、セッション再開時にチームメイトの状態が復元されないなどの既知の制限がある
- 各チームメイトが独立した Claude インスタンスのため、トークン消費量が大幅に増える
- 順次処理が必要なタスクや同一ファイルの編集が多い場合は、単一セッションやサブエージェントの方が適している
- メッセージは各チームメイトのコンテキストウィンドウに永続的に注入されるため、過度な通信はコンテキストを圧迫する

## 複数 PC 間での利用について

Agent Teams の通信はローカルファイルシステムベース（`~/.claude/teams/` 配下の JSON ファイル）のため、異なる PC 間では動作しません。例えば Mac Studio と MacBook でそれぞれ Claude Code を起動しても、チームメイトとして連携させることはできません。

### 検討した選択肢と課題

**SSH + Agent Teams（1台に集約）**

MacBook から Mac Studio に SSH して Agent Teams を動かす方法です。追加インフラ不要ですぐ始められますが、全チームメイトが Mac Studio 上で動くため CPU リソースの分散にはなりません。Claude API 呼び出し自体は Anthropic のサーバー側で処理されるため軽量ですが、ビルドやテスト実行などローカルで走るタスクが多い場合は1台に負荷が集中します。

**SSH 経由のサブエージェント（リモート操作）**

Mac Studio の Claude Code からサブエージェントが `ssh macbook "command"` で MacBook を操作する構成です。技術的には動きますが、Bash 呼び出しごとに SSH 接続が必要になり、Read/Edit/Glob 等の専用ツールが使えないため実用性は低いです。

**2台で独立して Claude Code を起動**

各マシンで Claude Code を動かせば CPU は分散できますが、Agent Teams のピアツーピア通信が使えないため、タスク調整は人手か Git 同期（push/pull）に頼ることになります。

### 自作 MCP チャットサーバーという選択肢

Channels の実体は MCP サーバーです。つまり、Telegram や Discord に頼らなくても、**LAN 内で動く自前のチャットサーバーを MCP で構築すれば、外部サービスを経由せずに複数 Mac 間を繋げます**。

```
Mac Studio: Claude Code ← stdio → 自作 MCP チャットサーバー ← WebSocket → LAN
MacBook: ブラウザで http://macstudio:3000 にアクセス
```

Channels の双方向通信は、以下の2つの MCP の仕組みで実現されています。

1. **ユーザー → Claude（通知 / Push）**: MCP サーバーが `notifications/claude/channel` イベントを発行し、Claude Code セッションにメッセージを注入
2. **Claude → ユーザー（ツール呼び出し）**: MCP サーバーに定義した `reply` ツールを Claude が呼び出し、WebSocket 経由でチャット UI に返信

実装には公式 MCP SDK（Python の `mcp` パッケージ、または Node.js の `@modelcontextprotocol/sdk`）を使用します。Web サーバー部分は FastAPI + WebSocket や Express + Socket.io で構築できます。

**Telegram Bot と比較した利点:**

- LAN 内完結で外部サービスに依存しない
- プライベートなコードや情報が外部を通らない
- レイテンシが低い

**注意点:**

- Channels 機能は research preview 段階のため、`--channels` フラグで起動できるのは公式プラグインのみという制限がバージョンによってある可能性がある
- ただし、汎用的な MCP の通知 + ツールを使った独自ブリッジは制限に関わらず構築可能

### まとめ: 複数 PC 連携の選択肢

| 構成 | 手軽さ | LAN 完結 | 向いているケース |
|---|---|---|---|
| SSH + Agent Teams | ★★★ | ○ | ターミナル操作に慣れている場合 |
| Telegram Bot + Channels | ★★★ | × | スマホからも操作したい場合 |
| 自作 MCP チャットサーバー | ★★ | ○ | 外部サービスを避けたい・カスタマイズしたい場合 |

「2台の Claude Code が自律的に協調する」という理想にはまだ届いていませんが、MCP ベースの自作サーバーであれば、それに近い体験を LAN 内で実現できます。

## Channels 機能の対応プラットフォーム

前述の Channels 機能（v2.1.80〜）について、対応プラットフォームの詳細を補足します。Channels は MCP サーバーとして動作し、外部メッセージングプラットフォームと稼働中の Claude Code セッションを双方向で接続する仕組みです。

### 公式対応プラットフォーム（2026年3月時点）

| プラットフォーム | 説明 |
|---|---|
| **Telegram** | Bot 経由で Claude Code にメッセージ送信・返信受信 |
| **Discord** | Bot 経由で同様の双方向通信 |
| **iMessage** | research preview に含まれている |
| **Fakechat** | localhost で動作するデモ用チャット UI（テスト・検証用） |

### 動作の流れ

1. メッセージングアプリの Bot にメッセージを送信
2. MCP サーバーがそのメッセージを稼働中の Claude Code セッションに転送
3. Claude がローカル環境（ファイルシステム、git、MCP ツール等）にフルアクセスした状態で処理
4. 結果を同じチャネル経由で返信

例えば、スマホの Telegram から「テスト実行して」と送れば、自宅の Mac 上の Claude Code がテストを実行して結果を Telegram に返してくれます。

### 要件

- Claude Code v2.1.80 以降
- Bun ランタイム
- claude.ai ログイン（API キー認証は未対応）

プラグインアーキテクチャで設計されており、Slack や WhatsApp など追加プラットフォームへの拡張が見込まれています。

### 複数 Mac での活用例

前述の通り、複数 PC 間での Agent Teams 直接連携はできませんが、Channels を活用すれば以下のような運用が可能です。

```
Mac Studio: Claude Code + Agent Teams（メイン開発環境）
    ↕ Telegram Bot (Channels)
MacBook / スマホ: Telegram からタスク指示・結果確認
```

ターミナルで直接操作したい場合は、MacBook から Mac Studio に SSH して Claude Code を操作する方法もあります。

```bash
# MacBook から Mac Studio に接続
ssh macstudio
claude  # Mac Studio 上で Agent Teams を起動
```

## まとめ

Agent Teams は、複数の Claude Code セッションが対等な立場でコミュニケーションしながら協調作業を行える機能です。従来のサブエージェントモデル（親→子の一方向）から、ピアツーピアのマルチエージェントモデルへの進化と言えます。

大規模な調査やマルチレイヤーにまたがる開発タスクで、その真価を発揮します。

## 参考リンク

- [公式ドキュメント: Orchestrate teams of Claude Code sessions](https://code.claude.com/docs/en/agent-teams)
- [公式ドキュメント: Push events into a running session with channels](https://code.claude.com/docs/en/channels)
