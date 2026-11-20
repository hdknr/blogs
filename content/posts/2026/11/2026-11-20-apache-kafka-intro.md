---
title: "Apache Kafka 入門：トピック・パーティション・コンシューマーグループから CDC まで"
description: "Apache Kafka 入門。トピック・パーティション・コンシューマーグループ、配信保証、KRaft、Debezium による CDC、Python の最小コード、Kafka が要らない場面（DB キュー・Redis Streams・SQS）までを整理します。"
date: 2026-11-20
lastmod: 2026-11-20
slug: "apache-kafka-intro"
draft: false
categories: ["AI/LLM"]
tags: ["Apache Kafka", "データエンジニアリング", "データ基盤", "CDC", "Debezium", "RAG", "python"]
---

## はじめに

[AI エンジニアこそデータエンジニアリングを学ぶべき理由](/blogs/posts/2026/11/data-engineering-for-ai-engineers/)では、データエンジニアリングの主要な道具が解く問題を 1 行ずつ並べました。Apache Kafka の行は「発生し続けるイベントをどう確実に受け渡し、消費するか」です。

この記事は、その 1 行を入門レベルまで掘り下げます。対象は、Kafka という名前は知っているけれど触ったことはない、アプリケーションや AI システムを作るエンジニアです。2026 年 11 月時点の最新系列は Kafka 4.4（4.4.0 は 2026 年 10 月リリース）で、記事の説明とコードはこれを前提にしています。

この記事で分かること:

- Kafka が解く問題と、トピック・パーティション・コンシューマーグループの基本
- 配信保証（at-least-once・冪等プロデューサー・exactly-once）とその限界
- Debezium による CDC で、業務 DB の変更を検索や RAG に流す構成
- Kafka を入れなくてよい場面（DB のキューテーブル・Redis Streams・SQS）

## 用語とプロダクト

先に、この記事で使う言葉をまとめておきます。

| 用語・プロダクト | 意味 |
|---|---|
| Apache Kafka | イベントを追記型のログとして保存し、複数の読み手に配る分散ストリーミング基盤 |
| ブローカー（broker） | Kafka のサーバー 1 台。複数台でクラスターを組み、データを複製して持つ |
| トピック（topic） | イベントの種類ごとの置き場所。`orders`、`user-signups` のように名前を付ける |
| パーティション（partition） | トピックを分割した単位。追記専用のログで、並列処理と順序保証の単位になる |
| オフセット（offset） | パーティション内のレコードに振られる連番。「どこまで読んだか」を表す |
| オフセットのコミット | 「ここまで処理した」という位置を Kafka に記録すること。再起動後はその続きから読む |
| プロデューサー（producer） | トピックにレコードを書き込むクライアント |
| コンシューマー（consumer） | トピックからレコードを読むクライアント |
| コンシューマーグループ（consumer group） | 同じ用途で読むコンシューマーの集まり。パーティションを分担し、読んだ位置をグループ単位で記録する |
| 冪等（べきとう） | 同じ操作を何回行っても、1 回行ったときと結果が変わらない性質 |
| KRaft | Kafka 自身がメタデータを管理する方式。Raft（複数のノードで多数決を取り、正しい状態を決める合意アルゴリズム）を基にしている |
| KIP | Kafka Improvement Proposal。Kafka の機能提案で、番号で呼ばれる |
| Kafka Connect | 外部システムと Kafka をつなぐ枠組み。取り込み側をソースコネクター、書き出し側をシンクコネクターと呼ぶ |
| Debezium | DB の変更ログを読み、行の変更をイベントとして Kafka に流す CDC 用のコネクター群 |
| CDC（Change Data Capture） | DB に起きた変更（挿入・更新・削除）を取り出して、別のシステムへ伝える手法 |

## Kafka が解く問題：イベントを複数の読み手に確実に配る

