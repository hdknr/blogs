---
title: "BDD と Gherkin 構文"
description: "振る舞い駆動開発と Gherkin による「仕様の共通言語化」。BDD の起源と 3 つの実践、Gherkin のキーワード・日本語での書き方、Cucumber Expressions、宣言的なシナリオの書き方、金融システムや AI 駆動開発で効く理由"
date: 2026-07-28
lastmod: 2026-11-15
aliases: ["BDD", "振る舞い駆動開発", "Gherkin", "ガーキン", "Cucumber", "SpecFlow", "Reqnroll", "Three Amigos", "動く仕様書", "Given When Then", "Cucumber Expressions", "Scenario Outline", "ステップ定義"]
related_posts:
  - "/posts/2026/07/financial-system-bdd-gherkin/"
  - "/posts/2026/11/gherkin-bdd-cucumber/"
  - "/posts/2026/11/ears-requirements-syntax/"
tags: ["BDD", "Gherkin", "Cucumber", "テスト自動化", "金融システム", "仕様駆動開発"]
---

## 概要

BDD（Behavior-Driven Development：振る舞い駆動開発）は、単なるテスト手法ではなく **「ビジネスの要求を、そのまま自動テストのコードに直結させる仕組み」**として運用される。中核にあるのは自然言語に近い **Gherkin（ガーキン）構文**で、ビジネス部門と開発エンジニアの間の認識のズレを解消する共通言語として機能する。

3 つの言葉は層が違う。**BDD** は振る舞いを具体例で合意してテストにする開発手法、**Gherkin** はその具体例を人にも機械にも読める形で書く記法、**Cucumber** はシナリオをコードに結びつけて実行するツールである。BDD に Cucumber が必須なわけではないが、Gherkin と Cucumber がもっとも広く知られた組み合わせ。

## 起源と 3 つの実践

BDD は Dan North 氏が提唱し、原典「Introducing BDD」は 2006 年 3 月に Better Software 誌に載った。TDD を教える中で「テスト」という言葉が何をどこまで書くかの迷いを生むと感じ、「振る舞い（behaviour）」に言い換えたのが出発点で、2003 年末にはテストの語彙を置き換えたフレームワーク JBehave に着手していた。Given / When / Then は North 氏と Chris Matts 氏がストーリーの受け入れ基準のテンプレートとして考えた。

Cucumber の公式ドキュメントは BDD を 3 つの実践に分ける。

| 実践 | 問い | 内容 |
|---|---|---|
| Discovery（発見） | 何ができうるか | 実例を中心にした対話で振る舞いを掘り下げる |
| Formulation（定式化） | 何をすべきか | 実例を Gherkin で文書にする |
| Automation（自動化） | 実際に何をするか | 文書をシステムに結びつけてテストとして実行する（Cucumber） |

Gherkin を書くのは 2 番目の段階にすぎず、**価値の多くはその前の対話で合意を作ること**にある。

## Gherkin 構文

主に 3 つのキーワードで構成される。

- **Given（前提）** — テストを実行する前の状態
- **When（もし〜のとき）** — 発生させるアクション
- **Then（ならば〜となる）** — 期待される結果

```gherkin
フィーチャ: 口座振替による出金処理

  シナリオ: 残高が十分にある場合の正常な出金
    前提   ユーザーAの口座残高が 50,000円 である
    かつ   その口座は「アクティブ（有効）」である
    もし   ユーザーAが 30,000円 の出金をリクエストした
    ならば 出金処理が成功すること
    かつ   ユーザーAの口座残高が 20,000円 になっていること

  シナリオ: 残高不足によるエラー判定
    前提   ユーザーAの口座残高が 10,000円 である
    もし   ユーザーAが 30,000円 の出金をリクエストした
    ならば 出金処理が「残高不足エラー」で拒否されること
    かつ   ユーザーAの口座残高は 10,000円 のままであること
```

### キーワード

| キーワード | 意味 |
|---|---|
| `Feature` | 機能の説明。`.feature` ファイルの最初に 1 つ |
| `Rule` | 1 つの業務ルールとそのシナリオをまとめる（Gherkin 6 から） |
| `Scenario` / `Example` | 具体例 1 つ（同義） |
| `And` / `But` / `*` | 直前と同じ種類のステップを続ける |
| `Background` | `Feature` か `Rule` 内の全シナリオの前に実行する共通の前提 |
| `Scenario Outline` + `Examples` | 同じシナリオを表の値を変えて繰り返す（`<回数>` が行ごとに置き換わる） |

ほかに Doc String（`"""`）、Data Table（`|`）、タグ（`@`）、行頭コメント（`#`）がある。Cucumber がステップ定義を探すとき **Given / When / Then のキーワードは照合に使われない**（`Given ログイン画面を開く` と `When ログイン画面を開く` は同じ定義に結びつく）。キーワードは読む人のためのもの。

### 日本語で書く

ファイル先頭に `# language: ja` と書くと日本語キーワードが使える（`gherkin-languages.json` の定義）。Feature＝フィーチャ／機能、Rule＝ルール、Background＝背景、Scenario＝シナリオ、Scenario Outline＝シナリオアウトライン／シナリオテンプレート、Examples＝例／サンプル、Given＝前提、When＝もし、Then＝ならば、And＝かつ、But＝しかし／ただし。日本語なら非エンジニアの業務担当者も仕様の正しさを確認しやすいが、英語のほうが Given / When / Then の区別が目に入りやすいという見方もあるので、チームでどちらかに決める。

### 良いシナリオを書くコツ

