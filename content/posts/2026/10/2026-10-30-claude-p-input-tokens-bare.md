---
title: "claude -p の入力トークンを実測 — Claude Code の既定 1 万前後を --bare で約 700 に減らす"
description: "claude -p に数百トークンの判断を頼んでも、既定では約 8,500〜13,400 トークンの入力が送られた。--bare で約 700 まで減る。オプション別の実測、プロンプトキャッシュの効果、--bare の認証（apiKeyHelper）と課金の注意をまとめる。"
date: 2026-10-30
lastmod: 2026-10-30
slug: "claude-p-input-tokens-bare"
draft: false
categories: ["AI/LLM"]
tags: ["claude-code", "claude -p", "トークン最適化", "コスト削減", "prompt-caching"]
---

Claude Code の非対話モード `claude -p` は、スクリプトやジョブから「小さな判断を頼む関数」として呼びたくなる（自動化から呼ぶ例は [claude -p をローカル文脈で動かす記事](/blogs/posts/2026/05/self-hosted-runner-vault-writeback/)を参照）。たとえば、JSON Schema で形を決めた計画や分類を返させる使い方だ。ところが `claude -p` は Claude Code そのものなので、プロンプトを短くしても、Claude Code 自身のシステムプロンプトや、設定から読み込まれる情報が毎回一緒に送られる。

本記事では、その「毎回必ず送られる入力（固定分）」がどれくらいあるのかを、オプションを変えながら実測した。わかるのは次の 4 点だ。

- 既定の `claude -p` が、数百トークンの判断にどれだけの入力を送っているか
- どのオプションが効き、どのオプションが効かないか（`--bare` で約 700 まで減る）
- プロンプトキャッシュで費用がどれだけ変わるか
- `--bare` を使うときの認証（`apiKeyHelper`）と課金の注意

## claude -p の入力トークンの測り方と測定条件

数百トークン程度の「計画を JSON で返す」プロンプトを用意し、オプションだけを変えて呼んだ。

- Claude Code 2.1.314、モデルは Sonnet
- 共通のオプションは `--output-format json`、`--tools ""`（ツールをすべて無効にする）、`--json-schema`（出力の形を検証させる）、`--no-session-persistence`（セッションを保存しない）。それ以外のオプションだけを変える
- 入力トークン数は、応答の `usage` にある `cache_creation_input_tokens` と `cache_read_input_tokens` の合計で数える。`claude -p` の入力はプロンプトキャッシュに載るため、入力の大半はこの 2 つに計上される（`input_tokens` は 2〜4 で、ほぼ無視できた）
- 実行場所は、表の「既定（空のディレクトリ）」だけが CLAUDE.md などのない空のディレクトリで、それ以外は筆者のブログのリポジトリ内

## オプション別の実測結果：既定は 1 万前後、`--bare` で約 700

| 呼び出し方 | 入力トークン |
|---|---|
| 既定（リポジトリ内） | 13,417 |
| 既定（空のディレクトリ） | 8,566 |
| `--system-prompt` で既定のシステムプロンプトを差し替え | 14,421 |
| `--strict-mcp-config`（MCP サーバーを読み込まない） | 11,712 |
| `--setting-sources ""`（ユーザー・プロジェクト・ローカルの設定ファイルを読み込まない） | 6,490 |
| `--setting-sources ""` と `--strict-mcp-config` | 6,490 |
| `--setting-sources ""` と `--strict-mcp-config` と `--system-prompt` | 4,077 |
| `--bare`（`apiKeyHelper` で認証） | 695 |
| `--bare` と `--system-prompt` | 651 |

`apiKeyHelper` は、API キーを返すスクリプトを指定する設定項目だ（詳しくは後述）。表から読み取れることは 4 つある。

