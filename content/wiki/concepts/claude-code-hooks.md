---
title: "Claude Code Hooks"
description: "Claude Code のライフサイクルイベント（PostToolUse / Stop / SessionEnd など）にスクリプトをフックして、AI Agent の挙動を周辺ツールから制御する仕組み"
date: 2026-05-18
lastmod: 2026-10-30
aliases: ["claude-code-hooks", "PostToolUse", "Stop hook", "SessionEnd hook"]
related_posts:
  - "/posts/2026/05/claude-code-vault-writeback-automation/"
  - "/posts/2026/05/self-hosted-runner-vault-writeback/"
  - "/posts/2026/10/jev-system-one-model/"
  - "/posts/2026/10/harness-design-intro-guardrails-boundary/"
tags: ["claude-code", "hooks", "automation", "PostToolUse"]
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

## PreToolUse で許可判断を返す（行動への柵）

`PreToolUse` フックは実行前のコマンドを受け取り、`allow` / `ask` などの許可判断を返せる。[ハーネスエンジニアリング](/blogs/wiki/concepts/harness-engineering/) の 3 層で言えば「行動への柵」であり、柵を走らせるレールのうち最も内側（最速だが、クライアント設定で無効化できる）にあたる。外側の Git hooks・CI と組み合わせて使う。

判定器として外部モデル（例: [Jev](/blogs/wiki/tools/jev/)）を呼ぶ試作から得た設計の勘所:

- **まず shadow モード**で分類結果をログに書くだけにし、精度を測ってから判断を返す
- **失敗したら何も出力しない**（API キーなし・タイムアウト・エラー時は通常の許可ルールに任せる）
- 送信前に秘密情報らしき文字列をマスクする
- 自動許可（`allow`）は高い確信度かつ、パイプ・連結・コマンド置換・リダイレクト・コメントを含まないコマンドに限るなど **コードで制限**する。モデルの判定は誘導コメントで揺らぐ
- hook が `allow` を返しても確認プロンプトが省かれるだけで、settings の deny / ask ルールは上書きされない
- フックの遅延は Bash 実行ごとに上乗せされる（外部 API 呼び出しで 0.4〜0.5 秒程度）

## セキュリティ上の注意

- `settings.json` のフック設定は **任意コード実行と等価** なので、信頼できないリポジトリの `<proj>/.claude/settings.json` を無批判に有効化しない
- `stdout` への過剰出力はエージェントの文脈を汚染する。promote 通知は 1〜3 行に抑える
- フックスクリプト本体のオーナー・権限を確認しておく

## 関連ページ

- [Claude Code](/blogs/wiki/tools/claude-code/) — フックの母体となる CLI
- [Obsidian Vault Writeback Loop](/blogs/wiki/concepts/obsidian-vault-writeback-loop/) — フックの代表的な応用例
- [Claude Code × Obsidian 統合ガイド](/blogs/wiki/guides/claude-code-obsidian-integration/) — 具体実装
- [ハーネスエンジニアリング](/blogs/wiki/concepts/harness-engineering/) — 馬具・柵・境界の中での hooks の位置づけ
- [Jev](/blogs/wiki/tools/jev/) — PreToolUse から呼ぶ判定特化モデル

## ソース記事

- [Obsidian Vault 書き戻しの自動化](/blogs/posts/2026/05/claude-code-vault-writeback-automation/) — 2026-05-18
- [GitHub Actions self-hosted runner で Obsidian Vault 書き戻しを完成させる](/blogs/posts/2026/05/self-hosted-runner-vault-writeback/) — 2026-05-18
- [Jev とは何か — 文章を書かず「判断だけ」を返す System One モデル](/blogs/posts/2026/10/jev-system-one-model/) — 2026-10-13
- [ハーネスエンジニアリング入門 — 馬具・柵・境界の3層で AI エージェントを自走させる](/blogs/posts/2026/10/harness-design-intro-guardrails-boundary/) — 2026-10-25
