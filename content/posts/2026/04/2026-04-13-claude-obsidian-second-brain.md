---
title: "Claude × Obsidian で「第二の脳」を作る — LLM Wiki パターン入門"
date: 2026-04-13
lastmod: 2026-04-13
draft: false
source_url: "https://github.com/hdknr/blogs/issues/1#issuecomment-4239438413"
categories: ["AI/LLM"]
tags: ["claude", "claude-code", "obsidian", "llm", "rag"]
description: "Claude Code と Obsidian を組み合わせて LLM Wiki パターンで「第二の脳」を構築する方法を解説。RAG との違い、3層アーキテクチャ、セットアップ手順、実用ユースケースを紹介。"
---

Claude Code と Obsidian を組み合わせて「第二の脳」を構築する手法が、海外の X（旧 Twitter）で 1,000 万インプレッションを超えて話題になっています。ベースとなっているのは Andrej Karpathy 氏が提唱した **LLM Wiki パターン** — LLM にナレッジベースの構築・メンテナンスを任せるアーキテクチャです。

本記事では、このパターンの仕組みとセットアップ方法、そして従来のセカンドブレインとの違いを解説します。

## 従来の「第二の脳」が挫折する理由

多くの人が Notion や Obsidian でナレッジベースを始めますが、大半は数か月で放置されます。理由はシンプルです。

- タグ付け・相互リンクの **メンテナンスコスト** が増え続ける
- 新しい情報を取り込むたびに既存ページとの **整合性チェック** が必要になる
- 忙しいときほど更新がスキップされ、システムが劣化する

つまり、知識の「蓄積」よりも「管理」に時間が取られてしまうのが根本的な問題です。

## LLM Wiki パターンとは

LLM Wiki パターンは、この管理作業をすべて LLM に委任するアプローチです。パターンの詳細は[前回の記事](/blogs/posts/2026/04/2026-04-05-karpathy-llm-wiki/)で解説していますが、ここでは通常の RAG（検索拡張生成）との違いを中心に整理します。

| 比較項目 | RAG | LLM Wiki パターン |
|---|---|---|
| 知識の処理 | クエリ時にチャンクを検索 | 取り込み時に要約・統合・相互リンク |
| 蓄積 | なし（毎回ゼロから検索） | あり（Wiki が成長し続ける） |
| メンテナンス | 手動でインデックス管理 | LLM が自動でクロスリファレンス更新 |
| 出力 | 一時的なチャット回答 | 永続的な Wiki ページ群 |

RAG は「毎回図書館で本を探し直す」アプローチです。一方、LLM Wiki は「読んだ内容をノートにまとめて、新しい情報が入るたびにノートを更新する」アプローチといえます。

## 3 層アーキテクチャ

LLM Wiki パターンは以下の 3 層で構成されます。

![LLM Wiki パターンの3層アーキテクチャ: Raw Sources（生ソース）、Wiki（LLM が管理する知識ベース）、Schema（構造定義）の関係図](/blogs/images/claude-obsidian-llm-wiki-architecture.png)

### Raw Sources（生ソース）

ユーザーが収集した元資料です。記事のクリッピング、PDF、書籍のハイライト、ポッドキャストのメモなど。LLM はこの層を読むだけで、変更は加えません。信頼できる唯一の情報源（Single Source of Truth）として機能します。

### Wiki（ナレッジベース）

LLM が完全に管理するマークダウンファイル群です。要約ページ、概念ページ、エンティティページ、比較表など。新しいソースが追加されると、LLM が関連する既存ページを更新し、相互リンクを張り、矛盾があればフラグを立てます。

### Schema（構造定義）

Wiki の構造規約やワークフローを定義するドキュメントです。Claude Code では `CLAUDE.md`、OpenAI Codex では `AGENTS.md` がこの役割を果たします。ユーザーと LLM がこのスキーマを共同で進化させていきます。

## 3 つの基本操作

### Ingest（取り込み）

新しいソースを追加したら、LLM に処理を指示します。

```bash
claude -p "I just added an article to /raw-sources.
Read it, extract the key ideas, write a summary page to /wiki/summaries/,
update index.md with a link and one-line description, and update any
existing concept pages that this article connects to.
Show me every file you touched." --allowedTools Bash,Write,Read
```

1 つの記事の取り込みで、LLM は 10〜15 の Wiki ページに触れることがあります。要約の作成、インデックスの更新、関連する概念ページの修正、矛盾のフラグ付けなどを一括で処理します。

### Query（照会）

