---
title: "AIが自律的にセキュリティタスクをこなす「reverse-skill」——逆向エンジニアリングスキルルーターの仕組み"
date: 2026-06-24
lastmod: 2026-06-24
slug: "reverse-skill-ai-security-router"
draft: false
description: "逆向エンジニアリング（リバースエンジニアリング）スキルをAIに与えるルーターパック「reverse-skill」のアーキテクチャ・routing.mdの仕組み・20以上のサブスキル・倫理的論点を解説する。"
source_url: "https://github.com/hdknr/blogs/issues/1#issuecomment-4785280496"
categories: ["セキュリティ"]
tags: ["セキュリティ", "リバースエンジニアリング", "claude-code", "agent", "ペネトレーションテスト", "CTF"]
---

## はじめに

「リバースエンジニアリング（逆向エンジニアリング）はもはや専門家の専売特許ではない」——そんな示唆を含む GitHub プロジェクトが X（旧 Twitter）で話題になった。プロジェクト名は **[reverse-skill](https://github.com/zhaoxuya520/reverse-skill)**。リバースエンジニアリング（バイナリやソフトウェアを解析して内部構造を理解する技術）・公認ペネトレーションテスト・セキュリティリサーチのサブスキルを束ね、AI コーディングクライアントに「自律ルーティング」で渡す仕組みだ。本記事ではプロジェクトのアーキテクチャ・ルーティングの仕組み・サブスキル一覧・倫理的論点を整理する。

投稿者はこれを「比較的危険なプロジェクト」と表現しつつ、4,400 以上のスターを集めている（2026-06-24 時点）。本記事ではその構造と動作原理を日本語で整理する。

## reverse-skill とは

`zhaoxuya520/reverse-skill` は、Claude Code・Kiro・Cursor・Cline といった AI コーディングクライアント向けの **セキュリティタスク・スキルルーターパック**だ。

> Reverse Engineering / Authorized Penetration Testing / Security Research Skill Router Pack
> AI-powered routing + On-demand toolchain bootstrapping + Self-evolving knowledge base

核心的なアイデアはシンプルで、`routing.md`（および `RULES.md`）を AI コンテキストに注入することで、AI が受け取ったタスクを自動分類し、適切なサブスキルへ振り分ける。ユーザーは「APK を解析して」と伝えるだけで、AI が自らどのツール・どの手順を使うかを判断して実行する。

## アーキテクチャ：二層構造

```text
reverse-skill/
├── README.md                     # AIエージェントブートストラップエントリ
├── CTF-Sandbox-Orchestrator/     # CTFコンペ向けフルスタック（40以上のサブスキル）
└── skills/                       # メインスキルディレクトリ
    ├── SKILL.md                  # メインコントローラエントリ
    ├── routing.md                # シナリオ→スキルのディスパッチテーブル
    ├── RULES.md                  # AIの完全な動作チェーン（ステップ0〜14）
    ├── tool-index.md             # ローカルツールインデックス（自動生成）
    ├── field-journal/            # 自動進化する経験ログ
    ├── apk-reverse/              # APK逆向解析
    ├── ida-reverse/              # IDA Pro静的解析
    ├── js-reverse/               # JSフロントエンド逆向
    ├── firmware-pentest/         # ファームウェアペネトレーション
    ├── edr-bypass-re/            # EDRバイパス逆向（レッドチーム向け）
    ├── pwn-chain/                # RE→エクスプロイト（スタック/ヒープ/カーネル）
    ├── patch-diff-exploit/       # Nデイパッチ差分→exploitation
    ├── radare2/                  # radare2 CLI逆向
    └── ...                       # 他多数
```

`CTF-Sandbox-Orchestrator` は CTF コンペ向けの垂直統合スタックで 40 以上のサブスキルを持ち、`skills/` 配下には APK 解析・IDA・EDR バイパスなど汎用的な逆向・ペンテスト系サブスキルが横断的に並ぶ。両者は同一階層に配置され、`routing.md` の相対パスで参照し合う。

## ルーティングの仕組み

プロジェクトの README は通常のドキュメントではなく、**AI エージェントが読み込むブートストラップエントリ**として設計されている。

```text
AI が README.md を読んだ直後に実行すべき設定フロー:
0. refresh-tool-index.sh を実行してローカルツールインデックスを生成
1. 実際のインストールパスを検出
2. OS を検出（Windows / Kali / Ubuntu / macOS / その他）
3. プラットフォーム固有のデプロイドキュメントを読み込む
4. RULES.md を読み込み → 完全な動作チェーンを実行
5. 対応するサブスキルに入り → タスクを開始
```

`routing.md` はシナリオごとのディスパッチテーブルとして機能し、AI は受け取ったタスクをここで照合して該当スキルに遷移する。`field-journal/` には実行結果が自動蓄積され、経験ベースが自己進化する設計になっている。

## カバーするサブスキル

ツイートで「20以上のサブスキル」と紹介されていた通り、以下を含む幅広い分野をカバーする。

| サブスキル | 内容 |
|---|---|
| `apk-reverse` | APK逆向解析 |
| `ida-reverse` | IDA Pro静的解析 |
| `js-reverse` | JavaScriptフロントエンド逆向 |
| `firmware-pentest` | ファームウェアペネトレーション（OWASP FSTM準拠） |
| `edr-bypass-re` | EDRバイパス逆向（レッドチーム） |
| `pwn-chain` | RE→実用エクスプロイト（スタック/ヒープ/カーネル） |
| `patch-diff-exploit` | Nデイパッチ差分→exploitation |
| `radare2` | radare2 CLI逆向解析 |
| `binary-diff` | クロスバージョンシンボルマイグレーション |
| `attack-chain` | マルチステージ攻撃チェーンオーケストレーション |
| `CTF-Sandbox-Orchestrator` | CTFコンペ対応（40以上のサブスキル） |

## 導入手順（概要）

```bash
# リポジトリをクローン
git clone https://github.com/zhaoxuya520/reverse-skill.git

# ローカルツールインデックスを生成（macOS/Linux）
bash skills/scripts/refresh-tool-index.sh

# 利用可能なブートストラップ機能を確認
bash skills/scripts/bootstrap-reverse.sh --list
```

AI コーディングクライアント側では、プロジェクトルールや CLAUDE.md などに `SKILL.md` や `routing.md` を参照する設定を追加する。AI は以降、逆向エンジニアリング系のタスクを受け取ると自動的にルーティングを行い、必要なツールをオンデマンドでインストール・実行する。

## 「危険」という評価について

ツイート投稿者は「比较危险的项目（比較的危険なプロジェクト）」と表現した。その背景にある論点は以下だ。

**セキュリティへの貢献としての側面**：

- 公認ペネトレーションテストや CTF の効率が大きく向上する
- セキュリティリサーチャーが繰り返し作業をオートメーション化できる
- 個別のツール習熟なしにセキュリティ業務に取り組める入門経路になる

**懸念される側面**：

- APK 解析・EDR バイパス・脆弱性 exploitation といった攻撃的技術のハードルが大幅に低下する
- プロジェクトは "Authorized Penetration Testing" を謳うが、実際の使用用途はユーザー次第だ
- AI がツールチェーンを自律的に選択・実行する構造は、誤用されたとき人間が介在しにくい

プロジェクト自体は「公認ペネトレーション・セキュリティリサーチ向け」と位置付けている。セキュリティスキルの民主化は避けられない流れだが、その先の倫理的な利用責任はコミュニティ全体に問われている。

## まとめ

`reverse-skill` は、AI に専門的なセキュリティスキルを持たせるための「スキルルーターパック」だ。`routing.md` + `RULES.md` によるタスク自動分類と、オンデマンドなツールチェーンブートストラップが特徴で、Claude Code や Cursor などの主要 AI クライアントで利用できる。

ツイート投稿者が「危険」と表現したように、強力なツールの普及は常に二面性を持つ。セキュリティ研究・教育・公認テストへの活用と、悪用リスクを天秤にかけつつ、AI 時代のセキュリティスキルのあり方を考える契機となるプロジェクトだ。
