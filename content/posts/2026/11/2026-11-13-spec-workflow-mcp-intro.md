---
title: "Spec Workflow MCP とは？ ダッシュボードで仕様を承認しながら進める MCP サーバーの使い方と注意点"
date: 2026-11-13
lastmod: 2026-11-13
slug: "spec-workflow-mcp-intro"
draft: false
categories: ["AI/LLM"]
tags: ["Spec Workflow MCP", "mcp", "仕様駆動開発", "SDD", "claude-code"]
---

**Spec Workflow MCP** は、AI コーディングエージェントに仕様駆動開発（SDD）の進め方を持ち込む **MCP サーバー** です。要件 → 設計 → タスクの順に仕様を作ります。特徴は、その一つひとつを **Web ダッシュボードや VS Code 拡張から人間が承認する** 仕組みです。

ほかの SDD ツールがスラッシュコマンドやスキルとして入るのに対し、Spec Workflow MCP は MCP サーバーとして動きます。そのため、MCP に対応したエージェント（Claude Code、Cursor、Codex など）なら、ほぼ同じ書き方の設定で使えます。

なお、2026 年 11 月時点でメンテナンスが休止しており、npm で入る版には最新の脆弱性修正が入っていません。詳しくは後半の「使う前に知っておきたい注意点」を読んでから導入を判断してください。

