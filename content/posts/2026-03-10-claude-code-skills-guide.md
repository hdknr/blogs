---
title: "Claude Code Skills 構築完全ガイド — Anthropic 公式 33 ページの要点まとめ"
date: 2026-03-10
lastmod: 2026-03-10
draft: false
source_url: "https://github.com/hdknr/blogs/issues/1#issuecomment-4031784046"
categories: ["AI/LLM"]
tags: ["claude-code", "claude", "anthropic", "prompt", "agent"]
---

Anthropic が公開した「The Complete Guide to Building Skills for Claude」は、Claude Code のスキル機能を本格的に活用するための 33 ページにわたる公式ガイドです。この記事では、ガイドの要点を日本語でまとめます。

## Skills とは何か

Skills は、Claude に特定のタスクやワークフローを教えるための **再利用可能な指示セット** です。フォルダにパッケージ化され、一度作れば Claude.ai、Claude Code、API のすべてで動作します。

従来のように毎回プロンプトで細かく指示する代わりに、Skills を使えば「一度教えて、何度でも使える」ようになります。

## Skills のファイル構造

```
my-skill/
├── SKILL.md          # メインの指示ファイル（必須）
├── scripts/          # 補助スクリプト
├── references/       # 参考資料
└── assets/           # アセットファイル
```

重要なルール:

- メインファイルは必ず `SKILL.md`（大文字小文字を区別）
- フォルダ名は kebab-case（例: `notion-project-setup`）
- README.md は含めない

## YAML フロントマターの設計

`SKILL.md` の冒頭に YAML フロントマターを記述します。ここがスキルの「顔」になります。

```yaml
---
name: deploy-checker
description: "本番デプロイ前のチェックリストを実行する。デプロイや本番リリースの話題が出たときに使用する"
---
```

`description` には **何をするか** と **いつ使うか** の 2 つを含めることが重要です。Claude はこのメタデータだけでスキルの使用タイミングを判断します。

## 3 段階のプログレッシブディスクロージャー

Claude のスキル読み込みは 3 段階で行われます:

1. **Level 1: YAML フロントマター**（常に読み込み） — 名前と説明文だけで約 50〜100 トークン
2. **Level 2: SKILL.md 本体**（関連すると判断したときに読み込み） — 詳細な指示
3. **Level 3: リンクファイル**（必要に応じて発見・読み込み） — scripts/ や references/ 内のファイル

この設計により、多数のスキルを登録してもコンテキストウィンドウを圧迫しません。

## 5 つの実装パターン

ガイドでは、実際のユースケースから導かれた 5 つのパターンが紹介されています。

### 1. シーケンシャルワークフロー

複数のステップを順番に実行するパターンです。例えば「Issue を読む → 調査する → PR を作成する」のような定型フローに適しています。

### 2. マルチ MCP 調整

複数の MCP サーバー（GitHub、Slack、データベースなど）を連携させるパターンです。各サービス間のデータフローを定義します。

### 3. 反復的改善

出力を段階的に改善するパターンです。最初にドラフトを生成し、チェック → 修正を繰り返して品質を上げます。

### 4. 文脈認識ツール選択

状況に応じて異なるツールやアプローチを使い分けるパターンです。条件分岐のロジックをスキル内に記述します。

### 5. ドメイン固有知識

業界固有の用語、ルール、ベストプラクティスを組み込むパターンです。references/ に資料を配置して参照させます。

## テスト戦略

スキルのテストは 3 段階で行います:

| テスト種別 | 確認内容 |
|---|---|
| トリガーテスト | 正しいタイミングでスキルが読み込まれるか |
| 機能テスト | 出力が期待通りか |
| パフォーマンス比較 | スキルなしと比較して改善されているか |

## skill-creator で自分専用のスキルを量産する

元ツイートで紹介されている活用法が特に実践的です:

> この資料そのまま Claude Code に投げて、オリジナルの「skill-creator」の skills を作ると、それ以降の skills の精度と品質が爆上がりします。
>
> — @tokyovibehacker

つまり、**このガイド自体を Claude Code に読ませて「スキルを作るためのスキル」を作る** というメタ的なアプローチです。こうすることで、以降のスキル作成時に:

- フロントマターの description が適切に設計される
- プログレッシブディスクロージャーを意識した構造になる
- テスト観点が自動的に組み込まれる

という品質向上が期待できます。

## 配布とチーム共有

- GitHub リポジトリでホストし、チームで共有するのが推奨
- Claude.ai の設定画面からスキルをアップロードして有効化
- MCP ドキュメントからリンクするモデルも利用可能

## 参考リンク

- [公式ガイド PDF](https://resources.anthropic.com/hubfs/The-Complete-Guide-to-Building-Skill-for-Claude.pdf)
- [公式ブログ記事](https://claude.com/blog/complete-guide-to-building-skills-for-claude)
- [ガイド Markdown 版（Gist）](https://gist.github.com/joyrexus/ff71917b4fc0a2cbc84974212da34a4a)

## まとめ

Claude Code の Skills は、繰り返し行うワークフローを標準化・自動化する強力な仕組みです。33 ページの公式ガイドは、構造設計からテスト、配布まで網羅しており、Skills を本格運用するなら必読の資料です。まずはガイド自体を Claude Code に読ませて「skill-creator」スキルを作るところから始めてみてはいかがでしょうか。
