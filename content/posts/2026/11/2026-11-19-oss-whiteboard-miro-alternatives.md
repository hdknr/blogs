---
title: "Miro の代わりになる OSS ホワイトボード比較：Excalidraw は MIT、tldraw は OSS ではない"
date: 2026-11-19
lastmod: 2026-11-19
slug: "oss-whiteboard-miro-alternatives"
draft: false
categories: ["ツール/開発環境"]
tags: ["ホワイトボード", "Excalidraw", "draw.io", "オープンソース", "ライセンス"]
---

## はじめに

Miro のようなホワイトボードを、データを手元に置いたまま、あるいは自分のアプリに組み込んで使いたい。そんなときの候補になる OSS を 6 つ取り上げ、特徴・セルフホストの方法・ライセンスを比較します。

結論を先に書くと、Miro 代替の本命は **Excalidraw（MIT）** です。アプリへの組み込みなら Excalidraw か **BlockSuite（MPL-2.0）** が候補になります。一方、人気の **tldraw はソースが公開されていますが OSS ではなく**、本番での利用には有償ライセンスが必要です。

この記事でわかること:

- 6 製品のライセンス・形態・向いている用途の比較
- セルフホストの手順と、運用するときの注意点
- tldraw のライセンスの落とし穴

[前回の記事](/blogs/posts/2026/11/affine-local-first-notion-alternative/)で取り上げた AFFiNE もホワイトボード機能を持っていますが、本記事ではホワイトボード単体のツールと、組み込み用の部品に絞っています。スター数とライセンスは、2026 年 11 月 19 日時点で GitHub API から取得した値です。

## 比較の一覧

