---
title: "Karpathy が語る Claude Code × Obsidian で「AI外部脳」を構築する完全ガイド — LLM Knowledge Base の3層アーキテクチャ"
date: 2026-04-29
lastmod: 2026-04-29
slug: "karpathy-claude-code-obsidian-ai-external-brain"
draft: false
source_url: "https://github.com/hdknr/blogs/issues/1#issuecomment-4340881969"
categories: ["AI/LLM"]
tags: ["claude-code", "Obsidian", "Karpathy", "LLMナレッジベース", "セカンド脳"]
---

OpenAI共同創業者の一人で元Tesla AI部門トップのAndrej Karpathyが、Claude Codeの使い方を1時間かけて語った動画が話題になっている（[出典](https://x.com/ClaudeCode_love/status/2049035960252608726)）。その要点と、彼が提唱する「AI外部脳」構築システムを解説する。

## Claude Code は「ツール」から「同僚」へ

Karpathyの核心的なメッセージはこうだ。**Claude Code は「人間なしで自己改善する」フェーズに入りつつある**とKarpathyは言う。

これまでの人間とAIの協調サイクルは：

1. 人間がプロンプトを書く
2. AIがコードを生成する
3. 人間がレビューする

というループだった。だが今後は：

1. Claude Code が問題を発見する
2. Claude Code が解決策を生成する
3. Claude Code が検証まで完結する

というサイクルに変わっていく。Claude Code の未来は「ツール」ではなく「同僚」だ。

## なぜ今の AI の使い方は「間違っている」のか

Karpathy のシステムの出発点は鋭い問題提起だ。

> 「ほとんどの人はAIを"記憶喪失の検索エンジン"として使っている」

質問する → 答えをもらう → タブを閉じる → 翌日また最初からやり直す。何も蓄積しない。何も複利にならない。同じ文脈を再発見するためにトークンを燃やし続けている。

Claude Code × Obsidian のシステムはこれを根本から変える。

## Karpathy の LLM Knowledge Base システム

仕組みは5ステップで回り続ける：

1. 素材を集める（記事、論文、YouTube書き起こし、PDF）
2. AIがすべて読んで構造化されたWikiを書く（要約、概念の解説、アイデアのつながり、マスターインデックス）
3. そのWikiに対して質問する（AIが自分で蓄積した知識を横断検索して引用付きの回答を返す）
4. 回答はWikiに自動で保存される（次の質問は過去の全作業の恩恵を受ける）
5. AIが定期的にWikiの健康チェックをする（矛盾、ギャップ、古い情報を見つけて修正）

**結果は？ 使うたびに賢くなるパーソナルナレッジベース**だ。1ヶ月も情報を入れ続ければ、Google検索では絶対に再現できない、深くリンクされた知識資産ができあがる。

## Level 1：完全初心者向け（Obsidian + Claude Chat）

技術スキルは一切不要。必要なものは2つだけ。

- **Obsidian**（無料）── [obsidian.md](https://obsidian.md) からダウンロード
- **Claude のサブスク**（月$20のPro、またはお好みのAIチャットボット）

### セットアップ手順（15分で完了）

**Step 1: Vaultを作る（2分）**

Obsidianを開いて「新しいVaultを作成」をクリック。名前をつけて保存場所を選ぶだけ。Vaultはただのフォルダで、その中のMarkdownファイルが自動でノートとして表示される。

**Step 2: 2つのフォルダを作る（1分）**

```text
raw/   ← 元素材を入れるフォルダ（記事、メモ、何でも）
wiki/  ← AIがまとめたナレッジを保存するフォルダ
```

**Step 3: 最初の素材を入れる（5分）**

自分が本当に興味あるテーマを1つ選び、そのテーマの良い記事を3〜5本見つける。それぞれ `raw/` フォルダにノートを作って本文をコピペ。先頭に `Source: [URL]` と書いておくだけ。

**Step 4: AIにWikiを作らせる（5分）**

Claude（claude.ai）を開いて、自分の素材を貼り付けて指示する：

```
各ソースの要約を書いて、主要な概念をリストアップして、
マスターインデックスを作ってください。
```

Claudeが構造化された出力を返すので、それぞれ `wiki/` フォルダにノートとして保存する。

**Step 5: グラフビューで繋がりを確認**

Obsidianのグラフビュー（Ctrl+G）を開くと、ノートが点として表示され、Wikiリンクが線でつながっている。これがあなたのナレッジベースのネットワークだ。

Level 1はコピペだけで動く。ターミナルもコーディングも不要。

## Level 2：フルシステム（3層アーキテクチャ + CLAUDE.md）

Level 1が「コピペ運用」だとすれば、Level 2は**「AIが自分でファイルを作って管理するシステム」**だ。

### 3層アーキテクチャ

| 層 | パス | 役割 |
|---|---|---|
| Layer 1 | `raw/` | 元素材。AIはここを読むが書き換えない |
| Layer 2 | `wiki/` | AIが生成・維持する。要約、概念記事、クロスリンク |
| Layer 3 | `CLAUDE.md` | AIへの指示ファイル。Wikiの構造・命名規則・操作手順を定義し、Claude Codeの動作を制御する |

### フォルダ構造

```text
my-knowledge-base/
├── raw/
│   ├── articles/
│   ├── papers/
│   ├── repos/
│   ├── datasets/
│   └── assets/
├── wiki/
│   ├── index.md
│   ├── log.md
│   ├── concepts/
│   ├── entities/
│   ├── sources/
│   ├── syntheses/
│   ├── outputs/
│   └── attachments/
├── templates/
└── CLAUDE.md
```

ファイル名はすべてケバブケース（`active-inference.md` ✓、`Active Inference.md` ✗）。

### 4つの運用サイクル

- **Ingest** ── 新しい素材を取り込む。AIが要約、概念ページ、つながりを自動生成
- **Compile** ── Wikiページを構築・更新。新情報を既存構造に統合
- **Query** ── 質問する。AIがWiki内を横断検索して引用付き回答を返す。回答はWikiに保存
- **Lint** ── 健康チェック。矛盾、ギャップ、壊れたリンク、古い情報を発見して自動修正

### CLAUDE.md の書き方

`CLAUDE.md` にはWikiの構造、命名規則、各操作の具体的な手順、ページ作成の閾値、品質基準などを記述する。

> 元記事いわく「このファイルは80行以内に収めること。すべての行がコンテキストウィンドウを食う」

## Level 3：自動化（5段階）

### Level 3-1: CLIで一発実行

Claude Code をターミナルで開いて、1つのコマンドで `raw/` 内の未処理ファイルを全部処理させる。

### Level 3-2: スラッシュコマンド

`.claude/commands/` にMarkdownファイルを置くと `/wiki-compile` のようなカスタムコマンドが使える。繰り返しのワークフローを1コマンドに集約する。

### Level 3-3: スケジュール実行

Claude Desktop の `/schedule` 機能やcronで、毎朝自動で `raw/` の新ファイルを処理させる。記事をクリップして寝れば、起きたときにはWikiが更新済みになっている。

### Level 3-4: GitHub Actions

VaultをGitHubリポジトリにして、`raw/` にpushするとGitHub Actions上でClaude CodeがWikiをコンパイル。PCが電源オフでも動く。

### Level 3-5: Agent Skills

`.claude/skills/` にスキルファイルを配置すると、Claudeが文脈を自動検出して適切な操作を実行。「raw/に新しいファイルを入れた」と言えば、コマンドを打たなくてもClaudeがIngestサイクルを自動で走らせる。

コミュニティがすでに `wiki-skills` プラグインを作っており、`/wiki-init` `/wiki-ingest` `/wiki-query` `/wiki-lint` のコマンドが即座に使える。手動で設定ファイルを書く必要すらない。

## なぜ「メンテナンス」が最大のボトルネックだったのか

Notion、Evernote、Roam Research... これまでも「セカンド脳」を標榜するツールはたくさんあった。しかしほとんどの人が数ヶ月で使わなくなる。理由は同じだ。**メンテナンスが面倒すぎる。**

> 「情報を入れるのは楽しい。でもタグの整理、クロスリファレンスの更新、構造の再編成── この追加作業が積み上がると、本来の仕事の上にさらに仕事が乗る。サボるとシステムが劣化する。半年後にリビルドを試みて、同じサイクルを繰り返す。」

Claude Code はこのサイクルを永久に壊す。メンテナンスはただのコマンドになる。Vault全体の再編成はプロンプト一発。Notionからの移行も全部自動化できる。

このメンテナンス問題の本質は、半世紀以上前にすでに見抜かれていた。1945年、Vannevar Bushは「Memex」という概念を提唱した。個人的にキュレーションされた知識ストアで、ドキュメント間のつながりがドキュメントそのものと同じくらい価値があるとされた。Bushはこれを描いたが、解決できなかったのは「誰がメンテナンスするか」だった。

いま、その答えが出た。

## Vaultに入れるべきもの

「この1年で消費して、そのまま消えたものを考えてみてほしい」というのが元記事の問いかけだ。

- 読み終わって忘れた本
- 考え方を変えたポッドキャスト
- 夜11時に保存して二度と開かなかった記事
- どのコースより多くのことを教えてくれたYouTubeの深夜ラビットホール
- マーカーを引いて二度と見なかったKindleのハイライト
- 大きな決断の前にやったリサーチ
- 古いプロジェクトのノート
- うまくいかなかったことから学んだ教訓

これらが全部Vaultに入るべきもの。もし何も素材がなかったら？ Claude チャットを開いて20分間話すだけでいい。その会話を Memory ファイルとして保存すれば、最初のセッションから「Claude が自分のことを知っている」感覚になる。

## まとめ

| ポイント | 内容 |
|---|---|
| Karpathy の主張 | Claude Code は「ツール」から「同僚」へ。自己改善フェーズに突入 |
| LLM Knowledge Base | 使うたびに賢くなるパーソナルナレッジベース |
| Level 1 | Obsidian + Claude Chat のコピペだけで始められる |
| Level 2 | 3層アーキテクチャ（raw / wiki / CLAUDE.md）+ 4サイクル |
| Level 3 | 5段階の自動化（CLI → スラッシュコマンド → スケジュール → GitHub Actions → Agent Skills） |
| 革新点 | 「メンテナンス」問題をAIが完全に肩代わりする |

## 出典

- [@ClaudeCode_love](https://x.com/ClaudeCode_love/status/2049035960252608726)（Claude Code Studio）
- 元記事：[@hooeem](https://x.com/hooeem/status/2041196025906418094)
