---
title: "仕様駆動開発（Spec Loop）"
description: "AI コーディングエージェントに「次の小さな仕様だけを書き、レビューし、テスト付きで実装する」を繰り返させる設計先行型の進め方。dpolivaev/spec-loop と、開発の手前を受け持つ hdknr 版 spec-loop との受け持ちの違い"
date: 2026-10-30
lastmod: 2026-10-30
aliases: ["Spec Loop", "spec-loop", "dpolivaev/spec-loop", "設計先行", "Design-First", "タスクファイル", "生きたドキュメント", "Living Project Documents"]
related_posts:
  - "/posts/2026/10/spec-loop-design-first-ai-development/"
  - "/posts/2026/10/spec-loop-two-frameworks-comparison/"
tags: ["仕様駆動開発", "AI駆動開発", "Agent Skills", "開発手法", "claude-code"]
---

## 概要

AI エージェントに開発を任せるとき、仕様をどこまで先に書くかには 2 つの失敗パターンがある。意図だけ伝えて隙間をモデルに埋めさせる**バイブコーディング**（判断の経緯が残らない巨大な差分、レビューが「考古学」になる）と、それを避けて完全な仕様を先に書こうとする**ウォーターフォール**（制約は実装中に見つかるので仕様が膨らみ、変更を阻むか無視される）である。

