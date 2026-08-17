---
title: "Claude Code から個人 Obsidian Vault に「書き戻す」設計 — inbox-first / Daily Note / ADR 二重書きの3パターン"
date: 2026-05-18
lastmod: 2026-05-18
slug: "claude-code-obsidian-vault-writeback"
draft: false
description: "プロジェクトで得た知見を個人 Obsidian Vault に循環させるための、Claude Code 側の書き戻し（writeback）設計をまとめる。inbox-first を基本に、サマリスキル・Daily Note 追記・ADR 二重書きの3パターンを、permissions と週次レビュー運用まで含めて解説。"
categories: ["AI/LLM"]
tags: ["claude-code", "Obsidian", "mcp", "Skills", "CLAUDE.md", "ADR", "Daily Notes", "writeback", "inbox-first", "permissions", "ナレッジマネジメント", "PKM"]
---

[Obsidian Vault を Claude Code に繋ぐ実践編](/blogs/posts/2026/05/claude-code-obsidian-vault-project-config/) では、**読み取り側**（Vault → プロジェクト）の設定パターンを整理しました。本記事はその続編で、**書き戻し（writeback）側**（プロジェクト → Vault）の設計を扱います。

ここを設計しないと、Vault は「過去の自分が書いたノート集」のまま古びていきます。プロジェクトで詰まったこと・学んだこと・設計判断の根拠が Vault に還流して初めて、AI Agent が「3 ヶ月前のあの話、応用できないか？」を提案できるようになります。

## 書き戻し設計で外せない3つの原則

具体的なパターンに入る前に、絶対に外せないルールを確認します。

1. **AI に Vault の正本（`topics/` や `projects/` の本文）を直接書かせない**
   Obsidian の `[[リンク]]` 構造とノート間の整合は、人間が編集してきた歴史の積み重ねです。AI に直接書かせると、リンク切れ・重複ノート・タグ揺れが一気に発生します。
2. **`inbox/` を必ず噛ませる**
   AI は `~/Documents/ObsidianVault/inbox/` にしか書かない。`inbox/` は「下書き置き場」と割り切り、人間が後で内容を吟味して Vault 本体に統合します。
3. **書き戻す対象は「リポジトリに収まらない知見」だけ**
   コードや設計書はリポジトリの `docs/` に書きます。Vault に書くのは、**プロジェクトを跨いで再利用される可能性のあるメタ知識** だけです。

つまり「AI が `inbox/` に下書きを溜める → 人間が週次レビューで Vault 本体に統合する」という二段階フローを基本形にします。AI は下書き工場、人間は編集長、という分業です。

## permissions と MCP の分離設計

書き戻しを安全に行う最大のコツは、**読み取り用 MCP と書き込み用 MCP を別サーバとして分離する** ことです。[前作で触れた permissions 設計](/blogs/posts/2026/05/claude-code-obsidian-vault-project-config/) を一段深めます。

```bash
# 読み取り専用ルート: Vault 全体を grep / Read できるが書き込みは禁止したい
claude mcp add -s local vault-readonly -- \
  npx -y @modelcontextprotocol/server-filesystem ~/Documents/ObsidianVault

# 書き込み用: inbox/ 限定で AI が書ける
claude mcp add -s local vault-inbox -- \
  npx -y @modelcontextprotocol/server-filesystem ~/Documents/ObsidianVault/inbox
```

これに加えて、`<proj>/.claude/settings.json` 側で symlink 越しの書き込みを禁止しておきます（前作で作った `<proj>/.claude/knowledge/` — Vault のサブセットを symlink した読み取り専用ディレクトリ — を経由する書き込みを塞ぐ目的）。

```jsonc
{
  "permissions": {
    "deny": [
      "Write(.claude/knowledge/**)",
      "Edit(.claude/knowledge/**)"
    ]
  }
}
```

CLAUDE.md には次のように明示します。

```markdown
## Vault への書き戻し

- 書き込みは必ず `vault-inbox` MCP サーバ経由で行う。
- 書き戻し先は `~/Documents/ObsidianVault/inbox/` 配下のみ。
- 既存ノート（`topics/`, `projects/`, Daily Notes など）への直接編集は禁止。
```

> `@modelcontextprotocol/server-filesystem` は引数で渡したディレクトリ配下を書き込みも含めて扱えるため、**サーバ単位で「見せたい範囲」を絞る** のが最も簡単な防御です。このサーバは起動時引数のディレクトリ配下しか FS ツリーとして公開しないため、`vault-readonly` セッションから見ると `inbox/` のパスはそもそも解決できず、書きようがありません。読み取り MCP と書き込み MCP を別サーバとして立てることが、構造的な「物理隔離」になります。

## パターン1: AI スキルで都度サマリを inbox に吐く（最も汎用）

PR 作成時やセッション終了時に明示的に呼ぶ、プロジェクト固有スキルです。文脈が最も濃いタイミング（議論が決着した直後）で要点だけ抽出して書き戻します。

`<proj>/.claude/skills/summary-back-to-vault/SKILL.md`:

