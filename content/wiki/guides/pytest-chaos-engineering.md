---
title: "pytest でカオスエンジニアリングを始めるガイド"
description: "pytest.mark.chaos カスタムマーカーを使って障害注入テストを実装し、CI/CD に組み込む手順"
date: 2026-04-23
lastmod: 2026-04-23
aliases: ["pytest chaos", "カオスエンジニアリング Python"]
related_posts:
  - "/posts/2026/04/2026-04-17-pytest-chaos-engineering/"
tags: ["Python", "pytest", "カオスエンジニアリング", "テスト", "CI/CD", "Claude Code"]
---

## 概要

「本番で障害が起きてから対処する」のではなく「テスト段階で意図的に障害を起こして耐性を確認する」カオスエンジニアリングの考え方を pytest に組み込む手法。`@pytest.mark.chaos` というカスタムマーカーで障害注入テストを分類・選択実行できる。

## セットアップ

### マーカー登録

```toml
# pyproject.toml
[tool.pytest.ini_options]
markers = [
    "chaos: カオスエンジニアリング関連のテスト（障害注入・耐性検証）",
]
```

### 選択実行

```bash
pytest -m chaos        # カオステストのみ
pytest -m "not chaos"  # 通常の CI（カオステストをスキップ）
pytest -m "chaos or integration"
```

## 主要な障害注入パターン

### ネットワーク障害

```python
@pytest.mark.chaos
def test_api_timeout_fallback():
    with patch("app.client.requests.get", side_effect=TimeoutError):
        result = app.client.fetch_user_profile(user_id=123)
    assert result == app.client.get_cached_profile(user_id=123)
```

### データベース障害

```python
@pytest.mark.chaos
def test_db_connection_lost():
    mock_primary = MagicMock(side_effect=ConnectionError("Connection lost"))
    with patch("app.db.get_primary_connection", mock_primary):
        result = app.db.query_user(user_id=123)
    assert result is not None  # リードレプリカから取得
```

### ランダム障害 Fixture（確率的注入）

```python
@pytest.fixture
def chaos_network(monkeypatch):
    """30% の確率でネットワーク遅延を注入"""
    original_get = requests.get
    def unstable_get(*args, **kwargs):
        if random.random() < 0.3:
            time.sleep(random.uniform(1.0, 5.0))
        if random.random() < 0.1:
            raise ConnectionError("Chaos: connection refused")
        return original_get(*args, **kwargs)
    monkeypatch.setattr("requests.get", unstable_get)
```

### Django との統合

```python
@pytest.mark.chaos
@pytest.mark.django_db
def test_cache_backend_failure(client):
    with patch("django.core.cache.cache.get", side_effect=Exception("Redis down")):
        response = client.get("/api/users/1/")
    assert response.status_code == 200  # キャッシュなしでも正常応答
```

## CI/CD 組み込み（GitHub Actions）

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
      - run: pip install -r requirements-test.txt
      - run: pytest -m chaos --tb=long -v
```

通常 CI では `pytest -m "not chaos"` で高速に回し、週次スケジュールジョブでカオステストのみ実行する運用が推奨される。

## Claude Code での自動化

`.claude/agents/chaos-engineer.md` にドメイン固有の観点を持つエージェントを定義し、コードベースの障害シナリオ分析とテストコード生成を自動化できる。

3軸の優先度分類（金融・トレーディング例）:
- **A. 金融判断・安全性**: 取引ロジック・残高計算
- **B. 状態整合性**: DB トランザクション・べき等性
- **C. 自己修正機構**: 自動診断・回復処理

## 関連ツール

| ツール | 対象 | 特徴 |
|--------|------|------|
| pytest-disrupt | pytest プラグイン | カオスエンジニアリングガイドライン準拠 |
| toxiproxy | ネットワーク層 | TCP レベルの遅延・切断・帯域制限 |
| Chaos Mesh | Kubernetes | Pod・ネットワーク・IO 障害注入 |
| AWS FIS | AWS サービス | EC2・RDS・ECS への障害注入 |

## 関連ページ

- [Claude Code](/blogs/wiki/tools/claude-code/) — chaos-engineer エージェントの実行環境
- [GitHub Actions セキュリティ](/blogs/wiki/guides/github-actions-security/) — CI/CD パイプラインとの統合

## ソース記事

- [pytest.mark.chaos で始めるカオスエンジニアリング](/blogs/posts/2026/04/2026-04-17-pytest-chaos-engineering/) — 2026-04-17
