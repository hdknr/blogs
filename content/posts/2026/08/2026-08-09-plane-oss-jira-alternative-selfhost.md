---
title: "OSS の Jira 代替 Plane をセルフホストする前に確認した3つの落とし穴"
date: 2026-08-09
lastmod: 2026-08-09
slug: "plane-oss-jira-alternative-selfhost"
draft: false
description: "OSS の Jira 代替として人気の Plane をセルフホストする前に確認したい3点。docker-compose.yml の実態は13サービスで Celery 用に RabbitMQ が別立て、無償版が Community/Commercial の2製品に分岐し席数の公式説明も矛盾、Jira 移行ツールは AGPL 版に含まれない。"
source_url: "https://github.com/hdknr/blogs/issues/572#issuecomment-5229332077"
categories: ["クラウド/インフラ"]
tags: ["Plane", "Jira", "セルフホスト", "docker", "OSS", "agpl"]
---

タスク管理基盤を自前で持ちたい、という話になると必ず候補に挙がるのが [Plane](https://github.com/makeplane/plane) だ。「Jira / Linear / Monday / ClickUp のオープンソース代替」を名乗る OSS である。GitHub スターは 55,722（2026年8月9日時点）、ライセンスは AGPL-3.0、直近リリースは v1.4.1（2026年8月7日）と開発も活発だ。紹介記事を読む限り、乗り換えない理由はなさそうに見える。

ただ、この手の「OSS 版は無償」という比較表は、**セルフホストする側が実際に踏む地雷を書いていない**ことが多い。そこで採用検討の前段として、一次情報に当たった。リポジトリの `docker-compose.yml`、公式ドキュメント、そして Issue トラッカーの3つだ。結果、事前に知っておくべき落とし穴が3つ見つかった。

- 「PostgreSQL + Redis」では済まない。既定構成では RabbitMQ が別立てで載り、Redis の実体は Valkey（コンテナ計13個）
- インストールコマンドの選択が、そのままライセンスと席数上限の選択になっている
- Jira からの移行ツールは、AGPL 版では使えない

以下、順に根拠付きで見ていく。

## 落とし穴1：docker-compose.yml が要求するのは「PostgreSQL + Redis」ではない

多くの紹介記事は、Plane の外部依存を「PostgreSQL、Redis、S3 互換ストレージ、SMTP」と説明する。これは**間違ってはいないが、足りない**。v1.4.1 の `docker-compose.yml` を実際に読むと、定義されているサービスは13個ある。

![Plane のセルフホスト構成図。ブラウザからの通信を Caddy の proxy コンテナが受け、web・admin・space・live のフロント/Node 層と、api・worker・beat-worker・migrator の Django バックエンドに振り分ける。バックエンドは PostgreSQL 15.7、Valkey 7.2.11、RabbitMQ 3.13.6、MinIO からなるデータ層に接続する。図の右側には、本番ではこのデータ層4つを RDS / ElastiCache / S3 などのマネージドサービスへ外出しするのが定石だと注記されている](/blogs/images/plane-selfhost-architecture.png)

構成を整理するとこうなる（計13サービス）。

| 層 | サービス | 実体（技術スタック） |
|---|---|---|
| 入口 | `proxy` | Caddy 2.11.3 |
| フロント/Node | `web` / `admin` / `space` | React Router 7.18 + Vite（メイン UI / インスタンス管理 / 公開ページ） |
| フロント/Node | `live` | 共同編集サーバー（Node、リッチテキストエディタ用） |
| バックエンド | `api` / `worker` / `beat-worker` / `migrator` | Django 5.2 + Celery |
| データ | `plane-db` | PostgreSQL 15.7 |
| データ | `plane-redis` | **Valkey 7.2.11** |
| データ | `plane-mq` | **RabbitMQ 3.13.6** |
| データ | `plane-minio` | MinIO |

このうち `migrator` は起動時に DB マイグレーションを流すワンショット（`restart: no`）なので、常時稼働するのは12個だ。

「PostgreSQL + Redis」という説明との差分は2点だ。片方は認識しておけば足りる話、もう片方は見積もりに直接効く話なので、分けて見ていく。

### `plane-redis` の実体は Redis ではなく Valkey

`docker-compose.yml` のイメージ指定は `valkey/valkey:7.2.11-alpine` になっている。サービス名が `plane-redis` のままなので、設定ファイルを眺めるだけでは気づきにくい。

ただしこれは、実害の大きい罠ではない。Valkey 7.2 は Redis 7.2 のフォークでワイヤ互換であり、Django 側の依存も `redis` / `django-redis` という通常の Redis クライアントだ。接続先は `REDIS_URL` で `redis://` スキームのまま外部指定でき、公式ドキュメントもマネージド Redis への接続を明示的にサポートしている。**「同梱イメージが Valkey である」という事実を認識しておけば十分**で、マネージド Redis への差し替え計画が破綻するわけではない。ソフトウェアの採用可否を社内で審査する場合に、審査対象が Redis ではなく Valkey になる、という程度の話だ。

### Celery のブローカーに RabbitMQ が別立てで載っている

こちらは見積もりに直接効く。Celery 用に独立したメッセージキューが立っており、既定の `CELERY_BROKER_URL` も `amqp://` を指している。「Redis があれば Celery は動く」という一般論で構成を推測すると、この1コンポーネントぶんの運用（永続化、監視、バージョン追従）が見積もりから丸ごと抜ける。

ただし**アーキテクチャ上の必須要件ではない**点は補足しておきたい。設定を読むと、ブローカー URL の決定はこうなっている。

```python
# apps/api/plane/settings/common.py
AMQP_URL = os.environ.get("AMQP_URL")

if AMQP_URL:
    CELERY_BROKER_URL = AMQP_URL
else:
    CELERY_BROKER_URL = f"amqp://{RABBITMQ_USER}:..."
```

`AMQP_URL` は変数名に反して値を素通しするだけなので、`redis://` を渡せば Celery は Redis ブローカーで動く。`redis` パッケージは既に依存に含まれており、`pika` のような AMQP を直接叩くコードもない。worker / beat の entrypoint もブローカーの起動を待たない。

とはいえ、公式の compose・swarm・AIO いずれも RabbitMQ 同梱前提で、Redis ブローカー構成のドキュメントは存在しない。非サポート経路に乗ることになるうえ、Celery の Redis ブローカーは visibility timeout ベースの再配送となり、worker 障害時の重複実行の挙動が AMQP とは異なる。**「RabbitMQ を1台増やす」か「非サポート構成を自己責任で維持する」かの二択**、というのが実際のところだ。

スペック要件は CPU 2コア・RAM 4GB（本番は 8GB 推奨）。これは公式 Docker Compose ページの Commercial Edition 節に書かれた数字だが、同ページの Community Edition 節も「最低 t3.medium 相当」＝2 vCPU / 4GiB と実質同じ水準を要求している。13コンテナのマイクロサービス構成を1ホストに詰めることを考えれば妥当な数字で、「小さな VPS の余ったリソースで動かす」類のアプリではない。本番運用なら、データ層の4つはマネージドサービスへ外出しするのが現実的だ。

## 落とし穴2：インストールコマンドが2種類あり、別製品が入る

ここが一番厄介だった。公式ドキュメントには Docker Compose でのインストール手順が2通り併記されている。

### インストールコマンドの違いは「経路違い」ではない

Community Edition:

```bash
curl -fsSL -o setup.sh https://github.com/makeplane/plane/releases/latest/download/setup.sh
chmod +x setup.sh
./setup.sh
```

`setup.sh` は対話メニュー方式で、実行すると次の8項目から選ぶ形になる。

```
   1) Install
   2) Start
   3) Stop
   4) Restart
   5) Upgrade
   6) View Logs
   7) Backup Data
   8) Exit
```

`./setup.sh stop` のように引数で直接指定することもできる。

Commercial Edition:

```bash
curl -fsSL https://prime.plane.so/install/ | sh -
```

こちらは配布元スクリプトを直接シェルに渡す形式なので、社内ポリシーによっては `-o` でいったん保存し、内容を確認してから実行したほうがよい。Community 側が `-o setup.sh` で保存する手順になっているのに対し、ここだけ非対称になっている。

コマンドが並んでいると「同じ製品のインストール経路違い」に見える。だが実際には**別々のコードベースを持つ別製品**で、ライセンスも席数上限も違う。

| 項目 | Community Edition | Commercial Edition |
|---|---|---|
| 入手元 | GitHub Releases の `setup.sh` | `prime.plane.so` |
| ライセンス | AGPL-3.0（ソース公開） | クローズドソース |
| ライセンスキー | 不要 | Free プランは不要、有料機能は要キー |
| 席数 | 後述（公式見解が割れている） | Free プランはワークスペースあたり12席 |
| 有料プラン移行 | 直接は不可（先に Commercial へ乗り換えが必要） | 可能 |

なお公式ドキュメントでは、この無償枠が Free plan / Free tier と表記ゆれしている。本記事では以降「Free プラン」に統一する。

Community から Pro / Business / Enterprise へ上げたくなった場合、**プランを買うだけでは済まず、先に Commercial Edition へ乗り換える必要がある**。公式ドキュメントにも "To upgrade to paid plans, you must first switch to the Commercial Edition." と明記されている。コードベースが別である以上、AGPL 版に社内改造を積み上げていれば、この乗り換えで改造を作り直すことになると考えておいたほうがいい（この点は公式が明言しているわけではなく、「エディションごとに別コードベース」という事実からの見立てだ）。最初の `curl` の1行が、後々の移行コストを左右する構造になっている。

なお正確には、Plane のエディションは Cloud / Community / Commercial / Airgapped の4本立てだ。ただし Airgapped は Commercial をインターネット非接続環境向けにしたもので有償なので、「無償でセルフホストできるもの」に限れば上記の2択になる。

### Plane Community Edition に人数制限はあるのか

さらに調べていて見つけたのが、Plane 本体の Issue [#9086「Community Edition user limit is documented four different ways」](https://github.com/makeplane/plane/issues/9086)（2026年5月16日起票）だ。タイトルの通り、Community Edition に席数の上限があるのかについて、Plane 自身が4通りの異なる説明を公開している、という指摘である。

報告されている4つの記述はこうだ。

1. **マーケティングページ**（plane.so/open-source）— "Community Edition is free with **no user limits**"
2. **比較ブログ記事**（Plane 公式ブログ、2026年2月）— セルフホスト無償版はクラウド無償版と同じく **12ユーザー上限**
3. **課金ドキュメント**（docs.plane.so）— "The Free plan supports up to 12 seats"。ただし "Community" とも "Commercial" とも書かれておらず、セルフホスト勢には自分が対象か判別できない
4. **メンテナによる Discussion での回答** — ハードな制限は Commercial Edition の Free プランにのみ存在し、"there is no hard-coded restriction on the Community Edition"

起票者自身が同日に追加したコメントで、根本原因の見立てが示されている。Plane は「無償のセルフホスト製品」を2つ抱えている。AGPL の Community Edition と、クローズドソースである Commercial Edition の Free プランだ。対外的な文章でこの2つが混同されている、という見立てである。この整理に従えば、**AGPL の Community Edition に席数のハードリミットはない**。12席の上限は `prime.plane.so` から入れた Commercial Edition の Free プランの話、ということになる。

ただし注意したいのは、この Issue が**執筆時点（2026年8月9日）でまだ open のまま、最終更新が2026年5月16日で止まっている**ことだ。メンテナからの公式な決着はついておらず、コメントも起票者自身の1件のみである。つまり現時点では「メンテナが Discussion でそう言っている」以上の保証はない。

実務的な結論はシンプルだ。席数を根拠に採否を判断するなら、公開ドキュメントを信じず、Plane へ直接問い合わせて書面で回答を得る。数十人規模で導入してから上限に当たると、移行先はコードベースの違う Commercial Edition になる。

## 落とし穴3：Jira 移行ツールは Community Edition では使えない

Plane の売り文句のひとつが「Jira / Linear / Asana からの公式移行ツール」だ。実際、対応インポート元は Jira、Linear、Asana、ClickUp、Notion、Confluence、Flatfile、CSV と充実している。

だが公式ドキュメントの Importers 概要には、こう明記されている。

> Importers are available on Plane Cloud and the Commercial Edition for self-hosted instances.

つまり**インポーターは Cloud と Commercial Edition 専用で、AGPL の Community Edition には含まれない**。

これは採用シナリオの前提を壊しうる。「Jira のライセンス費が高いので、OSS の Plane をセルフホストして公式ツールで移行する」という筋書きは、そのままでは成立しない。Community Edition を選ぶなら、既存データの移行は REST API を叩いて自前で書くことになる。

自前移行で最低限相手にすることになるのは、プロジェクト、課題（Work Items）、コメント、添付ファイルあたりだ。このうち添付ファイルは、Jira から実体をダウンロードして Plane 側のオブジェクトストレージへ入れ直す必要があるため、他のリソースとは別工程になりやすい。加えて、課題のステータスや優先度は Plane 側の値へマッピングし直す必要がある。ユーザーの紐付けも、両者のアカウントを突き合わせる作業が発生する。Jira から数年ぶんのデータを移すなら、この一式を移行工数として最初から積んでおきたい。

逆に「移行ツールを使いたいから Commercial Edition にする」と決めると、今度は落とし穴2の「12席の Free プラン」が効いてくる。**移行ツールの利用と、AGPL・席数無制限は両立しない**。比較表からはこの排他関係が読み取れない。

## 補足：fork してカスタマイズする場合の実務

ここまでを読むと「Community Edition を fork して自社向けに作り替えればいい」と考えたくなる。実際それは選択肢として成立するが、Plane 固有の地雷がいくつかある。

### 公開 fork なら AGPL の開示義務は満たせる

まず前提の整理から。AGPL-3.0 §13 の開示義務は「**改変した場合に**、ネットワーク越しに操作する全ユーザーへ改変版のソースを提供する機会を与えよ」というものだ。裏を返せば、**fork を公開リポジトリで維持していれば、この義務は素直に満たせる**。「AGPL だからカスタマイズできない」わけではない。

ただし、公開すれば終わりではない点に注意がいる。

- **§5(a)** は、改変したファイルに「**改変した旨と改変日**」を明記することを求める。リポジトリを公開しているだけでは足りない
- **既存の著作権表示を消してはいけない。** Plane は全 `.py` / `.ts` に `Copyright (c) 2023-present Plane Software, Inc.` と `SPDX-License-Identifier: AGPL-3.0-only` のヘッダを持ち、`addlicense` と `COPYRIGHT.txt` で CI 強制している。fork 側でもこの運用を引き継ぐ必要がある
- **商標は AGPL の対象外**である。自社向けにリブランドするなら「**ロゴと製品名は差し替えるが、著作権表示とライセンス表記は残す**」が正しい形になる。逆をやると両方の意味で誤る
- §13 が求めるのは「稼働中のアプリ内での prominent な提示」なので、フッター等にソースへの導線を置き、**デプロイ済みコミットと公開コミットの一致を CI で保証する**運用が要る

### 最大の地雷は Django マイグレーションの連番衝突

技術的にいちばん痛いのはここだ。`apps/api/plane/db/migrations/` には**連番のマイグレーションが122本**あり、単一アプリで管理されている（最新は `0122_alter_draftissue_assignees_...`）。

ここに独自モデルの `0123_xxx.py` を足すと、upstream も次のリリースで `0123_yyy.py` を追加してくる。結果、追従のたびに Django が `Conflicting migrations detected; multiple leaf nodes in the migration graph` を出して起動しなくなる。しかもマイグレーションの適用履歴は DB に残るため、番号を振り直す解決が本番では効かない。

**対策は単純で、`plane.db` にマイグレーションを追加しないこと。** 独自モデルは別の Django アプリとして作り、自前の migrations ディレクトリを持たせる。既存テーブルへ列を足したくなっても、外部キーで繋いだ別テーブルに寄せるほうが長期的には安全だ。

### 改変はどこに置くか

コンフリクト量は「既存ファイルを何行変えたか」にほぼ比例する。優先順位はこうなる。

| 手段 | 追従耐性 | 主な用途 |
|---|---|---|
| 環境変数・インスタンス設定 | ◎ 影響なし | 認証、SMTP、ストレージ |
| i18n ロケール | ○ JSON の値のみ | 用語の置換 |
| テーマ・CSS の上書き | ○ | 見た目 |
| 新規ファイルの追加 | ○ 衝突しない | 独自機能 |
| 既存ファイルの改変 | ✕ 毎回衝突 | 最終手段 |

日本語ロケールは既に `packages/i18n/src/locales/ja` に28ファイル揃っている（`work-item.json`、`cycle.json`、`module.json` など）。用語の置き換え程度なら**コード差分ゼロで済む**ので、まずここでどこまで行けるかを見極めるのが分岐点になる。

なお、`ce` / `ee` の分離は `packages/editor` にしか存在しない（`ce` 27ファイル、`ee` 4ファイルで、`ee` は `ce` を re-export しているだけ）。つまり Plane は editor 以外にプラグイン用の seam を持たないので、**独自機能の置き場所は自分で設計する必要がある**。

### 追従コストを実測する

fork の維持費は、upstream の変更量がそのまま効く。実際に測るとこうなる。

| 区間 | 変更量 |
|---|---|
| v1.3.1 → v1.4.1（約3ヶ月） | **109 コミット / 300 ファイル以上** |

追従は必ずリリースタグ基準で行うこと（`preview` ブランチを追うと壊れる）。そして**差別化に関係しない修正は upstream へ PR を出す**のが最も効く。取り込まれた分は恒久的にリベース対象から外れるからだ。`CONTRIBUTING.md` を見る限り CLA の要求は記載されていないので、上流化のハードルは低そうに見える。

### 公開リポジトリならではの注意

- **ロケールファイルは公開される。** 用語のカスタマイズを i18n に寄せる方針と直結する話で、顧客固有の名称や社内用語をそこへ入れるとそのまま公開される
- **公開前に履歴全体を秘匿情報スキャンにかける。** fork は upstream の履歴も引き継ぐので、自社コミットだけ見ても足りない
- **Issue / PR も公開になる。** 顧客名や障害の詳細を含む議論は別の場所で行う運用分離が要る
- 改変する以上、公式イメージは使えず自前ビルドになる。upstream の**セキュリティ修正をどの程度の遅延で取り込むかの基準**は、あらかじめ決めておきたい

## Plane 採用判断のチェックリスト

3つの落とし穴を踏まえると、検討時に潰しておくべき項目はこうなる。

### インフラ体制

- [ ] PostgreSQL / Redis 系 / RabbitMQ / オブジェクトストレージの4種を運用できるか（PostgreSQL はハードコードで回避不可、RabbitMQ は `AMQP_URL` で Redis に寄せれば回避可能だが非サポート）
- [ ] 本番で 8GB 以上のメモリを割ける、またはデータ層をマネージドへ外出しできるか
- [ ] 常時稼働12コンテナ（`migrator` はワンショット）のバージョン追従と監視を継続的に回せるか

### エディションの選択

- [ ] Community（AGPL・移行ツールなし）か Commercial（クローズド・12席）か、最初の `curl` を打つ前に決めたか
- [ ] 将来の有料プラン移行時に、コードベースが変わることを許容できるか
- [ ] 想定人数について、公開ドキュメントではなく Plane から直接回答を得たか

### ライセンス

- [ ] 利用形態は社内に閉じているか（社外へネットワーク越しに提供すると AGPL の開示義務が効く）
- [ ] 改変版を顧客向け SaaS に組み込む計画がないか
- [ ] 法務レビューを通したか

### 移行

- [ ] 既存データの移行を API 自作で賄う工数を見積もったか
- [ ] （移行ツールが必須なら）Commercial 前提でコストを再計算したか

### fork してカスタマイズする場合

- [ ] 独自モデルを `plane.db` ではなく別アプリに隔離したか（マイグレーション連番衝突の回避）
- [ ] 用語の変更を i18n ロケールで賄えるか検証したか（コード差分ゼロで済む範囲の見極め）
- [ ] 改変ファイルへの改変明記（AGPL §5(a)）と既存の著作権表示の保持を運用に組み込んだか
- [ ] 稼働アプリ内のソース導線と、デプロイ済みコミットの公開を CI で保証したか
- [ ] 四半期あたり 100 コミット超の追従工数を計画に入れたか

## まとめ：Plane をセルフホストすべきか

Plane 自体は、55,000 超のスター・活発な開発・AGPL という条件を満たした、真っ当な選択肢だ。今回見つかった3点はいずれも「Plane が悪い」という話ではなく、**紹介記事の比較表の粒度では落ちてしまう情報**である。

- 依存ミドルウェアは公称より1段重い（既定構成では Celery 用に RabbitMQ が別立て、計13サービス）
- 「無償のセルフホスト版」が2製品あり、インストールコマンドで分岐する。しかも席数の公式説明が食い違っており、Issue も未決着
- OSS 版の目玉に見える Jira 移行ツールは、実は OSS 版に入っていない

なお、fork してカスタマイズする道は AGPL 的には塞がっていない。公開リポジトリで維持すれば開示義務は満たせる。ただしその場合は、マイグレーションの連番衝突と追従工数という別種のコストを引き受けることになる。

セルフホスト前提の OSS を評価するときは、README と比較表だけでは足りない。`docker-compose.yml` を開き、公式ドキュメントのエディション差分を読み、Issue トラッカーを検索する。今回の3点はすべて、この3つの一次情報から出てきた。所要時間は1時間ほどで、いずれも導入後に気づくと手戻りが大きい種類の情報だ。

## 参考リンク

- [makeplane/plane（GitHub）](https://github.com/makeplane/plane)
- [v1.4.1 の docker-compose.yml](https://github.com/makeplane/plane/blob/v1.4.1/docker-compose.yml) — 落とし穴1の一次情報
- [Plane 公式サイト](https://plane.so/)
- [Deploy Plane on your infrastructure（公式ドキュメント）](https://developers.plane.so/self-hosting/overview)
- [Docker Compose でのセルフホスト手順](https://developers.plane.so/self-hosting/methods/docker-compose)
- [Understanding Plane's editions](https://developers.plane.so/self-hosting/editions-and-versions)
- [Importers overview](https://docs.plane.so/importers/overview)
- [Issue #9086: Community Edition user limit is documented four different ways](https://github.com/makeplane/plane/issues/9086)
