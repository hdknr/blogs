---
title: "BDD・Gherkin・Cucumber の違いとは？ キーワード一覧と日本語での書き方入門"
date: 2026-11-13
lastmod: 2026-11-13
slug: "gherkin-bdd-cucumber"
draft: false
categories: ["ツール/開発環境"]
tags: ["Gherkin", "BDD", "Cucumber", "テスト自動化", "仕様駆動開発"]
---

**Gherkin（ガーキン）** は、ソフトウェアの振る舞いを `Given`（前提）/ `When`（操作）/ `Then`（結果）の形で書くための記法です。**BDD（Behaviour-Driven Development：振る舞い駆動開発）** の考え方から生まれました。**Cucumber** というツールを使うと、Gherkin で書いたシナリオをそのまま自動テストとして実行できます。

```gherkin
Feature: ログイン試行の制限
  Scenario: パスワードを 5 回連続で間違えるとロックされる
    Given アカウント "alice" がロックされていない
    When 誤ったパスワードで 5 回連続ログインを試みる
    Then アカウント "alice" は 15 分間ロックされる
```

この記事では、3 つの言葉の関係を整理したうえで、Gherkin のキーワード、日本語で書く方法、Cucumber のステップ定義の基本、AI 駆動開発で使うときのポイントをまとめます。

関連する記事とページです。

- 要件を書く記法 EARS：[EARS 記法とは？ 6 つのパターンと日本語での書き方・Kiro での使い方](/blogs/posts/2026/11/ears-requirements-syntax/)
- 金融システムでの BDD の効用：[金融系システムで BDD が効く理由──Gherkin 構文で仕様とテストを一致させる開発手法](/blogs/posts/2026/07/financial-system-bdd-gherkin/)
- Wiki：[BDD と Gherkin 構文](/blogs/wiki/concepts/bdd-gherkin/)

## BDD・Gherkin・Cucumber の関係

3 つは層が違います。

| 名前 | 何か | 役割 |
| --- | --- | --- |
| BDD | 開発手法 | 振る舞いを具体例で合意し、それをテストにする進め方 |
| Gherkin | 記法 | 具体例（シナリオ）を、人にも機械にも読める形で書く |
| Cucumber | ツール | Gherkin のシナリオをコードに結びつけて実行する |

BDD を実践するのに Cucumber が必須なわけではありません。ただ、Gherkin と Cucumber は BDD の実装としてもっとも広く知られた組み合わせです。

## BDD の成り立ちと Given / When / Then の起源