- 1 シナリオは **3〜5 ステップ**が目安。長いなら複数の振る舞いを確かめていないか見直す
- `Background` が 4 行を超えたら、より高い水準のステップにまとめる
- `Given` では利用者の操作を語らない（状態を置くだけで、操作は `When`）
- **宣言的に書く**：「ID 欄に入力 → パスワード欄に入力 → ボタンを押す」ではなく「"alice" が誤ったパスワードでログインを試みる」。実装の詳細はステップ定義に隠せば、UI が変わってもシナリオは変わらない

## 開発フロー

フレームワークは **Cucumber**。公式実装は Cucumber-JVM・Cucumber-JS・Cucumber-Ruby・Cucumber-Scala・Cucumber.cpp など、準公式に behave・pytest-bdd（Python）、Behat（PHP）、gocuke（Go）、Reqnroll（.NET。開発終了した **SpecFlow** の後継）がある。Cucumber-JS なら `npm install --save-dev @cucumber/cucumber` で入れ、`features/` にシナリオと `step_definitions/` を置いて `npx cucumber-js` で実行する。

### ① Three Amigos による仕様定義

開発を始める前に「ビジネス担当者（PO）」「開発者」「テスター（QA）」の 3 者が集まり Gherkin でシナリオを確定させる。この場で例外パターンや境界値（残高がちょうど 0 円のときはどうするか等）を徹底的に洗い出す。この 3 者会議を **Three Amigos** と呼ぶ。

### ② 仕様書が自動テストコードに変身する

確定した `.feature` ファイルをツールに読み込ませると、各ステップに対応する**テストコードの枠組み（メソッド）の雛形が自動生成**される。開発者はその中に実際の処理を実装する。この接着剤にあたるコードを **Glue Code** あるいは**ステップ定義（Step Definition）**と呼ぶ。

```ruby
# Cucumber (Ruby) のステップ定義例
前提('ユーザーAの口座残高が {int}円 である') do |balance|
  @account = Account.create!(owner: 'A', balance: balance)
end

もし('ユーザーAが {int}円 の出金をリクエストした') do |amount|
  @result = @account.withdraw(amount)
end

ならば('ユーザーAの口座残高が {int}円 になっていること') do |expected|
  expect(@account.reload.balance).to eq(expected)
end
```

ステップの `{int}`・`{string}` は **Cucumber Expressions** のパラメーター型で、ほかに `{float}`・`{word}`・`{}`（何でも）がある。正規表現より直感的に書けるが、1 つの式の中で正規表現と混ぜることはできない。Cucumber-JS では World（シナリオごとの共有コンテキスト）を `this` で参照するため、ステップ定義はアロー関数ではなく `function` で書く。

### ③ Red → Green と回帰テストの自動化

最初は未実装なのでテストは Red（失敗）になる。ここが起点。本番コードを実装して Green になれば開発完了。このシナリオはそのまま**仕様書であり、同時にいつでも実行できる自動テスト（回帰テスト）**としてシステムに残り続ける。

## 金融システムで効く理由

金融システムは「複雑な業務ルール」「極めて高い品質要求」「絶対に失敗できない決済処理」という特徴を持つため、BDD の仕組みが噛み合う。

- **「動く仕様書」になりドキュメントの陳腐化を防げる** — 仕様とテストが同一物なので乖離しない
- **ビジネス部門との認識ズレを構造的に減らせる** — 非エンジニアがレビューできる形式で仕様が残る
- **境界値・例外パターンを事前に洗い出す文化が作られる** — Three Amigos が設計段階で強制する

## AI 駆動開発で使うとき

[仕様駆動開発](/blogs/wiki/concepts/spec-driven-development/) では、**要件は [EARS](/blogs/wiki/concepts/ears/)、受け入れテストは Gherkin** という分担がやりやすい。EARS の While・Where は `Given`、When・If は `When`、shall は `Then` に対応する。異常系の If も Gherkin では `When` になるので、異常系と分かる名前を `Scenario` に付ける。

- **シナリオは人間が書くかレビューして固定し、ステップ定義と実装は AI に任せる**。両方を AI が同時に書くとテストが実装に合わせて書かれ、仕様を確かめる役割を果たさない
- **実装の前に赤になることを確かめる**。最初から緑のシナリオは何も確かめていない可能性がある

## 関連ページ

- [pytest によるカオスエンジニアリング](/blogs/wiki/guides/pytest-chaos-engineering/) — 障害注入によるテスト
- [自動テスト修正パイプライン](/blogs/wiki/guides/auto-test-fix-pipeline/) — テストを軸にした自律修正
- [計画と実装を分ける承認ゲート設計](/blogs/wiki/concepts/orchestrator-coder-split/) — テストをゲートとして使う設計
- [EARS 記法](/blogs/wiki/concepts/ears/) — Gherkin のシナリオに書き換えられる要件の記法
- [仕様駆動開発（SDD）](/blogs/wiki/concepts/spec-driven-development/) — EARS と Gherkin を使い分ける開発手法
- [要求仕様書作成ループ](/blogs/wiki/concepts/requirements-spec-loop/) — 日本語 Gherkin を利用者との合意とテスト生成の元にする
- [形式手法](/blogs/wiki/concepts/formal-methods/) — 仕様の厳密化という別アプローチ

## ソース記事

- [金融系システムで BDD が効く理由──Gherkin 構文で仕様とテストを一致させる開発手法](/blogs/posts/2026/07/financial-system-bdd-gherkin/) — 2026-07-17
- [BDD・Gherkin・Cucumber の違いとは？ キーワード一覧と日本語での書き方入門](/blogs/posts/2026/11/gherkin-bdd-cucumber/) — 2026-11-13
- [EARS 記法とは？ 6 つのパターンと日本語での書き方・Kiro での使い方](/blogs/posts/2026/11/ears-requirements-syntax/) — 2026-11-13
