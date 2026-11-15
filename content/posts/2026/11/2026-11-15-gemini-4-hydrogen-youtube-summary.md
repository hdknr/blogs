---
title: "Gemini 4 Hydrogen の性能と料金まとめ — Gemini in Chrome で YouTube 動画を要約する方法も"
date: 2026-11-15
lastmod: 2026-11-15
slug: "gemini-4-hydrogen-youtube-summary"
draft: false
source_url: "https://github.com/hdknr/blogs/issues/694#issuecomment-6892948460"
categories: ["AI/LLM"]
tags: ["gemini", "Gemini 4", "YouTube", "プロンプトエンジニアリング", "Gemini in Chrome"]
---

## はじめに

2026 年 11 月 12 日、Google が Gemini 4 ファミリーの高速モデル **Gemini 4 Hydrogen** を公開しました。Gemini 3.8 Flash の 2.5 倍速く、API 料金は 100 万トークンあたり入力 $1.50・出力 $7.50 です。公開から数日で、X では実際に使った人の感想が流れてきています。

その中で目を引いたのが、StudioYebisu さん（[@studio_yebisu](https://x.com/studio_yebisu/status/2121835594674561098)）の投稿です。投稿は「私の中で情報系のYouTubeを自分で見る時代終わったわ。」という一文で始まります。YouTube を開いたまま Gemini in Chrome に要約プロンプトを貼るだけで、動画の要点がすぐにつかめるという内容です。この投稿を引用したなゆえんじんさん（[@nayuengin](https://x.com/nayuengin/status/2121839284613533932)）も「Hydrogenすごいぞ」と評価していました。

この記事では、まず Google の発表をもとに Gemini 4 Hydrogen がどんなモデルかを整理します。そのうえで、投稿で紹介された「YouTube 動画を Gemini in Chrome で要約する」使い方を、自分で試せる形にまとめます。なお、Gemini in Chrome が Hydrogen で動いているかは公式には明らかにされていないため、その点も合わせて整理します。

## 登場するプロダクトと用語

| 名前 | 説明 |
|---|---|
| Gemini 4 Hydrogen | Gemini 4 ファミリーの高速・低コストモデル。日々のコーディングとエージェント処理向け |
| Gemini 4 Carbon | 同ファミリーのフロンティアモデル。長く深い推論を受け持つ |
| Gemini 4 Argon | 同ファミリーのもう一つのフロンティアモデル |
| Gemini in Chrome | Chrome ブラウザに組み込まれた Gemini。開いているタブの内容を踏まえて質問に答える |
| 思考レベル | 推論にかける量の設定（段階は後述） |

## Gemini 4 Hydrogen とは

Google は Hydrogen を「エージェント処理の日常使い（daily driver）」と位置づけています。深い推論は Carbon や Argon に任せ、Hydrogen は速さと効率で日々のタスクをこなす役回りです。単体で使うだけでなく、Carbon と組み合わせて使うことも想定されています。

### Gemini 4 Hydrogen の速度とベンチマーク

Google の発表による主な数字は次のとおりです。いずれも Google 自身の発表値である点に注意してください。

- **速度**: 既定の思考レベル（high）で、Gemini 3.8 Flash より 2.5 倍速くタスクを終える
- **Artificial Analysis Intelligence Index**: high で 51、xhigh で 54。フロンティアモデルの Argon（50）と同等以上
- **Terminal-Bench 4.1**: 57%（Gemini 3.8 Flash は 18.2%）
- **ハルシネーション**: 事実と異なる主張が Gemini 3.8 Flash の 5 分の 1 以下

高速・低コスト向けのモデルでありながら、フロンティアモデルの Argon に並ぶスコアを出している点が目を引きます。

### Gemini 4 Hydrogen の API 料金とモデル ID

| 項目 | 内容 |
|---|---|
| モデル ID | `gemini-4-hydrogen` |
| コンテキストウィンドウ | 入力 100 万トークン |
| 思考レベル | low / medium / high（既定）/ xhigh |
| 料金（有料 API） | 入力 100 万トークンあたり $1.50、出力 100 万トークンあたり $7.50 |

料金はコンテキストの長さによらず一定です。API から呼ぶ場合は、まず SDK を入れて API キーを設定します。

```bash
pip install google-genai
export GEMINI_API_KEY="your-api-key"
```

最小のコード例は次のようになります。

```python
from google import genai

client = genai.Client()  # 環境変数 GEMINI_API_KEY を読む

response = client.models.generate_content(
    model="gemini-4-hydrogen",
    contents="Gemini 4 Hydrogen の特徴を 3 行で説明してください。",
)
print(response.text)
```

### どこで使えるか（Gemini アプリ・Google 検索・API）

- **Gemini アプリ（サブスクリプション利用者）**: モデル選択のドロップダウンから選べる
- **Gemini アプリ（無料ユーザー）**: プロンプトに合うと判断されたときに、自動のモデル選択で使われる
- **Google 検索**: 全世界の全ユーザーに順次展開
- **開発者向け**: Gemini API、Google AI Studio、Android Studio
- **企業向け**: Gemini for business、Google Antigravity、Gemini in Google Sheets（いずれも対象プランのみ）

なお、Google の発表には **Gemini in Chrome の名前は出てきません**。Gemini in Chrome が Hydrogen で動いているかどうかは公式には確認できていないため、ここは投稿者の体感として読んでおくのが安全です。

とはいえ、裏で動くモデルが何であれ、次に紹介する要約の使い方は今日から試せます。

## YouTube 動画を Gemini in Chrome で要約する

投稿で紹介されていた手順は、とても単純です。

1. Chrome で要約したい YouTube 動画を開く
2. Gemini in Chrome のパネルを開く
3. あらかじめ用意しておいた要約プロンプトを貼り付けて送る

投稿者は、YouTube の画面に組み込まれた Gemini よりもこちらのほうが要点がわかりやすいと述べています。また、要約から該当する時間位置や関連動画にそのまま飛べます。気になったところだけ動画で確かめる、という使い方ができるそうです。

### YouTube 要約プロンプトのテンプレート

投稿には実際のプロンプトが載っていますが、ここでは元の投稿を転載せず、同じ狙いで使えるプロンプトの例を示します。原文は[元の投稿](https://x.com/studio_yebisu/status/2121835594674561098)を参照してください。

```text
いま開いている YouTube 動画の内容を、次の形式で日本語でまとめてください。

1. この動画の結論を 1〜2 文で
2. 主要なポイントを 3〜7 個の箇条書きで（各項目に該当する時間位置を付ける）
3. 具体的な手順・数値・固有名詞があれば一覧に
4. 話し手の意見と事実を分けて書く
5. この動画を見るべき人・見なくてよい人

推測で補わず、動画で触れられていない内容は「動画内で言及なし」と書いてください。
```

ポイントは次の 3 つです。

- **出力の形を決めておく**: 毎回同じ構成で返ってくるので、複数の動画を比べやすくなる
- **時間位置を付けさせる**: 要約で気になった箇所だけを動画で確認できる
- **推測を禁じる**: 動画にない情報をもっともらしく補われるのを防ぐ

このプロンプトを macOS のユーザー辞書やランチャーアプリのスニペット機能に登録しておけば、動画を開くたびにすぐ呼び出せます。

### 使うときの注意

- **要約は動画の代わりにはならない**: 数値や手順など正確さが重要な箇所は、時間位置をたどって動画で確かめる
- **字幕のない動画は精度が落ちやすい**: 画面だけで説明する動画も同様。重要な箇所は動画で確認する
- **クリエイターへの配慮を忘れない**: 投稿者自身も、この使い方が YouTube のビジネスとぶつからないかを気にしていました。役に立った動画には、高評価やチャンネル登録で応えるのがよさそうです

## まとめ

- Gemini 4 Hydrogen は、Gemini 4 ファミリーの高速・低コストモデル。Gemini 3.8 Flash の 2.5 倍の速さで、フロンティアモデルの Argon に並ぶスコアを出す
- Gemini アプリでは無料ユーザーも自動のモデル選択で使え、API では `gemini-4-hydrogen` で呼べる
- YouTube を開いたまま Gemini in Chrome に要約プロンプトを貼れば、動画を最後まで見なくても要点と時間位置がわかる
- Gemini in Chrome が Hydrogen を使っているかは公式には未確認。要約は入口として使い、大事な箇所は動画で確かめる

## 参考

- [Introducing Gemini 4 Hydrogen for Agentic Workflows（Google 公式ブログ）](https://blog.google/innovation-and-ai/models-and-research/gemini-models/introducing-gemini-4-hydrogen/)
- [Gemini 4 Hydrogen: everyday coding and agentic workflows for developers（Google 公式ブログ）](https://blog.google/innovation-and-ai/technology/developers-tools/build-with-gemini-4-hydrogen/)
- [Gemini 4 Hydrogen Explained: Features, Benchmarks & Pricing（DataCamp）](https://www.datacamp.com/blog/gemini-4-hydrogen)
- [StudioYebisu さんの投稿](https://x.com/studio_yebisu/status/2121835594674561098)
- [なゆえんじんさんの投稿](https://x.com/nayuengin/status/2121839284613533932)
