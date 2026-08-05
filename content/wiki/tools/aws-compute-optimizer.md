---
title: "AWS Compute Optimizer"
description: "EC2・RDS・Lambda などの右サイジング推奨を無料で得られる AWS のサービス。メモリ推奨には CloudWatch Agent が必要という前提がある"
date: 2026-08-05
lastmod: 2026-08-05
aliases: ["Compute Optimizer", "右サイジング", "rightsizing", "アイドルリソース推奨", "拡張インフラメトリクス"]
related_posts:
  - "/posts/2026/07/aws-compute-optimizer/"
tags: ["aws", "compute-optimizer", "ec2", "CloudWatch", "コスト最適化"]
---

## 概要

AWS Compute Optimizer は、CloudWatch のメトリクスから機械学習で**リソースの右サイジング推奨**を生成するサービス。オプトインで有効化すると、EC2・RDS・Lambda・EBS・Auto Scaling グループなどについて「過剰／適正／不足」の Finding と、推奨インスタンスタイプを返す。基本機能は無料で使える。

## 使い始めるまで

オプトイン（有効化）が必要で、有効化してから推奨が出るまでには**メトリクスの蓄積期間**が要る。無料枠のルックバック期間は 32 日。リソースごとに「推奨を出すための最低稼働時間」の条件があるため、立ち上げ直後のリソースには推奨が付かない。

## Finding は3分類では足りない

Finding（Over-provisioned / Optimized / Under-provisioned）だけを見て判断すると精度が出ない。あわせて次を読む。

- **Finding reasons** — CPU・メモリ・ネットワークなど、どのスペックが問題なのかの内訳
- **Performance risk** — 推奨に従った場合の性能リスク（5段階）
- **Migration effort** と **Platform differences** — 適用にかかるコストの見積り。世代跨ぎの変更では ENA や NVMe まわりの差異が効く

## 最大の落とし穴：メモリは見えない

**CloudWatch はデフォルトで EC2 のメモリ使用率を収集しない。** そのため CloudWatch Agent を導入していないインスタンスでは、Compute Optimizer はメモリを考慮せずに推奨を出す。CPU だけを見て「過剰プロビジョニング」と判定されたインスタンスをそのまま縮小すると、メモリ不足で落ちる。

メモリ推奨を機能させるには CloudWatch Agent の導入が前提になる。これは有料の拡張インフラメトリクス（ルックバック期間を延長する機能）とは別の話である点に注意。

## アイドルリソース推奨

2026年6月に対象が12種類へ拡大した。判定基準はリソース種別ごとに異なり、ルックバック期間にも例外がある。推奨は「削除」だけではなく、停止やダウンサイズを含む。

## API から扱うときの注意

`boto3` で取得する場合、ページネーターと `maxResults` の扱いに癖がある。全件取れているつもりで先頭ページだけを見ている、という取りこぼしが起きやすい。

## 関連ページ

- [Grafana](/blogs/wiki/tools/grafana/) — メトリクスの可視化
- [Terraform で IaC](/blogs/wiki/guides/terraform-iac/) — 推奨を反映する側

## ソース記事

- [AWS Compute Optimizer の使い方 — EC2 の右サイジングを無料で始める手順と落とし穴](/blogs/posts/2026/07/aws-compute-optimizer/) — 2026-07-30
