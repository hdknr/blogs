---
title: "予知保全と保全高度化ラダー"
description: "BM→TBM→CBM→PdM という設備保全の高度化モデルと、IoT が価値を出すレイヤーの見取り図"
date: 2026-07-28
lastmod: 2026-07-28
aliases: ["予知保全", "PdM", "CBM", "保全高度化ラダー", "保全成熟度モデル"]
related_posts:
  - "/posts/2026/07/soracom-iot-building-maintenance-classification/"
  - "/posts/2026/07/soracom-iot-maintenance-subsidy-guide/"
  - "/posts/2026/07/soracom-iot-construction-site-demand/"
tags: ["IoT", "予知保全", "設備保全", "ビルメンテナンス", "SORACOM"]
---

## 概要

設備保全には **BM（事後保全）→ TBM（時間基準保全）→ CBM（状態基準保全）→ PdM（予知保全）** という高度化の流れが古くからある。IoT の役割を軸にこれを段階化したものが**保全高度化ラダー（保全成熟度モデル）**で、段が上がるほど予測型の保全へ近づく。IoT の価値は特に **L3〜L5 への移行に集中する**。

## 保全の4段階

| 略号 | 名称 | 考え方 |
|---|---|---|
| **BM** | 事後保全 (Breakdown Maintenance) | 壊れてから直す |
| **TBM** | 時間基準保全 (Time Based Maintenance) | 一定周期で点検・交換する |
| **CBM** | 状態基準保全 (Condition Based Maintenance) | 実際の状態を測り、閾値で判断する |
| **PdM** | 予知保全 (Predictive Maintenance) | 兆候から故障時期を予測して先回りする |

## 保全高度化ラダー（5段）

上記に省エネ最適化を加え、IoT の役割で 5 段のラダーとして描いたもの。

| 段 | レイヤー | 対応する保全段階 | IoT の役割 |
|---|---|---|---|
| **L1** | 遠隔見える化 | BM の高速化 | 稼働状態や警報を遠隔で把握し、故障時の一次対応を早める |
| **L2** | 点検の省力化 | TBM の遠隔化 | 定期巡回・検針・法定点検を遠隔化・自動化する |
| **L3** | 状態基準保全 | CBM | 実測値の常時取得と閾値監視 |
| **L4** | 予知保全 | PdM | 兆候検知による故障予測 |
| **L5** | エネルギー最適化 | — | 省エネ・運転最適化まで踏み込む |

### L1 遠隔見える化

「現地に行かないと状態が分からない」を解消する段階。クラウドカメラで機械室や制御盤を遠隔目視したり、接点端子で既存設備の警報接点を拾ってクラウドへ上げたりする。

### L2 点検の省力化

温湿度／CO2 センサーで室内環境を常時記録し、カメラで遠隔臨検する。人手不足が深刻なビルメンテナンス業界では、**巡回そのものを減らす**効果が大きい。

## 分類軸としての有用性

「デバイス種別」でも「業種」でもなく**保全高度化ラダー**を主軸に据えると、建築設備メンテナンス（ビルメン／FM）の文脈で IoT ソリューションを整理しやすくなる。設備カテゴリ軸と監視パラメータ軸は、これに直交する副軸として扱う。

> 分類は「誰の課題を解くか」で変わる。一過性の工事現場と、何十年も守る建築設備とでは、有効な軸が異なる。

## 補助金との対応

設備保全の IoT 化には国・自治体の補助金が使える。**どの段（ラダー）の取り組みかによって当てはめるべき制度が変わる**ため、ラダーは補助金申請の枠組みとしても機能する。詳細は [設備保全IoTの補助金制度](/blogs/wiki/guides/iot-maintenance-subsidy/) を参照。

## 関連ページ

- [SORACOM](/blogs/wiki/tools/soracom/) — 保全 IoT の主要プラットフォーム
- [設備保全IoTの補助金制度](/blogs/wiki/guides/iot-maintenance-subsidy/) — ラダー別の制度対応
- [IoT開発ボードの選定](/blogs/wiki/guides/iot-board-selection/) — デバイス側の選択肢

## ソース記事

- [建築設備メンテナンス視点で SORACOM の IoT を分類し直す — 保全高度化ラダーという第3の軸](/blogs/posts/2026/07/soracom-iot-building-maintenance-classification/) — 2026-07-22
- [【2026年度版】設備保全IoTに使える補助金制度ガイド](/blogs/posts/2026/07/soracom-iot-maintenance-subsidy-guide/) — 2026-07-22
- [SORACOM の IoT ソリューションは建設・工事現場で求められているか](/blogs/posts/2026/07/soracom-iot-construction-site-demand/) — 2026-07-22
