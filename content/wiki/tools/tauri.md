---
title: "Tauri"
description: "OS 標準の WebView で画面を描き、バックエンドを Rust で書くデスクトップアプリフレームワーク。Chromium を同梱する Electron より配布サイズとメモリを大きく抑えられる"
date: 2026-11-15
lastmod: 2026-11-15
aliases: ["tauri", "Tauri v2", "Tauri 2"]
related_posts:
  - "/posts/2026/11/gpui-vs-tauri/"
tags: ["tauri", "rust", "デスクトップアプリ"]
---

## 概要

Tauri は、フロントエンドを HTML・CSS・JavaScript（React、Vue など）、バックエンドを Rust で書くデスクトップアプリフレームワーク。画面の描画は各 OS に最初から入っているブラウザエンジン（WebView）に任せるので、Chromium を丸ごと同梱する Electron と比べて配布サイズとメモリ消費を大きく抑えられる。

## 詳細

### 仕組み

- **ハイブリッド構造**: 見た目とレイアウトは WebView が担当し、ファイル操作や重い処理だけを IPC 経由で Rust 側に任せる
- **OS ごとの WebView**: Windows は WebView2（Chromium ベース）、macOS は WKWebView（WebKit ベース）、Linux は WebKitGTK
- **配布サイズ**: ブラウザエンジンを同梱しないため、最小構成なら 1MB 未満にもなる

### Rust コマンドの呼び出し（v2）

Rust 側で `#[tauri::command]` を付けた関数を定義し、`generate_handler!` で登録する。フロントエンドからは `@tauri-apps/api/core` の `invoke` で呼ぶ。引数と戻り値はシリアライズされて JavaScript と Rust の境界を越える。

```rust
#[tauri::command]
fn greet(name: &str) -> String {
    format!("Hello, {}!", name)
}

pub fn run() {
    tauri::Builder::default()
        .invoke_handler(tauri::generate_handler![greet])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
```

```typescript
import { invoke } from "@tauri-apps/api/core";
const message = await invoke<string>("greet", { name: "World" });
```

### 向いているケースと限界

向いているのは、Web フロントエンドの資産やチームのスキルを流用したいアプリ、フォームや一覧が中心の業務ツール・社内ツール、配布サイズを小さくしたいアプリ。

限界は描画を Web の仕組み（DOM）に頼る点にある。

- 何千もの要素が同時に更新されるような画面では、DOM の描画負荷と JS⇔Rust 間のシリアライズが遅延の原因になる
- OS によって WebView のエンジンが違うため、CSS の挙動などの差異を吸収するコストがかかる

こうした要件が厳しいアプリでは、GPU で直接描画する [GPUI](/blogs/wiki/tools/gpui/) が候補になる。2026 年 11 月に Discord が新デスクトップクライアントで Tauri ではなく GPUI を選んだと報じられたのは、この対比の実例。

## 関連ページ

- [GPUI](/blogs/wiki/tools/gpui/) — Rust 製だが WebView を使わず GPU で直接描画する UI フレームワーク
- [Capacitor](/blogs/wiki/tools/capacitor/) — モバイル版の WebView 方式。Web 資産を流用する発想が同じ

## ソース記事

- [GPUI と Tauri の違い：Rust 製デスクトップアプリの描画アーキテクチャを比較](/blogs/posts/2026/11/gpui-vs-tauri/) — 2026-11-15
