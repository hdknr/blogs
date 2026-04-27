---
title: "ANOLISA"
description: "Alibaba が公開した AI Agent 向け Linux OS（Agentic OS）。Copilot Shell / Agent Sec Core / AgentSight / OS Skills の 4 コンポーネント構成"
date: 2026-04-23
lastmod: 2026-04-23
aliases: ["anolisa", "Agentic OS", "Alibaba Anolisa"]
related_posts:
  - "/posts/2026/04/2026-04-21-alibaba-anolisa-agentic-os/"
tags: ["alibaba", "agent", "ebpf", "agentic-os", "security", "linux"]
---

## 概要

Alibaba が 2026 年 3 月に公開した Agentic OS プロジェクト。正式名称は **ANOLISA**（Agentic Nexus Operating Layer & Interface System Architecture）。同社が保守する Anolis OS を AI Agent 実行基盤として再構築したもので、権限・観測・スキル管理を OS 層で解決する。Apache 2.0 ライセンス。

- リポジトリ: [alibaba/anolisa](https://github.com/alibaba/anolisa)
- ホームページ: [agentic-os.sh](https://agentic-os.sh)
- 主言語: TypeScript（Copilot Shell）/ Rust（AgentSight）/ C（eBPF プローブ）

## 4 コンポーネント

| Component | 役割 |
|-----------|------|
| **Copilot Shell（cosh）** | Qwen Code ベースの AI ターミナル UI。Multi-Provider・PTY・Skill/Hooks System 対応 |
| **Agent Sec Core** | OS 層セキュリティカーネル。最小権限・明示的認可・ゼロトラスト・多層防御・Security Over Execution の 5 原則 |
| **AgentSight** | eBPF ベースのゼロ侵襲 Agent オブザーバビリティ。LLM API コール・トークン消費・SSL/TLS トラフィックをカーネル側から観測 |
| **OS Skills** | 運用スキルの標準ライブラリ。RPM で `/usr/share/anolisa/skills/` に展開 |

## Agent Sec Core のセキュリティモデル

Agent 実行のたびに 3 フェーズのチェックが強制される:

1. システム堅牢化スキャン（`loongshield seharden`）
2. 全スキルの GPG 署名と SHA-256 ハッシュ検証
3. Phase 1 + Phase 2 の再確認

リスク区分は 4 段階で、コマンド種別ごとに `read-only` / `workspace-write` / `danger-full-access` のサンドボックステンプレートが割り当てられる。`~/.ssh/`・API トークン・`/etc/shadow` 等の保護対象資産は Agent から触れないことが OS 側で保証される。

## AgentSight の eBPF プローブ

| Probe | 役割 |
|-------|------|
| **sslsniff** | `SSL_read/SSL_write` に uprobe を仕掛け、暗号化前後の平文を捕捉 |
| **proctrace** | `execve` シスコールをトレースし、コマンドライン引数とプロセス木を記録 |
| **procmon** | プロセスの生成・終了を軽量監視し、AI Agent を自動発見 |

SSE（Server-Sent Events）解析でストリーミング応答のトークン数も正確に計測できる。

## OS 層実装の意義

アプリケーション層のラッパーでは補えない「権限・観測・再現性」の問題を OS 側の責務として解決する。Copilot Shell 以外の Agent（Claude Code、OpenClaw など）からも Agent Sec Core / AgentSight を共有利用できる。

## 関連ページ

- [AI エージェント](/blogs/wiki/concepts/ai-agent/) — ANOLISA が実行基盤を提供する対象
- [Claude Code](/blogs/wiki/tools/claude-code/) — ANOLISA の OS Skills で install-claude-code スキルが提供される
- [openclaw](/blogs/wiki/tools/openclaw/) — Agent Sec Core が適用可能な別の Agent OS

## ソース記事

- [ANOLISA とは — Alibaba が公開した AI Agent 向け Linux OS](/blogs/posts/2026/04/2026-04-21-alibaba-anolisa-agentic-os/) — 2026-04-21
