---
title: "TLA+ の TLC が出力する .dot ファイルとは — 状態グラフを Graphviz で可視化する"
date: 2026-11-27
lastmod: 2026-11-27
slug: "tlc-dot-state-graph"
draft: false
source_url: "https://github.com/hdknr/blogs/issues/556#issuecomment-7207119803"
description: "TLA+ のモデル検査器 TLC が -dump dot で出力する .dot ファイルの中身（状態ノード・遷移エッジ・初期状態の塗りつぶし）を、ドアの小さな仕様を例に解説する。Graphviz での PNG/SVG 変換、colorize・actionlabels などのオプション、既定オフの出力を使うべき場面と大きなモデルで避ける理由、反例だけを描く -dumpTrace dot まで。"
categories: ["ツール/開発環境"]
tags: ["TLA+", "形式手法", "モデル検査", "Graphviz", "状態遷移図"]
---

## はじめに

TLA+ のモデル検査器 **TLC** は、指定すると `*.dot` という拡張子のファイルを出力します。既定では作られず、TLA+ Toolbox で「Visualize state graph after completion of model checking」を有効にしたときか、TLC に `-dump dot` オプションを渡したときにだけ作られるファイルです。

中身は **TLC が探索した状態空間（状態グラフ）を Graphviz で描くためのテキストデータ**です。TLC が見つけた「すべての状態（ノード）」と「アクションによる状態遷移（エッジ）」が、Graphviz の DOT 言語で書かれています。画像に変換すれば、仕様が意図どおりに遷移しているか、どこで行き止まり（デッドロック）になっているかを目で確かめられます。

この記事では、小さな仕様を例に `.dot` ファイルの中身を読み、画像への変換方法と、`-dump dot` を使う場面・使わない場面を整理します。TLC そのものについては [TLA+ のモデル検査器 TLC とは](/blogs/posts/2026/11/tla-plus-tlc-model-checker/) を参照してください。

## 用語の整理

| 用語 | 意味 |
|---|---|
| TLC | TLA+ で書いた仕様の到達可能な状態を総当たりで探索するモデル検査器 |
| 状態（ノード） | 仕様の変数すべてに値が入った 1 つの組み合わせ（例: `door = "open"`, `locked = FALSE`） |
| アクション | 状態をどう変えるかを書いた TLA+ の式（例: 後述の `Open`） |
| 遷移（エッジ） | あるアクションを実行して、ある状態から次の状態へ移ること |
| 反例（エラートレース） | 不変条件違反やデッドロックに至るまでの状態の列 |
| DOT 言語 | ノードとエッジをテキストで書く、Graphviz のグラフ記法 |
| Graphviz | DOT 言語で書かれたグラフを画像にするオープンソースのツール群。`dot` コマンドはその 1 つ |
| フィンガープリント | TLC が状態を区別するために計算する 64 ビットのハッシュ値。`.dot` ではノード ID に使われる |

## TLC で `.dot` ファイルを出力する（-dump dot）

`-dump` は本来、到達したすべての状態をファイルに書き出すオプションです。そのあとに `dot` を付けると、書き出す形式が DOT になります。`dot` を省くと、到達可能な状態を TLA+ の式で列挙したテキスト（`.dump`）が出力されます。

```bash
java -cp tla2tools.jar tlc2.TLC -dump dot Door.dot Door.tla
```

`dot` のあとにカンマ区切りで指定を足すと、出力の見た目を変えられます。

| 指定 | 効果 |
|---|---|
| `colorize` | 遷移の矢印をアクションごとに色分けし、凡例（Next State Actions）を付ける |
| `actionlabels` | 遷移の矢印にアクション名のラベルを付ける |
| `constrained` | `CONSTRAINT` / `ACTION_CONSTRAINT` で探索から外れた状態も含める（薄い黄色で描かれる） |
| `snapshot` | 状態を書き出すたびに、その時点で閉じた DOT ファイルを `<名前>_snapshot.dot` として書き出す |

TLA+ Toolbox では、モデルの「TLC Options」ページの Features セクションにある「Visualize state graph after completion of model checking」にチェックを入れると、同じ出力が得られます（版によってはラベルが「Visualize state graph after completion」と短くなっています）。既定ではオフです。

