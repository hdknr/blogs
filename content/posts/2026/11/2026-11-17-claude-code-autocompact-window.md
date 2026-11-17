---
title: "Claude Code の /autocompact 設定 — 1M コンテキストの自動圧縮を 400K に早めるコストと品質の得失"
date: 2026-11-17
lastmod: 2026-11-17
slug: "claude-code-autocompact-window"
draft: false
source_url: "https://github.com/hdknr/blogs/issues/694#issuecomment-6935208811"
categories: ["AI/LLM"]
tags: ["claude-code", "コンテキスト圧縮", "Context Rot", "prompt-caching", "コスト削減"]
description: "Claude Code の /autocompact コマンドと autoCompactWindow 設定で、1M コンテキストのモデルが自動圧縮するタイミングを約 967K から 400K などに早める方法を解説。モデルごとの保存、環境変数との優先順位、プロンプトキャッシュを踏まえたコストと品質のトレードオフも整理する。"
---

## はじめに

X で「長いセッションを回すなら必ずやるべき設定」として、Claude Code の自動圧縮（auto-compact）を **400K トークン**で発動させる Tips が紹介されていた（[@ClaudeCode_love の投稿](https://x.com/ClaudeCode_love/status/2121019968481567021)）。要点は次の 3 行だ。

- 今のモデルだけ: `/autocompact 400k`
- 全モデル: `settings.json` に `"autoCompactWindow": 400000`
- 元に戻す: `/autocompact auto`

投稿の主張は「設定しないと Fable 5.2 や Opus 5.5 は約 967K トークンまで要約しない。Claude Code は毎ターン会話全体を送り直すので、400K で畳めば毎ターンの入力が 400K 前後に収まる」というもの。本記事では、この主張を公式ドキュメントと突き合わせながら、設定方法と、早めに圧縮することの得失を整理する。

## 用語の整理

| 用語 | 意味 |
| --- | --- |
| コンテキストウィンドウ | モデルが 1 回のリクエストで読める最大トークン数。Opus 5.5・Fable 5.2 などは Claude Code で 1M が既定 |
| 自動圧縮（auto-compact） | 会話が一定量に達したとき、Claude Code がそれまでの会話を要約して置き換える仕組み |
| auto-compact window | 自動圧縮の基準にするウィンドウの大きさ。これを小さくすると早く圧縮される（以下、本記事では「窓」と呼ぶ） |
| プロンプトキャッシュ | 前回と同じ先頭部分（プレフィックス）を再利用し、入力トークンを安く・速く処理する仕組み |
| Context Rot | コンテキストが長くなるほど、モデルが中の情報を正確に思い出しにくくなる現象 |

## 1M コンテキストの既定の自動圧縮タイミング（約 967K）

公式ドキュメント（[Model configuration](https://code.claude.com/docs/en/model-config)）によると、Fable 系、Sonnet 5 以降、Haiku 5.5、Opus 4.7 以降は Claude Code で **1M のコンテキストウィンドウが既定**で、`[1m]` サフィックスは要らない。そして 1M ウィンドウで動くモデルは、窓が埋まる手前の **約 967K トークン**で自動圧縮される。

つまり投稿の「約 967K まで要約しない」は公式の記述と一致する。1M から引くと約 33K の余白を残す計算になる。以前の記事「[Claude Code のコンテキスト圧縮戦略](/blogs/posts/2026/04/claude-code-context-compression/)」では、ソースコードの解析から 200K の窓で約 167K（同じく約 33K の余白）で発動すると紹介した。余白の大きさそのものは公式ドキュメントに明記されていないが、考え方は同じと見てよさそうだ。

## /autocompact と autoCompactWindow の設定方法

### `/autocompact` コマンド

| コマンド | 動作 |
| --- | --- |
| `/autocompact 400k` | このモデルの窓を 400K にする |
| `/autocompact` | 引数なし: 現在の窓をダイアログで表示 |
| `/autocompact auto` | モデル既定の窓に戻す |

- 指定できる範囲は **100K〜1M トークン**
- `400000`、`400k`、`1M` のほか、100〜1000 の数値だけを書くと千単位と解釈される（`/autocompact 400` は 400,000）
- コマンド一覧のドキュメントでは **v2.1.221 以降**が必要とされている
- **v2.1.288 以降はモデルごとに保存される**。ユーザー設定の `modelSettings.<model>.autoCompactWindow` に書き込まれ、現在のセッションにもすぐ反映される。それ以前のバージョンでは、全モデル共通のトップレベル `autoCompactWindow` に保存されていた

投稿の「`/autocompact` は今のモデルだけ」という説明は、v2.1.288 以降の挙動を指している。

### `settings.json` の `autoCompactWindow`

全モデルに同じ窓を当てたいなら、`~/.claude/settings.json` のトップレベルに書く。単位はトークンで、範囲は同じく 100,000〜1,000,000。

```json
{
  "autoCompactWindow": 400000
}
```

特定のモデルだけ変えたい場合は `modelSettings` の下に書ける（v2.1.288 以降）。同じファイル内では、モデル別の値がトップレベルの値より優先される。

### 環境変数

スクリプトやクラウド環境では、設定ファイルより環境変数のほうが扱いやすい。起動 1 回だけ変えたいときは `--autocompact` 起動フラグもある（優先順位は次節）。

```bash
# 窓をトークン数で指定（k / M サフィックスは v2.1.304 以降）
export CLAUDE_CODE_AUTO_COMPACT_WINDOW=400000
```

注意点として、この環境変数で数値だけを書くと **トークン数**として読まれる。`/autocompact 400` と同じ感覚で `CLAUDE_CODE_AUTO_COMPACT_WINDOW=400` と書くと 400 トークンになり、最小値を下回る。

## auto-compact window 設定の優先順位

複数の場所で指定したときの関係は、一直線の順位ではなく、組み合わせごとに決まっている（[Model configuration](https://code.claude.com/docs/en/model-config) の「Set the auto-compact window」より）。

| 指定方法 | 何より優先されるか | 補足 |
| --- | --- | --- |
| `CLAUDE_CODE_AUTO_COMPACT_WINDOW`（環境変数） | `/autocompact`、`--autocompact` 起動フラグ、`autoCompactWindow` 設定 | スクリプト・クラウド環境向け。設定中は `/autocompact` が保存せずに上書きを報告する |
| `--autocompact` 起動フラグ | 保存済みの設定 | その起動 1 回だけ上書きし、保存値は変えない。`/autocompact` と違い、管理設定のような上位スコープにも上書きされない |
| 管理設定（managed settings） | `/autocompact` で保存した値、`autoCompactWindow` 設定 | 組織が配布する設定。`/autocompact` で保存はできるが、セッションは管理設定の値のまま |
| `/autocompact` で保存したモデル別の値 | トップレベルの `autoCompactWindow` | 普段使いのモデル別設定 |
| トップレベルの `autoCompactWindow` | — | 全モデル共通の既定 |

環境変数と管理設定のどちらが勝つかは、公式ドキュメントには明記されていない。「`settings.json` に書いたのに効かない」というときは、まず環境変数や管理設定で窓が指定されていないかを確認するとよい。

## 自動圧縮に関係する環境変数と設定

| 設定 | 種類 | 内容 |
| --- | --- | --- |
| `CLAUDE_AUTOCOMPACT_PCT_OVERRIDE` | 環境変数 | 窓の何 % で圧縮するか（1〜100）。既定より早める方向にしか効かない |
| `DISABLE_AUTO_COMPACT=1` | 環境変数 | 自動圧縮とアイドル時の圧縮を止める。手動の `/compact` は使える |
| `DISABLE_COMPACT=1` | 環境変数 | 手動の `/compact` も含めてすべての圧縮を止める |
| `CLAUDE_CODE_DISABLE_1M_CONTEXT=1` | 環境変数 | 1M を使わず、200K の窓で動かす |
| `autoCompactEnabled` | settings.json | 自動圧縮のオン・オフを切り替える |

窓を小さくする（`autoCompactWindow`）のと、割合を下げる（`CLAUDE_AUTOCOMPACT_PCT_OVERRIDE`）のは、どちらも「早めに圧縮する」方向の設定だ。トークン数で直感的に決められる `autoCompactWindow` のほうが扱いやすい。

## なぜ早めに圧縮するのか

### 毎ターンの入力コストが減る（400K と 967K の試算）

公式ドキュメント（[Prompt caching](https://code.claude.com/docs/en/prompt-caching)）にあるとおり、Claude Code は毎ターン、システムプロンプト・プロジェクトの文脈・これまでのメッセージとツール結果をすべて送り直す。会話が 90 万トークンあれば、短い質問 1 つでも 90 万トークンの入力になる。

ただしこの大半はプロンプトキャッシュに乗る。[料金表](https://platform.claude.com/docs/en/about-claude/pricing)では、Opus 5.5 の入力は 100 万トークンあたり $4、キャッシュ読み出しは $0.20（入力の 0.05 倍）だ。Opus 5.5 で 1 ターンあたりの入力コストを概算すると次のとおり。

| 会話の長さ | キャッシュなし（$4/MTok） | キャッシュ読み出し（$0.20/MTok） |
| --- | --- | --- |
| 400K | 約 $1.60 / ターン | 約 $0.08 / ターン |
| 967K | 約 $3.87 / ターン | 約 $0.19 / ターン |

キャッシュが効いていても、1 ターンあたりの入力コストは会話の長さにほぼ比例する。上限どうしを比べると 400K は 967K の約 41% なので、長いセッションで何百ターンも回すなら、累計の入力コストは目安として半分程度まで下がりうる（実際の削減幅は、会話が上限に届くまでのターン数の配分で変わる）。

また、キャッシュの有効期限（API キーなら既定 5 分、サブスクリプションプランの利用枠内なら 1 時間）が切れた直後のターンは、キャッシュなしの料金で全文を読み直すことになる。会話が短いほど、この「読み直し」の痛みも小さい。

### 長いコンテキストでの精度低下（Context Rot）を避けられる

Anthropic のエンジニアリングブログ「[Effective context engineering for AI agents](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)」は、コンテキスト内のトークンが増えるほど、モデルが情報を正確に思い出す能力が下がると説明している。程度の差はあれ、この傾向はすべてのモデルに現れ、コンテキストは「限界効用が逓減する有限の資源」として扱うべきだという。

1M 窓が使えることと、1M まで詰め込んでよいことは別の話だ。この点は「[Claude Code のコンテキスト管理術 — Context Rot を防ぐ5つの選択肢](/blogs/posts/2026/04/claude-code-context-rot-session-management/)」でも取り上げた。

なお、「何トークンを超えると品質が落ちる」という公式の閾値は示されていない。**400K という数字は経験則であって、公式の推奨値ではない**ことは押さえておきたい。

## 早めに圧縮するときの注意点

### 要約で細部が落ちる

前述の Anthropic の記事は、圧縮が強すぎると「微妙だが重要な文脈」が失われうるとも書いている。圧縮後に何が残るかは [Context window](https://code.claude.com/docs/en/context-window) のドキュメントにまとまっている。

- **自動で入れ直されるもの**: プロジェクトルートの CLAUDE.md、自動メモリ、スキルの説明、直近に読んだファイル（最大 5 つ）
- **自動では入れ直されないもの**: パス単位のルール、サブディレクトリの CLAUDE.md（必要になったときに読み込み直される）

窓を小さくするほど圧縮の回数が増え、そのたびに要約の質に左右される。

### 圧縮そのものにもコストがかかる

圧縮すると会話部分のキャッシュは無効になる。要約のリクエストは、キャッシュの有効期限内であればプレフィックスをキャッシュから読むが、期限切れなら全文をキャッシュなしで処理し直す。久しぶりに再開したセッションで `/compact` するのが一番高くつくのはこのためだ。

### 手動の `/compact` と組み合わせる

自動圧縮に任せきりにせず、作業の区切りで手動で畳むと、要約の焦点を自分で決められる。

```text
/compact 認証バグの修正方針と、変更したファイルの一覧を中心に残して
```

`/context`（現在のコンテキスト使用量を表示）で状況を確認し、無関係な作業に移るときは `/clear`（会話をリセット）で会話を捨てるのが基本だ。`/autocompact` はその「保険」として、放っておいても会話が膨らみすぎない上限を決める設定と考えるとよい。

## まとめ

- 1M 窓のモデル（Opus 5.5、Fable 5.2 など）は、既定では約 967K トークンまで自動圧縮しない
- `/autocompact 400k` で今のモデルの窓を 400K にできる（v2.1.288 以降はモデルごとに保存）。全モデルに当てるなら `settings.json` の `"autoCompactWindow": 400000`、戻すなら `/autocompact auto`
- 環境変数 `CLAUDE_CODE_AUTO_COMPACT_WINDOW` や管理設定が上位にあると、`/autocompact` や設定ファイルの値は効かない
- 早めに圧縮すると、毎ターンの入力コストと長いコンテキストでの精度低下を抑えられる。代わりに、要約による細部の欠落と、圧縮そのもののコストが増える
- 400K は経験則。作業の性質（大きなコードベースを横断するか、短いタスクを繰り返すか）に合わせて調整し、区切りでは手動の `/compact` や `/clear` を併用したい
