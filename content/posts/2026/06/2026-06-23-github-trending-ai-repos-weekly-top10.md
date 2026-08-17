---
title: "今週GitHubで急上昇したAIリポジトリ10選"
date: 2026-06-23
lastmod: 2026-06-24
slug: "github-trending-ai-repos-weekly-top10"
draft: false
description: "2026年6月第3週にGitHubで急上昇したAIリポジトリ10選。トークン削減・エージェントセキュリティ・MCP対応・OCRなど多岐にわたる注目OSS。"
source_url: "https://github.com/hdknr/blogs/issues/1#issuecomment-4785277410"
categories: ["AI/LLM"]
tags: ["github", "AI", "agent", "mcp", "OSS", "llm", "ocr"]
---

今週 GitHub で急上昇した AI 関連リポジトリを 10 件まとめました。エージェントフレームワーク、トークン削減、セキュリティ、OCR など、多岐にわたるプロジェクトが注目を集めています。

## 1. headroom — LLM へのトークン消費を最大 95% 削減

**リポジトリ**: [headroomlabs-ai/headroom](https://github.com/headroomlabs-ai/headroom)

LLM に渡す前にログ・ファイル・RAG チャンクを圧縮し、トークン消費を 60〜95% 削減するツールです。ライブラリ・プロキシ・MCP サーバーの 3 つの形態で組み込めるため、既存パイプラインへの導入が柔軟です。

RAG を多用するシステムや、長大なログを LLM に解析させるユースケースでコスト削減に直結します。

## 2. Agent-Reach — APIキー不要のマルチプラットフォーム横断検索

**リポジトリ**: [Panniantong/Agent-Reach](https://github.com/Panniantong/Agent-Reach)

Twitter・Reddit・YouTube・GitHub などの主要プラットフォームを AI エージェントに横断検索させるツールです。API キー不要で CLI 1 本から動く手軽さが特徴です。

情報収集エージェントを構築したい場合に、すぐに使えるインターフェースを提供します。

## 3. agent-skills (addyosmani) — コーディングエージェント向け本番品質スキルセット

**リポジトリ**: [addyosmani/agent-skills](https://github.com/addyosmani/agent-skills)

Addy Osmani が公開した、コーディングエージェント向けの本番品質スキルセットです。AI アシスタントを実務レベルで動かすための土台となるスキル定義が揃っています。

Claude Code などのコーディングエージェントをカスタマイズしたい場合の参考実装として活用できます。

## 4. SkillSpector (NVIDIA) — エージェントスキルのセキュリティスキャナー

**リポジトリ**: [NVIDIA/SkillSpector](https://github.com/NVIDIA/SkillSpector)

AI エージェントスキルの脆弱性・悪意あるパターン・セキュリティリスクを検出するスキャナーです。NVIDIA が公開したエージェント安全対策ツールとして注目されています。

エージェントに外部スキルを組み込む際のセキュリティ審査に利用できます。

## 5. codebase-memory-mcp — コードベースを永続知識グラフとして管理

**リポジトリ**: [DeusData/codebase-memory-mcp](https://github.com/DeusData/codebase-memory-mcp)

コードベースを永続的な知識グラフとしてインデックス化する MCP サーバーです。158 言語に対応し、依存ゼロの単一バイナリで動作します。

コードベースの理解を AI エージェントに持続させたい場合に、セッションをまたいだ記憶として機能します。

## 6. OpenMontage — AIを動画制作エージェントに変換

**リポジトリ**: [calesthio/OpenMontage](https://github.com/calesthio/OpenMontage)

AI コーディングアシスタントを動画制作の環境に変えるオープンソースシステムです。12 本のパイプラインに 52 種のツールを搭載しており、映像編集ワークフローを自動化します。

スクリプトから映像・BGM・字幕の生成まで一気通貫で自動化したい映像クリエイターや、AIで動画制作パイプラインを構築したい開発者に向いています。

## 7. PaddleOCR — LLM入力前処理用の軽量OCRツールキット

**リポジトリ**: [PaddlePaddle/PaddleOCR](https://github.com/PaddlePaddle/PaddleOCR)

PDF や画像を、AI が扱いやすい構造化データに変換する軽量 OCR ツールキットです。100 言語以上に対応しており、LLM への入力前処理として広く使われています。

ドキュメント解析や RAG パイプラインの前段に組み込む用途に適しています。

## 8. agentsview — コーディングエージェントのローカル分析ツール

**リポジトリ**: [kenn-io/agentsview](https://github.com/kenn-io/agentsview)

Claude Code・Codex など 20 以上のコーディングエージェントのセッション履歴・トークン使用量・インサイトを、ローカルで検索・分析できるツールです。

複数のエージェントツールを並行利用している場合のコスト管理や、セッション振り返りに役立ちます。

## 9. LMCache — LLM の KV キャッシュ高速化レイヤー

**リポジトリ**: [LMCache/LMCache](https://github.com/LMCache/LMCache)

LLM の KV キャッシュを高速化する専用レイヤーです。同じコンテキストの再計算を省き、推論コストと遅延を下げます。

同一システムプロンプトや共通コンテキストを多用するサービスで、スループット改善に貢献します。

## 10. flue (withastro) — TypeScript製エージェントハーネスフレームワーク

**リポジトリ**: [withastro/flue](https://github.com/withastro/flue)

自律エージェントを構築・実行するための TypeScript 製ハーネスフレームワークです。セッション・ツール・スキルに加え、安全な実行のためのサンドボックスを備えています。

Astro チームが公開したことで注目されており、型安全なエージェント開発基盤として期待されています。

---

## まとめ

今週のトレンドを俯瞰すると、**トークン効率**（headroom, LMCache）、**エージェントセキュリティ**（SkillSpector）、**マルチプラットフォーム対応**（Agent-Reach）の 3 つが共通テーマとして浮かび上がります。エージェントの実用化が進むにつれ、品質・コスト・安全性を支えるインフラ層のツールが急増しています。

本記事は以下のポストを元に作成しました: [@so_ainsight](https://x.com/so_ainsight/status/2069281811168198760)
