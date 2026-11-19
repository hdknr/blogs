---
title: "Notion の OSS 代替 AFFiNE は本当に MIT？ライセンスとセルフホスト構成を確認"
date: 2026-11-19
lastmod: 2026-11-19
slug: "affine-local-first-notion-alternative"
draft: false
source_url: "https://github.com/hdknr/blogs/issues/694#issuecomment-7001411952"
categories: ["ツール/開発環境"]
tags: ["AFFiNE", "Notion", "オープンソース", "セルフホスト", "ナレッジ管理"]
---

## はじめに

X で「Notion の無料・オープンソース代替」として **AFFiNE** を紹介する投稿が流れてきました（[@josesilesdata の投稿](https://x.com/josesilesdata/status/2122978295260094534)）。投稿の要点は次のとおりです。

- オープンソースでローカルファースト。オフラインで動き、データは自分のもの
- ドキュメント・ホワイトボード・カンバンを 1 か所にまとめられる
- 要約・翻訳・書き直しができる AI を内蔵
- クラウドを使わずにデバイス間で同期できる
- Notion からワンクリックでインポートできる
- GitHub スター 44,000 超、MIT ライセンス

紹介としては魅力的ですが、「MIT ライセンス」「クラウド不要」あたりは採用判断に直結するので、リポジトリを直接確認しました。結論から言うと、**MIT なのはフロントエンドなどで、サーバー（バックエンド）は別ライセンス**です。本記事では AFFiNE の特徴を整理したうえで、ライセンスの実際とセルフホストの構成を見ていきます。

## 用語の整理

| 用語 | 意味 |
|---|---|
| AFFiNE | toeverything 社が開発するオールインワンのワークスペースアプリ。Notion と Miro の代替を掲げる |
| Miro | オンラインホワイトボードのサービス |
| ローカルファースト | データをまず手元のディスクに保存し、クラウドは同期の手段として使う設計思想 |
| CRDT | 複数端末で同時に編集しても衝突なくマージできるデータ構造 |
| Yjs / y-octo | CRDT の実装ライブラリ。y-octo は Rust 製で、AFFiNE のローカルファースト機能の中核 |
| BlockSuite | AFFiNE のエディタ部分を切り出した OSS プロジェクト |
| CE / EE | Community Edition（無償）と Enterprise Edition（有償） |
| AFFiNE Cloud | 公式が運営するホスティング型の同期サービス |

## AFFiNE の特徴

[GitHub リポジトリ](https://github.com/toeverything/AFFiNE)の README では、AFFiNE を「プライバシー重視・ローカルファースト・オープンソースの Notion & Miro 代替」と説明しています。2026 年 11 月 19 日時点のスター数は約 74,700 で、元投稿にある数字より多くなっています。

### ドキュメントとホワイトボードの統合

最大の特徴は、ドキュメントとホワイトボード（キャンバス）が完全に統合されている点です。キャンバスに置けるブロックには次のようなものがあります。

- リッチテキスト、付箋
- 埋め込み Web ページ、リンクページ
- 複数ビューのデータベース
- 図形、スライド

これらを境界のないキャンバス上に自由に配置できます。Notion のページで書いた内容を、そのまま Miro のようなボードに並べ替えられるイメージです。

### ローカルファーストとリアルタイム同期

データは手元のディスクに保存され、オフラインでも編集できます。同期とリアルタイム共同編集は CRDT で実現しており、Web 版とクロスプラットフォームのクライアントで動きます。

ただし「クラウドなしで同期できる」という点には補足が必要です。端末間の同期には同期先のサーバーが要るので、AFFiNE Cloud を使わないなら**自分でサーバーをセルフホストする**ことになります。1 台の端末で完結させるだけなら、ローカルのワークスペースで十分です。

### AI 機能

AFFiNE AI は、レポートの下書き、アウトラインからスライドへの変換、記事のマインドマップ化などを行うアシスタントです。クラウド版では有償のアドオンとして提供されています。

セルフホストでは、サーバーの `config.json` で AI 機能と BYOK（自分の API キーを持ち込む方式）を有効にし、API キー自体はワークスペースの設定画面から登録します。公式ドキュメントは、プロバイダーの API キーをサーバー設定に書かないよう注意しています。以前は `config.json` にキーを書く方式だったため、古い解説記事を見るときは注意してください。

### Notion からの移行

Notion から HTML 形式でエクスポートした ZIP を、AFFiNE のインポーターで取り込めます。元投稿は「ワンクリック」としていますが、実際はエクスポート、ダウンロード、インポート、内容の確認という手順を踏みます。

公式ブログでも、ビュー、リレーション、数式、権限、コメント、細かいスタイルは取り込み後の確認が必要としています。データベースを作り込んでいるなら、移行後に手直しする前提で工数を見積もるのが無難です。

## ライセンスの実際：「MIT」はどこまでか

元投稿は「MIT ライセンス」としていますが、GitHub API でリポジトリのライセンスを取得すると `NOASSERTION`（単一の SPDX ライセンスとして判定できない）が返ります。

```bash
gh api repos/toeverything/AFFiNE --jq '.license.spdx_id'
# => NOASSERTION
```

ルートの `LICENSE` ファイルを読むと、ディレクトリごとにライセンスが分かれています。

| 対象 | ライセンス |
|---|---|
| `packages/backend` と `packages/common/native` 配下 | `packages/backend/server/LICENSE` に定める **AFFiNE Enterprise Edition (EE) License** |
| サードパーティのコンポーネント | 各コンポーネントの元のライセンス |
| 上記以外（フロントエンドなど） | MIT |

EE License の要点は次のとおりです。

- 本番環境での利用には、AFFiNE の利用規約への同意と有効な Enterprise Edition サブスクリプションが必要
- 開発・テスト目的なら、サブスクリプションなしでコピー・改変してよい
- ただし、Community Edition（CE）として配布される部分と、クライアント側に配信される JavaScript・CSS・画像・フォントなどには EE License は適用されず、**MPL 2.0** となる

一方、README には「AFFiNE Community Edition (CE) はセルフホストなら MIT ライセンスで無償」と書かれています。CE 部分について、README は MIT、EE License の条文は MPL 2.0 と、**表記が揃っていません**。また、CE と EE の境界がディレクトリ単位でどう分かれるかも、条文からは読み取りにくくなっています。

使い方ごとに整理すると、次のようになります。

| 使い方 | 扱い |
|---|---|
| 公式の CE イメージをそのままセルフホストする | README の記述に従えば無償 |
| バックエンドを改変して本番運用する | EE License の範囲。サブスクリプションが必要になりうる |
| フロントエンドのコードを流用する | MIT（ルート `LICENSE`） |

フォークして自社サービスに組み込むような使い方を考えているなら、README ではなく `LICENSE` と EE License の条文を必ず読んでおきましょう。

## Docker Compose でセルフホストする

### 起動手順

公式の手順では、最新リリースに添付された `docker-compose.yml` を取得して起動します。

```bash
mkdir affine
cd affine
curl -L -o docker-compose.yml https://github.com/toeverything/AFFiNE/releases/latest/download/docker-compose.yml
docker compose up -d
```

起動後に `http://localhost:3010` を開き、最初の管理者アカウントを作成します。

### 構成

2026 年 11 月時点の最新リリース（v0.27.4）の `docker-compose.yml` は、次の 4 サービスで構成されています。

| サービス | イメージ | 役割 |
|---|---|---|
| `affine` | `ghcr.io/toeverything/affine:stable` | 本体サーバー（ポート 3010） |
| `affine_migration` | `ghcr.io/toeverything/affine:stable` | 起動前の DB マイグレーション（完了したら終了） |
| `redis` | `redis` | キャッシュ / キュー |
| `postgres` | `pgvector/pgvector:pg16` | データベース。ベクトル検索の拡張 pgvector 入り |

本体の定義を抜粋します。

```yaml
# docker-compose.yml の affine サービス（抜粋）
services:
  affine:
    image: ghcr.io/toeverything/affine:stable
    container_name: affine_server
    ports:
      - '3010:3010'
    depends_on:
      redis:
        condition: service_healthy
      postgres:
        condition: service_healthy
      affine_migration:
        condition: service_completed_successfully
    volumes:
      - ./data/storage:/root/.affine/storage
      - ./config:/root/.affine/config
    environment:
      - REDIS_SERVER_HOST=redis
      - DATABASE_URL=postgresql://affine@postgres:5432/affine
      - AFFINE_INDEXER_ENABLED=false
    restart: unless-stopped
```

`affine_migration` が `service_completed_successfully` になってから本体が起動する、という依存関係になっているのがポイントです。アップデート時もマイグレーションが先に走ります。設定ファイル（`config.json`）は `./config` に、アップロードされたファイルは `./data/storage` に置かれます。

### セキュリティ上の注意

サンプルの `postgres` サービスは `POSTGRES_HOST_AUTH_METHOD: trust` になっており、パスワードなしで接続できます。

```yaml
# docker-compose.yml の postgres サービス（抜粋）
services:
  postgres:
    image: pgvector/pgvector:pg16
    environment:
      POSTGRES_USER: affine
      POSTGRES_DB: affine
      POSTGRES_HOST_AUTH_METHOD: trust
```

`ports` を公開していないので、Docker ネットワークの外からは接続できません。とはいえ本番で使うなら、`POSTGRES_PASSWORD` を設定し、`DATABASE_URL` にもパスワードを含めておくのが安全です。また、3010 番ポートを直接インターネットに公開せず、TLS を終端するリバースプロキシを前段に置きましょう。

## Notion・Obsidian との位置づけ

| 観点 | AFFiNE | Notion | Obsidian |
|---|---|---|---|
| データの置き場所 | ローカル（同期はクラウドかセルフホスト） | Notion のクラウド | ローカルの Markdown ファイル |
| ホワイトボード | ドキュメントと統合 | 標準機能としてはなし | Canvas（別機能） |
| データベース | あり | あり（高機能） | コアプラグイン Bases で対応 |
| セルフホスト | 可能 | 不可 | サーバー不要（同期は Obsidian Sync や任意のストレージ） |
| ソースコード | 公開（MIT + EE License） | 非公開 | 非公開（プラグインは OSS が多い） |

「Notion のようなブロックエディタとデータベースがほしいが、データは手元に置きたい」「図とドキュメントを行き来しながら考えたい」という用途に AFFiNE は向いています。一方、プレーンな Markdown ファイルとして持ち運べることを重視するなら Obsidian のほうが素直です。

## まとめ

- AFFiNE は、ドキュメント・ホワイトボード・データベースを 1 つのキャンバスに統合したローカルファーストのワークスペースアプリ
- オフラインで動き、CRDT で同期と共同編集を実現。ただし端末間同期には AFFiNE Cloud かセルフホストのサーバーが必要
- 「MIT ライセンス」はフロントエンドなどの話。バックエンドは AFFiNE Enterprise Edition License で、CE のセルフホストが無償なのは README の記述による
- セルフホストは Docker Compose（本体・マイグレーション・Redis・PostgreSQL）で手軽に立ち上がる。DB 認証とリバースプロキシは自分で固める

SNS の紹介は「無料・MIT・クラウド不要」と気持ちよく要約されがちです。採用前に `LICENSE` を 1 回読むだけで、後から困る場面をかなり減らせます。

## 参考リンク

- [toeverything/AFFiNE（GitHub）](https://github.com/toeverything/AFFiNE)
- [AFFiNE 公式サイト](https://affine.pro)
- [AFFiNE セルフホストのドキュメント](https://docs.affine.pro/self-host-affine)
- [元になった X の投稿](https://x.com/josesilesdata/status/2122978295260094534)
