---
title: "Claude Code で Laravel→Django 全自動移行をやってみた（2/3）自動化基盤編"
date: 2026-03-26
lastmod: 2026-03-26
draft: false
description: "Claude Code を自律実行させるための Bash フレームワーク run-issue.sh の設計を解説。Issue 駆動の実行フロー、サブエージェント活用、Pre-commit Hook と CI による品質保証の実装。"
categories: ["AI/LLM"]
tags: ["Claude Code", "Laravel", "Django", "Python", "自動化"]
---

[前回の計画編](/posts/2026/03/2026-03-26-claude-code-laravel-django-migration-plan/)では、移行の方針とフェーズ設計を紹介しました。本記事では、計画を実際に自律実行するためのフレームワーク設計を解説します。

---

## 全体アーキテクチャ

自律移行の仕組みは、大きく 3 つのレイヤーで構成されています。

```text
┌─────────────────────────────────────────────────────┐
│  オーケストレーション層: run-issue.sh             │
│  - Issue 読み込み → ブランチ作成 → Claude 起動    │
│  - リトライ → Push → PR 作成 → マージ → Issue 閉じ │
└──────────────────┬──────────────────────────────────┘
                   ↓
┌─────────────────────────────────────────────────────┐
│  実行層: Claude Code (claude -p)                 │
│  - ソースコード調査 → 設計 → 実装 → テスト        │
│  - コミット（push はしない）                      │
│  - サブエージェント: explorer / architect / reviewer│
└──────────────────┬──────────────────────────────────┘
                   ↓
┌─────────────────────────────────────────────────────┐
│  品質保証層: Hooks + CI + verify-phase.sh        │
│  - Pre-commit: ruff format + check              │
│  - PostToolUse: 編集時の即座リント               │
│  - CI: lint → Django check → pytest             │
│  - Phase 検証: ファイル存在 + 機能チェック        │
└─────────────────────────────────────────────────────┘
```

### 責務分離の原則

最も重要な設計原則は、**ワークフロー制御と実装作業の責務分離**です。

| 責務 | 担当 | 理由 |
|------|------|------|
| ブランチ作成・切替 | スクリプト | 確定的に実行する必要がある |
| git push | スクリプト | タイミングを制御する必要がある |
| PR 作成・マージ | スクリプト | ワークフローの一部 |
| Issue クローズ | スクリプト | 完了判定はスクリプトが行う |
| コード実装 | Claude Code | 創造的判断が必要 |
| テスト作成 | Claude Code | 実装と一体 |
| コミット | Claude Code | こまめにコミットさせる |
| コードレビュー | Claude Code（サブエージェント） | 品質チェック |

この分離が不十分だったことが後述の「ブランチ分岐問題」の根本原因でした。

---

## run-issue.sh の設計

約 800 行の Bash スクリプトで、Issue 単位の自律実行を制御します。

### 実行フロー

```bash
./scripts/run-issue.sh <issue_number>
```

```text
1. GitHub Issue を読み込み（gh issue view）
2. 依存 Issue の完了チェック
3. feature ブランチを作成（main から分岐）
4. Claude Code を起動（claude -p <prompt>）
5. 完了判定（コミット有無 + テスト結果）
6. 失敗時: 最大 3 回リトライ（10 秒クールダウン）
7. 成功時: push → PR 作成 → マージ → Issue 閉じ
8. 実行ログを execution.md に追記
```

### バッチ実行

```bash
./scripts/run-issue.sh all    # 全 Issue を順次実行
./scripts/run-issue.sh resume # 中断した Issue から再開
```

`all` モードでは、Issue の依存関係を解決しながら順次実行します。前の Issue が失敗したら停止し、手動介入を待ちます。

### リトライ機構

Claude Code のセッションは非決定的です。同じプロンプトでも異なる結果になり得ます。リトライ時には前回の失敗情報をコンテキストとして渡します:

```bash
# リトライ時のプロンプト（概念）
"前回の実行が失敗しました。
git status, git diff, git log を確認し、
前回の作業状態を把握してから再開してください。"
```

実際に 15 Issue 中 8 Issue がリトライを経験しましたが、全て 2〜3 回目で成功しています。

---

## Claude Code に渡すプロンプトの設計

`run-issue.sh` が Claude Code を起動する際のプロンプトは約 360 行で、以下のステップで構成されています。

### 10 ステップの作業指示

```text
Step 1: Issue を読む（gh issue view で全文取得）
Step 2: ソースコード調査（feature-dev:code-explorer サブエージェント）
Step 3: 設計（feature-dev:code-architect サブエージェント、複雑な場合）
Step 4: 実装（Django のベストプラクティスに従う）
Step 5: テスト作成（pytest-django）
Step 6: 品質チェック（ruff format + check + Django check）
Step 7: コードレビュー（feature-dev:code-reviewer サブエージェント）
Step 8: 指摘事項の修正
Step 9: verify-phase.sh の実行
Step 10: execution.md への記録
```

### サブエージェントの活用

Claude Code には「サブエージェント」機能があり、メインの Claude とは別のコンテキストで専門的なタスクを実行できます。本プロジェクトでは 3 種類を活用しました:

**code-explorer**: Laravel のソースコードを深く調査し、移植すべきビジネスロジックを特定
```
「Laravel の ContractController を調査し、
 全メソッドのビジネスロジックを整理してください」
```

**code-architect**: 複雑な機能の設計方針を決定
```
「28 フィールドの検索フォームを Django で実装する
 最適なアーキテクチャを設計してください」
```

