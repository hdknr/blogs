---
title: "Obsidian Vault を Claude Code に繋ぐ実践編 — CLAUDE.md / Skills / Settings のプロジェクト別管理パターン"
date: 2026-05-18
lastmod: 2026-05-18
slug: "claude-code-obsidian-vault-project-config"
draft: false
description: "個人 Obsidian Vault を特定プロジェクトの Claude Code セッションに併用させたいときの設定パターンを実用例で解説。global / project / local の3層と、MCP filesystem サーバ・symlink の組み合わせで、機密を漏らさず Vault のサブセットだけを AI Agent に渡す構成を示す。"
categories: ["AI/LLM"]
tags: ["claude-code", "Obsidian", "mcp", "CLAUDE.md", "Skills", "symlink", "permissions", "ナレッジマネジメント", "PKM"]
---

[GitHubで全部完結する開発者にObsidianは本当に必要か？]({{< ref "posts/2026/05/2026-05-18-github-vs-obsidian-ai-agent.md" >}}) では、Obsidian を併用する場合の「思想差」と「AI Agent に渡せる文脈の質」を整理しました。本記事はその実践編です。**特定のプロジェクトで Claude Code セッションを行うときに、個人の Obsidian Vault を併用してエージェントに処理させるには、`CLAUDE.md` / Skills / Settings をどう階層管理すべきか** を具体的な設定例で示します。

ポイントは次の3つです。

1. Claude Code の設定階層（global / project / local）を理解して役割分担する
2. Vault は **gitignored 層** で繋ぐ（リポジトリにパスを残さない）
3. **CLAUDE.md には安定パスを書く** — Vault の生パスを書かない（symlink 経由で参照）

## Claude Code の3層構造を整理する

まず大前提として、Claude Code の設定は 3 層あり、それぞれ用途が違います。

| 階層 | 主なファイル | Git 管理 | 使いどころ |
| --- | --- | --- | --- |
| **Global (user)** | `~/.claude/CLAUDE.md` / `~/.claude/skills/` / `~/.claude/settings.json` | 個人の dotfiles で管理（任意） | 全プロジェクト共通の個人スタイル・横断スキル |
| **Project** | `<proj>/CLAUDE.md` / `<proj>/.claude/skills/` / `<proj>/.claude/settings.json` / `<proj>/.mcp.json` | リポジトリにコミット | プロジェクト固有の規約・公開してよい設定 |
| **Local** | `<proj>/.claude/settings.local.json` | `.gitignore` で除外 | **Vault パスなど個人秘匿情報を置く** |

`claude mcp add` の `--scope`（`-s`）オプションも、これと同じ 3 値を取ります（`local` / `user` / `project`）。重要なのはデフォルトの挙動です。

- `-s` を省略すると **`local` スコープ** が選ばれる
- 書き込み先は `<proj>/.claude/settings.local.json`
- `.claude/settings.local.json` はリポジトリの `.gitignore` で除外する前提（プロジェクトテンプレートに含めておく）

つまり `claude mcp add` を素直に叩いた時点で、**Vault パスはコミット対象外の個人設定ファイルにしか書かれない** ということです。これは Vault のような個人秘匿情報を扱う際に安全側に倒れる設計になっており、本記事ではこのデフォルト挙動を前提に話を進めます。

> **重要**: 公開リポジトリに `<proj>/.mcp.json`（`-s project`）で Vault のパスを書くと、OS ユーザー名（`/Users/hdknr/...`）や Vault のディレクトリ構造が世界に公開されます。Vault を繋ぐ MCP サーバは原則 `-s local` か `-s user` を使ってください。

## Obsidian Vault を Claude に接続する3つの方式

### 方式A: グローバル MCP filesystem サーバ（全プロジェクトから常時参照）

```bash
# ~/.claude.json に書き込まれる（全プロジェクトで有効）
claude mcp add -s user obsidian-vault -- \
  npx -y @modelcontextprotocol/server-filesystem ~/Documents/ObsidianVault
```

- **向き**: 個人プロジェクト中心で、常に Vault 全体を読ませたい人
- **注意**: 業務委託先のリポジトリでセッションを開いても Vault が見える状態になります。機密プロジェクトとの相性は要注意です。