## .dot ファイルの中身を読む — ドア仕様の状態グラフの例

ドアの開閉と施錠を表す、次の仕様を考えます。

- `Open`: 閉まっていて施錠されていなければ開ける
- `Close`: 開いていれば閉める
- `Lock`: 閉まっていて施錠されていなければ鍵をかける

ただし**鍵を開けるアクションを書き忘れています**。

```tla
---- MODULE Door ----
VARIABLES door, locked

Init == door = "closed" /\ locked = FALSE

Open   == door = "closed" /\ ~locked /\ door' = "open"   /\ UNCHANGED locked
Close  == door = "open"   /\ door' = "closed" /\ UNCHANGED locked
Lock   == door = "closed" /\ ~locked /\ locked' = TRUE  /\ UNCHANGED door

Next == Open \/ Close \/ Lock
====
```

同じディレクトリに、初期状態と次状態の式を指定する設定ファイル `Door.cfg` を置きます。

```text
INIT Init
NEXT Next
```

この仕様を、色分けとラベル付きで検査します。TLC は既定でデッドロックを検出するとそこで止まるので、今回は `-deadlock` でデッドロックの検査をオフにして、探索を最後まで進めます。

```bash
java -cp tla2tools.jar tlc2.TLC -deadlock -dump dot,colorize,actionlabels Door.dot Door.tla
```

出力される `.dot` ファイルはおおよそ次の形です。

```dot
strict digraph DiskGraph {
node [shape=box,style=rounded]
edge [colorscheme="paired12"]
nodesep=0.35;
subgraph cluster_graph {
color="white";
101 [label="/\\ door = \"closed\"\n/\\ locked = FALSE",style = filled]
101 -> 202 [label="Open",color="2",fontcolor="2"];
202 [label="/\\ door = \"open\"\n/\\ locked = FALSE",tooltip="..."];
101 -> 303 [label="Lock",color="3",fontcolor="3"];
303 [label="/\\ door = \"closed\"\n/\\ locked = TRUE",tooltip="..."];
202 -> 101 [label="Close",color="4",fontcolor="4"];
{rank = same; 101;}
{rank = same; 202;}
}
subgraph cluster_legend { ... }
}
```

※ ノード ID は本来 19 桁前後のフィンガープリントですが、読みやすさのため短い数字に置き換えています。`tooltip` と凡例（`cluster_legend`）の中身は省略しているので、このままでは `dot` に通せません。

読み方のポイントは次のとおりです。

- **ノード行**（`101 [label=...]`）: `label` にその状態での変数の値が `/\ 変数 = 値` の形で入ります
- **`style = filled` のノードは初期状態**です。画像にすると灰色に塗られます
- **エッジ行**（`101 -> 202`）: 状態間の遷移です。`actionlabels` を付けると `label` にアクション名が、`colorize` を付けると `color` に配色番号が入ります。配色番号はアクションが初めて現れた順に 2 から振られます
- **`{rank = same; ...}`**: 初期状態からの深さ（何手目で到達したか）が同じノードを同じ段にそろえる指定です。遷移元になったノードだけが登録されるので、出ていく矢印のない `303` は含まれません

これを画像にしたものが次の図です。

![TLC が出力した Door 仕様の状態グラフ。初期状態「door が closed で locked が FALSE」から、Open で「door が open」へ、Lock で「locked が TRUE」へ遷移し、open の状態からは Close で初期状態に戻る。locked が TRUE の状態からは出ていく矢印がない](/blogs/images/tlc-dot-state-graph-door.png)

`locked = TRUE` の状態から出ていく矢印が 1 本もありません。これが**デッドロック**です。`-deadlock` を付けなければ、TLC はこの状態でデッドロックを報告して検査を止めます。今回は検査をオフにしたので探索が最後まで進み、行き止まりの状態がグラフに残りました。図にすると「どの状態が行き止まりか」「そこへ至る経路は何か」がひと目でわかります。鍵を開ける `Unlock` アクションを `Next` に足せば、この状態から初期状態へ戻る矢印が増えます。

## Graphviz で .dot を PNG / SVG / PDF に変換する

`.dot` ファイルはテキストなので、表示するには描画ツールが必要です。

