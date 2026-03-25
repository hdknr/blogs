---
title: "Figma プラグイン Image Translator：画像からテキストを抽出して多言語翻訳"
date: 2026-03-11
lastmod: 2026-03-11
draft: false
source_url: "https://github.com/hdknr/blogs/issues/1#issuecomment-4041960375"
categories: ["ツール/開発環境"]
tags: ["figma"]
---

海外サービスの UI を調査するとき、スクリーンショット内のテキストを手作業で翻訳するのは地味に手間がかかる。TSUMIKI INC. の鈴木慎吾氏（[@shingo2000](https://x.com/shingo2000)）が公開した Figma プラグイン **Image Translator** は、この作業を自動化してくれる。

## Image Translator とは

[Image Translator](https://www.figma.com/community/plugin/1539071623933265305/image-translator) は、Figma 上で選択した画像からテキストを自動抽出（OCR）し、指定した言語に翻訳する Figma プラグインだ。

主な特徴：

- **画像からのテキスト自動抽出** — スクリーンショットや UI キャプチャからテキストを認識
- **多言語翻訳** — 英語、日本語、中国語、スペイン語、韓国語、ポルトガル語などに対応
- **2つの表示モード** — Figma のアノテーション機能で表示するモードと、テキストレイヤーとして配置するモードを選択可能

## 使い方

1. Figma で翻訳したい画像を選択する
2. プラグインメニューから Image Translator を起動する
3. 翻訳先の言語を選択する
4. 抽出・翻訳されたテキストがアノテーションまたはテキストレイヤーとして表示される

## 活用シーン

### 海外サービスのデザイン調査

競合分析や UI リサーチで海外アプリのスクリーンショットを収集した際、画面内のテキストを素早く日本語で確認できる。翻訳結果がアノテーションとして画像に紐づくため、チームメンバーとの共有にも便利だ。

### 多言語対応の確認

自社サービスの多言語版スクリーンショットを取り込み、各言語のテキストが正しく表示されているか確認する用途にも使える。

## まとめ

Image Translator は、デザイン調査における画像内テキストの翻訳という地味だが頻出する作業を自動化してくれるプラグインだ。海外サービスの UI を日常的に調査しているデザイナーにとって、ワークフローの効率化に役立つだろう。

- **Figma Community**: [Image Translator](https://www.figma.com/community/plugin/1539071623933265305/image-translator)
- **作者**: [鈴木慎吾 / TSUMIKI INC.](https://x.com/shingo2000)
