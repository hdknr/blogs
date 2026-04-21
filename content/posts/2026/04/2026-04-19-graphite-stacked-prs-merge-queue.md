---
title: "Graphite 徹底解説 — スタックドPRとマージキューがAIファースト開発を加速する理由"
date: 2026-04-19
lastmod: 2026-04-19
draft: false
categories: ["ツール/開発環境"]
tags: ["Graphite", "GitHub", "スタックドPR", "マージキュー", "AIコードレビュー", "CI/CD", "ハーネスエンジニアリング"]
---

[CreaoAI が25名で6週間のリリースサイクルを1日に短縮した事例](/blogs/posts/2026/04/2026-04-17-ai-first-harness-engineering-creao/)では、PR 管理ツールとして **Graphite** が採用されていた。1日8回デプロイ・AI が大量に PR を量産する運用で、素の GitHub PR フローは何が詰まり、Graphite は何を解決するのか。本記事では Graphite の3本柱（スタックドPR・マージキュー・AIレビュー）を、CLI コマンドと具体的な運用シナリオで解説する。

## Graphite とは

[Graphite](https://graphite.com/) は GitHub 上の PR ワークフローを拡張する開発者プラットフォーム。2025年3月に Anthropic から $52M の Series B を調達し、同時に AI コードレビュー「Diamond」をローンチした（現在は **Graphite Agent** に名称統合）。元 Airbnb・Meta のエンジニア出身チームが、Meta 内部で使われていた Phabricator / Sapling 的なスタック開発体験を GitHub に持ち込んだのが出発点だ。

主要機能は3つに整理できる。

1. **スタックドPR** — 大きな変更を依存関係のある小さな PR の連鎖に分割する
2. **マージキュー** — スタックを理解した状態で main にマージを直列化する（stack-aware）
3. **Graphite Agent（旧 Diamond）+ Chat** — AI によるコードレビューと対話的修正

## スタックドPR：大きな差分を「小さなレビュー単位の連鎖」に分解する

### 何が問題だったのか

AI エージェントや生産性の高い開発者は、1つのフィーチャーを実装する過程でしばしば以下のような複数階層の変更を生む。

- DBスキーマの追加
- それを使う API エンドポイント
- 認証ミドルウェアの更新
- フロントエンドの呼び出し

従来の GitHub PR モデルだと選択肢は2つしかない。

- **大きな1つの PR にまとめる** → レビュアーが 1,000 行以上を一度に見る羽目になり、レビュー品質が崩壊する
- **1つずつ順番に出す** → 親 PR がマージされるまで次の PR を作れず、開発者は待機する

### スタックドPRはこう解決する

Graphite は Git のブランチ依存関係を内部メタデータとして保持し、**依存する PR 同士を並べて同時にオープン** できるようにする。

```text
main
 └─ PR #1: DB schema                  ← レビュー中
     └─ PR #2: API endpoint           ← レビュー中（#1に依存）
         └─ PR #3: Auth middleware    ← レビュー中（#2に依存）
             └─ PR #4: Frontend       ← レビュー中（#3に依存）
```

各 PR は 100〜200 行程度の小さな差分になり、レビュアーは担当レイヤーだけを独立に見ればよい。親 PR に修正が入った場合、Graphite が自動で子ブランチをリベース（再スタック）してくれる。

### 主要な CLI コマンド

Graphite の CLI コマンドは `gt` で始まる。代表的なものを挙げる。

| コマンド | 用途 |
|--|--|
| `gt create -m "msg"` | 現在のブランチの上に新しい子ブランチ＋コミットを作る |
| `gt modify` | 既存ブランチを修正し、上流のスタックを自動リベース |
| `gt submit` | スタック全体（もしくは現在のブランチ以下）の PR を一括作成・更新 |
| `gt sync` | main を取り込んで、マージ済みブランチを掃除しつつスタックをリベース |
| `gt checkout` | スタック内のブランチを対話的に移動 |
| `gt log` | スタック構造を視覚化 |

### 典型的なワークフロー

```bash
# main から分岐してスタックを積んでいく
gt checkout main
gt create -m "feat: add users table"
# ... コード編集 ...
gt create -m "feat: add POST /users endpoint"
# ... コード編集 ...
gt create -m "feat: wire up frontend form"

# スタック全体を一発で PR 化
gt submit --stack

# 途中の PR にレビュー指摘が入った場合
gt checkout <branch-name>
# ... 修正 ...
gt modify            # ← 上のブランチも自動で再スタック
gt submit --stack    # ← 全 PR を更新
```

`gt submit --stack` 一発で 4つの PR が同時にオープンされ、それぞれのレビューが並列に進む。子 PR の本文には親 PR へのリンクが自動挿入される。

## マージキュー：`main` を壊さずに並列マージを捌く

### 素の GitHub で起きる事故

AI がコードを書く時代、1日に何十・何百の PR が同時に「グリーン・レビュー承認済み」状態になる。このとき、たとえば以下のような事故が頻発する。

1. PR-A と PR-B が同じファイルの別箇所を修正している
2. どちらもレビュー時点では CI グリーン
3. PR-A がマージされた後、PR-B は「テスト的には通る」けれど**論理的にコンフリクト**
4. PR-B をそのままマージ → main が壊れる

これを防ぐのがマージキューだ。

### Graphite Merge Queue の処理フロー

PR がキューに入ると、Graphite は次を自動実行する。

1. 最新の main にリベース
2. リベース後の状態で CI を**再実行**
3. グリーンなら main にマージ、赤ければキューから除外して通知

ここまでは GitHub Native Merge Queue や Mergify とおおむね同じ。Graphite の差別化ポイントは **stack-aware**（スタック対応）な点にある。

### なぜ「stack-aware」が効くのか

Graphite は「これはスタックされた 4つの PR だから、順序を保って並列に処理する」という判断ができる。

- **順序最適化** — 依存関係のあるスタックは親から順にマージ、独立なスタック同士は並列に処理
- **CI の並列化** — スタック全体で1回の CI 実行に集約して実行時間を短縮（CI コストも削減）
- **ホットフィックスの差し込み** — 緊急 PR をキュー先頭に挿入可能
- **フォールバック** — 赤い PR だけキューから落とし、後続をブロックしない

[Ramp Engineering の事例](https://graphite.com/blog/the-first-stack-aware-merge-queue)では、Graphite のマージキュー導入後にマージ間隔の中央値が **74% 短縮**、エンジニアが PR をマージするスピードが最大3倍になったと報告されている。

### マージ戦略

- **Rebase**（GitHub の rebase-and-merge 相当）
- **Squash**
- オプションで **Fast-forward merge** — スタックされた PR を本当に並列処理したい場合に使用

## Graphite Agent：PR ごとの AI レビューと対話

2026年時点では、2025年3月にローンチした **Diamond** とチャット機能が統合され **Graphite Agent** となった。

- **AIレビュー** — PR が作成されるたびに自動でコードを読み、ロジックエラー・セキュリティ・保守性の観点でコメント
- **Graphite Chat** — PR ページ上で「この CI 失敗どう直す？」と聞くと、修正案を提示しそのままコミットできる
- **サジェスチョンではなくゲート** — 人間レビュアーが追いつかない量の PR を、AI レビューが1次フィルターとして処理する

CreaoAI の事例で「PR ごとに Claude Opus 4.6 を3並列で走らせる」という設計思想と方向性が一致している。

## 料金プラン

2026年4月時点の公開プラン。

| プラン | 料金 | 主な内容 |
|--|--|--|
| Free | $0 | 基本機能、AIレビュー月次上限あり |
| Starter | $20/user/月 | 全リポジトリ対応、AIレビュー・Chat |
| Team | $40/user/月 | **Unlimited AIレビュー・Chat、マージキュー**、AIレビューのカスタマイズ |
| Enterprise | 要問い合わせ | SAML、Audit log (SIEM)、ACL、GHES、専用サポート |

年払いは 20% オフ。**マージキューは Team プラン以上**である点に注意（Starter だとスタックドPR は使えてもキューは使えない）。

## ハーネスエンジニアリングとの相性

[AIファースト戦略](/blogs/posts/2026/04/2026-04-17-ai-first-harness-engineering-creao/)でも触れたように、AI がコードを書く速度に対するレビュー・マージの律速を解消することが Harness 全体のスループットを決める。Graphite がその律速に対して提供する解は明快だ。

- **スタックドPR**: レビュー粒度を小さく保ち、人間と AI の両方のレビュー精度を上げる
- **マージキュー**: main を壊さずに並列マージを捌き、1日8回デプロイを構造的に成立させる
- **Graphite Agent**: AI が量産した PR を AI が1次審査する

逆に言えば、AI エージェントに大量のコードを書かせる前提がないチームでは、Graphite の真価は出にくい。**AIファーストのハーネスを組む時に検討するツール**、というのが2026年時点での正しいポジショニングだろう。

## 導入時のチェックリスト

- [ ] 既存 PR フローで「レビューが重い」「main がよく壊れる」など具体的な痛みがあるか
- [ ] Team プラン以上（マージキュー込み）を使う予算があるか
- [ ] `gt` CLI を使うか、GitHub 公式の UI だけで回すか（CLI 導入なしでも Web UI から基本機能は使える）
- [ ] 既存の GitHub Actions ワークフローがリベース再実行に耐えるか（環境変数・ベースブランチ参照など）
- [ ] AIレビューのコメント量を許容できるか（ノイズ対策の Customization が必要になる）

## 関連記事

- [「AIファースト」戦略の本当の意味 — ハーネスエンジニアリングで25人チームが6週間を1日に短縮した方法](/blogs/posts/2026/04/2026-04-17-ai-first-harness-engineering-creao/)

## 参考リンク

- [Graphite 公式サイト](https://graphite.com/)
- [Graphite Docs: Stacked PRs](https://graphite.com/docs/stacked-prs)
- [Graphite Docs: Merge Queue](https://graphite.com/docs/graphite-merge-queue)
- [How we built the first stack-aware merge queue (Graphite Blog)](https://graphite.com/blog/the-first-stack-aware-merge-queue)
- [Graphite raises $52M and launches Diamond](https://graphite.com/blog/series-b-diamond-launch)
- [Diamond — agentic AI code review](https://diamond.graphite.dev/)
