---
title: "Redshift か、S3 ＋ Iceberg のレイクハウスか：DWH とオープンテーブルフォーマットの選び方"
date: 2026-10-13
lastmod: 2026-10-13
slug: "redshift-vs-lakehouse"
draft: false
categories: ["データベース"]
tags: ["Redshift", "Apache Iceberg", "aws", "データ基盤", "DuckLake"]
---

AWS で分析基盤を作るとき、まず候補に挙がるのが **Amazon Redshift** です。一方で、S3 に Apache Iceberg 形式でデータを置き、Athena や Spark、DuckDB から読む**レイクハウス**という作り方も広まっています。

この記事は、次の 2 本に続くシリーズの 3 本目です。

- [Apache Iceberg 入門：データレイクを「テーブル」にする仕組みと DuckDB との関係](/blogs/posts/2026/10/apache-iceberg-duckdb/)
- [DuckLake 入門：メタデータを SQL データベースに置くレイクハウスフォーマットと Iceberg との違い](/blogs/posts/2026/10/ducklake-sql-lakehouse/)

前の 2 本では Iceberg と DuckLake という**テーブルフォーマット**同士を比べました。今回は一段上がって、「データを Redshift の中に持つか、S3 にオープンな形式で持つか」という**アーキテクチャ**の選び方を整理します。

## Redshift と Iceberg は同じ土俵にない

最初に押さえておきたいのは、Redshift と Iceberg は直接比べるものではない、という点です。

- **Iceberg / DuckLake**：S3 上のファイルをテーブルとして管理する**形式**です。計算エンジンは持たず、Athena や Spark、DuckDB などが読み書きします。
- **Redshift**：計算エンジン・テーブル管理・ストレージが一体になった **DWH（データウェアハウス）製品**です。

さらに、今の Redshift は Iceberg テーブルを読むだけでなく書くこともできます。つまり、両者は「どちらか」ではなく組み合わせられる関係です。そのため比べるべきは、データの**置き場所**になります。

![DWH 一体型とレイクハウスの構成を比べた図。左の DWH 一体型では、BI やアプリケーションが Amazon Redshift にアクセスし、Redshift の中に計算（Serverless の RPU またはノード）、テーブル管理（内部のカタログ）、Redshift マネージドストレージ（RMS）がまとまっている。右のレイクハウスでは、Redshift、Athena、Spark（Glue・EMR）、DuckDB の各エンジンが AWS Glue Data Catalog または S3 Tables のカタログを経由して、Amazon S3 上の Apache Iceberg テーブルを読み書きする。Redshift もエンジンの 1 つとして並んでいる](/blogs/images/redshift-vs-lakehouse-architecture.png)

| 観点 | Redshift にデータを持つ（RMS） | S3 に Iceberg で持つ（レイクハウス） |
|---|---|---|
| データの形式 | Redshift 内部の形式 | Parquet ＋ Iceberg のメタデータ（オープン） |
| 読み書きできるエンジン | 基本は Redshift のみ | Redshift、Athena、Spark、DuckDB など |
| テーブル管理 | Redshift 内部 | Glue Data Catalog / S3 Tables |
| トランザクション | 通常の DWH として複数文のトランザクションが使える | エンジンごとの制約あり（後述） |
| ベンダーロックイン | 強い | 弱い（形式がオープン） |

## Redshift の料金の仕組み

