---
title: "形式手法を Claude Code で回す — Z3 と TLA+ で仕様の穴を見つけ、反例をテストに落とす"
date: 2026-10-09
lastmod: 2026-10-09
slug: "formal-methods-claude-code-spec-check"
draft: false
description: "Claude Code に料金計算の仕様を Z3 で、キャッシュ設計を TLA+ で形式化させ、仕様の矛盾と並行実行の競合を見つけた。形式手法とテストの違い、道具の選び方、反例を pytest に落とす手順、検査の空振りの確かめ方を実行結果つきで解説する。"
categories: ["AI/LLM"]
tags: ["claude-code", "形式手法", "Z3", "TLA+", "pytest"]
---

形式手法を使うと、テストでは確かめられない「仕様そのものが正しいか」を機械で検査できます。テストは「実装が仕様どおりか」を確かめるものです。[mizchi さんの「俺のAIプログラミング手法」を読む](/blogs/posts/2026/10/mizchi-ai-coding-loop-formal/) では、記事の後半の柱としてこの形式手法を紹介しました。

ただ、前回の記事は道具の名前とプロンプトを並べただけでした。そこでこの記事では、形式手法とは何かを整理したうえで、**Claude Code に仕様を形式化させ、検査器を実際に走らせた例**を 2 つ載せます。

- **例 1：Z3** — 料金計算の仕様と実装を照合する。実装のバグに加えて、仕様そのものの矛盾が見つかった
- **例 2：TLA+** — キャッシュ無効化の設計をモデル検査する。並行実行で古い値が残り続ける実行順が見つかった

どちらも、反例を pytest のテストケースに落とすところまでやります。記事中の出力は、すべて手元で実行した結果です。

## 形式手法とは何か

形式手法は、仕様や設計を数学的に厳密な形で書き、その性質を機械で検査する技術の総称です。

テストとの違いは、調べる範囲にあります。テストは、人間が選んだ入力をいくつか試します。形式手法の検査器は、モデルが取りうる**すべての入力、すべての実行順**を調べ尽くします。あるいは、値を 1 つずつ試さずに、式のまま解いて答えを出します。そして、性質を破る例（反例）を 1 つ見つけるか、「反例はない」と答えます。

| | テスト | 形式手法 |
|---|---|---|
| 調べる範囲 | 人間が選んだ入力・実行順 | モデルの全入力・全実行順（有限の範囲内） |
| 対象 | 実装 | 仕様・設計のモデル |
| 答え | 通った／落ちた | 反例／「反例なし」 |
| 弱点 | 選ばなかったケースは調べない | モデルが実装と食い違えば、結果も外れる |

最後の行が重要です。検査器が保証するのは「**このモデルについて**」の結果です。モデルが実装を正しく写していなければ、「反例なし」は何も保証しません。だからこの記事では、反例を必ず実装のテストで再現させます。

### 道具の選び方

