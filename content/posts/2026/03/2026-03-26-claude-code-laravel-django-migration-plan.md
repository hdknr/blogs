---
title: "Claude Code で Laravel→Django 全自動移行をやってみた（1/3）計画編"
date: 2026-03-26
lastmod: 2026-03-26
draft: false
description: "Laravel 6 から Django 4.2 への全自動移行プロジェクトの計画編。inspectdb 方式によるモデル生成、8フェーズの段階設計、CLAUDE.md を活用した Claude Code への設計書作成手法を解説。"
categories: ["AI/LLM"]
tags: ["Claude Code", "Laravel", "Django", "Python", "自動化"]
---

業務管理システム（PHP/Laravel 6.20）を Python/Django 4.2 に移行するプロジェクトを、**Claude Code の自律実行**でほぼ全自動で完遂しました。

- **移行元**: Laravel 6.20 / PHP 8.0 / MySQL 5.7 / Blade テンプレート
- **移行先**: Django 4.2 LTS / Python 3.11+ / MySQL 8.0 / Django Templates
- **所要時間**: 約 5.5 時間（準備フェーズ除く）
- **成果物**: 17 モデル / 50+ テンプレート / 199 テスト / 15,000 行の Python コード

本記事は 3 部構成です。

1. **計画編**（本記事）— なぜやったか、どう計画したか
2. [**自動化基盤編**](/posts/2026/03/2026-03-26-claude-code-laravel-django-migration-automation/) — Claude Code を自律実行させるフレームワークの設計
3. [**実行結果・教訓編**](/posts/2026/03/2026-03-26-claude-code-laravel-django-migration-lessons/) — 実際に何が起きたか、次回への教訓

---

## プロジェクトの背景

移行対象は、ある業種特化の業務管理システムです。契約管理・マスタ管理・CSV インポート・Excel エクスポート・月次締処理・外部サービス連携（OAuth2 / REST / GraphQL）など、典型的な業務アプリの機能を一通り備えています。

Laravel 側のコードベースの規模感:
- コントローラ: 27 個
- Eloquent モデル: 21 個
- DB テーブル: 21 個（レコード数: 契約 4.1 万件、顧客マスタ 4.1 万件、外注先 4,800 件）
- 外部 API 連携: OAuth2 認証 + REST + GraphQL

「手で移行したら何人月かかるか」を考えたとき、Claude Code に全部やらせてみよう、という実験的な発想でプロジェクトが始まりました。

---

## 移行方針の決定

### 1. 既存 DB をそのまま使う（inspectdb 方式）

最も重要な設計判断は、**既存の本番 DB ダンプをそのまま使い、Django の `inspectdb` でモデル雛形を自動生成する**方式を採用したことです。

```text
既存 DB ダンプ取得 → Docker MySQL にリストア → inspectdb でモデル生成
→ managed = True に変更 → migrate --fake で初回適用
```

これにより:
- モデル定義の正確性が大幅に向上（カラム名・型・制約が実 DB と完全一致）
- 既存データで動作確認が可能（テストデータを作る手間がない）
- テーブル名の typo（例: `infomations`）もそのまま維持して互換性確保

当初は「Laravel のモデル定義を読んで手動で Django モデルを書く」方針でしたが、ユーザー（自分）の「それで大丈夫か？」という問いかけで方針転換しました。**ユーザーの素朴な疑問がアーキテクチャ改善に繋がった**好例です。

### 2. 外部 API の事前動作確認

Laravel のコードに書かれている API エンドポイントと、実際に動く API が一致しているとは限りません。準備段階で実際に `curl` で叩いて確認したところ、いくつかの重要な差異が見つかりました:

- GraphQL のクエリ名: コード上は `customers` → 実際は `customer_set`
- フィールド名: `branchCode` → 実際は `company_code`
- 認証方式: `client_credentials` grant → 実際は `assertion` grant のみ

これらの差異を事前に CLAUDE.md（Claude Code が読むプロジェクト設定ファイル）に記録したことで、全フェーズを通じて同じ間違いを繰り返さずに済みました。

### 3. フロントエンドは「コピー＆ペースト」

Laravel 側で使っていた UI テーマ（jQuery + Bootstrap ベース）の CSS/JS をそのまま Django の `static/` にコピーする方針を取りました。カスタム SASS/JS ビルドは不要 — プリビルドファイルをそのまま使います。

Django テンプレートでは `{% load static %}` で参照するだけ。フロントエンドのビルドパイプラインを移行する必要がないため、**バックエンドのビジネスロジック移行に集中**できました。

---

## フェーズ設計

