---
title: "仕様駆動開発（SDD）とは？ 3 つのアプローチ・EARS 記法・Kiro / Spec Kit・TDD との違い"
date: 2026-11-13
lastmod: 2026-11-13
slug: "spec-driven-development-overview"
draft: false
source_url: "https://github.com/hdknr/blogs/issues/694#issuecomment-6843965319"
categories: ["AI/LLM"]
tags: ["仕様駆動開発", "SDD", "AI駆動開発", "開発手法", "tdd"]
---

**Spec-Driven Development（SDD：仕様駆動開発）** とは、コードを書く前に構造化された「仕様（Spec）」を定義する開発手法です。その仕様を **唯一の信頼できる情報源（SSoT: Single Source of Truth）** として、設計・実装・テストを進めます。

考え方そのものは新しくありません。OpenAPI（Swagger）や GraphQL のスキーマ定義を起点にする「API 仕様駆動開発」は以前からありました。いま改めて注目されているのは、**AI コーディングエージェントによる開発の品質と再現性を担保する手法** としてです。曖昧な自然言語のプロンプトで AI に丸投げする「バイブコーディング（Vibe Coding）」は、手戻りやスパゲッティコードを生みやすく、SDD はそれを防ぐガードレールとして使われています。

この記事では、SDD に「標準手法」はあるのか、どんな進め方・ツールが定着しつつあるのか、TDD とはどう違うのかを整理します。

## SDD に標準手法はあるか？

結論から言うと、**ISO や IEEE の規格のような、単一の厳格な標準は存在しません**。使う AI ツールやチームの規模によって、運用の深さはまちまちです。

ただし実務上は、次の 3 つがおおむね共有されています（いずれも規格ではなく、主要なツールに共通する型をまとめたものです）。

1. 4 段階の共通ワークフロー
2. 仕様をどこまで保守するかによる 3 つのアプローチ
3. 事実上の標準（デファクトスタンダード）になりつつある記法とツール群

順に見ていきます。

## SDD の 4 段階ワークフロー

ツールごとに呼び名は違いますが、基本的には次のステップで進めます。後述する Kiro の requirements → design → tasks は、この流れの典型です。

| ステップ | 内容 |
| --- | --- |
| 1. 要件定義（Requirements） | 「何を作るか（What）」「なぜ作るか（Why）」を明確にし、受け入れ基準（Acceptance Criteria）とスコープ外を文書化する |
| 2. 設計（Design） | 要件をもとに、技術選定・アーキテクチャ境界・DB スキーマ・API インターフェースなどの構造を定義する |
| 3. タスク分解（Tasks） | 設計を、AI が 1 回の生成で迷わず完結できる小さな実装単位（タスクリスト）に分割する |
| 4. 実装・検証（Implementation & Verification） | AI がタスクに沿ってコードとテストを生成し、仕様どおりに動くかを検証する |

ポイントは、AI に渡す単位が「要件」ではなく「タスク」であることです。要件をそのまま渡すと、設計判断の空白を AI が黙って埋めてしまいます。設計とタスク分解を人間がレビューできる成果物として先に出しておくことで、その空白が表に出ます。

## Spec-First / Spec-Anchored / Spec-as-Source：3 つのアプローチ

