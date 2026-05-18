---
title: "Obsidian Vault 書き戻しの自動化 — Claude Code hooks と Git フックと GitHub Actions の使い分け"
date: 2026-05-18
lastmod: 2026-05-18
slug: "claude-code-vault-writeback-automation"
draft: false
description: "個人 Obsidian Vault への書き戻し（writeback）を自動化する3つの方式を比較。Claude Code の hooks（PostToolUse / Stop / SessionEnd）、Git クライアントフック（post-merge）、GitHub Actions それぞれが拾えるトリガと文脈の違いを示し、推奨は『フックは器を用意し、AI が中身を書く』分業。"
categories: ["AI/LLM"]
tags: ["Claude Code", "Obsidian", "Claude Code Hooks", "PostToolUse", "GitHub Actions", "Git", "post-merge", "writeback", "automation", "Daily Notes", "ナレッジマネジメント", "PKM"]
---

[Claude Code から個人 Obsidian Vault に「書き戻す」設計]({{< ref "posts/2026/05/2026-05-18-claude-code-obsidian-vault-writeback.md" >}}) では、書き戻しの設計パターンとして `summary-back-to-vault` スキル / Daily Note 追記 / ADR 二重書きの 3 つを示しました。本記事はその続編で、**書き戻しを自動化する仕組み**を扱います。

スキルを作ったとしても、毎回 `/summary-back-to-vault` と手で打つのは続きません。トリガを自動化しない限り、書き戻しは「気が向いたときだけ」になり、Vault は古びます。本記事では Claude Code のフック・Git のクライアントフック・GitHub Actions の 3 方式を、**それぞれが拾えるトリガと文脈の違い** に着目して整理します。

## 自動化候補の俯瞰

書き戻しを発火させる場所は大きく 3 つあります。

| 方式 | トリガ位置 | セッション文脈 | 適性 |
| --- | --- | --- | --- |
| **Claude Code hooks**（`PostToolUse`, `Stop`, `SessionEnd` 他） | セッション内、ツール呼び出し前後 | ✓ 会話履歴・スキル・MCP がすべて生きている | **AI Agent と最も相性が良い** |
| **Git クライアントフック**（`post-merge`, `pre-push` など） | クライアント側、`git pull` / `git push` 等 | ✗ PR の diff だけ | Vault が Git リポジトリ化されている人向け |
| **GitHub Actions** | サーバ側、`pull_request: closed` 等 | ✗ PR メタデータのみ | マシンを開いていなくても回したい場合 |

書き戻しに必要な「**会話の文脈（なぜそう判断したか／どこで詰まったか）**」を保てるのは Claude Code フックだけです。Git フックや Actions は PR の diff と説明文しか見えないため、サマリの「中身の濃さ」が大きく落ちます。これが本記事の核心です。

## 推奨: Claude Code の `PostToolUse` フックで「促す」

「PR を `gh pr merge` した直後に、書き戻しを促す」のが一番自然なタイミングです。Claude Code のフックは `~/.claude/settings.json` または `<proj>/.claude/settings.json` に書きます。

```jsonc
// <proj>/.claude/settings.json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "~/.claude/hooks/detect-pr-merge.sh"
          }
        ]
      }
    ]
  }
}
```

`~/.claude/hooks/detect-pr-merge.sh`:

```bash
#!/usr/bin/env bash
# PostToolUse フック: 直前の Bash コマンドが PR マージなら、
# 書き戻しを促す指示をエージェントに注入する

set -euo pipefail

# 標準入力に JSON 形式でツール呼び出し情報が来る
INPUT=$(cat)
COMMAND=$(echo "$INPUT" | jq -r '.tool_input.command // ""')

if echo "$COMMAND" | grep -qE '^gh pr merge'; then
  # stdout に出した内容は、ツール結果としてエージェントの文脈に追加される
  cat <<'EOF'
[automation hint]
PR がマージされました。今回のセッションで得た「他プロジェクトでも再利用できそうな知見」を、
/summary-back-to-vault スキルで個人 Vault の inbox に書き戻してください。
EOF
fi

exit 0
```

ポイントは **フックの stdout が「ツール結果のメモ」としてエージェントの文脈に注入される** 点です。エージェントはこの行を「ユーザーの指示に近い形」で受け取るので、続けて `/summary-back-to-vault` を呼ぶ動作が自然につながります。

