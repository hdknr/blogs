---
title: "Karpathy の autoresearch — LLMに「このLLMを訓練して」と丸投げしたら一晩で公式チームを超えた話"
date: 2026-03-13
lastmod: 2026-03-13
draft: false
source_url: "https://github.com/hdknr/blogs/issues/1#issuecomment-4058506995"
categories: ["AI/LLM"]
tags: ["llm", "agent", "python"]
---

Andrej Karpathy が2026年3月に公開した [autoresearch](https://github.com/karpathy/autoresearch) は、AIエージェントにLLMのトレーニングを丸投げするツールだ。GPU1台・一晩放置するだけで、エージェントが自律的にコード修正→実験→評価を繰り返し、人間の研究者なしで性能を改善していく。

実際に Karpathy 自身が約700回の実験を実行したところ、GPT-2の学習時間が2.02時間→1.80時間へ11%短縮された。さらに別の開発者は、8時間・37実験で0.8Bモデルが従来の1.6Bモデルを19%上回るスコアを叩き出している。

## autoresearch の仕組み

autoresearch はわずか630行のPythonで構成されており、3つのコアファイルで動作する。

### 3つのコンポーネント

| ファイル | 役割 | 編集者 |
|---|---|---|
| `program.md` | エージェントへの指示書（戦略・ルール・評価基準） | 人間 |
| `prepare.py` | データ準備・トークナイザー・評価関数（固定） | 変更禁止 |
| `train.py` | モデル・オプティマイザ・学習ループ | AIエージェント |

### エージェントループ

エージェントは以下のサイクルを自動で繰り返す:

1. `program.md` を読んで戦略を把握
2. `train.py` を修正（アーキテクチャ変更、ハイパーパラメータ調整など）
3. 5分間の固定時間でトレーニングを実行
4. `val_bpb`（検証ビット/バイト）が改善したか確認
5. 改善 → 変更を保持、悪化 → 変更を破棄
6. 1に戻る

5分の固定時間予算により、1時間あたり約12実験、一晩（8時間）で約100実験が可能になる。

## 実験結果

### Karpathy 自身の実験

Karpathy は自身の nanochat（GPT-2トレーニング環境）に autoresearch を適用:

- **約700回の実験**を2日間で実行
- **約20個の実質的な改善**を発見
- GPT-2到達時間: **2.02時間 → 1.80時間**（11%短縮）

発見された改善の例:
- バッチサイズの半減（5分以内のステップ数増加）
- モデル深度の調整（depth 9への最適化）
- スライディングウィンドウ比率のチューニング

### コミュニティの成果

GitHub Discussions で報告された改善:

- **Discussion #32**: val_bpb を 0.9979 → 0.9773 に改善（89実験、H100 80GB）
- **Discussion #43**: val_bpb を 0.9979 → 0.9697 に改善（126実験、H100 80GB）
- **Tobi のケース**: 0.8Bモデルが従来の1.6Bモデルを **19%上回るスコア**（37実験、8時間）

## 使用されるLLM

autoresearch のエージェントとして動作するLLM自体は外部モデルを使用する。Karpathy のテストでは Claude や GPT 系モデルが使われている。

Karpathy は Codex について「指示を無視して停止してしまう」と述べており、Claude との相性が良いことを示唆している。

## セットアップ

必要環境は NVIDIA GPU、Python 3.10+、uv パッケージマネージャー。

```bash
# リポジトリのクローン
git clone https://github.com/karpathy/autoresearch.git
cd autoresearch

# 依存関係のインストール
uv sync

# データ準備
uv run prepare.py

# トレーニング実行（エージェントなしのベースライン）
uv run train.py
```

エージェントによる自律実験は、Claude Code などのコーディングエージェントに `program.md` を読ませて `train.py` を編集させる形で実行する。

## なぜ重要か

autoresearch が示したのは、**ML研究のループそのものを自動化できる** という可能性だ。

従来のAutoMLやハイパーパラメータ探索ツール（Optuna等）は探索空間が事前定義されている。一方、autoresearch ではエージェントがコード自体を自由に書き換えるため、アーキテクチャの変更や新しい最適化手法の導入など、より創造的な探索が可能になる。

Karpathy 自身の言葉:

> 目標は、エージェントをエンジニアリングして、あなた自身の関与なしに継続的により速い研究進歩を実現することだ

ただし現状では、depth 12 での改善が depth 24 に転移するかは未確認の仮説であり、スケーリング時に最適化レジームが変わる可能性がある点は注意が必要だ。

## 参考

- [karpathy/autoresearch（GitHub）](https://github.com/karpathy/autoresearch)
- [Karpathy Open-Sources autoresearch（MarkTechPost）](https://www.marktechpost.com/2026/03/08/andrej-karpathy-open-sources-autoresearch-a-630-line-python-tool-letting-ai-agents-run-autonomous-ml-experiments-on-single-gpus/)
- [元ツイート（AIDB）](https://x.com/ai_database/status/2031930022014173695)
