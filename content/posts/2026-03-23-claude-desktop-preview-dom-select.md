---
title: "Claude Desktop Preview: 画面クリックでDOM要素を直接指定してUI修正できる新機能"
date: 2026-03-23
lastmod: 2026-03-23
draft: false
source_url: "https://github.com/hdknr/blogs/issues/1#issuecomment-4113385416"
categories: ["AI/LLM"]
tags: ["claude-code", "claude", "react"]
---

Claude Desktop の Preview 機能に、画面上の要素をクリックするだけで DOM 要素を直接指定できる機能が追加されました。「ヘッダー右のボタンの...」のような言葉での説明が不要になり、フロントエンド開発のワークフローが大きく変わります。

## 概要

Claude Code の開発者である Lydia Hallie 氏が X で紹介したこの機能では、Claude Desktop の Preview パネルで実行中のアプリをプレビューしながら、修正したい UI 要素をクリックで指定できます。

クリックすると Claude は以下の情報を自動的に取得します:

- HTML タグ名
- CSS クラス
- 主要なスタイル
- 周辺の HTML 構造
- クロップされたスクリーンショット

React アプリの場合はさらに:

- ソースファイルのパス
- コンポーネント名
- Props の情報

も取得されます。

## 使い方

1. Claude Desktop で Preview パネルを開く
2. 修正したい部分をクリックする
3. 「ここを青にして」のように指示する

これだけで Claude が該当要素を特定し、コードを修正してくれます。

## 活用シーン

- **デザイン修正の高速化**: 色、サイズ、レイアウトの微調整をクリック＋自然言語で即座に反映
- **非エンジニアによる UI 変更**: コードを読めなくても、画面を見ながら変更指示が可能
- **バグ箇所の特定**: 表示がおかしい要素をクリックするだけで、該当コンポーネントとソースファイルを特定

## 技術的な仕組み

Preview 機能の裏側では、`.claude/launch.json` で定義された開発サーバーが起動し、ヘッドレスブラウザと接続されます。Claude はスクリーンショット撮影、DOM 検査、クリックシミュレーション、ネットワーク監視などを直接実行できます。

ユーザーが要素をクリックすると、その要素のメタデータ（セレクタ、タグ、テキスト、ソース位置）が Claude Code のセッションコンテキストに自動的に注入される仕組みです。

## CLI 版 Claude Code で同様のことはできる？

この Preview パネルと「画面クリックで DOM 要素を指定」する機能は **Claude Desktop 専用**です。CLI 版の Claude Code には組み込みの Preview 機能はありません。

ただし、CLI 版でも **Chrome DevTools MCP** を使えば近いワークフローを実現できます。

### Chrome DevTools MCP によるアプローチ

[Chrome DevTools MCP](https://github.com/ChromeDevTools/chrome-devtools-mcp) は、ブラウザの DevTools Protocol を通じて Claude Code にブラウザ操作能力を与える MCP サーバーです。

セットアップ後にできること:

- DOM の検査・スナップショット取得
- スクリーンショットの撮影
- ページ上での JavaScript 実行
- コンソールログの読み取り
- ネットワークアクティビティの監視

### Desktop 版との違い

| 機能 | Desktop Preview | CLI + Chrome DevTools MCP |
|------|----------------|--------------------------|
| 要素のクリック指定 | 画面上で直接クリック | テキストでセレクタを指定 |
| 開発サーバー管理 | `.claude/launch.json` で自動起動 | 手動で起動が必要 |
| 自動検証 | 編集後に自動でスクリーンショット＋DOM検査 | 明示的に指示が必要 |
| React コンポーネント情報 | ソースファイル・Props を自動取得 | DOM 情報のみ |

CLI ユーザーで頻繁にフロントエンド開発を行う場合は、Claude Desktop への移行を検討する価値があります。

## まとめ

コードを探して場所を説明する時代から、「画面を触って指示する時代」への転換を象徴する機能です。特に React 開発では、コンポーネント名やソースファイルまで自動特定されるため、大規模なプロジェクトでも効率的に UI 修正を行えます。CLI ユーザーも Chrome DevTools MCP で部分的に同様のワークフローを取り入れることが可能です。
