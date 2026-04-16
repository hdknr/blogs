---
title: "Googleが1000億の実データで学習した予測AI「TimesFM」をひっそり公開していた"
date: 2026-04-14
lastmod: 2026-04-14
draft: false
source_url: "https://github.com/hdknr/blogs/issues/1#issuecomment-4246789955"
categories: ["AI/LLM"]
tags: ["TimesFM", "Google", "時系列予測", "ゼロショット", "機械学習", "建設DX", "EVM"]
---

Googleが時系列予測のための基盤モデル **TimesFM**（Time Series Foundation Model）をひっそりと公開していた。1000億以上の実データで学習済みで、自分のデータをファインチューニングすることなく（ゼロショットで）すぐに使える点が特徴だ。

## TimesFM とは

TimesFM は Google Research が開発した時系列予測に特化した基盤モデルだ。GPT-3 などの大規模言語モデルに着想を得たデコーダーのみのトランスフォーマーアーキテクチャを採用しており、テキストではなく「時系列データのパターン」を学習する。

- **パラメータ数**: 2億パラメータ（TimesFM 2.5 では最適化済み）
- **アーキテクチャ**: デコーダーのみのトランスフォーマー
- **コンテキスト長**: TimesFM 2.5 で 16,384 タイムポイント（8倍に拡張）

## 何が予測できるのか

TimesFM が得意とするユースケースは多岐にわたる。

- **売上・需要予測**: 小売の週次売上、在庫需要、サプライチェーン計画
- **市場価格予測**: 株式市場、コモディティ、仮想通貨の価格変動
- **電力需要予測**: 電力負荷、エネルギー価格、スマートグリッド最適化
- **ユーザートラフィック予測**: Web サイトのアクセス、API リクエスト量、サーバー負荷計画

## ゼロショットで使えるのが最大の強み

従来の深層学習モデルは、予測したいデータセットに合わせて個別にトレーニングする必要があった。TimesFM はそれとは異なり、**一切のファインチューニングなしに新しいデータセットに対して高精度な予測**を実現する。

公式の評価によると、ゼロショット状態の TimesFM は多くの個別学習済み深層学習モデルを上回るパフォーマンスを示している。

## 学習データ

TimesFM は以下のデータソースから 1000 億以上のデータポイントを使って学習されている。

| データソース | 内容 |
|---|---|
| Wikipedia ページビュー | 2012〜2023年の閲覧数時系列データ |
| Google トレンド | 22,000 件の検索関心度時系列データ（時間単位〜週単位） |
| 公開データセット | M4、電力、トラフィックなどのベンチマークデータ |
| 合成データ | ARMA 生成の 300 万件のシリーズ |

最新バージョンでは 4000 億以上の実世界タイムポイントで学習されているとも報告されている。

## 使い方

### インストール

```bash
pip install timesfm
```

### Python での基本的な使い方

```python
import timesfm

# モデルの初期化（Hugging Face からダウンロード）
tfm = timesfm.TimesFm(
    hparams=timesfm.TimesFmHparams(
        backend="pytorch",
        per_core_batch_size=32,
        horizon_len=128,
    ),
    checkpoint=timesfm.TimesFmCheckpoint(
        huggingface_repo_id="google/timesfm-2.5-200m-pytorch"
    ),
)

# 配列から予測
forecast_array, _ = tfm.forecast(
    inputs=[context_time_series],
    freq=[0],  # 0: 高頻度（日次以下）、1: 週次・月次、2: 四半期・年次
)

# DataFrame から予測
forecast_df = tfm.forecast_on_df(
    inputs=df,
    freq="D",  # 日次
    value_name="target",
    num_jobs=-1,
)
```

### Hugging Face モデル

複数のバリアントが公開されている。

| モデル ID | 説明 |
|---|---|
| `google/timesfm-1.0-200m` | オリジナル（200M パラメータ） |
| `google/timesfm-2.0-500m-pytorch` | 大規模バリアント |
| `google/timesfm-2.5-200m-pytorch` | 最新の最適化版（推奨） |

## TimesFM 2.5 の主な改善点（2026年3月31日リリース）

- **パラメータ削減**: 60% 削減しながら性能が向上
- **コンテキスト長の拡張**: 16,384 タイムポイントへ（8倍）
- **量子予測**: 最大 1,000 ステップの連続量子予測ヘッドを追加
- **共変量サポート復活**: 祝日、プロモーション、天気データなどの外部変数を組み込み可能
- **JAX/Flax バックエンド**: 高速推論のための Flax バージョン追加

## BigQuery・Google スプレッドシートとの統合

2026年2月からは **Google スプレッドシートの Connected Sheets** を通じて、BigQuery ML と TimesFM を使ったデータ予測機能が利用可能になった。SQL でも使える。

```sql
-- BigQuery ML での時系列予測
SELECT *
FROM AI.FORECAST(
  MODEL `myproject.mydataset.timesfm_model`,
  TABLE `myproject.mydataset.sales_data`,
  STRUCT(30 AS horizon, 0.9 AS confidence_level)
)
```

## 応用例：建設工事の原価進捗予測

TimesFM の活用先は IT 領域にとどまらない。たとえば **10億円規模の建設工事の進捗管理** にも応用できる可能性がある。

### S カーブ予測との相性

建設工事の累積原価は典型的な **S カーブ**（序盤緩やか→中盤急増→終盤緩やか）を描く。日次・週次で原価発生実績をプロットし、TimesFM に投入すれば「このペースで工期内に収まるか」をゼロショットで予測できる。

### 共変量で精度を上げる

TimesFM 2.5 の共変量サポートを活用すれば、原価の時系列データに加えて以下のような外部変数を組み込める。

- **天候データ**: 雨天・降雪による工事中断の影響
- **資材価格指数**: 鋼材・コンクリート等の市況変動
- **人員投入計画**: 作業員数の増減スケジュール

### EVM との併用が現実的

建設業界には **EVM（アーンドバリューマネジメント）** という確立された進捗管理手法がある。CPI（コスト効率指数）や SPI（スケジュール効率指数）で完工予測を行うものだ。

TimesFM は EVM を置き換えるものではなく、**補完するツール**として位置づけるのが現実的だろう。

| 手法 | 強み | 弱み |
|---|---|---|
| EVM | 業界標準、説明可能性が高い | 線形外挿が前提、突発変動に弱い |
| TimesFM | 非線形パターンを学習、共変量対応 | ブラックボックス、データ点数が少ないと精度低下 |

EVM で基本的な進捗管理を行いつつ、TimesFM で資材費・外注費などの個別原価項目のトレンド予測を補助する——というハイブリッド運用が、建設プロジェクトにおける AI 活用の一歩になるかもしれない。

## リソース

- GitHub: https://github.com/google-research/timesfm
- Hugging Face: https://huggingface.co/google/timesfm-2.5-200m-pytorch
- Google Research ブログ: https://research.google/blog/a-decoder-only-foundation-model-for-time-series-forecasting/

## まとめ

TimesFM は「時系列予測の LLM」とも言える存在だ。1000億以上の実データで学習されたゼロショット予測モデルが、ファインチューニングなしで商用ユースケースに使えるというのは実用的に大きな意味を持つ。売上予測や需要予測に悩んでいるなら、まず試してみる価値は十分にある。
