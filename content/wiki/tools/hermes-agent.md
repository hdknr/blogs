---
title: "Hermes Agent"
description: "Nous Research が公開するオープンソース（MIT）のセルフホスト型 AI エージェント。モデル非依存で、記憶とスキルがホスト側に残りモデルを替えても引き継がれる"
date: 2026-11-09
lastmod: 2026-11-09
aliases: ["Hermes", "hermes-agent", "Hermes-Agent", "Nous Research", "x_search"]
related_posts:
  - "/posts/2026/11/meta-muse-vs-hermes-agent/"
tags: ["AIエージェント", "Hermes", "hermes-agent", "OSS"]
---

## 概要

Hermes Agent は Nous Research が公開している**開発者・パワーユーザー向けのオープンソース（MIT ライセンス）でセルフホスト型のエージェント**。ローカル PC・自前サーバー・VPS で常駐させ、ツール呼び出し・コーディング・自動化パイプラインを担わせる。

一般ユーザー向けのマネージド型である [Meta Muse](/blogs/wiki/tools/meta-muse/) とは正反対の設計で、自由度とデータの手元保持と引き換えに、セットアップと運用は自己責任になる。

## 詳細

### 特徴

- **モデルを選べる**: ローカルのオープンウェイトモデルから OpenAI・Anthropic などの商用 API まで、メインのモデルを設定で切り替えられる
- **記憶とスキルが育つ**: 複雑なタスクを終えるとスキルを自動生成し、使いながら改善する。記憶はホスト上に残るため、**モデルを入れ替えても記憶とスキルはそのまま**
- **データを手元に置ける**: ローカルモデルと組み合わせれば、社内データや個人情報を外部に出さずに運用できる
- **スキルのエコシステム**: スター数上位のスキルには、開発の進め方を型にした `obra/superpowers` や Anthropic 公式の `anthropics/skills` などが挙がる
- **対応ツール**: [CodeGraph](/blogs/wiki/tools/codegraph/) などのコード知識グラフ系ツールも Hermes Agent を対応先に挙げている

### 毎日使うユーザーのレビュー

- Hermes 側の利用上限はない（自分の API キー、ローカルモデル、Nous Portal のサブスクリプションを使う）
- 平均的なセッションで入力トークンの 94.4% がキャッシュから読まれていた
- メモリ 2GB の仮想マシンでも安定して動いた
- ただし**性能の低いモデルを使うと、作り込んだ記憶や設定を数分で壊されることがある**。モデル選びと復旧は利用者の責任

### x_search を単体で使う

Hermes Agent には xAI の Grok を通じて X を検索する `x_search` ツールがある。x_search だけが目的なら Hermes 本体のインストールは不要で、Python と uv があれば `uvx` で Hermes の xAI OAuth 認証だけを実行し、内部 API の `x_search_tool` を直接呼べる。Hermes のモデルによる再解釈を省けるので速いが、得られるのは **Grok による検索結果の分析であって検索 API ではない**（X API が無料になったわけではない）。

### Muse との使い分けと併用

| 観点 | Hermes Agent | Meta Muse |
|---|---|---|
| 形態 | OSS、セルフホスト | フルマネージド |
| モデル | 非依存 | Muse Spark 固定 |
| 導入の手間 | 大きい | 小さい |

併用例では、Muse を指揮官（窓口）にし、Muse が取りこぼしがちなプロジェクト・タスク管理を Hermes Agent に任せ、実作業は Claude・Codex に委譲している。詳細は [Meta Muse](/blogs/wiki/tools/meta-muse/) を参照。

Slack 上のエージェント連携では、Anthropic の [Claude Tag](/blogs/wiki/tools/claude-tag/) が OpenClaw や Hermes-Agent の代替になり得ると評価されている。

## 関連ページ

- [Meta Muse](/blogs/wiki/tools/meta-muse/) — 対照的なマネージド型の常駐エージェント
- [OpenClaw](/blogs/wiki/tools/openclaw/) — 同じくセルフホスト型のエージェント基盤
- [AI エージェント](/blogs/wiki/concepts/ai-agent/) — エージェント基盤の分類
- [自己改善エージェント](/blogs/wiki/concepts/self-improving-agents/) — スキルを自動生成・改善する考え方
- [エージェントハーネスとメモリのロックイン](/blogs/wiki/concepts/agent-memory-lock-in/) — 記憶をホスト側に持つことの意味
- [Ollama](/blogs/wiki/tools/ollama/) — ローカルモデルの実行環境

## ソース記事

- [Meta Muse と Hermes Agent の違い — マネージド型とセルフホスト型、常駐 AI エージェントの選び方と併用例](/blogs/posts/2026/11/meta-muse-vs-hermes-agent/) — 2026-11-09
