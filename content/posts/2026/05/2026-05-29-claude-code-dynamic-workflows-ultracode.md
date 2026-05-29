---
title: "Claude Code の「Dynamic Workflows」を冷静に検証 — Opus 4.8 + /ultracode で本当に変わること・誇張されていること"
date: 2026-05-29
lastmod: 2026-05-29
slug: "claude-code-dynamic-workflows-ultracode"
draft: false
source_url: "https://github.com/hdknr/blogs/issues/1#issuecomment-4573497661"
description: "Claude Code の Dynamic Workflows と /effort ultracode を公式仕様と実機挙動で検証。サブエージェントの並列オーケストレーション・敵対的検証の実体と、\"全自動で自走\" というバイラル投稿の誇張を切り分ける。"
categories: ["AI/LLM"]
tags: ["claude-code", "サブエージェント", "ワークフロー", "並列実行", "AIエージェント"]
---

## はじめに

X（旧 Twitter）でこんな投稿が流れてきました。

> 【衝撃】Claude Code でとんでもないモードが解禁👀
> Opus 4.8 ＋ /ultracode で有効になる新機能「Dynamic Workflows」！
> ・タスク難易度を自動検知
> ・オーケストレーション用スクリプトを生成
> ・複数エージェントに役割分担
> ・検証フローまで自動構築
> ・エージェントスウォームで並列実行
> つまり開発フローの全工程を Claude が自走。

「人間はゴールを投げるだけ、Claude Code が PM ＋ 開発チームを自動編成して並列実行する」——確かにインパクトのある話です。

ただ、こういうバイラル投稿は機能を**過度に一般化**しがちです。本記事では、`/ultracode` と Dynamic Workflows の実体を公式ドキュメントと実機の挙動から整理します。そのうえで「本当に変わること」と「誇張されていること」を切り分けます。結論から言うと、**機能はほぼすべて実在しますが、"完全自動" ではありません**。

## Dynamic Workflows とは何か

Dynamic Workflows は、Claude Code が**複数のサブエージェントを JavaScript スクリプトで決定論的にオーケストレーションする**機能です。現在は research preview（研究プレビュー）として提供されています。

![Claude Code の Dynamic Workflows のオーケストレーション構造を示す図。左にユーザーのオプトイン起動経路（プロンプトに workflow、/effort ultracode、専用コマンド、保存済みワークフロー）、中央に phase/agent/parallel/pipeline を持つ JS ワークフロースクリプト、右に並列レビューフェーズと敵対的検証フェーズ、下に統合結果と /workflows による進捗監視を配置している](/blogs/images/claude-code-dynamic-workflows-orchestration.png)

ポイントは「決定論的」という部分です。通常のエージェントはモデルが自分の判断で次の手を決めますが、Workflow ではループ・分岐・ファンアウト（並列展開）といった制御フローを**スクリプトで明示的に記述**します。「何を並列にやるか」「何を検証するか」「何を統合するか」を人間（あるいは Claude）がコードとして固定できるわけです。

スクリプトは `export const meta = {...}` で始まり、本体で以下のような構成要素を使います。

- `phase(title)` — フェーズ（工程）を区切る
- `agent(prompt, opts)` — サブエージェントを 1 体起動する
- `parallel(thunks)` — 複数タスクを並列実行する（全完了を待つバリア）
- `pipeline(items, stage1, stage2, ...)` — 各アイテムを複数ステージに流す（ステージ間でバリアなし）

これらは実際の Workflow ツールが提供する API です。最小の例を見てみましょう。

