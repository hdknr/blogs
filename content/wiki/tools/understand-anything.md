---
title: "Understand-Anything"
description: "コードベース・ナレッジベースを対話的なナレッジグラフに変える OSS の Claude Code プラグイン。Tree-sitter の構造解析と LLM エージェントの意味付けを分業し、結果を JSON として残してチームで共有する"
date: 2026-11-09
lastmod: 2026-11-09
aliases: ["understand-anything", "Understand Anything", "/understand", "Egonex-AI", "コードベースのナレッジグラフ"]
related_posts:
  - "/posts/2026/11/understand-anything-codebase-knowledge-graph/"
tags: ["claude-code", "知識グラフ", "Tree-sitter", "プラグイン", "OSS", "LLM Wiki"]
---

## 概要

Understand-Anything（`Egonex-AI/Understand-Anything`）は、コードベース・ナレッジベース・ドキュメントを、探索・検索・質問できる対話的なナレッジグラフに変えるオープンソースのプラグイン。MIT ライセンス、TypeScript 実装で、2026 年 11 月時点の GitHub スターは約 9 万。作者はジョージア工科大学の大学院生 Yuxiang Lin 氏（Lum1104）で、現在は Egonex-AI の Organization に移管されている。

スローガンは「Graphs that teach > graphs that impress」。複雑さを誇示するのではなく、部品の組み合わさり方を教えるグラフを目指す。考え方は**全体の理解を事前計算して残し、必要なときに検索して使い回す**こと。

## 詳細

### 主な機能

- **構造グラフ**: ファイル・関数・クラスをノードにし、クリックで要約と関係を表示
- **ドメインビュー**: コードを業務ドメイン・フロー・ステップに対応付ける
- **ガイドツアー**: 依存関係順のアーキテクチャのウォークスルーを自動生成
- **検索・質問**: 「認証を扱っているのはどこ？」のような意味での検索、`/understand-chat` での質問
- **差分の影響分析**: コミット前に変更の波及先を表示（`/understand-diff`）
- **ペルソナ適応 UI・レイヤー可視化・言語概念の解説**（ジェネリクスなど 12 パターン）
- **LLM Wiki のグラフ化**: `/understand-knowledge` に Karpathy 流の LLM Wiki を渡すと記事同士の関係をグラフにできる

Claude Code ではプラグインとしてネイティブに動き、Codex・Cursor・VS Code + GitHub Copilot・Gemini CLI・OpenCode・Cline・Kiro などにもインストーラーで対応する（Codex では呼び出しが `$understand`）。

### 仕組み：Tree-sitter と LLM の分業

- **Tree-sitter**（決定的）: 構文木から import / export・定義・呼び出し・継承といった構造上の事実を抽出する。同じ入力から毎回同じ出力が得られ、差分更新のフィンガープリントにも使う
- **LLM**（意味的）: 要約・タグ・レイヤー・業務ドメインへの対応付け・ツアーなど、パーサーには作れないものを生成する

`/understand` は `project-scanner` → `file-analyzer`（最大 5 並列、1 バッチ 20〜30 ファイル）→ `architecture-analyzer` → `tour-builder` → `graph-reviewer` の 5 エージェントで動く。`/understand-domain` では `domain-analyzer`、`/understand-knowledge` では `article-analyzer` が加わる。

### グラフの中身

成果物は `.ua/knowledge-graph.json` 1 ファイル。`project`（解析時の git コミットハッシュを含む）、`nodes`（27 種類。コードに加え `endpoint`・`table`・`domain`・`flow` など）、`edges`（38 種類。`imports`・`calls`・`reads_from`・`tested_by` など）、`layers`、`tour` を持つ。各ノードには場所、**LLM が書いた要約**、タグ、複雑度が入る。

`/understand-chat` と `/understand-diff` は「グラフをまるごと読まず Grep で必要な部分だけ引く」手順書で、要約も検索対象になるため識別子に現れない言葉でも手がかりになる。どちらも最初に、記録されたコミットと HEAD の差分で**グラフの古さを検知して警告**する。

### 普段のエージェント作業との違いと限界

| | エージェントとの対話 | Understand-Anything |
|---|---|---|
| 解析の範囲 | 依頼に要る箇所だけその都度 | リポジトリ全体を一度に |
| 寿命 | セッション限り | JSON として残り差分更新 |
| 共有 | 本人の会話の中だけ | コミットすればチーム全員、閲覧に LLM 不要 |

- **普段の作業では自動参照されない**: MCP サーバーや読み取りフックはない。通常の依頼を効率化したいなら、MCP でグラフを引かせる [CodeGraph](/blogs/wiki/tools/codegraph/) のような道具のほうが目的に合う
- **省けるのは主に意味の理解**: import 関係は grep でも拾える。高くつく「何のためのファイルか」を要約として事前計算している
- **影響分析は 1 段先まで**: 間接的な呼び出し元は自動でたどらない
- **元が取れるかは使う回数しだい**: 初回解析はまとまったトークンを使う。README はサブスクリプションでの実行や、Ollama などローカルモデルへの切り替えを勧める。2 回目以降は差分解析

### チームでの共有と更新運用

`.ua/` をコミットすれば、他のメンバーはパイプラインを回さずに済む（`.ua/intermediate/` と `.ua/diff-overlay.json` は `.gitignore`、10MB 超は git-lfs 推奨）。コミット済みグラフは Node.js 18 以上だけで、トークン付きのローカル URL から読み取り専用で閲覧できる。

`--auto-update` の実体は git フックではなく **Claude Code のプラグインフック**。PostToolUse（Claude Code が `git commit` などを実行したとき）と SessionStart（記録コミットと HEAD のずれ検知）で差分更新を指示する。人がターミナルで打ったコミットや GitHub 上のマージでは発火せず、並行 PR がそれぞれ大きな JSON を更新すると衝突しやすい。

ソース記事の筆者の見解は、**機能 PR にはグラフ更新を含めず、マージ後の main で定期的またはリリース前に作り直してグラフだけの PR にする**運用。古い間は鮮度チェックの警告に頼り、`--auto-update` は個人作業向き。

## 関連ページ

- [CodeGraph](/blogs/wiki/tools/codegraph/) — MCP 経由でエージェントに引かせるコード知識グラフ
- [LLM Wiki パターン](/blogs/wiki/concepts/llm-wiki-pattern/) — `/understand-knowledge` でグラフ化できる知識ベースの手法
- [OpenWiki / Code Wiki](/blogs/wiki/tools/openwiki/) — リポジトリから常設 Wiki 層を生成する、同じく「事前計算して残す」系の実装
- [Claude Code](/blogs/wiki/tools/claude-code/) — ネイティブ対応のプラグイン実行環境
- [Claude Code Hooks](/blogs/wiki/concepts/claude-code-hooks/) — `--auto-update` を支えるフックの仕組み
- [Brownfield リファクタリング](/blogs/wiki/concepts/brownfield-refactoring/) — 知らない大規模コードベースの把握

## ソース記事

- [Understand-Anything：コードベースを対話的なナレッジグラフにする Claude Code プラグイン](/blogs/posts/2026/11/understand-anything-codebase-knowledge-graph/) — 2026-11-04
