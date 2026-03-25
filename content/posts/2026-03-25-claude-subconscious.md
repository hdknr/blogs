---
title: "Claude Subconscious：Claude Code にセッション横断の記憶力を与える Letta AI のオープンソースツール"
date: 2026-03-25
lastmod: 2026-03-25
draft: false
source_url: "https://github.com/hdknr/blogs/issues/1#issuecomment-4122425202"
categories: ["AI/LLM"]
tags: ["claude-code", "claude", "agent", "llm"]
---

Claude Code は強力な AI コーディングエージェントだが、セッションをまたいだ記憶の保持には課題があった。[Claude Subconscious](https://github.com/letta-ai/claude-subconscious) は、Letta AI が開発したオープンソースのプラグインで、Claude Code にバックグラウンドで動作する永続メモリを追加する。

## Claude Subconscious とは

Claude Subconscious は、Claude Code のセッションをバックグラウンドで監視し、ユーザーの作業パターンや好み、未完了のタスクを学習・記憶するエージェントだ。次のセッション開始時に、蓄積した記憶をプロンプトに自動注入することで、毎回ゼロからのスタートではなく、文脈を引き継いだ作業が可能になる。

主な特徴:

- **セッション横断の記憶**: 複数セッションをまたいで作業コンテキストを保持・統合
- **バックグラウンド動作**: Claude Code の操作をブロックせず、非同期で動作
- **自動コンテキスト注入**: プロンプトの前に関連する記憶やガイダンスを自動挿入
- **コードベースの探索**: Read、Grep、Glob ツールを使ってプロジェクトのコードを読み取り、理解を深める
- **完全無料・オープンソース**: [GitHub リポジトリ](https://github.com/letta-ai/claude-subconscious) で公開中

## 仕組み

Claude Subconscious は Claude Code のフックシステムを利用して、4 つのタイミングで介入する:

1. **SessionStart** — エージェントに通知し、レガシーファイルをクリーンアップ
2. **UserPromptSubmit** — 記憶とメッセージを stdout 経由で注入（10 秒タイムアウト）
3. **PreToolUse** — ワークフロー中の更新を配信（5 秒タイムアウト）
4. **Stop** — セッションのトランスクリプトをバックグラウンドエージェントに非同期送信

バンドルされたエージェントは 8 つのメモリブロックを管理する:

| メモリブロック | 用途 |
|---|---|
| `core_directives` | 役割定義 |
| `guidance` | アクティブセッションのガイダンス |
| `user_preferences` | 学習したコーディングスタイル |
| `project_context` | コードベースの知識 |
| `session_patterns` | 繰り返しの行動パターン |
| `pending_items` | 未完了の作業 |
| `self_improvement` | メモリ進化のガイドライン |
| `tool_guidelines` | ツール使用の指針 |

## インストール方法

Claude Code のプラグインシステムを使って 2 コマンドでインストールできる:

```bash
/plugin marketplace add letta-ai/claude-subconscious
/plugin install claude-subconscious@claude-subconscious
```

Letta の API キーが必要となる。[app.letta.com](https://app.letta.com) で取得可能だ。

## 設定オプション

環境変数で動作をカスタマイズできる:

```bash
# 必須
LETTA_API_KEY=your-api-key

# オプション
LETTA_MODE=whisper    # whisper（デフォルト）/ full / off
LETTA_AGENT_ID=...    # カスタムエージェント指定
LETTA_BASE_URL=...    # セルフホストの場合
LETTA_MODEL=...       # モデルのオーバーライド
```

`LETTA_MODE` の設定:

- **whisper**（デフォルト）: エージェントのメッセージのみ注入
- **full**: メモリブロック + メッセージを注入
- **off**: すべてのフックを無効化

## マルチプロジェクト対応

1 つの共有エージェントがすべてのプロジェクトを横断して統合メモリを維持する。各プロジェクトは独自の会話スレッドマッピングを持つ。プロジェクトごとに異なるエージェントを使いたい場合は、`LETTA_AGENT_ID` を環境変数や direnv で設定すればよい。

## Claude Code 標準メモリ機能との比較

Claude Code 自体もセッション間の記憶機能を標準で提供している。ここでは両者を詳しく比較する。

### Claude Code 標準のメモリシステム

Claude Code には 2 つの補完的なメモリ機構がある:

1. **CLAUDE.md ファイル**: ユーザーが手動で記述するプロジェクト指示書。コーディング規約、ビルドコマンド、アーキテクチャ決定などを記載する。プロジェクトルート、ユーザーホーム、組織レベルなど複数のスコープで配置可能
2. **Auto Memory（自動メモリ）**: Claude が自ら学習内容をメモとして保存する機能（v2.1.59 以降、デフォルト有効）。`~/.claude/projects/<project>/memory/` に `MEMORY.md` とトピック別ファイルとして保存される

### 比較表

| 観点 | Claude Code 標準メモリ | Claude Subconscious |
|---|---|---|
| **開発元** | Anthropic（公式） | Letta AI（サードパーティ） |
| **CLAUDE.md** | ユーザーが手動で記述 | 利用しない |
| **Auto Memory** | Claude が自動保存（ローカルファイル） | Letta サーバーに記憶を蓄積 |
| **記憶の保存先** | ローカルの Markdown ファイル | Letta クラウド（またはセルフホスト） |
| **記憶の仕組み** | セッション開始時に MEMORY.md の先頭 200 行を読み込み | フックで毎プロンプト前にコンテキスト注入 |
| **学習タイミング** | Claude が必要と判断した時に保存 | バックグラウンドエージェントが常時監視・学習 |
| **プロジェクト横断** | プロジェクトごとに独立 | 1 エージェントで全プロジェクト共有可能 |
| **外部依存** | なし | Letta API キーが必要 |
| **セットアップ** | 設定不要（デフォルト有効） | プラグインインストール + API キー取得 |
| **データの場所** | 完全ローカル | Letta サーバー（クラウド or セルフホスト） |
| **カスタマイズ性** | MEMORY.md を直接編集可能 | 環境変数でモード切替、エージェント設定変更 |

### どちらを選ぶべきか

**Claude Code 標準メモリが向いているケース:**

- 外部サービスへの依存を避けたい
- プロジェクトの指示を明示的にバージョン管理したい（CLAUDE.md）
- シンプルな構成で十分な場合
- チームで共有する指示が中心の場合

**Claude Subconscious が向いているケース:**

- 手動でメモリファイルを管理したくない
- より積極的な自動学習を求める場合
- 複数プロジェクトを横断した統一的な記憶が欲しい場合
- セッション中のリアルタイムなコンテキスト注入が必要な場合

両者は排他的ではなく、併用も可能だ。CLAUDE.md でプロジェクトの基本ルールを定義し、Claude Subconscious で動的な学習を補完するという使い方もできる。

## まとめ

Claude Code の標準メモリ機能（CLAUDE.md + Auto Memory）は、公式のシンプルかつ堅実なソリューションだ。一方、Claude Subconscious は Letta AI が提供するサードパーティのプラグインで、バックグラウンドエージェントによるより積極的な自動学習とリアルタイム注入を特徴とする。プロジェクトの規模や要件に応じて、標準機能だけで済ませるか、Claude Subconscious で拡張するかを選択できる。
