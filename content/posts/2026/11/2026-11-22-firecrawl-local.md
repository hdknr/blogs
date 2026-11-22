---
title: "Firecrawl Local：AI エージェントのスクレイピングを手元の Rust バイナリ 1 本で動かす"
date: 2026-11-22
lastmod: 2026-11-22
slug: "firecrawl-local"
draft: false
source_url: "https://github.com/hdknr/blogs/issues/694#issuecomment-7074024470"
categories: ["AI/LLM"]
tags: ["Firecrawl", "mcp", "rust", "スクレイピング", "AIエージェント"]
---

## はじめに

Web ページを LLM が読みやすい Markdown に変換するサービス **Firecrawl** が、2026 年 11 月 18 日に「[Firecrawl Local](https://x.com/firecrawl/status/2123096169630912637)」を発表しました。リポジトリを作り直し、AI エージェントが**手元のマシンでスクレイピングできる**ようにしたものです。

発表で挙げられた特徴は次の 3 点です。

- Rust で書いたスクレイピング部分が、従来のセルフホスト版より **37 倍速い**
- メモリ使用量は **230 分の 1**（待機時 11MB）
- **100% オープンソース**

さらに、Firecrawl の既存の MCP サーバーや SDK がそのまま使えます。ただし「Local」といっても、既定では検索や取得できなかったページの代理取得が Firecrawl Cloud に送られます。本記事では [GitHub リポジトリ](https://github.com/firecrawl/firecrawl) の README をもとに、導入方法と、何が手元で動き何が Cloud に行くのかを整理します。

## プロダクトと用語

| 名前 | 説明 |
| --- | --- |
| Firecrawl Cloud | firecrawl.dev のホスティング版。検索・構造化 JSON・ブラウザ操作など全機能を持つ |
| Firecrawl Local | 今回の新製品。`firecrawl-local` という 1 本のバイナリで動く。DB・キュー・コンテナは不要 |
| セルフホスト版 | `apps/api` にある従来のフルサーバー。Redis・PostgreSQL・ブラウザサービスを Docker Compose で動かす |
| MCP | Model Context Protocol。AI エージェントに外部ツールをつなぐための標準プロトコル |
| Alexandria | Firecrawl Cloud が提供する 550 以上のデータプロバイダーの集合（人物・企業・論文など） |

これまで「Firecrawl を自前で動かす」には、セルフホスト版のサーバー一式を立てる必要がありました。Firecrawl Local は、Cloud とフル構成のセルフホスト版の間を埋める軽量な選択肢です。

## インストール

crates.io（Rust のパッケージレジストリ）からインストールします。Rust と C コンパイラが必要です（macOS は `xcode-select --install`、Debian/Ubuntu は `build-essential`）。

```bash
cargo install firecrawl-local
firecrawl-local --version
```

オプションで次の 2 つがあると、できることが増えます。

- **Chrome / Chromium**: JavaScript が必要なページを、手元にインストール済みのブラウザでレンダリングします。ブラウザが無くても静的なページは取得できます。JavaScript でのレンダリングが必要なページは、その旨の警告付きで返ります。
- **Node.js 22 以上**: MCP サーバーは npm パッケージ `firecrawl-mcp` を `npx` 経由で動かすため必要です。

## 基本の使い方

コマンドラインから直接使えます。

```bash
# 1 ページを Markdown で出力
firecrawl-local scrape https://example.com --markdown

# サイトをクロールして 1 ページ 1 ファイルの Markdown を保存
firecrawl-local crawl https://docs.firecrawl.dev --limit 50 --out ./pages

# サイト内の URL を一覧
firecrawl-local map https://firecrawl.dev
```

`--markdown` を付けない `scrape` は、Firecrawl API と同じ JSON を出力します。`--format markdown,links` のように形式を選ぶこともでき、選択肢は `markdown`・`html`・`rawHtml`・`links` です。

HTML だけでなく、PDF や Office 文書もローカルで解析されます。

## AI エージェントへの組み込み（MCP）

`init` を実行すると、マシン上の AI ツールを探して MCP サーバーとして登録してくれます。

```bash
firecrawl-local init
```

対応しているのは Claude Code、Claude Desktop、Cursor、Windsurf、Gemini CLI、Codex です。設定ファイルは書き換える前にバックアップされます。登録後は AI ツールを再起動します。

- `--dry-run`: 書き込まずに変更内容だけを表示する
- `--agent cursor`: 指定した 1 つのツールだけを設定する

手で登録する場合は、`firecrawl-local mcp` を stdio の MCP サーバーとして指定します。`/path/to/firecrawl-local` は `which firecrawl-local` で調べたフルパス（通常は `~/.cargo/bin/firecrawl-local`）に置き換えてください。

```json
{
  "mcpServers": {
    "firecrawl": {
      "command": "/path/to/firecrawl-local",
      "args": ["mcp"]
    }
  }
}
```

`firecrawl-local mcp` は内部で、自分のマシン内（ループバック）だけで使うポートにローカル API を起動し、そこに向けて `firecrawl-mcp` パッケージを動かします。そのため、エージェントから見えるツールは通常の Firecrawl MCP と同じです。scrape・crawl・map・batch scrape は手元で動き、それ以外のツール（search など）は Firecrawl Cloud に送られます。

## localhost で Firecrawl API を動かす

`serve` は Firecrawl v2 API を 3002 番ポートで提供します。既存の Firecrawl 向けコードは API の URL を差し替えるだけで動き、ローカルのルートには API キーも要りません。

```bash
firecrawl-local serve
```

```bash
curl -s http://localhost:3002/v2/scrape \
  -H 'content-type: application/json' \
  -d '{"url":"https://example.com","formats":["markdown"]}'
```

Python SDK からはこう使います。

```bash
pip install firecrawl
```

```python
from firecrawl import Firecrawl

app = Firecrawl(api_url="http://localhost:3002")
print(app.scrape("https://example.com").markdown)
```

エンドポイントの扱いは次のとおりです。

- **手元で処理**: `POST /v2/scrape`、`POST /v2/map`、crawl と batch scrape の開始・状態確認・キャンセル、`GET /health`
- **Cloud に転送**: `/v2/search` など、それ以外の `/v2` エンドポイント（後述の `FIRECRAWL_CLOUD` で制御）
- **提供なし**: v0・v1 のエンドポイント

crawl と batch のジョブはメモリ上にあり、開始から 1 時間で消えます。

## 何が手元で動き、何がクラウドに行くのか

「Local」という名前ですが、すべてが手元で完結するわけではありません。この線引きは、導入前に押さえておくべき一番のポイントです。

![Firecrawl Local の処理の振り分けを示す図。AI エージェントや SDK からの要求のうち、scrape・crawl・map・batch scrape と PDF/Office 文書の解析は手元のマシンで処理され、検索、手元からは取得できなかったページ、Alexandria のデータプロバイダーは Firecrawl Cloud に送られる。環境変数 FIRECRAWL_CLOUD=off でクラウドへの送信を止められる](/blogs/images/firecrawl-local-what-runs-where.png)

| 機能 | Firecrawl Local | Firecrawl Cloud |
| --- | --- | --- |
| Scrape | Markdown・HTML・生 HTML・リンク | 加えて構造化 JSON・要約・スクリーンショット・ブラウザ操作 |
| Crawl / Map / Batch Scrape | ✅ | ✅ |
| PDF・Office 文書 | ✅ | ✅ |
| Search | Cloud 経由（アカウント不要、レート制限あり） | ✅ |
| Alexandria | Cloud 経由（`firecrawl-local login` が必要） | ✅ |
| Interact / Agent / Monitor | — | ✅ |

ローカルの scrape は `json` と `summary` の形式を警告付きでスキップし、ブラウザの `actions` も無視します。構造化 JSON の抽出やページ操作が必要なら Cloud を使う、という棲み分けです。

注意したいのは**ブロックされたページのフォールバック**です。単一ページの scrape で、通常の取得もローカルブラウザも拒否された場合、既定では Firecrawl Cloud が代わりに取得します。その結果には `"source": "firecrawl-cloud"` が付きます。Cloud でも取れなければ `"blocked": true` と理由付きの警告が返ります。

Cloud への送信は環境変数 `FIRECRAWL_CLOUD` で制御します。

| 値 | 効果 |
| --- | --- |
| `auto`（既定） | 検索・ブロック時のフォールバック・Alexandria がすべて有効 |
| `search` | 検索だけを Cloud に送る |
| `off` | Cloud には何も送らない |

認識できない値は `off` として扱われます。社内データや機密性の高いページを扱うなら、`FIRECRAWL_CLOUD=off` を明示しておくのが安全です。

> **送信される識別情報**: Cloud への呼び出しには、ランダムなインストール ID と呼び出し元のツール名が付きます。Firecrawl はこれでインストール数を集計しています。

## セキュリティの既定値

AI エージェントにスクレイパーを持たせるときに怖いのが、**SSRF**（サーバーに内部ネットワークの URL を開かせる攻撃）です。Firecrawl Local はこの点を丁寧に設計しており、README にも詳しく書かれています。

- **`scrape`・`crawl`・`map`・`mcp`** は、手元で操作するユーザー本人が使う前提のコマンドなので、`localhost` やプライベートネットワークにもアクセスできます。`scrape`・`crawl`・`mcp` には、それらを拒否する `--public-only` があります。
- **`serve`** は `127.0.0.1` で待ち受け、`--allow-private` を付けない限り localhost やプライベートアドレスへのリクエストを拒否します。`--host` で別のアドレスにバインドする場合は `--token` が必須で、Host ヘッダーも許可リストで照合されます。
- **リンクローカルとクラウドのメタデータアドレス**（`169.254.169.254` など）は、リダイレクトや DNS 解決の後も含めて、どのモードでも常に拒否されます。

README はプロンプトインジェクションの危険にも触れています。隠し指示を仕込んだページを読んだエージェントが、内部 URL を開かされるケースです。信頼できないサイトを読ませるなら、MCP サーバーは次のように登録するよう推奨しています。

```json
{
  "mcpServers": {
    "firecrawl": {
      "command": "/path/to/firecrawl-local",
      "args": ["mcp", "--public-only"]
    }
  }
}
```

ブラウザ側も同じルールで守られています。Chrome はヘッドレス・サンドボックス有効・使い捨てプロファイルで起動します。さらに、Firecrawl Local 内部のループバックプロキシの後ろに置かれ、リダイレクト、サブリソース、スクリプトのリクエスト、WebSocket まで、開く接続をすべて検査します。

### Docker で動かすときの seccomp 設定

Chrome のサンドボックスはユーザー名前空間を使いますが、Docker の既定の seccomp プロファイルはこれをブロックします。JavaScript ページをコンテナ内でレンダリングするには、既定に加えて `clone`・`setns`・`unshare` を許可したプロファイルを使います。Playwright が公開しているものが使えます。

```bash
curl -fsSLO https://raw.githubusercontent.com/microsoft/playwright/main/utils/docker/seccomp_profile.json
docker run --security-opt seccomp=seccomp_profile.json your-image
```

`your-image` は、firecrawl-local と Chrome を入れた自作のイメージに置き換えてください。

`seccomp=unconfined` は使わないよう README は明記しています。制御できないページを読み込むコンテナから、フィルターを丸ごと外すことになるためです。

## ライセンスと位置づけ

リポジトリは主に **AGPL-3.0** で、SDK と一部の UI コンポーネントは MIT です。Firecrawl Local は `apps/api/native/src` の HTML クリーニングコードをそのままコンパイルしています。つまり Cloud と同じ変換ロジックで Markdown が作られます。

セルフホスト版（`apps/api`）は Firecrawl Local の登場後もそのまま残っています。キュー・ワーカー・全形式が必要なら従来どおりそちらを使います。

## どれを選ぶか

| 用途 | 向いている選択肢 |
| --- | --- |
| 個人の AI エージェントにスクレイピングを持たせたい | Firecrawl Local（`init` で MCP 登録） |
| 既存の Firecrawl 連携コードを手元で試したい | Firecrawl Local（`serve`） |
| 構造化 JSON・ブラウザ操作・検索を本格的に使いたい | Firecrawl Cloud |
| 社内インフラで全機能を大規模に運用したい | セルフホスト版 |

## まとめ

Firecrawl Local は、「Web を Markdown にする」という Firecrawl の中核機能を、Rust バイナリ 1 本で手元に持ってこられるツールです。`cargo install` と `firecrawl-local init` の 2 コマンドで、Claude Code や Cursor から使えるようになります。

一方で、既定では検索とブロック時のフォールバックが Cloud に出ていきます。機密を扱う環境では `FIRECRAWL_CLOUD=off` を、信頼できないサイトを読ませるエージェントでは `--public-only` を設定してから使い始めるのがおすすめです。

## 参考

- [Firecrawl の発表ポスト（X）](https://x.com/firecrawl/status/2123096169630912637)
- [firecrawl/firecrawl（GitHub）](https://github.com/firecrawl/firecrawl)
- [Firecrawl Local README](https://github.com/firecrawl/firecrawl/tree/main/apps/local)
