---
title: "Matt Pocock の「Skills for Real Engineers」— Claude Code に現場のエンジニアリング作法を仕込む Markdown スキル集"
date: 2026-04-30
lastmod: 2026-04-30
slug: "matt-pocock-skills-for-real-engineers"
draft: false
source_url: "https://github.com/hdknr/blogs/issues/1#issuecomment-4349316259"
categories: ["AI/LLM"]
tags: ["claude-code", "Matt Pocock", "スキル", "AI開発", "typescript"]
---

TypeScript 界の著名エンジニア Matt Pocock が公開した「**Skills for Real Engineers**」が、公開 24 時間で 22,000 スター、現在は 64,000 スター超えという驚異的な勢いで注目を集めている。

[GitHub: mattpocock/skills](https://github.com/mattpocock/skills)

本記事では、このスキル集の設計思想・解決する問題・導入手順を紹介する。

## Skills for Real Engineers とは

「Skills for Real Engineers」は、Claude Code や Codex などの AI コーディングエージェントに「**現場のエンジニアリング作法**」を仕込むための Markdown ファイル集だ。

> My agent skills that I use every day to do real engineering - not vibe coding.

Matt Pocock 自身が毎日使っているエージェントスキルをそのままオープンソースとして公開したもので、「ノリでコーディング（vibe coding）」ではなく、現実のアプリケーション開発で機能する設計になっている。

## なぜ必要なのか — AI 開発 3 大失敗パターン

AI 開発で誰もがハマる以下の問題を解決するために設計されている。

### 1. エージェントが意図を汲まない

エンジニアと AI の間の「コミュニケーションギャップ」が最大の失敗原因。エージェントは何を作りたいかを正確に理解していないまま実装を進める。

**解決スキル:**
- `/grill-me` — コード不要のユースケースで詳細なヒアリングを実施
- `/grill-with-docs` — ドキュメント生成も含めた上位版

### 2. コードがいつまでも動かない

エージェントは「動いている」と思っていても、実際には壊れていることがある。テストと実装の間にギャップが生まれやすい。このスキル集にはテスト駆動の実装フローを強制するスキルも含まれている。

### 3. コードベースが荒れていく

長期運用でコードベースが複雑化し、エージェントの判断精度が落ちていく問題。プロジェクト直下に置く `CONTEXT.md`（プロジェクト固有の用語・命名規則・ドメインモデルを定義するファイル）を整備することで、エージェントが 20 語かけて説明するところを 1 語で伝えられるようになる。

## 特徴: 小さく・適応しやすく・組み合わせ可能

他の AI 開発フレームワーク（GSD・BMAD・Spec-Kit など、AI エージェントの開発プロセス全体を管理する重厚なフレームワーク）がプロセスの主導権を奪うのとは対照的に、Skills for Real Engineers は**スモールで組み合わせ可能なスキル**の集合体として設計されている。

- どのモデルでも動作する
- 数十年のエンジニアリング経験が凝縮されている
- 自由にカスタマイズして自分のものにできる

## 収録スキル一覧

リポジトリは 4 カテゴリ・計 19 スキルで構成されている。

### Engineering — コード作業向け（10 スキル）

日々のコード作業で使うコアスキル群。

- **diagnose** — 難しいバグ・性能劣化に対する規律ある診断ループ（再現 → 最小化 → 仮説 → 計測 → 修正 → 回帰テスト）
- **grill-with-docs** — ドメインモデルに照らして計画を厳しく検証し、`CONTEXT.md` と ADR をその場で更新する高機能版グリル
- **triage** — Issue をステートマシン状のトリアージロールで分類整理
- **improve-codebase-architecture** — `CONTEXT.md` と `docs/adr/` を参照してコードベースの深化機会を発見
- **setup-matt-pocock-skills** — リポジトリごとの設定（Issue tracker、ラベル語彙、ドメインドキュメント構成）を初期化。他スキルの基盤
- **tdd** — RED-GREEN-REFACTOR で 1 縦割りスライスずつ機能/バグ修正を進める TDD ループ
- **to-issues** — 計画/仕様/PRD を独立して着手可能な GitHub Issue に分解
- **to-prd** — 現在の会話コンテキストを PRD にまとめ、GitHub Issue として投稿
- **zoom-out** — エージェントに視野を広げさせ、コードの高レベルな全体像を語らせる
- **prototype** — 使い捨てのプロトタイプ（ターミナルアプリ、もしくは複数 UI バリエーション）で設計を炙り出す

### Productivity — 一般的なワークフロー（3 スキル）

コード以外の作業効率を上げる汎用スキル。

- **caveman** — 雑語を削ぎ落とした超圧縮コミュニケーションモード。技術的正確性を保ったままトークン消費を約 75% 削減
- **grill-me** — 計画/設計について決定木を全て潰すまで容赦なくインタビューを受ける
- **write-a-skill** — 新しいスキルを正しい構造（プログレッシブ・ディスクロージャ、同梱リソース）で作成

### Misc — 保持しているがほぼ使わない（4 スキル）

特定状況で役立つユーティリティ群。

- **git-guardrails-claude-code** — Hooks で危険な git コマンド（push、reset --hard、clean など）の実行をブロック
- **migrate-to-shoehorn** — テストファイルの `as` 型アサーションを `@total-typescript/shoehorn` に移行
- **scaffold-exercises** — 演習用ディレクトリ（sections / problems / solutions / explainers）の雛形を生成
- **setup-pre-commit** — Husky + lint-staged + Prettier + 型チェック + テストの pre-commit を構築

### Personal — 自分用（プラグインで宣伝されない、2 スキル）

Matt Pocock 自身のセットアップに紐付くスキル。

- **edit-article** — 記事の構成・明瞭さ・文章を改善（節再構成、引き締め）
- **obsidian-vault** — Obsidian vault のノートを wikilink/index ノート付きで検索・作成・管理

#### 補足: obsidian-vault の正体

「コミット時に自動でメモが登録される」ようなフックではなく、**対話型のメモ操作スキル**だ。`SKILL.md` の `description` が用途を端的に表している:

> Search, create, and manage notes in the Obsidian vault with wikilinks and index notes. Use when user wants to find, create, or organize notes in Obsidian.

ユーザーが Claude Code に明示的に「あのノートを探して」「これをメモして」「関連ノートを整理して」と頼んだ時に発動する。仕込まれているのは Matt 個人の vault ルール:

- **vault パス**: `/mnt/d/Obsidian Vault/AI Research/`（WSL パス、ハードコード）
- **構造**: フラット（フォルダで分けない）
- **命名**: Title Case
- **索引**: フォルダの代わりに `Ralph Wiggum Index.md` / `Skills Index.md` / `RAG Index.md` のような **Index ノート** を作り、`[[wikilink]]` のリストで集約
- **リンク**: 各ノートの末尾に `[[wikilink]]` で関連ノートを並べる

ワークフローは 4 つに集約されている:

1. **検索** — `find … -name "*.md" | grep -i keyword` または `grep -rl keyword` で vault スキャン
2. **新規作成** — Title Case ファイル名 + 末尾に `[[wikilink]]` を書く
3. **バックリンク発見** — `grep -rl "\[\[Note Title\]\]"` で被リンクを引く
4. **Index ノート発見** — `find … -name "*Index*"`

「personal」カテゴリでプラグインに宣伝されないのは、vault パスと命名規則が Matt 個人のものだから。流用するなら `SKILL.md` の vault パスと運用ルールを自分用に書き換えるのが前提だ。

post-commit で自動的に知識を登録したい場合は、別途仕組みを組む必要がある:

- **git の `post-commit` フック** で `claude` CLI を蹴り、コミット内容を要約して vault に書かせる
- Claude Code の `Stop` / `PostToolUse` フックで「対話で得た知見を vault に書け」と発火させる
- `obsidian-vault` スキルはその「書く先のルール（フラット構造・Title Case・Index ノート）」を提供する

つまりこのスキルは「自動化機構」ではなく「Obsidian に書く時の作法集」だ。

---

中核は Engineering の `diagnose` / `tdd` / `grill-with-docs` / `to-prd` / `to-issues` あたり。これが「現場のエンジニアリング作法を Markdown スキルに落としたもの」の本体だ。Productivity の `caveman`（トークン削減）と `grill-me`（要件詰問）は単独で導入する価値が大きく、SNS でもよく話題に上がっている。

## 導入方法（30 秒セットアップ）

```bash
npx skills@latest add mattpocock/skills
```

1. 上記コマンドを実行
2. 使いたいスキルとインストール先の AI エージェントを選択（**`/setup-matt-pocock-skills` を必ず選ぶ** — このスキルが他のスキルの設定基盤となるため）
3. エージェントで `/setup-matt-pocock-skills` を実行
   - Issue トラッカーの設定（GitHub / Linear / ローカルファイル）
   - トリアージ時のラベル設定
   - ドキュメント保存先の設定
4. 完了

## まとめ

「AI に任せたら意図が伝わらなかった」「コードが動かない」「コードベースが荒れる」——これらは 2026 年現在の AI 開発で最もよく聞く悩みだ。Skills for Real Engineers はそれぞれの問題に対して、スキル 1 つ 1 つという粒度で解決策を提供している。既存の重厚なフレームワークに疲れた開発者にとって、魅力的な選択肢になりえる。

Matt Pocock のニュースレター（約 60,000 人登録）でも継続的に新スキルが公開されているため、フォローしておく価値がある。
