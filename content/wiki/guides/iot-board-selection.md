---
title: "IoT開発ボードの選定"
description: "M5Stack / Raspberry Pi / Arduino / ESP32 / Wio を「試作↔量産」「シンプル↔高機能」の2軸で選び分ける"
date: 2026-07-28
lastmod: 2026-07-28
aliases: ["IoT基板の選び方", "マイコン選定", "SBC比較"]
related_posts:
  - "/posts/2026/07/iot-microcontroller-sbc-comparison/"
  - "/posts/2026/07/esp32-iot-microcontroller-explained/"
tags: ["IoT", "M5Stack", "Raspberry Pi", "Arduino", "ESP32"]
---

## 概要

IoT の基板選びは 2 軸で整理すると迷いにくい。**横軸が「試作・プロトタイプ向き ↔ 量産・本格運用向き」**、**縦軸が「シンプル・省電力 ↔ Linux が動くほど高機能」**。作りたいソリューションの要件から逆算して選ぶ。

## 2軸マップ上の位置

| ボード | 位置づけ | 一言 |
|---|---|---|
| **M5Stack** | 試作寄り・シンプル | ESP32 に液晶・ボタン・バッテリー・ケースを付けた完成品モジュール |
| **Raspberry Pi** | 試作寄り・高機能 | Linux が動く小さなパソコン（SBC） |
| **Arduino** | 試作寄り・シンプル | プロトタイピングの元祖。情報量が最も多い |
| **ESP32（単体）** | 量産寄り・シンプル | M5Stack の中身。組み込み前提 |
| **Wio LTE / Wio Terminal** | 中央 | セルラー通信内蔵の IoT 特化型 |

## 各ボードの使いどころ

### Raspberry Pi

**Linux OS が動く小さなパソコン**。M5Stack や Arduino が「電子回路を制御するチップ（マイコン）」なのに対し、こちらは汎用計算機に近い。カメラ画像の AI 推論、複数プロセスの常駐、データベースを載せる、といった用途で選ぶ。消費電力とコストは高め。

### Arduino

プロトタイピングの元祖。日本語情報とライブラリが豊富で、電子工作の学習に向く。ただし基本モデルは通信機能を持たないため、IoT 化には別途 Wi-Fi パーツが必要になる。

### ESP32

Wi-Fi/BLE 内蔵で数百円という価格が効く。詳細は [ESP32](/blogs/wiki/tools/esp32/) を参照。

### Wio LTE / Wio Terminal

**セルラー通信を内蔵**した IoT 特化型ボード。Wi-Fi の届かない屋外・現場に置くケースで選択肢になる。

## 選び方の指針

- 「画面でパッと状態を見たい」→ **M5Stack**
- 「AI で画像認識させたい」→ **Raspberry Pi**
- 「電池で長期間動かしたい・量産したい」→ **ESP32**
- 「電源も Wi-Fi もない屋外に置く」→ **Wio + セルラー**、または [SORACOM](/blogs/wiki/tools/soracom/) の SIM 付きデバイス
- 「まず電子工作を学びたい」→ **Arduino**

### セルラー以外の選択肢

屋外測位では、スマホを中継役に使うクラウドソース測位という手もある。専用回線を引かずに済むぶん初期コストを下げられる。

## 関連ページ

- [ESP32](/blogs/wiki/tools/esp32/) — M5Stack の中身にあたるチップ
- [SORACOM](/blogs/wiki/tools/soracom/) — セルラー接続とデバイス調達
- [予知保全と保全高度化ラダー](/blogs/wiki/concepts/predictive-maintenance/) — 設備保全での活用文脈

## ソース記事

- [IoT開発ボードの使い分け完全比較 — M5Stack / Raspberry Pi / Arduino / ESP32 / Wio](/blogs/posts/2026/07/iot-microcontroller-sbc-comparison/) — 2026-07-19
- [ESP32とは？IoTで「最強」と呼ばれるマイコンチップの3つの理由とM5Stackとの関係](/blogs/posts/2026/07/esp32-iot-microcontroller-explained/) — 2026-07-19
