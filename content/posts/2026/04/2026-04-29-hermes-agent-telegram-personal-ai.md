---
title: "Hermes Agent — Telegram × AI で個人専属エージェントを構築、使うほど成長する「資産型 AI」"
date: 2026-04-29
lastmod: 2026-04-29
slug: "hermes-agent-telegram-personal-ai"
draft: false
description: "Nous Research 製の自己進化型 AI エージェント Hermes Agent を Telegram 連携で 24 時間運用する方法。インストール・ゲートウェイ設定・OpenClaw 移行手順を解説。"
source_url: "https://github.com/hdknr/blogs/issues/1#issuecomment-4347270853"
categories: ["AI/LLM"]
tags: ["hermes-agent", "nous-research", "agent", "telegram", "openclaw", "ollama"]
---

Hermes Agent は Nous Research が開発した自己進化型 AI エージェントで、Telegram・Discord・Slack から操作でき、使うほどユーザー固有のスキルとメモリが蓄積される。本記事ではインストールから Telegram ゲートウェイ設定、OpenClaw からの移行手順まで解説する。

## Hermes Agent とは

[NousResearch/hermes-agent](https://github.com/NousResearch/hermes-agent)（GitHub 13.7万⭐）は、Nous Research が開発した自己進化型 AI エージェントだ。キャッチフレーズは「The agent that grows with you」— 使うほど自分専用に成長していく。

OpenClaw ユーザーからの移行を想定した `hermes claw migrate` コマンドが用意されており、設定・メモリ・スキル・API キーを丸ごとインポートできる。

## 主な特徴

### 使うほど成長する学習ループ

Hermes の最大の特徴は、フィードバックが自分のデータ内で完結する閉じた学習ループにある。

- 複雑なタスクをこなすたびにスキルを自動生成
- 過去の会話を FTS5 全文検索 + LLM 要約でクロスセッション想起
- ユーザーを深く理解するモデルを会話ごとに更新

自分が作ったスキルは `/skills list --source local` で一覧確認できる。スキルが積み上がっていく感覚が、個人専用のナレッジベース形成につながる。

### Telegram ゲートウェイ

Telegram 以外にも Discord・Slack・WhatsApp・Signal・Email に対応。VPS 上で 24 時間稼働させ、外出先からスマートフォンで操作するという使い方が現実的になっている。

### モデルを自由に切り替える

`/model` コマンドで会話中でも即時切替できる。用途に応じた使い分けの例:

| 用途 | モデル例 |
|------|---------|
| 日常会話 | Ollama Cloud（ほぼ無料） |
| 中程度の開発作業 | Sonnet |
| 複雑なタスク | Claude Code / Codex |

対応プロバイダーは Nous Portal・OpenRouter（200+ モデル）・NVIDIA NIM・OpenAI・Hugging Face など多数。コードを変更せずプロバイダーを切り替えられる。

### 自然言語でスケジュール設定

> 毎日朝 8 時にニュースまとめて

と話しかけるだけで定期実行タスクが設定できる。組み込みの cron スケジューラが Telegram などに配信する。

### 並列サブエージェント

独立したサブエージェントを spawn して複数のワークフローを並列実行できる。Python スクリプトからツールを RPC 呼び出しすることも可能で、コンテキストを消費せずに複数ステップの処理を実行できる。

### 対応バックエンド一覧（ローカル / Docker / VPS / サーバーレス）

| バックエンド | 特徴 |
|-------------|------|
| ローカル | 開発・テスト向け |
| Docker | 環境分離 |
| SSH | リモートマシン |
| Modal / Daytona | サーバーレス・アイドル時はほぼ無料 |
| $5 VPS | 24 時間常時稼働 |

## インストール方法

```bash
curl -fsSL https://raw.githubusercontent.com/NousResearch/hermes-agent/main/scripts/install.sh | bash
```

Linux・macOS・WSL2・Android（Termux）に対応。インストール後は以下で起動できる。

```bash
source ~/.bashrc   # シェル再読み込み
hermes             # 会話開始
```

Telegram ゲートウェイを設定するには:

```bash
hermes gateway setup   # ゲートウェイを設定（Telegram Bot Token が必要）
hermes gateway start   # 起動
```

## OpenClaw からの移行

```bash
hermes claw migrate              # 対話式移行（フル）
hermes claw migrate --dry-run    # プレビューのみ
hermes claw migrate --preset user-data   # シークレット除外
```

移行対象: SOUL.md（ペルソナ）・メモリ・スキル・コマンド許可リスト・Telegram 設定・API キーなど。

## Hermes Agent 基本情報まとめ

| 項目 | 内容 |
|------|------|
| 開発元 | Nous Research |
| リポジトリ | [NousResearch/hermes-agent](https://github.com/NousResearch/hermes-agent) |
| ライセンス | MIT |
| 対応 OS | Linux・macOS・WSL2・Android |
| 公式ドキュメント | [hermes-agent.nousresearch.com/docs](https://hermes-agent.nousresearch.com/docs/) |

従来の AI サービスは使い捨てに近い。しかし Hermes は異なる。使うほどユーザー固有のスキルとメモリが蓄積され、自分だけの AI 従業員へと進化していく。日常的に使い続けることで、汎用 AI サービスでは得られない個人最適化が蓄積される。インストールして 30 分もあれば体感できる。`hermes setup` ウィザードが全設定を一括でガイドしてくれる。
