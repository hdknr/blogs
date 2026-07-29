---
title: "ESP32"
description: "Wi-Fi/BLE を内蔵し数百円から使える IoT 向けマイコンチップ。M5Stack の中身でもある"
date: 2026-07-28
lastmod: 2026-07-28
aliases: ["ESP32-WROOM", "M5Stack の中身"]
related_posts:
  - "/posts/2026/07/esp32-iot-microcontroller-explained/"
  - "/posts/2026/07/iot-microcontroller-sbc-comparison/"
tags: ["ESP32", "IoT", "M5Stack", "マイコン", "Wi-Fi"]
---

## 概要

Espressif Systems が開発した IoT 向けマイコンチップ。Wi-Fi と Bluetooth (BLE) を内蔵し、チップ単体なら数百円、開発ボードでも 1,000〜2,000 円前後で入手できる。銀色のシールドカバーの中に通信機能まで詰め込まれており、「買ってきてすぐ通信できる」手軽さが IoT のハードルを大きく下げた。

## 「最強」と言われる3つの理由

### 1. 通信機能が最初から全部入り

Arduino Uno など従来の基本的なマイコンは、インターネット接続に別売りの Wi-Fi パーツが必要だった。ESP32 は **Wi-Fi と BLE を内蔵**しており、単体でデータをクラウドへ送ったりスマホと通信したりできる。

### 2. 破壊的な安さ

高性能でありながらチップ単体で数百円。「とりあえず試してみる」の心理的・金銭的コストがほとんどかからない。

### 3. 省電力

小型かつ省電力で、電池駆動のセンサーノード用途に向く。

## 生基板と開発ボードの違い

- **生基板（チップ／モジュール単体）** — 量産・組み込み向け。基板設計が前提
- **開発ボード** — USB ポートやピンヘッダが実装済み。学習・試作向け

## M5Stack との関係

**M5Stack の中身は ESP32 そのもの**である。M5Stack は ESP32 に液晶・ボタン・バッテリー・ケースを組み合わせ、すぐ使える形にモジュール化した製品と理解するとよい。「画面でパッと状態を見たい」用途では M5Stack、量産や組み込みでは ESP32 単体、という使い分けになる。

## 他ボードとの位置づけ

IoT 基板は「試作↔量産」「シンプル・省電力↔高機能（Linux）」の 2 軸で整理できる。ESP32 単体は**量産寄り・シンプル省電力**の象限に位置する。詳細は [IoT開発ボードの選定](/blogs/wiki/guides/iot-board-selection/) を参照。

## 採用例

スマートホーム家電の内部に組み込まれているケースが多く、市販の Wi-Fi 対応スマートプラグやセンサー類を分解すると ESP32 系のモジュールが出てくることがある。

## 関連ページ

- [IoT開発ボードの選定](/blogs/wiki/guides/iot-board-selection/) — M5Stack / Raspberry Pi / Arduino / Wio との比較
- [SORACOM](/blogs/wiki/tools/soracom/) — セルラー接続を足す場合のプラットフォーム

## ソース記事

- [ESP32とは？IoTで「最強」と呼ばれるマイコンチップの3つの理由とM5Stackとの関係](/blogs/posts/2026/07/esp32-iot-microcontroller-explained/) — 2026-07-19
- [IoT開発ボードの使い分け完全比較 — M5Stack / Raspberry Pi / Arduino / ESP32 / Wio](/blogs/posts/2026/07/iot-microcontroller-sbc-comparison/) — 2026-07-19
