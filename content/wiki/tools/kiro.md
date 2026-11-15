---
title: "Kiro"
description: "AWS が提供する Code OSS ベースの AI 開発環境。要件（EARS）・設計・タスクの Spec を先に作ってから実装する流れを IDE に組み込み、Steering・Hooks・MCP・権限モードを備える"
date: 2026-11-15
lastmod: 2026-11-15
aliases: ["Kiro IDE", "Kiro CLI", "kiro-cli", "Kiro Spec", "Steering", "Bugfix Spec", "Quick Spec"]
related_posts:
  - "/posts/2026/11/kiro-ai-ide-intro/"
  - "/posts/2026/11/spec-driven-development-overview/"
  - "/posts/2026/11/ears-requirements-syntax/"
  - "/posts/2026/11/cc-sdd-intro/"
tags: ["Kiro", "aws", "仕様駆動開発", "AI駆動開発", "EARS"]
---

## 概要

**Kiro** は AWS が開発・運営する AI 開発環境で、[仕様駆動開発](/blogs/wiki/concepts/spec-driven-development/) の代表的なツールである。AI に実装させる前に要件・設計・タスクの 3 文書（**Spec**）を作ってレビューする流れが IDE に組み込まれている。2025 年 7 月にプレビュー、同年 11 月 17 日に一般提供。IDE のほか CLI・Web・モバイルアプリでも提供される。

Code OSS（VS Code のオープンソース版）がベースなので操作感は VS Code とほぼ同じだが、拡張機能は OpenVSX から入れるため、VS Code Marketplace の拡張がすべて見つかるとは限らない。

## 詳細

### Spec

1 機能ごとに 3 つのファイルを作る。

| ファイル | 内容 |
|---|---|
| `requirements.md` | ユーザーストーリーと受け入れ基準。[EARS](/blogs/wiki/concepts/ears/) の `WHEN … THE SYSTEM SHALL …` で書く |
| `design.md` | アーキテクチャ、シーケンス図、実装上の考慮事項 |
| `tasks.md` | 個別に追跡できるタスクに分けた実装計画 |

- **進め方**：Requirements-First（要件から）、Design-First（設計から）、Quick Spec（承認を待たず 3 文書をまとめて自動生成）の 3 種類。基本は段階ごとに人間が承認する
- **Bugfix Spec**：`requirements.md` の代わりに `bugfix.md` で「現在の振る舞い」「期待する振る舞い」「変えてはいけない振る舞い」を書き分け、設計で根本原因を突き止める。タスクには再現・修正・回帰なしを確かめるプロパティベーステストが入る（仕様の正しさを PBT で確かめる機能は IDE のみ）
- **タスクの実行**：まとめて実行すると依存関係のグラフを作り、依存しないタスクを同じ「波（wave）」として並行に実行する

注意点として、Kiro の EARS は**イベント駆動の WHEN の形だけ**が示されているので、AI が書いた要件に状態依存や異常系（If / Then）の抜けがないかを人間が確かめる。

### チャットのエージェントと権限モード

組み込みエージェントは Default・Spec・Quick Spec・Plan（変更せず計画だけ）・Bug Fix。AI に任せる範囲はチャットごとの権限モードで選ぶ。

| モード | 動き |
|---|---|
| Supervised | ファイルを編集したターンのたびに止まって承認を待つ |
| Accept file changes | ファイル操作は確認なし、コマンドはルールで許可していなければ確認（1.4.154 より前は Autopilot） |
| Approve for me | 判断のつく操作はモデルが承認・拒否し、迷うときだけ人間に訊く |

コードと会話を任意の時点まで巻き戻すチェックポイントもある。

### Steering

プロジェクトの知識を Markdown で AI に渡す仕組み。`.kiro/steering/`（ワークスペース）と `~/.kiro/steering/`（全体共通）に置き、食い違えばワークスペースが優先。基本は `product.md`・`tech.md`・`structure.md` で、IDE の「Generate Steering Docs」で生成できる。読み込みは front matter の `inclusion` で `always`（既定）・`fileMatch`（パターン一致時）・`manual`（`#ファイル名` で指定）・`auto`（description と依頼が合うとき）から選ぶ。`AGENTS.md` にも対応し、こちらは常に読み込まれる。