形式手法の道具は、問いの形で選びます。mizchi さんが公開している仕様化スキル [formal-methods-reconciler](https://github.com/mizchi/skills/tree/main/formal-methods-reconciler) の分類を借りると、次のようになります。

| 問いの形 | 例 | 道具 |
|---|---|---|
| 純粋な述語（入力 → 真偽） | 料金計算、設定値の組み合わせ | Z3（SMT ソルバ） |
| 関係（ユーザー・ロール・リソース） | 権限、テナント分離 | Alloy |
| 状態遷移・並行実行 | キャッシュ、リトライ、分散プロトコル | TLA+ |
| 事前条件・事後条件つきの逐次コード | ループ不変条件、データ構造の不変条件 | Dafny |
| 無限の範囲での定理 | アルゴリズムの正しさ | Lean、Rocq |

補足すると、mizchi さんの元記事では、TLA+ と並べて Quint（TLA+ をベースに、より一般的なプログラミング言語に近い構文で書ける仕様言語）も挙がっています。

同じスキルには「Z3 で時相的なインターリーブ（複数の処理のステップが交互に実行される順番）を扱うな」「単純な述語の整合性に TLA+ を使うな」とも書かれています。**反例を出せる最小の道具を選ぶ**のが原則です。この記事では、表の 1 行目の例として Z3 を、3 行目の例として TLA+ を使います。

## Claude Code と検査器の役割分担

LLM と形式手法を組み合わせるときは、役割分担を決めておくことが肝心です。formal-methods-reconciler スキルの基本姿勢は「LLM がモデルを提案・修正し、ソルバやモデル検査器が判定する」です。正しさの判定を LLM に任せてはいけません。

![Claude Code で形式手法を回すときの役割分担を示すフロー図。人間が自然言語で仕様を書き、Claude Code が主張を抜き出して Z3 や TLA+ で形式化し、検査器が全入力と全実行順を調べる。反例が出たら Claude Code が実装のテストで再現させ、再現すれば人間が意図した挙動かバグか仕様の矛盾かを決めて回帰テストとして残す。再現しなければモデルの前提を直して再検査する。反例が出なければ、正常な状態に到達できるか、修正を外した変異版が落ちるかを確かめて空振りでないことを確認する](/blogs/images/formal-methods-claude-code-loop.png)

図の流れを言葉で整理すると、次のとおりです。

1. **人間**が仕様・設計を自然言語で書く
2. **Claude Code** が主張を抜き出して形式化する
3. **検査器**（Z3、TLA+ のモデル検査器 TLC）が判定する
4. 反例が出たら、**Claude Code** が実装のテストで再現させる。再現しなければ、モデルの前提を疑う
5. 意図した挙動か、バグか、仕様の矛盾かは、**人間**が決める
6. 反例は回帰テストとして CI に残す
7. 反例が出なければ、検査が空振りしていないかを確かめる

## 準備

この記事の例で使った環境は次のとおりです。

- Z3：Python バインディング（z3-solver 5.1.0）を `uv run --with z3-solver` で一時的に入れて実行
- TLA+：[tlaplus/tlaplus](https://github.com/tlaplus/tlaplus) の v1.7.4 リリースに含まれる `tla2tools.jar`（TLC2 Version 2.19）を Java 22 で実行
- pytest：`uv run --with pytest` で実行

`tla2tools.jar` は GitHub CLI で取ってこられます。私は作業ディレクトリの 1 つ上に置き、例ごとのディレクトリから `../tla2tools.jar` で参照しました。

```bash
gh release download v1.7.4 --repo tlaplus/tlaplus --pattern tla2tools.jar
```

## 例 1：Z3 で料金計算の仕様を検査する

### 題材：会員割引とクーポンの料金計算ルール

仕様はこの 3 行です。どこにでもありそうな割引ルールです。

```markdown
# 料金計算の仕様

- R1. 会員は 10% 引き（1 円未満は切り捨て）
- R2. 1,000 円引きクーポンは、注文額（割引前）が 3,000 円以上のときだけ使える
- R3. 最終金額は、注文額の 60% を下回ってはならない
```

実装はこうです。会員割引を掛けてから、クーポンを引いています。

```python
def final_price(price: int, member: bool, coupon: bool) -> int:
    p = price * 9 // 10 if member else price
    if coupon and price >= 3000:
        p -= 1000
    return p
```

一見すると、R1 と R2 をそのまま書いただけに見えます。しかし R3 を守っているかどうかは、コードを読むだけでは判断できません。

### Z3 の考え方：「破る入力」を探させる

Z3 は SMT ソルバです。「この制約をすべて満たす値はあるか」を問うと、あれば `sat` とその値を、なければ `unsat` を返します。

性質を検査するときは、**性質の否定**を制約として与えます。「R3 を破る入力はあるか」と問い、`unsat` が返れば、どの入力でも R3 は破れないことになります。`sat` なら、返ってきた値がそのまま反例です。

最小の検査スクリプトは次のとおりです。実装を Z3 の式に書き写し、R3 の否定を加えています。

```python
from z3 import Int, If, And, Bool, Solver, Not, sat


def final_price_v1(price, member, coupon):
    """The implementation as written: member discount, then coupon."""
    p = If(member, price * 9 / 10, price)
    return If(And(coupon, price >= 3000), p - 1000, p)


def check(name, impl, exclude=None):
    price, member, coupon = Int("price"), Bool("member"), Bool("coupon")
    s = Solver()
    s.add(price >= 1, price <= 1_000_000)
    if exclude is not None:
        # Rule out a counterexample class we already know about.
        s.add(Not(exclude(price, member, coupon)))
    # Ask for an input that breaks R3.
    s.add(Not(impl(price, member, coupon) * 10 >= price * 6))
    if s.check() == sat:
        m = s.model()
        print(f"{name}: sat (R3 violated) ->", m)
        print("  final price =", m.eval(impl(price, member, coupon)))
    else:
        print(f"{name}: unsat (R3 holds for every input)")


check("v1", final_price_v1)
check("v1 without coupon cases", final_price_v1,
      exclude=lambda price, member, coupon: And(coupon, price >= 3000))
```

`price * 0.6` のような小数を避けるため、R3 は `最終金額 × 10 ≥ 注文額 × 6` と整数で表しています。Z3 の `Int` 同士の `/` は、ここでは非負の値しか扱わないので切り捨て除算として働きます。

実行結果です。

```text
v1: sat (R3 violated) -> [price = 3001, member = True, coupon = True]
  final price = 1700
v1 without coupon cases: sat (R3 violated) -> [member = True, price = 1]
  final price = 0
```

反例が 2 種類出ました。

- **会員がクーポンを使い、注文額が 3,001 円**：最終金額は 1,700 円で、下限の 1,800.6 円を割る
- **会員で、注文額が 1 円**：10% 引きを切り捨てると 0 円になり、下限の 0.6 円を割る

ソルバは反例を 1 つずつしか返しません。そこで 2 回目は、1 つ目の反例の種類（クーポンが効くケース）を `exclude` で除外して問い直しています。修正を待たずに次の種類の反例を探すための、定番の手です。

### 反例をテストケースに落とす

Z3 の反例は、Z3 の式に書き写した実装についての主張です。書き写しを間違えていれば、本物の実装では再現しません。そこで、反例をそのまま pytest に落とします。

```python
import pytest

from pricing import final_price


# Counterexamples found by Z3, kept as regression tests
@pytest.mark.parametrize("price, member, coupon", [
    (3001, True, True),   # member discount + coupon
    (1, True, False),     # rounding down to 0 yen
])
def test_r3_floor(price, member, coupon):
    assert final_price(price, member, coupon) * 10 >= price * 6


def test_normal_case_is_unchanged():
    # Sanity check: the fix must not touch orders that were already fine
    assert final_price(10000, member=True, coupon=True) == 8000
```

元の実装に対して実行すると、反例の 2 件が落ちました。

```text
FF.                                                                      [100%]
=================================== FAILURES ===================================
.../test_pricing.py:12: assert (1700 * 10) >= (3001 * 6)
.../test_pricing.py:12: assert (0 * 10) >= (1 * 6)
=========================== short test summary info ============================
FAILED test_pricing.py::test_r3_floor[3001-True-True]
FAILED test_pricing.py::test_r3_floor[1-True-False]
2 failed, 1 passed in 0.00s
```

ここで私は、最終金額を下限で止める修正を書きました。

```python
def final_price(price: int, member: bool, coupon: bool) -> int:
    p = price * 9 // 10 if member else price
    if coupon and price >= 3000:
        p -= 1000
    floor = (price * 6 + 9) // 10  # R3: ceil(price * 0.6)
    return max(p, floor)
```

Z3 で R3 を検査し直すと `unsat` になり、テストも 3 件とも通りました。これで直った、と思いました。

### Claude Code に形式化させる

同じ題材を、今度は Claude Code に一から任せました。作業ディレクトリに `SPEC.md`（上の仕様）と、修正前の `pricing.py` だけを置き、非対話モード（`-p` オプション）で次のように頼んでいます。プロンプトの後半は、前回の記事で紹介した mizchi さんのプロンプトをほぼそのまま使っています。

```bash
claude -p "SPEC.md が仕様、pricing.py が実装です。仕様のうち形式化できる部分を Z3（uv run --with z3-solver python で実行）で形式化し、それをテストオラクルにして実装が仕様に従っているか確認してください。反例が出たら、その反例を pytest のテストケースに落として test_pricing.py に保存してください。実装は修正しないでください。最後に、何を検査したかを、ドメインの言葉を使わずに例え話で説明してください。" \
  --allowedTools "Read" "Write" "Edit" "Bash(uv run:*)" "Bash(ls:*)"
```

`--allowedTools` で、ファイルの読み書きと `uv run` だけを許可しています。数分で `spec_z3.py`（Z3 による形式化）と `test_pricing.py` ができました。

Claude Code の形式化は、私の最小スクリプトより一段深いものでした。中心になる部分を抜き出します（import と一部の定義は省略）。

```python
price = Int("price")
member = Bool("member")
coupon = Bool("coupon")
out = Int("out")  # 実装の戻り値

DOMAIN = price >= 0
COUPON_USABLE = And(coupon, price >= 3000)
MEMBER_PRICE = If(member, (price * 9) / 10, price)  # 非負整数では Z3 の / は floor

SPEC = {
    # R1 + R2 の「使えない」側: クーポンが効かないなら会員割引だけが掛かる
    "R1/R2: クーポン不可なら会員割引のみ": Implies(Not(COUPON_USABLE), out == MEMBER_PRICE),
    # R2 の「使える」側: 使えるときはちょうど 1,000 円安くなる（R3 の下限に当たらない限り）
    "R2: クーポンで最終金額が上がらない": out <= MEMBER_PRICE,
    # R3: out >= 0.6 * price を整数で表す
    "R3: 注文額の 60% 以上": out * 10 >= price * 6,
}
```

2 つ目の性質のコメントは「ちょうど 1,000 円安くなる」ですが、実際に検査しているのは「クーポンで金額が上がらない」という弱い性質です。割引の適用順が仕様に書かれていないため、Claude Code は正確な金額までは形式化しませんでした（後述の質問 3）。

ポイントは、実装の戻り値を `out` という**自由な変数**にしていることです。仕様を「入力と出力の関係」として書いているので、実装と切り離して仕様だけを検査できます。

実際、Claude Code は実装を見る前に、仕様そのものの無矛盾性を検査していました。「どんな出力を選んでも 3 つの規則を同時に満たせない入力」を、量化子 `ForAll` を使って探しています。

```python
all_spec = And(*SPEC.values())
s0 = Solver()
s0.add(DOMAIN, ForAll([out], Not(all_spec)))
```

`spec_z3.py` を実行した結果です。

```text
[矛盾] price=1 member=True coupon=False: 仕様を満たす出力が存在しない
[矛盾] price=1 member=True coupon=True: 仕様を満たす出力が存在しない
[矛盾] price=2 member=True coupon=False: 仕様を満たす出力が存在しない
[矛盾] price=2 member=True coupon=True: 仕様を満たす出力が存在しない
[OK]   R1/R2: クーポン不可なら会員割引のみ: 仕様が満たせる入力の全域（price >= 0）で反例なし
[OK]   R2: クーポンで最終金額が上がらない: 仕様が満たせる入力の全域（price >= 0）で反例なし
[NG]   R3: 注文額の 60% 以上: member=True coupon=True price=3000〜3334  例: final_price(3000, True, True)=1700 (下限 1800.0)  実装で再現=する

実装を price=0..20000 × member × coupon で全数実行した結果:
  R3: 注文額の 60% 以上 member=True coupon=False: 2 件 (1〜2)
  R3: 注文額の 60% 以上 member=True coupon=True: 337 件 (1〜3334)
```

読み取れることは 3 つあります。

- **1〜2 円の会員注文は、実装のバグではなく仕様の矛盾**だった。R1 の切り捨てに従うと 0 円・1 円になり、R3 の下限（0.6 円・1.2 円）を必ず割る。どう実装しても両方は守れない
- **クーポンの違反範囲は 3,000〜3,334 円**だった。Z3 の `Optimize` で最小値と最大値を求めている。私の最小スクリプトが返した 3,001 円は、範囲の中の 1 点にすぎない
- **Z3 の結果を、本物の実装で確かめ直している**。反例を `final_price` に入れ直すだけでなく、0〜20,000 円を全数実行して Z3 の仕様式で判定している

全数実行の「337 件」は、1〜2 円の 2 件と、3,000〜3,334 円の 335 件の合計です。

ここで、私の修正版を振り返ります。私が Z3 で検査したのは R3 だけでした。R3 については `unsat` で、それ自体は正しい結果です。しかし修正版は、1 円の会員注文に 1 円を返します。R1 どおりなら 0 円です。**R3 を優先して R1 を黙って破る、という仕様判断を、修正のつもりで勝手にしていた**わけです。性質を 1 つだけ検査して得た `unsat` は、ほかの性質とのトレードオフを見せてくれません。

Claude Code はこの点を自分では決めず、人間への質問として返してきました。

1. 会員がクーポンを使ったとき、下限で止めるのか、クーポンを使えなくするのか
2. 1〜2 円の注文では、R1 と R3 のどちらを優先するのか
3. 会員割引とクーポンは、どちらを先に適用するのか（仕様に書かれていない）

### Claude Code が生成した pytest テスト

Claude Code が保存した `test_pricing.py` です（冒頭の `import pytest` と `from pricing import final_price` は省略）。

```python
def satisfies_r3(price: int, final: int) -> bool:
    # R3: 最終金額 >= 注文額の 60%（小数を避けて 10 倍で比較）
    return final * 10 >= price * 6


# Z3 が出した違反範囲は member=True, coupon=True で price=3000〜3334。
# 両端と、その内側の代表値を固定する。
@pytest.mark.parametrize("price", [3000, 3001, 3333, 3334])
def test_r3_member_with_coupon_must_not_go_below_60_percent(price):
    assert satisfies_r3(price, final_price(price, member=True, coupon=True))


# 違反範囲のすぐ外側。ここが通ることで、上のテストが「何でも落ちる」検査ではないことを示す。
@pytest.mark.parametrize("price", [2999, 3335])
def test_r3_holds_just_outside_counterexample_range(price):
    assert satisfies_r3(price, final_price(price, member=True, coupon=True))


# price=1, 2 の会員は R1（floor(price*0.9) = 0, 1）と R3（0.6, 1.2 以上）が同時に満たせない。
# 実装ではなく SPEC.md の矛盾なので、仕様が決まるまで xfail で記録しておく。
@pytest.mark.xfail(strict=True, reason="SPEC.md の R1 と R3 が price=1,2 で矛盾（どの実装でも両立不可）")
@pytest.mark.parametrize("price", [1, 2])
def test_r3_tiny_member_price_conflicts_with_r1(price):
    assert satisfies_r3(price, final_price(price, member=True, coupon=False))
```

テストは 3 種類に分かれています。

- 違反範囲の両端と内側：実装を直すまで落ち続ける
- 範囲のすぐ外側：通る。テストが何でも落とすわけではないことを示す
- 仕様の矛盾：`xfail(strict=True)` で記録する。仕様が決まって挙動が変わり、想定外に通るようになると、XPASS として失敗扱いになるので気づける

Claude Code の報告をうのみにせず、私の手元でも実行し直しました。報告どおりの結果です。

```text
FFFF..xx                                                                 [100%]
4 failed, 2 passed, 2 xfailed in 0.01s
```

### 検査内容を例え話で説明させる

最後の「ドメインの言葉を使わずに例え話で」という指示には、次のような説明が返ってきました（抜粋）。

> ふつうのテストは、箱をいくつか手に取って振ってみる「抜き打ち検査」です。今回はその前に、約束を厳密な天秤の形に書き直し、「職人の箱の動きを全部並べて、天秤が傾く入れ方を一つでもいいから探せ」と、疲れを知らない探し屋（Z3）に頼みました。
>
> 探し屋はついでに、職人とは関係のない紙の側の欠陥も見つけました。中身がほんのひとつまみしかない箱では、「1 割減らせ（端数は捨てろ）」と「6 割は残せ」がそもそも両立しません。これは職人を責めても直らないので、紙を書いた人に返す問題です。

「実装のバグ」と「仕様の欠陥」を区別して説明しているので、形式手法に詳しくない人にも、何が見つかったかが伝わります。

## 例 2：TLA+ でキャッシュ無効化の競合を検査する

### 題材：DB 更新後にキャッシュを削除する設計

2 つ目は並行実行の問題です。よくある「DB を更新したらキャッシュを消す」設計を、`DESIGN.md` に書きました。

```markdown
# 商品情報キャッシュの設計

- 読み込み: キャッシュにあればそれを返す。なければ DB から読み、その値をキャッシュに入れて返す
- 更新: DB を更新したあと、キャッシュのエントリを削除する
- 読み込みと更新は別々のワーカーで並行して走る
- 期待: 処理が落ち着いたあと、キャッシュに DB と違う値が残り続けることはない
```

これは Z3 向きの問題ではありません。問題になるのは、読み込みと更新の各ステップが**どの順番で交互に実行されるか**（インターリーブ）です。こういう状態遷移の問題には、TLA+ のモデル検査器 TLC を使います。

### Claude Code に TLA+ でモデル化させる

今度は `DESIGN.md` だけを置いたディレクトリで、次のように頼みました。

```bash
claude -p "DESIGN.md はキャッシュの設計です。この設計を TLA+ でモデル化し、「期待」の行を不変条件として TLC でモデル検査してください。TLC は java -cp ../tla2tools.jar tlc2.TLC で実行できます。反例が出たら、そのトレースを人間が読める手順に直し、設計をどう直せばよいかを提案して、修正版のモデルでも検査してください。最後に、何を検査したかを、ドメインの言葉を使わずに例え話で説明してください。" \
  --allowedTools "Read" "Write" "Edit" "Bash(java:*)" "Bash(ls:*)"
```

生成された `Cache.tla` から、読み込み側の 3 ステップと、更新側の 2 ステップを抜き出します。TLA+ では、変数の次の状態をプライム付き（`cache'`）で書きます。各アクションは、1 回で割り込まれずに実行される 1 ステップを表します。

```text
\* (R1) キャッシュを見る。ヒットならそれを返して終わり、ミスなら DB へ
RCheck(r) ==
  /\ pc[r] = "check"
  /\ IF cache # NoVal
       THEN /\ Finish(r)
            /\ UNCHANGED <<lease>>
       ELSE /\ pc' = [pc EXCEPT ![r] = "readdb"]
            /\ lease' = IF UseLease THEN lease \cup {r} ELSE lease
            /\ UNCHANGED <<left>>
  /\ UNCHANGED <<db, cache, local>>

\* (R2) DB を読む
RReadDB(r) ==
  /\ pc[r] = "readdb"
  /\ local' = [local EXCEPT ![r] = db]
  /\ pc' = [pc EXCEPT ![r] = "fill"]
  /\ UNCHANGED <<db, cache, left, lease>>

\* (R3) 読んだ値をキャッシュに入れる（修正版ではリースが生きているときだけ）
RFill(r) ==
  /\ pc[r] = "fill"
  /\ cache' = IF ~UseLease \/ r \in lease THEN local[r] ELSE cache
  /\ lease' = lease \ {r}
  /\ Finish(r)
  /\ UNCHANGED <<db, local>>

\* (W1) DB を更新する
WUpdate(w) ==
  /\ pc[w] = "update"
  /\ db' = db + 1
  /\ pc' = [pc EXCEPT ![w] = "delete"]
  /\ UNCHANGED <<cache, local, left, lease>>

\* (W2) キャッシュのエントリを削除する（修正版では発行済みリースもすべて無効化）
WDelete(w) ==
  /\ pc[w] = "delete"
  /\ cache' = NoVal
  /\ lease' = {}
  /\ pc' = [pc EXCEPT ![w] = "done"]
  /\ UNCHANGED <<db, local, left>>
```

「期待」の行は、次の不変条件になりました。全ワーカーが終わったあとは、キャッシュも DB も二度と変わりません。そのため「その時点で食い違っていれば、食い違いが残り続ける」と読み替えています。

```text
Settled == \A p \in Procs : pc[p] = "done"

NoStaleWhenSettled == Settled => cache \in {NoVal, db}
```

定数 `UseLease` を `FALSE` にすると元の設計、`TRUE` にすると修正版になります。

### TLC が出した反例

読み込みワーカー 1 つ、更新ワーカー 1 つ、元の設計という最小構成で TLC を実行すると、不変条件違反が報告されます。出力から、各状態で変わった変数だけを抜き出します。

```text
Error: Invariant NoStaleWhenSettled is violated.
Error: The behavior up to this point is:
State 1: <Initial predicate>
/\ cache = NoVal
/\ db = 0
...
State 3: <RReadDB line 51, col 3 to line 54, col 41 of module Cache>
/\ local = (r1 :> 0)
...
State 4: <WUpdate line 66, col 3 to line 69, col 44 of module Cache>
/\ db = 1
...
State 5: <WDelete line 73, col 3 to line 77, col 34 of module Cache>
/\ cache = NoVal
...
State 6: <RFill line 58, col 3 to line 62, col 28 of module Cache>
/\ cache = 0
/\ pc = (r1 :> "done" @@ w1 :> "done")
/\ db = 1
```

人間が読める手順に直すと、次のとおりです。

| # | 誰が | 何をしたか | キャッシュ | DB |
|---|---|---|---|---|
| 1 | 読み込み | キャッシュを見る。ミス | 空 | 古い値 |
| 2 | 読み込み | DB から古い値を読んで手元に持つ | 空 | 古い値 |
| 3 | 更新 | DB を更新する | 空 | **新しい値** |
| 4 | 更新 | キャッシュを削除する。まだ空なので何も起きない | 空 | 新しい値 |
| 5 | 読み込み | 手順 2 で読んだ古い値をキャッシュに入れる | **古い値** | 新しい値 |

TLC の出力では初期状態が State 1 なので、表の手順 2 が State 3、手順 5 が State 6 にあたります。

全員が終わったので、この古い値を消す人はもういません。TTL（キャッシュの有効期限）が切れるか、次の更新が来るまで、読み込みは古い値を返し続けます。原因は、更新側の削除が読み込み側の書き戻しより**先に**走ってしまい、空振りしたことです。

Claude Code のモデルをうのみにしないため、私も同じ設計を、もっと単純な TLA+ モデルで独立に手書きして検査していました。そちらでも、同じ 5 ステップの反例が出ています。

### 修正案：リースで書き戻しを拒否する

Claude Code が提案した修正は、memcached の「リース」と同じ考え方です。Facebook の論文 [Scaling Memcache at Facebook](https://www.usenix.org/conference/nsdi13/technical-sessions/presentation/nishtala)（NSDI 2013）で、古い値の書き戻しを防ぐ仕組みとして紹介されています。

- **キャッシュミスのとき**：確認と同じ原子的なステップで、書き戻し用のトークン（リース）を受け取る
- **更新のとき**：DB を更新したあと、キャッシュを削除し、**発行済みのリースもすべて無効にする**
- **書き戻しのとき**：リースがまだ有効なときだけキャッシュに書く。無効なら書かずに、読んだ値を返すだけにする

上の表の手順 5 は、手順 4 でリースが無効になっているので拒否されます。

ほかの選択肢が解決にならない理由も、あわせて返ってきました。

- **少し待ってからもう一度削除する（遅延二重削除）**：待ち時間が、読み込み側の手順 2〜5 の間隔より長いときしか効かない。保証にはならない
- **TTL に頼る**：古い値が残る時間を短くするだけで、発生は防げない

### 修正版の検査と、空振りでないことの確認

Claude Code は修正版を検査するだけでなく、**検査が空振りしていないか**も自分で確かめていました。私の手元で再実行した結果と合わせてまとめます。先ほどの最小構成（読み込みワーカー 1 つ、更新ワーカー 1 つ）より大きい規模でも検査しています。

| 検査 | 期待 | 結果 |
|---|---|---|
| 元の設計（読み込みワーカー 2 つ × 各 2 回、更新ワーカー 2 つ） | 違反する | 違反する |
| 修正版（同じ規模） | 違反しない | 違反しない（2,790 状態を網羅） |
| 修正版（読み込みワーカー 3 つ × 各 3 回、更新ワーカー 2 つ） | 違反しない | 違反しない（212,675 状態を網羅） |
| 修正版で、キャッシュに値が入ることがある | 到達できる | 到達できる |
| 修正版で、全ワーカーがいつかは終わる | 成り立つ | 成り立つ |
| 修正版から「削除時にリースを無効にする」だけを外した変異版 | 違反する | 違反する |

下の 3 行が、空振りでないことの確認です。

- **キャッシュに値が入ることがある**：もし修正版で「キャッシュに一度も値が入らない」なら、不変条件は自明に成り立ってしまう。`NeverFilled == cache = NoVal` という「破られるべき」不変条件を置き、TLC が違反を報告することを確かめている
- **全ワーカーがいつかは終わる**：誰も終わらなければ `Settled` が真にならず、`NoStaleWhenSettled` は検査されないまま通ってしまう。時相論理の性質 `<>Settled`（いつかは必ず全員終わる）で確かめている
- **変異版が落ちる**：修正の中で効いているのがリースの無効化だと確認できる

これは、モデル検査器が「反例なし」と言ったときに、いちばん確かめるべき点です。性質がたまたま自明に成り立っていたり、検査されないまま通っていたりしないかを確認します。

実行例として、規模を大きくした修正版の TLC の出力を載せます。私が 1 ワーカーで再実行したときのものです。fingerprint の衝突確率の推定値や探索の深さは、実行条件によって少し変わります。Claude Code が 28 ワーカーで実行したときは 7.3E-9 と 22 でした。状態数は同じです。

```text
Model checking completed. No error has been found.
  Estimates of the probability that TLC did not check all reachable states
  because two distinct states had the same fingerprint:
  calculated (optimistic):  val = 5.5E-9
  based on the actual fingerprints:  val = 3.9E-9
693352 states generated, 212675 distinct states found, 0 states left on queue.
The depth of the complete state graph search is 21.
```

Claude Code は、モデルが**扱っていない**範囲も明記していました。

- 更新ワーカーが「DB 更新」と「キャッシュ削除」の間でクラッシュする場合。これも古い値が残るので、TTL やリトライキューなどで別に手当てが要る
- キャッシュと DB の各操作を、それぞれ原子的な 1 ステップとして扱っていること

### 反例を実装のテストで再現する

TLC のトレースも、モデルについての主張にすぎません。実装で同じ実行順を強制して、本当に起きるかを確かめます。

検査用に、ごく小さな読み込み型キャッシュを Python で書きました。`after_db_read` は、DB を読んだ直後に読み込み側を止めるためのテスト用フックです。

```python
import threading


class ReadThroughCache:
    def __init__(self, db: dict, version_check: bool = False, after_db_read=None):
        self.db = db              # key -> (version, value)
        self.cache = {}
        self.version_check = version_check
        self.after_db_read = after_db_read or (lambda: None)
        self.lock = threading.Lock()

    def get(self, key):
        if key in self.cache:
            return self.cache[key]
        version, value = self.db[key]
        self.after_db_read()      # test hook: lets a test pause the reader here
        with self.lock:           # check-and-set must be atomic (e.g. a Lua script in Redis)
            if not self.version_check or self.db[key][0] == version:
                self.cache[key] = value
        return value

    def update(self, key, value):
        with self.lock:
            version, _ = self.db[key]
            self.db[key] = (version + 1, value)
        self.cache.pop(key, None)
```

修正版（`version_check=True`）は、リースの代わりに DB のバージョン番号を使っています。「読んだときから更新されていなければ書き戻す」という同じ考え方を、確認と書き込みをロックで原子的にして実装したものです。リースのトークン管理を書かずに済むので、数十行の検証用実装で同じ性質を再現しやすい、というのがこの形にした理由です。

テストは、`threading.Event` で TLC のトレースの順番を強制します。コメントの Step は、上の表の手順番号です。

```python
import threading

import pytest

from cache import ReadThroughCache


@pytest.mark.parametrize("version_check", [False, True])
def test_tlc_trace_does_not_leave_stale_cache(version_check):
    """Replay the TLC trace: RReadDB -> WUpdate -> WDelete -> RFill."""
    read_done, resume = threading.Event(), threading.Event()

    def pause_reader():
        read_done.set()
        resume.wait(timeout=5)

    c = ReadThroughCache({"k": (1, "old")}, version_check, after_db_read=pause_reader)
    reader = threading.Thread(target=c.get, args=("k",))
    reader.start()
    read_done.wait(timeout=5)   # Step 2: the reader has read "old" from the DB
    c.update("k", "new")        # Steps 3-4: the writer updates the DB and deletes the cache
    resume.set()
    reader.join()               # Step 5: the reader fills the cache

    assert c.cache.get("k") in (None, c.db["k"][1])
```

実行結果です。元の設計ではキャッシュに `"old"` が残り、修正版では通りました。

```text
F.                                                                       [100%]
=================================== FAILURES ===================================
.../test_cache.py:25: AssertionError: assert 'old' in (None, 'new')
=========================== short test summary info ============================
FAILED test_cache.py::test_tlc_trace_does_not_leave_stale_cache[False]
1 failed, 1 passed in 0.00s
```

ふつうに並行テストを走らせても、この競合はまず再現しません。手順 2 と 5 の間に更新が割り込むのは、まれなタイミングだからです。TLC のトレースがあれば、**どこで止めて、何を割り込ませればよいか**がわかります。だから、決定的に再現するテストが書けます。

## 実務に組み込むときのポイント

2 つの例から、Claude Code と形式手法を組み合わせるときのポイントを整理します。

### 判定は検査器に任せ、LLM には判定させない

Claude Code の役割は、主張の抽出、形式化、反例の説明、修正案の提案です。「正しいかどうか」は Z3 や TLC の出力で決めます。Claude Code が「問題ありません」と書いても、検査器の出力がなければ信用しません。この記事でも、生成されたテストと TLC は手元で実行し直しています。

### 反例は必ず実装で再現させる

モデルの反例は、モデルについての主張です。実装のテストで同じ入力・同じ実行順を強制して、再現して初めてバグと言えます。再現しなければ、まずモデルの前提（原子性、ロックの粒度、リトライの方針など）を疑います。

### 「反例なし」は空振りを疑う

`unsat` や `No error has been found` は、次の場合にも出ます。

- 性質が自明に成り立っている（キャッシュに一度も値が入らない、など）
- 前提条件が一度も真にならない（誰も終わらない、など）
- 検査した性質が 1 つだけで、ほかの性質とのトレードオフが見えていない（例 1 の私の修正版）

正常な状態に到達できることと、修正を外した変異版が落ちることを、セットで確かめます。

### 仕様の矛盾は人間に返す

例 1 の 1〜2 円問題のように、どう実装しても満たせない仕様は、実装側では直せません。Claude Code に「決めずに質問として返す」よう任せると、仕様の持ち主が判断すべき点が整理されて戻ってきます。決まるまでは `xfail(strict=True)` で記録しておけば、判断が入ったときにテストが知らせてくれます。

### CI に残すのはテストと検査スクリプト

形式モデルとその検査コマンド、反例から作ったテストをリポジトリに残せば、あとで仕様や実装が変わったときに同じ検査を流せます。同じ mizchi/skills リポジトリには、こうした「仕様と実装のずれ」を継続的に見張るための姉妹スキル [formal-methods-drift-guard](https://github.com/mizchi/skills/tree/main/formal-methods-drift-guard) もあります。

## まとめ

- テストは選んだ点だけを調べる。形式手法はモデルの全入力・全実行順を調べ、反例か「反例なし」を返す
- 道具は問いの形で選ぶ。述語なら Z3、状態遷移や並行実行なら TLA+
- Claude Code には形式化と説明を任せ、判定は検査器に任せる
- 反例は実装のテストで再現させ、回帰テストとして残す
- どう実装しても満たせない仕様の矛盾は、実装で直さず人間に返す（決まるまでは xfail で記録）
- 「反例なし」は空振りを疑い、正常な状態への到達と変異版の失敗で確かめる

今回の 2 つの例は、どちらも数分で終わりました。仕様 3 行の料金計算でも、仕様の矛盾が 1 つ見つかっています。まずは手元の仕様の中から、条件が 3 つ以上重なっているものを 1 つ選んで、Claude Code に Z3 で形式化させてみてください。