### 方式B: プロジェクトの local settings に登録（プロジェクト単位 + 非公開）

`-s local`（デフォルト）で登録すると、`<proj>/.claude/settings.local.json`（gitignored）に書かれます。

```bash
cd <proj>
claude mcp add -s local obsidian-vault -- \
  npx -y @modelcontextprotocol/server-filesystem \
  ~/Documents/ObsidianVault/topics/nextjs
```

実体はこういう JSON になります。

```jsonc
// <proj>/.claude/settings.local.json (gitignored)
{
  "mcpServers": {
    "obsidian-vault": {
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/server-filesystem",
        "/Users/hdknr/Documents/ObsidianVault/topics/nextjs"
      ]
    }
  }
}
```

- **向き**: クライアントワーク等で「このプロジェクトでは Vault のこの領域だけ見せる」と切り分けたい場合
- **メリット**: Vault のパスがリポジトリに漏れない・プロジェクト単位で参照範囲を絞れる

### 方式C: Vault のサブディレクトリを symlink で取り込む（パス安定 + 軽量）

```bash
mkdir -p <proj>/.claude/knowledge
ln -s ~/Documents/ObsidianVault/topics/nextjs   <proj>/.claude/knowledge/nextjs
ln -s ~/Documents/ObsidianVault/topics/postgres <proj>/.claude/knowledge/postgres
echo ".claude/knowledge/" >> .gitignore
```

CLAUDE.md には `.claude/knowledge/` を参照する旨だけを書きます。Vault のフォルダ構造が変わっても、CLAUDE.md は書き換え不要になります。

- **向き**: Vault から取り込む領域が複数ある・参照パスを安定させたい場合
- **メリット**: ファイルパスが `.claude/knowledge/<topic>/...` の形に正規化されるため、CLAUDE.md やスキルから決め打ちで参照できる

## 推奨構成: 方式B（local MCP）+ 方式C（symlink）の併用

筆者がいまもっとも安定して回っているのは、**方式B（grep / 全文走査用に MCP filesystem を local scope で登録）+ 方式C（CLAUDE.md からの参照パスを安定化する symlink）** のハイブリッドです。

```
~/.claude/
├── CLAUDE.md                # 全プロジェクト共通の個人スタイル
├── skills/
│   ├── vault-search/        # Vault 横断検索スキル（共通）
│   └── vault-daily-log/     # Daily Notes 追記スキル（共通）
└── settings.json            # 共通の permission・hook 設定

<project>/
├── CLAUDE.md                # このプロジェクト固有のルール
├── .claude/
│   ├── skills/              # プロジェクト固有スキル（公開してOKなもの）
│   ├── knowledge/           # ← Vault サブディレクトリへの symlink (gitignored)
│   ├── settings.json        # コミット可能な permission/agent 設定
│   └── settings.local.json  # ← Vault パス等の個人情報 (gitignored)
└── .gitignore               # .claude/knowledge/ と .claude/settings.local.json を除外
```

理由はシンプルで、次の2つを同時に成立させたいからです。

- **CLAUDE.md は git にコミットされる** → 個人 Vault のパスを書きたくない
- **MCP filesystem サーバは検索・grep の速度が出やすい** → 大規模 Vault でも処理が軽い

なぜ片方だけでは足りないか、という観点で補足すると、

- **方式B（MCP）のみ**: CLAUDE.md から「このノートを必ず読む」と決め打ちで参照したいときに、毎回 MCP ツール呼び出しを介する必要がある。Read ベースの軽い参照には冗長で、コンテキスト消費も増える
- **方式C（symlink）のみ**: 「あの話、確か Vault のどこかに書いた」を引き当てる横断 grep ができない（symlink で取り込んだ範囲しか見えない）。未知の関連ノートを発見させる用途には弱い

そこで、`.claude/knowledge/` という symlink 越しの **安定パス** は CLAUDE.md から決め打ちで参照させ、**Vault 全体の横断検索** が必要なときは MCP サーバを呼ばせる、という二段構えにすると役割が綺麗に分離します。

## CLAUDE.md のテンプレート

### グローバル（`~/.claude/CLAUDE.md`）

