---
title: "Claude Code に Auto Mode が登場 — 許可プロンプトなしで長時間タスクを実行"
date: 2026-03-12
lastmod: 2026-03-12
draft: false
source_url: "https://github.com/hdknr/blogs/issues/1#issuecomment-4050723505"
categories: ["AI/LLM"]
tags: ["claude-code", "claude", "anthropic", "agent"]
---

Anthropic が Claude Code にリサーチプレビューとして「Auto Mode」を導入しました。`claude --permission-mode auto` で起動すると、ツール使用の許可判断を Claude 自身が行い、開発者の手動承認なしで長時間の連続作業が可能になります。

## Auto Mode とは

従来の Claude Code では、ファイルの書き込みやシェルコマンドの実行のたびに許可プロンプトが表示されていました。これは安全性の面では重要ですが、長時間のタスクでは開発フローが頻繁に中断される原因になっていました。

Auto Mode はこの問題に対処するもので、各操作について Claude 自身がリスクを判断し、安全と判断した操作は自動で承認します。

## 使い方

起動時にフラグを指定します:

```bash
claude --permission-mode auto
```

または、セッション中に `Shift+Tab` で許可モードを切り替えることもできます。

## 既存の許可モードとの比較

Claude Code には複数の許可モードがあります:

| モード | 動作 |
|--------|------|
| **Normal** | 操作ごとに許可を求める（デフォルト） |
| **Auto-accept edit** | ファイル編集は自動承認、シェルコマンドは確認 |
| **Auto Mode** | Claude がリスク判断して自動承認（新機能） |
| **Plan** | 読み取り専用、変更は一切行わない |

Auto Mode は `--dangerously-skip-permissions` のような全許可フラグとは異なり、Claude がリスク分類を行った上で判断するため、安全性と利便性のバランスを取ったアプローチです。

## セキュリティ上の注意点

Auto Mode は万能ではありません。Anthropic は以下の点を注意喚起しています:

- **隔離環境での使用を推奨**: 本番環境の認証情報やライブ API へのアクセスがあるマシンでは使わない
- **プロンプトインジェクション対策**: ファイルやコマンド出力内の悪意ある指示から保護する機能を搭載
- **トークン使用量の増加**: リスク判断のオーバーヘッドにより、若干のコスト・レイテンシ増加がある

## 組織での管理

IT 管理者は Auto Mode を制限することもできます:

- **MDM/OS レベル**: `disableAutoMode` ポリシーを設定
- **設定ファイル**: `managed-settings.json` で制御（macOS / Windows / Linux 対応）

## まとめ

Auto Mode は、開発者が `--dangerously-skip-permissions` などの危険な回避策に頼らず、安全に長時間タスクを実行するための選択肢を提供します。リサーチプレビューの段階ですが、Claude Code をヘビーに使っている開発者にとっては生産性向上が期待できる機能です。