業務システムでは、注文、決済、在庫の増減、ログイン、センサーの値といったイベントが絶え間なく発生します。そして 1 つのイベントを使いたい相手は 1 つとは限りません。注文 1 件だけでも、在庫の引き当て、メール送信、検索インデックスの更新、分析基盤への転送、RAG 用ベクトル DB の更新と、使う処理が 5 つあります。

これをアプリケーションから各相手へ直接送ると、次の問題が出てきます。

- 送り先が 1 つ増えるたびに、送る側のコードを直す必要がある
- 送り先の 1 つが止まっていると、送る側が待たされるか、イベントを取りこぼす
- 新しく作った処理に「過去 1 週間分のイベント」を流したくても、もう残っていない

Kafka は、イベントを**順番付きのログとして一定期間ディスクに残し、読み手がそれぞれ自分のペースで、自分の位置から読む**という形でこれを解きます。書き手は Kafka に書くだけで、誰が読むかを知りません。読み手が止まっていても、ログは残っているので再開すれば続きから読めます。

## トピック・パーティション・オフセット

![プロデューサーが注文 ID をキーにしてトピック orders へ書き込み、トピックは 3 つのパーティションに分かれてそれぞれ 0 から始まるオフセットで末尾に追記される。検索インデックス更新用のコンシューマーグループ A では 2 台のコンシューマーがパーティションを分担し、分析基盤への転送用のグループ B では 1 台が全パーティションを読む様子を示した図](/blogs/images/apache-kafka-intro-topic-partition.png)

トピックは 1 つ以上のパーティションに分かれます。パーティションは追記専用のログで、書き込まれたレコードには 0 から順にオフセットが振られます。レコードは読まれても消えません。

プロデューサーがレコードにキーを付けると、同じキーのレコードは同じパーティションに入ります（パーティション数を変えない限り）。Kafka が順序を保証するのは**パーティションの中だけ**です。トピック全体での順序は保証されません。注文 ID をキーにしておけば、「作成 → 支払い → 発送」という同じ注文のイベントは書いた順に読めます。

パーティションはブローカーをまたいで配置され、それぞれが複数のブローカーに複製（レプリケーション）されます。これにより、1 台が落ちてもデータを失わずに読み書きを続けられます。

## コンシューマーグループ：分担と独立した読み取り

コンシューマーは通常、どこかのコンシューマーグループに属して読みます（グループを使わずにパーティションを直接指定して読む方法もありますが、ここでは扱いません）。パーティションは並列処理の単位でもあり、グループの中ではこれを分担します。

- **グループの中では分担する**：1 つのパーティションは、グループ内の 1 台のコンシューマーにだけ割り当てられる。処理が追いつかなければコンシューマーを足せばよい。ただしパーティション数より多く足しても、余ったコンシューマーには何も割り当てられず待機するだけになる
- **グループどうしは独立している**：グループ A とグループ B は同じトピックを別々に全件読む。読んだ位置（コミット済みオフセット）もグループごとに記録される

コンシューマーの参加・離脱に合わせてパーティションの割り当てをやり直すことを**リバランス**と呼びます。Kafka 4.0 では、この割り当てをブローカー側で行う新しいコンシューマーグループのプロトコル（KIP-848）が一般提供（GA）になりました。クライアントで `group.protocol=consumer` を指定すると使えます。

新しい用途を足すときは、新しいグループ名で読み始めるだけで済みます。書き手のコードにも、既存の読み手にも手を入れる必要はありません。

## 保持期間と再読み込み

Kafka はレコードを読まれたかどうかに関係なく、トピックごとの保持設定に従って残します。ブローカーの既定値は 7 日（`log.retention.hours=168`）で、トピック単位で変えられます。

| 保持の方式 | 設定 | 向いている用途 |
|---|---|---|
| 期間・サイズで削除 | `cleanup.policy=delete`、`retention.ms`、`retention.bytes` | イベントの履歴（注文、クリック、ログ） |
| キーごとに最新だけ残す（ログコンパクション） | `cleanup.policy=compact` | 「顧客 ID ごとの最新の状態」のような変更履歴。CDC と相性がよい |

