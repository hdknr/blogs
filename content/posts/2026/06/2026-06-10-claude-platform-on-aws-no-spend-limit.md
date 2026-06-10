---
title: "Claude Platform on AWS には Spend Limit がない — AWS Budgets と Rate Limit で課金暴走を防ぐ"
date: 2026-06-10
lastmod: 2026-06-10
slug: "claude-platform-on-aws-no-spend-limit"
draft: false
description: "Claude Platform on AWS には金額上限（Spend Limit）がない。理由と、AWS Budgets のアラート・Rate Limit のキャップ・Amazon Bedrock の自動遮断という現実的な課金ガードレールの組み方を整理する。"
source_url: "https://github.com/hdknr/blogs/issues/93#issuecomment-4666921106"
categories: ["クラウド/インフラ"]
tags: ["AWS", "Claude", "コスト管理", "AWS Budgets", "レート制限"]
---

「Claude Code のループで暴走して、気付いたら数万〜数十万円の請求が来るのが怖い」——これは Claude Platform on AWS を使い始めた人がまず気にするポイントです。結論から言うと、**Anthropic のコントロールパネル（Claude Console）から「月額最大〇〇ドルまで」といった Spend Limit（利用金額制限）をかける機能は、Claude Platform on AWS ではサポートされていません。**

Anthropic の公式ドキュメント（Claude Platform on AWS の Feature support）には、明確にこう書かれています。

> **Spend limits: Not available. Rely on AWS billing controls instead.**
> （利用金額制限：利用不可。代わりに AWS の請求コントロールを利用してください。）

本記事では、なぜ金額制限ができないのか、そして「課金の暴走」をどう防ぐのかを、AWS 側のガードレールの実装まで含めて整理します。

## なぜ金額で制限できないのか

通常の Anthropic 直接契約の API は、「事前にお金をチャージする（デポジット制のクレジット購入）」または「Anthropic が請求書を発行する」モデルです。Console 側に残高や上限という概念があるため、自社システム側で金額の上限をコントロールできます。

一方、Claude Platform on AWS は **AWS Marketplace の従量課金**の仕組みに乗っています。使った分は **CCU（Claude Consumption Unit、1 CCU = 0.01 USD）** に換算されます。それが 1 時間ごとにメータリングされ、月末に AWS の請求書へ後払いで合算される、という流れです。プリペイドの残高や事前コミットがないため、Anthropic 側の管理画面から「残高ゼロで強制ストップ」をかける仕組み自体が存在しません。だから Spend Limit が省かれている、というわけです。

つまり「金額の蛇口」は Anthropic 側ではなく **AWS 側**にあります。コスト管理は AWS のネイティブ機能で行う、という前提に切り替える必要があります。

![Claude Platform on AWS の課金ガードレール。開発者や Claude Code からのリクエストが Claude Platform on AWS を経由し、Rate Limit による速度キャップと AWS Marketplace の従量課金（Spend Limit なし）につながる。AWS Budgets はアラート通知のみで自動遮断はできず、厳格に止めたい場合は Amazon Bedrock の Budget Actions や Lambda による IAM 権限剥奪で物理停止する、という全体像を示した図。](/blogs/images/claude-platform-on-aws-no-spend-limit-guardrails.png)

## 課金暴走を防ぐ 2 つの基本対策

Claude Platform on AWS のまま使う場合、現実的に効くのは次の 2 つです。

### 対策1：AWS Budgets でアラートを設定する（推奨）

AWS の基本機能である **AWS Budgets** を使い、Claude Platform on AWS（AWS Marketplace の利用料）に対して予算としきい値を設定します。

- **できること:** 「月 1 万円」などと設定し、実際の利用額または予測額が **80%・100% に達した瞬間にメールや Slack（Amazon SNS 経由）で通知**を受け取れます。
- **注意点1:** Budgets 単体では、予算を超えても**自動で API を遮断（ストップ）することはできません。** あくまで「今、使いすぎている」ことを検知するアラートです。
- **注意点2:** Budgets の集計は 1 日に数回（最大 4 回程度）の更新です。急激なスパイクは検知が遅れることがあるため、しきい値は低め・複数段階で仕込んでおくのが安全です。

段階的にしきい値を仕込む例:

- **5,000 円 到達（実績）** → 軽い注意喚起
- **8,000 円 予測（forecast）** → 早期警告
- **10,000 円 到達（実績）** → 最終アラート + 関係者全員に通知

CloudWatch の請求アラームと違い、Budgets は実績額だけでなく **forecast（予測額）** でもしきい値を切れるのが効きます。「このペースだと月末に上限を超える」を月の途中で掴めます。