### Graphviz のコマンドを使う

Graphviz をインストールしていれば、`dot` コマンドで変換できます（macOS なら `brew install graphviz`）。

```bash
dot -Tpng Door.dot -o Door.png
dot -Tsvg Door.dot -o Door.svg
dot -Tpdf Door.dot -o Door.pdf
```

SVG で出力すると、ノードにマウスを重ねたときに `tooltip` の内容（その状態の変数の値）が表示されます。状態が増えてラベルが読みにくいときに便利です。

### ブラウザのオンラインツールを使う

インストールせずに試したいなら、「Graphviz Online」などのブラウザ上の描画ツールに `.dot` ファイルの中身を貼り付けるだけで図になります。ただし、仕様の変数の値がそのまま入っているので、業務の仕様を外部サイトに貼るときは中身に注意してください。

### VS Code の拡張機能を使う

「Graphviz Interactive Preview」などの拡張機能を入れると、エディタの中でプレビューできます。拡大縮小やノードの強調ができるので、ある程度大きなグラフでも追いやすくなります。

## ツールの入力として使う — 状態グラフをプログラムで読む

`.dot` は人が画像にして眺めるだけのものではありません。**TLC が到達したすべての状態と遷移を、プログラムで読める形で取り出す手段**でもあります。TLC の標準出力には状態数や反例は出ますが、状態空間の全体は出ません。全体が要るツールは `-dump dot` の出力を読みます。

### 例: 状態遷移図をモデルからレンダリングする

筆者がメンテナンスしている spec-loop（Claude Code のプラグイン）の `formal-statechart.py` は、TLC のモデルを利用者の言葉の状態遷移図（Mermaid）にするスクリプトです。

1. モデルを `-continue -dump dot,actionlabels` を足して走らせる
2. `.dot` のノード（状態）とエッジ（遷移とアクション名）を読む
3. 別に用意した対応表で、変数の値やアクション名を利用者の言葉に置き換える
4. 反例の最後の状態に印を付け、Mermaid の `stateDiagram-v2` として出力する

### なぜ spec-loop は .dot を作るのか

一言でいえば、**利用者が読める状態遷移図を、TLC が検査したとおりに作るため**です。spec-loop の Formal Checker が見つけた反例は、もともと「どの操作をどの順に呼んだか」というテキストでしか渡せませんでした。それでは利用者は、どの状態から、どの操作で規則を破る状態に行くのかを、図で見て判断できません。

そこで図を作るのですが、図を LLM に描かせると、仕様を読み違えて状態を描き足したり描き落としたりする恐れがあります。検査したモデルと図がずれていては、図を見て判断する意味がありません。TLC が展開した状態グラフ（`.dot`）から機械的に図を作れば、図に出るのは TLC が実際に到達した状態と遷移だけになります。

`.dot` には、ほかに 2 つの役割があります。

- **言葉の当て漏れを見つける**: 対応表がすべての状態とアクションに利用者の言葉を当てているかを、`.dot` の全ノード・全エッジと突き合わせて確かめる。当たらないものがあれば図を作らずに止まる
- **規則を破る状態に印を付ける**: `-continue` で違反のあとも探索を続け、違反したすべての状態を図の上で見分けられるようにする

反例のテキストだけでは状態空間の一部しか見えず、全体を取り出せるのは `-dump dot` だけです。だから spec-loop は、人が見るためではなく図を作るための入力として `.dot` を作っています。

考え方は [形式検証 Skill を作る前に状態遷移をモデルにする](/blogs/posts/2026/11/statechart-before-formal-verification/) で、spec-loop が TLC をどう使っているかは [spec-loop は TLC をどう使っているか](/blogs/posts/2026/11/spec-loop-tlc-formal-checker/) で紹介しています。

### プログラムで読むときのオプション

- **`-continue`**: TLC は既定で最初の不変条件違反で止まります。`-continue` を付けると違反のあとも探索を続けるので、状態グラフが最後まで書かれ、違反したすべての状態が反例として報告されます
- **`-fp 0`**: ノード ID のフィンガープリントは、TLC が実行のたびにランダムに選ぶ多項式で計算されます。そのため、同じモデルでも実行ごとに ID が変わります。2 回の出力を比べたいときは `-fp 0` のように多項式の番号を固定します
- **小さなモデルに限る**: 人が見る場合と同じく、状態数が多いとファイルが巨大になります。spec-loop では遷移が一定の本数を超えると反例までの経路だけを描き、探索が途中で止まったときは図に「全体ではない」と書きます

