---
title: "Claude for Google Workspace"
description: "Google Docs・Sheets・Slides の中で Claude を使う統合（2026-10 公開ベータ）。開いている 1 ファイルを読んで直接編集するサイドバーと、チャットから操作するコネクターの 2 つの入口がある"
date: 2026-10-13
lastmod: 2026-10-13
aliases: ["Claude for Google Workspace", "Claude in Google Docs", "Claude in Google Sheets", "Claude in Google Slides"]
related_posts:
  - "/posts/2026/10/claude-for-google-workspace/"
tags: ["claude", "anthropic", "Google Workspace", "gemini", "Google Sheets"]
---

## 概要

Anthropic が 2026 年 10 月 6 日（米国時間）に公開ベータとして発表した、Google Docs・Sheets・Slides の中で Claude を使える統合。対象は Pro・Max・Team・Enterprise の有料プラン。これまでの「文章をコピーして Claude に貼り、直してもらって戻す」往復をなくし、**Google ファイルそのものを Claude に仕上げさせる**ためのもの。

## 詳細

### 2 つの入口

- **サイドバー（Google ファイルの中から）** — Google Workspace Marketplace でアドオンを入れ、「拡張機能」メニューから起動。1 回のインストールで Docs・Sheets・Slides に対応。開いているファイルを読み、選択した文章・セル範囲・スライドだけを処理させることもできる
- **コネクター（Claude のチャットから）** — チャットに Google ファイルのリンクを貼る、「この内容から Google スライドを作って」と頼むなどで、Claude 側から作成・編集する（ベータ）。複数資料を読みながら新しい企画書を作る作業向き。アクセス範囲は Google 側の共有権限に従い、Team / Enterprise ではオーナーの有効化が必要

モデル選択・Skills・コネクターの設定は両方で共有される。

### アプリごとにできること

| アプリ | できること |
|---|---|
| Docs | 書式を保ったまま書き直し・見出しスタイル変更。提案カードで変更ごとに採用・却下 |
| Sheets | 数式の作成・修正、ピボットテーブル、ネイティブのグラフ、タブ追加。選択範囲を Python に渡してデータの結合・クリーニングし、結果を書き戻す |
| Slides | 既存デッキのレイアウトとテーマで新規作成。要素の重なり・はみ出し・読みにくい文字を点検 |

### 編集の承認と履歴

| モード | 動き |
|---|---|
| Ask before edits（既定） | 変更を提示し、承認後に反映 |
| Accept all edits | 通常の編集は確認なしでまとめて処理 |

Accept all edits でも、リンク追加・外部画像の挿入・Web アドレスの扱い・共有権限の変更は承認を求める。変更は Google のバージョン履歴に残り、通常の編集と同じく元に戻せる。

### サイドバーが見る範囲は限定されている

アドオンが扱うのは**開いている 1 ファイルだけ**で、Google 側に求める権限もその範囲に限られる。Drive の他ファイルや Gmail・Calendar まで扱うには、別途 Claude 側で Google Workspace のコネクターを有効にする。管理者は Google 側でドメイン・グループ・組織部門単位で利用者を、Claude 側でコネクター・Skills・モデルの範囲を管理できる。

### Gemini との使い分け

Gemini は Gmail・Drive・Calendar・Meet・Chat に深く組み込まれ、Google の権限体系の中で情報を横断して扱うのが得意（[Gemini Agent](/blogs/wiki/tools/gemini-agent/) はその方向を突き詰めた機能）。解説記事の評価（公式比較ではない）では次のような分担になる。

- **Gemini 向き** — メール要約・予定調整・Drive 横断検索、Sheets の標準操作をすばやく
- **Claude 向き** — 長文を構造から作り直す、汚れたデータの Python によるクリーニング、自社の Skills・外部コネクターを使った資料作成、スライドのレイアウト崩れの点検

Claude Code や Claude Desktop で Skills やコネクターを整えている人ほど、その設定をそのまま持ち込めるので恩恵が大きい。

### ベータ版の制約

- アドオン単体では、開いているファイル以外の作成・コピーや PDF 書き出しはできない
- 処理中にサイドバーを閉じると止まる。Firefox は非対応。1 回の長い処理は最大 6 分
- Slides で作るグラフは画像として挿入され、元データが変わっても自動更新されない
- Enterprise の統制機能は一部のみ。Compliance API・CMEK・OpenTelemetry は対応、Bedrock・Vertex AI・Azure 経由の推論、ZDR、HIPAA は非対応で、組織独自のデータ保持設定も引き継がれない

## 関連ページ

- [Gemini Agent](/blogs/wiki/tools/gemini-agent/) — Google サービス横断の Gemini 側のエージェント
- [Google Apps Script（GAS）](/blogs/wiki/tools/google-apps-script/) — 同じ Workspace 上に社内ツールを置く基盤
- [MCP (Model Context Protocol)](/blogs/wiki/concepts/mcp/) — コネクターの仕組み
- [Microsoft 365 Copilot](/blogs/wiki/tools/m365-copilot/) — Microsoft 側のオフィス統合 AI
- [Claude Cowork と Record a skill](/blogs/wiki/tools/claude-cowork/) — Claude の Skills を業務で使う別の入口

## ソース記事

- [Claude for Google Workspace 公開ベータ — Docs・Sheets・Slides でできることと Gemini との使い分け](/blogs/posts/2026/10/claude-for-google-workspace/) — 2026-10-09
