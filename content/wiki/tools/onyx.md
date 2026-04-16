---
title: "Onyx（旧 Danswer）"
description: "MIT ライセンスのオープンソース AI プラットフォーム。RAG・AIエージェント・50以上のコネクタを備え、セルフホストで社内ナレッジ検索を実現"
date: 2026-04-16
lastmod: 2026-04-16
aliases: ["Danswer", "onyx"]
related_posts:
  - "/posts/2026/04/onyx-open-source-ai-platform/"
tags: ["RAG", "AIエージェント", "オープンソース", "セルフホスト", "Docker"]
---

## 概要

旧称 Danswer から改名されたオープンソースの企業向け AI アシスタント＆検索プラットフォーム。Slack・GitHub・Confluence・Google Drive など 50 以上のコネクタで社内ナレッジを統合し、自然言語で検索・質問できる。GitHub スター数 22,000 超。

- **ライセンス**: Community Edition (CE) は MIT ライセンスで無料
- **GitHub**: [onyx-dot-app/onyx](https://github.com/onyx-dot-app/onyx)

## 主な機能

| 機能 | 内容 |
|------|------|
| ハイブリッド検索 | ベクトル検索 + キーワード検索の組み合わせ |
| Agentic RAG | エージェントが自律的に多段階検索 |
| Deep Research | 複数ステップのリサーチでレポート生成 |
| カスタムエージェント | 独自の指示・知識・アクションを持つエージェント |
| 50 以上のコネクタ | Slack・GitHub・Notion・Jira・Linear など |
| MCP 対応 | MCP 経由のカスタムコネクタも可 |

## セルフホスト手順

Docker と Docker Compose があれば数分でデプロイ可能:

```bash
curl -fsSL https://raw.githubusercontent.com/onyx-dot-app/onyx/main/deployment/docker_compose/install.sh > install.sh
chmod +x install.sh
./install.sh
```

## 対応 LLM

クラウド LLM（OpenAI・Anthropic・Gemini）とローカル LLM（Ollama・vLLM・LiteLLM）の両方に対応。完全オンプレミス構成で外部 API なしの運用も可能。

## エディション比較

| 項目 | Community Edition | Enterprise Edition |
|------|------------------|-------------------|
| ライセンス | MIT（無料） | 商用ライセンス |
| 基本機能 | ✅ | ✅ |
| SSO（OIDC/SAML） | — | ✅ |
| エアギャップ環境 | — | ✅ |

## 関連ページ

- [RAG](/blogs/wiki/concepts/rag/) — Onyx のコア技術
- [Ollama](/blogs/wiki/tools/ollama/) — ローカル LLM との組み合わせ
- [MCP](/blogs/wiki/concepts/mcp/) — カスタムコネクタのプロトコル

## ソース記事

- [Onyx（旧 Danswer）完全ガイド — 無料で使えるオープンソース AI プラットフォーム](/blogs/posts/2026/04/onyx-open-source-ai-platform/) — 2026-04-03
