---
title: "Claude Code の JSONL ログを読む"
description: "Claude Code のセッションログ（JSONL）の保存先、実測したスキーマ（type 17 種類、user 行の 9 割はツール結果）、0 件で成功するパーサを避ける集計手順、usage によるトークン分析"
date: 2026-09-30
lastmod: 2026-09-30
aliases: ["Claude Code セッションログ", "transcript jsonl", "JSON Lines", "NDJSON"]
related_posts:
  - "/posts/2026/09/claude-code-jsonl-log-verified/"
tags: ["claude-code", "JSONL", "python", "ログ分析", "コンテキスト管理"]
---

## 概要

Claude Code はセッションの全履歴を JSONL で書き出しており、直接読めば `/cost` や `/context` では見えないターンごとのトークン推移、ツール呼び出しの傾向、コンパクションの位置まで取れる。ただし解説記事のスキーマ記述は環境によって成り立たず、しかも外れ方の多くが**エラーではなく出力 0 件の成功**になる。

41 セッション・29,043 行（Claude Code 2.1.222〜2.1.258）を横断集計した実測から、パーサを書く前に確かめることをまとめる。数値は絶対値ではなく**確認の手順**として読む。

## 詳細

### 保存先

```text
~/.claude/projects/<encoded-project-path>/<session-uuid>.jsonl
```

プロジェクトパスはディレクトリ名にエンコードされ（`/Users/you/code/my-app` → `-Users-you-code-my-app`）、1 セッション 1 ファイル・追記専用。

`~/.claude/sessions/<id>/transcript.jsonl` とする解説もあるが、手元には 1 件も無かった。厄介なのは **`~/.claude/sessions/` 自体は実在する**こと。中身はポート番号を冠した `.json` と権限 `600` の `.key` で、会話ログではない（`.key` は開いたり貼ったりしない）。存在しないディレクトリなら即座に気づけるが、実在するのに目的のファイルが無い場所には着地してしまう。

### JSONL が規格化しているのは封筒だけ

JSON Lines は標準化団体の規格ではなく、要件は UTF-8（BOM なし）・各行が valid な JSON・行終端 `\n` の 3 つだけ。MIME も未標準化と仕様自身が書いている。

| | 位置づけ | MIME | 行区切り |
|---|---|---|---|
| JSON Lines | jsonlines.org のコミュニティ仕様 | `application/jsonl`（未登録） | `\n` |
| NDJSON | ndjson-spec v1.0.0 | `application/x-ndjson`（未登録） | `\n`。空行は無視してよい（MAY） |
| JSON text sequences | RFC 7464（正式 RFC） | `application/json-seq`（IANA 登録済み） | 各レコードの前に RS `0x1E`。JSONL とは非互換 |

どの仕様も行の中身は決めていない。**Claude Code の行スキーマはアプリケーション定義で、参照すべき共通の権威がそもそも無い**ので、解説どうしが食い違う。

### 実測したスキーマ

- **全行にあるトップレベルキーは `type` だけ**。`sessionId` 98%、`timestamp` 79%、`uuid` / `parentUuid` / `cwd` / `gitBranch` / `version` 74%、`message` 55%。`o['uuid']` と書けば 26% の行で `KeyError`、`parentUuid` で張った会話ツリーはログの 74% 分しか無い
- **`sessionId` と `session_id` が同じログに共存**する。片方だけ見ると取りこぼす
- **`type` は 17 種類**で、会話本体（`assistant` 34%・`user` 21%）以外の 45% はメタイベント（`attachment` 17%、`last-prompt`、`mode`、`permission-mode`、`pr-link`、`ai-title`、`cost-state` など）。知らない type は `raise` せず捨てる実装にする。`pr-link` には PR 番号と URL、`cost-state` には累計コストが入っている
- **`type: "user"` の 92.5% はツール実行結果**。ツールの結果はモデルへ返すために `role: "user"` で記録されるので、人間の発言は全 29,043 行のうち 465 行（1.6%）。`content` は文字列の場合と配列の場合の両方がある
- 人間の発言を拾うなら `type: "last-prompt"` が素直。`promptId` はほぼ全 `user` 行にあるので、絞り込みではなく「1 回の指示でツール往復が何回あったか」のグルーピングに使う

```python
def is_human_utterance(o):
    if o.get('type') != 'user':
        return False
    msg = o.get('message')
    if not isinstance(msg, dict):
        return False
    c = msg.get('content')
    if isinstance(c, str):
        return bool(c.strip())
    if isinstance(c, list):
        return any(i.get('type') == 'text' for i in c if isinstance(i, dict))
    return False
```

### 0 件成功を避ける

- **他 CLI 向けのパーサを流用しない** — Codex CLI 形式（`event_msg` / `response_item` + `payload.*`）のパーサを当てると、`payload` キーが 1 行も無いので `.get("payload", {})` で全行が静かに捨てられ、正常終了して出力は空になる
- **`glob.glob('~/...')` はチルダを展開しない** — `os.path.expanduser` を通さないとエラーも出さずに 0 ファイル
- **件数をアサーションに入れる** — `assert files` と `assert matched > 0, f'0 件（総行数 {total}）。スキーマ想定を疑うこと'`
- **自分を含む母集団は 1 パスで全指標を出す** — 集計中のセッションもログを書き続けるので、別タイミングの数値を混ぜると内訳の合計が合わない

最初に走らせるべきは整形スクリプトではなく、**`type` の分布とキー出現率を出す 20 行ほどの集計**である。

### ツール呼び出しとトークン

- ツール呼び出しは `assistant` 行の `content` 配列内の `tool_use` ブロック。MCP ツールは `mcp__<server>__<tool>` なので `startswith('mcp__')` で選別できる（サーバー名にハイフンが入りうるので最初と最後の `__` で分割）
- 同じ ID のブロックが複数行に記録されることがあるので、回数は**ブロック数ではなくユニークな `tool_use.id`** で数える。`tool_result.tool_use_id` と突き合わせると実行中の呼び出しが分かる
- ターンの実プロンプトサイズは `input_tokens + cache_read_input_tokens + cache_creation_input_tokens`。キャッシュヒット率は 98.32% だった
- 「初回ターンの `cache_read` は全セッションで一致する固定コスト」という主張は再現せず、40 セッションで 14 通り（0〜30,799）に散った。**手法は再現するが、そこで得た定数は自分の環境の定数にすぎない**
- ピーク `ctx` は `claude-opus-5` で 765K に達した（1M 版を使用）。**`model` 文字列だけではウィンドウ長は決まらない**ので、コンパクション閾値を語るときは実際のウィンドウ長とセットで書く
- `model` が `<synthetic>` の行は API 呼び出しを伴わない内部生成で、コスト集計から外す

## 関連ページ

- [Claude Code](/blogs/wiki/tools/claude-code/) — ログを書き出す本体
- [沈黙する失敗](/blogs/wiki/concepts/silent-failure/) — 0 件で成功するパーサ
- [コンテキスト圧縮](/blogs/wiki/concepts/context-compression/) — ログから発動位置を追える圧縮カスケード
- [Context Rot](/blogs/wiki/concepts/context-rot/) — コンテキストの劣化と管理

## ソース記事

- [Claude Code の JSONL ログを 29,043 行で検証 — 解説記事の前提が自分の環境で成り立たなかった 6 点](/blogs/posts/2026/09/claude-code-jsonl-log-verified/) — 2026-09-04
