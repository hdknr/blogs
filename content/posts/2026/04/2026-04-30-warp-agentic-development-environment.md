---
title: "Warp がオープンソース化 — ターミナルから生まれた Agentic Development Environment（ADE）の全貌"
date: 2026-04-30
lastmod: 2026-04-30
draft: false
description: "AI ターミナル Warp が 2026-04-28 に Rust 製クライアントを AGPL v3 / MIT のデュアルライセンスでオープンソース化。OpenAI 設立スポンサー、Claude Code・Codex・Gemini CLI 連携、クラウドエージェント基盤 Oz まで含めた ADE の全貌を解説。"
source_url: "https://github.com/hdknr/blogs/issues/1#issuecomment-4349378460"
categories: ["AI/LLM"]
tags: ["warp", "agent", "claude-code", "openai", "rust", "terminal", "agpl"]
---

AI ターミナルとして知られる **Warp** が 2026 年 4 月 28 日にクライアントコードのオープンソース化を発表しました。発表からわずか 1 日あまりで GitHub Star が 34,000 を突破し、本記事執筆時点（2026-04-30）では **45,000 Star 超**という勢いで成長しています。

Warp は単なるターミナルから、開発者と AI エージェントが協働する **Agentic Development Environment（ADE）** へと進化しています。本記事ではオープンソース化の概要、ライセンス構成、内蔵エージェントと外部 CLI エージェント連携、そして OpenAI が「設立スポンサー」として参加した意味を整理します。

## TL;DR

