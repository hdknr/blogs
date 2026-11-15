---
title: "GPUI"
description: "Zed Industries が作った Rust 製の UI フレームワーク。HTML もブラウザエンジンも使わず、UI を Rust で定義して GPU で直接描画する。Zed エディタの土台で、2026 年 11 月には Discord の新デスクトップクライアントへの採用が報じられた"
date: 2026-11-15
lastmod: 2026-11-15
aliases: ["gpui", "Zed GPUI", "GPU 直接描画 UI"]
related_posts:
  - "/posts/2026/11/gpui-vs-tauri/"
tags: ["gpui", "rust", "zed", "デスクトップアプリ"]
---

## 概要

GPUI は、コードエディタ Zed の開発元 Zed Industries が作った Rust 製の UI フレームワーク。UI 部品をすべて Rust のコードで定義し、GPU を使って画面に直接描画する。ゲームエンジンや Flutter に近い独自描画型で、WebView を使う [Tauri](/blogs/wiki/tools/tauri/) とは描画の仕組みが根本的に異なる。

## 詳細

### 仕組み

- **言語**: UI 層もロジック層もすべて Rust。状態とビューが同じメモリ空間にあるので、言語間のシリアライズ（IPC）が発生しない
- **レイアウト**: Flexbox / Grid のレイアウトライブラリ Taffy をベースにしたレイアウトエンジンと、独自のテキスト描画エンジンを持つ
- **描画バックエンド**: macOS は Metal、Windows は Direct3D 11、Linux は wgpu（Vulkan / GLES）
- **書き方**: `Render` トレイトを実装し、`div()` から Tailwind CSS 風のメソッドチェーン（`.flex()`・`.bg()`・`.justify_center()`・`.child()` など）で要素ツリーを組み立てる

```rust
impl Render for HelloWorld {
    fn render(&mut self, _window: &mut Window, _cx: &mut Context<Self>) -> impl IntoElement {
        div()
            .flex()
            .bg(rgb(0x2e7d32))
            .size(px(500.0))
            .justify_center()
            .items_center()
            .child(format!("Hello, {}!", &self.text))
    }
}
```

### 強みと弱み

| 観点 | 内容 |
|---|---|
| 性能 | WebView を挟まないぶん、描画速度・メモリで有利になりやすい（Tauri と直接比べた公式ベンチマークはない） |
| 一貫性 | 独自描画なので OS 間で見た目がそろいやすい。フォントやウィンドウ装飾は OS 差が残る |
| 開発 | Web の資産は使えない。UI 部品も自前で作る部分が多く、学習コストが高い |

大量の要素を高いフレームレートで描き直し続けるアプリ（エディタ、チャットなど）に向く。フォームや一覧中心の一般的なアプリなら Tauri のほうが手早い。

### Discord の採用

2026 年 11 月、Discord の CTO が X で、デスクトップクライアントを Electron と React から Rust に作り直しており、UI フレームワークは Tauri ではなく GPUI だと明らかにした。初期の Windows 11 ビルドのメモリ使用量は約 290MB と報じられている。新クライアントは開発中で、リリース日は未定。

常駐しながらゲームのフレームレートを奪わないことが求められるアプリで、DOM と IPC のボトルネック、OS ごとの WebView の差異、ブラウザエンジンのメモリ負荷を避けられる点が、WebView 方式に対する利点として挙げられる。

## 関連ページ

- [Tauri](/blogs/wiki/tools/tauri/) — 同じく Rust でデスクトップアプリを作るが、描画は OS 標準の WebView に任せる
- [Capacitor](/blogs/wiki/tools/capacitor/) — モバイルで WebView 方式をとるランタイム。独自描画との対比が同じ構図

## ソース記事

- [GPUI と Tauri の違い：Rust 製デスクトップアプリの描画アーキテクチャを比較](/blogs/posts/2026/11/gpui-vs-tauri/) — 2026-11-15
