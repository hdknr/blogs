---
title: "claude-seo"
description: "Claude Code に SEO 分析機能を追加するオープンソーススキル。/seo audit 1つでサイト全体を並列監査し、GEO(AI検索最適化)まで25サブスキルでカバーする"
date: 2026-07-15
lastmod: 2026-07-15
aliases: ["claude-seo", "claude seo skill", "/seo audit"]
related_posts:
  - "/posts/2026/06/claude-seo-skill/"
tags: ["claude-code", "SEO", "スキル", "GEO", "E-E-A-T", "mcp"]
---

## 概要

**claude-seo** は Claude Code に SEO 分析機能を一括追加する MIT ライセンスの OSS スキル（開発者: AgriciDaniel、GitHub スター 9,600+）。Claude Code の「スキル」機構を使って `~/.claude/skills/` にインストールされ、`/seo` で始まるコマンドが使えるようになる。導入後は **25個のサブスキル＋18個のサブエージェント**が利用可能。必要なものは Python 3.8 以上と Claude Code。

## 詳細

### 主要コマンド

| コマンド | 機能 |
|---|---|
| `/seo audit` | サイト全体の SEO 監査（6サブエージェントが並列実行） |
| `/seo page` | ページ単位の詳細分析 |
| `/seo technical` | テクニカル SEO 診断（AIクローラーのアクセス可否も含む） |
| `/seo content` | E-E-A-T コンテンツ品質分析 |
| `/seo schema` | 構造化データの検出・検証・JSON-LD 生成 |
| `/seo geo` | AI 検索最適化（GEO） |
| `/seo plan` | 業種別 SEO 戦略設計（saas/local/ecommerce/publisher/agency） |

`/seo audit` は `FULL-AUDIT-REPORT.md` と優先度別の `ACTION-PLAN.md` を出力する。

### GEO（AI検索最適化）

2026年注目分野。引用適性（パッセージ 134〜167語が最適）・構造的可読性・マルチモーダル・権威性シグナル・技術的アクセシビリティ（llms.txt 等）の5指標でスコアリングする。

### データソースは2層

- **デフォルト**: HTML 静的解析＋Playwright スクリーンショット（APIキー不要）
- **オプション**: [Ahrefs](/blogs/wiki/tools/ahrefs/) / [Semrush](/blogs/wiki/tools/semrush/) / Google Search Console / PageSpeed Insights の各 MCP サーバー（ライブデータ用に認証情報が要る）。GA4 は標準データソースではない

### セキュリティ上の注意

公式 README も推奨する `git clone` 後に `bash install.sh` を実行する方式が安全（`curl | bash` はリポジトリ改ざんリスクで非推奨）。スキルは Claude Code 本体と同じ権限で動くため、信頼できるものだけ入れる。MCP の API キーを公開リポジトリに上げない。

## 関連ページ

- [Claude Code](/blogs/wiki/tools/claude-code/) — スキルの実行環境
- [MCP](/blogs/wiki/concepts/mcp/) — ライブデータ連携の接続プロトコル
- [Ahrefs](/blogs/wiki/tools/ahrefs/) / [Semrush](/blogs/wiki/tools/semrush/) — MCP 連携先の SEO データソース
- [インバウンドマーケティング](/blogs/wiki/concepts/inbound-marketing/) — SEO を含む集客の設計思想

## ソース記事

- [Claude Code の SEO スキル「claude-seo」とは？導入方法と全コマンドを解説](/blogs/posts/2026/06/claude-seo-skill/) — 2026-06-24
