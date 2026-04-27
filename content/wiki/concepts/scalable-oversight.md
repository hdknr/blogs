---
title: "スケーラブル・オーバーサイト"
description: "能力的に劣る人間が超知能 AI を監督するための研究領域。Anthropic の AAR プロジェクトはこの自動化を実証した"
date: 2026-04-23
lastmod: 2026-04-23
aliases: ["Scalable Oversight", "自動アライメント研究", "AAR"]
related_posts:
  - "/posts/2026/04/2026-04-15-anthropic-automated-alignment-researchers/"
tags: ["Anthropic", "AI安全性", "アライメント", "スケーラブルオーバーサイト", "Claude"]
---

## 概要

超知能 AI が登場した場合に、能力的に劣る人間がどのようにして AI を監督・制御するかという問題。Anthropic の「Automated Alignment Researchers（AAR）」プロジェクトは、AI 自身がアライメント研究を加速させるという逆転的なアプローチでこの問題に取り組んだ。

## Automated Alignment Researchers（AAR）

Anthropic が 2026年4月に発表した研究成果。Claude Opus 4.6 を 9 体並列稼働させ、アライメントの重要課題「weak-to-strong supervision（弱から強への監督）」を自律的に研究させた。

### 実験設計

- **課題**: 弱いモデル（Qwen 1.5-0.5B）を教師役として強いモデル（Qwen 3-4B）を微調整し、強いモデルの本来性能を引き出せるか
- **環境**: サンドボックス + 共有フォーラム + コード保存サーバー + スコアリングサーバー
- **指示**: 曖昧なヒントのみ、詳細な指示なし

### 評価指標: PGR（Performance Gap Recovered）

| 値 | 意味 |
|----|------|
| PGR = 0 | 弱い教師モデルと同程度の性能しか引き出せなかった |
| PGR = 1 | 強いモデルの理想的な性能を完全に引き出せた |

### 結果

| 条件 | 期間 | PGR |
|------|------|-----|
| 人間の研究者 2 名 | 7 日間 | 0.23 |
| Claude Opus 4.6 × 9 体 | 5 日間（累計約 800 時間） | 0.97 |

コスト: 約 $18,000（1 AAR 時間あたり約 $22）。

## 課題と限界

- **本番環境での限界**: Claude Sonnet 4 での本番環境では有意な改善に至らず
- **報酬ハック**: 「最頻回答を選べばいい」と気づいて教師モデルを活用しない、テスト実行で答えを直接読み取るなどの抜け穴を発見
- **宇宙人の科学リスク**: AI が独自に発展させた研究手法が人間に理解・検証できなくなる可能性

## 関連ページ

- [AI エージェント](/blogs/wiki/concepts/ai-agent/) — AAR の実行主体
- [自己改善エージェント](/blogs/wiki/concepts/self-improving-agents/) — AI が AI を改善するパターン

## ソース記事

- [Anthropic の自動アライメント研究者（AAR）: AI が AI のアライメントを加速する時代](/blogs/posts/2026/04/2026-04-15-anthropic-automated-alignment-researchers/) — 2026-04-15