実装が終わったあとも仕様を保守し続けるかどうかで、SDD の運用は 3 つのアプローチに分かれます。この分類は広く参照されています。出典は、Thoughtworks の Birgitta Böckeler 氏が martinfowler.com で公開した記事「[Understanding Spec-Driven-Development: Kiro, spec-kit, and Tessl](https://martinfowler.com/articles/exploring-gen-ai/sdd-3-tools.html)」です。

| アプローチ | 特徴 | 向いているケース（筆者の見立て） |
| --- | --- | --- |
| **Spec-First**（仕様ファースト） | 実装前に仕様を書いて AI の指針にする。実装後に仕様を保守し続けることは前提としない | 小規模開発、プロトタイピング、SDD 導入の第一歩 |
| **Spec-Anchored**（仕様アンカー） | タスクが終わっても仕様を残し、システムの進化や保守のたびに仕様も更新し続ける | 中〜大規模のプロダクト、チーム開発、長期保守が必要なシステム |
| **Spec-as-Source**（仕様をソースとする） | 人間は仕様だけを編集し、コードには直接触れない。コードは仕様から AI が生成する | 高度な検証パイプラインが整った領域（現状は実験的） |

長く運用するプロダクトで現実的なのは **Spec-Anchored** です。Spec-First は始めやすい反面、実装が進むにつれて仕様とコードが乖離し、仕様が「書いた当時のメモ」に戻ってしまいます。仕様とコードの同期を保つには、仕様から導いた受け入れテストを CI で回すなど、乖離を機械的に検出する仕組みを併せて用意するのが実務的です。Spec-as-Source は理想形ですが、仕様の変更から生成し直したコードが正しいことを機械的に確かめる仕組みがないと成り立ちません。

なお Böckeler 氏の記事では、Kiro は主に Spec-First、GitHub Spec Kit も Spec-Anchored を志向しつつ実際の使われ方は Spec-First に近い、と評価されています。ツールを入れただけで Spec-Anchored になるわけではない、という点は押さえておきたいところです。

## SDD の代表的な記法とツール

### 仕様の記法（EARS・Gherkin）

仕様は Markdown で管理しつつ、要件の曖昧さを減らすために構造化された記法を取り入れるのが一般的です。

- **EARS 記法（Easy Approach to Requirements Syntax）**: Rolls-Royce の Alistair Mavin 氏らが提案した、決まった型に要件を当てはめる記法。常時成り立つ要件・イベント駆動・状態駆動・望ましくない振る舞いなど、いくつかのパターンがある
- **Gherkin 構文**: `Given`（前提）/ `When`（操作）/ `Then`（結果）で振る舞いを書く記法。BDD（振る舞い駆動開発）ツールの Cucumber で使われる

EARS のイベント駆動パターンは `WHEN <トリガー> THE SYSTEM SHALL <応答>` という型です（原典ではシステム名を入れて `the <システム名> shall` と書きますが、Kiro などでは `THE SYSTEM SHALL` の形がよく使われます）。この型で書いた要件の例です。

```text
WHEN ユーザーが誤ったパスワードを 5 回連続で入力したとき
THE SYSTEM SHALL そのアカウントを 15 分間ロックする
```

同じ振る舞いを Gherkin で書くと次のようになります。

```gherkin
Feature: ログイン試行の制限
  Scenario: パスワードを 5 回連続で間違えるとロックされる
    Given ユーザー "alice" が登録されている
    When 誤ったパスワードで 5 回連続ログインを試みる
    Then アカウントは 15 分間ロックされる
```

どちらも「条件」と「期待する結果」を分けて書かせるので、受け入れ基準やテストケースにそのまま落とし込めます。

EARS の 6 つのパターンや日本語での書き方は「[EARS 記法とは？ 6 つのパターンと日本語での書き方・Kiro での使い方](/blogs/posts/2026/11/ears-requirements-syntax/)」で詳しく解説しています。

### 専用 AI IDE・フレームワーク（Kiro・GitHub Spec Kit・OpenSpec）

- **[Kiro](https://kiro.dev/)**: AWS が提供する AI IDE。対話しながら要件（`requirements.md`）・設計（`design.md`）・タスク（`tasks.md`）の仕様ファイルを生成し、それに沿って実装する
- **[GitHub Spec Kit](https://github.com/github/spec-kit)**: GitHub が公開している仕様駆動開発用のツールキット。既存の AI コーディングエージェントに、原則（constitution）→ 仕様 → 計画 → タスク → 実装の流れを組み込む
- **[OpenSpec](https://github.com/Fission-AI/OpenSpec) / [cc-sdd](https://github.com/gotalab/cc-sdd) / [Spec Workflow MCP](https://github.com/Pimzino/spec-workflow-mcp)**: Claude Code や Cursor などの既存エージェントに SDD のワークフローを組み込むオープンソースのツール群

OpenSpec については「[OpenSpec — 仕様駆動開発でVibe Codingの「あとから全部作り直し」を防ぐ](/blogs/posts/2026/05/openspec-spec-driven-development/)」で詳しく紹介しています。

## SDD と TDD（テスト駆動開発）の違い

SDD は TDD と対立するものではなく、**上流工程を補完する関係** にあります。

| | SDD（仕様駆動） | TDD（テスト駆動） |
| --- | --- | --- |
| 先に定義するもの | 何を作るか・なぜ作るか | コードの期待される入出力（テストケース） |
| 対象の粒度 | システム全体の振る舞い、設計の境界 | 実装レベルの入出力 |
| 成果物 | 要件・設計・タスクの仕様書 | テストコード |

実務では、**SDD で要件と設計の仕様を確定させ、その仕様をもとに AI に TDD のサイクル（テスト作成 → 実装）を回させる** という組み合わせが効果的です。仕様が「何が正しいか」を決め、テストがそれを実行可能な形で固定し、実装がテストを通す、という役割分担になります。

## まとめ

- SDD は、コードより先に仕様を定義し、それを SSoT として設計・実装・テストを進める手法
- 単一の国際標準はないが、「要件定義 → 設計 → タスク分解 → 実装・検証」の 4 段階は主要なツールに共通している
- 仕様の保守レベルで Spec-First / Spec-Anchored / Spec-as-Source の 3 つに分かれ、長期運用なら Spec-Anchored が現実的
- 記法は EARS や Gherkin、ツールは Kiro・GitHub Spec Kit・OpenSpec などが使われている
- TDD とは補完関係にあり、SDD で仕様を確定させてから TDD で実装する組み合わせが効果的

バイブコーディングで何が失われるのかについては「[バイブコーディングの本当の問題は、誰も決めていない仕様が実装されることだ](/blogs/posts/2026/11/vibe-coding-is-vibe-specifying/)」も参照してください。
