---
title: "OpenSpec — 仕様駆動開発でVibe Codingの「あとから全部作り直し」を防ぐ"
date: 2026-05-14
lastmod: 2026-05-14
slug: "openspec-spec-driven-development"
draft: false
source_url: "https://github.com/hdknr/blogs/issues/1#issuecomment-4447281857"
categories: ["AI/LLM"]
tags: ["OpenSpec", "仕様駆動開発", "SDD", "claude-code", "コンテキストエンジニアリング"]
---

## はじめに

「AIにコードを書かせるのは得意になったが、完成品が要件とずれていて全部作り直しになった」——そんな経験はないだろうか。

**Vibe coding**（感覚的なプロンプトだけでAIにコーディングさせるスタイル）は手軽な反面、AIとの認識齟齬が後から発覚してリワークが発生するリスクをはらんでいる。

**OpenSpec** は、その問題を「仕様駆動開発（SDD: Spec-Driven Development）」で解消するフレームワークだ。2025年8月に登場してから急速に普及し、2026年5月時点で⭐50,000超を獲得している。

- GitHub: [Fission-AI/OpenSpec](https://github.com/Fission-AI/OpenSpec)
- npm: `@fission-ai/openspec`
- ライセンス: MIT

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
→ built for brownfield （既存プロジェクトにも対応）
→ scalable from personal projects to enterprises
```

## 主要コマンド（`/opsx:*` スラッシュコマンド）

OpenSpecは `/opsx:propose` から始まる一連のスラッシュコマンドで動作する。

```text
# 機能を提案→仕様生成
You: /opsx:propose add-dark-mode
AI:  Created openspec/changes/add-dark-mode/
     ✓ proposal.md  — なぜやるか、何が変わるか
     ✓ specs/       — 要件とシナリオ
     ✓ design.md    — 技術的アプローチ
     ✓ tasks.md     — 実装チェックリスト
     Ready for implementation!

# 仕様に従って実装
You: /opsx:apply
AI:  Implementing tasks...
     ✓ 1.1 Add theme context provider
     ✓ 1.2 Create toggle component
     ✓ 2.1 Add CSS variables
     ✓ 2.2 Wire up localStorage
     All tasks complete!

# アーカイブして次へ
You: /opsx:archive
AI:  Archived to openspec/changes/archive/2025-01-23-add-dark-mode/
     Specs updated. Ready for the next feature.
```

`/opsx:propose` で要件を入力するだけで、AIが提案書・仕様書・設計書・タスクリストを自動生成する。人間はそれをレビューして合意した上で実装に進む。

## インストールと初期化

Node.js 20.19.0 以上が必要。

```bash
# グローバルインストール
npm install -g @fission-ai/openspec@latest

# プロジェクトディレクトリで初期化
cd your-project
openspec init

# AIに伝える
/opsx:propose <作りたいもの>
```

pnpm・yarn・bun・nixにも対応している。

## 対応ツール

30種類以上のAIツールに対応しており、主なものは以下のとおり。

- **Claude Code** (Anthropic)
- **Codex** (OpenAI)
- **Cursor**
- **GitHub Copilot**
- その他多数（[対応ツール一覧](https://github.com/Fission-AI/OpenSpec/blob/main/docs/supported-tools.md)）

推奨モデルは高推論モデル（OpenAI Codex / gpt-5.5、Anthropic Claude Opus 4.7）。

## 他のスペックフレームワークとの比較

| | OpenSpec | Spec Kit (GitHub) | Kiro (AWS) |
|---|---|---|---|
| 学習コスト | 低 | 高（Pythonセットアップ等） | 中 |
| フェーズゲート | なし（流動的） | 厳格 | あり |
| ツール縛り | なし（30種類以上） | なし | AWS Kiro IDEのみ |
| モデル縛り | なし | なし | Amazon Bedrock上のモデルのみ |

OpenSpecの強みは「軽量さ」と「ツールの自由度」。既存プロジェクトへの導入もしやすい。

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
| **AIのコンテキスト戦略が手動** | 「どの docs を読ませるか」を毎回人間が判断 | スラッシュコマンドが「コンテキストクリア → 該当 change だけ読む」を強制 |

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
2. **AI に実装を任せる比率が増えたとき** — `tasks.md` のチェックリストで進捗が機械可読になり、`/opsx:apply` で一気通貫の自動実装が可能になる
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

**ポイントは「規約はリポジトリに、依頼は短く」**。Issue にルール全文を毎回コピペするのではなく、リポジトリ内の固定ファイルとして外出しする。これは `CLAUDE.md` / `AGENTS.md` / `openspec/AGENTS.md` と同じパターンで、

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
- 後から OpenSpec を導入する場合も、`docs-structure.md` は `openspec/AGENTS.md` に変換しやすい

この形にしておくと、プロジェクトが育っても OpenSpec を導入するかどうかは選択肢として残しつつ、AI コーディング時代の最低限の構造は最初から確保できる。

## まとめ

| ポイント | 内容 |
|---|---|
| 課題 | Vibe codingでは要件齟齬が後から発覚しやすい |
| 解決策 | 仕様書（proposal/specs/design/tasks）を先に合意してから実装 |
| ツール | OpenSpec (`@fission-ai/openspec`) |
| 対応環境 | Claude Code・Codex・Cursor 他30種類以上 |
| 導入コスト | `npm install -g @fission-ai/openspec` で即日導入可能 |

仕様書を先に書く。それだけでAIの出力品質が桁違いに変わる。OpenSpecはこの単純な原則をツールとして具体化したプロジェクトだ。AIコーディングを本格的に活用したい開発者にとって、試す価値は十分にある。
