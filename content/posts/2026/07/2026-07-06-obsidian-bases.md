---
title: "Obsidian Basesとは？ノートをデータベース化するコアプラグイン"
date: 2026-07-06
lastmod: 2026-07-06
slug: "obsidian-bases"
draft: false
source_url: "https://github.com/hdknr/blogs/issues/1#issuecomment-4888314579"
categories: ["ツール/開発環境"]
tags: ["Obsidian", "Bases", "PKM", "ナレッジ管理", "プラグイン"]
---

松濤Vimmer氏（[@shotovim](https://x.com/shotovim)）が、Obsidian の[コアプラグイン](https://help.obsidian.md/plugins) **Obsidian Bases** について[解説を投稿した](https://x.com/shotovim/status/2070517620403757440)。Vault 内のノートをデータベースのように扱える機能だ。Notion のような外部データベースツールとは異なり、ファイルの保存場所を変えずに使えるのが最大の特徴という。

## Obsidian Basesとは

[公式ドキュメント](https://help.obsidian.md/bases)によると、Bases はノートをテーブルやカードなどのデータベース風ビューとして表示できるコアプラグインだ。ノートの[プロパティ](https://help.obsidian.md/properties)を使って、ファイルの表示・編集・並び替え・フィルタリングができる。

読書リストや旅行計画、プロジェクト管理など、様々な用途に応用できる。

## Notionとの違い

Notion のようなデータベースアプリにノートを移行すると、ファイルがそのデータベースの内部形式に閉じ込められてしまう。一方 Bases のデータはすべて Vault 内の通常の Markdown ファイルとその [Properties（プロパティ）](https://help.obsidian.md/properties) に保存される。

Bases のビュー自体はあくまで「フィルターを通して Vault から抽出したビュー」的な立ち位置であり、元のファイルやフォルダ構成の独立性はそのまま保たれる。ビューの定義は `.base` ファイルとして保存するか、Markdown ファイル内にコードブロックとして埋め込める。

## ビューの種類

Bases では以下のレイアウトでノートを表示できる。

- **Table** — ファイルを行、プロパティを列として表示する
- **List** — 箇条書きや番号付きリストとして表示する
- **Cards** — 画像を使ったギャラリー風のグリッドで表示する
- **Map** — ファイルを地図上のピンとして表示する

## 作成方法

Bases を作成する方法は複数ある。

### コマンドパレットから

1. コマンドパレットを開く
2. `Bases: Create new base`（アクティブなファイルと同じフォルダに新規ベースを作成）または `Bases: Insert new base`（現在のファイルにベースを埋め込む）を選択する

### ファイルエクスプローラーから

対象のフォルダを右クリックし、`New base` を選択する。

### リボンから

垂直リボンメニューの `Create new base` アイコンをクリックする。

なお、最初に作成した時点では Vault 内のすべてのファイルが対象になるため、フィルターで絞り込む必要がある。フィルターとビューは以下のように `base` コードブロックでも直接記述できる。

```yaml
filters:
  and:
    - file.hasTag("example")
views:
  - type: table
    name: Table
```

## まとめ

Bases は、既存の Markdown ファイル構成を崩さずに「データを見る角度を変える」ための機能だ。普通のノートアプリのデータベース機能のように元データの独立性を犠牲にすることなく、テーブル・カード・地図といった多様なビューでノートを整理・分析できる。プロパティを活用しているノートが多い Vault であれば、まず読書リストやタスク管理などの小さな用途から試してみるとよさそうだ。
