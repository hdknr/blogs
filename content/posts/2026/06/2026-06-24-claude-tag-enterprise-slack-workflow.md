---
title: "Claude Tag を Enterprise 環境で検証: OpenClaw 代替と Slack 自動化の可能性"
date: 2026-06-24
lastmod: 2026-06-24
slug: "claude-tag-enterprise-slack-workflow"
draft: false
source_url: "https://github.com/hdknr/blogs/issues/1#issuecomment-4785321009"
categories: ["AI/LLM"]
tags: ["Claude Tag", "Enterprise", "Slack", "AIエージェント", "ワークフロー自動化"]
---

## はじめに

2026 年 6 月 23 日、Anthropic は **Claude Tag** を正式に発表しました。Claude Tag は Slack チャンネルに Claude をチームメンバーとして参加させ、プロアクティブに動作する新しい仕組みです。

> "We're launching Claude Tag today. Tag Claude into Slack and it works in channel with you. It's proactive, multiplayer, with its own identity and memory. […]"  
> — Boris Cherny, Claude Code @anthropicai

本記事では、freee の Senior AI Platform Engineer である Jaesoon Jeong 氏（[@dev_soon0_0](https://x.com/dev_soon0_0)）が Enterprise 環境で約 1 時間試した体験をもとに、Claude Tag の実用性を掘り下げます。

## Enterprise 環境で約 1 時間試してわかったこと

### OpenClaw・Hermes-Agent の完全な代替になり得る

Jeong 氏の検証では、**OpenClaw や Hermes-Agent といった外部ツールの完全な代替**になり得ると評価しています。

これらのツールはこれまで、Slack 上での AI エージェント連携を実現するために使われてきましたが、Enterprise 環境で安全に運用するにはセキュリティ上の懸念や独自インフラの整備が必要でした。Claude Tag は Anthropic が直接提供するため、**安全な Enterprise 環境内で実行できる基盤**として十分に機能します。

### "Code with Claude" イベントでの事例: フィードバック → チケット → PR の自動化

Anthropic 主催の **"Code with Claude"** イベントでも、同様の活用事例が Anthropic の社員から直接共有されました。

その事例は以下の通りです。

1. ユーザーフィードバックや営業経由で上がってきたフィードバックが **Slack チャンネルに投稿される**
2. エージェントが自動でそのフィードバックを**チケットとして収集する**
3. さらに**自動で PR を生成する**

このワークフローは Claude Tag で実現できるものです。チャンネルを監視し、新しいフィードバックが来たら自律的に対応するエージェントとして Claude Tag が機能します。

## Claude ライセンスを持たないユーザーにも開放される

Claude Tag の大きな特徴のひとつが、**Claude ライセンスを持っていないユーザーでも利用できる**点です。

これにより、AI エージェントの「同僚」を手軽に構築できる範囲が大幅に広がります。従来は Claude を直接使えるユーザーに限られていた恩恵が、Slack を介してチーム全員に届くようになります。

- エンジニアだけでなく、営業・カスタマーサポート・バックオフィスのメンバーも同じ Claude を活用できる
- AI エージェントを「ツール」としてではなく「同僚」として扱う文化が醸成されやすい

## Enterprise 環境での Claude Tag の強み

| 観点 | 従来の Slack Bot / 外部ツール | Claude Tag |
|------|-------------------------------|------------|
| セキュリティ | 独自インフラが必要 | Anthropic 管理で安全 |
| セットアップ | 複雑な設定が必要 | 4 ステップで完了 |
| ライセンス | 利用者全員が個別に必要 | チャンネル単位で共有 |
| コンテキスト | セッションごとにリセット | 会話履歴をコンテキストとして保持 |
| 自律性 | 呼びかけに応答するのみ | アンビエントモードで自発通知 |

## まとめ

Claude Tag は単なる「Slack に AI を繋ぐ」機能を超えています。Enterprise 環境での 1 時間の検証から見えたのは、**安全・手軽・ライセンス不要**という三拍子が揃った実用的なツールだという評価です。

特に「フィードバック → チケット → PR」という自動化ワークフローは、開発チームの生産性向上に直結するユースケースです。OpenClaw や Hermes-Agent を使っていた企業にとっては、より安全で管理しやすい代替として検討する価値があります。

- ソース: [X (@dev_soon0_0)](https://x.com/dev_soon0_0/status/2069491713564139781)
- 公式発表: [Introducing Claude Tag](https://www.anthropic.com/news/introducing-claude-tag)
