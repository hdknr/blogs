---
title: "Claude Code"
description: "Anthropic 公式の CLI ベース AI コーディングエージェント"
date: 2026-04-06
lastmod: 2026-04-29
aliases: ["claude-code"]
related_posts:
  - "/posts/2026/04/claude-code-context-compression/"
  - "/posts/2026/04/claude-code-silent-degradation/"
  - "/posts/2026/04/karpathy-llm-wiki/"
  - "/posts/2026/04/claude-thinking-nerfed/"
  - "/posts/2026/04/2026-04-15-claude-code-routines/"
  - "/posts/2026/04/2026-04-15-claude-code-routines-desktop-update/"
  - "/posts/2026/04/2026-04-16-claude-code-team-onboarding/"
  - "/posts/2026/04/2026-04-17-claude-caveman-token-reduction/"
  - "/posts/2026/04/2026-04-17-claude-code-context-rot-session-management/"
  - "/posts/2026/04/2026-04-17-video-use-claude-code-video-editing/"
  - "/posts/2026/04/2026-04-17-apm-agent-package-manager/"
  - "/posts/2026/04/2026-04-21-claude-code-45-tasks-automation-student/"
  - "/posts/2026/04/2026-04-21-claude-code-auto-memory-skills/"
  - "/posts/2026/04/2026-04-21-claude-code-level5/"
  - "/posts/2026/04/2026-04-21-claude-code-zero-handwritten-code-49-features/"
  - "/posts/2026/04/2026-04-23-claude-code-local-llm-vllm/"
  - "/posts/2026/04/2026-04-23-claude-code-obsidian-second-brain/"
  - "/posts/2026/04/2026-04-23-claude-code-plan-mode-cost-reduction/"
  - "/posts/2026/04/2026-04-23-claude-code-sns-automation-affiliate/"
  - "/posts/2026/04/2026-04-25-exa-for-claude-mcp-plugin/"
  - "/posts/2026/04/2026-04-27-claude-code-creator-setup/"
  - "/posts/2026/04/2026-04-27-claude-code-kabukicho-ai-simulation/"
  - "/posts/2026/04/2026-04-27-claude-code-stock-trading-automation/"
  - "/posts/2026/04/2026-04-14-claude-code-world-ai-simulator/"
  - "/posts/2026/04/2026-04-17-pytest-chaos-engineering/"
  - "/posts/2026/03/2026-03-17-claude-code-auto-mode/"
  - "/posts/2026/03/2026-03-17-claude-code-commands/"
tags: ["claude-code", "claude", "anthropic", "AIエージェント"]
---

## 概要

Anthropic が開発する CLI ベースの AI コーディングエージェント。ターミナル上で対話しながらコードの読み書き、ファイル操作、git 操作、テスト実行などを行える。

## 主な特徴

- **CLI ネイティブ**: ターミナルで直接対話（IDE 拡張版も提供）
- **ツール統合**: ファイル読み書き、Bash 実行、Grep/Glob 検索、Web 検索等
- **CLAUDE.md**: プロジェクトごとのルール・設定ファイル（圧縮後も再読み込みされる）
- **サブエージェント**: 複雑なタスクを並列エージェントに委任可能
- **スキル/フック**: カスタムワークフローの定義と自動化

## コンテキスト管理

5段階の圧縮カスケードでコンテキストウィンドウを管理する:
Microcompact → Context Collapse → Session Memory → Full Compact → PTL Truncation

詳細: [コンテキスト圧縮](/blogs/wiki/concepts/context-compression/)

## LLM Wiki との関連

Karpathy は Claude Code を LLM Wiki の実行環境として使用。「左画面に Claude Code、右画面に Obsidian」というワークフローを実践。

## 思考深度のサイレント・ダウングレード問題

2026年4月、AMD のシニア AI ディレクターが約 6,852 セッション分のログ分析で発見した問題。2026年3月8日以降、Claude Code の思考の中央値が約 2,200 文字から約 600 文字（**67%減**）に低下していた。Anthropic は「アダプティブ・シンキング」による変更を認め、`/effort max` コマンドで高い思考深度を維持できると説明した。

## Routines — クラウド上での自動実行

