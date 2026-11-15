---
title: "Spec Workflow MCP"
description: "要件 → 設計 → タスクの仕様づくりを支える GPL-3.0 の MCP サーバー。文書ごとに承認の依頼を出し、Web ダッシュボードや VS Code 拡張で承認・修正依頼・却下を記録する。2026 年 11 月時点でメンテナンス休止中"
date: 2026-11-15
lastmod: 2026-11-15
aliases: ["spec-workflow-mcp", "Pimzino/spec-workflow-mcp", "@pimzino/spec-workflow-mcp"]
related_posts:
  - "/posts/2026/11/spec-workflow-mcp-intro/"
  - "/posts/2026/11/spec-driven-development-overview/"
tags: ["Spec Workflow MCP", "mcp", "仕様駆動開発", "SDD", "claude-code"]
---

## 概要

**Spec Workflow MCP**（[Pimzino/spec-workflow-mcp](https://github.com/Pimzino/spec-workflow-mcp)）は、AI エージェントに [仕様駆動開発](/blogs/wiki/concepts/spec-driven-development/) の進め方を持ち込む **[MCP](/blogs/wiki/concepts/mcp/) サーバー**である。要件 → 設計 → タスクの順に文書を作り、その一つひとつを**専用の画面で人間が承認し、記録を残す**のが最大の特徴。スラッシュコマンドやスキルとして入るほかの SDD ツールと違い、MCP に対応したエージェント（Claude Code・Cursor・Codex など）ならほぼ同じ設定で使える。

ライセンスはほかの SDD ツールと違い **GPL-3.0**。使うだけなら影響は小さいが、改変して配布するなら条件を確かめる。

## 詳細

### 導入

```bash
claude mcp add spec-workflow npx @pimzino/spec-workflow-mcp@latest -- /path/to/your/project
npx -y @pimzino/spec-workflow-mcp@latest --dashboard --port 5000   # ダッシュボードは別に起動
```

Claude Desktop・Cursor・Cline は `mcpServers` の JSON、Codex は `~/.codex/config.toml` の `[mcp_servers.spec-workflow]` に同じ引数で書く。ダッシュボードのポートは README とドキュメントで既定の説明が食い違うので `--port` で明示する。ダッシュボードは 1 つで複数プロジェクトを表示できる。

### 仕様づくりと承認

チャットで「Create a spec for user authentication」「Execute task 1.2 in spec user-auth」のように頼むと、エージェントは MCP サーバーが提供する手順に従って文書を作り、承認の依頼が自動で出る。人間はダッシュボードか VS Code 拡張で **Approve（承認）／Request Changes（コメント付きで修正依頼）／Reject（要件からやり直し）** を選ぶ。チャットで「OK」と返すのではなく、承認が記録として残る。

現在のソースで登録されている MCP ツールは `spec-workflow-guide`・`steering-guide`・`spec-status`・`approvals`・`log-implementation` の 5 つ（ドキュメントのツール一覧はこれより多く、ソースと合っていない）。

### 作られるファイル

| 置き場所 | 内容 |
|---|---|
| `.spec-workflow/specs/<仕様名>/` | `requirements.md`・`design.md`・`tasks.md` |
| `.spec-workflow/steering/` | `product.md`・`tech.md`・`structure.md` |
| `.spec-workflow/templates/` | 差し替え可能なテンプレート |
| `.spec-workflow/archive/` | 完了した仕様 |

文書構成は [Kiro](/blogs/wiki/tools/kiro/) とよく似ている。

### ダッシュボードと VS Code 拡張

Web ダッシュボードは進行中の仕様・タスク数・完了率、各文書、タスクを実装させるプロンプトのコピー、承認操作を WebSocket でリアルタイムに表示する。既定は `127.0.0.1` で待ち受ける。VS Code 拡張（`Pimzino.spec-workflow-mcp`）はサイドバーでほぼ同等の操作ができ、仕様のアーカイブなどダッシュボードにない機能もある。

### 使う前の注意点（2026 年 11 月時点）

- **メンテナンス休止中**：作者が個人的な理由で離れている旨が README の冒頭にあり、最後の push は 2026 年 7 月
- **npm の版に最新の修正がない**：`@latest` で入るのは 2.2.5（2026 年 3 月）。CHANGELOG の 2.2.7（承認カテゴリのパストラバーサル修正、simple-git の深刻な脆弱性対応）は npm 未公開
- **ダッシュボードに HTTPS と認証がない**：`127.0.0.1` のまま使い、外部に公開しない
- **ドキュメントの一部が古い**：ツール一覧やポートの説明が実装と合わない

承認を画面で記録できる仕組みは魅力だが、業務で使うならこれらを踏まえてリスクを判断する。承認の記録が欲しいだけなら、承認を git タグで残してスクリプトで照合する [要求仕様書作成ループ](/blogs/wiki/concepts/requirements-spec-loop/) のような方法もある。

## 関連ページ

- [仕様駆動開発（SDD）](/blogs/wiki/concepts/spec-driven-development/) — ツール比較と選び方
- [MCP (Model Context Protocol)](/blogs/wiki/concepts/mcp/) — このツールが乗るプロトコル
- [Kiro](/blogs/wiki/tools/kiro/) — よく似た文書構成の AI IDE
- [cc-sdd](/blogs/wiki/tools/cc-sdd/) / [GitHub Spec Kit](/blogs/wiki/tools/github-spec-kit/) — スキル・コマンド型の SDD ツール
- [Claude Code](/blogs/wiki/tools/claude-code/) — `claude mcp add` で登録する

## ソース記事

- [Spec Workflow MCP とは？ ダッシュボードで仕様を承認しながら進める MCP サーバーの使い方と注意点](/blogs/posts/2026/11/spec-workflow-mcp-intro/) — 2026-11-13
- [仕様駆動開発（SDD）とは？ 3 つのアプローチ・EARS 記法・Kiro / Spec Kit・TDD との違い](/blogs/posts/2026/11/spec-driven-development-overview/) — 2026-11-13