````markdown
---
name: summary-back-to-vault
description: 今回のセッションから「他プロジェクトでも再利用できそうな知見」だけを抜き出し、個人 Vault の inbox に Markdown として書き出す
---

## 手順

1. 直近の会話・PR・diff から、次に当てはまる項目だけを抽出する:
   - 設計判断とその根拠（ADR 級）
   - 詰まった点と回避策（gotcha）
   - 他プロジェクトでも使い回せそうなパターン・コマンド
2. 次の構造で Markdown を作る:

   ```
   ---
   date: YYYY-MM-DD
   source_project: <repo-name>
   source_pr: <PR URL>
   tags: [...]
   ---

   # <端的なタイトル>

   ## 状況
   ## 学んだこと
   ## 関連リンク
   ```

3. ファイル名は `YYYY-MM-DD-<slug>.md` とし、`vault-inbox` MCP サーバ経由で
   `~/Documents/ObsidianVault/inbox/` に書く。
4. 既存ファイルとの重複チェック: `vault-readonly` で `inbox/` と `topics/` を
   Grep し、同等のノートがあれば「追記候補」として人間に報告する（自動マージは禁止）。

## 書いてはいけないもの

- プロジェクト固有のコード断片（リポジトリの `docs/` に書く）
- 顧客名・認証情報・社内ドメイン用語
- 進行中タスクの ToDo（プロジェクト Issue に書く）
- 公開ドキュメントから読み取れる一般的な情報
````

このスキルを `/summary-back-to-vault` として呼び出すと、AI が会話履歴・diff・PR の議論を読み直し、再利用価値のある観点だけを `inbox/` に吐き出します。

**重複チェックを必ず入れる** のがポイントです。これがないと `inbox/` に同じトピックの似たノートが量産されてしまい、人間のレビュー負荷が爆発します。

## パターン2: Daily Note に追記する（軽量・連続的）

PR 単位でなく、日次で薄く書き戻すパターンです。Obsidian の Daily Notes プラグインと相性がよく、横断的な学習ログが自動で蓄積されます。

`~/.claude/skills/vault-daily-log/SKILL.md`:

```markdown
---
name: vault-daily-log
description: 今日の作業から「学び」を 1〜3 行で抽出し、今日の Daily Note の末尾に追記する
---

## 手順

1. 今日の日付で `~/Documents/ObsidianVault/daily/YYYY-MM-DD.md` のパスを作る。
2. ファイルが存在しない場合は Daily Note テンプレート（YAML frontmatter + `## Learned` セクション）で新規作成。
3. `## Learned` セクションに以下の形式で 1〜3 行だけ追記:
   - `<repo-name>: <一行の学び> ([PR #N](url))`
4. 同一日付に同じ PR が既に書かれていればスキップ（重複防止）。
5. このスキルは **書き込み用 MCP** 経由で実行する。原則「AI は `inbox/` にしか書かない」を守るため、Daily Notes も `~/Documents/ObsidianVault/inbox/daily/` 配下に置くか、`vault-daily` という別サーバを `daily/` 限定で立てる構成にする（既存 Vault の `daily/` を AI に直接書かせない）。
```

利点は次の3つです。

- **サマリほど重くない** — 1 行で済むので心理的コストが低い
- **日付軸で横断検索しやすい** — 「先週 Next.js で何を学んだか」を Daily Notes をスクロールするだけで思い出せる
- **Vault のリンク構造を壊さない** — Daily Notes はそもそも日次フローなので、頻繁な追記が前提

体系化されない雑多な気付きはこちらが向いています。`## Learned` のような特定見出しに **追記しかしない** ルールを徹底するのがコツです。

> セッション終了時に自動実行したい場合、Claude Code の `hooks`（`Stop` フックなど）から `vault-daily-log` を呼ぶ運用もあります。ただし「文脈の薄いセッションでもノイズが入る」副作用があるため、最初は手動呼び出し（`/vault-daily-log`）で始めて、頻度が上がってきたら hook 化する順序がおすすめです。

## パターン3: ADR（設計判断記録）の二重書き

設計判断は **リポジトリの `docs/adr/` が正本** で、Vault には **個人クロスリファレンス用のコピー** を残すパターンです。

```
<proj>/docs/adr/0042-use-bun-instead-of-node.md       ← 正本（コミット）
~/Documents/ObsidianVault/inbox/adr/0042-<proj>-use-bun.md  ← 個人参照用
```

`decision-log` スキルを作り、ADR を書くときに必ず両方に出力させます。

```markdown
---
name: decision-log
description: 設計判断（ADR）をプロジェクト docs と個人 Vault の inbox に二重書きする
---

## 手順

1. ADR テンプレート（Status / Context / Decision / Consequences）を埋める。
2. プロジェクト側に書く: `<proj>/docs/adr/NNNN-<slug>.md`
   - 番号 NNNN は `docs/adr/` の既存番号の次を採用
3. Vault 側に書く: `~/Documents/ObsidianVault/inbox/adr/NNNN-<proj-name>-<slug>.md`
   - ファイル名にプロジェクト名を含める（後で「Bun を採用したのはどのプロジェクトだっけ？」に答えやすくする）
   - 内容は本文をそのまま転記し、末尾に「正本: <repo>/docs/adr/NNNN-...」のリンクを残す
```

