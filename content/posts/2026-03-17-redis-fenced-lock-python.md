---
title: "redis-py の Lock をサブクラス化してフェンシングトークンを実装する"
date: 2026-03-17
lastmod: 2026-03-17
draft: false
categories: ["データベース"]
tags: ["redis", "python", "django"]
---

redis-py の `Lock` クラスは UUID ベースのトークンでロックの所有権を管理するが、フェンシングトークン（単調増加する数値）は提供しない。しかし、`Lock` クラスは `do_acquire` や Lua スクリプトをオーバーライドできる設計になっており、サブクラス化でフェンシングトークンを追加できる。

本記事では、redis-py の `Lock` を拡張してフェンシングトークンを発行する `FencedLock` クラスの実装例を紹介する。

## redis-py の Lock のカスタマイズポイント

redis-py の [`Lock` クラス](https://redis.readthedocs.io/en/stable/_modules/redis/lock.html)は、以下のメソッドをオーバーライドすることでカスタマイズできる：

| メソッド | 役割 |
|---|---|
| `do_acquire(token)` | 実際のロック取得処理（`SET NX PX`） |
| `do_release(expected_token)` | Lua スクリプトによるロック解放 |
| `do_extend(additional_time, replace_ttl)` | TTL の延長 |

通常の `do_acquire` は UUID トークンを `SET key <uuid> NX PX <timeout>` で書き込むだけだ。ここにフェンシングトークンの発行を追加する。

## FencedLock の実装

```python
import redis
from redis.lock import Lock


class FencedLock(Lock):
    """フェンシングトークン付き分散ロック。

    redis-py の Lock をサブクラス化し、ロック取得時に
    単調増加するフェンシングトークンを発行する。
    """

    # ロック取得とフェンシングトークン発行をアトミックに行う Lua スクリプト
    LUA_ACQUIRE_AND_FENCE = """
    local lock_key = KEYS[1]
    local fence_key = KEYS[2]
    local token = ARGV[1]
    local timeout = ARGV[2]

    -- ロック取得を試みる（NX = 存在しない場合のみ）
    local ok
    if timeout ~= '' then
        ok = redis.call('SET', lock_key, token, 'NX', 'PX', timeout)
    else
        ok = redis.call('SET', lock_key, token, 'NX')
    end
    if not ok then
        return nil  -- ロック取得失敗
    end

    -- フェンシングトークンをインクリメントして返す
    return redis.call('INCR', fence_key)
    """

    def __init__(self, redis, name, **kwargs):
        super().__init__(redis, name, **kwargs)
        self._fence_key = f"fence:{name}"
        self._fence_token = None
        self._acquire_and_fence = self.redis.register_script(
            self.LUA_ACQUIRE_AND_FENCE
        )

    @property
    def fence_token(self):
        """取得したフェンシングトークンを返す。"""
        return self._fence_token

    def do_acquire(self, token):
        timeout = int(self.timeout * 1000) if self.timeout else ""
        result = self._acquire_and_fence(
            keys=[self.name, self._fence_key],
            args=[token, timeout],
        )
        if result is not None:
            self._fence_token = int(result)
            return True
        return False

    def do_release(self, expected_token):
        # 解放時にフェンシングトークンをクリア
        self._fence_token = None
        super().do_release(expected_token)
```

### 実装のポイント

- **Lua スクリプトでアトミック化** — `SET NX` と `INCR` を1回の EVALSHA で実行する。2つのコマンドを別々に発行すると、ロック取得とトークン発行の間に他のクライアントが割り込む可能性がある
- **フェンスキーに TTL を設定しない** — `fence:{name}` は単調増加を保つために永続化する。TTL を設定すると、キーが消えた時点でカウンターがリセットされ、フェンシングの安全性が崩れる
- **既存の Lock API との互換性** — `do_acquire` をオーバーライドするだけなので、`blocking`, `blocking_timeout`, `thread_local` などの既存オプションはすべてそのまま使える

## 使い方

### 基本的な使用例

```python
r = redis.Redis()

lock = FencedLock(r, "order:1001", timeout=10)
if lock.acquire():
    token = lock.fence_token  # 例: 42
    print(f"ロック取得、フェンシングトークン: {token}")

    # データストア側でトークンを検証して書き込む
    cursor.execute(
        """
        UPDATE orders
        SET status = 'confirmed', fence_token = %s
        WHERE order_id = %s AND fence_token < %s
        """,
        (token, 1001, token),
    )
    if cursor.rowcount == 0:
        print("古いトークン：書き込みスキップ")

    lock.release()
```

### コンテキストマネージャとして使用

```python
with FencedLock(r, "order:1001", timeout=10) as lock:
    token = lock.fence_token
    # ... トークンを使った書き込み処理
```

redis-py の `Lock.__enter__` は `self` を返すため、`with ... as lock` でそのままフェンシングトークンにアクセスできる。

## Django（django-redis）との統合

django-redis の `cache.lock()` は内部で redis-py の `Lock` をそのまま使うため、`FencedLock` を直接差し込むことはできない。代わりに、redis-py のクライアントを直接取得して使う：

```python
from django_redis import get_redis_connection

conn = get_redis_connection("default")

lock = FencedLock(conn, "order:1001", timeout=10)
with lock:
    token = lock.fence_token
    Order.objects.filter(
        id=1001,
        fence_token__lt=token,
    ).update(
        status="confirmed",
        fence_token=token,
    )
```

### モデル側の準備

フェンシングトークンを検証するには、対象テーブルに `fence_token` カラムが必要だ：

```python
class Order(models.Model):
    status = models.CharField(max_length=20)
    fence_token = models.BigIntegerField(default=0)
```

## 注意点と限界

### フェンスキーの永続化

`fence:{name}` キーは Redis の永続化設定（RDB スナップショットや AOF）に依存する。Redis が再起動してフェンスキーが失われた場合、カウンターは 0 からリスタートする。これが許容できない場合は、フェンシングトークンの発行をデータベース側で行う方が安全だ：

```sql
-- データベースでトークンを発行する場合
UPDATE fence_tokens
SET token = token + 1
WHERE resource_name = 'order:1001'
RETURNING token;
```

### Redlock との併用

本実装はシングルインスタンスの Redis を前提としている。Redlock（複数 Redis インスタンスによる合意ベースのロック）と併用する場合、各インスタンスの `INCR` が異なる値を返すため、単調増加が保証されない。Redlock 環境でフェンシングトークンが必要な場合は、トークン発行を Redis 以外の仕組み（データベースや ZooKeeper）に委ねる必要がある。

## まとめ

redis-py の `Lock` は `do_acquire` のオーバーライドでフェンシングトークンを追加できる設計になっている。Lua スクリプトでロック取得とトークン発行をアトミックに行うことで、既存の Lock API との互換性を保ちつつ、データストア側での整合性検証が可能になる。

ただし、フェンシングトークンはあくまで「データストア側での最終防衛線」であり、ロック自体の信頼性を高めるものではない。ロックの TTL 設定、処理時間の見積もり、冪等な設計といった基本的な設計原則と組み合わせて使うことが重要だ。

## 参考

- [redis-py Lock ソースコード](https://redis.readthedocs.io/en/stable/_modules/redis/lock.html) — redis-py の Lock クラスの実装
- [How to do distributed locking](https://martin.kleppmann.com/2016/02/08/how-to-do-distributed-locking.html) — Martin Kleppmann によるフェンシングトークンの提唱
- [Distributed Locks with Redis](https://redis.io/docs/latest/develop/use/patterns/distributed-locks/) — Redis 公式の分散ロックパターン
- [fencelock](https://github.com/gsquire/fencelock) — Redis モジュールとしてのフェンシングトークン実装（C 言語）
