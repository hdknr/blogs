---
title: "エージェントループ設計（4種類のループ）"
description: "Claude Code チーム公式ガイドが定義する『停止条件を満たすまでエージェントが作業サイクルを繰り返す』ループの4分類。Turn-based / Goal-based / Time-based / Proactive を委譲の度合いで整理する"
date: 2026-07-15
lastmod: 2026-07-15
aliases: ["ループ設計", "agent loop", "エージェントループ", "Getting started with loops"]
related_posts:
  - "/posts/2026/07/claude-code-loop-design-guide/"
  - "/posts/2026/07/ai-agent-design-engineering-layers/"
tags: ["Claude Code", "エージェント", "自動化", "ループ設計", "プロンプトエンジニアリング"]
---

## 概要

Claude Code チームが公開した公式ガイド「Getting started with loops」（2026年6月30日）は、ループを「**停止条件が満たされるまで、エージェントが作業サイクルを繰り返すこと**」と定義し、実務で使う4種類に分類した。段階が進むごとに人間が手放す範囲が「チェック → 停止条件 → トリガー → プロンプトそのもの」へ広がる。ガイドは「すべてのタスクが複雑なループを必要とするわけではない。まずシンプルな解決策から」と繰り返し釘を刺している。

## 詳細

### 4種類のループ

| ループ | 手放すもの | 使うタイミング | 使う機能 |
|---|---|---|---|
| **Turn-based** | チェック | 探索中・意思決定中の短いタスク | カスタム検証スキル |
| **Goal-based** | 停止条件 | 完了の姿が分かっている | `/goal` |
| **Time-based** | トリガー | 作業がプロジェクト外でスケジュールに沿って発生 | `/loop`、`/schedule` |
| **Proactive** | プロンプトそのもの | 反復的かつ定型化された業務 | 上記すべて＋dynamic workflows |

- **Turn-based**: 普段使いの手動ループ。人間の確認手順を `SKILL.md` に固定し、Claude が自己検証できるようにするとターン数が減る。チェックが定量的なほど自己検証しやすい
- **Goal-based**: `/goal` で完了条件と試行上限を定義。**評価モデル（evaluator）**が停止のたびに条件を確認し、達成またはターン上限までゴールへ差し戻す。「テスト通過数」「スコア閾値」など決定論的な基準が効く
- **Time-based**: `/loop` は一定間隔でプロンプトを再実行（ローカル実行、止めれば止まる）。`/schedule` はそのクラウド常駐版
- **Proactive**: イベント/スケジュール駆動で人間が介在しない。auto mode や dynamic workflows を組み合わせ、`/schedule` + `/goal` + 並列 worktree + judge レビューを1文で構成できる

### 出力品質を保つ

コードベースを綺麗に保つ／Claude が検証できる手段を与える／ドキュメントに手が届くようにする／コードレビューは別エージェント（新鮮なコンテキストでバイアスが少ない）に任せる。個々の失敗はその場の修正で終わらせず、スキルやドキュメントの更新としてシステム側へ組み込む。

### トークン管理

適切なプリミティブとモデルを選ぶ／明確な成功・停止基準／大規模実行前のパイロット／決定論的作業はスクリプト化／必要以上に頻繁に回さない。使用量は `/usage`・引数なし `/goal`・`/workflows` で確認する。

## 関連ページ

- [AIエージェント設計レイヤー](/blogs/wiki/concepts/agent-design-layers/) — ループが積み重なりのどこに位置するか
- [Claude Code](/blogs/wiki/tools/claude-code/) — ループを構成するプリミティブの提供元
- [自律改善システムの設計](/blogs/wiki/concepts/autonomous-system-design/) — Proactive ループを安全に回す設計原則
- [自己改善エージェント](/blogs/wiki/concepts/self-improving-agents/) — 「プロンプトを書かない」自己改善ループの先の姿
- [マルチエージェント調整パターン](/blogs/wiki/concepts/multi-agent-coordination-patterns/) — dynamic workflows での並列・judge レビュー

## ソース記事

- [Claude Code チーム公式ガイド「ループ設計」を読み解く — Turn-based から Proactive まで4段階の委譲](/blogs/posts/2026/07/claude-code-loop-design-guide/) — 2026-07-01
