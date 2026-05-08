---
title: "Claude Code × Obsidian で「第二の脳」を構築する完全解説 — 海外1,240万views超え、AI記憶設計の新標準"
date: 2026-04-23
lastmod: 2026-04-23
draft: false
source_url: "https://github.com/hdknr/blogs/issues/1#issuecomment-4304039550"
categories: ["AI/LLM"]
tags: ["Claude Code", "Obsidian", "PKM", "LLM Wiki", "第二の脳", "ナレッジ管理"]
---

海外 AI 活用シーンで **Obsidian × Claude Code** の組み合わせが爆発的な注目を集めている。6本の主要記事だけで合計 **1,240万 views**、ブックマーク数は **8万件超え**。元 OpenAI 創設メンバーの Andrej Karpathy 氏が提唱し、Obsidian CEO の Steph Ango 氏自らが AI 連携スキルを GitHub で公開。ここまで業界の中心人物が動いたツール組み合わせは、近年なかった。

本記事は東大 ClaudeCode 研究所（[@ClaudeCode_UT](https://x.com/ClaudeCode_UT)）が公開した解説記事「【決定版】ゼロから始めるClaudeCode × Obsidianの完全解説」をベースに、その要点をまとめる。

## そもそも Obsidian とは何か

[Obsidian](https://obsidian.md/) は、個人向けのローカル Markdown ノートアプリだ。2020 年公開、個人利用は無料で、Mac / Windows / Linux / iOS / Android に対応している。同じノート系の Notion や Evernote とは設計思想が根本的に異なる。

- **ノート本体は Markdown ファイル** — 各ノートは `.md` としてディスク上に実ファイルで存在する。独自データベースに閉じ込められない。
- **Vault は OS のただのフォルダ** — ノートを束ねる「Vault」は普通のディレクトリ。Git でも Dropbox でも iCloud でも、好きな仕組みで同期・バックアップできる。
- **双方向リンク `[[ノート名]]`** — ノート同士をリンクで繋ぎ、知識をグラフ構造として可視化できる。Zettelkasten など既存 PKM 手法の基本機能を標準で備える。
- **ローカルファースト** — 規定ではすべて自分の PC 内に保存。クラウドに置くかどうかは利用者が選ぶ。
- **豊富なプラグイン** — 2,000 以上のコミュニティプラグインで、PDF 注釈・タスク管理・グラフ可視化まで拡張できる。

### なぜ「AI × 記憶設計」の目的に最適なのか

Obsidian のこれらの特徴は、Claude Code のような**ファイルシステムを直接操作する AI エージェント**と噛み合う。理由は3点ある。

1. **プレーンテキスト = AI が素手で読み書きできる** — Claude Code はローカルファイルを直接扱う。Obsidian のノートは `.md` なので、API もプラグインも介さず、そのまま読む・書き換える・リンクを張ることができる。これが Notion（クラウド DB + API 必須）との決定的な違いだ。
2. **ローカルだから I/O が速い** — AI が数百ノートを横断して読む場面で、クラウド同期のレイテンシがボトルネックにならない。
3. **双方向リンクが「Wiki の骨格」を最初から提供する** — 後述の LLM Wiki では AI が `[[リンク]]` で知識を相互接続する。その構文と可視化が Obsidian には既に備わっている。

Obsidian は「人間のためのノートアプリ」として設計されたが、結果として **AI エージェントが最小の摩擦で扱えるナレッジベース**になっていた。これが Claude Code × Obsidian が一気に広まった技術的な土台だ。

### MkDocs のような静的ドキュメントツールでは不足か？

「AI が Markdown を読み書きできればいいなら、[MkDocs](https://www.mkdocs.org/) / Docusaurus / Hugo でも同じでは？」という疑問は当然出てくる。結論から言うと、**「AI が整理済みナレッジを置く倉庫」としてなら成立するが、LLM Wiki パターンが狙う運用ループ全体では不足する**。

| 観点 | MkDocs 系 | Obsidian |
|------|----------|----------|
| AI からの読み書き（Markdown 直接操作） | ○ | ○ |
| ローカルで速い | ○ | ○ |
| 素早い編集 UX（ライブプレビュー、クイックスイッチャー、デイリーノート） | ×（ビルド前提） | ○ |
| 双方向リンク / バックリンク / グラフビュー | △（プラグイン依存・弱い） | ○（標準） |
| 非テキスト（PDF 注釈・Canvas・手書き） | × | ○ |
| モバイル編集（iOS / Android アプリ） | × | ○ |
| PKM 寄りプラグイン（Dataview, Templater, Tasks, Excalidraw） | ×（用途が違う） | ○ |

本質的な差は位置づけにある。MkDocs 系は「**書き終えたものを公開するための静的サイトジェネレーター**」で、開発者ワークフロー（エディタで書いて `mkdocs serve` して別窓で確認）が前提だ。対して LLM Wiki パターンは以下の3段ループが毎日回る:

1. `.raw/` に走り書きを雑に投入する（**編集**フェーズ）
2. AI が `wiki/` を整理・更新する（**整理**フェーズ）
3. 人間が読み直して追記・修正する（**育成**フェーズ）

MkDocs はこのうち 2 のデータ置き場としては機能するが、1 と 3 の「人間側の書く体験」がほぼ存在しない。加えて Karpathy が重視する「`[[相互リンク]]` で知識をグラフ化する」部分は、Obsidian ではグラフビュー・バックリンクペインが標準同期するのに対し、MkDocs 系では wiki-link プラグインを足してもリアルタイム可視化は得られない。

逆に MkDocs が勝るのは「**チームで共有・公開する技術ドキュメント**」「CI でリンク切れを検出したい」「Git と素直に統合したい」という用途。つまり棲み分けとしては、**公開する技術ドキュメントなら MkDocs、個人の PKM / 第二の脳なら Obsidian** が適切な選択だ。

## AI を「記憶喪失の派遣社員」として使っていないか

海外 AI 活用コンサルタントの sourfraser 氏はこう言い切る。

> 「ほとんどの人は AI を記憶喪失の派遣社員のように使っている」

毎朝出社するたびに、自分が誰で、何の仕事をしていて、何を頼みたいのかを一から説明する。ChatGPT でも Claude でも、会話が終わればコンテキストはリセットされる。同じ前提を毎回打ち込んでいる人は多いはずだ。

これは AI の性能の問題ではない。**「記憶の設計」をしていないこと**が根本原因だ。

## AI 活用は「記憶の設計」フェーズに入った

AI 活用の焦点はここ数年で急速に変化してきた。

| 時期 | 焦点 |
|------|------|
| 2023–2024 | どの AI ツールを使うか |
| 2024–2025 | どんなプロンプトを書くか |
| 2025–2026 | どんなコンテキスト・ハーネスを活用するか |
| 2026年〜 | **どういう記憶を設計して運用するか** |

プロンプトの工夫は「1回限り」の効果だ。毎回いいプロンプトを書く必要がある。対して **記憶の設計は複利的に効く**。AI に渡す記憶が増えるほど、出力の精度は自動的に上がっていく。今日始めた人と半年後に始める人では、蓄積された記憶の量に埋めがたい差が生まれる。

## 歴代ナレッジ管理手法が破綻してきた理由

「第二の脳を作ろう」という試みは何十年も前から繰り返されてきた。フォルダ整理、ブックマーク、PARA 法、Zettelkasten、エバーグリーンノート……。defileo 氏はそのパターンをこう描写する。

> 「整理して始める → メンテが溜まる → スキップする → 品質が劣化する → 散らかったメモに戻る → 6ヶ月後にまた挑戦する。これを繰り返す」

全ての従来手法に共通する弱点は、**「人間がメンテする前提」**だったことだ。

## LLM Wiki が 81 年越しの問題を解決した

1945 年、Vannevar Bush が「Memex」という個人知識装置を構想した。しかし Bush も、メンテを誰がやるかという問題は解決できなかった。

そこに登場したのが Karpathy 氏が提唱した **「LLM Wiki」** だ。Claude Code などの AI がソースを読み込み、自動で Wiki を構築し、メンテナンスまで引き受ける。

LLM Wiki は歴代の PKM 手法の良いところを取り込んでいる。

- Zettelkasten の「1ページ1概念 + リンクで相互接続 + インデックス」
- エバーグリーンノートの「概念が使うたびに進化する」
- MOC（Maps of Content）の「知識の全体地図をインデックスで作る」

違いはただ1つ。**人間がやるか、AI がやるか**だ。

## なぜ Obsidian が選ばれているのか

「Notion じゃダメなの？」という疑問は自然だが、Claude Code との組み合わせで選ばれているのは Obsidian だ。理由は3つある。

### 1. プレーンテキストだから AI が直接読み書きできる

Obsidian のファイルはすべて Markdown 形式。Claude Code はファイルシステムを直接操作できるエージェントなので、Obsidian のノートをそのまま読み、書き、リンクを追加できる。API やプラグインを介する必要がない。

### 2. ローカルだから速い

データはすべて自分の PC 内にある。クラウド同期の待ち時間がなく、Claude Code がファイルを読み書きする速度が最速になる。

### 3. ツール側が AI 前提で進化している

Obsidian CEO の Steph Ango 氏自身が AI エージェント連携スキルを開発して GitHub で公開（25,000 Stars 超え）。ツールの作り手自身が「AI と一緒に使う」前提でプロダクトを進化させている。

## セットアップ：今日から始める手順

### Step 1: Vault を作成する

[Obsidian 公式サイト](https://obsidian.md/) からダウンロードしてインストール。「Create new vault」を選んで新しい Vault を作成する。

Karpathy 氏が推奨する3フォルダ構造を使う:

```
vault/
├── .raw/      # 素材投入フォルダ（整理せず何でも放り込む）
├── wiki/      # AI が自動構築する Wiki
└── Home.md    # Vault 全体のハブページ
```

`.raw/` には読み終えた記事、ポッドキャストのメモ、調べたこと、プロジェクトノートを整理せず放り込む。整理は AI がやる。

### Step 2: Memory.md を作る

Vault を作ったら、まず1つだけファイルを作る。`Memory.md` だ。sourfraser 氏はこのファイルを「新入社員のオンボーディング文書」と表現している。以下を書く:

- あなたの仕事は何か
- どんなプロジェクトを進めているか
- よく使うツールは何か
- 仕事上の目標は何か
- 大事にしている判断基準は何か

20分もあれば十分。完璧である必要はまったくない。

### Step 3: 2つの OSS ツールを導入する

Claude Code と Obsidian を組み合わせるための道具が2つのオープンソースプロジェクトとして公開されている。

#### obsidian-skills（基盤層）

- **作者**: Obsidian CEO の Steph Ango 氏
- **Stars**: 26,000超（2026/04/23 時点）
- **GitHub**: [kepano/obsidian-skills](https://github.com/kepano/obsidian-skills)
- **ライセンス**: MIT

AI に「Obsidian の使い方」を教えるスキルセット。5つのスキルが含まれる:

- `obsidian-markdown`: マークダウンの正しい書き方
- `obsidian-bases`: データベースビューの操作
- `json-canvas`: ビジュアルキャンバスの操作
- `obsidian-cli`: Vault の読み書き・検索コマンド
- `defuddle`: Web ページからクリーンなマークダウンを抽出（広告・ナビゲーション除去）

`npx` でインストールするか、Vault の `.claude/` フォルダにリポジトリを配置する:

```bash
npx skills add git@github.com:kepano/obsidian-skills.git
```

#### claude-obsidian（応用層）

- **Stars**: 3,000超（2026/04/23 時点）
- **GitHub**: [AgriciDaniel/claude-obsidian](https://github.com/AgriciDaniel/claude-obsidian)
- **ライセンス**: MIT

Karpathy の LLM Wiki パターンに基づく AI「第二の脳」構築・維持スキルセット。主要コマンド:

| コマンド | 機能 |
|---------|------|
| `/wiki` | 初回セットアップ。Vault 構造を自動構築 |
| `ingest [file]` | 素材を読み込み、8–15 個の Wiki ページを自動生成 |
| `/save` | 今の会話を Wiki ノートとして保存 |
| `/autoresearch [topic]` | 指定トピックについて 3–5 ラウンドの Web 調査を実行 |

### Step 4: Vault を Private Git で同期・バックアップする

Vault をどう同期・バックアップするかは、AI を触らせる運用では**セットアップ手順の中でも特に重要**だ。Claude Code はファイルを直接書き換えるエージェントなので、**AI の誤動作が Vault を壊すリスクが常にある**。Git があれば次の4つを無料で得られる。

1. **誤上書き・誤削除を即 revert できる**
2. **「AI に試行させる → 気に入らなければ捨てる」を branch で扱える**
3. **差分で AI の編集内容をレビューできる**（大量ノートを AI が一括更新した時に効く）
4. **Memory.md の変遷が履歴として追える**（自分の仕事観・目標の変化が可視化される）

これは Obsidian Sync（公式・有料）や iCloud / Dropbox には無い価値だ。

#### 推奨構成

| レイヤー | 選択肢 | 備考 |
|---------|-------|------|
| ホスティング | **GitHub Private** / GitLab Private / self-hosted Gitea | 絶対 private。Memory.md に個人情報が入るため |
| 自動コミット | **Obsidian Git プラグイン** | 5–10 分おきに自動 commit + push 設定が定番 |
| iOS | Working Copy + Obsidian Git | Working Copy が Git クライアント役、Obsidian が編集役 |
| Android | Obsidian Git 単体 | 追加ツール不要 |
| バイナリ | **Git LFS** | PDF・画像が多い Vault は実質必須 |
| 機密部分 | **git-crypt** で個別ファイル暗号化 | 顧客情報・契約情報を扱うノートだけ透過暗号化 |

#### `.gitignore` の定番

```gitignore
# Obsidian のワークスペース状態（デバイスごとに別、競合の元）
.obsidian/workspace*
.obsidian/workspace-mobile.json

# キャッシュ・ゴミ箱
.obsidian/cache
.trash/

# OS ファイル
.DS_Store
Thumbs.db
```

逆に `.obsidian/plugins/` や `.obsidian/snippets/` は**コミットする**のが正解。プラグイン設定や CSS をデバイス間で揃えるため。

#### 注意点

- **Public リポジトリは絶対 NG** — Memory.md に書く自分の仕事・目標・クライアント情報が流出する。
- **コンフリクトは避けられない** — PC とモバイル両方で書くと発生する。Obsidian Git プラグインは自動 pull → commit → push の順だが、`Memory.md` のような頻繁に触るファイルは時々手動マージが要る。
- **プラグイン由来の絶対パス汚染** — Templater や Dataview のクエリが絶対パスを持つ場合があり、デバイス間で壊れる。気になったら相対パスに直す。
- **大量コミットによる肥大化** — 自動コミットは便利だが 1 年で数万コミットになる。定期的に `git gc --aggressive`、あるいは年単位で別リポに切る運用も検討する。

#### Obsidian Sync との比較

|  | Git Private | Obsidian Sync |
|--|-----------|---------------|
| 料金 | 無料（GitHub Private） | $4–8/月 |
| モバイル体験 | やや手間（Working Copy 等） | シームレス |
| 履歴 | 永続 | 最大1年 |
| ブランチ / 実験 | ○ | × |
| AI 編集のレビュー | ◎（diff で一発） | △ |
| 非エンジニア向き | × | ○ |

**エンジニアで AI を触らせる運用 → Git 一択**、**非エンジニア → Obsidian Sync** という棲み分けが現実的だ。

## 3つの記憶アプローチを使い分ける

「AI に記憶を持たせる」方法は大きく3つある。目的によって使い分けるのが現実的だ。

| アプローチ | 特徴 | 向いている用途 |
|-----------|------|--------------|
| **LLM Wiki方式**（Obsidian × Claude Code） | 使うほど Wiki が育つ複利効果 | 特定領域の専門知識を長期蓄積 |
| **NotebookLM方式**（Google） | 手軽だが知識は蓄積しない使い切り型 | 今すぐ資料について聞きたい場面 |
| **CLAUDE.md方式**（Claude Code 単体） | 「AIにどう動いてほしいか」を定義 | プロジェクト単位の行動基準を組み込む |

## Obsidian 構築代行ビジネスという新しい機会

ここまで技術的な話をしてきたが、ビジネス視点での動きも紹介しておく。

海外では **Obsidian 構築代行ビジネス**が台頭している。実質の構築は AI がやってくれるため、設計を上手くやれば収益化できるという考え方だ。

- 初期構築: 24万円
- 年間メンテ: 8万円
- 200件で年間 **1,600万円** の定期収入

ターゲットは弁護士・医者・コンサル・投資家など「情報に溺れているが整理する時間がない人たち」だ。日本でも Obsidian ニーズが高まりつつある今、参入機会があるかもしれない。

## まとめ

Obsidian × Claude Code の本質は、知識管理を「人間がメンテする仕組み」から「AI が自動メンテする仕組み」に転換することだ。

1. `Memory.md` に自分を定義する
2. `.raw/` に素材を放り込む
3. AI が自動的に Wiki を構築・更新する

最初の一歩は小さい。`Memory.md` に自分の仕事と目標を書くだけで、AI との対話の質が劇的に変わる。

**参考リソース**:
- [kepano/obsidian-skills](https://github.com/kepano/obsidian-skills) — Steph Ango 氏によるスキルセット
- [AgriciDaniel/claude-obsidian](https://github.com/AgriciDaniel/claude-obsidian) — LLM Wiki パターン実装
- [@sourfraser — Claude + Obsidian = A true AI employee](https://x.com/sourfraser/status/2035454870204100810)
- [@defileo — Claude + Obsidian have to be illegal](https://x.com/defileo/status/2042241063612502162)
- [@NickSpisak_ — How to Build Your Second Brain](https://x.com/NickSpisak_/status/2040448463540830705)
