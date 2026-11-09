---
title: "TLA+ と TLC"
description: "Leslie Lamport が考案した形式仕様記述言語 TLA+ と、そのモデル検査器 TLC。設計の到達しうる全状態を探索し、不変条件違反・デッドロック・活性の破れを反例トレースつきで返す。並行処理や分散システムの設計バグを実装前に見つける道具"
date: 2026-11-09
lastmod: 2026-11-09
aliases: ["TLA+", "TLC", "tla2tools", "tla2tools.jar", "TLAPS", "TLA+ Toolbox", "Temporal Logic of Actions", "モデル検査器"]
related_posts:
  - "/posts/2026/11/tla-plus-tlc-model-checker/"
  - "/posts/2026/11/quint-formal-specification-language/"
  - "/posts/2026/11/spec-loop-tlc-formal-checker/"
  - "/posts/2026/10/formal-methods-claude-code-spec-check/"
tags: ["TLA+", "形式手法", "モデル検査", "ソフトウェア検証", "同時実行制御"]
---

## 概要

**TLA+**（Temporal Logic of Actions）は、Leslie Lamport（2013 年チューリング賞）が考案した形式仕様記述言語。システムの状態（変数）と、状態がどう変わりうるか（アクション）を数学的に書く。**TLC** はその仕様を読み込み、到達しうる状態をすべて列挙して性質を検査するモデル検査器で、「TLA+ の検査器」と言えばふつう TLC を指す。

テストが人間の思いついた実行順しか試さないのに対し、TLC は**ありうる実行順（インターリーブ）をすべて試す**。並行処理・分散システムの競合状態を、コードを書く前の設計段階で見つけるのが役目。AWS や Microsoft Azure の設計検証で使われてきた。

## 詳細

### 道具の構成

| 名前 | 役割 |
|---|---|
| TLA+ | 仕様を書く言語。型は持たない |
| TLC | 到達状態を列挙して性質を検査するモデル検査器。`tla2tools.jar` に含まれる |
| TLAPS | TLA+ Proof System。性質を数学的に証明する対話的な証明系 |
| TLA+ Toolbox / VS Code 拡張 | TLC を呼び出す IDE（Toolbox は Eclipse ベース） |

いずれも公式の `tlaplus` プロジェクトが提供し、`tla2tools.jar` は tlaplus/tlaplus の GitHub Releases から入手できる。コマンドラインからは次のように実行する（仕様 `.tla` と、定数や検査する性質を書く設定 `.cfg` を渡す）。

```bash
java -cp tla2tools.jar tlc2.TLC -config Stock.cfg Stock.tla
```

### 書き方の要点

- 次の状態はプライム付き（`stock'`）で書き、各アクションは割り込まれずに実行される 1 ステップを表す
- `Init`（初期状態）と `Next`（遷移ルール）を書き、`Spec == Init /\ [][Next]_vars /\ WF_vars(Next)` のようにまとめる
- 設定ファイルの `CONSTANTS` で定数（購入者 `{b1, b2}` などのモデル値）を与え、`INVARIANT` に不変条件、`PROPERTY` に時相性質を指定する
- 全員が終わったあとに何も変えないステップ（`Done`）を置かないと、正常終了がデッドロックとして報告される

### 探索の仕組み

1. `Init` を満たす初期状態をすべて作る
2. `Next` を各状態に適用し、到達できる状態をすべて辿る。どのプロセスが次に動くかの組み合わせも別々の遷移として扱う
3. 性質を破る状態を見つけたら、初期状態からの手順（トレース）を出して止まる

既定は**幅優先**なので、安全性の違反は**最短の反例トレース**として返る（複数ワーカーでは厳密に最短とは限らない）。`-dfid` で反復深化の深さ優先、`-simulate` でランダムシミュレーション、`-continue` で最初の違反で止めずに続行する。

例：在庫 1 個を 2 人が「確認 → 減算」の 2 ステップで買うモデルでは、到達状態は 10 個。「b1 確認 → b2 確認 → b1 減算 → b2 減算」の 4 ステップで在庫が -1 になる反例を TLC が返す。確認と減算を 1 ステップ（アトミック）にすると、この実行順は存在しなくなる。

### 検証できる性質

| 種類 | 意味 | 指定 | 反例の形 |
|---|---|---|---|
| 不変条件（安全性） | どの実行順でも常に成り立つ | `INVARIANT` | 違反に至る有限の手順 |
| デッドロック（安全性） | どのアクションも実行できない状態 | 既定で検査。`-deadlock` で外す | 止まった状態までの手順 |
| 活性 | いつか必ず良いことが起きる（`<>P`、`P ~> Q`） | `PROPERTY` | 同じ状態に戻るループを含むトレース |

