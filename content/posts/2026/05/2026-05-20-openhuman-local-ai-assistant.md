---
title: "OpenHuman — 完全ローカルで動くパーソナルAIアシスタント：プライバシー最優先でChatGPT級の体験を自分のPCで"
date: 2026-05-20
lastmod: 2026-05-20
slug: "openhuman-local-ai-assistant"
draft: false
source_url: "https://github.com/hdknr/blogs/issues/1#issuecomment-4494575313"
description: "OpenHumanはRust製オープンソースのローカルAIアシスタント。Memory Tree・Ollama連携・118サービスAuto-fetchでChatGPT級の体験を完全ローカルで実現する。"
categories: ["AI/LLM"]
tags: ["OpenHuman", "ローカルAI", "ollama", "AIエージェント", "プライバシー"]
---

「クラウドAIに自分の悩みを打ち明けるのが不安」という声をよく聞く。仕事の機密、家族の話、健康上の悩み——ChatGPTに投げてはみるものの、その会話がサーバーに残り続けることへの抵抗感は根強い。

そこに登場したのが **OpenHuman** だ。GitHubスター数2.7万を超え、週に1,000以上のペースで増え続けるこのプロジェクトは、「ChatGPT級のAIを完全にローカルで動かす」という問いへの実践的な回答を提供している。

## OpenHumanとは

