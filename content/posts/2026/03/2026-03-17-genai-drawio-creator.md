---
title: "AWS Japan AI チームが draw.io 図解自動生成を arXiv 論文化——GenAI-DrawIO-Creator の概要"
date: 2026-03-17
lastmod: 2026-03-17
draft: false
source_url: "https://github.com/hdknr/blogs/issues/1#issuecomment-4078673005"
categories: ["AI/LLM"]
tags: ["draw.io", "Amazon Bedrock", "Claude", "図解生成", "arXiv"]
---

AWS Japan AI チームが「draw.io の図解自動生成」フレームワークを arXiv 論文にまとめた。論文名は **GenAI-DrawIO-Creator**（arXiv 2601.05162、2026年1月）。実装は GitHub で公開され、GitHub Trending の2位まで到達した。

## 概要

自然言語のテキストを入力すると、draw.io で使える XML 形式のダイアグラムを自動生成するフレームワーク。バックエンドには **Claude 3.7** を Amazon Bedrock 経由で使用している。

### 評価結果

| 指標 | 結果 |
|------|------|
| 初回セマンティック精度 | 94% |
| フィードバック後の精度 | 100% |
| 平均生成時間 | 7.4 秒（手動比約 5 倍速） |

「7.4秒で図が生成される」体験が当たり前になる日が近づいている。

## 仕組み

フレームワークの処理フローは以下のとおり:

1. **自然言語入力**: ユーザーがテキストでダイアグラムの内容を説明する
2. **LLM による XML 変換**: Claude 3.7 が自然言語を draw.io XML 形式に変換する
3. **フィードバックループ**: 生成結果を評価し、精度が不十分な場合は自動で再生成する
4. **draw.io への出力**: 生成した XML を draw.io で開いてそのまま使用できる

## GitHub 公開と反響

実装は **DayuanJiang/next-ai-draw-io** として GitHub で公開されており、公開直後に GitHub Trending の2位まで到達した。

- リポジトリ: [DayuanJiang/next-ai-draw-io](https://github.com/DayuanJiang/next-ai-draw-io)
- 論文: [arXiv 2601.05162](https://arxiv.org/abs/2601.05162)

## LLM と実用化の距離感

研究レベルから実用レベルへの距離がこれほど短いのは、LLM 関連の取り組みでは珍しくない。それでも毎回驚かされる。

ダイアグラム作成はエンジニアやデザイナーが日常的にこなす作業だが、手動での図解作成には相応の時間がかかる。7.4秒で初稿が出てくるなら、人間はレビューと調整に集中できる。「ツールを使う」から「ツールに説明する」へのシフトが、ドキュメント作業にも本格的に波及してきた。
