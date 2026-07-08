---
title: "/handoff スキルが海外でバズった理由 — Claude Code で計画して複数 Codex に並列投入する新ワークフロー"
date: 2026-06-15
lastmod: 2026-06-16
slug: "claude-code-handoff-codex-parallel"
draft: false
source_url: "https://github.com/hdknr/blogs/issues/1#issuecomment-4714981343"
categories: ["AI/LLM"]
tags: ["Claude Code", "handoff", "Codex", "git worktree", "並列処理"]
---

複数の案件を1人で抱えているエンジニアにとって、AIコーディングエージェントへの「実装待ち」は深刻な時間ロスだ。X（旧Twitter）で海外エンジニアの投稿が1万回以上閲覧されて注目を集めた。その投稿が紹介するのが、Claude Code の `/handoff` スキルを使って計画を立て、複数の Codex エージェントに並列で投げるワークフローだ。

## `/handoff` スキルとは何か

`/handoff` は Matt Pocock の [mattpocock/skills](https://github.com/mattpocock/skills) で公開されている Claude Code 用スキルだ（パス：`skills/productivity/handoff/`）。

その役割は「現在の Claude Code セッションの文脈を、別のエージェントが引き継げる形の構造化 Markdown に圧縮すること」に特化している。

生成されるドキュメントには、セッションの目標・現在の状況・未決定事項・次のエージェントが呼び出すべきスキルの提案（"suggested skills"）などが含まれる。実際の出力フォーマットはセッション内容によって柔軟に変わる。

重要な設計原則として、**既存の PRD やコミット・差分の内容はドキュメント内に繰り返さない**。パスや URL で参照するだけにとどめることで、handoff ドキュメント自体をコンパクトに保つ。センシティブな情報も自動的に編集される。

## なぜこれが問題を解決するのか

副業や複数案件を抱えているエンジニアが直面する典型的な詰まり：

- AIに「実装して」と指示して待っている間、別の案件は手が止まる
- 直列に処理していると、単純なタスクでも1日が終わる
- コンテキストを切り替えるたびに Claude Code に状況を再説明する手間がかかる

`/handoff` はこの「コンテキスト再説明コスト」を排除し、複数エージェントへの同時投入を可能にする。

## ワークフローの全体像

Ben Holmes が YouTube でデモを公開し、daily.dev にも掲載された。実践的なワークフローは次のとおりだ。

### ステップ1: Claude Code で計画を立てる

まず Claude Code 上でタスクを整理し、**`/grill-me`** スキルで計画を徹底的に問い詰める（`/grill-me` については[こちらの記事](/blogs/posts/2026/05/claude-code-grill-me/)を参照）。この段階で曖昧さを潰しておくことが後の並列化の精度を左右する。

### ステップ2: `/handoff` でドキュメントを生成する

```
/handoff
```

これだけで、現在のセッション状態を5セクションの Markdown に圧縮したドキュメントが生成される。このドキュメントが「次のエージェントへの引き継ぎ書」になる。

### ステップ3: 並列化できるタスクを分割する

handoff ドキュメントを見ながら、独立して実装できるサブタスクを洗い出す。

**並列化に向いているタスク**：
- 依存関係がなく、互いの結果を待たなくていいもの
- 曖昧さが低く、AIが自律して進められるもの
- 例）GitHub Actions 整備 ↔ UI コンポーネント実装

**並列化に向いていないタスク**：
- 前のタスクの出力を次が使うもの
- 設計判断が複数のファイルをまたぐもの

### ステップ4: git worktree で作業空間を複数作る

```bash
git worktree add -b feature/github-infra .worktrees/github-infra main
git worktree add -b feature/game-ui .worktrees/game-ui main
```

各 worktree はそれぞれ独立したブランチで、同じリポジトリの別のコピーとして機能する。ファイルが競合することなく複数の Codex が並行して書き込める。

Warp ターミナルを使うと worktree の切り替えが視覚的に管理しやすくなる。

### ステップ5: 各 worktree で Codex を起動する

```bash
# worktree A でターミナルを開いて Codex を起動
cd .worktrees/github-infra
codex "$(cat handoff.md) に基づいて GitHub Actions の CI/CD を整備して"

# 別のターミナルで worktree B を起動
cd .worktrees/game-ui
codex "$(cat handoff.md) に基づいてゲームの表示コンポーネントを実装して"
```

handoff ドキュメントの内容をプロンプトに含めることで、Codex は「プロジェクト全体の状況」を把握した上で担当タスクだけに集中できる。また、Codex がリポジトリルートの `AGENTS.md` を自動的に読み込む仕組みを利用して handoff 内容を渡す方法も有効だ。

### ステップ6: マージしてレビューする

各 Codex が実装を完了したら、Claude Code に戻って git diff を確認しながらマージレビューを行う。X ユーザーの BOOTOSHI（@KingBootoshi）が公開したパターンでは、Claude Code が各エージェントの git diff を自動レビューして人間に確認を求めるループを構成することも可能だ。

## `/handoff` スキルの導入方法

```bash
# mattpocock/skills リポジトリをクローン
git clone https://github.com/mattpocock/skills

# スキルを Claude Code のスキルディレクトリにコピー（productivity サブディレクトリに注意）
cp -r skills/productivity/handoff ~/.claude/skills/
```

またはプロジェクトのリポジトリに直接配置する：

```bash
cp -r skills/productivity/handoff .claude/skills/
```

## 実際の効果

このワークフローが注目を集めた理由はシンプルさだ。特別なツールや複雑な設定は不要で、既存の Claude Code + git worktree + Codex という組み合わせで完結する。副業で複数案件を同時進行させているエンジニアが「実装待ちで日が暮れる」問題を、エージェントの並列化によって解消できる。

ポイントをまとめると：

- **計画は Claude Code の `/grill-me` → `/handoff`** で一元管理
- **実装は Codex の並列 worktree** で同時進行
- **レビューは Claude Code** に戻って人間が確認

AIコーディングエージェントを「順番待ち」ではなく「チームで同時稼働」させる発想の転換が、このワークフローの本質だ。

## 関連ツール: parallel-code

より GUI 志向の選択肢として [johannesjo/parallel-code](https://github.com/johannesjo/parallel-code) という Electron 製 OSS アプリも存在する。タスクを投入すると自動で git ブランチと worktree を作成し、Claude Code・Codex・Gemini を選んで各 worktree で起動できる。完了後は組み込みの diff ビューアでレビューしてマージする仕組みだ。コマンドラインより視覚的に管理したい場合の選択肢となる。

---

副業エンジニアに限らず、複数のフィーチャーを並行して開発したいチームにも応用できるワークフローだ。「AIに指示して待つ」から「AIチームを並列で回す」への移行が、2026年の開発スタイルの次のフェーズになりつつある。
