---
title: "形式検証 Skill を作る前に状態遷移をモデルにする — 図は描かせずレンダリングする（pstack /statechart・TLA+・SCXML）"
date: 2026-11-17
lastmod: 2026-11-17
slug: "statechart-before-formal-verification"
draft: false
source_url: "https://github.com/hdknr/blogs/issues/556#issuecomment-6941497758"
categories: ["AI/LLM"]
tags: ["形式手法", "TLA+", "状態遷移図", "モデル検査", "SCXML", "Agent Skills", "claude-code"]
---

## はじめに

コーディングエージェントに形式検証をさせるとき、いきなり検証の Skill を作らせるより、**先に状態遷移図（statechart）を描かせたほうがうまくいく**——そんな使い方が X で話題になっていました。

発端は、poteto（lauren）さんの[投稿](https://x.com/poteto/status/2112736749281759566)です。poteto さんは React Compiler のコアチームのメンバーで、Cursor 向けの Skill 集 **pstack** の作者でもあります。投稿の内容は、エージェントに状態遷移図を描かせ、pstack で作った `/create-formal-verification-skill` を使って TLA+ のような道具でバグを探すと、「コードの理解」と「ユーザーの使い方のフロー」が同時に手に入り、ユーザーが踏むはずだった不具合を先に直せる、というものです。

これを引用した kaito さん（[@cu30rry_](https://x.com/cu30rry_/status/2112863970227016171)）は、次のように整理しています。

- 形式検証 Skill を作る**前に**、エージェントが提案した機能について状態遷移図を描かせるのが効果的
- 図を描くと、コードの状態とユーザーの使い方のフローを同時に把握できる
- 守るべき性質（仕様）を言語化しやすくなる
- pstack の「README やチュートリアルから先に考える」やり方と似た発想

この記事では、pstack の該当する Skill の中身を読みながら、この順番がなぜ効くのかを整理します。

### 「図を描かせる」をどう読むか

元の投稿の言い方は "draw a statechart"（状態遷移図を描かせる）です。ただ、図はあくまで見せ方（プレゼンテーション）です。エージェントに絵を描かせても、その絵は検査も実行もできません。

この記事では「描かせる」を、**状態遷移のモデルを書かせ、図はそこからレンダリングする**と読み替えます。後で見るとおり、pstack の `/statechart` も実際にこの形で動いています。正本（変更するときに手を入れる唯一の元データ）にするモデルには、検証が目的なら TLA+、実装そのものを状態機械として書くなら SCXML が候補になります。

### 登場するもの

| 名前 | 何か |
|---|---|
| pstack | poteto さんが公開している Skill 集。Cursor のプラグインとして配布され、Claude Code にも入る（[cursor/plugins](https://github.com/cursor/plugins/tree/main/pstack)） |
| `/create-formal-verification-skill` | バグの損害が大きくテストが届きにくい箇所を選び、性質を 1 つ形式検証し、それを再検査するプロジェクト専用の Skill を生成する |
| `/statechart` | TLA+ のモデルを TLC で検査し、Mermaid の状態遷移図として描く。規則を破る状態に印を付け、そこまでの最短経路を示す |
| `/in-your-own-words` | ユーザーの目的と解決したい問題を、エージェント自身の言葉で言い直させる |
| `/poteto-help` | pstack の使い方の相談役。どの Skill を使うか迷ったときに呼ぶ |
| TLA+ / TLC | 設計を状態と遷移で書く仕様記述言語と、そのモデル検査器 |
| SCXML | 状態遷移を XML で書く W3C の勧告。そのまま実行できる状態機械の定義 |

TLA+ と TLC そのものについては「[TLA+ のモデル検査器 TLC とは](/blogs/posts/2026/11/tla-plus-tlc-model-checker/)」で詳しく書きました。

## 全体の流れ

元の投稿の提案を、pstack の Skill の手順と重ねると次のようになります。左側の「理解する」段階を、形式検証の前に足すのがポイントです。

![形式検証 Skill を作る前に状態遷移をモデルにする流れ。左の「理解する」段階では、エージェントの機能提案から TLA+ や SCXML で状態遷移のモデルを書かせて図をレンダリングし、人がその図を読んで遷移の正しさや抜けを判断し、守るべき性質を 1 文で言語化する。右の「検証する」段階では /create-formal-verification-skill で性質を検証し、壊したコードで失敗することを確かめ、/statechart で違反までの最短経路を読み、反例を実コードで再現して、最後にプロジェクト専用の検証 Skill が残る](/blogs/images/statechart-before-formal-verification-flow.png)

- **理解する**：状態遷移のモデルを書かせ、図をレンダリングする → 人が読んで判断する → 守るべき性質を言葉にする
- **検証する**：性質を検証する → 壊したコードで失敗を確かめる → 反例を読む → 実コードで再現する

## /create-formal-verification-skill は何をするか

まず、検証側の Skill の中身を確認します。`SKILL.md` によると、この Skill は次のような手順で動きます。

1. **対象を選ぶ**：コードが約束していることのうち、壊れるとユーザーが困り、テストがめったに届かないものを選ぶ。検証しやすいものではなく、一番強い対象を選ぶ
2. **道具を選ぶ**：問いに合う道具を使う。「イベントが悪い順序で起きうるか」ならモデル検査器で、既定は TLA+。「全入力でコードが正しく動くか」ならコード上で動く検証器
3. **検証する**：性質を 1 つ検証し、壊したコードで失敗することも示す
4. **Skill を生成する**：次のエージェントが変更のたびに 1 コマンドで再検査できる、プロジェクト専用の Skill を書き出す

品質の条件には、たとえば次のものがあります。

- **コードに忠実であること**：モデルのどの部分も、レビューする人が開けるコードを指している
- **失敗できること**：一度も失敗したことのない検査は何も証明しない。チェックを外す、手順を入れ替えるなど、壊したコードで各性質が落ちることを示す
- **見つけたものは見つけたものとして扱う**：今のコードが性質を破るなら反例とともに報告する。通すために性質やモデルを弱めない
- **道具を知らなくても読める**：性質と、それが破れたときの害を、それぞれ平易な 1 文で述べる

「失敗できること」は、以前「[陽性対照（ポジティブコントロール）とは？](/blogs/posts/2026/11/positive-control-in-systems/)」で書いた、「異常なし」を信じる前に検査が異常を検出できることを確かめる考え方そのものです。

## 状態遷移を先にモデルにすると何が良いか

上の条件を見ると、この Skill を走らせる時点で次の 2 つが決まっていることが前提になると分かります。

- **何を守るべきか**（性質。`/statechart` では「規則」と呼び、TLA+ では不変条件として書く）
- **その性質が破れると誰がどう困るか**（害）

ところが「この機能を形式検証して」とだけ頼むと、エージェントはコードから性質を推測するしかありません。コードに書かれていない「本来こうあるべき」は、コードからは読み取れないからです。

そこで、先に状態遷移をモデルとして書かせ、図にして人に見せます。説明用の仮想例として、購入フローで試してみます。

### 例：購入フローを TLA+ で書く

エージェントに書かせるモデルは、たとえば次のようなものです。状態は 3 つの変数で表します。画面の段階（`phase`）、返事を待っている決済要求の数（`pending`）、実際に請求された回数（`captured`）です。

```text
---- MODULE Checkout ----
EXTENDS Naturals

VARIABLES phase, pending, captured
vars == <<phase, pending, captured>>

Init == phase = "cart" /\ pending = 0 /\ captured = 0

\* 支払い処理中でも購入ボタンが押せ、決済要求がもう 1 つ飛ぶ
PressBuy ==
    /\ phase \in {"cart", "paying"}
    /\ pending < 2
    /\ pending' = pending + 1
    /\ phase' = "paying"
    /\ UNCHANGED captured

ChargeSucceeds ==
    /\ pending > 0
    /\ pending' = pending - 1
    /\ captured' = captured + 1
    /\ phase' = "done"

\* 最後の決済要求が失敗したときだけ「支払い失敗」に移る
ChargeFails ==
    /\ pending > 0
    /\ pending' = pending - 1
    /\ phase' = IF phase = "paying" /\ pending = 1 THEN "failed" ELSE phase
    /\ UNCHANGED captured

Retry ==
    /\ phase = "failed"
    /\ phase' = "cart"
    /\ UNCHANGED <<pending, captured>>

\* 完了後は何も起きない（行き止まりをデッドロックと判定させないための足踏み）
Finished ==
    /\ phase = "done" /\ pending = 0
    /\ UNCHANGED vars

Next == PressBuy \/ ChargeSucceeds \/ ChargeFails \/ Retry \/ Finished

\* 規則: 1 回の注文で請求は 1 回だけ
ChargedAtMostOnce == captured <= 1
====
```

最後の `ChargedAtMostOnce` が、守るべき性質を不変条件にしたものです。設定ファイル `Checkout.cfg` には、初期状態・遷移・検査する不変条件を書きます。

```text
INIT Init
NEXT Next
INVARIANT ChargedAtMostOnce
```

TLC 2.19 で検査すると（`tlc` は `tla2tools.jar` の `tlc2.TLC` を呼ぶラッパーです）、7 つの状態を展開して次の反例を返しました。

```bash
tlc -workers 1 -config Checkout.cfg Checkout.tla
```

```text
Error: Invariant ChargedAtMostOnce is violated.
State 1: <Initial predicate>               phase = "cart",   pending = 0, captured = 0
State 2: <PressBuy>                        phase = "paying", pending = 1, captured = 0
State 3: <PressBuy>                        phase = "paying", pending = 2, captured = 0
State 4: <ChargeSucceeds>                  phase = "done",   pending = 1, captured = 1
State 5: <ChargeSucceeds>                  phase = "done",   pending = 0, captured = 2
```

（読みやすいように 1 行 1 状態に整形しています）

購入ボタンを 2 回押し、2 つの決済要求がどちらも成功すると、請求が 2 回になります。

### 図はモデルからレンダリングする

TLC は、展開した状態グラフを Graphviz の dot 形式で書き出せます。

```bash
tlc -dump dot,actionlabels checkout -config Checkout.cfg Checkout.tla
```

この状態グラフを、ユーザーに見える言葉に置き換えて Mermaid にすると、次の図になります。この記事では対応付けを手で書きました。後で見る pstack の `/statechart` なら、状態と遷移の言葉（ビュー）を書けば、Mermaid への変換は自動で行われます。

![TLC が展開した購入フローの状態グラフを Mermaid でレンダリングした図。カート確認中から購入ボタンを押すと支払い処理中になり、決済が成功すれば購入完了、失敗すれば支払い失敗からもう一度試せる。支払い処理中に購入ボタンをもう一度押すと決済要求が 2 件の状態になり、片方の決済が成功すると決済要求が 1 件残った購入完了に、残りの決済も成功すると二重請求の状態に進む。二重請求は「1 回の注文で請求は 1 回だけ」という規則への違反として赤く示されている](/blogs/images/statechart-before-formal-verification-checkout.png)

手で描いた図と違って、「描き忘れた矢印」がありません。図にすると、次の 3 つの利点があります。

- **抜けた遷移に気づく**：「支払い処理中にもう一度押したら？」という矢印が、モデルから機械的に出てくる。正常系だけを考えて手で描くと、この矢印は描かれない
- **性質が言葉になる**：「1 回の注文で請求は 1 回だけ」という規則を、図を見ながら確かめられる
- **人が判断できる**：状態の名前を「支払い処理中」のようなユーザーに見える言葉にしておけば、TLA+ を読めない人でも「この遷移はおかしい」と言える

### 直して、通ることを確かめる

直し方は、購入ボタンを押せるのをカート確認中だけに限ることです。`PressBuy` の 1 行目だけを変えます。

```text
PressBuy ==
    /\ phase = "cart"
    /\ pending < 2
    /\ pending' = pending + 1
    /\ phase' = "paying"
    /\ UNCHANGED captured
```

同じ設定で TLC にかけると、到達できる状態は 4 つに減り、`Model checking completed. No error has been found.` で終わりました。直す前の版で不変条件が破れることを先に見ているので、この「エラーなし」は検査が空振りしたのではない、と言えます。

こうして言葉になった規則と小さなモデルを `/create-formal-verification-skill` に渡せば、検証する性質を推測させずに済みます。

## pstack の /statechart がやっていること

pstack には、状態遷移図そのものを扱う `/statechart` という Skill もあります。`SKILL.md` の要点は次のとおりです。

- TLA+ の仕様と設定を書き、TLC で検査して、結果を Mermaid の状態遷移図にする
- 読む人が同意した規則を、それぞれ `INVARIANT`（不変条件）として書く。**規則を弱めて通すことはしない**
- 状態のラベルは読む人に見える言葉にし、変数名を出さない。遷移のラベルも「再生ボタンを押す」「接続が失敗する」のように、ユーザーから見た出来事として書く
- 条件付きの遷移は、`you press play [while the file loads]`（ファイルの読み込み中に再生を押す）のように角括弧で条件を添える
- 規則を破る状態には `breaks`、一部だけ破る状態には `mayBreak` の印が付き、レポートにはそこまでの最短経路が出る
- 図が読めなくならないよう、矢印は 20 本前後までに抑える

さらに、`/create-formal-verification-skill` 側には「検査が TLA+ のモデルなら、結果は `/statechart` で読むよう、生成する Skill に書いておく」という指示があります。違反があれば `/statechart` が最短経路を平易な言葉で示し、通ればシステムの状態の動きを図にします。

ここで大事なのは、`/statechart` が**図を描いていない**ことです。正本は TLA+ の仕様で、TLC がそこから到達できる状態をすべて展開します。エージェントがビューのモジュールに書く関数（状態のラベルを返す `state()`、遷移のラベルを返す `step()`）が、その状態と遷移をユーザーの言葉に置き換え、Mermaid の `chart.mmd` として出力します。

つまり pstack の中では、**状態遷移図は検証結果を人が読むための窓口**として組み込まれています。元の投稿が提案しているのは、この窓口を**検証の後だけでなく前にも**使うことだと読めます。

### 図に出た反例は実コードで確かめる

`/statechart` の手順の最後には、モデルが実コードを表しているなら、各バグの経路を 1 アクションずつ実コード上で再現するよう書かれています。再現しなければ、疑うべきはモデルのほうです。

状態遷移図はあくまでモデルの絵です。図の上で見つかった二重請求が、実際のコードでも起きるかどうかは、テストや、実際に動かしての再現で確かめる必要があります。

## 正本を SCXML にするという選択肢

「モデルを正本にして、図はレンダリングする」という方針は TLA+ に限りません。状態遷移を表すモデルの標準には、W3C 勧告の **SCXML**（State Chart XML）もあります。UML ステートマシンの元になった Harel のステートチャート（この記事でいう状態遷移図の元になった概念）を、XML で書けるようにしたものです。

直した後の購入フロー（支払い処理中は購入ボタンを受け付けない版）を SCXML で書くと、次のようになります。

```xml
<scxml xmlns="http://www.w3.org/2005/07/scxml" version="1.0" initial="cart">
  <state id="cart">
    <transition event="buy" target="paying"/>
  </state>
  <state id="paying">
    <!-- 入ったときに決済 API を呼ぶ。この状態に buy の遷移はない -->
    <transition event="charge.succeeded" target="done"/>
    <transition event="charge.failed" target="failed"/>
  </state>
  <state id="failed">
    <transition event="retry" target="cart"/>
  </state>
  <final id="done"/>
</scxml>
```

SCXML の定義は、そのまま実行できます。今の状態に合う遷移がないイベントは捨てられるので、この定義で画面を動かせば、支払い処理中に購入ボタンを押しても何も起きません。二重請求は、構造の上で起こりえなくなります。

TLA+ と SCXML は、どちらもモデルを正本にしますが、得意なことが違います。

| 正本 | 得意なこと | 苦手なこと | 向いている用途 |
|---|---|---|---|
| **TLA+** | 不変条件を書き、到達できる状態を TLC で総当たりして反例を出せる | 実行できず、モデルと実コードがずれうる | 既存のコードの性質を検証する（この記事の主題） |
| **SCXML** | 定義をそのまま実行できる。モデル＝実装なので、図と実装がずれない | 不変条件を書く場所がなく、総当たりの検査道具も一般的ではない | これから実装する UI のフローやプロトコルを状態機械として書く |

TLA+ の「ずれうる」という弱点があるので、`/create-formal-verification-skill` は「コードに忠実」や「反例を実コードで再現」をわざわざ求めています。SCXML の実行エンジンには Java の Apache Commons SCXML などがあります。JavaScript の XState も SCXML に着想を得たライブラリで、同じように定義から図も実装も出せます。

両方をつなぐなら、SCXML から TLA+ の骨組みを生成し、不変条件だけ人が足す構成も考えられます。ただし、広く使われている変換ツールは筆者の知る限りまだありません。

どちらの標準にも図の座標を書く仕組みはないので、図にするときのレイアウトは自動になります。図を手で整えたくなったら、それは図が正本になりかけている合図です。

## README 駆動・「言い直させる」との共通点

kaito さんは、この使い方を pstack の 2 つの考え方と並べています。

**README やチュートリアルから先に書く**。pstack の `/poteto-help` に同梱されたプロンプトの手引きには、共有パッケージや API を作るなら、まず README やチュートリアルを書かせて、そこからコードへ遡る、という助言があります。ドキュメントが、エージェントが自分の仕事を照らし合わせる目標になるからです。

**目的を言い直させる**。投稿では `/in-your-own-goal` と書かれていますが、pstack に実在するのは `/in-your-own-words` です。`/in-your-own-words` は、ユーザーの目的と問題をエージェント自身の言葉で言い直させるだけの短い Skill です。コードを書く前に、誤読が表に出ます。

状態遷移を先にモデルにして図で見せるのも同じ構図です。コードを書く（あるいは検証する）前に、**人が読んで正誤を判断できる形で、エージェントの理解を外に出させる**。README は使い方を、言い直しは目的を、状態遷移図は振る舞いを、それぞれ見える形にしています。

## 試すには

pstack は Claude Code にもプラグインとして入れられます（README より）。シェルではなく、Claude Code のプロンプトで次を実行します。

```text
/plugin marketplace add cursor/plugins
/plugin install pstack@cursor-plugins
```

Claude Code ではプラグインのコマンドに接頭辞が付くため、`/statechart` は `/pstack:statechart` のように呼びます。`/create-formal-verification-skill` と `/statechart` は、どちらもユーザーが明示的に呼んだときだけ動く Skill です（`disable-model-invocation: true`）。

全体の流れの図を、実際の操作に落とすと次のようになります。

1. 対象の機能について、エージェントに状態遷移のモデル（TLA+ など）を書かせ、図をレンダリングさせる。図のラベルはユーザーに見える言葉にさせる
2. レンダリングされた図を読み、おかしな遷移や抜けている遷移を指摘する
3. 守るべき規則を 1 文ずつ言葉にする（例：「1 回の注文で請求は 1 回だけ」）
4. その規則を添えて `/create-formal-verification-skill` を呼ぶ
5. 検証結果は `/statechart` の図とレポートで読み、反例は実コードで再現する

## まとめ

- pstack の `/create-formal-verification-skill` は、性質を 1 つ形式検証し、変更のたびに再検査できるプロジェクト専用の Skill を残す
- その性質を推測させないために、**先に状態遷移をモデルにして図で見せ、人が守るべき規則を言葉にする**のが効く
- 図はプレゼンテーションで、正本はモデル。エージェントには絵を描かせず、モデルを書かせて図はレンダリングする。pstack の `/statechart` はまさにその形で、TLA+ の仕様を TLC で展開し、「ユーザーに見える言葉の状態遷移図」と「違反までの最短経路」を出す。図は検証の後にも前にも使える
- 検証が目的なら TLA+、実装そのものを状態機械として書くなら SCXML や XState を正本にする
- README 駆動や「目的を言い直させる」と同じく、エージェントの理解を人が判断できる形で先に外に出させる、という考え方の一つ

形式検証というと「どの道具で何を証明するか」に目が向きがちですが、実際には「何を守るべきか」を決めることこそが最も難しい部分です。そこをモデルとその図で埋めるのは、エージェント時代の形式手法の現実的な入り口だと思います。

## 参考

- [poteto さんの投稿（X）](https://x.com/poteto/status/2112736749281759566)
- [kaito さんの投稿（X）](https://x.com/cu30rry_/status/2112863970227016171)
- [pstack（cursor/plugins）](https://github.com/cursor/plugins/tree/main/pstack)
- [create-formal-verification-skill の SKILL.md](https://github.com/cursor/plugins/blob/main/pstack/skills/create-formal-verification-skill/SKILL.md)
- [statechart の SKILL.md](https://github.com/cursor/plugins/blob/main/pstack/skills/statechart/SKILL.md)
- [State Chart XML (SCXML): State Machine Notation for Control Abstraction（W3C 勧告）](https://www.w3.org/TR/scxml/)
