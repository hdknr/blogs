---
title: "Claude Code の Code Mode を試す — ツール呼び出しを JavaScript で束ねる実験的機能の使いどころと起動のコツ"
date: 2026-11-17
lastmod: 2026-11-17
slug: "claude-code-code-mode"
draft: false
source_url: "https://github.com/hdknr/blogs/issues/694#issuecomment-6943911039"
categories: ["AI/LLM"]
tags: ["claude-code", "agent", "javascript", "トークン削減", "hooks"]
---

## はじめに

Claude Code に、ひっそりと **Code Mode** という実験的機能が追加されました。Oikon さんの [X への投稿](https://x.com/oikon48/status/2122346788665618672)（以下「投稿」）で知った方も多いと思います。

普段の Claude Code は、Bash・Read・Edit といったツールを **1 回に 1 つずつ** 呼び出し、結果を読んでから次の手を考えます。Code Mode を有効にすると、Claude は複数のツール呼び出しを **JavaScript のプログラムとして書きます**。そして、それを **1 ステップでまとめて実行** します。

この記事では、公式ドキュメントと投稿をもとに、Code Mode の仕組み、向いているタスク、有効化の手順、起動できないときの回避策、権限まわりの挙動と制約をまとめます。要点だけ先に書くと、有効化は `CLAUDE_CODE_EXPERIMENTAL_CODE_MODE=1`（v2.1.323 以降）で、起動しないときは `--setting-sources project,local` で切り分けられます。

## 用語の整理

| 用語 | 意味 |
|---|---|
| Code Mode | Claude Code の実験的機能。Claude がツール呼び出しを JavaScript で書いてまとめて実行する。既定ではオフ |
| `REPL` | Code Mode で Claude が書いたコードを実行するツールの名前。フックや権限ルールで指定するときに使う |
| `CLAUDE_CODE_EXPERIMENTAL_CODE_MODE` | Code Mode を有効（`1`）／無効（`0`）にする環境変数 |
| Cloudflare の Code Mode | MCP のツールを TypeScript の API に変換し、LLM にその API を呼ぶコードを書かせる手法。同じ発想の先行例 |

### 背景: 「ツールを呼ぶ代わりにコードを書かせる」発想

この考え方自体は新しいものではありません。Cloudflare が「[Code Mode: the better way to use MCP](https://blog.cloudflare.com/code-mode/)」で MCP 向けに提案しており、投稿によれば Pi エージェントなども先駆けとして取り入れていたとのことです。筆者は、Claude Code の Code Mode をこの発想を Bash や Edit などの組み込みツールにまで広げたものと捉えています（公式ドキュメントがそう位置づけているわけではありません）。

## Code Mode の仕組み

通常モードと Code Mode の処理の流れを比べると、次のようになります。

![通常モードでは Claude が Bash・Read・Edit・Bash を 1 つずつ呼び出し、そのたびに全出力が文脈に戻ってくるため往復が 4 回発生する。Code Mode では Claude が JavaScript を 1 回 REPL ツールに送り、シェル実行・結果の加工・編集・テストをコード内で連続して行い、必要な部分だけを Claude に返す様子を比較した図](/blogs/images/claude-code-code-mode-flow.png)

公式ドキュメントに載っている例を見ると、イメージがつかみやすいと思います。

```javascript
const files = await $`rg -l "function retryPolicy" src`.text();
const target = files.trim().split("\n")[0];
await edit(target, "maxAttempts: 3", "maxAttempts: 5");
({ edited: target, tests: $`npm test -- retryPolicy`.nothrow() });
```

`$` でシェルコマンドを実行し、その結果をもとに `edit()` でファイルを書き換え、最後にテストを走らせています。最終行では、編集したファイル名とテスト結果だけをまとめています。図の例のように通常モードなら 4 往復ほどかかる処理が、1 回のコード実行で済みます（往復数は筆者の想定で、公式の数字ではありません）。

画面上では、コードそのものではなく個々のツール呼び出し（編集の差分など）が表示されます。コードを確認したいときは `Ctrl+O` でトランスクリプトビューアーを開くと、各スクリプトが折りたたまれた **Code** 行として表示されます。

## Code Mode のメリットと使いどころ

投稿で挙げられていたメリットは次の 4 点です。

- **複数のツールを並列に実行できる** — 独立したコマンドを同時に走らせられる
- **中間出力を LLM がすべて読まなくてよい** — コードの中で必要な部分だけ取り出して返せるため、コンテキストを節約できる
- **ループや条件分岐を JavaScript で書ける** — 「全ファイルに同じ変更を当てる」といった処理をモデルの推論なしに回せる
- **データの加工やサービスをまたいだ受け渡しができる** — ある処理の結果を整形して次の処理に渡せる

公式ドキュメントでも、多数のファイルにまたがる同じ変更、読む前に絞り込みたい検索結果、同時に走らせられる独立したコマンド群が使いどころとして挙げられています。

### 向いているタスク

投稿者の所感では、**並列にできるステップが多いタスクほど効果が大きく、逐次的な作業ではあまり差が出ない** とのことです。具体的に便利だったケースとして、次のものが挙げられていました。

- バージョン間でのベンチマーク比較
- 大きな出力ファイルから差分だけを抽出する
- 前処理の結果を次の処理に引き継ぐ
- 複数のリポジトリやファイルを横断した調査

### 向いていないタスク

投稿では、**判断が必要で JavaScript のスクリプトに落とし込みにくいタスク** は不向きとされています。筆者の補足ですが、途中の結果を見て方針を変えるような作業は、従来どおり 1 ツールずつ進めたほうが Claude の判断を挟めるはずです。

## Code Mode の有効化手順（環境変数と settings.json）

### 1. バージョンを確認する

Code Mode には **Claude Code v2.1.323 以降** が必要です。

```bash
# 現在のバージョンを確認
claude --version
# v2.1.323 未満なら更新
claude update
```

### 2. 環境変数を設定する

`CLAUDE_CODE_EXPERIMENTAL_CODE_MODE` を `1` にして起動します。

```bash
CLAUDE_CODE_EXPERIMENTAL_CODE_MODE=1 claude
```

毎回有効にしたい場合は、ユーザー設定 `~/.claude/settings.json` の `env` に書きます。

```json
{
  "env": {
    "CLAUDE_CODE_EXPERIMENTAL_CODE_MODE": "1"
  }
}
```

なお、**プロジェクト設定やローカル設定（`.claude/settings.json`・`.claude/settings.local.json`）に書いたこの変数は無視されます**。クローンしたリポジトリが勝手に Code Mode を有効にできないようにするためです。

### 3. 初回の確認に答える

初めて Code Mode で起動すると確認が表示されるので、**Yes, turn on Code Mode** を選びます。再起動後、次のメッセージが出れば有効になっています。

```text
Code Mode (experimental) is on · this session can be resumed only with Code Mode on
```

無効にするには、変数を削除するか `0` を設定します。組織の管理設定（managed settings）で `0` を設定すれば、組織全体で Code Mode を禁止することもできます。

### 4. 試してみる

まず試すなら、公式ドキュメントが例に挙げている次のプロンプトがちょうどよい題材です（「このプロジェクトのすべての Markdown ファイルを読み、存在しないローカルファイルを指すリンクを一覧にして」という意味で、日本語で指示しても構いません）。

```text
Read every Markdown file in this project and list the links that point to local files that don't exist.
```

全 Markdown ファイルを読み、リンク先の存在を確かめる処理は、ループとフィルターで書ける典型的な「束ねると速い」タスクです。

## Code Mode が起動しないときの回避策（--setting-sources）

投稿者がつまずいたのがここで、**Code Mode は他の機能と競合して起動しにくい** とのことです。公式ドキュメントでも、次のような条件では Code Mode なしで起動すると明記されています（一部抜粋）。

- エージェントチーム（`CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS`）を有効にしていて、バージョンが v2.1.326 未満
- ツール呼び出しをチェックするプラグインや mod（Claude Code の画面や挙動をカスタマイズする拡張）が有効
- API キーヘルパー、OpenTelemetry のエクスポート、`DISABLE_TELEMETRY` などの設定
- Amazon Bedrock やゲートウェイ経由など、サードパーティのプロバイダーを使っている

有効にならなかった場合は、起動時に次の行と理由が表示されます。`/status` でも確認できます。

```text
Code Mode (experimental) isn't available
```

投稿者は、**読み込む設定ファイルを絞る** ことでこれを回避していました。

```bash
CLAUDE_CODE_EXPERIMENTAL_CODE_MODE=1 claude --setting-sources project,local
```

`--setting-sources project,local` を付けると、ユーザー設定（`~/.claude/settings.json`）が読み込まれなくなります。競合の原因になる設定がユーザー設定側にあるなら、これで一時的に外せるというわけです（どこに書かれているかは環境によるので、まずは `/status` で理由を確かめてください）。

なお、前述のとおりプロジェクト設定やローカル設定ではこの変数が無視されます。そのため、環境変数はこの例のようにシェルから渡してください。

## Code Mode での権限ルールと PreToolUse フック

Code Mode でも安全装置は残っています。

- コード内の各ツール呼び出しは、`Bash` などの **通常のツール名で** `deny`・`ask` の権限ルールや `PreToolUse` フックを通る
- **auto モード** では、分類器が個々のツール呼び出しではなく **コード全体を実行前に** 審査する
  - ただし実行時に決まる値（検索結果から取ったパスなど）は分類器から見えない。確実に制御したい呼び出しには、ルールやフックを残しておくのがよい
- それ以外の権限モードでは、コードは審査なしで実行が始まる。そのモードで本来確認を求めるツール呼び出しに達するたびに、個別に確認が表示される
- コードそのものを検査したい場合は、`REPL` にマッチする `PreToolUse` フックを書き、`tool_input.code` から JavaScript を読む

## Code Mode の制約（-p・VS Code・Bedrock では使えない）

実験的機能なので、制約も多めです。

- 対話的に起動したターミナルの `claude` セッションのみ。`-p`、Agent SDK、VS Code、デスクトップアプリ、クラウドセッションでは使えない
- Code Mode で始めたセッションを再開（`--continue` / `--resume`）するときも、変数を `1` にしておく必要がある
- 既定ではコードの完了を最大 10 分待つ。auto モードや `bypassPermissions` モードで始めたセッションなら、コードをバックグラウンドで最大 2 時間走らせながら会話を続けられる
- Remote Control、Claude in Chrome、computer use は使えない
- 対応モデルや契約形態にも条件がある（前述のサードパーティのプロバイダー経由や、ゼロデータ保持の組織では不可）
- 公式ドキュメントにも「どのリリースでも変更・削除される可能性がある」と書かれている

## まとめ

- Code Mode は、Claude がツール呼び出しを JavaScript で束ねて 1 ステップで実行する Claude Code の実験的機能
- 並列化できる処理や、大量の中間出力を絞り込みたい処理で効果が大きい。判断を挟みながら進める逐次的な作業には向かない
- `CLAUDE_CODE_EXPERIMENTAL_CODE_MODE=1` で有効化。プロジェクト設定やローカル設定からは有効にできない
- 他の機能と競合して起動しないときは、`--setting-sources project,local` でユーザー設定を外すと切り分けやすい
- コード内のツール呼び出しも通常の権限ルールとフックを通るため、既存の安全装置はそのまま効く

ベンチマークの比較や大規模な横断調査など、「ツールを何十回も呼ぶ」作業が多い方は一度試してみる価値があります。

## 参考

- [Oikon さんの投稿（X）](https://x.com/oikon48/status/2122346788665618672)
- [Code Mode — Claude Code Docs](https://code.claude.com/docs/en/code-mode)
- [Code Mode: the better way to use MCP — Cloudflare Blog](https://blog.cloudflare.com/code-mode/)
