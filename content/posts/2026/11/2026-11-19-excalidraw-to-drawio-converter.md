---
title: "Excalidraw の図を draw.io に変換する：Python で書いたコンバーターと、AI エージェントに描かせるならどちらか"
date: 2026-11-19
lastmod: 2026-11-19
slug: "excalidraw-to-drawio-converter"
draft: false
categories: ["ツール/開発環境"]
tags: ["Excalidraw", "draw.io", "AIエージェント", "python", "ホワイトボード"]
---

## はじめに

[AI エージェントへの指示は図で渡す](/blogs/posts/2026/11/excalidraw-diagram-for-ai-agent/)では、Excalidraw の図を JSON のままエージェントに読ませる方法を紹介しました。今回はその続きです。Excalidraw の `.excalidraw` ファイルを draw.io の XML（mxGraph 形式）に変換するスクリプトを Python で書き、実際の図で試しました。

結論を先に書きます。

- 図形・ラベル・矢印でできた構成図やフロー図なら、変換は 150 行足らずの Python で書ける。矢印のつながりも draw.io の接続線（`source` / `target`）として引き継げる
- ただし Excalidraw の `fixedPoint` をそのまま draw.io の接続点に使うと、矢印が 1 点に集まる。実際の矢印の端点から接続点を計算し直す必要があった
- AI エージェントに**描かせる**なら draw.io のほうが有利
- draw.io が入っている環境では、エージェントが扱う図は draw.io に統一し、Excalidraw は人がその場で描くホワイトボードに使う、という分け方が現実的

## なぜ変換するのか

Excalidraw と draw.io は得意分野が違います。

| | Excalidraw | draw.io |
|---|---|---|
| 得意なこと | 手書き風のラフ、リアルタイムの共同編集、会議中のホワイトボード | 整った構成図、AWS などのアイコン、長く保守する図 |
| ファイル形式 | JSON | XML（mxGraph） |
| 描画の CLI | 公式のものはない | デスクトップ版に `--export` がある |

人が Excalidraw でラフを描き、残す図は draw.io で清書・保守したい。あるいはエージェントに扱わせたい。そのとき、描き直さずに移せると便利です。

