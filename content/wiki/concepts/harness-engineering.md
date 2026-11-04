---
title: "ハーネスエンジニアリング"
description: "AI エージェントの出力品質を保証する設計パターン。検証層・制約層・フィードバック層で構成"
date: 2026-04-06
lastmod: 2026-10-30
aliases: ["Harness Engineering", "馬具・柵・境界"]
related_posts:
  - "/posts/2026/03/harness-engineering/"
  - "/posts/2026/03/ai-agent-qa/"
  - "/posts/2026/03/claude-code-review/"
  - "/posts/2026/04/anthropic-vs-openai-harness-strategy/"
  - "/posts/2026/04/agent-harness-memory-lock-in/"
  - "/posts/2026/04/ai-agent-harness-confusion/"
  - "/posts/2026/04/ai-first-harness-engineering-creao/"
  - "/posts/2026/07/ai-agent-design-engineering-layers/"
  - "/posts/2026/04/agent-harness-rag-context-size/"
  - "/posts/2026/04/claude-harness-v4-hokage/"
  - "/posts/2026/04/harness-engineering-agent-vs-user-harness/"
  - "/posts/2026/04/harness-engineering-beyond-rule-files/"
  - "/posts/2026/10/harness-design-intro-guardrails-boundary/"
  - "/posts/2026/10/jev-system-one-model/"
tags: ["agent", "品質保証", "CLAUDE.md", "設計パターン", "ロックイン"]
---

## 概要

AI エージェント全盛時代に必須の設計手法。CLAUDE.md（入力層）、MEMORY.md（実行記録層）、Hooks（検証層）、Agent Skills（ワークフロー層）の4層で AI 出力の品質を決定論的に保証する。Anthropic 公式の推奨パターン。

## 4層構造

| 層 | 役割 | 実装 |
|---|---|---|
| 入力層 | AI への指示・制約 | CLAUDE.md |
| 記録層 | 学習・実行履歴 | MEMORY.md |
| 検証層 | 出力の事前/事後チェック | Hooks (PreToolUse/PostToolUse) |
| ワークフロー層 | 構造化タスク定義 | Agent Skills (SKILL.md) |

## 馬具・柵・境界の 3 層モデル

`AGENT = MODEL + HARNESS`（モデル以外のすべてがハーネス）という広い定義に 2026 年 3〜7 月で議論がほぼ収束し、関心は「どう組むか」に移った。木下雄一朗氏の整理では、ハーネスを強さの違う 3 層に分ける。

| 層 | 役割 | 性質 | 道具 |
|---|---|---|---|
| 馬具 | 走る前に方向を伝える | 確率的（読んで従うかはモデル次第） | AGENTS.md・Skills・サブエージェント |
| 柵（ガードレール） | 逸脱を機械的に判定して止める・差し戻す | 決定論的 | lint・型・ビルド・テスト・Hooks・許可リスト |
| 境界 | 到達そのものを無くす | 構造的 | サンドボックス・通信遮断・最小権限 |

- **可逆な逸脱は柵で拾ってループに戻し、不可逆な逸脱は境界で試行そのものを無くす**。本番・機密・個人情報には道を作らない
- 柵には「成果物への柵」（正しく作れたか）と「行動への柵」（実行してよいか）の 2 種類がある
- 柵を自動で走らせる「レール」は 3 本: エージェントの Hooks（速いが無効化できる）→ Git hooks（`--no-verify` で抜けられる）→ CI＋ブランチ保護（抜け道なし）。外側ほど強い
- ループは「検証器＝`check` の 1 コマンド」と「ゴール＝`check` がすべて通る」を渡すだけで閉じる
- 判定が決定論的でも、テストが弱ければ間違いを毎回合格させる。LLM レビューは確率的なので柵には数えない
- 実行時の見方では `agent = model + context + runtime`。context への依存が減り runtime に寄るほど強い。**クレデンシャルは runtime に置き、context に入れない**（中継サーバーで代理実行するクレデンシャルブローカー構成など）
- 着手順は「境界 → ルール（最小限）→ 柵を `check` に束ねる → ループを閉じる → 繰り返しが見えたら Skills・サブエージェント → 定期的に棚卸し」。モデルの弱点を補う注意書きは次世代モデルで溶けるが、テスト・権限・固有規約は残る
- 無人で起動する（イベント駆動・定期実行）場合は 3 層それぞれの要求が上がる。外部入力はプロンプトインジェクション経路、停止条件にターン・時間・コスト上限、成果物は PR で出してレールを通す、トリガーごとにロールを分ける

