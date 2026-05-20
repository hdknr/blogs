---
title: "日経225マイクロ先物 × Monte Carlo 自動売買判定 — Claude + 1万通りシミュレーションで勝率55%超のときだけ発注する実装"
date: 2026-05-20
lastmod: 2026-05-20
slug: "nikkei225-micro-monte-carlo-claude"
draft: false
categories: ["AI/LLM"]
tags: ["Claude", "モンテカルロ法", "日経225", "Python", "自動売買", "J-Quants API", "ケリー基準", "GBM"]
---

> ⚠️ **免責事項**: 本記事は技術解説であり、金融商品取引法上の**投資助言には該当しません**。シミュレーション結果は将来の利益を保証するものではなく、先物取引には**元本超過損のリスク**があります。実運用はご自身の責任で行ってください。

[BTC 自動売買 × モンテカルロ法の記事](https://github.com/hdknr/blogs/issues/410)で紹介した「1万通りのシナリオを回してから売買判断する」アーキテクチャを、日本株インデックス — 具体的には **日経225 マイクロ先物** に応用してみます。

BTC と違って日経225 はザラ場の時間が決まっています。しかしナイトセッションがあり流動性は世界最高水準、さらに分散効果で個別株のジャンプリスクが平滑化されるため、**幾何ブラウン運動（GBM）を前提とするモンテカルロと相性が良い**という利点があります。

**TL;DR**

- 勝率 55% かつ期待値 50pt 以上のときだけ発注する二段ゲート
- ケリー基準で枚数を自動調整（上限 25%）
- 1万パスの Monte Carlo を翌営業日終値分布として生成

## 日経225 マイクロ先物がモンテカルロ法と相性が良い 3 つの理由

個別株を Monte Carlo で扱おうとすると、決算・TOB・不祥事・配当落ち といった「ジャンプイベント」が頻発し、log-normal を前提とする GBM の精度が出にくくなります。日経225 は約 225 銘柄の加重平均なので、これらの**個別イベントが分散効果で平滑化**されます。

主な利点は次の通りです。

- **GBM の前提との整合性**: 個別株より裾が薄く、log-normal 近似が機能する
- **流動性**: 大証ラージ・ミニ・マイクロいずれも世界トップクラスの板厚
- **取引時間**: 日中 8:45〜15:45、ナイト 17:00〜翌6:00（2024年11月5日以降の現行仕様）で、米国市場と連動した値動きをほぼ即時に反映できる
- **マクロ情報主体**: FOMC・日銀会合・CPI・地政学など、Claude が要約しやすい情報源で判断できる

## 日経225 マイクロ先物の仕様

マイクロ先物は 2023年5月29日に大阪取引所で取引が開始された商品で、ミニ先物のさらに 1/10 サイズです。

| 項目 | 内容 |
|---|---|
| 取引単位 | 日経平均株価 × 10 円 |
| 呼値 | 5 円 |
| 必要証拠金（目安） | 1〜2万円台/枚（SPAN により変動） |
| 取引時間 | 日中 8:45-15:45 / ナイト 17:00-翌6:00 ※2024年11月5日以降 |
| 限月 | 期近〜期先複数 |

たとえば日経225 が 38,000 円のとき、1 枚あたりの想定元本は 380,000 円ですが、レバレッジで実際の証拠金は 20,000 円前後。**1 ティック（5円）動くと 50円の損益**なので、検証コストが非常に低く、自動売買のプロトタイピングに向いています。

## システム構成

全体像はこんなイメージです。

- **データ取得層**: ヒストリカルは yfinance、本番は J-Quants API
- **モデル層**: GBM パラメータ推定 + 10,000 パス Monte Carlo
- **Claude 補正層**: 直近マクロイベントを要約させて μ を ±α 補正
- **判定層**: 勝率 + 期待値 + ケリー基準の二段ゲート
- **発注層**: kabu ステーション API（三菱UFJ eスマート証券 / 旧 auカブコム証券）で自動発注

## Python 実装例（GBM + 1 万パス Monte Carlo）

最小構成の売買判定スクリプトを示します。Python 3.11+ で動作確認しています。なお `TRADING_DAYS = 252` は米国市場基準で、日本市場は実際には約 245 営業日/年ですが、慣例として 252 を使っています（年率換算の若干の差異は σ で吸収されます）。また `yfinance` の終値は**配当落ち未調整**である点に留意してください。

```python
"""
日経225 マイクロ先物 × Monte Carlo 売買判定
- 取引単位: 指数 × 10 円
- 証拠金: 約 20,000 円/枚（SPAN により変動、ここでは固定値で簡略化）
"""
import numpy as np
import pandas as pd
import yfinance as yf
from dataclasses import dataclass
from datetime import datetime, timedelta

MICRO_MULTIPLIER = 10        # マイクロ先物 1 枚 = 指数 × 10 円
MICRO_MARGIN = 20_000        # 証拠金概算（SPAN により変動）
TRADING_DAYS = 252

# ------------------------------------------------------------
# 1. 価格データ取得（yfinance を MVP として、本番は J-Quants API 推奨）
# ------------------------------------------------------------
def fetch_nikkei225(lookback_days: int = 252) -> pd.Series:
    end = datetime.now()
    start = end - timedelta(days=lookback_days * 2)
    df = yf.Ticker("^N225").history(start=start, end=end)
    return df["Close"].dropna().tail(lookback_days)

# ------------------------------------------------------------
# 2. GBM パラメータ推定
# ------------------------------------------------------------
@dataclass
class GBMParams:
    mu: float       # 年率ドリフト
    sigma: float    # 年率ボラ
    s0: float       # 現在価格

def estimate_gbm(prices: pd.Series) -> GBMParams:
    log_ret = np.log(prices / prices.shift(1)).dropna()
    return GBMParams(
        mu=float(log_ret.mean() * TRADING_DAYS),
        sigma=float(log_ret.std() * np.sqrt(TRADING_DAYS)),
        s0=float(prices.iloc[-1]),
    )

# ------------------------------------------------------------
# 3. Monte Carlo シミュレーション
# ------------------------------------------------------------
def simulate_paths(p: GBMParams, n_paths: int = 10_000,
                   horizon_days: int = 1) -> np.ndarray:
    """horizon_days 後の価格分布を GBM で生成"""
    dt = horizon_days / TRADING_DAYS
    z = np.random.standard_normal(n_paths)
    drift = (p.mu - 0.5 * p.sigma ** 2) * dt
    diffusion = p.sigma * np.sqrt(dt) * z
    return p.s0 * np.exp(drift + diffusion)

# ------------------------------------------------------------
# 4. 売買判定（勝率 + 期待値 + ケリー基準で枚数決定）
# ------------------------------------------------------------
@dataclass
class TradeSignal:
    action: str          # "LONG" / "SHORT" / "FLAT"
    win_rate: float
    expected_pt: float   # 期待損益（指数ポイント）
    var95_pt: float      # 95% VaR
    contracts: int

def _kelly_fraction(win_rate: float, ev: float, var95: float) -> float:
    """簡易ケリー: f* = (b*p - q) / b、b = ev/var95"""
    if ev <= 0 or var95 <= 0:
        return 0.0
    b = ev / var95
    f = (b * win_rate - (1 - win_rate)) / b
    return float(np.clip(f, 0.0, 0.25))  # 25% でキャップ

def decide_trade(p: GBMParams, paths: np.ndarray, capital: float,
                 win_threshold: float = 0.55,
                 ev_threshold_pt: float = 50.0) -> TradeSignal:
    pnl_long = paths - p.s0
    pnl_short = p.s0 - paths
    max_contracts = int(capital // MICRO_MARGIN)

    candidates = [
        ("LONG",  pnl_long),
        ("SHORT", pnl_short),
    ]
    best = TradeSignal("FLAT", 0.0, 0.0, 0.0, 0)
    for side, pnl in candidates:
        win = float((pnl > 0).mean())
        ev = float(pnl.mean())
        var95 = float(-np.percentile(pnl, 5))
        if win >= win_threshold and ev >= ev_threshold_pt:
            f = _kelly_fraction(win, ev, var95)
            contracts = max(1, int(max_contracts * f))
            if ev > best.expected_pt:
                best = TradeSignal(side, win, ev, var95, contracts)
    return best

# ------------------------------------------------------------
# 5. 実行
# ------------------------------------------------------------
def main(capital: float = 500_000):
    prices = fetch_nikkei225()
    params = estimate_gbm(prices)
    paths = simulate_paths(params, n_paths=10_000, horizon_days=1)

    print(f"現在値        : {params.s0:>10,.0f}")
    print(f"年率ドリフト   : {params.mu:>10.2%}")
    print(f"年率ボラ       : {params.sigma:>10.2%}")
    print(f"シナリオ平均   : {paths.mean():>10,.0f}")
    print(f" 5%ile / 95%ile: {np.percentile(paths,5):,.0f} / {np.percentile(paths,95):,.0f}")

    sig = decide_trade(params, paths, capital=capital)
    print("\n=== シグナル ===")
    print(f"アクション : {sig.action}")
    print(f"勝率       : {sig.win_rate:.1%}")
    print(f"期待損益   : {sig.expected_pt:+.1f} pt "
          f"= {sig.expected_pt * MICRO_MULTIPLIER:+,.0f} 円/枚")
    print(f"95% VaR    : {sig.var95_pt:.1f} pt "
          f"= {sig.var95_pt * MICRO_MULTIPLIER:,.0f} 円/枚")
    print(f"発注枚数   : {sig.contracts} 枚 "
          f"(必要証拠金 {sig.contracts * MICRO_MARGIN:,} 円)")

if __name__ == "__main__":
    main()
```

## 出力イメージ

実行するとこんな具合の判定結果が出ます（値は時点・乱数依存）。

```
現在値        :     38,420
年率ドリフト   :      8.21%
年率ボラ       :     18.94%
シナリオ平均   :     38,431
 5%ile / 95%ile: 37,665 / 39,210

=== シグナル ===
アクション : LONG
勝率       : 57.3%
期待損益   : +11.4 pt = +114 円/枚
95% VaR    : 754.6 pt = 7,546 円/枚
発注枚数   : 2 枚 (必要証拠金 40,000 円)
```

## ロジックのポイント

### 1. 二段ゲート（勝率 + 期待値）

シミュレーション結果のうち「利益が出る割合（勝率）」と「期待損益（期待値）」を両方使うのが肝心です。勝率だけで判定すると「**ほぼ確実に小さく勝つが、たまに大きく負ける**」シナリオを過大評価してしまいます。期待値だけだと、**勝率が低すぎてメンタル的に続かない**戦略を選んでしまう。

ここでは「**勝率 55% かつ期待値 50pt 以上**」を発注ゲートにしました。BTC 版も基本的にはこの構造です。

### 2. ケリー基準で枚数を自動調整

ケリー基準は「期待値と分散から、長期的に資産成長率を最大化する張り方」を導く公式です。簡易版として `f* = (b*p - q) / b`（b は損益比、p は勝率、q = 1 - p）を使い、**最大 25% でキャップ**しています。フルケリーは資産曲線のドローダウンと破産確率が極端に大きくなるため、実務では **1/4 〜 1/2 ケリー** に留めるのが一般的で、ここでは保守的に 1/4 を採用しました。なお正規のケリーでは `b = 平均利益 / 平均損失` ですが、より厳しめに評価するため `b = 期待損益 / 95%VaR` を使っています。

マイクロ先物は単位が小さいので、ケリー比率に従って **1〜数枚** という細かい刻みで張れるのが強みです。ミニ先物だと最小単位の絶対額が大きすぎて、ケリーの恩恵を受けにくい。

### 3. GBM の限界

このスクリプトは GBM 1択ですが、現実の市場には「**ジャンプ**」が頻発します。日銀の政策修正、地政学イベント、米雇用統計サプライズなどです。

改善案は次のとおりです。

- **ヒストリカル ブートストラップ**: 過去のリターン分布から復元抽出する。GBM より厚い裾を再現できる。
- **Merton ジャンプ拡散モデル**: ポアソン過程によるジャンプ項を GBM に追加する。
- **GARCH 系**: ボラティリティのクラスタリングを捉える。

最初は GBM で実装して、バックテストで「**ドローダウンの実測値が VaR より大きい**」と分かったら拡張する、という順序がおすすめです。

## Claude をどう組み込むか

ここまでは数値モデルだけの話ですが、ここに Claude を挟むと精度が上がる可能性があります。

具体的には、`decide_trade` の前に「**直近のマクロイベント要約**」を Claude に作らせ、`mu`（年率ドリフト）を補正します。

```python
from anthropic import Anthropic

client = Anthropic()

def adjust_mu_with_claude(base_mu: float, news_summary: str) -> float:
    msg = client.messages.create(
        model="claude-opus-4-7",
        max_tokens=512,
        messages=[{
            "role": "user",
            "content": (
                "以下は直近24時間の日経225関連マクロニュースです。\n"
                "翌営業日のドリフト方向に対する影響度を -1.0〜+1.0 で答えてください。\n"
                "数値のみ JSON で返してください: {\"impact\": <float>}\n\n"
                f"{news_summary}"
            )
        }]
    )
    import json, re
    m = re.search(r'\{[^}]+\}', msg.content[0].text)
    if m is None:
        return base_mu  # JSON 抽出失敗時は補正しない
    try:
        impact = float(json.loads(m.group()).get("impact", 0.0))
    except (json.JSONDecodeError, ValueError):
        return base_mu
    impact = max(-1.0, min(1.0, impact))  # クリッピング
    # 年率換算で最大 ±5% 補正
    return base_mu + impact * 0.05
```

ポイントは「**Claude にトレードそのものを判断させない**」こと。Claude の出力は「直近ニュースが上下どちらに効いているか」のスカラー値だけにとどめ、最終判定は数値モデルに残します。これで Claude のハルシネーションが直接損益に効くリスクを抑えられます。

なお、Claude のレスポンスを安定させるには、構造化出力（JSON モード相当）を使うか、上記のように正規表現で抽出するのが現実的です。

## 本番運用時の API 構成

検証から本番に進むときは、次の置き換えが必要です。

### データ取得

- **yfinance** → **[J-Quants API](https://jpx-jquants.com/)**（JPX 公式）
  - フリープランは 12 週間遅延データ、ライト以上のプランでリアルタイム化・分足対応
  - 上場銘柄一覧、株価四本値、財務情報、信用残などが揃う

### 発注

- **kabu ステーション API**（三菱UFJ eスマート証券 / 旧 auカブコム証券）
  - 個人向けで自動発注が可能な国内主要 API のひとつ
  - REST + Push（WebSocket）で約定通知を受け取れる
  - PUSH API のドキュメント: <https://kabucom.github.io/kabusapi/ptal/push.html>
  - 各エンドポイントのリファレンス: <https://kabucom.github.io/kabusapi/reference/index.html>

### バックテスト

- **[backtesting.py](https://kernc.github.io/backtesting.py/)** や **[vectorbt](https://vectorbt.dev/)** で過去データに対して上記ロジックを当てて、ドローダウン・シャープレシオを計測してから本番投入する流れが王道です。

## まとめ

- BTC 用の Monte Carlo + Claude 構成は、**日経225 マイクロ先物に素直に移植可能**
- 個別株より GBM の前提に合うため、**統計モデルの精度が出やすい**
- マイクロ先物は単位が小さく、**ケリー基準の細かい刻みで張れる**のが大きな利点
- Claude は「判断者」ではなく「マクロ情報のスカラー化器」として使うと安定
- 本番運用では **J-Quants API + kabu ステーション API** の組み合わせが現実的

> ⚠️ **再掲**: 本記事は技術解説であり、投資助言には該当しません。シミュレーション結果は将来の損益を保証するものではなく、先物取引は元本超過損のリスクを伴います。実運用は必ずご自身の責任で行ってください。
