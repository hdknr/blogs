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

## 応用: Claude Code でローカルLLM（Qwen等）を追加トレーニングできるか

autoresearch の構成を理解すると、「Claude Code を使ってローカルの Qwen などを追加トレーニングできるのか？」という疑問が浮かぶ。答えは **原理的にはYes** だ。

### 役割分担を理解する

```
┌─────────────┐     指示を読む      ┌──────────────┐
│ Claude Code  │ ◄────────────────── │ program.md   │
│（エージェント）│                     │（人間が書く） │
└──────┬──────┘                     └──────────────┘
       │ train.py を編集
       ▼
┌─────────────┐     5分間実行       ┌──────────────┐
│  train.py   │ ──────────────────► │ ローカルGPU   │
│（学習コード）│                     │（実際の訓練） │
└─────────────┘                     └──────────────┘
```

重要なのは、**Claude Code 自体がモデルを訓練するわけではない**という点だ。Claude Code は研究者の代わりに「コードを読んで仮説を立て、`train.py` を書き換える」頭脳の役割を担い、実際の訓練はローカルGPUが PyTorch で実行する。

### Qwen のファインチューニングに応用する場合

autoresearch は nanochat（GPT-2相当の小型モデル）向けに設計されているが、Qwen のファインチューニングにも応用できる。手順は以下の通り:

1. Qwen の学習スクリプトを `train.py` として用意する
2. `program.md` に「何を最適化するか」（LoRAランク、学習率、データ配分など）の指示を書く
3. Claude Code に `program.md` を読ませて自律的に実験させる

### 実用上の制約

ただし、いくつかの制約がある:

- **時間予算**: autoresearch は5分で1実験を回す設計。Qwen のフル学習には向かないが、**LoRA/QLoRA などの軽量ファインチューニング**なら5分で1イテレーション回せる可能性がある
- **VRAM要件**: Qwen-7B で最低16GB程度のGPU VRAMが必要。QLoRA（4bit量子化）なら要件を下げられる
- **評価指標の設計**: `val_bpb` の代わりに、タスク固有の評価指標（精度、F1スコアなど）を `prepare.py` に定義する必要がある

要するに「Claude Code が頭脳、ローカルGPU が手足」という構成で、人間が寝ている間にファインチューニングの試行錯誤を自動化できるのが autoresearch の本質だ。

## 参考

- [karpathy/autoresearch（GitHub）](https://github.com/karpathy/autoresearch)
- [Karpathy Open-Sources autoresearch（MarkTechPost）](https://www.marktechpost.com/2026/03/08/andrej-karpathy-open-sources-autoresearch-a-630-line-python-tool-letting-ai-agents-run-autonomous-ml-experiments-on-single-gpus/)
- [元ツイート（AIDB）](https://x.com/ai_database/status/2031930022014173695)
