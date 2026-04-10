---
title: "AutoAgent — AIがAIを育てる自己改善エージェントOSSライブラリ"
date: 2026-04-05
lastmod: 2026-04-05
slug: "autoagent-self-improving-agents"
draft: false
source_url: "https://github.com/hdknr/blogs/issues/1#issuecomment-4189423123"
categories: ["AI/LLM"]
tags: ["agent", "llm", "python", "github", "claude"]
description: "AutoAgent は AI エージェントのハーネス（プロンプト・ツール・オーケストレーション）を AI 自身が自律的に改善する Python 製 OSS ライブラリ。24時間の最適化で SpreadsheetBench・TerminalBench 世界1位を達成。"
---

AIエージェントの性能を左右する「ハーネス」を、AI自身が自律的に改善するOSSライブラリ **AutoAgent** が公開されました。ハーネスとは、システムプロンプト・ツール・オーケストレーションから成るエージェントの構成一式のことです。24時間の自律最適化だけで、SpreadsheetBench と TerminalBench の2つのベンチマークで世界1位を達成しています。

## AutoAgent とは

AutoAgent は Kevin Gu 氏（Third Layer CTO）が開発したPython製OSSライブラリで、「AIがAIを育てる」仕組みを提供します。

従来、AIエージェントを実用レベルにするには、システムプロンプトの調整、ツールの追加、実行フローの設計といった「ハーネス設計」が不可欠でした。この作業は専門知識を要し、1つのハーネスに何日もかかることがあります。AutoAgent はこのハーネス設計をAI自身に任せることで、人間の手動チューニングを超える精度を実現しました。

