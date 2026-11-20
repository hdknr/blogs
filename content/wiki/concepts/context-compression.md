---
title: "コンテキスト圧縮"
description: "LLM の会話が長くなった際にコンテキストウィンドウを管理する戦略群。Claude Code の圧縮カスケードと、自動圧縮のタイミング（auto-compact window）の調整"
date: 2026-04-06
lastmod: 2026-11-19
aliases: ["Context Compression", "コンテキスト管理", "auto-compact", "自動圧縮", "autoCompactWindow", "/autocompact"]
related_posts:
  - "/posts/2026/04/claude-code-context-compression/"
  - "/posts/2026/04/claude-code-context-rot-session-management/"
  - "/posts/2026/04/claude-caveman-token-reduction/"
  - "/posts/2026/04/claude-rate-limit-mac-mini-local-model/"
  - "/posts/2026/11/claude-code-autocompact-window/"
tags: ["llm", "claude-code", "コンテキスト", "トークン削減"]
---

## 概要

LLM のコンテキストウィンドウには上限がある。会話が長くなると古い情報を捨てるか圧縮する必要があり、その戦略設計は AI コーディングエージェントの中心課題。

ウィンドウが 1M トークンまで広がっても圧縮の問題は消えない。エージェントは毎ターン会話全体を送り直すので、会話が長いほど 1 ターンあたりの入力コストが増え、[Context Rot](/blogs/wiki/concepts/context-rot/) で精度も落ちる。「いつ畳むか」も設計の対象になる。

## 詳細

### Claude Code の 5 つの圧縮戦略

軽量な処理から順にカスケードとして適用される（前段にツール結果のバジェッティングがある）。

1. **Microcompact** — 古いツール結果を時間ベースで消去（API 呼び出し不要）
2. **Context Collapse** — 会話の部分範囲を要約で置換（直近の文脈は保持）
3. **Session Memory** — 重要情報を別ファイルに永続化（`/compact` 手動実行時にも使用）
4. **Full Compact** — 履歴全体を包括的に要約（auto-compact: 約 33K トークンのバッファ残し）
5. **PTL Truncation** — 最も古いメッセージ群を切り落とす最終手段

### 自動圧縮のタイミング（auto-compact window）

1M ウィンドウのモデル（Opus 5.5・Fable 5.2 など）は、既定では窓が埋まる手前の**約 967K トークン**で自動圧縮する（200K 窓の約 167K と同じく約 33K の余白）。基準にする窓を小さくすると早く畳める。

| 指定方法 | 範囲・効き方 |
|---|---|
| `/autocompact 400k` | 今のモデルだけ。v2.1.288 以降は `modelSettings.<model>.autoCompactWindow` に保存。`/autocompact auto` で戻す |
| `settings.json` の `"autoCompactWindow": 400000` | 全モデル共通（モデル別の値が優先） |
| `--autocompact` 起動フラグ | その起動 1 回だけ |
| `CLAUDE_CODE_AUTO_COMPACT_WINDOW` | 環境変数。コマンドや設定より優先。数値だけだと**トークン数**扱い（`400` は 400 トークン） |

指定範囲は 100K〜1M。管理設定（managed settings）も `/autocompact` で保存した値より優先されるので、「設定したのに効かない」ときは環境変数と管理設定を先に疑う。ほかに `CLAUDE_AUTOCOMPACT_PCT_OVERRIDE`（窓の何 % で畳むか）、`DISABLE_AUTO_COMPACT`、`DISABLE_COMPACT`、`CLAUDE_CODE_DISABLE_1M_CONTEXT` がある。

### 早めに畳むことの得失

| 得 | 失 |
|---|---|
| 1 ターンの入力コストが会話の長さにほぼ比例して下がる。Opus 5.5 のキャッシュ読み出し（$0.20/MTok）でも 967K で約 $0.19、400K で約 $0.08 / ターン | 要約で細部が落ちる。圧縮の回数が増えるほど要約の質に左右される |
| キャッシュ期限切れ直後の全文読み直しが安くなる | 圧縮すると会話部分のキャッシュが無効になり、期限切れ後の圧縮は全文をキャッシュなしで処理する |
| 長いコンテキストでの精度低下を避けられる | 400K は経験則で、公式の閾値は示されていない |

圧縮後に自動で入れ直されるのは、プロジェクトルートの CLAUDE.md・自動メモリ・スキルの説明・直近に読んだファイル（最大 5 つ）。パス単位のルールやサブディレクトリの CLAUDE.md は必要になったときに読み直される。

### 実用的な対策

- `/autocompact` は会話が膨らみすぎない上限を決める「保険」として使う
- タスクの区切りで `/compact <残したい焦点>` を手動実行する
- 圧縮で失われたくない情報は `CLAUDE.md` に記載する
- `/context` で使用量を確認し、異なるタスク間では `/clear` でリセットする
- 大きな出力はサブエージェントに委任する。中間出力を文脈に入れないという意味では、ツール呼び出しを JavaScript で束ねる [Claude Code](/blogs/wiki/tools/claude-code/) の Code Mode も同じ方向の手段

## 関連ページ

- [Claude Code](/blogs/wiki/tools/claude-code/) — この圧縮戦略を実装しているツール
- [Context Rot](/blogs/wiki/concepts/context-rot/) — 長いコンテキストでの精度低下と 5 つのセッション管理
- [LLM Wiki パターン](/blogs/wiki/concepts/llm-wiki-pattern/) — 知識の永続化という関連アプローチ

## ソース記事

- [Claude Code のコンテキスト圧縮戦略 — ソースコードから見える5つのアプローチ](/blogs/posts/2026/04/claude-code-context-compression/) — 2026-04-02
- [Claude Code の /autocompact 設定 — 1M コンテキストの自動圧縮を 400K に早めるコストと品質の得失](/blogs/posts/2026/11/claude-code-autocompact-window/) — 2026-11-17
