---
title: "SLIDE.md 実践ガイド：Claude CodeとClaude Designでスライドを自動生成する"
date: 2026-06-24
lastmod: 2026-06-24
slug: "slide-md-claude-design-practical-guide"
draft: false
source_url: "https://github.com/hdknr/blogs/issues/1#issuecomment-4785286459"
categories: ["AI/LLM"]
tags: ["Claude Code", "Claude Design", "SLIDE.md", "スライド作成", "プレゼン"]
---

[SLIDE.md](https://github.com/sho-ai-magic/slide.md) は、Claude CodeのスキルとClaude Designを組み合わせてプレゼンテーションスライドを自動生成するためのデザインシステムです。Claude Designは高品質なスライドを生成できる一方、毎回デザインがバラつくという課題がありました。SLIDE.mdはこの問題を解決するために設計されたスライド専用デザインシステムで、色・フォント・余白・構図を統一定義し、一貫性のあるプレゼン資料を短時間で生成できます。

3つのClaude Codeスキルと、以下のドキュメントセットで構成されます：

- **slide-md-creator** — デザインシステム（SLIDE.md）を生成するスキル
- **slide-pattern-creator** — スライドパターンを画像から抽出・追加するスキル
- **slide-deck-builder** — プレゼン内容を受け取り設計書（SLIDE-DECK.md）を生成するスキル
- **SLIDE.md** — 色・フォント・余白などのデザイン定義ファイル（4種類のサンプル付き）
- **SLIDE-PATTERN-{name}.md** — 各スライドの構図定義（99種類）

スライド生成は4つのステップで進みます。初回のみStep 1が必要で、2回目以降はStep 3から始められます。

## Step 1：インストール

### 必要なもの

- Claude Code（有料プランまたはAPIアクセス）
- Claude Designへのアクセス（Claudeの有料プランに含まれています）

### インストール方法

Claude Codeを作業フォルダで開き、チャット欄に以下を入力するだけでセットアップが完了します：

```
SLIDE.mdをインストールしてください
```

これにより以下が自動でセットアップされます：

- 3つのスキル（slide-md-creator・slide-pattern-creator・slide-deck-builder）
- 4種類のサンプルデザインシステム（SLIDE.md）
- 99種類のスライドパターン（SLIDE-PATTERN）

### 手動インストール

Claude Codeからのインストールがうまくいかない場合は、[GitHubリポジトリ](https://github.com/sho-ai-magic/slide.md)から手動セットアップできます。

1. 「Code」→「Download ZIP」でダウンロード＆解凍
2. `skills/` にある3つのフォルダを以下のパスにコピー
   - Mac: `/Users/（ユーザー名）/.claude/skills/`
   - Windows: `C:\Users\（ユーザー名）\.claude\skills\`
3. `docs/SLIDE-md/` と `docs/SLIDE-PATTERN/` を作業フォルダにコピー

## Step 2：デザインシステムを用意する

### サンプルをそのまま使う場合（推奨）

インストール時点で4種類のサンプルデザインシステムが `SLIDE-md/` フォルダに入っています。各フォルダ内の `sample.html` をブラウザで開いて好みのデザインを確認し、そのままStep 3に進めます。

### オリジナルのデザインシステムを作る場合

自社ブランドや既存スライドに合わせたデザインシステムを作るには `slide-md-creator` スキルを使います。Claude Codeにスライドの画像、PowerPoint、参考Webサイトのいずれかを添付して話しかけると、以下の対話が進みます：

1. **デザイン要素の読み取り** — 色・フォント・余白・雰囲気を自動で分析
2. **不明な点だけ確認** — フォント名など読み取れなかった情報のみ質問（3〜5問）
3. **SLIDE.mdとsample.htmlの生成** — 確認後に自動生成

生成された `sample.html` をブラウザで開くと、6ページのプレビューでデザインを確認できます。

## Step 3：SLIDE-DECK.mdを生成する

最も重要なステップです。`slide-deck-builder` スキルがプレゼン内容を受け取り、スライドの設計書（SLIDE-DECK.md）を生成します。

Claude Codeに話しかけると、以下の流れで対話が進みます：

### ① ブリーフのヒアリング（4問）

聴衆・目的・時間・トーンなど基本情報をヒアリングします。

### ② プレゼン内容を渡す

テキストを貼り付けるか、`.md` や `.pdf` ファイルを添付します。Claude などのAIで事前にテキストベースで内容を作成し、Markdownファイルとして添付する方法がおすすめです。

### ③ デザインシステムを選ぶ

`SLIDE-md/` フォルダにあるSLIDE.mdが一覧表示されるので、使いたいものを番号で選びます。

### ④ スライド構成の確認

AIが自動でスライド構成案を提示します。「5枚目と6枚目の順番を入れ替えて」「8枚目は不要」など自由に変更指示を出せます。

### ⑤ パターンの割り当て確認

各スライドにどのパターンを割り当てるかAIが自動提案します。[スライドギャラリー](https://sho-ai-magic.github.io/slide.md/)でパターン一覧を確認しながら変更できます。

### ⑥ SLIDE-DECK.mdの生成

承認すると `SLIDE-DECK-{name}/SLIDE-DECK-{name}.md` が生成されます。このファイルにはデザインシステム・スライドパターン・各スライドのコンテンツひな型がすべて含まれます。

## Step 4：Claude Designでスライドを生成する

1. [claude.ai/design](https://claude.ai/design)（またはClaude左メニューの「デザイン」）を開く
2. 「Slides」を選択
3. Step 3で生成した `SLIDE-DECK-{name}.md` をアップロードして「Send」をクリック

Claude Designがデザインシステムとパターン定義を読み取り、スライドを自動生成します。

### 生成後の微調整

- **Mark up** — 修正箇所を直接指定して修正指示を出せます
- **Edit** — テキストなどを直接編集できます

現時点では細かな位置調整には向いていないため、軽微な修正にとどめるのが現実的です。

### ダウンロード形式

| 形式 | 推奨度 | 備考 |
|------|--------|------|
| PDF | ★★★ | 発表・共有に最適。デザイン通りに出力される |
| HTML | ★★★ | ブラウザでフルスクリーン表示可能。オフライン動作 |
| PowerPoint | ★☆☆ | 現時点ではデザインが崩れる場合あり |

迷ったらPDFが確実です。

## よくある質問

**Q. Claude Codeがなくても使えますか？**

SLIDE-DECK.mdを手書きで作れば使えますが、かなり手間がかかります。スキルを使ってClaude Codeで生成するのが現実的です。

**Q. NotebookLMやChatGPTでも使えますか？**

使えます。SLIDE-DECK.mdはどのAIツールにも渡せます。ただし、Claude Designがビジュアルデザインに最も特化しており高品質な仕上がりになります。

**Q. 99種類以外のパターンを追加したいのですが？**

`slide-pattern-creator` スキルを使えば、スライド画像からパターンを抽出・追加できます。Claude Codeに「スライドパターンを抽出して」と話しかけ、スライドの画像を渡すだけです。

## まとめ

初回セットアップが終われば、「slide-deck-builderに話しかけてSLIDE-DECK.mdを生成 → Claude Designにアップロード」という2ステップだけでプレゼン資料が完成します。

- GitHubリポジトリ: [sho-ai-magic/slide.md](https://github.com/sho-ai-magic/slide.md)
- スライドギャラリー: [sho-ai-magic.github.io/slide.md](https://sho-ai-magic.github.io/slide.md/)
