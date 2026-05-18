---
title: "Claude Code Hooks"
description: "Claude Code のライフサイクルイベント（PostToolUse / Stop / SessionEnd など）にスクリプトをフックして、AI Agent の挙動を周辺ツールから制御する仕組み"
date: 2026-05-18
lastmod: 2026-05-18
aliases: ["claude-code-hooks", "PostToolUse", "Stop hook", "SessionEnd hook"]
related_posts:
  - "/posts/2026/05/claude-code-vault-writeback-automation/"
  - "/posts/2026/05/self-hosted-runner-vault-writeback/"
tags: ["Claude Code", "Hooks", "automation", "PostToolUse"]
---

## 概要

Claude Code のフックは、エージェントのライフサイクル上の特定イベント（ツール呼び出し前後、応答終了、セッション終了など）でシェルスクリプトを発火させる仕組み。`settings.json` の `hooks` フィールドで定義する。フックは **直接エージェントを駆動できない**（次のターンを発火できない）が、stdout の出力がエージェントの文脈に注入されるため、「**フックは器を用意し、AI が中身を書く**」という分業が成立する。

## 主なイベント

| イベント | 発火タイミング | エージェントへの指示 | 主な用途 |
| --- | --- | --- | --- |
| `PreToolUse` | ツール呼び出し直前 | ✓ | 危険なコマンドのブロック・引数の正規化 |
| `PostToolUse` | ツール呼び出し直後 | ✓ stdout で次ターンに hint を渡せる | 結果の通知・後続スキルの promote 通知 |
| `Stop` | アシスタントの応答が終わった瞬間（毎ターン） | ✓ | 直前のターンの成果に応じた追加作業の促し |
| `SessionEnd` | セッション終了時（1 回） | ✗ もうエージェントは動かない | 純粋な事後ログ・成果物のアーカイブ |
| `UserPromptSubmit` | ユーザープロンプト送信時 | ✓ | プロンプトの前処理・コンテキスト追加 |
| `SessionStart` | セッション開始時 | ✓ | 環境チェック・初期文脈の差し込み |
| `Notification` | 通知発火時 | ✓ | デスクトップ通知などへの中継 |
| `SubagentStop` | サブエージェント終了時 | ✓ | サブエージェント完了の伝播 |
| `PreCompact` | コンテキスト圧縮直前 | ✓ | 重要情報の退避 |

## 設定例

```jsonc
// ~/.claude/settings.json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          { "type": "command", "command": "~/.claude/hooks/detect-pr-merge.sh" }
        ]
      }
    ],
    "Stop": [
      {
        "hooks": [
          { "type": "command", "command": "~/.claude/hooks/append-daily-log.sh" }
        ]
      }
    ]
  }
}
```

- `matcher` はツール名（`Bash`, `Write`, `Edit` など）を正規表現で指定
- フックは標準入力で JSON 形式のイベント情報を受け取る（`tool_input.command`, `transcript_path` など）
- 標準出力に書いた内容がエージェントの次ターンに hint として渡る

## `Stop` と `SessionEnd` の使い分け

- **`Stop`**: 会話継続中の hint。直前のターンで成果が出たとき、AI に追加作業（書き戻し本体など）を促す
- **`SessionEnd`**: 会話後の墓標。AI には頼めないので、純粋な事後ログ用途に絞る

## セキュリティ上の注意

- `settings.json` のフック設定は **任意コード実行と等価** なので、信頼できないリポジトリの `<proj>/.claude/settings.json` を無批判に有効化しない
- `stdout` への過剰出力はエージェントの文脈を汚染する。promote 通知は 1〜3 行に抑える
- フックスクリプト本体のオーナー・権限を確認しておく

## 関連ページ

- [Claude Code](/blogs/wiki/tools/claude-code/) — フックの母体となる CLI
- [Obsidian Vault Writeback Loop](/blogs/wiki/concepts/obsidian-vault-writeback-loop/) — フックの代表的な応用例
- [Claude Code × Obsidian 統合ガイド](/blogs/wiki/guides/claude-code-obsidian-integration/) — 具体実装

## ソース記事

- [Obsidian Vault 書き戻しの自動化](/blogs/posts/2026/05/claude-code-vault-writeback-automation/) — 2026-05-18
- [GitHub Actions self-hosted runner で Obsidian Vault 書き戻しを完成させる](/blogs/posts/2026/05/self-hosted-runner-vault-writeback/) — 2026-05-18
