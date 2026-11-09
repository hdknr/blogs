---
title: "Quint とは — TLA+ の論理をプログラマ向けの構文で書く形式仕様記述言語と、TLC との使い分け"
date: 2026-11-09
lastmod: 2026-11-09
slug: "quint-formal-specification-language"
draft: false
source_url: "https://github.com/hdknr/blogs/issues/694#issuecomment-6737298800"
description: "Quint は TLA+ と同じ論理に、型付きでプログラマ向けの構文を載せた形式仕様記述言語。在庫を 2 人が同時に買う例を、シミュレータ・Apalache・TLC の 3 通りで実際に検査し、TLA+ / TLC との違いと使い分けを整理する。"
categories: ["ツール/開発環境"]
tags: ["Quint", "TLA+", "形式手法", "モデル検査", "Apalache"]
---

**Quint** は、分散システムや並行プロトコルの設計を書いて検査するための形式仕様記述言語です。Informal Systems が開発を始めた言語で、GitHub のリポジトリは現在 [quint-co/quint](https://github.com/quint-co/quint) にあります。

論理の土台は Leslie Lamport が考案した TLA+（Temporal Logic of Actions）と同じです。そのうえで、構文は TypeScript や Rust に近く、型検査・REPL（式をその場で評価できる対話環境）・テストといった、普段の開発で当たり前の道具が最初から付いてきます。「TLA+ の考え方はそのままに、プログラマが書きやすい形にしたもの」と捉えるとわかりやすいでしょう。

前回の記事「[TLA+ のモデル検査器 TLC とは](/blogs/posts/2026/11/tla-plus-tlc-model-checker/)」では、在庫 1 個を 2 人が同時に買う例を TLA+ で書き、TLC で検査しました。この記事では同じ例を Quint で書き直し、実際に 3 通りの方法で検査して、TLA+ / TLC との違いと使い分けを整理します。

## Quint の主な特徴

- **プログラマに馴染みやすい構文**：TLA+ は `/\`（かつ）、`\/`（または）、`\in`（属する）のように、数学記号を ASCII で表して書く。Quint は波括弧 `{}` やドット記法（`pc.get(b)`）を使い、関数型のプログラミング言語に近い見た目になる
- **静的な型検査**：型推論つきの型検査器があり、仕様の書き間違いを検査の実行前に見つけられる。TLA+ は型を持たない言語なので、この種の間違いは TLC で状態を探索している途中に初めて表に出る
- **開発ツールが揃っている**：REPL、VS Code の拡張機能、`run` 定義で書いた実行手順を `quint test` で再現するテスト機能が標準で使える
- **検査の方法を選べる**：ランダムシミュレータ（`quint run`）、記号的モデル検査器 **Apalache**（`quint verify`）、明示的状態探索のモデル検査器 **TLC**（`quint verify --backend=tlc`）の 3 つを、同じ仕様に対して使い分けられる

各コマンドの関係は次の図のとおりです。

![Quint のツールチェーンの図。仕様ファイル stock.qnt を、書きながらのフィードバック用の quint typecheck・quint repl・quint test と、性質の検査用の 3 つのコマンドに渡す。quint run はランダムシミュレータで、速いが網羅ではない。quint verify は既定で Apalache を使い、SMT ソルバ Z3 による記号的モデル検査で指定した手数までを網羅する。quint verify --backend=tlc は仕様を TLA+ に変換してから TLC に渡し、到達状態をすべて列挙する](/blogs/images/quint-toolchain.png)

## Quint のインストール

Quint は npm で配布されています。この記事のコマンドと出力は、Quint 0.33.1 で実際に実行したものです。

```bash
npm install -g @informalsystems/quint
```

型検査・テスト・`quint run` は Node.js だけで動きます。`quint verify` は Apalache を、`--backend=tlc` は Apalache と TLC を使うため、**Java の実行環境が必要**です。Apalache と TLC の本体は、初回の実行時に自動でダウンロードされます。

## 在庫の例を Quint で書く

「在庫があるか確認してから、在庫を 1 つ減らす」処理を、確認と減算が別々のステップになっている版（非アトミック版）と、1 ステップで行う版（アトミック版）の 2 通りで書きます。前回の TLA+ 版と同じ構成です。次の内容を `stock.qnt` として保存します。

```text
module stock {
  // 購入者ごとの処理段階
  type Phase = Check | Buy | Done

  const BUYERS: Set[str]
  const INIT_STOCK: int
  const ATOMIC: bool

  var stock: int
  var pc: str -> Phase

  action init = all {
    stock' = INIT_STOCK,
    pc' = BUYERS.mapBy(_ => Check),
  }

  // 非アトミック版: 在庫を確認する
  action check(b: str): bool = all {
    not(ATOMIC),
    pc.get(b) == Check,
    pc' = pc.set(b, if (stock > 0) Buy else Done),
    stock' = stock,
  }

  // 非アトミック版: 確認した結果を信じて 1 つ減らす
  action buy(b: str): bool = all {
    pc.get(b) == Buy,
    stock' = stock - 1,
    pc' = pc.set(b, Done),
  }

  // アトミック版: 確認と減算を 1 ステップで行う
  action checkAndBuy(b: str): bool = all {
    ATOMIC,
    pc.get(b) == Check,
    stock' = if (stock > 0) stock - 1 else stock,
    pc' = pc.set(b, Done),
  }

  // 全員が終わったあとは何も変えない（デッドロックと誤検出させない）
  action done = all {
    BUYERS.forall(b => pc.get(b) == Done),
    stock' = stock,
    pc' = pc,
  }

  action step = any {
    nondet b = oneOf(BUYERS) any {
      check(b),
      buy(b),
      checkAndBuy(b),
    },
    done,
  }

  // 安全性: 在庫はマイナスにならない
  val nonNegative = stock >= 0

  // 特定の実行順を再現するテスト
  run doubleBuyTest =
    init
      .then(check("b1"))
      .then(check("b2"))
      .then(buy("b1"))
      .then(buy("b2"))
      .then(all {
        assert(stock == -1),
        stock' = stock,
        pc' = pc,
      })
}

module main {
  import stock(BUYERS = Set("b1", "b2"), INIT_STOCK = 1, ATOMIC = false).*
}

module mainAtomic {
  import stock(BUYERS = Set("b1", "b2"), INIT_STOCK = 1, ATOMIC = true).*
}
```

TLA+ 版と読み比べると、次の対応になっています。

| TLA+ | Quint | 意味 |
| --- | --- | --- |
| `/\ A /\ B` | `all { A, B }` | すべて成り立つ |
| `\/ A \/ B` | `any { A, B }` | どれか 1 つが起きる |
| `\E b \in Buyers : ...` | `nondet b = oneOf(BUYERS) ...` | 購入者を非決定的に 1 人選ぶ |
| `[pc EXCEPT ![b] = "done"]` | `pc.set(b, Done)` | 写像の 1 か所だけを書き換える |
| `pc[b]` | `pc.get(b)` | 写像の値を引く |
| `UNCHANGED vars` | `stock' = stock, pc' = pc` | 変数を変えない |
| `.cfg` ファイルの `CONSTANTS` | `import stock(BUYERS = ...)` | 定数に具体的な値を与える |

プライム付きの `stock'` で次の状態を書く点は TLA+ と同じです。一方で、処理段階 `Phase` を文字列ではなく `Check | Buy | Done` の直和型（`Check`・`Buy`・`Done` のどれか 1 つの値をとる型。列挙型に近い）で定義しているので、`"chek"` のような綴り間違いは型検査の時点で弾かれます。

`done` は、TLA+ 版の `Done` と同じく、全員が終わったあとに何も変えないステップです。これがないと、全員が終わった状態からはどのアクションも実行できず、検査器によってはデッドロックとして報告します（後述）。

検査の条件（購入者 2 人・在庫 1 個）は、TLA+ では別ファイル（`.cfg`）に書きました。Quint では `main` と `mainAtomic` のように、定数を与えたモジュールとして同じファイルに書けます。

なお、TLA+ 版にあった活性（「いつか全員の処理が終わる」）と公平性の仮定は、この記事では省き、安全性（`nonNegative`）だけを扱います。

## quint typecheck による型検査：書き間違いをすぐに見つける

試しに、`buy` の `stock' = stock - 1` を `stock' = "zero"` に書き換えて型検査にかけると、次のように止まります。

```bash
quint typecheck stock.qnt
```

```text
 Error [QNT000]: Couldn't unify int and str
Trying to unify int and str
Trying to unify (_t67, _t67) => bool and (int, str) => _t68


  at stock.qnt:28:5
  28:     stock' = "zero",
          ^^^^^^^^^^^^^^^

error: typechecking failed
```

整数の変数に文字列を代入しようとしていることが、行番号つきで返ってきます。状態を探索する前に返る、速いフィードバックです。

## quint test：特定の実行順を再現する

仕様の末尾に書いた `run doubleBuyTest` は、「b1 が確認 → b2 が確認 → b1 が減らす → b2 が減らす」という順番を、`.then` でつないで再現するテストです。最後に `assert(stock == -1)` で、在庫がマイナスになることを確かめています。

```bash
quint test --main=main stock.qnt
```

```text
  main
    ok main::stock::doubleBuyTest passed 1 test(s)

  1 passing (10ms)
```

単体テストを書く感覚で、「このシナリオではこうなるはず」を仕様に対して確かめられます。ただし、ここで確かめているのは人間が思いついた 1 つの順番だけです。思いつかない順番を探すのは、次の 3 つのコマンドの役目です。

## Quint の 3 つの検査方法：シミュレータ・Apalache・TLC

### quint run：ランダムシミュレータ

```bash
quint run --main=main --invariant=nonNegative --max-samples=1000 --max-steps=10 stock.qnt
```

`--max-samples` は試す実行の数、`--max-steps` は 1 回の実行の最大ステップ数です。

```text
An example execution:

[State 0]
{ main::stock::pc: Map("b1" -> Check, "b2" -> Check), main::stock::stock: 1 }

[State 1]
{ main::stock::pc: Map("b1" -> Buy, "b2" -> Check), main::stock::stock: 1 }

[State 2]
{ main::stock::pc: Map("b1" -> Buy, "b2" -> Buy), main::stock::stock: 1 }

[State 3]
{ main::stock::pc: Map("b1" -> Done, "b2" -> Buy), main::stock::stock: 0 }

[State 4]
{ main::stock::pc: Map("b1" -> Done, "b2" -> Done), main::stock::stock: -1 }

[violation] Found an issue (12ms at 6250 traces/second).
Use --verbosity=3 to show executions.
Use --seed=0x803e63d8589b7748 --backend=rust to reproduce.
error: Invariant violated
```

ランダムに実行を試し、在庫が -1 になる手順を見つけました。出力の最後に表示される `--seed` を付けて実行し直せば、同じ反例を再現できます。どちらの購入者が先に動くかは乱数で決まるので、実行するたびに b1 と b2 の順番が入れ替わることがあります。

シミュレータは速い反面、**網羅ではありません**。アトミック版（`--main=mainAtomic`）で同じコマンドを実行すると `[ok] No violation found` が返りますが、同時に `You may increase --max-samples and --max-steps.` とも表示されます。「試した範囲では見つからなかった」という意味であって、「違反がない」ことの証明ではありません。

### quint verify：Apalache による記号的モデル検査

```bash
quint verify --main=main --invariant=nonNegative --max-steps=5 stock.qnt
```

`quint verify` は既定で **Apalache** を使います。Apalache は状態を 1 つずつ列挙する代わりに、「`--max-steps` ステップ以内に不変条件が破れる実行はあるか」を論理式に変換し、SMT ソルバ（論理式を満たす値の組み合わせがあるかを自動で判定するツール。Apalache は Z3 を使う）に解かせます。

```text
An example execution:

[State 0]
{ main::stock::pc: Map("b1" -> Check, "b2" -> Check), main::stock::stock: 1 }

[State 1]
{ main::stock::pc: Map("b1" -> Check, "b2" -> Buy), main::stock::stock: 1 }

[State 2]
{ main::stock::pc: Map("b1" -> Buy, "b2" -> Buy), main::stock::stock: 1 }

[State 3]
{ main::stock::pc: Map("b1" -> Buy, "b2" -> Done), main::stock::stock: 0 }

[State 4]
{ main::stock::pc: Map("b1" -> Done, "b2" -> Done), main::stock::stock: -1 }

[violation] Found an issue (3524ms).
error: found a counterexample
```

（実際の出力では、この前に Apalache の処理ログが続きます。）

ランダムシミュレータと違い、Apalache の結果は**指定したステップ数の範囲では網羅的**です。アトミック版（`--main=mainAtomic`）では `[ok] No violation found` が返り、これは「5 ステップ以内に在庫がマイナスになる実行は 1 つもない」ことを意味します。逆に言えば、6 ステップ目以降で初めて起きる違反は見つかりません。このようにステップ数に上限を置いて検査する方式を、有界モデル検査（bounded model checking）と呼びます。

Apalache は**デッドロックも検出します**。試しに `done` を外したアトミック版を検査すると、在庫は正しく保たれているにもかかわらず `error: reached a deadlock` で止まります。全員が終わった状態から先に進めないためです。仕様に `done` を入れているのはこのためです。

なお、Apalache はカレントディレクトリに `_apalache-out/` という出力ディレクトリを作ります。リポジトリの中で実行するなら `.gitignore` に入れておくとよいでしょう。

### quint verify --backend=tlc：TLA+ に変換して TLC で検査

```bash
quint verify --backend=tlc --main=main --invariant=nonNegative stock.qnt
```

`--backend=tlc` を付けると、Quint は仕様を TLA+ に変換し、TLC に渡して検査させます（変換には Apalache を使います）。出力は TLC そのものです。途中の状態は省略して示します。

```text
Error: Invariant q_inv is violated.
Error: The behavior up to this point is:
State 1: <Initial predicate>
/\ main_stock_stock = 1
/\ main_stock_pc = [b1 |-> [Check |-> [tag |-> "UNIT"]], b2 |-> [Check |-> [tag |-> "UNIT"]]]

（State 2〜4 は省略）

State 5: <main_stock_buy("b2") line 73, col 3 to line 76, col 70 of module main>
/\ main_stock_stock = -1
/\ main_stock_pc = [b1 |-> [Done |-> [tag |-> "UNIT"]], b2 |-> [Done |-> [tag |-> "UNIT"]]]

14 states generated, 10 distinct states found, 0 states left on queue.
The depth of the complete state graph search is 5.
```

`[Check |-> [tag |-> "UNIT"]]` は、Quint の直和型の値を TLA+ に変換したときの表現です。また、TLC は状態を 1 から数えるので、State 5 は初期状態から 4 ステップ目にあたります。シミュレータや Apalache の `[State 4]` と同じ位置です。

「10 distinct states found」は、前回の記事で TLA+ 版の状態遷移図に描いた 10 個の状態と一致します。同じ設計を同じ検査器で見ているので当然と言えば当然ですが、変換が意味を保っていることの確認になります。

アトミック版（`--main=mainAtomic`）を TLC で検査すると、到達できる 4 状態をすべて調べたうえで違反なしと報告します。こちらはステップ数の上限なしの、文字どおりの全探索です。

```text
Model checking completed. No error has been found.
（中略）
6 states generated, 4 distinct states found, 0 states left on queue.
```

1 点注意があります。Quint 0.33.1 は TLC を `-deadlock` オプション付きで起動するので、**TLC 側ではデッドロックを検査しません**。Apalache とは扱いが異なるため、デッドロックの有無を確かめたいときは Apalache で検査するか、TLC を直接実行する必要があります。

変換後の TLA+ だけが欲しいときは `quint compile --target=tlaplus stock.qnt` で標準出力に書き出せます。

## Quint と TLA+ / TLC の比較

ここで比べる対象を整理しておきます。TLC は言語ではなく、TLA+ のための**検査器**です。一方の Quint は言語とツール群の名前で、検査器としては Apalache・シミュレータ・TLC を使い分けます。したがって比較は「Quint で書いて Apalache / シミュレータで検査する」と「TLA+ で書いて TLC で検査する」の比較になります。

| 比較項目 | Quint（Apalache / シミュレータ） | TLA+ と TLC |
| --- | --- | --- |
| 位置づけ | 言語とツール群（TLC にも渡せる） | TLA+ は仕様記述言語、TLC はその明示的状態探索のモデル検査器 |
| 構文 | TypeScript / Rust 風。静的型付き | 数学記号を ASCII で表した数式。型なし |
| 検査の方式 | 記号的（SMT ソルバ Z3）＋ランダムシミュレーション | 到達状態を幅優先（または深さ優先）で 1 つずつ列挙 |
| 大きな値の扱い | 整数などを記号のまま扱えるので、値の範囲が広くても状態を列挙せずに済む | 状態空間を有限かつ小さく絞り込む必要がある（状態爆発に弱い） |
| 実行の長さ | Apalache は指定した最大ステップ数までを網羅（有界）。シミュレータは網羅しない | 状態空間が有限なら、長さの上限なしに全実行を網羅する |
| フィードバックの速さ | 型検査・REPL・シミュレータは秒未満（Apalache は秒単位） | 構文と意味の検査（SANY）はあるが、型の間違いは探索の途中で表に出る |
| 実績 | 比較的新しい。Cosmos などのブロックチェーンや分散プロトコルの開発で使われてきた | 1999 年の論文発表以来の長い実績。AWS や Azure の設計検証での公開事例が多い |

## Quint と TLA+ のどちらを選ぶか

### Quint が向いているケース

- チームにプログラマが多く、数学的な記法よりも普段の言語に近い書き方でモデルを書きたい
- 仕様からトレースを生成し、実装のテストに結びつけたい（モデルベーステスト）。`quint run` と、Apalache バックエンドの `quint verify` は、`--out-itf` で反例のトレースを ITF（Informal Trace Format）の JSON に書き出せる。これを実装側のテストで同じ手順を再生する素材にできる
- 整数の範囲が広いなど状態空間が大きく、明示的な列挙では手に負えないので、Apalache の記号的な検査やランダムシミュレーションで探したい

### TLA+ / TLC が向いているケース

- 論文、書籍、AWS の事例など、TLA+ で書かれた豊富な資料をそのまま参考にしたい
- 小〜中規模の有限な状態空間を、ステップ数の上限なしに全探索して安全性を確かめたい
- 公平性の仮定を伴う活性（「いつか必ず〇〇になる」）を検査したい。TLC は安全性と活性の両方を検査でき、Quint のドキュメントでも Apalache 側の時相性質の対応は部分的とされている。活性と公平性については[前回の記事の「安全性と活性」の節](/blogs/posts/2026/11/tla-plus-tlc-model-checker/)で説明している

### 書くのは Quint、検査は使い分ける

二者択一である必要はありません。この記事で見たとおり、Quint で書いた仕様はそのまま TLC にも渡せます。次の組み合わせが現実的です。

- 書いている最中は、型検査・`quint test`・`quint run` で素早く間違いを潰す
- 状態空間が小さく絞れる性質は、`--backend=tlc` で上限なしに全探索する
- 値の範囲が広い性質は、Apalache で有界に網羅する

どの検査器を使うにしても、「違反なし」という結果は、その検査器が何を網羅したのか（ランダムな試行か、ステップ数の上限までか、全状態か）、何を検査しなかったのか（TLC 経由ではデッドロックを見ない、など）とセットで読む必要があります。

## まとめ

- Quint は TLA+ と同じ論理を土台に、型付きでプログラマに馴染みやすい構文を持つ形式仕様記述言語
- 型検査・REPL・`run` によるテストで、書きながら速いフィードバックが得られる
- 検査器はランダムシミュレータ・Apalache（記号的・有界）・TLC（明示的・全探索）から選べ、同じ仕様に対して使い分けられる。Quint で書いた仕様は `--backend=tlc` でそのまま TLC にも渡せる
- 在庫の例では、3 つの検査器すべてが 4 ステップで在庫が -1 になる反例を返し、TLC は TLA+ 版と同じ 10 状態を探索した

TLC そのものの仕組みや、安全性・活性・状態爆発の話は「[TLA+ のモデル検査器 TLC とは](/blogs/posts/2026/11/tla-plus-tlc-model-checker/)」に、形式手法全体の道具の選び方は [形式手法](/blogs/wiki/concepts/formal-methods/) の wiki ページにまとめています。