```markdown
## Personal knowledge base (Obsidian Vault)

- 個人 Vault のルートは `~/Documents/ObsidianVault`。
- 各プロジェクトの `.claude/knowledge/` は、この Vault のサブセットを symlink した読み取り専用ディレクトリ。
- 設計判断・命名・過去の検討経緯を参照したいときは、まず `.claude/knowledge/` を `Grep` する。
- Vault 全体を横断したい場合は、MCP サーバ `obsidian-vault` を経由する。
- Vault への書き込みは禁止（個人 Vault の整合性を壊さないため）。
- 公開コミットに Vault の生の文章を引用しない。必要なら要点だけプロジェクト内 docs に書き直す。
```

### プロジェクト（`<proj>/CLAUDE.md`）

```markdown
## Personal knowledge base (optional)

- 個人 Obsidian Vault を併用する場合、`.claude/knowledge/` を symlink で用意する想定。
- 存在しない場合はこのセクションのルールを無視してよい（チームメンバー向けの逃げ道）。

このプロジェクト固有の参照ポイント:

- ドメイン用語: `.claude/knowledge/<client>/glossary.md` を正とする
- 過去の設計検討: `.claude/knowledge/nextjs/auth-decisions.md`
- 既知の落とし穴: `.claude/knowledge/postgres/locking-pitfalls.md`

設計判断やコードレビューの前に、対応するノートを必ず一度 `Read` してから着手すること。
```

「**個人 Vault がない人でも動く**」ように、`存在しない場合はこのセクションのルールを無視してよい` と明示しておくのがコツです。チームメンバーが Claude Code を使う場合でも、CLAUDE.md がエラーにならず破綻しません。CLAUDE.md は短く絞るほど効くので、Vault 連携セクションが膨らみすぎたら別ファイルに切り出して `@import` する手もあります（参考: [CLAUDE.md の設定を99%消したら逆にうまくいった話：AI への指示は「哲学」だけ残せ]({{< ref "posts/2026/03/2026-03-11-claude-md-less-is-more.md" >}})）。

## Skills の使い分け

Claude Code のスキル（Skills）は、グローバルとプロジェクトの両方に置けます。Vault 関連のスキルは「個人で常に使うもの」と「プロジェクト固有のワークフロー」で分けるのが運用しやすいです。

**グローバルに置くスキル例**（`~/.claude/skills/`）:

- `vault-search`: Vault 全体をクエリ横断検索し、関連ノートのパスとサマリを返す
- `vault-daily-log`: 今日の Daily Note に決まったテンプレートで作業ログを追記する
- `vault-link`: 引数で指定したノート 2 つに相互 `[[リンク]]` を貼る

**プロジェクト固有に置くスキル例**（`<proj>/.claude/skills/`）:

- `decision-log`: ADR（Architecture Decision Record）をリポジトリ内 docs と Vault の両方に書き出す
- `summary-back-to-vault`: PR のサマリを抽出し、Vault の該当 topic ノートに「過去事例」として追記する

スキルのスコープ管理で詰まりやすい挙動（auto-memory との衝突など）は [Claude Code の Skills が会話ごとにずれる原因は auto-memory だった]({{< ref "posts/2026/04/2026-04-21-claude-code-auto-memory-skills.md" >}}) にまとめてあります。

スキルから Vault に書き込ませる場合は、**書き込み先を `~/Documents/ObsidianVault/inbox/` のような専用フォルダに固定** してください。AI が直接 Vault の正本に追記するとリンク構造が壊れます。あとから人間が `inbox/` を見て、必要なノートにリンク・移動する運用にすると安全です。

> **重要**: 後述の permissions で `.claude/knowledge/**` への Write を全面禁止するため、`inbox/` は **`.claude/knowledge/` 配下の symlink には含めず、MCP filesystem サーバ経由で Vault の実パス（`~/Documents/ObsidianVault/inbox/`）に書かせる構成** にしてください。読み取り用 symlink と書き込み用 MCP サーバの役割を分離する形になります。

## permissions で「事故」を構造的に潰す

CLAUDE.md でルールを書くだけでなく、`settings.json` の `permissions` で書き込みを禁止しておくと、AI が誤って Vault を破壊するリスクが構造的になくなります。

