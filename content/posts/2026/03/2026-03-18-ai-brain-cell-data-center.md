---
title: "人間の脳細胞で動く「データセンター」— Cortical Labs の生体コンピューティング革命"
date: 2026-03-18
lastmod: 2026-03-18
draft: false
source_url: "https://github.com/hdknr/blogs/issues/1#issuecomment-4079198048"
categories: ["AI/LLM"]
tags: ["ai", "biocomputing", "data-center", "energy"]
description: "Cortical Labs が脳細胞を使った生体データセンターを建設予定。消費電力は電卓以下で、AI のエネルギー問題に挑む生体コンピューティングの最前線を解説。"
---

オーストラリアのスタートアップ Cortical Labs が、人間の脳細胞（ニューロン）をシリコンチップ上に培養し、それを演算装置として利用する「生体データセンター」の構想を発表しました。1 台あたりの消費電力は電卓以下とされ、従来の GPU ベースの AI インフラとはまったく異なるアプローチで、エネルギー問題への解決策として注目されています。

## CL1 — 生体コンピュータユニット

Cortical Labs が開発した **CL1** は、ヒト血液幹細胞から培養した約 20 万個のニューロンをマイクロ電極アレイ（MEA）チップ上に配置した生体コンピュータです。

主な特徴:

- **電気信号によるソフトウェア連携**: MEA チップを通じてニューロンに電気信号を送信し、その応答をリアルタイムで記録・処理する
- **超低消費電力**: 1 台の CL1 の消費電力は電卓以下。GPU クラスタと比較して桁違いに省エネルギー
- **長寿命**: ニューロンは通常 6 か月以上生存し、最長 1 年の維持実績がある
- **学習能力**: 少量のデータセットから学習可能で、構造化された電気フィードバックにより適応的に活動パターンを変化させる

## DishBrain — Pong から DOOM へ

CL1 の基盤となった研究が **DishBrain** プロジェクトです。

- **2022 年**: 学術誌「Neuron」に論文発表。約 80 万個の培養ニューロンが Pong ゲームをプレイすることに成功
- **2026 年 2 月**: より複雑な 3D ゲーム「DOOM」のプレイに成功。生体ニューロンの情報処理能力の向上を実証

2022 年の Pong 成功以降、ニューロンの制御精度と情報処理能力の改善を重ね、4 年で単純な 2D ゲームから複雑な 3D 環境への対応を実現しました。

## データセンター構想

Cortical Labs は 2 つの生体データセンターの建設を計画しています。

### メルボルン（オーストラリア）

- **120 台** の CL1 ユニットを設置予定
- Cortical Labs 本社近くに建設

### シンガポール

- サステナビリティ重視のデータセンター企業 **DayOne Data Centers** と提携
- シンガポール国立大学 Yong Loo Lin 医学部に **20 台** の CL1 ユニットを設置するプロトタイプ施設を初期検証フェーズとして構築
- 最終的には約 **1,000 台** の CL1 を擁する大規模 Bio Data Centre を建設予定（2026 年 9 月頃着手目標）

## なぜ脳細胞なのか — AI のエネルギー危機

AI の学習・推論に必要な計算量は急速に増大しており、データセンターの消費電力は世界的な課題です。生体ニューロンには以下の優位性があります:

- **エネルギー効率**: 人間の脳は約 20W で動作し、同等の処理を行う GPU クラスタの数千分の一の電力で済む
- **複雑な情報処理**: ノイズの多いデータや構造が統一されていないデータに対する判断能力では、生体ニューロンが従来のコンピュータを大幅に上回る
- **少量データ学習**: 大量のデータセットを必要とする従来の深層学習と異なり、少ないサンプルから効率的に学習できる

## オルガノイド・インテリジェンス（OI）

Cortical Labs の取り組みは、**オルガノイド・インテリジェンス（OI）** という新しい学際分野の一部です。幹細胞由来の脳オルガノイド（3D 培養脳組織）を計算ユニットとして活用する研究が世界的に進んでいます。

米国の国立科学財団（NSF）も 2024 年に「Biocomputing through EnGINeering Organoid Intelligence」プログラムを立ち上げ、倫理学者を共同主任研究者として必須とするなど、技術と倫理の両面から研究が推進されています。

## 倫理的課題

生体ニューロンを計算に利用することには、倫理的な議論が伴います。培養された脳細胞に「意識」が生じる可能性はあるのか、生体組織を商業的な計算インフラとして利用することの倫理的な問題など、技術の進展とともに慎重な議論が求められています。

一部の脳オルガノイド研究の先駆者からは、バイオコンピューティングに対する過大な主張がバックラッシュを招く可能性への懸念も表明されています。

## まとめ

Cortical Labs の生体データセンター構想は、AI インフラのエネルギー問題に対する根本的に新しいアプローチです。DOOM をプレイできるニューロンチップから、1,000 台規模のデータセンターへ。2026 年後半にかけて、この「脳細胞データセンター」がどこまで実用化に近づくか注目です。

## 参考リンク

- [Cortical Labs 公式サイト — CL1](https://corticallabs.com/cl1)
- [Tom's Hardware — Human brain cells set to power two new data centers](https://www.tomshardware.com/tech-industry/artificial-intelligence/human-brain-cells-set-to-power-two-new-data-centers-thanks-to-body-in-the-box-cl1-cortical-labs-targets-the-ai-energy-crisis-with-biological-computer-that-reportedly-uses-less-energy-than-a-calculator)
- [Data Center Dynamics — Cortical Labs partners with DayOne](https://www.datacenterdynamics.com/en/news/australian-startup-cortical-labs-unveils-biological-data-center-prototype/)
- [ITmedia — 人間の"脳細胞"で動く「データセンター」開設へ](https://www.itmedia.co.jp/news/articles/2603/18/news037.html)