BDD は Dan North 氏が提唱した考え方です。原典の記事「[Introducing BDD](https://dannorth.net/blog/introducing-bdd/)」は 2006 年 3 月に Better Software 誌に掲載されました。

出発点は、TDD（テスト駆動開発）を教える中で感じた「テスト」という言葉の弊害でした。何をテストすればよいのか、どこまで書けばよいのかで迷う人が多かったため、North 氏は「テスト」の代わりに **「振る舞い（behaviour）」** という言葉を使い始めます。記事の発表に先立つ 2003 年の終わりには、テストの語彙を振る舞いの語彙に置き換えたフレームワーク JBehave の開発に着手していました。

Given / When / Then の型も、この流れで生まれています。North 氏と Chris Matts 氏が、ストーリーの受け入れ基準を書くためのテンプレートとして考えたものです。

- **Given**：ある初期状態があるとき
- **When**：あるイベントが起きたら
- **Then**：ある結果になることを確かめる

### BDD の 3 つの実践

Cucumber の公式ドキュメント（[Behaviour-Driven Development](https://cucumber.io/docs/bdd/)）は、BDD を次の 3 つの実践に分けています。

| 実践 | 問い | 内容 |
| --- | --- | --- |
| Discovery（発見） | 何ができうるか | 実例を中心にした対話（ディスカバリーワークショップ）で、振る舞いを掘り下げる |
| Formulation（定式化） | 何をすべきか | 見つけた実例を、人にも機械にも読める文書にする（ここで Gherkin を使う） |
| Automation（自動化） | 実際に何をするか | 文書をシステムに結びつけてテストとして実行する（ここで Cucumber を使う） |

Gherkin を書くこと自体は 2 番目の段階にすぎません。BDD の価値の多くは、その前の対話で合意を作ることにあります。

## Gherkin のキーワード一覧

公式のリファレンス（[Gherkin Reference](https://cucumber.io/docs/gherkin/reference/)）に沿って、キーワードを整理します。

### 主要なキーワード

| キーワード | 意味 |
| --- | --- |
| `Feature` | 機能の説明。`.feature` ファイルの最初のキーワードは必ず `Feature` で、1 ファイルに 1 つ |
| `Rule` | 1 つの業務ルールと、それを表すシナリオをまとめる（Gherkin 6 から） |
| `Example` / `Scenario` | 具体例 1 つ。`Scenario` は `Example` の別名 |
| `Given` / `When` / `Then` | 前提・操作・結果のステップ |
| `And` / `But` / `*` | 直前と同じ種類のステップを続ける |
| `Background` | `Feature` か `Rule` の中の、すべてのシナリオの前に実行する共通の前提 |
| `Scenario Outline` / `Scenario Template` | 同じシナリオを、値を変えて繰り返す |
| `Examples` / `Scenarios` | `Scenario Outline` に渡す値の表 |

### 補助的な記法

| 記法 | 意味 |
| --- | --- |
| `"""`（または ```` ``` ````） | 複数行の文字列（Doc String）をステップに渡す |
| `\|` | 表（Data Table）をステップに渡す |
| `@` | タグ。シナリオを分類し、実行する対象を絞り込む |
| `#` | コメント。行の先頭にだけ書ける |

### まとめて使った例

```gherkin
@auth
Feature: ログイン試行の制限
  パスワードを続けて間違えたアカウントを一時的にロックし、総当たり攻撃を防ぐ。

  Background:
    Given アカウント "alice" が登録されている
    And アカウント "alice" がロックされていない

  Rule: 5 回連続で間違えるとロックする

    Scenario: 5 回目の失敗でロックされる
      When 誤ったパスワードで 5 回連続ログインを試みる
      Then アカウント "alice" は 15 分間ロックされる
      But 管理者には通知されない

    Scenario Outline: 失敗が 5 回未満ならロックされない
      When 誤ったパスワードで <回数> 回連続ログインを試みる
      Then アカウント "alice" はロックされていない

      Examples:
        | 回数 |
        | 1    |
        | 4    |
```

`Background` の 2 つのステップは、各シナリオの前に毎回実行されます。`Scenario Outline` の `<回数>` は、`Examples` の表の行ごとに置き換えられて、シナリオが 2 回実行されます。

### ステップのキーワードは照合に使われない

Cucumber がステップに対応するコード（ステップ定義）を探すとき、`Given` / `When` / `Then` / `And` / `But` のキーワードは照合に使われません。`Given ログイン画面を開く` と `When ログイン画面を開く` は、同じステップ定義に結びつきます。キーワードは、読む人のために前提・操作・結果を区別する役割を持っています。

## 日本語で Gherkin を書く

### `# language: ja` でキーワードを日本語にする

Gherkin は多くの言語に対応しています。ファイルの先頭に `# language: ja` と書くと、キーワードを日本語で書けます（書かなければ英語として扱われます）。

日本語のキーワードは、Cucumber の [gherkin-languages.json](https://github.com/cucumber/gherkin/blob/main/gherkin-languages.json) で次のように定義されています。

| 英語 | 日本語 |
| --- | --- |
| Feature | フィーチャ、機能 |
| Rule | ルール |
| Background | 背景 |
| Scenario | シナリオ |
| Scenario Outline | シナリオアウトライン、シナリオテンプレート、テンプレ、シナリオテンプレ |
| Examples | 例、サンプル |
| Given | 前提 |
| When | もし |
| Then | ならば |
| And | かつ、且つ |
| But | しかし、但し、ただし、然し |

冒頭の例を日本語のキーワードで書くと、次のようになります。

```gherkin
# language: ja
機能: ログイン試行の制限

  シナリオ: パスワードを 5 回連続で間違えるとロックされる
    前提 アカウント "alice" がロックされていない
    もし 誤ったパスワードで 5 回連続ログインを試みる
    ならば アカウント "alice" は 15 分間ロックされる
```

キーワードまで日本語にすると、業務の担当者も読みやすくなります。一方で、英語のキーワードのほうが Given / When / Then の区別が目に入りやすい、という見方もあります。チームでどちらかに決めておくとよいでしょう。

## Cucumber でシナリオを実行する

### 公式・準公式の実装

Cucumber は言語ごとに実装があります。[インストールのページ](https://cucumber.io/docs/installation/)では、次のように分類されています（抜粋）。

| 区分 | 実装 |
| --- | --- |
| 公式 | Cucumber-JVM（Java・Kotlin）、Cucumber-JS（JavaScript）、Cucumber-Ruby、Cucumber-Scala、Cucumber.cpp（C++）、Android |
| 準公式 | behave・pytest-bdd（Python）、Behat（PHP）、Reqnroll（.NET）、gocuke（Go）ほか |

Python で Gherkin を使う場合は、準公式の behave か pytest-bdd を選ぶことになります。pytest-bdd は Gherkin の一部の機能を実装したもので、pytest の仕組みの上で動きます。

### プロジェクトの構成と実行

Cucumber-JS の場合、パッケージを入れて、`features/` の下にシナリオとステップ定義を置きます。

```bash
npm install --save-dev @cucumber/cucumber
```

```text
features/
├── login.feature                  # シナリオ（Gherkin）
└── step_definitions/
    └── login.steps.js             # ステップ定義（JavaScript）
```

既定では `features/` の下の `.feature` ファイルとステップ定義が読み込まれるので、次のコマンドで実行できます。

```bash
npx cucumber-js
```

### ステップ定義と Cucumber Expressions

シナリオの各ステップは、**ステップ定義** と呼ばれるコードに結びつけて実行します。冒頭のシナリオのステップ定義を Cucumber-JS で書くと、次のようになります。

```javascript
const { Given, When, Then } = require("@cucumber/cucumber");
const assert = require("node:assert");

Given("アカウント {string} がロックされていない", function (name) {
  this.account = this.accounts.unlock(name);
});

When("誤ったパスワードで {int} 回連続ログインを試みる", function (count) {
  for (let i = 0; i < count; i++) {
    this.auth.login(this.account.name, "wrong-password");
  }
});

Then("アカウント {string} は {int} 分間ロックされる", function (name, minutes) {
  const account = this.accounts.find(name);
  assert.strictEqual(account.lockedForMinutes(), minutes);
});
```

`this.accounts` や `this.auth` は、テスト用に用意したオブジェクトを指す仮の名前です。実際には、Cucumber の World（シナリオごとに作られる共有のコンテキスト）にテスト対象のクライアントを持たせて使います。World を `this` で参照するため、ステップ定義はアロー関数ではなく `function` で書きます。

`{string}` や `{int}` は **Cucumber Expressions** のパラメーター型です。Cucumber Expressions は、正規表現より直感的に書ける照合の記法で、主な組み込み型は次のとおりです。

| 型 | 一致するもの |
| --- | --- |
| `{int}` | 整数（`71`、`-19` など） |
| `{float}` | 小数（`3.6`、`.8`、`1.5E+3` など） |
| `{word}` | 空白を含まない語（`banana` など） |
| `{string}` | 一重引用符か二重引用符で囲んだ文字列。値は引用符を外して渡される |
| `{}` | 何にでも一致する |

正規表現も使えますが、1 つの式の中で Cucumber Expressions と正規表現の書き方を混ぜることはできません。

## Gherkin で良いシナリオを書くコツ（宣言的に書く）

公式リファレンスには、シナリオの書き方についての指針もいくつか書かれています。

- **1 つのシナリオは 3〜5 ステップ** を目安にする。長くなるなら、シナリオが複数の振る舞いを確かめていないかを見直す
- **`Background` が 4 行を超えたら**、関係の薄い詳細を、より高い水準のステップにまとめることを検討する
- **`Given` では利用者の操作を語らない**。`Given` は前提となる状態を置くもので、操作は `When` で書く
- **実装の詳細はステップ定義に隠す**。シナリオには、画面の部品やクリックの手順ではなく、業務の言葉で振る舞いを書く

最後の点は、「宣言的に書く」とも言われます。次の 2 つを比べると違いが分かります。

```gherkin
# 手順を書いている（UI が変わるたびにシナリオを直すことになる）
When ID 欄に "alice" と入力する
And パスワード欄に "wrong" と入力する
And ログインボタンを押す
```

```gherkin
# 振る舞いを書いている（UI が変わってもシナリオは変わらない）
When "alice" が誤ったパスワードでログインを試みる
```

## AI 駆動開発で Gherkin を使うときのポイント

### 要件は EARS、受け入れテストは Gherkin

AI コーディングエージェントに仕様を渡す開発では、仕様駆動開発（SDD）の進め方がよく使われます。SDD では、要件を EARS で書き、受け入れテストを Gherkin で書く分担がやりやすい方法です。両者は次のように対応させられます（筆者の整理です）。

| EARS | Gherkin |
| --- | --- |
| `While`〈事前条件〉 | `Given` |
| `When` / `If`〈トリガー〉 | `When` |
| `shall`〈応答〉 | `Then` |

EARS の `If` は異常系のトリガーです。Gherkin にすると同じ `When` になるので、異常系のシナリオだと分かる名前を `Scenario` に付けておくと、正常系と区別しやすくなります。SDD の全体像は「[仕様駆動開発（SDD）とは？ 3 つのアプローチ・EARS 記法・Kiro / Spec Kit・TDD との違い](/blogs/posts/2026/11/spec-driven-development-overview/)」を参照してください。

### シナリオは人間が書くかレビューし、ステップ定義は AI に任せる

Gherkin のシナリオは「何が正しいか」を決めるものです。AI に書かせる場合も、シナリオは人間がレビューして合意してから固定します。ステップ定義と実装はその後で AI に任せます。

シナリオとステップ定義の両方を AI が同時に書くと、テストが実装に合わせて書かれてしまいます。そうなると、テストは仕様を確かめる役割を果たせません。

### 先に失敗（赤）することを確かめる

テストが失敗する状態を赤、成功する状態を緑と呼びます。ステップ定義を書いた直後、実装の前にシナリオを実行し、**赤になることを確かめます**。Cucumber の公式ドキュメントも、自動化の段階では「振る舞いをまだ実装していないのでテストは失敗する」状態から始めると説明しています。最初から緑になるシナリオは、何も確かめていない可能性があります。

## まとめ

- BDD は開発手法、Gherkin は記法、Cucumber はそれを実行するツールで、層が違う
- BDD は Dan North 氏が提唱し、Given / When / Then は North 氏と Chris Matts 氏が受け入れ基準のテンプレートとして考えた
- Gherkin を書くのは BDD の一段階にすぎず、価値の中心はその前の対話（Discovery）にある
- Gherkin の主なキーワードは `Feature`・`Rule`・`Scenario`・`Given` / `When` / `Then`・`Background`・`Scenario Outline` / `Examples`
- `# language: ja` で、`機能`・`シナリオ`・`前提`・`もし`・`ならば` などの日本語キーワードが使える
- Cucumber はステップを Cucumber Expressions でステップ定義に結びつけて実行する
- シナリオは 3〜5 ステップを目安に、手順ではなく振る舞いを宣言的に書く
- AI 駆動開発では、シナリオを人間が固定し、赤になることを確かめてから AI に実装させる