LLM 系の判定器を柵に組み込む例として、[Jev](/blogs/wiki/tools/jev/) で Bash コマンドを分類する PreToolUse hook がある。確信度が低い・誘導コメントで揺らぐといった性質があるため、自動許可の最終判断はコードに置く必要がある。

## Anthropic vs OpenAI のハーネス戦略

両社はともにハーネスの重要性を認識しているが、アプローチが対照的だ。

| 観点 | OpenAI | Anthropic |
|------|--------|-----------|
| ハーネスの位置づけ | エンジニアが設計する環境（Harness Engineering） | プラットフォームが提供する基盤（Managed Agent） |
| 人間の役割 | プロジェクトマネージャー | AI との協働者 |
| 製品 | Codex + Symphony | Claude Code + Managed Agent |

OpenAI は AI がソフトウェア開発を全面的に担う方向を目指し、Anthropic はエージェント実行基盤を「Agent OS」としてプラットフォーム化している。

## ハーネスとメモリのロックイン

LangChain 創設者 Harrison Chase が指摘する通り、ハーネスとメモリは不可分だ。メモリはコンテキストの一形態であり、ハーネスの中核的な責任。クローズドなハーネスを使うことは、以下の4層すべての管理を第三者に委ねることを意味する:

1. **コンテキストウィンドウ内のメッセージ履歴** — 構成方法でモデルの応答が変わる
2. **コンパクション（会話の要約圧縮）** — 何を残し何を捨てるかでエージェントの「記憶の質」が変わる
3. **永続ファイル・データベース（長期メモリ）** — エージェントの「人格」を形成する
4. **設定・スキルのロード方式** — エージェントの能力を規定する

## ハーネスの「内側」と「外側」の混乱

「ハーネス」という言葉は話者のポジションによって意味がズレる（watany 氏, 2026年4月）:

| 視点 | 定義 | 文脈 |
|------|------|------|
| **内側のハーネス** | モデル呼び出し間でコンテキストを引き継ぐ機構（LangChain / Anthropic） | プラットフォーム・フレームワーク側 |
| **外側のハーネス** | エージェントが同じミスを繰り返さないように設計する実践（Mitchell Hashimoto / OpenAI） | ユーザー・実践者側 |

## Claude Harness v4.0.0 "Hokage" — Go ネイティブ化

Claude Code のハーネスエンジニアリングを 1 パッケージで組み込んだ外装プラグイン「Claude Harness」が v4.0.0 "Hokage" をリリース（2026-04-14）。

| 改善点 | Before | After |
|---|---|---|
| フック実行速度 | ~300ms（bash → Node.js → TypeScript 3段ロケット） | ~10ms（Go バイナリ 1 本、30 倍速） |
| 設定ファイル数 | 5〜6 本を手動整合（plugin.json / hooks.json / settings.json 等） | harness.toml 1 本（SSOT） |
| ガードレール | R12 warn | R12 deny + Bash bypass 二重防御 |
| Node.js 依存 | 必要 | 不要（ネイティブバイナリ 3 本） |

pure-Go SQLite（`modernc.org/sqlite`）採用で Node.js ランタイム要件を完全排除。`bin/harness sync` で `plugin.json` / `hooks.json` / `settings.json` が全て整合される。

## AI ファースト運用の実績（CreaoAI, 25 名）

CreaoAI は「AIファーストハーネスエンジニアリング」を実践し、6 週間のリリースサイクルを 1 日に短縮した:

- コードの 99% を AI が生成
- 1 日 8 回デプロイ（14 日間平均 3〜8 回/日）
- モノレポへの統合（AI が全体を把握できるようにするため）
- 3 つの並列 Claude レビューパス（コード品質・セキュリティ・依存関係スキャン）

解消した 3 つのボトルネック: PM の計画サイクル、QA のテスト時間、ヘッドカウント不足。

## RAG なしで高精度になる理由

