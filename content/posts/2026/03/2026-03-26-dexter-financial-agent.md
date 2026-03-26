---
title: "Dexter: 約200行で動く自律型金融リサーチエージェント"
date: 2026-03-26
lastmod: 2026-03-26
draft: false
description: "約200行のTypeScriptで動くオープンソースの金融リサーチAIエージェント Dexter の仕組み、アーキテクチャ、始め方を解説"
source_url: "https://github.com/hdknr/blogs/issues/1#issuecomment-4132000585"
categories: ["AI/LLM"]
tags: ["agent", "typescript", "github", "react", "anthropic"]
---

オープンソースの自律エージェント **Dexter** が注目を集めている。X では「Claude Code の金融版」と紹介され話題になった。約200行のコードで、銘柄スクリーニングから財務分析、投資根拠のレポート作成までを自動で行うツールだ。

## Dexter とは

[Dexter](https://github.com/virattt/dexter) は、virattt 氏が開発したオープンソースの自律型金融リサーチエージェント。2026年3月時点で GitHub スター数は 18,000 を超える。複雑な金融の質問を受けて、自分でリサーチ計画を立て、データを収集し、結果を検証してレポートにまとめる。

主な機能:

- 割安な銘柄の自動スクリーニング
- 財務データの詳細分析
- 投資根拠のレポート化
- 作業内容の自己検証（セルフバリデーション）

## アーキテクチャ: 4つのエージェント構成

Dexter は ReAct（Reasoning + Acting）パターンに基づくマルチエージェントアーキテクチャで構成されている。ReAct とは、LLM が「考える（Reasoning）」と「行動する（Acting）」を交互に繰り返すことで、複雑なタスクを段階的に解決するパターンだ。

| エージェント | 役割 |
|:---|:---|
| **Planning** | 金融クエリを分析し、リサーチ計画をステップに分解 |
| **Action** | 計画に基づいてツールを呼び出し、リアルタイムデータを取得 |
| **Validation** | 各ステップの完了を検証し、データの十分性をチェック |
| **Answer** | 収集した情報を統合してレポートを生成 |

この Validation エージェントが Dexter の特徴的な部分だ。金融分野では精度が重要なため、自分自身の出力を検証するレイヤーを設けている。ループ検出やステップ数制限などの安全機構も備えている。

## 技術スタック

- **ランタイム**: Bun（高速な JavaScript ランタイム）
- **言語**: TypeScript
- **UI**: React + Ink（React コンポーネントでターミナル UI を構築するライブラリ）
- **LLM オーケストレーション**: LangChain.js
- **LLM プロバイダ**: OpenAI、Anthropic、Google、ローカル Ollama に対応
- **データソース**: Financial Datasets API（リアルタイム市場データ）

## 始め方

リポジトリをクローンして依存関係をインストールする。

```bash
git clone https://github.com/virattt/dexter.git
cd dexter
bun install
```

LLM プロバイダの API キー（OpenAI、Anthropic など）と Financial Datasets の API キーを `.env` に設定して起動する。詳細なセットアップ手順はリポジトリの [README](https://github.com/virattt/dexter) を参照してほしい。

## 注意点

Dexter はあくまでリサーチ支援ツールであり、投資判断を自動化するものではない。出力結果は参考情報として扱い、実際の投資判断は自己責任で行う必要がある。また、Financial Datasets API の利用には別途 API キーの取得が必要になる。

## まとめ

Dexter は「AI エージェントが金融リサーチをどう変えるか」を示す好例だ。約200行という少ないコードでマルチエージェントによる自律的な分析を実現しており、LangChain.js を使ったエージェント開発の参考にもなる。金融データ分析や AI エージェント開発に興味がある人はぜひ [GitHub リポジトリ](https://github.com/virattt/dexter) をチェックしてみてほしい。

## 参考リンク

- [GitHub: virattt/dexter](https://github.com/virattt/dexter)
- [Dexter: Self-Validating AI Agent for Financial Research (YUV.AI)](https://yuv.ai/blog/dexter)
