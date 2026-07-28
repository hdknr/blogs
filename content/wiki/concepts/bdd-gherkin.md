---
title: "BDD と Gherkin 構文"
description: "振る舞い駆動開発と Gherkin による「仕様の共通言語化」。金融システムで BDD が効く理由と、Three Amigos・ステップ定義・動く仕様書という実務の型"
date: 2026-07-28
lastmod: 2026-07-28
aliases: ["BDD", "振る舞い駆動開発", "Gherkin", "ガーキン", "Cucumber", "SpecFlow", "Reqnroll", "Three Amigos", "動く仕様書", "Given When Then"]
related_posts:
  - "/posts/2026/07/financial-system-bdd-gherkin/"
tags: ["BDD", "Gherkin", "Cucumber", "テスト自動化", "金融システム"]
---

## 概要

BDD（Behavior-Driven Development：振る舞い駆動開発）は、単なるテスト手法ではなく **「ビジネスの要求を、そのまま自動テストのコードに直結させる仕組み」**として運用される。中核にあるのは自然言語に近い **Gherkin（ガーキン）構文**で、ビジネス部門と開発エンジニアの間の認識のズレを解消する共通言語として機能する。

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

Gherkin は英語キーワード（`Feature` / `Scenario` / `Given` / `When` / `Then` / `And`）だけでなく**日本語を含む多言語のローカライズに対応**している。日本語で書けば、非エンジニアのビジネス担当者が見ても仕様の正しさを一目で確認できる。

## 開発フロー

フレームワークは **Cucumber**（Ruby / Java / JavaScript など）や **SpecFlow**（.NET 系。開発終了しており後継の **Reqnroll** への移行が進んでいる）。

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

### ③ Red → Green と回帰テストの自動化

最初は未実装なのでテストは Red（失敗）になる。ここが起点。本番コードを実装して Green になれば開発完了。このシナリオはそのまま**仕様書であり、同時にいつでも実行できる自動テスト（回帰テスト）**としてシステムに残り続ける。

## 金融システムで効く理由

金融システムは「複雑な業務ルール」「極めて高い品質要求」「絶対に失敗できない決済処理」という特徴を持つため、BDD の仕組みが噛み合う。

- **「動く仕様書」になりドキュメントの陳腐化を防げる** — 仕様とテストが同一物なので乖離しない
- **ビジネス部門との認識ズレを構造的に減らせる** — 非エンジニアがレビューできる形式で仕様が残る
- **境界値・例外パターンを事前に洗い出す文化が作られる** — Three Amigos が設計段階で強制する

## 関連ページ

- [pytest によるカオスエンジニアリング](/blogs/wiki/guides/pytest-chaos-engineering/) — 障害注入によるテスト
- [自動テスト修正パイプライン](/blogs/wiki/guides/auto-test-fix-pipeline/) — テストを軸にした自律修正
- [計画と実装を分ける承認ゲート設計](/blogs/wiki/concepts/approval-gate-design/) — テストをゲートとして使う設計
- [形式手法](/blogs/wiki/concepts/formal-methods/) — 仕様の厳密化という別アプローチ

## ソース記事

- [金融系システムで BDD が効く理由──Gherkin 構文で仕様とテストを一致させる開発手法](/blogs/posts/2026/07/financial-system-bdd-gherkin/) — 2026-07-17
