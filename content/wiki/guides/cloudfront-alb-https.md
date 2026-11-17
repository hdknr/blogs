---
title: "CloudFront → ALB → Django の HTTPS 判定"
description: "ALB が X-Forwarded-Proto を上書きする問題の解決ガイド"
date: 2026-04-06
lastmod: 2026-11-17
related_posts:
  - "/posts/2026/02/5d604ad7617c043a1bb80b6a43ffbb48/"
tags: ["aws", "CloudFront", "ALB", "django", "HTTPS"]
---

## 概要

CloudFront + ALB + Django 構成では ALB が X-Forwarded-Proto を上書きするため、Django に HTTP 判定されて API レスポンス URL が http:// になる問題。CloudFront の custom_header（X-Forwarded-Ssl）は ALB に干渉されない。Django の SECURE_PROXY_SSL_HEADER をカスタムヘッダー参照に変更。

