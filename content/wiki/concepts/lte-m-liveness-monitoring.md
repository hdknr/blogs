---
title: "LTE-M 機の死活監視とセッション挙動"
description: "LTE-M IoT 機器のセッション再接続の切り分けと、死活監視の閾値をサンプリング周期から逆算する方法"
date: 2026-08-23
lastmod: 2026-08-23
aliases: ["LTE-M 死活監視", "PSM", "セッション再接続"]
related_posts:
  - "/posts/2026/08/lte-session-reconnect-iot-gateway/"
  - "/posts/2026/08/lte-m-liveness-monitoring-interval/"
tags: ["IoT", "SORACOM", "LTE-M", "遠隔監視", "監視"]
---

## 概要

LTE-M を使う IoT 機器の運用で頻出する 2 つの問題 —— 「セッションが張り直され続ける」と「無通信アラートの閾値をどう決めるか」—— を扱う。どちらも **デバイスのサンプリング周期と電源構成** に帰着する。

## セッションが Deleted → Created を繰り返す

SORACOM のセッション履歴に Deleted → Created が繰り返し記録される場合、デバイス・無線区間・コア網・プラットフォームの 4 層で切り分ける。

### 3つの誤解

| 誤解 | 実際 |
|---|---|
| ハンドオーバーでセッションが張り直される | ハンドオーバーは **Modified** として記録される。Deleted → Created ではない |
| PSM が張り直しを増やしている | **PSM は張り直しを増やさない** |
| コンソールのオンライン表示で生死が分かる | **オンライン表示は証拠にならない** |

確認は `soracom sims session-events` で実際のイベント種別を見る。表示ではなくイベントログが根拠になる。

## 「1分間通信がなければアラート」は作れるか

SORACOM Lagoon 3 の no data アラートで「一定時間データが来なければ通知」自体は作れる。問題は閾値の決め方で、**これはデバイスのサンプリング周期で決まる**。

### 電源構成で結論が反転する

| 電源 | サンプリング周期 | 1分アラートの可否 |
|---|---|---|
| **USB 給電** | 出荷時 10 秒（SmartFitPRO の例） | 周期の 6 倍で妥当。**作れる** |
| **電池運用** | 周期を延ばすしかない | 無通信タイマーを超えてしまい、**成立しない** |

電池運用では周期を延ばすことでしか電池を持たせられず、その結果アラート閾値が無通信タイマーを超える。「1 分アラート」は電源構成の話であって、監視ツールの機能の話ではない。

## 関連ページ

- [SORACOM](/blogs/wiki/tools/soracom/) — セッション管理と Lagoon 3
- [IoT センサーのカテゴリ](/blogs/wiki/concepts/iot-sensor-categories/)
- [IoT ボードの選定](/blogs/wiki/guides/iot-board-selection/)

## ソース記事

- [SORACOM のセッションが Deleted → Created を繰り返す](/blogs/posts/2026/08/lte-session-reconnect-iot-gateway/) — 2026-08-19
- [「1 分間通信がなければアラート」は作れるか](/blogs/posts/2026/08/lte-m-liveness-monitoring-interval/) — 2026-08-20