| ソフトウェア | ライセンス | スター数 | 形態 | 向いている用途 |
|---|---|---|---|---|
| [Excalidraw](https://github.com/excalidraw/excalidraw) | MIT | 約 13.6 万 | Web アプリ / React コンポーネント | 手書き風の図、ブレスト、アプリへの組み込み |
| [BlockSuite](https://github.com/toeverything/blocksuite) | MPL-2.0 | 約 6,100 | Web Components のエディタ部品 | ドキュメントとキャンバスを統合したエディタの構築 |
| [draw.io](https://github.com/jgraph/drawio) | Apache-2.0 | 約 9,500 | Web アプリ / デスクトップ | 構成図・フローチャート |
| [WBO](https://github.com/lovasoa/whitebophir) | AGPL-3.0 | 約 2,700 | Web アプリ | 手軽な共同お絵描きボード |
| [Spacedeck Open](https://github.com/spacedeck/spacedeck-open) | AGPL-3.0 | 約 1,100 | Web アプリ | 画像・動画・付箋を並べるムードボード |
| [OpenBoard](https://github.com/OpenBoard-org/OpenBoard) | GPL-3.0 | 約 3,100 | デスクトップアプリ | 授業用の電子黒板 |
| （参考）[tldraw](https://github.com/tldraw/tldraw) | 独自ライセンス | 約 5.1 万 | React の SDK | 本番利用は有償ライセンスが必要 |

### ライセンスの違い

ライセンスの違いは、組み込みや改変をするときに効いてきます。

| ライセンス | 種類 | 押さえておく点 |
|---|---|---|
| MIT / Apache-2.0 | 寛容型 | 著作権表示を残せば、改変・組み込み・商用利用が自由 |
| MPL-2.0 | ファイル単位のコピーレフト | 改変した MPL のファイルはソース公開が必要。組み合わせた自分のコードは公開不要 |
| GPL-3.0 | コピーレフト | 改変版を配布するとき、改変版全体のソース公開が必要 |
| AGPL-3.0 | ネットワーク越しにも効くコピーレフト | 改変版を Web サービスとして提供するだけでも、改変版全体のソース公開が必要 |

## Excalidraw：最有力の MIT ホワイトボード

Excalidraw は手書き風のタッチで図を描ける、無限キャンバスのホワイトボードです。スター数は約 13.6 万で、このジャンルでは最大の規模です。

主な機能は次のとおりです。

- 矩形・円・ひし形・矢印・線・フリーハンドなどの描画ツール
- 矢印のバインド（図形に吸着する矢印）とラベル付き矢印
- 画像の貼り付け、図形ライブラリ、ダークモード
- PNG・SVG への書き出しと、`.excalidraw`（JSON）形式での保存

公式の [excalidraw.com](https://excalidraw.com) は、ブラウザ内に自動保存され（ローカルファースト）、オフラインでも動きます（PWA）。エンドツーエンド暗号化されたリアルタイム共同編集にも対応しています。

### アプリへの組み込み

Excalidraw の本体は npm パッケージとして公開されており、React アプリに組み込めます。

```bash
npm install react react-dom @excalidraw/excalidraw
```

MIT ライセンスなので、自社サービスに組み込んで商用提供しても問題ありません。README には、Google Cloud、Meta、CodeSandbox、Notion などのサービスや、Obsidian のプラグインが採用例として挙がっています。

### セルフホストで共同編集する際の注意点

共同編集機能は、npm パッケージではなく excalidraw.com のアプリ側にあります。セルフホストで共同編集まで使うには、次の 3 つが必要です。

- **ルームサーバー**：WebSocket で編集内容を中継する [excalidraw-room](https://github.com/excalidraw/excalidraw-room) を別に立てる
- **フロントエンドの再ビルド**：接続先 URL（`VITE_APP_WS_SERVER_URL`）はビルド時に埋め込まれるので、自分のルームサーバーを指すようにビルドし直す
- **HTTPS**：共同編集はブラウザの `crypto.subtle` を使うため、HTTPS か localhost でしか動かない

excalidraw-room の更新は 2024 年 7 月で止まっています。1 人で使うだけなら excalidraw.com をそのまま使い、チームで共有するなら公式の商用サービス Excalidraw+ を検討するのが手軽です。

## BlockSuite：AFFiNE のエディタを部品として使う

BlockSuite は、AFFiNE のエディタ部分を独立させた OSS です。README では、VS Code に対する Monaco Editor のような関係だと説明しています。ただし Monaco と違い、BlockSuite は AFFiNE のコードから自動生成されるのではなく、独立したプロジェクトとして保守されています。

2 種類のエディタを提供しています。

- `PageEditor`：ブロックベースのドキュメントエディタ
- `EdgelessEditor`：キャンバス上で図形とリッチテキストを扱うエディタ（AFFiNE のホワイトボードモードに相当）

どちらも Web Components で作られているので、React 以外のフレームワークからも使えます。データ層（`@blocksuite/store`）は、CRDT（複数人の同時編集を競合なくマージできるデータ構造）のライブラリ Yjs の上に作られています。そのため、リアルタイム共同編集と履歴の巻き戻しに対応しています。

ライセンスは MPL-2.0 です。BlockSuite 自体のファイルを改変した場合は、そのファイルのソース公開が必要です。BlockSuite を部品として使うだけなら、自分のアプリのコードを公開する必要はありません。ただし README には「まだ初期段階」と明記されているので、本番採用の前に API の安定度を確認してください。

## draw.io：構成図向け。Docker でセルフホストできる

draw.io（diagrams.net）は、構成図・フローチャート・ER 図などを描くためのツールです。付箋を貼っていくホワイトボードとは少し方向性が違いますが、図形ライブラリの豊富さは群を抜いています。本ブログの図も draw.io で描いています。

ソースは Apache-2.0 で公開されており、Docker イメージでセルフホストできます。

```bash
docker run -it --rm --name="draw" -p 8080:8080 -p 8443:8443 jgraph/drawio
```

起動後に `http://localhost:8080/?offline=1` を開きます。`?offline=1` はクラウドストレージ連携を無効にするセキュリティ用のパラメーターです。

注意点として、[docker-drawio](https://github.com/jgraph/docker-drawio) の README では、このイメージは「評価用のテスト版」とされています。本番向けには有償版が案内されているので、社内で本格運用するなら、この記述を確認したうえで判断してください。

## WBO：Docker 1 コマンドで立つ共同ホワイトボード

WBO（Whitebophir）は、多人数で同時にお絵描きできる軽量なホワイトボードです。ボードは SVG ファイルとして保存されるので、データベースは要りません。

```bash
mkdir wbo-boards
chown -R 1000:1000 wbo-boards
docker run -it --publish 5001:80 --volume "$(pwd)/wbo-boards:/opt/app/server-data" lovasoa/wbo:latest
```

Linux では `chown` に `sudo` が必要な場合があります。起動後に `http://localhost:5001` を開けば使えます。

初期状態では、ボードの URL を知っている人なら誰でも編集できます。社内で使うなら、環境変数 `AUTH_SECRET_KEY` を設定して JWT 認証を有効にしましょう。トークンに `editor:team` のようなボード単位のロールを持たせることで、開けるボードと権限を制御できます。

## Spacedeck Open：画像や動画を並べるボード

Spacedeck Open は、もともと商用 SaaS だった Spacedeck を OSS にしたものです。2018 年に spacedeck.com が終了したあと公開され、2020 年から MNT Research GmbH が開発を再開しています。

付箋や図形に加えて、画像・動画・音声をドラッグ＆ドロップで並べられるのが特徴で、ムードボード、ブレスト、デザイン思考のワークショップに向いています。ボードをズームするプレゼンテーションとして見せる機能もあります。

Node.js で動き、データはデフォルトで SQLite に保存されます。リポジトリに `docker-compose.yml` が含まれているので、`config/default.json` を調整してから Docker Compose で起動できます。

```bash
git clone https://github.com/spacedeck/spacedeck-open.git
cd spacedeck-open
docker compose up -d
```

## OpenBoard：授業向けの電子黒板

OpenBoard は、学校での利用を主な目的としたデスクトップ型の電子黒板アプリです。Windows・macOS・Debian 向けのインストーラーが用意されており、35 言語に対応しています。

Web サイトをボード上に配置して操作できる「Web ウィジェット」があり、教材をそのまま黒板に貼り付けられます。ブラウザで共同編集するタイプではないので、Miro の代わりというより、プロジェクターや電子黒板で使う授業ツールとして見るのが適切です。

## 注意：tldraw のライセンスは OSS ではない（本番利用は有償）

tldraw は約 5.1 万スターを集める人気のホワイトボード SDK で、「OSS のホワイトボード」として紹介されることもあります。しかし GitHub API でライセンスを取得すると、`NOASSERTION`（GitHub が標準のライセンスとして判定できなかったことを示す値）が返ります。

```bash
gh api repos/tldraw/tldraw --jq '.license.spdx_id'
# => NOASSERTION
```

`LICENSE.md` を読むと、tldraw 社独自のライセンスでした。要点は次のとおりです。

- 開発環境での利用・改変・自分のプロジェクトへの同梱は許可されている
- **本番環境での利用は禁止**。本番で使うには商用ライセンスか、期間限定のトライアルライセンスが必要
- ライセンスキーを検証する仕組みが組み込まれており、その無効化は禁止
- ライセンス遵守のため、使用状況データを tldraw 社に送信することがある

つまりソースは公開されていますが、本番利用を制限している時点で、OSI（Open Source Initiative）の定義する「オープンソース」には当たりません。本番で無償で使える組み込み用ホワイトボードを探しているなら、Excalidraw（MIT）か BlockSuite（MPL-2.0）を選ぶことになります。

## 用途別の選び方

| やりたいこと | おすすめ |
|---|---|
| Miro の代わりにすぐ使いたい | Excalidraw（excalidraw.com） |
| 自分のアプリにホワイトボードを組み込みたい | Excalidraw（MIT） |
| ドキュメントとキャンバスを統合したエディタを作りたい | BlockSuite（MPL-2.0） |
| ドキュメントとホワイトボードを統合したワークスペースが欲しい | [AFFiNE](/blogs/posts/2026/11/affine-local-first-notion-alternative/) |
| 構成図・フローチャートを描きたい | draw.io |
| 社内に軽量な共同ボードを立てたい | WBO（JWT 認証を有効にする） |
| 画像や動画を並べるムードボードが欲しい | Spacedeck Open |
| 授業で電子黒板として使いたい | OpenBoard |

WBO と Spacedeck Open は AGPL-3.0 です。社内でそのまま使う分には問題ありませんが、改変してサービスとして外部に提供する場合は、上の表のとおりソース公開義務が生じます。

## まとめ

- Miro 代替の OSS ホワイトボードの本命は Excalidraw。MIT ライセンスで、npm パッケージとして組み込める
- ただし Excalidraw をセルフホストして共同編集まで使うには、ルームサーバーの構築とフロントエンドの再ビルドが要る
- AFFiNE のホワイトボード部分は BlockSuite として MPL-2.0 で公開されており、自分のアプリに組み込める
- draw.io は図を描く用途に強いが、公式 Docker イメージは評価用と位置づけられている
- WBO・Spacedeck Open は AGPL-3.0。セルフホストは簡単だが、改変してサービス提供する場合はソース公開義務に注意
- OpenBoard は Miro 代替というより、授業用の電子黒板
- tldraw はソース公開だが独自ライセンスで、本番利用には有償ライセンスが必要

「ソースが GitHub にある」ことと「本番で自由に使える」ことは別の話です。採用前に `LICENSE` を確認する習慣は、ホワイトボードでも変わりません。

## 参考リンク

- [excalidraw/excalidraw](https://github.com/excalidraw/excalidraw)
- [excalidraw/excalidraw-room](https://github.com/excalidraw/excalidraw-room)
- [toeverything/blocksuite](https://github.com/toeverything/blocksuite)
- [jgraph/drawio](https://github.com/jgraph/drawio)
- [jgraph/docker-drawio](https://github.com/jgraph/docker-drawio)
- [lovasoa/whitebophir](https://github.com/lovasoa/whitebophir)
- [spacedeck/spacedeck-open](https://github.com/spacedeck/spacedeck-open)
- [OpenBoard-org/OpenBoard](https://github.com/OpenBoard-org/OpenBoard)
- [tldraw/tldraw](https://github.com/tldraw/tldraw)
