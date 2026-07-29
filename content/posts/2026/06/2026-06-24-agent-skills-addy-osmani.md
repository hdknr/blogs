---
title: "「動くけど雑」なAIコードを卒業する — Addy Osmaniの agent-skills"
date: 2026-06-24
lastmod: 2026-06-24
slug: "agent-skills-addy-osmani"
draft: false
source_url: "https://github.com/hdknr/blogs/issues/1#issuecomment-4785289375"
categories: ["AI/LLM"]
tags: ["claude-code", "agent-skills", "AIエージェント", "tdd", "コード品質"]
---

AIにコードを書かせると「動くけど雑」になりがちだ。テストが抜ける、セキュリティレビューが飛ぶ、コミット粒度が荒い——AIは最短経路を取るので、ベテランエンジニアが当たり前にやっている手順を省略してしまう。

元Google Director（Google Cloud AI担当）のAddy Osmaniがその問題への解法として公開したのが **[agent-skills](https://github.com/addyosmani/agent-skills)** だ。本番品質のエンジニアリングスキルをAIコーディングエージェントに仕込むためのオープンソースパック。GitHubスター数は6.6万を超えている（2026-06-24現在）。

## agent-skills とは

agent-skills はAIエージェントに「ベテランの作業手順と品質ゲート」を埋め込むためのスキル集だ。スキルは構造化されたワークフローとして記述されており、AIが一貫した品質で作業を進められるようにする。

開発ライフサイクルの6フェーズ（DEFINE → PLAN → BUILD → VERIFY → REVIEW → SHIP）を全てカバーし、各フェーズで適切なスキルが自動的に起動する設計になっている。

## スキルの仕組み

各スキルは一貫した構造（SKILL.md）で記述されている。

- **Frontmatter** — スキル名と適用条件（いつ使うか）
- **Overview** — このスキルが何をするか
- **When to Use** — 起動条件
- **Process** — ステップバイステップのワークフロー
- **Rationalizations** — よくある言い訳と反論
- **Red Flags** — 問題のサイン
- **Verification** — エビデンス要件

**重要な設計原則：**

- **プロセスであって参照ドキュメントではない** — スキルはエージェントが従うワークフローであり、読むだけの資料ではない。各ステップにチェックポイントと終了基準がある。
- **合理化への対抗** — 「後でテストを追加する」などエージェントがステップを飛ばすときによく使う言い訳とその反論が各スキルに組み込まれている。
- **検証は必須** — すべてのスキルはエビデンス要件で終わる。「たぶん大丈夫」は許容されない。
- **プログレッシブディスクロージャー** — `SKILL.md` がエントリーポイント。補助的な参考資料は必要なときだけ読み込み、トークン消費を最小化する。

## 8つのスラッシュコマンド

開発ライフサイクルに対応した8つのスラッシュコマンドが用意されている。

| コマンド | 目的 | キー原則 |
|---------|------|---------|
| `/spec` | 何を作るかを定義する | コードの前にスペックを書く |
| `/plan` | どう作るかを計画する | 小さくアトミックなタスクに分解 |
| `/build` | インクリメンタルに実装する | 一度に一スライスずつ |
| `/test` | 動作を証明する | テストは証拠 |
| `/review` | マージ前にレビューする | コード健全性を高める |
| `/webperf` | Webパフォーマンスを監査する | 最適化の前に計測する |
| `/code-simplify` | コードをシンプルにする | 賢さより明快さ |
| `/ship` | 本番にデプロイする | 速さが安全性につながる |

`/build auto` を使うと、スペックがある状態から計画の生成と全タスクの実装を一度の承認で自動実行できる。各タスクはテスト駆動でコミットされる。失敗や危険なステップでは自動的に一時停止する。

## 24のスキル

コマンドはエントリーポイントに過ぎない。agent-skills には合計24のスキル（ライフサイクルスキル 23 + メタスキル 1）が含まれており、作業内容に応じて自動的に適切なスキルが選ばれる。

### Define（定義）

| スキル | 役割 |
|-------|------|
| `interview-me` | 1問ずつ質問してユーザーが本当に欲しいものを引き出す |
| `idea-refine` | 漠然としたアイデアを具体的な提案に絞り込む |
| `spec-driven-development` | PRDをコードより先に書く |

### Plan（計画）

| スキル | 役割 |
|-------|------|
| `planning-and-task-breakdown` | スペックを小さく検証可能なタスクに分解し、依存順に並べる |

### Build（実装）

| スキル | 役割 |
|-------|------|
| `incremental-implementation` | 薄い垂直スライスで実装・テスト・コミットを繰り返す |
| `test-driven-development` | Red-Green-Refactor、テストピラミッド（ユニット80%・統合15%・E2E5%） |
| `context-engineering` | 適切な情報を適切なタイミングでエージェントに提供する |
| `source-driven-development` | 公式ドキュメントに根ざしたフレームワーク決定 |
| `doubt-driven-development` | 高リスクな決定を別の視点（新しいコンテキスト）から批判的に再検証する |
| `frontend-ui-engineering` | コンポーネント設計、状態管理、WCAG 2.1 AAアクセシビリティ |
| `api-and-interface-design` | コントラクトファースト設計、Hyrum's Law対応 |

### Verify（検証）

| スキル | 役割 |
|-------|------|
| `browser-testing-with-devtools` | Chrome DevTools MCPでライブランタイムデータを活用 |
| `debugging-and-error-recovery` | 5ステップのトリアージ（再現・局所化・縮小・修正・ガード） |

### Review（レビュー）

| スキル | 役割 |
|-------|------|
| `code-review-and-quality` | 5軸レビュー、1PRあたりの変更量の目安（約100行）、重大度ラベル |
| `code-simplification` | Chesterton's Fence、Rule of 500 |
| `security-and-hardening` | OWASP Top 10防止、認証パターン、シークレット管理 |
| `performance-optimization` | Core Web Vitals目標、プロファイリングワークフロー |

### Ship（リリース）

| スキル | 役割 |
|-------|------|
| `git-workflow-and-versioning` | トランクベース開発、アトミックコミット |
| `ci-cd-and-automation` | Shift Left、フィーチャーフラグ、品質ゲートパイプライン |
| `deprecation-and-migration` | コードを負債として扱う、マイグレーションパターン |
| `documentation-and-adrs` | Architecture Decision Records、APIドキュメント標準 |
| `observability-and-instrumentation` | 構造化ログ、REDメトリクス、OpenTelemetryトレーシング |
| `shipping-and-launch` | ローンチ前チェックリスト、段階的ロールアウト、ロールバック手順 |

## 4つのエージェントペルソナ

スキルがワークフローを定義するのに対し、エージェントペルソナは特定のレビュータスクに特化した役割として動作する。

| エージェント | 役割 |
|------------|------|
| `code-reviewer` | シニアスタッフエンジニア視点の5軸コードレビュー |
| `test-engineer` | テスト戦略、カバレッジ分析、Prove-Itパターン |
| `security-auditor` | 脆弱性検出、脅威モデリング、OWASP評価 |
| `web-performance-auditor` | Core Web Vitals監査（クイック/ディープモード） |

## インストール方法

### Claude Code（推奨）

Marketplace経由でインストールできる。

```bash
/plugin marketplace add addyosmani/agent-skills
/plugin install agent-skills@addy-agent-skills
```

Marketplace のデフォルトは SSH 接続のため、SSH 鍵が設定されていない場合は代わりに HTTPS URL を指定する。

```bash
/plugin marketplace add https://github.com/addyosmani/agent-skills.git
/plugin install agent-skills@addy-agent-skills
```

ローカルでの使用も可能。

```bash
git clone https://github.com/addyosmani/agent-skills.git
claude --plugin-dir /path/to/agent-skills
```

### Cursor

任意の `SKILL.md` を `.cursor/rules/` にコピーするか、`skills/` ディレクトリ全体を参照する。

### Gemini CLI

```bash
gemini skills install https://github.com/addyosmani/agent-skills.git --path skills
```

他にも Windsurf、GitHub Copilot、Kiro IDE など主要なAIコーディングツールに対応している。

## Googleエンジニアリング文化の実践

agent-skills はGoogleのエンジニアリング文化からのベストプラクティスを体系化している。これらは抽象的な原則ではなく、AIが実際に従うステップバイステップのワークフローに組み込まれている。

- **Hyrum's Law** — APIと依存関係の設計に組み込まれている（`api-and-interface-design`）
- **ベイヨンセルール** — 「壊れたくなければテストを書け」というテスト戦略に反映（`test-driven-development`）
- **テストピラミッド** — ユニット80%・統合15%・E2E5%の配分
- **Chesterton's Fence** — コード簡素化スキルに組み込まれている。変更前に存在理由を理解せよという原則（`code-simplification`）
- **トランクベース開発** — Gitワークフロースキルの基本方針（`git-workflow-and-versioning`）
- **Shift Left** — CI/CDスキルの中核原則。テストと品質チェックを開発プロセスの早期に移動する（`ci-cd-and-automation`）

## まとめ

agent-skills は、ベテランエンジニアの判断と手順をAIが従えるワークフローとして体系化したパックだ。Claude Code、Cursor、Gemini CLI など主要ツールに対応しており、インストールも数コマンドで済む。「動くだけで雑なコード」から脱したいなら、まず `/spec` と `/test` の2コマンドだけ取り込んで試してみることをすすめる。

- リポジトリ: [addyosmani/agent-skills](https://github.com/addyosmani/agent-skills)
