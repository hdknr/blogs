---
title: "Claude Code 新機能「Auto Mode」完全解説"
date: 2026-03-17
lastmod: 2026-03-17
draft: false
source_url: "https://github.com/hdknr/blogs/issues/1#issuecomment-4078718977"
categories: ["AI/LLM"]
tags: ["Claude Code", "Auto Mode", "許可管理", "開発ツール", "CLI"]
---

これまでClaude Codeを使っていて「許可ボタン押すのめんどくさすぎ問題」にイラッとしてた人、朗報です。Claude Codeに新機能「Auto Mode」が追加されました。

「全部自動でやってくれるやつでしょ？」と思った人、半分正解で半分不正解。

Auto Modeは「Claude自身がAI判断で、この操作は許可していいかどうかを決める」モードなので、全部無条件に自動承認するわけじゃないんです。ここ、めちゃくちゃ大事。

## そもそもなぜAuto Modeが必要だったのか

Claude Codeはファイルの編集やコマンドの実行のたびに「これやっていい？」と確認してきますよね。

1回2回ならいいけど、長時間のコーディングだと10回20回と確認が出る。正直めんどくさい。

これまでClaude Codeで「確認をスキップしたい人」には2つの選択肢しかありませんでした。

- **Auto-Accept Mode** → ファイル編集だけ自動。コマンド系は毎回確認が出る
- **Dangerously Skip Permissions** → 全部ノーチェック。かーなーり危険なやつ

つまり「ちょうどいい中間」がなかったんです。ファイル編集だけ自動じゃ足りないけど、全部ノーチェックは怖い。この隙間を埋めるのが Auto Mode。

## Auto Modeの仕組み

Auto Modeでは、Claude自身が操作ごとに「これは安全か？」をAIが判断します。

- **プロジェクト内のファイル読み書き** → 安全と判断して自動承認
- **外部ネットワークへのアクセスやシステムに影響するコマンド** → 危険と判断して確認を出す

つまり人間が毎回「Yes / No」を押す代わりに、Claudeが代わりに判断してくれる仕組み。

### 注意点

- AI判断にトークンを使うので、コストが少し増える
- 判断が完璧とは限らない。Anthropic公式も「隔離環境での使用を推奨」としている
- あくまでリサーチプレビュー（研究段階のお試し版）

## Auto Modeの始め方

ターミナルでClaude Codeを使っている場合は、以下のどちらかで起動します。

```bash
claude --enable-auto-mode
# または
claude --permission-mode auto
```

どちらでもOKです。

### VS Codeで使う場合の注意

VS Codeの拡張機能でClaude Codeを使っている場合は、Auto Modeは使えないようです（2026年3月時点）。

VS Codeの設定（`claudeCode.initialPermissionMode`）で選べるのは以下の4つだけで、「auto」は選択肢にありません。

- `default`
- `acceptEdits`（Auto-Accept Mode）
- `plan`
- `bypassPermissions`

最新のAuto Mode を使いたい場合は、ターミナルから起動する必要があります。VS Code内でターミナルを開いてClaude Codeを起動する形でも、`--enable-auto-mode` フラグをつければAuto Modeが使えます。

## 3つのモードの違いを整理

名前が似ている機能が複数あるので整理します。

### Auto-Accept Mode（従来からの機能）

「acceptEdits」というモードです。ファイル編集だけ自動承認し、コマンドは毎回確認が出ます。

- `Shift+Tab` を押すか、VS Codeではチャット欄下のモード表示をクリックで切り替え
- 「編集の確認だけ省きたい」人向け

### Dangerously Skip Permissions（従来からの機能）

```bash
claude --dangerously-skip-permissions
```

すべての確認を無条件でスキップし、AI判断もありません。名前に "Dangerously（危険）" が入っている通り、仮想環境やコンテナ専用のモードです。

### 3つの違いのまとめ

| モード | 動作 |
|--------|------|
| Auto-Accept Mode | ファイル編集だけ自動。コマンドは確認する |
| **Auto Mode（NEW）** | **AIが判断して、安全そうなら自動。危なそうなら確認する** |
| Dangerously Skip Permissions | 全部自動。何も確認しない |

安全度は **Auto-Accept > Auto Mode > Dangerously Skip** の順です。

## まとめ

- Auto Modeは「AIが許可判断する」新機能
- 起動は `claude --enable-auto-mode` または `claude --permission-mode auto`
- Auto Modeを使うならターミナルから起動する
- Auto-Accept Mode（Shift+Tab / acceptEdits）とは別物
- Dangerously Skip Permissionsとも別物。AI判断の有無が違う
- 安全度順：Auto-Accept > Auto Mode > Dangerously Skip

「全部ノーチェック（Dangerously Skip）は怖いけど、毎回確認もめんどくさい」という人にとって、ちょうどいい選択肢がやっと来た感じです。

## 参考ドキュメント

- [Permission Modes](https://code.claude.com/docs/en/permissions)
- [サンドボックス](https://code.claude.com/docs/en/sandboxing)
- [VS Code拡張](https://code.claude.com/docs/en/ide-integrations)
- [CLIリファレンス](https://code.claude.com/docs/en/cli-reference)
