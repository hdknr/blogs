---
title: "ウェブサイトのスタイルを丸ごと抽出してDESIGN.md / SKILL.mdを自動生成するChrome拡張 — Claude Codeに渡すデザイン文脈を一瞬で構造化する"
date: 2026-06-16
lastmod: 2026-06-16
slug: "chrome-extension-design-md-skill-md-extractor"
draft: false
source_url: "https://github.com/hdknr/blogs/issues/1#issuecomment-4714965668"
description: "Chrome拡張「DESIGN.md Style Extractor - TypeUI」を使えば、任意のWebサイトのカラー・タイポグラフィ・スペーシングをワンクリックでDESIGN.mdまたはSKILL.mdに書き出せる。Claude Code・Codex・Google Stitchに渡すデザイン文脈を自動構造化する方法を解説する。"
categories: ["ツール/開発環境"]
tags: ["chrome-extension", "claude-code", "DESIGN.md", "SKILL.md", "デザインシステム"]
---

「このサイトのデザインに合わせて作って」——Claude Code や Codex に開発を任せるとき、毎回この説明から始める必要があった。
フォントサイズ、カラーパレット、スペーシング、ボーダー半径……これらをテキストで伝えるのは手間がかかるし、伝え漏れも起きやすい。

この課題を解決するChrome拡張が登場した。**任意のウェブサイトを開いてボタンを押すだけで、そのサイトのデザインシステムを`DESIGN.md`または`SKILL.md`として書き出せる**ツールだ。

## 何ができるか

GitHub リポジトリ [bergside/design-md-chrome](https://github.com/bergside/design-md-chrome)（2026年6月時点でスター2,200以上）で公開されているこの拡張の主な機能は次のとおりだ。

- **任意のウェブサイトのスタイルを抽出** — タイポグラフィ、カラー、スペーシング、ボーダー半径、シャドウ、モーションなど
- **`DESIGN.md` か `SKILL.md` を選んで出力** — 用途に合わせて生成形式を切り替えられる
- **Claude Code / Codex / Google Stitch にそのまま渡せる** — 生成されたファイルをAIエージェントのコンテキストに置くだけで使える
- **無料** — Chrome Web Store から無料でインストール可能

## DESIGN.md と SKILL.md の違い

| ファイル | 主な用途 |
|---------|---------|
| `DESIGN.md` | デザインシステムのドキュメント。色・フォント・スペーシングなどのトークンを一覧化する |
| `SKILL.md` | AIエージェント向けのスキル定義。エージェントが参照して実装の判断に使う形式 |

Claude Code では`SKILL.md`をプロジェクトに置くと、定義されたデザインルールをコンテキストとして参照しながらコンポーネントを実装する。

## インストール

Chrome Web Store で「DESIGN.md Style Extractor - TypeUI」を検索するか、以下のリンクから直接インストールできる。

- [DESIGN.md Style Extractor - TypeUI（Chrome Web Store）](https://chromewebstore.google.com/detail/designmd-style-extractor/ogpdnchdjiibhobphelbbkemnnemkfma)

ソースコードはオープンソースとして公開されている。

- [bergside/design-md-chrome - GitHub](https://github.com/bergside/design-md-chrome)

## 使い方

1. 参考にしたいデザインのサイトをChromeで開く
2. 拡張のアイコンをクリック
3. `DESIGN.md` か `SKILL.md` を選択
4. 生成されたMarkdownをコピーしてプロジェクトルートに配置

たとえばStripeのサイトを開いて抽出すれば、Stripeのデザイン言語を記述したファイルが得られる。それをClaude Codeのプロジェクトに置けば、「Stripeっぽいデザインで」と口で説明しなくても、エージェントがデザインシステムを参照しながら実装を進めてくれる。

## 生成されるDESIGN.mdの例

抽出されるMarkdownは以下のような構造になる。

```markdown
# Design System

## Colors
- Primary: #635BFF
- Background: #0A2540
- Text: #425466

## Typography
- Font family: -apple-system, BlinkMacSystemFont, "Segoe UI"
- Base size: 16px
- Heading scale: 1.25

## Spacing
- Base unit: 8px
- Section padding: 64px

## Border Radius
- Small: 4px
- Default: 8px
- Large: 16px
```

CSSのカスタムプロパティや実際に使われているスタイルをスキャンして、設計トークンとして整理する。

## Claude Codeでの活用方法

生成した`SKILL.md`をプロジェクトのルートに配置しておくと、Claude Codeが自動的に読み込む。

```text
myproject/
├── SKILL.md        ← 抽出したデザインスキル
├── CLAUDE.md
├── src/
└── ...
```

あとは普通に「ログインフォームを実装して」と指示するだけで、エージェントは`SKILL.md`に定義されたフォントサイズやカラーを参照しながらコンポーネントを組んでくれる。

## まとめ

| 従来 | この拡張を使う場合 |
|------|-----------------|
| 毎回デザインをテキストで説明 | ワンクリックで構造化ファイルを生成 |
| 説明の抜け漏れが発生しやすい | CSS変数から自動抽出するため漏れが少ない |
| 汎用プロンプトになりがち | デザインシステムを参照した精度の高い実装 |

Claude Code にデザイン文脈を渡す作業は、これまで「毎回やり直す手作業」だった。この拡張を使えば、**参考サイトを開いてクリックするだけで、再利用可能なデザイン定義ファイルが手に入る**。AIエージェントを使った開発フローに組み込むと、デザインの一貫性を保ちながら実装速度を上げられる。
