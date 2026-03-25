---
title: "Claude Codeで「専門家チーム」を構築する：カスタムエージェントとCoworkの活用法"
date: 2026-03-25
lastmod: 2026-03-25
draft: false
categories: ["AI/LLM"]
tags: ["claude-code", "claude", "anthropic", "agent", "mcp"]
---

[前回の記事](/posts/2026-03-23-notebooklm-20-experts/)では、NotebookLM を使って「20人の専門家チーム」を構築する方法を紹介しました。この記事では、同じ考え方を Claude Code や Cowork で実現する方法を解説します。

## NotebookLM と Claude Code の発想の違い

NotebookLM は「入れた資料だけを根拠に回答する」ことが強みです。テーマごとにノートブックを分けることで、各ノートブックが「専門家」として機能します。

Claude Code でも同じアプローチが取れます。さらに、**コード実行・ファイル編集・外部ツール連携**ができるため、「相談する」だけでなく「調査して、コードを書いて、PR を作成する」ところまで一気通貫で任せられます。

| 観点 | NotebookLM | Claude Code |
|---|---|---|
| 専門家の定義 | ノートブック + ソース | `.claude/agents/` + ナレッジ |
| 知識の投入 | PDF / Web / Fast Research | MCP / ローカルファイル / WebSearch |
| 同時相談 | 手動で切替 | Cowork / Agent Teams で並行実行 |
| 引用元表示 | 自動リンク | ファイルパス・行番号 |
| 強み | 非技術者でも簡単 | コード実行・ファイル編集が可能 |

## 方法1: カスタムエージェント（`.claude/agents/`）

最もシンプルで NotebookLM の「専門家ノート」に直接対応する方法です。

### カスタムエージェントの仕組み

`.claude/agents/` ディレクトリに Markdown ファイルを置くだけで、専門エージェントが定義できます。各ファイルにはそのドメインの専門知識・指示・参照先を書きます。

```text
.claude/agents/
├── marketing-expert.md      # マーケティング専門家
├── legal-advisor.md          # 法務アドバイザー
├── seo-advisor.md            # SEO アドバイザー
└── fact-checker.md           # ファクトチェッカー
```

### エージェント定義ファイルの書き方

