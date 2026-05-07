---
title: "Amazon Quick デスクトップアプリ登場 — エンタープライズ向け AI アシスタントが Claude Code とも連携"
date: 2026-04-30
lastmod: 2026-04-30
draft: false
description: "AWS が 2026 年 4 月に発表した Amazon Quick デスクトップアプリの概要。エンタープライズ向けセキュリティ、Claude Code との ACP 連携、Microsoft Copilot との競合関係を解説。"
source_url: "https://github.com/hdknr/blogs/issues/1#issuecomment-4349319466"
categories: ["AI/LLM"]
tags: ["Amazon Quick", "AWS", "Claude Code", "エンタープライズ", "デスクトップアプリ"]
---

AWS が 2026 年 4 月 28 日に開催したイベント「What's Next with AWS 2026」で、**Amazon Quick** のデスクトップアプリ（Preview）が発表・リリースされた。エンタープライズ向けのセキュアな AI アシスタントとして、Claude Code を含む開発者ツールとの MCP 連携も備えている。

## Amazon Quick とは

Amazon Quick は AWS が提供するデスクトップ AI アシスタントで、ユーザーの日常業務を横断的に支援することを目的に設計されている。今回のデスクトップアプリリリース以前から Web・モバイル版が存在していたが、OS レベルの統合が加わったことで機能が大幅に拡張された。

対応 OS は **macOS と Windows** の両方。AWS アカウントは不要で、個人メール・Google・Apple・GitHub・Amazon 認証のいずれかでサインアップできる。

## 主な機能

### パーソナル知識グラフによるコンテキスト学習

Amazon Quick はバックグラウンドで常時動作し、ユーザーの作業パターン・人間関係・プロジェクトを学習する「パーソナル知識グラフ」を構築する。会話のたびにゼロから始めるのではなく、蓄積したコンテキストを活用して返答するのが特徴だ。

### 広範なエンタープライズアプリ統合

以下のような主要サービスとシームレスに統合される:

- **コミュニケーション**: Slack、Microsoft Teams、Outlook、Gmail、Zoom
- **プロジェクト管理**: Jira、Asana、Airtable
- **CRM / ERP**: Salesforce、ServiceNow
- **ストレージ / 文書**: Google Workspace、Microsoft 365、Dropbox

### ローカルファイルとカレンダーへの直接アクセス

デスクトップアプリの特徴として、ローカルファイルをクラウドにアップロードせず直接読み取れる。カレンダーやメールも連携し、会議の事前準備・フォローアップメールの下書き・優先度管理といったタスクを自動化できる。

### Claude Code および Kiro CLI との連携

開発者向けの大きな特徴として、**Claude Code** や Kiro CLI（AWS のローカル AI コーディングエージェント）などの開発者ツールへのローカル接続をサポートしている。接続には **ACP（Agent Client Protocol）** を使用する「Coding agents」機能として実装されており、ブラウザベースのワークフロー自動化やローカルスクリプト実行と組み合わせた複合タスクを一括リクエストで実行できる。なお、MCP サーバーとの接続も別途サポートされており、Claude Code の MCP 設定ファイルをインポートして利用する経路もある。

## エンタープライズ向けセキュリティ

Amazon Quick は AWS の既存インフラ（IAM、暗号化、コンプライアンス認証）をそのまま活用する。「**ユーザーデータは他社モデルの学習には一切使用されない**」という方針が明示されており、セキュリティ部門が既に AWS を承認済みの企業であれば追加審査なしに導入できる点が強調されている。

すでに 3M・AstraZeneca・BMW・Mondelēz・NFL などのグローバル大企業が採用している。

## Microsoft Copilot との位置付け

The Register は Amazon Quick を「**Copilot for all your apps**」と表現しており、Microsoft 365 に特化した Microsoft Copilot の直接競合と位置付けている。今回のデスクトップアプリリリースのタイミングについて、X（旧 Twitter）上では「Microsoft の独占クラウド契約が切れた瞬間に一気に複数サービスをリリースしてきた（複数の投稿より）」という指摘も見られた。

同じイベントでは AWS と OpenAI のパートナーシップ拡大も同時発表されており、AI インフラをめぐる各クラウドベンダーの競争が一段と激化している。

## 料金プラン

Amazon Quick は **Free** ティアと **Plus** ティアが用意されている（詳細は公式サイト参照）。デスクトップアプリは現在 Preview として米国東部（バージニア北部）リージョンの全サブスクライバーに提供中。

## まとめ

Amazon Quick デスクトップアプリは、エンタープライズのセキュリティ要件を満たしながら Claude Code との MCP 連携も備えた AI アシスタントだ。AWS の幅広いコンプライアンス認証を引き継ぐ形でのデプロイが可能なため、セキュリティを重視する組織にとって導入ハードルは低い。Claude Code ユーザーにとっても、Quick から直接コーディングエージェントを呼び出せる点は注目に値する。

- 公式サイト: [Amazon Quick](https://aws.amazon.com/quick/)
- デスクトップアプリダウンロード: [Download Amazon Quick](https://aws.amazon.com/quick/download/)
- AWS ブログ: [Top announcements of the What's Next with AWS, 2026](https://aws.amazon.com/blogs/aws/top-announcements-of-the-whats-next-with-aws-2026/)
