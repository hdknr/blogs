---
title: "Claude Platform on AWS が GA — Amazon Bedrock との違いと day-one でフル機能を使える理由"
date: 2026-05-13
lastmod: 2026-05-13
draft: false
description: "Anthropic が 2026 年 5 月 11 日に GA した Claude Platform on AWS を Amazon Bedrock と比較。day-one で使える Managed Agents・Skills・MCP connector、既存 AWS コミットメントの消化など、AWS 顧客が選び分けるための判断材料をまとめる。"
summary: "Claude Platform on AWS の GA を Amazon Bedrock との比較で整理。ネイティブ API フル機能と AWS IAM・請求の両立がもたらす意味を解説。"
source_url: "https://github.com/hdknr/blogs/issues/1#issuecomment-4439456381"
categories: ["AI/LLM"]
tags: ["Claude", "AWS", "Anthropic", "Amazon Bedrock", "Managed Agents", "MCP", "Skills"]
---

Anthropic は 2026 年 5 月 11 日、**Claude Platform on AWS** の一般提供（GA）を開始した。Anthropic 公式 API のフル機能を、AWS の IAM 認証・CloudTrail 監査・単一請求書で利用できる新しいアクセス経路である。すでに展開している Amazon Bedrock 経由の Claude とは別サービスとして位置付けられている。

## 何が新しいのか

これまで AWS 顧客が Claude を使う公式の選択肢は **Amazon Bedrock** 経由が中心だった。Bedrock は AWS がデータ処理事業者となり、AWS バウンダリ内で完結する一方で、Anthropic ネイティブ API の最新機能やベータ機能は遅れて追随する形になっていた。

Claude Platform on AWS は、**ネイティブ Claude API と完全に同じ機能セット**を AWS の認証・課金レイヤーから直接呼び出せるようにしたものだ。Anthropic 公式ブログによれば、新機能やベータは **ネイティブ API と同日リリース（day-one access）** される。

