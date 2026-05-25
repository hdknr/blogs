---
title: "claude-obsidian × Obsidianで「勝手に育つ第2の脳」を構築する — AIが自動でリンクを張り、使うほど賢くなるVaultの作り方"
date: 2026-05-20
lastmod: 2026-05-20
slug: "claude-obsidian-second-brain"
draft: false
source_url: "https://github.com/hdknr/blogs/issues/1#issuecomment-4504069816"
categories: ["AI/LLM"]
tags: ["Obsidian", "Claude Code", "LLM Wiki", "ナレッジ管理", "第2の脳", "PKM"]
---

「メモはたくさん溜まるのに、結局どこに何を書いたか分からない」
「AIを活用したいけど、毎回コンテキストを一から説明するのが面倒」

こういった悩みを一気に解決するツールが注目を集めています。GitHubで5000スター超えを達成した **claude-obsidian** です。

## claude-obsidianとは何か

[claude-obsidian](https://github.com/AgriciDaniel/claude-obsidian) は、Claude Code × Obsidian を連携させるオープンソースプラグインです（MIT License）。Andrej Karpathy氏（OpenAI創設メンバー、元Tesla AI部門ディレクター）が提唱した **LLM Wikiパターン** を実装したもので、一言でいうと「知識が複利で増えるObsidian Vault」を作るツールです。

従来のAI × ノートツールの問題点は、**毎回セッションが切れるとコンテキストがリセットされること**。claude-obsidianはこの問題を根本から解決します。

ソースを投げれば、Claudeが以下を自動実行します：

1. 内容を読み込み、エンティティと概念を抽出
2. 既存ページへの相互参照を更新
3. 構造化されたObsidian Vaultにファイリング

1つの記事を入れるだけで8〜15の相互リンクされたWikiページが自動生成されます。使えば使うほどVaultが賢くなる — 知識が「複利」で積み上がっていく仕組みです。

## 始め方 — 3つのインストール方法

必要なものは以下の3つです：

- Obsidian（デスクトップ版）
- Node.js 18以上
- Claude Code（CLIまたはデスクトップアプリ）

### 方法1: Vault Clone（推奨・2分で完了）

```bash
git clone https://github.com/AgriciDaniel/claude-obsidian
cd claude-obsidian
bash bin/setup-vault.sh
```

クローンしたフォルダをObsidianで開くだけ。最も簡単です。

### 方法2: Claude Codeプラグインとして追加

```bash
claude plugin marketplace add AgriciDaniel/claude-obsidian
claude plugin install claude-obsidian@claude-obsidian-marketplace
```

### 方法3: 既存のVaultに導入

GitHubリポジトリから `WIKI.md` をコピーして自分のVaultに配置し、Claudeにセットアップを指示するだけです。

## `/wiki` コマンド — Vaultの骨格を一発構築

インストール後、最初に `/wiki` を実行するとVaultの骨格が自動生成されます：

- `wiki/index.md` — マスターカタログ（全ページの目次）
- `wiki/hot.md` — ホットキャッシュ（最近のコンテキストを保持）
- ドメイン別のサブインデックス
- `.raw/` フォルダ — 取り込んだ原文の保管場所

特に重要なのが `hot.md` と `index.md` の2ファイルです。

**`hot.md`** はセッション間のコンテキストを自動で保持するファイルです。通常のAIチャットでは会話が切れると全部忘れますが、claude-obsidianでは `hot.md` に最近の作業内容が自動キャッシュされるため、次のセッションでも「さっきの続き」から始められます。

**`index.md`** はVault全体のマスターカタログ。Claudeはまずこのファイルを読んで、どのページに何が書いてあるかを把握します。全ページを毎回読み込むのではなく、インデックスから必要なページだけを選択的にロードするため、**トークンコストを大幅に節約**できます。

## 3つのコアコマンド

claude-obsidianの日常的な操作は、主に3つのコマンドで回ります。

### `/save` — 会話をWikiノートに変換

Claudeとの会話で価値のある情報が出たら `/save` を打つだけ。Claudeが以下を自動実行します：

- 会話全体を読んでキーアイデアを抽出
- 適切にフォーマットされたWikiページを作成
- 既存ページへのWikilinkを自動生成
- `index.md` を更新

```text
/save プロンプトエンジニアリング
```

のように名前を指定することも可能です。

### `/autoresearch` — 自律リサーチループ

```text
/autoresearch RAG最新手法
```

と実行すると、Claudeがそのトピックについて自律的にリサーチを行い、結果をWikiページとしてVaultに蓄積します。

### `/canvas` — ビジュアルナレッジマップ

Obsidianのキャンバス機能と連携し、知識の視覚的なマッピングを行います。12のビジュアルテンプレートと6つのレイアウトアルゴリズムが用意されており、プレゼンテーション、フローチャート、ナレッジグラフなどを自動生成できます。

## 毎日のインジェストループ — `.raw/` フォルダの使い方

claude-obsidianの真価は「日常的な情報の取り込み」にあります。やり方はシンプルです：

1. 気になった記事、論文、メモを `.raw/` フォルダに保存する
2. `ingest [ファイル名]` コマンドを実行
3. Claudeが自動で読み込み、要約し、概念を抽出し、既存のWikiページと相互リンクを張る

複数ファイルを一括処理したい場合は `ingest all of these` で一括取り込みが可能です。このとき、**ファイル間の相互参照も自動で生成**されます。

さらに便利なのが `lint the wiki` コマンド。Vault全体のヘルスチェックを実行し、以下を検出します：

- 壊れたリンク（デッドリンク）
- 孤立したページ（どこからもリンクされていないノート）
- 知識のギャップ（言及されているが詳細ページがないトピック）
- 古くなった記述

Vaultの「メンテナンス」までAIが自動でやってくれます。

## コスト効率の設計

「AI × ノートツール」で多くの人が心配するのがAPIコストです。claude-obsidianはここも巧みに設計されています。コスト削減の仕組みは3つです：

| 仕組み | 役割 |
|--------|------|
| `hot.md` | 直近のコンテキストだけをキャッシュし、毎回全履歴を読まない |
| `index.md` | マスターカタログから必要なページだけを選択的にロード |
| ドメイン別サブインデックス | 関連する領域のページだけにアクセスを限定 |

たとえばプログラミングについて質問した場合、Claudeは `index.md` を見て「programming」関連のサブインデックスだけを読み、そこからさらに必要なページだけを開きます。Vault全体が1000ページあっても、実際に読み込むのは10〜20ページ程度で済む設計です。

これにより、Vaultが巨大化してもトークンコストが線形に増加しない設計になっています。

## マルチモデル対応

「claude-obsidian」という名前ですが、実はClaude以外のモデルでも動作します。

対応モデル：
- **Claude**（推奨）
- Gemini
- Codex
- Cursor
- Windsurf

プロバイダーに縛られない設計のため、将来的にモデルを切り替えても蓄積した知識はそのまま使えます。

## 1ヶ月後のグラフビュー — 知識が「見える」瞬間

このツールを紹介してバズを起こしたX（旧Twitter）ユーザー @defileo 氏の投稿で最も反響があったのが、1ヶ月間運用した後のObsidianグラフビューのスクリーンショットです。

ノード（概念）が色分けされ、それぞれが相互にリンクで繋がっている。手動では絶対に作れない、密度の高いナレッジグラフが自動的に形成されています。

最初の1週間はページ数も少なくリンクもまばら。しかし2〜3週間と続けるうちに、新しく入れた情報が既存の知識と自動的に結びつき、ネットワーク効果が加速します。4週間目には「自分が何を知っているか」がグラフで一望できる状態になります。

## まとめ — 「メモを溜めるだけ」を卒業する

claude-obsidianが解決する問題は明確です：

**従来のObsidian運用**
メモを書く → リンクを手動で貼る → 面倒で続かない → ノートが散らばる → 結局検索頼み

**claude-obsidian導入後**
ソースを `.raw/` に入れる → ingestする → 自動でWikiページ生成・相互リンク・インデックス更新 → 使うほど賢くなるVaultが育つ

オープンソース（MIT License）で無料、GitHubでは5000スター超えを達成しており、海外のObsidianコミュニティではすでに定番ツールになりつつあります。「AIセカンド脳」を始めたいなら、最もハードルが低く、最もリターンが大きい選択肢の1つです。

### 今すぐ試す手順（5分）

```bash
# 1. リポジトリをクローン
git clone https://github.com/AgriciDaniel/claude-obsidian

# 2. セットアップスクリプトを実行
cd claude-obsidian
bash bin/setup-vault.sh

# 3. Obsidianでフォルダを開く
# 4. /wiki でVaultを初期化
# 5. 好きな記事を .raw/ に入れて ingest する
```

データはすべてローカルのMarkdownファイルとして保存されるため、クラウドに依存せず、自分のマシンに完全にコントロールが残ります。
