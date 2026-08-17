---
title: "GitHub Actions self-hosted runner で Obsidian Vault 書き戻しを完成させる — claude -p をローカル文脈で動かす"
date: 2026-05-18
lastmod: 2026-05-18
slug: "self-hosted-runner-vault-writeback"
draft: false
description: "PR マージのイベント駆動で Obsidian Vault に書き戻す処理を、self-hosted runner で手元の Mac に降ろす設計。cloud-hosted Actions の弱点（Vault に書けない・skills が使えない・会話文脈ゼロ）を一気に解消し、claude -p で Vault 直書きを実現する具体的な workflow と launchd セットアップを解説。"
categories: ["AI/LLM"]
tags: ["claude-code", "Obsidian", "GitHub Actions", "self-hosted runner", "claude -p", "writeback", "automation", "launchd", "ナレッジマネジメント", "PKM"]
---

[Obsidian Vault 書き戻しの自動化](/blogs/posts/2026/05/claude-code-vault-writeback-automation/) では、3 方式（Claude Code hooks / Git クライアントフック / GitHub Actions）の使い分けをまとめました。そこで「GitHub Actions は会話文脈が失われる・Vault に書けない」と書きましたが、これは **cloud-hosted runner** を前提にした話です。**self-hosted runner**（GitHub の job を手元のマシンで実行する仕組み）に切り替えると、その制約が一気に外れます。

本記事では、自宅 Mac を self-hosted runner にして、PR マージのイベント駆動で `claude -p` を **ローカル文脈**（Vault・Skills・CLAUDE.md・MCP サーバ）の中で動かし、Vault に直接書き戻す構成を解説します。ここでの「ローカル文脈」は **対話履歴ではなく、ファイルシステムに永続化された個人資産のセット** を指す点に注意してください。シリーズ 5 部作の最終ピースです（思想編 → 読み取り側 → 書き戻し設計 → フック自動化 → self-hosted runner）。

## なぜ self-hosted runner が正解になるか

cloud-hosted Actions の最大の弱点は次の 3 点でした。

- Vault が手元のファイルシステムにあるので、cloud runner からは見えない
- ローカルの MCP サーバ（`vault-readonly` / `vault-inbox`）に接続できない
- ローカルの Skills や CLAUDE.md が読めず、`/summary-back-to-vault` を呼べない

self-hosted runner は「ジョブは GitHub のイベント駆動で立ち上がるが、実体は手元のマシンが処理する」というハイブリッドです。3 つの弱点がすべて解消します。

| 観点 | GitHub-hosted | Self-hosted (local) |
| --- | --- | --- |
| Vault ファイルへのアクセス | ✗ そもそも見えない | ✓ ローカル FS でそのまま |
| MCP サーバ（`vault-inbox` 等） | ✗ 接続不可 | ✓ 立てておけばそのまま |
| Claude Code Skills / CLAUDE.md | ✗ workflow に持ち込み必要 | ✓ `~/.claude` を読む |
| API キー | GitHub Secrets に保管 | ローカル `~/.claude.json` に保管 |
| 常時稼働 | 不要（ジョブ時起動） | 必要（マシンを開いている時間） |
| プライベートリポの実行時間課金 | 課金される | 無料（電気代のみ） |
| セキュリティ責任 | GitHub のサンドボックス | 自前で repo allowlist 必須 |

cloud-hosted が「漏れを拾う最後の砦（ただし質は薄い）」だったのに対し、self-hosted runner は「**漏れを拾いつつ、Vault 直書きの質も保てる最強の砦**」になります。Vault を Git 化する必要も消えるので、運用も簡素化します。

## 全体構成

PR マージから Vault 書き戻しまでの流れは次のとおりです。

1. **GitHub（blogs リポジトリ）**: PR がマージされ、`pull_request.closed` イベントが発火する
2. **Self-hosted runner（手元の Mac）**: 当該リポジトリ用にラベル付きで登録された runner が job を pull する
3. **Claude Code（headless 起動）**: runner が `claude -p "/summary-back-to-vault ..."` を実行
4. **ローカル資産の参照**: `~/.claude/settings.json` から MCP サーバが起動し、`<repo>/CLAUDE.md` と `<repo>/.claude/skills/` が読み込まれる
5. **重複チェック**: `vault-readonly` MCP 経由で Vault 全体を Grep し、既存ノートとの重複を排除
6. **書き込み**: `vault-inbox` MCP 経由で `~/Documents/ObsidianVault/inbox/` に Markdown を出力

