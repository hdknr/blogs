---
title: "アダプティブ・シンキング（Claude の思考深度制御）"
description: "Anthropic が導入した Claude の思考量を動的に調整する仕組み。ユーザーから「サイレント・ダウングレード」と批判され、/effort max で元の深度に戻せる"
date: 2026-04-13
lastmod: 2026-09-30
aliases: ["adaptive thinking", "effort level", "claude thinking depth", "effort パラメーター"]
related_posts:
  - "/posts/2026/04/claude-thinking-nerfed/"
  - "/posts/2026/09/claude-opus-5-5-prompting/"
tags: ["claude", "claude-code", "思考深度", "anthropic", "llm"]
---

## 概要

Anthropic が Claude Code に導入した、タスクの複雑さに応じて思考量（extended thinking のトークン数）を自動調整する仕組み。AMD の AI ディレクターが 7,000 セッションのログ分析で思考深度の 67% 低下を発見し、「サイレント・ダウングレード」として SNS で大きな議論を呼んだ。

## 発覚の経緯

2026年4月2日、AMD シニア AI ディレクター Stella Laurenzo 氏が GitHub Issue（anthropics/claude-code#42796）を投稿。2026年1〜3月の約 6,852 セッション（234,760 ツールコール、17,871 思考ブロック）を分析した結果:

| 指標 | 変更前（1月末〜2月中旬） | 変更後（3月8日〜23日） |
|------|--------------------------|------------------------|
| 思考の中央値（文字数） | 約 2,200 文字 | 約 600 文字（67% 減） |
| 思考ブロックの割合 | 約 30% | 約 15% |

## Anthropic の説明

Anthropic は「アダプティブ・シンキング」と「エフォートレベルの変更」の2点を認めた。

- **アダプティブ・シンキング**: タスクの複雑さを判断して思考量を動的に調整する仕組みを導入
- **エフォートレベルの変更**: デフォルトの effort レベルを意図的に下げた

ユーザーへの事前告知・変更履歴の明示はなく、「サイレントな仕様変更」として批判された。

## 対処方法

### 1. エフォートレベルを最大に設定

```bash
# Claude Code セッション内で実行
/effort max
```

### 2. アダプティブ・シンキングを無効化

環境変数を設定することで、常に最大の思考深度を強制できる。

```bash
export CLAUDE_CODE_DISABLE_ADAPTIVE_THINKING=1
```

ただし、レスポンス時間の増加とトークン消費増のトレードオフがある。

## 論点

- Anthropic は思考量削減で **API コスト削減とレスポンス高速化** を実現した可能性
- 一方、複雑なタスクでの **品質低下** を招くトレードオフ
- ユーザーへの透明性の欠如が最大の問題として指摘された

## その後: Opus 5.5 で思考は常にオンに

Claude Opus 5.5（2026 年 9 月）では思考が**常にオン**になり、どれだけ考えるかはモデルが決め、調整手段は `effort` に一本化された。API で `thinking: {"type": "disabled"}` や `budget_tokens` を送ると 400 エラーになり、`thinking` を省略するか `{"type": "adaptive"}` を送る。

- 既定の effort は `medium`（Opus 5 は `high`）。Opus 5.5 の `medium` は評価上 Opus 5 の `high` と同等以上
- 同じ effort 名でも Opus 5.5 のほうが多く考える（`xhigh` / `max` で顕著）ので、旧モデルの設定を持ち込まず測り直す
- 思考トークンは中身が返らなくても `max_tokens` に含まれる
- 思考を減らしたいなら、プロンプトで「考えすぎるな」と書くより effort を下げるほうが確実。逆に「回答前によく考えて」はシステムプロンプトから消してよい

「思考量をモデルが決め、人は effort で上限側を調整する」という 4 月の変更の方向は、そのまま標準の使い方になった。詳細は [Claude Opus 5.5](/blogs/wiki/tools/claude-opus-5-5/)。

## 関連ページ

- [Claude の EQ（脳内トレース能力）](/blogs/wiki/concepts/claude-eq/)
- [Claude Mythos](/blogs/wiki/concepts/claude-mythos/)
- [Claude Opus 5.5](/blogs/wiki/tools/claude-opus-5-5/) — effort を主な調整手段にしたモデル

## ソース記事

- [Claude の思考深度が67%低下？AMD AIディレクターの分析が示す「サイレント・ダウングレード」問題](/blogs/posts/2026/04/claude-thinking-nerfed/) — 2026-04-13
- [Claude Opus 5.5 の使い方 — 「よく考えて」を消し、effort と継続指示で長いタスクを回す](/blogs/posts/2026/09/claude-opus-5-5-prompting/) — 2026-09-30
