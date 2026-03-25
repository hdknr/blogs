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

## Claude Code 標準のメモリ機能との違い

Claude Code 自体にも `CLAUDE.md` ファイルによるプロジェクトメモリ機能がある。Claude Subconscious はこれを補完する形で、より動的で自動的な記憶管理を提供する。手動でメモリファイルを管理する必要がなく、セッション中の行動を自動的に学習・蓄積していく点が特徴的だ。

## まとめ

Claude Subconscious は、Claude Code の「毎回リセットされる記憶」という課題に対する実用的なソリューションだ。Letta AI が開発・公開しているオープンソースプロジェクトであり、Claude Code のプラグインとして簡単に導入できる。コーディングスタイルの学習やプロジェクトコンテキストの維持により、AI コーディングエージェントとの協業をよりスムーズにしてくれる。
