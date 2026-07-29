---
title: "Ponytail"
description: "AIエージェントに『7段のラダー』で意思決定させ、コードを書く前に本当に必要かを確認させる過剰実装抑制プラグイン。YAGNI を体現する"
date: 2026-07-15
lastmod: 2026-07-15
aliases: ["Ponytail", "YAGNI プラグイン", "7段ラダー"]
related_posts:
  - "/posts/2026/06/ponytail-ai-agent-minimal-code/"
tags: ["ponytail", "claude-code", "ai-agent", "yagni", "ツール/開発環境"]
---

## 概要

Ponytail（`DietrichGebert/ponytail`）は、AI エージェントに「ラダー（梯子）」と呼ばれる意思決定フローを組み込み、コードを書く前に本当に必要かを確認させる MIT ライセンスの OSS プラグイン（GitHub スター 54,000+）。名前の由来は「50行を1行に置き換えるあのシニア開発者」。Claude Code・Cursor・GitHub Copilot・Aider・Codex・Gemini CLI・OpenCode など14種類以上に対応する。

## 詳細

### 7段のラダー

コードを書く前にこの順で判断する。①本当に必要か(YAGNI) → ②既にあるか(再利用) → ③標準ライブラリで済むか → ④プラットフォームのネイティブ機能か → ⑤インストール済み依存か → ⑥1行で書けるか → ⑦該当しない時のみ最小限のコードを書く。ただし「問題を理解する」ことには手を抜かない（解決策の選択にだけ怠惰）。

### ベンチマーク（Haiku 4.5 / FastAPI+React / 12タスク）

ponytail はコード行数 -54%・トークン -22%・コスト -20%・時間 -27% を、**安全性100%を保ったまま**達成。「1行で書け」という単純プロンプトは安全性が95%に下がるのに対し、Ponytail は検証・エラー処理・セキュリティ・アクセシビリティをカットしない。コマンドは `/ponytail [lite|full|ultra|off]`、`/ponytail-review`、`/ponytail-audit` など。

### どんな場面で効くか（適用条件）

- **greenfield（新規開発）で最も効く** — ラダーの各段は「これから何を作るか」の新規判断そのもの。成熟した [brownfield](/blogs/wiki/concepts/brownfield-refactoring/) では効果が薄まる（作業がバグ修正・データ移行中心で新規判断が少なく、既存規約と役割が重なる）
- **「コード量」がリスクのとき効く** — 主要リスクが「正しさ」（間違った項目名・ID・データ不整合）にある場合は最適化が直交する。金融・仕訳系では短さより可読性を優先
- **弱いモデルに規律を与えるとき効く** — 高度な推論モデルではラダー自体がトークンを消費し逆効果になりうる
- 全部入れず「YAGNI → 既存資産の再利用 → 標準/組込み → 最小実装」の核だけを1行に蒸留して既存のエージェント規約に足す中間解もある

## 関連ページ

- [Brownfield リファクタリング](/blogs/wiki/concepts/brownfield-refactoring/) — Ponytail が薄まる成熟コードベース側の武器（対比）
- [Claude Code](/blogs/wiki/tools/claude-code/) — 主要な導入先
- [AI 開発と保守コスト](/blogs/wiki/concepts/ai-maintenance-cost/) — 書かないコードがバグ・CVE を生まない発想

## ソース記事

- [Ponytail — AIエージェントを「怠惰なシニア開発者」にするプラグイン](/blogs/posts/2026/06/ponytail-ai-agent-minimal-code/) — 2026-06-24
