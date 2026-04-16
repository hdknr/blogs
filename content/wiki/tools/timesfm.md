---
title: "TimesFM"
description: "Google Research が開発した時系列予測の基盤モデル。1000億以上の実データで学習済みで、ゼロショット（ファインチューニング不要）で売上・需要・市場価格・トラフィック予測が可能"
date: 2026-04-14
lastmod: 2026-04-14
aliases: ["Times FM", "Time Series Foundation Model", "google/timesfm"]
related_posts:
  - "/posts/2026/04/google-timesfm-prediction-ai/"
tags: ["TimesFM", "Google", "時系列予測", "ゼロショット", "機械学習", "予測AI"]
---

## 概要

Google Research が開発した時系列予測専用の基盤モデル（Time Series Foundation Model）。デコーダーのみのトランスフォーマーアーキテクチャを採用し、1000億以上の実データで学習済み。自分のデータでファインチューニングすることなく（ゼロショットで）時系列予測が可能。

- **GitHub**: [google-research/timesfm](https://github.com/google-research/timesfm)
- **Hugging Face**: `google/timesfm-2.5-200m-pytorch`（最新推奨）
- **パラメータ数**: 2億（200M）
- **ライセンス**: Apache 2.0

## 主なユースケース

| ユースケース | 説明 |
|------------|------|
| 売上・需要予測 | 小売の週次売上、在庫需要、サプライチェーン計画 |
| 市場価格予測 | 株式・コモディティ・仮想通貨の価格変動 |
| 電力需要予測 | 電力負荷、エネルギー価格、スマートグリッド最適化 |
| トラフィック予測 | Web サイトアクセス、API リクエスト量、サーバー負荷 |

## ゼロショット予測の強み

従来の深層学習モデルはデータセットごとに個別学習が必要だったが、TimesFM はゼロショットで新しいデータセットに対して高精度な予測を実現。公式評価では多くの個別学習済み深層学習モデルを上回るパフォーマンスを示している。

## 使い方

```bash
pip install timesfm
```

```python
import timesfm

tfm = timesfm.TimesFm(
    hparams=timesfm.TimesFmHparams(
        backend="pytorch",
        horizon_len=128,
    ),
    checkpoint=timesfm.TimesFmCheckpoint(
        huggingface_repo_id="google/timesfm-2.5-200m-pytorch"
    ),
)

# 配列から予測
forecast, _ = tfm.forecast(inputs=[context_series], freq=[0])

# DataFrame から予測
forecast_df = tfm.forecast_on_df(inputs=df, freq="D", value_name="target")
```

**freq パラメータ**: `0` = 高頻度（日次以下）、`1` = 週次・月次、`2` = 四半期・年次

## TimesFM 2.5 の改善点（2026年3月リリース）

- **コンテキスト長**: 16,384 タイムポイントへ拡張（8倍）
- **パラメータ削減**: 60% 削減しながら性能向上
- **量子予測**: 最大 1,000 ステップの連続量子予測ヘッドを追加
- **共変量サポート**: 祝日・プロモーション・天気データなどの外部変数を組み込み可能

## BigQuery / Google スプレッドシート統合

2026年2月から Google スプレッドシートの Connected Sheets で TimesFM による予測が利用可能。SQL からも使える。

```sql
SELECT * FROM AI.FORECAST(
  MODEL `project.dataset.timesfm_model`,
  TABLE `project.dataset.sales`,
  STRUCT(30 AS horizon, 0.9 AS confidence_level)
)
```

## 関連ページ

- [RAG](/blogs/wiki/concepts/rag/) — 時系列データとの組み合わせによる予測強化
- [AI エージェント](/blogs/wiki/concepts/ai-agent/) — 予測 AI をエージェントに組み込む応用

## ソース記事

- [Googleが1000億の実データで学習した予測AI「TimesFM」をひっそり公開していた](/blogs/posts/2026/04/google-timesfm-prediction-ai/) — 2026-04-14