- **GitHub**: [kevinrgu/autoagent](https://github.com/kevinrgu/autoagent)
- **ライセンス**: MIT
- **言語**: Python

## ベンチマーク結果

| ベンチマーク | スコア | 順位 |
|---|---|---|
| SpreadsheetBench | 96.5% | 1位 |
| TerminalBench（GPT-5スコア） | 55.1% | 1位 |

他のエントリーはすべて人間が手動チューニングしたものです。AutoAgentだけが自律的にこのスコアに到達しました。

## 仕組み: メタエージェントとタスクエージェント

AutoAgent は2つのAIの役割分担で動作します。

### メタエージェント（コーチ役）

ハーネスを改良することが仕事。タスクエージェントの失敗トレースを読み、プロンプト・ツール・オーケストレーションを書き換えます。

### タスクエージェント（選手役）

実際のタスクをこなすことが仕事。メタエージェントが設計したハーネスに従って作業を実行します。

### 最適化ループ

人間がやることは、AutoAgent の設定ファイル `program.md` にゴール（成功の定義）を書くだけです。あとはAIが24時間、以下のループを回します:

1. メタエージェントがハーネスを書き換える
2. タスクエージェントがタスクを実行する
3. スコアを測定する
4. 失敗トレースを分析し「なぜ失敗したか」を特定する
5. 改善なら採用、悪化なら元に戻す
6. 1に戻る

これを数千の並列サンドボックス（隔離された実行環境）で同時実行します。

## なぜAIのほうが上手く改善できるのか — 「モデル共感」

人間はどうしても自分の感覚でAIを設計してしまいます。しかし、AIは人間とは異なる思考回路で動いています。

同じモデル同士（例: Claude × Claude）でペアリングすると、コーチ（メタエージェント）は選手（タスクエージェント）の「失敗パターン」を自分ごととして理解できます。同じ重みを共有しているため、内側のモデルがどう推論するかを正確に把握できるのです。

AutoAgent の開発チームはこれを **「モデル共感（model empathy）」** と呼んでいます。実際に、Claude メタエージェント + Claude タスクエージェントの組み合わせは、Claude メタエージェント + GPT タスクエージェントの組み合わせよりも高い性能を示しました。

## プログラムされていない改善行動の創発

AutoAgent の最適化過程で、設計者が意図していなかった改善行動が自然に出現しました:

- **スポットチェック**: 小さな編集は単体タスクだけで検証し、反復を高速化
- **強制検証ループ**: 自己修正ターンをバジェットに組み込む
- **自前テスト作成**: タスクエージェントが自分でユニットテストを書く
- **プログレッシブ開示**: 長いコンテキストはファイルに退避
- **サブエージェント生成**: ドメインに応じて自律的に役割分担

## Harbor — AutoAgent を支える評価フレームワーク

AutoAgent の自己改善ループを支えているのが [Harbor](https://github.com/harbor-framework/harbor) です。Harbor はエージェント評価と RL 環境の実行フレームワークで、AutoAgent とは以下のような役割分担になっています。

| コンポーネント | 役割 |
|---|---|
| **Harbor** | タスクの実行環境を提供。Docker コンテナ内でエージェントを動かし、テストスクリプトがスコア（0.0〜1.0）を出力する |
| **AutoAgent** | Harbor が返すスコアを見て、ハーネス（`agent.py`）を自動改善する |

つまり **Harbor = 評価インフラ**、**AutoAgent = その上で自己改善するレイヤー** という関係です。Harbor がなければスコアを測定できず、メタエージェントは改善の方向を判断できません。

タスクは Harbor のフォーマットに従って `tasks/` ディレクトリに配置します。各タスクには、エージェントへの指示（`instruction.md`）と検証ロジック（`tests/`）が含まれます。

```text
tasks/my-task/
  task.toml           -- 設定（タイムアウト等）
  instruction.md      -- エージェントに送るプロンプト
  tests/
    test.sh           -- エントリポイント
    test.py           -- 検証ロジック
  environment/
    Dockerfile        -- タスクコンテナ（FROM autoagent-base）
  files/              -- コンテナにマウントするファイル
```

## クイックスタート

AutoAgent を試すには、Docker、Python 3.10 以上、[uv](https://docs.astral.sh/uv/) が必要です。

### 1. インストール

```bash
# uv のインストール（未導入の場合）
curl -LsSf https://astral.sh/uv/install.sh | sh

# 依存関係のインストール
uv sync
```

### 2. 環境変数の設定

使用する LLM プロバイダーの API キーを `.env` に設定します。

```bash
cat > .env << 'EOF'
OPENAI_API_KEY=...
EOF
```

### 3. Docker ベースイメージのビルド

```bash
docker build -f Dockerfile.base -t autoagent-base .
```

### 4. タスクの準備と実行

```bash
# 単一タスクの実行
uv run harbor run -p tasks/ --task-name "<task-name>" -l 1 -n 1 \
  --agent-import-path agent:AutoAgent -o jobs --job-name latest

# 全タスクを並列実行（-n = 並列数）
uv run harbor run -p tasks/ -n 100 \
  --agent-import-path agent:AutoAgent -o jobs --job-name latest
```

前述の Harbor セクションで説明したフォーマットで `tasks/` にタスクを配置した上で実行します。

### 5. メタエージェントの起動

コーディングエージェント（Claude Code 等）でリポジトリを開き、以下のプロンプトを実行します:

```
Read program.md and let's kick off a new experiment!
```

メタエージェントが `program.md` の方針を読み、ハーネス（`agent.py`）の改善ループを自律的に開始します。

### プロジェクト構成

```text
agent.py          -- ハーネス本体（メタエージェントの編集対象）
program.md        -- メタエージェントへの方針指示（人間が編集）
Dockerfile.base   -- ベースイメージ
.agent/           -- エージェントのワークスペース（スキル・メモ等）
tasks/            -- 評価タスク
jobs/             -- 実行結果
results.tsv       -- 実験ログ
```

ポイントは **`agent.py` を人間が直接編集しない** ことです。人間は `program.md` にメタエージェントへの方針を書き、ハーネスの改善はメタエージェントに任せます。

## 実務への示唆

AutoAgent のアプローチは、日常的なAIエージェント運用にも応用可能です:

- **Cron定期実行**: Claude Code の `CLAUDE.md` やスキル定義を定期的にAIに見直させることで、近い効果が得られる可能性がある
- **エージェント群のインフラ**: 企業には自動化すべきワークフローが数百存在します。それぞれに異なるハーネスが必要ですが、人間チームが数百のハーネスを手動調整するのは現実的ではありません。メタエージェントならそれが可能です
- **ゴール定義の重要性**: 「成功の定義さえ与えれば、ハーネスはメタエージェントが考える」— これが AutoAgent の核心的メッセージ

## まとめ

AutoAgent は「エージェントを設計する」仕事を「エージェントに設計させる」仕事に変えるライブラリです。ハーネス設計という職人作業をAIが自動化できる時代が始まりつつあります。

OSSで公開されているため、自分のドメインで試すことができます。評価用のベンチマークとゴール定義を用意して、メタエージェントに最適化させてみましょう。

**参考リンク**:
- [AutoAgent GitHub リポジトリ](https://github.com/kevinrgu/autoagent)
- [Kevin Gu 氏の発表ポスト](https://x.com/kevingu/status/2039874388095651937)
- [MarkTechPost の解説記事](https://www.marktechpost.com/2026/04/05/meet-autoagent-the-open-source-library-that-lets-an-ai-engineer-and-optimize-its-own-agent-harness-overnight/)
