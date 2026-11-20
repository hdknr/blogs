---
title: "データ品質入門：RAG とエージェントに壊れたデータを渡さないための 6 つの観点と 3 つの関所"
date: 2026-11-20
lastmod: 2026-11-20
slug: "data-quality-intro"
draft: false
description: "AI エンジニア・アプリケーションエンジニア向けのデータ品質入門。完全性・妥当性・一意性・一貫性・鮮度・正確性の 6 観点、取り込み直後・変換の後・公開の前の 3 つの検査地点、データコントラクトとスキーマ変更の扱い、dbt テスト・Great Expectations・Soda・pandera の使い分けを整理します。"
categories: ["AI/LLM"]
tags: ["データ品質", "dbt", "データ基盤", "RAG", "AIエージェント", "データエンジニアリング"]
---

## はじめに

[AI エンジニアこそデータエンジニアリングを学ぶべき理由](/blogs/posts/2026/11/data-engineering-for-ai-engineers/)では、RAG やエージェントが本番で崩れる原因の多くはモデルではなくデータの流れにある、という話を紹介しました。その記事ではデータ品質に 1 行触れただけでしたが、AI エンジニアが最初に手を付けるべきところの 1 つです。

データの品質問題は、たいてい**エラーを出しません**。重複した行も、空の列も、3 日前で止まった同期も、パイプラインは「成功」として通します。[RAG](/blogs/wiki/concepts/rag/) はそのデータをもっともらしく要約し、エージェントはそのデータを根拠に操作を実行します。誤ったデータは誤った回答で終わらず、誤った操作として速く広く波及します。

この記事では、アプリケーション側から来た人向けに、データ品質を「何を」「どこで」「何を使って」確かめるかを整理します。要点は次の 3 つです。

- 品質は 6 つの観点に分けると、機械的な検査に落とし込める
- 検査は「取り込み直後」「変換の後」「公開の前」の 3 か所に置く
- 検査に失敗したら、新しいデータを公開せず前の版を使い続ける

## 用語とプロダクト

先に、この記事で使う用語とプロダクトをまとめておきます。

