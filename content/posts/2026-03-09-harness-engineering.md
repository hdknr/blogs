---
title: "Harness Engineering ベストプラクティス 2026 — AI コーディングエージェントを安定稼働させる設計術"
date: 2026-03-09
lastmod: 2026-03-09
draft: false
source_url: "https://github.com/hdknr/blogs/issues/1#issuecomment-4022922774"
categories: ["AI/LLM"]
tags: ["claude-code", "agent", "typescript", "python", "github"]
---

Claude Code や Codex といった AI コーディングエージェントを現場に投入する開発者が増えるなか、「ハーネスエンジニアリング」という新しい実践領域が注目を集めている。逆瀬川氏（[@gyakuse](https://x.com/gyakuse)）が公開した[まとめ記事](https://nyosegawa.github.io/posts/harness-engineering-best-practices-2026/)から、要点を紹介する。

## ハーネスとは何か

ハーネスエンジニアリングとは、AI コーディングエージェントが確実に動作する**環境・仕組み**を設計する技術のことだ。核心的な洞察は「ハーネスがモデルより重要」という点にある。同じモデルでもハーネスを改善すれば出力品質が劇的に向上する。責任の所在が「正しいコードを書く」から「エージェントが確実に正しいコードを生産する環境を設計する」へとシフトしている。

## 7 つの主要トピック

### 1. リポジトリ衛生

- 実行可能なアーティファクト（コード、テスト、設定）を優先する
- 説明的ドキュメントは腐敗しやすいため最小化する
- ADR（Architecture Decision Records）で決定履歴を保全する
- テストはドキュメントより腐敗に強い

最大の敵は「説明的ドキュメントの腐敗」だ。エージェントは「3 ヶ月前のメモ」と「現在の真実」を区別できないため、古い情報が存在するだけで性能が低下する。

### 2. 決定論的ツールで品質を強制する

リンター・フォーマッターは LLM より信頼性が高い。PostToolUse Hook でファイル編集のたびにリンターを実行し、エラーをエージェントに即時フィードバックする。

言語別の推奨スタック:

| 言語 | PostToolUse | プリコミット | カスタムルール |
|------|-----------|----------|-----------|
| TypeScript | Biome + Oxlint | tsc + ESLint | eslint-plugin-local-rules |
| Python | Ruff check/format | Ruff + mypy | ast-grep |
| Go | gofumpt + golangci-lint | 同左 | ast-grep |

リンター設定の保護も重要だ。エージェントがルールを勝手に緩和・改ざんするのを防ぐ仕組みが必要になる。

### 3. ポインタ設計の AGENTS.md / CLAUDE.md

- **50 行以下**を目標にする
- 詳細は別ファイルに分離し、参照のみ記述する
- 記述的説明ではなくルーティング指示に集中する

### 4. 計画と実行の分離

- 計画段階を人間がレビューする
- 一度に複数機能に取り組まない
- テストで完了を検証する

### 5. E2E テスト戦略

各領域ごとの推奨ツール:

- **Web**: アクセシビリティツリー（Playwright CLI / agent-browser）
- **Mobile**: mobile-mcp、XcodeBuildMCP
- **CLI**: bats-core、expect
- **API**: Hurl、Pact
- **Infrastructure**: terraform test、conftest
- **AI/ML**: lm-evaluation-harness、DeepEval、RAGAS

ユニバーサル原則は「構造化テキストで検証し、決定論的に実行可能にする」こと。

### 6. セッション間の状態管理

- 起動ルーティンを標準化する
- Git ログとコミットメッセージで前回状態を記録する
- 進捗は JSON で機械的に解析可能な形式にする

### 7. Codex vs Claude Code

- **Claude Code**: Hooks で毎回のツール実行を介入可能（品質重視）
- **Codex**: クラウドサンドボックスで非同期並列実行（スループット重視）
- 実装パターンによってはハイブリッド構成も有効

## MVH（Minimum Viable Harness）ロードマップ

段階的に導入するためのロードマップ:

- **Week 1**: AGENTS.md 作成、プリコミットフック導入、PostToolUse Hook 設定
- **Week 2-4**: テスト追加、計画→実行ワークフロー確立、E2E テスト導入
- **Month 2-3**: カスタムリンター構築、記述ドキュメント削減
- **Month 3+**: 高度なフィードバックループ、複数エージェント管理

## まとめ

「コンテキスト内で発見できないものは存在しないのと同じ」であり、「リポジトリ内で発見できる古い情報は最新の真実と区別不可能」。このジレンマを理解した上で、実行可能なアーティファクトと決定論的ツールを中心にハーネスを設計することが、AI コーディングエージェント時代の開発者に求められるスキルだ。

## 参考

- [Harness Engineering ベストプラクティス 2026年版](https://nyosegawa.github.io/posts/harness-engineering-best-practices-2026/) — 逆瀬川氏による原文
- [元ツイート](https://x.com/gyakuse/status/2030897233089204230)
