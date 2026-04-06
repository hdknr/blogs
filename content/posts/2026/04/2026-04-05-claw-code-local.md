---
title: "claw-code-local — Claude Code風のAIコーディングエージェントをローカルLLMで動かす"
date: 2026-04-05
lastmod: 2026-04-05
draft: false
source_url: "https://github.com/hdknr/blogs/issues/1#issuecomment-4188029033"
categories: ["AI/LLM"]
description: "Claude Code風のAIコーディングエージェント claw-code-local の紹介。Ollama や LM Studio でローカルLLMを使い、API費用ゼロ・プライバシー保護でコード生成を実現する方法を解説。"
tags: ["claude-code", "ローカルLLM", "Ollama", "Rust", "agent"]
---

Claude Code ライクなターミナル AI コーディングエージェントを、Anthropic API なしでローカル LLM で動かせる「claw-code-local」が登場しました。Rust で実装された軽量・高速なツールで、Ollama や LM Studio など好みの LLM バックエンドを自由に選べます。

## claw-code-local とは

[claw-code-local](https://github.com/codetwentyfive/claw-code-local) は、Claude Code のアーキテクチャをクリーンルーム方式（既存コードを参照せず仕様から独自に再実装する手法）で作られた「Claw Code」のフォークです。ローカル LLM や任意の OpenAI 互換エンドポイントに接続できるよう拡張されています。

オリジナルの Claw Code は Rust で書かれたマルチプロバイダー API レイヤーを持っていましたが、実際のバイナリにはその機能が組み込まれていませんでした。claw-code-local はこの部分を修正し、Ollama、LM Studio、OpenAI、xAI など様々なプロバイダーに接続できるようにしています。

## 主な特徴

- **ローカル LLM 対応**: Ollama、LM Studio、その他 OpenAI 互換エンドポイントで動作
- **Rust 実装**: 軽量・高速なバイナリ
- **マルチプラットフォーム**: Windows、Linux、macOS に対応
- **コストゼロ**: ローカル LLM を使えば API 費用が不要
- **プライバシー保護**: コードが外部サーバーに送信されないため、機密情報の漏洩リスクを低減

## セットアップ手順

### 1. リポジトリのクローンとビルド

```bash
git clone https://github.com/codetwentyfive/claw-code-local.git
cd claw-code-local/rust
cargo build -p rusty-claude-cli --release
```

ビルド後のバイナリは以下に生成されます:

- Linux/macOS: `rust/target/release/claw`
- Windows: `rust/target/release/claw.exe`

### 2. Ollama でローカルモデルを起動

```bash
# Ollama がインストール済みでない場合（Linux）
# macOS の場合は brew install ollama または公式サイトからダウンロード
curl -fsSL https://ollama.com/install.sh | sh

# コーディング向けモデルをダウンロード・起動
# qwen3-coder:30b は MoE アーキテクチャで、実際のアクティブパラメータは 3.3B のため比較的軽量
ollama pull qwen3-coder:30b
ollama serve
```

### 3. claw-code-local の実行

```bash
# Claw Code が内部的に API キーの存在チェックを行うため、
# ローカル LLM 使用時でもダミー値の設定が必要
export ANTHROPIC_API_KEY="dummy"

# 詳しいオプションは --help で確認
./rust/target/release/claw
```

具体的な使い方やオプションについては、リポジトリの [USAGE.md](https://github.com/codetwentyfive/claw-code-local/blob/main/USAGE.md) を参照してください。

## おすすめのローカルモデル

ローカルで動かす場合、モデルの選択がコード生成品質を大きく左右します。MoE（Mixture of Experts）モデルは総パラメータ数が大きくても、推論時に活性化されるパラメータが少ないため、比較的少ない VRAM で動作します。

| モデル（Ollama名） | アクティブパラメータ | 特徴 |
|--------|-----------|------|
| `qwen3-coder:30b` | 3.3B（MoE） | SWE-Bench で高スコア、コーディング特化 |
| `qwen2.5-coder:32b` | 32B | コーディング能力が高く安定 |
| `deepseek-coder-v2:16b` | 2.4B（MoE） | 軽量ながらコード生成に強い |
| `qwen2.5-coder:7b` | 7B | VRAM 8GB 程度でも動作する軽量モデル |

## Claw Code エコシステムの背景

Claw Code は 2026 年 3 月に公開されたオープンソースプロジェクトで、Claude Code のアーキテクチャを参考にした AI コーディングエージェントフレームワークです。Rust（約73%）と Python（約27%）のハイブリッド構成で、Rust がパフォーマンスクリティカルなパスを、Python がエージェントオーケストレーションと LLM 連携を担当しています。

なお、Claw Code は Claude Code の npm パッケージに含まれていたソースマップ（難読化前のソースコードを復元可能にするファイル）が公開状態になっていた件をきっかけに生まれたプロジェクトです。

claw-code-local はこのエコシステムの中で「ローカル LLM 特化」のポジションを担っており、企業の機密コードを扱う開発者や、API コストを抑えたい個人開発者にとって有力な選択肢となります。

## 注意点

- ローカル LLM の性能は Claude や GPT-4 クラスのクラウドモデルと比べると劣る場合がある。特に複雑なリファクタリングや大規模なコード生成では差が出やすい
- VRAM が十分でない環境では、量子化モデル（Q4_K_M など）の使用が必要になる
- Claw Code 自体はオープンソースだが、前述のソースマップ流出がきっかけで生まれた経緯があり、法的なステータスについては議論が続いている

## まとめ

claw-code-local は「Claude Code の使い勝手をローカル LLM で実現したい」というニーズに応えるツールです。Ollama との組み合わせで、コストゼロかつプライバシーを保ちながら AI コーディングエージェントを活用できます。VRAM に余裕のある GPU を持っている方は、ぜひ試してみてください。
