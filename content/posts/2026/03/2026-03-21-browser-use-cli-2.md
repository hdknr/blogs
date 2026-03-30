---
title: "Browser Use CLI 2.0 — Playwrightを超える次世代ブラウザ自動化ツール"
date: 2026-03-21
lastmod: 2026-03-21
draft: false
description: "Browser Use CLI 2.0 は Playwright より2倍速く、コスト半減のブラウザ自動化ツール。CDP直接接続、既存Chromeセッションの再利用、AIエージェント連携に対応。セットアップ方法とPlaywrightとの使い分けを解説。"
source_url: "https://github.com/hdknr/blogs/issues/1#issuecomment-4102360362"
categories: ["ツール/開発環境"]
tags: ["browser-use", "ブラウザ自動化", "CDP", "AI", "playwright", "python"]
---

Browser Use CLI 2.0 がリリースされた。Playwright より速く、コストも半分。起動中の Chrome にそのまま接続できるこのツールは、AI エージェント時代のブラウザ自動化の本命になりそうだ。

## Browser Use とは

[Browser Use](https://github.com/browser-use/browser-use) は、AI エージェントのためのブラウザ自動化フレームワーク。GitHub スター数は 85,000 超で、Python ベースのオープンソースプロジェクトだ。

従来の Playwright がセレクタベースで要素を特定するのに対し、Browser Use はページ上のインタラクティブな要素をインデックスで管理する。セレクタのメンテナンスが不要で、AI エージェントとの相性が良い。

## CLI 2.0 の主な特徴

2026年3月22日にリリースされた CLI 2.0 では、以下の改善が入った。

### 処理速度 2 倍・コスト半減

バックグラウンドデーモンがブラウザをコマンド間で維持するため、コマンド実行あたりのレイテンシは約 50ms。毎回ブラウザを起動する Playwright と比べて圧倒的に速い。

### 起動中の Chrome に接続可能

3 つのブラウザモードをサポートする:

- **マネージド Chromium**: ヘッドレスで自動管理
- **リアル Chrome**: 既存のユーザープロファイル（Cookie、セッション）をそのまま利用
- **クラウドブラウザ**: Browser Use Cloud API 経由

リアル Chrome モードでは、ログイン済みのセッションをそのまま使える。API が提供されていないサービスでも、ブラウザを直接操作して自動化できる。

### AI コーディングツールとの統合

Claude Code、Cursor など主要な AI コーディングツールから直接利用できる。ターミナルからブラウザを操作するワークフローがシームレスになった。

## セットアップ

```bash
# インストール（pip install browser-use でも可）
uv pip install browser-use

# Chromium のインストール
browser-use install

# 環境チェック
browser-use doctor
```

## なぜ CDP 直叩きが効くのか

Browser Use の高速性の鍵は、Chrome DevTools Protocol（CDP）を直接利用している点にある。

Playwright は CDP の上にさらに抽象レイヤーを重ねており、クロスブラウザ対応やセレクタエンジンのオーバーヘッドがある。一方、Browser Use は Chrome/Chromium に特化して CDP を直接叩くことで、余分なレイヤーを省いている。

さらに、ボット検出を回避するための仕組みも組み込まれている。Cloudflare Turnstile や hCaptcha などの CAPTCHA に対応する独自モデルも開発されており、自動化ツールがブロックされがちなサイトでも動作しやすい。

## CLI の主要コマンド

```bash
# ページを開く
browser-use open "https://example.com"

# 要素をクリック
browser-use click <element-index>

# 要素を指定してテキスト入力
browser-use input <element-index> "テキスト"

# スクリーンショット取得
browser-use screenshot
```

コマンド間でブラウザが維持されるため、対話的にブラウザを操作できる。

## Playwright との使い分け

Playwright が不要になるわけではない。以下のように使い分けるのが現実的だ。

| 用途 | 推奨ツール |
|------|-----------|
| E2E テスト（CI/CD） | Playwright |
| クロスブラウザテスト | Playwright |
| AI エージェントの Web 操作 | Browser Use |
| API がないサービスの自動化 | Browser Use |
| ログイン済みセッションの再利用 | Browser Use |

## まとめ

LLM に「Playwright で十分か？」と聞けば、訓練データの時点での知識で答える。新しいツールの体感パフォーマンスは、自分で動かして確かめるのが一番速い。

Browser Use CLI 2.0 は、AI エージェントがブラウザを操作する場面で Playwright に代わる有力な選択肢だ。特に「既存の Chrome セッションを使いたい」「API がないサービスを自動化したい」といったユースケースでは、試す価値がある。
