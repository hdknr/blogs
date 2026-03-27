---
title: "opencli-rs: Rust製の爆速Webスクレイピングツールで55以上のサイトをCLI化する"
date: 2026-03-27
lastmod: 2026-03-27
draft: false
source_url: "https://github.com/hdknr/blogs/issues/1#issuecomment-4140834709"
categories: ["ツール/開発環境"]
tags: ["rust", "agent", "github"]
---

[opencli-rs](https://github.com/nashsu/opencli-rs) は、55以上の主要サイトに対応したRust製のCLIツールです。サイトごとにAPIやスクレイピング方法が異なる煩雑さを解消し、1つのコマンドで各プラットフォームの情報を取得できます。

## opencli-rs とは

opencli-rs は、元々TypeScriptで実装されていた OpenCLI をRustで完全に書き直したツールです。X (Twitter)、YouTube、Reddit、Hacker News、Bilibili、Zhihu、Xiaohongshu（小紅書）など多数のプラットフォームに対応しています。Chromeのログインセッションを再利用するため、APIキーなしでデータを取得できます。

出力形式はテーブル、JSON、YAML、CSV、Markdownに対応しており、用途に応じて使い分けが可能です。また、Electronベースのデスクトップアプリをコマンドラインから制御する機能も備えており、GUIアプリの操作をスクリプト化できます。

### 主な特徴

- **処理速度が最大12倍に向上** — TypeScript版と比較して大幅な高速化（例: Bilibili Hot の取得が20.1秒から1.66秒に）
- **メモリ使用量を10分の1に削減** — 95-99MBから9-15MBへ
- **シングルバイナリで動作** — わずか4.7MB、追加のランタイム不要でどの環境にも導入可能

## インストール

インストールスクリプトが用意されており、システムとアーキテクチャを自動検出してバイナリをダウンロードします。

```bash
curl -fsSL https://raw.githubusercontent.com/nashsu/opencli-rs/main/scripts/install.sh | sh
```

Rustの開発環境がある場合はソースからビルドすることもできます。

```bash
git clone https://github.com/nashsu/opencli-rs.git
cd opencli-rs
cargo build --release
```

## AIエージェントとの連携

opencli-rs はAIエージェントとの連携を前提に設計されています。Claude Code や Cursor などに組み込むことで、「Hacker Newsのトップ記事を取得して要約する」「競合のX投稿を定期的にチェックする」といったWeb情報収集の自動化が可能です。

AIエージェント向けのスキルパッケージ [opencli-rs-skill](https://github.com/nashsu/opencli-rs-skill) も提供されています。

```bash
npx skills add https://github.com/nashsu/opencli-rs-skill
```

これにより、AIエージェントが `AGENT.md` や `.cursorrules` の設定を通じて利用可能なツールを自動的に検出し、自然言語でWebスクレイピングを実行できるようになります。

## まとめ

opencli-rs は、Rustの性能を活かしたWebスクレイピングツールとして、速度・メモリ効率・導入の手軽さにおいて優れた選択肢です。AIエージェントとの連携も充実しており、市場調査や競合分析の自動化に活用できます。

- GitHub: [nashsu/opencli-rs](https://github.com/nashsu/opencli-rs)
- AIエージェント向けスキル: [nashsu/opencli-rs-skill](https://github.com/nashsu/opencli-rs-skill)
