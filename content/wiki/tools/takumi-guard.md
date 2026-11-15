---
title: "Takumi Guard"
description: "GMO Flatt Security の Takumi byGMO の機能。パッケージレジストリと開発者の間に入るプロキシとして、悪性と判定したパッケージのダウンロードをブロックする。既知の脆弱性（CVE）の検出は別の仕組みで補う"
date: 2026-11-15
lastmod: 2026-11-15
aliases: ["Takumi byGMO", "GMO Flatt Security", "悪性パッケージのブロック"]
related_posts:
  - "/posts/2026/11/cc-sdd-coderabbit-takumi-guard-ai-dev-flow/"
tags: ["セキュリティ", "サプライチェーン攻撃", "npm", "AI駆動開発"]
---

## 概要

**Takumi Guard** は、GMO Flatt Security のセキュリティ AI エージェント「Takumi byGMO」に 2026 年 3 月に追加された、ソフトウェアサプライチェーン攻撃対策の機能である。**パッケージレジストリと開発者の間に入るプロキシ**として働き、ダウンロード時に悪性かどうかを検証して、悪性と判定したものをブロックする。

## 詳細

### 仕組み

npm ならレジストリの参照先を Takumi Guard に向けて使う。提供開始時は npm が対象で、npm に公開された全パッケージを検査して作った独自のブロックリストで判定すると説明されていた。現在の製品ページでは PyPI・RubyGems・Go・Packagist にも対象が広がっている。

### なぜインストール経路に関所を置くか

非エンジニアやエージェントに「このライブラリを入れて」と任せるようになると、何がインストールされるかを人間が逐一確かめるのは現実的でない。正規の名前に似せたタイポスクワッティングや、乗っ取られた正規パッケージを経由する攻撃には、**インストールの経路そのものに関所を置く**のが効く。利用者のいない自律ループ（エージェントが自分の判断で依存を足す場面）では特に、誰も見ないまま依存が増える穴になりやすい。

### 何を止めないか

紹介記事などでは「脆弱性のあるライブラリをブロック」と書かれることがあるが、GMO Flatt Security の説明では対象は**悪意あるパッケージ**である。既知の脆弱性（CVE）を持つバージョンの検出は、SBOM 管理や依存関係スキャン（Dependabot など）で別に補う前提で考える。

### 開発フローでの位置づけ

cc-sdd を軸にした AI 駆動開発フローの事例では、Takumi Guard とインフラのアクセス制御を「機械的に検出できる問題はツールで潰し、人間はリリース判断に集中する」原則の一部として置いている（[cc-sdd](/blogs/wiki/tools/cc-sdd/)）。

## 関連ページ

- [cc-sdd](/blogs/wiki/tools/cc-sdd/) — Takumi Guard を組み込んだ開発フローの事例
- [必須コードレビューの代替](/blogs/wiki/concepts/code-review-alternatives/) — 依存関係スキャンなど、レビューを機械に移す手段
- [要求仕様書作成ループ](/blogs/wiki/concepts/requirements-spec-loop/) — spec-loop / dev-loop に依存パッケージの関門がないという指摘
- [GitHub Actions スクリプトインジェクション対策](/blogs/wiki/guides/github-actions-security/) — CI 側のサプライチェーン対策

## ソース記事

- [非エンジニアの社長が出した巨大 PR をどう受け止めるか — cc-sdd・CodeRabbit・Takumi Guard で組む AI 駆動開発フロー](/blogs/posts/2026/11/cc-sdd-coderabbit-takumi-guard-ai-dev-flow/) — 2026-11-13
