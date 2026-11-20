---
title: "Z3 とは？SMT ソルバの仕組みと Python での使い方入門"
date: 2026-11-20
lastmod: 2026-11-20
slug: "z3-smt-solver-intro"
draft: false
categories: ["ツール/開発環境"]
tags: ["Z3", "形式手法", "python", "ソフトウェア検証"]
---

**Z3** は、Microsoft Research が開発した **SMT ソルバ**です。「この条件をすべて満たす値はあるか」を問うと、あれば具体的な値を、なければ「ない」と答えます。Python からは `pip install z3-solver` で入れてすぐに使えます。地味な道具に見えますが、仕様の矛盾探し、プログラムの検証、パズルの求解、最適化と、使い道は幅広くあります。

このブログでも、[料金計算の仕様の穴探し](/blogs/posts/2026/10/formal-methods-claude-code-spec-check/)や [UI の表示ルールの検査](/blogs/posts/2026/11/ui-spec-verification-layers/)で Z3 を使ってきました。ただ、「SMT ソルバとは何か」「Z3 で何ができるか」を正面から説明したことはありませんでした。この記事はその入門編です。まず SAT から SMT への流れを押さえ、そのあと Python から Z3 を使う基本を、手元で動かした例で説明します。

## 登場する用語

| 用語 | 一言でいうと |
|---|---|
| SAT ソルバ | 真偽値（true / false）だけの論理式を、すべて満たす割り当てがあるかを判定する。SAT は Satisfiability（充足可能性）の略 |
| SMT ソルバ | SAT に「理論」（整数・実数・ビット列・配列など）を足したもの。`x + y == 10` のような式を直接扱える |
| 理論（theory） | 整数の算術、ビットベクタ（固定長のビット列）など、変数がとる値の世界とその演算のルール |
| 制約 | ソルバに渡す条件式。Python では `s.add(...)` で加える |
| sat / unsat / unknown | ソルバの答え。満たせる / 満たせない / 判定できなかった |
| モデル（model） | sat のときに返る、制約を満たす具体的な値の組 |
| 反例 | 「この性質は成り立たない」ことを示す具体的な入力。性質の否定を問うと、モデルがそのまま反例になる |
| unsat core | unsat のときに、矛盾に関わった制約の組 |
| 量化子 | 「すべての x について」（`ForAll`）、「ある x が存在して」（`Exists`）を表す記号 |
| 陽性対照 | わざと誤りを入れた版で、検査が誤りを検出できることを確かめる手法 |
| SMT-LIB | SMT ソルバ共通の入力形式。Z3 の標準の入力形式でもある |

## SMT ソルバとは：SAT から SMT へ

**SAT ソルバ**が扱うのは、`(a or b) and (not a or c)` のような、真偽値の変数だけでできた論理式です。「どの変数に true / false を割り当てれば式全体が true になるか」を探します。単純に見えますが、現代の SAT ソルバは非常に大きな問題を解けるほど速く、ハードウェア検証などで使われてきました。

ただ、ソフトウェアの条件は `price >= 3000` や `a[i] == x` のように、数や配列を含むのが普通です。これを真偽値だけで表すのは大変です。そこで登場したのが **SMT（Satisfiability Modulo Theories）ソルバ**です。SAT ソルバに、理論ごとの専用の判定手続きを組み合わせています。名前は「理論を法とした充足可能性」という意味で、整数の算術、実数、ビットベクタ、配列、文字列などを、そのままの形で扱えます。

## Z3 とは