`claude -p` は新規セッションを立ち上げるので、**いま開いている会話の文脈** は引き継げません。ただし、ローカルの Skills と Vault が見えるので、**「PR の diff と Vault の過去ノートの両方を AI に読ませて、再利用価値のある観点を抽出する」** という処理は十分にできます。cloud-hosted で失われていた「Vault 側の文脈」がここで戻ってくる、というのが本質です。

## セットアップ手順

### 1. self-hosted runner をインストール

GitHub repo の **Settings → Actions → Runners → New self-hosted runner** で、OS とアーキを選ぶと当該ページに具体的なコマンドが表示されます。macOS arm64 の例:

```bash
mkdir ~/actions-runner
cd ~/actions-runner

curl -o actions-runner-osx-arm64.tar.gz -L \
  https://github.com/actions/runner/releases/download/v2.334.0/actions-runner-osx-arm64-2.334.0.tar.gz
tar xzf ./actions-runner-osx-arm64.tar.gz

# 登録トークンは GitHub の上記ページで発行される（短期有効）
./config.sh \
  --url https://github.com/<owner>/<repo> \
  --token <REGISTRATION_TOKEN> \
  --labels self-hosted,macos,local-vault
```

ラベル（`local-vault`）を独自に振っておくと、workflow 側で `runs-on: [self-hosted, local-vault]` のように **このマシンを明示** できます。誤って他人の runner や cloud runner に降りるのを防ぐ仕掛けです。

### 2. launchd サービスとして常駐させる

手で起動するのは続かないので、サービス化してマシン起動と同時に立ち上がるようにします。

```bash
./svc.sh install
./svc.sh start
./svc.sh status
```

これでログイン時に `launchd` 経由で runner プロセスが立ち、GitHub からジョブを pull するようになります。本記事は macOS + launchd 前提で書いていますが、Linux サーバを runner にする場合は `systemd` で同等の常駐化が可能です（Mac mini を専用 runner にする後述の運用にしっくり来るなら macOS のままで OK）。

ステータス確認は GitHub repo の **Settings → Actions → Runners** で「Idle」表示になっていれば OK。`Offline` のままなら、launchd の plist や HOME 解決まわりで詰まっていることが多いので、`tail -f ~/actions-runner/_diag/Runner_*.log` でログを追ってください。

### 3. workflow を書く

`.github/workflows/vault-writeback.yml`:

```yaml
name: Vault writeback (self-hosted)

on:
  pull_request:
    types: [closed]

jobs:
  writeback:
    if: github.event.pull_request.merged == true
    runs-on: [self-hosted, macos, local-vault]
    timeout-minutes: 10

    # fork PR を絶対に走らせない（self-hosted runner の鉄則）
    permissions:
      contents: read
      pull-requests: read

    steps:
      - uses: actions/checkout@v4

      - name: Reject fork PRs
        if: github.event.pull_request.head.repo.full_name != github.repository
        run: |
          echo "Fork PR detected. Aborting on self-hosted runner."
          exit 1

      - name: Collect PR context
        env:
          GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        run: |
          gh pr view ${{ github.event.pull_request.number }} \
            --json title,body,comments,files,url \
            > "$RUNNER_TEMP/pr-context.json"

      - name: Run summary-back-to-vault via claude -p
        env:
          # launchd 経由の runner では HOME が取り違えられがちなので明示
          HOME: /Users/<your-user>
        run: |
          mkdir -p "$HOME/.claude/logs"

          PROMPT=$(cat <<EOF
          次の PR の文脈を読み、/summary-back-to-vault スキルを実行して
          ~/Documents/ObsidianVault/inbox/ に学びを書き戻してください。

          PR context:
          $(cat "$RUNNER_TEMP/pr-context.json")
          EOF
          )

          claude -p "$PROMPT" \
            --output-format text \
            --max-budget-usd 0.50 \
            >> "$HOME/.claude/logs/writeback-$(date +%Y%m%d).log" 2>&1
```

