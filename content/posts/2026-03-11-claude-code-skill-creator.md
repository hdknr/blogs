---
title: "Claude Code のスキルを作るなら skill-creator プラグインを使おう"
date: 2026-03-11
lastmod: 2026-03-11
draft: false
source_url: "https://github.com/hdknr/blogs/issues/1#issuecomment-4042055345"
categories: ["AI/LLM"]
tags: ["claude-code", "claude", "agent", "prompt"]
---

Anthropic が公開した「The Complete Guide to Building Skills for Claude」という 33 ページの PDF ガイドが話題になっています。このガイドをそのまま Claude Code のメモリに読み込ませてスキル構築に活用しようとする人もいますが、実は公式の **skill-creator プラグイン**を使う方がはるかに効率的です。

skill-creator はガイドの内容をすべて反映しているだけでなく、テスト・最適化・トリガー精度改善といった仕組みも組み込まれています。PDF をメモリに入れるとコンテキストウィンドウを圧迫するリスクもあるため、新規スキル作成には skill-creator を導入するのがおすすめです。

## Claude Code のスキルとは

スキルとは、Claude に特定のタスクの実行方法を教える **指示・スクリプト・リソースのフォルダ** です。`SKILL.md` ファイルに YAML フロントマターと指示を記述するだけで作成できます。

Claude Code は 3 段階の情報ロードシステム（**Progressive Disclosure**）を採用しています。

1. **起動時**: インストール済みスキルの名前と説明文のみをシステムプロンプトに読み込む（スキルあたり約 50〜100 トークン）
2. **判定時**: ユーザーの入力に関連するスキルがあるかを判定
3. **実行時**: 該当スキルの全内容をロード

この仕組みにより、多数のスキルをインストールしてもコンテキストウィンドウを無駄に消費しません。

## skill-creator プラグインのインストール

skill-creator は Anthropic 公式マーケットプレイスに含まれています。Claude Code 内で以下のコマンドを実行するだけでインストールできます。

```shell
/plugin install skill-creator@claude-plugins-official
```

インストール後、プラグインを有効化します。

```shell
/reload-plugins
```

なお、`/plugin` コマンドで **Discover** タブを開き、GUI からインストールすることも可能です。プラグイン機能を利用するには Claude Code **バージョン 1.0.33 以上** が必要です（`claude --version` で確認できます）。

## skill-creator の 4 つのモード

**skill-creator** は Anthropic が公式に提供するプラグインで、スキルの開発ライフサイクル全体をサポートします。4 つのモードがあります。

### Create モード

ゼロからスキルを作成します。

```
/skill-creator Create a new skill that reviews PRs for security issues
```

スキルの目的を伝えるだけで、適切な `SKILL.md` のフロントマター・指示・ディレクトリ構造を自動生成します。

### Eval モード

スキルの動作をテストする評価（Eval）を実行します。

```
/skill-creator Run evals on my code-review skill
```

テストプロンプトと期待する結果を定義し、スキルが想定通りに動作するかを検証します。モデル更新時の品質低下（回帰）の検出にも活用できます。

### Improve モード

テスト結果に基づいてスキルを改善します。

```
/skill-creator Improve my deploy skill based on these test cases
```

### Benchmark モード

スキルのパフォーマンスを定量的に測定します。

```
/skill-creator Benchmark my skill across 10 runs and show variance
```

測定項目は以下の通りです。

- 評価の合格率
- 経過時間
- トークン使用量
- 実行ごとのばらつき（分散分析）

## マルチエージェントによる並列テスト

skill-creator は独立したエージェントを並列に起動して評価を実行します。各エージェントは独自のコンテキストで動作するため、テスト間の干渉（コンテキスト汚染）がありません。

また、**Comparator エージェント** による A/B テストにも対応しています。2 つのスキルバージョン、またはスキルあり/なしの出力をブラインド比較し、変更が実際に改善をもたらしたかを判定できます。

## トリガー精度の改善

スキルの説明文（description）は、Claude がそのスキルをいつ発動すべきか判断するための重要な要素です。skill-creator はこの説明文を最適化し、意図したタイミングで正確にスキルが発動するよう調整します。公式ブログによると、6 つの公開スキルのうち 5 つでトリガー精度の改善が確認されています。

## PDF ガイドと skill-creator の違い

| 観点 | PDF ガイドを読み込む | skill-creator を使う |
|------|---------------------|---------------------|
| コンテキスト消費 | 大（33 ページ分） | 小（必要時のみロード） |
| テスト機能 | なし | Eval・Benchmark 内蔵 |
| A/B テスト | なし | Comparator エージェント |
| スキル改善 | 手動 | Improve モードで自動化 |
| トリガー最適化 | 手動 | 自動で説明文を最適化 |
| 最新の反映 | PDF 更新待ち | プラグイン更新で即時 |

PDF ガイド自体は Claude Code のスキルシステムの設計思想や背景を理解するのに優れた資料です。一方、実際にスキルを作成・テスト・改善する作業には skill-creator が適しています。

## まとめ

Claude Code でスキルを作るなら、PDF をメモリに詰め込むよりも **skill-creator プラグイン** を導入しましょう。スキルの作成・テスト・改善・ベンチマークまで一貫してサポートしてくれます。

## 参考

- [Skill Creator – Claude Plugin](https://claude.com/plugins/skill-creator)
- [Improving skill-creator: Test, measure, and refine Agent Skills](https://claude.com/blog/improving-skill-creator-test-measure-and-refine-agent-skills)
- [Extend Claude with skills - Claude Code Docs](https://code.claude.com/docs/en/skills)
- [The Complete Guide to Building Skills for Claude (PDF)](https://resources.anthropic.com/hubfs/The-Complete-Guide-to-Building-Skill-for-Claude.pdf)
- [anthropics/claude-plugins-official - skill-creator](https://github.com/anthropics/claude-plugins-official/tree/main/plugins/skill-creator)
