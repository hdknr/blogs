---
title: "OpenWiki / Code Wiki"
description: "リポジトリから常設 Wiki 層を生成するツール群。LLM Wiki パターンの実装にあたる"
date: 2026-08-23
lastmod: 2026-08-23
aliases: ["Code Wiki", "DeepWiki", "コードWiki"]
related_posts:
  - "/posts/2026/08/openwiki-github-actions-ci/"
  - "/posts/2026/08/google-code-wiki-llm-wiki-pattern/"
tags: ["OpenWiki", "LangChain", "Code Wiki", "GitHub Actions", "ドキュメント自動生成"]
---

## 概要

リポジトリのコードから Wiki を生成し、チャットがコードではなく **生成済み Wiki を読む** 構造を作るツール群。[LLM Wiki パターン](/blogs/wiki/concepts/llm-wiki-pattern/) の実装にあたる。「毎回読み直す」RAG 的なアプローチをやめ、常設の Wiki 層を置くのが共通の設計思想。

## 主要な実装

| ツール | 提供元 | 特徴 |
|---|---|---|
| **Code Wiki** | Google（2025年11月公開） | チャットが生成済み Wiki を読む構造。**プライベートリポジトリ非対応** |
| **OpenWiki** | LangChain | CLI にエージェント本体が同梱。CI で回す運用モデル |
| **DeepWiki** | — | 同種の先行実装 |

## OpenWiki を GitHub Actions で回す

エージェント本体は CLI に同梱されているため、**自分で用意するのは推論プロバイダと認証情報だけ**。

### 設定の3層

設定は 3 層に分かれており、どこに何を置くかを決めるのが構成作業の中心になる。

### OIDC キーレス認証

長期の API キーをリポジトリシークレットに置かず、OIDC でキーレス化できる。

### `fetch-depth: 0` の落とし穴

`actions/checkout` の既定は浅いクローンで、履歴が必要な解析が動かない。`fetch-depth: 0` の指定が要る。

## mkdocs との運用モデルの違い

Code Wiki が「チャットの読み先」として Wiki を持つのに対し、OpenWiki は **mkdocs のように CI で定期生成する** モデル。前者はサービス、後者はパイプラインとして組む。

## 関連ページ

- [LLM Wiki パターン](/blogs/wiki/concepts/llm-wiki-pattern/) — 設計思想の元
- [GitHub Actions のセキュリティ](/blogs/wiki/guides/github-actions-security/) — OIDC 認証の背景
- [RAG](/blogs/wiki/concepts/rag/) — 対比される方式

## ソース記事

- [OpenWiki を GitHub Actions で定期実行する — 設定と API キーをどこに置くか](/blogs/posts/2026/08/openwiki-github-actions-ci/) — 2026-08-16
- [Google Code Wiki を設計として読む — 「毎回読み直す」をやめた常設 Wiki 層](/blogs/posts/2026/08/google-code-wiki-llm-wiki-pattern/) — 2026-08-16