ポイントを補足します。

- **`runs-on: [self-hosted, macos, local-vault]`**: ラベルマッチでこの runner を指定。`self-hosted` だけだと他のマシンに降りる可能性がある
- **fork PR の明示拒否**: `permissions` で書き込みを潰したうえで、fork PR を `exit 1` で弾く。self-hosted runner の最大のセキュリティリスクへの一次防御
- **`HOME` を明示**: launchd 起動の runner で踏みやすい罠。`~/.claude/` の解決をユーザー HOME に固定する。`<your-user>` の部分は **コピペ前に必ず自分のユーザー名に置換** すること（`id -un` で確認できる）。プレースホルダのまま動かすと `/Users/<your-user>` という存在しないディレクトリが作られて静かに落ちる
- **`--max-budget-usd 0.50`**: `claude -p` が暴走したときの保険。1 PR あたりの API コスト上限を切る。フラグ名・挙動は使用バージョンの `claude --help` で必ず再確認すること（Claude Code は活発に開発されており、フラグが改名される可能性がある）

### 4. ローカル Skills の置き場所

`/summary-back-to-vault` スキルは **ユーザースコープの `~/.claude/skills/summary-back-to-vault/`** に置いておくのが正解です。理由は次のとおりです。

- self-hosted runner からの `claude -p` は新規セッションで、`working-directory` は checkout した repo になる
- repo 直下の `<repo>/.claude/skills/` は読まれるが、これは **その repo 用のスキル** で、別 repo からの workflow では使えない
- ユーザースコープの `~/.claude/skills/` は **どの repo の workflow からトリガしても読まれる**

つまり「個人 Vault に書き戻すスキルは個人スコープ」「リポジトリ固有の規約は `<repo>/CLAUDE.md`」と分けると、self-hosted runner 経由でも一貫して動きます。

## 受け取れる「ローカル資産」一覧

self-hosted runner にしたことで、cloud runner では使えなかった以下がすべて使えるようになります。

- `~/.claude/CLAUDE.md`（個人スタイル指示）
- `<repo>/CLAUDE.md`（プロジェクト規約）
- `~/.claude/skills/` と `<repo>/.claude/skills/`
- `~/.claude/settings.json` / `<repo>/.claude/settings.local.json`（MCP サーバ設定）
- Vault 本体（`~/Documents/ObsidianVault/`）
- 既存の `vault-readonly` / `vault-inbox` MCP プロセス（あるいは workflow 内で起動）

前 4 記事で組んできた「読み取り MCP / symlink / inbox-first / スキル」の全セットを **CI のイベント駆動でそのまま呼び出せる** 状態が完成します。

## セキュリティ上の必須ガード

self-hosted runner は **手元のマシンで任意のコードを動かせる権限を GitHub に渡している** のと等価なので、以下は必須です。GitHub 公式ドキュメントも「**public リポ + self-hosted runner は強く非推奨**」と明記しています。

1. **public リポでは絶対に使わない**: fork PR が runner で走ると、攻撃者が任意コード実行可能。本記事の構成は **プライベートリポ前提**
2. **Organization の Runner Group で repo allowlist**: Org 配下なら Runner Group の `Repository access` で許可リポを限定。個人アカウントなら repo ごとに runner を分ける
3. **fork PR のジョブを workflow 側でも拒否**: 上記 YAML の `Reject fork PRs` ステップで `head.repo.full_name != github.repository` の場合 `exit 1`。多重防御の二段目
4. **runner を低権限ユーザーで動かす**: root や admin で起動しない。Vault と `~/.claude/` だけにアクセスできる専用ユーザーが理想。最低限、`sudo` パスワードのキャッシュをクリアしておく
5. **`workflow_dispatch` の手動起動は最小限**: UI から任意の人が手動キックできる経路を塞ぐ。必要な場合は `if: github.actor == 'your-username'` で発火者を絞る
6. **`secrets` を self-hosted job に渡さない**: API キーは GitHub Secrets ではなく、ローカルの `~/.claude.json` 側で管理する。万一 workflow がリークしても秘密が外に出ない（ローカル側の秘密管理を強化するなら [SOPS で AI Agent のシークレットを管理する](/blogs/posts/2026/05/sops-ai-agent-secrets-management/) も参照）