Wiki に対して質問すると、LLM はインデックスを読んで関連ページを探し、引用付きで回答します。重要なのは、良い回答は Wiki に新しいページとして保存できること。比較分析や発見した新しい関連性は、チャット履歴に消えるのではなく、Wiki に蓄積されます。

### Lint（健全性チェック）

定期的に Wiki の健全性をチェックします。

```bash
claude -p "Read every file in /wiki/. Find: contradictions between pages,
orphan pages with no inbound links, concepts mentioned repeatedly but
with no dedicated page, and claims that seem outdated based on newer files
in /raw-sources/. Write a health report to /wiki/lint-report.md with
specific fixes." --allowedTools Bash,Write,Read
```

ページ間の矛盾、孤立ページ、欠落している概念ページ、古くなった記述などを自動検出します。

## セットアップ手順

### 1. Obsidian の準備

[Obsidian](https://obsidian.md/) をインストールし、新しい Vault（保管庫）を作成します。Vault は通常のフォルダなので、任意の場所に配置できます。

### 2. Claude Code の設定

[Claude Code](https://claude.ai/download) をインストールし、作成した Vault のフォルダを開きます。

```bash
cd /path/to/your-vault
claude
```

### 3. スキーマ（CLAUDE.md）の作成

Vault のルートに `CLAUDE.md` を作成します。ここに Wiki の構造規約を記述します。Karpathy 氏が公開した LLM Wiki テンプレートでは、以下のような構造が推奨されています。

```text
vault/
├── CLAUDE.md          # スキーマ（構造定義）
├── raw-sources/       # 生ソース（記事、PDF、メモ）
├── wiki/
│   ├── index.md       # 全ページのカタログ
│   ├── log.md         # 操作ログ（時系列）
│   ├── summaries/     # ソースの要約
│   ├── concepts/      # 概念ページ
│   └── entities/      # エンティティページ
└── ...
```

### 4. ソースの投入を開始

Obsidian Web Clipper（ブラウザ拡張機能）で記事をクリッピングして `raw-sources/` に保存し、Claude Code に取り込みを指示します。

## 実用的なユースケース

### モーニングブリーフィング

```bash
claude -p "Write a Python script called morning_digest.py that:
1) reads Memory.md and surfaces any open actions due today
2) reads any new files added to /raw-sources in the last 24 hours
3) prints a clean briefing to the terminal.
Then schedule it as a cron job every morning at 7:30am." --allowedTools Bash,Write
```

### 会議メモの自動処理

```bash
claude -p "Read the transcript in /transcripts/call-today.md.
Extract every decision made, every action item with owner and deadline,
and a 3-bullet summary. Add actions to /Action-Tracker.md, log decisions
to /Decision-Log.md, and create a client note in /clients/ linking back
to this transcript." --allowedTools Bash,Write,Read
```

会議の文字起こしから、決定事項・アクションアイテム・要約を抽出し、対応する Wiki ページに自動で反映します。

## なぜこのアプローチが有効か

1945 年、アメリカの科学者 Vannevar Bush は **Memex** という個人用知識ストアの構想を発表しました。ドキュメント間の関連付け（連想トレイル）が、ドキュメントそのものと同じくらい価値を持つというアイデアです。Bush が解決できなかった問題は「誰がメンテナンスするのか」でした。

LLM Wiki パターンは、この問題に対する回答です。

- **人間の役割**: ソースのキュレーション、良い質問をすること、意味を考えること
- **LLM の役割**: 要約、相互参照、整理、記録管理 — ナレッジベースを実用的にし続けるすべての作業

メンテナンスコストがほぼゼロになるため、知識ベースは劣化せずに成長し続けます。使えば使うほど賢くなる蓄積型の AI アシスタントとして機能します。

## 注意点

- LLM Wiki パターンはあくまで**設計思想**であり、特定のツールに依存しません。Claude Code 以外にも OpenAI Codex や他の LLM エージェントで実装できます
- Obsidian はあくまで Wiki を閲覧するためのビューアです。実際の編集は LLM が行います
- 大量のソースを一括で取り込む場合は、品質を確保するために少量ずつ処理することが推奨されます

## まとめ

Claude × Obsidian による「第二の脳」は、従来のノート管理アプリの延長ではなく、LLM にナレッジベースの構築と維持を委任する新しいパラダイムです。RAG のように毎回検索するのではなく、知識を構造化して蓄積し続ける点が革新的です。

セットアップに必要なのは Obsidian と Claude Code だけ。数時間の初期設定で、日々成長し続ける個人のナレッジベースを手に入れることができます。
