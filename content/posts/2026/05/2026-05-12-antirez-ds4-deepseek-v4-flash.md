---
title: "Redis 作者 antirez の \"ds4\" — DeepSeek V4 Flash 専用ローカル推論エンジンが M3 Ultra 512GB で 26 token/sec を叩き出す"
date: 2026-05-12
lastmod: 2026-05-12
draft: false
description: "Redis 作者 antirez が公開した DeepSeek V4 Flash 専用ローカル推論エンジン ds4（DwarfStar 4）を解説。Mac Studio M3 Ultra 512GB で 26 token/sec、KV キャッシュのディスク永続化、OpenAI / Anthropic 互換 API、Claude Code からの利用方法、2bit 非対称量子化、Exact Replay 設計まで網羅。"
source_url: "https://github.com/hdknr/blogs/issues/1#issuecomment-4429298637"
categories: ["AI/LLM"]
tags: ["deepseek-v4-flash", "antirez", "ローカルLLM", "apple-silicon", "claude-code", "kv-cache", "llm"]
---

## TL;DR

- Redis 作者の Salvatore Sanfilippo（antirez）が、DeepSeek V4 Flash 専用のローカル推論エンジン **ds4 (DwarfStar 4)** を公開した（公開から数日で 7,700+ stars）
- Apple Silicon の **Metal** と Linux の **CUDA** をターゲットにした C 実装。GGML/llama.cpp にはリンクせず、DeepSeek V4 Flash 一本に特化した「narrow bet」設計
- 公式ベンチで **Mac Studio M3 Ultra 512GB / Q4 / 12k context** で **26.62 token/sec**、Q2 なら 96/128GB の MacBook でも動作
- **OpenAI 互換 + Anthropic 互換** API を持ち、Claude Code から `ANTHROPIC_BASE_URL` を差し替えるだけでローカルモデルとして使える
- **KV キャッシュをディスクに永続化**するなど、ローカル推論の常識を更新する設計思想が随所に光る
- 実運用報告では **コンテキスト 100K → 1M、KV ディスク 8GB → 64GB に拡張して Think Max モードを Claude Code 上でアンロック** した例も登場

## きっかけ: 「ds4 凄すぎるな」というツイート

