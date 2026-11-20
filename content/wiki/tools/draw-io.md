---
title: "draw.io（diagrams.net）"
description: "構成図・フローチャート向けの Apache-2.0 の作図ツール。mxGraph XML で保存し、デスクトップ版の CLI で PNG に書き出せるため、AI エージェントに図を描かせて自己確認させる用途に向く"
date: 2026-11-19
lastmod: 2026-11-19
aliases: ["diagrams.net", "drawio", "mxGraph", "draw.io CLI"]
related_posts:
  - "/posts/2026/11/oss-whiteboard-miro-alternatives/"
  - "/posts/2026/11/excalidraw-diagram-for-ai-agent/"
  - "/posts/2026/11/excalidraw-to-drawio-converter/"
  - "/posts/2026/03/genai-drawio-creator/"
tags: ["draw.io", "Excalidraw", "AIエージェント", "図解生成", "オープンソース", "ホワイトボード"]
---

## 概要

draw.io（diagrams.net）は構成図・フローチャート・ER 図などを描くための作図ツール。ソースは Apache-2.0 で公開され、Web 版とデスクトップ版がある。付箋を貼るホワイトボードとは方向性が違うが、AWS などのアイコンを含む図形ライブラリの豊富さは群を抜く。このブログの図も draw.io で描いている。

ファイルは mxGraph 形式の XML で、デスクトップ版の CLI で PNG などに書き出せる。この 2 点から、AI エージェントに**描かせる**図の形式として有利というのがブログでの結論。

## 詳細

### ファイル形式（mxGraph XML）

- `<mxfile>` → `<diagram>` → `<mxGraphModel>` → `<root>` の下に `mxCell` が並ぶ。`id="0"` と `id="1"`（`parent="0"`）のセルが土台
- 図形は `vertex="1"` のセル。ラベルは `value`、見た目は `style`（`rounded=0;` `ellipse;` `rhombus;` `sketch=1;` など `;` 区切り）、位置とサイズは `<mxGeometry>`
- 接続線は `edge="1"` のセルで、`source` / `target` 属性に図形の ID を書く。接続点は `exitX` / `exitY`、`entryX` / `entryY`（図形に対する 0〜1 の比率）で指定できる
- `edgeStyle=orthogonalEdgeStyle` などを指定すれば、線の経路は draw.io が自動で引く

接続が属性として明示されるので、厳密なグラフ構造を表すのに向く。テキストなので Git で差分も追える。

### CLI での書き出し

```bash
/Applications/draw.io.app/Contents/MacOS/draw.io --export --format png --scale 2 --output out.png in.drawio
```

macOS の場合のパス。Windows / Linux ではインストール先の実行ファイルに読み替える。このブログでは `static/images/<name>.drawio` を書き、この CLI で PNG にしている。

### AI エージェントに描かせるなら draw.io が有利な理由

| 観点 | draw.io | [Excalidraw](/blogs/wiki/tools/excalidraw/) |
|---|---|---|
| 接続 | 線の `source` / `target` だけ | 矢印側の binding と図形側の `boundElements` の両方 |
| 線の経路 | 自動。接続点も外周に自動で決まる | 点列を座標で全部書く |
| 図形内ラベル | `value` に書く | 別のテキスト要素を `containerId` でつなぐ |
| 記述量 | 少ない | 多い（`seed` / `version` などが要素ごとにある） |
| 描画の確認 | CLI で PNG に書き出してエージェント自身が見て直せる | 公式の CLI レンダラーはない |

差が大きいのは「線の経路」と「描画の確認」。エージェントは図形の位置だけを決めればよく、出力を PNG にして自分で見直すループが回せる。Excalidraw→draw.io 変換の落とし穴（矢印が 1 点に集まる、余計な折り返し、斜線の塗り）も、このループで初めて見つかった。

一方で注意点もある。

- 描画にはデスクトップ版が必要。XML 自体は CI などでも書き直せるが、自己確認の描画はデスクトップ版のある環境で行う
- リアルタイム共同編集には Google Drive や OneDrive などにファイルを置く必要がある。会議中にその場で描く用途は Excalidraw のほうが手軽

### 使い分けの目安

| 図の種類 | ツール |
|---|---|
| エージェントが描く図、リポジトリで保守する図 | draw.io |
| 会議中に人がその場で描くホワイトボード | Excalidraw |
| Excalidraw で描いたが成果物として残す図 | 変換して draw.io へ移す（[Excalidraw](/blogs/wiki/tools/excalidraw/) の変換の節） |

自然言語から draw.io XML を生成する研究としては [GenAI-DrawIO-Creator](/blogs/wiki/tools/draw-io-ai/) がある。

### セルフホスト

公式 Docker イメージで立てられる。

```bash
docker run -it --rm --name="draw" -p 8080:8080 -p 8443:8443 jgraph/drawio
```

`http://localhost:8080/?offline=1` で開く（`?offline=1` はクラウドストレージ連携を無効にする）。ただし [docker-drawio](https://github.com/jgraph/docker-drawio) の README はこのイメージを「評価用のテスト版」としており、本番向けには有償版が案内されている。社内で本格運用する前に確認が必要。

## 関連ページ

- [Excalidraw](/blogs/wiki/tools/excalidraw/) — 手書き風ホワイトボード。draw.io への変換と OSS ホワイトボード比較
- [GenAI-DrawIO-Creator](/blogs/wiki/tools/draw-io-ai/) — 自然言語から draw.io XML を自動生成するフレームワーク
- [AI エージェント](/blogs/wiki/concepts/ai-agent/) — 図を描かせて自己確認させる主体

## ソース記事

- [Excalidraw の図を draw.io に変換する：Python で書いたコンバーターと、AI エージェントに描かせるならどちらか](/blogs/posts/2026/11/excalidraw-to-drawio-converter/) — 2026-11-19
- [AI エージェントへの指示は図で渡す：Excalidraw の JSON をプロンプトに変換する方法と落とし穴](/blogs/posts/2026/11/excalidraw-diagram-for-ai-agent/) — 2026-11-19
- [Miro の代わりになる OSS ホワイトボード比較：Excalidraw は MIT、tldraw は OSS ではない](/blogs/posts/2026/11/oss-whiteboard-miro-alternatives/) — 2026-11-19
- [AWS Japan AI チームが draw.io 図解自動生成を arXiv 論文化——GenAI-DrawIO-Creator の概要](/blogs/posts/2026/03/genai-drawio-creator/) — 2026-03-17
