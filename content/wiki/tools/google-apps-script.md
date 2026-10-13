---
title: "Google Apps Script（GAS）"
description: "Google Workspace に含まれるスクリプト実行環境。Web アプリとしてドメイン限定で公開でき、AI で社員が作った社内ツールの追加コストゼロの置き場所になる"
date: 2026-10-13
lastmod: 2026-10-13
aliases: ["GAS", "Apps Script", "GAS Web アプリ", "clasp", "社内限定アプリ基盤"]
related_posts:
  - "/posts/2026/10/gas-internal-app-platform/"
tags: ["GAS", "Google Workspace", "claude-code", "Agent Skills", "MDM"]
---

## 概要

Google Apps Script（GAS）は Google Workspace に含まれるスクリプト実行環境で、**Web アプリとしてデプロイすると自社ドメインのアカウントだけが開ける社内ツール**を作れる。kubell（旧 Chatwork）は、Claude Code などで社員が作った社内アプリの公開先を GAS の Web アプリに統一し、その「安全な道」を社内スキルで舗装した。

コーディングエージェントが全社に行き渡ると、非エンジニアも業務ツールを作り始め、次の論点は「**作ったツールをどこに置くか**」になる。GAS は既存の Workspace 契約の範囲で、その答えを追加費用なしに用意できる。

## 詳細

### なぜ Vercel / Netlify ではなく GAS か

Vercel や Netlify は自然に選ばれがちだが、社内ツールの置き場所としては「URL が分かれば社外から開ける」「Basic 認証や IP 制限は設定漏れしやすい」「個人アカウントだと退職でツールが消える」「情シスが把握しない社外データストアに業務データが置かれる」という懸念がある。AWS に自前の基盤を作る案は、認証・ホスティング・DB・監視の運用コストと、業務データの多くがある Google API を別クラウドから呼ぶ認証情報の管理が重い。

| 観点 | GAS Web アプリでの扱い |
|---|---|
| 公開範囲 | 自社ドメインのアカウントだけに限定 |
| 利用者の識別 | 開いた人のアカウントをサーバ側で取得 |
| データの置き場所 | 自社 Workspace のスプレッドシート |
| 費用 | 追加費用なし、個人のクレジットカードも不要 |
| 引き継ぎ | オーナー譲渡や共有ドライブで会社の管理下に残せる |

### Web アプリの基本構成

- **`doGet()`** — `HtmlService.createHtmlOutputFromFile('Index')` で HTML を返す。URL は `https://script.google.com/a/macros/<ドメイン>/s/<デプロイID>/exec` 形式
- **`google.script.run`** — ブラウザからサーバ関数を非同期に呼ぶ。API サーバ、CORS、認証トークン管理が不要。サーバ側は `Session.getActiveUser().getEmail()` で利用者を特定し、シートは `getDataRange().getValues()` でまとめて 1 回で読む
- **`appsscript.json` の `webapp`** — `access: "DOMAIN"` で同じドメインのみ、`executeAs` は `USER_ACCESSING`（開いた人の権限。利用者にシートの編集権限が要り、直接開けば他人の行も編集できる）か `USER_DEPLOYING`（デプロイした人の権限）をデータの共有範囲で選ぶ。`getActiveUser()` は設定やポリシーで空文字を返すことがあるので最初に確かめる
- **単一 HTML にビルド** — GAS は HTML をファイル単位で配信するので、Vite + React + TypeScript を vite-plugin-singlefile で 1 つの `Index.html` にまとめ、画像も data URI にする
- **clasp でデプロイ** — デプロイ ID を固定したまま更新すれば URL を変えずに差し替えられる。サブコマンド名はバージョンで違うので `clasp --help` で確認。開発中は `vite dev` と `google.script.run` のモック

### 社内スキルで「安全な道」を舗装する

本質は技術選定より、**社員がその道を自然に選ぶ仕組み**にある。全社配布のスキル集「kube-mas」で、onboarding（用途とデータの共有範囲を 2〜3 問ヒアリング。Vercel 希望時の案内も担う）・scaffold（雛形）・deploy（社内公開）を分け、利用者は自然言語で頼むだけでよい。

1. **事故が起きやすい箇所を確認させる** — clasp でプロジェクトを作ると `appsscript.json` が既定値に上書きされ公開範囲が消えるので書き戻し、タイムゾーンが `America/New_York` のままなら失敗と判定する。個人 Gmail でのデプロイを防ぐためドメインを確認する
2. **体感速度を最初から確保する** — GAS は 1 回数百ミリ秒〜1 秒かかる。楽観的更新・再訪時のキャッシュ表示・同期中の表示を雛形に組み込み、「GAS は遅いと先回りして言わない」とスキルに書く。**体感速度もガバナンスを保つための要件**
3. **既知の罠リストを育てる** — 例: HTML は iframe 内に表示されるので URL のハッシュが届かず、共有 URL を開くと真っ白になる。症状・原因・対処を追記し続け、同じ問題で 2 人目が詰まらない

### スキルと設定を全社に配る

- Claude Code は管理者が OS の決まった場所（macOS は `/Library/Application Support/ClaudeCode/`）に置いた設定・スキルを全ユーザーに読み込ませられる
- 設定一式は GitHub で管理し、main へのマージで GitHub Actions が macOS pkg と Windows パッケージを生成、Jamf / Intune（MDM）で全端末に配布。claude.ai デスクトップアプリにはプラグインとして組織単位で配布
- 全社共通の `CLAUDE.md` に、外部 AI サービスの組み込みや外部クラウドへのデプロイをしようとしたらガイドラインの該当箇所を示して確認を促すよう書く（原文は Confluence から自動同期）。**ツールを作る瞬間に AI がガイドラインを持ってくる**

### 制約と向き不向き

- 1 回の実行は最大 6 分、API 呼び出しに 1 日のクォータ。重いバッチや大量アクセスには向かない
- `access: "DOMAIN"` は同じテナントのユーザーしか開けない。関連会社など別テナントには中継の仕組みが要る
- iframe の制約（URL ハッシュが届かない、自動リダイレクト不可）
- スプレッドシートは本格的な DB の代わりにならない。同時書き込みは `LockService.getScriptLock()` で直列化する

社内の小規模ツールなら大半は GAS で足りる。「禁止する」より「正しい置き場所を一番楽にする」アプローチは、AI 時代の社内 IT ガバナンスの参考になる。

## 関連ページ

- [シャドーAI](/blogs/wiki/concepts/shadow-ai/) — 管理外の AI 利用・データ持ち出しのリスク
- [Claude for Google Workspace](/blogs/wiki/tools/claude-for-google-workspace/) — Google ファイルの中で Claude を使う統合
- [Claude Code](/blogs/wiki/tools/claude-code/) — スキルと全社配布の仕組み
- [GA4 / Search Console API の認証設定](/blogs/wiki/guides/google-api-oauth-ga4-search-console/) — Google API の認証

## ソース記事

- [AI で作った社内ツールは GAS に置く：追加コストゼロの「社内限定」アプリ基盤](/blogs/posts/2026/10/gas-internal-app-platform/) — 2026-10-09
