---
title: "Claude CodeのSEOスキル「claude-seo」とは？導入方法と全コマンドを解説"
date: 2026-06-24
lastmod: 2026-06-24
slug: "claude-seo-skill"
draft: false
source_url: "https://github.com/hdknr/blogs/issues/1#issuecomment-4785292468"
categories: ["AI/LLM"]
tags: ["claude-code", "SEO", "スキル", "GEO", "E-E-A-T"]
---

`/seo audit` コマンド1つでサイト全体の並列監査が走り、AI検索最適化（GEO）まで25のサブスキルをカバーする——Claude Code向けSEOスキル「claude-seo」の全容を解説します。

## claude-seoとは

**claude-seo**は、Claude CodeにSEO分析機能を追加するオープンソースのスキルです。Claude Codeの「スキル」機能を活用して `~/.claude/skills/` にインストールされ、`/seo` で始まるカスタムコマンドが使えるようになります。

- **開発者**: AgriciDaniel（GitHub）
- **ライセンス**: MIT（無料・商用利用OK）
- **GitHubスター**: 9,600+（2026年6月時点）
- **対応環境**: Mac / Linux / Windows
- **必要なもの**: Python 3.8以上、Claude Code

インストール後は、**25個のサブスキル＋18個のサブエージェント**が利用可能になります。

## 主要コマンド一覧

| コマンド | 機能 |
|---|---|
| `/seo audit` | サイト全体のSEO監査（複数のサブエージェントが並列実行） |
| `/seo page` | ページ単位の詳細分析 |
| `/seo technical` | テクニカルSEO診断 |
| `/seo content` | E-E-A-Tコンテンツ品質分析 |
| `/seo content-brief` | コンテンツブリーフの自動生成 |
| `/seo schema` | 構造化データの検出・検証・生成 |
| `/seo images` | 画像最適化分析 |
| `/seo sitemap` | XMLサイトマップの検証・生成 |
| `/seo geo` | AI検索最適化（GEO） |
| `/seo plan` | SEO戦略の設計 |
| `/seo programmatic` | プログラマティックSEO分析 |
| `/seo competitor-pages` | 競合比較ページの生成 |
| `/seo hreflang` | 多言語サイトのhreflang検証 |
| `/seo cluster` | セマンティッククラスタリング |