### 対策2：Rate Limit を低いまま運用する

金額の制限（Spend Limit）はできませんが、1 分あたりに使えるトークン量・リクエスト数の制限（**Rate Limit**）は適用されています。

Claude Platform on AWS では、サブスクライブ時に **Tier 1** のレート制限が割り当てられます。重要なのは、**第一者の Claude API と違って自動でのティア昇格（automatic tier advancement）が行われない**点です。つまり、何もしなければ Tier 1 のキャップがかかり続けます。

初期状態の Tier 1 のままであれば、万が一ループ事故が起きても「1 分間に消費できる最大量」に物理的な天井があるため、一瞬で数百万円まで跳ね上がる、という最悪のシナリオは抑えられます。

逆に「処理を速くしたいから」と安易に上限引き上げ（Rate Limit Increase）を申請すると、事故時のダメージ上限も比例して大きくなります。引き上げは「事故時の最大被害額を引き上げる行為」でもある、と意識しておくべきです。

> なお Claude Platform on AWS では、上限引き上げは自動申請ではなく、ワークスペース ID と希望スループットを添えて Anthropic の担当者に依頼する形になります。

## 「予算超過で確実に止めたい」場合の選択肢

「予算を超えたら自動で API を完全にストップさせたい」という厳格なコスト管理が必要なら、**Amazon Bedrock**——Claude Platform on AWS とは別に、AWS がマネージドサービスとして Claude を提供する経路——の利用を検討する価値があります。Bedrock であれば AWS 標準のコスト制御に素直に乗せられます。

### Budget Actions で IAM/SCP を自動適用する

AWS Budgets には **Budget Actions** という機能があり、しきい値超過時に **IAM ポリシーや SCP（サービスコントロールポリシー）を自動で適用**できます。これを使い、超過時に Bedrock の `InvokeModel` を拒否するポリシーをアタッチすれば、実質的にアクセスを止められます。

ただし注意点として、Budget Actions が直接「API を停止する」アクションを持っているわけではありません。**IAM/SCP の適用・対象 EC2/RDS の停止**といったアクションを介して間接的に止める、という設計になります。

### Lambda で IAM 権限を剥奪して物理停止する

より柔軟にやるなら、Budgets → SNS → **Lambda** の連携です。

1. Budgets が予算超過を検知して Amazon SNS トピックに通知。
2. SNS をサブスクライブした Lambda が起動。
3. Lambda が対象ロール/ユーザーから Bedrock 実行権限（IAM ポリシー）を一時的に剥奪し、**物理的に API 呼び出しを強制停止**。

この経路（Budgets → SNS → Lambda → IAM 権限の Deny/Detach）なら、通知を待たずに自動で蛇口を閉められます。冒頭の図でも「厳格に止めたい場合の選択肢」として示したルートです。

### API Gateway を挟んでチーム単位で制御する

開発者が直接 API を叩くのではなく、社内プロキシ（**API Gateway**）を経由させる構成も有効です。使用量プラン（Usage Plans）と API キーで、ユーザーごと・チームごとに日次/月次のリクエスト上限を設定・管理できます。これは Claude Platform on AWS でも、自前のプロキシ層を挟めば応用可能な考え方です。

## まとめ

- Claude Platform on AWS に **Spend Limit（金額上限）は存在しない**。公式に「AWS の請求コントロールを使え」と明記されている。
- 理由は AWS Marketplace の**従量・後払い（CCU 課金）**モデルに乗っているため。金額の蛇口は AWS 側にある。
- 現実的な自衛策は **AWS Budgets のアラート（低め・複数段階・forecast 併用）** と **Rate Limit を Tier 1 のまま低く保つ**こと。ただし Budgets 単体は通知のみで自動遮断はできない。
- 「超過したら確実に止める」を実現したいなら、**Amazon Bedrock + Budget Actions（IAM/SCP 自動適用）または Lambda による権限剥奪**で物理停止を組む。

まずは AWS Budgets で数千円〜1 万円単位の細かい通知を仕込んでおく——これが、現状の Claude Platform on AWS で最初に打つべき一手です。

---

### 参考リンク

- [Feature support — Claude Platform on AWS](https://docs.aws.amazon.com/claude-platform/latest/userguide/feature-support.html)
- [Billing — Claude Platform on AWS](https://docs.aws.amazon.com/claude-platform/latest/userguide/billing.html)
- [Rate limits and quotas — Claude Platform on AWS](https://docs.aws.amazon.com/claude-platform/latest/userguide/rate-limits.html)
- [Configuring budget actions — AWS Cost Management](https://docs.aws.amazon.com/cost-management/latest/userguide/budgets-controls.html)
