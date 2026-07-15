---
title: "Google製 DESIGN.md — AIコーディングエージェントにデザインを伝える標準フォーマット"
date: 2026-06-24
lastmod: 2026-06-24
slug: "google-design-md-ai-coding"
draft: false
source_url: "https://github.com/hdknr/blogs/issues/1#issuecomment-4785282859"
categories: ["AI/LLM"]
description: "Google Labs が公開した DESIGN.md は、YAMLトークン＋Markdownの二層構造でAIコーディングエージェントにデザインシステムを伝える標準フォーマット。フォーマット仕様・CLI（lint/diff/export）・Tailwind連携を解説。"
tags: ["DESIGN.md", "AIコーディング", "デザインシステム", "デザイントークン", "Google"]
---

「いい感じのUIにして」と10回言っても伝わらないのに、ファイルを1枚置いたら一発で意図通りになった――。そんな体験談とともに X（旧 Twitter）で話題になったのが、Google Labs が公開した **DESIGN.md** というフォーマット仕様だ。

本記事では DESIGN.md の概要、フォーマットの仕組み、付属 CLI の使い方を解説する。

## DESIGN.md とは

[google-labs-code/design.md](https://github.com/google-labs-code/design.md)（2026年6月時点で GitHub スター 16,000 超）は、**AIコーディングエージェントにビジュアルアイデンティティを伝えるためのファイルフォーマット仕様**だ。

> A format specification for describing a visual identity to coding agents. DESIGN.md gives agents a persistent, structured understanding of a design system.

CLAUDE.md や AGENTS.md がコーディングの振る舞いを定義するのと同じ発想で、DESIGN.md はデザインシステムを定義する。エージェントがこのファイルを読めば、色・タイポグラフィ・余白・コンポーネントの具体値を把握したうえでコードを生成できる。

## フォーマットの構造

DESIGN.md は **2つの層** で構成される。

| 層 | 内容 | 目的 |
|---|---|---|
| YAML フロントマター | デザイントークン（機械可読） | エージェントに正確な値を与える |
| Markdown 本文 | デザイン根拠の説明（人間可読） | *なぜその値なのか* をコンテキストとして与える |

トークンは規範的な値であり、散文はその適用方法を補足する。この二層構造が「10回言っても伝わらなかった」問題を解消する鍵だ。

### 実際の例

```markdown
---
name: Heritage
colors:
  primary: "#1A1C1E"
  secondary: "#6C7278"
  tertiary: "#B8422E"
  neutral: "#F7F5F2"
typography:
  h1:
    fontFamily: Public Sans
    fontSize: 3rem
  body-md:
    fontFamily: Public Sans
    fontSize: 1rem
rounded:
  sm: 4px
  md: 8px
spacing:
  sm: 8px
  md: 16px
---

## Overview

Architectural Minimalism meets Journalistic Gravitas. The UI evokes a
premium matte finish — a high-end broadsheet or contemporary gallery.

## Colors

The palette is rooted in high-contrast neutrals and a single accent color.

- **Primary (#1A1C1E):** Deep ink for headlines and core text.
- **Secondary (#6C7278):** Sophisticated slate for borders, captions, metadata.
- **Tertiary (#B8422E):** "Boston Clay" — the sole driver for interaction.
- **Neutral (#F7F5F2):** Warm limestone foundation, softer than pure white.
```

このファイルを読んだエージェントは、深いインク色の見出し（Public Sans）、温かみのある石灰岩色の背景、Boston Clay 色の CTA ボタンを持つ UI を生成できる。

## トークンスキーマ

```yaml
version: <string>       # optional, current: "alpha"
name: <string>
description: <string>   # optional
colors:
  <token-name>: <Color>
typography:
  <token-name>: <Typography>
rounded:
  <scale-level>: <Dimension>
spacing:
  <scale-level>: <Dimension | number>
components:
  <component-name>:
    <token-name>: <string | token reference>
```

トークン参照には `{colors.primary}` のようなパス記法を使う。コンポーネントトークンでは `backgroundColor`・`textColor`・`typography`・`rounded`・`padding` などのプロパティが有効だ。

## CLI の使い方

`@google/design.md` パッケージとして npm に公開されている。

### インストール

```bash
npm install @google/design.md
```

### lint — 構造検証

```bash
npx @google/design.md lint DESIGN.md
```

壊れたトークン参照、WCAG コントラスト比違反、孤立トークンなどを JSON 形式で報告する。

```json
{
  "findings": [
    {
      "severity": "warning",
      "path": "components.button-primary",
      "message": "textColor (#ffffff) on backgroundColor (#1A1C1E) has contrast ratio 15.42:1 — passes WCAG AA."
    }
  ],
  "summary": { "errors": 0, "warnings": 1, "info": 1 }
}
```

### diff — バージョン比較

```bash
npx @google/design.md diff DESIGN.md DESIGN-v2.md
```

トークンレベルの追加・削除・変更を検出し、リグレッションがあれば `exit code 1` を返す。

### export — 他フォーマット出力

```bash
# Tailwind v3 JSON
npx @google/design.md export --format json-tailwind DESIGN.md > tailwind.theme.json

# Tailwind v4 CSS
npx @google/design.md export --format css-tailwind DESIGN.md > theme.css

# W3C DTCG tokens.json
npx @google/design.md export --format dtcg DESIGN.md
```

Tailwind v3 の `theme.extend` JSON、Tailwind v4 の CSS カスタムプロパティ、W3C Design Tokens Format Module への出力に対応している。

### spec — 仕様出力

```bash
npx @google/design.md spec
```

エージェントプロンプトにスペックを注入したいときに便利だ。

## リンティングルール一覧

| ルール | 重大度 | チェック内容 |
|---|---|---|
| `broken-ref` | error | 未解決のトークン参照 |
| `missing-primary` | warning | `primary` カラーが未定義 |
| `contrast-ratio` | warning | WCAG AA（4.5:1）未満のコンポーネント |
| `orphaned-tokens` | warning | どのコンポーネントにも参照されていないトークン |
| `token-summary` | info | 各セクションのトークン数サマリ |
| `missing-sections` | info | 他トークンが存在するのに spacing/rounded がない |
| `missing-typography` | warning | カラーはあるがタイポグラフィがない |
| `section-order` | warning | 推奨セクション順序からの逸脱 |
| `unknown-key` | warning | `colours:` → `colors:` のようなタイポ候補 |

## まとめ

DESIGN.md は「テキストで何度伝えても伝わらない」というデザイン指示の属人化問題に、**構造化トークン × 設計根拠の散文**という二層アプローチで答えている。CLAUDE.md や AGENTS.md と並べてリポジトリに置くことで、AIコーディングエージェントはコードだけでなくデザインの意図も理解した状態で動作できる。

まだ `alpha` だが、GitHub スターの伸びと活発な開発を見ると、AIコーディング時代のデザインシステム管理の標準になる可能性は高い。
