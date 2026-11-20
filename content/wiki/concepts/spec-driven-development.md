---
title: "仕様駆動開発（SDD）"
description: "コードより先に構造化された仕様を書き、それを唯一の情報源として AI に設計・実装・テストを進めさせる手法。4 段階のワークフロー、Spec-First / Spec-Anchored / Spec-as-Source の 3 アプローチ、Kiro・Spec Kit・cc-sdd などのツール比較、TDD との関係、dpolivaev/spec-loop・hdknr 版 spec-loop の違い"
date: 2026-10-30
lastmod: 2026-11-20
aliases: ["SDD", "Spec-Driven Development", "Spec Loop", "spec-loop", "dpolivaev/spec-loop", "設計先行", "Design-First", "Spec-First", "Spec-Anchored", "Spec-as-Source", "タスクファイル", "生きたドキュメント", "Living Project Documents"]
related_posts:
  - "/posts/2026/10/spec-loop-design-first-ai-development/"
  - "/posts/2026/10/spec-loop-two-frameworks-comparison/"
  - "/posts/2026/11/vibe-coding-is-vibe-specifying/"
  - "/posts/2026/11/spec-driven-development-overview/"
  - "/posts/2026/11/kiro-ai-ide-intro/"
  - "/posts/2026/11/github-spec-kit-intro/"
  - "/posts/2026/11/cc-sdd-intro/"
  - "/posts/2026/11/spec-workflow-mcp-intro/"
  - "/posts/2026/11/spec-driven-development-org-maturity/"
  - "/posts/2026/11/sdd-ai-driven-development-practice/"
tags: ["仕様駆動開発", "SDD", "AI駆動開発", "Agent Skills", "開発手法", "claude-code", "要求定義", "tdd"]
---

## 概要

**仕様駆動開発（SDD: Spec-Driven Development）** は、コードを書く前に構造化された仕様を定義し、それを**唯一の信頼できる情報源（SSoT）**として設計・実装・テストを進める手法である。OpenAPI や GraphQL のスキーマを起点にする API 仕様駆動開発は以前からあったが、いま注目されているのは **AI コーディングエージェントの品質と再現性を担保するガードレール**としてである。曖昧なプロンプトで丸投げする [Vibe Coding](/blogs/wiki/concepts/vibe-coding/) は、誰も決めていない仕様を AI が黙って埋め、手戻りを生む。

ISO や IEEE のような単一の標準はない。共有されているのは、4 段階のワークフロー、仕様の保守の深さによる 3 つのアプローチ、事実上の標準になりつつある記法とツールの 3 つである。すべてに共通する出発点は **AI に仕様の空白を黙って埋めさせない**ことにある。

## 詳細

### 4 段階のワークフロー

| ステップ | 内容 |
|---|---|
| 1. 要件定義 | 何を・なぜ作るか、受け入れ基準とスコープ外を文書化する |
| 2. 設計 | 技術選定・アーキテクチャ境界・DB スキーマ・API を定義する |
| 3. タスク分解 | AI が 1 回で迷わず完結できる小さな実装単位に分ける |
| 4. 実装・検証 | AI がタスクに沿ってコードとテストを作り、仕様どおりかを確かめる |

AI に渡す単位は「要件」ではなく「タスク」である。要件をそのまま渡すと設計判断の空白を AI が埋めてしまう。設計とタスクを人間がレビューできる成果物として先に出すことで、空白が表に出る。各段階で人間が承認してから次へ進むのが基本で、承認を省く「Quick Spec」のようなモードは速さと引き換えになる。

### 3 つのアプローチ

Thoughtworks の Birgitta Böckeler 氏が martinfowler.com で示した分類で、実装後も仕様を保守し続けるかで分かれる。

| アプローチ | 特徴 | 向くケース |
|---|---|---|
| **Spec-First** | 実装前に仕様を書いて AI の指針にする。保守は前提にしない | 小規模、プロトタイプ、導入の第一歩 |
| **Spec-Anchored** | タスク後も仕様を残し、変更のたびに更新し続ける | 長期保守するプロダクト、チーム開発 |
| **Spec-as-Source** | 人間は仕様だけを編集し、コードは仕様から生成する | 検証パイプラインが整った領域（実験的） |

長期運用で現実的なのは Spec-Anchored だが、**ツールを入れただけでは Spec-Anchored にならない**。Böckeler 氏の評価では Kiro は主に Spec-First、Spec Kit も Spec-Anchored を志向しつつ実態は Spec-First に近い。仕様から導いた受け入れテストを CI で回すなど、乖離を機械的に検出する仕組みと、誰がいつ仕様を更新するかの運用ルールを併せて持つ。

### 記法

