---
title: "oh-my-openagent — Claude Code・Codex・Gemini CLI を統合管理する AIエージェントハーネス（★5.7万）"
date: 2026-05-11
lastmod: 2026-05-13
slug: "oh-my-openagent-multi-ai-agent-harness"
draft: false
source_url: "https://github.com/hdknr/blogs/issues/1#issuecomment-4424486460"
description: "oh-my-openagent（omo）は Claude Code・Codex・Gemini CLI を一元管理し、タスクに応じて最適な AI エージェントへ自動ルーティングする TypeScript 製ハーネス。Team Mode による最大 8 並列実行と ulw コマンドによる自律実行を解説。"
categories: ["AI/LLM"]
tags: ["oh-my-openagent", "claude-code", "agent", "openai", "gemini"]
---

複数の AI コーディングエージェントを使い分けるのは手間がかかる。その課題を解決するのが **oh-my-openagent（omo）** だ。Claude Code・OpenAI Codex・Gemini CLI といった主要エージェントを一元管理し、タスクに応じて最適なモデルへ自動ルーティングするオープンソースのハーネスで、GitHub スター数は **5.7 万超**（2026 年 5 月時点）に達している。

## oh-my-openagent とは

[oh-my-openagent](https://github.com/code-yeongyu/oh-my-openagent) は、もともと **oh-my-opencode** という名称で 2025 年 12 月に登場し、その後マルチエージェント対応を強化するかたちでリブランドされたツールだ。

- **作者**: code-yeongyu
- **言語**: TypeScript
- **ライセンス**: SUL-1.0
- **公式サイト**: [ohmyopenagent.com](https://ohmyopenagent.com/)

キャッチフレーズは「**the best agent harness**」。単一のエージェントに何でも任せるのではなく、専門化されたエージェント群がタスクを分担し、並列実行することで開発速度と品質を両立させる設計思想を持つ。

## 対応エージェントとプロバイダー

oh-my-openagent は以下のエージェント・モデルプロバイダーに対応している。

| プロバイダー | 主なモデル |
|---|---|
| Anthropic | Claude Code（claude-opus-4-6 / 4-7 等） |
| OpenAI | Codex、GPT-5.5 |
| Google | Gemini CLI |
| GitHub | Copilot |
| その他 | Kimi K2、DeepSeek V4 等 |

インストール時に利用中のサブスクリプションプラン（Claude Pro/Max、ChatGPT Plus など）を選択することで、利用可能なプロバイダーのみを有効化できる。

## 主要機能

### マルチモデルオーケストレーション

タスクの種類ごとに最適なモデルを自動選択する「**カテゴリベースのモデル割り当て**」が核心機能だ。

- **visual-engineering**（フロントエンド・UI 実装）→ Gemini
- **ultrabrain**（高難度なアーキテクチャ設計）→ Claude Opus 4.7
- **artistry**（クリエイティブな文章生成）→ GPT-5.5
- **deep**（深い推論・リサーチ）→ Claude Opus / Kimi K2

コスト最適化の観点から、大量ファイル生成のような作業は DeepSeek V4-Flash などの安価なモデルに自動振り分けされる。

### IntentGate（意図分類）

ユーザーの要求を実行前に「**調査（research）・実装（implement）・修正（fix）**」などのカテゴリに分類する機構。曖昧な指示を受け取っても、omo が意図を解析してから適切なエージェントを選択する。

### Sisyphus オーケストレーター

メインの調整役を担う **Sisyphus** は、以下の 4 フェーズで動作する。

1. **意図解析** — ユーザーの要求を IntentGate で分類
2. **コードベース評価** — リポジトリの構造と技術スタックを把握
3. **スペシャリスト委譲** — 最適な専門エージェントにタスクを割り当て
4. **独立検証** — 実装結果を別エージェントが検証

セッション継続性は `boulder.json` というファイルで管理され、作業を中断しても再開が可能だ。

### 専門エージェント群

| エージェント名 | 役割 |
|---|---|
| **Prometheus** | 戦略的計画立案。ユーザーにインタビューしてゴールを明確化 |
| **Atlas** | Prometheus の計画を受け取り、専門エージェントへタスクを配分・管理 |
| **Oracle** | アーキテクチャ相談専門の高知能コンサルタント |
| **Hephaestus** | GPT-5.5 ネイティブの自律型エージェント。深い分析と複雑な問題解決を担当 |
| **Metis / Momus** | 計画・実装の検証担当 |

### Team Mode（並列実行）

最大 **8 エージェント**を同時起動して並列作業させる Team Mode を備える。tmux と連携したビジュアライゼーションにより、複数エージェントの進捗をターミナル上でリアルタイム監視できる。

### ulw コマンド（Ultra Work mode）

```bash
omo ulw "Eコマースサイトの注文管理画面を実装して"
```

`ulw`（Ultra Work）コマンドは、以下を**ユーザー介入なし**で自律実行する。

1. 自動プランニング（Prometheus が設計）
2. 深層リサーチ（関連コードベースの調査）
3. 並列エージェント実行（Team Mode 起動）
4. 自己修正ループ（エラー検出 → 自動修正 → 再検証）

## インストール

インストールには **Bun** を使用する（npm/yarn/pnpm は非対応）。

```bash
bunx oh-my-openagent install
```

インタラクティブなインストーラーが起動し、以下の手順でセットアップが進む。

1. **サブスクリプション確認** — 利用可能なプロバイダーを選択
2. **インストール実行** — フラグで細かく制御可能。CI 環境など対話 UI が使えない場合は `--no-tui` を指定し、Claude Max 20 プランを使う場合は `--claude=max20` を指定する。

   ```bash
   bunx oh-my-openagent install --no-tui --claude=max20
   ```

3. **動作確認**

   ```bash
   bunx oh-my-openagent doctor
   ```

4. **認証設定** — Anthropic・Google・GitHub 等の OAuth 認証を完了

インストール完了後はターミナルで `opencode` コマンドを使って操作を開始できる。対応プラットフォームは macOS（ARM64・x64）・Linux（x64・ARM64）・Windows（x64）と幅広い。

## なぜ 5.7 万スターを獲得したのか

oh-my-openagent が急速に普及した背景には、**AI エージェントの乱立**という課題がある。Claude Code・Codex・Gemini CLI はそれぞれ得意不得意が異なり、開発者は複数ツールを手動で切り替えながら作業していた。

omo はこの切り替えコストをゼロにする。タスクを投げるだけで最適なエージェントが動き出し、並列で処理が進む——この体験が「チームで開発している感覚」と評価され、開発者に支持されている。

また、TypeScript 製でカスタマイズが容易な点も評価されている。独自のスキルや専門エージェントを追加してプロジェクト固有のワークフローを構築できる。

## まとめ

| 項目 | 内容 |
|---|---|
| GitHub | [code-yeongyu/oh-my-openagent](https://github.com/code-yeongyu/oh-my-openagent) |
| スター数 | 57,492（2026/05 時点） |
| 言語 | TypeScript |
| インストール | `bunx oh-my-openagent install` |
| 対応 OS | macOS / Linux / Windows |
| 主な対応 AI | Claude・GPT・Gemini・Codex・Kimi・DeepSeek |

複数の AI エージェントを統合し、タスクに応じて自動ルーティングする oh-my-openagent は、AI 活用を本格化させたい開発者にとって試す価値の高いツールだ。マルチモデル環境がスタンダードになりつつある今、エージェントハーネスというレイヤーはますます重要になっていくだろう。
