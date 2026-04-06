---
title: "メール認証（SPF/DKIM/DMARC）"
description: "なりすまし防止のためのメール認証技術3層：送信元IP検証・電子署名・ポリシー決定"
date: 2026-04-06
lastmod: 2026-04-06
aliases: ["SPF", "DKIM", "DMARC", "メール認証"]
related_posts:
  - "/posts/2026/03/email-authentication-spf-dmarc-survey/"
tags: ["メール認証", "SPF", "DKIM", "DMARC", "セキュリティ"]
---

## 概要

- **SPF**: 送信元 IP アドレス検証
- **DKIM**: 電子署名で改ざん検知
- **DMARC**: 両者の結果に基づきポリシー実行（none/quarantine/reject）

## 日本の現状

上場企業 3,745 社調査で DMARC 未設定 34.5%、p=none（監視のみ）52.0%。実効的な reject+quarantine はわずか 13.4%。18か国中最下位。

## ソース記事

- [メール認証 SPF/DMARC 調査](/blogs/posts/2026/03/email-authentication-spf-dmarc-survey/) — 2026-03