> **重要な制約**: フック自体はエージェントを駆動できない（次のターンを発火できない）ので、「マージ直後にエージェントが自律的にサマリを書く」のではなく、「マージ直後にサマリを書くよう **促す**」という形になります。完全自動駆動が必要な場合は、後述の GitHub Actions と組み合わせます。なお、スキル側に「マージ後に実行する」と書いてもセッションのターン境界では発火しない罠については [Claude Code のスキルで「マージ後」の指示が PR 作成中に発火する罠]({{< ref "posts/2026/05/2026-05-13-claude-skill-post-merge-trap.md" >}}) に詳しく書いてあります。フックでトリガを外出ししないと拾えない理由を、別角度から理解できます。

### `PostToolUse` フックの matcher を絞る

上の例では `"matcher": "Bash"` で全 Bash 呼び出しに反応させ、シェルスクリプト側で `gh pr merge` を検出していますが、Claude Code の matcher を使ってもっと絞ることも可能です。matcher は正規表現で書けます。

```jsonc
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          { "type": "command", "command": "~/.claude/hooks/detect-pr-merge.sh" }
        ]
      },
      {
        "matcher": "Write|Edit",
        "hooks": [
          { "type": "command", "command": "~/.claude/hooks/notify-doc-change.sh" }
        ]
      }
    ]
  }
}
```

matcher が `Bash` の場合はすべての Bash 呼び出しが対象になります。コマンド内容で絞り込みたい場合は、シェルスクリプト側で `tool_input.command` を見るのが現状最も柔軟です。

## `Stop` と `SessionEnd` の使い分け

Claude Code には会話の終端を捉えるフックが 2 つあります。役割の違いを先に整理します。

| イベント | 発火タイミング | エージェントへの指示 | 主な用途 |
| --- | --- | --- | --- |
| **`Stop`** | アシスタントが応答を終えた瞬間（毎ターン） | ✓ stdout で次ターンに hint を渡せる | 直前のターンで成果が出たとき、AI に追加作業（書き戻し本体）を促す |
| **`SessionEnd`** | セッション終了時（1 回） | ✗ もうエージェントは動かない | 純粋な事後ログ・成果物のアーカイブ |

つまり「**`Stop` は会話継続中の hint、`SessionEnd` は会話後の墓標**」と覚えると、用途を間違えません。器（ファイルの雛形）を作るのは `SessionEnd` でもよいですが、その器の中身を AI に書かせる前提なら、トリガは `Stop` 側に置く必要があります。

## 軽量パターン: `Stop` フックで Daily Note の「器」を自動作成

書き戻しの粒度が「セッションの最後に 1〜3 行のログ」で十分な場合（Daily Note 用途）は、`Stop` フックが軽量です。次のターンが続く可能性があるタイミングで器を作っておけば、エージェントに「中身を書いて」と促せます。

```jsonc
{
  "hooks": {
    "Stop": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "~/.claude/hooks/append-daily-log.sh"
          }
        ]
      }
    ]
  }
}
```

`Stop` は「アシスタントが応答を終えた瞬間」に毎回発火します。毎ターン Daily Note を書くと冗長なので、フック側で「直近の応答に意味のある成果（PR 作成、commit、ファイル編集）が含まれていたか」を判定する条件分岐を入れます。

```bash
#!/usr/bin/env bash
# Stop フック: セッションで「学び」を産んだら Daily Note の器を用意
set -euo pipefail

INPUT=$(cat)
TRANSCRIPT_PATH=$(echo "$INPUT" | jq -r '.transcript_path // ""')

# 直近のツール呼び出しに gh pr create / git commit があるかをチェック
# 注: transcript は JSONL なので、本番では jq で tool_use.input.command を
# 構造化して取り出すのが安全。下の grep は最短実装の例として割り切る。
if [[ -f "$TRANSCRIPT_PATH" ]] \
   && grep -qE '"gh pr create |"git commit ' "$TRANSCRIPT_PATH"; then

  TODAY=$(date +%Y-%m-%d)
  VAULT_INBOX="$HOME/Documents/ObsidianVault/inbox/daily/$TODAY.md"
  mkdir -p "$(dirname "$VAULT_INBOX")"

  # ファイルが無ければテンプレートで初期化
  if [[ ! -f "$VAULT_INBOX" ]]; then
    cat > "$VAULT_INBOX" <<EOF
---
date: $TODAY
---

## Learned

EOF
  fi

  # フックはあくまで「箱を用意するだけ」。中身は次回エージェントに書かせる
  echo "[automation hint] 今日の Daily Note ($VAULT_INBOX) に '## Learned' エントリを追記してください。"
fi

exit 0
```

ここでもポイントは「**フックがファイルの器を用意し、エージェントに中身を書かせる**」分業です。フック自体に Markdown 本文を書かせると、AI が読んだセッション文脈を活かせません。フックは I/O だけ、中身の判断は AI、という分担を徹底すると壊れにくいです。