## トレードオフ

良い面:

- **会話文脈は失われるが、Vault と Skills が使えるのでサマリの質は cloud-hosted Actions より明らかに上**
- API キーがマシンから出ない
- プライベートリポの Actions 分単位課金がゼロ（個人アカウントの Pro プランでも minutes は気にしなくてよくなる）
- Vault を Git 化する必要がない（個人ノートをリポジトリにする心理的ハードルが消える）

注意点:

- **マシンが落ちている間はジョブが滞留する**: GitHub のジョブ TTL（最大 24 時間）以内に runner が起きれば実行される。常時起動の Mac mini を runner 専用に立てる人もいる
- **複数 PR の同時 merge は直列で消化される**: 並列性を上げたければ runner を複数登録する
- **launchd / systemd の権限ハマり**: 最初は `claude --version` だけ動かすミニ workflow で疎通確認するのを強く推奨。本格 workflow をいきなり書くと、どこで詰まったかわからなくなる
- **runner の更新運用**: GitHub は old runner を定期的に obsolete にする。`actions-runner` の autoupdate を有効化するか、定期的に手で `./config.sh remove && reinstall` する想定

## 段階導入のロードマップ（最終版）

シリーズの全 5 記事を通して、書き戻し自動化の段階的な導入順序は次のように整理できます。

1. **Claude Code `PostToolUse` フック**: `gh pr merge` 直後に AI に promote 通知。10 行のシェルで効果絶大
2. **Claude Code `Stop` フック**: Daily Note の器を自動作成。慣れたら追加
3. **Git `post-merge` フック**: GitHub UI 派の取りこぼしフォールバック
4. **Self-hosted runner + GitHub Actions**: 上記でも漏れる PR を確実に拾う最後の砦 ← **本記事**
5. **Cloud-hosted GitHub Actions** — 書き戻し用途では self-hosted で代替できるため不要。ただし「Vault に触らない CI」（lint・テスト・secret scanning など）には引き続き有効で、self-hosted と排他ではない

step 4 まで揃うと、書き戻しが「気が向いたとき」ではなく「**マージしたら勝手に走るインフラ**」になります。シリーズの起点だった [GitHubで全部完結する開発者にObsidianは本当に必要か？](/blogs/posts/2026/05/github-vs-obsidian-ai-agent/) で書いた「AI Agent がプロジェクトを跨いだ伏線回収を提案してくれる」状態が、ここで初めて実装として完成します。

## まとめ

self-hosted runner は、**GitHub のイベント駆動の便利さと、ローカル資産（Vault・Skills・MCP・CLAUDE.md・API キー）のフル活用を両立する** ハイブリッド構成です。書き戻しの自動化レイヤーとして cloud-hosted Actions を置く意味は、本シリーズの構成では消えます。

セットアップで最も詰まりやすいのは launchd 周りなので、本記事の構成を試すなら次の順で進めることをおすすめします。

1. `./svc.sh status` で「Idle」を確認
2. `claude --version` だけ走らせるミニ workflow で疎通確認
3. PR context を JSON で吐くステップだけを足す
4. 最後に `claude -p` を呼ぶ本処理を載せる

各段階でログ（`~/actions-runner/_diag/` と `~/.claude/logs/`）を確認しながら進めると、launchd の HOME 取り違えや MCP 起動失敗などのハマりを早期に検知できます。

シリーズ 5 部作の全体像（思想 → 読み取り側設定 → 書き戻し設計 → フック自動化 → self-hosted runner）を組み上げると、Obsidian Vault は「個人の知の OS」として AI Agent 越しに自己強化されるループに入ります。手元のマシンが起動している限り、PR を merge するだけで Vault が新鮮に保たれる、というのが最終形です。
