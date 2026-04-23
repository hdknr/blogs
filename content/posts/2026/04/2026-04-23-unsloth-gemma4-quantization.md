---
title: "Unsloth で Gemma 4 26B を極限まで量子化 — 16〜18GB VRAM で動く最強ローカル LLM"
date: 2026-04-23
lastmod: 2026-04-23
draft: false
source_url: "https://github.com/hdknr/blogs/issues/1#issuecomment-4303995463"
categories: ["AI/LLM"]
tags: ["Unsloth", "Gemma4", "LocalLLM", "量子化", "GGUF"]
---

Google の最新 MoE モデル **Gemma 4 26B-A4B** を、個人 PC のローカル環境で最高効率で動かせるようになりました。Unsloth が公開した GGUF 量子化版は、精度を維持しながら劇的な軽量化を実現し、2026 年 4 月時点でローカル LLM の最前線に立っています。

## Gemma 4 26B-A4B とは

Gemma 4 は Google が 2026 年に公開したモデルファミリーで、E2B・E4B・26B-A4B・31B の 4 サイズが提供されています。

**26B-A4B** の「A4B」は *Active 4B*（推論時に活性化するパラメータ数の目安）を意味します。Mixture-of-Experts（MoE）アーキテクチャにより、モデル全体のパラメータ数は 25.2B ありながら、1 トークン生成ごとに動かすパラメータは 3.8B 相当に絞られます。

| 指標 | 26B-A4B (MoE) | 31B (Dense) |
|---|---|---|
| 総パラメータ数 | 25.2B（モデル名は 26B） | 31B |
| 推論時アクティブパラメータ | 3.8B | 31B |
| LMArena スコア (テキスト) | 1441 | 1452 |
| 必要 VRAM (4-bit) | 16〜18GB | — |

26B と名乗りながら推論速度は 4B クラスという驚異的な効率を実現しています。

## Unsloth の GGUF 量子化 — Dynamic 2.0

Unsloth が開発した **Dynamic 2.0 GGUF** は、従来の均一量子化とは異なるアプローチを採用しています。

### KL ダイバージェンスによる精度評価

量子化後のモデルと元モデルの出力分布の差を **KL ダイバージェンス** で測定し、精度劣化が最小になるように各レイヤーの量子化ビット数を動的に調整します。Unsloth の 2026 年 4 月ベンチマークでは、この手法が GGUF 量子化の中で最高精度を記録しています。

### 16〜18GB VRAM に収まる新フォーマット

Unsloth は Gemma 4 26B-A4B 向けに、16〜18GB VRAM のコンシューマー向け GPU でも動かせる量子化フォーマットを提供しています。RTX 4080・RTX 3080 Ti クラスの GPU でも、商用レベルの性能を持つ LLM を安定稼働させられます。軽量フォーマット（IQ4_NL 等）を選べば 16GB に収まるケースもあります。

Apple Silicon 向けには IQ4_NL など ARM 最適化フォーマットも提供されており、Mac ユーザーも恩恵を受けられます。

## ローカルで動かす方法

### 1. モデルのダウンロード

Hugging Face の [unsloth/gemma-4-26B-A4B-it-GGUF](https://huggingface.co/unsloth/gemma-4-26B-A4B-it-GGUF) から GGUF ファイルを取得します。

### 2. llama.cpp / Ollama での実行

```bash
# llama.cpp を使う場合
./llama-cli \
  -m gemma-4-26B-A4B-it-UD-Q4_K_XL.gguf \
  --ctx-size 8192 \
  -p "あなたは優秀なアシスタントです。"
```

```bash
# Ollama を使う場合（Modelfile 経由）
# 1. Modelfile を作成
echo 'FROM ./gemma-4-26B-A4B-it-UD-Q4_K_XL.gguf' > Modelfile
# 2. モデルを登録して起動
ollama create gemma4-26b -f Modelfile
ollama run gemma4-26b
```

### 3. Unsloth ドキュメントの参照

公式の手順は [Gemma 4 - How to Run Locally | Unsloth Documentation](https://unsloth.ai/docs/models/gemma-4) に詳しくまとめられています。

## なぜ今これが革命的なのか

| 状況 | Before | After (Gemma 4 + Unsloth) |
|---|---|---|
| 必要 VRAM | 大型モデルは 40GB+ | 16〜18GB でフラッグシップ級 |
| 推論速度 | 26B なら低速 | MoE で 3.8B 相当の速度 |
| 精度 | 量子化で大きく劣化 | KL ダイバージェンス最小化で高精度維持 |

個人 PC で「商用レベル」の AI を安定運用できる時代が、ついに現実になりつつあります。

## まとめ

- **Gemma 4 26B-A4B** は MoE により 26B の賢さを 3.8B の速度で使える
- **Unsloth Dynamic 2.0 GGUF** は KL ダイバージェンスで精度を最大限維持しながら量子化
- 16〜18GB VRAM のコンシューマー向け GPU でも実用運用が可能
- Apple Silicon（IQ4_NL 等）向けの ARM 最適化フォーマットも提供済み

ローカル LLM の世界は急速に進化しており、Unsloth はベンチマークを更新し続けています。

---

**参考リンク**

- [unsloth/gemma-4-26B-A4B-it-GGUF — Hugging Face](https://huggingface.co/unsloth/gemma-4-26B-A4B-it-GGUF)
- [Gemma 4 - How to Run Locally | Unsloth Documentation](https://unsloth.ai/docs/models/gemma-4)
- [Unsloth Dynamic 2.0 GGUFs](https://unsloth.ai/docs/basics/unsloth-dynamic-2.0-ggufs)