移行作業を 8 フェーズ・15 の GitHub Issue に分割しました。各 Issue に依存関係を定義し、順序通りに自動実行する設計です。

```text
Phase 0: 初期セットアップ（Docker + Django プロジェクト）
    ↓
Phase 1: モデル定義
  ├── 1-1: マスタ系 10 モデル
  ├── 1-2: 契約系 4 モデル
  └── 1-3: 入金・会計系モデル
    ↓
Phase 2: 認証 & 外部 API 連携
    ↓
Phase 3: テンプレート & CRUD
  ├── 3-1: 共通レイアウト + 静的ファイル
  └── 3-2: マスタ管理画面（9 種 × CRUD）
    ↓
Phase 4: 契約管理
  ├── 4-1: 一覧・検索（28 フィールドフィルタ）
  ├── 4-2: 登録・編集・削除（3 ステップフォーム）
  └── 4-3: 支払更新・番号修正・入金管理
    ↓
Phase 5: データ入出力
  ├── 5-1: CSV インポート（3 種）
  └── 5-2: Excel エクスポート（4 種）
    ↓
Phase 6: 月次締処理 & ダッシュボード
    ↓
Phase 7: テスト & 品質保証
    ↓
Phase 8: 本番デプロイ準備
```

### 技術スタック対応表

| 項目 | Laravel（移行元） | Django（移行先） |
|------|-------------------|-----------------|
| 言語 | PHP 8.0 | Python 3.11+ |
| フレームワーク | Laravel 6.20 | Django 4.2 LTS |
| ORM | Eloquent | Django ORM |
| テンプレート | Blade | Django Templates |
| フォーム | Form Request | Django Forms |
| Excel 処理 | Maatwebsite Excel | openpyxl |
| HTTP クライアント | Guzzle | httpx |
| テスト | PHPUnit | pytest-django |
| パッケージ管理 | Composer / npm | uv |
| コンテナ | PHP-FPM + Nginx | Gunicorn + Nginx |

---

## CLAUDE.md — Claude Code への「設計書」

Claude Code はプロジェクトルートの `CLAUDE.md` を自動的に読み込み、プロジェクト固有のルールとして従います。ここに移行プロジェクト特有の情報を集約しました:

```markdown
# 記載した内容の例

## DB 移行方針
- inspectdb で雛形生成、managed = True に変更
- テーブル名の typo もそのまま使用

## 設計方針
- 認証: 実際の OAuth2 フローをそのまま実装（モック不要）
- フロントエンド: 既存テーマの CSS/JS をそのまま使用
- 外部 API: ハイブリッド構成（DB キャッシュ + API クライアント）

## GraphQL クエリ名の注意
- 顧客: customer_set（Laravel コードの customers は誤り）
- フィールド: company_code（branch_code は存在しない）

## 禁止事項
- git branch / checkout / switch を実行しない
- git push を実行しない
- gh pr create / merge を実行しない
```

特に重要だったのは **「やってはいけないこと」の明示** です。Claude Code は指示がなければ自律判断しますが、禁止事項がないと予期しない操作（ブランチ切替、main への直接 push 等）を行うことがあります。これは[実行結果・教訓編](/posts/2026/03/2026-03-26-claude-code-laravel-django-migration-lessons/)で紹介する「ブランチ分岐問題」の原因にもなりました。

---

## 品質保証の設計

自律実行では人間のコードレビューが介在しないため、品質保証の仕組みを多層的に設計しました。

### 1. Pre-commit Hook
```bash
# コミット前に自動実行
uv run ruff format <staged files>
uv run ruff check --fix <staged files>
```

### 2. PostToolUse Hook（Claude Code 固有）
Claude Code がファイルを編集するたびに `ruff check` を自動実行。構文エラーやスタイル違反を即座にフィードバックします。

### 3. GitHub Actions CI
```text
push/PR → ruff format + ruff check → Django check → pytest
```

### 4. verify-phase.sh
各フェーズ完了後に実行する検証スクリプト:
- ファイル存在チェック
- lint / format チェック
- Django システムチェック
- マイグレーション整合性チェック
- テスト実行

### 5. code-reviewer サブエージェント
Claude Code 内部で別の Claude インスタンスをコードレビュアーとして起動し、セキュリティ問題やロジックエラーを検出します。実際に GraphQL インジェクション、XSS、URL エンコード漏れなどを検出・修正できました。

---

## 次回予告

計画編では「何を、なぜ、どう設計したか」を紹介しました。

次の[自動化基盤編](/posts/2026/03/2026-03-26-claude-code-laravel-django-migration-automation/)では、この計画を実際に自律実行するためのフレームワーク — `run-issue.sh` の設計と、Claude Code をどう制御するかを解説します。
