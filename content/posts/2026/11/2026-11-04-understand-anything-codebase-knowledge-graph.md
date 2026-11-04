---
title: "Understand-Anything：コードベースを対話的なナレッジグラフにする Claude Code プラグイン"
date: 2026-11-04
lastmod: 2026-11-04
slug: "understand-anything-codebase-knowledge-graph"
draft: false
source_url: "https://github.com/hdknr/blogs/issues/694#issuecomment-6625210229"
categories: ["ツール/開発環境"]
tags: ["claude-code", "知識グラフ", "Tree-sitter", "プラグイン", "OSS", "LLM Wiki"]
---

新しいチームに入ったら、コードベースは 20 万行。どこから読めばいいのか——。[Understand-Anything](https://github.com/Egonex-AI/Understand-Anything) は、この問いに「コードベースをナレッジグラフにして、地図として眺めながら読む」という答えを出すオープンソースのプラグインです。Claude Code・Codex・Cursor などの AI コーディングツールで使えます。

X では「フォロワー 32 人の大学院生が作ったサイドプロジェクトが数万スターを集めた」という話題で紹介されていました。紹介投稿によれば、作者はジョージア工科大学でマルチモーダル感情認識を研究する Yuxiang Lin 氏（GitHub: Lum1104）です。プロジェクトは現在、Egonex-AI の Organization に移管されています。2026 年 11 月 4 日時点で GitHub スター数は約 9 万です。

この記事では、Understand-Anything が何をするのか、どう動いているのか、導入時に何に気をつけるべきかを README をもとに整理します。

## Understand-Anything とは

README の一文を借りると「コードベース・ナレッジベース・ドキュメントを、探索・検索・質問できる対話的なナレッジグラフに変える」ツールです。

- ファイル・関数・クラス・依存関係をノードとエッジにしたグラフを生成する
- グラフを Web ダッシュボードで表示し、パン・ズーム・検索ができる
- ノードを選ぶと、平易な英語（`--language` 指定で日本語なども可）の要約と関係が表示される

リポジトリの説明文に掲げられたスローガンは「Graphs that teach > graphs that impress」。README でも、目指すのはコードベースの複雑さを誇示するグラフではないと述べています。各部品がどう組み合わさっているかを静かに教えてくれるグラフだ、というわけです。

ライセンスは MIT、実装は TypeScript です。Claude Code のプラグインとしてネイティブに動くほか、Codex、Cursor、VS Code + GitHub Copilot、Gemini CLI、OpenCode、Cline、Kiro など多数の AI コーディングツールに対応しています。

## Understand-Anything の主な機能

| 機能 | 内容 |
| --- | --- |
| 構造グラフ | ファイル・関数・クラスをノードとして表示。クリックで要約と関係を確認 |
| ドメインビュー | コードを業務ドメイン・フロー・ステップに対応付けて表示 |
| ガイドツアー | 依存関係の順に並べたアーキテクチャのウォークスルーを自動生成 |
| ファジー／セマンティック検索 | 「認証を扱っているのはどこ？」のような意味での検索 |
| 差分の影響分析 | コミット前に、変更がどこへ波及するかを表示 |
| ペルソナ適応 UI | ジュニア開発者・PM・パワーユーザーで詳細度を切り替え |
| レイヤー可視化 | API・Service・Data・UI・Utility などのレイヤーで色分け |
| 言語概念の解説 | ジェネリクス、クロージャ、デコレータなど 12 のパターンを登場箇所で解説 |

コードだけでなく、[Karpathy 流の LLM Wiki](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f)（LLM が Markdown の記事群を継続的に書き足していく知識ベースの手法）を `/understand-knowledge` に渡すと、Wiki の記事同士の関係をグラフ化することもできます。

## 仕組み：Tree-sitter と LLM の分業

Understand-Anything の設計で興味深いのは、静的解析と LLM の役割をはっきり分けている点です。

### 構造と意味の分業

図のように、処理は構造の抽出（Tree-sitter）と意味付け（LLM エージェント）の 2 段に分かれます。

![Understand-Anything の /understand の処理の流れ。Tree-sitter による構造解析の結果を LLM エージェント群が意味付けし、.ua/knowledge-graph.json に保存して、ダッシュボードや差分分析などで使う図](/blogs/images/understand-anything-pipeline.png)

- **Tree-sitter（決定的）**: Tree-sitter は多言語対応のインクリメンタル構文解析ライブラリです。ソースを構文木にパースし、import / export、関数・クラス定義、呼び出し箇所、継承といった構造上の事実を抽出します。同じ入力からは毎回同じ出力が得られ、インクリメンタル更新のための変更検出（フィンガープリント）にも使われます。
- **LLM（意味的）**: パース結果と元のソースを読み、平易な要約、タグ、アーキテクチャ上のレイヤー、業務ドメインへの対応付け、ガイドツアーなど、パーサーには作れないものを生成します。

この分業により、グラフの「構造」側（どのファイルがどれを import しているか）は再現性があり、「意味」側（そのファイルが何のためにあるか）は LLM が補う、という形になっています。

### /understand のマルチエージェントパイプライン

`/understand` は 5 つの専門エージェントを順に動かします。

| エージェント | 役割 |
| --- | --- |
| `project-scanner` | ファイルの発見、言語・フレームワークの検出 |
| `file-analyzer` | Tree-sitter の解析結果（importMap）を受け取り、関数・クラス・import からグラフのノードとエッジを生成 |
| `architecture-analyzer` | アーキテクチャ上のレイヤーを特定 |
| `tour-builder` | 学習用のガイドツアーを生成 |
| `graph-reviewer` | グラフの完全性と参照整合性を検証（既定はインライン、`--review` で LLM によるフルレビュー） |

`/understand-domain` では `domain-analyzer`、`/understand-knowledge` では `article-analyzer` が加わります。`file-analyzer` は最大 5 並列、1 バッチ 20〜30 ファイルで処理されます。

## Understand-Anything の使い方

### インストール（Claude Code）

Claude Code のプロンプトで次を入力します（シェルではありません）。

```text
/plugin marketplace add Egonex-AI/Understand-Anything
/plugin install understand-anything
```

Codex・Gemini CLI・OpenCode などの場合は、プラットフォーム名を指定するインストーラーをシェルで実行します。

```bash
curl -fsSL https://raw.githubusercontent.com/Egonex-AI/Understand-Anything/main/install.sh | bash -s codex
```

インストーラーはリポジトリを `~/.understand-anything/repo` にクローンし、各プラットフォーム用のシンボリックリンクを作ります。なお Codex ではスキルの呼び出しが `/understand` ではなく `$understand` になる点に注意してください。

> `curl ... | bash` 形式は手軽ですが、実行前にスクリプトの中身を確認する習慣をつけておくと安心です。Claude Code であれば、上のプラグインマーケットプレイス経由のインストールを使えばこの形式を避けられます。

### 解析とダッシュボード

以下も Claude Code のプロンプトで入力します。

```text
# コードベースを解析して .ua/knowledge-graph.json を生成
/understand

# 日本語で要約やダッシュボードを生成
/understand --language ja

# ダッシュボードを開く
/understand-dashboard
```

`--language` を指定せずに初めて実行すると、会話で使っている言語を自動で検出します。英語以外の場合は確認したうえで、`.ua/config.json` に保存します。

### その他のコマンド

```text
# コードベースに質問する
/understand-chat 決済フローはどう動いている？

# 手元の変更の影響範囲を分析
/understand-diff

# 特定のファイルや関数を深掘り
/understand-explain src/auth/login.ts

# 新メンバー向けのオンボーディングガイドを生成
/understand-onboard

# 業務ドメインの知識（ドメイン・フロー・ステップ）を抽出
/understand-domain

# LLM Wiki 形式のナレッジベースをグラフ化
/understand-knowledge ~/path/to/wiki

# コミットごとに post-commit フックで自動更新
/understand --auto-update

# 巨大なモノレポではサブディレクトリに絞る
/understand src/frontend
```

## ナレッジグラフをコミットしてチームで共有する

生成されたグラフはただの JSON なので、**一度コミットすればチームメンバーはパイプラインを回さずに済みます**。コミット対象は `.ua/` ディレクトリです。ローカルの作業用ファイルは除外するため、`.gitignore` に次の 2 行を追加します。

```gitignore
.ua/intermediate/
.ua/diff-overlay.json
```

10MB を超える大きなグラフは git-lfs での管理が推奨されています。

コミット済みのグラフは、Claude Code も LLM も API キーもなしに、Node.js 18 以上だけで閲覧できます。

```bash
npx https://github.com/Egonex-AI/Understand-Anything/releases/latest/download/understand-anything-viewer.tgz /path/to/analyzed/project
```

アクセストークン付きのローカル URL（`http://127.0.0.1:5173/?token=…`）が表示され、ブラウザでダッシュボードが開きます。データはローカルディスクから読み取り専用で配信され、外部には送られません。

## 導入時の注意点：初回解析のトークン消費

README 自身が「初回の `/understand` はコードベース全体を解析するため、大きなプロジェクトではかなりのトークンを消費する」と注意を促しています。Tree-sitter による構造の抽出は LLM を使いませんが、意味付けの段階では LLM のトークンを消費します。

対策として README が挙げているのは次の 2 点です。

- 従量課金の API ではなく、サブスクリプションのプランで実行する
- プライバシーや企業要件がある場合は、Ollama などのローカルモデルに切り替える

2 回目以降はデフォルトでインクリメンタル（変更されたファイルだけ再解析）なので、消費は大きく減ります。

## まとめ

Understand-Anything は、Tree-sitter による決定的な構造解析と、LLM エージェントによる意味付けを組み合わせ、コードベースを「読める地図」に変えるツールです。次のような場面で効果を発揮しそうです。

- 知らないコードベースに入るときのオンボーディング
- 変更前の影響範囲の確認
- グラフをコミットして、LLM なしでもチーム全員が閲覧

初回のトークン消費にさえ気をつければ、まず手元の中規模リポジトリで `/understand` を試してみる価値は十分にあるでしょう。[ライブデモ](https://understand-anything.com/demo/)ではインストールせずにダッシュボードを触ることもできます。

## 参考リンク

- [Egonex-AI/Understand-Anything（GitHub）](https://github.com/Egonex-AI/Understand-Anything)
- [Understand Anything ホームページ](https://understand-anything.com/)
- [ライブデモ](https://understand-anything.com/demo/)
