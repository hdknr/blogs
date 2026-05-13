---
title: "Claude Code のスキルで「マージ後」の指示が PR 作成中に発火する罠 — バッチ並行実行で起きた wiki コンフリクトの原因と修正"
date: 2026-05-13
lastmod: 2026-05-13
slug: "claude-skill-post-merge-trap"
draft: false
categories: ["AI/LLM", "ツール/開発環境"]
tags: ["claude-code", "skill", "SKILL.md", "ハーネスエンジニアリング", "バッチ処理", "ハマりどころ"]
---

## 症状

`blog-batch.sh` で夜間バッチを回した結果、こんな状態になっていた:

- 同じ wiki ファイル（`content/wiki/concepts/harness-engineering.md`、`content/wiki/tools/claude-code.md`）が**複数の blog PR で同時に変更**されていた
- main にマージしようとすると毎回コンフリクト
- 直近の #368・#369・#371・#372 はすべてこの原因で手動コンフリクト解消が必要だった

調査して原因が判明したので、修正内容と「LLM スキルを書くときに気をつけるべきポイント」を共有する。

## PR の中身を見ると 3 コミットあった

通常の `/blog` で作った PR は「記事 1 本分の 1 コミット」のはずだが、見ると 3 コミットあった:

```text
35a61c2 Add blog post: トレーダーのSランクスキル5選...
86e5bd4 Update wiki-last-ingest.txt: mark all posts through 2026-05-07 as ingested
0bc4e1f Update Wiki: ingest posts 2026-04-15 through 2026-04-21 (5 updated, 16 new pages)
```

2 つ目と 3 つ目は **wiki ingest の結果コミット**。これが各 blog PR に混入していて、複数 PR で同じ wiki ファイルを並行更新 → コンフリクトという流れ。

## SKILL.md は「マージ後」と書いてあった

`/blog` スキルの SKILL.md には、最後にこうある:

```markdown
## Post-merge follow-up

1. Send the PR URL to the user.
2. After merge, auto-remove the worktree...
3. **Wiki auto-ingest check**: after merge, decide whether to run `/wiki-ingest`:
   1. Read the last ingest date from `.claude/wiki-last-ingest.txt`...
   2. Count posts in `content/posts/` whose frontmatter `date` is on or after that date.
   3. **≥ 20 posts**: auto-run `/wiki-ingest all`, then update `.claude/wiki-last-ingest.txt` to today.
```

人間の読み方では明確に「**PR がマージされた後で**、20 件以上溜まっていれば wiki ingest を実行する」と書かれている。実装上はバッチ処理を想定すれば、各 PR は人間がレビューしてマージするのが普通だから、wiki ingest は人間のマージ判断の後にしか走らないはず。

**しかし実際は、PR 作成中に発火していた。**

## 根本原因: LLM の「単一セッション」と「時系列」のズレ

`claude -p "/blog <URL>"` という呼び出しは **単一の Claude セッション** で完結する。このセッション内で:

1. ブログ記事を作成
2. ブランチを作って PR を発行
3. ... ここで本来は「人間がマージするまで待つ」フェーズがあるはず ...
4. 「Post-merge follow-up」セクションへ進む
5. `/wiki-ingest all` を実行
6. その結果を **まだ生きている blog ブランチ** にコミット

LLM はマージを待たない。`claude -p` は同期実行で、関数呼び出しのように上から下までシーケンシャルに進む。「after merge」という人間にとっての時系列指示は、LLM の実行モデルでは **「次のステップ」** とほぼ同義になる。

結果として、`/blog` セッションは「PR 作成」の直後に「wiki ingest」まで走り抜けてしまい、wiki 変更が blog ブランチに含まれてしまった。

### 図解

```text
人間の頭の中:                            LLM の実行モデル:
┌────────────┐                          ┌────────────┐
│ ブログ作成  │                          │ ブログ作成  │
└─────┬──────┘                          └─────┬──────┘
      │                                       │
┌─────▼──────┐                          ┌─────▼──────┐
│ PR 作成    │                          │ PR 作成    │
└─────┬──────┘                          └─────┬──────┘
      │                                       │
   〜人間のレビュー〜                    （何も挟まらない）
      │                                       │
   〜人間のマージ〜                            │
      │                                       │
┌─────▼──────┐                          ┌─────▼──────┐
│ wiki ingest │                          │ wiki ingest │
└────────────┘                          └────────────┘
                                          ↑
                                  blog ブランチに混入
```

