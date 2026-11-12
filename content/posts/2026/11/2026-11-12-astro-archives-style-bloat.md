---
title: "Astro のアーカイブページが遅い原因は View Transition の <style> が 1,121 個だった"
date: 2026-11-12
lastmod: 2026-11-12
slug: "astro-archives-style-bloat"
draft: false
description: "Astro + AstroPaper のアーカイブページが遅い原因は、記事ごとに生成される View Transition 用の style タグ 1,121 個でした。curl と puppeteer で切り分け、専用の 1 行表示に変えて DOMContentLoaded を 846 ms から 87 ms に短縮した手順を紹介します。"
categories: ["Web開発"]
tags: ["Astro", "AstroPaper", "View Transitions", "パフォーマンス", "フロントエンド"]
---

このブログは Astro + AstroPaper で作り、GitHub Pages でホスティングしています。その [アーカイブページ](/blogs/archives/) を開くと、表示されるまで一瞬もたつくことに気づきました。原因を調べてみると、ネットワークではなく、**記事 1 件ごとに埋め込まれた View Transition 用の `<style>` タグ**でした。全記事を 1 ページに並べるアーカイブでは、それが 1,121 個に膨らんでいました。

この記事では、原因の切り分け方と直し方、直した後の計測結果を紹介します。修正のあと、DOMContentLoaded は 846 ms から 87 ms に、スタイル再計算は 655 ms から 14 ms になりました。

## まずネットワークを疑う

最初に `curl` で、サイズとサーバーの応答時間を測りました。

```bash
curl -s -o /dev/null -w "size=%{size_download} ttfb=%{time_starttransfer} total=%{time_total}\n" \
  https://hdknr.github.io/blogs/archives/
# size=4102599 ttfb=0.315071 total=0.517766

curl -s --compressed -o /dev/null \
  -w "transfer=%{size_download}\n" https://hdknr.github.io/blogs/archives/
# transfer=246604

# 中身を調べるために HTML を保存しておく
curl -s -o archives.html https://hdknr.github.io/blogs/archives/
```

HTML は展開後で **4.1 MB** もありました。ただ、gzip で圧縮すると転送量は 247 KB で、TTFB も 0.3 秒です。ダウンロードにはほとんど時間がかかっていません。遅いのはダウンロードの後、つまり**ブラウザが HTML を解析し、スタイルを計算する部分**だと見当がつきます。

## HTML の中身を数える

では 4.1 MB の中身は何なのか。保存した HTML を Python で集計しました。

```python
import re
h = open("archives.html", encoding="utf-8").read()
print("li", h.count("<li"))
print("style", h.count("<style"),
      sum(len(m) for m in re.findall(r"<style.*?</style>", h, re.S)))
print("svg", h.count("<svg"),
      sum(len(m) for m in re.findall(r"<svg.*?</svg>", h, re.S)))
```

| 項目 | 個数 | サイズ |
|---|---|---|
| `<li>`（ナビゲーションを含む） | 1,137 | — |
| `<style>` タグ | **1,121** | **2.87 MB**（全体の約 70%） |
| インライン `<svg>` | 1,127 | 490 KB |
| `<p>`（大半が記事の説明文） | 未集計 | 420 KB |

並んでいる記事は 1,119 件です。一番大きいのは `<style>` で、記事の数とほぼ同じ 1,121 個ありました。中身を見ると、次のような View Transition のルールが記事ごとに 1 つずつ入っています。

```html
<style>[data-astro-transition-scope="astro-jyu37kgb-1"] { view-transition-name: p-2026-11-2026-11-11-contract-formal-verification; }@layer astro { ::view-transition-old(p-2026-11-2026-11-11-contract-formal-verification) {
	animation-duration: 180ms;
	animation-timing-function: cubic-bezier(0.76, 0, 0.24, 1);
	...
```

## 原因：Card の `transition:name`

アーカイブページ（`src/pages/archives/index.astro`）は、トップページと同じ `Card` コンポーネントで記事を 1 件ずつ描画していました。その `Card` の見出しには、`transition:name` が付いています（抜粋）。

```astro
<li class="my-6">
  <a href={getPostUrl({ data }, Astro.currentLocale)} class="...">
    <Heading transition:name={toTransitionName(id)}>
      {title}
    </Heading>
  </a>
  <Datetime {...props} />
  <p>{description}</p>
</li>
```

`transition:name` は、一覧ページの見出しと記事ページのタイトルを、ページ遷移のアニメーションでつなぐための指定です。`::view-transition-old()` / `::view-transition-new()` は、遷移アニメーションの旧画面と新画面を指す擬似要素です。Astro は、`transition:name` が付いた要素ごとに、これらのルールを持つ `<style>` を生成します。1 つあたり約 2.5 KB です。

トップページのように 10 件ずつページを分けている一覧なら、`<style>` は 10 個ほどで済み、気になりません。ところがアーカイブは全記事を 1 ページに並べるので、記事数がそのまま `<style>` の数になります。このブログでは 1,100 件を超えていました。さらに、`Card` の中の `Datetime` が出すカレンダーアイコンの SVG（計 490 KB）と説明文（計 420 KB）も、記事数に比例して増えていました。

## 直し方：アーカイブ専用の軽い 1 行表示にする

対策として、次の 3 つを考えました。

1. アーカイブの `Card` から `transition:name` を外す
2. アーカイブを「日付＋タイトル」だけの軽い一覧にする（説明文と SVG をなくす）
3. 年ごとにページを分ける（`/archives/2026/` など）

このうち 1 と 2 は、アーカイブで `Card` を使わずに専用の 1 行表示を書けば、まとめて片付きます。`Card` を使わなければ `transition:name` も付かないからです。

