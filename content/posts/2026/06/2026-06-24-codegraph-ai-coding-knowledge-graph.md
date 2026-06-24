---
title: "CodeGraph：AIコーディングのツール呼び出しを58%削減するコード知識グラフOSS"
date: 2026-06-24
lastmod: 2026-06-24
slug: "codegraph-ai-coding-knowledge-graph"
draft: false
source_url: "https://github.com/hdknr/blogs/issues/1#issuecomment-4785302719"
categories: ["AI/LLM"]
tags: ["CodeGraph", "Claude Code", "MCP", "知識グラフ", "OSS"]
---

AIコーディングツールの最大のボトルネックのひとつが、コードベースを探索するための大量のツール呼び出しだ。grep・glob・ファイル読み込みを繰り返してから、ようやく本来の作業に入る——この非効率を、**ツール呼び出し58%削減・22%高速化**という実測値で解消する OSS が **CodeGraph** だ。

## CodeGraph とは

[CodeGraph](https://github.com/colbymchenry/codegraph) は、コードベースをあらかじめ「知識グラフ」として索引化しておくローカル実行の OSS ツールだ。MIT ライセンスで公開されており、2026年6月時点で GitHub スター数は約5.4万を超えている。

AI エージェントがコードを理解する際、従来はファイルを一枚ずつ grep・glob・Read して構造を把握していた。CodeGraph はシンボル・呼び出しエッジ・依存関係を事前にグラフ化しておくため、エージェントが「1回のクエリ」で必要なコードを正確に取得できる。動的ディスパッチのホップ（実行時に決まるメソッドの呼び出し先）も追跡できるため、grep では辿り着けない呼び出しパスも把握できる。

対応エージェントは幅広い：

- Claude Code
- Cursor
- Codex CLI
- OpenCode
- Hermes Agent
- Gemini CLI
- Antigravity IDE
- Kiro

## ベンチマーク結果

対象: 実際のオープンソースコードベース7つ（7言語）
方法: Claude Code（ヘッドレスモード）でアーキテクチャ質問に回答させ、各4回の中央値を比較

**全コードベース共通の中央値: ツール呼び出し58%減 / 22%高速化 / ファイル読み込みほぼゼロ**

| コードベース | 言語 | ツール呼び出し | 処理時間 | ファイル読み込み | トークン | コスト |
|----------|----------|------------|------|------------|--------|------|
| **VS Code** | TypeScript (~1万ファイル) | 81%減 | 11%高速 | 0 vs 9 | 64%減 | 18%安 |
| **Excalidraw** | TypeScript (~640) | 40%減 | 27%高速 | 0 vs 7 | 25%減 | 同等 |
| **Django** | Python (~3千) | 77%減 | 13%高速 | 0 vs 9 | 60%減 | 8%安 |
| **Tokio** | Rust (~790) | 57%減 | 18%高速 | 0 vs 8 | 38%減 | 同等 |
| **OkHttp** | Java (~645) | 50%減 | 31%高速 | 0 vs 4 | 54%減 | 25%安 |
| **Gin** | Go (~110) | 44%減 | 24%高速 | 1 vs 6 | 23%減 | 19%安 |
| **Alamofire** | Swift (~110) | 58%減 | 33%高速 | 0 vs 9 | 64%減 | 40%安 |

ファイル読み込み列は「CodeGraph あり vs なし」の中央値比較。コスト削減効果はコードベースの規模に依存する面があるが、ツール呼び出しの削減と高速化はあらゆる規模で一貫して確認されている。

## どんなプロジェクトに効くか

ツール呼び出しの削減効果はプロジェクトの規模を問わず現れるが、トークン・コストの節約は大規模コードベースほど顕著になる。

- **小〜中規模プロジェクト**: 高速化とツール呼び出し削減が主なメリット
- **大規模モノレポ**: 上記に加えてトークン・コスト削減も積み重なる

Claude Code や Cursor をすでに使っていて「コードベース探索に時間がかかる」と感じているなら、導入コストは低いので試す価値は高い。

## CodeGraph のインストール方法

### バイナリ（推奨・Node.js 不要）

OS 向けのビルド済みバイナリが自動で取得される：

```bash
# macOS / Linux
curl -fsSL https://raw.githubusercontent.com/colbymchenry/codegraph/main/install.sh | sh

# Windows (PowerShell)
irm https://raw.githubusercontent.com/colbymchenry/codegraph/main/install.ps1 | iex
```

### npm（Node.js がある場合）

```bash
npm i -g @colbymchenry/codegraph
```

アップグレードはいつでも：

```bash
codegraph upgrade
```

## セットアップ手順

### 1. エージェントへの接続

> **注意:** インストール後は新しいターミナルセッションで実行すること（PATH を反映させるため）。

```bash
codegraph install
```

`codegraph install` は使用中のエージェントを自動検出し、各エージェントの設定に CodeGraph の MCP サーバーを組み込む。

### 2. プロジェクトの初期化

```bash
cd your-project
codegraph init
```

`.codegraph/` ディレクトリを作成し、プロジェクト全体のグラフを一度に構築する。

### 3. 自動同期

デフォルトでファイル変更を監視し、グラフを自動更新する。エージェントがコードを編集中でも、ファイルを追加・変更・削除しても、インデックスは常に最新の状態を保つ。`codegraph init` 後は放置するだけでよい。

## アンインストール

```bash
codegraph uninstall   # 全エージェントから削除
codegraph uninit      # プロジェクトのインデックス削除
```

## まとめ

CodeGraph は「AIに都度コードを探索させる」から「事前に知識グラフを持たせる」へのシフトを実現するツールだ。Claude Code・Cursor・Codex などと透過的に連携し、100%ローカルで動作する点も安心感がある。ツール呼び出しの大幅な削減は、レスポンスの高速化とコストの両面で実質的なメリットをもたらす。
