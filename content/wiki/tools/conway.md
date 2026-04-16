---
title: "Anthropic Conway"
description: "Anthropic が内部開発中の常駐型（Always-On）AI エージェント環境。外部イベントやスケジュールに基づき自律的に稼働し、ブラウザ操作・Webhook 連携・.cnw 拡張を備える"
date: 2026-04-03
lastmod: 2026-04-03
aliases: ["Conway", "claude-conway"]
related_posts:
  - "/posts/2026/04/anthropic-conway-agent/"
tags: ["anthropic", "claude", "agent", "always-on", "webhook"]
---

## 概要

Anthropic が内部テスト中の常駐型 AI エージェント環境（コードネーム「Conway」）。2026年4月に TestingCatalog がリーク報道で存在を確認した。従来の Claude Desktop / Claude Code が「ユーザーの入力をトリガーとするワンショット型」であるのに対し、Conway は 24 時間バックグラウンドで稼働し続け、外部イベントやスケジュールを起点に自律的にタスクを実行する。

## 主な特徴

| 機能 | 説明 |
|------|------|
| Always-On（常時稼働） | ユーザーが不在でもバックグラウンドで継続動作 |
| Webhook 連携 | 外部サービスからのイベントをトリガーに自動実行 |
| ブラウザ操作 | Chrome を通じた Web 上のマルチステップ処理 |
| Claude Code 連携 | コーディングタスクの自動化（コードネーム "Epitaxy"） |
| .cnw 拡張機構 | `.cnw.zip` 形式のカスタムツール・UI タブ・コンテキストハンドラ |
| 通知システム | タスク完了などのイベント通知 |

## Anthropic エージェント製品との対比

| 製品 | 起動方式 | 主な用途 |
|------|----------|----------|
| Claude Desktop | ユーザープロンプト | 対話型チャット |
| Claude Code | ユーザー指示 | CLI コーディング支援 |
| Cowork | 非同期タスク | クラウド上の自律タスク |
| **Conway** | 外部イベント / スケジュール | 常駐型自律エージェント |

## 想定ユースケース

- メール受信時に自動で要約・分類
- GitHub Issue 作成をトリガーにした調査・対応
- Slack メンション通知への自動応答
- 定期的なデータ収集・レポート生成

## 現状

2026年4月時点では Anthropic 内部テスト段階。公式アナウンスは未実施。

## 関連ページ

- [Claude Managed Agents](/blogs/wiki/tools/claude-managed-agents/) — 同時期に公開されたマネージドエージェント基盤
- [AI エージェント](/blogs/wiki/concepts/ai-agent/) — エージェント基盤の概念
- [ハーネスエンジニアリング](/blogs/wiki/concepts/harness-engineering/) — エージェント設計パターン

## ソース記事

- [Anthropic Conway とは — 24時間稼働する常駐型AIエージェントの全貌](/blogs/posts/2026/04/anthropic-conway-agent/) — 2026-04-03