## 修正内容

### 1. `blog-batch.sh` のプロンプトに skip 指示

各 `/blog` 呼び出しのプロンプトに、必ず次の文言を付与するようにした:

```text
重要: SKILL.md の 'Post-merge follow-up' ステップ 3（Wiki auto-ingest check）は
実行しないでください。バッチ処理中なので個別 ingest は不要です。
Wiki 更新はバッチ完了後にまとめて行います。
```

### 2. `--final-wiki-ingest` フラグで明示的タイミング制御

バッチ完了後に **1 回だけ** `/wiki-ingest all` を実行するフラグを追加:

```bash
nohup ./scripts/blog-batch.sh 1 --overnight --final-wiki-ingest \
  > .claude/temp/blog-batch-stdout.log 2>&1 &
```

ingest のタイミングを **バッチ駆動側が支配** することで、blog ブランチへの混入を防ぐ。

### 3. SKILL.md に skip-condition を明記

`Post-merge follow-up` の Wiki auto-ingest check 冒頭に次を追加した:

```markdown
**Skip-condition check first**: if the caller has explicitly told you to skip
Wiki auto-ingest, do not execute this step at all. This applies whenever
`/blog` is invoked from `scripts/blog-batch.sh` or any other automation,
because running `/wiki-ingest` inside the same blog branch causes wiki commits
to be bundled into every blog PR and creates merge conflicts when multiple
blog PRs run in parallel.
```

呼び出し元（バッチドライバ）が指示する場合は、`/blog` 側が必ず**先にスキップ判定**する設計に変えた。

## 教訓: LLM スキルに「時系列」を書くときの注意

今回学んだのは、**SKILL.md（≒ システムプロンプト）の表現が LLM の実行モデルとズレると、見た目正しいスキルが間違った挙動をする**という話。

### "after X" 系の表現は危険

| 人間の意図 | LLM の解釈（単一セッション） |
|---|---|
| "after merge" | 「次のステップ」 |
| "後でやる" | 「すぐやる」 |
| "次回セッションで" | 「このセッションで」 |
| "ユーザーがレビューしてから" | （レビュー待ちの概念がないので）スキップしてすぐ次へ |

### 安全な書き方

- **条件分岐で明示する**: 「呼び出し元が X と指示している場合のみ実行」のような明示的なスキップ条件
- **タイミングは外部から制御する**: ingest のような副作用が大きい処理は、スキル内ではなく **バッチドライバ側**でタイミングを決める
- **副作用の境界を明確にする**: 1 つのスキルが「post 作成」と「wiki 集約」の両方を担うと、副作用の範囲が予測不能になる。役割を分割する

## まとめ

| 項目 | 内容 |
|---|---|
| 症状 | 並行 blog PR で同じ wiki ファイルがコンフリクト |
| 直接原因 | wiki ingest コミットが各 blog ブランチに混入 |
| 根本原因 | SKILL.md の "Post-merge" 指示が単一 claude -p セッション内で発火 |
| 修正 | バッチプロンプトに skip 指示 + `--final-wiki-ingest` フラグ + SKILL.md に skip-condition |
| 教訓 | LLM スキルでは「時系列の後で〇〇する」は成立しない。条件分岐と外部制御で副作用のタイミングを明示せよ |

「Post-merge」のような時系列ベースの指示は、**人間のオペレーションを前提にした書き方**だと気づきにくい罠だった。Skill 設計時には、**「LLM の実行モデルから見て、この指示はいつ実行されるか」**を必ず想像することが、ハーネスエンジニアリングの一部だと思う。

## 関連記事

- [「言語税」対策として CLAUDE.md を英語化する](/blogs/posts/2026/05/2026-05-13-claude-md-english-prompt-caching/) — Skill 設計の別角度（トークン削減）
- [CLAUDE.md+SKILL.md 英語化で 37.6% トークン削減 — tiktoken による実測結果と内訳](/blogs/posts/2026/05/2026-05-13-claude-md-english-tiktoken-measurement/)
- [ハーネスエンジニアリング](/blogs/wiki/concepts/harness-engineering/)
- [Claude Code](/blogs/wiki/tools/claude-code/)
