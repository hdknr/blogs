---
title: "OpenSpec とは？ 仕様駆動開発の使い方・/openspec-* スキルと Spec Kit・Kiro との違い"
date: 2026-05-14
lastmod: 2026-11-13
slug: "openspec-spec-driven-development"
draft: false
source_url: "https://github.com/hdknr/blogs/issues/1#issuecomment-4447281857"
categories: ["AI/LLM"]
tags: ["OpenSpec", "仕様駆動開発", "SDD", "AI駆動開発", "claude-code"]
---

> **2026-11-13 更新:** OpenSpec v2.0.0（2026 年 11 月 11 日リリース）で `/opsx:*` のスラッシュコマンドが廃止され、`/openspec-*` のスキルに置き換わった。使い方・インストール方法・対応ツール・比較表を最新の情報に合わせて書き直し、仕様の差分（delta spec）と v1.x からの移行の節を追加した。

## はじめに

「AIにコードを書かせるのは得意になったが、完成品が要件とずれていて全部作り直しになった」——そんな経験はないだろうか。

**Vibe coding**（感覚的なプロンプトだけでAIにコーディングさせるスタイル）は手軽な反面、AIとの認識齟齬が後から発覚してリワークが発生するリスクをはらんでいる。

**OpenSpec** は、その問題を「[仕様駆動開発（SDD: Spec-Driven Development）](/blogs/posts/2026/11/spec-driven-development-overview/)」で解消するフレームワークだ。2025 年 8 月にリポジトリが公開されてから急速に普及し、2026 年 11 月時点で GitHub のスターは 7 万を超えている。

