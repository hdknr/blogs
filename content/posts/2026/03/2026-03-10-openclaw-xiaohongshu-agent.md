---
title: "OpenClaw × 小紅書 — AI エージェントが SNS アカウントを完全自動運営する時代"
date: 2026-03-10
lastmod: 2026-03-10
draft: false
source_url: "https://github.com/hdknr/blogs/issues/1#issuecomment-4034084623"
categories: ["AI/LLM"]
tags: ["openclaw", "agent", "mcp"]
---

中国の SNS「小紅書（Xiaohongshu / RED）」で、**AI エージェントがアカウントを完全自動運営している事例**が話題になっている。いち氏（[@ichiaimarketer](https://x.com/ichiaimarketer)）が[紹介したツイート](https://x.com/ichiaimarketer/status/2031135692210807291)によると、「虾薯（シャーシュー）」というアカウントは人間ではなく AI エージェントが運営しており、投稿の作成から公開、コメント返信、バズったコンテンツの分析・再現まで、すべて自動で行われている。

## 仕組み：2 つのスキルの連携

このシステムは、OpenClaw のスキル（プラグイン）として公開されている 2 つの GitHub プロジェクトで構成されている。

### Auto-Redbook-Skills（コンテンツ制作）

[comeonzhj/Auto-Redbook-Skills](https://github.com/comeonzhj/Auto-Redbook-Skills) — AI による記事作成と画像生成、自動公開を担当する。

- AI がテーマに沿った投稿文を自動生成
- 8 種類のテンプレートからカバー画像を自動レンダリング
- 小紅書への自動公開

### xiaohongshu-ops-skill（運営オペレーション）

[Xiangyu-CAS/xiaohongshu-ops-skill](https://github.com/Xiangyu-CAS/xiaohongshu-ops-skill) — アカウントの日常運営を自動化する。

- 投稿の自動公開スケジューリング
- コメントへの自動返信（アカウントのペルソナに合わせた口調で）
- バズった投稿の分析と複製（「爆款復刻」）
- アカウントごとのキャラクター設定

この 2 つが連携することで、**AI が記事を書き → カバー画像を生成 → 自動公開 → コメントに返信 → バズコンテンツを分析して再現**という完全自動のループが実現している。

## OpenClaw エコシステムの広がり

OpenClaw は 2026 年に入って爆発的に成長し、GitHub のスター数は 2,400 万を超えた。個人の端末上で動作する AI エージェントで、WhatsApp・Telegram・Discord などのチャットアプリを通じて操作できる。

小紅書以外にも、TikTok や各種 SNS プラットフォーム向けのスキルが続々と公開されており、「一人で複数アカウントをマトリクス運営する」ことが技術的に可能になっている。

関連プロジェクトも活発だ：

- [openclaw-xhs](https://github.com/zhjiang22/openclaw-xhs) — MCP 統合 + ホットトピック追跡 + 個人メモリ機能
- [xiaohongshu-skills](https://github.com/autoclaw-cc/xiaohongshu-skills) — OpenClaw や Claude Code の SKILL.md 形式に対応

## コンプライアンス上の懸念

技術的には可能だが、**プラットフォームの利用規約やコンプライアンスの問題は無視できない**。

- **コンテンツ審査**: 自動生成コンテンツに対する各プラットフォームの規制は強化傾向
- **アカウント制限**: ボット検出による凍結やシャドウバンのリスク
- **法的リスク**: AI 生成コンテンツの開示義務に関する各国の法規制
- **倫理的問題**: 人間を装った AI アカウントの透明性

ブラウザ自動化ベースで動作するため API 利用規約違反のリスクは低いとされるが、プラットフォーム側の対策も日々進化している。

## SNS 運用の「次のフェーズ」

いち氏が「SNS 運用、次のフェーズに入ったかもしれません」と述べているように、この事例が示唆するのは SNS マーケティングの構造変化だ。

従来の SNS 運用は「人間がコンテンツを考え、投稿し、エンゲージメントを管理する」ものだった。AI ツールの導入後も、補助的な使い方（キャプション生成、画像編集など）が主流だった。しかし OpenClaw のスキルエコシステムは、**企画から運営までの全プロセスを AI に委譲する**モデルを実現しつつある。

ただし、本当に価値のあるコンテンツを継続的に生み出せるかは別問題だ。AI が量産するコンテンツとフォロワーの信頼関係をどう構築するか — そこが次の課題になるだろう。

## 参考

- [いち氏のツイート](https://x.com/ichiaimarketer/status/2031135692210807291) — 元の紹介投稿
- [開発者 Hailey のツイート](https://x.com/IndieDevHailey/status/2029742108383531497) — 虾薯アカウントの実演動画
- [Auto-Redbook-Skills](https://github.com/comeonzhj/Auto-Redbook-Skills) — コンテンツ制作スキル
- [xiaohongshu-ops-skill](https://github.com/Xiangyu-CAS/xiaohongshu-ops-skill) — 運営自動化スキル
- [OpenClaw 小紅書運用ガイド（知乎）](https://zhuanlan.zhihu.com/p/2014084383691286125) — 20 日で 0→1000 フォロワーの実例