- **自分のプロンプトより固定分のほうがずっと大きい**：数百トークンの判断を頼むのに、既定の呼び出しでは空のディレクトリでも約 8,500 トークン、リポジトリ内では 1 万トークンを超える入力が送られている
- **どのディレクトリで実行するかで変わる**：同じ呼び出しでも、リポジトリ内で実行すると、空のディレクトリより約 4,900 トークン多かった。CLAUDE.md の分量が効くことは、[CLAUDE.md の英語化でトークンを測った記事](/blogs/posts/2026/05/claude-md-english-tiktoken-measurement/)でも見た。自動化から呼ぶときは、作業ディレクトリをどこにするかも設計の一部になる
- **システムプロンプトの差し替えだけでは減らない**：
  - `--system-prompt` 単独では、かえって少し増えた
  - 設定ファイルの読み込みを止めると、リポジトリ内の既定の半分以下になった。`--strict-mcp-config` を足しても値は変わらなかったので、MCP サーバーの設定も設定ファイル経由で読まれていたと考えられる
  - さらにシステムプロンプトを差し替えると、既定の約 3 割まで下がった
- **いちばん効くのは `--bare`**：hooks・プラグイン・MCP サーバー・CLAUDE.md の自動読み込みなどをまとめて省く `--bare` では、既定の約 5% になった。プロンプトに含めた情報だけで決まる判断（計画や分類）には、これで十分だ。ただし、認証と課金のしかたが変わる（後述）

数値は、使っている人の設定・プラグイン・MCP サーバーの数によって大きく変わる。自分の環境で測ってから決めたい。応答を JSON で保存し、`jq` で `usage` を読めば測れる（条件をそろえるなら `--json-schema` も付ける）。

```bash
claude -p "（自分のプロンプト）" --output-format json --tools "" > out.json
jq '.usage.cache_creation_input_tokens + .usage.cache_read_input_tokens' out.json
```

## プロンプトキャッシュで費用はさらに変わる

費用にはもう 1 つ大きな要因がある。プロンプトキャッシュだ。同じ呼び出しを 2 回続けて実行すると、2 回目は入力がキャッシュから読まれて安くなった。金額は、応答の `total_cost_usd` に出る推定値だ。既定の行はサブスクリプションで認証した呼び出しなので、この額がそのまま請求されるわけではない。`--bare` の行は API の利用として課金される額の目安になる。

| 呼び出し方 | 1 回目 | 2 回目（キャッシュあり） |
|---|---|---|
| 既定（リポジトリ内） | 約 0.055 ドル | 約 0.003 ドル |
| `--bare` | 約 0.0033 ドル | 約 0.0016 ドル |

キャッシュがない 1 回目では、既定と `--bare` の差は約 17 倍ある。キャッシュに乗った 2 回目では、差は約 2 倍まで縮む。同じ形の判断を何度も呼ぶ自動化では、固定分を削ることと、固定分を毎回同じに保ってキャッシュに乗せることの両方が効く。キャッシュが効きやすいのは固定部分を毎回同じにしたときだ（[CLAUDE.md の部分英語化でキャッシュを効かせる記事](/blogs/posts/2026/05/claude-md-english-prompt-caching/)、[Claude Code の既定設定とトークンの記事](/blogs/posts/2026/04/claude-code-token-optimization/)も参考になる）。

## claude -p --bare の認証（apiKeyHelper）と課金の注意

### 認証と課金が変わる

`--bare` では、Anthropic への認証は `ANTHROPIC_API_KEY` か、`--settings` で指定する `apiKeyHelper` だけになる（`claude --help` の説明による）。サブスクリプションの OAuth やキーチェーンは読まれない。つまり、呼び出しはサブスクリプションの枠ではなく、API キーを発行した Claude Console 上の組織の API 利用として課金される。

