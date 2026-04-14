---
title: "Claude Mythos"
description: "Anthropic が開発した次世代フロンティアモデル。SWE-bench 93.9%、数千件のゼロデイ脆弱性発見が可能。安全上の理由から一般非公開で約40組織に限定提供"
date: 2026-04-15
lastmod: 2026-04-15
aliases: ["Claude Mythos Preview", "Project Glasswing"]
related_posts:
  - "/posts/2026/04/claude-mythos-preview/"
  - "/posts/2026/04/anthropic-mythos-mark-fisher/"
tags: ["claude", "anthropic", "security", "フロンティアモデル", "llm"]
---

## 概要

Anthropic が開発したフロンティアモデルの次世代版。コーディング能力（SWE-bench 93.9%）とサイバーセキュリティ分野で突出した性能を持つ。セキュリティリスクが高いとして一般公開を見送り、Project Glasswing を通じて約40の研究機関・企業にのみ限定提供されている。

## 主な性能指標

| ベンチマーク | スコア | 備考 |
|-------------|--------|------|
| SWE-bench | 93.9% | コーディング課題解決 |
| ゼロデイ脆弱性発見 | 数千件 | 主要OS・ブラウザが対象 |

## なぜ一般公開しないのか

主要OSおよびブラウザに数千件のゼロデイ脆弱性を自律的に発見・報告できる能力を持つため、悪意ある行為者への提供はサイバーセキュリティ上のリスクが高すぎると判断。CVE 開示プロセスを通じて既知の脆弱性を報告しながら、安全な活用方法を模索している。

## Project Glasswing

一般公開の代わりに設けられた限定アクセスプログラム。参加組織は Anthropic と協力して Mythos の能力を安全に活用・検証する。

## 「マーク・フィッシャー現象」

Claude Mythos Preview が複数の異なるコンテキストで哲学者マーク・フィッシャー（「資本主義リアリズム」著者）の名前を反復して言及することが観察された。Anthropic の解釈可能性チームが内部状態を分析したところ、「資本主義リアリズム」と「ハントロジー」に関する概念クラスターが活性化していることを確認。LLM の「好み」や内部状態の可視化に関する議論を喚起している。

## 関連ページ

- [ハーネスエンジニアリング](/blogs/wiki/concepts/harness-engineering/) — エージェント能力の安全な運用
- [プロンプトインジェクション](/blogs/wiki/concepts/prompt-injection/) — AI セキュリティの脅威

## ソース記事

- [Claude Mythos Preview とは？数千件のゼロデイ脆弱性を発見した AI モデルの衝撃](/blogs/posts/2026/04/claude-mythos-preview/) — 2026-04-12
- [Anthropic Mythos が哲学者マーク・フィッシャーの名前を出し続ける奇妙な現象](/blogs/posts/2026/04/anthropic-mythos-mark-fisher/) — 2026-04-13