```javascript
export const meta = {
  name: 'review-changes',
  description: '変更ファイルを複数の観点でレビューし、各指摘を検証する',
  phases: [{ title: 'Review' }, { title: 'Verify' }],
}

// 観点ごとにレビュー → 見つかった指摘を並列で検証
const DIMENSIONS = [
  { key: 'bugs', prompt: 'バグや論理エラーを探して' },
  { key: 'perf', prompt: 'パフォーマンス問題を探して' },
]

const results = await pipeline(
  DIMENSIONS,
  d => agent(d.prompt, { label: `review:${d.key}`, phase: 'Review', schema: FINDINGS_SCHEMA }),
  review => parallel(review.findings.map(f => () =>
    agent(`次の指摘を敵対的に検証して: ${f.title}`, {
      label: `verify:${f.file}`, phase: 'Verify', schema: VERDICT_SCHEMA,
    }).then(v => ({ ...f, verdict: v }))
  ))
)

const confirmed = results.flat().filter(Boolean).filter(f => f.verdict?.isReal)
return { confirmed }
```

このスクリプトは「変更を観点別にレビュー → 各指摘を別のエージェントが敵対的に検証 → 本物だけ残す」というレビュー工程をコードで表現しています。`bugs` 観点の指摘が検証フェーズに進んでいる間に、`perf` 観点はまだレビュー中——という具合に、`pipeline` ならアイテムごとに独立して流れるので待ち時間が最小化されます。

## `/ultracode` の正体は「努力レベル」の設定

ここが投稿で最も誤解を生みやすいポイントです。

`/ultracode` は単独の魔法コマンドではなく、**`/effort ultracode`（努力レベルの設定）**です。`xhigh`（最大の推論努力）と「自動ワークフロー オーケストレーション」を組み合わせたモードで、これをオンにすると Claude が**複雑なタスクごとにワークフローを自動で計画・実行**するようになります。

つまり投稿の「タスク難易度を自動検知して自走する」という表現は、**ultracode をオンにしている間に限って**正しいわけです。デフォルトはオフであり、ユーザーがセッション全体に対して明示的にこのモードを有効化する必要があります。

```text
/effort ultracode    # セッション全体でワークフロー自動編成をオンにする
/effort high         # 通常の高努力モードに戻す
```

なお `xhigh` 努力をサポートするモデルが前提になります。Opus 4.8 はこれに該当しますが、「Opus 4.8 だけで有効になる」というより「対応モデル＋ ultracode 設定」の組み合わせ、と理解するのが正確です。

## ワークフローはこう起動する（4 つのオプトイン経路）

「全部自動」という印象とは裏腹に、ワークフローの起動は基本的に**ユーザーのオプトイン**です。経路は主に 4 つあります。

| 経路 | 起動方法 |
|:--|:--|
| キーワード | プロンプトに "workflow" という単語を含める |
| 努力レベル | `/effort ultracode` でセッション全体を自動編成モードに |
| 専用コマンド | `/deep-research` など、内部でワークフローを呼ぶコマンドを明示実行 |
| 保存済みワークフロー | 名前付きで保存したワークフローを呼び出す |

逆に言うと、これらのどれにも当てはまらないタスクでは、Claude は勝手に大量のエージェントを起動しません。Workflow は数十体のエージェントを生成しトークンを大量消費しうるため、**ユーザーがそのスケールを要求していること**が前提になっているのです。これは暴走防止の設計であり、むしろ安心材料です。

## 進捗の可視化：`/workflows`

走らせたワークフローは `/workflows` コマンドで監視できます。

- 実行中・完了済みのワークフローを一覧表示
- 各ワークフローのフェーズ、エージェント数、トークン使用量、経過時間を表示
- 個別エージェントの詳細にドリルダウン可能
- 矢印キー／Enter で移動、`p` で一時停止・再開、`x` で停止

「エージェントスウォームで並列実行」という投稿の表現に対応するのがこの画面です。ただし公式には "swarm（スウォーム）" という用語ではなく「background agents」「concurrent（並列）」と呼ばれます。並列実行数には上限があり、おおむね `min(16, CPUコア数 - 2)` 程度に制限されます。100 件渡しても同時に走るのは十数体です。残りは順次処理される、現実的な設計になっています。

## ワークフローが活きる典型パターン

研究プレビューのドキュメントが想定しているのは、「1 つのコンテキストでは持ちきれないスケール」や「複数視点で確証を得たい」タスクです。代表的なパターンを挙げます。

