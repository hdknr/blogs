---
title: "mattpocock/skills — 有名エンジニアが毎日使う Claude Code スキル集を .claude ごと公開、13万スター突破"
date: 2026-06-16
lastmod: 2026-06-16
slug: "mattpocock-skills"
draft: false
source_url: "https://github.com/hdknr/blogs/issues/1#issuecomment-4714883999"
description: "Matt Pocock が本番開発で使う Claude Code スキル15種を npx skills@latest add mattpocock/skills でインストールできる。/grill-me・/tdd・/diagnose 等のスキルで vibe coding から工学的開発へ移行する方法を解説する。"
categories: ["AI/LLM"]
tags: ["claude-code", "TypeScript", "tdd", "開発効率化", "prompt"]
---

## 概要

TypeScript の第一人者として知られる Matt Pocock が、自身の `.claude` ディレクトリをそのままオープンソース化したリポジトリ [**mattpocock/skills**](https://github.com/mattpocock/skills) が急速に注目を集め、13万スターを超えた。[4月の公開直後に 22,000 スターで話題になったリポジトリ](/blogs/posts/2026/04/matt-pocock-skills-for-real-engineers/)の約2か月後のアップデートとして、改めて全スキルの設計思想と使い方を整理する。

「雰囲気コーディング（vibe coding）」ではなく、実際の本番開発で使える工学的なスキルセットを集めたものとして、海外エンジニアコミュニティで話題になっている。

> "My agent skills that I use every day to do real engineering - not vibe coding."
> — Matt Pocock

## インストール

セットアップは30秒で完了する。

```bash
npx skills@latest add mattpocock/skills
```

コマンド実行後、使用したいスキルと適用するコーディングエージェント（Claude Code など）を選択する。まず **`/setup-matt-pocock-skills`** を選んで初期設定を行うことが推奨されている。

初期設定では以下の項目を対話式で確認する：

- 利用するイシュートラッカー（GitHub / Linear / ローカルファイル）
- トリアージ時に付与するラベル
- ドキュメントの保存先

## なぜこのリポジトリが注目されるのか

### ソフトウェアエンジニアリングの基本を AI 時代に再実装

Matt Pocock 自身が README で述べているように、このスキル集は「AI コーディングの典型的な失敗パターン」に対処するために設計されている。以下、4つの失敗パターンとその対処スキルを整理する。

### 失敗パターン 1: エージェントが期待通りに動かない

**原因**: 開発者とエージェントの間に「認識のズレ」が生まれる。人間のエンジニア同士でも起きる、仕様の齟齬と同じ問題だ。

**対策**: `/grill-me` スキル

```text
/grill-me
```

エージェントが実装前にユーザーを徹底的にインタビューし、要件の不明点を洗い出す。このスキルは「最も人気のあるスキル」と紹介されており、変更を加えるたびに使うことが推奨されている。

コードを伴う場合は `/grill-with-docs` が上位互換。ドメイン固有の語彙（CONTEXT.md）とアーキテクチャ上の判断記録（ADR）も同時に整備できる。詳しくは[grill-me 解説記事](/blogs/posts/2026/05/claude-code-grill-me/)も参照。

### 失敗パターン 2: エージェントが冗長すぎる

**原因**: エージェントはプロジェクト固有の用語を知らないため、1つの概念を20語かけて説明する。

**対策**: 共有語彙（CONTEXT.md）の構築

`/grill-with-docs` が自動で `CONTEXT.md` を生成・更新する。たとえば「セクション内のレッスンがファイルシステム上に実体化されたとき」という説明が、`マテリアライゼーションカスケード` という1語に短縮される。

この効果は単なる簡潔化にとどまらない。

- 変数・関数・ファイル名が共有語彙で一貫して命名される
- コードベースのナビゲーションがエージェントにとって容易になる
- エージェントが思考に使うトークン数が減る

### 失敗パターン 3: 生成されたコードが動かない

**対策**: TDD ループと診断スキル

```text
/tdd
```

`/tdd` スキルはテスト駆動開発（赤→緑→リファクタリング）のループをエージェントに適用する。「まず失敗するテストを書かせ、それを通す」という手順により、フィードバックを確認せずに暴走するエージェントの問題に対処できる。

デバッグには `/diagnose` スキルが対応している。「再現 → 最小化 → 仮説 → 計測 → 修正 → 回帰テスト」という規律あるループを実行させる。

### 失敗パターン 4: コードがごちゃごちゃになる

**対策**: アーキテクチャ改善スキル

AI の登場により、コードの増加速度が人間だけの時代とは比べものにならないほど速くなった。コード量の増加に比例して、技術的負債の蓄積も速まる。

```text
/improve-codebase-architecture
```

数日に1回実行することで、いわゆる「泥団子（Ball of Mud）」状態になりかけたコードベースを救出できる。`CONTEXT.md` のドメイン語彙と ADR に基づいて、モジュールを深化させる機会を特定する。

## スキル一覧

### エンジニアリング系

| スキル | 用途 |
|---|---|
| `/grill-with-docs` | コード変更前の要件詰め + 語彙整備 |
| `/tdd` | 赤→緑→リファクタリングのテスト駆動開発 |
| `/diagnose` | バグと性能問題の段階的診断ループ |
| `/to-prd` | 会話内容を PRD 化して GitHub Issue に投稿 |
| `/to-issues` | PRD を独立した GitHub Issues に分解 |
| `/triage` | イシューをステートマシンでトリアージ |
| `/zoom-out` | コードをシステム全体の文脈で説明させる |
| `/improve-codebase-architecture` | アーキテクチャ改善の機会を発見 |
| `/prototype` | 設計を検証するための捨てプロトタイプ作成 |
| `/setup-matt-pocock-skills` | 初期設定（最初に1回実行） |

### 生産性系

| スキル | 用途 |
|---|---|
| `/grill-me` | 計画・設計のインタビューセッション |
| `/caveman` | トークン使用量を75%削減する超圧縮モード |
| `/handoff` | 会話をハンドオフ文書にまとめ別エージェントに引き継ぐ |
| `/teach` | 複数セッションにまたがる学習サポート |
| `/write-a-skill` | 新しいスキルを正しい構造で作成 |

### その他

| スキル | 用途 |
|---|---|
| `/git-guardrails-claude-code` | 危険な git コマンドをブロックするフック設定 |
| `/setup-pre-commit` | Husky + lint-staged + Prettier + 型チェック設定 |

## どこが「すごい」のか

このリポジトリの本質は、スキルの内容そのものよりも「配布方法」にある。

通常、AI エージェントの使い方は個人の試行錯誤に委ねられている。しかし `mattpocock/skills` は、熟練エンジニアが実務で磨き上げた「考え方のパターン」を、再利用可能な形で即座にインストールできる仕組みを提供している。

`npx skills@latest add mattpocock/skills` の1コマンドで、『達人プログラマー』や DDD（ドメイン駆動設計）の思想に基づいた開発プロセスを、自分のエージェント環境に取り込める。

## まとめ

`mattpocock/skills` は「AI ができることを最大化する」ためではなく、「ソフトウェアエンジニアリングの基本を AI 時代にも守り続ける」ために作られたツール集だ。

雰囲気で書いてすぐ動かなくなるコードではなく、テスト・設計・共有語彙という基礎の上に AI の速度を乗せる——そのアプローチに、13万人以上のエンジニアが共感している。

- GitHub: [mattpocock/skills](https://github.com/mattpocock/skills)
- インストール: `npx skills@latest add mattpocock/skills`
- 詳細な使い方はニュースレター: [aihero.dev/s/skills-newsletter](https://www.aihero.dev/s/skills-newsletter)