```jsonc
// <proj>/.claude/settings.json (コミットしてOK — Vault パスは書かない)
{
  "permissions": {
    "deny": [
      "Write(.claude/knowledge/**)",
      "Edit(.claude/knowledge/**)",
      "Bash(rm:*.claude/knowledge*)",
      "Bash(mv:*.claude/knowledge*)"
    ]
  }
}
```

ポイントは「symlink 先（= Vault 本体）への書き込み」を symlink パス越しに禁止していることです。Claude が `.claude/knowledge/nextjs/auth-decisions.md` に `Edit` をかけようとした瞬間に弾かれるので、ルール違反が事故になりません。

ただし、この設定で防げるのは **`.claude/knowledge/` パス越しのアクセス** だけです。次の経路はこのプロジェクト設定では塞げません。

- `Bash(rm -rf ~/Documents/ObsidianVault/...)` のような **Vault 実パスを直接叩く操作**
- 他プロジェクトのセッションから Vault に書き込もうとする操作

前者は `~/.claude/settings.json`（global）側で `Bash(rm:*ObsidianVault*)` や `Write(/Users/<you>/Documents/ObsidianVault/**)` を deny しておくと一括で塞げます。後者は次節のチェックリストで触れます。`Bash(rm:*.claude/knowledge*)` 形式の glob は Claude Code の permission 構文に依存するため、最新の permissions ドキュメントで挙動を確認した上で採用してください。

Vault 横断検索 MCP も「読み取り専用」モードで動かしておくと万全です。`@modelcontextprotocol/server-filesystem` は引数で渡したディレクトリを書き込みも含めて扱える設計なので、Vault 用には別途 read-only ラッパを噛ませるか、書き込みが必要なときだけ `inbox/` 配下に限定して書かせる方針が安全です。

## プライバシー上の落とし穴チェックリスト

最後に、運用で踏みやすい地雷をリスト化しておきます。

1. **`-s project` で MCP サーバを登録しない** — `.mcp.json` にパスが書かれて世界に公開される
2. **`<proj>/.gitignore` に `.claude/knowledge/` と `.claude/settings.local.json` の両方を必ず入れる** — 片方忘れると symlink が `git status` に出る
3. **`.claude/settings.local.json` を `git mv` で誤ってコミットしないか確認** — `git ls-files .claude/` でコミット対象を時々監査する
4. **チームメンバーの環境で動くか確認** — Vault がない環境で CLAUDE.md がエラーにならないこと（前述の「逃げ道」セクションが効く）
5. **クライアント A の Vault を、クライアント B のセッションから見せない** — 業務委託先ごとに Vault のサブツリーを分けるか、`local` スコープで読ませる範囲を絞る
6. **`--add-dir` の都度指定でしのぐパターンも併用可能** — `claude --add-dir ~/Documents/ObsidianVault/topics/nextjs` でセッション開始すれば、設定ファイルに何も残さず一時的に繋げられる。機密プロジェクトとの行き来が多い人向け
7. **global 層の permission が project 層に降りてくる挙動を理解する** — `~/.claude/settings.json` で `Read(~/Documents/ObsidianVault/**)` を許可していると、業務委託先プロジェクトのセッションでも自動的に Vault が読める状態になる。機密プロジェクトでは `~/.claude/settings.json` 側で許可を絞り、Vault 接続は **個別プロジェクトの `.claude/settings.local.json` で明示的に有効化** する方針が安全

## まとめ

特定プロジェクトで Claude Code セッションを行うときに個人 Obsidian Vault を併用する場合、設計の肝は次の 3 点です。

- **Claude Code の3層構造（global / project / local）と Vault の機密性を対応付ける** — Vault は必ず gitignored 層（local settings + symlink）で繋ぐ
- **CLAUDE.md には `.claude/knowledge/` という安定パスを書く** — Vault の生パスは書かない
- **permissions で書き込み禁止を構造化** — ルール違反を事故にしない

この構成にしておくと、プロジェクトごとに「どこまで Vault を見せるか」を絞りつつ、CLAUDE.md とスキルは安定したパスで動き続けます。Vault 全体を見せる「個人プロジェクト用」と、サブセットだけ見せる「業務委託用」を共存させやすいのが、このパターンの一番の利点です。
