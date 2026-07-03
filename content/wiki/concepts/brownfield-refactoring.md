---
title: "Brownfield リファクタリング"
description: "改修を重ねた既存コード（brownfield）を、振る舞いを固定してから安全に作り替えるための原則・ワークフロー・パターン。greenfield との対比で捉える。"
date: 2026-07-03
lastmod: 2026-07-03
aliases: ["brownfield", "greenfield", "レガシーコード リファクタリング", "特性テスト", "Characterization Test", "Strangler Fig"]
related_posts:
  - "/posts/2026/07/brownfield-refactoring-django-react/"
tags: ["refactoring", "brownfield", "テスト", "django", "react"]
---

## 概要

**brownfield（ブラウンフィールド）** は、すでに動いていて改修を重ねてきた既存コードベースを指す。更地から作る新規開発 **greenfield（グリーンフィールド）** の対義語で、工事現場での「更地への新築」対「既存建物の改修」の比喩に由来する。brownfield のリファクタリングでは、最大のリスクは過剰実装ではなく **「正しさの後退」**（間違った項目名・ID、データ不整合、意図しない挙動変化）にある。したがって鉄則は一つ——**振る舞いを固定してから、内部を動かす**。

## 大原則：安全網を先に張る

リファクタリングの定義は「外部から見た振る舞いを変えずに内部構造を改善する」こと。振る舞いを固定する手段を最初に用意することが出発点になる。

- **特性テスト（Characterization Test）**: 「正しい仕様」ではなく「今の実際の挙動」を記録するテスト。仕様書が信用できない前提で現状を凍結する（Michael Feathers『レガシーコード改善ガイド』の中核）。
- **Golden Master / スナップショット**: 個別アサーションが難しい複雑なロジックや UI は、出力・レンダリング結果を丸ごと比較して守る。
- **境界の契約**: API・DB スキーマ・イベントなど外部インターフェースに特性テストを置いてから内部を動かす。
- **1 コミット 1 リファクタリング**: 振る舞い変更と構造変更を混ぜない。問題の切り分けが容易になる。

## ワークフロー（6 ステップ）

順序に意味がある。安全網（②凍結）より前に大きく動かさず、削除（⑥）を最後に回す。

1. **計測** — 「変更頻度 × 複雑度」の高いホットスポットから着手する。
2. **凍結** — 現状挙動を特性テストで記録する（安全網の要）。
3. **継ぎ目（Seam）** — 依存を差し込めるテスト可能な接合点を作る。
4. **変換** — 振る舞い不変の小さな変更を IDE と codemod で積む。
5. **段階置換** — 新旧を並行稼働させ機能単位で差し替える。
6. **削除** — 旧経路とデッドコードを消す。

⑥から①へ戻り、ホットスポットを潰し切るまで反復する。

## 段階置換のパターン

- **Strangler Fig**: 新実装を旧の周りに這わせ、機能単位で差し替えて最後に旧を除去。
- **Branch by Abstraction**: 抽象層を挟み新旧を並行稼働、フラグで切替えながら main で継続。
- **Mikado Method**: 目標→前提依存をグラフ化し葉から潰す。行き詰まったら即 revert。
- **Seam の導入**: テスト用に振る舞いを差し込める継ぎ目を作る。
- **Scientist（並行検証）**: 旧経路と新経路を本番で並行実行し、結果の差異だけ記録。

## スタック別ツールの勘所

- **Django / Python**: `pytest-django`＋`coverage`（凍結・計測）、`syrupy`（golden master）、`django-test-migrations`（マイグレーション安全）、`import-linter`（層依存の契約）、`libcst`/`django-upgrade`（codemod）、`django-waffle`（フラグで段階置換）、`nplusone`（N+1 検出）、`vulture`（デッドコード削除）。
- **React / TypeScript**: Testing Library＋`Playwright`（凍結）、`Storybook`＋`Chromatic`（ビジュアル golden master）、`dependency-cruiser`/`madge`（依存の契約）、`ts-morph`/`ast-grep`（codemod）、`type-coverage`（型カバレッジ ratchet）、`knip`（未使用検出）。

## AI エージェントとの組み合わせ

主要リスクが「正しさ」である以上、AI に丸投げせず「凍結 → 小変換 → 検証」の小刻みループに乗せる。まず特性テストを書かせて現状を固定し、範囲を絞った変換だけ依頼し、テストが緑のままかを確認する。AST を理解する codemod（`ts-morph` / `libcst`）と組み合わせると、AI は「変換の設計」に集中でき機械的置換はツールが担う。過剰実装を抑える [Ponytail](/blogs/posts/2026/06/ponytail-ai-agent-minimal-code/) が greenfield の武器なら、brownfield ではこの規律が武器になる。

## 関連ページ

- [AI 開発と保守コスト](/blogs/wiki/concepts/ai-maintenance-cost/) — 保守コスト削減とリファクタリングの関係
- [Vibe Coding](/blogs/wiki/concepts/vibe-coding/) — AI 主導コーディングのスタイル
- [pytest でカオスエンジニアリング](/blogs/wiki/guides/pytest-chaos-engineering/) — テストで堅牢性を担保する
- [Django ツリー構造のマイグレーション](/blogs/wiki/guides/django-tree-migration/) — brownfield マイグレーションの実例

## ソース記事

- [brownfield を壊さず作り替える — Django × React/TS リファクタリング実践ガイド](/blogs/posts/2026/07/brownfield-refactoring-django-react/) — 2026-07-03
