---
title: "Excalidraw"
description: "手書き風の図を描ける MIT ライセンスの OSS ホワイトボード。図を JSON で保存するため AI エージェントへの指示に使え、draw.io への変換もできる。Miro 代替 OSS の比較も収録"
date: 2026-11-19
lastmod: 2026-11-19
aliases: ["エクスカリドロー", ".excalidraw", "Miro 代替", "OSS ホワイトボード", "excalidraw-mcp"]
related_posts:
  - "/posts/2026/11/oss-whiteboard-miro-alternatives/"
  - "/posts/2026/11/excalidraw-diagram-for-ai-agent/"
  - "/posts/2026/11/excalidraw-to-drawio-converter/"
tags: ["Excalidraw", "ホワイトボード", "draw.io", "AIエージェント", "mcp", "オープンソース", "ライセンス"]
---

## 概要

Excalidraw は手書き風のタッチで図を描ける無限キャンバスのホワイトボード。MIT ライセンスで、GitHub スター約 13.6 万（2026 年 11 月時点）とこのジャンルで最大規模。公式の excalidraw.com はブラウザ内に自動保存されるローカルファースト設計で、PWA としてオフラインでも動き、エンドツーエンド暗号化されたリアルタイム共同編集に対応する。

図は `.excalidraw`（JSON）で保存されるため、画像ではなく**データとして** AI エージェントに渡せる点が、ブログ内では特に注目されている。

## 詳細

### 主な機能と組み込み

- 矩形・楕円・ひし形・矢印・線・フリーハンドなどの描画ツール
- 図形に吸着する矢印（バインド）とラベル付き矢印
- PNG / SVG への書き出し。「Embed scene」を有効にすると画像の中に元データが入り、Excalidraw で開き直して編集できる
- npm パッケージ `@excalidraw/excalidraw` として React アプリに組み込める。MIT なので商用サービスへの組み込みも自由
- Obsidian にはコミュニティ製の Excalidraw プラグインがある（図のデータは既定で圧縮されるので、エージェントに読ませるときは圧縮を解除するか `.excalidraw` として書き出す）

### セルフホストで共同編集する場合

共同編集は npm パッケージではなく excalidraw.com のアプリ側の機能。セルフホストで使うには次がすべて必要になる。