Markdown ファイルの先頭に YAML フロントマターでメタ情報を定義し、本文にシステムプロンプトを書きます。詳細は [公式ドキュメント](https://code.claude.com/docs/en/sub-agents) を参照してください。

```markdown
---
name: マーケティングコンサルタント
description: マーケティング戦略、SNS運用、競合分析の専門家
tools: [WebSearch, Read, Grep, Glob]
---

あなたはマーケティングの専門家です。
以下のナレッジに基づいて回答してください。

## 参照ソース
- docs/marketing/ 配下のドキュメント
- 競合分析レポート: docs/competitors/

## 専門領域
- デジタルマーケティング戦略
- SNS運用・コンテンツ戦略
- KPI設計と効果測定

## 回答のルール
- 根拠を示すこと（参照ファイル名・行番号）
- 実行可能なアクションアイテムを含めること
```

**ポイント:**

- `tools` で使えるツールを制限できる（読み取り専用にもできる）
- ユーザーレベル（`~/.claude/agents/`）に置けば全プロジェクトで共有できる
- プロジェクトレベル（`.claude/agents/`）に置けばチームで共有できる

### カスタムエージェントの呼び出し方

Claude Code はタスクの内容から自動的にマッチするエージェントを選択します。Agent ツールの `subagent_type` にエージェント名を指定して明示的に呼び出すこともできます。

```bash
# Claude Code の対話中に、Agent ツールで明示的に呼び出す例
# subagent_type: "marketing-expert" を指定

# CLI から直接指定する場合
claude "マーケティング戦略を分析して" --agent marketing-expert
```

また、別の Claude Code セッション（メインの会話）から `Agent` ツールを使ってサブエージェントとして起動することも可能です。この場合、サブエージェントは独自のコンテキストウィンドウで動作し、結果だけがメインに返されます。

## 方法2: Cowork / Agent Teams — 複数の専門家を同時に動かす

NotebookLM ではノートブックを手動で切り替える必要がありましたが、Claude Code の Agent Teams では**複数の専門家を並行して動かせます**。

### Agent Teams の構成例

```text
チームリード（メインの Claude Code セッション）
├── marketing-agent  — マーケティング戦略を調査
├── legal-agent      — 法的リスクを分析
├── finance-agent    — 財務面を評価
└── tech-agent       — 技術的実現可能性を調査
```

例えば「新サービスの立ち上げ計画」のような複合的な課題に対して、4人の専門家が同時に調査し、チームリードが結果を統合します。Agent Teams の詳細は [公式ドキュメント](https://code.claude.com/docs/en/agent-teams) を参照してください（現在は実験的機能）。

### Agent Teams の実績：10万行の C コンパイラ構築

Anthropic のエンジニアリングチームは、16のエージェントを並行して稼働させ、約2,000セッションで10万行の Rust 製 C コンパイラを構築しました（[事例記事](https://www.anthropic.com/engineering/building-c-compiler)）。

### Claude Cowork（デスクトップ版）

Claude Code がターミナルベースの開発者向けツールであるのに対し、[Cowork](https://claude.com/product/cowork) はデスクトップ UI のナレッジワーカー向けツールです。ローカルファイルやアプリケーションに接続し、マルチステップのタスクを実行できます。Cowork の基本的な使い方は[こちらの記事](/posts/2026-03-16-claude-cowork-starter-pack/)も参考になります。

## 方法3: MCP サーバーでナレッジを接続

NotebookLM の強みは「入れた資料だけを根拠に回答する」点でした。Claude Code で同等のことを実現するのが、**MCP（Model Context Protocol）サーバーによる外部ナレッジの接続**です。

### .mcp.json の設定例

`.mcp.json` でプロジェクト単位の MCP サーバーを定義できます。以下は構成の例です（実際の MCP サーバーの構築方法は [公式ドキュメント](https://code.claude.com/docs/en/mcp) を参照）。

```json
{
  "mcpServers": {
    "knowledge": {
      "command": "node",
      "args": ["./mcp-servers/knowledge/index.js"],
      "env": {
        "DOCS_DIR": "./docs"
      }
    }
  }
}
```

### MCP サーバーの活用パターン

- **Notion MCP サーバー**: 社内ドキュメントを直接参照
- **データベース MCP**: 業務データに基づいた回答
- **カスタム MCP**: 自社のナレッジベースを検索可能にする

エージェント定義で `tools: [mcp__knowledge__search]` のように接続先を指定すれば、そのエージェントは特定のナレッジソースだけを参照して回答します。MCP の実践例として、[freee MCP × Claude Code の連携記事](/posts/2026-03-10-freee-mcp-claude-code/)も参考になります。

## 実践例: Hugo ブログに Claude Code 専門家チームを構築する

この技術ブログ自体を例に、どんな専門家エージェントが有用かを考えてみます。

### テクニカルライター エージェント

```markdown
---
name: テクニカルライター
description: ブログ記事の構成・読みやすさを改善する編集者
tools: [Read, Grep, Glob, WebSearch]
---

あなたはテクニカルライティングの専門家です。
以下の観点で記事をレビューしてください:

- 見出しの階層構造が適切か
- 冒頭で記事の価値が伝わるか
- コード例にシンタックスハイライトが付いているか
- 専門用語に適切な説明があるか
```

### SEO アドバイザー エージェント

```markdown
---
name: SEO アドバイザー
description: ブログ記事のタイトル・タグ・メタデータを最適化する
tools: [Read, Grep, Glob, WebSearch]
---

あなたは SEO の専門家です。
Hugo ブログの記事に対して以下を提案してください:

- 検索されやすいタイトルの改善案
- 適切なタグとカテゴリの提案
- メタディスクリプションの作成
```

### トレンドリサーチャー エージェント

```markdown
---
name: トレンドリサーチャー
description: 最新の技術動向を調査してブログ記事のネタを提案する
tools: [WebSearch, Read]
---

あなたは技術トレンドのリサーチャーです。
以下の分野の最新動向を調査し、ブログ記事のネタを提案してください:

- AI/LLM の新機能・新サービス
- 開発ツールのアップデート
- セキュリティの最新脅威と対策
```

## NotebookLM から Claude Code に移行するメリット

1. **「調べる」から「実行する」へ**: NotebookLM は情報提供までですが、Claude Code は調査結果をもとにコードを書き、ファイルを編集し、PR を作成するところまで自動化できる
2. **バージョン管理**: エージェント定義を `.claude/agents/` に置けば Git で管理でき、チームで共有できる
3. **並行実行**: Agent Teams で複数の専門家を同時に動かし、結果を統合できる
4. **ツール連携**: MCP でデータベース、API、社内ツールに直接接続できる

## まとめ

NotebookLM の「テーマごとにノートブックを分けて専門家を作る」というアイデアは、Claude Code ではカスタムエージェント（`.claude/agents/`）として実装できます。さらに Cowork / Agent Teams で並行実行、MCP でナレッジ接続と、より強力な専門家チームを構築できます。

まずは1つのエージェント定義ファイルを作るところから始めてみてください。[AI チーフ・オブ・スタッフの構築記事](/posts/2026-03-13-claude-code-chief-of-staff/)も、実践の参考になります。
