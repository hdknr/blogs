---
title: "EARS 記法とは？ 6 つのパターンと日本語での書き方・Kiro での使い方"
date: 2026-11-13
lastmod: 2026-11-13
slug: "ears-requirements-syntax"
draft: false
categories: ["AI/LLM"]
tags: ["EARS", "要求定義", "仕様駆動開発", "AI駆動開発", "Gherkin"]
---

**EARS（Easy Approach to Requirements Syntax）** は、自然言語で書く要件を、いくつかの決まった型に当てはめて書くための記法です。たとえば次のような形をしています。

```text
When "mute" is selected, the laptop shall suppress all audio output.
```

Kiro が `requirements.md` の受け入れ基準に採用しました。そのため、仕様駆動開発（SDD）の文脈で名前を見かけることが増えています。

この記事では、EARS の成り立ちと 6 つのパターンを、考案者の公式ガイドに沿って整理します。そのうえで、日本語で書くときの工夫と、AI コーディングエージェントに渡す要件として使うときのポイント、Gherkin のテストへのつなげ方をまとめます。

SDD の全体像は「[仕様駆動開発（SDD）とは？ 3 つのアプローチ・EARS 記法・Kiro / Spec Kit・TDD との違い](/blogs/posts/2026/11/spec-driven-development-overview/)」で扱っています。

## EARS の成り立ち

EARS は、Rolls-Royce の Alistair Mavin 氏らが考案した記法です。ジェットエンジン制御システムの耐空性（航空機が安全に飛行できる状態）に関する規則を分析する中で生まれました。論文は 2009 年の国際会議 RE'09（17th IEEE International Requirements Engineering Conference）で発表されています（Mavin, Wilkinson, Harwood, Novak「Easy Approach to Requirements Syntax (EARS)」）。