Z3 は、Microsoft Research の Leonardo de Moura と Nikolaj Bjørner が開発した SMT ソルバです。2008 年の論文「Z3: An Efficient SMT Solver」（TACAS 2008）で発表されました。2015 年に MIT ライセンスのオープンソースになり、現在は GitHub の [Z3Prover/z3](https://github.com/Z3Prover/z3) で開発されています。

特徴は次のとおりです。

- **多くの言語から使える**：C・C++・Python・Java・.NET・OCaml・Go のバインディングがリポジトリに含まれ、WebAssembly 版が npm の `z3-solver` として公開されています。Rust や Julia にはコミュニティのバインディングがあります
- **標準の入力形式は SMT-LIB 2**：ほかの SMT ソルバとも同じ書き方で問題を渡せます
- **解くだけでなく、最適化（Optimize）や矛盾の原因の特定（unsat core）もできる**

ほかの SMT ソルバには cvc5、Yices、Bitwuzla などがあります。

## Z3 のインストール（pip install z3-solver）

Python からは `z3-solver` パッケージで入ります（パッケージ名は `z3` ではありません）。

```bash
pip install z3-solver
```

この記事の例は、2026 年 11 月時点の最新版の Z3 5.4.1 で動かしました。`z3-solver` を入れると、コマンドラインの `z3` も一緒に使えるようになります。

```bash
z3 --version
```

```text
Z3 version 5.4.1 - 64 bit - build hashcode 145c0c51570a357cc558ce898ce77573ba9d4fbf
```

## 条件を満たす値を探す（solve）

まずは連立方程式です。`Ints` で整数の変数を作り、条件を `solve` に渡します。

```python
from z3 import Ints, solve

x, y = Ints("x y")
solve(x + y == 10, x - y == 4)
solve(x + y == 10, x - y == 3)
```

```text
[y = 3, x = 7]
no solution
```

1 つ目は `x = 7, y = 3` という解（モデル）が返りました。2 つ目は、`x + y` と `x - y` の差が奇数になり、整数では解けないので `no solution` です。同じ式でも、変数を実数（`Reals`）にすれば解が出ます。**変数がどの理論に属するかで答えが変わる**のが SMT ソルバの特徴です。

## 反例を探して性質を証明する（prove / Solver）

Z3 を検証に使うときの基本形は、**確かめたい性質の否定**を問うことです。

![Z3 で性質を確かめる流れの図。確かめたい性質 P の否定 Not(P) を制約として Z3 に渡す。sat なら P を破る入力があり、そのモデルが反例になる。unsat ならどの入力でも P が成り立つ。unknown なら判定できなかった](/blogs/images/z3-check-flow.png)

「P は常に成り立つか」を直接問う代わりに、「P を破る入力はあるか」を問います。

- **sat**：破る入力がある。返ってきたモデルが**反例**
- **unsat**：破る入力がない。つまり、どの入力でも P が成り立つ
- **unknown**：判定できなかった

図の例（中点が `lo` と `hi` の間に入るか）は、後の「整数とビットベクタ」の節で実際に検査します。

この手順をまとめた関数が `prove` です。`Implies(A, B)` は「A なら B」を表します。

```python
from z3 import Int, Implies, prove

x = Int("x")
prove(Implies(x > 2, x * x > 4))
prove(Implies(x > -3, x * x > 4))
```

```text
proved
counterexample
[x = 2]
```

「`x > 2` なら `x * x > 4`」は `proved` でした。一方、「`x > -3` なら `x * x > 4`」には反例 `x = 2`（`2 * 2 = 4` は `4` より大きくない）が返りました。

ここが、テストとの一番の違いです。テストは、試した値についてしか保証しません。Z3 の `proved` は、**整数全体について**の結論です。

`prove` の中身は、`Solver` に性質の否定を加えて `check()` しているだけです。実務では `Solver` を直接使うことが多いので、同じ検査をこの形でも書いてみます。

```python
from z3 import Implies, Int, Not, Solver, sat

x = Int("x")
s = Solver()
s.add(Not(Implies(x > -3, x * x > 4)))  # 性質の否定を加える
if s.check() == sat:
    print("反例:", s.model())
```

```text
反例: [x = -2]
```

今度は `x = -2` が返りました。反例は 1 つとは限らず、そのうちどれが返るかは決まっていません。

## 理論で答えが変わる：整数とビットベクタ

理論の違いが効く例として、二分探索でよく書く**中点の計算** `(lo + hi) / 2` を調べてみます。確かめたい性質は「`lo <= hi` なら、中点は `lo` と `hi` の間に入る」です。

コードでは、まず数学の整数（`Int`）で、次に 32 ビットのビットベクタ（`BitVec`）で同じ性質を調べます。`BitVecs("lo hi", 32)` は、32 ビットのビット列の変数を 2 つ作ります。ビットベクタの `/` と `<=` は符号付きとして扱われるので、符号なしの比較と除算には `ULE` と `UDiv` を使います。

```python
from z3 import And, BitVecs, Implies, Ints, UDiv, ULE, prove

# 数学の整数：中点は必ず lo と hi の間に入る
lo, hi = Ints("lo hi")
mid = (lo + hi) / 2
prove(Implies(lo <= hi, And(lo <= mid, mid <= hi)))

# 32 ビットの符号なし整数：lo + hi があふれる
lo, hi = BitVecs("lo hi", 32)
mid = UDiv(lo + hi, 2)
prove(Implies(ULE(lo, hi), And(ULE(lo, mid), ULE(mid, hi))))

# あふれない書き方
mid = lo + UDiv(hi - lo, 2)
prove(Implies(ULE(lo, hi), And(ULE(lo, mid), ULE(mid, hi))))
```

```text
proved
counterexample
[hi = 4294967295, lo = 134217728]
proved
```

数学の整数では、性質は成り立ちます。ところが、32 ビットのビットベクタにすると反例が出ます。`lo + hi` が 2³² を超えてあふれ、中点が `lo` より小さくなるからです。`lo + (hi - lo) / 2` と書き直すと、ビットベクタでも成り立ちます。

これは、Java の標準ライブラリの二分探索に長く残っていた有名なバグと同じ形です。プログラムの整数は数学の整数ではありません。**実際の型に合った理論でモデル化しないと、検査は本物のバグを見逃します**。

## Z3 で最適化する（Optimize）

`Optimize` を使うと、条件を満たす解の中から、ある値を最大化・最小化する解を探せます。

```python
from z3 import Ints, Optimize, sat

# 1 個 120 円のパンと 1 個 150 円のおにぎりを、合わせて 10 個以上、
# 予算 1,400 円以内で買う。おにぎりはできるだけ多く。
bread, onigiri = Ints("bread onigiri")
opt = Optimize()
opt.add(bread >= 0, onigiri >= 0)
opt.add(bread + onigiri >= 10)
opt.add(120 * bread + 150 * onigiri <= 1400)
opt.maximize(onigiri)
if opt.check() == sat:
    m = opt.model()
    print(m, "合計", m.eval(120 * bread + 150 * onigiri))
```

```text
[bread = 4, onigiri = 6] 合計 1380
```

おにぎりを 7 個にすると、パン 3 個と合わせて 1,410 円になり、予算を超えます。6 個が最大です。

検証でも `Optimize` は役立ちます。たとえば料金計算の仕様に反例が見つかったとき、「反例になる注文額の最小値と最大値」を求めれば、問題の範囲がわかります。

## 仕様の矛盾の原因を探す（unsat core）

仕様のルールを全部入れたら `unsat`（満たせない）になったとします。どのルール同士がぶつかっているのかを知りたいときは、**unsat core** を使います。各制約に名前を付けて加えると、矛盾に関わった制約の組を返してくれます。

```python
from z3 import Int, Solver

price = Int("price")        # 注文額（円）
discount = Int("discount")  # 値引き額（円）
s = Solver()
s.assert_and_track(price >= 3000, "R1: 3,000 円以上の注文")
s.assert_and_track(discount == 1000, "R2: クーポンは 1,000 円引き")
s.assert_and_track((price - discount) * 10 >= price * 7, "R3: 支払いは注文額の 70% 以上")
s.assert_and_track(price <= 3200, "R4: 注文額の上限は 3,200 円")
s.assert_and_track(price >= 0, "R5: 注文額は 0 円以上")
print(s.check())
print(s.unsat_core())
```

```text
unsat
[R2: クーポンは 1,000 円引き,
 R3: 支払いは注文額の 70% 以上,
 R4: 注文額の上限は 3,200 円]
```

R2・R3・R4 の 3 つがぶつかっていると返ってきました。1,000 円引いても注文額の 70% 以上を払ってもらうには、注文額が 3,334 円以上必要です。ところが上限は 3,200 円です。R1 と R5 は矛盾に関わっていないので、core に入っていません。

ルールが数十個ある仕様では、「どれとどれがぶつかっているか」を人が探すのは大変です。unsat core はその範囲を絞ってくれます。ただし、返る core は**最小とは限りません**。core に含まれる制約を 1 つ外しても unsat のままなら、その制約は矛盾に必須ではありません。必要に応じて 1 つずつ外して確かめてください。

決定表の抜けと矛盾を検査し、見つかった反例を利用者への質問に変えていく進め方は「[要求仕様書作成ループ](/blogs/posts/2026/10/requirements-spec-loop/)」で書いています。

## SMT-LIB 形式と z3 コマンドの使い方

Python を使わずに、SMT-LIB 2 の形式で書いたファイルを `z3` コマンドに渡すこともできます。「条件を満たす値を探す」の連立方程式を、次の内容で `example.smt2` として保存します。

```lisp
(declare-const x Int)
(declare-const y Int)
(assert (= (+ x y) 10))
(assert (= (- x y) 4))
(check-sat)
(get-model)
```

```bash
z3 example.smt2
```

```text
sat
(
  (define-fun y () Int
    3)
  (define-fun x () Int
    7)
)
```

S 式（Lisp と同じ、括弧を入れ子にする書き方）なので人間には読みにくいですが、ソルバ同士で共通の形式です。ほかのツールが Z3 に問題を渡すときや、Python の `Solver` の中身を `s.sexpr()` で確かめるときに目にします。

## Z3 を裏で使っているツール

Z3 は、ほかの検証ツールの「エンジン」としても広く使われています。名前を知らなくても、間接的に Z3 を使っていることがあります。

- **Apalache**：TLA+ の仕様を検査するツール。状態を 1 つずつ数え上げる代わりに、検査を Z3 で解く論理式に変換します。[Quint](/blogs/posts/2026/11/quint-formal-specification-language/) の `quint verify` は、既定でこの Apalache を使います
- **Dafny**：検証機能つきのプログラミング言語。書いた事前条件・事後条件が成り立つことを、Z3 で証明します
- **angr**：バイナリ解析のフレームワーク。プログラムの実行経路の条件を Z3 で解き、特定の分岐に入る入力を求めます

## 使うときに気をつけること

- **unknown がありうる**：整数の非線形の式（変数同士の掛け算など）や量化子（`ForAll`）を含むと、Z3 が判定できないことがあります。`unknown` を `unsat` と取り違えないでください
- **書き写しを間違えると、間違った式を正しく検査するだけ**：Z3 が調べるのは、あなたが書いた式です。仕様や実装を式に書き写すときに誤れば、結果も的外れになります。反例は実装のテストで再現させて確かめます
- **unsat を信じる前に陽性対照**：わざと性質を破る版を作り、`sat` が出ることを確かめます。検査の書き方を誤って何も調べていない、という空振りを防げます（[陽性対照とは？](/blogs/posts/2026/11/positive-control-in-systems/)）
- **反例は 1 回に 1 つ**：別の種類の反例を探すには、見つけた種類を制約で除外して問い直します
- **状態遷移や並行処理は別の道具が向く**：処理の順番やタイミングが問題になる場合は、[TLA+ と TLC](/blogs/posts/2026/11/tla-plus-tlc-model-checker/) のようなモデル検査器を使います

## まとめ

- SMT ソルバは、SAT ソルバに整数・ビットベクタ・配列などの「理論」を足したもの。Z3 はその代表で、Microsoft Research が開発し、MIT ライセンスで公開されている
- 検証の基本形は**性質の否定を問う**こと。sat ならモデルが反例、unsat ならすべての入力で成り立つ
- 整数とビットベクタのように、**理論の選び方で答えが変わる**。実際の型に合わせてモデル化する
- `Optimize` で最大・最小を、unsat core で矛盾の原因を探せる
- unknown と書き写しの誤りに注意し、unsat は陽性対照で確かめてから信じる

まずは `pip install z3-solver` を入れて、手元の条件分岐を 1 つ `prove` にかけてみてください。

## 次に読む

- [AIコード生成時代に形式手法が実用段階へ](/blogs/posts/2026/06/formal-methods-ai-verification/)：形式手法がなぜ今注目されているか
- [形式手法を Claude Code で回す — Z3 と TLA+ で仕様の穴を見つけ、反例をテストに落とす](/blogs/posts/2026/10/formal-methods-claude-code-spec-check/)：料金計算の仕様を Z3 で検査し、反例を pytest に落とす実践編
- [AIが作ったUIモックの仕様をどう検証するか](/blogs/posts/2026/11/ui-spec-verification-layers/)：決定表の抜けと矛盾を Z3 で探す例
- [契約書を形式手法で検証する](/blogs/posts/2026/11/contract-formal-verification/)：Alloy・TLA+・Z3 の使い分け
- wiki：[SMT ソルバ（Z3）](/blogs/wiki/concepts/smt-solver/)、[形式手法](/blogs/wiki/concepts/formal-methods/)、[TLA+ と TLC](/blogs/wiki/tools/tla-plus/)