- GitHub: [Fission-AI/OpenSpec](https://github.com/Fission-AI/OpenSpec)
- ドキュメント: [openspec.dev](https://openspec.dev/docs/)
- npm: `@fission-ai/openspec`
- ライセンス: MIT

要点は次の 3 つ。

- OpenSpec は、Claude Code などの既存のエージェントに追加する、軽量な SDD ツールである
- `/openspec-propose` → `/openspec-apply-change` → `/openspec-archive-change` の 3 ステップで進む
- 変更を差分（delta spec）で扱うので、既存のプロジェクトにも導入しやすい

## Vibe Codingの落とし穴

AIコーディングアシスタントは非常に強力だが、要件がチャット履歴の中にしか存在しない場合、出力は予測不能になりやすい。よくある失敗パターンは次のとおり。

- 「ざっくり作って」と頼んだら意図と全く異なる設計になった
- 途中で要件変更を伝えたら、AIが古い前提を引きずった
- 長いセッションでコンテキストが失われ、最初の仕様が無視された

OpenSpecはこれを「コードを書く前にAIと仕様に合意する」プロセスを導入することで防ぐ。

## OpenSpecとは

OpenSpecは、AIコーディングアシスタント向けの軽量な仕様レイヤーを提供するフレームワーク。プロジェクトに `openspec/` ディレクトリを作り、変更ごとに **proposal・specs・design・tasks** の4つのアーティファクトを生成・管理する。

**設計哲学:**

```text
→ fluid not rigid      （柔軟、固定フェーズなし）
→ iterative not waterfall （反復的、ウォーターフォールではない）
→ easy not complex     （シンプル）
→ built for brownfield not just greenfield （新規だけでなく既存プロジェクトにも対応）
→ scalable from personal projects to enterprises
```

## OpenSpec の使い方：`/openspec-*` スキルと基本の流れ

OpenSpec は、AI コーディングアシスタントに追加する **スキル**（エージェントが呼び出せる手順書のようなもの）で動作する。v2.0.0 からはスキルが `.agents/skills/` に置かれる。

どのスキルを入れるかは「プロファイル」で切り替える。既定の `core` プロファイルで使えるのは次の 6 つだ（詳細は [Skills](https://openspec.dev/docs/skills)）。

| スキル | 役割 |
|---|---|
| `/openspec-explore` | 変更として提案する前に、アイデアを検討する |
| `/openspec-propose` | 変更を提案し、4 つのアーティファクト（proposal・specs・design・tasks）をまとめて生成する |
| `/openspec-apply-change` | 提案した変更のタスクを実装する |
| `/openspec-update-change` | アーティファクトを修正する |
| `/openspec-sync-specs` | アーカイブせずに、変更の仕様を `openspec/specs/` に反映する |
| `/openspec-archive-change` | 完了した変更をアーカイブに移す |

Codex では `/` の代わりに `$openspec-propose` のように呼ぶ。

### 基本の 3 ステップ

流れは、提案 → 実装 → アーカイブの 3 ステップ。エージェントのチャット欄で、次の順に実行する。

```text
/openspec-propose add-dark-mode
/openspec-apply-change
/openspec-archive-change
```

`/openspec-propose` で作りたいものを伝えると、`openspec/changes/add-dark-mode/` に次のファイルが作られる。人間はそれをレビューして合意した上で実装に進む。

| ファイル | 内容 |
|---|---|
| `proposal.md` | なぜやるか、何が変わるか |
| `specs/` | 要件とシナリオ（変更分） |
| `design.md` | 技術的アプローチ |
| `tasks.md` | 実装チェックリスト |

アーカイブすると、変更のフォルダは `openspec/changes/archive/YYYY-MM-DD-<変更名>/` に移る。同時に、変更分の仕様が `openspec/specs/` の仕様に統合される。

### 追加のスキルとプロファイル

既定の 6 つのほかに、次のようなスキルもある。

- `/openspec-continue-change`：アーティファクトを 1 つずつ作る
- `/openspec-verify-change`：実装がアーティファクトと合っているかを確かめる（報告だけで、変更はしない）

これらは既定では入っていない。プロファイルで選んでから、各プロジェクトでスキルを入れ直す。

```bash
openspec config profile   # 使うスキルを選ぶ
openspec update           # 各プロジェクトでスキルを入れ直す
```

### 仕様の差分（delta spec）

`specs/` に書くのは、仕様全体ではなく **変更分（差分）** だ。追加・変更・削除・名前の変更を見出しで分けて書く。次は書式を示すための例（文面は説明用に作ったもの）。

```markdown
## ADDED Requirements

### Requirement: Theme selection
The system SHALL allow users to choose between light and dark themes.

#### Scenario: User toggles dark mode
- **WHEN** the user selects dark mode
- **THEN** the interface switches to the dark theme
```

見出しは `## ADDED Requirements`・`## MODIFIED Requirements`・`## REMOVED Requirements`・`## RENAMED Requirements` を使う。要件には少なくとも 1 つの `#### Scenario:` が必要で、`openspec validate` で形式を確かめられる。

既存のコードに手を入れる変更でも変わる部分だけを書けばよいので、既存プロジェクト（brownfield）にも導入しやすい。

## インストールと初期化

インストールスクリプトを使えば、Node.js がなくても入れられる（[Installation](https://openspec.dev/docs/installation)）。

```bash
# macOS / Linux（スタンドアロン版）
curl -fsSL https://openspec.dev/cli/install.sh | sh

# npm で入れる場合（Node.js 22.12.0 以上が必要）
npm install -g @fission-ai/openspec@latest

# プロジェクトディレクトリで初期化
cd your-project
openspec init
```

Windows は PowerShell の `irm https://openspec.dev/cli/install.ps1 | iex` で入れられる。Homebrew（`brew install openspec`）・pnpm・yarn・bun・Nix にも対応している。

初期化したら、エージェントで `/openspec-propose <作りたいもの>` を実行する。

### v1.x（`/opsx:*`）からの移行

v1.x では `/opsx:propose`・`/opsx:apply`・`/opsx:archive` のようなスラッシュコマンドを使っていた。v2.0.0 でこれらは廃止され、`/openspec-propose`・`/openspec-apply-change`・`/openspec-archive-change` などのスキルに置き換わった。

v1.x から使っているプロジェクトでは、`openspec update` を実行する。古いバージョンが作ったファイルが整理され、新しいスキルに入れ替わる。

### テレメトリの無効化

OpenSpec は、匿名の利用統計（コマンド名とバージョンのみ）を収集する。`openspec config set telemetry.enabled false` か、環境変数 `OPENSPEC_TELEMETRY=0` で無効にできる。

## 対応ツール（Claude Code・Codex・Cursor など）

README では「30 種類以上」とされ、[対応ツールの一覧](https://openspec.dev/docs/supported-tools)には 40 を超えるツールが並んでいる。主なものは以下のとおり。

- **Claude Code** (Anthropic)
- **Codex** (OpenAI)
- **Cursor**
- **GitHub Copilot**
- **Gemini CLI**
- **Kiro**

README では、計画と実装の両方に高推論モデル（Codex 5.5 と Opus 4.7）を推奨している。

## Spec Kit・Kiro との違い

| | OpenSpec | Spec Kit (GitHub) | Kiro (AWS) |
|---|---|---|---|
| 形態 | 既存のエージェントに追加する | 既存のエージェントに追加する | 専用の AI 開発環境（IDE・CLI・Web など） |
| 導入 | インストールスクリプト 1 行か npm | Python 3.11 以上と uv / pipx | Kiro 自体をインストール |
| 進め方 | 提案 → 実装 → アーカイブ（固定フェーズなし） | 原則 → 仕様 → 計画 → タスク → 実装 | 要件 → 設計 → タスク → 実装（承認を省く Quick Spec もある） |
| 使えるエージェント | 30 種類以上（一覧では 40 超） | 40 種類以上 | —（専用環境） |
| モデル | エージェントに依存 | エージェントに依存 | Kiro が提供するモデル（Claude・OpenAI・オープンウェイトなど） |

OpenSpec の README は、Spec Kit を「徹底しているが重い（厳格なフェーズゲート、大量の Markdown、Python のセットアップ）」と評している。Kiro については「強力だが IDE に縛られ、Claude のモデルに限られる」とする。ただし 2026 年 11 月時点の Kiro は、CLI や Web からも使え、Claude 以外のモデルも選べる。OpenSpec 自身による比較なので、割り引いて読むとよい。

そのうえで筆者の見立てを言えば、OpenSpec の強みは「軽量さ」と「ツールの自由度」だ。固定フェーズがなく、変更を差分で扱うので、既存プロジェクトにも導入しやすい。

Kiro の機能と料金の詳細は「[Kiro とは？ AWS の仕様駆動 AI IDE の Spec・Steering・Hooks と料金プラン](/blogs/posts/2026/11/kiro-ai-ide-intro/)」、Spec Kit のコマンドと原則（constitution）は「[GitHub Spec Kit とは？ 仕様駆動開発のコマンド・constitution と Kiro との違い](/blogs/posts/2026/11/github-spec-kit-intro/)」を参照。

## コンテキストエンジニアリングの標準化

OpenSpecが注目されるもう一つの理由が、**コンテキストエンジニアリングの標準化**だ。

AIコーディングアシスタントが失敗する根本原因の多くは「コンテキスト管理の失敗」にある。長いセッションで仕様が揮発したり、複数ファイルの変更で前提が食い違ったりする。

OpenSpecは変更ごとに `openspec/changes/<feature>/` 以下にアーティファクトを整理することで、AIが常に正しい文脈で作業できる環境を維持する。「コンテキストを毎回クリアしてから実装を開始する」というベストプラクティスも公式に推奨されている。

## 既存の「docs/ に仕様書を書かせてからレビュー → 実装」運用との比較

OpenSpec を導入していなくても、すでに **「docs/ フォルダに mkdocs などで仕様書を書かせ、人間がレビューしてから実装に入る」** 運用をしている開発者は多い。これは Spec-Driven Development の原則そのものであり、本質的には正しい方向を向いている。

ではそのうえで OpenSpec を使う意味はあるのか。両者を比較すると、現状方式で解きにくい「2つの本質的な問題」が見えてくる。

| 問題 | docs/ + mkdocs 方式 | OpenSpec の解 |
|---|---|---|
| **why / what / how / do の混在** | 1つの仕様書に動機・要件・設計・タスクが混ざりがち | `proposal.md` / `specs/` / `design.md` / `tasks.md` で物理分離 |
| **AIのコンテキスト戦略が手動** | 「どの docs を読ませるか」を毎回人間が判断 | 変更ごとのフォルダにアーティファクトがまとまる（README は実装前のコンテキストのクリアも推奨） |

> **補足: 「変更履歴」は git で足りる**
>
> docs/ を git 管理している場合、変更履歴自体は commit log・PR description・issue で十分に残る。OpenSpec の `archive/` が git に対して優位なのは、(1) 機能単位の物理隔離(PR と機能は必ずしも 1:1 ではない)、(2) AI から読みやすい固定パスにアーティファクトが置かれる、(3) 完了時点のスナップショットが上書きされない、の3点に絞られる。「変更履歴を残すため」を OpenSpec 採用の主理由にするのは弱い。

### docs/ + mkdocs 方式の強み

逆に現状方式にも、OpenSpec にはない強みがある。

- **公開ドキュメントと AI 用仕様書を同居できる** — `openspec/` は AI のワーキングメモリで、人間が読む前提では設計されていない
- 自由度が高く、認知負荷ゼロで継続できる
- mkdocs の検索性は AI のコンテキスト探索とも相性がよい

### OpenSpec が効いてくる閾値

逆に言えば、次の状況に達したときに OpenSpec の導入価値が跳ね上がる。

1. **複数機能を並行開発するようになったとき** — docs/ がフラットだと AI が読むべき範囲を絞れないが、`changes/<feature>/` は機能単位で物理隔離される
2. **AI に実装を任せる比率が増えたとき** — `tasks.md` のチェックリストで進捗が機械可読になり、`/openspec-apply-change` で一気通貫の自動実装が可能になる
3. **why/what/how/do を1ファイルに書き散らかして AI が混乱し始めたとき** — 4アーティファクト分離は単なる整理整頓ではなく、AI のコンテキスト窓を節約する仕組みとして効く

### 折衷案: docs/ 上で OpenSpec の構造だけ真似る

OpenSpec を全採用しなくても、**「変更単位で隔離する」「tasks.md でチェックリスト化する」** の2点だけ docs/ 配下に取り込むと、現状方式の弱点が8割埋まる。

```text
docs/
├── changes/
│   ├── 2026-05-26-add-dark-mode/
│   │   ├── proposal.md   # なぜやるか
│   │   ├── design.md     # 技術的アプローチ
│   │   └── tasks.md      # 実装チェックリスト
│   └── archive/
│       └── 2026-04-10-add-search/
└── specs/                # 最新の正(specs はここに集約)
```

つまり「OpenSpec をフレームワークとして導入する」より、**「OpenSpec の構造を mkdocs 上で真似る」** ほうが、すでに docs/ 運用が回っているプロジェクトには合っている。OpenSpec を導入するかどうかの判断は「フレームワークを入れるか」ではなく、「変更単位の隔離と why/what/how/do の物理分離を、自分のプロジェクトに取り込むか」で考えるとよい。

### 実践例: docs-structure.md + GitHub Issue で初期化する

mkdocs ベースで開発を始めるとき、リポジトリ作成直後の典型的なフローはこうなる。

1. main ブランチで `PLAN.md` にプロジェクトの目的・手段・要件を記載
2. リポジトリルートに **`docs-structure.md`** を置いてルールを定義
3. GitHub Issue は「`docs-structure.md` に従って docs/ を作って」と一行で立てる
4. AI コーディングアシスタントに着手させる

**ポイントは「規約はリポジトリに、依頼は短く」**。Issue にルール全文を毎回コピペするのではなく、リポジトリ内の固定ファイルとして外出しする。これは `CLAUDE.md` / `AGENTS.md` と同じパターンで、

- 1箇所更新すれば全 Issue に伝播
- AI コーディングアシスタントが固定パスでコンテキストに投入できる
- `git log` で規約自体の変遷も追える
- Issue が肥大化しない

という利点がある。

#### ① リポジトリルートに置く `docs-structure.md`

````markdown
# docs-structure.md — 仕様書ディレクトリの規約

このリポジトリの `docs/` は mkdocs + 以下のルールで運用する。
新規プロジェクト初期化時、および新機能追加時はこのファイルに従うこと。

## ディレクトリ構造

```text
docs/
├── index.md           # PLAN.md の要約を載せる
├── specs/             # 合意済みの「最新の正」を集約
│   └── .gitkeep
└── changes/
    ├── _template/     # 新規 change 作成時にコピーする雛形
    │   ├── proposal.md
    │   ├── design.md
    │   └── tasks.md
    ├── archive/       # 実装完了した change の保管先
    │   └── .gitkeep
    └── .gitkeep
```

## アーティファクトの責務

| ファイル | 役割 | 書く内容 |
|---|---|---|
| `proposal.md` | Why | 背景・課題、提案する変更、スコープ外、関連 issue/PR |
| `design.md` | How | 採用するアプローチ、代替案と却下理由、依存・前提、影響範囲 |
| `tasks.md` | Do | 実装チェックリスト(`- [ ]` 形式、機械可読) |
| `specs/` 配下 | What(最新の正) | 合意済みの要件・仕様 |

1ファイル内で why/how/do を混在させない。

## 運用フロー

1. 新機能を追加するときは `docs/changes/YYYY-MM-DD-<feature>/` を作り、`_template/` からコピーする
2. **proposal → design → tasks の順で人間がレビュー**してから実装に入る
3. 実装完了後、当該ディレクトリを `docs/changes/archive/` に移送し、`docs/specs/` を更新する
4. AI に作業させるときは **「該当 change のディレクトリだけ」をコンテキストに入れる**(他の change のファイルは読ませない)
5. `docs/specs/` は常に「最新の正」のみを置く。履歴は archive と git に任せる

## 初期化時の受け入れ条件

- [ ] `pip install mkdocs mkdocs-material` の手順が README にある
- [ ] `mkdocs.yml` がプロジェクト直下にある
- [ ] `mkdocs serve` でローカル閲覧できる
- [ ] `docs/specs/` `docs/changes/` `docs/changes/archive/` `docs/changes/_template/` が初期化されている
- [ ] `_template/` に proposal.md / design.md / tasks.md が配置されている
- [ ] (任意) `mkdocs build --strict` が CI に組み込まれている

## なぜこの構造にするのか

- **変更単位の物理隔離** — 並行開発で AI が読むべき範囲が `docs/changes/<feature>/` に絞られる
- **why/what/how/do の分離** — 1ファイル混在による AI の混乱を防ぐ
- **コンテキスト戦略の標準化** — 「change ディレクトリだけ読ませる」が運用ルールとして明文化される
- 履歴は git の commit log・PR・issue で十分残るため、archive は AI から読みやすい位置に固定する目的に絞る
````

#### ② GitHub Issue 本文(短縮版)

```markdown
## 課題
`docs-structure.md` のルールに従って、`docs/` 以下に mkdocs で仕様書を作ってください。

## 前提
- `PLAN.md` にプロジェクトの目的・手段・要件は記載済み
- main ブランチで作業

## 完了条件
- [ ] `docs-structure.md` の「初期化時の受け入れ条件」をすべて満たしている
- [ ] PR を出す
```

Issue はこれだけ。後続の「機能 X を追加」系の Issue も「`docs-structure.md` に従って `docs/changes/YYYY-MM-DD-feature-x/` を作って」の一行で発注できる。

#### 注意点

- **`docs-structure.md` 自体が「契約」になる**ので、曖昧さは AI が文字通り解釈して事故る。受け入れ条件は機械的に判定できる形で書く
- **`PLAN.md` と `docs-structure.md` の責務分離を明確に** — `PLAN.md` は「何を作るか」、`docs-structure.md` は「どう書くか」
- 後から OpenSpec を導入する場合も、`changes/` と `specs/` の構造が同じなので移行しやすい

この形にしておくと、プロジェクトが育っても OpenSpec を導入するかどうかは選択肢として残しつつ、AI コーディング時代の最低限の構造は最初から確保できる。

## まとめ

| ポイント | 内容 |
|---|---|
| 課題 | Vibe codingでは要件齟齬が後から発覚しやすい |
| 解決策 | 仕様書（proposal/specs/design/tasks）を先に合意してから実装 |
| ツール | OpenSpec (`@fission-ai/openspec`) |
| 対応環境 | Claude Code・Codex・Cursor・Kiro など 30 種類以上（一覧では 40 超） |
| 使い方 | `/openspec-propose` → `/openspec-apply-change` → `/openspec-archive-change` |
| v2.0.0 の変更 | `/opsx:*` から `/openspec-*` スキルへ（v1.x からは `openspec update` で移行） |
| 導入コスト | インストールスクリプトか `npm install -g @fission-ai/openspec` で即日導入可能 |

仕様書を先に書く。それだけでAIの出力品質が桁違いに変わる。OpenSpecはこの単純な原則をツールとして具体化したプロジェクトだ。AIコーディングを本格的に活用したい開発者にとって、試す価値は十分にある。