レコードが残っている限り、コンシューマーは読む位置を巻き戻せます。バグのあった処理を直して過去分を再処理する、新しく作った埋め込みモデルでベクトル DB を作り直す、といった作業が、元の DB に負荷をかけずにできます。巻き戻しの具体的なコマンドは、後の「Python で動かしてみる」で示します。

## 配信保証：at-least-once・冪等プロデューサー・exactly-once

分散システムでは、ネットワークの切断や再起動のたびに「送れたのか、送れなかったのか」が分からない瞬間が生まれます。Kafka の配信保証は、その瞬間にどちらへ倒すかの選択です。

| 保証 | 意味 | 典型的な実現方法 |
|---|---|---|
| at-most-once | 失われることはあるが、重複はしない | 処理する前にオフセットをコミットする |
| at-least-once | 失われないが、重複することがある | 処理が終わってからオフセットをコミットする。実務の基本形 |
| exactly-once | 失われず、重複もしない（ように見える） | 冪等プロデューサー + トランザクション + `isolation.level=read_committed` |

### 冪等プロデューサー

プロデューサーが送信をリトライすると、1 回目が実は届いていた場合に同じレコードが 2 回書かれます。**冪等プロデューサー**（`enable.idempotence=true`）は、送信ごとにプロデューサー ID とシーケンス番号を付けます。ブローカーはこれを見て重複を捨てるので、パーティション内の順序も保たれます。Java クライアントでは Kafka 3.0 から `enable.idempotence=true` と `acks=all` が既定値になりました。

ただし、Python の `confluent-kafka` などが使う C ライブラリ librdkafka では、`enable.idempotence` の既定値は今も `false` です。使うクライアントの既定値は、言語ごとに確認しておく必要があります。

### exactly-once の範囲

Kafka のトランザクションを使うと、「トピック A から読み、加工してトピック B に書き、読んだ位置をコミットする」までを 1 つの単位にできます。読み手が `read_committed` で読めば、途中で失敗したトランザクションの書き込みは見えません。これが Kafka の exactly-once です。

ただし、この保証が効くのは**Kafka の中で読み書きが完結する場合**です。たとえば、コンシューマーが外部のベクトル DB に書いた直後、オフセットをコミットする前に落ちたとします。再起動すると、同じレコードをもう一度処理します。外部へ書く処理は、次のどちらかで重複に耐えるようにしておくのが定石です。

- ドキュメント ID をレコードのキー（注文 ID など）から決め、upsert（あれば更新、なければ挿入）で書く
- 処理済みのオフセットを書き込み先と同じトランザクションで保存する

つまり、Kafka を入れたから重複が消えるわけではありません。データエンジニアリングの記事で挙げた「同期処理が途中で落ちて再実行したとき、重複データが生まれないか」という問いは、Kafka を使っても読み手の設計として残ります。

## CDC：業務 DB と検索・RAG をつなぐ

AI エンジニアが Kafka に出会う場面で多いのが CDC です。

RAG のナレッジベースを業務 DB に合わせて更新し続けたいとき、素朴な方法は「夜間に全件をエクスポートして入れ直す」か「`updated_at` が前回以降の行を定期的に取りに行く」です。前者は鮮度が 1 日遅れ、後者は削除された行を拾えません。

CDC は、DB が内部に持つ変更ログ（PostgreSQL の WAL、MySQL の binlog など）を読み、挿入・更新・削除をすべてイベントとして取り出します。**Debezium** はこれを Kafka Connect のソースコネクターとして実装したもので、テーブルごとのトピックに行の変更前・変更後の値を書き込みます。

![業務 DB（PostgreSQL や MySQL）の変更ログを Kafka Connect 上の Debezium ソースコネクターが読み取り、テーブルごとのトピックに挿入・更新・削除のイベントとして書き込む。そこから検索エンジン向けのシンクコネクター、ベクトル DB を更新する埋め込みワーカー、DWH やレイクハウス向けのシンクコネクターがそれぞれ独立に読む構成を示した図](/blogs/images/apache-kafka-intro-cdc-pipeline.png)

