---
title: "pytest.mark.chaos で始めるカオスエンジニアリング — Python テストに障害注入を組み込む"
date: 2026-04-17
lastmod: 2026-04-17
draft: false
source_url: "https://github.com/hdknr/blogs/issues/93#issuecomment-4265898247"
categories: ["プログラミング言語"]
tags: ["Python", "pytest", "カオスエンジニアリング", "テスト", "障害注入", "Claude Code", "AIエージェント"]
---

「本番で障害が起きてから対処する」のではなく、「テスト段階で意図的に障害を起こして耐性を確認する」。これがカオスエンジニアリングの基本思想だ。Python の pytest には、この考え方をテストコードに組み込むためのシンプルな仕組みがある。

## pytest.mark.chaos とは

`@pytest.mark.chaos` は、pytest のカスタムマーカー機能を使って「カオステスト」を分類するためのラベルだ。pytest にはビルトインのマーカー（`@pytest.mark.skip`、`@pytest.mark.parametrize` など）があるが、`chaos` は**ユーザーが自由に定義するカスタムマーカー**に該当する。

```python
import pytest

@pytest.mark.chaos
def test_network_timeout():
    """ネットワークタイムアウト時にフォールバックが機能するか"""
    result = call_api_with_timeout(timeout=0.001)
    assert result == "fallback_response"
```

### マーカーの登録

カスタムマーカーは `pyproject.toml` または `pytest.ini` に登録しておくと、`PytestUnknownMarkWarning` 警告を抑制できる。

```toml
# pyproject.toml
[tool.pytest.ini_options]
markers = [
    "chaos: カオスエンジニアリング関連のテスト（障害注入・耐性検証）",
]
```

### 選択実行

```bash
# カオステストだけを実行
pytest -m chaos

# カオステスト以外を実行（通常の CI）
pytest -m "not chaos"

# カオステストと統合テストを実行
pytest -m "chaos or integration"
```

これにより、通常の CI パイプラインではカオステストをスキップし、定期的なレジリエンス検証時にだけ実行するという運用が可能になる。

## カオステストの実装パターン

### パターン 1: ネットワーク障害の注入

外部 API がタイムアウトした場合のフォールバック動作を検証する。

```python
import pytest
from unittest.mock import patch

@pytest.mark.chaos
def test_api_timeout_fallback():
    """外部 API タイムアウト時にキャッシュからレスポンスを返すか"""
    with patch("app.client.requests.get", side_effect=TimeoutError):
        result = app.client.fetch_user_profile(user_id=123)
    assert result == app.client.get_cached_profile(user_id=123)


@pytest.mark.chaos
def test_api_connection_refused():
    """接続拒否時にリトライ後にエラーハンドリングされるか"""
    with patch("app.client.requests.get", side_effect=ConnectionError):
        with pytest.raises(app.exceptions.ServiceUnavailable):
            app.client.fetch_user_profile(user_id=123)
```

### パターン 2: データベース障害

DB 接続が切れた場合の挙動を検証する。

```python
import pytest
from unittest.mock import patch, MagicMock

@pytest.mark.chaos
def test_db_connection_lost():
    """DB 接続断時にリードレプリカにフォールバックするか"""
    mock_primary = MagicMock(side_effect=ConnectionError("Connection lost"))
    with patch("app.db.get_primary_connection", mock_primary):
        result = app.db.query_user(user_id=123)
    assert result is not None  # リードレプリカから取得できている


@pytest.mark.chaos
def test_db_slow_query():
    """スロークエリ発生時にタイムアウトが正しく機能するか"""
    import time

    def slow_query(*args, **kwargs):
        time.sleep(5)
        return []

    with patch("app.db.execute_query", side_effect=slow_query):
        with pytest.raises(app.exceptions.QueryTimeout):
            app.db.query_user(user_id=123)
```

### パターン 3: ランダム障害注入（Fixture 方式）

pytest の fixture を使って、確率的に障害を注入するパターン。実際のカオスエンジニアリングに近い手法だ。