コンテキストウィンドウの拡大（20k〜1M トークン）により、100 ファイル以下のコードベースはハーネスがファイルをそのまま読み込める。RAG の「断片的コンテキスト問題」を回避できるため、より正確な依存関係・型・インターフェースを参照できる。100 ファイルを超える場合は GraphRAG 等のインデックス戦略が有効。

## 関連ページ

- [ループエンジニアリング](/blogs/wiki/concepts/loop-engineering/) — ハーネスの上に載る制御プレーン層
- [要求仕様書作成ループ](/blogs/wiki/concepts/requirements-spec-loop/) — ハーネスの手前で仕様そのものの妥当性を固めるループ
- [AIエージェント設計レイヤー](/blogs/wiki/concepts/ai-agent-design-layers/) — ハーネスがどのレイヤーを担当するかの地図
- [AI エージェント](/blogs/wiki/concepts/ai-agent/) — ハーネスで品質保証される対象
- [エージェントメモリのロックイン](/blogs/wiki/concepts/agent-memory-lock-in/) — ハーネスとメモリの不可分性とロックインリスク
- [Claude Code](/blogs/wiki/tools/claude-code/) — ハーネスエンジニアリングの主要実装環境
- [Claude Managed Agents](/blogs/wiki/tools/claude-managed-agents/) — Anthropic のマネージドハーネス
- [自己改善エージェント](/blogs/wiki/concepts/self-improving-agents/) — ハーネス自体を AI が改善するパターン
- [Graphite](/blogs/wiki/tools/graphite/) — AI ファースト開発での PR 管理ツール
- [RAG](/blogs/wiki/concepts/rag/) — ハーネスとの組み合わせ判断
- [AIエージェント設計の5レイヤー](/blogs/wiki/concepts/ai-agent-design-layers/) — ハーネスが第3層として位置づく全体地図
- [グラフエンジニアリング](/blogs/wiki/concepts/graph-engineering/) — ハーネスの上に積む最上位レイヤー
- [オーケストレーター／コーダー分業と承認ゲート](/blogs/wiki/concepts/orchestrator-coder-split/) — ゲートを仕組みとして強制する実装例
- [Claude Code Hooks](/blogs/wiki/concepts/claude-code-hooks/) — 行動への柵・最も内側のレール
- [Jev](/blogs/wiki/tools/jev/) — hook から呼ぶ判定特化モデル
- [プロンプトインジェクション](/blogs/wiki/concepts/prompt-injection/) — lethal trifecta と境界設計

## ソース記事

- [ハーネスエンジニアリング](/blogs/posts/2026/03/harness-engineering/) — 2026-03
- [AI エージェント QA 手法](/blogs/posts/2026/03/ai-agent-qa/) — 2026-03
- [Anthropic vs OpenAI：Harness 戦略はなぜ真逆なのか](/blogs/posts/2026/04/anthropic-vs-openai-harness-strategy/) — 2026-04-13
- [エージェントハーネスとメモリのロックイン問題](/blogs/posts/2026/04/agent-harness-memory-lock-in/) — 2026-04-12
- [AI エージェントの「ハーネス」を巡る混乱](/blogs/posts/2026/04/ai-agent-harness-confusion/) — 2026-04-16
- [「AIファースト」戦略の本当の意味 — ハーネスエンジニアリングで 25 人チームが 6 週間を 1 日に短縮した方法](/blogs/posts/2026/04/ai-first-harness-engineering-creao/) — 2026-04-17
- [RAG なしでも高精度に動く Agent Harness の秘密](/blogs/posts/2026/04/agent-harness-rag-context-size/) — 2026-04-17
- [Claude Harness v4.0.0 "Hokage" — Go ネイティブ化で 30 倍速、設定が harness.toml 1 本に](/blogs/posts/2026/04/claude-harness-v4-hokage/) — 2026-04-14
- [Jev とは何か — 文章を書かず「判断だけ」を返す System One モデル](/blogs/posts/2026/10/jev-system-one-model/) — 2026-10-13
- [ハーネスエンジニアリング入門 — 馬具・柵・境界の3層で AI エージェントを自走させる](/blogs/posts/2026/10/harness-design-intro-guardrails-boundary/) — 2026-10-25
