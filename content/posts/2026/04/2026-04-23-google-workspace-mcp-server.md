---
title: "Google Workspace 公式 MCP サーバー登場 — Gmail・Drive・Calendar を AI エージェントから直接操作"
date: 2026-04-23
lastmod: 2026-04-23
draft: false
source_url: "https://github.com/hdknr/blogs/issues/1#issuecomment-4304029563"
description: "Google Cloud Next 2026 で発表された Workspace 公式 MCP サーバーの対応サービスと設定手順を解説。Claude Desktop や Gemini CLI から Gmail・Drive・Calendar を自然言語で操作できる。"
categories: ["AI/LLM"]
tags: ["MCP", "Google Workspace", "Gmail", "Claude", "Gemini CLI"]
---

Google Cloud Next 2026 で、Google Workspace の**公式 MCP サーバー**がデベロッパープレビューとして発表された。Gmail・Drive・Calendar・Chat などの Workspace データを、Claude・Gemini CLI・IDE などの AI アプリから Model Context Protocol（MCP）経由で直接操作できるようになる。

## これまでの課題

Workspace のデータを AI エージェントと連携させたい場合、これまでは以下の障壁があった。

- 公式のサポートがなく、サードパーティ製コネクターに頼るしかなかった
- OAuth フローの実装が複雑で、開発コストが高かった
- エージェントからのアクセス権限管理が整備されていなかった

公式 MCP サーバーはこれらの壁をまとめて解消する。

## 対応サービスと提供ツール数

| サービス | ツール数 | 主な操作 |
|----------|---------|---------|
| Gmail | 10 | メール検索・下書き作成・送信 |
| Drive | 7 | ファイル取得・アップロード・検索 |
| Calendar | 8 | 予定作成・一覧取得・更新 |
| People | 3 | 連絡先の参照 |
| Chat | 2 | メッセージ確認・送信 |

## 対応 AI アプリ

- **Claude** (Enterprise / Pro / Max / Team プラン)
- **Gemini CLI**
- **VS Code** などの対応 IDE

MCP 標準に準拠しているため、今後 MCP 対応のアプリ・フレームワークはすべて利用できる見込み。

## Workspace CLI と gws mcp

公式 MCP サーバーの発表と合わせ、Workspace CLI（`googleworkspace/cli`）も近日一般公開予定と Google より告知されている。

> **注**: `googleworkspace/cli` リポジトリの README には "This is not an officially supported Google product" と明記されており、MCP サーバー本体（Workspace MCP Server）とは異なりサポート対象外扱いとなっている。

CLI のコマンド名は `gws` で、MCP サーバーモードは以下のように起動する。

```bash
gws mcp
```

- 「人間にも AI エージェントにも使える、Workspace のための 1 つの CLI」と位置づけ
- 構造化 JSON 出力によるエージェント向けワークフローを標準サポート
- Gmail・Drive・Docs・Calendar・Sheets 向けに **100 以上のエージェントスキル**を同梱済み

## Claude から使う設定例

`claude_desktop_config.json` に以下を追記するだけで、Claude Desktop から Workspace 操作が可能になる。

```json
{
  "mcpServers": {
    "google-workspace": {
      "command": "gws",
      "args": ["mcp"]
    }
  }
}
```

設定後は Claude から「先週のメールを要約して」「明日の会議を確認して」などの自然言語指示で Workspace を操作できる。

## 公式ドキュメント

- [Configure the Google Workspace MCP servers](https://developers.google.com/workspace/guides/configure-mcp-servers)
- [Configure the Calendar MCP server](https://developers.google.com/workspace/calendar/api/guides/configure-mcp-server)
- [Announcing official MCP support for Google services](https://cloud.google.com/blog/products/ai-machine-learning/announcing-official-mcp-support-for-google-services)
- [10 more announcements for Workspace at Cloud Next 2026](https://workspace.google.com/blog/product-announcements/10-more-announcements-workspace-at-next-2026)

## まとめ

Google Workspace 公式 MCP サーバーの登場により、「Workspace データを使いたいが連携が難しい」という問題が解消される。現在はデベロッパープレビュー段階だが、Claude や Gemini CLI との組み合わせで業務自動化の幅が大きく広がる。公式 CLI の一般公開と合わせて、エージェント活用の実践が一気に加速しそうだ。
