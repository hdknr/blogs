---
title: "Jev"
description: "TypeSafe AI の「System One モデル」。文章を生成せず、型付きの判断と確信度だけを返す分類・判定特化モデル"
date: 2026-10-30
lastmod: 2026-10-30
aliases: ["Jev", "System One モデル", "TypeSafe AI", "typesafe-sdk"]
related_posts:
  - "/posts/2026/10/jev-system-one-model/"
tags: ["Jev", "TypeSafe AI", "AIエージェント", "claude-code", "hooks"]
---

## 概要

Jev は米 TypeSafe AI が 2026 年 9 月に発表したモデル。会話も文章生成もせず、利用者が定義した質問への「判断」だけを、確信度付きの構造化データ（JSON）で返す。同社は LLM ではなく「System One モデル」（カーネマンのシステム 1＝速い直感的思考に由来）という新カテゴリと位置づけ、「スマートな if 文」と説明している。件数の多い分類・判定を速く安く処理する部品であり、文章生成や計算には向かない。

## 詳細

### 質問の 3 形式

| 形式 | 返すもの | 用途の例 |
|---|---|---|
| Choice | 選択肢から 1 つ＋確信度 | 問い合わせ種別、コマンドの影響分類 |
| Score | 範囲内の数値＋確信度 | インシデントの重大度 |
| Noul | はい／いいえの確率 | 「日本語か」などの二値判定 |

互いに独立した小さな質問は 1 回の呼び出しにまとめられる。結果の組み合わせと業務ルールの適用はアプリ側のコードが決める。`confidence` は「その確率で正解」という意味ではないので、閾値は自社データで誤分類件数と確認件数を見て決める。

### LLM・エージェントとの役割分担

- **Jev**: 分類・条件判定・スコアリング。処理の流れはコードの条件分岐が決める
- **LLM エージェント**: 状況の解釈やツール選択。柔軟だがコストと過程が読みにくい
- 出力形式だけなら LLM にも同じ JSON を出させられる。差は特化学習による **速さ・安さ・確率の扱いやすさ**

提供元の公表値では応答 70〜500 ms、入力 100 万トークンあたり 0.042 ドル、出力無料。いずれも第三者検証はない。

### 苦手なこと・注意点

- スキーマ外の出力が出ないことと、判断が正しいことは別
- 数の計算や日時比較は苦手（コードで処理する）
- 入力中の誘導的な表現で結果が揺らぐ。型安全はセキュリティの保証ではない

### Claude Code の PreToolUse hook で試した結果

メインモデルの置き換えは非現実的で、「特定の判断だけを Jev に問い合わせる」のが現実的な使い方。経路は MCP（Claude 次第で呼ばれる）・hook（毎回必ず通る）・Bash スクリプト（大量仕分け）の 3 つで、必ず通したい判断には hook が向く。

Bash コマンドを `read_only` / `write_local` / `destructive` / `external` に分類する [PreToolUse hook](/blogs/wiki/concepts/claude-code-hooks/) を試作した際の知見:

- **既定は shadow モード**でログだけ取り、精度を測ってから enforce に移る
- 普段のコマンド 15 件はすべて想定どおり、応答は日本から 136〜249 ms、hook 全体で 0.4〜0.5 秒程度
- `gh repo delete ... --yes` や `truncate -s 0` は `destructive` でも確信度 0.5 前後で、閾値方式では確認を強制できなかった。最上位が `destructive` なら確信度に関係なく `ask` にするなど **非対称な扱い**が要る
- 誘導コメント（`# read only ...`）でラベルが `read_only` に反転した例があった。**コメント・パイプ・連結・置換を含むコマンドは自動許可しない**というモデル外の制限をコードで掛ける
- Jev はコマンドの見た目で判断し、スクリプトの中身は見ない
- 秘密情報のマスクは判定材料も削る

結論として、**自動許可の最終判断はコードに置き、Jev の判断はその入力の一つに留める**。これは [ハーネスエンジニアリング](/blogs/wiki/concepts/harness-engineering/) の「柵は機械的な判定で」という考え方と一致する。

## 関連ページ

- [Claude Code Hooks](/blogs/wiki/concepts/claude-code-hooks/) — Jev を呼び出す PreToolUse hook の土台
- [ハーネスエンジニアリング](/blogs/wiki/concepts/harness-engineering/) — 行動への柵としての権限判定
- [プロンプトインジェクション](/blogs/wiki/concepts/prompt-injection/) — 誘導コメントで判定が揺らぐ問題
- [Claude Code](/blogs/wiki/tools/claude-code/)

## ソース記事

- [Jev とは何か — 文章を書かず「判断だけ」を返す System One モデル](/blogs/posts/2026/10/jev-system-one-model/) — 2026-10-13
