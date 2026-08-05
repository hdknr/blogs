---
title: "RDS Blue/Green デプロイでのバージョン移行"
description: "RDS for MySQL のマイナー／メジャー移行を Blue/Green で行うときの Terraform 設計、切替のタイムライン、DNS 伝播による実停止時間の実測"
date: 2026-08-05
lastmod: 2026-08-05
aliases: ["RDS Blue/Green", "Blue/Green デプロイ", "MySQL 8.4 移行", "RDS バージョンアップ", "標準サポート終了"]
related_posts:
  - "/posts/2026/08/rds-mysql-84-blue-green-migration/"
tags: ["aws", "rds", "mysql", "terraform", "blue-green-deployment"]
---

## 概要

RDS の Blue/Green デプロイは、本番（Blue）のレプリカとして別バージョンの環境（Green）を作り、同期させたうえでエンドポイントを切り替える機能。バージョン移行のダウンタイムを短くする目的で使う。

## 実停止時間は「書き込み停止1秒」ではない

最も重要な実測値がここにある。**RDS 側の書き込み停止が1秒でも、アプリから見た停止は24秒**になった。差分の原因は **DNS 伝播**である。

切替時にエンドポイントの向き先が変わるため、アプリケーション側の DNS キャッシュが切れるまで旧インスタンスを見続ける。移行計画のダウンタイム見積りは、RDS が公表する切替時間ではなく **DNS TTL とコネクションプールの挙動を含めた実測**で立てる必要がある。

## Terraform 側の設計 — family 差し替えではなく「併設」

パラメータグループを新バージョン用の family に差し替える形で書くと、Blue/Green の途中状態を表現できない。**新旧のパラメータグループを併設**しておき、切替後に不要な側を消す設計にする。

## 切替後は実質ロールバックできない

Green へ切り替えた時点で、旧 Blue へ戻す現実的な経路は失われると考えたほうがよい。切替前の検証と、切替後に発覚した問題を前進で直す準備の両方が要る。

## 効果が大きかった準備

- 事前に本番同等データで Green を作り、アプリケーションから実際に接続して検証する
- DNS TTL とコネクションプールの再接続挙動を事前に確認する
- 切替のタイムラインを分単位で書き出し、各ステップの判断者を決めておく

公式の事前資料に載っていない落とし穴が複数あるため、**リハーサルを1回通す**ことが最も効く。

## 関連ページ

- [Terraform で IaC](/blogs/wiki/guides/terraform-iac/) — インフラ定義側
- [AWS Compute Optimizer](/blogs/wiki/tools/aws-compute-optimizer/) — 移行後のサイジング見直し
- [インシデントレスポンス](/blogs/wiki/guides/incident-response/) — 切替失敗時の体制

## ソース記事

- [RDS for MySQL 8.0 → 8.4 を標準サポート終了当日に Blue/Green で移行した記録 — 実測](/blogs/posts/2026/08/rds-mysql-84-blue-green-migration/) — 2026-08-03
