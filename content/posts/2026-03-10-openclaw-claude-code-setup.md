---
title: "OpenClaw × Claude Code セットアップガイド — AI エージェントチームを構築する2つのアプローチ"
date: 2026-03-10
lastmod: 2026-03-10
draft: false
categories: ["AI/LLM"]
tags: ["claude-code", "openclaw", "agent", "mcp"]
---

OpenClaw と Claude Code を組み合わせることで、AI エージェントチームの構築・管理を効率化できます。本記事では、2つの主要な連携アプローチとそのセットアップ方法を解説します。

## アプローチ1: Claude Code のスキルで OpenClaw を管理する

Claude Code のスキル機能（`.claude/skills/` に配置する Markdown ファイル）を使い、OpenClaw のエージェント作成・設定管理を標準化する方法です。

### なぜスキルで管理するのか

複数の AI エージェントを運用していると、以下の問題が発生します:

- モデルやコンテキストの違いによる設定の不統一
- タイムゾーンフィールドの欠落、命名規則の不一致
- スキーマ検証やコミットフックによる検証が存在しない

Claude Code スキルは「実行可能な基準」として機能し、モデルに依存せず一貫した手順を強制します。

### セットアップ

[cc-openclaw](https://github.com/rahulsub-be/cc-openclaw) リポジトリを使います:

```bash
git clone https://github.com/rahulsub-be/cc-openclaw.git ~/cc-openclaw
cd ~/cc-openclaw
stow --no-folding -t ~/your-openclaw-home-repo .
```

スキルはリポジトリの位置を動的に判定します:

```bash
OPENCLAW_REPO=$(readlink ~/.openclaw/openclaw.json 2>/dev/null | sed 's|/.openclaw/openclaw.json||')
```

### 利用可能なスキル一覧

| スキル | 機能 |
|-------|------|
| `/openclaw-new-agent` | エージェント作成（ディレクトリ構造・6つの Markdown ファイルを自動生成） |
| `/openclaw-add-channel` | メッセージングチャネル追加（複数プラットフォーム対応） |
| `/openclaw-add-cron` | スケジュール設定（タイムゾーン自動処理） |
| `/openclaw-dream-setup` | メモリ蒸留ルーチン設定 |
| `/openclaw-add-script` | スクリプト生成（テンプレート自動使用） |
| `/openclaw-add-secret` | シークレット管理（3ファイル同時更新） |
| `/openclaw-status` | ダッシュボード表示 |
| `/openclaw-restart` | ゲートウェイ再起動 |
| `/openclaw-stow` | デプロイメント実行 |

### 使用例

```bash
# Claude Code 内で実行
/openclaw-new-agent devin-jr "Devin Junior"
```

これだけで、Claude Code がディレクトリ作成、ファイル生成、JSON 編集、stow 実行、ゲートウェイ再起動までを一括で行います。

## アプローチ2: OpenClaw から Claude Code を MCP 経由で呼び出す

[openclaw-claude-code-skill](https://github.com/Enderfga/openclaw-claude-code-skill) を使い、OpenClaw のエージェントが Claude Code の開発機能を利用する方法です。

### インストール

```bash
git clone https://github.com/Enderfga/openclaw-claude-code-skill.git
cd openclaw-claude-code-skill
npm install
npm run build
npm link  # グローバルにリンク（オプション）
```

### 前提条件

- Node.js 18 以上
- Claude Code CLI（`npm install -g @anthropic-ai/claude-code`）

### 環境設定

```bash
export BACKEND_API_URL="http://127.0.0.1:18795"
```

### 基本コマンド

```bash
# セッション開始
claude-code-skill session-start myproject -d ~/project

# タスクを送信（ストリーミング出力）
claude-code-skill session-send myproject "テストを追加して" --stream

# セッション状態の確認
claude-code-skill session-status myproject

# セッション終了
claude-code-skill session-stop myproject
```

### MCP サーバー設定

`mcp_config.json` でツール連携を設定できます:

```json
{
  "mcpServers": {
    "filesystem": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem", "/path/to/workspace"]
    }
  }
}
```

### セッションオプション

```bash
claude-code-skill session-start myproject \
  -d ~/project \
  --model claude-opus-4-6 \
  --permission-mode bypassPermissions \
  --allowed-tools "Bash(git:*,npm:*),Read,Edit" \
  --max-budget 5.00
```

## どちらを選ぶべきか

| 観点 | アプローチ1（スキル管理） | アプローチ2（MCP 連携） |
|------|------------------------|----------------------|
| 主な用途 | OpenClaw の設定・運用管理 | 開発タスクの委譲 |
| 操作する人 | 人間（Claude Code 経由） | OpenClaw エージェント |
| 強み | 設定の一貫性・標準化 | コーディング能力の活用 |
| 適したシーン | エージェントの追加・変更が頻繁 | 開発系タスクを自動化したい |

両方を併用することも可能です。日常業務は OpenClaw エージェントが処理し、開発タスクが発生したら MCP 経由で Claude Code に委譲する構成が実用的です。

## OpenClaw スキルの自作

Claude Code を使って OpenClaw 用のカスタムスキルを開発することもできます。基本的な流れは以下の通りです:

1. `pnpm` で OpenClaw 開発環境をセットアップ
2. `manifest.json` と `skill.ts` でスキルを定義
3. Vitest でテストを記述
4. `pnpm dev` でローカルテスト
5. Docker またはクラウドにデプロイ

詳しくは [Building OpenClaw Skills with Claude Code](https://claude-world.com/articles/building-openclaw-skills-with-claude-code/) を参照してください。

## 参考リンク

- [Managing OpenClaw with Claude Code](https://trilogyai.substack.com/p/managing-openclaw-with-claude-code)
- [openclaw-claude-code-skill (GitHub)](https://github.com/Enderfga/openclaw-claude-code-skill)
- [everything-claude-code: The OpenClaw Guide](https://github.com/affaan-m/everything-claude-code/blob/main/the-openclaw-guide.md)
- [OpenClaw vs Claude Code (DataCamp)](https://www.datacamp.com/blog/openclaw-vs-claude-code)