この構成には、次の利点があります。

- **削除を拾える**：削除もイベントとして届くので、退職者の資料や取り消された契約書を RAG のインデックスから消せる
- **読み手を足しても DB の負荷が増えない**：検索、ベクトル DB、分析基盤がそれぞれ別のグループで Kafka を読む。業務 DB から読むのは Debezium だけ
- **作り直せる**：ログコンパクションしたトピックや保持期間内のイベントから、インデックスを一から作り直せる

一方で、CDC は DB の変更ログという内部の仕組みに依存します。DB のバージョンアップやフェイルオーバーで変更ログの位置が変わると、取り込みが止まったり欠けたりします。筆者の環境で AWS DMS の CDC が RDS の Blue/Green 切替後に静かに止まっていた事例は、[RDS の Blue/Green 切替で DMS が静かに死んだ話](/blogs/posts/2026/08/rds-blue-green-dms-cdc-incident/)に書きました。Debezium でも、コネクターが動いているか、取り込みがどれだけ遅れているかを監視しておく必要があります。

## KRaft：ZooKeeper が要らなくなった

かつての Kafka は、クラスターのメタデータ（どのブローカーがどのパーティションを持つか、など）の管理を別のシステムである Apache ZooKeeper に任せていました。Kafka を動かすには、ZooKeeper のクラスターも別に運用する必要があったのです。

**KRaft** は、このメタデータ管理を Kafka 自身のコントローラーが行う方式です。2025 年 3 月リリースの Kafka 4.0 で ZooKeeper のサポートは削除され、KRaft が唯一の方式になりました。

これから Kafka を始めるなら、ZooKeeper について学ぶ必要はありません。古い記事に出てくる `--zookeeper` オプションや ZooKeeper の構築手順は、4.x では使えないと考えてください。ZooKeeper で動いている既存のクラスターは、3.x のうちに KRaft へ移行してから 4.x に上げる必要があります。移行の足場には 3.9 系を使うことが推奨されています。

なお 4.0 からは、ブローカー・Connect・ツール類に Java 17 以上、クライアントと Kafka Streams に Java 11 以上が必要です。

## Python（confluent-kafka）と Docker で動かしてみる

手元で試すなら、公式の Docker イメージで KRaft モードのブローカーを 1 台起動するのが手軽です。

```bash
docker run -d --name kafka -p 9092:9092 apache/kafka:4.4.0
```

パーティションを 3 つ持つトピックを作ります。ブローカーの起動には数秒かかるので、エラーが出たら少し待ってからやり直してください。

```bash
docker exec kafka /opt/kafka/bin/kafka-topics.sh \
  --bootstrap-server localhost:9092 \
  --create --topic orders --partitions 3 --replication-factor 1
```

Python のクライアントには `confluent-kafka` を使います。

```bash
pip install confluent-kafka
```

プロデューサーは注文 ID をキーにして書き込みます。前述のとおり librdkafka では冪等性が既定で無効なので、明示的に有効にします。

```python
# producer.py
import json
from confluent_kafka import Producer

producer = Producer({
    "bootstrap.servers": "localhost:9092",
    "enable.idempotence": True,  # librdkafka では既定値が false
})

def on_delivery(err, msg):
    if err:
        print(f"送信失敗: {err}")
    else:
        print(f"送信成功: partition={msg.partition()} offset={msg.offset()}")

for order_id, status in [("A-1", "created"), ("A-2", "created"), ("A-1", "paid")]:
    producer.produce(
        "orders",
        key=order_id,
        value=json.dumps({"order_id": order_id, "status": status}),
        on_delivery=on_delivery,
    )

producer.flush()
```

コンシューマーは自動コミットを切り、処理が終わってからオフセットをコミットします。これで at-least-once になります。グループ名はコマンドライン引数で受け取ります。

