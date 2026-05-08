---
title: "HubSpot CMS のキャッシュをバイパスする hsCacheBuster の使い方と注意点"
date: 2026-04-23
lastmod: 2026-04-23
draft: false
description: "HubSpot CMS のページ変更が反映されないときに使える ?hsCacheBuster クエリパラメータの使い方と、自分のリクエストだけ最新になる挙動の注意点、公開ユーザーへ反映するための再保存テクニックまでまとめた。"
source_url: "https://github.com/hdknr/blogs/issues/71#issuecomment-4300962242"
categories: ["Web開発"]
tags: ["hubspot-cms", "cache-busting", "marketing-hub", "cdn", "hsdebug"]
---

HubSpot CMS で「変更したのにページに反映されない」「自分の環境だけ古いまま見える」といった経験はないだろうか。HubSpot は CDN とサーバーサイドキャッシュが多層構造で動作しているため、保存直後にブラウザでアクセスしても古いキャッシュを掴んでしまうことがある。

そんなときに役立つのが、URL の末尾に付けるだけでキャッシュをバイパスできる `?hsCacheBuster` クエリパラメータだ。**ただし「キャッシュをクリアする」のではなく「自分のリクエストだけキャッシュを経由させない」挙動なので、その違いを押さえて使うのがポイントになる。**

## `?hsCacheBuster` の基本的な使い方

確認したいページの URL の末尾に `?hsCacheBuster` を付与してアクセスする。

```text
https://www.example.com/landing-page?hsCacheBuster
https://www.example.com/landing-page?hsCacheBuster=001
```

任意の値（数字や文字列）を渡すこともできる。値を変えながらアクセスすれば、確実に毎回キャッシュを通さずに最新コンテンツを取得できる。これは、同一 URL が CDN にキャッシュされる仕組みのため、値が変わると別 URL として扱われ、毎回オリジンから取得されるためだ。

```text
https://www.example.com/landing-page?hsCacheBuster=20260423-1
https://www.example.com/landing-page?hsCacheBuster=20260423-2
```

## 重要 — あくまで「自分の環境」のキャッシュバイパス

`?hsCacheBuster` で起きるのは **自分のリクエストに対してのみ、キャッシュを経由せず最新コンテンツが返る** という挙動である。

- ✅ 自分の画面では最新の HTML が確認できる
- ❌ 他のユーザー（クライアントや訪問者）にもすぐに反映されるわけではない
- ❌ HubSpot 側のキャッシュ自体が無効化されるわけでもない

つまり「変更が自分には見えるが、他の人にはまだ反映されていない」というケースは珍しくない。**「キャッシュを消す」ボタンではなく「キャッシュをバイパスして取得する」ボタン** と理解しておくのが正確だ。

## 公開ユーザーにも即時反映させたいとき

公開ユーザー全員にすぐ反映させたい場合は、ページエディター側で軽微な変更をかけて保存し直すのが手軽な方法だ。

- ヘッダー HTML や設定欄に半角スペースを 1 つ追加して保存
- そのまま再度保存（スペースを消す）

これで HubSpot 側がページを再生成し、CDN キャッシュも切り替わる。実コンテンツに変更を加えなくても、保存をトリガーすれば再ビルドが走るのがポイントである（2026 年 4 月時点での挙動）。

なお、HubSpot のキャッシュは通常のページなら **15 分程度で切り替わる** が、ブログ一覧ページなどでは数時間かかることもあるとされる（出典は後述の HubSpot Community 投稿）。急ぎの反映確認では、上記の「保存トリガー + `?hsCacheBuster` で確認」を組み合わせるのが現実的だ。

## 開発時に便利な使い方

### `hsDebug` と組み合わせる

HubSpot の CMS 開発では、`?hsDebug=true` を付けると開発者向けの詳細情報やテンプレートのデバッグ情報が表示できる。これと `hsCacheBuster` を組み合わせると、テンプレートの変更確認時に便利だ（利用にはポータルへのログインと CMS 開発権限が必要）。

```text
https://www.example.com/page?hsDebug=true&hsCacheBuster=1
```

### ブラウザ拡張で省力化

毎回 URL 末尾に手で入力するのが面倒な場合、サードパーティ製のブラウザ拡張機能を使うと、ボタン 1 つで現在のタブをキャッシュバイパスつきでリロードできる。Chrome / Firefox 双方に拡張機能が公開されている。

- Chrome: [HubSpot Cache Buster Shortcut](https://chromewebstore.google.com/detail/hubspot-cache-buster-shor/phfbkioeajpmehlcheipaoamacjodlcp)
- Firefox: [HubSpot Cache Buster](https://addons.mozilla.org/en-US/firefox/addon/hubspot-cache-buster/)

利用前に各拡張機能の権限要求（アクティブタブへのアクセス等）は確認しておくとよい。

## まとめ

| 目的 | 方法 |
|---|---|
| 自分だけ最新の HTML を見たい | URL 末尾に `?hsCacheBuster` を付ける |
| 公開ユーザー全員に反映させたい | ページエディターで保存をやり直す（スペース追加など） |
| キャッシュ自体を消したい | HubSpot 側で自動的にクリアされるのを待つ（通常 15 分前後） |

`?hsCacheBuster` は HubSpot CMS / Marketing Hub を扱う上で覚えておきたい基本テクニックの 1 つ。「変更したのに反映されない」と慌てる前に、まず URL に付けて確認するクセをつけておくと、トラブルシュートの初手として習慣化でき、調査工数を大きく削減できる。

## 参考

- [HubSpot Community: Website strange cache behaviour](https://community.hubspot.com/t5/CMS-Development/Website-strange-cache-behaviour/m-p/1042710)
- [Introducing hsCachebuster – A Simple Cache-Busting Extension for HubSpot Developers](https://www.seoanseo.ca/articles/hscachebuster)
- [HubSpot Cache Buster Shortcut（Chrome 拡張）](https://chromewebstore.google.com/detail/hubspot-cache-buster-shor/phfbkioeajpmehlcheipaoamacjodlcp)
- [HubSpot Cache Buster（Firefox 拡張）](https://addons.mozilla.org/en-US/firefox/addon/hubspot-cache-buster/)
