---
title: "Harness Engineering：AIエージェントを信頼性高く動かすランタイム設計の考え方"
date: 2026-06-16
lastmod: 2026-06-16
slug: "harness-engineering-ai-agents"
draft: false
source_url: "https://github.com/hdknr/blogs/issues/1#issuecomment-4714997720"
categories: ["AI/LLM"]
tags: ["Harness Engineering", "ai-agent", "llm", "claude-code", "エージェント設計"]
---

## はじめに

「エージェント = モデル + ハーネス」

AIエージェントの構築を考えるとき、多くの人はモデルそのものの性能に注目しがちです。しかし実際のエージェント開発において、同じくらい重要なのが **ハーネス（Harness）** と呼ばれるランタイム層の設計です。

Mercado LibreのエンジニアであるSanti（[@santtiagom_](https://x.com/santtiagom_/)）がXでシェアしたポストには、この考え方が端的にまとめられていました。

> agente = modelo + harness.  
> modelo → es el cerebro.  
> harness (runtime) → es la capa que coordina la ejecución del agente.  
> Conecta al modelo con tools, memory, y loops.  
> Además encargarse de: planificación, permisos, monitoreo, validaciones, manejo de errores, y reintentos.

日本語に訳すと：

> エージェント = モデル + ハーネス  
> モデル → 脳みそ  
> ハーネス（ランタイム）→ エージェントの実行を調整するレイヤー  
> モデルをツール・メモリ・ループと接続する  
> さらに担うこと：計画立案、権限管理、監視、バリデーション、エラーハンドリング、リトライ

このシンプルな等式こそが、Harness Engineering という分野の核心をついています。

## Harness Engineering とは

[walkinglabs.github.io のコース](https://walkinglabs.github.io/learn-harness-engineering/es/)では、Harness Engineering の考え方を次のように表現しています。

> A harness doesn't "make the model smarter"; rather, it establishes a closed-loop working system for the model.

つまり、ハーネスはモデルを「賢く」するものではなく、モデルのための「閉ループ動作システム」を確立するものです。コースはさらに「モデルの重みの外にあるすべての工学的インフラが、モデルの能力をどれだけ実際に発揮できるかを決定する」と強調します。

つまり、モデルのキャパビリティを向上させるのではなく、**モデルが動く環境そのものを設計・制御する**という発想の転換です。

### ハーネスが担う役割

ハーネスはモデルと外部世界の橋渡し役を果たします。具体的には以下を統括します。

| 役割 | 内容 |
|------|------|
| **ツール連携** | ファイル操作・API呼び出し・コード実行などのツールをモデルに提供 |
| **メモリ管理** | 会話履歴・タスク状態・コンテキストの永続化 |
| **実行ループ** | モデルの応答→ツール呼び出し→結果フィードバックのサイクル制御 |
| **計画立案** | 複雑なタスクのステップ分解と順序管理 |
| **権限管理** | どの操作を許可するかのポリシー適用 |
| **監視・ロギング** | 実行過程の可視化とデバッグ支援 |
| **バリデーション** | モデル出力の検証と正規化 |
| **エラーハンドリング** | 失敗時のリトライ・フォールバック戦略 |

## Harness Engineering の主要概念

コースの学習目標をもとに整理すると、以下の5つの設計上の考え方が浮かび上がります。

### 1. 行動制約（Behavioral Constraints）

明示的なルールと境界線を設けることでエージェントの行動をガイドします。例えば Claude Code の `CLAUDE.md` や `settings.json` の allowlist がこれに相当します。モデルに何でもさせるのではなく、**何をしてよいか・何をしてはいけないか**を明確にすることで信頼性が上がります。

### 2. コンテキストの永続化（Context Persistence）

長時間タスクや複数セッションにまたがる状態管理です。エージェントが「どこまでやったか」「何を知っているか」を維持することで、タスクの一貫性を保ちます。

### 3. 早期成功の防止と検証（Premature Success Prevention）

エージェントが実際には完了していないのに「完了した」と宣言してしまう問題への対策です。「動いた」と「正しく動いた」は別物であることを前提に、end-to-endテストや自己検証（self-reflection）のメカニズムを組み込みます。これにより、表面的な成功宣言を防ぎつつ、出力の本当の正しさを確認します。

### 4. 実行の透明性（Runtime Transparency）

エージェントの実行過程を観察・デバッグできる仕組みを整えます。ブラックボックスなエージェントは本番運用に耐えません。

## なぜ今 Harness Engineering が重要か

Claude Code・Cursor・Devinのようなコーディングエージェントが普及し始めた今、「モデルを使う」から「エージェントを運用する」フェーズに移行しています。

高性能なモデルを使っていても、ハーネスの設計が貧弱だとエージェントは：

- 同じミスを何度も繰り返す
- タスクを中途半端なまま「完了」と報告する
- 予期しない副作用を起こす（例：ファイルの誤削除、意図しないAPIコール）
- 長時間タスクでコンテキストを失い、最初からやり直す

これらはモデルの問題ではなく、**ハーネスの問題**です。

## 学習リソース

[Learn Harness Engineering コース](https://walkinglabs.github.io/learn-harness-engineering/es/)では3つの学習パスが用意されています。

1. **講義（Lectures）** — 高性能なモデルでも失敗する理由の理論的解説
2. **プロジェクト（Projects）** — ゼロから信頼性の高いエージェント環境を構築するハンズオン
3. **リソース（Resources）** — すぐに使えるテンプレート（AGENTS.md、feature_list.jsonなど）

コースはスペイン語で提供されていますが、内容自体はOpenAIやAnthropicの研究を参照した普遍的な設計原則です。

## まとめ

AIエージェント開発において「モデルの賢さ」だけに頼る時代は終わりつつあります。Harness Engineering は、エージェントの信頼性・安全性・可観測性を体系的に向上させるための実践的なアプローチです。

**エージェント = モデル + ハーネス** — この等式を常に念頭に置きながら設計することで、本番環境で使えるエージェントシステムを構築できます。