```python
# consumer.py
import json
import sys
from confluent_kafka import Consumer

group_id = sys.argv[1] if len(sys.argv) > 1 else "search-indexer"

consumer = Consumer({
    "bootstrap.servers": "localhost:9092",
    "group.id": group_id,
    "auto.offset.reset": "earliest",  # コミット済みの位置がなければ先頭から
    "enable.auto.commit": False,
})
consumer.subscribe(["orders"])

def upsert_to_index(doc_id: str, doc: dict) -> None:
    # 実際は検索エンジンやベクトル DB に doc_id をキーにして upsert する。
    # 同じレコードを 2 回処理しても結果が変わらないようにしておく
    print(f"[{group_id}] upsert {doc_id}: {doc}")

try:
    while True:
        msg = consumer.poll(1.0)
        if msg is None:
            continue
        if msg.error():
            print(f"エラー: {msg.error()}")
            continue
        doc = json.loads(msg.value())
        upsert_to_index(msg.key().decode(), doc)
        consumer.commit(message=msg, asynchronous=False)
finally:
    consumer.close()
```

ターミナルを 2 つ開き、片方でコンシューマーを起動してから、もう片方でプロデューサーを実行します。コンシューマーは無限ループなので、Ctrl+C で止めます。

```bash
python consumer.py
```

```bash
python producer.py
```

出力は次のようになります（パーティション番号とオフセットは環境によって変わります）。

```text
送信成功: partition=1 offset=0
送信成功: partition=1 offset=1
送信成功: partition=0 offset=0
```

```text
[search-indexer] upsert A-1: {'order_id': 'A-1', 'status': 'created'}
[search-indexer] upsert A-1: {'order_id': 'A-1', 'status': 'paid'}
[search-indexer] upsert A-2: {'order_id': 'A-2', 'status': 'created'}
```

`A-1` の 2 件は同じパーティションに入るので、`created` → `paid` の順で届きます。`A-2` は別のパーティションに入るので、`A-1` との前後関係は保証されません。

続けて `python consumer.py analytics` で別のグループのコンシューマーを起動すると、同じ 3 件をもう一度先頭から読むことが確かめられます。

読む位置の巻き戻しも試せます。`search-indexer` グループのコンシューマーを止めてから、次のコマンドでオフセットを先頭に戻します（`--execute` を付けないと、変更内容を表示するだけで実行されません）。

```bash
docker exec kafka /opt/kafka/bin/kafka-consumer-groups.sh \
  --bootstrap-server localhost:9092 \
  --group search-indexer --topic orders \
  --reset-offsets --to-earliest --execute
```

もう一度 `python consumer.py` を起動すると、3 件が最初から再処理されます。試し終わったら、ブローカーを削除しておきます。

```bash
docker rm -f kafka
```

## Kafka が要らない場面：キューテーブル・Redis Streams・SQS との使い分け

Kafka は便利ですが、ブローカーの台数とディスク、パーティション数の設計、レプリケーション、監視、バージョンアップなど、運用で気にすることが増えます。マネージドサービス（Amazon MSK、Confluent Cloud など）を使っても、パーティションやコンシューマーの設計は利用者側に残ります。次のような場合は、もっと軽い選択肢で足ります。

| 選択肢 | 向いている場面 | Kafka との違い |
|---|---|---|
| DB のキューテーブル | すでに PostgreSQL や MySQL があり、ジョブの件数が多くない | `SELECT ... FOR UPDATE SKIP LOCKED` で複数のワーカーが行を取り合わずに処理できる。業務データの更新とジョブの登録を同じトランザクションにできるのが大きな利点 |
| Redis Streams | すでに Redis を運用しており、低遅延で配りたい | `XADD` で追記し、コンシューマーグループと `XACK` で処理済みを管理できる。データは基本的にメモリ上にあるので、長期間の保持や大量の再読み込みには向かない |
| Amazon SQS | AWS 上で、ジョブを確実にワーカーへ渡したい | サーバーの運用が不要。処理が終わったメッセージは削除されるので、別の用途で後から読み直すことはできない |

判断の目安は次のとおりです。