## `SessionEnd` フックでログだけ取る

セッションが終わるタイミングで「このセッションで何があったか」のメタ情報だけ Vault に残したい場合は `SessionEnd` フックが使えます。前節の対比どおり、ここでは AI に追加作業を頼めないので、純粋な事後ログ用途に絞ります。

```jsonc
{
  "hooks": {
    "SessionEnd": [
      {
        "hooks": [
          { "type": "command", "command": "~/.claude/hooks/session-log.sh" }
        ]
      }
    ]
  }
}
```

`SessionEnd` の特徴は「**もうエージェントは動かないので、stdout でエージェントに指示はできない**」点です。器の用意ではなく、純粋な事後ログとして使います。たとえば、

- そのセッションで触れたリポジトリ名
- 開発に使った時間（`SessionStart` の時刻と差を取る）
- マージした PR 番号一覧

を `~/Documents/ObsidianVault/inbox/sessions/YYYY-MM-DD-HHMM.md` に追記する、という用途が向きます。後で人間がレビューするときの「何があったかの目次」になります。

## 並行案: Git の `post-merge` フック

Vault を **自分の Git リポジトリで管理している人** は、Git クライアントフックも選択肢に入ります。`post-merge` は `git merge`（および `git pull`）の直後に発火します。

```bash
#!/usr/bin/env bash
# .git/hooks/post-merge
# main ブランチに merge が反映された後だけ動く

set -euo pipefail

# 対話シェル経由の git pull だけを対象にする（CI や別スクリプトを除外）
[[ -t 1 ]] || exit 0

BRANCH=$(git rev-parse --abbrev-ref HEAD)
[[ "$BRANCH" == "main" ]] || exit 0

# 直近の merge commit の説明文
LAST_MERGE=$(git log -1 --merges --format="%B" || true)
[[ -z "$LAST_MERGE" ]] && exit 0

# ログを残し、Claude Code を headless で起動して /summary-back-to-vault を呼ぶ
# 注: 新規セッションなので「いま開いていた会話の文脈」は引き継げない
LOG_DIR="$HOME/.claude/logs"
mkdir -p "$LOG_DIR"
claude -p "/summary-back-to-vault 直近マージ: $LAST_MERGE" \
  --output-format text \
  >> "$LOG_DIR/post-merge-$(date +%Y%m%d).log" 2>&1 &
disown
```

このパターンの **弱点** は前述のとおり「会話の文脈が失われる」点です。`claude -p` は新規セッションを立ち上げるので、PR で何を議論したかは PR 本文と diff からしか読み取れません。

それでも `post-merge` が役立つ場面は、

- 自分の PC で `gh pr merge` ではなく **GitHub UI で merge** したあと、ローカルに `git pull` で反映する人
- セッションを既に閉じてしまっていて、Claude Code フックが間に合わない場合

の 2 ケースです。`PostToolUse` フックを主軸にしつつ、`post-merge` をフォールバックとして併用する構成にすると取りこぼしが減ります。

## 完全自動化: GitHub Actions で「漏れを拾う」

「マシンを開いていなくても、PR が落ちたら勝手に Vault に学びを書いてほしい」場合は、GitHub Actions で Claude API を叩く構成になります。Vault が **Git リポジトリ化** されていることが前提です。

```yaml
# .github/workflows/post-merge-summarize.yml
name: Summarize merged PR back to Vault
on:
  pull_request:
    types: [closed]

jobs:
  summarize:
    if: github.event.pull_request.merged == true
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          ref: ${{ github.event.pull_request.base.ref }}

      - name: Fetch PR diff and discussion
        env:
          GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        run: |
          gh pr view ${{ github.event.pull_request.number }} \
            --json title,body,comments,files \
            > /tmp/pr-context.json

      - name: Generate summary via Claude API
        env:
          ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
        run: |
          # ペイロードは必ず jq で組み立てる（PR 本文に " や \ が混ざっても壊れない）
          jq -n \
            --rawfile pr /tmp/pr-context.json \
            --arg model "claude-sonnet-4-6" \
            --arg sys "summary-back-to-vault テンプレートに従う。書き戻し不要なら 'SKIP' とだけ返す。" \
            '{
              model: $model,
              max_tokens: 2048,
              system: $sys,
              messages: [{role: "user", content: $pr}]
            }' > /tmp/payload.json

          curl -sS https://api.anthropic.com/v1/messages \
            -H "x-api-key: $ANTHROPIC_API_KEY" \
            -H "anthropic-version: 2023-06-01" \
            -H "content-type: application/json" \
            -d @/tmp/payload.json > /tmp/summary.json

          jq -r '.content[0].text' /tmp/summary.json > /tmp/summary.md

      - name: Open PR against personal Vault repo
        env:
          VAULT_TOKEN: ${{ secrets.VAULT_REPO_TOKEN }}
        run: |
          # SKIP なら何もしない
          grep -q '^SKIP$' /tmp/summary.md && exit 0
          # /tmp/summary.md を Vault リポジトリの inbox/ にコミットして PR を立てる
          # （リポジトリのクローン、ブランチ作成、gh pr create は省略）
```

