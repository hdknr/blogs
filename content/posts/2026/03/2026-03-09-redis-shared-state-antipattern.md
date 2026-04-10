---
title: "Redisを「共有状態」として使うアンチパターン：キー設計の落とし穴"
date: 2026-03-09
lastmod: 2026-03-09
slug: "redis-shared-state-antipattern"
draft: false
source_url: "https://github.com/hdknr/blogs/issues/1#issuecomment-4022716816"
categories: ["データベース"]
tags: ["redis"]
---

Redis はキャッシュとして非常に優秀なツールだが、複数のチームやサービスが**共有状態（shared state）**として Redis を使い始めると、設計上の問題が発生しやすくなる。

## キャッシュと共有状態の違い

Redis をキャッシュとして使う場合、データは一時的なものであり、いつ消えても問題ない。元データは RDB などに存在し、キャッシュミス時に再構築できる。

一方、共有状態として使う場合は話が変わる。複数のサービスが同じ Redis キーを読み書きし、そのデータが「正」として扱われる。RDB のようなスキーマや制約がないため、以下の問題が起きやすい。

## 暗黙の契約に依存したデータ構造

RDB であればスキーマによってデータ構造が明示的に定義される。カラム名、型、制約、外部キーなどが設計書の役割を果たす。

Redis にはそのような仕組みがない。キーの命名規則やデータ形式は開発者間の「暗黙の契約」に依存する。チームが増えると、以下のような問題が顕在化する：

- **キーの命名が衝突する** — 異なるチームが同じプレフィックスを使ってしまう
- **データ形式の不一致** — あるサービスは JSON、別のサービスは MessagePack で書き込む
- **バージョン管理の欠如** — データ構造を変更しても、読み取り側が追従できない

## 「削除できないキー」問題

最も厄介な問題の一つが、**誰が所有しているのか分からないキー**が残り続けることだ。

本番環境で以下のような状況が発生する：

```
# このキーは誰が作った？いつ expire する？削除していい？
GET user:session:abc123:metadata
```

- 作成したサービスがすでに廃止されている
- TTL が設定されていないため、永遠に残る
- 他のサービスが依存している可能性があり、安易に削除できない

## キーを「パブリック API」として扱う

この問題に対する実践的なアプローチとして、**Redis キーをパブリック API のように扱う**という考え方がある：

1. **バージョニング** — キー名にバージョンを含める（例: `v2:user:session:{id}`）
2. **ドキュメント化** — どのキーがどのサービスによって管理されているかを明文化する
3. **オーナーの明確化** — 各キーに責任を持つチーム・サービスを割り当てる
4. **TTL の必須化** — 共有キーには必ず TTL を設定し、期限切れを明示する

## 補足：分散ロック基盤としての Redis

Redis を共有状態として使うもう一つの典型例が、**トランザクション境界をまたぐ分散ロック**だ。`SET key value NX PX timeout` を使ったロックや、Redlock アルゴリズムは広く利用されているが、ここにも落とし穴がある。

### ロックが「破られる」パターン

分散ロックで最も危険なのは、**ロック保持者がロックを持っていると信じているが、実際には期限切れになっている**状況だ：

```
処理A: ロック取得（TTL=10秒）
処理A: 長時間の処理 or GC pause で 10秒超過
        → ロック自動解放
処理B: ロック取得（成功してしまう）
処理A: まだロックを持っていると思って書き込み
処理B: 同時に書き込み → データ不整合
```

