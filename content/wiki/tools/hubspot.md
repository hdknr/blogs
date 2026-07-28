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

## EU/UK 宛メールでの制約

メールトラッキング（開封ピクセル・計測リンク）は ePrivacy の同意対象になるが、HubSpot 側には**地域別・コンタクト別のトラッキング切替が上位プランにも存在しない**。アカウントレベルの 4 トグルとメール単位の ON/OFF しかなく、しかもメール単位の設定は**送信後に変更できない**。「処理の法的根拠」プロパティーは GDPR 6条・ePrivacy 13条に効くもので、5条3項（計測の同意）には効かない点も設計ミスの温床になる。詳細は [メールトラッキングと ePrivacy 同意](/blogs/wiki/concepts/email-tracking-consent/) を参照。

## 関連ページ

- [インバウンドマーケティング](/blogs/wiki/concepts/inbound-marketing/) — HubSpot の根幹思想
- [メールトラッキングと ePrivacy 同意](/blogs/wiki/concepts/email-tracking-consent/) — EU/UK 宛送信時の法令と製品仕様
- [メール認証（SPF/DKIM/DMARC）](/blogs/wiki/concepts/email-authentication/) — 到達性の前提

## ソース記事

- [HubSpot Pro プランの実用メリット](/blogs/posts/2026/04/hubspot-pro-merits/) — 2026-04-28
- [HubSpot CMS の hsCacheBuster](/blogs/posts/2026/04/hubspot-hscachebuster/) — 2026-04-23
- [HubSpot で EU/UK 宛にメールを送るときの注意点](/blogs/posts/2026/07/hubspot-eu-email-tracking-consent/) — 2026-07-28
