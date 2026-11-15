---
title: "GPUI と Tauri の違い：Rust 製デスクトップアプリの描画アーキテクチャを比較"
date: 2026-11-15
lastmod: 2026-11-15
slug: "gpui-vs-tauri"
draft: false
source_url: "https://github.com/hdknr/blogs/issues/694#issuecomment-6888200119"
categories: ["プログラミング言語"]
tags: ["rust", "gpui", "tauri", "デスクトップアプリ", "zed"]
---

## はじめに

**GPUI** と **Tauri** は、どちらも「Rust で軽量・高速なデスクトップアプリを作る」ための選択肢として名前が挙がります。しかし、**画面を描画する仕組み（アーキテクチャ）は根本的に異なります**。

一言でいうと、次のような違いです。

- **Tauri**：Web 技術（ブラウザ）で画面を作るアプローチ
- **GPUI**：ゲームエンジンのように GPU を直接叩いて画面を描くアプローチ

先に結論を書くと、Web フロントエンドの資産を活かしたい一般的なアプリなら Tauri、大量の要素を高頻度で描き直し続けるアプリなら GPUI が候補になります。2026 年 11 月には、Discord がデスクトップクライアントを GPUI で作り直していると明らかにし、注目を集めました。

この記事では、両者のアーキテクチャの違い、性能と開発体験の比較、それぞれが向いているケースを整理します。本記事で登場する主な用語は次のとおりです。

| 名前 | 概要 |
| --- | --- |
| Tauri | OS 標準の WebView を使い、フロントエンドを Web 技術、バックエンドを Rust で書くデスクトップアプリフレームワーク |
| GPUI | コードエディタ Zed の開発元 Zed Industries が作った、GPU で UI を直接描画する Rust 製 UI フレームワーク |
| WebView | OS に組み込まれたブラウザエンジンを、アプリ内に埋め込んで使う部品 |
| IPC | プロセス間通信。Tauri ではフロントエンド（JavaScript）とバックエンド（Rust）の間のメッセージのやり取りを指す |
| シリアライズ | データを JSON などの受け渡し可能な形式に変換すること |
| Taffy | Rust 製の Flexbox / Grid レイアウトライブラリ |

## GPUI と Tauri のアーキテクチャの違い

両者の構成を図にすると次のようになります。

![Tauri は HTML・CSS・JavaScript のフロントエンドが OS 標準の WebView で描画され、Rust のバックエンドとは IPC で通信する。GPUI は Rust で書いた UI とロジックを、Taffy によるレイアウトを経て GPU API で直接描画することを示す比較図](/blogs/images/gpui-vs-tauri-architecture.png)

### Tauri：OS 標準の WebView（ブラウザ）を利用

Electron はアプリに Chromium を丸ごと同梱します。一方 Tauri は、**各 OS に最初から入っているブラウザエンジン（WebView）** を利用します。

- **構成**：フロントエンド（HTML / CSS / JavaScript・TypeScript）＋ バックエンド（Rust）
- **仕組み**：画面の見た目やレイアウトは WebView が担当し、ファイル操作や重い処理だけを IPC 経由で Rust 側に任せるハイブリッド構造

フロントエンドからは、Rust 側に定義して登録したコマンドを `invoke` で呼び出します（以下は抜粋です）。

```rust
// src-tauri/src/lib.rs
#[tauri::command]
fn greet(name: &str) -> String {
    format!("Hello, {}!", name)
}

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    tauri::Builder::default()
        .invoke_handler(tauri::generate_handler![greet])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
```

```typescript
// フロントエンド（TypeScript）
import { invoke } from "@tauri-apps/api/core";

const message = await invoke<string>("greet", { name: "World" });
```

引数と戻り値はシリアライズされて、JavaScript と Rust の境界を越えます。この「境界をまたぐコスト」が、後述の「DOM と IPC のボトルネック」の論点になります。

### GPUI：GPU による直接描画（純粋な Rust）

GPUI は HTML もブラウザエンジンも一切使いません。**すべての UI パーツを Rust のコードで定義します。そして GPU を使って画面に直接描画します。**

- **構成**：UI 層・ロジック層ともにすべて Rust
- **描画バックエンド**：macOS は Metal、Windows は Direct3D 11、Linux は wgpu（Vulkan / GLES）
- **レイアウト**：Taffy ベースのレイアウトエンジンと、独自のテキスト描画エンジン
- **設計思想**：ゲームエンジンや Flutter のような独自描画型の UI フレームワークに近く、高いフレームレートでの描画を目指している

UI は Rust の要素ツリーとして、Tailwind CSS に似たメソッドチェーンで組み立てます（以下はビュー部分の抜粋で、アプリの起動コードは省いています）。

```rust
use gpui::{div, prelude::*, px, rgb, Context, SharedString, Window};

struct HelloWorld {
    text: SharedString,
}

impl Render for HelloWorld {
    fn render(&mut self, _window: &mut Window, _cx: &mut Context<Self>) -> impl IntoElement {
        div()
            .flex()
            .bg(rgb(0x2e7d32))
            .size(px(500.0))
            .justify_center()
            .items_center()
            .text_xl()
            .text_color(rgb(0xffffff))
            .child(format!("Hello, {}!", &self.text))
    }
}
```

状態もビューも同じ Rust のメモリ空間にあるため、Tauri のような言語間のシリアライズは発生しません。