[dpolivaev/spec-loop](https://github.com/dpolivaev/spec-loop)（Freeplane の開発から生まれた MIT ライセンスのスキル集）はその中間を取り、**仕様は「次の一歩」に必要な範囲だけ書き、レビューしてからテスト付きで実装する**ことを繰り返す。同名の hdknr 版 spec-loop は開発の手前で「何を作るか」を確定させるもので、受け持つ工程が違う（[要求仕様書作成ループ](/blogs/wiki/concepts/requirements-spec-loop/)）。

## 詳細

### フェーズと人間の承認

作業は **PLAN・EXECUTION・DONE** の 3 フェーズで、PLAN → EXECUTION と EXECUTION → DONE の遷移にはどちらも人間の明示的な承認が要る。新しい依頼・追加修正・拡張はすべて PLAN に戻す。依頼が変わったのにモデルが**惰性で実装を続ける**のを防ぐためで、承認済みの意図を変える発見が実装中にあった場合もタスクを更新して再承認を取る。

| ステップ | スキル | 内容 |
|---|---|---|
| clarify | `spec-loop-clarify-task` | 計画の前・途中で重要な未解決の問いを解消する（推測で埋めない） |
| plan | `spec-loop-plan-task` | 計画の形式を選んでタスクを書く。ADR などへの振り分けも |
| break down | `spec-loop-plan-work-breakdown` | 大きな作業をサブタスク・複数タスクに分割 |
| approve | `spec-loop-prepare-execution-approval` | 承認できる状態に整え、人間が承認 |
| execute / review | `spec-loop-implementation-flow` | コード・テスト・関連ドキュメントの更新を統制し、review へ |

計画の形式は作業の大きさで選ぶ。taskless（ドキュメントだけ、または合意済みのごく小さな実装）、chat-only task（Scope・Design・Test specification の 3 セクションだけ）、**task file（既定）**、サブタスク付き・複数タスクへの分割。軽い形式を使うときは理由を説明して許可を求めるが、**形式への同意は実行の承認ではない**。分割は層ごと（scaffolding / model / UI）ではなく、単独でリリースできる縦切り（vertical slice）が基本。

### タスクファイル

セクションは見出しではなく太字ラベルの箇条書きで並べる（サブタスクで階層が深くなりすぎないため）。要点は次のとおり。

- **Research** — 実装前の現状について観察・確認済みの事実だけ。今のタスクに必要な範囲に意図的に絞る。書き残すので、人間はコードを書く前に「正しい箇所を調べたか」を確かめられ、レガシーでの白紙からの作り直しを防ぐ
- **Analysis** — 確定した判断を because / so that で 1 行ずつ記録する台帳。「ユーザーがそう言ったから」は理由にならない
- **Design** — 実装の契約。最終的な名前だけを使い、`Helper` や `Manager` のような仮の名前は原則禁止。良い名前が付かないなら設計の欠陥とみなす
- **Constraints** — Design と矛盾したら Constraints が優先
- **Test specification** — 自動テストの項目。これがないと承認に進めない

Research には現状を、Design には目標を PlantUML で描き、クラス図とテスト項目に **+（追加）・=（変更せず再利用）・±（変更）** の変更記号を付ける。状態は `backlog` / `in-progress` / `review` / `done` のフォルダで管理して `git mv` で動かし、`done` への移動は常にユーザーだけが行う。

### 短命なタスクファイルと生きたドキュメント

タスクファイルは短命な作業成果物で、リリースタグを作ったら作業ツリーから消す。長く残すのは仕様・API 契約・ADR・用語集などの**生きたドキュメント**だけで、範囲も狭く保つ。コード変更で直す必要があればタスクの Design に列挙し、**コードと同じ増分で完了させてレビューに含める**（影響がなければ `None affected`）。

用語集は特に重視され、新しい用語を足す前に**綴りではなく意味で**既存の抽象と同じかを確かめる。完了も「コードが動いた」からは推論しない。承認済み設計の実装、テスト仕様の実装と合格、計画からの逸脱の記録、生きたドキュメントの更新、ユーザーの明示的な承認がそろって done になる。

自己評価では、着手前と実装は中コスト、文書保守は低コスト（正本の範囲が狭い）、タスクごとの再調査は中コスト。**広い問題領域の分析から始める用途は弱く**（★★）、作業の方向が決まった後の計画・調査・承認・実装の統制に最も強い。

### 2 つの spec-loop の比較

| 観点 | dpolivaev 版 | hdknr 版 |
|---|---|---|
| 受け持つ工程 | 方向が決まった後の調査・計画・実装・レビュー | 要求確定・仕様レビュー・見積り・提案書・Issue への引き渡し |
| 人間の相手 | 開発者 1 人 | 利用者・予算責任者・決裁者 |
| 仕様の単位と寿命 | 次の小さな仕様 1 つ。リリース後に削除 | 版ごとの全体（`docs/v<n>/`）。リリースした版は凍結 |
| 関門の判定 | 人間の承認。ルールは文章でエージェントが従う | 照合と終了条件の一部はスクリプト、残りは書き込みツールを持たない別ティアの判定役 |
| 実装への渡し方 | 計画と実装が同じループの中 | `spec_ir.json` → Red テスト・Issue という明示的な契約で dev-loop へ |

hdknr 版で dpolivaev 版と重なるのは spec-loop ではなく、その後ろの **dev-loop**（Issue 1 件を verify 通過で 1 周させる）である。違いの多くは**相手の違い**から来る。開発者 1 人が毎回承認するなら人間の目が最後の関門になり、仕様の細部を読まない利用者・決裁者と回すなら細部の検査を機械と別モデルに任せる必要がある（[maker-checker](/blogs/wiki/concepts/maker-checker/)）。版の全体を残す側では仕様の膨張が実際に起きる（要求 190 行・決定表 15 行に対して仕様 768 行・テスト 300 件）ので、テストケースが要求より速く増えたら減らす見直しをする歯止めが要る。

共通する根っこは、**推測で埋めない**、**人間の判断を飛ばさない**、**小さく回す**、**テストを仕様の一部にする**（テストを書き起こせない仕様は未確定）、**決まりの住所を 1 つにする**、の 5 つ。組み合わせるなら、hdknr 版が作った Issue 1 件を dpolivaev 版のタスク 1 つの入力にできるが dev-loop と役割が重なるので、**計画の書き方（Research・変更記号・生きたドキュメント・用語の扱い）は dpolivaev 版から借り、停止条件は dev-loop のまま**が現実的。逆方向には、関門をスクリプト判定に置き換える、自己チェックを書けない別モデルに任せる、会話で解消した論点を表に残す、が取り入れられる。

### 導入

```bash
npx skills add dpolivaev/spec-loop -s '*'      # プロジェクトに全スキル
npx skills add dpolivaev/spec-loop -s '*' -g   # グローバル
```

中核は plan-task・plan-work-breakdown・clarify-task・prepare-execution-approval・implementation-flow・write-adr・write-readable-tests の 7 スキル。write-readable-tests は単体でもテスト設計のガイドとして使える。

## 関連ページ

- [要求仕様書作成ループ](/blogs/wiki/concepts/requirements-spec-loop/) — hdknr 版 spec-loop。開発の手前で要求と予算を確定させる
- [Vibe Coding](/blogs/wiki/concepts/vibe-coding/) — Spec Loop が避けようとする片側の失敗パターン
- [作る役と確かめる役の分離（maker-checker）](/blogs/wiki/concepts/maker-checker/) — 別ティアの判定役
- [ループエンジニアリング](/blogs/wiki/concepts/loop-engineering/) — 人間のゲートと機械のゲート
- [ハーネスエンジニアリング](/blogs/wiki/concepts/harness-engineering/) — 開発ループ側の実行環境
- [エクストリーム・プログラミング（XP）](/blogs/wiki/concepts/extreme-programming/) — Baby Steps・Incremental Design という同じ発想の源流

## ソース記事

- [Spec Loop — 次の小さな仕様だけを書いて回す、AI エージェント向け仕様駆動開発フレームワーク](/blogs/posts/2026/10/spec-loop-design-first-ai-development/) — 2026-10-25
- [AI 仕様駆動開発の 2 つの spec-loop を比べる — 実装ループと要求確定ループ](/blogs/posts/2026/10/spec-loop-two-frameworks-comparison/) — 2026-10-25
