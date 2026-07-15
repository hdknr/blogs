---
title: "ECC（Everything Claude Code）— 220K スターのClaude Code 最強エコシステムガイド"
date: 2026-06-24
lastmod: 2026-06-24
slug: "everything-claude-code-ecc"
draft: false
source_url: "https://github.com/hdknr/blogs/issues/1#issuecomment-4785315257"
categories: ["AI/LLM"]
description: "ECC（Everything Claude Code）は Claude Code 向けのエージェント67種・スキル271種・フック・MCP設定・AgentShieldを網羅したオープンソースエコシステム。インストール方法と主要コンポーネントを解説する。"
tags: ["claude-code", "ecc", "agent", "mcp", "hooks", "security", "claude"]
---

Claude Code を使っているなら、ぜひ確認しておきたいリポジトリがある。**ECC（Everything Claude Code）**だ。

スキル・エージェント・フック・MCP・ワークフローを網羅した、Claude Code 向けの総合コレクション。220K を超えるスターを獲得し、230 名以上のコントリビューターが参加するオープンソースプロジェクトとして急速に成長している。

## ECC とは何か

ECC は「エージェントハーネスのオペレーティングシステム」と位置づけられている。単なる設定ファイルの集まりではなく、スキル・インスティンクト（セッションから抽出した行動パターンの保存単位）・メモリ最適化・継続的学習・セキュリティスキャン・リサーチファーストな開発のための**完結したシステム**だ。

