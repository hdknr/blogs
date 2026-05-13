---
title: "HubSpot"
description: "インバウンドマーケティングを軸とした CRM・MA・営業統合プラットフォーム"
date: 2026-04-28
lastmod: 2026-04-28
aliases: ["hubspot crm", "hubspot pro"]
related_posts:
  - "/posts/2026/04/2026-04-23-hubspot-hscachebuster/"
  - "/posts/2026/04/2026-04-28-hubspot-pro-merits/"
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

## 関連ページ

- [インバウンドマーケティング](/blogs/wiki/concepts/inbound-marketing/) — HubSpot の根幹思想

## ソース記事

- [HubSpot Pro プランの実用メリット](/blogs/posts/2026/04/2026-04-28-hubspot-pro-merits/) — 2026-04-28
- [HubSpot CMS の hsCacheBuster](/blogs/posts/2026/04/2026-04-23-hubspot-hscachebuster/) — 2026-04-23
