---
title: "脆弱性管理の次の時代 ── Exposure Management とは何か"
date: 2026-03-11
lastmod: 2026-03-11
draft: false
source_url: "https://github.com/hdknr/blogs/issues/1#issuecomment-4041976236"
categories: ["セキュリティ"]
tags: ["security"]
---

企業のセキュリティチームは深刻な課題に直面しています。NVD（National Vulnerability Database）に登録される CVE は年間 25,000 件以上。多くの企業では数万〜数十万の脆弱性がスキャンで検出されます。しかし現実は明確で、「すべてを修正することは不可能」です。

この状況を背景に、ガートナーは新しいセキュリティの考え方として **Exposure Management（エクスポージャー管理）** を提示しました。

## CVSS とは何か

Exposure Management を理解する前に、従来の脆弱性管理の中核にある **CVSS（Common Vulnerability Scoring System）** について押さえておきましょう。

CVSS は、脆弱性の深刻度を **0.0〜10.0** のスコアで数値化する国際的な評価基準です。FIRST（Forum of Incident Response and Security Teams）が管理しており、現在は v3.1 と v4.0 が使われています。

| スコア | 深刻度 |
|--------|--------|
| 9.0〜10.0 | Critical（緊急） |
| 7.0〜8.9 | High（重要） |
| 4.0〜6.9 | Medium（警告） |
| 0.1〜3.9 | Low（注意） |

スコアは以下の観点から算出されます。

- **攻撃元区分** — ネットワーク経由か、物理アクセスが必要か
- **攻撃条件の複雑さ** — 特殊な条件が必要か
- **必要な特権レベル** — 認証が必要か
- **ユーザ関与** — ユーザの操作（リンクのクリック等）が必要か
- **影響範囲** — 機密性・完全性・可用性への影響度

CVSS は脆弱性の**技術的な深刻度**を標準化された方法で伝える点で非常に有用です。しかし、このスコアだけに頼る運用には限界があります。

## 従来の脆弱性管理の限界

従来のアプローチは「脆弱性スキャン → CVSS スコアで優先順位付け → パッチ適用」というものでした。しかし現代の IT 環境では以下の課題があります。

### 脆弱性の数が多すぎる

スキャンを実行すると数千〜数万の脆弱性が検出され、アラート疲れ（Alert Fatigue）が発生します。

### CVSS だけでは優先順位が決められない

CVSS が示すのは技術的な深刻度であり、「その脆弱性が自社環境で実際に攻撃されるか」というビジネスリスクとは必ずしも一致しません。

- 外部公開されていないサーバの脆弱性（CVSS 9.8）→ 実は「低」リスク
- 外部公開 + Exploit 公開済み（CVSS 7.5）→ 「極めて高い」リスク

### IT 環境が複雑になりすぎた

クラウド、Kubernetes、SaaS、IAM、エンドポイント、IoT/OT と攻撃対象領域（Attack Surface）が拡大し、脆弱性管理ツール単体では全体像が見えなくなっています。

## Exposure（エクスポージャー）という考え方

Exposure とは単なる脆弱性の存在ではなく、「**実際に攻撃される可能性**」を意味します。

```
Exposure = Vulnerability（脆弱性）
         + Asset Importance（資産の重要度）
         + Exploitability（攻撃可能性）
         + Threat Intelligence（脅威情報）
         + Attack Path（攻撃経路）
```

問いの本質が変わります。

- 旧：「この脆弱性の CVSS スコアはいくつか？」
- 新：「この脆弱性は**本当に攻撃されるのか？**」

## Exposure Management の 3 ステップ

Exposure Management は、組織の攻撃対象領域全体のリスクを統合的に評価・管理するアプローチです。

### Step 1：資産の可視化

「何を守るべきか」の把握が出発点です。対象はクラウド（AWS EC2, Azure VM, GCP Compute）、コンテナ（Kubernetes Pod, Docker Image）、SaaS（Salesforce, Slack, Microsoft 365）、ID/アクセス権限（IAM ロール, サービスアカウント）、エンドポイント、IoT/OT と多岐にわたります。

