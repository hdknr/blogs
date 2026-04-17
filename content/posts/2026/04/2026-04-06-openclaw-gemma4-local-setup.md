---
title: "OpenClaw + Ollama + Gemma4 でローカル無料AIエージェントを構築する"
date: 2026-04-06
lastmod: 2026-04-06
draft: false
source_url: "https://github.com/hdknr/blogs/issues/1#issuecomment-4194457096"
categories: ["AI/LLM"]
tags: ["OpenClaw", "Ollama", "Gemma4", "ローカルLLM", "AIエージェント"]
---

API課金なしで、ローカル環境にAIエージェントを無制限で運用できるセットアップ方法を紹介します。OpenClaw（エージェントインターフェース）+ Ollama（ローカルモデルサーバー）+ Gemma4（推論エンジン）の組み合わせにより、Telegram・Discord・LINEなどの既存チャンネルともシームレスに連携できます。

## 構成概要

| コンポーネント | 役割 |
|---|---|
| **OpenClaw** | AIエージェントのインターフェース・オーケストレーション |
| **Ollama** | ローカルLLMサーバー（モデルの管理・API提供） |
| **Gemma4** | 推論エンジン（Google製オープンモデル） |

この3つを組み合わせることで、クラウドAPIへの依存なしにフル機能のAIエージェントが動作します。

## セットアップ手順

### 1. Ollama のインストール

```bash
# macOS / Linux
curl -fsSL https://ollama.ai/install.sh | sh

# Windows
# https://ollama.ai から インストーラーをダウンロード
```

### 2. Gemma4 モデルの取得

```bash
ollama pull gemma4
```

### 3. OpenClaw のインストール

```bash
npm install -g openclaw
```

### 4. オンボーディングウィザードの実行

```bash
openclaw onboard
```

ウィザードに従ってOllama接続設定とチャンネル連携（Telegram・Discord・LINEなど）を行います。

## よくある失敗箇所とトラブルシューティング

### Ollama が起動していない

`openclaw onboard` 実行時に Ollama への接続エラーが出る場合、先に Ollama サーバーを起動してください：

```bash
ollama serve
```

### モデル名の不一致

OpenClaw の設定でモデル名を指定する際、`ollama list` で表示される正確な名前を使用してください：

```bash
ollama list
```

### ポートの競合

Ollama はデフォルトで `11434` ポートを使用します。他のサービスと競合している場合は環境変数で変更できます：

```bash
OLLAMA_HOST=0.0.0.0:11435 ollama serve
```

## チャンネル連携

OpenClaw は以下のチャンネルと連携可能です：

- **Telegram**: Bot Token を設定するだけで即座に動作
- **Discord**: Application ID と Token を設定
- **LINE**: Messaging API のチャンネルアクセストークンを使用

`openclaw onboard` のウィザード内でそれぞれの設定項目が案内されます。

## APIコスト ゼロで無制限運用

クラウドLLMのAPIは高頻度利用でコストが膨らみますが、この構成ではすべてローカルで処理が完結するため：

- API課金が発生しない
- レート制限がない
- データがローカルに留まる（プライバシー保護）

ローカルGPUの性能に応じてレスポンス速度は変わりますが、Gemma4はコンシューマー向けGPUでも十分に動作します。

## まとめ

OpenClaw + Ollama + Gemma4 の組み合わせは、AIエージェントをゼロコストで本番運用したい方に最適な選択肢です。`openclaw onboard` ウィザードで設定が完結するため、技術的なハードルも低く抑えられています。

AIエージェント活用に関心のある方は、OpenClaw Guild（LINEコミュニティ、1,200名以上）も参考になるでしょう。
