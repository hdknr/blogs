---
title: "Apache Kafka"
description: "イベントを追記型のログとして一定期間残し、複数の読み手がそれぞれの位置から読む分散ストリーミング基盤。CDC で業務 DB の変更を検索や RAG に流す定番の経路"
date: 2026-11-20
lastmod: 2026-11-20
aliases: ["Kafka", "Kafka Connect", "KRaft", "Debezium", "Amazon MSK", "MSK Connect"]
related_posts:
  - "/posts/2026/11/apache-kafka-intro/"
  - "/posts/2026/11/data-engineering-for-ai-engineers/"
tags: ["Apache Kafka", "データエンジニアリング", "データ基盤", "CDC", "Debezium"]
---

## 概要

Apache Kafka は、イベントを**順番付きのログとしてディスクに一定期間残し、読み手がそれぞれ自分のペース・自分の位置から読む**分散ストリーミング基盤。書き手は誰が読むかを知らなくてよく、読み手を足しても書き手のコードは変わらない。読み手が止まっていても、ログが残っている限り再開すれば続きから読める。

## 詳細

### 基本の構造

| 概念 | 意味 |
|---|---|
| トピック | イベントの種類ごとの置き場所（`orders` など） |
| パーティション | トピックを分割した追記専用のログ。並列処理と順序保証の単位 |
| オフセット | パーティション内の連番。「どこまで読んだか」を表す |
| コンシューマーグループ | グループの中ではパーティションを分担し、グループどうしは独立に全件を読む。読んだ位置はグループごとに記録される |

順序が保証されるのは**パーティションの中だけ**。同じキーのレコードは同じパーティションに入るので、注文 ID をキーにすれば同じ注文のイベントは書いた順に読める。グループ内のコンシューマーをパーティション数より増やしても、余った分は待機するだけになる。

### 保持と再読み込み

レコードは読まれても消えず、保持設定（ブローカーの既定は 7 日）に従って残る。期間・サイズで消す `delete` と、キーごとに最新だけ残す `compact`（ログコンパクション。CDC と相性がよい）がある。保持期間内なら読む位置を巻き戻せるので、バグを直して過去分を再処理する、新しい埋め込みモデルでベクトル DB を作り直す、といった作業を元の DB に負荷をかけずにできる。

### 配信保証

| 保証 | 実現方法 |
|---|---|
| at-most-once | 処理の前にオフセットをコミットする |
| at-least-once | 処理の後にコミットする。実務の基本形 |
| exactly-once | 冪等プロデューサー + トランザクション + `read_committed` |

exactly-once が効くのは Kafka の中で読み書きが完結する場合だけ。外部のベクトル DB などへ書く処理は、キーから決めた ID で upsert するか、処理済みのオフセットを書き込み先と同じトランザクションで保存して、重複に耐える作りにする。冪等プロデューサーは Java クライアントでは 3.0 から既定で有効だが、librdkafka（Python の `confluent-kafka` など）では既定が `false` のまま。

### CDC：業務 DB と検索・RAG をつなぐ

Debezium は、DB の変更ログ（PostgreSQL の WAL、MySQL の binlog）を読み、挿入・更新・削除を Kafka Connect のソースコネクターとしてトピックに流す。`updated_at` で差分を取る方式と違って**削除を拾える**ので、退職者の資料や取り消された契約書を [RAG](/blogs/wiki/concepts/rag/) のインデックスから消せる。業務 DB を読むのは Debezium だけなので、検索・ベクトル DB・分析基盤と読み手を足しても DB の負荷は増えない。

ただし CDC は DB の内部の仕組みに依存し、バージョンアップやフェイルオーバーで取り込みが止まることがある。コネクターの稼働と遅延は監視が要る（[沈黙する失敗](/blogs/wiki/concepts/silent-failure/)）。

### KRaft

Kafka 4.0（2025 年 3 月）で ZooKeeper のサポートが削除され、メタデータを Kafka 自身が管理する KRaft が唯一の方式になった。`--zookeeper` オプションなど古い手順は 4.x では使えない。ZooKeeper で動く既存クラスターは、3.x（推奨は 3.9 系）のうちに KRaft へ移行してから 4.x に上げる。

### AWS のマネージドサービスとの対応

| サービス | 位置づけ |
|---|---|
| Amazon MSK | Kafka そのもののマネージド版。プロビジョニング型とサーバーレス型（IAM 認証必須） |
| MSK Connect | Kafka Connect のマネージド版。Debezium を載せられる |
| Kinesis Data Streams | AWS 独自のストリーム。Kafka API 非互換。シャード ≈ パーティション |
| AWS DMS | CDC を Kinesis や MSK に流せる（MSK のサーバーレス型は非対応） |
| SNS / SQS | 読み直しの要らない通知・キュー |

### 使わなくてよい場面

読み手が 1 種類で処理後に捨ててよいなら、DB のキューテーブル（`SELECT ... FOR UPDATE SKIP LOCKED`）、[Redis](/blogs/wiki/tools/redis/) Streams、SQS で足りる。Kafka が効くのは、同じイベントを複数の用途で読む、後から読み直す、CDC で DB の変更を流す、1 台で受けきれない件数を水平に広げる、といった場面。Kafka 4.2 ではキューとして使えるシェアグループ（KIP-932）も本番利用可能になった。

## 関連ページ

- [RAG](/blogs/wiki/concepts/rag/) — CDC で鮮度を保つ対象のナレッジベース
- [Redis](/blogs/wiki/tools/redis/) — Streams が軽い代替になる
- [Apache Spark](/blogs/wiki/tools/apache-spark/) — Structured Streaming で Kafka を読む
- [Apache Airflow](/blogs/wiki/tools/apache-airflow/) — イベント駆動ではなく定時バッチで同期する場合の選択肢
- [沈黙する失敗](/blogs/wiki/concepts/silent-failure/) — CDC が止まっても気づけない問題
- [レイクハウス](/blogs/wiki/concepts/lakehouse/) — CDC の流し先の 1 つ

## ソース記事

- [Apache Kafka 入門：トピック・パーティション・コンシューマーグループから CDC まで](/blogs/posts/2026/11/apache-kafka-intro/) — 2026-11-20
- [AI エンジニアこそデータエンジニアリングを学ぶべき理由：RAG のデモが本番で崩れるところ](/blogs/posts/2026/11/data-engineering-for-ai-engineers/) — 2026-11-19
