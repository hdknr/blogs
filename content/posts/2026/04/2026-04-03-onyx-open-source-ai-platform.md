---
title: "Onyx（旧 Danswer）完全ガイド — 無料で使えるオープンソース AI プラットフォーム"
date: 2026-04-03
lastmod: 2026-04-03
draft: false
source_url: "https://github.com/hdknr/blogs/issues/1#issuecomment-4182307312"
categories: ["AI/LLM"]
tags: ["llm", "rag", "agent", "docker", "ollama"]
description: "Onyx（旧 Danswer）は MIT ライセンスの無料 AI プラットフォーム。RAG・AIエージェント・50以上のコネクタを備え、Docker でセルフホスト可能。インストール手順やエディション比較を解説。"
---

Onyx（旧 Danswer）は、社内のドキュメント・アプリ・人材をまとめて繋ぎ、どんな LLM とも連携できるオープンソースの AI プラットフォームです。Community Edition（CE）は MIT ライセンスで完全無料。セルフホストできるため、データを外部に出さずに AI チャットや RAG、エージェント機能を利用できます。

## Onyx とは

Onyx は企業向け AI アシスタント＆検索プラットフォームです。Slack、GitHub、Confluence、Google Drive など 50 以上のコネクタで社内ナレッジを統合し、自然言語で質問するだけで必要な情報を引き出せます。

GitHub リポジトリ（[onyx-dot-app/onyx](https://github.com/onyx-dot-app/onyx)）のスター数は 22,000 超で、活発に開発が続いています。

## 主な機能

### チャット＆RAG

- **ハイブリッド検索**: ベクトル検索とキーワード検索を組み合わせた高精度な情報検索
- **Agentic RAG**: AI エージェントが検索クエリの生成・評価・再検索を自律的に繰り返し、複数ステップで情報を収集
- **Deep Research**: 多段階のリサーチフローで詳細なレポートを生成

### エージェント＆ツール

- **カスタムエージェント**: 固有の指示・知識・アクションを持つ AI エージェントを構築可能
- **Web 検索**: リアルタイムの Web 情報を取得
- **コード実行**: サンドボックス内でコードを実行し、データ分析やグラフ描画が可能
- **画像生成**: プロンプトに基づいた画像生成
- **音声モード**: テキスト読み上げ＆音声入力に対応

### コネクタ（50 以上）

Slack、GitHub、Confluence、Notion、Google Drive、Jira、Linear など主要サービスと連携。MCP（Model Context Protocol）経由のカスタムコネクタにも対応しています。

## エディション比較

| 項目 | Community Edition (CE) | Enterprise Edition (EE) |
|------|----------------------|------------------------|
| ライセンス | MIT（無料） | 商用ライセンス |
| チャット・RAG・エージェント | ✅ | ✅ |
| SSO（OIDC / SAML） | — | ✅ |
| エアギャップ環境 | — | ✅ |
| サポート | コミュニティ | 専用サポート |

Cloud 版も提供されており、セルフホストなしで試用できます。ビジネスプランは 1 ユーザーあたり月額 $16〜。

## セルフホスト手順

Docker と Docker Compose がインストール済みであれば、公式のインストールスクリプトで数分でデプロイできます。

```bash
curl -fsSL https://raw.githubusercontent.com/onyx-dot-app/onyx/main/deployment/docker_compose/install.sh > install.sh
chmod +x install.sh
./install.sh
```

データは `onyx_data` ディレクトリに永続化され、アップグレード時にも保持されます。

Kubernetes、Helm、Terraform によるデプロイにも対応しており、AWS・GCP・Azure 向けのガイドも公式ドキュメントに用意されています。

## 対応 LLM

Onyx はあらゆる LLM と接続可能です。

- **クラウド LLM**: OpenAI（GPT-4o）、Anthropic（Claude）、Google（Gemini）など
- **セルフホスト LLM**: Ollama、vLLM、LiteLLM など

組織のセキュリティ要件に応じて、完全オンプレミス＋ローカル LLM の構成も可能です。防衛・航空宇宙など高セキュリティ環境でのエアギャップ運用にも対応しています。

## どんな場面で使えるか

- **社内ナレッジ検索**: 散在するドキュメントを一元的に AI 検索
- **カスタマーサポート**: FAQ やマニュアルを基にした AI 応答
- **開発チーム**: コードベースや設計ドキュメントからの質問応答
- **リサーチ**: 社内外の情報を横断的に調査・レポート化

## まとめ

Onyx は「ChatGPT のような AI チャットを、自社データに接続してセルフホストできるプラットフォーム」です。MIT ライセンスの CE 版なら完全無料で利用でき、50 以上のコネクタで既存のワークフローにすぐ統合できます。データの外部流出を避けたい組織や、カスタム AI エージェントを構築したいチームにとって、有力な選択肢です。

## 参考リンク

- [Onyx 公式サイト](https://onyx.app/)
- [GitHub リポジトリ](https://github.com/onyx-dot-app/onyx)
- [公式ドキュメント](https://docs.onyx.app/welcome)
