---
title: "Modern Web Guidance"
description: "AI が書くフロントエンドが学習データのせいで古い書き方に留まる問題を、Baseline に基づく最新のガイドを Agent Skills として渡して補う Chrome チームのオープンソースプロジェクト"
date: 2026-11-15
lastmod: 2026-11-15
aliases: ["Modern Web Guidance", "modern-web-guidance", "GoogleChrome/modern-web-guidance", "Baseline target", "AI フロントエンドの 2019 年問題"]
related_posts:
  - "/posts/2026/11/modern-web-guidance-ai-frontend/"
tags: ["Agent Skills", "フロントエンド", "Baseline", "AIエージェント", "claude-code"]
---

## 概要

Modern Web Guidance は、Web プラットフォームのベストプラクティスとブラウザ互換性データを、コーディングエージェントに **Agent Skills**（必要に応じて読み込む手順書・知識のパッケージ）として渡す Google Chrome チームのオープンソースプロジェクト（[GoogleChrome/modern-web-guidance](https://github.com/GoogleChrome/modern-web-guidance)）。2026 年 5 月の Google I/O でアーリープレビュー、11 月 10 日に 1.0 になった。Firefox と Edge のチームも協力している。

## 詳細

### なぜ AI のフロントエンドは古くなるのか

1. **新しい機能を知らない**：学習データにはネイティブ機能が登場する前の「JavaScript で頑張る」コードが多い
2. **知っていても使い方やサポート状況を誤る**：構文が古い、どのブラウザで使えるかの前提が違う

同じプロンプトでガイダンスの有無だけ変えた比較（LogRocket）では、次のような差が出た。

| 機能 | ガイダンスなし | ガイダンスあり |
| --- | --- | --- |
| モーダル | JS の状態とタイムアウトで開閉 | ネイティブ `<dialog>` + CSS トランジション |
| カードの出し分け | メディアクエリ | コンテナクエリ |
| 2,000 件の検索 | `useMemo` で同期フィルタ | `scheduler.yield()` で分割処理 |
| ツールチップ | Floating UI ライブラリ | CSS Anchor Positioning |

### 仕組み

- **Baseline に基づく**：互換性の判断に [Baseline](https://web.dev/baseline) を使い、既定は「Baseline Widely available」。必要ならフォールバックやプログレッシブエンハンスメントを付ける
- **検索して必要なガイドだけ読む**：スキルがエージェントに CLI を呼ばせ、タスク内容でガイドを検索（`search`）し、該当する Markdown を取り出す（`retrieve`）。全ガイドを常にコンテキストに載せない
- **カテゴリ**：accessibility、css、forms、performance、security、ui-components、built-in-ai、webmcp など
- **1.0 の追加**：HTML・CSS・JS・`package.json` を静的解析して安全に上げられる箇所を探すモダナイズのワークフロー（対応パターンは限定的）と、支援技術を使ったアクセシビリティのレビュー

### 導入と設定

- 推奨：`npx modern-web-guidance@latest install`（対話式ウィザード、自動更新あり）。プレビュー版からは `update`
- Claude Code のプラグインとして：`claude plugin marketplace add GoogleChrome/modern-web-guidance` → `claude plugin install modern-web-guidance@googlechrome`
- Codex・Copilot CLI・Gemini CLI などにも手順があり、`npx skills add` や `gh skill install` でも入る
- **Baseline ターゲット**は `CLAUDE.md` や `AGENTS.md` に一文（`This project's Baseline target is Baseline 2024.`）書くだけで指定できる。ターゲットで「そのまま使うか、フォールバックを付けるか」が変わる
- 単一エンジンだけの実験的機能や Origin Trial は既定では取り出せない。`set-allow-volatile-features` / `set-allow-origin-trials` で必要なものだけオプトインする

### 効果と限界

公式の評価ダッシュボードは、完成したアプリを Playwright で実ブラウザで開き、要件ごとのチェックの合格率で測る。導入事例では note が 180 回の評価で合格率 61% → 94% と報告されている。一方で、出回っている「56% → 88%」という数字は公式ブログでは確認できない。

ガイダンスは**出発点を良くするもの**で、コードレビューや実ブラウザでのテスト、アクセシビリティの確認（`<dialog>` のフォーカスの戻り・キーボード操作・読み上げ）の代わりにはならない。実行時の検証には Chrome DevTools for agents（低スペック CPU での INP 計測、メモリリーク調査）を組み合わせることが勧められている。

## 関連ページ

- [Claude Code](/blogs/wiki/tools/claude-code/) — プラグインとして導入できるエージェント
- [Astro](/blogs/wiki/tools/astro/) — このブログのフロントエンドと、表示性能の切り分け事例
- [AI エージェント](/blogs/wiki/concepts/ai-agent/)

## ソース記事

- [AI が書くフロントエンドが「2019年」で止まる問題と、Chrome チームの Modern Web Guidance](/blogs/posts/2026/11/modern-web-guidance-ai-frontend/) — 2026-11-15
