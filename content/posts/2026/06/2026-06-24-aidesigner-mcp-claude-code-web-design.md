---
title: "AIDesigner MCP：気に入ったWebサイトのデザインをClaude Codeで数秒で解析・再現する"
date: 2026-06-24
lastmod: 2026-06-24
slug: "aidesigner-mcp-claude-code-web-design"
draft: false
source_url: "https://github.com/hdknr/blogs/issues/1#issuecomment-4785283983"
description: "WebサイトのURLを渡すだけでHTML/CSSを自律解析してカラー・フォント・コンポーネントをコード化するClaude Code用MCPサーバー「AIDesigner」の使い方と活用シナリオを解説します。"
categories: ["AI/LLM"]
tags: ["claude-code", "mcp", "UI設計", "フロントエンド", "デザイン自動化", "typescript", "プロトタイピング"]
---

Webデザインのプロトタイピングに革命をもたらすClaude Code専用のMCP「AIDesigner」が話題になっています。気に入ったWebサイトのURLを渡すだけで動作します。デザイン構造を数秒で解析し、コードとして出力できます。

## AIDesigner MCPとは

**AIDesigner**（[bacoco/AiDesigner](https://github.com/bacoco/AiDesigner)）は、WebサイトのHTML/CSSを自律的に解析し、以下の要素を自動で抽出してコード化するModel Context Protocol（MCP）サーバーです。

- 色（カラーパレット）
- フォント
- レイアウト構成
- コンポーネント（ボタン、カード、ナビゲーションなど）

TypeScriptで実装されており、Claude Code、Cursor、VS CodeなどのAIアシスタントと統合して使用できます。

## Webサイトデザインの自動解析と再現

### 優れたUIの構造を瞬時に移植

ゼロからUIを組み上げる代わりに、参考にしたいデザインのURLを渡すだけで、そのデザインの骨格をクリーンなコードとして手に入れられます。

### コンポーネントの自動抽出

ClaudeがターゲットサイトのHTML/CSSを解析し、個々のコンポーネントを正確に識別してコード化します。ボタン一つひとつの角丸・シャドウ・カラーから、グリッドやフレックスのレイアウト構成まで、自動で取り出せます。

### 自由なリミックス

再現されたクリーンなコードをベースに、自社のブランドカラーや独自のスタイルを重ねるだけで、オリジナルデザインが完成します。

## Claude Code + AIDesigner MCP の実際の動作フロー

[デモ動画（@Hyde_ai3）](https://x.com/Hyde_ai3/status/2068910620318253472)で公開された56秒の映像では、以下の流れで動作することが確認できます。

1. ターミナルでClaude Codeに対し「`aidesigner-mcp`を使って対象サイトをクローンして」と指示
2. MCPが対象サイトのHTML/CSSを自律的に解析し、色やコンポーネントのデータを抽出
3. Browserbase・Linear風UI・Posthog風SaaSランディングページなどが、オリジナルと遜色ないクオリティで再現

## Claude Codeでの使い方

AIDesignerはMCPサーバーとして動作するため、Claude Codeの設定ファイルに追加するだけで利用できます。

```bash
# リポジトリをクローン
git clone https://github.com/bacoco/AiDesigner.git
cd AiDesigner

# 依存関係のインストール
npm install

# ビルド
npm run build
```

Claude CodeのMCP設定（`~/.claude/settings.json` やプロジェクトの `.claude/settings.json`）に追加します。

```json
{
  "mcpServers": {
    "aidesigner": {
      "command": "node",
      "args": ["/path/to/AiDesigner/dist/index.js"]
    }
  }
}
```

設定後、Claude Codeのセッションで次のように指示するだけです。

```text
aidesigner-mcpを使って https://example.com のデザインをクローンして
```

## AIDesigner MCPを使ったフロントエンド開発ワークフローの変化

AIDesignerが示すワークフローは、デザイン制作の考え方を根本から変えます。

従来は2つの手順が必要でした。参考デザインを見ながら手作業でコードを書き起こすか、Figmaなどで再現してからエンジニアに渡すかです。

AIDesignerを使えば、**「気に入ったUIの構造をAIに素早くインポートさせ、人間はその上に乗せる独自の体験やカスタマイズに集中する」** という役割分担が実現します。

| 作業 | 従来 | AIDesigner使用後 |
|------|------|-----------------|
| デザイン解析 | 手作業・目視 | 自動（数秒） |
| コンポーネント抽出 | 手作業でコーディング | 自動生成 |
| カスタマイズ | 全体を書き直す | 差分だけ修正 |

## まとめ

AIDesigner MCPは、フロントエンド開発やデザインプロトタイピングの初期プロセスを劇的に効率化する可能性を持ったツールです。特に「良いデザインを見つけて、それをベースにカスタマイズしたい」という場面で力を発揮します。Claude Codeへの導入は数ステップで完了するため、フロントエンドエンジニアだけでなく、デザイナーがプロトタイプを素早く検証したい場面にも活用できます。

Claude CodeのMCPエコシステムが広がる中、こうした実用的なツールがどんどん登場しているのは非常に興味深い動向です。

- GitHubリポジトリ: [bacoco/AiDesigner](https://github.com/bacoco/AiDesigner)
- オリジナルのデモツイート: [@Hyde_ai3](https://x.com/Hyde_ai3/status/2068910620318253472)
