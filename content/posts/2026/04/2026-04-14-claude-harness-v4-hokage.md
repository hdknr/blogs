---
title: "Claude Harness v4.0.0 \"Hokage\" — Go ネイティブ化で 30 倍速、設定が harness.toml 1 本に"
date: 2026-04-14
lastmod: 2026-04-14
draft: false
source_url: "https://github.com/hdknr/blogs/issues/1#issuecomment-4265196767"
categories: ["ツール/開発環境"]
tags: ["Claude Code", "Claude Harness", "AI開発", "OSS", "Go"]
---

Claude Code の拡張 OSS「Claude Harness」が v4.0.0 "Hokage" をリリースした。コア全体を Go ネイティブに書き換え、フック実行速度が約 30 倍に向上。設定ファイルも `harness.toml` 1 本に集約され、大幅に扱いやすくなった。

## Claude Code の拡張機構とは

Claude Code には最初から強力な拡張機構が備わっている。

- **hooks** — `PreToolUse` / `PostToolUse` / `SessionStart` などのイベントでスクリプトを差し込める
- **permissions** — `settings.json` の deny ルールで危険なコマンドを事前ブロックできる
- **plugin system** — `plugin.json` で自作プラグインを作り、チーム配布できる
- **skills** — スラッシュコマンドで自作ワークフローを走らせられる
- **MCP** — 外部ツール（DB・Slack・GitHub…）をネイティブ連携できる

「AI がやらかしそうなこと」「自律運用のワークフロー」「危ないコマンドのブロック」はほぼ全部、Claude Code の機能で実現できる。

## 自分で全部セッティングするのは無理ゲー

強力だからといって、簡単ではない。  
自作で「AI に危ないコマンドを通させない」ワークフローを組もうとすると、以下を理解しておかなければならない。

- `plugin.json` — プラグインマニフェスト
- `hooks.json` — PreToolUse に走らせるスクリプトを宣言
- `settings.json` — deny ルールを人力で組み立てる
- `.mcp.json` — MCP サーバー設定
- `.claude-plugin/hooks.json` — プラグイン経由のフックも別途

整合させる JSON が 5〜6 本。どれか 1 つを直すと別がズレる。  
さらに「Plan → Work → Review の自律運用」を乗せようとすると以下も必要になる。

- `Plans.md` のタスク管理ルールを自作
- 実装用エージェントの prompt を書く
- レビュー用の別エージェントも自作
- フックでタスク進捗を同期
- ガードレールのルールテーブルを設計

本業の片手間にやると数日〜1 週間は溶ける。その後の運用中も地味にメンテナンスコストがかかり続ける。

## Claude Harness は、これを 1 パッケージで組み込んだ外装プラグイン

Harness は Claude Code の拡張機構をフル活用した外装プラグイン。  
AI エンジニアが自作すると数日かかる構成を、インストール 1 回で手元に落とす。

> 「自分で組み立てると数日かかる」が、  
> 「`/plugin install` して 3 分で動く」になる。

v4.0.0 "Hokage" は、その鎧をより軽く・より厳しく・より身軽にしたリリースだ。

## v4.0.0 の 4 つの進化ポイント

### ⚡ フック実行が 30 倍速になった: Go ネイティブ化

**問題:**  
以前の Harness フックは `bash → Node.js → TypeScript ガードレールエンジン` の 3 段ロケットで動いており、1 回の呼び出しに約 300ms かかっていた。Plan と Work を行き来するだけで気づかないうちに手元が重くなる。

**解決:**  
v4 でこれが Go バイナリ 1 本になった。`bin/harness` が `hooks.json` から直接呼ばれ、フック 1 回の実行が約 10ms まで短縮された。30 倍の高速化だ。

**技術メモ:**  
pure-Go SQLite（`modernc.org/sqlite`）を採用し、Node.js ランタイム要件を完全排除した。

### 🛡️ さらに厳格化: R12 が deny に、Bash bypass も防止

**問題:**  
AI に実装を任せていると「それ、実行させちゃダメだった」が通ることがあった。  
`git push --force`、`rm -rf`、保護ブランチへの直 push、`--no-verify` による hook bypass などが、警告のみで止まらないケースがあった。

**解決:**  
v4 でガードレール R12 を `deny` に格上げ。保護ブランチへの直接 push は完全ブロック。  
さらに Claude Code 2.1.98 で発見された Bash permission bypass 2 種も、Harness 側で二層目として重ねて塞いだ。

**技術メモ:**  
defense in depth — CC 本体が塞いだ穴を Harness が再度塞ぐ構造で、auto-allow すり抜け対策を強化。

### 📁 設定が harness.toml 1 本に: SSOT 化

**問題:**  
冒頭で触れた 5〜6 本の JSON 整合。これを運用中ずっと手でやるのは、地味につらい。  
どれか 1 つを直すと、別のどれかでズレて、開発体験を削る。

**解決:**  
v4 で `harness.toml` 1 本が SSOT になった。

```bash
# harness.toml を書いて
$ bin/harness sync
# plugin.json / hooks.json / settings.json
# が全て整合。
```

手動同期の事故は、ゼロになった。

### 📦 身軽になった: Node.js 依存ゼロ、ネイティブ 3 バイナリ配布

**問題:**  
以前は Harness を動かすために Node.js をマシンに入れる必要があった。  
`better-sqlite3` が Node のバージョン依存で、Node 24 に上げると壊れる互換問題もあった。

**解決:**  
v4 からランタイム依存はゼロ。ネイティブバイナリ 3 本で配布される。

## まとめ

| 改善点 | Before | After |
|---|---|---|
| フック実行速度 | ~300ms | ~10ms（30 倍速） |
| 設定ファイル数 | 5〜6 本を手動整合 | harness.toml 1 本 |
| ガードレール | R12 warn | R12 deny + Bash bypass 二重防御 |
| Node.js | 必要 | 不要（ネイティブバイナリ） |

Claude Code は強力な拡張機構を持っている。  
でも全部自分で組むと、5〜6 個の設定ファイル、自作エージェント、独自ルール…で数日溶ける。

Harness は、それを 1 パッケージで組み込んだ外装プラグイン。  
v4.0.0 "Hokage" はその鎧を、軽く・厳しく・より身軽にしたリリースだ。

## 使ってみる

Claude Code v2.1.92 以上（推奨）があれば、以下の手順で導入可能。

```bash
# Claude Code を起動した状態で
/plugin marketplace add Chachamaru127/claude-code-harness
/plugin install claude-code-harness@claude-code-harness-marketplace
/harness-setup
```

あとは `/harness-plan` をつけて最初の依頼を指示するだけ。

既に使っている人は:

```bash
/plugin update claude-code-harness
```

- GitHub: [Chachamaru127/claude-code-harness](https://github.com/Chachamaru127/claude-code-harness)
