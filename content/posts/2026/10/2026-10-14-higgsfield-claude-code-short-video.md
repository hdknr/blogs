---
title: "Claude Code で Higgsfield 用ショート動画シナリオを量産する — CLAUDE.md でプロンプト構文を固定し MCP で生成まで"
date: 2026-10-14
lastmod: 2026-10-14
slug: "higgsfield-claude-code-short-video"
draft: false
source_url: "https://github.com/hdknr/blogs/issues/297#issuecomment-6162214033"
categories: ["AI/LLM"]
tags: ["claude-code", "Higgsfield", "動画生成", "CLAUDE.md", "mcp"]
---

## はじめに

動画生成 AI プラットフォーム **Higgsfield** でショート動画を作るとき、手間がかかるのは生成そのものではありません。「カット割り」と「英文プロンプト」を毎回考える作業です。ここを **Claude Code** に任せると、シナリオ作成からプロンプトの書き出し、さらには生成の実行までをターミナルの中で完結できます。

Claude Code はローカルのファイルを直接作成・編集できるエージェントです。そのため単にチャットでシナリオを返してもらうのではなく、次のようなことまでできます。

- プロンプトの構文や出力フォーマットを `CLAUDE.md` に固定し、毎回同じ形で書かせる
- 1 つのテーマから「シナリオ」「カットごとの説明」「Higgsfield 用英文プロンプト」をまとめてファイルに保存させる
- 保存したシナリオを CSV などに変換するスクリプトも書かせ、後工程（生成・編集）に渡す

この記事では、シナリオ設計をファイルとして管理するワークフローを順に紹介し、最後に Higgsfield MCP で実際の生成につなぐ方法を説明します。

## ワークフローの全体像

作業は大きく 2 段階に分かれます。

| 段階 | やること | 使うもの |
|---|---|---|
| 設計 | テーマ → カット割り → 英文プロンプトをファイルに保存 | `CLAUDE.md`、Claude Code |
| 生成 | 保存したプロンプトで画像・動画を生成 | Higgsfield（Web 版または MCP） |

設計段階を Git リポジトリ上のファイルとして残しておくのがポイントです。プロンプトを差分で見比べられるので、「どの言い回しに変えたら絵が良くなったか」を後から追えます。

## Step 1. CLAUDE.md でルールを固定する

プロジェクトフォルダに `CLAUDE.md` を置き、役割と出力フォーマットを書いておきます。Claude Code はセッション開始時にこのファイルを読み込むので、毎回指示し直す必要がなくなります。

````markdown
# Higgsfield Scenario Generator Rule

## 役割
あなたは Higgsfield 用のショート動画シナリオライターです。

## 出力フォーマット
テーマを受け取ったら、4 カット分を次の形式で `scenarios/<slug>.md` に保存してください。

```text
## Cut <番号> [<開始秒>-<終了秒>s] <役割（フック／展開／変化／CTA など）>
- シーン: <日本語のシーン説明>
- Prompt: <英文プロンプト>
```

## プロンプト構文
英文プロンプトは次の順で書くこと:
Subject, Action, Background, Camera work, Lighting
````

見出しを `## Cut 1 [0-3s]` の形に固定しておくと、後でスクリプトから機械的に読み取れます（Step 4）。

## Step 2. Claude Code にショート動画シナリオを依頼する

ターミナル、または VS Code の Claude Code パネルから、自然言語で依頼します。

> 「朝の時短スキンケア」をテーマに 15 秒のショート動画シナリオを作成して、`scenarios/skincare.md` に保存して。

`CLAUDE.md` のルールがあるので、テーマと保存先を伝えるだけで済みます。権限設定によっては、Claude Code がファイルを書き込む前に確認を求めてくるので、内容を見て許可します。

## Step 3. 出力されたシナリオと Higgsfield 用プロンプトを確認する

Claude Code が指定パスにファイルを書き出します。出力イメージは次のとおりです。

