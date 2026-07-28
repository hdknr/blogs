---
title: "SORACOM"
description: "IoT 向け通信プラットフォーム。SIM・センサー・カメラを接続／収集／導入の3レイヤで提供する"
date: 2026-07-28
lastmod: 2026-07-28
aliases: ["ソラコム", "ソラカメ", "LTE-M Button"]
related_posts:
  - "/posts/2026/07/soracom-iot-store-solution-map/"
  - "/posts/2026/07/soracom-iot-building-maintenance-classification/"
  - "/posts/2026/07/soracom-iot-construction-site-demand/"
  - "/posts/2026/07/soracom-iot-maintenance-subsidy-guide/"
tags: ["IoT", "SORACOM", "LTE-M", "センサー", "遠隔監視"]
---

## 概要

IoT 向けの通信プラットフォーム。SIM・通信モジュールから GPS トラッカー・環境センサー・クラウドカメラ・LTE-M ボタンまでを IoT ストアで提供する。デバイスカタログとして眺めるよりも、**「どんな課題を解くか」のソリューション軸**で捉えるほうが実務では使いやすい。

## 3つのレイヤ

| レイヤ | 役割 | 主な製品 |
|---|---|---|
| **接続レイヤ（つなぐ）** | データをクラウドへ届ける土台 | SIM、通信モジュール、ルーター |
| **収集レイヤ（取る）** | 位置・環境・映像・操作・設備のデータ取得 | GPS トラッカー、各種センサー、ソラカメ、LTE-M Button |
| **導入・拡張レイヤ（立ち上げる）** | PoC・学習からパッケージ導入までの支援 | スターターキット、導入支援 |

この 3 層を「業種別ユースケース」（物流・店舗・インフラ保守・見守り・農業など）が束ねる構造になっている。

## 主要デバイス

- **ソラカメ** — クラウドカメラ。機械室や制御盤の遠隔目視、現場の遠隔臨場に使う
- **LTE-M Button Plus** — 接点端子を持ち、既存設備の警報接点を拾ってクラウドへ上げられる。レトロフィット用途に強い
- **GPS マルチユニット / 環境センサー** — 位置・温湿度・CO2 などの常時取得

## 建設・工事現場での需要

建設現場で IoT 需要が高い背景には 3 つの構造的圧力がある。

- **人手不足** — 巡回・監視の省力化圧力
- **労働災害・熱中症対策** — 環境モニタリングと即時アラート
- **遠隔臨場** — 発注者検査の遠隔化（国交省が推進）

大成建設や Nikon-Trimble の導入事例がある。接続レイヤが特に効くのは、**工事現場が「電源も回線もない場所に一時的に立つ」**ためで、セルラー接続前提のデバイスが刺さりやすい。

## 建築設備メンテナンスでの位置づけ

工事現場が「一過性の現場」なのに対し、ビルメンテナンス／FM は「何十年も守る設備」を相手にする。このため分類軸が変わり、[保全高度化ラダー](/blogs/wiki/concepts/predictive-maintenance/)（BM→TBM→CBM→PdM）を主軸に据えるほうが整理しやすい。ダイキンの Kirei ウォッチ、キッツのバルブ予兆検知などが実事例として挙げられる。

## 導入のリアル

PoC から始めるケースが多く、**補助金の活用が前提になりやすい**。中小企業省力化投資補助金、デジタル化・AI導入補助金（旧 IT 導入補助金）、ものづくり補助金、省エネ補助金（SII）、自治体制度などが対象になる。詳細は [設備保全IoTの補助金制度](/blogs/wiki/guides/iot-maintenance-subsidy/) を参照。

## 関連ページ

- [予知保全と保全高度化ラダー](/blogs/wiki/concepts/predictive-maintenance/) — 保全文脈での分類軸
- [設備保全IoTの補助金制度](/blogs/wiki/guides/iot-maintenance-subsidy/) — 導入資金の制度
- [IoT開発ボードの選定](/blogs/wiki/guides/iot-board-selection/) — 自作デバイス側の選択肢
- [ESP32](/blogs/wiki/tools/esp32/) — Wio など SORACOM 系ボードの中身

## ソース記事

- [SORACOM IoT ストアの取扱製品を「ソリューション」で分類する](/blogs/posts/2026/07/soracom-iot-store-solution-map/) — 2026-07-22
- [建築設備メンテナンス視点で SORACOM の IoT を分類し直す](/blogs/posts/2026/07/soracom-iot-building-maintenance-classification/) — 2026-07-22
- [SORACOM の IoT ソリューションは建設・工事現場で求められているか](/blogs/posts/2026/07/soracom-iot-construction-site-demand/) — 2026-07-22
- [【2026年度版】設備保全IoTに使える補助金制度ガイド](/blogs/posts/2026/07/soracom-iot-maintenance-subsidy-guide/) — 2026-07-22
