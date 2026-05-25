---
title: "Netflixの1時間より価値がある — スタンフォードCS336「ゼロからLLMを構築する」2時間講義が無料公開中"
date: 2026-05-21
lastmod: 2026-05-21
slug: "stanford-cs336-llm-lecture"
draft: false
source_url: "https://github.com/hdknr/blogs/issues/1#issuecomment-4504081182"
categories: ["AI/LLM"]
tags: ["スタンフォード", "LLM", "機械学習", "ChatGPT", "Claude"]
---

「NetflixのドラマよりもこのスタンフォードのAI講義を2時間見た方がいい——大手AI企業で働く多くの人がキャリア全体を通じて学ぶより多くのことを学べる。」

スペイン語圏最大のAIニュースレター「IAPROACTIV」を率いるSanti Torres（@SantiTorAI）がXに投稿した。そのメッセージは10万ビューを超えて拡散し、彼が紹介しているのは、スタンフォード大学が2026年春学期に開講した **CS336: Language Modeling from Scratch**（ゼロから言語モデルを構築する）という講義だ。

## Stanford CS336 とは

**Stanford CS336: Language Modeling from Scratch** は、2026年3月30日から6月3日にかけて開講されたスタンフォード大学のコースで、ChatGPTやClaudeのようなLLMを「一から」実装することを目標にしている。

- **講師**: Tatsunori Hashimoto / Percy Liang（Stanford NLPの主要研究者）
- **公式サイト**: [cs336.stanford.edu](https://cs336.stanford.edu/)
- **YouTube プレイリスト**: [Spring 2026 全講義](https://www.youtube.com/playlist?list=PLoROMvodv4rMqXOcazWaTUHhq-yembLCV)
- **GitHub**: [stanford-cs336](https://github.com/stanford-cs336)

OSの仕組みを学ぶために「OSを自作するコース」があるように、このコースではLLMの仕組みを学ぶために**LLM自体を自作する**という哲学を貫いている。

## 講義でカバーされる内容

### データ収集・クリーニング

事前学習に必要なデータをCommon Crawlのダンプから構築する方法を学ぶ。フィルタリングや重複排除など、大規模テキストデータの品質管理も含まれる。

### トランスフォーマーの実装

Transformerアーキテクチャの各コンポーネント（Self-Attention、FFN、LayerNorm等）を一から実装し、それぞれの役割を深く理解する。

### モデルのトレーニング

スケーリング則（Scaling Laws）を使ったモデルサイズと学習量の見積もり、分散学習（データ並列・テンソル並列）、GPU最適化まで踏み込む。

### アライメントと強化学習

RLHF（人間のフィードバックによる強化学習）を含むアライメント手法の実装も演習に含まれる。

### トークナイザーからRL基盤まで

5つの主要課題を通じて、BPEトークナイザーの実装から始まり、RLベースのアライメント手法まで一気通貫で経験する。「他のコースの少なくとも10倍のコードを書くことが期待される」と公式サイトに記載があるほど実装量が多い。

## 第1回講義: Overview と Tokenization

特に話題を集めているのが**第1回講義（Overview, Tokenization）**で、YouTubeで公開されている。

- **YouTube**: [Lecture 1: Overview, Tokenization](https://www.youtube.com/watch?v=JuoVZkPBiKk)
- 時間: 約1時間44分

この講義一本で、LLMのアーキテクチャ全体の俯瞰からトークナイザーの実装まで理解できる構成になっている。Xで拡散したのはこの動画（またはその切り抜き）だ。

## なぜ無料公開されているのか

スタンフォードは以前からCS229（機械学習）やCS231n（画像認識）などの人気コースをYouTubeで無料公開してきた。CS336もその流れを受けて全講義がYouTubeで視聴可能だ。

ChatGPTが世界中に普及した今、「LLMがどう動くか」を本当に理解しているエンジニアはまだ少ない。CS336はその知識格差を埋める最短ルートの一つだ。

## どう活用するか

### エンジニア・ML実践者向け

全10週分の講義動画とスライド、GitHubのコード課題が揃っているので、自分のペースで独学できる。特に実装課題は「一から実装することでブラックボックスをなくす」という点で非常に価値が高い。

### 勉強会・チーム学習

講義動画を見ながら輪読会形式で進めるのも有効だ。プレイリストが整備されているので進捗管理もしやすい。

### キャッチアップ教材として

「Transformerはなんとなく知っているが内部は追っていない」というエンジニアにとって、CS336の第1講義は最適な入り口になる。

## まとめ

| 項目 | 内容 |
|------|------|
| コース名 | Stanford CS336: Language Modeling from Scratch |
| 講師 | Tatsunori Hashimoto, Percy Liang |
| 期間 | 2026年3月〜6月（Spring 2026） |
| 公式サイト | [cs336.stanford.edu](https://cs336.stanford.edu/) |
| YouTube | [全講義プレイリスト](https://www.youtube.com/playlist?list=PLoROMvodv4rMqXOcazWaTUHhq-yembLCV) |
| GitHub | [stanford-cs336](https://github.com/stanford-cs336) |
| 費用 | 無料（視聴のみ） |

大手AI企業が公開するブログやドキュメントを読むより、「自分で実装する」というプロセスがLLMの理解を本物にする。スタンフォードがその機会を無料で提供している今、まずは第1講義から視聴してみてほしい。