公式ガイド（[alistairmavin.com/ears](https://alistairmavin.com/ears/)）では、Airbus・Bosch・Dyson・Honeywell・Intel・NASA・Siemens などが利用している組織として挙げられています。特徴として強調されているのは次の点です。

- 自然言語の要件によくある問題を減らせる、あるいはなくせる
- 軽量で、学習の負担が小さく、専用のツールが要らない
- 書いた要件が読みやすい
- 英語を母語としない人が英語で要件を書くときに、特に効果がある

形式手法（数学的な記法で仕様を厳密に書く手法）のように厳密な文法を持つわけではありません。あくまで「自然言語のまま、文の骨組みだけを揃える」記法です。だからこそ、レビューする人も、受け取る AI も、特別な知識なしで読めます。

## EARS の基本構文

どの要件も、次の骨組みから必要な部分だけを取り出した形になります。

```text
While <省略可能な事前条件>, when <省略可能なトリガー>, the <システム名> shall <システムの応答>
```

要素ごとの個数のルールは次のとおりです。

| 要素 | 個数 |
| --- | --- |
| 事前条件（While） | 0 個以上 |
| トリガー（When） | 0 個または 1 個 |
| システム名 | ちょうど 1 個 |
| システムの応答（shall の後） | 1 個以上 |

節の順番はいつも同じで、時間の流れに沿っています。「どんな状態のときに」→「何が起きたら」→「どのシステムが」→「何をするか」の順です。

## EARS の 6 つのパターン（While / When / Where / If-Then）

公式ガイドの定義と例文を、日本語訳とあわせて示します。

### 1. 常時（Ubiquitous）— キーワードなし

条件なしに、常に成り立つ要件です。

```text
The <システム名> shall <システムの応答>
```

> The mobile phone shall have a mass of less than XX grams.
> （携帯電話の質量は XX グラム未満でなければならない）

### 2. 状態駆動（State-driven）— While

ある状態が続いている間、成り立つ要件です。

```text
While <事前条件>, the <システム名> shall <システムの応答>
```

> While there is no card in the ATM, the ATM shall display "insert card to begin".
> （ATM にカードが入っていない間、ATM は「カードを挿入してください」と表示しなければならない）

### 3. イベント駆動（Event-driven）— When

あるイベント（トリガー）が起きたときの応答を定める要件です。ユーザーの操作や外部からの通知など、多くの場面で使います。

```text
When <トリガー>, the <システム名> shall <システムの応答>
```

> When "mute" is selected, the laptop shall suppress all audio output.
> （「ミュート」が選ばれたとき、ノート PC はすべての音声出力を止めなければならない）

### 4. オプション機能（Optional feature）— Where

その機能や構成を持つ製品だけに当てはまる要件です。製品ラインや、プランによって機能が変わるサービスで使います。

```text
Where <機能が含まれる>, the <システム名> shall <システムの応答>
```

> Where the car has a sunroof, the car shall have a sunroof control panel on the driver door.
> （サンルーフを備える車では、運転席のドアにサンルーフの操作パネルがなければならない）

### 5. 望ましくない振る舞い（Unwanted behaviour）— If / Then

エラー、故障、不正な入力など、起きてほしくない状況への応答を定める要件です。

```text
If <トリガー>, then the <システム名> shall <システムの応答>
```

> If an invalid credit card number is entered, then the website shall display "please re-enter credit card details".
> （無効なクレジットカード番号が入力された場合、Web サイトは「カード情報を再入力してください」と表示しなければならない）

正常系の When と、異常系の If / Then を分けて書けるのが、このパターンの大事なところです。キーワードで区別しておけば、異常系の要件がいくつ書かれているかを文面から数えられます。

### 6. 複合（Complex）— While + When など

複数のキーワードを組み合わせた要件です。

```text
While <事前条件>, when <トリガー>, the <システム名> shall <システムの応答>
```

> While the aircraft is on ground, when reverse thrust is commanded, the engine control system shall enable reverse thrust.
> （航空機が地上にある間に逆推力が指令されたとき、エンジン制御システムは逆推力を有効にしなければならない）

異常系を含む複合の要件は、If / Then を使って書きます。

```text
While <事前条件>, if <トリガー>, then the <システム名> shall <システムの応答>
```

## EARS のパターンを選ぶ早見表

| 書きたいこと | パターン | キーワード |
| --- | --- | --- |
| いつでも成り立つ性質・制約 | 常時 | なし |
| ある状態の間だけ成り立つ振る舞い | 状態駆動 | While |
| 何かが起きたときの応答 | イベント駆動 | When |
| 特定の構成・プランにだけある機能 | オプション機能 | Where |
| エラー・故障・不正入力への対処 | 望ましくない振る舞い | If / Then |
| 状態とイベントの組み合わせ | 複合 | While + When など |

## 日本語で書くときの工夫

EARS は英語の文型を前提にしていますが、日本語でも骨組みはそのまま使えます。コツは、キーワードに当たる言い回しを決めておくことです。

| パターン | 日本語の型の例 |
| --- | --- |
| 常時 | 〈システム名〉は〈応答〉しなければならない |
| 状態駆動 | 〈事前条件〉の間、〈システム名〉は〈応答〉しなければならない |
| イベント駆動 | 〈トリガー〉とき、〈システム名〉は〈応答〉しなければならない |
| オプション機能 | 〈機能〉がある場合、〈システム名〉は〈応答〉しなければならない |
| 望ましくない振る舞い | もし〈トリガー〉ならば、〈システム名〉は〈応答〉しなければならない |
| 複合 | 〈事前条件〉の間に〈トリガー〉とき、〈システム名〉は〈応答〉しなければならない |

日本語では「場合」「とき」「ならば」を入れ替えて使いがちです。EARS として書くなら、言い回しをチーム内で固定しましょう。たとえばイベントは「とき」、オプション機能は「場合」、異常系は「もし〜ならば」とすると、文面だけでパターンを判別できます。

Kiro のように、キーワードだけ英語の大文字で残す書き方もあります。

```text
WHEN ユーザーがログアウトボタンを押した THE SYSTEM SHALL セッションを破棄する
```

日本語の文としては自然ではありませんが、パターンが一目で分かり、grep で数えられるという利点があります。

## AI 駆動開発で EARS を使うときのポイント

### Kiro の EARS は簡略版

Kiro のドキュメント（[Feature Specs](https://kiro.dev/docs/specs/feature-specs/)）では、`requirements.md` の要件を次の形で書くと説明されています。

```text
WHEN [condition/event] THE SYSTEM SHALL [expected behavior]
```

Kiro そのものの機能（Spec・Steering・Hooks など）は「[Kiro とは？ AWS の仕様駆動 AI IDE の Spec・Steering・Hooks と料金プラン](/blogs/posts/2026/11/kiro-ai-ide-intro/)」で紹介しています。

示されているのはイベント駆動の形だけで、While・Where・If / Then は出てきません。そのため AI に要件を書かせると、すべてが WHEN の文になりがちです。たとえば「誤ったパスワードを 5 回連続で入力した」は不正入力への対処なので、本来は If / Then で書く異常系です。**状態に依存する要件や異常系が WHEN の中に紛れ込んでいないか** を人間が確かめると、抜けを見つけやすくなります。

### 異常系の If / Then を数える

AI に要件を書かせて最初に見るべきなのは、If / Then の要件の数です。要件を正常系の When だけで書くと、エラー時の振る舞いを AI が実装の段階で黙って決めることになります。

- もし入力の検証に失敗したならば
- もし外部 API がタイムアウトしたならば
- もし権限のないユーザーが操作したならば
- もし同じ操作が二重に送られたならば

こうした場面ごとに If / Then の要件があるかを確かめ、なければ足すよう AI に指示します。

### 1 文 1 応答を守る

「〜し、〜し、さらに〜する」のように応答を詰め込むと、どれが満たされていないのかをテストで判定しにくくなります。公式のルールでは、応答は 1 個以上書いてかまいません。ただし受け入れ基準として使うなら、**1 つの要件に 1 つの検証可能な応答** を目安に分けましょう。そうすれば、テストケースと 1 対 1 で対応させられます。

### 曖昧な形容詞を数値にする

EARS は文の骨組みを揃えますが、「すばやく」「適切に」「十分な」といった言葉の曖昧さまでは取り除きません。公式の例文が「XX グラム未満」と数値で書いているように、応答の中身は測れる値にします。

```text
検索ボタンが押されたとき、検索 API は 95 パーセンタイルで 500 ミリ秒以内に結果を返さなければならない
```

### Gherkin のテストにつなげる

EARS の要件は、Gherkin のシナリオに書き換えられます。対応は次のとおりです。

| EARS | Gherkin |
| --- | --- |
| While〈事前条件〉、Where〈機能〉 | `Given`（前提） |
| When / If〈トリガー〉 | `When`（操作・出来事） |
| shall〈応答〉 | `Then`（結果） |

先ほどの異常系を EARS で書き、Gherkin にすると次のようになります。

```text
もしユーザーが誤ったパスワードを 5 回連続で入力したならば、認証サービスはそのアカウントを 15 分間ロックしなければならない
```

```gherkin
Feature: ログイン試行の制限
  Scenario: パスワードを 5 回連続で間違えるとロックされる
    Given アカウント "alice" がロックされていない
    When 誤ったパスワードで 5 回連続ログインを試みる
    Then アカウント "alice" は 15 分間ロックされる
```

要件は EARS で書いて人間がレビューし、受け入れテストは Gherkin や通常のテストコードで AI に書かせます。この分担にすると、要件からテストまでの対応を追いやすくなります。

## まとめ

- EARS は Rolls-Royce の Alistair Mavin 氏らが 2009 年に発表した、自然言語の要件を決まった型で書く記法
- 骨組みは「While〈事前条件〉, when〈トリガー〉, the〈システム名〉shall〈応答〉」で、節の順番は時間の流れに沿う
- パターンは常時・状態駆動（While）・イベント駆動（When）・オプション機能（Where）・望ましくない振る舞い（If / Then）・複合の 6 つ
- 日本語で書くときは、パターンごとの言い回しをチームで固定する
- Kiro の EARS はイベント駆動の形だけなので、AI に書かせた要件では状態依存と異常系の抜けを確かめる
- 1 文 1 応答と数値化でテストできる要件にし、Gherkin の受け入れテストにつなげる
