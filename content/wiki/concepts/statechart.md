---
title: "状態遷移モデル（statechart）"
description: "システムの振る舞いを状態と遷移で書くモデルと、その図（状態遷移図）。エージェントには図を描かせずモデル（TLA+ や SCXML）を書かせて図はレンダリングする考え方、形式検証の前に状態遷移を見せて守るべき性質を言語化する手順、pstack の /statechart、TLA+ と SCXML の使い分け"
date: 2026-11-19
lastmod: 2026-11-19
aliases: ["statechart", "statecharts", "ステートチャート", "状態遷移図", "状態遷移", "ステートマシン", "状態機械", "SCXML", "State Chart XML", "XState", "Harel statechart", "pstack", "/statechart", "create-formal-verification-skill"]
related_posts:
  - "/posts/2026/11/statechart-before-formal-verification/"
  - "/posts/2026/11/tla-plus-tlc-model-checker/"
  - "/posts/2026/11/requirements-definition-book-ai/"
tags: ["状態遷移図", "SCXML", "形式手法", "TLA+", "モデル検査", "Agent Skills"]
---

## 概要

**状態遷移モデル**は、システムの振る舞いを「取りうる状態」と「状態を変える出来事（遷移）」で書いたもの。D. Harel が考案した**ステートチャート（statechart）**は階層や並行状態を持てる拡張で、UML ステートマシンの元になった。W3C 勧告の **SCXML**（State Chart XML）は、それを実行できる XML として標準化したものである。

エージェント時代の要点は、**図はプレゼンテーションで、正本はモデル**だということ。エージェントに絵を描かせても検査も実行もできない。状態遷移をモデル（[TLA+](/blogs/wiki/tools/tla-plus/) や SCXML）として書かせ、図はそこから機械的にレンダリングする。こうすると「描き忘れた矢印」が無くなる。

## 詳細

### 形式検証の前に状態遷移を見せる

コーディングエージェントに形式検証をさせるとき、いきなり検証させるより**先に状態遷移のモデルを書かせて図で見せる**ほうがうまくいく（poteto さんの投稿を kaito さんが整理）。検証には「何を守るべきか（性質）」と「破れると誰がどう困るか（害）」が要るが、「本来こうあるべき」はコードからは読み取れず、エージェントは推測するしかないからである。

1. **理解する**：対象機能の状態遷移モデルを書かせ、ユーザーに見える言葉の図をレンダリングする → 人が読んでおかしな遷移・抜けた遷移を指摘する → 守るべき規則を 1 文で言語化する（例：「1 回の注文で請求は 1 回だけ」）
2. **検証する**：規則を不変条件として検査する → 壊したコードで失敗することを確かめる → 反例（違反までの最短経路）を読む → 実コードで再現する

例：購入フローを TLA+ で書くと、「支払い処理中にもう一度購入ボタンを押す」遷移がモデルから機械的に出てきて、TLC が二重請求の 5 ステップの反例を返す。正常系だけを考えて手で描いた図には、この矢印は描かれない。ボタンを押せる状態をカート確認中だけに絞ると「No error has been found」になり、直す前の版で違反を見ているので空振りではないと言える（[陽性対照](/blogs/wiki/concepts/positive-control/)）。

図にする利点は 3 つ：**抜けた遷移に気づく**、**性質が言葉になる**、**TLA+ を読めない人でも「この遷移はおかしい」と判断できる**（状態名をユーザーに見える言葉にしておくのが条件）。

### pstack の /statechart と /create-formal-verification-skill

pstack は poteto さんの Skill 集で、Cursor のプラグインとして配布され Claude Code にも入る（`/plugin marketplace add cursor/plugins` → `/plugin install pstack@cursor-plugins`、呼び出しは `/pstack:statechart`）。どちらもユーザーが明示的に呼んだときだけ動く。

| Skill | すること |
|---|---|
| `/create-formal-verification-skill` | 壊れるとユーザーが困りテストが届きにくい性質を 1 つ選び、道具を選んで（順序の問題なら既定は TLA+）検証し、変更のたびに再検査できるプロジェクト専用の Skill を生成する |
| `/statechart` | TLA+ の仕様を TLC で展開し、Mermaid の状態遷移図にする。規則を破る状態に `breaks`／`mayBreak` の印を付け、そこまでの最短経路を示す |