[OpenHuman](https://github.com/tinyhumansai/openhuman) は、TinyHumans AIが開発するオープンソースのエージェント型AIアシスタントだ。Rustをコアに持ち、デスクトップアプリとして動作する。

公式の説明は簡潔にまとめられている。

> **Your Personal AI super intelligence. Private, Simple and extremely powerful.**

ポイントは3点だ。

- Memory Tree による長期記憶
- Obsidianスタイルのローカルナレッジベース
- 118以上のサービス連携

これらを組み合わせることで、「インストールから数分でユーザーを知り尽くしたエージェント」を目指している。

## なぜ「ローカルAI」が重要なのか

ChatGPTをはじめとするクラウドAIの課題は、会話が外部サーバーへ送信される点にある。個人情報保護の観点から問題となるだけでなく、企業での利用では情報漏洩リスクが伴う。

OpenHumanが解決しようとしているのはこの点だ。

- **会話が外に出ない** — ローカルLLM（Ollama経由）を選べば推論まで完結する
- **自分のPCだけで動く** — プライバシー最優先の設計思想
- **日本語README完備** — 日本語ユーザーへの配慮も行き届いている
- **Rust製で爆速** — コアがRustで書かれており、動作が軽快

もちろん、デフォルト構成ではモデルルーティングやOAuth連携の一部にOpenHuman側のマネージドバックエンドを使う。完全オフラインにしたい場合はローカルモデルとComposio直接モードを組み合わせる設定が必要だ。

## 主な機能

### Memory Tree + Obsidian Vault

OpenHumanの中核機能は **Memory Tree** だ。接続した各種サービスから取得したデータを3,000トークン以内のMarkdownチャンクに圧縮し、SQLiteに階層的に保存する。同時に、Obsidianと互換性のある `.md` ファイルとしてローカルVaultへ書き出す。

Karpathy氏の [Obsidian Wikiワークフロー](https://x.com/karpathy/status/2039805659525644595) にインスパイアされており、AIが「あなたの文脈」をリアルタイムで持ち続けるための仕組みとなっている。Obsidianを使っているユーザーはそのままナレッジベースとして参照・編集できる。

### 118以上のサービス連携（Auto-fetch）

Gmail、Notion、GitHub、Slack、Stripe、Google Calendar、Google Drive、Linear、Jiraなど118以上のサービスにOAuth一発で接続できる。

**Auto-fetch** 機能が特徴的で、20分ごとに各連携サービスから新しいデータを自動取得してMemory Treeへ流し込む。ポーリングループを自分で書く必要はない。翌朝起動した時点で、昨晩のメールや今日のカレンダーがすでにエージェントのコンテキストに入っている。

### TokenJuice — トークン圧縮層

LLMにデータを渡す前に必ずTokenJuiceというトークン圧縮層を通す。HTMLをMarkdownへ変換し、長いURLを短縮し、冗長なツール出力を要約する。CJK（日本語・中国語・韓国語）や絵文字はグラフェム単位で保持されるため、日本語テキストが文字化けすることはない。

公式によれば、**コストと遅延を最大80%削減**できるとしている。

### デスクトップマスコット・ネイティブボイス

OpenHumanにはAIに「顔」がある。デスクトップ上に常駐するマスコットが発話・表情変化・リップシンクを行い、Google Meetへ実際の参加者として参加させることもできる。ネイティブボイス機能はデフォルトでElevenLabs TTSを使うが、v0.54.0以降はWhisper + Piper による完全ローカルの STT（音声認識）/ TTS（音声合成）も選択可能だ。

### モデルルーティング

OpenHumanの単一プランの中で、タスクに応じて推論・高速・ビジョンなど複数のLLMを自動選択する。Ollamaを使ったローカルAIも選択肢のひとつとして統合されている。

#### 「ローカルLLM」の中身

OpenHuman自身はモデルweightsを同梱せず、**OllamaまたはLM Studioにpullを委譲する**設計だ。公式ドキュメント（[Local AI](https://tinyhumans.gitbook.io/openhuman/features/model-routing/local-ai)）でデフォルト/推奨として挙げられているモデルは次のとおり。

| 用途 | デフォルト/推奨モデル | サイズ |
|------|---------------------|--------|
| Memory embeddings（記憶の埋め込み） | `all-minilm:latest` | 約23 MB |
| Summary-tree 構築（Memory Tree要約） | `gemma3:1b-it-qat` | 約700 MB |
| Chat / Reasoning | ユーザー設定（既定なし） | — |

チャット推論用のモデルは固定されておらず、ドキュメントの設定例では `ollama:llama3.1:8b` や `ollama:qwen2.5:14b` といった指定が示されている。つまり「ローカルLLM」の正体は、埋め込みに all-MiniLM、Memory Tree の階層要約に Google の Gemma 3 1B 量子化版が使われ、チャットは Llama 3.1 8B や Qwen2.5 14B などユーザーが pull した小〜中型モデルに委ねる構成だ。

「ChatGPT級のローカル体験」と謳われるが、実態は**フロンティアモデル級の推論性能を1台のPCで再現するのではなく、Memory Tree・Auto-fetch・TokenJuiceでコンテキストを最大化し、小型モデルでも実用ラインに引き上げる**というアプローチに近い。

## 他のAIアシスタントとの比較

以下は、公式READMEが競合として挙げているClaude Cowork（AnthropicのデスクトップAIエージェント製品。コーディングアシスタントのClaude Codeとは別製品）との比較だ。

| 項目 | Claude Cowork | OpenHuman |
|------|---------------|-----------|
| オープンソース | プロプライエタリ | GNU |
| 導入の手軽さ | デスクトップ + CLI | クリーンなUI、数分で完了 |
| メモリ | チャットスコープ | Memory Tree + Obsidianボールト |
| 連携数 | 少数 | 118以上（OAuth） |
| Auto-fetch | なし | 20分ごとのメモリ同期 |
| モデルルーティング | 単一モデル | 組み込み済み |

> 出典: OpenHuman公式READMEの比較表（Claude CoworkはAnthropicのデスクトップエージェント製品。Claude Codeとは別製品）

## インストール方法

macOS / Linux の場合はターミナルから1行で導入できる。

```bash
curl -fsSL https://raw.githubusercontent.com/tinyhumansai/openhuman/main/scripts/install.sh | bash
```

Windows の場合は PowerShell から次のコマンドを実行する。

```powershell
irm https://raw.githubusercontent.com/tinyhumansai/openhuman/main/scripts/install.ps1 | iex
```

または [tinyhumans.ai/openhuman](https://tinyhumans.ai/openhuman) からDMG・EXEをダウンロードすることもできる。

> **注意**: 現在アーリーベータ段階のため、荒削りな部分が残っている。LinuxのWayland環境でのAppImageクラッシュ問題（[#2463](https://github.com/tinyhumansai/openhuman/issues/2463)）はすでにクローズ済みだが、READMEには環境変数によるワークアラウンドへの参照が残っている。Arch Linux向けには `openhuman-bin` AURパッケージも用意されている。

### ビルドに必要なもの（ソースから開発する場合）

- Git、Node.js 24以上、pnpm 10.10.0
- Rust 1.93.0（`rustfmt` + `clippy`）
- CMake、Ninja、ripgrep、プラットフォームごとのデスクトップビルド前提条件

```bash
# サブモジュール初期化が必要
git submodule update --init --recursive
pnpm install

# UI開発のみ
pnpm dev

# デスクトップアプリ込み
pnpm --filter openhuman-app dev:app
```

## まとめ

OpenHumanは「クラウドAIに頼らずに、自分専用のAIアシスタントを持ちたい」というニーズに対する現時点での最も完成度の高い回答のひとつだ。

Memory Tree・Auto-fetch・TokenJuiceという3つの機能が組み合わさることで、「インストールしたその日からコンテキストを持ったAI」が実現する。アーリーベータの荒削りさはあるものの、週1,000スター超のペースは本物の需要を反映している。

プライバシーを重視するユーザーや、企業の機密情報をクラウドへ出したくないチームにとって、OpenHumanは試す価値のある選択肢だ。
