---
title: "Claude Tag"
description: "Slack チャンネルに Claude をチームメンバーとして参加させ、独自の identity とメモリを持ってプロアクティブに動く Anthropic の仕組み"
date: 2026-07-15
lastmod: 2026-07-15
aliases: ["Claude Tag", "Claude in Slack"]
related_posts:
  - "/posts/2026/06/claude-tag-enterprise-slack-workflow/"
tags: ["claude", "anthropic", "Slack", "AIエージェント", "ワークフロー自動化", "Enterprise"]
---

## 概要

Claude Tag は 2026年6月23日に Anthropic が正式発表した、Slack チャンネルに Claude を「チームメンバー」として参加させる仕組み。呼びかけに応答するだけの Bot と違い、独自の identity とメモリを持ち、チャンネルを監視して **プロアクティブ（アンビエントモード）に自発通知**する点が特徴。Claude ライセンスを持たないユーザーもチャンネル単位で利用できる。

## 詳細

### 従来の Slack Bot / 外部ツールとの違い

| 観点 | 従来の Slack Bot / 外部ツール | Claude Tag |
|---|---|---|
| セキュリティ | 独自インフラが必要 | Anthropic 管理で安全 |
| セットアップ | 複雑な設定 | 4ステップで完了 |
| ライセンス | 利用者全員が個別に必要 | チャンネル単位で共有 |
| コンテキスト | セッションごとにリセット | 会話履歴を保持 |
| 自律性 | 応答のみ | アンビエントモードで自発通知 |

### Enterprise 環境での評価

freee の Senior AI Platform Engineer による約1時間の検証では、Slack 上の AI エージェント連携に使われてきた **OpenClaw や Hermes-Agent の完全な代替**になり得ると評価された。Anthropic が直接提供するため、Enterprise 環境内で安全に運用できる。

### 代表的ワークフロー: フィードバック → チケット → PR

"Code with Claude" イベントで共有された事例として、Slack に投稿されたユーザー/営業フィードバックをエージェントが自動でチケット化し、さらに自動で PR を生成する流れがある。チャンネルを監視して新しいフィードバックに自律対応するエージェントとして機能する。

## 関連ページ

- [OpenClaw](/blogs/wiki/tools/openclaw/) — Claude Tag が代替し得る Slack 連携ツール
- [Claude Code](/blogs/wiki/tools/claude-code/) — 同じ Anthropic のエージェント環境
- [マルチエージェント調整パターン](/blogs/wiki/concepts/multi-agent-coordination-patterns/) — チーム型エージェント運用の設計

## ソース記事

- [Claude Tag を Enterprise 環境で検証: OpenClaw 代替と Slack 自動化の可能性](/blogs/posts/2026/06/claude-tag-enterprise-slack-workflow/) — 2026-06-24