```markdown
# 朝の時短スキンケア（15秒）

## Cut 1 [0-3s] フック
- シーン: 朝、鏡を見て肌の乾燥にショックを受ける女性
- Prompt: A young woman, looking in the mirror with a surprised expression, bright bathroom, close-up shot, soft morning light

## Cut 2 [3-8s] 展開
- シーン: オールインワン美容液を手に取り、さっと塗る
- Prompt: A woman's hand, applying smooth skincare serum to her face, clean bright bathroom, slow-motion close-up, soft glowing light

## Cut 3 [8-12s] 変化
- シーン: うるおった肌で笑顔になる
- Prompt: The same woman, smiling at the mirror with dewy glowing skin, bright bathroom, medium shot with slow dolly in, warm morning sunlight

## Cut 4 [12-15s] CTA
- シーン: 商品ボトルのアップとキャッチコピー
- Prompt: A minimal white serum bottle, standing on a marble counter, clean bathroom shelf, slow orbit camera, soft rim lighting
```

どのプロンプトも `CLAUDE.md` で決めた「Subject, Action, Background, Camera work, Lighting」の順に並んでいます。人が読むときは日本語の「シーン」で流れを確認し、生成に使うのは英文の「Prompt」だけ、という分担です。

## Step 4. Python でシナリオを CSV に変換・検証する

テーマが増えてくると、カット単位の一覧があると便利です。たとえば「`scenarios/` 配下の Markdown を全部読んで、カットごとに 1 行の CSV にするスクリプトを書いて」と頼むと、次のようなスクリプトが得られます（Python 3.8 以降）。`scenario_to_csv.py` として保存します。

```python
import csv
import re
import sys
from pathlib import Path

CUT = re.compile(r"^## Cut (\d+) \[(\d+)-(\d+)s\]\s*(.*)$")
FIELD = re.compile(r"^- (シーン|Prompt): (.+)$")


def parse(path: Path):
    rows, cur = [], None
    for line in path.read_text(encoding="utf-8").splitlines():
        if m := CUT.match(line):
            cur = {"file": path.name, "cut": int(m[1]),
                   "start": int(m[2]), "end": int(m[3]), "label": m[4]}
            rows.append(cur)
        elif cur and (m := FIELD.match(line)):
            cur["scene" if m[1] == "シーン" else "prompt"] = m[2]
    return rows


def main(src_dir: str, out: str):
    rows = [r for p in sorted(Path(src_dir).glob("*.md")) for r in parse(p)]
    missing = [f"{r['file']} Cut {r['cut']}" for r in rows if "prompt" not in r]
    if missing:
        sys.exit("Prompt がないカット: " + ", ".join(missing))
    fields = ["file", "cut", "start", "end", "label", "scene", "prompt"]
    with open(out, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)
    print(f"{len(rows)} cuts -> {out}")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit("usage: scenario_to_csv.py <src_dir> <out.csv>")
    main(sys.argv[1], sys.argv[2])
```

Step 3 のファイルに対して実行した結果です。

```console
$ python3 scenario_to_csv.py scenarios prompts.csv
4 cuts -> prompts.csv
$ head -3 prompts.csv
file,cut,start,end,label,scene,prompt
skincare.md,1,0,3,フック,朝、鏡を見て肌の乾燥にショックを受ける女性,"A young woman, looking in the mirror with a surprised expression, bright bathroom, close-up shot, soft morning light"
skincare.md,2,3,8,展開,オールインワン美容液を手に取り、さっと塗る,"A woman's hand, applying smooth skincare serum to her face, clean bright bathroom, slow-motion close-up, soft glowing light"
```

`Prompt` 行が抜けたカットがあると、CSV を書かずにエラーで止まります。たとえば `skincare.md` の Cut 4 から `- Prompt:` 行を消して実行すると、次のようになります。LLM が出力フォーマットを崩したときに、そのまま後工程へ流れてしまうのを防ぐためのチェックです。