`/create-formal-verification-skill` の品質条件は、**コードに忠実**（モデルの各部分が開けるコードを指す）、**失敗できる**（壊したコードで各性質が落ちる）、**見つけたものは見つけたものとして扱う**（通すために性質やモデルを弱めない）、**道具を知らなくても読める**（性質と害を平易な 1 文で）。

`/statechart` は図を描いていない。正本は TLA+ の仕様で、エージェントはビューの関数（状態のラベルを返す `state()`、遷移のラベルを返す `step()`）だけを書き、変換は自動で行われる。ラベルは「再生ボタンを押す」のようなユーザーから見た出来事にし、条件付き遷移は `[while the file loads]` のように角括弧で添え、矢印は 20 本前後に抑える。図に出た反例は 1 アクションずつ実コードで再現し、再現しなければモデルを疑う。

### 正本の選び方：TLA+ と SCXML

| 正本 | 得意なこと | 苦手なこと | 向く用途 |
|---|---|---|---|
| TLA+ | 不変条件を書き、到達状態を TLC で総当たりして反例を出せる | 実行できず、モデルと実コードがずれうる | 既存コードの性質を検証する |
| SCXML | 定義をそのまま実行できる。モデル＝実装なので図と実装がずれない | 不変条件を書く場所がなく、総当たりの検査道具も一般的でない | これから作る UI フローやプロトコルを状態機械として書く |

SCXML では今の状態に合う遷移がないイベントは捨てられるので、「支払い処理中」に `buy` の遷移を置かなければ二重請求は構造上起こりえない。実行エンジンには Apache Commons SCXML（Java）があり、JavaScript の XState も SCXML に着想を得て定義から図と実装を出せる。SCXML から TLA+ の骨組みを生成して不変条件だけ人が足す構成も考えられるが、広く使われる変換ツールはまだない。

どちらにも図の座標を書く仕組みはないので、レイアウトは自動になる。**図を手で整えたくなったら、図が正本になりかけている合図**である。

### 同じ発想の仲間

pstack の「README やチュートリアルを先に書かせる」、`/in-your-own-words`（目的をエージェント自身の言葉で言い直させる）と同じ構図で、コードを書く前に**エージェントの理解を人が判断できる形で外に出させる**。README は使い方を、言い直しは目的を、状態遷移図は振る舞いを見える形にする。

要件定義の側でも、業務ステータスのライフサイクルと状態遷移の定義は業務要件の一部として扱われる（[要件定義](/blogs/wiki/concepts/requirements-definition/)）。[要求仕様書作成ループ](/blogs/wiki/concepts/requirements-spec-loop/)の仕様チェックリストにも状態遷移が入っており、並行・リトライ・取り消しを含む業務フローは TLC で検査する。

## 関連ページ

- [TLA+ と TLC](/blogs/wiki/tools/tla-plus/) — 状態遷移モデルの正本と、到達状態を全探索するモデル検査器
- [形式手法（Formal Methods）](/blogs/wiki/concepts/formal-methods/) — 問いの形による道具の選び方と LLM との分担
- [Lean 4（仕様記述言語として）](/blogs/wiki/tools/lean/) — 形式仕様を正本にして生成物を人に見せる、同じ向きの方式
- [陽性対照（ポジティブコントロール）](/blogs/wiki/concepts/positive-control/) — 壊したコードで検査が落ちることを確かめる
- [要件定義](/blogs/wiki/concepts/requirements-definition/) — 業務ルールと状態遷移を業務要件として定義する
- [要求仕様書作成ループ](/blogs/wiki/concepts/requirements-spec-loop/) — 業務フローの状態遷移を仕様レビューで検査する

## ソース記事

- [形式検証 Skill を作る前に状態遷移をモデルにする — 図は描かせずレンダリングする（pstack /statechart・TLA+・SCXML）](/blogs/posts/2026/11/statechart-before-formal-verification/) — 2026-11-17
- [TLA+ のモデル検査器 TLC とは — 起こりうる全状態を総当たりして設計バグを見つける](/blogs/posts/2026/11/tla-plus-tlc-model-checker/) — 2026-11-06
- [『図と事例でやさしく学べる 要件定義 基本からAI対応まで』を目次から読む — 5 領域モデルと生成 AI の使いどころ](/blogs/posts/2026/11/requirements-definition-book-ai/) — 2026-11-17