- **理解（Understand）** — 複数のリーダーが各サブシステムを並列で読み、構造マップに統合
- **設計（Design）** — N 個の独立した案を別々のエージェントが出し、採点して統合
- **レビュー（Review）** — 観点ごとに探索 → 各指摘を敵対的に検証
- **リサーチ（Research）** — 複数の検索モードでスイープ → 精読 → 引用付きで統合
- **マイグレーション（Migrate）** — 対象箇所を洗い出し → 各所を変換（worktree で隔離）→ 検証

### 敵対的検証（adversarial verify）

特に有効なのが**敵対的検証（adversarial verify）**です。1 つの指摘に対して複数の「懐疑役」エージェントを立て、それぞれに「この指摘を反証せよ」と指示し、過半数が反証したら棄却します。これにより、もっともらしいが間違っている指摘を排除できます。

```javascript
// 1 つの主張に対し 3 体の懐疑役で多数決
const votes = await parallel(Array.from({ length: 3 }, () => () =>
  agent(`次を反証せよ: ${claim}。確信が持てなければ refuted=true を既定とせよ。`, { schema: VERDICT })))
const survives = votes.filter(Boolean).filter(v => !v.refuted).length >= 2
```

## 投稿の主張を採点する

ファクトチェックの結果を表にまとめます。

| 投稿の主張 | 判定 | 補足 |
|:--|:--|:--|
| `/ultracode` が実在する | ✅ | 正確には `/effort ultracode`（努力レベル設定） |
| Dynamic Workflows が実在する | ✅ | research preview として提供 |
| オーケストレーション用スクリプトを生成 | ✅ | JS スクリプトで phase/agent/parallel/pipeline を記述 |
| 複数エージェントに役割分担 | ✅ | サブエージェントは独立コンテキスト・ツール制限を持てる |
| 検証フローまで自動構築 | ✅ | 敵対的検証などのパターンが標準的 |
| 並列実行（スウォーム） | ✅ | ただし上限あり・用語は "concurrent/background agents" |
| **タスク難易度を自動検知して全自動で自走** | ⚠️ | これが当てはまるのは `ultracode` オン時のみ。基本はオプトイン |

そのほか押さえておきたい注意点：

- **Dynamic Workflows は research preview** であり、提供プランやバージョンに制限がある場合があります。
- `/code-review` と `/simplify` は別物です。`/simplify` は品質改善（修正適用）専用で、バグ探索は行いません。バグ探索＋修正は `/code-review --fix` を使います。
- 投稿が挙げる `/simplify`・`/code-review`・Plugins・Hooks・Subagents・権限管理は**すべて実在**します。「思想レベルで変わってきている」という感想自体は妥当です。

## まとめ

バイラル投稿の主張は、**機能の実在性についてはほぼ正確**でした。Dynamic Workflows も `/ultracode`（`/effort ultracode`）も実在し、複数エージェントの並列オーケストレーションと検証フローの自動構築は本物です。

一方で、「人間はゴールを投げるだけで全自動」という部分は誇張です。実際には：

1. ワークフローの起動は**ユーザーのオプトイン**が基本（キーワード／`ultracode`／専用コマンド／保存済み）
2. 「タスク難易度を自動検知して全タスクをワークフロー化」するのは **`ultracode` モードをオンにしている間だけ**
3. 並列数には上限があり、研究プレビューゆえの**提供制限**もある

とはいえ、これは「がっかり」な話ではありません。むしろ、暴走的にエージェントとトークンを消費しないよう**意図的にオプトイン設計**になっているのは健全です。`/effort ultracode` を試すにせよ、プロンプトに "workflow" と入れて手動で起動するにせよ、まずは小さなレビューや調査タスクで `/workflows` の画面を眺めてみるのが、この新しいパラダイムを掴む一番の近道でしょう。

「進化が早すぎてついていけない」——その感覚は正常です。ただ、誇張に振り回されず一次情報で仕様を確かめる癖さえあれば、変化はちゃんと追えます。
