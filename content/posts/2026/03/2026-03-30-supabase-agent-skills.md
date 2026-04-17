---
title: "Supabase × Claude Code: agent-skills でパフォーマンスと RLS の正確性を高める"
date: 2026-03-30
lastmod: 2026-04-17
draft: false
source_url: "https://github.com/hdknr/blogs/issues/1#issuecomment-4157861135"
categories: ["AI/LLM"]
tags: ["Supabase", "Claude Code", "RLS", "PostgreSQL", "パフォーマンス"]
---

## Supabase とは

[Supabase](https://supabase.com) は **Firebase のオープンソース代替** として急成長している BaaS（Backend as a Service）だ。PostgreSQL をベースに、認証・リアルタイムデータベース・ストレージ・Edge Functions をワンストップで提供する。

- **PostgreSQL がそのまま使える** — 独自のクエリ言語ではなく標準 SQL
- **Row Level Security (RLS)** — テーブル単位でアクセス制御ポリシーを定義
- **自動生成 REST API** — テーブル定義から即座に CRUD API が生成される
- **オープンソース** — セルフホスティングも可能
- **無料枠あり** — 個人プロジェクトなら無料で始められる

Firebase との最大の違いは「中身が PostgreSQL」である点だ。NoSQL ではなく RDB なので、既存の SQL 知識がそのまま活かせる。

---

Supabase を使っているプロジェクトで Claude Code を活用している場合、公式の `supabase/agent-skills` をインストールするだけでコード品質とパフォーマンスが大幅に向上する。特に Row Level Security (RLS) の書き方ミスを防ぐ効果が高い。

## なぜ agent-skills が必要なのか

Claude Code は Supabase の細かいベストプラクティスをデフォルトでは把握していない。たとえば RLS ポリシーで頻出する次のパターンを考えてほしい。

```sql
-- ❌ Claude がデフォルトで書きがちなコード
create policy "users can view own records" on public.records
  for select using (auth.uid() = user_id);

-- ✅ パフォーマンスを考慮した正しい書き方
create policy "users can view own records" on public.records
  for select using ((select auth.uid()) = user_id);
```

`auth.uid()` をそのまま使うとクエリの行ごとに関数が評価されるが、`(select auth.uid() as uid)` のようにサブクエリ化することでクエリプランナーが一度だけ評価するよう最適化できる。これによってテーブルスキャン時のパフォーマンスが大幅に改善する。

`supabase/agent-skills` はこのような Supabase 固有のベストプラクティスを Claude Code に認識させるためのスキル集だ。

## supabase/agent-skills とは

[supabase/agent-skills](https://github.com/supabase/agent-skills) は Supabase が公式に提供している Agent Skills リポジトリで、Claude Code・GitHub Copilot・Cursor・Cline など 18 以上の AI エージェントに対応している。

含まれているスキルは主に 2 つ:

### `supabase` スキル

Supabase 全製品をカバーする包括的なスキル。以下を含む:

- Database、Auth、Edge Functions、Realtime、Storage、Vectors、Cron、Queues
- `supabase-js`、`@supabase/ssr` などのクライアントライブラリ
- Next.js、React、SvelteKit、Astro、Remix との SSR 統合
- RLS・セッション・JWT・Cookie の認証トラブルシューティング
- Supabase CLI および MCP サーバーの使い方
- スキーマ変更、マイグレーション、セキュリティ監査、`pg_graphql`・`pg_cron`・`pg_vector` などの Postgres 拡張

### `supabase-postgres-best-practices` スキル

Supabase が提供する Postgres パフォーマンス最適化ガイドライン。8 カテゴリに渡る参考資料がインパクト順に整理されている:

| カテゴリ | 優先度 |
|---|---|
| Query Performance | Critical |
| Connection Management | Critical |
| Security & RLS | Critical |
| Schema Design | High |
| Concurrency & Locking | Medium-High |
| Data Access Patterns | Medium |
| Monitoring & Diagnostics | Low-Medium |
| Advanced Features | Low |

## インストール方法

### npx を使う（全スキル一括）

```bash
npx skills add supabase/agent-skills
```

### 特定のスキルのみインストール

```bash
npx skills add supabase/agent-skills --skill supabase
npx skills add supabase/agent-skills --skill supabase-postgres-best-practices
```

### Claude Code プラグインとしてインストール

```bash
# 1. マーケットプレイスに追加
claude plugin marketplace add supabase/agent-skills

# 2. 使いたいプラグインをインストール
claude plugin install supabase@supabase-agent-skills
claude plugin install postgres-best-practices@supabase-agent-skills
```

グローバルにインストールすれば、すべての Supabase プロジェクトで自動的に適用される。

## インストール後の効果

スキルをインストールした状態で Claude Code に Supabase 関連のコードを書かせると:

- RLS ポリシーを `(select auth.uid())` 形式で正しく生成する
- インデックス設計のベストプラクティスが自動的に考慮される
- Row Level Security とパフォーマンスの両立が取りやすくなる
- Supabase 公式 CLI コマンドの構文ミスが減る

## まとめ

Supabase + Claude Code の組み合わせを使っているなら、`supabase/agent-skills` のインストールは必須レベルの設定だ。特に RLS のパフォーマンス問題は見落とされやすく、データ量が増えてから気づくことが多い。事前にスキルを入れておくことで、AI が生成するコードの品質を底上げできる。

詳細なインストール手順は [Supabase AI Skills 公式ドキュメント](https://supabase.com/docs/guides/getting-started/ai-skills) を参照してほしい。
