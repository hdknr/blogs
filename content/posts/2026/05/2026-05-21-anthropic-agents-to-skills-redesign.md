---
title: "Skills vs Agents — Anthropic の研究チームが設計哲学を全転換した理由と Claude Code 実践ガイド"
date: 2026-05-21
lastmod: 2026-05-21
slug: "anthropic-agents-to-skills-redesign"
draft: false
source_url: "https://github.com/hdknr/blogs/issues/1#issuecomment-4513719495"
categories: ["AI/LLM"]
tags: ["Claude Code", "Skills", "Agents", "Anthropic", "SKILL.md", "agentskills.io", "モジュラー設計"]
---

Anthropic の研究・プロダクトチーム（Barry Zhang・Mahesh Murag）が、2025年11月の AI Engineering Code Summit で衝撃的な発言をした。

> **「Agents をやめて、Skills に全振りした」**

Agent ツールを実際に開発してきた当事者が、この言葉を口にした意味は重い。単なる命名変更ではなく、AI 自動化の設計哲学そのものが変わった瞬間だ。

この記事では、なぜ Anthropic が Agents から Skills へシフトしたのか、その背景と技術的な理由、そして今すぐ自分のワークフローに活かせるポイントを解説する。

## Agents の限界 — 何が問題だったのか

従来の「Agent」アプローチの核心は、**中央集権型オーケストレーター**だった。1 つの LLM が多数のツールを持ち、あらゆるタスクに対応しようとする構成だ。具体的には以下の 4 点が問題になった。

- **ツールオーバーロード**: ツール数が増えるほど、LLM はどのツールを使うべきか判断しにくくなる
- **再現性の低さ**: 複雑なシナリオで中央オーケストレーターが混乱し、同じ入力に対して異なる結果が出やすい
- **モデル依存**: Claude 専用に設計された Agent は、他のモデルでは動かない
- **コンテキスト肥大化**: すべての能力を一度にロードするため、トークンが無駄に消費される

Barry Zhang と Mahesh Murag はこれらの問題を実装レベルで体験し、「根本から再設計が必要だ」という結論に至った。

## Skills とは何か — Agent との本質的な違い

Skills は、Claude Code の拡張機能の単位だ。`SKILL.md` と必要なスクリプト・設定ファイルを 1 つのフォルダにまとめて定義し、必要なときだけオンデマンドでメイン会話コンテキストに注入される。

| 観点 | Agents | Skills |
|------|--------|--------|
| 設計思想 | 中央集権型オーケストレーター | モジュラー・再利用可能な能力単位 |
| モデル対応 | Claude 専用 | Claude + 他モデル両対応 |
| 実行コンテキスト | 独立した隔離環境 | メイン会話内（記憶・フォローアップが可能） |
| ロード方式 | 常時ロード | オンデマンド（トークン節約） |
| 再現性 | 複雑なシナリオで低下しやすい | 実用レベルで高い |

最も重要な変化は**モデル非依存**になったことだ。Anthropic は 2025年12月に Skills をオープンスタンダードとして [agentskills.io](https://agentskills.io) で公開し、Microsoft/VS Code・OpenAI・Cursor・GitHub・Google Gemini CLI・JetBrains Junie など主要プラットフォームが採用済みだ。Claude だけでなく、他のモデルでも同じスキルが動作する。

## なぜ Skills の方が「実用での再現性が高い」のか

テーブルの「再現性」の差は、設計の違いから来ている。

Agents の孤立した実行環境は「客観的なコードレビュー」のような隔離が必要なタスクには適している。しかし多くの実務ユースケースでは、前のやりとりの文脈を引き継ぎながら作業を続けたい。

Skills がメイン会話コンテキスト内で実行される設計は、**継続性の問題を解決**する。さらにモジュール化によってツールオーバーロードが解消され、LLM は「今何の能力が必要か」を明確に理解できる。この継続性はエージェントの長期運用にも直結する。過去の文脈を引き継いで成長し続ける AI と、毎回リセットされる AI では実務での価値がまったく異なる。Skills のアーキテクチャはこの記憶継続性とも本質的に相性が良い。

## 今すぐ自分のワークフローに活かすには

発表後、有志エンジニアが「200 個以上のスキルを検証して 20 個を選んだ」記事を公開している（[I tested 200 Claude Code skills — here are the 20 that actually changed how I work](https://www.indiehackers.com/post/i-tested-200-claude-code-skills-so-you-dont-have-to-here-are-the-20-that-actually-changed-how-i-work-b383a23ce3)）。特に評価が高いカテゴリは以下だ。

- **ドキュメント処理**: 長大な契約書や仕様書を高速レビューする PDF スキル
- **マーケティング・SEO**: コンテンツ生成から競合分析まで一括対応
- **知識管理統合**: Obsidian などのツールと連携した第 2 の脳構築

自分が今使っている自動化構成を見直してみると良い。**「このタスクは `SKILL.md` として型化できないか？」** という問いが設計改善の出発点になる。

## まとめ — Skills 移行のポイント

Anthropic のチームが「Skills に全振り」した判断は、実装を積み重ねてきた側からの証言として重く受け止めるべきだ。

- Agents の中央集権型アーキテクチャは、複雑なシナリオで限界を露呈する
- Skills はモジュラー・モデル非依存・オンデマンドロードで再現性が高い
- Skills のオープンスタンダード化（[agentskills.io](https://agentskills.io)）で、Claude の外にも展開可能

今日からできる具体的なアクションは 1 つだ。今使っている自動化構成の中で最も頻繁に実行するタスクを 1 つ選び、それを `SKILL.md` として型化してみることだ。
