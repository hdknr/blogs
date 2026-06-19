---
title: "kabu ステーション API"
description: "三菱UFJ eスマート証券（旧 auカブコム証券）が提供する個人向け自動発注 API。REST + WebSocket Push で株式・先物の発注と約定通知を扱える"
date: 2026-05-20
lastmod: 2026-05-20
aliases: ["kabuS API", "kabusapi", "auカブコム API"]
related_posts:
  - "/posts/2026/05/nikkei225-micro-monte-carlo-claude/"
tags: ["kabuステーション", "三菱UFJ eスマート証券", "自動売買", "API", "WebSocket"]
---

## 概要

kabu ステーション API は **三菱UFJ eスマート証券（旧 auカブコム証券）** が提供する個人向けの自動発注 API である。日本国内で個人が利用できる主要な自動発注 API のひとつで、REST + WebSocket Push で発注操作と約定通知の両方を扱える。

- リファレンス: <https://kabucom.github.io/kabusapi/reference/index.html>
- PUSH API: <https://kabucom.github.io/kabusapi/ptal/push.html>

## 主要機能

- **REST API**: 発注・取消・建玉照会・口座情報取得
- **WebSocket Push**: 約定通知・板情報のストリーミング
- 現物株・信用取引・先物・オプション・FX をカバー

## 自動売買での位置づけ

Monte Carlo + Claude 系の自動売買アーキテクチャでは「発注層」を担当する。

- 判定層が `LONG / SHORT / FLAT` のシグナルを出した直後、kabu API で実発注
- WebSocket Push で約定通知を受け取り、ポジション状態を更新
- 紙トレードから本番運用への移行が比較的スムーズ

## 注意点

- 2024 年に **auカブコム証券 → 三菱UFJ eスマート証券** に社名変更されている
- 旧名（auカブコム証券）で書かれた古いドキュメント・記事も残っているため検索時は要注意

## 関連ページ

- [J-Quants API](/blogs/wiki/tools/j-quants-api/) — データ取得層
- [モンテカルロ法による売買判定](/blogs/wiki/concepts/monte-carlo-trading/) — 本 API の主要ユースケース

## ソース記事

- [日経225マイクロ先物 × Monte Carlo 自動売買判定 — Claude + 1万通りシミュレーションで勝率55%超のときだけ発注する実装](/blogs/posts/2026/05/nikkei225-micro-monte-carlo-claude/) — 2026-05-20