Martin Kleppmann は「[How to do distributed locking](https://martin.kleppmann.com/2016/02/08/how-to-do-distributed-locking.html)」でこの問題を詳細に分析し、Redis ベースの分散ロックの限界を指摘している。

### 「効率性」と「正確性」の使い分け

Redis ロックの適切な使い方は、ロックの目的によって異なる：

- **効率性のためのロック**（重複処理の回避など）— Redis で十分。最悪2重実行されても致命的でない場合に使う
- **正確性のためのロック**（データ整合性の厳密な保証）— Redis 単体では不十分な場合がある

### フェンシングトークンによる対策

正確性が求められる場合は、**フェンシングトークン（fencing token）**を併用する。フェンシングトークンとは、ロックサービスがロックを付与するたびに発行する**単調増加する数値**だ。

#### なぜロックだけでは不十分なのか

分散システムでは、ロックを取得したクライアントが「自分はロックを持っている」と信じていても、実際にはロックが期限切れになっているケースを完全には防げない。GC pause、ネットワーク遅延、プロセスのスワップアウトなど、クライアント側の停止はいつでも起こりうる。

ロックサービスが「ロックは1つのクライアントにしか渡さない」ことを保証しても、**クライアントがロックの有効性を確認してから実際に書き込むまでの間**にロックが失効する可能性がある。この時間差を完全にゼロにすることはできない。

#### フェンシングトークンの仕組み

フェンシングトークンは、この問題をデータストア側で解決する：

```
時刻 1: クライアント A がロック取得 → トークン 33 を受け取る
時刻 2: クライアント A が GC pause に入る
時刻 3: ロックの TTL が切れる
時刻 4: クライアント B がロック取得 → トークン 34 を受け取る
時刻 5: クライアント B がトークン 34 でデータストアに書き込み → 成功
時刻 6: クライアント A が復帰、トークン 33 で書き込み → 拒否される
```

ポイントは、**データストア側が「受け付けた最大のトークン番号」を記録し、それより小さいトークンの書き込みを拒否する**ことだ。これにより、ロックが二重に取得されても、古いロック保持者の書き込みが後から到着してデータを破壊することを防げる。

#### 実装パターン

フェンシングトークンの発行方法はロックサービスによって異なる：

| ロックサービス | トークンの取得方法 |
|---|---|
| ZooKeeper | シーケンシャルノードの `czxid`（トランザクション ID） |
| etcd | リビジョン番号（単調増加が保証される） |
| Redis + 自前実装 | `INCR` コマンドで別キーのカウンターをインクリメント |

#### Redis + 自前実装の例

Redis でフェンシングトークンを実現するには、ロック取得とトークン発行を**アトミックに**行う必要がある。Lua スクリプトを使えば、2つの操作を1回の呼び出しで実行できる：

```lua
-- lock_with_token.lua
-- ロック取得とフェンシングトークン発行をアトミックに行う
local lock_key = KEYS[1]
local token_key = KEYS[2]       -- "fence:" .. resource_name
local client_id = ARGV[1]
local ttl_ms = ARGV[2]

-- ロック取得を試みる（NX = 存在しない場合のみ）
local ok = redis.call('SET', lock_key, client_id, 'NX', 'PX', ttl_ms)
if not ok then
    return nil  -- ロック取得失敗
end

-- トークンをインクリメントして返す
local token = redis.call('INCR', token_key)
return token
```

Python での利用例：

```python
import redis
import uuid

r = redis.Redis()

LOCK_SCRIPT = """
local lock_key = KEYS[1]
local token_key = KEYS[2]
local client_id = ARGV[1]
local ttl_ms = ARGV[2]

local ok = redis.call('SET', lock_key, client_id, 'NX', 'PX', ttl_ms)
if not ok then
    return nil
end

local token = redis.call('INCR', token_key)
return token
"""

lock_with_token = r.register_script(LOCK_SCRIPT)


def acquire_lock(resource, ttl_ms=10000):
    client_id = str(uuid.uuid4())
    token = lock_with_token(
        keys=[f"lock:{resource}", f"fence:{resource}"],
        args=[client_id, ttl_ms],
    )
    if token is None:
        return None, None
    return client_id, int(token)


def process_order(order_id):
    client_id, token = acquire_lock(f"order:{order_id}")
    if token is None:
        raise Exception("ロック取得失敗")

    # データストア側でトークンを検証して書き込む
    cursor.execute(
        """
        UPDATE orders
        SET status = 'confirmed', fence_token = %s
        WHERE order_id = %s AND fence_token < %s
        """,
        (token, order_id, token),
    )

    if cursor.rowcount == 0:
        # より新しいトークンで既に更新済み → 自分の処理は無効
        raise Exception("フェンシングトークン検証失敗：古いロック")
```

この実装のポイント：

- **Lua スクリプトでアトミック化** — `SET NX` と `INCR` を1回の呼び出しで実行し、ロック取得とトークン発行の間に他のクライアントが割り込む隙をなくす
- **トークンキーに TTL を設定しない** — `fence:{resource}` は単調増加を保つために永続化する（リセットすると安全性が崩れる）
- **検証はデータストア側** — Redis 側ではなく、最終的な書き込み先（RDB 等）で `fence_token < ?` を条件にする

#### django-redis の lock はフェンシングトークンを提供しない

Django プロジェクトでは [django-redis](https://github.com/jazzband/django-redis) の `cache.lock()` が手軽に使える：

```python
from django.core.cache import cache

with cache.lock("my-resource"):
    do_something()
```

しかし、この `lock()` の内部実装は以下のように委譲されるだけだ：

```
django-redis cache.lock()
  → redis-py client.lock()
    → Redis SET key <UUID> NX PX <timeout>
```

redis-py の `Lock` クラスは UUID（ランダム値）をトークンとして使用する。これはロック解放時に「自分が取得したロックだけを解放する」ための所有者検証には有効だが、**単調増加する値ではない**ため、データストア側で「どちらの書き込みが新しいか」を判定できない。

つまり、django-redis の lock が**解決する**のは：

- 他のクライアントのロックを誤って解放する問題
- スレッド間の誤操作（`thread_local=True`）

django-redis の lock が**解決しない**のは：

- TTL 切れによる二重取得後のデータ不整合
- GC pause 後に古いロック保持者が書き込みを行う問題

Django プロジェクトで正確性が求められる場合は、前述の Lua スクリプトによる自前実装でフェンシングトークンを発行するか、`SELECT ... FOR UPDATE` のようなデータベースレベルのロックを検討する必要がある。

#### Redlock の限界

Redis の Redlock アルゴリズムにはフェンシングトークンを生成する仕組みが組み込まれていない。`INCR` コマンドで自前のカウンターを用意することは可能だが、Redlock 自体の設計にはトークンの単調増加を保証するメカニズムがない。これが Kleppmann が指摘する Redlock の根本的な限界の一つだ。

正確性が重要なユースケースでは、ZooKeeper や etcd のようにトークンの単調増加をプロトコルレベルで保証する合意システムの利用が推奨される。

#### フェンシングトークンの限界

フェンシングトークンも万能ではない。データストア側がトークンの検証に対応している必要があり、外部 API の呼び出しやメール送信のような**副作用のある操作**にはフェンシングトークンを適用できない。このような場合は、冪等キーや二相コミットなど、別のアプローチが必要になる。

Redis のロックは「ベストエフォート」であり、RDB のトランザクション分離レベルのような厳密な保証を提供するものではない。**最悪ロックが破られた場合にどうなるか**を設計時に考慮し、フェンシングトークンや冪等性の仕組みを併用するのが定石だ。

## まとめ

Redis は高速で柔軟なツールだが、その柔軟さゆえに「なんでも入れられる共有ストレージ」として使われがちだ。キャッシュとして使う分には問題ないが、共有状態や分散ロックとして使う場合は、それぞれ固有のリスクを理解した上での設計規律が求められる。

キーの命名規則、所有者、TTL、データ形式を明文化し、パブリック API と同じレベルで管理すること。分散ロックでは「ロックが破られる前提」で冪等性やフェンシングトークンを併用すること。これらが Redis を安全に運用するための鍵となる。

## 参考

- [Redis Anti-Patterns Every Developer Should Avoid](https://redis.io/learn/howtos/antipatterns) — Redis 公式のアンチパターン集
- [Distributed Locks with Redis](https://redis.io/docs/latest/develop/use/patterns/distributed-locks/) — Redis 公式の分散ロックパターン
- [How to do distributed locking](https://martin.kleppmann.com/2016/02/08/how-to-do-distributed-locking.html) — Martin Kleppmann による Redlock 批判