| 用語・プロダクト | 意味 |
|---|---|
| データ品質（Data Quality） | データが使う目的に足りる状態か。完全性・妥当性・一意性などの観点に分けて測る |
| DWH（データウェアハウス） | 分析用にデータを集約したデータベース。Redshift、BigQuery、Snowflake など |
| 区分値 | ステータスや種別のように、決められた値の一覧からしか取らない値（enum） |
| データコントラクト（Data Contract） | データを渡す側と使う側が、スキーマ・意味・品質・更新頻度を明文化した取り決め |
| 鮮度（Freshness） | データが最後に更新されてからどれだけ時間が経っているか |
| データオブザーバビリティ（Data Observability） | 鮮度・件数・スキーマ・分布・リネージを継続的に監視し、異常に気付けるようにすること |
| リネージ（Lineage） | どのデータがどこから来て、どこで使われているかという依存関係 |
| [dbt](/blogs/wiki/tools/dbt/) | DWH 上の変換を SQL と YAML で書くツール。データテスト・鮮度チェック・モデルコントラクトを持つ |
| [Great Expectations](https://greatexpectations.io/)（GX） | Python のデータ検証フレームワーク。「Expectation」と呼ぶ検査を組み合わせて使う |
| [Soda](https://www.soda.io/) | YAML で検査を書くデータ品質ツール。OSS の Soda Core と商用サービスがある |
| [pandera](https://pandera.readthedocs.io/) | pandas・Polars などの DataFrame をスキーマで検証する Python ライブラリ |

## データ品質の 6 つの観点

「データが汚い」は漠然としすぎていて、検査に落とし込めません。よく使われる分け方は次の 6 つです。

| 観点 | 問い | 典型的な検査 | RAG・エージェントで起きること |
|---|---|---|---|
| 完全性（Completeness） | 必要な値・行が揃っているか | `NULL` の件数、行数が前日比で急減していないか | 部署名が空の文書が権限フィルタをすり抜ける |
| 妥当性（Validity） | 値が決められた型・範囲・形式に収まるか | 区分値の一覧、日付の形式、金額が負でない | 想定外のステータス値でエージェントの分岐が誤る |
| 一意性（Uniqueness） | 同じものが 2 行になっていないか | 主キーの重複 | 再実行で同じ文書が 2 回索引され、検索結果が偏る |
| 一貫性（Consistency） | テーブル間・システム間で矛盾しないか | 外部キーの参照先が存在するか、合計が一致するか | 注文はあるのに顧客がいない、という回答が返る |
| 鮮度（Timeliness / Freshness） | 必要な時点までに更新されているか | 最終更新時刻が閾値以内か | 改訂前の規程を「最新」として答える |
| 正確性（Accuracy） | 値が現実と一致しているか | 業務システムの帳票と代表値を突き合わせる | 指標の定義違いで、もっともらしい誤った数字を出す |

正確性は、データの中だけを見ても判定できません。現実（元の業務システムや帳票）と比べる必要があるため、自動化が最も難しい観点です。指標の定義を 1 か所にまとめる[セマンティックレイヤー](/blogs/wiki/concepts/semantic-layer/)は、この観点の対策の 1 つです。残りの 5 つは、ルールさえ決めればツールで機械的に確かめられます。

## どこで確かめるか：データ品質チェックを置く 3 つの関所

検査は 1 か所にまとめるより、データの流れに沿って「関所」を置くほうが、問題の場所を特定しやすくなります。

![業務システムから取り込み・変換・索引化と公開を経て RAG やエージェントに届くデータの流れに、取り込み直後・変換の後・公開の前という 3 つの品質検査の地点を対応させ、全体をデータオブザーバビリティが見張る構成を示した図](/blogs/images/data-quality-intro-checkpoints.png)

### ① 取り込み直後：入ってきたものを疑う

ここで確かめるのは、上流が約束どおりのデータを送ってきたかです。

- スキーマ（列名・型）が想定どおりか
- 件数が極端に減っていないか（0 件は「成功」ではない）
- 最終更新時刻が古すぎないか（鮮度）

上流の変化はここで止めるのが一番安上がりです。変換まで進んでからだと、どの段階で壊れたのかを遡って調べる必要が出てきます。

### ② 変換の後：自分たちのロジックを疑う

結合や集計を書いたのは自分たちです。ここでは次のような問題が出ます。

- 結合キーの取り違えによる行の増殖
- `LEFT JOIN` で生まれる `NULL`
- 区分値の変換漏れ

確かめるのは、主キーの一意性、必須列の非 `NULL`、区分値、参照整合性（外部キーの参照先が実在すること）です。dbt のデータテストが最も活きるのがこの地点です。

### ③ 公開の前：使う側の前提を確かめる

ベクトル DB や API に出す直前に、RAG やエージェントが前提にしていることを確かめます。

- 同じ文書の古い版が残っていないか
- 権限フィルタに使う属性（部署・公開範囲）が全件に入っているか
- 埋め込み対象のテキストが空になっていないか

ここで失敗したら、**新しいデータを公開せず、前の版を使い続ける**のが基本です。壊れた最新版より、少し古い正しい版のほうが害は小さいからです。たとえば新しい索引やテーブルを別名で作り、検査に通ったときだけエイリアス（参照先の名前）を切り替えるようにすれば、失敗しても利用者は前の版を見続けます。

## データコントラクトとスキーマ変更

取り込み直後の検査で最も多い失敗は、上流のスキーマ変更です。列名が変わった、型が文字列から数値になった、列が消えた。上流のチームにとっては自分のアプリの改修でも、下流のパイプラインにとっては予告なしの破壊的変更になります。

これを「気付いたら壊れていた」から「変える前に分かる」にするのが**データコントラクト**です。渡す側と使う側で、次のことを明文化します。

- スキーマ：列名・型・必須かどうか
- 意味：その列が何を表すか、区分値の一覧
- 品質：満たすべき検査（一意・非 `NULL` など）
- 運用：更新頻度、鮮度の上限、連絡先

形式の標準化も進んでいます。Linux Foundation AI & Data 傘下の [Bitol](https://bitol.io/) プロジェクトが、YAML でコントラクトを書く **Open Data Contract Standard（ODCS）** を公開しています。

コントラクトを置いたうえで、スキーマ変更は次のように扱うのが定石です。

1. **追加は通す、削除と型変更は止める。** 列の追加は下流を壊しにくい一方、削除・改名・型変更は壊します
2. **止めるなら取り込みの段階で。** 中途半端に流し込んでから失敗すると、後片付けが増えます
3. **破壊的変更は版を分ける。** 旧版と新版をしばらく並行して出し、下流が移行してから旧版を消します

dbt にも、変換結果の側でこれを支える**モデルコントラクト**があります。`contract: {enforced: true}` を付けたモデルは、全列の名前と `data_type` を宣言する必要があります。ビルド時の事前チェックで SQL の出力と宣言が食い違うと、そのモデルは作られません。さらに前回の状態と比較すると、列の削除や型の変更を破壊的変更として検出できます。

## データ品質ツールの使い分け：dbt・Great Expectations・Soda・pandera

| ツール | 書き方 | 向いている場面 |
|---|---|---|
| dbt データテスト | モデルの YAML に宣言、またはテスト用の SQL | DWH 上で dbt を使って変換している |
| Great Expectations | Python で Expectation を組み立てる | Python のパイプラインで、多様な検査と結果レポートが欲しい |
| Soda | YAML で検査やコントラクトを書き、CLI で実行 | SQL を書かずに、複数のデータソースへ同じ形式で検査をかけたい |
| pandera | Python のクラスや型ヒントでスキーマを書く | pandas・Polars の DataFrame を処理するコードの中で検証したい |

全部を入れる必要はありません。変換に dbt を使っているなら、まず dbt のデータテストから始めるのが最も手軽です。

### dbt：4 つの組み込みテストと鮮度チェック

dbt には、`unique`・`not_null`・`accepted_values`・`relationships` の 4 つの汎用データテストが組み込まれています。モデルの YAML に書くだけで、`dbt test`（またはビルドと検査を順に行う `dbt build`）で実行されます。

```yaml
# models/marts/schema.yml
models:
  - name: orders
    columns:
      - name: order_id
        data_tests:
          - unique
          - not_null
      - name: status
        data_tests:
          - accepted_values:
              arguments:
                values: ['placed', 'shipped', 'completed', 'returned']
      - name: customer_id
        data_tests:
          - not_null
          - relationships:
              arguments:
                to: ref('customers')
                field: id
```

上から順に、一意性・完全性・妥当性・一貫性に対応しています。

テストごとに `config:` の下で `severity: warn` を設定すると、失敗してもビルドを止めずに警告だけ出せます。最初は警告で入れて実データの状態を把握し、落ち着いてから `error` に上げると、導入時に全パイプラインが止まる事態を避けられます。

鮮度は、ソースの定義に閾値を書いて確かめます。

```yaml
# models/staging/sources.yml
sources:
  - name: app
    tables:
      - name: orders
        config:
          loaded_at_field: updated_at
          freshness:
            warn_after: {count: 6, period: hour}
            error_after: {count: 24, period: hour}
```

鮮度チェックを実行すると、`updated_at` の最大値が 6 時間より古ければ警告、24 時間より古ければエラーになります。同期ジョブが止まっても「成功」のまま古いデータを出し続ける——この検査は、そうした事態を捕まえます。コマンドは長く `dbt source freshness` でしたが、現在のドキュメントでは `dbt freshness` が推奨され、`dbt source freshness` は旧来のコマンドとして引き続き使えます。

> **バージョンによる書き方の違い**
> - キー名は、単体テスト（unit test）の導入に合わせて `tests:` から `data_tests:` に改められました（`tests:` も引き続き使えます）
> - テストの引数を `arguments:` の下に入れる書き方は dbt 1.10.5 以降です。それより前の版では `values:` や `to:` をテスト名の直下に書きます
> - ソースの `freshness` は 1.9 から、`loaded_at_field` は 1.10 から `config:` の下に書く形になりました

### Great Expectations：Python で許容幅付きの検査

GX Core（1.x）は Python の API で使います。たとえば `ExpectColumnValuesToNotBeNull` のような Expectation を Expectation Suite にまとめ、Checkpoint で実行します。`mostly` 引数で「99.9% 以上が非 `NULL` なら合格」のような許容幅を持たせられるのが特徴です。1.x では API が大きく変わり、Python のコードから操作するのが中心になりました。0.x 時代の記事にある CLI ベースの手順は、そのままでは使えないことがあるので注意してください。

### Soda：YAML で検査を書く

Soda は、検査を YAML で書きます。Soda Core 3 系までは SodaCL という記法で検査ファイルを書き、`soda scan` で実行します。

```yaml
# checks.yml（Soda Core 3 系の SodaCL）
checks for orders:
  - row_count > 0
  - missing_count(order_id) = 0
  - duplicate_count(order_id) = 0
  - freshness(updated_at) < 1d
```

`missing_count`（欠損）、`duplicate_count`（重複）、`freshness`（鮮度）と、観点がそのまま関数名になっているので読みやすい記法です。現行の Soda Core 4 系はデータコントラクトの YAML を中心にした形に移り、`soda contract verify` でコントラクトを検証します。これから始めるなら、使う版のドキュメントを確認してください。

### pandera：コードの中で DataFrame を検証

pandera は、アプリケーションのコードの中で DataFrame を検証したいときに向いています。RAG の前処理を Python で書いているなら、索引化の直前に挟めます。

```python
import pandas as pd
import pandera.pandas as pa
from pandera.errors import SchemaErrors
from pandera.typing import Series


class Orders(pa.DataFrameModel):
    order_id: Series[int] = pa.Field(unique=True)
    status: Series[str] = pa.Field(isin=["placed", "shipped", "completed", "returned"])
    amount: Series[float] = pa.Field(ge=0)


df = pd.DataFrame({
    "order_id": [1, 2, 2],
    "status": ["placed", "shipped", "unknown"],
    "amount": [1200.0, -50.0, 800.0],
})

try:
    # lazy=True で、最初の違反で止めずに全違反をまとめて報告する
    Orders.validate(df, lazy=True)
except SchemaErrors as err:
    print(err.failure_cases)  # 重複・区分値・負の金額がすべて並ぶ
    raise  # 公開せずに止める
```

pandas 用のスキーマは、pandera 0.24.0 以降 `pandera.pandas` から読み込むのが推奨です。Polars の DataFrame も、`pandera.polars` から同じ考え方で検証できます。

## 関所の外側：データオブザーバビリティ

ここまでの検査は、すべて「こうなっているはず」というルールを人が先に書く方式です。ルールを書いていない異常、たとえば「ある列の値の分布が急に偏った」「件数がじわじわ半分になった」には気付けません。

そこで使われるのが**データオブザーバビリティ**です。よく挙げられる観点は、鮮度・件数（ボリューム）・スキーマ・分布・リネージの 5 つです。過去の傾向から外れた変化を検知し、影響を受ける下流（どのダッシュボードや RAG の索引か）をリネージで示します。

規模が小さいうちは、専用製品を入れなくても始められます。

- 各テーブルの行数と最終更新時刻を毎日記録し、前日比で大きく動いたら通知する
- dbt の鮮度チェックを定期実行して、結果を監視に流す
- 「0 件で成功」を成功として扱わない

最後の項目は特に重要です。[RDS の Blue/Green 切替で DMS が静かに死んだ話](/blogs/posts/2026/08/rds-blue-green-dms-cdc-incident/)では、CDC（変更データキャプチャ。DB の変更を逐次取り出す仕組み）が止まって出力がゼロになったまま、18 日間誰も気付きませんでした。アラームが「メトリクスがない＝正常」と扱っていたためです。[自律システムはなぜ自分の欠陥に気づけないのか](/blogs/posts/2026/07/autonomous-system-blind-spots/)でも、遅れていたのは判断ロジックではなくデータの供給でした。[沈黙する失敗](/blogs/wiki/concepts/silent-failure/)は、データパイプラインで最も起きやすく、最も見つけにくい失敗です。

## AI エージェントは悪いデータを増幅する

ダッシュボードの数字が間違っていても、人が見て「おかしい」と気付く余地があります。RAG やエージェントでは、その余地が小さくなります。

- **もっともらしさが疑いを消す。** LLM は重複や欠損を含むデータからでも、流暢で自信のある回答を作ります。人が数字を見て違和感を覚える機会がありません
- **判断が行動になる。** エージェントは読んだデータを根拠に、メールを送り、チケットを起票し、在庫を発注します。誤ったデータは誤った回答で終わらず、誤った操作になります
- **速く、広く波及する。** 人なら 1 件ずつ処理するところを、エージェントは同じ誤りを数百件に同時に適用できます
- **誤りが次の入力になる。** エージェントが書き込んだ誤ったデータは、次のエージェントや次回の索引化の入力になり、元をたどりにくくなります

だからこそ、エージェントにデータを渡す前の「③ 公開の前」の関所と、検査に失敗したら前の版を使い続ける仕組みが効いてきます。AI に向けたデータの整え方は [AI-ready データ](/blogs/wiki/concepts/ai-ready-data/)でもまとめています。

## まとめ

- データ品質は、完全性・妥当性・一意性・一貫性・鮮度・正確性の 6 つの観点に分けると検査に落とし込める
- 検査は「取り込み直後」「変換の後」「公開の前」の 3 つの関所に置くと、壊れた場所を特定しやすい
- 上流のスキーマ変更には、データコントラクトで取り決めを明文化し、破壊的変更は取り込みの段階で止める
- dbt を使っているなら、`unique`・`not_null`・`accepted_values`・`relationships` と鮮度チェックから始めるのが手軽
- ルールで書けない異常はデータオブザーバビリティで拾う。「0 件で成功」を成功扱いしない
- エージェントは悪いデータを、もっともらしい回答と実際の操作に変えて増幅する。公開前の関所が最後の防波堤になる

## 関連記事

- [AI エンジニアこそデータエンジニアリングを学ぶべき理由：RAG のデモが本番で崩れるところ](/blogs/posts/2026/11/data-engineering-for-ai-engineers/)
- [RDS の Blue/Green 切替で DMS が静かに死んだ話 — 18日間気付かなかった監視の三重の穴](/blogs/posts/2026/08/rds-blue-green-dms-cdc-incident/)
- [自律システムはなぜ自分の欠陥に気づけないのか — Claude Code で自律システムを作るときの5つの教訓](/blogs/posts/2026/07/autonomous-system-blind-spots/)
- [データ照会チャットボットはデータ分析基盤を作ってから？ツール呼び出し・Text-to-SQL・セマンティックレイヤーの関係と進め方](/blogs/posts/2026/11/data-chatbot-and-data-platform/)
- [AWS だけで作る AI ネイティブなデータ分析基盤：Aurora zero-ETL × Redshift × dbt 構成案](/blogs/posts/2026/11/aws-only-ai-native-data-platform/)
- [AI エージェントのためのデータ基盤：レイクハウスを土台に「意味・費用・権限・取り消し」を設計する](/blogs/posts/2026/10/ai-agent-data-platform/)
- [デジタル庁の行政手続 MCP サーバーに学ぶ「LLM に計算させない」データ設計](/blogs/posts/2026/08/digital-agency-mcp-ai-ready-data/)
- wiki：[dbt](/blogs/wiki/tools/dbt/)、[AI-ready データ](/blogs/wiki/concepts/ai-ready-data/)、[沈黙する失敗](/blogs/wiki/concepts/silent-failure/)、[セマンティックレイヤー](/blogs/wiki/concepts/semantic-layer/)
