---
title: "APM（Agent Package Manager）— AI エージェント設定を npm のように管理するツール"
date: 2026-04-17
lastmod: 2026-04-17
draft: false
source_url: "https://github.com/hdknr/blogs/issues/1#issuecomment-4266529068"
categories: ["AI/LLM"]
tags: ["APM", "Claude Code", "AI エージェント", "パッケージ管理", "開発ツール"]
---

フロントエンドエキスパートの mizchi さんが「チームでの skills 共有に apm いいじゃん。採用」と [X にポスト](https://x.com/mizchi/status/2044667087290032202)して話題になった [APM（Agent Package Manager）](https://github.com/microsoft/apm)。Microsoft がオープンソースで開発しているこのツールは、AI エージェントの設定を `package.json` のように宣言的に管理・共有できます。

## APM とは

APM は **AI エージェント向けの依存関係マネージャー**です。`npm` や `pip` がライブラリ依存を管理するように、APM はエージェントが必要とするコンテキスト（スキル、プロンプト、プラグイン、MCP サーバーなど）を `apm.yml` に宣言して管理します。

対応エージェント:
- GitHub Copilot
- Claude Code
- Cursor
- OpenCode
- Codex CLI

### 解決する問題

AI コーディングエージェントを使うには、標準設定・プロンプト・スキル・プラグインといったコンテキストが必要ですが、現状は開発者が各自で手動セットアップしています。移植性がなく、再現性もありません。

APM を使えば、プロジェクトに `apm.yml` を 1 つ置くだけで、リポジトリをクローンした全員が同じエージェント環境を即座に再現できます。

## 基本的な使い方

### インストール

```bash
# macOS / Linux
curl -sSL https://aka.ms/apm-unix | sh

# Homebrew
brew install microsoft/apm/apm

# pip
pip install apm-cli
```

### apm.yml の設定例

```yaml
name: your-project
version: 1.0.0
dependencies:
  apm:
    # 任意のリポジトリからスキルを取得
    - anthropics/skills/skills/frontend-design
    # プラグイン
    - github/awesome-copilot/plugins/context-engineering
    # エージェントプリミティブ
    - github/awesome-copilot/agents/api-architect.agent.md
    # バージョン指定した APM パッケージ
    - microsoft/apm-sample-package#v1.0.0
```

### セットアップ

```bash
git clone <org/repo>
cd <repo>
apm install   # エージェント設定が一括セットアップされる
```

### マーケットプレイスからのインストール

```bash
apm marketplace add github/awesome-copilot
apm install azure-cloud-development@awesome-copilot
```

## 主な機能

### 1 つのマニフェストで全対応

`apm.yml` で以下をすべて管理できます:

- **instructions** — エージェントへの指示
- **skills** — Claude Code スキルなど
- **prompts** — プロンプトテンプレート
- **agents** — エージェント定義
- **hooks** — Claude Code hooks など
- **plugins** — GitHub Copilot・Cursor プラグイン
- **MCP サーバー** — Model Context Protocol サーバー設定

### どこからでもインストール可能

GitHub、GitLab、Bitbucket、Azure DevOps など主要な Git ホスティングサービスに対応。GitHub Enterprise も含みます。

### 推移的依存解決

パッケージがパッケージに依存できます（推移的依存）。APM が依存ツリー全体を自動解決するため、利用者は直接参照するパッケージだけ `apm.yml` に書けば済みます。

### セキュリティスキャン

```bash
apm audit   # 不正な Unicode などを検出
```

`apm install` は侵害されたパッケージをエージェントが読む前にブロックします。

### プラグイン作成と配布

```bash
apm pack    # 設定をパッケージ化（zip または standalone plugin.json）
```

Copilot・Claude・Cursor プラグインを依存管理付きで作成し、`plugin.json` 標準形式でエクスポートできます。

### CI/CD 対応

[GitHub Action](https://github.com/microsoft/apm-action) でワークフローに組み込めます。

## チームでの活用シナリオ

1. **スキル共有**: チームで使う Claude Code スキルを `apm.yml` に宣言、`apm install` で全員が同じスキルを利用
2. **プロジェクト標準化**: プロジェクトごとのエージェント設定をリポジトリに同梱
3. **オンボーディング短縮**: 新メンバーが `apm install` だけで開発環境のエージェント設定を完了

## agentrc との連携

同じく Microsoft 製の [agentrc](https://github.com/microsoft/agentrc) と組み合わせることで、コードベースを分析して最適なエージェント指示を自動生成し、APM でパッケージとして配布するワークフローが構築できます。`.instructions.md` 形式を両ツールが共有しているため変換不要です。

## まとめ

APM は「AI エージェント設定の再現性と共有」という実用的な課題を解決するツールです。Claude Code を含む主要エージェントに対応し、`npm install` の感覚でチーム全員のエージェント環境を揃えられます。

- [GitHub リポジトリ](https://github.com/microsoft/apm)
- [ドキュメント](https://microsoft.github.io/apm/)
- [クイックスタート](https://microsoft.github.io/apm/getting-started/quick-start/)
