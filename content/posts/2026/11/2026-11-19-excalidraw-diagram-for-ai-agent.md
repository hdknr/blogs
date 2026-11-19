---
title: "AI エージェントへの指示は図で渡す：Excalidraw の JSON をプロンプトに変換する方法と落とし穴"
date: 2026-11-19
lastmod: 2026-11-19
slug: "excalidraw-diagram-for-ai-agent"
draft: false
categories: ["AI/LLM"]
tags: ["AIエージェント", "Excalidraw", "プロンプトエンジニアリング", "python", "mcp"]
---

## はじめに

AI エージェントにシステム構成や処理の流れを伝えるとき、文章で「API Gateway が認証サービスに JWT を渡し、検証に成功したら…」と書くより、図を 1 枚描いたほうが早い場面があります。

[Miro の代わりになる OSS ホワイトボード比較](/blogs/posts/2026/11/oss-whiteboard-miro-alternatives/)で紹介した Excalidraw は、図を構造化された JSON として保存します。そのため、画像としてではなく**データとして**エージェントに渡せます。

本記事では、Excalidraw の図をエージェントへの指示に使う方法を整理します。あわせて、JSON を軽いプロンプトに変換するスクリプトを作り、公開されている実際の図で試した結果を紹介します。

結論を先に書くと、次のとおりです。

- 見た目が大事なら画像、つながりが大事なら JSON を渡す
- JSON はそのままだと冗長なので、ノードと接続の一覧に縮める
- ただし実際の図では、矢印やラベルが図形にひも付いていないことが多く、変換で情報が落ちる。描き方のルールを決めておくのが一番効く

## 画像で渡すか、データで渡すか

| 渡し方 | エージェントが受け取るもの | 向いている場面 |
|---|---|---|
| 画像（PNG / SVG） | 見た目。マルチモーダルのモデルが解釈する | 画面のラフ、レイアウト、「この辺をこう変えて」という指示 |
| `.excalidraw`（JSON） | 図形・テキスト・矢印の接続がデータとして読める | 構成図、処理フロー、依存関係 |
| 両方 | 画像で全体像、データで正確なラベルと接続 | 取り違えが許されない指示 |

画像で渡すと、モデルは「この矢印はどの図形につながっているか」「この文字はどの図形のラベルか」を見た目から推測します。図形と矢印が多い図ほど、推測を誤る余地が増えます。JSON で渡せば、つながりは推測ではなくデータとして読めます。

### 画像とデータを 1 ファイルにまとめる（Embed scene）

Excalidraw で PNG や SVG を書き出すとき、「シーンを埋め込む」（Embed scene）オプションを有効にすると、画像の中に元の図のデータが入ります。この画像は Excalidraw で開き直して編集できます。

画像を見られるエージェントには、そのまま見せられます。元データも同じファイルで管理できるので、指示用の図をリポジトリに置く運用と相性がよい方法です。

## Excalidraw の JSON のどこにつながりが入っているか

Excalidraw のソースコード（`packages/element/src/types.ts`）の型定義を見ると、つながりは次のフィールドに入っています。

| 要素 | フィールド | 意味 |
|---|---|---|
| 矢印（`type: "arrow"`） | `startBinding.elementId` / `endBinding.elementId` | 矢印の始点・終点が吸着している図形の ID。吸着していなければ `null` |
| テキスト（`type: "text"`） | `containerId` | テキストが入っている図形（または矢印）の ID。独立したテキストなら `null` |
| すべての要素 | `isDeleted` | 削除済みの要素もファイルに残るので、読むときは除外する |

テキストを入れられる「コンテナ」は、矩形・ひし形・楕円・付箋（`stickynote`）に加えて矢印です。矢印の上のラベルも `containerId` で矢印にひも付きます。

## JSON をプロンプト向けに縮めるスクリプト

`.excalidraw` には座標・色・乱数シードなども含まれていて、そのまま渡すとトークンを大量に消費します。後で試す 1 つ目の図では、元の JSON が約 43KB あるのに対し、図形と接続だけを書き出すと 20 行ほどに収まりました。

次のスクリプトを `excalidraw2md.py` として保存します。Python 3 の標準ライブラリだけで動きます。

