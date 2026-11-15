---
title: "EARS 記法"
description: "自然言語の要件を 6 つの決まった型（常時・While・When・Where・If/Then・複合）に当てはめて書く記法。Kiro の requirements.md が採用し、AI に書かせた要件の抜けを見つける型として使える"
date: 2026-11-15
lastmod: 2026-11-15
aliases: ["EARS", "Easy Approach to Requirements Syntax", "THE SYSTEM SHALL", "受け入れ基準の記法"]
related_posts:
  - "/posts/2026/11/ears-requirements-syntax/"
  - "/posts/2026/11/spec-driven-development-overview/"
  - "/posts/2026/11/kiro-ai-ide-intro/"
  - "/posts/2026/11/cc-sdd-intro/"
tags: ["EARS", "要求定義", "仕様駆動開発", "AI駆動開発"]
---

## 概要

**EARS（Easy Approach to Requirements Syntax）** は、自然言語の要件を少数の決まった型に当てはめて書く記法である。Rolls-Royce の Alistair Mavin 氏らがジェットエンジン制御の耐空性規則を分析する中で考案し、2009 年の RE'09 で発表した。Airbus・Bosch・NASA・Siemens などが使っている。

形式手法のような厳密な文法ではなく、**自然言語のまま文の骨組みだけを揃える**のが特徴で、学習の負担が小さく専用ツールも要らない。Kiro が `requirements.md` の受け入れ基準に採用したことで、[仕様駆動開発](/blogs/wiki/concepts/spec-driven-development/) の文脈で広く知られるようになった。

## 詳細

### 基本構文

```text
While <事前条件>, when <トリガー>, the <システム名> shall <システムの応答>
```

事前条件（While）は 0 個以上、トリガー（When）は 0 か 1 個、システム名はちょうど 1 個、応答は 1 個以上。節の順番は時間の流れ（どんな状態で → 何が起きたら → どのシステムが → 何をする）に沿う。

### 6 つのパターン

| パターン | キーワード | 書きたいこと | 例 |
|---|---|---|---|
| 常時（Ubiquitous） | なし | いつでも成り立つ性質・制約 | The mobile phone shall have a mass of less than XX grams. |
| 状態駆動（State-driven） | While | ある状態の間だけの振る舞い | While there is no card in the ATM, the ATM shall display "insert card to begin". |
| イベント駆動（Event-driven） | When | 何かが起きたときの応答 | When "mute" is selected, the laptop shall suppress all audio output. |
| オプション機能（Optional feature） | Where | 特定の構成・プランだけの機能 | Where the car has a sunroof, the car shall have a sunroof control panel on the driver door. |
| 望ましくない振る舞い（Unwanted behaviour） | If / Then | エラー・故障・不正入力への対処 | If an invalid credit card number is entered, then the website shall display "please re-enter credit card details". |
| 複合（Complex） | While + When など | 状態とイベントの組み合わせ | While the aircraft is on ground, when reverse thrust is commanded, the engine control system shall enable reverse thrust. |

正常系の When と異常系の If / Then をキーワードで分けておくと、**異常系の要件がいくつ書かれているかを文面から数えられる**。異常系を含む複合は `While …, if …, then the … shall …` と書く。

### 日本語で書く

骨組みはそのまま使える。言い回しをパターンごとにチームで固定するのがコツで、日本語では「場合」「とき」「ならば」を入れ替えがちなので、たとえばイベントは「とき」、オプション機能は「場合」、異常系は「もし〜ならば」と決める。

| パターン | 日本語の型 |
|---|---|
| 常時 | 〈システム名〉は〈応答〉しなければならない |
| 状態駆動 | 〈事前条件〉の間、〈システム名〉は〈応答〉しなければならない |
| イベント駆動 | 〈トリガー〉とき、〈システム名〉は〈応答〉しなければならない |
| オプション機能 | 〈機能〉がある場合、〈システム名〉は〈応答〉しなければならない |
| 望ましくない振る舞い | もし〈トリガー〉ならば、〈システム名〉は〈応答〉しなければならない |

Kiro や cc-sdd のように**キーワードだけ英語の大文字で残す**書き方（`WHEN ユーザーがログアウトボタンを押した THE SYSTEM SHALL セッションを破棄する`）もある。日本語としては不自然だが、パターンが一目で分かり grep で数えられる。

### AI 駆動開発で使うときのポイント

- **Kiro の EARS は簡略版**：ドキュメントが示すのは `WHEN [condition/event] THE SYSTEM SHALL [expected behavior]` のイベント駆動の形だけ。AI に書かせるとすべて WHEN になりがちなので、**状態依存や異常系が WHEN に紛れ込んでいないか**を人間が確かめる（「誤ったパスワードを 5 回連続で入力した」は If / Then の異常系）
- **If / Then の数を最初に見る**：入力検証の失敗、外部 API のタイムアウト、権限のない操作、二重送信といった場面ごとに異常系の要件があるか。なければエラー時の振る舞いを AI が実装段階で黙って決めることになる
- **1 文 1 応答**：公式ルールでは応答は複数可だが、受け入れ基準なら 1 要件 1 検証可能な応答にしてテストと 1 対 1 で対応させる
- **曖昧な形容詞を数値にする**：EARS は骨組みを揃えるだけで「すばやく」の曖昧さは消さない。「95 パーセンタイルで 500 ミリ秒以内」のように測れる値にする

### Gherkin への対応

| EARS | Gherkin |
|---|---|
| While〈事前条件〉、Where〈機能〉 | `Given` |
| When / If〈トリガー〉 | `When` |
| shall〈応答〉 | `Then` |

If は Gherkin では同じ `When` になるので、異常系だと分かる名前を `Scenario` に付ける。要件は EARS で書いて人間がレビューし、受け入れテストは Gherkin で AI に書かせる分担にすると、要件からテストまでを追いやすい（[BDD と Gherkin 構文](/blogs/wiki/concepts/bdd-gherkin/)）。

## 関連ページ

- [仕様駆動開発（SDD）](/blogs/wiki/concepts/spec-driven-development/) — EARS が使われる開発手法の全体像
- [BDD と Gherkin 構文](/blogs/wiki/concepts/bdd-gherkin/) — EARS の要件を受け入れテストにする記法
- [Kiro](/blogs/wiki/tools/kiro/) — `requirements.md` に EARS を採用した AI IDE
- [cc-sdd](/blogs/wiki/tools/cc-sdd/) — EARS の書式を生成ルールとして持つ Claude Code 向けスキル
- [形式手法](/blogs/wiki/concepts/formal-methods/) — 自然言語ではなく数学的記法で仕様を厳密に書く手法

## ソース記事

- [EARS 記法とは？ 6 つのパターンと日本語での書き方・Kiro での使い方](/blogs/posts/2026/11/ears-requirements-syntax/) — 2026-11-13
- [仕様駆動開発（SDD）とは？ 3 つのアプローチ・EARS 記法・Kiro / Spec Kit・TDD との違い](/blogs/posts/2026/11/spec-driven-development-overview/) — 2026-11-13
- [Kiro とは？ AWS の仕様駆動 AI IDE の Spec・Steering・Hooks と料金プラン](/blogs/posts/2026/11/kiro-ai-ide-intro/) — 2026-11-13
- [cc-sdd とは？ Claude Code・Codex で Kiro 式の仕様駆動開発を回すスキルと使い方](/blogs/posts/2026/11/cc-sdd-intro/) — 2026-11-13
