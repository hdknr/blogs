---
title: "REA（Reverse Engineer Anything）"
description: "AI エージェントにリバースエンジニアリングの道具を持たせる MCP サーバー兼 CLI。結論ごとに Evidence（根拠）を返す"
date: 2026-10-30
lastmod: 2026-10-30
aliases: ["REA", "Reverse Engineer Anything", "rea-agents"]
related_posts:
  - "/posts/2026/10/rea-reverse-engineer-anything/"
tags: ["リバースエンジニアリング", "mcp", "AIエージェント", "claude-code", "セキュリティ"]
---

## 概要

REA は、AI コーディングエージェントがソースコードのないアプリを検査し、機能の仕組みを根拠付きで説明し、自分のスタックで同等機能を再実装できるようにする MIT ライセンスの MCP サーバー兼 CLI（npm パッケージ `rea-agents`、TypeScript 製）。REA 自身は逆コンパイラを持たず、エージェントと既存の解析エンジン（Hopper / Ghidra / IDA など）の間に立つ仲介役である。2026 年 10 月に GitHub で急速にスターを集めた。

## 詳細

### 仕組み：逆コンパイル → 理解 → 再構築

1. エージェントが MCP 経由で「この機能はどう動いている？」と問い合わせる
2. REA が対象を検査し、関連コードを辿る
3. 結果を **Evidence** として構造化して返す
4. エージェントが説明し、必要なら追加で質問する
5. 自分のスタックで同等機能を実装・テストする

Evidence は SHA-256 ベースの ID、対象ファイルのハッシュ、使ったエンジンとパラメータ、整合性ポリシー（既定 `fail`）を持つ in-toto 風のレコード。根拠が見つからない点は推測で埋めず **unknowns** として返し、「それらしい作り話」を抑える。

### 対象とエンジン

| 対象 | 必要なもの |
|---|---|
| ネイティブバイナリ | Hopper / Ghidra / IDA のいずれか |
| JavaScript / Electron | Node.js のみ（実行せず静的解析） |
| .NET アセンブリ | 不要（静的解析のみ） |
| Android APK | ヘッドレス JADX と JDK |
| Web サイト | Chrome 系ブラウザ |

.NET アプリはクラス名が残りやすく、ソースを失った VB.NET 業務アプリを逆コンパイラなしで読み解き Web 化した国内事例もある。

### 導入

- `npx rea-agents setup` で対話的にエージェント（Claude Code / Codex / Cursor / Gemini CLI など）へ MCP と Agent Skill を登録。**終わったらエージェントを再起動**しないと反映されない
- CLI 単体でも使える（`npx -y rea-agents@latest analyze-javascript-application <絶対パス> --json`。常用するなら `npm install --global rea-agents`）
- `rea doctor --provider ghidra` のようにエンジンを絞って診断する。引数なしだと未導入エンジンで `healthy: false` になる
- `rea capabilities --json` で各機能の副作用（プロセス起動・書き込み・ネットワーク）を確認できる

### 使う前の注意

- **解析対象の EULA**: REA が MIT でも、対象ソフトの規約がリバースエンジニアリングを禁じていることは多い。「理解できる」と「複製してよい」は別
- **商用エンジンのライセンス**は利用者が別途取得する
- **ローカル解析でも結果はモデル提供元に送られる**。顧客のバイナリならデータポリシーを確認する
- **権限を絞る**: 解析セッションではエージェントの書き込み・ネットワーク権限を外す
- **バイナリ側からのプロンプトインジェクション**: 細工した文字列で AI を誤誘導しうる。Evidence を人が確認する
- **バージョン固定**: 更新が速いので業務では `rea-agents@<version>` に固定し、リリースノートを見てから上げる

守る側の示唆として、クライアントアプリ（特に Electron / Android）に API キーや秘密のロジックを埋め込む設計はこれまで以上に危険になる。

## 関連ページ

- [MCP](/blogs/wiki/concepts/mcp/) — REA が提供するインターフェース
- [プロンプトインジェクション](/blogs/wiki/concepts/prompt-injection/) — 解析対象からの誘導リスク
- [AI エージェント時代のシークレット管理](/blogs/wiki/guides/ai-agent-secret-management/) — 秘密情報をエージェントやクライアントに置かない設計
- [Claude Code](/blogs/wiki/tools/claude-code/)

## ソース記事

- [REA とは？AI エージェントにリバースエンジニアリングさせる MCP ツールの使い方と注意点](/blogs/posts/2026/10/rea-reverse-engineer-anything/) — 2026-10-13
