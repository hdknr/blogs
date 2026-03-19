---
title: "geo-seo-claude：AI検索時代のSEO最適化をClaude Codeで自動化するオープンソースツール"
date: 2026-03-12
lastmod: 2026-03-12
draft: false
source_url: "https://github.com/hdknr/blogs/issues/1#issuecomment-4043632679"
categories: ["AI/LLM"]
tags: ["claude-code", "claude", "llm", "agent", "github"]
---

ChatGPTやClaude、Perplexityなどの AI 検索エンジンに自社サイトを見つけてもらうための最適化ツール「[geo-seo-claude](https://github.com/zubair-trabzada/geo-seo-claude)」がオープンソースで公開されている。従来の SEO に加えて、AI が引用・参照しやすいコンテンツ構造を自動分析・提案してくれる Claude Code 用スキルだ。

## GEO（Generative Engine Optimization）とは

従来の SEO が Google などの検索エンジンでの上位表示を目指すのに対し、GEO は AI 検索エンジン（ChatGPT、Claude、Perplexity、Gemini、Google AI Overviews）での「引用されやすさ」を最適化する考え方だ。

AI がウェブ上の情報を参照して回答を生成する際、どのサイトが引用されるかは以下のような要素に左右される：

- コンテンツの構造化の度合い
- AI クローラーへのアクセス許可（robots.txt）
- ブランドの権威性（各プラットフォームでの言及）
- スキーママークアップの品質

## geo-seo-claude の主な機能

### 引用可能性スコアリング（Citability Scoring）

コンテンツが AI に引用されやすい構造になっているかを評価する。134〜167語の最適な段落長、明確な見出し構造、事実ベースの記述かどうかなどをチェックする。

### AI クローラー分析

`robots.txt` を解析し、14以上の AI ボット（GPTBot、ClaudeBot、PerplexityBot など）へのアクセス許可状況を確認する。ブロックしているボットがあれば、許可すべきかの推奨事項を提示する。

### ブランド言及スキャン

YouTube、Reddit、Wikipedia、LinkedIn など7つ以上のプラットフォームでのブランド言及を検出する。AI は複数ソースでの言及が多いサイトをより信頼性が高いと判断する傾向がある。

### プラットフォーム別最適化

ChatGPT、Perplexity、Google AI Overviews それぞれの特性に合わせた最適化提案を行う。各 AI 検索エンジンがコンテンツを処理する方法は異なるため、プラットフォームごとのカスタマイズが重要になる。

### llms.txt 生成

AI クローラーがサイト構造を理解しやすくするための新興標準ファイル `llms.txt` を自動生成する。Answer.AI の Jeremy Howard が提案した規格で、`robots.txt` の AI 版のような位置づけを目指している（現時点ではまだ提案段階）。

### PDF レポート生成

スコアゲージ、棒グラフ、カラーコード付きテーブルなど、視覚的にわかりやすいプロフェッショナルな監査レポートを PDF 形式で出力できる。

## インストールと使い方

### インストール

ワンコマンドでインストールできる：

```bash
curl -fsSL https://raw.githubusercontent.com/zubair-trabzada/geo-seo-claude/main/install.sh | bash
```

または手動で：

```bash
git clone https://github.com/zubair-trabzada/geo-seo-claude.git
cd geo-seo-claude
./install.sh
```

### 主なコマンド

Claude Code 内で以下のスラッシュコマンドとして利用する：

```bash
# 完全監査（全項目チェック）
/geo audit https://example.com

# 60秒クイック診断
/geo quick https://example.com

# 引用可能性スコアのみ
/geo citability https://example.com

# PDF レポート生成
/geo report-pdf
```

## 技術的な仕組み

内部では5つのサブエージェントが並列で実行される：

1. **AI 可視性エージェント** — AI クローラーのアクセス状況を分析
2. **プラットフォーム分析エージェント** — 各 AI 検索エンジンでの表示状況を評価
3. **技術 SEO エージェント** — 従来の SEO 基盤をチェック
4. **コンテンツ品質エージェント** — 引用されやすいコンテンツ構造を評価
5. **スキーマエージェント** — 構造化データの品質を分析

これらの結果を Python スクリプトで統合し、0〜100 の複合スコアを算出する。

## まとめ

AI 検索が急速に普及する中、従来の SEO だけではウェブサイトの可視性を維持するのが難しくなってきている。geo-seo-claude は Claude Code のスキルとして動作するため、開発者が普段の作業フローの中で GEO 最適化を取り入れられる点が実用的だ。GitHub で 2,800 以上のスターを獲得しており、注目度の高さがうかがえる。