```bash
java -cp tla2tools.jar tlc2.TLC -fp 0 -continue -dump dot,actionlabels Door.dot Door.tla
```

## -dump dot を使う場面と使わない場面

### 必要なときだけオンにする

`.dot` の出力は既定でオフです。CLI では `-dump dot` を付けない限り作られず、Toolbox の設定も既定ではチェックが入っていません。**要らないなら最初から作らない**のが基本です。

出力をオンにしてもオフにしても、検査の結果は変わりません。`-dump` は探索中に見つけた状態を別のファイルにも書き出すだけで、探索の範囲や判定には関わらないからです。不変条件違反やデッドロックの反例も、オフのままで TLC の出力に表示されます。オフにして失うのは、状態グラフ全体の図だけです。

`.dot` が役に立つのは、状態数が数十〜数百程度の小さなモデルです。

- 仕様を書き始めたばかりで、遷移の形が意図どおりかを目で確かめたいとき
- TLA+ を学んでいて、仕様と状態空間の対応を見たいとき
- 小さな定数でデッドロックや想定外のループの位置を探したいとき
- 状態グラフ全体をツールの入力にしたいとき（前節）

### 大きなモデルでオンにしたままにしない

`-dump dot` は**到達したすべての状態と遷移**を書き出します。状態数が数千を超えるモデルでは `.dot` ファイルが巨大になり、Graphviz の描画が終わらなかったり、ビューアが固まったりします。検査そのものもファイル書き込みのぶん遅くなり、ディスクも消費します。

小さなモデルで試したあと、オンにしたまま定数を大きくしてしまうのがよくある失敗です。その場合は次のように外します。

- **TLA+ Toolbox**: 「TLC Options」ページの Features セクションにある **「Visualize state graph after completion of model checking」** のチェックを外す
- **CLI / TLA+ の VS Code 拡張機能**: TLC に渡すオプションから `-dump dot ...` を外す

### 反例（エラートレース）だけを図にする: -dumpTrace dot

全体の状態グラフではなく、**不変条件違反などの反例だけを図にしたい**なら、`-dumpTrace dot <ファイル>` が使えます。違反が起きたときだけ、その経路を DOT 形式で書き出します。ただし `dot` 形式の `-dumpTrace` は [CommunityModules](https://github.com/tlaplus/CommunityModules) がクラスパスに必要です。

```bash
java -cp tla2tools.jar:CommunityModules-deps.jar tlc2.TLC -dumpTrace dot Door_trace.dot Door.tla
```

クラスパスの区切り `:` は macOS / Linux の書き方で、Windows では `;` を使います。

状態数を減らす工夫（`SYMMETRY` や `CONSTRAINT` など）は [TLA+ のモデル検査器 TLC を速くする](/blogs/posts/2026/11/tla-plus-tlc-performance-tuning/) にまとめています。まず小さな定数で検査して状態グラフを眺めます。仕様の形が見えてから定数を大きくすると、`.dot` 出力が最も役に立ちます。

## まとめ

- TLC の `.dot` ファイルは、探索した状態（ノード）と遷移（エッジ）を Graphviz の DOT 言語で書いた状態グラフ
- `-dump dot,colorize,actionlabels <ファイル>` でアクションごとの色分けとラベル付きで出力できる
- 初期状態は塗りつぶしで描かれ、出ていく矢印のないノードがデッドロックの状態
- `dot -Tpng` / `-Tsvg` で画像に変換。SVG ならツールチップで状態の値を確認できる
- 状態空間の全体をプログラムで読む入力にもなる。`-continue` で違反後も探索を続け、`-fp 0` でノード ID を固定する
- 出力は既定でオフ。検査の結果には影響しないので、小さなモデルで必要なときだけオンにする
- 大きなモデルでは使わず、反例だけを図にしたいときは `-dumpTrace dot` を使う
