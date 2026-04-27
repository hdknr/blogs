---
title: "Claude Code で株式投資を自動化する — Alpaca API + 期待値計算で3週間4.19%の実績"
date: 2026-04-27
lastmod: 2026-04-27
draft: false
source_url: "https://github.com/hdknr/blogs/issues/1#issuecomment-4326332567"
description: "Claude Code と Alpaca API を組み合わせた米国株自動売買システムの構築方法を解説。期待値計算ベースのルールで損切り・利確を自動化し、3週間で月次リターン4.19%を達成した実装例を紹介。"
categories: ["AI/LLM"]
tags: ["claude-code", "Alpaca", "株式投資", "自動売買", "GitHub Actions", "python", "米国株"]
---

「判断ロジックさえ言語化できれば、Claude Code で株式投資を自動化できるのでは？」という仮説を立て、3週間試した結果、月次リターン 4.19% を達成したという事例が話題になっています。

## なぜAlpacaなのか

日本の主要ネット証券（SBI証券、楽天証券、マネックスなど）は、個人向けの自動売買 API を（調査した限りでは）公開していません。唯一カブコム証券には API がありますが、口座開設の手間や日本株に限定されるという制約があります。

米国株を自動売買したいなら、選択肢はほぼ **Alpaca（アルパカ）** 一択になります。

### AlpacaのAPIが優れている理由

- **全機能を Python から操作可能**: 注文・ポジション管理・履歴取得など
- **株・ETF・仮想通貨をすべて API で売買できる**
- 「ほぼ自動売買のために作られた証券会社」という印象

ただしデメリットもあります。米国の証券会社であるため、確定申告の手続きが複雑になる点や、日本居住者の口座開設にそれなりの手間がかかる点は事前に承知しておく必要があります。

## 投資ロジックの言語化

このシステムの核心は「**負けなければいい**」という考え方です。予測に頼るのではなく、期待値がプラスになるルールを設定して淡々と運用するだけです。

麻雀で相手が満貫や倍満だと分かっているのに、リーのみでリーチしないのと同じ理屈で、期待値が見合っていない状況では投資しないのが原則です。

具体的には以下の3カテゴリのポートフォリオを組んでいます。

### 1. 資産の70%：配当貴族

「配当貴族」と呼ばれる、何十年も株価が上がり続けている銘柄に損切りなしで長期投資します。

### 2. 中期成長株

**「-8% で損切り、+20% で利確」** というルールを設定しています。

```
期待値 = (0.33 × 20%) + (0.67 × -8%) = 1.24%
```

3回に1回勝てばトントン以上になる計算です。予測なしでルールを守るだけで期待値がプラスになります。

### 3. 短期株

**「-3% で損切り、+9% で利確」** という設定です。

```
期待値 = (0.5 × 9%) + (0.5 × -3%) = +3%
```

勝率50%でも利益が積み上がる計算になります。

## Claude Code + Alpaca API の連携構成

実装は驚くほどシンプルです。判断ロジックを言語化して API と連携するだけなので、特に難しいことはありません。

> **注意:** `alpaca_trade_api` は現在 deprecated です。Alpaca 公式は新 SDK **`alpaca-py`** (`pip install alpaca-py`) への移行を推奨しています。以下のサンプルは旧 SDK の例として示します。

```python
import alpaca_trade_api as tradeapi

api = tradeapi.REST(
    key_id=API_KEY,      # os.environ["ALPACA_API_KEY"]
    secret_key=SECRET_KEY,  # os.environ["ALPACA_SECRET_KEY"]
    base_url="https://paper-api.alpaca.markets"  # ペーパートレードで検証
)

# ポジション取得
positions = api.list_positions()

# 損切りチェック（中期成長株の例）
for position in positions:
    unrealized_pct = float(position.unrealized_plpc) * 100
    if unrealized_pct <= -8.0:
        api.submit_order(
            symbol=position.symbol,
            qty=position.qty,
            side="sell",
            type="market",
            time_in_force="gtc"
        )
```

Claude Code を使ってロジックを記述し、Alpaca API と連携することで、判断ルールさえ言語化できれば自動化が完成します。

## GitHub Actions で毎日 Slack に通知

ポートフォリオのリアルタイム状況を把握するため、GitHub Actions と Slack Webhook を組み合わせて毎日の損益レポートを自動送信しています。

```yaml
name: Daily Portfolio Report

on:
  schedule:
    - cron: "0 22 * * 1-5"  # 平日22時（NY市場終了後）

jobs:
  report:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Run portfolio report
        env:
          ALPACA_API_KEY: ${{ secrets.ALPACA_API_KEY }}
          ALPACA_SECRET_KEY: ${{ secrets.ALPACA_SECRET_KEY }}
          SLACK_WEBHOOK_URL: ${{ secrets.SLACK_WEBHOOK_URL }}
        run: python scripts/daily_report.py
```

## 3週間の実績

- **月次リターン: 4.19%**
- 運用資本ベースの月次換算: 4.19% ÷ 0.7 ≈ 6%（資産の70%を運用中のため、運用資本に対するリターンに換算）
- 年利換算: (1.06)^12 - 1 ≈ **約101%**

あくまで試算ですが、このまま運用を続けた場合の資産は2倍になる計算です。もちろん過去3週間の実績が将来を保証するわけではありませんが、ルールベースの期待値運用が機能していることは示されています。

## まとめ

Claude Code で株式投資を自動化するポイントは以下に集約されます。

1. **証券口座は Alpaca 一択**（日本からの米国株自動売買）
2. **投資ロジックを言語化する**（「負けない方法とは？」を期待値で定義）
3. **Claude Code + API 連携**（ロジックをコードに落とすのは簡単）
4. **GitHub Actions で監視・通知**（毎日の損益を Slack に自動報告）

投資の知識がなくても「負けない方法とは何か」を考えてルール化し、そのロジックを言語化して API に繋ぐだけで自動化できてしまうのが、Claude Code の面白いところではないでしょうか。

> ※ 本記事の内容は投資助言ではありません。株式投資にはリスクが伴います。