- **[EARS](/blogs/wiki/concepts/ears/)** — 要件を `When <トリガー>, the <システム> shall <応答>` などの型に当てはめる。正常系（When）と異常系（If / Then）を書き分けられる
- **[Gherkin](/blogs/wiki/concepts/bdd-gherkin/)** — `Given / When / Then` で振る舞いを書き、Cucumber でテストとして実行する

「要件は EARS で書いて人間がレビューし、受け入れテストは Gherkin で書く」という分担にすると、要件からテストまでを追跡しやすい。

### ツールの比較

| ツール | 形態 | 進め方 | 特徴 |
|---|---|---|---|
| [Kiro](/blogs/wiki/tools/kiro/) | AWS の専用 AI IDE（CLI もあり） | 要件 → 設計 → タスク → 実装 | Spec・Steering・Hooks が IDE に統合 |
| [GitHub Spec Kit](/blogs/wiki/tools/github-spec-kit/) | 既存エージェントに足すツールキット（MIT） | 原則 → 仕様 → 計画 → タスク → 実装 | constitution で AI の判断を縛る |
| [cc-sdd](/blogs/wiki/tools/cc-sdd/) | 既存エージェントに足すスキル（MIT） | discovery → 要件 → 設計 → タスク → 実装 | Kiro と同じ文書構成。サブエージェントで実装とレビュー |
| [Spec Workflow MCP](/blogs/wiki/tools/spec-workflow-mcp/) | MCP サーバー（GPL-3.0） | 要件 → 設計 → タスク | ダッシュボードで承認を記録。メンテナンス休止中 |
| [OpenSpec](/blogs/posts/2026/05/openspec-spec-driven-development/) | 既存エージェントに足すスキル（MIT） | 提案 → 適用 → アーカイブ | 変更を差分で扱う |

選び方の目安は、IDE ごと統合したいなら Kiro、手元のエージェントで決まった手順を試すなら Spec Kit、Kiro の文書構成を Claude Code や Codex で使うなら cc-sdd、既存コードへの変更を軽く回すなら OpenSpec。どのツールでも、**小さな変更にまで仕様を作るとレビューの手間が上回る**ので、変更の大きさで使い分ける（cc-sdd の `/kiro-discovery` のように入口で振り分ける仕組みもある）。

### TDD との関係

SDD は TDD と対立せず**上流を補完する**。SDD は「何を作るか・なぜ」とシステム全体の振る舞いを、TDD は実装レベルの入出力を先に定義する。SDD で要件と設計を確定させ、AI に TDD（RED → GREEN）を回させるのが効果的で、Spec Kit の constitution の「Test-First」や cc-sdd の実装役もこの形をとる。

### 2 つの spec-loop

