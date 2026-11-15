---
title: "AI が書くフロントエンドが「2019年」で止まる問題と、Chrome チームの Modern Web Guidance"
date: 2026-11-15
lastmod: 2026-11-15
slug: "modern-web-guidance-ai-frontend"
draft: false
source_url: "https://github.com/hdknr/blogs/issues/694#issuecomment-6888099161"
categories: ["Web開発"]
tags: ["AIエージェント", "Agent Skills", "フロントエンド", "claude-code", "Baseline"]
---

## はじめに

「フロントエンド向けに今日の AI が書くコードの大きな問題は、2019年に留まっていること——学習データが古くて廃れたコードで満ちているから」。
X に投稿されたこの指摘（[@EngMoElgaraihy](https://x.com/EngMoElgaraihy/status/2121385282415006180)）が話題になりました。投稿が「公式の解決策」として紹介しているのが、Google Chrome チームのオープンソースプロジェクト **Modern Web Guidance** です。

Modern Web Guidance は 2026年5月の Google I/O でアーリープレビューとして発表され、11月10日に [1.0 として安定版](https://developer.chrome.com/blog/modern-web-guidance-v1)になりました。この記事では、なぜ AI のフロントエンドコードが古くなるのか、Modern Web Guidance がそれをどう補うのか、導入方法と注意点をまとめます。

## なぜ AI のフロントエンドは古くなるのか

原因は大きく 2 つあります。

1. **新しい機能を知らない**: 学習データには、ネイティブ機能が登場する前の「JavaScript で頑張る」コードが大量に含まれています。そのため、CSS Anchor Positioning で済むツールチップにライブラリを持ち出してしまいます。
2. **知っていても使い方やサポート状況を誤る**: 機能の存在は知っていても、構文が古かったり、どのブラウザで使えるかの前提が間違っていたりします。

[LogRocket の解説記事](https://blog.logrocket.com/chromes-modern-web-guidance-prevent-ai-coding-agents/)では、同じ Next.js アプリを同じプロンプトでガイダンスの有無だけ変えて作らせた比較が載っています。

| 機能 | ガイダンスなし | ガイダンスあり |
|---|---|---|
| モーダル | JS で状態とタイミングを自前管理 | ネイティブ `<dialog>` + CSS トランジション |
| タスクカード | メディアクエリ | コンテナクエリ |
| 2,000 件の検索 | `useMemo` で同期フィルタ | `scheduler.yield()` で分割処理 |
| ヘルプのツールチップ | Floating UI ライブラリ | CSS Anchor Positioning |

ガイダンスなしのモーダルは、JavaScript の状態と 300ms のタイムアウトで開閉を管理する実装でした。こうした「動くけれど古い」コードは、バンドルサイズや保守コスト、壊れる箇所を増やします。

## Modern Web Guidance とは

Modern Web Guidance は、Web プラットフォームのベストプラクティスとブラウザ互換性データを、コーディングエージェントに渡すための **Agent Skills**（エージェントが必要に応じて読み込む手順書・知識のパッケージ）のセットです。リポジトリは [GoogleChrome/modern-web-guidance](https://github.com/GoogleChrome/modern-web-guidance) で、1.0 の発表では Firefox と Edge のチームも協力していると紹介されています。

ポイントは次のとおりです。

- **Baseline に基づく**: 互換性の判断には [Baseline](https://web.dev/baseline) のデータを使います。何も指定しなければ「Baseline Widely available」を前提にし、必要に応じてフォールバックやプログレッシブエンハンスメントを付けます。
- **ガイドを検索して取り出す**: スキルはエージェントに CLI を呼ばせます。タスク内容でガイドを検索し、該当するガイドの Markdown を取り出して読ませます。全部を常にコンテキストへ載せるわけではありません。
- **幅広いカテゴリ**: README によれば、ガイドのカテゴリには accessibility、css、forms、performance、security、ui-components、built-in-ai、webmcp などがあります。

1.0 では次の機能が追加されました。

- **モダナイズのワークフロー**: HTML・CSS・JavaScript・`package.json` を静的に解析し、安全にアップグレードできる箇所を探します（対応パターンはまだ限定的）。
- **エキスパートによるレビュー**: ユーザー向けのガイドには、支援技術を使ったアクセシビリティテストも行われています。

## 導入方法

次のいずれか 1 つの方法で導入します。推奨は Chrome チームの CLI を使う方法です。対話式のウィザードが起動し、自動更新も有効になります。

```bash
npx modern-web-guidance@latest install
```

既にプレビュー版を入れている場合は、次のコマンドで 1.0 に更新できます。

```bash
npx modern-web-guidance@latest update
```

Claude Code だけで使う場合は、プラグインとして入れる方法もあります。[公式の Get started](https://developer.chrome.com/docs/modern-web-guidance/get-started) にある次の 2 ステップを実行します。

```bash
claude plugin marketplace add GoogleChrome/modern-web-guidance
claude plugin install modern-web-guidance@googlechrome
```

ほかにも Codex、Copilot CLI、Gemini CLI、Antigravity、WebStorm、Goose などの導入手順が用意されています。Vercel の Skills CLI や GitHub CLI でも入れられます（どちらか一方）。

```bash
# Vercel Skills CLI の場合
npx skills add GoogleChrome/modern-web-guidance

# GitHub CLI の場合
gh skill install GoogleChrome/modern-web-guidance
```

## エージェントが内部でやっていること

スキルが入ると、エージェントは次の流れでガイドを参照します。CLI を直接実行すると、エージェントが何を受け取るかを確認できます。

```bash
# タスク内容からガイドを探す（id・description・featuresUsed・similarity を JSON で返す）
npx modern-web-guidance@latest search "animate a dialog modal backdrop"

# 選んだガイドを ID で取り出す（Markdown が出力される）
npx modern-web-guidance@latest retrieve "animate-to-from-top-layer"
```

## プロジェクトの Baseline ターゲットを指定する

サポートするブラウザの範囲は、`AGENTS.md` や `CLAUDE.md` に一文書くだけで指定できます。

```markdown
This project's Baseline target is Baseline 2024.
```

ターゲットによって、エージェントが機能をそのまま使うか、フォールバックを付けるかが変わります。単一エンジンだけが実装している実験的機能や Origin Trial（Chrome が期間限定で試験提供する機能）は、検索には出てきますが、既定ではガイドを取り出せません。使いたい場合はプロジェクトルートで、必要なものだけ明示的にオプトインします。

```bash
# 実験的機能を許可する場合
npx modern-web-guidance@latest set-allow-volatile-features

# Origin Trial を許可する場合
npx modern-web-guidance@latest set-allow-origin-trials
```

## 効果はどのくらいか

元の投稿は「成功率と品質が 56% から 88% に上がる」と紹介していますが、この数字は Chrome の公式ブログでは確認できませんでした。

公式には [評価ダッシュボード](https://googlechrome.github.io/modern-web-guidance-src/) が公開されています。完成したアプリを Playwright を使って実ブラウザで開き、DOM・スタイル・ソースを要件ごとにチェックして「通ったチェック数 ÷ 実行したチェック数」で合格率を出す方式です。

1.0 の発表記事には、導入企業の事例として次の数字が載っています。

- **note**: 180 回の評価で、モダン Web のチェックの合格率が 61% → 94%
- **WeTV**: 失敗したパフォーマンスチェックの 90% をエージェントが解決し、デバッグ時間が 4 時間 → 30 分
- **MetaMask**: レビューボットが約 480 件の PR のうち 64 件にコメントし、43 件が修正された

数字は環境やタスクによって変わるので、自分のプロジェクトで試して確かめるのが確実です。

## 注意点

ガイダンスはあくまで「出発点を良くする」ものです。LogRocket の記事も、次のような点を指摘しています。

- コードレビューや実ブラウザでのテストの代わりにはならない。
- アクセシビリティは引き続き確認が必要。
- Anchor Positioning のような新しい機能は、対象ブラウザによってはフォールバックやライブラリがまだ必要。

ネイティブ `<dialog>` に置き換えた場合も、キーボード操作・フォーカスの戻り・スクリーンリーダーの読み上げは自分で確かめておきましょう。

公式ブログは、実行時の検証には **Chrome DevTools for agents** を組み合わせることを勧めています。低スペック CPU をシミュレートしたパフォーマンストレースで INP（操作してから画面が反応するまでの時間の指標）を確認したり、メモリリークを調べたりする用途です。

## まとめ

- AI のフロントエンドコードが古くなるのは、学習データに「ネイティブ機能がなかった頃のコード」が多く、新機能やブラウザサポートの知識が欠けているから。
- Modern Web Guidance は、Baseline に基づく最新のガイドをエージェントが必要なときに検索・参照できるようにする Agent Skills。2026年11月に 1.0 になった。
- `npx modern-web-guidance@latest install` で導入でき、Claude Code・Codex・Copilot などに対応している。
- Baseline ターゲットを `CLAUDE.md` や `AGENTS.md` に書いておくと、プロジェクトのブラウザ要件に合わせた提案になる。
- ガイダンスは出発点を良くするもので、コードレビューや実ブラウザでのテストは引き続き必要。

AI にフロントエンドを書かせているなら、まず手元のプロジェクトに入れて、モーダルやツールチップを作らせて差を比べてみるとよいでしょう。
