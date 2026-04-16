---
title: "Claude Code"
description: "Anthropic 公式の CLI ベース AI コーディングエージェント"
date: 2026-04-06
lastmod: 2026-04-14
aliases: ["claude-code"]
related_posts:
  - "/posts/2026/04/claude-code-context-compression/"
  - "/posts/2026/04/claude-code-silent-degradation/"
  - "/posts/2026/04/karpathy-llm-wiki/"
  - "/posts/2026/04/claude-thinking-nerfed/"
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

## 関連ページ

- [コンテキスト圧縮](/blogs/wiki/concepts/context-compression/) — Claude Code のコンテキスト管理戦略
- [LLM Wiki パターン](/blogs/wiki/concepts/llm-wiki-pattern/) — Claude Code を活用した知識管理パターン
- [AutoAgent](/blogs/wiki/tools/autoagent/) — Claude Code をメタエージェントとして活用可能
- [dmux](/blogs/wiki/tools/dmux/) — Claude Code の並列実行環境を安全に管理するツール
- [Claude Managed Agents](/blogs/wiki/tools/claude-managed-agents/) — Anthropic のマネージドエージェント基盤

## ソース記事

- [Claude Code のコンテキスト圧縮戦略](/blogs/posts/2026/04/claude-code-context-compression/) — 2026-04-02
- [Claude Code のサイレントな性能劣化を見逃すな](/blogs/posts/2026/04/claude-code-silent-degradation/) — 2026-04-03
- [Karpathy の LLM Wiki](/blogs/posts/2026/04/karpathy-llm-wiki/) — 2026-04-05
- [Claude の思考深度が 67% 低下？サイレント・ダウングレード問題](/blogs/posts/2026/04/claude-thinking-nerfed/) — 2026-04-13
