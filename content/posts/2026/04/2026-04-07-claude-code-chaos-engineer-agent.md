---
title: "Claude Code にカオスエンジニアリングエージェントを導入してリポジトリの弱点を発見する"
date: 2026-04-07
lastmod: 2026-04-07
draft: false
source_url: "https://github.com/hdknr/blogs/issues/1#issuecomment-4198086645"
categories: ["ツール/開発環境"]
tags: ["Claude Code", "カオスエンジニアリング", "AIエージェント", "セキュリティ", "開発効率化"]
---

Claude Code のカスタムエージェント機能を使って「カオスエンジニア」を導入すると、リポジトリの潜在的な弱点を自動的に発見できる。`.md` ファイルを1つ置くだけで有効化でき、驚くほど多くの問題が見つかることで話題になっている。

## カオスエンジニアリングとは

カオスエンジニアリングは、本番システムに意図的に障害を注入してシステムの耐障害性を検証する手法だ。Netflix が提唱した概念で、`Chaos Monkey` のような自動障害注入ツールが知られている。

Claude Code にカオスエンジニアリングの思考を持ったエージェントを持ち込むと、コードベースに対して「もし〇〇が壊れたら？」という視点で弱点分析を行ってくれる。

## 導入方法

Claude Code のカスタムエージェントは `.claude/agents/` ディレクトリに `.md` ファイルを置くだけで使える。

以下が chaos-engineer エージェントの定義例だ:

```markdown
# chaos-engineer

あなたはカオスエンジニアリングの専門家です。
システムに意図的に障害を起こす視点でリポジトリを分析し、
潜在的な弱点・単一障害点・エラーハンドリングの欠如を特定してください。

## 分析観点

- 単一障害点（SPOF）の特定
- エラーハンドリングの欠如箇所
- タイムアウト設定の不備
- リトライ処理の欠如
- 環境変数・設定値のハードコーディング
- 依存サービスがダウンした場合の挙動
- データ整合性が保証されない処理
- テストカバレッジが低い重要処理

## 出力形式

各問題について以下を明記する:
- 問題箇所（ファイルパス・行番号）
- 障害シナリオ
- 影響範囲
- 推奨する対策
```

このファイルを `.claude/agents/chaos-engineer.md` として保存する。

## 使い方

エージェントを配置したら、Claude Code のチャットで以下のように指示するだけだ:

```
chaos-engineer を使ってこのリポジトリの弱点を分析して
```

Claude Code が chaos-engineer エージェントを呼び出し、リポジトリ全体を「壊す側の視点」でスキャンして問題点を列挙してくれる。

## 実際に見つかる問題の例

カオスエンジニアの視点でスキャンすると、通常のコードレビューでは見落としがちな問題が浮かび上がる:

### 1. エラーハンドリングの欠如

```javascript
// 問題のあるコード
const data = await fetch('/api/data');
const json = await data.json();

// 改善後
const response = await fetch('/api/data');
if (!response.ok) {
  throw new Error(`API error: ${response.status}`);
}
const json = await response.json();
```

### 2. タイムアウト未設定

```python
# 問題のあるコード
requests.get('https://external-api.example.com/data')

# 改善後
requests.get('https://external-api.example.com/data', timeout=10)
```

### 3. 環境変数の検証不足

```python
# 問題のあるコード
API_KEY = os.environ['API_KEY']  # KeyError で即クラッシュ

# 改善後
API_KEY = os.environ.get('API_KEY')
if not API_KEY:
    raise ValueError("API_KEY environment variable is required")
```

### 4. データベース接続の単一障害点

接続プールの設定がなく、DB がダウンすると全リクエストが詰まるケース。

### 5. リトライ処理の欠如

外部 API 呼び出しで一時的なネットワークエラーが起きると即エラーになる処理。

## `.claude/agents/` の仕組み

Claude Code のカスタムエージェントは、プロジェクトルートの `.claude/agents/` に置いた Markdown ファイルで定義できる。各エージェントは:

- **専用のシステムプロンプト**を持つ
- **特定のツール**だけを使う権限を持てる
- **並列実行**も可能

```
.claude/
└── agents/
    ├── chaos-engineer.md    # カオスエンジニア
    ├── security-reviewer.md # セキュリティレビュー
    └── performance-analyst.md # パフォーマンス分析
```

目的別のエージェントを複数定義しておくと、コードレビューの幅が大きく広がる。

## まとめ

Claude Code のカスタムエージェント機能を使ったカオスエンジニアリングは、手軽に試せる割に発見できる問題の量が多く、実際に試した開発者から驚きの声が上がっている。

`.md` ファイルを1つ置くだけで有効化できるため、既存プロジェクトへの導入コストがほぼゼロなのも魅力だ。テストカバレッジが低いプロジェクトや、エラーハンドリングが甘いと感じているコードベースにぜひ試してみてほしい。