```python
import pytest
import random

@pytest.fixture
def chaos_network(monkeypatch):
    """30% の確率でネットワーク遅延を注入する fixture"""
    original_get = requests.get

    def unstable_get(*args, **kwargs):
        if random.random() < 0.3:
            import time
            time.sleep(random.uniform(1.0, 5.0))  # 1〜5秒の遅延
        if random.random() < 0.1:
            raise ConnectionError("Chaos: connection refused")
        return original_get(*args, **kwargs)

    monkeypatch.setattr("requests.get", unstable_get)


@pytest.mark.chaos
def test_service_under_unstable_network(chaos_network):
    """不安定なネットワーク環境でもサービスが応答を返すか"""
    for _ in range(10):
        result = app.service.health_check()
        assert result.status in ("ok", "degraded")
```

### パターン 4: リソース枯渇

メモリやディスク容量の枯渇をシミュレートする。

```python
import pytest
from unittest.mock import patch

@pytest.mark.chaos
def test_disk_full():
    """ディスク容量不足時にログ書き込みがグレースフルに失敗するか"""
    with patch("builtins.open", side_effect=OSError("No space left on device")):
        # ログ書き込み失敗がアプリケーションをクラッシュさせないことを確認
        app.logger.write("test message")
        assert app.service.is_running()


@pytest.mark.chaos
def test_memory_pressure():
    """メモリ逼迫時にキャッシュが適切にエビクションされるか"""
    # キャッシュを上限まで埋める
    for i in range(10000):
        app.cache.set(f"key_{i}", "x" * 1024)

    # 新しいエントリが古いエントリを押し出すことを確認
    app.cache.set("new_key", "new_value")
    assert app.cache.get("new_key") == "new_value"
    assert app.cache.size() <= app.cache.max_size
```

## conftest.py での一元管理

プロジェクト全体のカオステスト設定を `conftest.py` にまとめる。

```python
# conftest.py
import pytest

def pytest_configure(config):
    config.addinivalue_line(
        "markers", "chaos: カオスエンジニアリングテスト"
    )

@pytest.fixture
def chaos_config():
    """カオステストの共通設定"""
    return {
        "network_delay_probability": 0.3,
        "network_error_probability": 0.1,
        "db_error_probability": 0.05,
        "max_delay_seconds": 5.0,
    }

def pytest_collection_modifyitems(config, items):
    """CI 環境ではカオステストに xfail マーカーを自動付与"""
    import os
    if os.getenv("CI") and not os.getenv("CHAOS_ENABLED"):
        chaos_marker = pytest.mark.xfail(
            reason="カオステストは CHAOS_ENABLED=1 で明示的に有効化が必要"
        )
        for item in items:
            if "chaos" in item.keywords:
                item.add_marker(chaos_marker)
```

## 関連ツール・フレームワーク

pytest のカスタムマーカーだけでも基本的なカオステストは実現できるが、より本格的な障害注入には専用ツールとの組み合わせが有効だ。

| ツール | 対象 | 特徴 |
|--------|------|------|
| **pytest-disrupt** | pytest プラグイン | カオスエンジニアリングガイドラインに準拠した障害注入 |
| **toxiproxy** | ネットワーク層 | TCP レベルでの遅延・切断・帯域制限。Python クライアントあり |
| **Chaos Mesh** | Kubernetes | Pod・ネットワーク・IO レベルの障害注入 |
| **AWS FIS** | AWS サービス | EC2・RDS・ECS 等への障害注入。pytest との統合可能 |
| **Litmus** | Kubernetes | ChaosHub からの実験テンプレート。CI/CD 統合対応 |

### userver フレームワークとの統合

