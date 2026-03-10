---
title: "Karpathy の autoresearch — AI エージェント群が研究コミュニティを代替する未来"
date: 2026-03-09
lastmod: 2026-03-09
draft: false
source_url: "https://github.com/hdknr/blogs/issues/1#issuecomment-4027631113"
categories: ["AI/LLM"]
tags: ["agent", "python", "llm", "github"]
---

Andrej Karpathy が公開した [autoresearch](https://github.com/karpathy/autoresearch) が話題を呼んでいる。630 行の Python コードで、AI エージェントが単一 GPU 上で自律的に ML 実験を回し続けるというツールだ。さらに Karpathy は「次のステップは、エージェント同士が非同期かつ大規模に協調する仕組みだ」と[述べており](https://x.com/karpathy/status/2030705271627284816)、単なるツール公開にとどまらないビジョンを示している。

## autoresearch の仕組み

autoresearch のコア設計はシンプルだ。3 つのファイルで構成される:

- **`prepare.py`** — データとトークナイザーの準備（修正不可）
- **`train.py`** — モデル・オプティマイザー・訓練ループ（エージェントが編集する対象）
- **`program.md`** — エージェントへの指示書（人間が編集する対象）

エージェントは以下のサイクルを自律的に繰り返す:

1. `train.py` のコードを修正する
2. **5 分間**の訓練を実行する（時間予算は固定）
3. 評価指標（val_bpb = 検証ビット/バイト）で結果を判定する
4. 改善なら保持、悪化なら破棄して次の仮説へ

```bash
# セットアップ
uv sync
uv run prepare.py   # データ準備（約2分）
uv run train.py     # 単一実験実行（5分）
```

「一晩放置しておけば、朝にはエージェントが何十もの実験を試して最良の結果を残している」というのがコンセプトだ。

## 「研究コミュニティをエミュレートせよ」

autoresearch の真価は、ツール単体ではなく Karpathy が示した次のステップにある。

> The goal is not to emulate a single PhD student, it's to emulate a research community of them.
> （目標は一人の博士課程の学生をエミュレートすることではない。研究コミュニティをまるごとエミュレートすることだ。）

現在の autoresearch はコミットを同期的に一本のスレッドで積み上げていく。だが Karpathy が構想するのは、リポジトリを「種」として無数のエージェントがそこから枝分かれし、異なる研究方向に並列で進んでいく世界だ。SETI@home のような分散コンピューティングモデルを研究に適用するイメージだと言える。

この構想が実現するには、いくつかの技術的課題がある:

- **分散タスクシャーディング** — 実験をどう分割して割り当てるか
- **結果の重複排除** — 同じ仮説を複数エージェントが試す無駄をどう防ぐか
- **クロスエージェントメモリ** — あるエージェントの発見を他のエージェントが活用できる仕組み
- **Git の限界** — 「一本の master ブランチ + 一時的な PR」という既存の Git モデルでは、エージェントが数千のコミットを並列に管理する構造に対応しきれない

Karpathy 自身も、Discussions や PR を使ったエージェント間の知見共有を軽量にプロトタイピングしたと述べている。

## 「一つを賢くする」から「場の設計」へ

IT navi 氏（[@itnavi2022](https://x.com/itnavi2022)）は、この動きを端的に[こう要約している](https://x.com/itnavi2022/status/2031015950783516715):

> AI が一人の研究者を代替するのではなく、無数のエージェントが並列に仮説を試し、成果や失敗を持ち寄りながら、ひとつの研究コミュニティのように知を前進させる未来だ。問題は、一つのエージェントを賢くすることではなく、無数のエージェントが枝分かれしながら知見を蓄積する場をどう設計するかに移りつつある。

これは AI エージェント開発における重要なパラダイムシフトを示している。これまでの議論は「いかにモデルを賢くするか」「いかにプロンプトを最適化するか」に集中していた。だが autoresearch が示す方向は、**個のエージェントの能力向上よりも、エージェント群の協調システム設計**に重心が移りつつあるということだ。

Karpathy の言葉を借りれば、エージェントの「知性、注意力、粘り強さがボトルネックでなくなった」とき、既存の開発抽象（Git、CI/CD、コードレビュー）にますます圧力がかかる。

## ハーネスエンジニアリングとの接点

この議論は、[ハーネスエンジニアリング](/posts/2026-03-09-harness-engineering/) の文脈ともつながる。autoresearch の `program.md` はまさに AGENTS.md / CLAUDE.md に相当する入力層であり、5 分間の固定時間予算と val_bpb による自動評価は検証層だ。

単一エージェントのハーネスでさえ設計が難しいのに、複数エージェントが並列で動く環境では、ハーネスの重要性はさらに増す。「何を読ませるか」「品質をどう強制するか」「結果をどう検証するか」という 3 層構造を、分散環境でどうスケールさせるかが次の課題になるだろう。

## 参考

- [autoresearch](https://github.com/karpathy/autoresearch) — Karpathy のリポジトリ
- [Karpathy のツイート（研究コミュニティ構想）](https://x.com/karpathy/status/2030705271627284816)
- [IT navi 氏のツイート](https://x.com/itnavi2022/status/2031015950783516715)
- [Andrej Karpathy Open-Sources 'Autoresearch'](https://www.marktechpost.com/2026/03/08/andrej-karpathy-open-sources-autoresearch-a-630-line-python-tool-letting-ai-agents-run-autonomous-ml-experiments-on-single-gpus/) — MarkTechPost