[dpolivaev/spec-loop](https://github.com/dpolivaev/spec-loop)（Freeplane の開発から生まれた MIT ライセンスのスキル集）は、バイブコーディングとウォーターフォールの中間を取り、**仕様は「次の一歩」に必要な範囲だけ書き、レビューしてからテスト付きで実装する**ことを繰り返す。

作業は **PLAN・EXECUTION・DONE** の 3 フェーズで、遷移にはどちらも人間の明示的な承認が要る。新しい依頼や拡張はすべて PLAN に戻し、モデルが惰性で実装を続けるのを防ぐ。スキルは clarify（推測で埋めない）・plan・break down・approve・execute / review の流れで、計画の形式は作業の大きさで選ぶ（taskless / chat-only / task file / 分割）。**形式への同意は実行の承認ではない**。分割は層ごとではなく縦切りが基本。

タスクファイルの要点は、**Research**（観察済みの事実だけ）、**Analysis**（because / so that で判断を 1 行ずつ）、**Design**（最終的な名前だけ。`Helper` のような仮名は設計の欠陥とみなす）、**Constraints**（Design より優先）、**Test specification**（ないと承認に進めない）。PlantUML の図とテスト項目に **+（追加）・=（再利用）・±（変更）** の変更記号を付ける。タスクファイルは短命でリリース後に消し、長く残すのは仕様・API 契約・ADR・用語集などの狭い**生きたドキュメント**だけ。それらはコードと同じ増分で更新してレビューに含める。

| 観点 | dpolivaev 版 | hdknr 版 |
|---|---|---|
| 受け持つ工程 | 方向が決まった後の調査・計画・実装・レビュー | 要求確定・仕様レビュー・見積り・提案書・Issue への引き渡し |
| 人間の相手 | 開発者 1 人 | 利用者・予算責任者・決裁者 |
| 仕様の単位と寿命 | 次の小さな仕様 1 つ。リリース後に削除 | 版ごとの全体（`docs/v<n>/`）。リリースした版は凍結 |
| 関門の判定 | 人間の承認 | スクリプトと、書き込みツールを持たない別ティアの判定役 |
| 実装への渡し方 | 計画と実装が同じループの中 | `spec_ir.json` → Red テスト・Issue で dev-loop へ |

hdknr 版（[要求仕様書作成ループ](/blogs/wiki/concepts/requirements-spec-loop/)）で dpolivaev 版と重なるのは後ろの **dev-loop** である。違いの多くは相手の違いから来る。開発者 1 人が毎回承認するなら人間の目が最後の関門になり、仕様の細部を読まない利用者・決裁者と回すなら細部の検査を機械と別モデルに任せる（[maker-checker](/blogs/wiki/concepts/maker-checker/)）。組み合わせるなら、**計画の書き方は dpolivaev 版から借り、停止条件は dev-loop のまま**が現実的。

### 現場で回すときの勘所

アサイン社の事例（要件定義 → 設計 → 実装 → PR）では、各フェーズの**出力を次のフェーズの入力**にして、前段の文書を MCP 経由で AI に読ませる。効果を決めるのは「仕様を書くこと」より、**仕様をどの粒度で区切り、どの文書をどのフェーズに渡すか**の設計である。

- 何度も参照される文書を見極める（API 設計書は全工程で 5 回参照された）。長い作業の途中で AI が現在地を見失わないよう、全体設計書を地図として渡す
- 画面仕様は「左上に #D70C18 のアイコン」のように解釈の余地なく書く
- 作業は 1 スコープ 1 PR に区切る。大雑把な指示は auto-compact を招いて精度が落ちる
- 残った課題は**スコープの肥大化**と**セルフレビューの負荷**。対策は、ベテランの分割ルールなどの暗黙知を言語化して渡すこと、規約に「何をすべきでないか」を書き、レビューの指摘を文書へ戻し続けること

### 組織に広げる 6 つの段階

SDD を個人の実験から組織の開発能力にする道のりを、Microsoft Tech Community の記事は **実験 → 再現性 → 一貫性 → 協調 → ガバナンス → 計測** の 6 段階で示す（厳密な順序でも認定モデルでもない目安）。前提は、SDD とは AI に先に文書を書かせることではなく、**変更の意図をデリバリーの終わりまで検証可能な形で保つこと**であり、広がらないときに足すべきはテンプレートやエージェントではない、という点である。

| 段階 | 目的 | 次へ進む合図 |
|---|---|---|
| 1. 実験 | 変更の意図を明示する | 作者と話さなくても他の人が意図を理解できる |
| 2. 再現性 | チームの実践にする | 特定の詳しい人に頼らずチームが回せる |
| 3. 一貫性 | 全社の原則・技術標準・現場の判断の 3 層を分ける | 何が必須で、何を調整してよく、誰が決めるかを区別できる |
| 4. 協調 | リポジトリの境界を越えて計画する | 分散した変更が 1 つのデリバリーにどう寄与し、互換性をどう検証するかを説明できる |
| 5. ガバナンス | 開発フローに組み込む | 不要な承認の連鎖なしに不確実さと手戻りが減る |
| 6. 計測 | 活動ではなく結果を測る | 証拠を遵守の強制ではなく実践の調整に使っている |

- 複数リポジトリにまたがる機能は、目的・契約・E2E の受け入れ基準を置く**アンカーリポジトリ**で計画し、各サービスが自分のスライスを再検証する（必須ではない選択肢）。**両方の PR が緑でも統合の完成は証明されない**ので、検証済みのバージョンとデプロイ順を記録する
- 「関わる人」と「責任を持つ人」を分ける。Actions はファイルの存在しか確かめられず、CODEOWNERS だけでは承認を強制しない。チェックは情報提供から始めてブロッキングに上げる
- 計測は文書数やコマンドの実行回数ではなく、トレーサビリティ・曖昧さによる手戻り・依存の事前発見・レビューの負荷・実践の持続性で見る
- 展開は診断 → 基盤（フローと責任分担）→ 1 サービスでのパイロット → 段階的な自動化 → 拡大の順。中央集権を強めても成熟度は自動的には上がらない

### 空白を埋めさせず、表に出させる

Vibe Coding の根には「業務を持つ側が要求・条件・例外を定義しきれない」という AI 以前からの問題がある。仕様駆動開発では、従来ビジネスアナリストの力量に依存していた仕事を AI と検査器の仕組みにし、AI を「埋める側」ではなく「問いを立てる側」に置く。

| 定義しきれない理由 | 対案 |
|---|---|
| 暗黙知は当たり前すぎて書かれない | 具体的な場面と選択肢・推奨を AI に挙げさせて選んでもらい、答えを仕様とテストに残す |
| 例外は組み合わせで爆発する | 決定表で抜けと矛盾を機械に検出させ、業務フローは形式検査で反例を探す |
| 見て触らないと分からない要求がある | 捨てるプロトタイプを AI に作らせ、分かったことを仕様に書き起こす |
| 書いた本人は書き漏れに気づけない | 文脈とモデルを変え、書き込み権限のないレビュー役に突かせる |

出てきた空白は**決める権限を持つ人**が決める。業務要件（誰が何をできるか、どの条件で断るか、失敗をどう見せるか）は業務を持つ側に返し、技術の空白は開発者が決めて記録する。業務要件の空白だけは AI に決めさせない。hdknr 版 spec-loop は、暗黙知を Q&A 表の選択肢付き質問に、組み合わせを Formal Checker の検査器（[形式手法](/blogs/wiki/concepts/formal-methods/)）に、書き漏れを別ティアの判定役に割り当てている。

共通する根っこは、**推測で埋めない**、**人間の判断を飛ばさない**、**小さく回す**、**テストを仕様の一部にする**（テストを書き起こせない仕様は未確定）、**決まりの住所を 1 つにする**の 5 つ。

## 関連ページ

- [EARS 記法](/blogs/wiki/concepts/ears/) — 要件を決まった型で書く記法
- [BDD と Gherkin 構文](/blogs/wiki/concepts/bdd-gherkin/) — 受け入れテストを振る舞いで書く
- [Kiro](/blogs/wiki/tools/kiro/) / [GitHub Spec Kit](/blogs/wiki/tools/github-spec-kit/) / [cc-sdd](/blogs/wiki/tools/cc-sdd/) / [Spec Workflow MCP](/blogs/wiki/tools/spec-workflow-mcp/) — SDD のツール
- [要求仕様書作成ループ](/blogs/wiki/concepts/requirements-spec-loop/) — hdknr 版 spec-loop。開発の手前で要求と予算を確定させる
- [Vibe Coding](/blogs/wiki/concepts/vibe-coding/) — SDD が防ごうとする失敗パターン
- [形式手法](/blogs/wiki/concepts/formal-methods/) — 決定表の抜け・矛盾や業務フローの反例を検査器で探す
- [作る役と確かめる役の分離（maker-checker）](/blogs/wiki/concepts/maker-checker/) — 別ティアの判定役
- [ループエンジニアリング](/blogs/wiki/concepts/loop-engineering/) — 人間のゲートと機械のゲート
- [エクストリーム・プログラミング（XP）](/blogs/wiki/concepts/extreme-programming/) — Baby Steps・Incremental Design という同じ発想の源流

## ソース記事

- [Spec Loop — 次の小さな仕様だけを書いて回す、AI エージェント向け仕様駆動開発フレームワーク](/blogs/posts/2026/10/spec-loop-design-first-ai-development/) — 2026-10-25
- [AI 仕様駆動開発の 2 つの spec-loop を比べる — 実装ループと要求確定ループ](/blogs/posts/2026/10/spec-loop-two-frameworks-comparison/) — 2026-10-25
- [バイブコーディングの本当の問題は、誰も決めていない仕様が実装されることだ](/blogs/posts/2026/11/vibe-coding-is-vibe-specifying/) — 2026-11-08
- [仕様駆動開発（SDD）とは？ 3 つのアプローチ・EARS 記法・Kiro / Spec Kit・TDD との違い](/blogs/posts/2026/11/spec-driven-development-overview/) — 2026-11-13
- [Kiro とは？ AWS の仕様駆動 AI IDE の Spec・Steering・Hooks と料金プラン](/blogs/posts/2026/11/kiro-ai-ide-intro/) — 2026-11-13
- [GitHub Spec Kit とは？ 仕様駆動開発のコマンド・constitution と Kiro との違い](/blogs/posts/2026/11/github-spec-kit-intro/) — 2026-11-13
- [cc-sdd とは？ Claude Code・Codex で Kiro 式の仕様駆動開発を回すスキルと使い方](/blogs/posts/2026/11/cc-sdd-intro/) — 2026-11-13
- [Spec Workflow MCP とは？ ダッシュボードで仕様を承認しながら進める MCP サーバーの使い方と注意点](/blogs/posts/2026/11/spec-workflow-mcp-intro/) — 2026-11-13
- [組織で仕様駆動開発（SDD）を広げる 6 つの段階 — Spec Kit を個人の実験からチームの開発能力へ](/blogs/posts/2026/11/spec-driven-development-org-maturity/) — 2026-11-16
- [仕様駆動開発（SDD）の実践事例 — PRD から PR まで AI に渡す設計書と 2 つの課題](/blogs/posts/2026/11/sdd-ai-driven-development-practice/) — 2026-11-17
