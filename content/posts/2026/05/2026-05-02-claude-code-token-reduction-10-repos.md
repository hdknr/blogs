---
title: "Claude Code のトークン消費を最大90%削減する10のGitHubリポジトリ"
date: 2026-05-02
lastmod: 2026-05-02
slug: "claude-code-token-reduction-10-repos"
draft: false
description: "Claude Code のトークン消費を最大90%削減できる10のOSSツールを、出力フィルタリング・シンボル単位参照・プロンプト制御・MCPサーバーの4アプローチで分類・解説。導入コストの低い順にも整理。"
source_url: "https://github.com/hdknr/blogs/issues/1#issuecomment-4363251305"
categories: ["AI/LLM", "ツール/開発環境"]
tags: ["claude-code", "トークン最適化", "mcp", "コスト削減", "コンテキスト管理"]
---

Claude Code を使い続けると、トークン消費が積み重なってコストが気になってくる。X（旧 Twitter）ユーザーの [@xiaoying_eth](https://x.com/xiaoying_eth) が、トークン消費を最大90%削減できる10のGitHubリポジトリをまとめて紹介している。本記事では出力フィルタリング・シンボル単位参照・プロンプト制御・MCP サーバーという4アプローチで各ツールを分類し、導入しやすいものから解説する。

## 1. RTK (Rust Token Killer)

**リポジトリ**: [rtk-ai/rtk](https://github.com/rtk-ai/rtk)

コンテキストに流れ込む前にターミナル出力をフィルタリングするツール。よく使う開発コマンド（`cargo build`、`npm test` など）の冗長な出力を削減することで、**60〜90%** のトークン削減を実現する。Rust 製のため高速で、Claude Code の実際のコーディングセッションでの効果が大きい。

詳細は「[RTK（Rust Token Killer）で Claude Code のトークン使用量を60〜90%削減する](/blogs/posts/2026/04/rtk-rust-token-killer-claude-code/)」を参照。

## 2. Context Mode

**リポジトリ**: [mksglu/context-mode](https://github.com/mksglu/context-mode)

Playwright や GitHub のツール出力を SQLite に転送し、クリーンな要約のみを Claude に送信するアプローチ。生のツール出力をそのままコンテキストに流さないことで **98%** の削減を達成している。ブラウザ自動化や CI/CD 連携を多用するワークフローに特に有効。

## 3. code-review-graph

**リポジトリ**: [tirth8205/code-review-graph](https://github.com/tirth8205/code-review-graph)

Tree-sitter を使ってローカルでコードリポジトリをナレッジグラフに変換するツール。ファイル全体を渡す代わりにグラフ構造で必要な情報だけを抽出するため、大型モノリポでは **49倍** のトークン削減が可能。コードレビューや依存関係の調査に向いている。

## 4. Token Savior

**リポジトリ**: [Mibayy/token-savior](https://github.com/Mibayy/token-savior)

MCP サーバーとして動作し、ファイル全体ではなくシンボル単位（関数・クラス・変数）でコードを参照するツール。コードナビゲーション操作で **97%** のトークン削減を達成。外部依存がゼロなので導入しやすい。

## 5. Caveman Claude

**リポジトリ**: [JuliusBrussee/caveman](https://github.com/JuliusBrussee/caveman)

"原始人の口調" で Claude に話させることで出力トークンを削減するユニークなアプローチ。技術的な正確性は維持しつつ、出力を **65〜75%** 削減できる。プロンプトエンジニアリングによる出力スタイルの制御という発想が面白い。

詳細は「[Claude を「原始人」口調にするとトークンが 80% 減る話](/blogs/posts/2026/04/claude-caveman-token-reduction/)」を参照。

## 6. claude-token-efficient

**リポジトリ**: [drona23/claude-token-efficient](https://github.com/drona23/claude-token-efficient)

`CLAUDE.md` ファイルをプロジェクトに置くだけで出力を簡潔に保てるシンプルなツール。コードの変更が不要で、長いセッションに最適。`CLAUDE.md` をリポジトリにコミットすればチーム全体に設定が共有される。

## 7. token-optimizer-mcp

**リポジトリ**: [ooples/token-optimizer-mcp](https://github.com/ooples/token-optimizer-mcp)

キャッシュ・圧縮・インテリジェントツール制御を備えた MCP サーバー。繰り返し実行されるツール出力をキャッシュして圧縮することで **95%以上** の削減を実現。ツールの呼び出し回数自体を減らすインテリジェントな制御機能も持つ。

## 8. claude-token-optimizer

**リポジトリ**: [nadimtuhin/claude-token-optimizer](https://github.com/nadimtuhin/claude-token-optimizer)

再利用可能なプロジェクト最適化プロンプトのコレクション。適切なプロンプトセットを適用することで、5分以内に **90%** のトークン節約が見込める。プロンプトエンジニアリングの知見をパッケージ化したアプローチ。

## 9. token-optimizer

**リポジトリ**: [alexgreensh/token-optimizer](https://github.com/alexgreensh/token-optimizer)

このツールが "ghost tokens"（幽霊トークン）と呼ぶ、静かにコンテキストを消費し続ける不要情報を発見・除去するコンテキスト分析ツール。圧縮後も出力品質が低下しないことが特徴。

## 10. claude-context（by Zilliz）

**リポジトリ**: [zilliztech/claude-context](https://github.com/zilliztech/claude-context)

BM25 + ベクトル検索の MCP サーバーで、コードリポジトリ全体をコンテキストにロードできるツール。全ファイルを渡す代わりに関連するコードだけを検索して提供するため、同等の検索精度を保ちながら **約40%** のトークン削減が可能。Zilliz（Milvus ベクトルデータベースの開発元）が提供する本格的な RAG アプローチ。

## まとめ：Claude Code トークン削減の4つのアプローチ

これら10のツールは、大きく4つのアプローチに分類できる。

| アプローチ | ツール | 削減効果 |
|---|---|---|
| 出力フィルタリング | RTK, Context Mode | 60〜98% |
| シンボル単位参照 | code-review-graph, Token Savior | 49倍〜97% |
| プロンプト制御 | Caveman Claude, claude-token-efficient, claude-token-optimizer | 65〜90% |
| MCP サーバー | token-optimizer-mcp, claude-context | 40〜95%+ |
| コンテキスト分析 | token-optimizer | — |

Claude Code のコスト削減を考えるなら、まず `claude-token-efficient`（CLAUDE.md を置くだけ）と `RTK`（ターミナル出力フィルタリング）から試してみることをすすめる。MCP サーバーを活用しているなら `token-optimizer-mcp` や `claude-context` も組み合わせると効果的だ。

コンテキスト管理の全体像については「[Claude Code のコンテキスト管理術 — Context Rot を防ぐ5つの選択肢](/blogs/posts/2026/04/claude-code-context-rot-session-management/)」も参照してほしい。
