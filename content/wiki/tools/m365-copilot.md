---
title: "Microsoft 365 Copilot"
description: "Word・Excel・PowerPoint・Teams・Outlook に組み込まれ、社内データ(メール・会議・ドキュメント)を文脈に理解して回答・生成する Microsoft の AI アシスタント"
date: 2026-07-15
lastmod: 2026-07-15
aliases: ["M365 Copilot", "Microsoft 365 Copilot", "Copilot Chat", "Copilot Cowork"]
related_posts:
  - "/posts/2026/06/m365-copilot-getting-started/"
tags: ["Microsoft 365", "Copilot", "Teams", "Excel", "Outlook", "AIアシスタント"]
---

## 概要

Microsoft 365 Copilot は Word・Excel・PowerPoint・Teams・Outlook などの M365 アプリに直接組み込まれた AI アシスタント。単なるチャット AI ではなく、社内データ（Exchange メール・Teams 会議録・SharePoint ドキュメント）を文脈として理解した上で回答・生成できる点が特徴。2026年1月には Anthropic の Claude モデルがほとんどの商用テナント（EU/英国を除く）でデフォルト有効化され、同年3月の「Wave 3」で自律タスク実行「Copilot Cowork」も登場した。

## 詳細

### 導入直後に試したい機能

| 機能 | できること |
|---|---|
| **Copilot Chat**（旧 M365 Chat） | 社内メール・会議録・ドキュメントを横断検索。情報収集の起点 |
| **Teams 会議要約** | 要点・アクションアイテムを自動生成（2026年3月から日本語音声要約に正式対応） |
| **Word 下書き** | 「Copilot で下書き」で提案書・報告書のたたき台を生成 |
| **Excel データ分析** | 自然言語で傾向分析・フィルタ・予測。テーブル化(Ctrl+T)しておくと精度が上がる |
| **Outlook 返信** | メール返信の下書き・長いスレッドの3行要約 |

### 使いこなしのコツ

- プロンプトは具体的に（相手・文体・目的を明示）
- 数値・日付・固有名詞は必ずソースを確認（出力を鵜呑みにしない）
- 全機能を一度に使わず「今週は Teams 要約だけ」と1機能ずつ習慣化する

### 料金（2026年時点・税抜年払い）

| プラン | 月額/ユーザー |
|---|---|
| Microsoft 365 Copilot（法人） | 約4,497円 |
| Copilot Business（中小企業向け） | 約2,698円 |

いずれも既存 M365 ライセンスへのアドオン。

## 関連ページ

- [Claude Code](/blogs/wiki/tools/claude-code/) — 同じく Claude を基盤に使う開発者向けエージェント
- [AI エージェント](/blogs/wiki/concepts/ai-agent/) — Copilot Cowork の自律タスク実行に関わる概念

## ソース記事

- [M365 Copilot の使い方入門：会社導入後に知っておきたい基本と活用術](/blogs/posts/2026/06/m365-copilot-getting-started/) — 2026-06-24