3 は見送りました。1 と 2 だけで、HTML は約 0.4 MB まで減る見込みでした。また、アーカイブの一番の価値は、全記事を 1 ページで見渡せることと、ブラウザのページ内検索（Ctrl+F）で探せることです。分割すると URL もページ送りも増えます。

書き換えた後のコードは次のとおりです（抜粋）。`<ul>` は年・月ごとのループの内側にあり、年・月でまとめる処理と件数の表示は元のままにしています。

```astro
---
import { getPostUrl } from "@/utils/getPostPaths";
// ...
const dayFormatter = new Intl.DateTimeFormat(locale, {
  day: "numeric",
  timeZone: config.site.timezone,
});
---

<ul class="mb-4 sm:my-6">
  {monthGroup
    .sort((a, b) => new Date(b.data.date).getTime() - new Date(a.data.date).getTime())
    .map(post => (
      <li class="flex gap-x-3 py-1">
        <time
          class="text-muted-foreground w-10 shrink-0 text-sm leading-7 tabular-nums"
          datetime={new Date(post.data.date).toISOString()}
        >
          {dayFormatter.format(new Date(post.data.date))}
        </time>
        <a href={getPostUrl(post, locale)} class="text-accent decoration-dashed underline-offset-4 hover:underline">
          {post.data.title}
        </a>
      </li>
    ))}
</ul>
```

`Card` 自体は変えていないので、トップページやタグ別のページでは、これまでどおり View Transition のアニメーションが使えます。

修正の前後で、ページから張られている記事リンクの集合を比べました。どちらも 1,119 件で、完全に一致しています。

## 修正後の計測

### HTML のサイズ

| | 変更前 | 変更後 |
|---|---|---|
| HTML サイズ | 4.1 MB | **469 KB**（-89%） |
| 転送サイズ（gzip） | 247 KB | **84 KB** |
| `<style>` | 1,121 個 | 1 個 |
| `<svg>` | 1,127 個 | 8 個 |

### ブラウザでの描画時間

遅さの原因はブラウザ側の処理だったので、ヘッドレス Chrome でも測りました。puppeteer-core で、修正前と修正後に保存した HTML をそれぞれ 5 回開き、中央値を取っています。指標は Navigation Timing の `domContentLoadedEventEnd` と、`page.metrics()` が返す `RecalcStyleDuration`・`LayoutDuration`・`Nodes` です。

計測部分の抜粋は次のとおりです。

```js
const page = await browser.newPage();
await page.setViewport({ width: 1280, height: 800 });
await page.goto(url, { waitUntil: "load" });
const dcl = await page.evaluate(
  () => performance.getEntriesByType("navigation")[0].domContentLoadedEventEnd
);
const m = await page.metrics();
// m.RecalcStyleDuration と m.LayoutDuration は秒単位
console.log(dcl, m.RecalcStyleDuration * 1000, m.LayoutDuration * 1000, m.Nodes);
```

| | 変更前 | 変更後 |
|---|---|---|
| DOMContentLoaded | 846 ms | **87 ms** |
| スタイル再計算 | 655 ms | **14 ms** |
| レイアウト | 67 ms | 84 ms |
| DOM ノード数 | 16,967 | 6,225 |

一番効いたのはスタイル再計算で、655 ms から 14 ms に減りました。1,100 個の `<style>` が重さの主因だったという見立てと合っています。レイアウトは少し増えましたが、全体から見れば誤差の範囲です。

数字はどれも Mac 上のヘッドレス Chrome で測った値です。スマートフォンでは絶対値が何倍かになりますが、変更前後の比はほぼ変わらないはずです。

## ほかのページは大丈夫か

同じ方法で、本番の一覧ページと記事ページも測りました。こちらは保存した HTML ではなく本番の URL を直接開いて測ったので、ネットワークの時間も少し含まれています。そのため、修正後のアーカイブの値は上の表と少し違います。

| ページ | `<style>` | 一覧の件数 | DOMContentLoaded | スタイル再計算 |
|---|---|---|---|---|
| トップ `/` | 12 | 10 | 45 ms | 4 ms |
| `/posts/` | 12 | 10 | 45 ms | 4 ms |
| `/tags/`（タグ一覧） | 2 | 1,403 | 63 ms | 18 ms |
| `/tags/claude-code/` | 7 | 10 | 44 ms | 3 ms |
| `/categories/ai/llm/` | 12 | 10 | 42 ms | 4 ms |
| 記事ページ（例） | 7 | — | 48 ms | 5 ms |
| `/archives/`（修正後） | 1 | 1,119 | 84 ms | 14 ms |

`Card` を使う一覧はどれも 10 件ずつに分かれているので、`<style>` は多くても 12 個で、50 ms 以内に表示されています。タグ一覧はタグが 1,403 個あって DOM は大きめですが、1 件が軽いリンクなので 63 ms で済んでいます。

## まとめ

- **転送が軽くても、表示が速いとは限りません。** 今回は gzip 転送が 247 KB でも、展開後の 4.1 MB の HTML をブラウザが処理するのに時間がかかっていました。`curl` で転送サイズと展開後のサイズを両方測ると、ネットワークの問題かブラウザの問題かを切り分けられます。
- **`transition:name` は、付けた要素の数だけ `<style>` を増やします。** 件数を区切った一覧では問題になりませんが、全件を並べるページに同じコンポーネントを使い回すと、件数に比例して重くなります。
- **全件を並べるページには、専用の軽い表示を用意します。** 部品を共有するより、見せる情報を絞ったほうが効果的でした。

同じように AstroPaper ベースでブログを運営していて、記事が数百件を超えたら、アーカイブページの `<style>` の数を一度数えてみてください。

```bash
curl -s https://<your-site>/archives/ | grep -o '<style' | wc -l
```
