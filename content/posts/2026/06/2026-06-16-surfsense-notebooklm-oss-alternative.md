---
title: "SurfSense — NotebookLMのオープンソース代替ツール"
date: 2026-06-16
lastmod: 2026-06-16
slug: "surfsense-notebooklm-oss-alternative"
draft: false
description: "SurfSenseはNotebookLMの制約（ソース数・LLM選択・セルフホスト不可）を解消するOSSプラットフォーム。Docker1コマンドで導入でき、100以上のLLM・27以上の外部コネクタ・チームRAG機能を提供する。"
source_url: "https://github.com/hdknr/blogs/issues/1#issuecomment-4714984317"
categories: ["AI/LLM"]
tags: ["SurfSense", "notebooklm", "RAG", "セルフホスト", "docker"]
---

Google NotebookLMは使い勝手の良いAIプラットフォームですが、使い込むほどにいくつかの制約が目立ってきます。そこで注目されているのが **SurfSense** です。「NotebookLMのオープンソース版が来た」としてGitHubやHacker Newsなどで話題となり、2026年6月時点でGitHubのスター数は15,000以上に達しています。

## SurfSenseとは

[SurfSense](https://github.com/MODSetter/SurfSense) は、プライバシーを重視したオープンソースのNotebookLM代替ツールです。チーム利用を念頭に設計されており、データ制限なしで利用できます。

- **GitHub**: https://github.com/MODSetter/SurfSense
- **公式サイト**: https://www.surfsense.com
- **スター数**: 15,000+

## NotebookLMの何が不満か

SurfSenseが解決しようとするNotebookLMの課題は次のとおりです。

| 制約 | NotebookLM | SurfSense |
|------|-----------|-----------|
| ノートブックあたりのソース数 | 最大600（有料プラン） | 無制限 |
| ノートブック数 | 最大500 | 無制限 |
| ソースサイズ制限 | 50万語・200MBまで | 制限なし |
| 利用可能LLM | Google Geminiのみ | 100以上 |
| セルフホスト | 不可 | 可（Dockerワンライナー） |
| オープンソース | No | Yes |
| 外部データソース | Google Drive・YouTube・Webサイト | 27以上のコネクタ |

## 主な機能

### データ制限なし

ソース数・ノートブック数の制限がなく、ソースサイズの上限もありません。大量のドキュメントを管理するチームでも快適に利用できます。

### 任意のLLMを選択可能

OpenAI互換のAPI仕様とLiteLLMを通じて100以上のLLMに対応しています。vLLMやOllamaによるローカルLLMも利用できます。データを外部に出したくないオンプレミス環境にも対応できます。

### 27以上の外部コネクタ

次のような多様なサービスとの連携をサポートしています。

- Google Drive / OneDrive / Dropbox
- Notion / Confluence / BookStack
- Slack / Microsoft Teams / Discord
- GitHub / Linear / Jira / ClickUp
- Gmail / Google Calendar
- SearXNG / Tavily などの検索エンジン

### 引用付きAI検索

セマンティック検索とフルテキスト検索を組み合わせたハイブリッド検索で、回答には引用が付きます。Perplexityスタイルの出典表示により、情報の信頼性を確認しやすくなっています。

### AIエージェントとオートメーション

LangChain Deep Agentsをベースにした高度なエージェント機能を備えています。

- **スケジュール実行**: 毎朝のブリーフィング、週次ダイジェストなどを自動化
- **イベントトリガー**: フォルダにドキュメントが追加されたタイミングでエージェントを起動
- **書き戻し**: 処理結果をNotion・Slack・Linear・Google Driveに自動投稿

### チームコラボレーション

Owner / Admin / Editor / Viewerのロールベースアクセス制御（RBAC）を備え、チームメンバーがリアルタイムで共同チャットやコメントを利用できます。

### デスクトップアプリ

ネイティブデスクトップアプリも提供されており、次の機能を任意のアプリから呼び出せます。

- **General Assist**: グローバルショートカットでSurfSenseを即起動
- **Quick Assist**: テキストを選択してAIに説明・リライトを依頼
- **Screenshot Assist**: 画面の任意領域をキャプチャしてAIに質問
- **Watch Local Folder**: ローカルフォルダを監視し、変更をナレッジベースに自動同期（Obsidianとの連携も可能）

## セルフホスト方法

DockerとDockerComposeに対応しています。Linux / macOSの場合は次のワンライナーで導入できます。

```bash
curl -fsSL https://raw.githubusercontent.com/MODSetter/SurfSense/main/docker/scripts/install.sh | bash
```

Windows の場合:

```powershell
irm https://raw.githubusercontent.com/MODSetter/SurfSense/main/docker/scripts/install.ps1 | iex
```

インストールスクリプトは [Watchtower](https://github.com/nicholas-fedor/watchtower) も同時にセットアップし、毎日の自動アップデートを行います。Watchtowerのセットアップをスキップしたい場合は、インストールスクリプトの末尾に `--no-watchtower` フラグを追加します。

クラウド版は [surfsense.com](https://www.surfsense.com) で無料から利用可能です。

## まとめ

SurfSenseは、NotebookLMの制約を正面から解決することを目的に設計されたOSSプロジェクトです。LLMの選択自由度・セルフホスト・外部コネクタの豊富さが主な差別化ポイントです。まだプロダクションレディではないと開発チーム自身が述べていますが、急速に機能追加が進んでおり、今後の動向が注目されます。
