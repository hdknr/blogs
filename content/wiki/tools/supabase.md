---
title: "Supabase"
description: "PostgreSQL ベースの BaaS プラットフォーム。Firebase のオープンソース代替。Claude Code 向け agent-skills でベストプラクティスを自動適用可能"
date: 2026-04-06
lastmod: 2026-04-16
aliases: ["supabase"]
related_posts:
  - "/posts/2025/01/supabase/"
  - "/posts/2026/03/supabase-agent-skills/"
tags: ["BaaS", "PostgreSQL", "API", "RLS", "Claude Code"]
---

## 概要

PostgreSQL を基盤とした BaaS。PostgREST でスキーマから自動 REST API 生成、PostGraphile で GraphQL 対応。AWS 上でのセルフホスト構成も Terraform で可能。Firebase ライクなコンセプトで PostgreSQL の柔軟性を備える。

## Claude Code との連携：supabase/agent-skills

Supabase が公式提供する [supabase/agent-skills](https://github.com/supabase/agent-skills) を Claude Code にインストールすることで、Supabase 固有のベストプラクティスを AI が自動的に適用できるようになる。Claude Code・Cursor・Cline など 18 以上の AI エージェントに対応。

### インストール方法

```bash
# 全スキルを一括インストール
npx skills add supabase/agent-skills

# Claude Code プラグインとして
claude plugin marketplace add supabase/agent-skills
claude plugin install supabase@supabase-agent-skills
claude plugin install postgres-best-practices@supabase-agent-skills
```

### 含まれるスキル

| スキル | 内容 |
|--------|------|
| `supabase` | Auth・Edge Functions・Realtime・Storage など全製品のベストプラクティス |
| `supabase-postgres-best-practices` | クエリ最適化・RLS・接続管理など8カテゴリのガイドライン |

## RLS パフォーマンスの注意点

Row Level Security ポリシーで `auth.uid()` をそのまま使うと、行ごとに関数が再評価されパフォーマンスが低下する。

```sql
-- ❌ 避けるべき書き方（行ごとに auth.uid() が評価される）
create policy "..." on public.records
  for select using (auth.uid() = user_id);

-- ✅ 推奨される書き方（クエリプランナーが一度だけ評価）
create policy "..." on public.records
  for select using ((select auth.uid()) = user_id);
```

agent-skills をインストールすると、Claude がこの最適な形式で自動的にコードを生成する。

## 関連ページ

- [RAG](/blogs/wiki/concepts/rag/) — Supabase Vectors を使ったベクトル検索
- [MCP](/blogs/wiki/concepts/mcp/) — Supabase MCP Server 経由の AI 連携

## ソース記事

- [Supabase](/blogs/posts/2025/01/supabase/) — 2025-01
- [Supabase × Claude Code: agent-skills でパフォーマンスと RLS の正確性を高める](/blogs/posts/2026/03/supabase-agent-skills/) — 2026-03-30
