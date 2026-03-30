---
title: "Claude Code + Celery: LLMが決定論的処理を動的に委譲するオーケストレーション"
date: 2026-03-30
lastmod: 2026-03-30
draft: false
description: "Claude Code を Celery タスクキューと組み合わせ、LLM が判断・計画を行い、決定論的処理をワーカーに委譲するオーケストレーションアーキテクチャを解説。"
categories: ["AI/LLM"]
tags: ["claude-code", "celery", "python", "agent", "オーケストレーション"]
---

Claude Code を単なるコーディングアシスタントではなく、バックエンド処理のオーケストレーターとして活用するアーキテクチャを考察する。Python Celery をタスクブローカーとして組み合わせるアプローチを紹介する。LLM が判断し、決定論的な処理（同じ入力に対して常に同じ結果を返す処理）を動的に Celery ワーカーへ委譲する仕組みが実現できる。

## 背景: 既存の Claude Code オーケストレーション

現在、Claude Code の並列実行やマルチエージェント構成には主に以下のパターンが使われている。

### tmux + git worktree

最も普及しているパターン。複数の Claude Code CLI セッションを tmux で並列起動し、git worktree で各セッションの作業ディレクトリを分離する。

- [multi-agent-shogun](https://github.com/yohey-w/multi-agent-shogun) — 将軍→家老→足軽の階層構造
- [claudio](https://github.com/Iron-Ham/claudio) — worktree ベースの並列実行

### MCP サーバーによる連携

MCP（Model Context Protocol）サーバーがタスクブローカーの役割を担い、ワーカーとなる Claude Code インスタンスにタスクを割り当てる。

- [claude-swarm](https://github.com/cj-vana/claude-swarm) — MCP サーバーベースのスウォーム制御

### 共通の特徴

これらはいずれも **Claude Code 同士の連携** が主眼であり、LLM が LLM に指示を出す構造になっている。LLM を必要としない決定論的な処理（画像変換、データ集計、API 呼び出しなど）にも LLM のリソースを消費するため、コスト・速度・信頼性の面で非効率な場面がある。

## 提案: Claude Code + Celery アーキテクチャ

### 基本思想

Claude Code（LLM）は **判断と計画** に集中し、決定論的な処理は Celery ワーカーに委譲する。

```
Claude Code（非決定論的: 状況判断・計画立案）
    │
    │  "この画像を3サイズにリサイズして、
    │   S3にアップロードして、DBを更新する"
    │
    ▼
Celery タスクを動的に生成
    ├─ resize_image.delay("img.png", 800)
    ├─ resize_image.delay("img.png", 400)
    ├─ upload_to_s3.delay(...)
    └─ update_db_record.delay(...)
```

### Airflow/Prefect との違い

従来のワークフローエンジンでは DAG（有向非巡回グラフ）を事前に定義する必要がある。Claude Code + Celery パターンでは、Claude Code が実行時に状況を判断し、DAG を動的に構築する。

| 方式 | ワークフロー定義 | 柔軟性 |
|------|-----------------|--------|
| Airflow / Prefect | 事前に DAG を定義 | 定義済みフローのみ |
| Claude Code + Celery | LLM が実行時に動的構築 | 状況に応じて自在に変更 |

## 実装パターン

### Claude Code から Celery タスクを呼び出す

Claude Code は CLI の非対話モード（`claude -p`）で呼び出せるため、Celery ワーカーから直接起動できる。逆に、Claude Code が Python スクリプトを実行して Celery タスクを投入することも可能。

```python
from celery import Celery

app = Celery('tasks', broker='redis://localhost:6379/0')

@app.task
def resize_image(path, size):
    from PIL import Image
    from pathlib import Path as P
    p = P(path)
    img = Image.open(p)
    img.thumbnail((size, size))
    output = f"{p.stem}_{size}{p.suffix}"
    img.save(output)
    return output

@app.task
def upload_to_s3(file_path, bucket, key):
    import boto3
    s3 = boto3.client('s3')
    s3.upload_file(file_path, bucket, key)
    return f"s3://{bucket}/{key}"

@app.task
def run_sql(query, params=None):
    import psycopg2
    conn = psycopg2.connect(dsn="...")
    with conn.cursor() as cur:
        cur.execute(query, params)
        conn.commit()
```

### 汎用ディスパッチャーパターン

タスクの種類が多い場合、個別のタスク関数を定義する代わりに汎用ディスパッチャーを使う方法がある。新しい Celery タスク関数を登録せずに処理の種類を増やせる（ハンドラ関数自体の追加にはワーカー再起動が必要）。

```python
@app.task
def run_step(step_type, params):
    """Claude Code が指定する step_type に応じて処理を実行"""
    handlers = {
        "resize_image": resize_image,
        "upload_s3": upload_to_s3,
        "run_sql": run_sql,
        "http_request": http_request,
        "shell_command": run_shell,
    }
    handler = handlers.get(step_type)
    if handler is None:
        raise ValueError(f"Unknown step type: {step_type}")
    return handler(**params)
```

Claude Code 側は引数の組み立てだけを担当する:

```python
run_step.delay("resize_image", {"path": "img.png", "size": 800})
run_step.delay("http_request", {"url": "https://api.example.com/notify", "method": "POST", "body": {"status": "done"}})
```

### Celery チェイン/グループによるワークフロー構築

Claude Code が Celery のプリミティブ（chain, group, chord）を組み合わせて、実行時にワークフローを組み立てる。

```python
from celery import chain, group, chord

# download の結果を resize に渡さない場合は .si()（immutable signature）を使う
# group の後にタスクを続ける場合、Celery は内部的に chord に変換する
workflow = chain(
    run_step.s("download", {"url": "https://example.com/photo.jpg"}),
    chord(
        group(
            run_step.si("resize", {"path": "photo.jpg", "size": 800}),
            run_step.si("resize", {"path": "photo.jpg", "size": 400}),
            run_step.si("resize", {"path": "photo.jpg", "size": 200}),
        ),
        run_step.si("upload_s3", {"bucket": "assets"}),
    ),
)
workflow.apply_async()
```

## 動的なタスク追加とワーカー再起動

Celery ワーカーは起動時にタスクモジュールをインポートするため、新しいタスク関数を追加するにはワーカーの再起動が必要になる。しかし、これは実用上の障壁にはならない。

### キュー消費の一時停止による安全な再起動

```bash
# 1. キュー消費を停止（タスクは Redis に残る）
celery -A app control cancel_consumer default

# 2. 新しいタスクモジュールをデプロイ

# 3. graceful restart（処理中のタスクは完了を待つ）
celery multi restart worker1 -A app --pool=prefork
```

処理中のタスクは中断されず、キュー内のタスクも Redis に保持されるため、データ損失は発生しない。

### ローリングデプロイによるダウンタイムゼロ

複数ワーカーがある場合は、ローリングデプロイで無停止更新が可能:

```
Worker A: 消費停止 → 処理中完了待ち → 再起動（新コード）
Worker B: 通常稼働中（タスクを処理し続ける）
    ↓
Worker A: 復帰（新コード）
Worker B: 消費停止 → 処理中完了待ち → 再起動（新コード）
```

### Claude Code による自律的な機能追加フロー

Claude Code 自身がこの一連の流れを自律的に実行できる:

1. 「この処理には新しいハンドラが必要」と判断
2. Python モジュールを書き出す
3. `app.control.cancel_consumer()` でキュー消費を停止
4. ワーカーを graceful restart
5. 新タスクを `send_task()` で投入
6. 結果を待つ

Celery の制御 API（`app.control`）はリモートからプログラマティックに操作可能なため、Claude Code がシェルコマンド経由でこのフローを完結させられる。

## Celery パターンが適するユースケース

- **バッチ処理の動的構成**: データ移行、一括変換など、処理対象によって手順が変わるタスク
- **障害対応の定型部分の自動化**: Claude Code がログを分析し、復旧手順の決定論的な部分（再起動、キャッシュクリア等）を Celery に委譲
- **マルチステップ API 連携**: 外部 API を順番に呼び出す処理を Claude Code が計画し、実行は Celery が担当
- **コスト最適化**: LLM のトークンを判断にのみ使い、実行は Celery ワーカー（CPU コストのみ）で処理

## チャットbot 方式との比較

「LLM にすべてやらせるチャットbot」と「Claude Code + Celery」を比較すると、タスクの性質によって優劣が明確に分かれる。

### 定量比較

| 評価軸 | チャットbot（LLM が全処理） | Claude Code + Celery |
|--------|---------------------------|---------------------|
| **トークンコスト** | 全ステップで消費 | 判断部分のみ |
| **処理速度** | 逐次実行（LLM レイテンシ込み） | 決定論的部分は並列実行可能 |
| **再現性** | 非決定論的（同じ入力でも結果が揺れる） | 決定論的部分は 100% 再現 |
| **リトライ** | 会話全体をやり直し | 失敗タスクだけリトライ |
| **可観測性** | ログは会話履歴のみ | Flower / Redis で個別タスク監視可能 |

### コスト差が開く具体例

「100 枚の画像をリサイズして S3 にアップロード」という処理を考える。

- **チャットbot方式**: 各画像ごとにツール呼び出しのターンが発生し、100 回分のコンテキストを LLM が処理する。入出力トークンは数万〜数十万に達する。
- **Celery 方式**: LLM は「100 枚をリサイズして S3 へ」という 1 回の判断でタスクを投入する。入出力トークンは数千で済み、実際のリサイズ・アップロードは CPU コストのみ。

繰り返し処理の回数が増えるほど、コスト差は線形に拡大する。

### 障害回復の違い

処理の途中で 3 番目のタスクが失敗した場合:

- **チャットbot**: 会話コンテキストの復元が必要で、最初からやり直しになりやすい
- **Celery**: 失敗したタスクだけをリトライし、完了済みのタスクはそのまま保持される

### 判断基準

```
タスクが少数・単発・探索的  → チャットbot で十分
タスクが多数・反復・決定論的 → Celery の方が有利
```

「LLM に毎回やらせる必要があるか？」が分岐点になる。画像リサイズを 100 回 LLM に頼む必要はないが、「どの画像をどうリサイズすべきか」の判断は LLM の仕事である。

## まとめ

Claude Code + Celery のアーキテクチャは、「AI がプログラマブルなインフラを道具として使う」パターンの一つである。LLM が得意な判断・計画と、決定論的処理の高速・低コストな実行を分離することで、両者の強みを活かせる。従来のタスクキュー基盤（Celery）は、AI オーケストレーターのバックエンドとしても有効に機能する。