- WebSocket で中継するルームサーバー [excalidraw-room](https://github.com/excalidraw/excalidraw-room)（更新は 2024 年 7 月で止まっている）
- 接続先 URL（`VITE_APP_WS_SERVER_URL`）はビルド時に埋め込まれるため、フロントエンドの再ビルド
- `crypto.subtle` を使うため HTTPS（または localhost）

個人なら excalidraw.com、チームなら公式の商用サービス Excalidraw+ を使うのが手軽。

### JSON 構造：つながりはどこに入っているか

| 要素 | フィールド | 意味 |
|---|---|---|
| 矢印（`type: "arrow"`） | `startBinding.elementId` / `endBinding.elementId` | 吸着先の図形 ID。吸着していなければ `null` |
| テキスト | `containerId` | テキストが入っている図形または矢印の ID。独立テキストなら `null` |
| すべての要素 | `isDeleted` | 削除済み要素もファイルに残るので読むときに除外する |

座標・色・乱数シード（`seed`）・`version` などの管理用フィールドも要素ごとにあるため、生の JSON は冗長（約 43KB の図が、ノードと接続の一覧にすると 20 行程度）。新しい形式では吸着情報に `fixedPoint` も入るが、orbit モードで吸着した矢印では実際の接点と一致せず、0〜1 の範囲外の値も出る。

### AI エージェントへの指示に使う

| 渡し方 | 向いている場面 |
|---|---|
| 画像（PNG / SVG） | 画面のラフ、レイアウトの指示 |
| `.excalidraw`（JSON） | 構成図、処理フロー、依存関係など「つながり」が大事なもの |
| 両方（Embed scene の画像など） | 取り違えが許されない指示 |

JSON はノードと接続の一覧（Markdown）に縮めてから渡すのが実用的。ただし公開されている実際の図で試すと、次の 3 つで情報が落ちた。

1. **ラベルが図形にひも付いていない**：図形の「中」ではなく「上」にテキストを重ねただけで `containerId` が空
2. **同じラベルの図形が複数ある**：接続先が曖昧になる
3. **矢印が吸着していない**：端点が図形の近くにあるだけでは `startBinding` / `endBinding` は `null`

人が見る図では自然に起きるため、エージェントに渡す図は描き方を最初から決めておくのが最も効く。

- 矢印は必ず図形に吸着させる
- ラベルは図形の中に書く（選択してダブルクリックか Enter）
- 同じ名前の図形を作らない
- 矢印にもラベルを付ける（「何を渡すか」）
- 色や線種の意味は文章で添える
- フリーハンドは避ける

### AI エージェントに描かせる

- [mermaid-to-excalidraw](https://github.com/excalidraw/mermaid-to-excalidraw)（MIT）：エージェントには Mermaid を書かせ、人が Excalidraw で清書する分担ができる
- [excalidraw/excalidraw-mcp](https://github.com/excalidraw/excalidraw-mcp)：excalidraw 組織の MCP サーバー。リモートエンドポイントをカスタムコネクタとして追加して使う。名前の似たコミュニティ製サーバーも多いのでリポジトリを確認する
- Element Skeleton API（`convertToExcalidrawElements`）：`label` と `start` / `end` の ID だけで図形サイズや吸着を計算してくれる。ドキュメント上はベータで、JavaScript 実行環境が要る

ただし Excalidraw は接続を矢印側（`startBinding` / `endBinding`）と図形側（`boundElements`）の両方に書く必要があり、線の経路も座標で全部書く。公式の CLI レンダラーもないため、エージェントが自分の出力を描画して確かめるループは回しにくい。この点で「描かせる」用途は [draw.io](/blogs/wiki/tools/draw-io/) のほうが有利。

### draw.io への変換

draw.io 本体には Excalidraw の読み込み機能がなく、既存の [excalidraw-converter](https://github.com/sindrel/excalidraw-converter)（MIT、Go 製）は Gliffy 形式を経由する。ブログでは標準ライブラリだけの Python（150 行足らず）で mxGraph XML を直接生成した。

| Excalidraw | draw.io |
|---|---|
| `rectangle` / `ellipse` / `diamond` | `vertex`（`rounded=0;` / `ellipse;` / `rhombus;`） |
| `containerId` を持つテキスト | セルの `value` |
| `startBinding` / `endBinding` | `edge` の `source` / `target` |
| `roughness` | `sketch=1` |
| `angle`（ラジアン） | `rotation`（度） |

変換結果を draw.io の CLI で PNG にして目で確かめたことで、3 つの落とし穴が見つかった。

- `fixedPoint` を接続点に流用すると矢印が 1 点に集まる → 矢印の実際の端点から外接矩形に対する比率を計算し直す
- draw.io 側で折り返すとフォント幅の差で余計に改行される → 折り返さず Excalidraw の改行だけを使う
- `sketch=1` では塗りが斜線（hachure）になる → `fillStyle=solid` を明示する

グループ（`groupIds`）、手書きフォント、フレームの親子関係、矢印ラベルの位置は引き継げない。

### OSS ホワイトボードの比較（Miro 代替）

| ソフトウェア | ライセンス | 形態 | 向いている用途 |
|---|---|---|---|
| Excalidraw | MIT | Web アプリ / React コンポーネント | 手書き風の図、ブレスト、組み込み |
| BlockSuite | MPL-2.0 | Web Components のエディタ部品 | ドキュメントとキャンバスを統合したエディタの構築 |
| [draw.io](/blogs/wiki/tools/draw-io/) | Apache-2.0 | Web / デスクトップ | 構成図・フローチャート |
| WBO | AGPL-3.0 | Web アプリ | 軽量な共同お絵描き（`AUTH_SECRET_KEY` で JWT 認証を有効に） |
| Spacedeck Open | AGPL-3.0 | Web アプリ | 画像・動画を並べるムードボード |
| OpenBoard | GPL-3.0 | デスクトップ | 授業用の電子黒板 |
| tldraw（参考） | 独自ライセンス | React SDK | **OSS ではない**。本番利用には商用ライセンスが必要 |

- **BlockSuite** は [AFFiNE](/blogs/wiki/tools/affine/) のエディタを切り出した独立プロジェクト。Yjs（CRDT）上に作られ、`PageEditor` と `EdgelessEditor` を提供する。改変した MPL ファイルはソース公開が必要だが、部品として使うだけなら自分のコードは公開不要。README 上「まだ初期段階」
- **tldraw** はソース公開だが GitHub API のライセンス判定は `NOASSERTION`。開発環境での利用・改変は許可される一方、本番利用は商用またはトライアルのライセンスキーが必要で、キー検証の無効化は禁止、使用状況データの送信もありうる。OSI の定義するオープンソースには当たらない
- **AGPL-3.0**（WBO、Spacedeck Open）は社内でそのまま使う分には問題ないが、改変版をサービスとして外部提供するとソース公開義務が生じる

「ソースが GitHub にある」ことと「本番で自由に使える」ことは別。採用前に `LICENSE` を読む。

## 関連ページ

- [draw.io](/blogs/wiki/tools/draw-io/) — 変換先。エージェントに描かせるならこちらが有利
- [GenAI-DrawIO-Creator](/blogs/wiki/tools/draw-io-ai/) — 自然言語から draw.io XML を生成する研究
- [AFFiNE](/blogs/wiki/tools/affine/) — ホワイトボードを統合したワークスペース。BlockSuite の母体
- [Obsidian](/blogs/wiki/tools/obsidian/) — Excalidraw プラグインがある PKM ツール
- [MCP](/blogs/wiki/concepts/mcp/) — excalidraw-mcp の基盤プロトコル
- [AI エージェント](/blogs/wiki/concepts/ai-agent/) — 図で指示を受け取る側

## ソース記事

- [Miro の代わりになる OSS ホワイトボード比較：Excalidraw は MIT、tldraw は OSS ではない](/blogs/posts/2026/11/oss-whiteboard-miro-alternatives/) — 2026-11-19
- [AI エージェントへの指示は図で渡す：Excalidraw の JSON をプロンプトに変換する方法と落とし穴](/blogs/posts/2026/11/excalidraw-diagram-for-ai-agent/) — 2026-11-19
- [Excalidraw の図を draw.io に変換する：Python で書いたコンバーターと、AI エージェントに描かせるならどちらか](/blogs/posts/2026/11/excalidraw-to-drawio-converter/) — 2026-11-19