マイクロサービスフレームワーク [userver](https://userver.tech/) では、`@pytest.mark.chaos` がフレームワークレベルでサポートされている。テスト実行時にネットワーク遅延・切断・DB 障害などを自動的に注入し、サービスのフォールバック動作を検証できる。

## CI/CD への組み込み

### GitHub Actions の例

```yaml
name: Chaos Tests

on:
  schedule:
    - cron: '0 3 * * 1'  # 毎週月曜 AM3:00

jobs:
  chaos-test:
    runs-on: ubuntu-latest
    env:
      CHAOS_ENABLED: "1"
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.12'
      - run: pip install -r requirements-test.txt
      - run: pytest -m chaos --tb=long -v
```

通常の CI では `pytest -m "not chaos"` で高速にテストを回し、週次のスケジュールジョブでカオステストを実行するという運用が推奨される。

## Django プロジェクトでの活用

Django のテストスイートにカオステストを組み込む例。

```python
import pytest
from unittest.mock import patch
from django.test import TestCase

@pytest.mark.chaos
@pytest.mark.django_db
def test_cache_backend_failure(client):
    """キャッシュバックエンド障害時に DB フォールバックが機能するか"""
    with patch("django.core.cache.cache.get", side_effect=Exception("Redis down")):
        response = client.get("/api/users/1/")
    assert response.status_code == 200  # キャッシュなしでも正常応答


@pytest.mark.chaos
@pytest.mark.django_db
def test_celery_broker_down(client):
    """Celery ブローカー障害時に同期フォールバックが機能するか"""
    with patch("app.tasks.send_email.delay", side_effect=ConnectionError):
        response = client.post("/api/register/", data={
            "email": "test@example.com",
            "password": "secure_password"
        })
    assert response.status_code == 201  # 登録自体は成功する
```

## Claude Code でカオステストを自動生成する

ここまでカオステストの書き方を紹介してきたが、「どの障害シナリオを検証すべきか」の洗い出し自体が大きな作業だ。Claude Code のカスタムエージェント機能を使うと、この分析とテスト生成を AI に委任できる。

### chaos-engineer エージェントの設計

Claude Code では `.claude/agents/` にエージェント定義を置くことで、ドメイン特化の専門エージェントを作成できる。以下は自律型トレーディングシステムで実際に運用されている chaos-engineer エージェントの設計思想だ。

```markdown
# .claude/agents/chaos-engineer.md

---
name: chaos-engineer
description: カオスエンジニアリング分析。「もし〇〇が壊れたら」の視点で検証する
tools: Glob, Grep, Read, Bash, WebFetch
---

あなたはカオスエンジニアリングの専門家です。
「もし〇〇が壊れたら？」の視点でリポジトリを分析し、
単一障害点・エラーハンドリング欠如・状態整合性の地雷を特定してください。
```

エージェントに与える指示のポイント:

- **ドメイン固有の観点を明示する** — 汎用的な「エラーハンドリングを確認して」ではなく、「残高取得失敗時に 0 円扱いで計算が継続していないか」のように具体的に
- **優先度分類の軸を定義する** — 金融判断・状態整合性・自己修正機構など、プロジェクトに合った分類軸を設定
- **出力形式を指定する** — 障害シナリオ・影響範囲・推奨対策を構造化して出力させる

### 3 軸の優先度分類

トレーディングシステムの例では、以下の 3 軸で指摘を分類している:

| 軸 | 対象 | 例 |
|----|------|-----|
| **A. 金融判断・安全性** | 取引ロジック・残高計算・DRY_RUN ガード | 残高取得失敗時の 0 円扱い |
| **B. 状態整合性** | DB トランザクション・べき等性・多重実行 | Issue 作成と DB update の片方だけ成功 |
| **C. 自己修正機構** | 自動診断・回復処理・学習データの適用 | 自動検知 Issue 自体の作成失敗 |

これらの軸はプロジェクトのドメインに応じてカスタマイズする。Web アプリなら「認証・認可」「データ一貫性」「外部サービス依存」といった軸が考えられる。

### ワークフロー: 分析 → テスト生成 → 実行

Claude Code と chaos-engineer エージェントを組み合わせたワークフローは 3 段階で進む。

**Step 1: 脆弱性分析**

chaos-engineer エージェントにコードベースを分析させ、障害シナリオを洗い出す。

```
> @chaos-engineer リポジトリ全体を分析して、障害シナリオを重大度付きでリストアップしてください
```

エージェントはコードを読み、`Grep` で `except` パターンや外部 API 呼び出しを検索し、具体的な行番号付きで指摘を出力する。

**Step 2: テストコード生成**

分析結果をもとに、Claude Code にテストコードを生成させる。

```
> 分析結果の critical/high 指摘について pytest.mark.chaos テストを生成してください
```

生成されるテストは `@pytest.mark.chaos` マーカー付きで、`pyproject.toml` に登録済みのマーカー定義と整合する。

```toml
# pyproject.toml
[tool.pytest.ini_options]
markers = [
    "chaos: chaos-engineer 分析由来の回帰テスト (pytest -m chaos で実行)",
]
```

**Step 3: テスト実行と結果の反映**

```bash
# カオステストの実行
uv run pytest -m chaos -v

# 失敗したテスト = 実際に脆弱な箇所
# → 修正を実装 → テストが通ることを確認
```

### エージェント定義の設計指針

実際の運用で効果的だったエージェント定義のパターン:

```markdown
## 分析観点（エージェントに指示する内容）

### 共通観点
- 単一障害点 (SPOF) の特定
- `except: pass` で握り潰されたエラー
- タイムアウト設定の不備
- リトライ処理の欠如（特に外部 API）

### ドメイン固有観点（プロジェクトごとにカスタマイズ）
- [具体的な障害シナリオ 1]
- [具体的な障害シナリオ 2]
- ...

## 出力形式
各指摘について以下を明記:
- **問題箇所**: `src/xxx.py:123`（行番号必須）
- **障害シナリオ**: もし〇〇が〇〇したら...
- **影響範囲**: 何が起きるか
- **推奨する対策**: 具体的な修正案 + テスト方法
```

### 他のエージェントとの連携

chaos-engineer エージェントの出力を他のワークフローに接続することで、カオスエンジニアリングを継続的に回せる:

- **Go-Live チェック**: 本番デプロイ前に chaos-engineer を実行し、新コードの障害耐性を検証
- **定期的な再分析**: コードが変化するたびに新たな脆弱性が生まれる。月次で再分析を実行
- **Issue 化**: critical/high の指摘を GitHub Issue として自動起票し、対応を追跡

Claude Code のカスタムエージェントを使うことで、「カオスエンジニアリングの専門知識がなくても、ドメイン知識をエージェント定義に注入するだけで高品質な障害分析とテスト生成ができる」という点が最大のメリットだ。

## まとめ

`@pytest.mark.chaos` は pytest の標準機能であるカスタムマーカーを活用した、シンプルで強力なカオスエンジニアリング手法だ。

- **分類**: `pytest -m chaos` でカオステストだけを選択実行
- **障害注入**: mock / monkeypatch / fixture を組み合わせてネットワーク障害・DB 障害・リソース枯渇をシミュレート
- **CI 統合**: 通常の CI ではスキップし、定期スケジュールで実行する運用が現実的
- **段階的導入**: まず最も壊れやすい外部依存（API・DB・キャッシュ）から始め、徐々に範囲を広げる
- **Claude Code 連携**: chaos-engineer エージェントで障害シナリオの分析とテスト生成を自動化

「あえて壊してみるテスト」をテストスイートの一部として日常的に実行できるのが、pytest.mark.chaos の最大の利点だ。さらに Claude Code のカスタムエージェントを活用すれば、「どこを壊すべきか」の分析自体も AI に委任でき、カオスエンジニアリングの導入障壁を大幅に下げられる。

## 参考リンク

- [pytest markers ドキュメント](https://docs.pytest.org/en/stable/how-to/mark.html)
- [pytest-disrupt（GitHub）](https://github.com/grafuls/pytest-disrupt)
- [Chaos Testing Guide 2026（Testomat）](https://testomat.io/blog/discover-the-power-of-chaos-testing-techniques/)
- [userver testsuite](https://userver.tech/db/daa/group__userver__testsuite.html)
