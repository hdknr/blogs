---
title: "iOS開発が完全自動化される時代が来た：オープンソースmacOSアプリ「Blitz」とは"
date: 2026-03-22
lastmod: 2026-03-22
draft: false
source_url: "https://github.com/hdknr/blogs/issues/1#issuecomment-4106914372"
categories: ["AI/LLM"]
tags: ["agent", "mcp", "claude-code", "swift"]
---

AI エージェントが iOS アプリ開発を丸ごと自動化するオープンソースツール「Blitz」が公開された。ビルドからテスト、App Store 提出まで、これまで手作業だった工程を AI に任せられる時代が到来しつつある。

## Blitz とは

[Blitz](https://blitz.dev/) は、AI エージェントに iOS 開発ライフサイクルの完全な制御を与えるネイティブ macOS アプリケーション。シミュレーター/iPhone の管理、データベース設定、App Store Connect への提出まで、開発に必要な一連の操作を AI エージェントが実行できる。

GitHub リポジトリ: [blitzdotdev/blitz-mac](https://github.com/blitzdotdev/blitz-mac)（Apache-2.0 ライセンス）

## 主な特徴

### MCP サーバーによる AI 連携

Blitz には MCP（Model Context Protocol）サーバーが組み込まれており、Claude Code をはじめとする MCP クライアントからアプリのビルド、テスト、App Store への提出が可能になる。

### 自動化される範囲

- **コード署名とビルド**: Xcode プロジェクトのビルドを AI が実行
- **テスト実行**: シミュレーターや実機でのテストを自動化
- **App Store メタデータ**: アプリの説明やスクリーンショットの管理
- **App Store 提出**: App Store Connect API を通じた申請処理

### iPhone MCP

関連プロジェクトとして [iPhone-mcp](https://github.com/blitzdotdev/iPhone-mcp) も公開されている。AI が実際の iPhone を操作してアプリをテストし、バグを発見できる仕組みだ。

## セキュリティとプライバシー

- MCP サーバーは `127.0.0.1` にのみバインドされ、外部ネットワークには公開されない
- 連絡先、写真、位置情報などの個人データにはアクセスしない
- 画面キャプチャは iOS シミュレーターウィンドウに限定
- ネットワーク通信は Apple の App Store Connect API と GitHub のリリース API（更新チェック用）のみ

## 技術スタック

- SwiftUI で構築されたシングルターゲットアプリ
- Swift Package Manager によるビルド
- CLAUDE.md ファイルによるアーキテクチャドキュメントが整備されている

## iOS 開発の未来

従来の iOS 開発では、Xcode での手動操作が多くの時間を占めていた。Blitz のようなツールが成熟すれば、開発者はアプリのロジックや UX 設計に集中し、ビルド・テスト・提出といった反復的な作業は AI に委ねるワークフローが一般的になるかもしれない。

特に Claude Code との組み合わせにより、コードの生成から実機テスト、ストアへの提出までを一貫して AI エージェントが担当する開発スタイルが現実味を帯びてきている。
