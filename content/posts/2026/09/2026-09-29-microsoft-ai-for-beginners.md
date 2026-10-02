---
title: "Microsoft の AI-For-Beginners 日本語版 — LLM の「手前」を積み直す教材として使う"
date: 2026-09-29
lastmod: 2026-10-02
slug: "microsoft-ai-for-beginners"
draft: false
source_url: "https://github.com/hdknr/blogs/issues/556#issuecomment-5883166575"
categories: ["AI/LLM"]
tags: ["Microsoft", "機械学習", "ディープラーニング", "llm", "github"]
---

Microsoft が GitHub で公開している AI 入門カリキュラム [AI-For-Beginners](https://github.com/microsoft/AI-For-Beginners) の日本語版が、X で「かなり良い」と紹介されていました（[connect24h さんの投稿](https://x.com/connect24h/status/2104756980279877731)）。紹介の要点は、いきなり LLM だけを触らない点です。知識表現 → ニューラルネットワーク → コンピュータビジョン（CV）/ 自然言語処理（NLP）→ Transformer → LLM と、歴史と構造を順に踏めます。AI を「使える」から「説明できる」へ進みたい人向け、という位置づけでした。

実際にリポジトリの中身を確認すると、その評価はおおむね妥当です。ただし、LLM の章はかなり古いまま残っています。この記事では、カリキュラムの構成を整理したうえで、どこに価値があり、どこは割り切って読むべきかをまとめます。あわせて、日本語版だけを軽くクローンする方法と、LLM を説明できるようになるための絞った進め方も紹介します。

## AI-For-Beginners とは

- 提供元: Microsoft（主執筆者は Dmitry Soshnikov 氏）
- リポジトリ: [microsoft/AI-For-Beginners](https://github.com/microsoft/AI-For-Beginners)
- ライセンス: MIT
- 公開: 2021 年 3 月（GitHub のスター数は 2026 年 9 月時点で約 6.9 万）
- 謳い文句: 「12 Weeks, 24 Lessons, AI for All!」
- 日本語版: [translations/ja/README.md](https://github.com/microsoft/AI-For-Beginners/blob/main/translations/ja/README.md)

日本語版は README だけでなく、各レッスンの本文と Jupyter Notebook まで `translations/ja/` 以下に揃っています。無料で、日本語のまま最後まで進められます。

## カリキュラムの構成

レッスンは大きく 7 つのパートに分かれています（番号は日本語版 README の表に従っています）。

| パート | レッスン | 主な内容 |
|---|---|---|
| I. AI 入門 | 01 | [AI の紹介と歴史](/blogs/posts/2026/09/ai-for-beginners-01-intro-history/) |
| II. シンボリック AI | 02 | [知識表現、エキスパートシステム、オントロジー](/blogs/posts/2026/09/ai-for-beginners-02-symbolic-ai/) |
| III. ニューラルネットワーク | 03〜05 | [パーセプトロン、多層パーセプトロンの自作、PyTorch / TensorFlow 入門と過学習](/blogs/posts/2026/09/ai-for-beginners-03-neural-networks/) |
| IV. コンピュータビジョン | 06〜12 | [OpenCV、CNN、転移学習、オートエンコーダーと VAE、GAN、物体検出、セマンティックセグメンテーション](/blogs/posts/2026/10/ai-for-beginners-04-computer-vision/) |
| V. 自然言語処理 | 13〜20 | [BoW / TF-IDF、Word2Vec / GloVe、RNN、Transformer と BERT、固有表現抽出、大規模言語モデル](/blogs/posts/2026/10/ai-for-beginners-05-nlp/) |
| VI. その他の AI 技術 | 21〜23 | [遺伝的アルゴリズム、深層強化学習、マルチエージェントシステム](/blogs/posts/2026/10/ai-for-beginners-06-other-ai/) |
| VII. AI 倫理 | 24 | [AI 倫理と責任ある AI](/blogs/posts/2026/10/ai-for-beginners-07-ethics/) |

全 7 パートの詳しい解説も書いています。表のリンクから読めます（「I. AI 入門」の [AI の歴史と基本をやさしく解説 — Microsoft AI-For-Beginners レッスン 01](/blogs/posts/2026/09/ai-for-beginners-01-intro-history/)、「II. シンボリック AI」の [知識表現とエキスパートシステムをやさしく解説 — Microsoft AI-For-Beginners レッスン 02](/blogs/posts/2026/09/ai-for-beginners-02-symbolic-ai/)、「III. ニューラルネットワーク」の [ニューラルネットワークの基礎をやさしく解説 — Microsoft AI-For-Beginners レッスン 03〜05](/blogs/posts/2026/09/ai-for-beginners-03-neural-networks/)、「IV. コンピュータビジョン」の [コンピュータビジョンの基礎をやさしく解説 — Microsoft AI-For-Beginners レッスン 06〜12](/blogs/posts/2026/10/ai-for-beginners-04-computer-vision/)、「V. 自然言語処理」の [自然言語処理の基礎をやさしく解説 — Microsoft AI-For-Beginners レッスン 13〜20](/blogs/posts/2026/10/ai-for-beginners-05-nlp/)、「VI. その他の AI 技術」の [遺伝的アルゴリズム・強化学習・マルチエージェントをやさしく解説 — Microsoft AI-For-Beginners レッスン 21〜23](/blogs/posts/2026/10/ai-for-beginners-06-other-ai/)、「VII. AI 倫理」の [AI 倫理と責任ある AI をやさしく解説 — Microsoft AI-For-Beginners レッスン 24](/blogs/posts/2026/10/ai-for-beginners-07-ethics/)）。

これに加えて、環境構築用のレッスン 0（コースセットアップ）と、エクストラとしてマルチモーダル（CLIP と VQGAN）のレッスン 25 があります。「24 レッスン」は本編の数で、その前後にレッスン 0 と 25 が 1 本ずつ付く構成です。

各レッスンには次の教材が付いています。

- 講義前・講義後のクイズ（[オンライン版](https://ff-quizzes.netlify.app/)あり）
- PyTorch 版と TensorFlow 版の Jupyter Notebook（理論の説明も Notebook 側に多く含まれる）
- ラボ（学んだ内容を別の課題に適用する。一部のレッスンのみ）

README 自身が「少なくともどちらか一方の Notebook を一通り学習する必要がある」と書いている通り、本文だけ読んで終わる教材ではありません。手を動かす前提の構成です。

## 扱わないもの

README には「このカリキュラムで扱わない内容」も明記されています。

- ビジネスにおける AI 活用事例
- クラシックな機械学習（別カリキュラムの [ML-For-Beginners](https://github.com/microsoft/ML-For-Beginners) が担当）
- Azure の AI サービスを使ったアプリケーション開発
- 対話型 AI やチャットボット
- 深層学習の背後にある高度な数学

つまり、回帰や決定木といった古典的な機械学習は飛ばして、ニューラルネットワーク以降に集中する構成です。scikit-learn で扱うような古典的機械学習の基礎から入りたい場合は ML-For-Beginners が先になります。

## 価値があるのは LLM の「手前」

生成 AI から AI に入った人にとって、このカリキュラムの価値は LLM の章そのものではなく、そこに至るまでの道のりにあります。

- パーセプトロンや多層パーセプトロンを自分で組み、誤差逆伝播がどう動くかを体感できる（レッスン 03〜04）
- テキストを数値にする方法が、BoW / TF-IDF → 単語埋め込み → 言語モデル → RNN → Transformer と段階的に並んでいる（レッスン 13〜18）
- レッスン 15 で登場した言語モデルが、レッスン 20 で「次の単語の条件付き確率を予測する」ものとして改めて定式化され、パープレキシティの定義と一緒に説明されている

今の LLM がなぜ「次のトークンを予測するだけ」で多くのタスクをこなせるのかは、埋め込みと Transformer を一度自分の手で動かしてみると腑に落ちやすくなります。紹介投稿が言う、「なぜ今の AI がこう動くのか」を一度下から積み直すという使い方には、確かに向いています。

## 割り切って読むべきところ

一方で、そのまま鵜呑みにしないほうがよい点もあります。

### LLM の章は GPT-2 / GPT-3 の時代で止まっている

レッスン 20「大規模言語モデル」の中心は、GPT-2 の論文（*Language Models are Unsupervised Multitask Learners*）と、ゼロショット・少数ショットでタスクを解くという話です。Notebook も Hugging Face Transformers で OpenAI-GPT を動かす内容です。RLHF（人間のフィードバックによる強化学習）、指示チューニング、RAG（検索拡張生成）、エージェントといった、現在の LLM 活用の中心となる話題は扱っていません。README 自身も「最先端技術については一部不足があるかもしれません」と断っています。

さらに、同じレッスンの GPT ファミリーの表には、GPT-4 について「100 兆のパラメータ」と書かれています。これは翻訳の誤りではなく、英語原文でも「100T parameters」となっています。OpenAI は GPT-4 のパラメータ数を公表しておらず、この数字は公開前に出回った噂の値です。GPT-4 の行は教材の誤りとして読み飛ばしてください。

### 日本語版は機械翻訳

日本語版の末尾には免責事項があります。[Co-op Translator](https://github.com/Azure/co-op-translator) による AI 翻訳であり、正式な情報源は原文の文書である、という内容です。README によれば翻訳は GitHub Actions で自動更新されていますが、機械翻訳である以上、訳語の揺れや不自然な表現は残ります。数式や用語で引っかかったら、英語原文（`translations/ja/lessons/…` に対応する `lessons/…`）と突き合わせるのが確実です。

## git sparse-checkout で日本語版だけをクローンする

リポジトリには 50 以上の言語の翻訳が含まれていて、全体はかなり大きくなります。README では、翻訳を除外する sparse-checkout（リポジトリの一部だけを作業ディレクトリに展開する Git の機能）の手順が紹介されています。ただし、そのまま使うと日本語版も一緒に消えます。日本語版だけ残したい場合は、除外したうえで `ja` だけ戻すパターンにします。

```bash
git clone --depth 1 --filter=blob:none --sparse https://github.com/microsoft/AI-For-Beginners.git
cd AI-For-Beginners
git sparse-checkout set --no-cone '/*' '!translations' '!translated_images' '/translations/ja/' '/translated_images/ja/'
```

ポイントは `translated_images/ja/` も戻すことです。日本語版のレッスンは、画像をリポジトリ直下の `translated_images/ja/` から相対パス（`../../../../translated_images/ja/...` など）で参照しています。そのため `translations/ja/` だけを戻すと、本文の図がすべてリンク切れになります。

展開結果は次のように確かめられます。

```bash
ls translations translated_images
```

```text
translated_images:
ja

translations:
ja
```

筆者の環境で試したところ、上記のパターンで `translations/` と `translated_images/` の下には `ja` だけが展開され、作業ディレクトリ全体（`.git` を含む）は約 222MB でした。そのうち `translations/ja` が約 26MB、`translated_images/ja` が約 7MB です。

ローカルに環境を作りたくない場合は、README にある Binder（ブラウザ上で Notebook を実行できるサービス）のバッジや、VS Code / GitHub Codespaces での実行手順（レッスン 0 の「コードの実行方法」）も使えます。

## どう進めるか

全レッスンを 12 週間かけて順に進めるのが正攻法ですが、「LLM を説明できるようになりたい」という目的なら、次のように絞る読み方もあります。

1. レッスン 03〜05 でニューラルネットワークと学習の仕組みを押さえる
2. レッスン 13〜18 でテキスト表現から Transformer / BERT までを通す
3. レッスン 20 で言語モデルとしての GPT の考え方を確認する（GPT ファミリーの表の GPT-4 の行は読み飛ばす）
4. 現在の LLM 活用は、同じ Microsoft の [Generative AI for Beginners](https://github.com/microsoft/generative-ai-for-beginners) や [AI Agents for Beginners](https://github.com/microsoft/ai-agents-for-beginners) に引き継ぐ

コンピュータビジョンのパートは LLM とは直接つながりませんが、CNN や転移学習はマルチモーダルなモデルを理解する下地になります。時間があれば寄り道する価値はあります。

## まとめ

- AI-For-Beginners は、シンボリック AI からニューラルネットワーク、CV、NLP、Transformer、LLM までを、Notebook・クイズ・ラボ付きで順に辿れる無料の教材
- 日本語版は本文と Notebook まで揃っているが、Co-op Translator による機械翻訳
- 価値があるのは LLM に至るまでの道のりで、LLM の章自体は GPT-2 / GPT-3 の時代で止まっている。GPT-4 を「100 兆パラメータ」とする記述は原文ごと誤り
- 日本語版だけ手元に置くなら、sparse-checkout で `translations/ja/` と `translated_images/ja/` の両方を戻す

生成 AI を道具として使うところから入った人が、仕組みの側を一度下から積み直すための教材として、使いどころを選べば十分に役立ちます。
