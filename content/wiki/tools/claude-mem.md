---
title: "claude-mem"
description: "Claude Code にセッションをまたいだ永続的な記憶機能を追加する MCP プラグイン。SQLite + Chroma の3層検索でトークン消費を95%削減。公開48時間で46,000スター獲得"
date: 2026-04-13
lastmod: 2026-04-16
aliases: ["claude-mem persistent memory", "claude code memory"]
related_posts:
  - "/posts/2026/04/claude-mem-persistent-memory/"
tags: ["Claude Code", "MCP", "メモリ", "トークン最適化", "オープンソース"]
---

## 概要

[thedotmack/claude-mem](https://github.com/thedotmack/claude-mem) は Claude Code にセッションをまたいだ記憶を持たせる MCP（Model Context Protocol）ベースのオープンソースプラグイン。公開から48時間で46,000スターを獲得し、「トークン消費95%削減」「コンテキスト上限に到達しない」「前回の続きから再開できる」という特徴が開発者の注目を集めた。

## 主な特徴

| 特徴 | 内容 |
|------|------|
| トークン削減 | セッションあたり約95% |
| ストレージ | ローカル SQLite + Chroma |
| インストール | `npx claude-mem install`（1コマンド） |
| ライセンス | オープンソース・完全無料 |

## 3層検索フロー

関連する記憶を効率よく取り出すために、以下の段階的なフィルタリングを採用する:

1. **キーワード検索** (`search`) — テキストマッチで候補を絞り込む
2. **タイムライン確認** (`timeline`) — 時系列で文脈を絞り込む
3. **詳細取得** (`get_observations`) — 必要な記憶だけを取得する

先に絞り込んでから詳細取得することで不要なトークン消費を防ぐ。この仕組みが「95%削減」の源泉。

## 記憶の保存と圧縮

- Claude Code のセッション中の操作を自動キャプチャ
- AI を使って記憶を圧縮・要約（Claude Agent SDK を使用）
- ローカルの SQLite データベースに永続化
- Chroma によるベクトル埋め込み検索で意味的に類似した記憶を検索

## インストール

```bash
npx claude-mem install
```

特別な API キーや外部サービスの登録は不要。完全ローカルで動作する。

## MemPalace との比較

| 観点 | claude-mem | MemPalace |
|------|------------|-----------|
| 対象 | Claude Code 専用 | 複数 AI ツール対応 |
| インストール | 1コマンド | Python セットアップ |
| 公表スコア | トークン95%削減 | LongMemEval 96.6%（論争あり） |
| アーキテクチャ | 3層検索 | 宮殿構造（Wing/Hall/Room） |

## 関連ページ

- [MemPalace](/blogs/wiki/tools/mempalace/) — 別アプローチの AI メモリシステム
- [エージェントメモリのロックイン](/blogs/wiki/concepts/agent-memory-lock-in/) — メモリ管理の設計上の課題
- [Claude Code](/blogs/wiki/tools/claude-code/) — claude-mem の動作環境
- [MCP](/blogs/wiki/concepts/mcp/) — プラグインの接続プロトコル

## ソース記事

- [claude-mem: Claude Code に永続的な記憶を追加し、48 時間で 46,000 スター](/blogs/posts/2026/04/claude-mem-persistent-memory/) — 2026-04-13