```python
"""Convert an .excalidraw scene into a compact Markdown node/edge list for LLM prompts."""
import json
import sys

SHAPES = {"rectangle", "ellipse", "diamond", "stickynote"}


def one_line(text):
    return " ".join(text.split())


def main(path):
    with open(path, encoding="utf-8") as f:
        scene = json.load(f)
    els = {e["id"]: e for e in scene["elements"] if not e.get("isDeleted")}

    # 図形や矢印に入ったテキストを、その要素のラベルにする
    labels, free = {}, []
    for e in els.values():
        if e["type"] != "text":
            continue
        cid = e.get("containerId")
        if cid in els:
            labels[cid] = one_line(e["text"])
        else:
            free.append(e)

    # 救済: 図形の上に置いただけのテキストは、中心点を含む最小の図形のラベルとみなす
    notes = []
    for t in free:
        cx, cy = t["x"] + t["width"] / 2, t["y"] + t["height"] / 2
        hits = [s for s in els.values()
                if s["type"] in SHAPES and s["id"] not in labels
                and s["x"] <= cx <= s["x"] + s["width"]
                and s["y"] <= cy <= s["y"] + s["height"]]
        if hits:
            best = min(hits, key=lambda s: s["width"] * s["height"])
            labels[best["id"]] = one_line(t["text"])
        else:
            notes.append(one_line(t["text"]))

    # 同じラベルの図形が複数あると接続が曖昧になるので、ID の先頭を付ける
    counts = {}
    for v in labels.values():
        counts[v] = counts.get(v, 0) + 1

    def name(eid):
        label = labels.get(eid)
        if label is None:
            return f'({els[eid]["type"]} {eid[:6]})'
        return f"{label} [{eid[:6]}]" if counts[label] > 1 else label

    nodes, edges, loose = [], [], 0
    for eid, e in els.items():
        if e["type"] in SHAPES:
            nodes.append(f"- {name(eid)}")
        elif e["type"] == "arrow":
            s = (e.get("startBinding") or {}).get("elementId")
            t = (e.get("endBinding") or {}).get("elementId")
            if s in els and t in els:
                label = f" : {labels[eid]}" if eid in labels else ""
                edges.append(f"- {name(s)} -> {name(t)}{label}")
            else:
                loose += 1

    print("## ノード", *nodes, sep="\n")
    print("\n## 接続", *edges, sep="\n")
    if notes:
        print("\n## 図形の外のテキスト", *[f"- {n}" for n in notes], sep="\n")
    if loose:
        print(f"\n<!-- 図形に吸着していない矢印: {loose} 本（接続は不明） -->")


if __name__ == "__main__":
    main(sys.argv[1])
```

使い方は、ファイルを渡すだけです。

```bash
python3 excalidraw2md.py architecture.excalidraw > architecture.md
```

## 実際の図で試してわかったこと

GitHub で公開されている `.excalidraw` ファイル 3 つで試しました。

