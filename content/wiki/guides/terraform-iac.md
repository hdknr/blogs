---
title: "Terraform IaC ベストプラクティス"
description: "大規模 Terraform プロジェクトの設計・運用：モジュール化・ファイル分割・state 管理"
date: 2026-04-06
lastmod: 2026-04-06
related_posts:
  - "/posts/2021/06/terraform/"
tags: ["Terraform", "IaC", "DevOps", "AWS"]
---

## 概要

main.tf（リソース）/ variables.tf（入力）/ outputs.tf（出力）に分割。大規模化時は modules/ 配下でコンポーネント化。環境ごと（prod/stage）で terraform.tfvars を分離。state lock でマルチユーザーの同時実行防止。

## ソース記事

- [Terraform](/blogs/posts/2021/06/terraform/) — 2021-06
