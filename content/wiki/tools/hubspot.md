---
title: "HubSpot"
description: "インバウンドマーケティングを軸とした CRM・MA・営業統合プラットフォーム"
date: 2026-04-28
lastmod: 2026-07-28
aliases: ["hubspot crm", "hubspot pro"]
related_posts:
  - "/posts/2026/04/hubspot-hscachebuster/"
  - "/posts/2026/04/hubspot-pro-merits/"
  - "/posts/2026/07/hubspot-eu-email-tracking-consent/"
tags: ["hubspot", "crm", "ma", "インバウンドマーケティング", "営業"]
---

## 概要

HubSpot は CRM（顧客管理）、MA（マーケティングオートメーション）、営業支援、カスタマーサポート、CMS を 1 つのプラットフォームに統合した SaaS。インバウンドマーケティング思想（顧客に「見つけてもらう」発想）を製品化したのが特徴。

公式: <https://www.hubspot.com/>

## エディション

無料プランから始めて、Starter / Professional / Enterprise へとステップアップする構成。

- **Free**: CRM の基本機能・コンタクト管理・基本フォーム
- **Starter**: 小規模ビジネス向け・有料機能の入口
- **Professional**: ワークフロー自動化・カスタムレポート・SEO 推奨機能などが揃う中核プラン
- **Enterprise**: 大規模組織向け・カスタムオブジェクト・高度な権限管理

Pro プランは「機能の網羅性」と「価格」のバランス点で、本格運用の最初の選択肢になりやすい。

## 主要機能

- **CRM**: 顧客・商談・タスクの一元管理。無料から使える
- **マーケティング**: メールマーケティング、ランディングページ、SEO 推奨、ワークフロー
- **セールス**: シーケンス（メール自動送信）、ミーティング予約、商談パイプライン管理
- **サービス**: チケット管理、ナレッジベース、フィードバック収集
- **CMS**: コンテンツ配信用 CMS（テーマ・モジュール開発可能）
- **オペレーションズ**: データ同期・カスタムコード・ガバナンス

## 開発者向けの留意点

CMS Hub のテーマ開発では **`hsCacheBuster`** などの内部キャッシュ制御パラメータが付与される。テンプレート上書きやキャッシュ無効化の挙動把握が、フロント実装のトラブルシュート上重要になる。

## EU/UK 宛メールの注意点

EU/UK のコンタクトにマーケティングメールを送る場合、**HubSpot の機能名と法令が 1 対 1 で対応していない**ため設計を誤りやすい。「送れるか」（ePrivacy 13条）と「開封・クリックを測れるか」（ePrivacy 5条3項）は別問題であり、送信可・トラッキング不可という状態が普通に発生する。

既存コンタクトの同意状態を「一旦リセットして全員に許諾メールを送る」のは最もリスクの高い操作にあたる。詳細は [EU/UK 宛メールのトラッキング同意設計](/blogs/wiki/guides/hubspot-eu-email-consent/) を参照。

## 関連ページ

- [インバウンドマーケティング](/blogs/wiki/concepts/inbound-marketing/) — HubSpot の根幹思想
- [EU/UK 宛メールのトラッキング同意設計](/blogs/wiki/guides/hubspot-eu-email-consent/) — GDPR / ePrivacy 対応

## ソース記事

- [HubSpot Pro プランの実用メリット](/blogs/posts/2026/04/hubspot-pro-merits/) — 2026-04-28
- [HubSpot CMS の hsCacheBuster](/blogs/posts/2026/04/hubspot-hscachebuster/) — 2026-04-23
- [HubSpot で EU/UK 宛にメールを送るときの注意点 ── トラッキング同意と製品仕様の実務メモ](/blogs/posts/2026/07/hubspot-eu-email-tracking-consent/) — 2026-07-28