## Tauri と GPUI の比較表（性能・メモリ・配布サイズ・開発体験）

| 比較項目 | Tauri | GPUI |
| --- | --- | --- |
| **描画エンジン** | OS の WebView（WebView2 / WKWebView / WebKitGTK） | GPU 直接描画（Metal / Direct3D 11 / wgpu） |
| **UI を書く言語** | HTML / CSS / JavaScript（React、Vue など） | **Rust のみ** |
| **描画速度・応答性** | ブラウザ相当（複雑な DOM 操作で重くなることも） | WebView を挟まないぶん有利になりやすい |
| **メモリ消費量** | 少ない（Electron より大幅に省メモリ） | WebView のオーバーヘッドがないぶん、さらに抑えやすい |
| **配布ファイルサイズ** | **極めて小さい**（最小構成なら 1MB 未満も可能） | アプリ次第（公式の目安はない） |
| **OS 間の見た目の一貫性** | OS ごとの WebView の差異（CSS の挙動など）が出る | **一致しやすい**（独自描画のため。フォントやウィンドウ装飾は OS 差が残る） |
| **開発のしやすさ** | Web 開発の資産・ライブラリがそのまま使える | 学習コストが高い（UI 部品も自前で作る部分が多い） |

性能とメモリについては、両者を直接比べた公式ベンチマークはありません。上の表は、アーキテクチャから見た傾向として読んでください。

ざっくり言えば、**Tauri は「Web の資産を活かして軽く作る」**、**GPUI は「描画まで握って速さと一貫性を取る」** という棲み分けです。

## Tauri が向いているケース

- **Web フロントエンドの資産を流用したい**：React や Vue のコンポーネント、CSS フレームワーク、既存の Web アプリをほぼそのまま使えます。
- **一般的な業務ツールや社内ツール**：フォームや一覧が中心で、毎秒大量の要素を描き直す必要がないアプリです。
- **配布サイズを最小にしたい**：ブラウザエンジンを同梱しないため、インストーラーを非常に小さくできます。
- **チームが Web 技術に慣れている**：UI を Rust で書く必要がないので、学習コストを抑えられます。

## Discord はなぜ Tauri ではなく GPUI なのか

2026 年 11 月、Discord の共同創業者で CTO の Stanislav Vishnevskiy 氏は X で次のことを明らかにしました（[heise の報道](https://www.heise.de/en/news/Discord-is-rebuilding-in-Rust-leaving-React-and-Electron-behind-11516113.html)）。

- デスクトップクライアントを、Electron と React から Rust に作り直している
- UI フレームワークは Tauri ではなく GPUI である
- 初期の Windows 11 ビルドのメモリ使用量は約 290MB

新クライアントはまだ開発中で、リリース日は発表されていません。

Discord は、大量のメッセージ・画像・動画・音声通話の状態が常に更新され続けるアプリです。しかも、ゲームと並行して常駐します。以下は、このようなアプリで Tauri（WebView）に残る課題を、アーキテクチャの面から整理したものです（Discord 自身が挙げた理由ではなく、筆者の整理です）。

### 1. DOM と IPC のボトルネック

Tauri であっても、画面描画は Web の仕組み（DOM ツリー）に依存します。何千ものメッセージやリアクション、ボイスチャットのアニメーションが同時に動く場面を考えます。このとき WebView の描画負荷と、Rust と JavaScript の間のデータ受け渡し（シリアライズを伴う通信）が遅延の原因になります。

GPUI なら**状態から描画までが同じ Rust のメモリ空間で完結**するため、言語間通信のオーバーヘッドがありません。

### 2. OS ごとの WebView の挙動の違い

Tauri は OS によって動くブラウザエンジンが異なります。

- Windows：WebView2（Chromium ベース）
- macOS：WKWebView（WebKit ベース）
- Linux：WebKitGTK

大規模で複雑な UI を全 OS で同じ品質・挙動に保つには、この差異を吸収するコストが重くなります。GPUI は描画を自前でコントロールするため、OS 間で見た目と挙動をそろえやすくなります。

### 3. 省メモリ・低 CPU 負荷

WebView はブラウザエンジン一式をメモリに載せるため、アプリ自体が軽くても一定のメモリと CPU を使い続けます。

ゲーマーがバックグラウンドで常に起動し続けるチャットアプリにとって、**ゲームのフレームレート（FPS）を奪わないこと**は最優先事項です。ブラウザエンジンを丸ごと排除できる GPUI の方式は、この要件に合致します。

## まとめ

ひとことで言えば、Tauri は「Web の資産を活かして軽く作る」、GPUI は「描画まで握って速さと一貫性を取る」選択肢です。

- **Tauri** は OS 標準の WebView で画面を描き、Rust はバックエンドを担います。Web 開発の知識とライブラリをそのまま使え、配布サイズも小さくできます。
- **GPUI** は UI もロジックもすべて Rust で書き、GPU で直接描画します。WebView を挟まないぶん性能と OS 間の一貫性で有利ですが、学習コストと UI 部品を自作する手間がかかります。
- 一般的な業務ツールや、Web フロントエンドの資産を流用したいアプリなら Tauri が向いています。エディタ（Zed）やチャット（Discord）のように**大量の要素を高いフレームレートで更新し続けるアプリ**なら、GPUI が候補になります。
