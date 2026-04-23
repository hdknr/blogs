---
title: "Open-notebook — NotebookLM をセルフホストできる完全ローカル OSS"
date: 2026-04-22
lastmod: 2026-04-22
draft: false
source_url: "https://github.com/hdknr/blogs/issues/1#issuecomment-4303873480"
description: "NotebookLM の完全ローカル実装 OSS「open-notebook」の機能・導入手順・NotebookLM との比較を解説。Ollama 対応でゼロコスト運用も可能。"
categories: ["AI/LLM"]
tags: ["NotebookLM", "セルフホスト", "Docker", "Ollama", "ローカルLLM"]
---

Google の NotebookLM に触発されたオープンソース実装 **open-notebook** が海外のテック界隈で注目を集めている。データを一切外部に送信しない完全ローカル動作を売りに、Docker で約2分で立ち上げられる手軽さも人気の理由だ。

## open-notebook とは

[open-notebook](https://github.com/lfnovo/open-notebook) は、NotebookLM の主要機能をすべて再実装した OSS プロジェクト。2024年10月に公開され、2026年4月時点で **22,000 スター超** を獲得している。

公式サイト: [open-notebook.ai](https://www.open-notebook.ai)

## 主な機能

### マルチソースの知識統合

PDF・動画・音声・ウェブページを横断で読み込ませ、AI とのチャット形式で対話できる。NotebookLM と同様の使い勝手を、完全ローカル環境で実現する。

### 多数の AI バックエンドに対応

OpenAI・Anthropic（Claude）・Google Gemini・Ollama・Mistral・Groq・xAI・Deepseek など主要なプロバイダーを幅広くサポートしている。

| バックエンド | 備考 |
|---|---|
| Anthropic (Claude) | クラウド |
| OpenAI (GPT) | クラウド |
| Google Gemini | クラウド |
| Ollama | ローカル・完全無料 |
| Mistral / Groq / xAI / Deepseek など | クラウド |

Ollama を選択すれば、外部サービスへの通信がゼロのオフライン環境でも完全無料で運用できる。

### ポッドキャスト風音声の生成

複数の話者でポッドキャスト形式の音声を自動生成できる。NotebookLM が2人固定なのに対し、open-notebook は話者数をカスタマイズ可能な点が差別化ポイント。

### REST API 完備

REST API が標準搭載されているため、企業内アプリへの組み込みや外部サービスとの連携が容易。n8n や LangChain などのワークフローツールからも呼び出せる。

### 日本語 UI 対応

インターフェースが日本語に対応しており、日本のユーザーでもすぐに使い始められる。

## クイックスタート（Docker）

```bash
git clone https://github.com/lfnovo/open-notebook
cd open-notebook
docker compose up -d
```

Docker さえあれば約2分でローカル環境が立ち上がる。

## NotebookLM との比較

| 機能 | NotebookLM | open-notebook |
|---|---|---|
| データのプライバシー | Google サーバー | 完全ローカル |
| AI バックエンド | Google のみ | 多数（Ollama 含む） |
| 音声生成の話者数 | 2人固定 | カスタマイズ可能 |
| REST API | なし | あり |
| 料金 | 無料（制限あり） | Ollama 利用なら完全無料 |
| セルフホスト | 不可 | 可 |

## まとめ

open-notebook は「NotebookLM の機能をそのままに、データを手元に置きたい」というニーズに応えるプロジェクト。特に医療・法律・金融など機密情報を扱う業種や、企業内ドキュメントを外部 AI に送りたくない場面で有力な選択肢になりそうだ。Ollama 対応によるゼロコスト運用も魅力で、個人開発者から企業まで幅広いユーザー層に対応した設計と言える。