Team プランと Max プランなら、毎月の API クレジットを充てられる。Console の組織を紐付けておけば、その組織の API キーでの利用がクレジットから引かれる。クレジットは翌月に繰り越されず、Team プランは席数分を合算して月 500 ドルが上限だ。対話で使う Claude Code の利用はクレジットの対象外になる（[Monthly API credits for Max and Team plans](https://support.claude.com/en/articles/17154008-monthly-api-credits-for-max-and-team-plans)）。

### --bare で「Not logged in」になるときは apiKeyHelper を使う

公式ドキュメントでは、`--bare` のときは `ANTHROPIC_API_KEY` を環境変数で設定するのが標準の手順になっている。ところが手元では、環境変数だけで渡すと「Not logged in」で失敗し、同じキーを `apiKeyHelper` からも返すようにすると動いた。

キー自体は、API の token counting エンドポイントで有効だと確かめてある。原因は特定できていない。なお、キーはチームに変換した Console の組織で発行したもので、先頭が `sk-ant-api` ではなかった。

`apiKeyHelper` には、キーを標準出力に返すだけのスクリプトを指定する。キーそのものは権限 600 のファイルに置き、スクリプトには実行権限を付けておく。

```sh
#!/bin/sh
# key_helper.sh（chmod 700）。キーは ~/.config/anthropic/api_key（chmod 600）に置く
cat "$HOME/.config/anthropic/api_key"
```

呼び出しは次のようになる。`/path/to/key_helper.sh` は、上のスクリプトの絶対パスに置き換える。`$SCHEMA` には、返してほしい形を表す JSON Schema を入れる。

```bash
SCHEMA='{"type":"object","properties":{"done":{"type":"boolean"},"steps":{"type":"array"}},"required":["done","steps"]}'
claude -p "（判断を頼むプロンプト）" --bare --settings '{"apiKeyHelper": "/path/to/key_helper.sh"}' \
  --output-format json --json-schema "$SCHEMA" --tools ""
```

### 本番ではキーを置かない構成も検討する

サーバーで動かすなら、キーのファイルはシークレットマネージャーに置き換えたい。AWS や Google Cloud、GitHub Actions などの上なら、Claude Console の [Workload Identity Federation](https://platform.claude.com/docs/en/manage-claude/workload-identity-federation) で、長期の API キーを置かずに済ませる手もある。ただし、`claude -p --bare` と組み合わせて動くかどうかは確かめていない。

## claude -p・--bare・Messages API の使い分け

`--bare` で固定分を 700 程度まで削るなら、Messages API や Claude Agent SDK を直接呼ぶのも手だ。`claude -p --bare` には、`--json-schema` による出力の検証や、CLI 1 行で呼べる手軽さが残る。

- **ツールを有効にしてリポジトリのファイルを読ませながら考える判断**：既定の `claude -p`。ツールを有効にすると、固定分はさらに増える
- **プロンプトに含めた情報だけで決まる判断**：`claude -p --bare`、または API の直接呼び出し
- **同じ判断を繰り返し呼ぶ場合**：どちらを選んでも、固定部分を毎回同じにしてキャッシュに乗せる

## まとめ

- `claude -p` は、プロンプトを短くしても既定で約 8,500〜13,400 トークンの固定分を送っていた（筆者の環境）
- 作業ディレクトリによっても約 4,900 トークン変わる。自動化では実行場所も設計の一部になる
- `--system-prompt` だけでは減らない。効くのは設定ファイルの読み込みを止めることで、`--bare` なら既定の約 5% まで減る
- プロンプトキャッシュも費用に大きく効く。既定の呼び出しでも、2 回目の推定費用は約 0.055 ドルから約 0.003 ドルに下がった
- `--bare` は API キーでの認証になり、課金先が Console の組織に変わる。環境変数で「Not logged in」になったら `apiKeyHelper` を試す
- 数値は環境しだいなので、自分の環境で一度測ってから決める

## 参考

- [Claude Code: Run Claude Code programmatically（headless / `claude -p`）](https://code.claude.com/docs/en/headless)
- [Claude Code: CLI reference](https://code.claude.com/docs/en/cli-reference)
- [Monthly API credits for Max and Team plans](https://support.claude.com/en/articles/17154008-monthly-api-credits-for-max-and-team-plans)
- [Workload Identity Federation（Claude Platform）](https://platform.claude.com/docs/en/manage-claude/workload-identity-federation)
