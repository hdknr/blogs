---
title: "期限切れ特許を Claude に食わせて Amazon で売る — 420万件のパブリックドメイン特許から商品を発掘するパイプライン"
date: 2026-04-30
lastmod: 2026-04-30
slug: "claude-expired-patents-product-discovery"
draft: false
source_url: "https://github.com/hdknr/blogs/issues/1#issuecomment-4349314496"
categories: ["AI/LLM"]
tags: ["Claude", "特許", "ビジネス", "python", "markitdown", "自動化", "USPTO"]
description: "期限切れ特許420万件をClaudeでスコアリングし、Alibabaで製造してAmazonで販売するパイプラインを個人で構築する手法を解説。製造原価$1.80、Amazon販売価格$11.99の具体的なユニットエコノミクス付き。"
---

> この発想、めちゃくちゃ盲点だったわ。Claudeに期限切れ特許を食わせて、誰も作らなくなった商品を掘り起こし、それを1つすでに生産開始したらしい。420万件以上のパブリックドメイン特許から、シンプルに作れて売れそうなやつをAIがピックアップ。こういう新しいハックポイントを力技じゃなく出来るってのも、また新しいターニングポイントではある。
> — [@tanaka_yuto](https://x.com/tanaka_yuto/status/2049463805873438753)

@gippp69 が公開した手法が話題だ。期限切れ特許を Claude に大量投入し、商品化できそうなものをスコアリングして Alibaba で製造委託、Amazon で販売するパイプラインを個人で構築した。

設計図（特許文書）のコスト：$0。製造コスト：$1.80/個。Amazon 販売価格：$11.99。

## なぜ「期限切れ特許」なのか

特許は本来、発明者に一定期間の独占権を与える代わりに、発明の詳細を全て公開することを義務付けている。これが期限切れになると、**詳細な製造仕様書が誰でも無料で使えるパブリックドメイン資産**になる。

過去10年間だけで、米国では420万件以上の特許が失効している。失効理由はさまざまだ：

- 企業の倒産
- 更新費用（$1,600程度）の未払い
- 買収後の整理
- 事業方針の変更

大事なのは、**製品が失敗したのではなく、製品を守っていた企業が消えた**という点だ。需要は存在したまま、供給だけが途絶えた商品が大量に埋もれている。

1件あたり何十ページもある特許文書を人間が読んで評価するのは現実的ではない。4,200,000件など到底無理だ。だが Claude なら読める。

## パイプライン全体像

```
USPTO Bulk Data API
       │
       ▼
  Python スクレイパー（カテゴリ・出願者規模・日付でフィルタ）
       │
       ▼
  markitdown（特許文書を Markdown に変換）
       │
       ▼
  files-to-prompt（50件ずつバッチ化）
       │
       ▼
  Claude スコアリングパイプライン（1〜10点で評価）
       │
       ▼
  Google Patents（スコア7以上の案件を詳細確認）
       │
       ▼
  Alibaba（特許図面を送って製造見積もり）
       │
       ▼
  Amazon 出品
```

### Step 1: 特許データの取得とフィルタリング

USPTO（米国特許商標庁）は Bulk Data ポータルで全特許の全文をパブリックドメインで公開している。

```python
# patent_filter.py — 一次フィルタ
FILTERS = {
    "status": "expired",
    "type": "utility",          # デザイン特許は除外
    "assignee_size": "small",   # IBM・Samsung などは除外
    "categories": [
        "household",
        "tools",
        "pet_products",
        "office_supplies",
        "garden",
        "kitchen"
    ],
    "expired_after": "2014-01-01",
    "min_claims": 3,
    "max_claims": 25            # 請求項が多すぎる = 複雑すぎる
}
```

大企業の特許は製造に専用設備が必要だったり、法務リスクが高かったりする。中小企業のシンプルな消費者向け製品に絞るのがポイントだ。このフィルタで約34万件まで絞り込んだ。

### Step 2: markitdown で Claude が読める形式に変換

特許文書は PDF や独自形式が多い。[microsoft/markitdown](https://github.com/microsoft/markitdown)（GitHub 121K+ stars）を使えば、あらゆる形式のドキュメントをクリーンな Markdown に変換できる。

```bash
markitdown patent_US8234811.pdf > patent_US8234811.md
```

### Step 3: files-to-prompt でバッチ化

[simonw/files-to-prompt](https://github.com/simonw/files-to-prompt)（GitHub 3K+ stars）で、50件の特許 Markdown をまとめて1つのプロンプトコンテキストに詰め込む。1バッチあたりの処理時間は約 90 秒（@gippp69 の報告）。

### Step 4: Claude によるスコアリング

核心部分のシステムプロンプト：

```
ROLE: Patent Commercial Viability Analyst

INPUT: Expired US utility patent (full text + claims)

ANALYZE AND RETURN:
─────────────────────────────────────────────────
1. PLAIN_ENGLISH:    What does this actually do?
2. CONSUMER_VIABLE:  Could a consumer version exist? (yes/no)
3. BOM_ESTIMATE:     Bill of materials at 1000 MOQ (Alibaba)
4. AMAZON_GAP:       Does any current listing use this exact mechanism?
5. REVIEW_SIGNAL:    What do competing product reviews complain about?
6. SCORE:            Commercial viability 1-10

REJECT IMMEDIATELY:
- Requires FDA/FCC clearance
- Needs custom semiconductor fab
- Chemical formulation patents
- Software/algorithm patents
- Requires tooling over $50K

RETURN FORMAT: JSON only. No commentary.
```

このプロンプトの設計が秀逸だ。スコアだけでなく「Amazon に既存品があるか」「競合レビューの不満点」まで一度に評価させることで、商品機会のサイズを自動的に推定できる。

## 実際に見つかった商品

80件に1件程度でスコア7以上が出てくる。3週間で6件の有望案件を発見した。

### Hit #1 — 自己給水プランターインサート

パッシブウィッキングシステム。ポンプ不要、電池不要、可動部品なし。

- **特許元**: オハイオ州の園芸ツール会社（従業員12名）
- **特許取得**: 2009年
- **失効理由**: 2016年に倒産、$1,600の更新費用を誰も払わなかった

Claude の評価出力：

```json
{
  "patent_id": "US8,234,811",
  "plain_english": "Self-watering planter insert with passive felt wick.
    Pulls moisture from reservoir to soil via capillary action.
    No pump, no battery.",
  "consumer_viable": true,
  "bom_estimate": "$1.60-2.10 at 1000 MOQ",
  "amazon_gap": true,
  "review_signal": "Competing products: water pools at bottom,
    wicks clog after 2 weeks, not optimized for small pots",
  "score": 8
}
```

Amazon の既存品レビューには「底に水が溜まる」「芯が2週間で機能しなくなる」という不満が並ぶ。この特許はまさにそれを解決している。

- Alibaba 見積もり：$1.80/個（1,000個 MOQ）
- Amazon 販売価格帯：$14〜22
- 月間検索ボリューム：118,000
- **現在すでに生産開始、Amazon 出品準備中**

### Hit #2 — 折りたたみペット用水飲みボウル

片手でスナップ開閉できるロック機構付き。ヒンジなし、シリコン折りたたみなし、可動部品なし。

```
製品比較 — 折りたたみペット用ボウル
────────────────────────────────────────────────
                    特許設計         Amazon 上位5品
機構:               スナップロック    シリコン折りたたみ
可動部品:           0                2〜4
故障率:             約2%             約31%（レビューより）
単価（1K MOQ）:    $0.95            $1.40〜2.20
形状保持:          ○               ×（荷重で潰れる）
片手操作:          ○               ×
```

- Alibaba 見積もり：$0.95/個
- Amazon 価格帯：$8〜15
- マージンは「absurd」（原文のまま、"驚くほど高い"という意）

### Hit #3 — ケーブル管理クリップ

粘着ベース + ケーブル径に自動フィットするラチェット顎。2mm〜12mmのケーブルをサイズ交換なしで固定できる。

```
Unit Economics — ケーブルクリップ（30個パック）
─────────────────────────────────────────────
製造（30 x $0.12）:     $3.60
パッケージ＋ラベル:     $0.40
FBA への輸送:           $0.85
Amazon FBA 手数料:      $3.20
PPC（推定）:            $1.10
─────────────────────────────────────────────
合計コスト:             $9.15
販売価格:               $11.99
純利益:                 $2.84（23.7%）

月800個販売時:          月$2,272 純利益
```

## なぜ特許文書は「製造マニュアル」なのか

特許を取得するには、その分野の専門家が再現できるだけの技術的詳細を開示しなければならない。寸法、公差、素材、組み立て順序、性能仕様 — 工場が製造見積もりを出すために必要な情報がすべて含まれている。

特許文書はこんな見た目をしている：

```
"A fluid-wicking apparatus comprising a porous fibrous
member disposed within a reservoir cavity, wherein said
member maintains capillary continuity with a growth
medium positioned superiorly, characterized in that
the fibrous member exhibits a mean pore diameter of
between 40 and 120 micrometers..."
```

普通の人はこれを見てタブを閉じる。Claude はこれを読んで上記の JSON を返す。

**これが唯一のエッジだ**。より良い製品アイデアでも、賢い市場仮説でも、秘密の Amazon ハックでもない。人間がスキップする法律用語に見えるドキュメントを読む能力だけ。

## 使用したツール一覧

| ツール | 用途 | 入手先 |
|--------|------|--------|
| USPTO Bulk Data | 特許データ取得 | [bulkdata.uspto.gov](https://bulkdata.uspto.gov) |
| markitdown | 文書を Markdown 変換 | [microsoft/markitdown](https://github.com/microsoft/markitdown) |
| files-to-prompt | バッチ化 | [simonw/files-to-prompt](https://github.com/simonw/files-to-prompt) |
| Claude（Skills 経由） | スコアリング | [Claude Code Skills](https://docs.anthropic.com/ja/docs/claude-code/overview) |
| MCP | ツール連携 | [modelcontextprotocol](https://github.com/modelcontextprotocol/modelcontextprotocol) |
| Google Patents | 特許詳細確認 | [patents.google.com](https://patents.google.com) |
| Alibaba | 製造見積もり | — |

Claude ワークフロー全体は Skills フレームワークを使って再現可能なパイプラインとして構築されており、外部ツールとの接続には [MCP（Model Context Protocol）](https://github.com/modelcontextprotocol/modelcontextprotocol) が使われている。

## 期限切れ特許が切り拓く、AI 時代の新しいビジネス資産クラス

このアプローチが面白いのは、既存市場のトレンドを追いかけるのではなく、「かつて価値があったが誰も作らなくなった製品」を探すという逆張りの発想にある。

特許を取得するには当時 $15,000 程度の費用がかかる。それほどのコストをかけて守ろうとした技術が、維持費 $1,600 を誰も払わなかっただけでパブリックドメインになっている。420万件分。

Claude がなければ、人間にはこのスケールの探索は不可能だった。AI が「新しい仕事のやり方」を生み出しているというより、**AI によって初めてアクセス可能になった資産クラスが存在する**、という事例として記憶しておきたい。
