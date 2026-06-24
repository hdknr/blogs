---
title: "Ponytail — AIエージェントを「怠惰なシニア開発者」にするプラグイン"
date: 2026-06-24
lastmod: 2026-06-24
slug: "ponytail-ai-agent-minimal-code"
draft: false
source_url: "https://github.com/hdknr/blogs/issues/1#issuecomment-4785353161"
categories: ["AI/LLM"]
tags: ["ponytail", "claude-code", "ai-agent", "yagni", "ツール/開発環境"]
---

AIエージェントに簡単なタスクを頼んだはずが、500行のコードが返ってきた——そんな経験はないだろうか。**Ponytail** はそれを解決するためのオープンソースプラグインだ。MITライセンスで公開され、すでに54,000以上のスターを集めている。

## Ponytail とは何か

[Ponytail](https://github.com/DietrichGebert/ponytail) は、AIエージェントに「ラダー（梯子）」と呼ばれる意思決定フローを組み込み、コードを書く前に本当に必要かどうかを確認させるプラグインだ。

名前の由来は、どのチームにもいる「あのシニア開発者」のイメージ——長いポニーテール、楕円形の眼鏡、バージョン管理システムよりも長くその会社にいる人物。50行のコードを見せると、一言も言わずに1行に置き換えてくれる。

**Ponytail はそのシニアをAIエージェントの中に宿らせる。**

## 7段のラダー

コードを書く前に、エージェントはこの順序で判断する：

```
1. これは本当に必要か？           → 不要なら: スキップ (YAGNI)
2. このコードベースに既にある？    → あれば再利用、書き直しは不要
3. 標準ライブラリで対応できる？    → できるなら使う
4. プラットフォームのネイティブ機能？ → あれば使う
5. インストール済みの依存ライブラリ？ → あれば使う
6. 1行で書ける？                  → 1行で書く
7. 上記すべてが該当しない時のみ: 最小限のコードを書く
```

このラダーは「問題を理解する」より前には走らない。まずコードを読んで実際のフローを把握し、その上で梯子を登る。エージェントは解決策の選択には怠惰だが、理解することには手を抜かない。

### 典型例：日付ピッカー

通常のエージェントに日付ピッカーを依頼すると、flatpickr をインストールし、ラッパーコンポーネントを書き、スタイルシートを追加し、タイムゾーンについて議論を始める。

Ponytail を使うと：

```html
<!-- ponytail: ブラウザにネイティブ機能がある -->
<input type="date">
```

## ベンチマーク結果

実際の Claude Code セッションで計測した結果（モデル: Haiku 4.5 / 対象: FastAPI + React の OSS リポジトリ / 12タスク、n=4）：

| 比較対象 | コード行数 | トークン数 | コスト | 時間 | 安全性 |
|---|--:|--:|--:|--:|--:|
| **ponytail** | **-54%** | **-22%** | **-20%** | **-27%** | **100%** |
| caveman（制御群） | -20% | +7% | +3% | +2% | 100% |
| "YAGNI + 1行" プロンプト | -33% | -14% | -21% | -30% | 95% |

※安全性：検証・エラーハンドリング・セキュリティ・アクセシビリティが維持されたタスクの割合。

Ponytail だけがすべての指標を削減し、かつ安全性を100%に保った唯一のアプローチだ。「1行で書け」という単純なプロンプトは安全性が95%に下がるが、Ponytail はこれらの品質要素を決してカットしない。

## コマンド

| コマンド | 説明 |
|---|---|
| `/ponytail [lite \| full \| ultra \| off]` | 強度の設定または現在のレベルを確認 |
| `/ponytail-review` | 現在の diff を過剰エンジニアリングの観点でレビュー |
| `/ponytail-audit` | リポジトリ全体を監査 |
| `/ponytail-debt` | 後回しにした `ponytail:` ショートカットを一覧化 |
| `/ponytail-gain` | ベンチマークによる効果スコアボードを表示 |
| `/ponytail-help` | コマンドのクイックリファレンス |

## インストール方法

### Claude Code

```
/plugin marketplace add DietrichGebert/ponytail
```

```
/plugin install ponytail@ponytail
```

2つのプロンプトを別々に送る必要がある（同時送信は不可）。デスクトップアプリの場合は UI から「Customize」→「+ by personal plugins」→「Create plugin and add marketplace」→「Add from repository」でリポジトリURLを入力する。

### Cursor / Windsurf / Cline / GitHub Copilot（エディタ）

リポジトリから対応するルールファイルをコピーする：

- Cursor: `.cursor/rules/`
- Windsurf: `.windsurf/rules/`
- Cline: `.clinerules/`
- GitHub Copilot: `.github/copilot-instructions.md`

### Codex

```bash
codex plugin marketplace add DietrichGebert/ponytail
codex
```

その後 `/plugins` でインストール、`/hooks` でライフサイクルフックを承認する。

### Gemini CLI

```bash
gemini extensions install https://github.com/DietrichGebert/ponytail
```

### OpenCode

`opencode.json` に追記する：

```json
{ "plugin": ["@dietrichgebert/ponytail"] }
```

## なぜ有効なのか

「最短のトークン数」が目標ではない。**タスクに必要なものだけを書く**が目標だ。結果としてコードが小さくなるのは、必要なものだけだから。パフォーマンスが向上するのは、書かないコードに関連するバグや CVE がゼロだからだ。

> "The best code is the code you never wrote."

このラダーは高度な推論モデル（GPT-5.5 など）では逆効果になる場合もあると README は正直に述べている。ラダーの各段を深く考えるためにトークンを費やすモデルでは、コストが増えることがある。使うモデルに合わせて検証してみるのが良い。

## まとめ

Ponytail は単なる「コードを短くするプロンプト」ではなく、エージェントの意思決定プロセスそのものを構造化するプラグインだ。AIエージェントが過剰なコードを返してきて困っている開発者には、試してみる価値がある。インストールも1コマンドで済む。

- GitHubリポジトリ: [DietrichGebert/ponytail](https://github.com/DietrichGebert/ponytail)
- ライセンス: MIT
- 対応エージェント: Claude Code, Cursor, GitHub Copilot, Aider, Codex, Gemini CLI, OpenCode など14種類以上
