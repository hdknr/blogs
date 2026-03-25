---
title: "Perplexity Personal Computer — Mac mini を常時稼働AIエージェントに変える新サービス"
date: 2026-03-12
lastmod: 2026-03-12
draft: false
source_url: "https://github.com/hdknr/blogs/issues/1#issuecomment-4044242848"
categories: ["AI/LLM"]
tags: ["agent", "llm", "openclaw"]
---

Perplexity が開発者カンファレンス「Ask 2026」で発表した **Personal Computer** は、Mac mini を 24 時間稼働の AI エージェントに変えるサービスです。OpenClaw と同じ「コンピュータ操作型 AI」の領域に参入しつつ、クラウド管理・サブスクリプション型という独自のアプローチを採っています。

## Personal Computer とは

Personal Computer は Perplexity が提供する 2 つ目の AI エージェント製品です。

| | Perplexity Computer | Personal Computer |
|---|---|---|
| **実行環境** | クラウドサンドボックス | ユーザーの Mac mini（ローカル） |
| **特徴** | タスク分解・マルチモデル | ローカルファイル・アプリアクセス |
| **発表** | 2026年2月 | 2026年3月（Ask 2026） |

Personal Computer はハードウェアではなく、Mac mini 上で常時稼働する **永続的な AI エージェント** です。ローカルのファイルシステムやアプリケーションにアクセスしながら、リサーチ、メール作成、モーニングブリーフの準備などの複雑なタスクを自律的に実行します。

## マルチモデルアーキテクチャ

Perplexity Computer / Personal Computer の基盤となるのは **19 以上のフロンティアモデル** を統合するマルチモデル設計です。

- **Claude Opus 4.6**（Anthropic）: コアオーケストレーションエンジン
- **Gemini**（Google）: ディープリサーチ
- **ChatGPT 5.2**（OpenAI）: 長文コンテキスト処理
- **Grok**（xAI）: 軽量タスクの高速処理
- **Veo 3.1**（Google）: 動画生成
- **Nano Banana**: 画像生成

タスクを自動的にサブタスクに分解し、各サブタスクに最適なモデルを割り当てる「モデルアグノスティック設計」により、モデルの進化に柔軟に対応できます。

## 料金と利用条件

| プラン | 月額 | 状態 |
|---|---|---|
| **Max** | $200 / 年額 $2,000 | ウェイトリスト受付中 |
| Pro | $20 | 数週間以内に提供予定 |
| Enterprise | - | 数週間以内に提供予定 |

Max プランでは月 10,000 クレジットが付与され、支出上限の設定も可能です。

## OpenClaw との比較

Personal Computer は OpenClaw と同じ「AI がコンピュータを操作する」カテゴリに属しますが、設計思想は大きく異なります。

### 共通点

- コンピュータ操作型の AI エージェント
- ファイルシステムやアプリケーションへのアクセス
- 複雑なマルチステップタスクの自律実行

### 相違点

| | OpenClaw | Perplexity Personal Computer |
|---|---|---|
| **実行方式** | ローカル実行（オープンソース） | クラウド管理 + ローカルデバイス |
| **モデル** | Claude 単体 | 19+ モデルのオーケストレーション |
| **料金** | API 従量課金 | $200/月 サブスクリプション |
| **セキュリティ** | ユーザー責任 | 操作確認・監査ログ・キルスイッチ |
| **アプリ連携** | MCP サーバー経由 | 400+ アプリ統合（ビルトイン） |

Perplexity のアプローチは、OpenClaw のメール誤削除インシデントを教訓として、すべてのセンシティブな操作にユーザー確認を必須とし、監査証跡（audit trail）とキルスイッチを標準搭載しています。

## 「技術を作ったのではなく、摩擦を取り除いた」

ツイートの指摘にもあるように、Perplexity が独自に開発した技術は多くありません。コアモデルは Anthropic、Google、OpenAI 等の既存モデルを利用しています。Perplexity の価値は「**誰でも使えるようにした**」点にあります。

- 複数モデルの自動選択・オーケストレーション
- セットアップ不要のマネージドサービス
- エンタープライズ向けのセキュリティ・コンプライアンス
- 400+ のアプリ統合をビルトインで提供

$21B の評価額は、技術力ではなく「使いやすさ」と「誰が使えるか」のスケーラビリティに基づいています。これは AI エージェント市場が「技術開発」フェーズから「プロダクト化」フェーズに移行していることを示唆しています。

## まとめ

Perplexity Personal Computer は、OpenClaw が切り拓いた「コンピュータ操作型 AI エージェント」の市場に、クラウドマネージド・サブスクリプション型のプロダクトとして参入した注目のサービスです。技術そのものよりも、摩擦のない UX とエンタープライズ対応が差別化ポイントとなっています。

開発者にとっては、OpenClaw のオープンソースアプローチとの棲み分けがどう進むかが注目点です。

## 参考リンク

- [Perplexity Personal Computer ウェイトリスト](https://www.perplexity.ai/personal-computer-waitlist)
- [Perplexity Computer とは？ - TECH NOISY](https://tech-noisy.com/2026/02/27/perplexity-computer-multi-agent-ai-launch-2026/)
- [9to5Mac: Perplexity's Personal Computer](https://9to5mac.com/2026/03/11/perplexitys-personal-computer-is-a-cloud-based-ai-agent-running-on-mac-mini/)