**code-reviewer**: 実装済みコードのセキュリティ・品質レビュー
```
「変更されたファイルをレビューし、
 セキュリティ問題・ロジックエラーを報告してください」
```

---

## 権限管理

Claude Code の権限は `.claude/settings.json` で制御します。自律実行に必要な操作のみをホワイトリストで許可しました。

```json
{
  "permissions": {
    "allow": [
      "Bash(git *)",
      "Bash(docker compose *)",
      "Bash(uv run *)",
      "Bash(gh issue view *)",
      "Read", "Edit", "Write", "Glob", "Grep"
    ]
  }
}
```

ただし、CLAUDE.md の禁止事項で `git push` / `git branch` / `gh pr create` を禁止しているため、実質的には「読み取り + 実装 + コミット」に限定されます。

---

## 品質保証の実装

### Pre-commit Hook

```bash
#!/bin/bash
# .githooks/pre-commit
STAGED_PY=$(git diff --cached --name-only --diff-filter=d -- '*.py')
[ -z "$STAGED_PY" ] && exit 0

uv run ruff format $STAGED_PY
uv run ruff check --fix $STAGED_PY
git add $STAGED_PY
```

Claude Code がコミットするたびに自動フォーマット + lint 修正が走ります。

### PostToolUse Hook

Claude Code 固有の機能で、Edit や Write ツールが実行されるたびにフック関数が呼ばれます。

```bash
#!/bin/bash
# .claude/hooks/post-edit-lint.sh
# Claude が Python ファイルを編集するたびに ruff check を実行
uv run ruff check "$FILE_PATH"
```

これにより、コミット前の段階でスタイル違反を検出・フィードバックできます。

### verify-phase.sh

各フェーズ完了後の検証チェックリスト:

```bash
#!/bin/bash
# scripts/verify-phase.sh <issue_number>

echo "=== Phase 検証開始 ==="

# 共通チェック
check "git 状態がクリーン" git diff --quiet HEAD
check "ruff format" uv run ruff format --check .
check "ruff check" uv run ruff check .
check "Django check" uv run python manage.py check
check "マイグレーション整合性" uv run python manage.py makemigrations --check --dry-run

# Phase 固有チェック（ファイル存在確認など）
case $ISSUE in
  2) check "masters/models.py が存在" test -f masters/models.py ;;
  5) check "accounts/middleware.py が存在" test -f accounts/middleware.py ;;
  # ...
esac

# テスト実行
check "pytest 全パス" uv run pytest
```

### GitHub Actions CI

```yaml
# .github/workflows/ci.yml
jobs:
  lint:
    steps:
      - run: uv run ruff format --check .
      - run: uv run ruff check .

  django-check:
    needs: lint
    services:
      mysql: { image: mysql:8.0 }
    steps:
      - run: uv run python manage.py check
      - run: uv run python manage.py makemigrations --check --dry-run

  test:
    needs: django-check
    steps:
      - run: uv run pytest
```

---

## Docker 環境

開発環境は Docker Compose で完結させ、Claude Code が Docker 内で動作確認できるようにしました。

```yaml
# docker-compose.yml
services:
  db:
    image: mysql:8.0
    volumes:
      - ./docker/mysql/init/001-dump.sql:/docker-entrypoint-initdb.d/001-dump.sql
    # ↑ 既存 DB ダンプを初回起動時に自動リストア

  app:
    build: .
    depends_on:
      db: { condition: service_healthy }
    volumes:
      - .:/app  # ライブリロード用

  nginx:
    image: nginx:alpine
    ports: ["8080:80"]
```

41MB の本番 DB ダンプを `docker/mysql/init/` に配置し、`docker-compose up` だけで既存データ入りの環境が立ち上がります。Claude Code は `docker compose exec app pytest` でテスト実行、`docker compose exec app python manage.py check` で Django チェックを行えます。

---

## 実行ログの自動記録

`execution.md` にタイムスタンプ付きの実行ログを自動記録します。

```markdown
### Issue #2: マスタ系モデル定義
- 開始: 2026-03-26 12:18:50
- リトライ 2: 2026-03-26 12:31:22
- 完了: 2026-03-26 12:33:21
- 所要時間: 14分32秒
- 試行回数: 2
- 結果: 成功

#### 作業内容
- inspectdb で全テーブルのモデル雛形を自動生成
- マスタ系 10 モデルを分類・整理
- ForeignKey リレーション設定
- Django Admin に登録
...
```

「作業内容」と「成果物」のセクションは Claude Code 自身が記述します。スクリプトはタイムスタンプと結果のみを書き込みます。

---

## 設計で重視したこと

### 1. 冪等性
リトライ時に副作用が蓄積しないよう設計。ブランチが既に存在すれば再利用、コミットが既にあれば追加のみ。

### 2. 障害の局所化
1 つの Issue が失敗しても他に影響しない。各 Issue は独立したブランチで作業し、main にマージされるまで他の Issue に影響しません。

### 3. 可観測性
実行ログ・git log・GitHub Issue/PR のコメントで、何が起きたかを事後に追跡可能。

### 4. 中断耐性
「こまめなコミット」を指示することで、Claude Code のセッションが中断しても未コミットの変更を最小化。実際に中断からの復旧に成功したケースがありました。

---

## 次回予告

自動化基盤編では「どう動かすか」の設計を解説しました。

次の[実行結果・教訓編](/posts/2026/03/2026-03-26-claude-code-laravel-django-migration-lessons/)では、実際に 15 Issue を自律実行した結果 — 成功パターン、発生した問題（ブランチ分岐問題）、そして次回のプロジェクトに活かすべき教訓を紹介します。
