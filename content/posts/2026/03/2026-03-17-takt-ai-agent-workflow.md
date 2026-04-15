---
title: "takt — AIコーディングエージェントのワークフローをYAMLで定義するCLIツール"
date: 2026-03-17
lastmod: 2026-03-17
draft: false
source_url: "https://github.com/hdknr/blogs/issues/1#issuecomment-4078664295"
categories: ["AI/LLM"]
tags: ["Claude Code", "AI agent", "CLI", "workflow", "multi-agent"]
---

[takt](https://github.com/nrslib/takt) は、Claude Code や Codex などの AI コーディングエージェントのワークフローを YAML で定義できる CLI ツールです。エージェントに単にコードを書かせるだけでなく、レビューループや人間の介入ポイントを宣言的に管理することで、品質の高いアウトプットを継続的に得られるよう設計されています。

## takt とは

**TAKT** は **T**AKT **A**gent **K**oordination **T**opology の略で、ドイツ語の「拍子・指揮棒」を由来とする名前です。オーケストラの指揮者のように複数の AI エージェントを統率するというコンセプトが込められています。

- **GitHub**: https://github.com/nrslib/takt
- **言語**: TypeScript
- **スター数**: 952（2026年4月時点）
- **ライセンス**: MIT

対応エージェント: Claude Code、Codex、OpenCode、Cursor、GitHub Copilot CLI

## なぜ takt が必要か

AI コーディングエージェントを使う上で重要なのは、ワークフローの設計です。エージェントに「コードを書いて」と指示するだけでは、品質にばらつきが生じます。takt は以下の課題を解決します:

- **レビューループの自動化**: 実装 → レビュー → 修正 のサイクルを自動で回す
- **再現性の確保**: 実行パスを YAML で宣言するため、チーム間で同じ品質プロセスを共有できる
- **マルチエージェント対応**: 異なるペルソナ・権限・レビュー基準を持つ複数エージェントをオーケストレーション
- **完全なトレーサビリティ**: 全ステップを NDJSON でログに記録

## インストールと基本的な使い方

```bash
npm install -g takt
```

### 設定ファイル

`~/.takt/config.yaml` を作成してプロバイダーを指定します:

```yaml
provider: claude    # claude, codex, opencode, cursor, copilot
model: sonnet
language: ja
```

API キーを直接使う場合（CLI のインストール不要）:

```bash
export TAKT_ANTHROPIC_API_KEY=sk-ant-...
```

### タスクをキューに積んで実行する

```bash
$ takt

Select workflow:
  › 🎼 default (current)

> ユーザー認証を JWT で実装してください

[AI が要件を整理・確認]

> /go

What would you like to do?
    Execute now
  › Queue as task   ← 通常はこちら
```

キューに積まれたタスクは `.takt/tasks/` に保存され、`takt run` で実行されます。実行時は独立した worktree が作成され、ワークフロー（計画 → 実装 → レビュー → 修正ループ）が完了すると PR 作成を提案します。

```bash
# GitHub Issue をタスクとして追加
takt add #6
takt add #12

# 全タスクを実行
takt run

# タスクブランチを管理（マージ、リトライ、削除など）
takt list
```

## ワークフローの仕組み

ワークフローは YAML でステップとルールを定義します。シンプルな例:

```yaml
name: plan-implement-review
initial_step: plan
max_steps: 10

steps:
  - name: plan
    persona: planner
    edit: false
    rules:
      - condition: Planning complete
        next: implement

  - name: implement
    persona: coder
    edit: true
    required_permission_mode: edit
    rules:
      - condition: Implementation complete
        next: review

  - name: review
    persona: reviewer
    edit: false
    rules:
      - condition: Approved
        next: COMPLETE
      - condition: Needs fix
        next: implement    # ← 修正ループ
```

`COMPLETE` でワークフロー成功終了、`ABORT` で失敗終了。ルール条件によって次のステップが決まります。

### 組み込みワークフロー

| ワークフロー | 用途 |
|-------------|------|
| `default` | 標準開発。テストファースト + AIアンチパターンレビュー + 並列レビュー（アーキテクチャ + スーパーバイザー） |
| `frontend-mini` | フロントエンド向けミニ構成 |
| `backend-mini` | バックエンド向けミニ構成 |
| `dual-mini` | フロントエンド + バックエンド構成 |

## カスタマイズ

### ワークフローのカスタマイズ

```bash
# 組み込みワークフローを ~/.takt/workflows/ にコピーして編集
takt eject default
```

### カスタムペルソナの作成

```markdown
# ~/.takt/personas/security-reviewer.md
You are a code reviewer specialized in security vulnerabilities.
```

ワークフローから参照:

```yaml
persona: security-reviewer
```

### レパートリーパッケージのインストール

```bash
takt repertoire add <github-repo>
```

## CI/CD 連携

GitHub Actions 用の [takt-action](https://github.com/nrslib/takt-action) が提供されています:

```yaml
- uses: nrslib/takt-action@main
  with:
    anthropic_api_key: ${{ secrets.TAKT_ANTHROPIC_API_KEY }}
    github_token: ${{ secrets.GITHUB_TOKEN }}
```

パイプラインモードでの実行:

```bash
takt --pipeline --task "Fix the bug" --auto-pr
```

## プロジェクト構成

```
~/.takt/                    # グローバル設定
├── config.yaml             # プロバイダー・モデル・言語設定
├── workflows/              # ユーザー定義ワークフロー
├── facets/                 # ペルソナ・ポリシー等
└── repertoire/             # インストール済みパッケージ

.takt/                      # プロジェクトレベル
├── config.yaml             # プロジェクト設定
├── workflows/              # ワークフロー上書き
├── tasks.yaml              # ペンディングタスク
└── runs/                   # 実行レポート・ログ
```

## まとめ

takt は AI コーディングエージェントを「ただ動かす」のではなく、「品質を保ちながら動かす」ための仕組みを提供します。YAML によるワークフロー定義、レビューループの自動化、マルチエージェント対応など、チーム開発での AI 活用に特に有用です。

ツイートで紹介した通り、AI コーディングエージェントを使う上でワークフロー設計は本質的な課題です。takt はその課題に正面から向き合ったツールといえるでしょう。
