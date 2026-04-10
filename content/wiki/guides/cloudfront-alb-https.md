---
title: "CloudFront → ALB → Django の HTTPS 判定"
description: "ALB が X-Forwarded-Proto を上書きする問題の解決ガイド"
date: 2026-04-06
lastmod: 2026-04-06
related_posts: []
tags: ["AWS", "CloudFront", "ALB", "Django", "HTTPS"]
---

## 概要

CloudFront + ALB + Django 構成では ALB が X-Forwarded-Proto を上書きするため、Django に HTTP 判定されて API レスポンス URL が http:// になる問題。CloudFront の custom_header（X-Forwarded-Ssl）は ALB に干渉されない。Django の SECURE_PROXY_SSL_HEADER をカスタムヘッダー参照に変更。