- **リポジトリ**: [affaan-m/ECC](https://github.com/affaan-m/ECC)
- **ライセンス**: MIT
- **バージョン**: v2.0.0（2026年6月リリース）
- **対応ハーネス**: Claude Code、Codex、Cursor、OpenCode、Gemini、Zed、GitHub Copilot

10ヶ月以上にわたる実プロダクト開発での日常的な使用から進化したもので、実践的なワークフローパターンが詰まっている。

## 主要コンポーネント

ECC は以下の主要コンポーネントで構成される。

### エージェント（67種）

専門タスクに委譲するサブエージェントが 67 種類用意されている。

| エージェント | 役割 |
|---|---|
| `planner` | 機能実装の計画 |
| `architect` | システム設計の判断 |
| `code-reviewer` | コード品質・セキュリティレビュー |
| `security-reviewer` | 脆弱性分析 |
| `tdd-guide` | テスト駆動開発 |
| `go-reviewer` / `python-reviewer` | 言語特化レビュー |
| `loop-operator` | 自律ループ実行 |
| `mle-reviewer` | 本番MLパイプラインのレビュー |

### スキル（271種）

スキルは Claude Code の主要な操作インタフェース。コーディングスタンダードから機械学習ワークフローまで幅広く揃っている。

```text
skills/
├── backend-patterns/       # API・DB・キャッシュ
├── frontend-patterns/      # React・Next.js
├── tdd-workflow/           # テスト駆動開発
├── security-review/        # セキュリティチェックリスト
├── eval-harness/           # 検証ループ評価
├── continuous-learning-v2/ # インスティンクトベースの継続学習
├── autonomous-loops/       # 自律ループパターン
├── mle-workflow/           # 本番MLデータ契約・評価・デプロイ
├── django-patterns/        # Django パターン
├── springboot-patterns/    # Java Spring Boot
├── golang-patterns/        # Go イディオム
└── liquid-glass-design/    # iOS 26 Liquid Glass デザイン
```

特に注目は `continuous-learning-v2`。セッションから学習したパターンを「インスティンクト（instinct）」として保存し、将来のセッションで再利用する仕組みだ。詳細な動作については[こちらの記事](/blogs/posts/2026/04/ecc-instinct-system/)で解説している。

### フック

Claude Code のツールイベントに反応する自動化。セッション開始・終了時のメモリ永続化、コンパクション提案、パターン抽出などが含まれる。

```json
{
  "matcher": "tool == \"Edit\" && tool_input.file_path matches \"\\.(ts|tsx)$\"",
  "hooks": [{
    "type": "command",
    "command": "grep -n 'console\\.log' \"$file_path\" && echo '[Hook] console.log を削除してください' >&2"
  }]
}
```

フックのプロファイルは環境変数で制御できる。

```bash
export ECC_HOOK_PROFILE=minimal   # 最小限
export ECC_HOOK_PROFILE=standard  # 標準（デフォルト）
export ECC_HOOK_PROFILE=strict    # 厳格
```

### ルール

`~/.claude/rules/ecc/` に配置する「常時適用ガイドライン」。

```text
rules/
├── common/       # 言語非依存の原則（必ずインストール）
├── typescript/   # TypeScript/JavaScript
├── python/       # Python
├── golang/       # Go
├── swift/        # Swift
└── php/          # PHP
```

### MCP 設定

`mcp-configs/mcp-servers.json` に GitHub・Supabase・Vercel・Railway などの MCP サーバー設定がまとまっている。

## インストール方法

### プラグインインストール（推奨）

Claude Code のプラグイン機能から直接インストールできる。

```bash
/plugin marketplace add https://github.com/affaan-m/ECC
/plugin install ecc@ecc
```

これだけで 67 エージェント・271 スキル・92 レガシーコマンドシム（v1 系の `/コマンド` 形式との後方互換レイヤー）が使える状態になる。

**注意**: プラグイン経由では `rules/` は配布されない。ルールは手動でコピーする必要がある。

```bash
git clone https://github.com/affaan-m/ECC.git
cd ECC
mkdir -p ~/.claude/rules/ecc
cp -r rules/common ~/.claude/rules/ecc/
cp -r rules/typescript ~/.claude/rules/ecc/   # 使用スタックに合わせて選択
```

### 手動インストール

より細かいコントロールが必要な場合：

```bash
# エージェントをコピー
cp agents/*.md ~/.claude/agents/

# スキルをコピー
mkdir -p ~/.claude/skills
cp -r skills/search-first ~/.claude/skills/

# フックのインストール
bash ./install.sh --target claude --modules hooks-runtime
```

**重要**: プラグイン経由と手動インストールを重複させないこと。二重インストールは動作の重複を引き起こす。

## 注目ツール

### AgentShield — セキュリティ監査ツール

Claude Code の設定ファイル（CLAUDE.md、settings.json、MCP設定、フック、エージェント定義）に潜む脆弱性を自動検出する。

```bash
# クイックスキャン（インストール不要）
npx ecc-agentshield scan

# 安全な問題は自動修正
npx ecc-agentshield scan --fix

# Claude Opus 4.6 の3エージェントによる深掘り分析
npx ecc-agentshield scan --opus --stream
```

`--opus` フラグを使うと、攻撃者・防御者・監査者の3エージェントが連携する。レッドチーム/ブルーチーム/監査パイプラインで動作し、優先度付きリスク評価を生成する。1282 テスト・102 ルールに基づく静的解析だ。

### 継続学習システム

セッションからパターンを自動抽出して、インスティンクトとして蓄積する。

```bash
/instinct-status    # 学習済みインスティンクトを確認（信頼度付き）
/instinct-import    # 他者のインスティンクトをインポート
/instinct-export    # 自分のインスティンクトをエクスポート
/evolve             # 関連インスティンクトをスキルにクラスタリング
```

### スキルクリエーター

リポジトリの git 履歴を分析して、プロジェクト固有のスキルを自動生成する。

```bash
/skill-create               # 現在のリポジトリを分析
/skill-create --instincts   # インスティンクトも生成
```

## 使い方の参考コマンド

```bash
# 機能実装の計画
/ecc:plan "ユーザー認証を追加"

# コードレビュー
/code-review

# ビルドエラーの修正
/build-fix

# Go テスト
/go-test

# PM2 サービス管理
/pm2

# マルチエージェントタスク分解
/multi-plan
```

## まとめ

ECC は Claude Code ユーザーにとって非常に価値のあるリソースだ。何かをインストールしなくても、リポジトリを眺めるだけで、エージェントの設計方法・スキルの書き方・フックの活用パターンについて多くのアイデアを得られる。

まずプラグインインストールで試してみて、気に入ったコンポーネントだけを選んで使うのが現実的な始め方だ。Claude Code を本格的に活用したいなら、ぜひリポジトリを一度確認してみてほしい。

### 関連記事

- [ECC の instinct システム詳解](/blogs/posts/2026/04/ecc-instinct-system/)
- [Claude Code のフック・カスタムコマンド・サブエージェント解説](/blogs/posts/2026/03/claude-code-hooks-commands-subagents/)
- [Claude Code スキルクリエーター](/blogs/posts/2026/03/claude-code-skill-creator/)