最新のサブスキル一覧は[公式リポジトリの skills/ ディレクトリ](https://github.com/AgriciDaniel/claude-seo)で確認できます。

## Claude Codeの「スキル」とは

Claude Codeには「スキル（Skills）」という拡張機能の仕組みがあります。`~/.claude/skills/` ディレクトリに `SKILL.md` ファイルを配置すると、Claude Codeがそれを読み込んで、カスタムコマンド（スラッシュコマンド）として使えるようになります。

claude-seoはこの仕組みを活用して、メインのオーケストレータースキル（`/seo`）と25個のサブスキル、18個のサブエージェントをインストールします。

## 導入方法

### Mac / Linuxの場合

公式READMEではセキュリティ上の理由から `git clone` 方式を推奨しています。

```bash
git clone https://github.com/AgriciDaniel/claude-seo.git
bash claude-seo/install.sh
```

スクリプトの内容を確認してから実行したい場合は `cat install.sh` で内容を確認してください。

### Windowsの場合

```powershell
git clone https://github.com/AgriciDaniel/claude-seo.git
powershell -ExecutionPolicy Bypass -File claude-seo\install.ps1
```

### インストールされるもの

| インストール先 | 内容 |
|---|---|
| `~/.claude/skills/seo/` | メインのオーケストレータースキル |
| `~/.claude/skills/seo-*/` | 25個のサブスキル |
| `~/.claude/agents/seo-*.md` | 18個のサブエージェント定義 |
| `~/.claude/skills/seo/scripts/` | Pythonスクリプト（HTML解析、スクリーンショット等） |
| `~/.claude/skills/seo/.venv/` | Python仮想環境（依存パッケージ） |

オプションでPlaywright（Chromium）もインストールされます。スクリーンショット撮影やビジュアル分析に使われますが、インストールに失敗しても他の機能は問題なく動作します。

### アンインストール方法

```bash
curl -fsSL https://raw.githubusercontent.com/AgriciDaniel/claude-seo/main/uninstall.sh | bash
```

> **注意**: アンインストールは公式が `curl | bash` 形式のみ提供しています。実行前に内容を確認したい場合はURLをブラウザで開いてスクリプトを確認してください。

## 主要コマンドの使い方

### /seo audit — サイト全体のSEO監査

```text
/seo audit https://example.com
```

6つのサブエージェントが並列稼働するため、最も包括的な分析が得られるコマンドです。サイト全体をクロールし、**各専門エージェントが同時並行で分析**を実行します。

| サブエージェント | 担当領域 |
|---|---|
| seo-technical | クロール可能性、インデックス、セキュリティ、CWV |
| seo-content | E-E-A-T評価、薄いコンテンツの検出、AI引用適性 |
| seo-schema | 構造化データの検出・検証・JSON-LD生成 |
| seo-sitemap | XMLサイトマップの検証、品質ゲート |
| seo-performance | Core Web Vitals（LCP・INP・CLS）の計測 |
| seo-visual | Playwrightによるスクリーンショット、ファーストビュー分析 |

分析結果は以下の2つのファイルとして出力されます。

- **`FULL-AUDIT-REPORT.md`** — 全カテゴリの詳細レポート
- **`ACTION-PLAN.md`** — 優先度別（Critical → High → Medium → Low）のアクションプラン

ヘルススコアの算出配分は以下のとおりです。

| カテゴリ | 配分 |
|---|---|
| テクニカルSEO | 25% |
| コンテンツ品質 | 25% |
| オンページSEO | 20% |
| 構造化データ | 10% |
| Core Web Vitals | 10% |
| 画像最適化 | 5% |
| AI検索対応 | 5% |

### /seo page — ページ単位の詳細分析

```text
/seo page https://example.com/about
```

1ページに対して、オンページSEO・コンテンツ品質・テクニカル要素・構造化データ・画像を総合的に分析します。主なチェック項目は以下のとおりです。

- タイトルタグ（50〜60文字）
- メタディスクリプション（150〜160文字）
- H1タグの数と構造
- コンテンツのキーワード密度（1〜3%）
- canonical、robots meta、OGP、Twitter Card
- 画像のalt属性、ファイルサイズ

### /seo technical — テクニカルSEO診断

```text
/seo technical https://example.com
```

8カテゴリにわたるテクニカルSEOの診断を実行します。クロール可能性、インデックス、セキュリティ（HTTPS・CSP・HSTS）、URL構造、モバイル対応、Core Web Vitals、構造化データ、JavaScript描画（CSR/SSR判定）などをチェックします。

AIクローラー（GPTBot、ClaudeBot、PerplexityBotなど）のアクセス可否チェックも含まれており、AI検索が主流となった2026年ならではの診断項目です。

### /seo content — E-E-A-Tコンテンツ分析

```text
/seo content https://example.com/blog/article
```

Googleの品質評価ガイドラインに基づいて、E-E-A-T（経験・専門性・権威性・信頼性）の観点からコンテンツを評価します。AI生成コンテンツの検出も行い、低品質なAIマーカー（汎用的な表現、独自の知見なし、著者情報なし等）をフラグ付けします。

### /seo schema — 構造化データの検出・検証・生成

```text
/seo schema https://example.com
```

ページ上の構造化データ（JSON-LD、Microdata、RDFa）を検出し、Googleがサポートする型に対して検証を行います。不足している構造化データがあれば、JSON-LDテンプレートを自動生成してくれます。

2026年現在、以下の構造化データは廃止・制限されています。

| 構造化データ | 状況 |
|---|---|
| HowTo | 2023年8月（モバイル）〜9月（デスクトップ）に段階的にリッチリザルト表示が終了 |
| FAQ | 2023年8月に政府・認可済み医療機関サイトのみに制限。2026年5月7日に完全廃止 |
| SpecialAnnouncement | 2025年7月31日に廃止 |

claude-seoはこれらの最新情報を把握しているため、廃止された構造化データを誤って実装するリスクを防げます。

### /seo geo — AI検索最適化（GEO）

```text
/seo geo https://example.com
```

Google AI Overview、ChatGPT、Perplexity等のAI検索での表示を最適化するためのコマンドです。2026年のSEOで最も注目されている分野の一つで、以下の5つの指標でスコアリングされます。

| 指標 | 配分 | 概要 |
|---|---|---|
| 引用適性スコア | 25% | パッセージの長さ（134〜167語が最適）、引用可能な記述の有無 |
| 構造的可読性 | 20% | 見出し階層、質問形式の見出し、短い段落 |
| マルチモーダルコンテンツ | 15% | 画像・動画・表などの多様なコンテンツ形式 |
| 権威性・ブランドシグナル | 20% | 著者情報、Wikipedia・Reddit・YouTubeでの言及 |
| 技術的アクセシビリティ | 20% | AIクローラーへのアクセス許可、SSR対応、llms.txt |

### /seo plan — SEO戦略の設計

```text
/seo plan saas
```

業種別のSEO戦略を自動設計します。対応している業種テンプレートは `saas`、`local`、`ecommerce`、`publisher`、`agency` の5種類です。URL階層の設計、コンテンツカレンダー、実装ロードマップ（4フェーズ）まで出力されます。

## claude-seoの特徴

### サブエージェントによる並列処理

`/seo audit` の実行時、6つの専門サブエージェントが並列で稼働します。Claude Codeのエージェント機能を活用した設計で、1つのエージェントが順番に処理するよりも大幅に高速です。

### MCP連携でライブデータ分析

claude-seoはMCP（Model Context Protocol）サーバーと連携することで、実際のSEOデータを使った分析が可能になります。

| MCPサーバー | 提供データ |
|---|---|
| Ahrefs（@ahrefs/mcp） | バックリンク、キーワード、サイト監査のライブデータ |
| Semrush（公式リモートMCP） | ドメイン分析、キーワードリサーチ |
| Google Search Console（コミュニティ製） | 検索パフォーマンスデータ |
| PageSpeed Insights（コミュニティ製） | Core Web Vitalsの実測データ |

MCPサーバーがなくても、HTMLの静的解析による基本的な分析は実行できます。

### データソースと必要な設定

claude-seoのデータソースは2層に分かれます。**入口は認証不要**で、Googleなどのライブデータが欲しいときだけ追加設定が必要になります。

| 層 | データソース | 必要な設定 |
|---|---|---|
| **デフォルト** | HTML静的解析（クロール＋パース）、Playwrightによるスクリーンショット | **なし**（APIキー不要） |
| **オプション** | Ahrefs / Semrush / Google Search Console / PageSpeed Insights のライブデータ | 各MCPサーバーの認証情報 |

`/seo audit` の大部分はデフォルトのHTML静的解析だけで動作します。Google系のライブデータを使う場合のみ、次の設定が必要です。

- **Google Search Console（GSC）** — Google Cloudで Search Console API を有効化し、OAuthクライアントまたはサービスアカウントの認証情報を発行してMCPに設定します。
- **PageSpeed Insights** — Google Cloudで PageSpeed Insights API を有効化し、APIキーを発行します。少量なら鍵なしでも動く場合がありますが、実運用ではレート制限を避けるためAPIキーの設定が推奨されます。

> **GA4（Google Analytics）はclaude-seoの標準データソースではありません。** 標準で連携するGoogle系データはGSCとPageSpeed Insightsで、GA4の分析を組み込みたい場合はGA4対応のMCPサーバーを別途用意する必要があります。

具体的な認証設定の手順は各MCPサーバーのREADMEが最終的な正となるため、導入時にそちらを確認してください。

### 2026年最新のSEOトレンドに対応

- Core Web VitalsのINP（FIDから2024年3月に移行済み）
- E-E-A-Tの全競合クエリへの適用拡大（2025年12月コアアップデート）
- GEO（AI検索最適化）— AI Overview、ChatGPT、Perplexity対応
- AIクローラー（GPTBot、ClaudeBot等）のアクセス制御チェック
- llms.txt標準への対応

## セキュリティ上の注意

claude-seoを導入する前に、セキュリティ面を確認しておきましょう。

**インストール方法のリスク**: 本記事では `git clone` 後に `bash install.sh` を実行する方式を推奨しています。ネット上のスクリプトをそのままPCで実行する `curl | bash` 形式はリポジトリが第三者に改ざんされた場合のリスクがあり、公式READMEもこの形式を非推奨としています。まず[GitHubのinstall.sh](https://github.com/AgriciDaniel/claude-seo/blob/main/install.sh)の中身を確認してからインストールしましょう。

**スキルの権限**: Claude Codeのスキルは、Claude Code本体と同じ権限で動作します。つまり、PCのファイルを読み書きしたり、シェルコマンドを実行できます。信頼できるスキルのみインストールするようにしてください。

**APIキーの管理**: Ahrefs等のMCPサーバーを連携する場合、APIキーがClaude Codeの設定ファイルに保存されます。GitHubの公開リポジトリに設定ファイルをアップロードしないよう注意してください。

## まとめ

claude-seoは、Claude CodeにSEO分析機能を一括で追加できる強力なオープンソーススキルです。コマンド1つでインストールでき、サイト全体の並列監査・E-E-A-T分析・AI検索最適化など2026年のSEOトレンドを網羅しています。

Ahrefs等のMCPサーバーと連携することでライブデータを使った分析も可能になります。セキュリティ面に注意しながら、Claude CodeでのSEO業務自動化に活用してみてください。