- **読み手が 1 種類で、処理し終わったら捨ててよい**：キューテーブルか SQS で足りる
- **同じイベントを複数の用途で読みたい、後から読み直したい、DB の変更を CDC で流したい**：Kafka が効いてくる
- **1 秒あたりの件数が多く、1 台では受けきれない**：パーティションで水平に広げられる Kafka が向く

なお、Kafka 側も「キューとしての使い方」に近づいています。Kafka 4.2 では**シェアグループ**（KIP-932、Queues for Kafka）が本番で使えるようになりました。パーティション数に縛られず、複数のコンシューマーがレコード単位で取り合える仕組みです。とはいえ、キューだけが欲しいなら、まず手元にある DB や Redis で足りないかを考えるのが先です。

Redis Streams を使った配信基盤の事例は、[Redis Pub/Sub から Streams への移行で帯域 99% 削減](/blogs/posts/2026/03/92ce5b95cd28ffb9ca25100b1991d6d3/)で紹介しています。Redis そのものについては [wiki の Redis のページ](/blogs/wiki/tools/redis/)にまとめています。

## まとめ

- Kafka は、イベントを順番付きのログとして一定期間残し、複数の読み手がそれぞれの位置から読む仕組み。書き手は読み手を知らなくてよい
- 順序が保証されるのはパーティションの中だけ。順序が要るイベントは同じキーで書く
- コンシューマーグループの中ではパーティションを分担し、グループどうしは独立に全件を読む
- 保持期間内なら読む位置を巻き戻して再処理でき、ベクトル DB や検索インデックスを作り直せる
- 実務の基本は at-least-once。冪等プロデューサーで書き込みの重複は防げるが、外部システムへの書き込みは upsert などで重複に耐える設計が要る
- Debezium による CDC は、業務 DB の変更（削除を含む）を検索や RAG のインデックスへ流す定番の構成
- 4.0 で ZooKeeper は削除され、KRaft が唯一の方式になった
- 読み手が 1 種類で捨ててよいなら、DB のキューテーブル、Redis Streams、SQS で足りることが多い

## 関連記事

- [AI エンジニアこそデータエンジニアリングを学ぶべき理由：RAG のデモが本番で崩れるところ](/blogs/posts/2026/11/data-engineering-for-ai-engineers/)
- [RDS の Blue/Green 切替で DMS が静かに死んだ話 — 18日間気付かなかった監視の三重の穴](/blogs/posts/2026/08/rds-blue-green-dms-cdc-incident/)
- [Redis Pub/Sub から Streams への移行で帯域 99% 削減 --- 同時接続 30 万超チャットの実践記録](/blogs/posts/2026/03/92ce5b95cd28ffb9ca25100b1991d6d3/)
- [Iceberg と DuckLake の先へ：2026 年に注目したいレイクハウスの技術とプロダクト](/blogs/posts/2026/10/lakehouse-ecosystem-2026/)
- [wiki: RAG (Retrieval-Augmented Generation)](/blogs/wiki/concepts/rag/)
- [wiki: Redis](/blogs/wiki/tools/redis/)

## 参考資料

- [Apache Kafka 4.0.0 Release Announcement](https://kafka.apache.org/blog/2025/03/18/apache-kafka-4.0.0-release-announcement/)
- [Apache Kafka 4.2.0 Release Announcement](https://kafka.apache.org/blog/2026/02/17/apache-kafka-4.2.0-release-announcement/)
- [Apache Kafka 4.4.0 Release Announcement](https://kafka.apache.org/blog/2026/10/22/apache-kafka-4.4.0-release-announcement/)
- [Apache Kafka Documentation](https://kafka.apache.org/documentation/)
- [KIP-679: Producer will enable the strongest delivery guarantee by default](https://cwiki.apache.org/confluence/spaces/KAFKA/pages/165221843/KIP-679+Producer+will+enable+the+strongest+delivery+guarantee+by+default)
- [Debezium](https://debezium.io/)
- [librdkafka CONFIGURATION.md](https://github.com/confluentinc/librdkafka/blob/master/CONFIGURATION.md)
