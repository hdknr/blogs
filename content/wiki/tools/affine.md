---
title: "AFFiNE"
description: "ドキュメント・ホワイトボード・データベースを 1 つのキャンバスに統合したローカルファーストのワークスペース。Notion / Miro の OSS 代替を掲げるが、ライセンスはフロントエンドが MIT、バックエンドが独自の EE License"
date: 2026-11-19
lastmod: 2026-11-19
aliases: ["アフィン", "Notion 代替", "AFFiNE CE", "BlockSuite"]
related_posts:
  - "/posts/2026/11/affine-local-first-notion-alternative/"
  - "/posts/2026/11/oss-whiteboard-miro-alternatives/"
tags: ["AFFiNE", "Notion", "オープンソース", "セルフホスト", "ナレッジ管理", "ホワイトボード", "ライセンス"]
---

## 概要

AFFiNE は toeverything 社が開発するオールインワンのワークスペースアプリ。README では「プライバシー重視・ローカルファースト・オープンソースの Notion & Miro 代替」と説明している。GitHub スターは約 74,700（2026 年 11 月時点）。

SNS では「無料・MIT・クラウド不要」と紹介されがちだが、実際には**MIT なのはフロントエンドなどで、サーバー側は別ライセンス**、端末間同期には **AFFiNE Cloud かセルフホストのサーバーが必要**。

## 詳細

### 特徴

- **ドキュメントとホワイトボードの統合**：リッチテキスト、付箋、埋め込み Web ページ、複数ビューのデータベース、図形、スライドを境界のないキャンバスに配置できる
- **ローカルファースト**：データは手元のディスクに保存されオフラインで編集できる。同期と共同編集は CRDT（Yjs / Rust 製の y-octo）で実現
- **AFFiNE AI**：下書き、アウトライン→スライド、マインドマップ化など。クラウド版では有償アドオン。セルフホストでは `config.json` で AI と BYOK を有効にし、API キーはワークスペースの設定画面で登録する（サーバー設定にキーを書かない。古い解説記事の方式とは異なる）
- **Notion からの移行**：Notion の HTML エクスポート ZIP を取り込める。ビュー、リレーション、数式、権限、コメントなどは取り込み後の確認・手直しが前提

エディタ部分は **BlockSuite**（MPL-2.0）として独立した OSS になっており、自分のアプリに組み込める（[Excalidraw](/blogs/wiki/tools/excalidraw/) の OSS ホワイトボード比較を参照）。

### ライセンスの実際

GitHub API のライセンス判定は `NOASSERTION`。ルートの `LICENSE` はディレクトリごとに分かれている。

| 対象 | ライセンス |
|---|---|
| `packages/backend`、`packages/common/native` 配下 | AFFiNE Enterprise Edition (EE) License |
| サードパーティのコンポーネント | 各コンポーネントの元のライセンス |
| それ以外（フロントエンドなど） | MIT |

EE License の要点：

- 本番利用には利用規約への同意と有効な EE サブスクリプションが必要
- 開発・テスト目的ならサブスクリプションなしでコピー・改変できる
- Community Edition（CE）として配布される部分と、クライアントに配信される JS・CSS・画像・フォントなどには EE License は適用されず MPL 2.0 とされる

一方 README は「CE はセルフホストなら MIT で無償」と書いており、CE 部分の表記（MIT と MPL 2.0）が揃っていない。CE と EE の境界も条文からは読み取りにくい。

| 使い方 | 扱い |
|---|---|
| 公式 CE イメージをそのままセルフホスト | README の記述に従えば無償 |
| バックエンドを改変して本番運用 | EE License の範囲。サブスクリプションが必要になりうる |
| フロントエンドのコードを流用 | MIT |

フォークして自社サービスに組み込むなら、README ではなく `LICENSE` と EE License の条文を読むこと。

### Docker Compose でのセルフホスト

最新リリースに添付された `docker-compose.yml` を取得して `docker compose up -d`、`http://localhost:3010` で最初の管理者を作る。v0.27.4 時点の構成は 4 サービス。

| サービス | 役割 |
|---|---|
| `affine` | 本体サーバー（3010 番） |
| `affine_migration` | 起動前の DB マイグレーション。完了後に本体が起動する（`service_completed_successfully`） |
| `redis` | キャッシュ / キュー |
| `postgres` | `pgvector/pgvector:pg16`。ベクトル検索拡張入り |

設定は `./config`、アップロードファイルは `./data/storage` に置かれる。

セキュリティ上の注意：

- サンプルの `postgres` は `POSTGRES_HOST_AUTH_METHOD: trust`（パスワードなし）。ポートは公開されていないが、本番では `POSTGRES_PASSWORD` を設定し `DATABASE_URL` にも含める
- 3010 番を直接インターネットに出さず、TLS を終端するリバースプロキシを前段に置く

### Notion・Obsidian との位置づけ

| 観点 | AFFiNE | Notion | [Obsidian](/blogs/wiki/tools/obsidian/) |
|---|---|---|---|
| データの置き場所 | ローカル（同期はクラウドかセルフホスト） | Notion のクラウド | ローカルの Markdown |
| ホワイトボード | ドキュメントと統合 | 標準機能としてはなし | Canvas（別機能） |
| セルフホスト | 可能 | 不可 | サーバー不要 |
| ソースコード | 公開（MIT + EE License） | 非公開 | 非公開（プラグインは OSS が多い） |

ブロックエディタとデータベースを手元に置きたい、図とドキュメントを行き来して考えたい用途には AFFiNE、プレーンな Markdown として持ち運べることを重視するなら Obsidian が素直。

## 関連ページ

- [Mozilla Hubs](/blogs/wiki/tools/mozilla-hubs/) — 同じくセルフホストで公式サービスの代替にするツール
- [Excalidraw](/blogs/wiki/tools/excalidraw/) — OSS ホワイトボードの比較（BlockSuite・tldraw のライセンス含む）
- [draw.io](/blogs/wiki/tools/draw-io/) — 構成図向けの作図ツール
- [Obsidian](/blogs/wiki/tools/obsidian/) — ローカルファーストの Markdown PKM

## ソース記事

- [Notion の OSS 代替 AFFiNE は本当に MIT？ライセンスとセルフホスト構成を確認](/blogs/posts/2026/11/affine-local-first-notion-alternative/) — 2026-11-19
- [Miro の代わりになる OSS ホワイトボード比較：Excalidraw は MIT、tldraw は OSS ではない](/blogs/posts/2026/11/oss-whiteboard-miro-alternatives/) — 2026-11-19