Vault 側のファイル名にプロジェクト名を含めるのは重要な工夫です。Vault 内で `adr-*-use-bun.md` を一覧したときに、どのプロジェクトでの判断だったかが即座にわかります。これがないと、後で見返したときに「どの文脈での Bun 採用か」を毎回開いて確認するハメになります。

## どのトリガで書き戻すか

3 つのパターンは、起動タイミングで使い分けます。

| トリガ | 適したパターン | 理由 |
| --- | --- | --- |
| **PR マージ直前** | パターン1（サマリ） | 議論が決着した直後、文脈が最も濃い瞬間 |
| **セッション終了時** | パターン2（Daily Note） | 「今日何を学んだか」を機械的に残す |
| **設計判断をした瞬間** | パターン3（ADR 二重書き） | あとから探すコストを下げる |
| **週次レビュー** | （人間が `inbox/` を promote） | 整理は人間の責務 |

「全部一度にやろう」とすると破綻するので、まずは **パターン1 だけを `/summary-back-to-vault` で手動運用** するところから始めるのが現実的です。それで Vault に書き戻しの流れができてから、Daily Note や ADR 二重書きを足していくと、運用が定着しやすくなります。

## inbox → 本棚への「昇格」運用

`inbox/` は溜まる前提なので、人間側のレビュー運用がワークフローの肝です。

**週次レビュー（15〜30 分）の手順:**

1. Obsidian で `inbox/` を開き、新規ノートを一覧する。
2. 各ノートに対して 4 つの選択肢から選ぶ:
   - **昇格**: `topics/<area>/` または `concepts/<name>/` に移動・rename し、`[[既存ノート]]` でリンクを張る
   - **追記**: 類似ノートが既にある場合、そちらに merge してから inbox 側を削除
   - **保留**: もう少し情報が溜まってから判断したい → タグ `#review-later` を付けて残す
   - **破棄**: ただの作業ログで再利用価値なし → 削除
3. 2 週間以上 `inbox/` に残っているノートはアーカイブ（`inbox/_archive/`）または削除。ただし `#review-later` タグが付いているノートは「意図的に保留中」なので archive 対象から除外し、別途月次でまとめてレビューする。

この運用にしておくと、Vault 本体は人間が手を入れたノートだけで構成され、リンクグラフが綺麗に保たれます。AI に「自動で昇格させる」役割を持たせると、ほぼ確実にリンク構造が壊れます。**昇格判断だけは人間に残す** のが、Vault を長期運用する上での生命線です。

## 書き戻すべきもの／避けるべきもの

最後に判断のチェックリストです。

**書き戻すべきもの:**

- 他プロジェクトでも同じ落とし穴に出会いそうな gotcha
- 「なぜこの設計にしたか」の意思決定の根拠
- 公式ドキュメントから読み取れない実運用での挙動
- 横断的に使えるコマンドスニペット・設定パターン

**書き戻してはいけないもの:**

- プロジェクト固有の業務ロジック（リポジトリの `docs/` で十分）
- 顧客名・認証情報・契約に関わる情報
- 進行中の ToDo（Issue で管理）
- 公開資料に既にある情報（リンクだけ Vault に残せばよい）

**判断に迷ったとき**: 「3 ヶ月後に別プロジェクトで同じ問題に出会ったとき、自分はこのノートを検索するか？」を自問してください。Yes なら書き戻す価値があります。

## まとめ

書き戻しは、Vault を「資産」に変える最後のピースです。読み取り側だけ設定しても、Vault は過去の自分の知識のスナップショットのままで、AI Agent が「過去の自分から学ぶ」現象は起こりません。

設計の肝は次の 3 点です。

- **inbox-first**: AI は `inbox/` にしか書かない。本棚は人間が編集する
- **読み取り用と書き込み用の MCP サーバを分離**: サーバ単位で「見せる範囲」を絞り、構造的に事故を防ぐ
- **書き戻すのはリポジトリに収まらないメタ知識だけ**: コードや設計書はリポジトリ、Vault は横断知識

[読み取り側の設定](/blogs/posts/2026/05/claude-code-obsidian-vault-project-config/) と組み合わせると、「Vault から AI に文脈を渡す → プロジェクトで活用する → 得た知見を inbox に書き戻す → 週次レビューで昇格」という循環が回り始めます。シリーズの最初の問題提起である [GitHubで全部完結する開発者にObsidianは本当に必要か？](/blogs/posts/2026/05/github-vs-obsidian-ai-agent/) に立ち返ると、Obsidian の価値は **「個人の知の網が AI Agent 越しに自己強化される」ループ** にあり、書き戻しの設計こそがそのループを閉じる役割を担っている、と言えます。
