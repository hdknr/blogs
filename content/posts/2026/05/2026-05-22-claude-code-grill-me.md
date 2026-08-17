---
title: "grill-me — コードを1行も書く前にAIに徹底的に詰められる、最も人気の Claude Code スキル"
date: 2026-05-22
lastmod: 2026-05-22
slug: "claude-code-grill-me"
draft: false
description: "mattpocock/skills の grill-me は、コードを書く前に AI が設計の盲点を洗い出す4文の Claude Code スキル。深さ優先の質問戦略と Codebase-First 原則で、ミスアライメントを事前に解消する。"
source_url: "https://github.com/hdknr/blogs/issues/1#issuecomment-4514466911"
categories: ["AI/LLM"]
tags: ["claude-code", "grill-me", "AI活用", "プロンプト設計", "設計レビュー"]
---

## grill-me とは何か

[`mattpocock/skills`](https://github.com/mattpocock/skills) は、Total TypeScript で知られる Matt Pocock が自分の `~/.claude/skills/` から実際に使っている 23 本のスキルをそのまま公開したリポジトリだ。「教材向けに整えた」ではなく「本番運用している実物」というのが特徴で、X（旧 Twitter）でも注目を集めている。

その中でも最も人気が高いのが **`/grill-me`** だ。スキルの定義は英文 4 文だけ。しかしこの短さが本質で、「コードを 1 行も書く前に AI があなたを徹底的に詰める」という仕組みを実現する。リポジトリには engineering・productivity・misc の 3 カテゴリにわたる 18 本以上のスキルが収録されている。

実際のスキル定義（`skills/productivity/grill-me/SKILL.md`）は次のとおり：

```markdown
Interview me relentlessly about every aspect of this plan until we reach a shared understanding.
Walk down each branch of the design tree, resolving dependencies between decisions one-by-one.
For each question, provide your recommended answer.

Ask the questions one at a time.

If a question can be answered by exploring the codebase, explore the codebase instead.
```

## なぜ「詰め」が必要なのか

生成 AI にコードを書かせる際の最大の落とし穴は、**曖昧なまま走り出すこと**だ。「なんとなくこういうのを作りたい」で投げると、それらしいコードは出てくるが、後から要件とのズレが発覚して作り直しになる。

Matt Pocock 自身も [README](https://github.com/mattpocock/skills#1-the-agent-didnt-do-what-i-want) でこう述べている：

> The most common failure mode in software development is misalignment. You think the dev knows what you want. Then you see what they've built - and you realize it didn't understand you at all.

`/grill-me` はこのミスアライメントを事前に解消するためのスキルだ。AI が「答えを出す役」ではなく「質問をする役」に徹することで、人間が無意識に回避していた判断を引きずり出す。

## 仕組みのポイント

### 深さ優先の質問戦略

計画を決定木として捉え、**1 つの枝を掘り切ってから次に進む**。「15 個の質問を一気に投げて答えられない」という典型的な失敗パターンを回避している。常に 1 問ずつ聞いてくるので、会話が迷子にならない。

### Codebase-First 原則

「コードベースを調べれば分かる質問は自分で調べてから聞く」という原則が組み込まれている。

> If a question can be answered by exploring the codebase, explore the codebase instead.

つまり「モジュール X はキャッシュ処理していますか？」とは聞かない。モジュール X を自分で読んだ上で「TTL キャッシュが 5 分で切れる設計でしたが、追加するキャッシュ層とどう整合させますか？」と鋭く聞いてくる。ユーザーの時間を奪わない設計だ。

### 各質問に推奨回答を添える

> For each question, provide your recommended answer.

ただ詰めるだけでなく、AI 自身が「こう思う」という推奨案をセットで出してくる。これにより会話が「詰問」ではなく「共同設計」に変わる。

## 7 種類の質問パターン

grill-me を試したユーザーの分析によると、AI が使う質問の切り口はシニアエンジニアの設計レビューと重なる 7 種類に分類できる：

| 観点 | 例 |
|---|---|
| 実現可能性 | この制約下で本当に動くのか |
| 依存関係 | 先に解くべき前提は何か |
| エッジケース | こうなったらどうする |
| 代替案 | なぜこれで、なぜ A ではないのか |
| スコープ | 意図的に後回しにしているのか |
| 順序 | 何から始めるべきか |
| 失敗モード | 壊れた時の回復はどうするか |

### 関連スキル：grill-with-docs

エンジニアリング向けには [`/grill-with-docs`](https://github.com/mattpocock/skills/blob/main/skills/engineering/grill-with-docs/SKILL.md) も用意されている。`/grill-me` の機能に加えて、プロジェクトの共通言語ドキュメント（`CONTEXT.md`）や ADR（Architecture Decision Records）の更新も同時に行う。

Matt Pocock は「共通言語を持つことで、変数名・ファイル名の一貫性が上がり、エージェントが思考に使うトークン数も減る」と説いており、`/grill-with-docs` はそのベストプラクティスを自動化したものだ。

## インストール方法

```bash
npx skills@latest add mattpocock/skills
```

インタラクティブなセレクターでほしいスキルを選び、Claude Code などのエージェントにインストールできる。`/setup-matt-pocock-skills` を最初に実行してリポジトリごとの設定（Issue トラッカー連携など）を済ませておくと、他のスキルも快適に動く。

## コーディングより「問い」の設計が差になる時代

`/grill-me` が示唆するのは、AI 時代のエンジニアに求められるスキルの変化だ。コードを書く作業自体はコモディティ化しつつある。差がつくのは「何を作るかの解像度」であり、設計の詰め方、問いの立て方だ。

このアプローチは開発以外にも転用できる。新規事業の企画、PRD の作成、採用要件の定義、組織設計——いずれも「誰も深く問い直してくれないまま進む」から失敗する。AI が徹底的に詰めてくれる文化が広がれば、意思決定の質は底上げされる。

4 文のスキル定義でここまでできるという事実は、プロンプト設計においても示唆が深い。「長ければ良い」ではなく、「適切な言葉を適切なタイミングで使わせる」設計が本質なのだ。
