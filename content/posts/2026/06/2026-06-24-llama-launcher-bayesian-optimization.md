---
title: "llama-launcher：ベイズ最適化でllama.cppの起動パラメータを自動調整するGUIツール"
date: 2026-06-24
lastmod: 2026-06-24
slug: "llama-launcher-bayesian-optimization"
draft: false
source_url: "https://github.com/hdknr/blogs/issues/1#issuecomment-4785351760"
description: "OSSツール llama-launcher の紹介。Optuna の TPE によるベイズ最適化で llama.cpp のスレッド数・バッチサイズ・KVキャッシュ型・投機的デコード設定を自動探索し、PPL検証で品質を保ちながら推論速度を改善する仕組みと使い方を解説。"
categories: ["AI/LLM"]
tags: ["LLM", "llama.cpp", "ローカルLLM", "ベイズ最適化", "Optuna"]
---

## 概要

ローカル環境で `llama.cpp` を使って LLM を動かすとき、地味に面倒なのが起動パラメータの調整だ。スレッド数、バッチサイズ、KVキャッシュの型、投機的デコード（speculative decoding）の設定など、チューニング対象は多岐にわたり、最適値はハードウェア構成やモデルによって変わる。

この面倒なパラメータ調整を自動化する OSS ツールが **llama-launcher** だ。X（旧Twitter）で AI 系情報発信をしている「葉加瀬アイ(Ai-Hakase)」氏（[@ai_hakase_](https://x.com/ai_hakase_)）の[投稿](https://x.com/ai_hakase_/status/2066838712269304255)で紹介されているのを見かけた。ちょうど v1.3 系で「ベイズ最適化」機能が実装されたタイミングの投稿で、同投稿では推論速度が最大15%向上したと報告されている。

実際にリポジトリを確認したところ、[SolaryKryptic/llama-launcher](https://github.com/SolaryKryptic/llama-launcher) という実在の OSS で、Optuna の TPE（Tree-structured Parzen Estimator）によるベイズ最適化を使ってパラメータを自動探索する機能が実装されていることがわかった。本記事ではこの自動最適化の仕組みと使い方を紹介する。

## llama-launcher とは

llama-launcher は、`llama.cpp` の `llama-server` 起動コマンドを GUI で組み立てるための Python 製アプリケーションだ。GGUFモデルを選択し、各種設定をポチポチ変更するだけで起動コマンドが生成される。`llama.cpp` 本体は同梱されておらず、事前にビルド済みであることが前提となる。

主な機能は次の通り。

- **ハードウェア自動検出**：CPU（コア/スレッド数）、GPU、VRAM、システムRAMを起動時に表示（Windows の WMI を利用）
- **GGUFモデル選択**：ファイルダイアログでの選択に加え、Hugging Face の GGUFモデル一覧へのリンクも用意
- **自動最適化（Auto-Optimiser）**：Optuna の TPE によるベイズ最適化でスレッド数、バッチサイズ、KVキャッシュ型、投機的デコード関連の設定などを自動探索
- **コマンドプレビュー／コピー／`.bat`保存**：生成したコマンドをその場でコピーしたり、`cmd.exe` で直接実行したり、`.bat` ファイルとして保存できる

## ベイズ最適化（Auto-Optimiser）の仕組み

v1.3 系で導入された最大の目玉が、この Auto-Optimiser 機能だ。README によると、逐次探索（Sequential optimisation）は廃止され、Optuna ベースの TPE によるベイズ最適化のみがサポートされている。

### 探索対象パラメータ

- スレッド数・実効スレッドバッチ数
- バッチサイズ／マイクロバッチサイズ
- KVキャッシュ型、ドラフト（MTP：投機的デコードで使う軽量な下書きモデル関連）のキャッシュ型
- 投機的デコード（speculative decoding）関連の設定

### 品質検証とフォールバック

最適化プロセスは、速度だけでなく出力品質も損なわないよう次のように設計されている。

1. **PPL検証**：キャッシュ設定を変更した試行に対して `llama-perplexity` を使い、元のベースラインとパープレキシティ（PPL）を比較して品質劣化がないかを検証する
2. **ペナルティ付与**：ベンチマークやPPL計算が失敗した試行には低いペナルティスコアを与え、Optuna が「悪い領域」を学習して次の探索に活かせるようにする
3. **ベースラインへのフォールバック**：最終的にベースラインを上回るPPL検証済みの試行が見つからなければ、結果画面はベースラインのコマンドをそのまま採用する

最適化が終わると、結果画面にはベースラインとのスコア・速度・PPLの比較、そして改善率（improvement percentage）が表示される。投稿で言及されていた「推論速度が最大15%向上」という数字は、こうした改善率表示の一例だと考えられる。ハードウェアやモデル構成によって数値は変動するため、あくまで目安として捉えておくとよいだろう。

## 使い方

現時点では Windows 環境（ハードウェア検出に WMI を利用）向けに提供されている。

1. GitHub の [Releases](https://github.com/SolaryKryptic/llama-launcher/releases) から `.exe` をダウンロードして実行する（Windows SmartScreen の警告が出た場合は「詳細情報」→「実行」を選択）
2. GGUFモデルファイルを選択する
3. 「Auto-Optimiser」から最適化設定（スコアの重み付け、コンテキストサイズ、試行回数、PPL閾値など）を行い、最適化を実行する
4. 最適化完了後、結果画面で改善率を確認し、生成されたコマンドをコピーするか `.bat` として保存する

事前準備として、`llama-server.exe` と `llama-perplexity.exe` を含む `llama.cpp` のビルド済みバイナリが必要になる点は注意したい。

## まとめ

llama-launcher は、ローカルLLM運用でありがちな「どのフラグを組み合わせれば最速になるか分からない」という問題に対して、ベイズ最適化による自動探索というアプローチで応えるツールだ。PPL検証によって品質劣化を防ぎつつ速度改善を狙える設計になっており、`llama.cpp` を日常的に触っている人であれば試してみる価値がある。

- リポジトリ: [SolaryKryptic/llama-launcher](https://github.com/SolaryKryptic/llama-launcher)
