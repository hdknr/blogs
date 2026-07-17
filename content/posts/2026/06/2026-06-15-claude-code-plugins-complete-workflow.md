---
title: "Claude Code の開発フローを完結させる厳選プラグイン10選 — Ralph Loop から Security Guidance まで実践解説"
date: 2026-06-15
lastmod: 2026-06-15
slug: "claude-code-plugins-complete-workflow"
draft: false
source_url: "https://github.com/hdknr/blogs/issues/1#issuecomment-4714974366"
categories: ["AI/LLM"]
tags: ["claude-code", "claude", "mcp", "agent", "security"]
---

Claude Code 単体でも十分強力だが、プラグインを組み合わせると「思考 → 実装 → テスト → セキュリティチェック」の完全な開発ワークフローをターミナル一本で回せるようになる。AI コーディングと Agent ワークフローの実践者 Vince（[@vincemask](https://x.com/vincemask)）が実際に使い込んで有用だと感じた10本を解説した記事をもとに、日本語で整理する。

現在 ClaudePluginHub・Claude-Plugins.dev・Anthropic の Marketplace を合わせると 9000 以上のプラグインが存在するが、数が多ければいいわけではない。プラグインを追加するたびに Claude のコンテキストウィンドウにツール定義が積み上がり、多すぎると逆にレスポンスが遅くなる。まずは「自分のボトルネック」を1つ解消するプラグインから入り、1週間使ってみてから判断するのが正しいアプローチだ。

---

## 1. Ralph Loop — 自律プログラミングループ

```bash
/plugin install ralph-loop@claude-plugins-official
```

Anthropic 公式プラグイン。名前はアニメ『ザ・シンプソンズ』のキャラクター「Ralph Wiggum（ラルフ・ウィガム）」に由来する。**stop-hook パターン**を実装しており、Claude が長時間・複数タスクの自律コーディングセッションを実行できるようにする。

仕組みはシンプルだ。PRD（製品要件定義書）をタスクリストとして Claude に渡してループを起動すると、Claude は順番にタスクを拾い、実装して commit し、クリーンなコンテキストで次のタスクに移る。完了まで人手が不要になる。

**最適な用途:** CRUD 生成・DB マイグレーション・テストカバレッジ拡充など、要件さえ明確なら自動で進められる繰り返し作業。PRD が曖昧だと Claude が迷走して時間を無駄にするため、仕様の精度が成否を左右する。

---

## 2. Context7 — リアルタイムドキュメント注入

```bash
/plugin install context7@claude-plugins-official
```

Claude が古い API で平然とコードを書いてしまう問題——一度は経験したことがあるはずだ。Context7 はそれをシンプルに解決する。**最新バージョンのドキュメントをリアルタイムで Claude のコンテキストに直接注入する** MCP サーバーだ。

Claude はトレーニングデータに頼るのではなく、必要に応じて Context7 の MCP サーバーに問い合わせ、Next.js 15・React 19・Tailwind CSS 4 などのフレームワークの最新 API 情報を取得する。幻覚が減り、生成されるコードも現在の書き方に沿ったものになる。

**最適な用途:** 更新頻度の高いライブラリやフレームワークを使う場合。特にメジャーバージョンが頻繁に変わるエコシステムで効果が大きい。

---

## 3. Firecrawl — AI 向け Web データ変換

```bash
claude plugin install firecrawl@claude-plugins-official
/firecrawl:setup  # API キーを設定
```

Web データ抽出の評価が最も高いプラグイン。JavaScript レンダリングの不安定さ・生 HTML のノイズ・静的スクレイピングの鮮度問題を一括解決する。具体的には **JavaScript を自動レンダリングし、ページをクリーンな Markdown または構造化 JSON に変換する**。Claude が直接消費できる形にして渡すわけだ。

主要コマンド:

| コマンド | 用途 |
|---|---|
| `/firecrawl:scrape` | 単一ページを取得・変換 |
| `/firecrawl:crawl` | サイト全体をクロール |
| `/firecrawl:search` | Web 検索 |
| `/firecrawl:interact` | フォーム送信などのブラウザ操作 |
| `/firecrawl:map` | サイト構造をマッピング |

チャットで一言伝えるだけで、Claude がページ取得・サイトクロール・Web 検索・フォーム送信・サイト構造図の生成を行う。

**最適な用途:** 市場調査・競合分析・ドキュメント集約、リアルタイムの Web データを必要とする自動化ワークフロー全般。

---

## 4. Playwright MCP — 自然言語ブラウザテスト

```bash
/plugin install playwright@claude-plugins-official
```

フロントエンドのテストスクリプトを書くのは時間がかかる。Playwright MCP は **Claude が画面上に見える Chrome ウィンドウを直接操作**できるようにする。

スクリプトを書く必要はない。「チェックアウトフローをテストして」「お問い合わせフォームを入力して送信して」と指示するだけで、ブラウザ内でリアルタイムに実行される。ブラウザを手動でログインした後、そのログイン済みセッションを Claude に引き継がせることも可能だ。

**最適な用途:** UI フローのテストをしたい・本番ページのデバッグをしたい・非同期動作の問題を掴みたいが、テストコードは書きたくないフロントエンドエンジニア。

---

## 5. Security Guidance — コード安全護衛（必須）

```bash
/plugin install security-guidance@claude-plugins-official
```

Claude はコードを速く書く。それがセキュリティ上の問題を見落としやすくする原因でもある。Security Guidance はすべてのファイル編集前に一度セキュリティスキャンを実行し、次の9種類の脆弱性パターンを検出する。

- コマンドインジェクション
- クロスサイトスクリプティング（XSS）
- `eval()` の使用
- 危険な HTML パターン
- Pickle デシリアライズ
- `os.system` 呼び出し
- その他の危険なパターン

リスクを検出すると編集をブロックし、警告・説明・修正提案を表示する。セッションごとに各パターンは1回のみ通知されるため、頻繁に作業を中断されることはない。

**最適な用途:** すべての開発者。まず最初にインストールすべき1本。

---

## 6. Figma MCP — デザイン稿を直接コードに変換

```bash
/plugin install figma@claude-plugins-official
```

フロントエンド開発で最も時間を食うフェーズの一つが、Figma のデザイン稿をコードに落とす作業だ。Figma MCP は Claude が**実際の Figma ファイルを読み取れる**ようにする——スクリーンショットでも文字での説明でもなく、本物のデザインデータだ。

Claude は frame・コンポーネント・レイアウト数値を直接読み込み、デザインに忠実なコードを生成する。デザイナーとの往復回数が大幅に減り、初期実装のスピードが向上する。

**最適な用途:** デザインファイルから UI を実装することが多いフロントエンドおよびフルスタックエンジニア。

---

## 7. Frontend Design — AI の UI 同質感を除去

```bash
/plugin install frontend-design@claude-plugins-official
```

AI が生成する UI には共通した「味」がある。Inter・Roboto・紫のグラデーション・どこかで見たような placeholder コンポーネント。Frontend Design はこの問題に対処するスキルで、Claude が**視覚的なアイデンティティを意識したデザイン判断**を行えるようにする。

具体的には:

- 使い古されたデフォルト（Inter、Roboto、紫グラデーション）を避ける
- 凝集力のある審美的方向性を設定する
- より重厚なタイポグラフィ・雰囲気のある背景・非対称レイアウトを取り入れる
- コンポーネントの配置だけでなく、視覚的な識別性から考える

**最適な用途:** プロダクト UI・ランディングページ・ダッシュボードなど、最終的な見た目にデザイナーが関与したように見せたい場合。

---

## 8. Linear — issue トラッカーをターミナルへ

```bash
/plugin install linear@claude-plugins-official
```

ターミナルと issue トラッカーの間でウィンドウを切り替えることはコンテキストスイッチのコストが大きい。Linear プラグインは Claude Code を Linear のワークスペースに直接接続し、チケット取得・タスク分解・ステータス変更・変更実装をすべてプログラミング環境から離れずに実行できるようにする。

使用例:

```
「sprint 24 のすべての open チケットをまとめて」
「チケット ENG-482 を開始して、サブタスクに分解して」
「ENG-391 を in progress にして」
```

**最適な用途:** チームで Linear をプロジェクト管理に使っており、コーディング中断を最小化したいエンジニア。

---

## 9. Code Review — 複数 AI エージェント並列 PR レビュー

```bash
/plugin install code-review@claude-plugins-official
```

通常の「ざっと1回スキャン」ではなく、**複数の専門 AI エージェントを並列で走らせて**コードをレビューする。テスト・型・エラーハンドリング・コード品質・重複ロジックの簡略化可能性をそれぞれ担当エージェントが担う。

各指摘には confidence score が付くため、必須修正と提案の区別が一目でわかる。

```
High Confidence:
  - Missing error handling in api/users.ts:45
Medium Confidence:
  - Consider extracting duplicate logic in utils/format.ts
```

**最適な用途:** 人間のレビュアーが見る前に、構造化されたレビューを一本通したいエンジニア。

---

## 10. Chrome DevTools MCP — Claude にブラウザをデバッグさせる

```bash
/plugin install chrome-devtools-mcp@chrome-devtools-plugins
/chrome  # 拡張機能のセットアップを実行
```

スクリーンショットとログファイルだけでは限界がある。Chrome DevTools MCP は Claude が**既存のログイン済み Chrome セッションのフルランタイム状態**——ネットワークリクエスト・コンソールエラー・パフォーマンス指標——にアクセスできるようにする。

「このリクエストがなぜ失敗したのか？」「何が LCP スコアを引き下げているのか？」という質問に対して、Claude はリアルタイムの DevTools データに基づいて答えを返す。推測ではなく実測値だ。

**最適な用途:** 複雑なデバッグ・ログイン状態が必要なページ・JavaScript ヘビーなアプリケーション。静的解析では追えない問題に最適。

---

## 推奨インストール順序

すべてを一度に入れる必要はない。以下の3本から始めると、Claude Code の主要な弱点——セッション跨ぎの記憶喪失・古いドキュメントへの依存・セキュリティの見落とし——を最優先で解消できる。

**まず入れる3本:**

1. **MemClaw または他のプロジェクトメモリシステム** — セッションを跨いで長期的なコンテキストを保持。アーキテクチャ・決定事項・規約・過去の作業を覚えさせ、毎回ゼロから説明し直す無駄をなくす。
2. **Firecrawl または Context7** — 最新のドキュメント・API・Web コンテンツを取得。過時のトレーニングデータへの依存を減らし、現代的なフレームワークを扱うときの精度を大幅に上げる。
3. **Security Guidance** — セキュリティ審査ゲートを一枚追加。危険な変更・脆弱性・シークレットの露出・安全でないコードパターンをデプロイ前に止める。

その後、用途に応じて Playwright・Code Review・Linear を追加していく。

最速で出荷するエンジニアは、単に Claude Code を使っているだけではない。正しいプラグインを選び、自分の作業スタイルに合わせてチューニングした Claude Code を使っている。

---

*元ツイート: [@vincemask](https://x.com/vincemask/status/2066482407419838620)*