draw.io 本体には Excalidraw の読み込み機能がありません。draw.io のソースを検索した範囲でも、Excalidraw のファイルを読む処理は見当たりませんでした。既存のツールとしては [sindrel/excalidraw-converter](https://github.com/sindrel/excalidraw-converter)（MIT、Go 製）があります。ただしこれは Gliffy 形式に変換して、それを draw.io で読み込む仕組みです。draw.io の XML を直接作りたかったので、自分で書くことにしました。

## Excalidraw と draw.io の要素の対応表

Excalidraw の要素と draw.io のセルは、次のように対応づけました。

| Excalidraw | draw.io | 試作での扱い |
|---|---|---|
| `rectangle` / `ellipse` / `diamond` / `stickynote` | `vertex` の `mxCell`。スタイルは `rounded=0;` / `ellipse;` / `rhombus;` | 対応。座標とサイズはそのまま使える |
| `containerId` を持つテキスト | 図形や線の `value`（ラベル） | 対応 |
| 独立したテキスト | `text;` スタイルの `vertex` | 対応 |
| `arrow` の `startBinding` / `endBinding` | `edge` の `source` / `target` 属性 | 対応 |
| `line`（矢印のない線） | `endArrow=none` の `edge` | 対応 |
| 矢印の `points`（始点からの相対座標） | `<Array as="points">`（絶対座標） | 対応 |
| `strokeColor` / `backgroundColor` / `strokeStyle` / `angle`（ラジアン） | `strokeColor` / `fillColor` / `dashed` / `rotation`（度） | 対応 |
| `roughness`（手書き風） | `sketch=1` | 対応。見た目は近いが同一ではない |
| `frame` | 点線の枠と名前のラベル | 対応。親子関係は持たせていない |
| `image`（`files` に dataURL） | `shape=image;image=...` | 対応 |
| `freedraw` | 曲線の折れ線 | 近似 |
| グループ（`groupIds`） | draw.io のグループ | 未対応 |
| フォント（手書き風の Virgil など） | 同じフォントはない | 未対応 |

## 変換スクリプト

次のスクリプトを `excalidraw2drawio.py` として保存します。Python 3 の標準ライブラリだけで動きます。

```python
"""Convert an .excalidraw scene into a draw.io (mxGraph XML) file."""
import json
import math
import sys
from xml.sax.saxutils import escape, quoteattr

SHAPE_STYLE = {
    "rectangle": "rounded=0;",
    "stickynote": "rounded=0;",
    "ellipse": "ellipse;",
    "diamond": "rhombus;",
}


def base_style(e):
    """すべての要素に共通する色・線・手書き風の指定"""
    # Excalidraw は折り返し済みのテキストを改行付きで持つので、draw.io では折り返さない
    s = "html=1;"
    if e.get("roughness", 0) > 0:
        s += "sketch=1;curveFitting=1;jiggle=2;"
    s += f"strokeColor={e.get('strokeColor') or '#1e1e1e'};"
    fill = e.get("backgroundColor") or "transparent"
    if fill == "transparent":
        s += "fillColor=none;"
    else:
        s += f"fillColor={fill};"
        # sketch=1 は塗りが既定で斜線になるので、solid も明示する
        s += f"fillStyle={e.get('fillStyle') or 'solid'};"
    if e.get("strokeStyle") == "dashed":
        s += "dashed=1;"
    elif e.get("strokeStyle") == "dotted":
        s += "dashed=1;dashPattern=1 4;"
    if e.get("angle"):
        s += f"rotation={math.degrees(e['angle']):.1f};"
    return s


def geometry(e):
    return (f'<mxGeometry x="{e["x"]}" y="{e["y"]}" width="{e["width"]}" '
            f'height="{e["height"]}" as="geometry"/>')


def html(text):
    return escape(text).replace("\n", "<br>")


def vertex(cid, value, style, e):
    return (f'<mxCell id={quoteattr(cid)} value={quoteattr(value)} '
            f'style={quoteattr(style)} vertex="1" parent="1">{geometry(e)}</mxCell>')


def main(path):
    with open(path, encoding="utf-8") as f:
        scene = json.load(f)
    files = scene.get("files", {})
    els = [e for e in scene["elements"] if not e.get("isDeleted")]
    by_id = {e["id"]: e for e in els}

    # 図形や矢印に入ったテキストは、そのセルのラベルにする
    bound = {e["containerId"]: e for e in els
             if e["type"] == "text" and e.get("containerId") in by_id}

    def label(eid):
        t = bound.get(eid)
        return (html(t["text"]), f"fontSize={t.get('fontSize', 20)};") if t else ("", "")

    cells = []
    for e in els:
        cid = "x" + e["id"]
        t = e["type"]

        if t in SHAPE_STYLE:
            value, font = label(e["id"])
            cells.append(vertex(cid, value, SHAPE_STYLE[t] + base_style(e) + font, e))

        elif t == "frame":
            style = ("rounded=0;dashed=1;fillColor=none;strokeColor=#bbbbbb;"
                     "align=left;verticalAlign=top;spacingLeft=4;html=1;")
            cells.append(vertex(cid, html(e.get("name") or "Frame"), style, e))

        elif t == "text" and e.get("containerId") not in by_id:
            style = ("text;html=1;align=left;verticalAlign=top;"
                     f"fontSize={e.get('fontSize', 20)};"
                     f"fontColor={e.get('strokeColor') or '#1e1e1e'};")
            cells.append(vertex(cid, html(e["text"]), style, e))

        elif t == "image" and e.get("fileId") in files:
            # draw.io のスタイルは ';' 区切りなので、';base64' を取り除く
            data = files[e["fileId"]]["dataURL"].replace(";base64", "")
            cells.append(vertex(cid, "", f"shape=image;imageAspect=0;image={data};", e))

        elif t in ("arrow", "line", "freedraw"):
            pts = [(e["x"] + px, e["y"] + py) for px, py in e["points"]]
            style = base_style(e).replace("fillColor=none;", "")
            style += "edgeStyle=none;curved=1;" if t == "freedraw" else "edgeStyle=none;"
            style += ("endArrow=classic;" if t == "arrow" and e.get("endArrowhead")
                      else "endArrow=none;")
            if t == "arrow" and e.get("startArrowhead"):
                style += "startArrow=classic;"

            attrs = ""
            for end, key, prefix, (px, py) in (("source", "startBinding", "exit", pts[0]),
                                               ("target", "endBinding", "entry", pts[-1])):
                b = e.get(key) or {}
                s = by_id.get(b.get("elementId"))
                if s is None:
                    continue
                attrs += f' {end}={quoteattr("x" + s["id"])}'
                # fixedPoint は向きの目安で接点ではないので、矢印の実際の端点から
                # 接続点（図形の外接矩形に対する 0〜1 の比率）を求める
                rx = min(max((px - s["x"]) / s["width"], 0), 1) if s["width"] else 0.5
                ry = min(max((py - s["y"]) / s["height"], 0), 1) if s["height"] else 0.5
                style += f"{prefix}X={rx:.3f};{prefix}Y={ry:.3f};"

            value, font = label(e["id"])
            style += font
            mid = "".join(f'<mxPoint x="{x}" y="{y}"/>' for x, y in pts[1:-1])
            cells.append(
                f'<mxCell id={quoteattr(cid)} value={quoteattr(value)} '
                f'style={quoteattr(style)} edge="1" parent="1"{attrs}>'
                '<mxGeometry relative="1" as="geometry">'
                f'<mxPoint x="{pts[0][0]}" y="{pts[0][1]}" as="sourcePoint"/>'
                f'<mxPoint x="{pts[-1][0]}" y="{pts[-1][1]}" as="targetPoint"/>'
                + (f'<Array as="points">{mid}</Array>' if mid else "")
                + '</mxGeometry></mxCell>')

    print('<mxfile><diagram name="Page-1"><mxGraphModel><root>'
          '<mxCell id="0"/><mxCell id="1" parent="0"/>'
          + "".join(cells)
          + '</root></mxGraphModel></diagram></mxfile>')


if __name__ == "__main__":
    main(sys.argv[1])
```

変換して、draw.io のデスクトップ版で PNG に書き出すまでの手順は次のとおりです（macOS の場合。Windows や Linux では、インストール先の draw.io の実行ファイルに読み替えてください）。

```bash
python3 excalidraw2drawio.py diagram.excalidraw > diagram.drawio
/Applications/draw.io.app/Contents/MacOS/draw.io \
  --export --format png --scale 2 \
  --output diagram.png diagram.drawio
```

## 実際の図で試した結果

[前回の記事](/blogs/posts/2026/11/excalidraw-diagram-for-ai-agent/)と同じく、GitHub で公開されている `.excalidraw` 3 つと、フレームと画像を確かめるために自作した小さな図で試しました。

次の図は、[swiftlysingh/excalidraw-cli](https://github.com/swiftlysingh/excalidraw-cli)（MIT）の `example.excalidraw` を変換し、draw.io で描画したものです。

![Excalidraw の構成図を draw.io に変換して描画した結果。左に Traditional System、右に Agentic System のひし形があり、それぞれ下の Simulator Engine の矩形と、Cooling Sensor Data などのラベル付き矢印でつながっている。線は手書き風で、上部の破線矢印にも Workload Forecast などのラベルが付いている](/blogs/images/excalidraw-to-drawio-converter-example.png)

ひし形と矩形、図形の中のラベル、矢印のラベル、破線、手書き風の線が再現できています。図形に吸着していた矢印は draw.io でも接続線になっているので、draw.io 上で図形を動かすと矢印もついてきます。

残りの 2 つ（ニュースフィードのシステム設計図と RAG の流れ図）も draw.io で開いて描画できました。どちらもライセンスの表記がないリポジトリの図なので、画像は載せていません。後で紹介する落とし穴のうち、テキストの折り返しは RAG の図で見つかったものです。

フレームと画像、塗りつぶしは、自作の小さな図で確かめました。

![自作の Excalidraw の図を draw.io に変換した結果。Backend という名前の点線のフレームの中に、水色で塗りつぶした API の矩形と緑の画像があり、矩形から画像へ手書き風の矢印が伸びている](/blogs/images/excalidraw-to-drawio-converter-frame.png)

## 試してわかった 3 つの落とし穴

変換した XML が draw.io で開けることと、元の図と同じに見えることは別です。次の 3 つは、どれも変換結果を draw.io で PNG に書き出し、目で確かめて初めて見つかりました。

### 1. 矢印が 1 点に集まる：`fixedPoint` は接点ではない

Excalidraw の新しい形式では、吸着した矢印の `startBinding` / `endBinding` に `fixedPoint` という 2 つの数値が入っています。型定義のコメントには「図形の幅と高さに対する比率（0.0〜1.0）」とあり、draw.io の接続点（`exitX` / `exitY`、`entryX` / `entryY`）と同じ考え方に見えます。

ところが、これをそのまま draw.io の接続点に使うと、ひし形に向かう矢印の先端が 1 点に集まってしまいました。値を確かめると、`[0.5001, 0.049]` や `[0.549, 0.5001]` のように片方の軸が `0.5001` になっているものが多く、`[1.126, 0.5001]` や `[-0.027, 0.930]` のように 0〜1 の範囲を外れる値もありました。使った図の矢印はすべて、矢印を図形の外側に沿わせる「orbit」モードで吸着しています。このモードでの `fixedPoint` は、矢印が実際に図形に触れる点とは一致しないようです。

そこで、矢印の実際の端点の座標から、図形の外接矩形に対する比率を計算し直して接続点にしました。draw.io はその点を図形の外周に投影するので、矢印が 1 点に集まる状態は解消しました。ただし、ひし形の辺の上で矢印の先端が近い位置に並ぶなど、元の図と完全に同じ位置にはなりません。

### 2. テキストが折り返される

Excalidraw のテキストは、折り返した結果を改行文字つきで保存しています。draw.io 側で `whiteSpace=wrap` を指定すると、フォントの幅の違いでさらに折り返されました。たとえば RAG の図では、中国語のラベル「问题」が「问」と「题」の 2 行に分かれました。draw.io では折り返さない指定にして、改行は Excalidraw のものだけを使うようにしています。

### 3. 塗りつぶしが斜線になる

手書き風を再現するために draw.io の `sketch=1` を指定したところ、`fillStyle` を指定していない図形の塗りつぶしが斜線（hachure）で描画されました。Excalidraw でベタ塗り（solid）にした図形も斜線になってしまうので、`fillStyle=solid` を明示しています。

## 残る制約

- **矢印ラベルの位置**: draw.io は線の中央付近にラベルを置くので、Excalidraw で動かしたラベルの位置は再現されない
- **グループ**: `groupIds` は変換していない。draw.io 上で図形がばらばらに動く
- **フォント**: 手書き風のフォント（Virgil など）は draw.io の標準フォントで描画される
- **フレームの親子関係**: フレームは枠として描くだけで、中の図形をフレームの子にはしていない
- **吸着していない矢印**: 接続線ではなく、座標だけを持つ線になる

## AI エージェントに描かせるなら、draw.io と Excalidraw のどちらか

変換を書いてみると、2 つの形式がエージェントにとってどれだけ書きやすいかの違いもよく見えます。

| 観点 | draw.io（mxGraph XML） | Excalidraw（JSON） |
|---|---|---|
| 接続の書き方 | 線の `source` / `target` に図形の ID を書く | 矢印の `startBinding` / `endBinding` と、図形の `boundElements` の両方に書く |
| 線の経路 | `edgeStyle=orthogonalEdgeStyle` などで自動で引かれる。接続点も外周に自動で決まる | 矢印の点列を座標で全部書く |
| 図形内のラベル | 図形の `value` に書く | 別のテキスト要素を作り、`containerId` でつなぐ。テキストの幅と高さも必要 |
| 記述量 | 少ない | 多い（`seed` や `version` などの管理用フィールドが要素ごとにある） |
| 部品 | AWS などのアイコンをスタイル名で呼び出せる | 基本図形が中心 |
| 描画の確認 | デスクトップ版の CLI で PNG に書き出し、エージェントが自分で見て直せる | 公式の CLI レンダラーはない |
| 描かせるための道具 | 特になし（XML を直接書く） | excalidraw 組織の MCP サーバー [excalidraw-mcp](https://github.com/excalidraw/excalidraw-mcp)、[mermaid-to-excalidraw](https://github.com/excalidraw/mermaid-to-excalidraw) |

Excalidraw の接続について補足すると、読み込み処理（`restore.ts` の `restoreElements`）には、`repairBindings` オプションを付けたときに働く修復処理があります。たとえばテキストの `containerId` から、図形側の `boundElements` に足りない登録を補います。ただしすべての不整合を直すわけではないので、エージェントが直接書くなら両側を揃えておくのが安全です。

差が大きいのは「線の経路」と「描画の確認」です。draw.io では、エージェントが決めるのは図形の位置だけで、線は draw.io が引きます。さらに CLI で PNG にできるので、エージェントが自分の出力を見て直すループが回せます。本記事の 3 つの落とし穴も、まさにこのループで見つかりました。

Excalidraw にも、npm パッケージに簡略形式から要素を組み立てる API（`convertToExcalidrawElements`、[Element Skeleton API](https://docs.excalidraw.com/docs/@excalidraw/excalidraw/api/excalidraw-element-skeleton)）があります。ラベルを `label` で、接続先を `start` / `end` の ID で書けば、図形のサイズや吸着を計算してくれます。ただしドキュメント上はベータ版で、使うには JavaScript の実行環境が要ります。

## draw.io が入っている環境なら draw.io に統一する

以上を踏まえると、draw.io のデスクトップ版が入っている環境では、次のように分けるのが現実的です。

| 図の種類 | 使うツール | 理由 |
|---|---|---|
| エージェントが描く図、リポジトリで保守する図 | draw.io | 書きやすく、CLI で描画して自己確認できる。差分も XML のテキストとして追える |
| 人が会議中にその場で描くホワイトボード | Excalidraw | 手書き風の描きやすさと、リアルタイムの共同編集 |
| Excalidraw で描いたが、成果物として残す図 | 変換して draw.io へ移す | 本記事のスクリプトで、図形・ラベル・接続を引き継げる |

注意点が 2 つあります。

- **描画には draw.io のデスクトップ版が要る**: XML 自体はテキストなので、draw.io がない環境（CI など）でもエージェントは書いたり直したりできる。ただし自己確認のための描画は、デスクトップ版がある環境で行う必要がある
- **共同編集は Excalidraw のほうが手軽**: draw.io でリアルタイムに同時編集するには、Google Drive や OneDrive などにファイルを置く必要がある。人が集まってその場で描く用途まで draw.io に寄せる必要はない

このブログでも図は draw.io で描き、エージェントが XML を書いて CLI で PNG にし、それを見て直す運用にしています。

## まとめ

- Excalidraw の図は、150 行足らずの Python で draw.io の XML に変換できる。図形・ラベル・矢印のつながりは引き継げる
- `fixedPoint` は接点ではないので、矢印の実際の端点から接続点を計算し直す。テキストは折り返さず、`sketch=1` の塗りは `solid` を明示する
- どの不具合も、変換結果を draw.io で描画して目で確かめて初めて見つかった
- AI エージェントに描かせるなら、線を自動で引け、CLI で描画を確かめられる draw.io が有利
- draw.io が入っている環境では、エージェントが扱う図は draw.io に統一し、Excalidraw は人がその場で描くホワイトボードとして使い分けるのが現実的

## 参考リンク

- [excalidraw/excalidraw](https://github.com/excalidraw/excalidraw)（要素の型定義: `packages/element/src/types.ts`、読み込み時の修復: `packages/excalidraw/data/restore.ts`）
- [Excalidraw Element Skeleton API](https://docs.excalidraw.com/docs/@excalidraw/excalidraw/api/excalidraw-element-skeleton)
- [jgraph/drawio](https://github.com/jgraph/drawio)
- [sindrel/excalidraw-converter](https://github.com/sindrel/excalidraw-converter)
- [swiftlysingh/excalidraw-cli](https://github.com/swiftlysingh/excalidraw-cli)（検証に使った `example.excalidraw`）