このパターンの **強み** は「セッションを閉じても動く」「複数マシン・チームメンバーの作業全部から書き戻せる」点です。**弱み** は「会話の文脈が失われる」点なので、PR 本文と Issue コメントに **判断の根拠を書く習慣** が前提になります（書いていない PR はサマリが薄くなる）。

なお、Anthropic API には [プロンプトキャッシュ](https://platform.claude.com/docs/en/build-with-claude/prompt-caching) があるので、`system` プロンプト（テンプレート部分）を `cache_control` で固定すると、PR ごとの呼び出しコストが大きく下がります。実運用に乗せるならキャッシュは必須です。

## どの方式を選ぶか — 導入順序

経験則として、最初に入れるべき自動化はこの順番です。

1. **まず `PostToolUse` フックで promote 通知だけ** — 自分が `gh pr merge` した直後に「書き戻して」と促されるだけでも、書き戻し漏れが激減する
2. **慣れたら `Stop` フックで Daily Note の器を自動作成** — 毎日コードを書く人にだけ追加
3. **`post-merge` フックは Vault が Git の人だけ** — GitHub UI でマージする運用に変えたタイミングで足す
4. **複数マシン横断・同僚共有まで広げたいなら GitHub Actions** — Vault を Git 化するコストを払う価値が出てくるタイミングで導入

最初から GitHub Actions に手を出すと、Vault を Git 化する作業や API キー管理に時間を取られ、肝心の「書き戻し体験」を試す前に消耗します。`PostToolUse` フックは 10 行のシェルスクリプトと 1 つの JSON 設定で動くので、ここから始めるのが圧倒的に速いです。

## 共通の落とし穴

3 方式に共通する注意点をリストにしておきます。

1. **フックの実行は非対話的** — `claude` CLI を headless 起動するなら `claude -p "..." --output-format text` を使う。ただし新しいセッションが立つので「現在の会話の文脈」は引き継げない
2. **`Stop` フックで毎ターン Vault 書き込みするとノイズが爆発する** — 必ず条件分岐（成果のあるセッションだけ反応）を入れる
3. **`gh pr merge` を CI でやっている場合、ローカルの `PostToolUse` フックは発火しない** — その場合は GitHub Actions 側に倒すしかない
4. **フックスクリプトはセキュリティに注意** — `~/.claude/settings.json` のフック設定を他人が書き換えると任意コード実行になる。`settings.json` のオーナー・権限を確認し、信用できないリポジトリの `<proj>/.claude/settings.json` を無批判に有効化しない
5. **`stdout` への過剰出力は会話コンテキストを汚す** — フックの promote 通知は 1〜3 行に抑える。長文をエージェントに渡すと、本来の作業の文脈が押し出される

## まとめ

書き戻しの自動化は「**フックは器を用意し、AI が中身を書く**」の分業が肝です。Git フックや GitHub Actions だけで完結させると、AI Agent 時代の本当の価値である「会話の文脈を活かした学び」を取りこぼします。

3 方式の使い分けを一行で要約すると次のとおりです。

- **Claude Code hooks**: 会話文脈が活かせる。最初に入れるべき層
- **Git クライアントフック**: GitHub UI マージ派の取りこぼしを拾う補助層
- **GitHub Actions**: マシンを閉じていても回る最後の砦。ただし文脈は失われる

シリーズの起点だった [GitHubで全部完結する開発者にObsidianは本当に必要か？]({{< ref "posts/2026/05/2026-05-18-github-vs-obsidian-ai-agent.md" >}}) で書いた「AI Agent が **プロジェクトを跨いだ伏線回収を提案してくれる**」状態は、ここまでの 4 記事（思想 → 読み取り側設定 → 書き戻し設計 → 書き戻し自動化）の合計で初めて実装されます。Vault が「常に新鮮なまま、AI Agent 越しに自己強化されるループ」が回り始めたとき、Obsidian は単なるノートアプリではなく、**個人の知の OS** として機能し始めます。