この記事では、リポジトリ（[Pimzino/spec-workflow-mcp](https://github.com/Pimzino/spec-workflow-mcp)）とドキュメントをもとに、導入方法、仕様の作り方と承認の流れ、ダッシュボード、使う前に知っておきたい注意点を整理します。内容は 2026 年 11 月 13 日時点のものです。

あわせて読みたい関連記事です。

- SDD の全体像：[仕様駆動開発（SDD）とは？ 3 つのアプローチ・EARS 記法・Kiro / Spec Kit・TDD との違い](/blogs/posts/2026/11/spec-driven-development-overview/)
- 同じ文書構成を使う AI 開発環境：[Kiro とは？ AWS の仕様駆動 AI IDE の Spec・Steering・Hooks と料金プラン](/blogs/posts/2026/11/kiro-ai-ide-intro/)

## Spec Workflow MCP の概要

| 項目 | 内容 |
| --- | --- |
| 作者 | Pimzino 氏（GitHub） |
| ライセンス | GPL-3.0 |
| 公開 | 2025 年 8 月 |
| npm パッケージ | `@pimzino/spec-workflow-mcp`（npm の最新は 2.2.5、2026 年 3 月 2 日） |
| 形態 | MCP サーバー ＋ Web ダッシュボード ＋ VS Code 拡張 |
| ダッシュボードの言語 | 日本語・英語を含む 11 言語 |

ライセンスが MIT ではなく **GPL-3.0** である点は、ほかの SDD ツールとの違いです。ツールとして使うだけなら影響は小さいですが、改変して配布する場合は条件を確かめてください。

## 導入方法

### Claude Code

プロジェクトのパスを指定して、MCP サーバーとして登録します。

```bash
claude mcp add spec-workflow npx @pimzino/spec-workflow-mcp@latest -- /path/to/your/project
```

`/path/to/your/project` は、自分のプロジェクトの絶対パスに置き換えます（以下の設定例も同じです）。

### そのほかのエージェント

Claude Desktop・Cursor・Cline などは、MCP の設定ファイルに次の形で追加します。

```json
{
  "mcpServers": {
    "spec-workflow": {
      "command": "npx",
      "args": ["-y", "@pimzino/spec-workflow-mcp@latest", "/path/to/your/project"]
    }
  }
}
```

Codex では `~/.codex/config.toml` に次のように書きます。

```toml
[mcp_servers.spec-workflow]
command = "npx"
args = ["-y", "@pimzino/spec-workflow-mcp@latest", "/path/to/your/project"]
```

### ダッシュボードを起動する

ダッシュボードは MCP サーバーとは別に起動します（[Configuration](https://github.com/Pimzino/spec-workflow-mcp/blob/main/docs/CONFIGURATION.md)）。

```bash
npx -y @pimzino/spec-workflow-mcp@latest --dashboard
```

ポートは `--port` で指定できます。README は `http://localhost:5000` の例ですが、ドキュメントには「指定しなければ空いているポートを自動で選ぶ」という記述もあり、食い違っています。決まったポートで開きたいなら、`--port 5000` のように明示してください。

ダッシュボードは 1 つだけ起動すれば、複数のプロジェクトをまとめて表示できます。

## Spec Workflow MCP で仕様を作り承認する流れ

### チャットで頼む

エージェントのチャットで、自然な言葉で頼みます（README の例）。

```text
Create a spec for user authentication
List my specs
Execute task 1.2 in spec user-auth
```

エージェントは、MCP サーバーが提供する手順の説明に従って、要件（requirements）→ 設計（design）→ タスク（tasks）の順に文書を作ります。

### 承認の流れ

文書を作ると、承認の依頼が自動で出ます。人間はダッシュボードか VS Code 拡張で文書を読み、次のどれかを選びます（[User Guide](https://github.com/Pimzino/spec-workflow-mcp/blob/main/docs/USER-GUIDE.md)）。

| 操作（画面の表示） | 日本語 | 意味 |
| --- | --- | --- |
| Approve | 承認 | そのまま受け入れる |
| Request Changes | 修正依頼 | コメントを付けて修正を求める |
| Reject | 却下 | 要件からやり直す |

修正を求めると、エージェントが文書を直して再び承認を依頼します。承認された文書をもとに、次の段階へ進みます。チャットの中で「OK」と返すのではなく、**専用の画面で承認の記録が残る** のが、このツールのいちばんの特徴です。

### 提供する MCP ツール

現在のソースで登録されている MCP ツールは次の 5 つです。

| ツール | 役割 |
| --- | --- |
| `spec-workflow-guide` | 仕様の作り方の手順を説明する |
| `steering-guide` | steering 文書の作り方を説明する |
| `spec-status` | 仕様の状態を返す |
| `approvals` | 承認の依頼と状態を扱う |
| `log-implementation` | タスクの実装記録を残す |

ドキュメントのツール一覧（TOOLS-REFERENCE.md）には、これより多くのツールが載っていますが、現在のソースとは合っていません。ドキュメントの更新が追いついていない可能性があります。

## 作られるファイル

仕様はプロジェクトの `.spec-workflow/` の下に作られます。

| 置き場所 | 内容 |
| --- | --- |
| `.spec-workflow/specs/<仕様名>/` | `requirements.md`、`design.md`、`tasks.md` |
| `.spec-workflow/steering/` | プロジェクト全体の知識（`product.md`、`tech.md`、`structure.md`） |
| `.spec-workflow/templates/` | 文書のテンプレート（独自のものに差し替えられる） |
| `.spec-workflow/archive/` | 完了した仕様の保管先 |

steering 文書は「Create steering documents for my project」のように頼むと作られます。仕様の文書構成（requirements・design・tasks と steering の 3 ファイル）は Kiro とよく似ています。

## ダッシュボードと VS Code 拡張

### Web ダッシュボード

Web ダッシュボードでは、次の情報の確認と操作ができます。

- プロジェクトの概要（進行中の仕様、タスクの数、完了率、最近の動き）
- 仕様ごとの進み具合と、要件・設計・タスクの各文書
- タスクの一覧と、そのタスクを実装させるプロンプトをコピーするボタン
- 承認の操作（承認・修正依頼・却下とコメント）

画面は WebSocket でリアルタイムに更新されます。既定では `127.0.0.1` で待ち受け、外部からは接続できません。

### VS Code 拡張

VS Code の拡張「[Spec Workflow MCP](https://marketplace.visualstudio.com/items?itemName=Pimzino.spec-workflow-mcp)」を入れると、Web ダッシュボードとほぼ同等の画面をサイドバーで使えます。承認・却下・修正依頼のほか、仕様のアーカイブといった、Web ダッシュボードにはない機能もあります。

```bash
code --install-extension Pimzino.spec-workflow-mcp
```

## 使う前に知っておきたい注意点

導入する前に、次の点を確かめておくことをおすすめします。

- **メンテナンスが休止中**
    - README の冒頭に、作者が個人的な理由でしばらくリポジトリから離れている、との記載
    - 最後の push は 2026 年 7 月
- **npm の版と CHANGELOG が合っていない**
    - npm の最新：2.2.5（2026 年 3 月）。`@latest` で入るのはこちら
    - CHANGELOG の最新：2.2.7（2026 年 5 月）。2026 年 11 月 13 日時点で npm には未公開
    - 2.2.7 の主な修正：承認のカテゴリでのパストラバーサルの修正、依存ライブラリ（simple-git）の深刻な脆弱性への対応
- **ダッシュボードは HTTPS と認証を持たない**
    - README のセキュリティの表でも、HTTPS と利用者の認証は未実装
    - 既定の `127.0.0.1` のまま使い、外部には公開しないこと
- **ドキュメントの一部が古い**
    - ツール一覧やポートの説明に、現在の実装と合わない記述がある

承認を画面で記録できる仕組みは魅力ですが、業務で使うなら、上の点を踏まえてリスクを判断してください。

## Kiro・cc-sdd・Spec Kit・OpenSpec との違い

| 項目 | Spec Workflow MCP | Kiro | cc-sdd | Spec Kit | OpenSpec |
| --- | --- | --- | --- | --- | --- |
| 形態 | MCP サーバー | 専用の AI 開発環境 | エージェントのスキル | CLI ＋ スラッシュコマンド | エージェントのスキル |
| ライセンス | GPL-3.0 | 商用製品 | MIT | MIT | MIT |

承認の記録を画面で残したい、MCP に対応したエージェントならどれでも同じように使いたい、という場合に Spec Workflow MCP が合います。ただし、前の節の注意点を踏まえて判断してください。ほかのツールは、それぞれの紹介記事を参照してください。

- [cc-sdd とは？ Claude Code・Codex で Kiro 式の仕様駆動開発を回すスキルと使い方](/blogs/posts/2026/11/cc-sdd-intro/)
- [GitHub Spec Kit とは？ 仕様駆動開発のコマンド・constitution と Kiro との違い](/blogs/posts/2026/11/github-spec-kit-intro/)
- [OpenSpec とは？ 仕様駆動開発の使い方・/openspec-* スキルと Spec Kit・Kiro との違い](/blogs/posts/2026/05/openspec-spec-driven-development/)

## まとめ

- Spec Workflow MCP は、要件 → 設計 → タスクの仕様づくりを支える MCP サーバーで、ライセンスは GPL-3.0
- `claude mcp add` や各エージェントの MCP 設定に追加して使い、ダッシュボードは `--dashboard` で別に起動する
- 文書ごとに承認の依頼が出て、ダッシュボードや VS Code 拡張で承認・修正依頼・却下を選べる
- 仕様は `.spec-workflow/` の下に、Kiro とよく似た構成で作られる
- メンテナンスが休止中で、npm の版には最新の脆弱性修正が入っていない。使う前にリスクを判断する
