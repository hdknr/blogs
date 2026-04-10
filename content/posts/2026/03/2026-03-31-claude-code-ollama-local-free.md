---
title: "Claude Code を Ollama でローカル無料実行する方法"
date: 2026-03-31
lastmod: 2026-03-31
slug: "claude-code-ollama-local-free"
draft: false
source_url: "https://github.com/hdknr/blogs/issues/1#issuecomment-4165254271"
categories: ["AI/LLM"]
tags: ["claude-code", "ollama", "llm", "anthropic"]
description: "Ollama v0.15 以降で Claude Code をローカル LLM バックエンドで無料実行する方法。ollama launch コマンドによるワンコマンドセットアップから、環境変数による手動設定、ハードウェア要件、実用上の注意点まで解説。"
---

Claude Code がローカル LLM で無料実行できるようになった。Ollama を使えば、API 料金なしで Claude Code のインターフェースを活用できる。

## 背景

Claude Code は Anthropic が提供する CLI ベースの AI コーディングアシスタントだ。通常は Anthropic API を通じて利用するため、API 使用料が発生する。しかし Ollama v0.14.0 以降で Anthropic Messages API 互換のエンドポイントが実装され、ローカル LLM を Claude Code のバックエンドとして使えるようになった。

2026年1月にリリースされた Ollama v0.15 では `ollama launch claude` コマンドが追加され、セットアップがさらに簡単になっている。

## セットアップ手順

### 方法1: `ollama launch`（推奨・v0.15 以降）

Ollama v0.15 で追加された `ollama launch` コマンドを使えば、環境変数の設定なしでワンコマンドで起動できる:

```bash
ollama launch claude
```

モデルを指定する場合:

```bash
ollama launch claude --model qwen3-coder
```

### 方法2: 環境変数を手動設定（v0.14 以降）

#### 1. Ollama のインストール

macOS/Linux の場合は以下のコマンドでインストールできる。macOS では公式サイトのインストーラーも利用可能:

```bash
curl -fsSL https://ollama.com/install.sh | sh
```

#### 2. モデルのダウンロード

コーディング用途に適したモデルをダウンロード（pull）する:

```bash
ollama pull qwen3-coder
```

他の選択肢として `glm-4.7-flash`（128k コンテキストウィンドウ）や `gpt-oss:20b` なども利用可能。

#### 3. 環境変数の設定

Claude Code が Ollama のローカルサーバーに接続するよう環境変数を設定する:

```bash
export ANTHROPIC_AUTH_TOKEN=ollama
export ANTHROPIC_BASE_URL=http://localhost:11434
```

永続化したい場合は `~/.zshrc` や `~/.bashrc` に追記する。

#### 4. Claude Code の起動

通常どおり `claude` コマンドで起動すれば、ローカル LLM がバックエンドとして動作する。

## ハードウェア要件

ローカル LLM を実用的な速度で動かすには、十分なハードウェアリソースが必要:

- **NVIDIA GPU**: 20B パラメータモデルで VRAM 16GB 以上
- **Apple Silicon Mac**: ユニファイドメモリ 32GB 以上が推奨

Claude Code ではコンテキストウィンドウ 64k トークン以上のモデルが推奨されている（最低 32k）。コーディング用途では長いコンテキストが必要になるため、できるだけ大きなコンテキストウィンドウを持つモデルを選びたい。

## 実用性の注意点

技術的には動作するが、以下の制約がある:

- **応答速度**: クラウド API と比較すると大幅に遅い
- **モデル品質**: ローカルモデルは Claude のオリジナルモデルとは異なる。Claude Code の UI を借りているだけで、Claude そのものが動いているわけではない
- **安定性**: 長い会話や複雑なタスクでは途中で応答が止まることがある

単純なコード補完や短い質問には十分だが、大規模なリファクタリングや複雑なマルチファイル編集には向かない。

## どんな場面で使えるか

- API 料金をかけずに Claude Code の操作感を試したい場合
- プライバシーを重視し、コードを外部に送信したくない場合
- オフライン環境での開発
- Claude Code の学習・練習用途

## まとめ

Ollama との連携により、Claude Code をローカルで無料実行できる環境が整った。ただし、実務での本格利用を考えるなら、応答速度とモデル品質の差は認識しておくべきだ。まずは試してみて、自分のユースケースに合うか判断するのがよいだろう。