### Hooks・MCP・モデル・CLI

- **Hooks**：`.kiro/hooks/` の JSON で、ファイルの作成・保存・削除（エージェントの変更にだけ反応）、Spec のタスクの前後、ツール使用の前後、プロンプト送信などをトリガーにシェルコマンドかプロンプトを実行する。用途はリンター・型チェック・関連ファイルの生成など
- **MCP**：stdio 型とリモートの HTTP 型のサーバーの両方に対応（[MCP](/blogs/wiki/concepts/mcp/)）
- **モデル**：推奨の Auto がモデルルーターで依頼に応じて選ぶ。Claude や OpenAI、オープンウェイトのモデルも選べるが、プランで異なり頻繁に入れ替わる
- **Kiro CLI**：`kiro-cli`。CLI 3.0 以降は Steering・カスタムエージェント・Hooks・権限・MCP の設定を IDE と共有し、ヘッドレスモードで CI/CD に組み込める。Steering の 4 つの読み込みモードが全部使えるのも CLI V3 以降

### 料金（2026 年 11 月時点）

| プラン | 月額 | 月間クレジット |
|---|---|---|
| Free | 0 ドル | 50 |
| Pro | 20 ドル | 1,000 |
| Pro+ | 40 ドル | 2,000 |
| Pro Max | 100 ドル | 5,000 |
| Power | 200 ドル | 10,000 |

クレジットは作業量の単位で、個人プランは翌月に繰り越さない。追加は 1 クレジット 0.04 ドル。条件は変わるので契約前に公式ページで確かめる。

### 向き・不向き

- 向く：何を作るかを先に固めたい新機能、Steering と Hooks でチームの AI の使い方を揃えたい場合、Bugfix Spec による再発防止
- 注意：Böckeler 氏の評価では主に **Spec-First** のツールで、仕様とコードが自動で同期し続けるわけではない。仕様を誰がいつ更新するかはチームで決める。小さな修正は Default エージェントで直すなど、変更の大きさで使い分ける

### Kiro 以外で同じ流れを使う

IDE を替えずに同じ流れを使うなら、同じ文書構成を Claude Code や Codex に持ち込む [cc-sdd](/blogs/wiki/tools/cc-sdd/)、MCP サーバーとして承認を記録する [Spec Workflow MCP](/blogs/wiki/tools/spec-workflow-mcp/)、原則から始める [GitHub Spec Kit](/blogs/wiki/tools/github-spec-kit/) がある。Spec Kit は `--integration kiro-cli` で Kiro CLI 上でも使える。

## 関連ページ

- [仕様駆動開発（SDD）](/blogs/wiki/concepts/spec-driven-development/) — Kiro が体現する開発手法とツール比較
- [EARS 記法](/blogs/wiki/concepts/ears/) — `requirements.md` の受け入れ基準の書き方
- [cc-sdd](/blogs/wiki/tools/cc-sdd/) — Kiro に着想を得た Claude Code・Codex 向けのスキル
- [GitHub Spec Kit](/blogs/wiki/tools/github-spec-kit/) — GitHub の SDD ツールキット
- [Spec Workflow MCP](/blogs/wiki/tools/spec-workflow-mcp/) — Kiro とよく似た文書構成の MCP サーバー
- [Claude Code Hooks](/blogs/wiki/concepts/claude-code-hooks/) — Kiro の Hooks に相当する仕組み

## ソース記事

- [Kiro とは？ AWS の仕様駆動 AI IDE の Spec・Steering・Hooks と料金プラン](/blogs/posts/2026/11/kiro-ai-ide-intro/) — 2026-11-13
- [仕様駆動開発（SDD）とは？ 3 つのアプローチ・EARS 記法・Kiro / Spec Kit・TDD との違い](/blogs/posts/2026/11/spec-driven-development-overview/) — 2026-11-13
- [EARS 記法とは？ 6 つのパターンと日本語での書き方・Kiro での使い方](/blogs/posts/2026/11/ears-requirements-syntax/) — 2026-11-13
- [cc-sdd とは？ Claude Code・Codex で Kiro 式の仕様駆動開発を回すスキルと使い方](/blogs/posts/2026/11/cc-sdd-intro/) — 2026-11-13
