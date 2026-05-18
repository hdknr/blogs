---
title: "ObsidianとN8Nで月$120の「一人ヘッジファンド」を構築 — 6ヶ月で$180,000を稼いだ自動トレーディングAIの全仕組み"
date: 2026-05-13
lastmod: 2026-05-13
slug: "obsidian-n8n-trading-ai"
draft: false
source_url: "https://github.com/hdknr/blogs/issues/1#issuecomment-4435889027"
categories: ["AI/LLM"]
tags: ["Obsidian", "n8n", "自動化", "トレーディング", "第二の脳"]
---

海外で話題になっているある個人トレーダーの話が、X（旧Twitter）で拡散されている。彼はObsidianとN8Nを組み合わせて「自動トレーディングAI」を構築し、6ヶ月で$180,000（約2,700万円）を稼ぎ出したという。月のAPIコストはたった$120。クラウドサーバーも、アナリストチームも、Bloombergターミナルも不要だ。

元ネタのツイートは[@browomo](https://x.com/browomo)によるもので、4,500以上のいいね、90万回以上の閲覧数を記録している。

## システムの全体像

このシステムの核心は、Obsidianのローカルvaultをナレッジの「中枢」として、N8Nの6本のワークフローパイプラインが情報を自動収集・分析・配信する構造にある。構成要素は次の通りだ。

- **ハードウェア**: 自宅のMac Mini（ローカルでvaultを保管・パイプラインを常時稼働）
- **モバイル**: iPhoneでvaultにアクセス・アイデアをキャプチャ
- **コスト**: Readwise・Whisper API・N8Nホスティングのサブスクリプションで月約$120

伝統的なクオンツファンドが同等のインサイトフローのために8人のチームを雇っている一方、このシステムはその機能を個人レベルで再現している。

## VAULT.md に書かれた「AIアナリストへの指示」

システムの起点となるのは、Obsidian vaultのルートに置かれた `VAULT.md` ファイルだ。ここにAIアナリストへの役割定義と行動指針が記されている：

```text
you are the AI analyst of a solo trader. you read his vault every morning at 6:00,
find connections between fresh and old notes, and deliver 3 trading ideas he can verify
in the hour before the market opens.

pipelines:

// Reader (pulls every article and highlight from Readwise, Twitter bookmarks, and Kindle into /notes)
// Listener (transcribes podcasts through Airr and voice notes through Whisper, puts them in /notes)
// Catcher (accepts any message from the Telegram bot and writes it to /inbox with a timestamp)
// Connector (every night reads across the entire vault and updates the connection graph between 4,000 notes)
// Briefer (at 6:00 AM writes a brief: 3 trading ideas for today plus the emerging thesis of the week, puts it in /inbox)
// Mobile (lives in the iPhone, answers any question about the vault by voice, and confirms alerts while the owner is on the go).

you wake the owner with a push notification only when a fresh note contradicts his active thesis
or when 1 of the 3 morning ideas has a confidence score above 90%.
```

この指示が秀逸なのは、AIに「何を自律的にやるか」と「いつ人間を介入させるか」の境界を明確に定義している点だ。

## 6本のパイプラインの役割

N8Nで構築された6本のパイプラインは、それぞれ独立した役割を持つ。

### Reader — 情報収集

ReadwiseのハイライトやKindleのメモ、Twitterブックマークを自動的に `/notes` へ取り込む。1日あたり約80件の記事・ハイライトを処理する。

### Listener — 音声・ポッドキャスト処理

AirrとWhisper APIを通じてポッドキャストや音声メモをテキスト化し `/notes` に格納する。週4〜6本のポッドキャストを処理。

### Catcher — モバイルからのアイデア収集

Telegramボットを介して外出先でのアイデアや思いつきを受け取り、タイムスタンプ付きで `/inbox` に書き込む。1日平均15〜20件をキャプチャ。

### Connector — ナレッジグラフの更新

毎晩、vault全体の4,000ノートを横断的に読み込み、ノート間の接続グラフを更新する。毎晩25〜30の新しいエッジを追加。

### Briefer — 朝のブリーフィング生成

毎朝6時に3つのトレーディングアイデアと「今週の浮上テーマ」をまとめたブリーフを `/inbox` に配信する。

### Mobile — スマートフォン対応エージェント

iPhoneからvaultへの音声質問に答え、移動中でもアラートを確認できる。「先週この銘柄について何を書いたか」「NVDA ロングを支持するソースはどれか」といった質問に即答する。

## 実際のブリーフィング例

ある月曜日の朝のブリーフがこのようなものだったという：

```text
reader: 78 materials added over the weekend, 11 of them about semiconductors,
4 about energy, 3 about biotech. passing to connector.

connector: 27 new connections found between fresh materials and the vault,
the strongest one is that the Goldman report from Wednesday matches
the NVDA thesis you wrote 3 weeks ago.

briefer: 3 trading ideas for today:
  long NVDA (confidence 0.84),
  short Tesla at the close of the quarterly report (0.71),
  watch URI (0.62).
  emerging thesis of the week: the market is underpricing capex on data centers.

alert: your fresh note about long-term risk in semis contradicts the NVDA thesis.
       sending for review.
```

Connectorが新しい情報と過去のノートの接続を発見し、Brieferが確信度スコア付きでトレードアイデアを提示している。そして、新しいノートが既存のテーゼと矛盾する場合のみオーナーに通知が飛ぶ。

## 「通知しない」設計の重要性

このシステムで特に注目すべきは「何を通知しないか」の設計だ。

AIアナリストが毎朝アイデアを届けても、ただちに通知はしない。通知が飛ぶのは次の2条件のみ：

1. 新しいノートがアクティブなテーゼと矛盾した場合
2. 3つのアイデアのうち1つの確信度スコアが90%を超えた場合

これにより、トレーダーはジムや朝食中にiPhoneで音声確認できる。ニューヨーク市場が開く前に判断・発注まで完結する設計だ。

## なぜこの構成が強いのか

**ローカルファースト**: Mac Miniのローカル環境で全てが完結し、クラウドへのデータ送信を最小化。プライバシーを確保しつつ、ランニングコストを抑えている。

**ナレッジの複利効果**: 4,000ノートの接続グラフが毎晩更新されることで、古い知識と新しい情報が自動的に結びつく。人間が気づかないパターンをAIが発見する。

**コンテキスト保持**: Readwise・Kindle・Podcast・音声メモ・Twitterブックマークが全て同じvaultに集約されるため、AIは全てのコンテキストを横断的に参照できる。

**コスト効率**: 月$120のAPIコストで、月平均$30,000の利益を生み出しているとされる。ROIは250倍。

## 同様のシステムを構築するために必要なもの

このシステムを再現するために必要なツールと概算コスト：

| ツール | 用途 | 概算コスト |
|--------|------|-----------|
| Obsidian | ナレッジvault | 無料（商用は$50/年） |
| N8N | ワークフロー自動化 | セルフホスト無料 or クラウド€20〜/月 |
| Readwise | ハイライト同期 | $9.99/月（年払い$5.59/月） |
| Whisper API | 音声テキスト化 | 使用量課金（$0.006/分） |
| Airr | ポッドキャスト | $9.99/月 |
| Telegram Bot | モバイルキャプチャ | 無料 |
| LLM API | AI分析 | 最大費用の大半 |

ツール自体は全て既存のものの組み合わせだ。重要なのはVAULT.mdの「役割定義」と、6本のパイプラインのアーキテクチャ設計だ。

## まとめ

このシステムが示すのは、「AIの活用は大企業だけのものではない」という事実だ。適切なアーキテクチャ設計と、既存ツールの組み合わせにより、個人でも機関投資家レベルのインサイトパイプラインが構築できる時代になった。

月$120のAPIコストで6ヶ月$180,000という数字は飛び抜けているが、構造そのものはナレッジワーカー全般に応用できる。Obsidian + N8Nという組み合わせは、トレーディング以外にも研究・コンテンツ制作・意思決定支援など、あらゆるドメインに転用可能だ。

---

**元ツイート（英語）**: [@browomo on X](https://x.com/browomo/status/2052333456416186585)
**日本語紹介**: [@obsidianstudio9 on X](https://x.com/obsidianstudio9/status/2054124441215619246)