活性の検査には**公平性**の仮定（`WF_vars(Next)` など）が要る。仮定がないと「ずっと足踏みする」実行が許され、「いつか終わる」が成り立たない。

### 実績

2015 年の論文「How Amazon Web Services Uses Formal Methods」（Communications of the ACM）は、S3 や DynamoDB の設計に TLA+ を使った経験を報告している。DynamoDB では、TLC が見つけたバグの最短反例が **35 ステップ**に及んだ。Microsoft は Azure Cosmos DB の 5 つの一貫性レベルの仕様を [Azure/azure-cosmos-tla](https://github.com/Azure/azure-cosmos-tla) で公開している。

### 限界と対策

- **状態爆発**：ノード数・バッファサイズ・メッセージ数が増えると状態が組み合わせ的に増える。対策は次のとおり
  - 定数を小さく取る（並行処理のバグの多くはノード 2〜3 台で再現する）
  - 対称性：`Permutations(Buyers)` を返す演算子を `SYMMETRY` に指定して同一視する。活性の検査と組み合わせると違反を見逃すことがあるので、不変条件だけの構成で使う
  - `-workers` で並列化する
- **モデルと実装の差**：TLC が見るのはモデルであって実装ではない。反例は実装のテストで再現させてからバグと判断する
- **「違反なし」は空振りを疑う**：ガード条件の書き間違いで肝心の状態に到達しないモデルでも検査は「成功」する。`stock = InitStock` のような**破られるべき性質**を置き、違反が出ることを確かめる

### TLAPS との使い分け

TLC は有限のモデルを総当たりするので、保証は絞った範囲内に限られる。任意の台数・任意の長さで成り立つことを示すには TLAPS で証明する（人間が証明の構造を書き、各ステップを自動証明器に検査させる）。手間が大きいので、まず TLC で設計の穴を潰し、特に重要な性質だけを TLAPS で証明するのが現実的な順番。

### Quint から使う

TLA+ と同じ論理をプログラマ向けの構文で書ける [Quint](/blogs/wiki/tools/quint/) は、`quint verify --backend=tlc` で仕様を TLA+ に変換して TLC に渡せる。在庫の例では TLA+ 版と同じ 10 状態を探索した。ただし Quint 経由の TLC は `-deadlock` 付きで起動されるのでデッドロックを検査しない。

### エージェントの検査役として

[要求仕様書作成ループ](/blogs/wiki/concepts/requirements-spec-loop/)の Claude Code プラグイン spec-loop では、仕様レビューの判定役 Formal Checker が、並行・リトライ・取り消しを含む業務フローの検査に TLC を使う。Java と `tla2tools.jar` が手元に無ければ判定役を起動せず、業務フローの検査を手作業の総当たりで代用することもしない。

## 関連ページ

- [形式手法（Formal Methods）](/blogs/wiki/concepts/formal-methods/) — 道具の選び方と LLM との役割分担
- [Quint](/blogs/wiki/tools/quint/) — TLA+ の論理を型付きの構文で書き、Apalache・TLC で検査する
- [要求仕様書作成ループ](/blogs/wiki/concepts/requirements-spec-loop/) — Formal Checker が TLC で業務フローを検査する
- [分散ロック](/blogs/wiki/concepts/distributed-lock/) — 反例で見つかった競合を実装で防ぐ手段の 1 つ
- [ミューテーションテスト](/blogs/wiki/concepts/mutation-testing/) — 「破られるべき性質」で空振りを確かめる考え方が共通

## ソース記事

- [TLA+ のモデル検査器 TLC とは — 起こりうる全状態を総当たりして設計バグを見つける](/blogs/posts/2026/11/tla-plus-tlc-model-checker/) — 2026-11-06
- [Quint とは — TLA+ の論理をプログラマ向けの構文で書く形式仕様記述言語と、TLC との使い分け](/blogs/posts/2026/11/quint-formal-specification-language/) — 2026-11-09
- [spec-loop は TLC をどう使っているか — Formal Checker の設計と、実案件で見えた 2 つの穴](/blogs/posts/2026/11/spec-loop-tlc-formal-checker/) — 2026-11-08
- [形式手法を Claude Code で回す — Z3 と TLA+ で仕様の穴を見つけ、反例をテストに落とす](/blogs/posts/2026/10/formal-methods-claude-code-spec-check/) — 2026-10-09
