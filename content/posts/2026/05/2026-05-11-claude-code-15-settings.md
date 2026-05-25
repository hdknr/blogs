---
title: "ほとんどの人が知らない Claude Code の 15 設定 — 思考深度デフォルト変更の真相と本来の性能を取り戻す方法"
date: 2026-05-11
lastmod: 2026-05-11
slug: "claude-code-15-settings"
draft: false
source_url: "https://github.com/hdknr/blogs/issues/1#issuecomment-4424520058"
categories: ["AI/LLM"]
tags: ["claude-code", "claude", "llm", "anthropic", "mcp"]
---

2026 年 3 月、Anthropic は Claude Code の思考深度（thinking effort）のデフォルト値を **`high` から `medium` に静かに変更した**。
リリースノートには目立つ記述がなく、多くの開発者は「最近 Claude の質が落ちた気がする」と感じながら原因を見つけられずにいた。

Claude Code の開発者である Boris Cherny 氏が Hacker News でこの変更を認め、その後 AI 開発者コミュニティで 15 の重要設定がまとめられて話題になった。
本記事ではそれらを日本語で解説する。

## 1. 思考深度（effort level）の復元

**問題：** 2026 年 3 月以降、デフォルトが `medium` に変更された。Claude の思考回数が減り、コードの質・ツール呼び出し数・コメントの充実度すべてが低下している。

**修正方法：** セッション内で一時的に変更する場合は `/effort high`、恒久的に変更する場合はシェル設定に追記する。

```bash
export CLAUDE_CODE_EFFORT_LEVEL=high
```

本格的なコーディング作業では `high` または `max` を設定することで、2026 年 2 月以前の品質に戻せる。

## 2. Adaptive thinking の無効化

**問題：** 2026 年 2 月以降、Claude はタスクの複雑さを自己判断して推論量を動的に調整するようになった。「簡単なタスク」と判断した場合はほぼ思考せず、バグを見逃すことがある。

**修正方法：**

```bash
export CLAUDE_CODE_DISABLE_ADAPTIVE_THINKING=1
```

これで毎ターン固定の推論バジェットが確保され、Claude が手を抜かなくなる。

## 3. デフォルト permission モードの変更

**問題：** デフォルトモードではほぼすべてのツール呼び出しに確認が入る。ある開発者は午前中だけで 47 回の確認プロンプトを数えた。

**修正方法：** `settings.json` に追記する。

```json
{
  "permissions": {
    "defaultMode": "acceptEdits"
  }
}
```

利用可能なモードは `default`、`acceptEdits`、`plan`、`auto`、`dontAsk`、`bypassPermissions` の 6 種類。よく知っているプロジェクトでは `acceptEdits`、不慣れなリポジトリでは `plan` が推奨。セッション途中でも `Shift+Tab` で切り替えられる。

## 4. Allow / Deny ルールの設定

**問題：** allow ルールがないと `npm install`、`git commit`、テスト実行のたびに確認が求められる。deny ルールがないと `.env` や `.ssh` を Claude が読み取れてしまう。

**修正方法：**

```json
{
  "permissions": {
    "allow": [
      "Read", "Glob", "Grep", "LS", "Edit",
      "Bash(npm run *)", "Bash(git status)", "Bash(git diff *)",
      "Bash(git add *)", "Bash(git commit *)"
    ],
    "deny": [
      "Read(**/.env*)", "Read(**/.ssh/**)", "Read(**/.aws/**)",
      "Bash(rm -rf *)", "Bash(sudo *)", "Bash(git push *)"
    ]
  }
}
```

## 5. モデルの使い分け

**問題：** 多くの人がすべての作業に同じモデルを使っている。Opus を簡単な質問に使うと Sonnet の 5 倍のコストがかかる。

**修正方法：** セッション途中で `/model` コマンドを使う。再起動不要。

```text
/model sonnet     → 日常的なコーディング、レビュー、テスト
/model opus       → 複雑なリファクタ、アーキテクチャ設計
/model haiku      → 短い質問、フォーマット
```

タスクの 80% は Sonnet で十分こなせる。

## 6. Compact のカスタム指示

**問題：** デフォルトの `/compact` はコンテキストを汎用的にサマリする。プロジェクト固有の重要なコンテキストが失われやすい。

**修正方法：** サマリ時に残すべき情報を指定する。

```text
/compact preserve all architecture decisions, file paths mentioned, and error messages
```

アーキテクチャ判断・言及されたファイルパス・エラーメッセージが compaction を生き延びる。