```console
$ python3 scenario_to_csv.py scenarios prompts.csv
Prompt がないカット: skincare.md Cut 4
```

こうして作った CSV は、プロンプトを Higgsfield の Web 版に貼り付けるときの台本にも、動画編集ツールでカットを並べるときの尺の目安にも使えます。

## Step 5. Higgsfield MCP で生成までつなぐ

設計だけでなく生成まで Claude Code から行いたい場合は、Higgsfield の公式 MCP サーバーを追加します。

```bash
claude mcp add --transport http --scope user higgsfield https://mcp.higgsfield.ai/mcp
```

- エンドポイントは末尾が `/mcp` の URL です。`/mcp` を付けずに `https://mcp.higgsfield.ai/` で登録すると接続に失敗する、という報告があります。その場合は `claude mcp remove higgsfield` で消してから登録し直します。
- 認証は OAuth です。API キーは不要で、初回の利用時にブラウザで Higgsfield アカウントにサインインします。
- 接続できたかは `claude mcp list` で確認できます。

登録後は「`prompts.csv` の `skincare.md` Cut 1 のプロンプトで縦長の動画を生成して」のように頼めば、Claude Code が MCP 経由で生成を実行します。設計段階のファイルがそのまま生成の入力になるのが、ファイルで管理しておく利点です。Higgsfield MCP を使った制作フローの具体例は [Claude Code × Higgsfield MCP でCM制作が一撃完結](/blogs/posts/2026/05/claude-code-higgsfield-mcp-cm-production/) でも紹介しています。

なお、API キーで認証する Higgsfield API は MCP とは別の開発者向け製品です。自前のスクリプトから直接呼び出したい場合はこちらを検討します。

## Higgsfield MCP のクレジット消費と注意点

- MCP 経由の生成は**必ずクレジットを消費**します。Higgsfield の公式ヘルプによると、Web 版の無制限プランや無料生成の枠は MCP・CLI などの自動化ツールには適用されず、通常レートでクレジットが引かれます。
- 毎月の無料クレジットの量やプランの内容は情報源によって記述が異なり、変更される可能性もあります。使う前に Higgsfield の公式情報で確認してください。
- エージェントに生成させたコンテンツでも、公開する責任は使う側にあります。人物や商品が登場するシナリオは、生成前に人の目でレビューする工程を挟むのが安全です。
- 一括生成を頼むとクレジットが一気に減ります。まずは 1 カットだけ生成して品質を確かめてから、残りに広げるのがおすすめです。

## まとめ

- `CLAUDE.md` にプロンプト構文と出力フォーマットを固定すると、Claude Code が毎回同じ形でシナリオを書き出す
- シナリオを Markdown ファイルで管理すれば、差分レビューやスクリプトでの変換ができる
- 出力フォーマットを厳密にしておくと、CSV 変換のような後工程を自動化しやすい
- 生成まで行うなら Higgsfield MCP を追加する。ただしクレジットは必ず消費される

Higgsfield MCP 自体の紹介や、動画制作の具体例は以下の記事も参考にしてください。

- [Higgsfield MCP 正式リリース — 1つのコネクタで30以上のAI動画・画像モデルをエージェントから使う](/blogs/posts/2026/04/higgsfield-mcp-official-release/)
- [Claude Code × Higgsfield MCP でCM制作が一撃完結](/blogs/posts/2026/05/claude-code-higgsfield-mcp-cm-production/)
- [Claude Code + 4ツールMCP連携で動画10本量産](/blogs/posts/2026/06/claude-code-4tool-video-mass-production-mcp/)

## 参考

- [Claude Code と Higgsfield の連携（liacsy）](https://liacsy.com/technology/generation-ai/collaboration-between-claude-code-and-higgsfield/)
- [What is Higgsfield MCP?（Higgsfield Help Center）](https://higgsfield.ai/creator-hub/help-center/mcp-cli/what-is-higgsfield-mcp)
