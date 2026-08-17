---
title: "CodeGraph"
description: "コードベースを事前に知識グラフとして索引化し、AIコーディングのツール呼び出しを58%削減・22%高速化するローカル実行のOSS。MCP 経由で各エージェントと連携する"
date: 2026-07-15
lastmod: 2026-07-15
aliases: ["CodeGraph", "コード知識グラフ", "knowledge graph"]
related_posts:
  - "/posts/2026/06/codegraph-ai-coding-knowledge-graph/"
tags: ["CodeGraph", "claude-code", "mcp", "知識グラフ", "OSS"]
---

## 概要

CodeGraph（`colbymchenry/codegraph`）は、コードベースをあらかじめ「知識グラフ」として索引化しておくローカル実行の OSS（MIT ライセンス、GitHub スター 5.4万超）。AI エージェントが grep・glob・Read を繰り返してコードを探索する非効率を、シンボル・呼び出しエッジ・依存関係を事前グラフ化することで解消し、**ツール呼び出し58%削減・22%高速化・ファイル読み込みほぼゼロ**（7言語7コードベースの中央値）を実測している。100% ローカル動作。Claude Code・Cursor・Codex CLI・OpenCode・Hermes Agent・Gemini CLI など幅広く対応。

## 詳細

### 仕組みと導入

MCP サーバーとしてエージェントに接続し、1回のクエリで必要なコードを正確に取得させる。動的ディスパッチのホップも追跡できる。

```bash
codegraph install   # 使用中のエージェントを自動検出し MCP を組み込む
cd your-project
codegraph init      # .codegraph/ を作りグラフを構築（以後ファイル変更を自動監視）
```

### 効果はプロジェクト規模で変わる

- ツール呼び出しの削減・高速化は規模を問わず一貫して現れる
- トークン・コスト削減は大規模モノレポほど顕著

### 実プロジェクト検証で見えた盲点（43万LOCのDjango）

同カテゴリの知識グラフツール GitNexus での実測から、静的解析型グラフの限界が確認された。

- **アプリ跨ぎの通常 Python 呼び出しは正確に張れる** — 知識グラフの本領。grep より速く安全
- **Django の動的ディスパッチは繋がらない** — `signal.connect()` / `.delay()` / `.apply_async()` は実行時に張られるエッジで静的解析では捕捉できず、`impactedCount: 0` の false-safe を返しうる。CodeGraph も同じ静的解析ゆえ同じ盲点を踏む可能性が高い
- **日本語(CJK)の自然言語クエリは縮退する** — 英語やシンボル名主体の運用が要る
- **索引の陳腐化は運用コスト** — 「自動監視」を過信せず更新の点検は残る

教訓: ベンチマークの 58%削減は静的呼び出しが素直な言語で測ったもので、signals/Celery が主戦場の Django には直接転移しない。既に同カテゴリツールを使うなら、乗り換えは同一クエリでの精度実測で判断する。

## 関連ページ

- [Claude Code](/blogs/wiki/tools/claude-code/) — CodeGraph を MCP で接続する主要エージェント
- [MCP](/blogs/wiki/concepts/mcp/) — エージェントとの接続プロトコル
- [Brownfield リファクタリング](/blogs/wiki/concepts/brownfield-refactoring/) — 大規模既存コードの依存把握に関わる

## ソース記事

- [CodeGraph：AIコーディングのツール呼び出しを58%削減するコード知識グラフOSS](/blogs/posts/2026/06/codegraph-ai-coding-knowledge-graph/) — 2026-06-24