Redshift には、ノード数を決めて常時起動するプロビジョンド型と、使った分だけ課金される **Redshift Serverless** があります。ここでは Serverless を中心に見ます。[料金ページ](https://aws.amazon.com/redshift/pricing/)の記載は次のとおりです（金額はバージニア北部リージョンの計算例）。

| 項目 | 内容 |
|---|---|
| 計算 | RPU（Redshift Processing Unit）× 時間で課金。計算例では 1 RPU 時間あたり $0.375 |
| 基本容量 | 4〜1024 RPU の範囲で設定 |
| 課金単位 | 秒単位（最低 60 秒） |
| アイドル時 | 課金なし |
| ストレージ（RMS） | 計算例では 1 GB・月あたり $0.024 |
| S3 上の外部データへのクエリ | 別課金ではなく、RPU 時間に含まれる |

計算例の単価で最小の 4 RPU を動かすと、1 時間あたり $1.50 です（料金ページにも「as low as $1.50 per hour」とあります）。アイドル時に課金されないので、日中だけ使うような負荷なら Serverless が合います。プロビジョンド型では、混雑時に自動で処理能力を足す Concurrency Scaling の無料枠が、1 日最大 1 時間分たまります。

レイクハウス側の代表である Athena は、[料金ページ](https://aws.amazon.com/athena/pricing/)の計算例ではスキャンしたデータ 1 TB あたり $5 です。DuckDB は自分の PC や Lambda で動かすので、エンジンそのものの利用料はかかりません。

ここから言えるのは、**料金の構造が違う**ということです。

- **Redshift Serverless**：起動している時間と RPU 数で決まる。基本容量で収まる範囲なら、クエリの本数が増えても料金は変わらない。ただし負荷が高まって RPU が自動で増えると、その分も同じ単価で課金される。
- **Athena**：スキャン量で決まる。たまにしか投げないなら安いが、大量のデータを何度も読むと膨らむ。
- **DuckDB**：利用料はかからず、手元のマシンの能力が上限になる。

どれが安いかはクエリの頻度とデータ量で逆転するので、一概には言えません。実際の見積もりは、自分のリージョンの料金で試算してください。

## Redshift から Iceberg を読み書きする

Redshift の Iceberg 対応は、ここ 1 年で大きく広がりました。

| 時期 | 内容 |
|---|---|
| 2025 年 11 月 | Iceberg テーブルへの書き込みが GA（CREATE TABLE、INSERT など） |
| 2026 年 5 月 | Iceberg テーブルへの ALTER TABLE と、自動マウントされる `awsdatacatalog` 経由の書き込みに対応 |
| 2026 年 8 月 | Iceberg v3 テーブル（削除ベクター、行の系譜、列の既定値）に対応 |

現行の[ドキュメント](https://docs.aws.amazon.com/redshift/latest/dg/iceberg-writes-sql-syntax.html)では、CREATE TABLE、CREATE TABLE AS SELECT、INSERT、UPDATE、DELETE、MERGE が使えます。Iceberg テーブルは AWS Glue Data Catalog に登録されている必要があり、プロビジョンド型と Serverless のどちらからも書き込めます。

```sql
-- Glue Data Catalog（自動マウントされた awsdatacatalog）上に Iceberg テーブルを作る
CREATE TABLE awsdatacatalog.my_glue_db.orders (
  order_id INT,
  status VARCHAR,
  region VARCHAR
)
USING ICEBERG
LOCATION 's3://amzn-s3-demo-bucket/orders/';

-- S3 Tables のテーブルバケットにある既存のテーブルには、3 部構成の名前で書く
INSERT INTO "amzn-s3-demo-bucket@s3tablescatalog".my_namespace.orders
VALUES (1, 'pending', 'us-east-1');
```

ここで作ったテーブルは、Athena や Spark、DuckDB からも同じように読めます。Redshift で集計した結果を Iceberg テーブルとして書き出し、ほかのチームは別のエンジンで使う、という分担ができるわけです。

### Iceberg への書き込みの制約

一方で、Redshift の内部テーブル（RMS）と同じ感覚では使えません。[トランザクションの仕様](https://docs.aws.amazon.com/redshift/latest/dg/iceberg-writes-transaction-semantics.html)には、次の制約があります。

- Iceberg への書き込みは 1 文が 1 トランザクションです。`BEGIN` 〜 `COMMIT` の中に Iceberg への書き込みを入れると、同じブロックにほかの文は入れられません。
- 2 つのトランザクションが同じテーブルやパーティションを同時に変更すると、コミットが失敗します。Redshift は自動で再試行しないので、アプリケーション側で再実行が必要です。
- ストアドプロシージャの中からは、Iceberg に書き込めません。
- Redshift 以外で作った Iceberg テーブルに書く場合は、v2 か v3 で、データ形式が Parquet であることなどが条件です。

複数のテーブルをまとめて更新する ETL や、ストアドプロシージャで組んだ既存の処理は、RMS のテーブルに残すほうが無難です。

## どれを選ぶか

ここまでの 3 本をまとめると、選び方は次のようになります。

| 状況 | おすすめの構成 |
|---|---|
| 分析するのは 1 人〜少人数、データは数十 GB 程度 | DuckDB ＋ DuckLake（または S3 上の Iceberg を DuckDB で読む） |
| 複数のチームが別々のエンジンで同じデータを使う | S3 ＋ Iceberg（Glue Data Catalog / S3 Tables）を中心にする |
| 多数のユーザーが BI ダッシュボードから同時にクエリする | Redshift（RMS）にデータを持つ |
| 上の 2 つが混ざっている | 共有データは Iceberg、頻繁に読む集計は Redshift の RMS |

実務では最後の**組み合わせ**になることが多いはずです。生データや履歴は S3 の Iceberg テーブルに置き、どのエンジンからも読めるようにしておきます。そのうえで、BI から何度も読まれる集計テーブルだけを Redshift の RMS に持ち、同時実行性能を確保します。

Redshift から Iceberg に書けるようになったので、「Redshift を使う＝データを Redshift に閉じ込める」ではなくなりました。最初から Redshift に全部入れるのではなく、まず Iceberg で持つことを基本にして、性能が必要な部分だけ Redshift に寄せる、という順番で考えると、あとで構成を変えやすくなります。

## まとめ

- Redshift は計算・テーブル管理・ストレージが一体の DWH 製品で、Iceberg や DuckLake はテーブルの形式です。比べるべきは「データをどこに、どの形式で置くか」です。
- Redshift Serverless は RPU 時間で課金され、アイドル時は無料です。Athena はスキャン量、DuckDB は利用料なしと、料金の構造がそれぞれ違います。
- Redshift は Iceberg テーブルの読み書きに対応し、2026 年には ALTER TABLE や Iceberg v3 にも対応しました。ただし書き込みは 1 文 1 トランザクションで、競合時は自動で再試行されないなどの制約があります。
- 実務では、共有データを Iceberg に置き、同時実行性能が必要な集計だけ Redshift の RMS に持つ組み合わせが現実的です。
