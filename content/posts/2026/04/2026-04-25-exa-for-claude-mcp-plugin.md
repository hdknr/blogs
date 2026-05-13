---
title: "Exa for Claude — Web・論文・企業情報を標準検索より高速・高精度に扱う MCP プラグイン"
date: 2026-04-25
lastmod: 2026-04-27
draft: false
source_url: "https://github.com/hdknr/blogs/issues/1#issuecomment-4324637258"
description: "Claude に本格的なニューラル検索を付与する MCP サーバー「Exa」の使い方を解説。企業情報・LinkedIn・コード検索など多様なツールを Claude Desktop と Claude Code で利用する方法を紹介。"
categories: ["AI/LLM"]
tags: ["Claude", "MCP", "Exa", "検索", "Claude Code", "ニューラル検索", "AI エージェント"]
---

Claude に本格的な検索能力を付与する MCP サーバー「Exa for Claude」が注目を集めている。Web 検索・ドキュメント・企業/人物情報など多様なソースに対応し、標準の `web_search` より高速・高精度とされる。Claude Desktop や Claude Code を使う開発者向けに、導入手順と活用例をまとめる。

## Exa とは

[Exa](https://exa.ai) は「将来の検索」を構築するために設立された AI 研究ラボで、ニューラル検索エンジンを提供している。キーワードマッチングではなく意味的類似性を軸にした検索で、AI エージェントが使うことを前提に設計されている。

[exa-labs/exa-mcp-server](https://github.com/exa-labs/exa-mcp-server)（GitHub スター 4,300 超）として OSS 公開されており、Claude・Cursor・VS Code などの MCP 対応ツールから利用できる。

## 提供される検索ツール

Exa MCP サーバーが提供する主なツールは以下の通り。

| ツール | 状態 | 用途 |
|---|---|---|
| `web_search_exa` | 現行 | リアルタイム Web 検索 |
| `web_search_advanced_exa` | 現行 | 高度な Web 検索（カテゴリ・日付範囲・ドメイン指定など） |
| `company_research_exa` | Deprecated | 企業サイトをクロールして詳細情報を取得 |
| `linkedin_search_exa` | Deprecated | LinkedIn での企業・人物検索 |
| `people_search_exa` | Deprecated | 人物情報検索 |
| `crawling_exa` | Deprecated | 指定 URL からコンテンツを抽出（→ `web_fetch_exa` へ移行） |
| `get_code_context_exa` | Deprecated | コードコンテキストの取得（→ `web_search_exa` へ移行） |
| `deep_researcher_start` / `deep_researcher_check` | Deprecated | 非同期ディープリサーチ |

`web_search_advanced_exa` では `category` パラメータで論文・ニュース・コードなど用途別に絞り込める。Deprecated ツールは現在も動作するが、将来的に `web_search_advanced_exa` に統合される方向で整理が進んでいる。

## 標準 web_search との違い

Claude Desktop には組み込みの `web_search` ツールがあるが、Exa MCP には明確な優位点がある。

**標準 web_search**
- 汎用的なウェブ検索
- 結果の精度・鮮度はやや平凡

**Exa MCP**
- ニューラル検索による意味的マッチング
- 用途別ツールを使い分けることで精度向上（論文・企業・コードなど）
- 数時間〜数日以内の最新ドキュメントも取得
- GitHub・Stack Overflow・公式ドキュメントからの実際のコード例を重視
- `deep_researcher_start` / `deep_researcher_check` で複数ステップのリサーチを非同期実行

Claude Code での開発・調査ワークフローにおいて、ライブラリのドキュメント取得、競合調査、人物・企業リサーチなど幅広い場面で精度向上が期待できる。

## 導入方法

まず [exa.ai](https://exa.ai) でアカウントを作成し API キーを発行する。その後、以下のいずれかの方法で MCP サーバーを追加する。

### Claude Desktop（ネイティブコネクタ）

最も簡単な方法は Claude Desktop の「コネクタ」機能を使う方法だ。設定ファイルやターミナルコマンドが不要で、GUI から追加できる。

1. Claude Desktop を開く
2. 「+」（コネクタを追加）をクリック
3. Exa を検索して追加
4. API キーを入力

### claude_desktop_config.json で手動設定

```json
{
  "mcpServers": {
    "exa": {
      "command": "npx",
      "args": ["-y", "exa-mcp-server"],
      "env": {
        "EXA_API_KEY": "your-api-key-here"
      }
    }
  }
}
```

特定のツールのみ有効にする場合は `args` に `--tools` オプションを追加する。

```json
"args": ["-y", "exa-mcp-server", "--tools=web_search_exa,web_search_advanced_exa"]
```

### Claude Code（CLI）

Claude Code では HTTP トランスポート方式で追加するのが現在の推奨だ。

```bash
claude mcp add --transport http exa https://mcp.exa.ai/mcp
```

## 使用例

Claude Code で企業調査や技術調査を行う際の例。

```text
# 最新ライブラリドキュメントの取得
「React 19 の use() フックの使い方は?」
→ web_search_exa で最新ドキュメントを検索

# 学術論文サーベイ
「RAG の最新研究をまとめてください」
→ web_search_advanced_exa（category: "research paper"）で横断検索

# 企業調査
「○○社のプロダクト戦略を調べてください」
→ company_research_exa で公式サイトをクロール

# 競合分析
「○○というサービスに近い製品を教えてください」
→ web_search_advanced_exa で類似サービスを検索
```

## まとめ

Exa for Claude は、Claude Code 時代における「調べる」行為の質を大きく底上げするツールだ。単なる Web 検索の強化ではなく、企業・人物・コードといった専門ドメインに特化したツール群を持つ点が特徴的。Claude Desktop のコネクタ機能を使えば設定ファイルを書かずに導入できるため、Claude Desktop や Claude Code をメインに使っている開発者は一度試してみる価値がある。