2026年4月14日リリースの **Claude Code Routines** により、PC をオフラインにしたままでもクラウド上でエージェントをスケジュール実行できるようになった。トリガー: cron / API コール / GitHub イベント。

## 新 Desktop — 複数セッション並列管理

同日リリースの新 Desktop では複数セッションの同時管理が可能になった。リポジトリ・Issue を並列で扱い、コンテキストを保持したまま別タスクに移行できる。

## /team-onboarding コマンド

過去 30 日のセッション履歴を分析してチーム向けオンボーディング資料を自動生成するコマンド。作業タイプの割合・よく使うスキル・MCP 接続使用回数を Markdown 形式で出力し、Notion や GitHub Wiki にコピペできる。

## トークン削減: 原始人プロンプト

システムプロンプトに `原始人みたいに喋れ。中身は全部残せ。無駄だけ消せ。` を追加するだけで日本語応答のトークンを最大 80% 削減できる（英語版 Caveman テクニックの日本語版）。CLAUDE.md に追記するだけで適用できる。

## Context Rot 管理

Claude Code のコンテキストウィンドウは 100 万トークン。長いセッションでは Context Rot（コンテキスト劣化）が発生する。5 つのセッション管理選択肢（Continue / Rewind / /clear / /compact / Subagent）を使い分けることで性能を維持できる。

詳細: [Context Rot](/blogs/wiki/concepts/context-rot/)

## 関連ページ

- [コンテキスト圧縮](/blogs/wiki/concepts/context-compression/) — Claude Code のコンテキスト管理戦略
- [Context Rot](/blogs/wiki/concepts/context-rot/) — コンテキスト劣化現象と 5 つの対処法
- [LLM Wiki パターン](/blogs/wiki/concepts/llm-wiki-pattern/) — Claude Code を活用した知識管理パターン
- [AutoAgent](/blogs/wiki/tools/autoagent/) — Claude Code をメタエージェントとして活用可能
- [dmux](/blogs/wiki/tools/dmux/) — Claude Code の並列実行環境を安全に管理するツール
- [Claude Managed Agents](/blogs/wiki/tools/claude-managed-agents/) — Anthropic のマネージドエージェント基盤
- [Video Use](/blogs/wiki/tools/video-use/) — Claude Code スキルとして動作する動画編集自動化ツール
- [Claude Harness](/blogs/wiki/tools/claude-harness/) — Claude Code の拡張機構をワンパッケージで提供する外装プラグイン

## ソース記事

- [Claude Code のコンテキスト圧縮戦略](/blogs/posts/2026/04/claude-code-context-compression/) — 2026-04-02
- [Claude Code のサイレントな性能劣化を見逃すな](/blogs/posts/2026/04/claude-code-silent-degradation/) — 2026-04-03
- [Karpathy の LLM Wiki](/blogs/posts/2026/04/karpathy-llm-wiki/) — 2026-04-05
- [Claude の思考深度が 67% 低下？サイレント・ダウングレード問題](/blogs/posts/2026/04/claude-thinking-nerfed/) — 2026-04-13
- [Claude Code Routines リリース — 常駐しないエージェントという新しい設計思想](/blogs/posts/2026/04/2026-04-15-claude-code-routines/) — 2026-04-15
- [Claude Code、1日でアプデ3連発 — Routines・新 Desktop・ストリーム安定性](/blogs/posts/2026/04/2026-04-15-claude-code-routines-desktop-update/) — 2026-04-15
- [Claude Code の /team-onboarding コマンド](/blogs/posts/2026/04/2026-04-16-claude-code-team-onboarding/) — 2026-04-16
- [Claude を「原始人」口調にするとトークンが 80% 減る話](/blogs/posts/2026/04/2026-04-17-claude-caveman-token-reduction/) — 2026-04-17
- [Claude Code のコンテキスト管理術 — Context Rot を防ぐ 5 つの選択肢](/blogs/posts/2026/04/2026-04-17-claude-code-context-rot-session-management/) — 2026-04-17
- [Video Use — Claude Code で動画編集を完全自動化するオープンソーススキル](/blogs/posts/2026/04/2026-04-17-video-use-claude-code-video-editing/) — 2026-04-17
