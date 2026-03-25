---
title: "Karpathy の autoresearch — 寝ている間にAIが100回実験して朝にはモデルが賢くなっている世界"
date: 2026-03-10
lastmod: 2026-03-10
draft: false
source_url: "https://github.com/hdknr/blogs/issues/1#issuecomment-4030998838"
categories: ["AI/LLM"]
tags: ["llm", "agent", "python", "claude-code"]
---

Andrej Karpathy が公開した [autoresearch](https://github.com/karpathy/autoresearch) は、AI エージェントが自律的に ML 実験を繰り返すツールだ。寝ている間に AI が 100 回実験し、朝起きたらモデルが賢くなっている——そんな研究スタイルを 630 行の Python コードで実現する。

## autoresearch とは

nanochat（軽量 LLM 学習コア）をシングル GPU・1 ファイルに凝縮し、AI エージェントが自律ループで学習コードを改善していく仕組み。

基本構造はシンプル:

- **人間**が `.md` ファイル（プロンプト）を設計する
- **AI エージェント**が `.py`（学習コード）を自律的に改善する

各実験は **ちょうど 5 分間** のトレーニングで構成され、1 時間あたり約 12 回、一晩で約 100 回の実験が自動で回る。

```
人間: program.md を設計（研究の方針・制約を定義）
  ↓
AI エージェント: 学習コードを修正
  ↓
5分間のトレーニング実行
  ↓
結果を評価（validation loss）
  ↓
改善されていれば git commit → 次のイテレーションへ
```

## 技術的な特徴

### 630 行のミニマル設計

autoresearch の核心は「小さく始めて、エージェントに任せる」という哲学にある。

- シングル GPU で完結（マルチ GPU 不要）
- ニューラルネットワークのアーキテクチャ、オプティマイザ、ハイパーパラメータすべてを AI が調整
- git feature ブランチ上で動作し、改善があれば自動コミット
- MIT ライセンスで公開

### 「コードを書く」のではなく「プログラムをプログラムする」

Karpathy が強調するのは、研究者が Python ファイルを直接触るのではなく、**Markdown でエージェントへの指示を設計する**というパラダイムシフトだ。

> You're not touching any of the Python files like you normally would as a researcher. Instead, you are programming the program.md Markdown files.

## 実際の成果

公開直後の 3 月 8〜9 日の夜、Hyperspace ネットワーク上で 35 の自律エージェントが **333 回の実験** を完全無人で実行した。

Shopify CEO の Tobi Lutke はこのフレームワークを社内プロジェクトに適用し、小規模モデルのアーキテクチャをエージェントに反復改善させることで、**バリデーションスコアを 19% 改善**したと報告している。

## 研究を超えた「業務の自律ループ」という考え方

この autoresearch の考え方は、研究だけでなく日常業務にも応用できる。

チャエン氏（[@masahirochaen](https://x.com/masahirochaen)）は、Claude Code をベースに全ての業務やタスクに `.md` や skill を配置し、AI が自律的に動ける環境を構築していると述べている。

ポイントは「**業務を AI だけで自己完結させて、フィードバックのループを作る**」こと:

1. 業務のループを一度設計する
2. AI にそのループを回し続けさせる
3. アウトプットの質を極限まで高める

これは autoresearch が ML 実験で行っていることと本質的に同じ構造だ。人間が「問い」や「方針」を設計し、AI が実行と改善のループを自律的に回す。

## まとめ

autoresearch が示しているのは、AI との協働における新しい役割分担だ:

- **人間**: 問いを設計し、方向性を定める（`.md` を書く）
- **AI**: 実行し、検証し、改善する（`.py` を回す）

> 次の時代を作るのは、いちばん頭がいい人でも、いちばん働く人でもなく、いちばん上手く「問いを設計できる人」だ。

この考え方を持って AI ツールに向き合うかどうかで、今後の成長曲線は大きく変わるだろう。