## 7. Memory の活用

**問題：** セッションをまたいで Claude が学習したパターンを忘れる。毎回同じプロジェクトの慣習を説明し直している。

**修正方法：**

```text
/memory
```

で現在の自動記憶を確認し、手動でも追記できる。

```text
/memory add "このプロジェクトでは pnpm を使い、npm は使わない"
/memory add "auth ロジックは src/lib/auth/ に置き、components には入れない"
```

記憶は `~/.claude/projects/<project>/memory/` に永続化される。

## 8. 自動フォーマット用 Hooks

**問題：** Claude がコードを書くたびに手動で prettier を実行し、また作業に戻るという繰り返しが発生する。

**修正方法：** `settings.json` に PostToolUse hook を追加する。

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Write(*.ts)",
        "hooks": [{ "type": "command", "command": "npx prettier --write $file" }]
      }
    ]
  }
}
```

Claude が `.ts` ファイルを書くたびに自動でフォーマットが走る。

## 9. ログ前処理 Hooks

**問題：** 10,000 行のログファイルを Claude に読ませると数千トークン消費する。大半はノイズだ。

**修正方法：**

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash(cat *log*)",
        "hooks": [{ "type": "command", "command": "grep -n 'ERROR\\|WARN' $file | head -50" }]
      }
    ]
  }
}
```

Claude には 10,000 行ではなく関連する 50 行だけが届く。

## 10. Git worktree 分離

**問題：** Claude が作業中のブランチのファイルを直接編集するため、コミットしていない自分の変更と Claude の変更が混ざる。

**修正方法：**

```bash
claude -w
```

または settings でワークツリーオプションを有効化する。Claude は独立した git worktree 内で作業し、メインブランチはそのまま保たれる。

## 11. Bare モード（起動高速化）

**問題：** Claude Code は起動のたびにすべての設定を読み込み、CLAUDE.md を解析し、プロジェクトをスキャンする。短い質問のためだけに数秒かかる。

**修正方法：**

```bash
claude --bare
```

設定ファイルの探索をスキップし、最小構成で起動する。1 日に何十回も Claude Code を立ち上げる場合に起動時間を節約できる。

## 12. 自動化の予算上限

**問題：** CI/CD でヘッドレス実行した Claude Code が誰も監視していない間に無限ループに入り、トークンを消費し続ける。

**修正方法：**

```bash
claude -p "auth モジュールをリファクタ" --max-budget-usd 5.00
```

そのタスクで $5 を使い切ったら自動停止する。

## 13. Thinking サマリの表示

**問題：** UI はデフォルトで思考をサマリして表示する。Claude の推論が少なく見えるが、実際には隠れているだけのことがある。

**修正方法：**

```json
{
  "showThinkingSummaries": true
}
```

サマリではなく完全な思考チェーンを表示する。Claude が誤った判断をする場面でのデバッグに役立つ。

## 14. 並列サブエージェント数の制限

**問題：** エージェントのファンアウトによって 20 以上のサブエージェントが同時起動し、単純なタスクにトークンを大量消費する。

**修正方法：** プロンプトで明示的にエージェント数を指定する。

```
"サブエージェントをちょうど 3 つ生成してください：スタイルレビュー担当、バグ検出担当、セキュリティスキャン担当。それ以上は不要です。"
```

あるいは `--max-budget-usd` で全エージェント合計の支出を上限管理する。

## 15. MCP サーバーのツール数確認

**問題：** MCP サーバーは 1 サーバーにつき毎ターン 18,000 トークン以上を消費する。5 つ以上接続していると、最初のプロンプトを送る前に 90,000 トークンのオーバーヘッドが発生している。

**修正方法：**

```
/mcp
```

接続中のサーバーと各サーバーがロードするツール数を確認する。積極的に使っていないサーバーは削除する。1 サーバー削除するだけでセッションあたり数千トークンを節約できる。

## 1 分でできる基本設定

まず `.zshrc` または `.bashrc` に以下の 2 行を追記してリロードする。

```bash
export CLAUDE_CODE_EFFORT_LEVEL=high
export CLAUDE_CODE_DISABLE_ADAPTIVE_THINKING=1
```

次に `settings.json` に permission ルールと hooks を追記する（設定 3・4・8 を参照）。

環境変数 2 本 + 設定ファイル 1 枚。それが Claude Code を「自分の邪魔をするツール」から「自分のために動くツール」に変える分岐点だ。