### Step 2：リスク情報の統合

異なるソースからのリスク情報を一元化します。

- **脆弱性**（CVE）
- **設定ミス**（Misconfiguration）
- **ID リスク**（過剰な権限、未使用アカウント）
- **攻撃面**（外部公開資産、シャドー IT）

### Step 3：リスクの優先順位付け

Exploit コードの存在、インターネット公開有無、資産のビジネス重要度、攻撃経路の有無、脅威インテリジェンスを考慮し、**数万件の脆弱性から「今すぐ対処すべき数十件」を見極めます**。

## Exposure Assessment Platform（EAP）

ガートナーは 2024 年に、従来の Vulnerability Assessment（VA）と Vulnerability Prioritization Technology（VPT）を統合し、**Exposure Assessment Platform（EAP）** という新しい市場カテゴリを定義しました。2025 年には EAP の Magic Quadrant も発表されています。

EAP は以下の機能を統合的に提供します。

| 機能 | 内容 |
|------|------|
| 攻撃対象領域の発見 | 資産発見・分類・管理 |
| リスク分析 | 優先順位付け |
| 修復管理 | ワークフロー・チケット連携 |

## なぜ今 Exposure Management なのか

攻撃者は CVSS スコアではなく、攻撃経路（Attack Path）を見ています。

```
外部公開サーバ（初期侵入）
  ↓ 既知の脆弱性を悪用（権限取得）
  ↓ 内部ネットワークへ横展開（Lateral Movement）
  ↓ 重要資産へ到達（データ窃取・ランサムウェア展開）
```

防御側も攻撃者と同じ目線でリスクを見ることで、限られたリソースを最も効果的に配分できます。

## Sysdig が実現する Exposure Management

クラウドネイティブ環境でこのアプローチを実践するプラットフォームの一つが **Sysdig** です。最大の特徴は **Runtime Insights（ランタイムインサイト）** です。

### Risk Spotlight（In Use）

従来のスキャンは「静的な情報」に基づいていますが、Sysdig はランタイムの実行情報を加えます。実行中のワークロードを観察し、どのパッケージが**実際にロードされているか**を把握します。

統計によると、コンテナイメージの 87% が高・クリティカルな脆弱性を含む一方、ランタイムでロードされているパッケージに紐づく脆弱性はわずか 15% です。つまり **85% の脆弱性は実行されていないコードに存在**しており、In Use フラグで大幅に絞り込めます。

### Sysdig Sage：AI によるリスク評価

**Sysdig Sage** は AI セキュリティアナリストで、重大度・In Use・公開状況・悪用可能性を総合評価し、98% 以上の低リスクノイズをフィルタリングします。ビジネスコンテキストを理解した修復手順を提案し、対応時間を大幅に短縮します。

## まとめ

| 従来のアプローチ | Exposure Management |
|-----------------|---------------------|
| CVE の数を数える | 実際に攻撃される可能性を評価する |
| CVSS スコアで優先順位付け | 攻撃経路・脅威情報を含めた総合判断 |
| 脆弱性管理ツール単体で運用 | 攻撃対象領域全体を統合管理 |

セキュリティの世界は「**脆弱性の数から、脆弱性のリスク優先度へ**」シフトしています。この流れを理解し、自社の戦略に取り入れることが今後ますます重要になります。

## 参考

- [脆弱性管理の次の時代 ── Exposure Management とは何か（Qiita）](https://qiita.com/keitah/items/8dbbbbdf530e2673ec1a)
- [Gartner Magic Quadrant for Exposure Assessment Platforms 2025](https://www.tenable.com/analyst-research/tenable-gartner-magic-quadrant-exposure-assessment-platforms)
- [Risk Spotlight (In Use) - Sysdig Docs](https://docs.sysdig.com/en/sysdig-secure/risk-spotlight/)
- [Sysdig Sage - AI Cloud Security Analyst](https://www.sysdig.com/generative-ai)
