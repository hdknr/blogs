---
title: "Claudeで金融論文を24時間監視し、今も使えるトレード戦略だけ残すバックテスト自動化"
date: 2026-11-22
lastmod: 2026-11-22
slug: "finance-paper-strategy-mining-ai"
draft: false
source_url: "https://github.com/hdknr/blogs/issues/554#issuecomment-7074051149"
categories: ["AI/LLM"]
tags: ["claude", "バックテスト", "クオンツ", "論文", "ペーパートレード"]
description: "arXiv・SSRN・NBER の新着金融論文を AI に読ませ、売買ルールの抽出からバックテスト・頑健性テスト・判定までを自動化するパイプラインを解説。LLM に任せる工程と決定的なコードに任せる工程の分け方、公開後に効かなくなる戦略の見分け方も整理します。"
---

## はじめに

X で、トレーダーのべーた（[@foodloss_otoko](https://x.com/foodloss_otoko/status/2123813729930445051)）さんが興味深い投稿をしていました。Claude Fable 5.2 を使えば、SSRN・arXiv・NBER に出る金融論文を24時間監視し、実際に売買できるルールを持つ論文だけを残すシステムが作れる、という内容です。

金融の学術論文は毎日のように公開されますが、その大半は理論や実証分析で、そのまま売買に使えるルールを含むものは一部です。さらに、論文に書かれた好成績が手数料込み・公開後のデータでも再現するとは限りません。人間が全部読んで検証するのは現実的ではありません。そこで「読む」「抽出する」「検証する」をパイプラインにして機械に回させよう、というのが投稿の趣旨です。

この記事では、投稿で示された7段階の流れを整理し、各段階をどう実装するかを具体例付きで解説します。この記事でわかることは次の3つです。

- LLM に任せる工程と、通常のプログラムに任せる工程の分け方
- LLM が書いた YAML やコードを機械的に検証する方法
- 論文の公開後に効かなくなった戦略の見分け方

> 元投稿は投稿者が配布する EA（自動売買プログラム）の案内を兼ねています。この記事は設計の考え方だけを扱い、特定の EA や成績を推奨するものではありません。

## 全体像

投稿で示されたパイプラインは次の7段階です。

![arXiv・SSRN・NBER の論文を入力に、①アブストラクト選別、②YAML 抽出、③コード化と照合までを AI が担当し、④バックテスト、⑤頑健性テスト、⑥判定と日次レポートを決定的なコードが担当し、WORKS と判定された戦略だけが⑦ペーパートレードに進むパイプライン図。頑健性テストで小さな変更で崩れた戦略はカーブフィッティングとして破棄される](/blogs/images/finance-paper-strategy-mining-pipeline.png)

| 段階 | 内容 | 主な担当 |
|---|---|---|
| ① アブストラクト選別 | エントリー・エグジット・保有期間が具体的な論文だけ残す | LLM |
| ② YAML 抽出 | 数式・変数・売買条件・必要データ・時間足・論文の成績を1論文1ファイルに | LLM |
| ③ コード化と照合 | 数式をコードにし、テストデータで論文の数式と一致するか確認 | LLM + テスト |
| ④ バックテスト | 4年以上のデータで手数料・スリッページ（注文価格と実際の約定価格のずれ）込み。論文の検証期間内と公開後の両方 | 決定的なコード |
| ⑤ 頑健性テスト | 手数料2倍、別銘柄、パラメータ変更、期間変更。崩れたら破棄 | 決定的なコード |
| ⑥ 判定と日次レポート | WORKS / DECAYED / FAILED / NOT TESTABLE のラベル付け | 決定的なコード |
| ⑦ ペーパートレード | 実資金を入れる前に仮想売買で確認 | 人間 |

ポイントは、**LLM に任せるのは「読む・書き起こす」工程まで**で、成績を測る工程は決定的なコード（同じ入力なら必ず同じ結果を返す、LLM を介さない通常のプログラム）で回すことです。LLM に「この戦略は儲かりますか」と聞いても根拠のある答えは返りません。LLM は論文を構造化データに変換する役に徹し、良し悪しはバックテストの数字で決めます。

## ① 論文の収集とアブストラクト選別

### 新着論文の取得

arXiv には公式の API があり、金融分野は `q-fin` カテゴリにまとまっています。売買戦略に近いのは `q-fin.TR`（Trading and Market Microstructure）や `q-fin.PM`（Portfolio Management）です。Atom 形式で返るので、`feedparser` で読むのが手軽です。

```bash
pip install feedparser
```

```python
import feedparser

ARXIV_API = "http://export.arxiv.org/api/query"

def fetch_arxiv(category: str = "q-fin.TR", max_results: int = 50):
    url = (
        f"{ARXIV_API}?search_query=cat:{category}"
        f"&sortBy=submittedDate&sortOrder=descending&max_results={max_results}"
    )
    feed = feedparser.parse(url)
    return [
        {
            "id": e.id,
            "title": e.title,
            "abstract": e.summary,
            "published": e.published,
        }
        for e in feed.entries
    ]
```

arXiv の API マニュアルは、連続して呼ぶときは3秒の間隔を空けること、同じクエリを1日に2回以上呼ぶ必要はないことを求めています。「24時間監視」といっても、カテゴリごとに1日1回取得すれば十分です。

SSRN と NBER には arXiv のような汎用の検索 API が用意されていないため、新着一覧のページや RSS、メール通知を取り込む形になります。NBER は新着ワーキングペーパーの RSS や週次メール（New This Week）を提供しています。SSRN はメール通知（eJournal の購読）が中心です。いずれもサイトの利用規約を確認し、アクセス頻度を抑えて取得してください。

### LLM による選別

アブストラクトだけを LLM に渡し、売買ルールとして再現できるかを判定させます。判定は自由記述ではなく、決まった形式で返させると後段で扱いやすくなります。

```text
次の金融論文のアブストラクトを読み、売買戦略として再現可能かを判定してください。
以下の3つがすべて読み取れる場合のみ "testable": true とします。

- エントリー条件（何を見て買う/売るか）
- エグジット条件または保有期間
- 対象資産と時間足

JSON で回答してください:
{"testable": bool, "reason": "判定理由を1文で", "asset_class": "equity|fx|futures|crypto|other"}
```

この段階は件数が多いので、上位モデルではなく安価なモデルで十分です。取りこぼしを減らしたいなら、迷ったものは `testable: true` 側に倒し、次の段階で落とします。ここで `testable: false` になった論文は、ラベルを付けずにログに残すだけにします（件数だけ日次レポートに載せると、選別の厳しさの目安になります）。

## ② YAML への抽出

選別を通った論文は本文（PDF）を読ませ、戦略の仕様を1論文1ファイルの YAML に書き起こします。ここで形式を固定しておくことが、後段を自動化できるかどうかの分かれ目です。

```yaml
paper:
  id: "arXiv:XXXX.XXXXX"
  title: "..."
  published: 2026-11-18
strategy:
  asset_class: equity
  universe: "米国大型株（S&P 500 構成銘柄）"
  timeframe: daily
  signal:
    formula: "z = (close - SMA(close, 20)) / STD(close, 20)"
    variables:
      close: "終値"
  entry: "z < -2.0 で買い"
  exit: "z > 0 で決済、または保有5営業日で強制決済"
  holding_period: "最大5営業日"
data_required:
  - "日次の終値（配当・分割調整済み）"
paper_results:
  sample_period: "2005-01 〜 2020-12"
  annual_return: 0.11
  sharpe: 1.2
  costs_included: false
notes:
  - "論文は取引コストを考慮していない"
```

`paper_results` に論文自身が主張する成績と検証期間を残しておくのが重要です。後段で「論文期間内では再現したが公開後は効かない」といった比較をするときの基準になります。`costs_included` のように、論文が手数料を考慮しているかも記録しておきます。

抽出には誤りが入り得るので、YAML のスキーマ検証（必須項目の有無、型）はコードで行い、通らないものは NOT TESTABLE に回します。

## ③ コード化と数式の照合

YAML の `signal.formula` や `entry` / `exit` を LLM にコード化させます。ここで一番怖いのは、**コードが論文の定義とずれていること**です。たとえば次のような誤りは、バックテストの成績を簡単に水増しします。

- 移動平均の期間が1日ずれている
- 当日の終値でシグナルを出し、同じ当日の終値で約定している（先読み）

対策として、手計算できる小さなテストデータで期待値と一致するかを確認するテストを先に用意します。

```python
import numpy as np
import pandas as pd

from strategy import zscore_signal  # LLM が生成した関数

def test_zscore_matches_formula():
    close = pd.Series(np.arange(1.0, 26.0))  # 1, 2, ..., 25
    z = zscore_signal(close, window=20)
    window = close.iloc[5:25]
    expected = (close.iloc[24] - window.mean()) / window.std()
    assert np.isclose(z.iloc[24], expected)

def test_signal_uses_only_past_data():
    close = pd.Series(np.random.default_rng(0).normal(100, 1, 100))
    z_full = zscore_signal(close, window=20)
    z_cut = zscore_signal(close.iloc[:60], window=20)
    # 未来のデータを足しても過去のシグナルは変わらないはず
    assert np.allclose(z_full.iloc[:60].dropna(), z_cut.dropna())
```

2つ目のテストは、データを途中で切っても過去のシグナルが変わらないことを確かめるものです。これが通らないコードは未来のデータを参照しています。照合に失敗した論文は無理に直さず、NOT TESTABLE として人間の確認待ちに回すのが安全です。

## ④ 手数料込みバックテストと公開後の検証

ここからは LLM を使わず、決定的なコードで回します。投稿で示された条件は次のとおりです。

- **4年以上**のデータを使う
- **手数料とスリッページ**を必ず入れる
- **論文の検証期間内**（以下、論文期間内）と**論文の公開後**の両方で測る

### 論文公開後にリターンが下がる理由

最後の「公開後」が特に重要です。学術論文で報告された予測可能性は、公開後に弱まることが知られています。McLean と Pontiff の研究（"Does Academic Research Destroy Stock Return Predictability?", *Journal of Finance*, 2016）は、97の株式リターン予測変数を調べました。その結果、論文の検証期間外ではリターンが約26%、公開後では約58%低下したと報告しています。論文期間内で再現しても、それは「論文が正しく実装できた」ことの確認にすぎず、「今も儲かる」ことの証明にはなりません。

### バックテストのコード例

次は概念を示すコードです。`signal` は z 値そのものではなく、YAML の entry / exit 条件（z < -2 で買い、z > 0 か5営業日で決済）を適用した後の **0/1 のポジション列**を想定しています。手数料は bps（ベーシスポイント、1bps = 0.01%）で指定します。

```python
def run_backtest(signal, prices, fee_bps=5, slippage_bps=5):
    # signal: その日の終値時点で持ちたいポジション（0 または 1）
    # 翌日の始値で約定させる（当日終値での約定は先読みになる）
    position = signal.shift(1).fillna(0)
    returns = prices["open"].pct_change().shift(-1)
    gross = position * returns
    turnover = position.diff().abs().fillna(0)
    cost = turnover * (fee_bps + slippage_bps) / 10_000
    return (gross - cost).dropna()

# paper_end は YAML の paper_results.sample_period の終わり、
# published は paper.published から取る
in_sample = run_backtest(sig[:paper_end], prices[:paper_end])
post_pub = run_backtest(sig[published:], prices[published:])
```

## ⑤ 頑健性テストでカーブフィッティングを見抜く

バックテストで良い数字が出ても、それが特定の条件にたまたま合っただけ（カーブフィッティング）かもしれません。投稿では、手数料・銘柄・パラメータ・期間に小さな変更を加えても成績が保てるかを確認し、崩れる戦略は捨てるとしています。具体的な変更の例を挙げると次のとおりです。

| テスト | 例（筆者による例示） |
|---|---|
| 手数料を2倍にする | 5bps → 10bps |
| 別の銘柄・市場で試す | 米国株 → 日本株、ドル円 → ユーロドル |
| パラメータを少し動かす | 移動平均20日 → 15日・25日 |
| 期間を変える | 前半・後半に分けて別々に測る |

パラメータを少し動かしただけで成績が大きく崩れる戦略は、その値に過剰に合わせ込まれている可能性が高いと考えます。逆に、周辺のパラメータでもそこそこの成績が出るなら、背後に何らかの構造がある可能性が上がります。

検証する本数が多いほど、偶然好成績になる戦略が混じりやすくなる点にも注意が必要です。100本検証すれば、何の根拠もない戦略でも何本かは良い数字を出します。頑健性テストは、この「たまたま当たり」をふるい落とす役割も担います。

## ⑥ 判定と日次レポート

最後に、各論文を4つのラベルに分類します。ラベル名は投稿にあるものです。意味と判定条件は筆者が補ったもので、成績の物差しにはシャープレシオ（リスク1単位あたりのリターン）を使います。

| ラベル | 意味 | 判定条件の例 |
|---|---|---|
| WORKS | 公開後も手数料込みで機能している | 公開後のシャープレシオが基準以上、かつ頑健性テストをすべて通過 |
| DECAYED | 論文期間内では再現したが公開後は劣化 | 論文期間内は基準以上、公開後は基準未満 |
| FAILED | 再現しない、または頑健性テストで崩れる | 論文期間内で手数料込みの成績が基準未満、または頑健性テスト不合格 |
| NOT TESTABLE | データ不足・抽出失敗・照合失敗 | ②・③で脱落、または公開後のデータがまだ足りない |

```python
def classify(in_sample_sharpe, post_pub_sharpe, robust_ok, threshold=0.5):
    if in_sample_sharpe is None or post_pub_sharpe is None:
        return "NOT TESTABLE"
    if in_sample_sharpe < threshold or not robust_ok:
        return "FAILED"
    if post_pub_sharpe >= threshold:
        return "WORKS"
    return "DECAYED"
```

日次レポートには WORKS の論文だけでなく、DECAYED や FAILED の件数も載せておくと、パイプラインが正しく動いているかの目安になります。毎日 WORKS ばかり出るなら、どこかで先読みやコストの入れ忘れが起きている疑いがあります。

## ⑦ ペーパートレード

WORKS と判定されても、すぐに実資金を入れるべきではありません。バックテストでは、約定の遅れ、流動性、データの修正などを再現しきれません。そのため、まずは仮想売買で一定期間動かし、バックテストと同程度の成績が出るかを確認します。ペーパートレードで得た実現シャープレシオをバックテストの値と並べ、大きく下回るなら実装か前提のどこかがずれていると判断します。この最終判断は人間が行います。

## まとめ

- 金融論文を24時間監視するパイプラインは、**LLM が読んで構造化し、決定的なコードが測る**という役割分担で組み立てる
- LLM の出力（YAML・コード）は、スキーマ検証と数式照合のテストで機械的に確かめてから使う
- バックテストは**手数料・スリッページ込み**で、**論文の公開後**の期間でも必ず測る。公開後に効果が弱まるのはよくあること
- 頑健性テストで、カーブフィッティングや多数検証による「たまたま当たり」を落とす
- WORKS と判定されても、実資金の前にペーパートレードで確認する

論文の大半は使えない、という前提で「捨てる仕組み」を先に作るのがこのパイプラインの本質です。LLM のおかげで「読む」コストが下がった分、検証の厳しさにコストをかけられるようになった、と捉えるとよいでしょう。

> 本記事は技術的な設計の解説であり、投資助言ではありません。実際の売買は自己責任で行ってください。
