---
title: "AI-For-Beginners（Microsoft）"
description: "Microsoft が GitHub で公開する無料の AI 入門カリキュラム。シンボリック AI からニューラルネットワーク、CV、NLP、Transformer までを 24 レッスンで辿る。日本語版あり"
date: 2026-09-30
lastmod: 2026-10-13
aliases: ["AI For Beginners", "microsoft/AI-For-Beginners", "12 Weeks, 24 Lessons, AI for All"]
related_posts:
  - "/posts/2026/09/microsoft-ai-for-beginners/"
  - "/posts/2026/09/ai-for-beginners-01-intro-history/"
  - "/posts/2026/09/ai-for-beginners-02-symbolic-ai/"
  - "/posts/2026/09/ai-for-beginners-03-neural-networks/"
  - "/posts/2026/10/ai-for-beginners-04-computer-vision/"
  - "/posts/2026/10/ai-for-beginners-05-nlp/"
  - "/posts/2026/10/ai-for-beginners-06-other-ai/"
  - "/posts/2026/10/ai-for-beginners-07-ethics/"
tags: ["Microsoft", "AI-For-Beginners", "機械学習", "ディープラーニング", "llm"]
---

## 概要

[microsoft/AI-For-Beginners](https://github.com/microsoft/AI-For-Beginners) は、Microsoft（主執筆者 Dmitry Soshnikov 氏）が 2021 年から MIT ライセンスで公開している AI 入門カリキュラム。「12 Weeks, 24 Lessons, AI for All!」を掲げ、知識表現 → ニューラルネットワーク → CV / NLP → Transformer → LLM と、歴史と構造の順に積み上げる。日本語版は README だけでなく各レッスン本文と Jupyter Notebook まで `translations/ja/` に揃っている。

生成 AI から入った人が、**LLM の「手前」を下から積み直す**教材として価値がある。LLM の章そのものは古い。

## 詳細

### 構成

| パート | レッスン | 主な内容 |
|---|---|---|
| I. AI 入門 | 01 | AI の定義と歴史、2 つのアプローチ |
| II. シンボリック AI | 02 | 知識表現、エキスパートシステム、オントロジー |
| III. ニューラルネットワーク | 03〜05 | パーセプトロン、多層パーセプトロンの自作、PyTorch / TensorFlow と過学習 |
| IV. コンピュータビジョン | 06〜12 | OpenCV、CNN、転移学習、VAE、GAN、物体検出、セグメンテーション |
| V. 自然言語処理 | 13〜20 | BoW / TF-IDF、Word2Vec、RNN、Transformer と BERT、固有表現抽出、LLM |
| VI. その他 | 21〜23 | 遺伝的アルゴリズム、深層強化学習、マルチエージェント |
| VII. AI 倫理 | 24 | 責任ある AI |

前後に環境構築のレッスン 0 とマルチモーダル（CLIP / VQGAN）のレッスン 25 が付く。各レッスンに講義前後のクイズ、PyTorch 版と TensorFlow 版の Notebook、一部にラボがあり、**Notebook を動かす前提**の教材である。古典的な機械学習（回帰・決定木）は姉妹カリキュラム ML-For-Beginners の担当で扱わない。

### レッスン 01 の地図

- AI の対象は「人間は経験からできるが、**手順を書き出せない問題**」（写真から年齢を当てる、など）
- 知能を載せる方法は、推論をまねるトップダウン（[記号的 AI](/blogs/wiki/concepts/symbolic-ai/)）と、脳の構造をまねるボトムアップ（[ニューラルネットワーク](/blogs/wiki/concepts/neural-network-basics/)）の 2 本柱。ほかに創発的・マルチエージェント的アプローチと進化的アプローチ
- チューリングテストは知能を定義する代わりに「人間と区別できるか」という判定方法を与えた。2014 年の Eugene Goostman について教材は「ボットではなく作者が人間を欺いた」と釘を刺す。2025 年にはペルソナを与えた GPT-4.5 が 3 者間テストで 73% の確率で人間と判定された。**区別できないことと理解していることは別**
- チェスは「探索（アルファベータ枝刈り）→ 事例ベース推論 → ニューラルネットワーク＋強化学習」、対話は「ELIZA → ハイブリッド型アシスタント → ニューラルネットワークだけの対話」と主役が移った。後者は教材の予想どおり LLM で実現した

### 割り切って読むべきところ

- **LLM の章は GPT-2 / GPT-3 の時代で止まっている** — RLHF・指示チューニング・RAG・エージェントは扱わない。GPT ファミリーの表の「GPT-4 は 100 兆パラメータ」は英語原文ごと誤り（公開前の噂の値）
- **日本語版は Co-op Translator による機械翻訳** — レッスン 01 の「話すプログラム」の節は本文が途中で欠落している。数式や用語で引っかかったら英語原文と突き合わせる
- **レッスン 01 の史実の圧縮** — AI の冬は一般に 2 回（1970 年代と 1980 年代末）。2015 年に画像分類で人間の推定精度を初めて上回った論文は ResNet ではなく PReLU の *Delving Deep into Rectifiers*
- **Notebook は 2021〜2022 年のライブラリのまま** — 今の環境では動かないセルがある（MNIST データ形式の差し替え、NumPy 2、Matplotlib、Keras 3。詳細は[ニューラルネットワークの基礎](/blogs/wiki/concepts/neural-network-basics/)）
- レッスン 02 の Microsoft Concept Graph の演習は API 停止で動かない。日本語版ディレクトリには `data/` が無く FamilyOntology は失敗する

### パート IV〜VII の要点（シリーズ解説より）

- **IV. コンピュータビジョン（06〜12）** — 画像は NumPy 配列（OpenCV のカラーは BGR 順）。CNN は小さなフィルターを画像全体に当て、パーセプトロンの「位置がずれると誤分類する」弱点を克服する。畳み込み＋プーリングのピラミッド型が基本。学習済み CNN を特徴抽出器として借りる**転移学習**なら猫と犬の分類が 1 エポックで 97% 台（一から作った小さな CNN では Oxford-IIIT Pet 37 品種で検証 0.491 止まり）。オートエンコーダー・GAN は画像を作り、物体検出は四角で位置を、セグメンテーションは画素ごとに当てる
- **V. 自然言語処理（13〜20）** — BoW / TF-IDF → 埋め込み（Word2Vec、GloVe）→ 単語を予測する課題で埋め込みを学習する言語モデル（CBoW）と進み、最後が LLM の出発点。RNN / LSTM はニュース分類で TF-IDF との差がわずか。Transformer はアテンションで全単語を同時に見る。BERT の追加学習は画像の転移学習と同じ考え方。NER は BIO タグの分類で、単語単位の正解率はパディングと O タグで水増しされる（「全部 O」で 0.968）ので固有表現単位の F1 を見る。ノートブックの GPT は GPT-1 で、プロンプトだけではタスクを解けない
- **VI. その他（21〜23）** — 遺伝的アルゴリズム（交叉・突然変異・選択。効率のよい全探索がある問題では全探索のほうが速い）、深層強化学習（CartPole は方策勾配法で数十〜百数十エピソードで支えられるが、Mountain Car は報酬の工夫なしでは解けない）、マルチエージェント（NetLogo の Flocking。NetLogo は 2025 年 9 月に 7.0、NetLogo Web でも動く）
- **VII. AI 倫理（24）** — Microsoft の責任ある AI の 6 原則。詳細と Fairlearn での検証は[責任ある AI](/blogs/wiki/concepts/responsible-ai/)

### 黙って結果を変える教材の誤り

エラーにならず結果だけが静かに間違う箇所が各パートにある（[沈黙する失敗](/blogs/wiki/concepts/silent-failure/)の典型）。

- **CV**: フレーム差分の uint8 桁あふれ、`vgg.eval()` 忘れで分類が揺れる、AAE の識別器が一度も更新されない、DCGAN の生成器が評価モードのまま学習、セグメンテーションでシグモイドを 2 重がけ（`BCEWithLogitsLoss` との併用）
- **NLP**: 学習済み埋め込みが `weight[i].data = ...` で書き込まれていない、TensorFlow 版の埋め込みが 2 行ずれている（直すと 0.61 → 0.8661）、AG_NEWS の学習とテストを逆に受け取る、BERT のウォームアップをサンプル数で計算して学習率がほとんど上がらない、ロジットを確率として損失に渡す
- **その他**: N クイーンの `genetic()` が正解でない解を返す、突然変異の確率が説明（30%）と違い 20%、CartPole-v1 の「解けた」基準に v0 の 195 を使っている
- 損失をバッチサイズで 2 回割っていて表示が小さすぎる誤りは CV・NLP の補助モジュールに共通

### 2026 年の環境で動かすときの共通の注意

- **日本語版フォルダからは動かない** — `data/` や補助モジュール（`pytorchcv.py` など）が無い。ノートブックは英語版 `lessons/` で動かし、説明を日本語版で読む
- **Mac では GPU（MPS）が選ばれず CPU で動く** — デバイス選択に `mps` を足す（DCGAN は CPU で 1 エポック約 2,400 秒、MPS で 6〜10 秒）
- **Keras 3 / PyTorch 2.6 / NumPy 2** — `lr` → `learning_rate`、保存拡張子 `.keras`、`torch.load(..., weights_only=False)`、`np.int` 削除など。Keras 3 では GAN の識別器が学習しないセルもある
- **torchtext は開発終了**でレッスン 13〜18 の PyTorch 版はそのまま動かない
- **Gym は NumPy 2 非対応** — Gymnasium に置き換え、`reset()` と `step()` の戻り値（`terminated` / `truncated`）を書き換える
- 日本語版はラボや課題の説明が欠けている箇所があり、英語版と突き合わせる

### 日本語版だけをクローンする

リポジトリには 50 以上の言語の翻訳が入っていて大きい。README の sparse-checkout 手順をそのまま使うと日本語版も消えるので、除外したうえで `ja` だけを戻す。

```bash
git clone --depth 1 --filter=blob:none --sparse https://github.com/microsoft/AI-For-Beginners.git
cd AI-For-Beginners
git sparse-checkout set --no-cone '/*' '!translations' '!translated_images' '/translations/ja/' '/translated_images/ja/'
```

日本語版の本文は画像を `translated_images/ja/` から相対パスで参照するので、**`translated_images/ja/` も戻さないと図が全部リンク切れになる**。作業ディレクトリ全体は約 222MB になった。

### LLM を説明できるようになりたい場合の絞り方

1. レッスン 03〜05 でニューラルネットワークと学習の仕組み
2. レッスン 13〜18 でテキスト表現から Transformer / BERT まで
3. レッスン 20 で言語モデルとしての GPT の考え方（GPT-4 の行は読み飛ばす）
4. 現在の LLM 活用は Microsoft の Generative AI for Beginners / AI Agents for Beginners に引き継ぐ

## 関連ページ

- [記号的 AI（知識表現とエキスパートシステム）](/blogs/wiki/concepts/symbolic-ai/) — パート II の内容
- [ニューラルネットワークの基礎](/blogs/wiki/concepts/neural-network-basics/) — パート III の内容と Notebook の動かし方
- [責任ある AI](/blogs/wiki/concepts/responsible-ai/) — パート VII の内容と Fairlearn での検証
- [沈黙する失敗](/blogs/wiki/concepts/silent-failure/) — エラーにならず結果だけ変わる教材の誤り
- [RAG](/blogs/wiki/concepts/rag/) — 教材が扱わない現在の LLM 活用の一例
- [AI エージェント](/blogs/wiki/concepts/ai-agent/) — 同上

## ソース記事

- [Microsoft の AI-For-Beginners 日本語版 — LLM の「手前」を積み直す教材として使う](/blogs/posts/2026/09/microsoft-ai-for-beginners/) — 2026-09-29
- [AI の歴史と基本をやさしく解説 — Microsoft AI-For-Beginners レッスン 01](/blogs/posts/2026/09/ai-for-beginners-01-intro-history/) — 2026-09-29
- [知識表現とエキスパートシステムをやさしく解説 — Microsoft AI-For-Beginners レッスン 02](/blogs/posts/2026/09/ai-for-beginners-02-symbolic-ai/) — 2026-09-30
- [ニューラルネットワークの基礎をやさしく解説 — Microsoft AI-For-Beginners レッスン 03〜05](/blogs/posts/2026/09/ai-for-beginners-03-neural-networks/) — 2026-09-30
- [コンピュータビジョンの基礎をやさしく解説 — Microsoft AI-For-Beginners レッスン 06〜12](/blogs/posts/2026/10/ai-for-beginners-04-computer-vision/) — 2026-10-02
- [自然言語処理の基礎をやさしく解説 — Microsoft AI-For-Beginners レッスン 13〜20](/blogs/posts/2026/10/ai-for-beginners-05-nlp/) — 2026-10-02
- [遺伝的アルゴリズム・強化学習・マルチエージェントをやさしく解説 — Microsoft AI-For-Beginners レッスン 21〜23](/blogs/posts/2026/10/ai-for-beginners-06-other-ai/) — 2026-10-02
- [AI 倫理と責任ある AI をやさしく解説 — Microsoft AI-For-Beginners レッスン 24](/blogs/posts/2026/10/ai-for-beginners-07-ethics/) — 2026-10-02