きっかけは [@m_sigepon](https://x.com/m_sigepon/status/2053882891487391976) 氏のツイートだった。

> M3 Ultra MacStudio 512GBで4bit量子化のDeepSeek 4 Flashを動かしてるが、ds4凄すぎるな。KVキャッシュでプロンプト処理がほぼノータイム、thinking有効でも26token/sec安定で出る。

リンク先の `antirez/ds4` を見に行くと、たった数日前（2026-05-06）に公開されたばかりのリポジトリが既に話題になっていた。

## ds4 (DwarfStar 4) とは

[antirez/ds4](https://github.com/antirez/ds4) は、[**DeepSeek V4 Flash**](/blogs/posts/2026/04/2026-04-25-deepseek-v4-open-source/) 専用に作られたネイティブ推論エンジンだ。README の第一段落がこの設計思想を端的に表している。

> DwarfStar 4 is a small native inference engine for DeepSeek V4 Flash. It is intentionally narrow: not a generic GGUF runner, not a wrapper around another runtime, and not a framework.

「**意図的にナロー（narrow）**」というのがポイントだ。GGUF 汎用ランナーでもなく、他のランタイムのラッパーでもなく、フレームワークでもない。DeepSeek V4 Flash 1 モデルに特化した Metal/CUDA グラフエグゼキュータで、専用のロード、プロンプトレンダリング、KV ステート、サーバ API までを一気通貫で持つ。

`ds4.c` は GGML に **リンクしない**。ただし GGUF の量子化形式、CPU 量子化/ドットロジック、一部のカーネルは llama.cpp から拝借しており、LICENSE にもオリジナルの著作権表示を残している（llama.cpp / GGML へのリスペクトが明記されている）。

## なぜ DeepSeek V4 Flash 専用なのか

README ではこのモデルを「専用エンジンを書く価値がある」とする理由を 8 つ挙げている。要点を抜粋すると:

1. **アクティブパラメータが少ない MoE** なので、284B 級の総パラメータでも高速
2. **Thinking モードの長さが問題複雑度に比例** する（max thinking でなければ他モデルの 1/5 のことも）
3. コンテキストウィンドウが **100 万トークン**
4. 284B のスケールで「知識の端」の質問でも 27B/35B より明確に強い
5. 英語・イタリア語の出力が「準フロンティアモデル感」
6. [**KV キャッシュ**](/blogs/posts/2026/03/2026-03-13-claude-code-local-llm-kv-cache/)が極端に圧縮されており、**ローカルマシンでの長コンテキスト** と **ディスクへの KV キャッシュ永続化** が現実的
7. **2bit 量子化** で品質が崩れない（特殊な非対称量子化を使う）
8. DeepSeek 側からの v4 Flash の **継続的なアップデート** が期待できる

特に「KV キャッシュをディスクに置く」というのは、ローカル推論の暗黙の前提（KV cache は RAM に置くもの）を覆す主張で、これは Mac の高速 SSD と圧縮 KV キャッシュの組み合わせで初めて成立する設計だ。

## 性能ベンチマーク: M3 Ultra / M3 Max / DGX Spark の比較

README に掲載されている公式ベンチ（`--ctx 32768 --nothink --greedy -n 256`）から、ツイートで言及された数字の出所を確認できる。

| マシン | Quant | Prompt | Prefill (t/s) | Generation (t/s) |
| --- | ---: | ---: | ---: | ---: |
| MacBook Pro M3 Max 128GB | Q2 | short | 58.52 | 26.68 |
| MacBook Pro M3 Max 128GB | Q2 | 11,709 tokens | 250.11 | 21.47 |
| Mac Studio M3 Ultra 512GB | Q2 | short | 84.43 | 36.86 |
| Mac Studio M3 Ultra 512GB | Q2 | 11,709 tokens | 468.03 | 27.39 |
| Mac Studio M3 Ultra 512GB | **Q4** | short | 78.95 | **35.50** |
| Mac Studio M3 Ultra 512GB | **Q4** | 12,018 tokens | 448.82 | **26.62** |
| DGX Spark GB10 128GB | Q2 | 7,047 tokens | 343.81 | 13.75 |

ツイートの「**M3 Ultra 512GB / 4bit / 26 token/sec 安定**」は、Q4 で 12k トークン入れた状態の **26.62 t/s** にきれいに一致する。Apple Silicon の Mac Studio が DGX Spark (GB10) を生成速度で上回っているのも興味深いポイントだ。

## 2bit 量子化の「非対称」設計（IQ2_XXS / Q2_K）

2bit という極端な圧縮でなぜ品質が保てるかというと、**MoE のルーティング先 expert だけ強く量子化** し、それ以外（shared expert、projection、routing）はそのまま残す、という非対称設計を採用しているからだ。

- routed MoE experts の up/gate: `IQ2_XXS`
- routed MoE experts の down: `Q2_K`
- shared experts / projections / routing: **量子化しない**

README には「2bit でもコーディングエージェントでツールを安定して呼べる」と書かれており、実質的にローカルでエージェント運用に耐えうる品質ということだ。

## インストールと使い方

### モデルダウンロード

[Hugging Face の `antirez/deepseek-v4-gguf`](https://huggingface.co/antirez/deepseek-v4-gguf) から、専用ビルドの GGUF を取得する。ただし、**汎用の DeepSeek GGUF は動作しないので注意**。

```sh
# 96/128GB マシン向け（imatrix チューニング済み）
./download_model.sh q2-imatrix

# 256GB 以上マシン向け
./download_model.sh q4-imatrix

# 投機的デコーディング用（オプション）
./download_model.sh mtp
```

`./ds4flash.gguf` というシンボリックリンクで選択中のモデルが指される。

### ビルド

macOS（Metal）・Linux（CUDA）はそのまま:

```sh
make
```

Linux で CPU だけのビルドが必要な場合は `make cpu`。

> **注意**: macOS の現行バージョンには **CPU パスを走らせるとカーネルがクラッシュするバグ**（仮想メモリ実装の不具合）がある。Mac では Metal パスのみ実用に耐える、と README に明記されている。

### CLI

```sh
# ワンショット
./ds4 -p "Explain Redis streams in one paragraph."

# インタラクティブ
./ds4
ds4>
```

インタラクティブモードは KV チェックポイントを保持した本物のマルチターンチャット。`/think`, `/think-max`, `/nothink`, `/ctx N`, `/read FILE`, `/quit` などのコマンドがある。デフォルトは thinking モード。

## OpenAI / Anthropic 互換サーバ（ds4-server）

`ds4-server` を立てれば、OpenAI と Anthropic の両方の API 形式で叩ける。

```sh
./ds4-server --ctx 100000 --kv-disk-dir /tmp/ds4-kv --kv-disk-space-mb 8192
```

サポートされているエンドポイント:

- `GET  /v1/models`
- `GET  /v1/models/deepseek-v4-flash`
- `POST /v1/chat/completions` — OpenAI 互換（tools / tool_choice 対応）
- `POST /v1/completions`
- `POST /v1/messages` — **Anthropic 互換**（Claude Code 等で利用可能）

`/v1/messages` が用意されていることで、Claude Code のような Anthropic API クライアントから **ベース URL を差し替えるだけ** でローカルモデルに切り替えられる。

### Claude Code から ds4 を使う

README に紹介されている `~/bin/claude-ds4` 相当のラッパーを書けば、Claude Code のバックエンドが ds4 になる:

```sh
#!/bin/sh
unset ANTHROPIC_API_KEY

export ANTHROPIC_BASE_URL="${DS4_ANTHROPIC_BASE_URL:-http://127.0.0.1:8000}"
export ANTHROPIC_AUTH_TOKEN="${DS4_API_KEY:-dsv4-local}"
export ANTHROPIC_MODEL="deepseek-v4-flash"

export ANTHROPIC_CUSTOM_MODEL_OPTION="deepseek-v4-flash"
export ANTHROPIC_CUSTOM_MODEL_OPTION_NAME="DeepSeek V4 Flash local ds4"
export ANTHROPIC_CUSTOM_MODEL_OPTION_DESCRIPTION="ds4.c local GGUF"

exec claude "$@"
```

ローカルで完結する Claude Code 環境が手に入る、というのは応用範囲が広い。コードがネットを出ない、料金がかからない、レイテンシが下がる――と利点が並ぶ。なお [Apple Silicon の MLX ベース推論加速](/blogs/posts/2026/04/2026-04-15-dflash-mlx-apple-silicon-llm/) と組み合わせる発想も同じ系譜にある。

### opencode から使う

`~/.config/opencode/opencode.json` にプロバイダを追加するだけ:

```json
{
  "$schema": "https://opencode.ai/config.json",
  "provider": {
    "ds4": {
      "name": "ds4.c (local)",
      "npm": "@ai-sdk/openai-compatible",
      "options": {
        "baseURL": "http://127.0.0.1:8000/v1",
        "apiKey": "dsv4-local"
      },
      "models": {
        "deepseek-v4-flash": {
          "name": "DeepSeek V4 Flash (ds4.c local)",
          "limit": { "context": 100000, "output": 384000 }
        }
      }
    }
  }
}
```

## ツール呼び出しの正確性: Exact Replay と DSML 形式

ds4-server のサーバ実装で面白いのは、**ツール呼び出しの DSML テキストを「サンプル時のバイト列ごと」記憶する** という設計だ。

DeepSeek V4 Flash はツールコールを DSML というテキスト形式で出力する。一方、エージェントクライアントは次のターンで OpenAI / Anthropic の JSON オブジェクトとしてツール結果を返してくる。サーバはこの JSON を再び DSML としてレンダリングする必要がある。しかし、**バイト列がわずかでもズレると KV チェックポイントとマッチせず、プロンプト全体を再構築せざるを得なくなる**。

その対策が「Exact Replay」:

- ツール呼び出しごとに推測不可能な API ツール ID を発行
- `tool id → exact sampled DSML block` をサーバが保持
- 次のリクエストで同じ ID が来たら、**モデルが実際にサンプルした正確なバイト列を再注入**

`--disable-exact-dsml-tool-replay` で無効化もできて、その場合は決定的なカノニカル化（JSON から DSML を再生成）にフォールバックする。

加えて、生成中に DSML タグ・パラメータヘッダー・JSON 句読点といった「構造」を出力している間は `temperature=0` に強制し、引数 payload（文字列・ファイル内容など）は通常のサンプリング設定を維持する、というハイブリッド戦略も採用されている。

## 実運用例: 100K → 1M コンテキストへの拡張

ローカル LLM 運用者の都乃健 [@Tono_Ken3](https://x.com/Tono_Ken3/status/2053630984256659669) 氏（RTX Pro 6000 クラスターで「off-grid home AGI」を運用中）が、ds4 の KV キャッシュ SSD 永続化機能を活かした実用例を報告している。

> おぉぉ！DS4 によって KV キャッシュは SSD 容量を使うことができたのでコンテキスト長さを大きい値に設定しても大丈夫なはず
>
> ClaudeCode で DeepSeek V4 Flash Q4 (Anthropic 互換 API)
>
> -c100K → -c1M
> 8192MB → 65536MB
>
> DeepSeek V4 Flash + Think Max モードアンロック！

ポイントを整理すると以下のようになる。

| 項目 | 変更前 | 変更後 |
| --- | --- | --- |
| コンテキスト長（`--ctx`） | 100,000 トークン | **1,000,000 トークン**（DeepSeek V4 Flash の上限） |
| KV ディスク領域（`--kv-disk-space-mb`） | 8,192 MB（8 GB） | **65,536 MB（64 GB）** |
| 思考モード | 通常 | **Think Max モード** |

ds4-server の起動例で言えば次のような変化に相当する。

```sh
# 標準的な設定
./ds4-server --ctx 100000 --kv-disk-dir /tmp/ds4-kv --kv-disk-space-mb 8192

# Tono_Ken3 氏の「全部入り」設定
./ds4-server --ctx 1000000 --kv-disk-dir /tmp/ds4-kv --kv-disk-space-mb 65536
```

これは **DeepSeek V4 Flash の最大コンテキスト 1M トークンを実運用で使い切る** 設定であり、KV キャッシュ全体がメモリではなく SSD に逃がせるからこそ成立する。README には「1M コンテキストの圧縮 KV インデクサだけで 26GB ほどメモリを使う」と書かれており、128GB クラスのマシンでは正攻法で 1M を回そうとすると圧迫されるが、ds4 の SSD 永続化で 64GB の KV ディスクを割り当てれば、メモリは推論本体に温存できる。

さらに注目すべきは「**Think Max モードのアンロック**」だ。DeepSeek V4 Flash は通常の thinking モードでも問題複雑度に比例した可変長の思考を出すが、Think Max では思考量の上限を取り払う。普通なら思考トークンだけで数万〜数十万に膨れあがり、コンテキストが現実的に持たないところを、**1M コンテキスト + KV ディスク永続化のセットで初めて Claude Code 上の最大思考が実用に乗る** ということだ。

「Mac 一台でローカル Claude Code + 1M コンテキスト + Think Max」という、つい数か月前まで非現実だった構成が、ds4 という narrow bet のおかげで動いてしまっている。

## 「narrow bet」という設計思想

README の以下の一節が ds4 のすべてを物語っている。

> The local inference landscape contains many excellent projects, but new models are released continuously, and the attention immediately gets captured by the next model to implement. This project takes a deliberately narrow bet: one model at a time, official-vector validation (logits obtained with the official implementation), long-context tests, and enough agent integration to know if it really works.

「次から次へとモデルが出る → みんな次のモデルの実装に走る」というローカル推論界隈の構造を踏まえて、**1 モデルに腰を据えて end-to-end の完成度を上げる** ことを選んだ。具体的には:

- A) HTTP API 付き推論エンジン
- B) そのエンジン専用に作り込んだ GGUF
- C) コーディングエージェントの実装でテストと検証

の 3 つを同時に揃えてこそ「ローカルモデルが完成したと言える」というビジョンだ。`ds4flash.gguf` という **エンジン専用 GGUF** しか動かない仕様は、この A+B+C の整合性を担保するための意図的な制約だ。

## AGENT.md と AI 共同開発

このプロジェクトのもうひとつの注目点は、README に堂々と書かれている「**GPT 5.5 の強力なアシスト** で開発した」という事実だ。

> This software is developed with strong assistance from GPT 5.5 and with humans leading the ideas, testing, and debugging. We say this openly because it shaped how the project was built.

リポジトリには `AGENT.md` も含まれており、Redis 作者クラスのプロでも AI と共同開発する時代になった、というメッセージが見える。「AI 生成コードが気に入らないならこのソフトウェアはあなた向けではない」と明示する誠実さも印象的だ。

## まとめ: ローカル推論の「完成形」を再定義する試み

ds4 は単なる「速い推論エンジン」ではなく、**ローカル推論の方向性そのものに対する提案** として読める。

| 既存の前提 | ds4 の提案 |
| --- | --- |
| 汎用エンジン + 任意の GGUF | **1 モデル専用エンジン + 専用 GGUF** で end-to-end 最適化 |
| KV キャッシュは RAM に置く | **KV キャッシュはディスクの一級市民**（SSD 永続化） |
| 2bit クォントは品質が崩れる | **MoE expert のみ非対称に圧縮** で品質維持 |
| ツール呼び出しは毎回 JSON から再構築 | **Exact Replay** でモデル出力のバイト列を保存・再注入 |
| ローカル推論は趣味、本気はクラウド | **エージェント運用に耐える品質** をローカルで実現 |

公開直後で **alpha 品質** とは明記されているが、Mac Studio M3 Ultra 512GB を持っているなら今すぐ試す価値がある。128GB の MacBook Pro でも Q2 で動き、README には 96GB Mac で 250k コンテキストを通した報告もある。

「1 モデルに腰を据えて end-to-end を磨く」という ds4 の方針は、ローカル LLM の次の標準像を示しているように見える。

## 参考リンク

- [antirez/ds4 (GitHub)](https://github.com/antirez/ds4)
- [antirez/deepseek-v4-gguf (Hugging Face)](https://huggingface.co/antirez/deepseek-v4-gguf)
- [ツイート: @m_sigepon の動作報告](https://x.com/m_sigepon/status/2053882891487391976)
- [ツイート: @Tono_Ken3 の 1M コンテキスト + Think Max アンロック報告](https://x.com/Tono_Ken3/status/2053630984256659669)
- [llama.cpp (謝辞先)](https://github.com/ggml-org/llama.cpp)

### 関連記事

- [DeepSeek-V4 Preview — Claude Opus 4.6 匹敵・100 万トークン対応のオープンソース LLM が無償公開](/blogs/posts/2026/04/2026-04-25-deepseek-v4-open-source/)
- [Claude Code × ローカル LLM で KV キャッシュが毎回無効化される問題と対策](/blogs/posts/2026/03/2026-03-13-claude-code-local-llm-kv-cache/)
- [Mac の ローカル LLM が 4.1 倍速に — Apple Silicon 向け新技術「DFlash」](/blogs/posts/2026/04/2026-04-15-dflash-mlx-apple-silicon-llm/)
