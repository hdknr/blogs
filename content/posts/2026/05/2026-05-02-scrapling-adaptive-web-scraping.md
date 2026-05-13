---
title: "Scrapling — BeautifulSoup比784倍速い適応型Webスクレイピング・Cloudflare突破・MCP対応まとめ"
date: 2026-05-02
lastmod: 2026-05-02
draft: false
source_url: "https://github.com/hdknr/blogs/issues/1#issuecomment-4363538280"
categories: ["ツール/開発環境"]
tags: ["Python", "スクレイピング", "Cloudflare", "MCP", "Scrapy"]
---

Webスクレイピングの定番ライブラリといえば BeautifulSoup だが、それを最大784倍上回るパフォーマンスを持つ Python フレームワーク **Scrapling** が注目を集めている。GitHub スター数は約47,000（2026年5月時点）に達する。Cloudflare Turnstile 突破やサイト構造変化への自動適応など、現代のWebスクレイピング課題を一手に解決するのが特徴だ。

## Scrapling とは

[Scrapling](https://github.com/D4Vinci/Scrapling) は Karim Shoair（D4Vinci）が開発した適応型Webスクレイピングフレームワークだ。単発リクエストからフルスケールクローリングまでをカバーし、以下の3つを柱とする。

1. **Adaptive Scraping**: サイトのデザインが変わっても対象要素を自動的に再探索
2. **Anti-bot Bypass**: Cloudflare Turnstile 等のアンチボットを標準でバイパス
3. **Spider Framework**: Scrapy ライクな Spider API で並列クロールをスケールアウト

## パフォーマンスベンチマーク

5,000 個のネスト要素に対するテキスト抽出速度（100回平均）。出典: [公式 README ベンチマーク](https://github.com/D4Vinci/Scrapling#performance-benchmarks)：

| ライブラリ           | 処理時間（ms） | Scrapling比  |
|---------------------|:-------------:|:------------:|
| **Scrapling**       |     2.02      |     1.0x     |
| Parsel/Scrapy       |     2.04      |     1.01x    |
| Raw Lxml            |     2.54      |     1.26x    |
| PyQuery             |    24.17      |    ~12x      |
| Selectolax          |    82.63      |    ~41x      |
| MechanicalSoup      |   1549.71     |   ~767x      |
| BS4 with Lxml       |   1584.31     |   **~784x**  |
| BS4 with html5lib   |   3391.91     |   ~1679x     |

公式ドキュメントで強調されている「BeautifulSoup 比 784 倍」はこのベンチマークに基づいている。

## インストール

Python 3.10 以上が必要。

```bash
# パーサーのみ（軽量）
pip install scrapling

# フェッチャー付き（ブラウザ自動化含む）
pip install "scrapling[fetchers]"
scrapling install

# すべての機能
pip install "scrapling[all]"
scrapling install
```

Docker イメージも提供されている。

```bash
docker pull pyd4vinci/scrapling
```

## 主要機能と使い方

### 1. Fetcher — 高速ステルス HTTP リクエスト

```python
from scrapling.fetchers import Fetcher, FetcherSession

# ワンショットリクエスト
page = Fetcher.get('https://quotes.toscrape.com/')
quotes = page.css('.quote .text::text').getall()

# セッションを使い回す（Chrome の TLS フィンガープリントを偽装）
with FetcherSession(impersonate='chrome') as session:
    page = session.get('https://example.com/', stealthy_headers=True)
    data = page.css('.product').getall()
```

### 2. StealthyFetcher — Cloudflare 突破

```python
from scrapling.fetchers import StealthyFetcher, StealthySession

# Cloudflare Turnstile を自動突破してフェッチ
page = StealthyFetcher.fetch('https://nopecha.com/demo/cloudflare')

# セッションを維持しながら複数ページ取得
with StealthySession(headless=True, solve_cloudflare=True) as session:
    page = session.fetch('https://example.com/', google_search=False)
    data = page.css('#content a').getall()
```

### 3. DynamicFetcher — フルブラウザ自動化

```python
from scrapling.fetchers import DynamicFetcher

# Playwright の Chromium でフルレンダリング
page = DynamicFetcher.fetch('https://quotes.toscrape.com/')
data = page.xpath('//span[@class="text"]/text()').getall()
```

### 4. 適応型スクレイピング — サイト変更に自動追随

まず `auto_save=True` で対象要素の位置情報を保存しておき、次回以降は `adaptive=True` を渡すことでサイト構造が変わっても自動的に再探索させられる。

```python
from scrapling.fetchers import StealthyFetcher

StealthyFetcher.adaptive = True
p = StealthyFetcher.fetch('https://example.com', headless=True, network_idle=True)

# auto_save=True で要素位置を記憶（初回）
products = p.css('.product', auto_save=True)

# サイト構造が変わっても adaptive=True で自動再探索（2回目以降）
products = p.css('.product', adaptive=True)
```

### 5. Spider フレームワーク — フルスケールクローリング

```python
from scrapling.spiders import Spider, Response

class QuotesSpider(Spider):
    name = "quotes"
    start_urls = ["https://quotes.toscrape.com/"]
    concurrent_requests = 10

    async def parse(self, response: Response):
        for quote in response.css('.quote'):
            yield {
                "text": quote.css('.text::text').get(),
                "author": quote.css('.author::text').get(),
            }

        next_page = response.css('.next a')
        if next_page:
            yield response.follow(next_page[0].attrib['href'])

result = QuotesSpider().start()
print(f"Scraped {len(result.items)} quotes")
result.items.to_json("quotes.json")
```

クロールの中断・再開（Ctrl+C で graceful shutdown、同じ `crawldir` で再起動すれば再開）：

```python
QuotesSpider(crawldir="./crawl_data").start()
```

## CLI でコードなしにスクレイピング

```bash
# インタラクティブシェル
scrapling shell

# URL からコンテンツをファイルに抽出
scrapling extract get 'https://example.com' content.md
scrapling extract stealthy-fetch 'https://protected.example.com' output.html \
  --css-selector '#main' --solve-cloudflare
```

## MCP サーバーとして AI エージェントと連携

Scrapling は MCP（Model Context Protocol）サーバー機能を内蔵しており、Claude や Cursor などの AI エージェントからWebスクレイピングを呼び出せる。

```bash
pip install "scrapling[ai]"
```

HTML 全体を AI に渡すのではなく、Scrapling 側で必要部分だけ抽出してから AI に渡すため、トークン消費を大幅に削減できる点が特徴だ。

## 豊富なセレクタ API

BeautifulSoup ユーザーにも馴染みやすいマルチパラダイム対応：

```python
page = Fetcher.get('https://quotes.toscrape.com/')

# CSS セレクタ
quotes = page.css('.quote')

# XPath
quotes = page.xpath('//div[@class="quote"]')

# BeautifulSoup スタイル
quotes = page.find_all('div', class_='quote')

# テキスト検索
quotes = page.find_by_text('quote', tag='div')

# 類似要素を自動探索
similar = quotes[0].find_similar()
```

## まとめ

Scrapling は「Scrapy のスパイダーフレームワーク × BeautifulSoup の使いやすさ × ステルスブラウザ自動化」を1つのライブラリで提供する。特にアンチボット対策が強化されたサイトや、デザイン変更が頻繁なサイトのデータ収集に威力を発揮し、MCP サーバー機能により AI エージェントとの連携も容易だ。Webスクレイピングの現場で抱えがちな「サイトが更新されるたびにコードを直す」苦労から解放してくれる有力な選択肢だ。

> **注意**: 本ライブラリは教育・研究目的で提供されている。利用にあたってはデータスクレイピングに関する法規制と対象サイトの利用規約を遵守すること。