| ファイル | 内容 | 図形 | ラベルが取れた図形 | 接続 | 吸着していない矢印 |
|---|---|---|---|---|---|
| [swiftlysingh/excalidraw-cli](https://github.com/swiftlysingh/excalidraw-cli) の `example.excalidraw` | シミュレーターと 2 つの制御システムの構成図 | 4 | 4 | 8 | 6 |
| [swaymun/system-design-excalidraws](https://github.com/swaymun/system-design-excalidraws) の `newsfeed.excalidraw` | ニュースフィードのシステム設計 | 16 | 5 | 5 | 2 |
| [lizhe2004/Awesome-LLM-RAG-Application](https://github.com/lizhe2004/Awesome-LLM-RAG-Application) の `llm-rag.excalidraw` | RAG の流れ | 6 | 4 | 2 | 0 |

1 つ目の図の出力は次のとおりです（接続 8 本のうち 5 本を抜粋。ラベルの閉じ括弧が欠けているのは元の図のとおりです）。

```markdown
## ノード
- Simulator Engine [Q2nNJZ]
- Simulator Engine [ABczdx]
- Traditional System
- Agentic System

## 接続
- Simulator Engine [Q2nNJZ] -> Agentic System : Job Queue
- Simulator Engine [Q2nNJZ] -> Agentic System : Cooling Sensor Data
- Simulator Engine [Q2nNJZ] -> Agentic System : Rack & Room Sensor Data
- Agentic System -> Simulator Engine [Q2nNJZ] : Chiller Setpoints (Liquid Temps
- Simulator Engine [ABczdx] -> Traditional System : Cooling Sensor Data
...

<!-- 図形に吸着していない矢印: 6 本（接続は不明） -->
```

ラベル付きの矢印がそのまま「何が何に何を渡すか」になっていて、文章で書くよりずっと短く正確です。一方で、試すなかで次の 3 つの問題が見つかりました。

### 1. ラベルが図形にひも付いていない

掲載したスクリプトの「救済」の処理を入れる前は、`containerId` だけでラベルを判定していました。すると 1 つ目の図では、2 つの「Simulator Engine」がどちらも `(rectangle Q2nNJZ)` のような ID 表示になりました。テキストを図形の**中に入れた**のではなく、図形の**上に重ねて置いた**だけだったためです。見た目は同じでも、データ上はひも付いていません。

そこで、テキストの中心点を含む最小の図形をラベルの持ち主とみなす救済処理を足しました。これで 1 つ目の図はすべての図形にラベルが付きました。ただし 2 つ目の図では、データベースを表す楕円の多くがラベルを図形の外（上）に置いていて、救えませんでした。

### 2. 同じラベルの図形がある

1 つ目の図には「Simulator Engine」が 2 つあります。ラベルだけで接続を書き出すと、どちらの Simulator Engine につながる矢印なのか区別できません。スクリプトでは、重複したラベルにだけ ID の先頭 6 文字を付けて区別しています。

### 3. 矢印が図形に吸着していない

1 つ目の図では 14 本中 6 本、2 つ目の図でも 2 本の矢印が、どの図形にも吸着していませんでした。端点が図形の近くにあるだけでは、`startBinding` / `endBinding` は `null` のままです。この接続はデータからは復元できないので、スクリプトは本数だけを報告します。

人が見るための図は、見て読めれば十分です。そのため、この 3 つは自然に起きます。**エージェントに渡す前提の図は、描き方を最初から決めておく**のが一番確実です。

## AI エージェントに渡す図の描き方 6 つのルール

- **矢印は必ず図形に吸着させる。** 端点を図形に重ねると吸着する
- **ラベルは図形の中に書く。** 図形を選んでダブルクリックか Enter で、図形の中にテキストを入れられる。上に重ねたテキストはひも付かない
- **同じ名前の図形を作らない。** 必要なら「API（本番）」「API（検証）」のように区別する
- **矢印にもラベルを付ける。**「何を渡すか」が矢印のラベルに入ると、指示の情報量が大きく増える
- **色や線種の意味は文章で添える。**「赤枠は新規実装」のような約束事は、データだけでは伝わらない
- **フリーハンドは避ける。** 手書きの線は、エージェントにとってはただの座標の列

変換したら、スクリプトの出力の「図形の外のテキスト」と「吸着していない矢印」が空になっているかを確認します。この 2 つが残っていれば、図のどこかでひも付けが漏れています。

## draw.io・Obsidian との比較

| ツール | つながりの表現 | エージェントからの扱いやすさ |
|---|---|---|
| Excalidraw | 矢印の `startBinding` / `endBinding`（吸着したときだけ） | JSON なので読みやすいが、吸着漏れに注意 |
| draw.io | XML のエッジに `source` / `target` 属性 | 接続が属性として明示されるので、厳密なグラフ向き |
| Obsidian の Excalidraw プラグイン | Excalidraw と同じ（ただし図のデータは既定で圧縮） | そのままでは読めない |

Obsidian の [Excalidraw プラグイン](https://github.com/zsviczian/obsidian-excalidraw-plugin)で描いた図をエージェントに読ませるなら、圧縮を解除する設定を使うか、`.excalidraw` として書き出して渡します。

## 逆方向：AI エージェントに Excalidraw の図を描かせる

人が描いた図をエージェントに読ませるのとは逆に、エージェントに図を描かせる方法もあります。

- **Mermaid から変換する。** [mermaid-to-excalidraw](https://github.com/excalidraw/mermaid-to-excalidraw)（MIT）は、Mermaid の記法から Excalidraw の図を作る。エージェントには書きやすい Mermaid を書かせ、人は Excalidraw で清書・修正する、という分担ができる
- **excalidraw 組織の MCP サーバーを使う。** [excalidraw/excalidraw-mcp](https://github.com/excalidraw/excalidraw-mcp) は、プロンプトから Excalidraw の図を生成する MCP サーバー

excalidraw-mcp は、README によればリモートのエンドポイント `https://mcp.excalidraw.com` をカスタムコネクタとして追加すると使えます。MCP Apps に対応したクライアントでは、生成した図を会話の中で表示・編集できます。名前の似たコミュニティ製の MCP サーバーも複数あるので、導入するときはリポジトリを確認してください。

## まとめ

- 構成図や処理フローの指示は、文章より図のほうが早く正確に伝わる場面がある
- Excalidraw の図は JSON なので、矢印の接続（`startBinding` / `endBinding`）とラベル（`containerId`）をデータとして渡せる。Embed scene を使えば、画像とデータを 1 ファイルにまとめられる
- JSON はそのままだと冗長なので、ノードと接続の一覧に縮めて渡す
- 公開されている実際の図で試すと、ラベルが図形にひも付いていない、同じ名前の図形がある、矢印が吸着していない、の 3 つで情報が落ちた
- エージェントに渡す図は、「矢印は吸着させる」「ラベルは図形の中に書く」というルールで描くのが一番確実
- 逆にエージェントに図を描かせるなら、Mermaid からの変換か excalidraw 組織の MCP サーバーが使える

## 参考リンク

- [excalidraw/excalidraw](https://github.com/excalidraw/excalidraw)（要素の型定義: `packages/element/src/types.ts`）
- [excalidraw/mermaid-to-excalidraw](https://github.com/excalidraw/mermaid-to-excalidraw)
- [excalidraw/excalidraw-mcp](https://github.com/excalidraw/excalidraw-mcp)
- [zsviczian/obsidian-excalidraw-plugin](https://github.com/zsviczian/obsidian-excalidraw-plugin)
