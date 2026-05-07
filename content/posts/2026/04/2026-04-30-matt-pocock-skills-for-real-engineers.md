---
title: "Matt Pocock の「Skills for Real Engineers」— Claude Code に現場のエンジニアリング作法を仕込む Markdown スキル集"
date: 2026-04-30
lastmod: 2026-04-30
draft: false
source_url: "https://github.com/hdknr/blogs/issues/1#issuecomment-4349316259"
categories: ["AI/LLM"]
tags: ["Claude Code", "Matt Pocock", "スキル", "AI開発", "TypeScript"]
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