> The Claude Platform on AWS brings the full set of Claude API features to AWS customers for the first time, with all new features and betas shipping the same day they go live on the native Claude API.
>
> （訳: Claude Platform on AWS は AWS 顧客に初めて Claude API のフル機能セットを提供する。新機能とベータはネイティブ Claude API でローンチされるのと同日にリリースされる。）
> （出典: [claude.com/blog/claude-platform-on-aws](https://claude.com/blog/claude-platform-on-aws)）

## Claude Platform on AWS と Amazon Bedrock の違い

両者は競合ではなく、**運営主体とデータ処理境界が異なる別オプション**として並列に提供される。

| 観点 | Claude Platform on AWS | Claude on Amazon Bedrock |
| --- | --- | --- |
| 運営主体 | Anthropic | AWS |
| データ処理 | AWS の信頼境界（バウンダリ）外 | AWS の信頼境界内 |
| ネイティブ API 機能 | フル（day-one） | サブセット |
| 認証 | AWS IAM | AWS IAM |
| 請求 | AWS 単一請求書（既存コミットメント消化可） | AWS 単一請求書 |
| 向いている用途 | 最新機能を最速で使いたい場合 | AWS 内でのデータ処理が必須の場合 |

つまり、**「データ処理を AWS 内に閉じ込める要件があるか」** が選び分けの軸になる。要件がなければ Claude Platform on AWS のほうが機能面で有利、要件があれば引き続き Bedrock という整理だ。関連: [Claude Managed Agents の公式ローンチ](/blogs/posts/2026/04/2026-04-10-claude-managed-agents/) も Bedrock ではなくこのプラットフォームの中核機能として整理されている。

## day-one アクセスで使える Claude ネイティブ API 機能一覧

公式ブログに列挙されている主な機能は次のとおり。多くが現時点でも `(beta)` ラベルが付くが、これらが AWS 経由でもネイティブ API と同タイミングで使えるのが今回の核心だ。

- **Claude Managed Agents (beta)** — エージェントをスケールで構築・展開
- **Advisor strategy (beta)** — アドバイザーモデルに諮問して知能をブースト
- **Web search / Web fetch** — Web から最新情報を取得
- **Code execution** — API 呼び出し内で Python を実行、可視化やデータ分析
- **Files API (beta)** — ドキュメントをアップロードして会話横断で参照
- **Skills (beta)** — ベストプラクティスを教え込み、一貫した出力を実現
- **MCP connector (beta)** — クライアントコードを書かずに任意のリモート MCP サーバーへ接続
- **Prompt caching** — 繰り返しコンテキストでコスト・レイテンシ削減
- **Citations** — ソース文書による根拠付き応答
- **Batch processing** — 大量・非同期ワークロード向けバッチ処理

加えて、Anthropic の開発者向け Web コンソールである **Claude Console**（プロンプト改善ツール、プロンプトジェネレーター、評価ツールを含む）にもアクセスできる。

利用可能なモデルは **Claude Opus 4.7 / Sonnet 4.6 / Haiku 4.5** で、Anthropic は新モデルもローンチに合わせて順次提供する予定としている。

## 既存の AWS 運用に馴染む

Claude Platform on AWS の設計は、AWS をすでに使っている組織にとって導入の摩擦を最小化することを狙っている。

- **認証**: 既存の AWS IAM クレデンシャル・ポリシーをそのまま使う。新しい認証基盤を別途構築する必要がない
- **監査ログ**: CloudTrail に記録され、既存のセキュリティ運用フローに統合できる
- **請求**: AWS の単一請求書にまとまり、**既存の AWS コミットメント（EDP: Enterprise Discount Program など）の消化に充当**される。別途 Anthropic に支払いを起こす必要がない
- **リージョン**: 多くの AWS 商用リージョンで提供、グローバルおよび米国（U.S.）の推論リージョン（inference geography）をサポート

特に「既存の AWS コミットメントを消化（retire）できる」点は、すでに大型コミットメントを抱える企業にとって価値が大きい。Anthropic への直接契約だと別予算ラインを立てる必要があったところを、AWS の枠内に収められる。

## 顧客の声から見える導入動機

公式ブログには 3 社のコメントが掲載されている。三者三様に「ネイティブ API と同等の最新機能を、AWS の運用モデルを崩さずに使える」点を強調している。

- **Jonathan Echavarria 氏（Principal Research Scientist）**: Claude へのアクセス簡素化、Claude Code エンジニアの体験向上、既存のクラウド運用モデルを維持したままサイバーセキュリティ・エンジニアリングのワークフローへ AI を統合
- **Tomas Oliva 氏（OpenRouter / AI Platform Engineer）**: ネイティブ Claude API の最新機能への直接アクセス、他の AWS サービスと同じ IAM クレデンシャルでアクセス制御
- **Avinash Vishwakarma 氏（Chief Architect）**: 「canonical Anthropic API + AWS をアクセスレイヤーとする構成」で機能パリティ（feature parity）と新モデル機能への day-one アクセスを実現

## 導入時の注意点

Anthropic は導入前に押さえておくべき点も明示している。

> If you have an existing Bedrock private offer, please contact your Anthropic or AWS account executive before getting started with Claude Platform on AWS to ensure your discounts are applied correctly. Discounts cannot be applied retroactively to usage incurred before a Claude Platform private offer is accepted.
>
> （訳: 既存の Bedrock プライベートオファーをお持ちの場合は、Claude Platform on AWS を利用開始する前に Anthropic または AWS の営業担当に連絡し、割引が正しく適用されるようにしてください。Claude Platform プライベートオファーを受諾する前に発生した利用分に対して、割引をさかのぼって適用することはできません。）

つまり、**既存の Bedrock プライベートオファーがある場合は、先に営業担当に連絡して割引を Claude Platform on AWS 側にも適用する手続きを取る必要がある**。割引はさかのぼって適用されないため、契約調整は利用開始前に済ませる必要がある。

## Claude Platform on AWS と Bedrock どちらを選ぶ？判断フロー

新規に AWS 上で Claude を採用する場合、選択は次の問いに集約される。

1. **データ処理を AWS の信頼境界内に閉じ込める法令・契約上の要件があるか？**
   - **YES** → Claude on Amazon Bedrock
   - **NO** → Claude Platform on AWS
2. **ネイティブ API のベータや最新機能を day-one で使いたいか？**
   - **YES** → Claude Platform on AWS
   - **NO（安定版のみで十分）** → どちらでも可
3. **既存の AWS コミットメントを Claude 利用で消化したいか？**
   - **YES** → どちらも AWS 請求にまとまるので可。割引の適用範囲は営業確認
   - **NO** → 通常請求でどちらも可

特に [Claude Managed Agents](/blogs/posts/2026/04/2026-04-10-claude-managed-agents/) や Skills、MCP connector、Code execution など、Claude Platform の魅力的なベータ機能を試したいエンジニアリングチームには、Claude Platform on AWS が現実的な唯一解になる。

## 開発者にとっての意味

Anthropic 視点では、これはいわゆる **「Bedrock のサブセット問題」を解消する戦略的な動き**でもある。Claude のフロンティア機能（Managed Agents、Skills、MCP connector など）はベータ段階から出荷頻度が高く、Bedrock 経由だとどうしてもラグが出ていた。

AWS 顧客にとっては「ネイティブ API を直接叩く（= AWS 外の請求・認証を別途運用する）」か「Bedrock で待つ」かの二択だった。今回そこに、**「AWS の運用そのままでネイティブ API のフル機能」** という第三の選択肢が加わった意味は大きい。

エージェント開発、特に Claude Managed Agents や Skills を中核に据えた本番システムを AWS で動かす場合、これからのデフォルトは Claude Platform on AWS になるだろう。

## 参考リンク

- [Introducing the Claude Platform on AWS（Anthropic 公式ブログ）](https://claude.com/blog/claude-platform-on-aws)
- [Claude Platform on AWS（AWS ランディングページ）](https://aws.amazon.com/jp/claude-platform/)
- [元ポスト（X / @hata_AI_master）](https://x.com/hata_AI_master/status/2053968293283979694)
