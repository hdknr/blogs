---
title: "Quint"
description: "TLA+ と同じ論理に、型付きでプログラマ向けの構文を載せた形式仕様記述言語。型検査・REPL・テストで書きながら間違いを潰し、ランダムシミュレータ・Apalache（記号的・有界）・TLC（明示的・全探索）を同じ仕様に使い分けられる"
date: 2026-11-09
lastmod: 2026-11-09
aliases: ["Quint", "quint", "Apalache", "quint verify", "quint run", "Informal Systems", "@informalsystems/quint", "ITF"]
related_posts:
  - "/posts/2026/11/quint-formal-specification-language/"
tags: ["Quint", "TLA+", "形式手法", "モデル検査", "Apalache"]
---

## 概要

Quint は、分散システムや並行プロトコルの設計を書いて検査する形式仕様記述言語。Informal Systems が開発を始め、GitHub のリポジトリは現在 [quint-co/quint](https://github.com/quint-co/quint) にある。論理の土台は [TLA+](/blogs/wiki/tools/tla-plus/) と同じで、構文は TypeScript や Rust に近く、型検査・REPL・テストが最初から付いてくる。「TLA+ の考え方はそのままに、プログラマが書きやすい形にしたもの」と捉えるとわかりやすい。

TLC が TLA+ の**検査器**であるのに対し、Quint は**言語とツール群**の名前で、検査器としてランダムシミュレータ・Apalache・TLC を使い分ける。

## 詳細

### インストール

npm で配布されている（パッケージ名 `@informalsystems/quint`）。

```bash
npm install -g @informalsystems/quint
```

型検査・テスト・`quint run` は Node.js だけで動く。`quint verify`（Apalache）と `--backend=tlc`（Apalache と TLC）は Java の実行環境が必要で、本体は初回実行時に自動でダウンロードされる。Apalache はカレントディレクトリに `_apalache-out/` を作るので、リポジトリ内で使うなら `.gitignore` に入れる。

### TLA+ との書き方の対応

| TLA+ | Quint | 意味 |
|---|---|---|
| `/\ A /\ B` | `all { A, B }` | すべて成り立つ |
| `\/ A \/ B` | `any { A, B }` | どれか 1 つが起きる |
| `\E b \in Buyers : ...` | `nondet b = oneOf(BUYERS) ...` | 非決定的に 1 つ選ぶ |
| `[pc EXCEPT ![b] = "done"]` | `pc.set(b, Done)` | 写像の 1 か所を書き換える |
| `pc[b]` | `pc.get(b)` | 写像の値を引く |
| `UNCHANGED vars` | `stock' = stock, pc' = pc` | 変数を変えない |
| `.cfg` の `CONSTANTS` | `import stock(BUYERS = ...)` | 定数に値を与える |

プライム付きで次の状態を書く点は TLA+ と同じ。状態を `type Phase = Check | Buy | Done` のような直和型で定義できるので、`"chek"` のような綴り間違いは型検査で弾かれる。検査条件は `.cfg` の別ファイルではなく、定数を与えたモジュール（`module main { import stock(...).* }`）として同じファイルに書ける。

### 書きながらのフィードバック

- `quint typecheck`：型推論つきの静的型検査。整数の変数に文字列を代入すると、行番号つきで `Couldn't unify int and str` を返す。TLA+ は型がないので、この種の間違いは TLC の探索中に初めて出る
- `quint repl`：式をその場で評価する
- `quint test`：`run` 定義に `.then` でつないだ特定の実行順を再現し、`assert` で結果を確かめる。人間が思いついた 1 つの順番だけを確かめるテストで、思いつかない順番を探すのは次の検査器の役目

### 3 つの検査方法

| コマンド | 検査器 | 方式 | 「違反なし」の意味 |
|---|---|---|---|
| `quint run` | ランダムシミュレータ | `--max-samples` 回、最大 `--max-steps` 手の実行を試す | 試した範囲では見つからなかった（網羅ではない） |
| `quint verify` | **Apalache**（既定） | 「N 手以内に破れる実行はあるか」を論理式にし SMT ソルバ Z3 に解かせる記号的な有界モデル検査 | `--max-steps` 以内には 1 つもない |
| `quint verify --backend=tlc` | TLC | 仕様を TLA+ に変換（変換には Apalache を使う）し、到達状態を全列挙 | 上限なしの全探索で違反なし |

- `quint run` の反例は出力末尾の `--seed` を付ければ再現できる
- Apalache は**デッドロックも検出する**（終了後の `done` ステップを外すと `error: reached a deadlock` で止まる）
- 一方、Quint（0.33.1 で確認）は TLC を **`-deadlock` 付きで起動する**ので、TLC 経由ではデッドロックを検査しない。確かめたいときは Apalache を使うか TLC を直接実行する
- TLC の出力では直和型の値が `[Check |-> [tag |-> "UNIT"]]` のように表れ、状態は 1 から数える
- 変換後の TLA+ だけが欲しいときは `quint compile --target=tlaplus`

在庫 1 個を 2 人が同時に買う例では、3 つの検査器すべてが 4 ステップで在庫が -1 になる反例を返し、TLC は TLA+ 版と同じ 10 状態を探索した。確認と減算をアトミックにした版では、TLC が 4 状態を全探索して違反なしと報告した。

### TLA+ / TLC との比較

| 項目 | Quint（Apalache / シミュレータ） | TLA+ と TLC |
|---|---|---|
| 構文 | TypeScript / Rust 風、静的型付き | 数学記号を ASCII で表す。型なし |
| 検査方式 | 記号的（Z3）＋ランダムシミュレーション | 到達状態を 1 つずつ列挙 |
| 大きな値 | 記号のまま扱えるので値の範囲が広くても列挙せずに済む | 状態空間を小さく絞る必要がある |
| 実行の長さ | Apalache は指定ステップ数まで（有界） | 状態空間が有限なら上限なしに網羅 |
| 活性 | Apalache の時相性質の対応は部分的（Quint のドキュメント） | 公平性つきの活性まで検査できる |
| 実績 | 比較的新しい。Cosmos などブロックチェーン・分散プロトコル | 1999 年以来の長い実績。AWS・Azure の事例 |

### どう使い分けるか

- **Quint が向く**：プログラマ中心のチーム。モデルベーステスト（`quint run` と Apalache の `quint verify` は `--out-itf` で反例を ITF〈Informal Trace Format〉の JSON に書き出せ、実装側のテストで同じ手順を再生する素材になる）。整数の範囲が広く明示的な列挙では手に負えない状態空間
- **TLA+ / TLC が向く**：論文・書籍・AWS の事例など TLA+ の資料を参考にしたい。小〜中規模の有限状態を上限なしに全探索したい。公平性つきの活性を検査したい
- **組み合わせる**：書いている間は型検査・`quint test`・`quint run` で素早く潰し、状態空間を小さく絞れる性質は `--backend=tlc` で全探索、値の範囲が広い性質は Apalache で有界に網羅する

どの検査器でも「違反なし」は、何を網羅したか（ランダム試行か、ステップ上限までか、全状態か）と、何を検査しなかったか（TLC 経由ではデッドロックを見ない、など）とセットで読む。

## 関連ページ

- [TLA+ と TLC](/blogs/wiki/tools/tla-plus/) — 論理の土台と、`--backend=tlc` で使うモデル検査器
- [形式手法（Formal Methods）](/blogs/wiki/concepts/formal-methods/) — 問いの形による道具の選び方
- [ミューテーションテスト](/blogs/wiki/concepts/mutation-testing/) — 「違反なし」の空振りを疑う考え方

## ソース記事

- [Quint とは — TLA+ の論理をプログラマ向けの構文で書く形式仕様記述言語と、TLC との使い分け](/blogs/posts/2026/11/quint-formal-specification-language/) — 2026-11-09