- Warp クライアント（Rust 製）が [warpdotdev/warp](https://github.com/warpdotdev/warp) でオープンソース化
- ライセンスは **デュアル**: UI フレームワーク（`warpui_core` / `warpui` クレート）が **MIT**、それ以外が **AGPL v3**
- **OpenAI が設立スポンサー**。新しい Agent 駆動の管理ワークフローは GPT モデルで動作
- 内蔵コーディングエージェントに加え、**Claude Code / Codex / Gemini CLI** などの外部 CLI エージェントを呼び出せる
- クラウドエージェント基盤 **Oz** が Issue トリアージから Spec 作成・実装・PR レビューまでを担う

## Warp とは何か — Agentic Development Environment（ADE）

Warp は当初、macOS 向けに登場した Rust 製の高速・モダンなターミナルです。現在は Linux にも対応しており、リッチな UI、ブロックベースの履歴、AI コマンド補完を特徴としています。

ここ数年の Agent 化トレンドを背景に、Warp は単なるターミナルから「開発者と AI エージェントが共同でソフトウェアを作る場」へと位置づけを変えました。これが **Agentic Development Environment（ADE）** です。Warp 公式は ADE を「IDE の次に来る形態」として打ち出しており、「**通常 10 分かかるタスクが数秒で完了する**」という現場の声を紹介しています。

## オープンソース化の概要

公式リポジトリ [warpdotdev/warp](https://github.com/warpdotdev/warp) の README には次のように書かれています。

> OpenAI is the founding sponsor of the new, open-source Warp repository, and the new agentic management workflows are powered by GPT models.

ポイントを整理するとこうなります。

| 項目 | 内容 |
|------|------|
| 公開日 | 2026 年 4 月 28 日 |
| 開発元 | Warp（CEO: Zach Lloyd） |
| 言語 | Rust |
| 設立スポンサー | OpenAI |
| 管理ワークフロー駆動モデル | GPT モデル |
| Star 数（本記事執筆時点） | 45,000+ |

商用 SaaS ではなく **クライアントコード本体** を公開した点が特徴で、Tokio・NuShell・Alacritty・Fig Completion Specs などの OSS 依存先も README に明示されています。

## デュアルライセンス: MIT と AGPL v3

Warp は単一ライセンスではなく、コンポーネントごとにライセンスを使い分けるデュアル方式を採用しています。

- **MIT**: `warpui_core` および `warpui` クレート（UI フレームワーク部分）
- **AGPL v3**: その他すべてのコード

UI 部分を MIT にしているのは、他のアプリケーションが Warp の UI コンポーネントを取り込みやすくするためと推測できます。一方、本体に AGPL v3 を選んだ意図は明確です。「**ネットワーク経由でサービスとして提供される派生物にもソースコード開示義務が及ぶ**」という強力なコピーレフトにより、競合が Warp をフォークして SaaS で囲い込むことを防ぐ狙いがあります。

AGPL v3 は GPL v3 をベースに「サービス提供（SaaS）でも改変ソースの公開義務を負う」という条項（13 条）を加えた厳格なコピーレフトライセンスです。商用利用そのものは禁止されていませんが、**派生物の公開義務がネットワーク越しのユーザーにも適用される**点で MIT/Apache のような寛容ライセンスとは大きく異なります。

## 内蔵エージェント + 外部 CLI エージェント

README によれば Warp は「内蔵コーディングエージェント」と「外部 CLI エージェント」の **両方** をファーストクラスでサポートします。

> Use Warp's built-in coding agent, or bring your own CLI agent (Claude Code, Codex, Gemini CLI, and others).

OpenAI のスポンサーシップは GPT モデル駆動の管理ワークフローに紐付いていますが、開発者個人が日々のコーディングで使うエージェントは自由に選べる設計です。

- **内蔵エージェント**: 起動直後から利用可能。Warp 内部で完結
- **Claude Code**（Anthropic）: 外部 CLI エージェント
- **Codex**（OpenAI）: 外部 CLI エージェント
- **Gemini CLI**（Google）: 外部 CLI エージェント
- その他 CLI Agent も対応

ターミナルがエージェント実行の「ホスト」になることで、複数の AI ベンダーを横断して使うワークフローがそのまま Warp 上に乗ります。**「どのモデルを使うか」が日々変わる時代における共通レイヤー** を狙った設計と読めます。

## Oz — クラウドエージェントオーケストレーション

Warp のもうひとつの中核が **Oz** と呼ばれるクラウドエージェントオーケストレーションプラットフォームです。GitHub の OSS 開発フローを Oz が自動化します。

[build.warp.dev](https://build.warp.dev) では以下を確認できます。

- 数千の Oz エージェントが Issue をトリアージし、Spec 作成・実装・PR レビューを進める様子を観察できる
- トップコントリビューターやリリース直前の機能を閲覧できる
- GitHub サインインで自分の Issue を追跡できる
- アクティブなエージェントセッションを、ブラウザ上で動作する WebAssembly 版 Warp ターミナルから直接クリックして覗ける

Issue ラベルは `ready-to-spec`（仕様検討の段階）と `ready-to-implement`（実装受付中）の 2 段階で進行し、コミュニティ貢献者がいつ介入すべきかを明示しています。**人間とエージェントが同じ Issue を共有しながら開発する** 設計です。いわゆる「OSS リポジトリで AI エージェントを大量に走らせる」未来形を現実のフローに落とし込んだ事例といえます。

## ローカルでビルドして動かす

オープンソース化により、自分のマシンで Warp をビルド・実行できるようになりました。リポジトリ直下のスクリプトで完結します。

```bash
git clone https://github.com/warpdotdev/warp.git
cd warp

./script/bootstrap   # プラットフォーム依存セットアップ
./script/run         # ビルドして Warp を起動
./script/presubmit   # fmt / clippy / tests
```

詳細なエンジニアリングガイドは `WARP.md` に集約されており、コーディングスタイル、テスト、プラットフォーム依存の注意点などが整理されています。

なお、すぐに使いたいだけなら従来通り [Warp 公式サイトのダウンロードページ](https://www.warp.dev/download) からインストーラーで導入できます。

## どう貢献するか — Issue to PR フロー

README が示す貢献フローはシンプルです。

1. **既存 Issue 検索**: `is:issue is:open sort:reactions-+1-desc` で既知の要望を確認
2. **Issue 作成**: テンプレートに沿って起票（セキュリティ脆弱性は CONTRIBUTING.md の私的報告チャネル経由）
3. **メンテナによるレビュー** → 準備完了ラベル付与
   - `ready-to-spec`: コミュニティが仕様策定可能
   - `ready-to-implement`: 仕様が固まり PR 受付中
4. **PR 提出**

ラベル付与のリクエストや問題エスカレーションは、Issue 上で `@oss-maintainers` をメンションして行います。「**仕様策定からコードまでコミュニティが関与できる**」設計で、PR を投げる前に Spec レビューで方向性を合わせられるのが特徴です。

## OpenAI 設立スポンサーが意味すること

OpenAI が「設立スポンサー」として関与し、管理ワークフローが GPT モデル駆動だという点は注目に値します。

- Warp は内蔵エージェントの選択肢として OpenAI 製モデルだけに縛らない（Claude Code / Gemini CLI も併記）
- 一方で、Oz が走らせるクラウドエージェントは GPT モデルで動く

つまり **「個別開発者の手元では好きなエージェント、共有 OSS 運営では GPT」** というすみ分けです。これは「クラウド側のオーケストレーションコストを GPT で賄う」というスポンサーシップの構造として理解できます。Anthropic の Claude Code を使う開発者にとっても、Warp 経由でターミナル UX を共有しつつ Oz の OSS 運営に貢献できる、という二重の入口が用意されているわけです。

## 開発者にとっての示唆

Warp のオープンソース化は単なる「OSS 化トピック」を超えて、**ターミナルがエージェント実行のハブになる** 流れを象徴しています。

- 複数 AI ベンダーを横断してコーディングする時代における **ホスト UX** が標準化される可能性
- AGPL v3 によるエコシステム保護は、似た領域（Cursor / Zed / Continue など）の競合戦略と一線を画す
- Oz のような「クラウド側でエージェントが OSS を運営する」モデルは、他の OSS プロジェクトにも波及する可能性

Claude Code をはじめとする CLI エージェントを既に使っている開発者にとって、Warp は「自分のエージェントをそのまま使える、より生産的なターミナル」という導入動機になります。クライアント側の利用であれば AGPL v3 の条項を過度に気にする必要はありません。**今すぐ手元にクローンして試せる**——これが今回のオープンソース化最大の価値といえるでしょう。

## 関連リンク

- GitHub: [warpdotdev/warp](https://github.com/warpdotdev/warp)
- 公式サイト: [warp.dev](https://www.warp.dev)
- ドキュメント: [docs.warp.dev](https://docs.warp.dev)
- ダッシュボード: [build.warp.dev](https://build.warp.dev)
- ダウンロード: [warp.dev/download](https://www.warp.dev/download)
