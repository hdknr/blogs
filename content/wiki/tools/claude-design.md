---
title: "Claude Design"
description: "日本語のざっくり指示でスライド・LP・アプリ試作品・アニメーションなど7種類のデザインを『ライブHTML』で生成する Anthropic のAIデザインツール"
date: 2026-07-15
lastmod: 2026-07-15
aliases: ["Claude Design", "claude.ai/design", "デザインシステム機能"]
related_posts:
  - "/posts/2026/06/claude-design-update-2026/"
tags: ["claude", "anthropic", "デザイン", "UI/UX", "ノーコード"]
---

## 概要

Claude Design は、日本語でざっくり指示するだけでスライド・ランディングページ・アプリのモックアップ・提案書などを生成できる Anthropic の AI デザインツール。2026年4月17日に公開され、6月18日にデザインシステム機能を含む大幅アップデートが行われた。出力は静止画ではなく操作できる **ライブHTML** 形式なのが特徴。`claude.ai/design` から利用でき、Pro・Max・Team・Enterprise プランが対象（無料プランは不可、Pro は $20/月で追加料金なし）。

## 詳細

### 7種類の作り方（カード）

ホーム画面の「Make something new」に7枚のカードが並ぶ。作りたいものでカードを選ぶ。

| カード | 用途 |
|---|---|
| **Slides** | セミナー資料・ピッチデック。Upload a doc / Paste your notes / Existing deck の3入力 |
| **Product prototype** | 操作できるアプリ・サービスの動く試作品 |
| **Product wireframe** | 画面構成の骨格だけを先に決める |
| **Document** | LP・提案書・レポート・履歴書。最も汎用的。「Talk it out」機能あり |
| **Animation** | 動きのあるバナー・モーショングラフィック（Edit 不可、Tweaks のみ） |
| **Blank canvas** | 完全な白紙から作る |
| **Start with a file** | DOCX/PPTX/XLSX/PDF/JPG/PNG をデザインに変換 |

### デザインシステム機能（2026年6月アップデート）

「Set up design system」でブランドカラー・フォント・ロゴを一度登録すると以後のデザインに自動反映され、「毎回色がバラバラになる」問題を解消する。登録は2択。

- **Create here**（初心者向け）: フォーム入力・GitHub URL・Figma ファイルなど。コード不要
- **Create using Claude Code**（BEST FIDELITY）: React 製サービスのコードからブランド情報を読み込む。`node -v` 確認 → `package.json` と `tokens.js` 作成 → Claude Code で `/design-sync` 実行

### 使いこなしのコツ

- ビジュアルスタイルは最初に決める（途中の全変更は一貫性を崩す）
- 生成後は「Tweaks」パネルでチャット感覚に修正。一度に全部変えず1つずつ
- プロンプトは「目的・構成・対象・スタイル」の4点を入れると精度が上がる
- アニメーションを PDF 書き出しすると動きが消える。保持するなら HTML 形式

## 関連ページ

- [Claude Code](/blogs/wiki/tools/claude-code/) — BEST FIDELITY のデザインシステム連携に使う
- [draw.io AI](/blogs/wiki/tools/draw-io-ai/) — AI による図表生成ツール

## ソース記事

- [Claude Design 大幅アップデート——7種類の作り方とデザインシステム機能を完全解説](/blogs/posts/2026/06/claude-design-update-2026/) — 2026-06-24
