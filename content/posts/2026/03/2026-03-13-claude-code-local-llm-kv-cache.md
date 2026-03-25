---
title: "Claude Code × ローカルLLM で KVキャッシュが毎回無効化される問題と対策"
date: 2026-03-13
lastmod: 2026-03-13
draft: false
source_url: "https://github.com/hdknr/blogs/issues/1#issuecomment-4051391820"
categories: ["AI/LLM"]
tags: ["claude-code", "llm", "ollama"]
---

Claude Code をローカルLLM（llama.cpp、Ollama など）で使う際に、**毎回プロンプト処理に異常な時間がかかる**という問題が報告されています。原因は Claude Code が付加する「Attribution Header」によるKVキャッシュの無効化です。設定一つで解決できるので、対処法をまとめます。

## 何が起きているのか

Claude Code v2.1.36 以降、リクエストごとに以下のような Attribution Header がプロンプトの先頭に付加されるようになりました。

```
x-anthropic-billing-header: cc_version=xxxx; cc_entrypoint=cli; cch=xxxx;
```

この `cch` の値がリクエストのたびに変化します。ローカルLLMサーバー（llama.cpp、Ollama、LM Studio など）は**プロンプトの先頭からバイト単位で一致した部分までKVキャッシュを再利用**する仕組みのため、先頭が毎回変わると**キャッシュが丸ごと無効化**されます。

結果として、数万トークンのシステムプロンプトや会話履歴を毎回ゼロから処理することになり、**推論速度が最大90%低下**するという報告があります。

## 対策：Attribution Header を無効化する

`~/.claude/settings.json` の `env` セクションに以下を追加します。

```json
{
  "env": {
    "CLAUDE_CODE_ATTRIBUTION_HEADER": "0"
  }
}
```

既に `settings.json` がある場合は `env` セクション内にキーを追加してください。

### 注意点

- **`export CLAUDE_CODE_ATTRIBUTION_HEADER=0` ではダメ**。シェルの環境変数として設定しても反映されません。必ず `settings.json` 経由で設定します
- ついでに不要なテレメトリも無効化しておくと、余計な通信を減らせます

```json
{
  "env": {
    "CLAUDE_CODE_ATTRIBUTION_HEADER": "0",
    "CLAUDE_CODE_ENABLE_TELEMETRY": "0",
    "CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC": "1"
  }
}
```

## KVキャッシュの仕組みをおさらい

ローカルLLMサーバーが採用している Prefix Caching（Automatic Prefix Caching）は、プロンプトの**先頭から連続して一致するトークン列**のKV（Key-Value）テンソルを再利用する仕組みです。

```
リクエスト1: [システムプロンプト][会話A]
リクエスト2: [システムプロンプト][会話A][新しいメッセージ]
             ^^^^^^^^^^^^^^^^^^^^^^^^
             この部分のKVキャッシュを再利用 → 高速
```

ところが先頭に変動するヘッダーが入ると：

```
リクエスト1: [header-abc][システムプロンプト][会話A]
リクエスト2: [header-xyz][システムプロンプト][会話A][新しいメッセージ]
             ^^^^^^^^^^^^
             先頭が不一致 → キャッシュ全破棄 → 全トークン再処理
```

これが「毎回クッソ待たされる」原因です。

## llama.cpp 側のチューニング

KVキャッシュ自体を有効活用するために、llama.cpp サーバー側の設定も確認しておきましょう。

| パラメータ | 説明 |
|---|---|
| `-cram` | KVキャッシュサイズの指定（デフォルト8GB、`-1` で無制限） |
| `--swa-full` | SWA（Sliding Window Attention）使用時にキャッシュをフルサイズで保持 |
| `--cache-type-k q8_0` | KVキャッシュの量子化（VRAMの節約） |

## おすすめのローカルLLMモデル

2026年3月時点で、Claude Code との組み合わせで評価の高いモデル：

- **Qwen3.5 32B（MoE）** — エージェント型コーディングタスクに強い
- **GLM-4.7-Flash** — 軽量で高速、35B MoE
- **DeepSeek-R1 系** — 推論能力が高い

## まとめ

| 項目 | 内容 |
|---|---|
| 原因 | Claude Code の Attribution Header が毎回変化し、KVキャッシュを破棄 |
| 対策 | `~/.claude/settings.json` で `CLAUDE_CODE_ATTRIBUTION_HEADER` を `"0"` に設定 |
| 効果 | プロンプト処理時間が大幅短縮（最大10倍の改善報告あり） |

ローカルLLMで Claude Code を使っている方は、この設定を忘れずに入れておきましょう。
