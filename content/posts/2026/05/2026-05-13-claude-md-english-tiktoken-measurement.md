---
title: "CLAUDE.md+SKILL.md 英語化で 37.6% トークン削減 — tiktoken による実測結果と内訳"
date: 2026-05-13
lastmod: 2026-05-13
slug: "claude-md-english-tiktoken-measurement"
draft: false
categories: ["AI/LLM", "ツール/開発環境"]
tags: ["claude-code", "prompt-caching", "CLAUDE.md", "tiktoken", "トークン削減", "実測"]
---

## 結論を先に

`CLAUDE.md` と 4 つの `SKILL.md` を日本語から英語に書き換えた結果、毎セッション読み込まれる固定資産のトークン量が **13,538 → 8,441（-37.6%、絶対値で 5,097 トークン削減）** になった。

文字数は逆に **+49%** 増えているのに、トークンは大幅に減るという一見矛盾した結果である。理由と内訳を以下に示す。

## 背景

[CLAUDE.md 英語化の記事](/blogs/posts/2026/05/2026-05-13-claude-md-english-prompt-caching/) と Skills 英語化 PR (#394) の続編。

前 2 つの作業で、ハーネスの「内側」（LLM だけが読む固定資産）を英語化し、「外側」（人間が読むブログ記事や許可プロンプト）は日本語のまま維持する**部分英語化パターン**を実装した。

ただし、その記事では「Anthropic 公開の日本語比率 1.94x」から **推定 48% 削減** とラフに見積もっていた。実際の効果は推定モデル次第で 2% 〜 48% と幅があり、本当の値を知るには実測しかない。

## 計測手法

### tiktoken (cl100k_base) を採用

- **理由**: オフラインで動く、API key 不要、結果が再現可能
- **限界**: Anthropic Claude のトークナイザーではなく OpenAI GPT-4 系。ただし日本語のトークン化挙動は近似として広く使われる
- **対案**: Anthropic SDK の `count_tokens` API が最も正確だが、API キーが必要

### venv で隔離

PEP 668 で system Python が保護されているため、`.claude/temp/venv-tiktoken/` に隔離した venv を作って tiktoken だけ入れた。

```bash
python3 -m venv .claude/temp/venv-tiktoken
.claude/temp/venv-tiktoken/bin/pip install tiktoken
```

### 計測対象

| ファイル | 役割 |
|---|---|
| `CLAUDE.md` | プロジェクトルート規約。毎セッション読み込み |
| `.claude/skills/blog/SKILL.md` | `/blog` スキル定義 |
| `.claude/skills/wiki-ingest/SKILL.md` | `/wiki-ingest` スキル定義 |
| `.claude/skills/wiki-lint/SKILL.md` | `/wiki-lint` スキル定義 |
| `.claude/skills/permission-review/SKILL.md` | `/permission-review` スキル定義 |

旧バージョンは `git show 4bf84cf^:CLAUDE.md` のように、英語化直前のコミットから取り出した。

## 実測結果

### ファイル別トークン数

| ファイル | 旧 tokens | 新 tokens | 削減 | 削減率 |
|---|---:|---:|---:|---:|
| CLAUDE.md | 2,301 | 1,530 | -771 | **-33.5%** |
| blog/SKILL.md | 6,555 | 4,121 | -2,434 | **-37.1%** |
| wiki-ingest/SKILL.md | 1,364 | 847 | -517 | **-37.9%** |
| wiki-lint/SKILL.md | 1,060 | 693 | -367 | **-34.6%** |
| permission-review/SKILL.md | 2,258 | 1,250 | -1,008 | **-44.6%** |
| **TOTAL** | **13,538** | **8,441** | **-5,097** | **-37.6%** |

最も効率化が大きかったのは `permission-review/SKILL.md`（-44.6%）。次が `wiki-ingest`（-37.9%）。CJK 文字密度が高かったファイルほど削減効果が大きい。

### 文字数とトークン数の逆説

| 指標 | 旧（日本語混在） | 新（英語中心） | 変化 |
|---|---:|---:|---:|
| 総文字数 | 21,129 | 31,476 | **+49.0%** |
| 総トークン数 | 13,538 | 8,441 | **-37.6%** |
| CJK 文字数 | 8,678 | 531 | **-93.9%** |
| tokens / char | 0.641 | 0.268 | **-58.2%** |

**文字数が 49% 増えてもトークンが 38% 減る** — これが英語化の本質的なメリットだ。

日本語 1 文字あたり約 0.64 トークン、英語 1 文字あたり約 0.27 トークン。英訳で表現が長くなっても、1 文字あたりのトークン消費が **2.4 倍効率化** されるので、結果的にトークン総量が減る。

## 推定モデルとの突き合わせ

前記事では tokenizer がなかったので、3 つの推定モデルでレンジを出していた。実測値との比較:

| モデル | 仮定 | 推定削減率 | 実測 (37.6%) との誤差 |
|---|---|---:|---:|
| A. Conservative | CJK 1.7 chars/tok | 2.0% | **-35.6 pt（過小評価）** |
| B. Anthropic-likely | CJK 1.0 chars/tok | 29.8% | -7.8 pt（やや過小評価） |
| C. PR #372 ratio | 1.94x 逆算 | 48.5% | +10.9 pt（過大評価） |
| **実測 (cl100k_base)** | — | **37.6%** | — |

事前推定の中では **モデル B**（CJK 1.0 chars/tok）が最も近かった。モデル C は Anthropic の公開比率 1.94x をそのまま使ったが、これは「同じ内容を完全に英訳した場合」の理想値で、実翻訳には英語の冗長性が含まれて到達しない。

ただし cl100k_base は GPT-4 系で、Anthropic Claude のトークナイザーとはズレる。**真の Claude 値は実測の 37.6% から数 pt 上振れする可能性**がある（Anthropic は日本語に対して cl100k_base よりわずかに非効率なため）。

## 5,097 トークン削減の意味

絶対値で **5,097 トークン**。これは毎セッションのシステムプロンプト先頭で読み込まれる「固定費」が約 5K 減ったことを意味する。

体感での価値:

- 短い質問 1 回分のコンテキスト（簡単な「これって何？」レベル）≈ 数百トークン
- 中規模の `/blog` セッション（記事 1 本作成）≈ 2 万〜10 万トークン
- 5,097 トークン削減 ≈ **新規セッション 1 回ごとに数百分の 1〜数十分の 1 のコスト圧縮**

prompt caching が効くと cache hit 後はこのコストはさらに 1/10 程度になるので、**真の効果は「キャッシュミス時の初回読み込み」と「キャッシュ無効化されたとき」に最も効く**。

## 残課題と次のステップ

### 1. Anthropic 実値での再測定

cl100k_base は近似。`anthropic` SDK の `count_tokens` API でやり直すと数 pt 変動する可能性がある:

```python
import anthropic
client = anthropic.Anthropic()
client.messages.count_tokens(
    model="claude-opus-4-7",
    messages=[{"role": "user", "content": text}]
)
```

API キーが必要で、外部 API 呼び出しが発生する点が留意事項。

### 2. 英訳の冗長性削減

文字数が +49% 増えているのは、英訳が冗長すぎる可能性がある。`should not` を `do not` に短縮するなど、英語側の最適化でさらに数 % 削減できる余地はある。ただし可読性とのトレードオフ。

### 3. キャッシュヒット率の観測

理論上のトークン削減と、実際のセッションコストは違う。`prompt caching` のヒット率を観測しないと真の効果は測れない。次のセッションで `/cost` の出力を Before/After で比較すると現実値が見える。

## まとめ

| 項目 | 値 |
|---|---|
| 削減トークン | **5,097** |
| 削減率 | **-37.6%** |
| 文字数の代償 | +49.0% |
| CJK 文字削減 | -93.9% |
| tokens/char 効率化 | 2.4 倍 |

**「ハーネスの内側を英語化、外側は日本語維持」というパターンは、トークン換算で約 38% の削減効果がある**ことが実測で裏付けられた。

`prompt caching` が普及した現在、毎セッション読み込まれる規約・スキル定義のような固定資産を英語化するのは、**翻訳プロキシのような大掛かりな仕組みを使わずに「言語税」を払い続ける現実的な解**である。

## 関連記事

- [LLM で日本語を使うと英語の 1.48 倍トークンを消費する「言語税」の実態](/blogs/posts/2026/04/2026-04-30-llm-japanese-token-language-tax/) — 言語税の元データ
- [「言語税」対策として CLAUDE.md を英語化する](/blogs/posts/2026/05/2026-05-13-claude-md-english-prompt-caching/) — 設計方針
- [Claude を「原始人」口調にするとトークンが 80% 減る話](/blogs/posts/2026/04/2026-04-17-claude-caveman-token-reduction/) — 出力側の削減手法
- [ハーネスエンジニアリング](/blogs/wiki/concepts/harness-engineering/)
