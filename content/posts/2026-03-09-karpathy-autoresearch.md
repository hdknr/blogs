---
title: "Karpathy の autoresearch — AIが寝ている間に100回実験を回す仕組み"
date: 2026-03-09
lastmod: 2026-03-09
draft: false
source_url: "https://github.com/hdknr/blogs/issues/1#issuecomment-4026634592"
categories: ["AI/LLM"]
tags: ["llm", "agent", "python"]
---

Andrej Karpathy が公開した [autoresearch](https://github.com/karpathy/autoresearch) は、AI エージェントが単一 GPU 上で自律的に ML 実験を繰り返すツールです。わずか約630行の Python コードで「コード修正 → 学習 → 評価 → 改善」のループを自動化し、研究の競争軸を「コード品質」から「改善ループの速度」へと変えようとしています。

## autoresearch とは

autoresearch のコンセプトはシンプルです:

> AIエージェントに小さいが本物の LLM トレーニング環境を渡し、一晩中自律的に実験させる

エージェントはトレーニングコード（`train.py`）を自動修正し、5分間のトレーニングを実行、検証損失（val_bpb）が改善したかを確認し、結果に基づいて次の実験に進みます。

## プロジェクト構成

autoresearch はたった3つのファイルで構成されています:

| ファイル | 役割 | 編集者 |
|---------|------|--------|
| `prepare.py` | データ準備・ランタイムユーティリティ | 変更不可 |
| `train.py` | モデル・オプティマイザ・学習ループ | AIエージェント |
| `program.md` | エージェントへの指示書 | 人間 |

従来のML研究では Python ファイルを直接編集しますが、autoresearch では **Markdown ファイル（`program.md`）でエージェントに指示を与える** という設計になっています。人間が行うのは「プログラムのプログラミング」です。

## 固定時間予算という設計判断

autoresearch の重要な設計判断は、全てのトレーニングを **ちょうど5分間** に固定していることです:

- 1時間あたり約12回の実験が可能
- 一晩（8時間）で約100回の実験を自動実行
- プラットフォームに依存せず公平な比較が可能

```bash
# セットアップ
uv sync
uv run prepare.py  # データ準備（初回のみ、約2分）

# 単一実験の実行
uv run train.py    # 約5分で完了
```

エージェントの起動は、Claude などの AI に対して以下のように指示するだけです:

```
Hi have a look at program.md and let's kick off a new experiment!
```

## 実績: Shopify CEO も活用

公開直後、Shopify CEO の Tobi Lutke がこのフレームワークを社内プロジェクトに適用。エージェントに小規模モデルのアーキテクチャを反復最適化させたところ、検証スコアが **19% 改善** し、手動チューニングした大規模モデルを上回る結果を出しました。

## 競争軸の変化

autoresearch が示唆するのは、AI研究における競争軸の変化です:

- **従来**: 優秀な研究者がコードを書き、手動で実験を設計・実行する
- **これから**: 人間は実験戦略を設計し（`program.md`を書き）、AIエージェントが反復実行する

コードの品質そのものではなく、**改善ループをどれだけ速く・効率的に回せるか** が重要になります。単一 GPU でも、エージェントが一晩中休まず実験を回し続ければ、大規模計算資源を持つチームに匹敵する成果を出せる可能性があります。

## まとめ

autoresearch は「AIによる自律的研究」の最小実装と言えます。630行のコードと1台の GPU、そして適切な指示書（`program.md`）があれば、AI が自分で実験を設計・実行・評価するループが回り始めます。研究者の役割は「実験を行う人」から「実験の方向性を設計する人」へと変わりつつあります。

- GitHub: [karpathy/autoresearch](https://github.com/karpathy/autoresearch)
