---
title: "Astro"
description: "コンテンツ中心のサイト向け静的サイトジェネレーター。このブログは Astro + AstroPaper で構築している。View Transitions の transition:name が全件一覧ページで 1,121 個の style を生んだ事例と、切り分け・計測の手順"
date: 2026-11-15
lastmod: 2026-11-15
aliases: ["Astro", "AstroPaper", "View Transitions", "transition:name"]
related_posts:
  - "/posts/2026/11/astro-archives-style-bloat/"
tags: ["Astro", "AstroPaper", "View Transitions", "パフォーマンス", "フロントエンド"]
---

## 概要

Astro はコンテンツ中心のサイト向けの静的サイトジェネレーター。このブログは Astro と、その上のブログテーマ **AstroPaper** で構築し、GitHub Pages でホスティングしている（Hugo + PaperMod から移行）。Astro の View Transitions は、一覧の見出しと記事ページのタイトルをページ遷移アニメーションでつなげられるが、`transition:name` を付けた要素ごとに `<style>` が生成される点に注意が要る。

## 詳細

### transition:name は要素の数だけ style を増やす

`transition:name` を付けると、Astro は要素ごとに `view-transition-name` と `::view-transition-old()` / `::view-transition-new()` のルールを持つ `<style>` を生成する（1 つ約 2.5 KB）。10 件ずつページ分割した一覧なら 10 個ほどで問題にならないが、全記事を 1 ページに並べるアーカイブで同じ `Card` コンポーネントを使い回すと、記事数がそのまま `<style>` の数になる。

このブログでは 1,119 件の記事に対し `<style>` が 1,121 個（2.87 MB、HTML の約 70%）、`Datetime` のカレンダー SVG が 1,127 個（490 KB）あり、HTML は展開後 4.1 MB になっていた。

### 切り分けの手順

1. **ネットワークを測る**：`curl -w "size=%{size_download} ttfb=%{time_starttransfer}"` で展開後サイズと TTFB、`--compressed` で転送量を見る。gzip で 247 KB・TTFB 0.3 秒なら遅いのはダウンロード後（ブラウザの解析とスタイル計算）
2. **HTML の中身を数える**：保存した HTML で `<style>` `<svg>` `<li>` の個数とサイズを集計する
3. **ブラウザで測る**：puppeteer-core で同じ HTML を複数回開き中央値を取る。指標は Navigation Timing の `domContentLoadedEventEnd` と、`page.metrics()` の `RecalcStyleDuration`・`LayoutDuration`・`Nodes`

手早く確かめるなら `curl -s https://<site>/archives/ | grep -o '<style' | wc -l`。

### 直し方と効果

アーカイブだけ `Card` を使わず、「日付＋タイトル」の専用 1 行表示に書き換えた。`Card` を使わなければ `transition:name` も付かないので、style と SVG と説明文が同時に消える。`Card` 自体は変えていないので、トップやタグ別ページの View Transition はそのまま。年ごとのページ分割は、全記事を 1 ページで見渡せる・Ctrl+F で探せるというアーカイブの価値を損なうので見送った。

| | 変更前 | 変更後 |
| --- | --- | --- |
| HTML サイズ | 4.1 MB | 469 KB |
| `<style>` | 1,121 個 | 1 個 |
| DOMContentLoaded | 846 ms | 87 ms |
| スタイル再計算 | 655 ms | 14 ms |

修正前後でページ内の記事リンク集合（1,119 件）が一致することも確かめている。

### 教訓

- 転送が軽くても表示が速いとは限らない。転送サイズと展開後サイズを両方測ると、ネットワークとブラウザのどちらの問題かを切り分けられる
- 全件を並べるページには、部品を共有するより見せる情報を絞った専用表示を用意する

### このブログでの構成メモ

- `content/` と `static/` はリポジトリ直下に置き、Astro 側から読む（`publicDir: "../static"`）
- Markdown の画像は rehype プラグインで WebP の `<picture>` に変換する
- 検索は Pagefind で、記事と Wiki だけを索引する

## 関連ページ

- [Modern Web Guidance](/blogs/wiki/concepts/modern-web-guidance/) — AI に書かせるフロントエンドを最新の Web 標準に寄せる
- [Claude Code](/blogs/wiki/tools/claude-code/) — ブログ運用の自動化に使うエージェント

## ソース記事

- [Astro のアーカイブページが遅い原因は View Transition の `<style>` が 1,121 個だった](/blogs/posts/2026/11/astro-archives-style-bloat/) — 2026-11-12
