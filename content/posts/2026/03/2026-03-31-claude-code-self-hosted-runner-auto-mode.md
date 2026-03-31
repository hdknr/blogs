---
title: "Claude Code + Self-hosted Runner: 「Auto mode is unavailable for your plan」エラーの原因と対処"
date: 2026-03-31
lastmod: 2026-03-31
draft: false
categories: ["AI/LLM"]
tags: ["claude-code", "github-actions"]
source_url: "https://gist.github.com/hdknr/aa914d314b67a0ef8c1c4eabd1edb654"
---

## 症状

GitHub Actions の self-hosted runner で `claude --print` を使った自動処理が突然動かなくなった。

```
claude CLI failed (rc=1): stdout=Auto mode is unavailable for your plan
```

すべてのエージェント呼び出し（researcher, risk, portfolio optimizer）が同じエラーで失敗し、日次の投資提案が生成されなくなった。

ローカルで `claude --print "hello"` を実行すると正常に動作する。`claude auth status` でも Max プランで認証済みと表示される。

## 原因

2つの問題が重なっていた。

### 1. OAuth トークンの期限切れ（副次的問題）

ワークフローで `CLAUDE_CODE_OAUTH_TOKEN` 環境変数に **期限切れの OAuth トークン** を GitHub Secrets から渡していた。

```yaml
# daily-proposal.yml
- name: 日次投資提案を生成
  env:
    CLAUDE_CODE_OAUTH_TOKEN: ${{ secrets.CLAUDE_CODE_OAUTH_TOKEN }}  # ← 2月に設定したまま
```

- GitHub Secrets のトークンは静的で自動更新されない
- ローカルでは環境変数未設定のため、キーチェーンから有効なトークンが自動取得されて動作していた

### 2. Opus の auto mode 制限（真の原因）

`claude --print` はデフォルトで **auto mode**（ツール自動承認）で動作する。Max プランで **Opus モデルの auto mode が制限された**ため、トークンが有効でも Opus では `--print` が使えなくなっていた。

```bash
# NG: auto mode (デフォルト)
$ claude --print --model claude-opus-4-20250514 "hello"
Auto mode is unavailable for your plan

# OK: permission-mode default を明示
$ claude --print --permission-mode default --model claude-opus-4-20250514 "hello"
Hello! How can I help you?

# OK: Sonnet は auto mode でも動作
$ claude --print --model claude-sonnet-4-20250514 "hello"
Hello! How can I help you?
```

## 対処

### Step 1: OAuth トークンをファイルベースで動的取得

GitHub Actions の self-hosted ランナーは macOS キーチェーンにアクセスできない（`security find-generic-password` が空を返す）ため、ファイル経由でトークンを渡す。

**トークンエクスポートスクリプト** (`scripts/refresh-oauth-token.sh`):

```bash
#!/bin/bash
TOKEN_FILE="$HOME/.claude/.oauth_token"
TOKEN=$(security find-generic-password -s "Claude Code-credentials" -w 2>/dev/null | \
  python3 -c "import sys,json; print(json.load(sys.stdin)['claudeAiOauth']['accessToken'])" 2>/dev/null)
echo -n "$TOKEN" > "$TOKEN_FILE"
chmod 600 "$TOKEN_FILE"
```

**launchd で4時間ごとに自動更新** (`~/Library/LaunchAgents/com.trader.refresh-oauth-token.plist`):

```xml
<dict>
    <key>Label</key>
    <string>com.trader.refresh-oauth-token</string>
    <key>ProgramArguments</key>
    <array>
        <string>/path/to/scripts/refresh-oauth-token.sh</string>
    </array>
    <key>StartInterval</key>
    <integer>14400</integer>
    <key>RunAtLoad</key>
    <true/>
</dict>
```

**ワークフローでファイルから読み取り**:

```yaml
- name: Claude OAuth トークン取得
  id: claude-auth
  run: |
    TOKEN=$(cat "$HOME/.claude/.oauth_token")
    echo "::add-mask::$TOKEN"
    echo "token=$TOKEN" >> "$GITHUB_OUTPUT"

- name: 日次投資提案を生成
  env:
    CLAUDE_CODE_OAUTH_TOKEN: ${{ steps.claude-auth.outputs.token }}
```

### Step 2: --permission-mode default を追加

```python
# Before
subprocess.run([claude_cmd, "--print", "--model", model, "--system-prompt", prompt, message])

# After
subprocess.run([claude_cmd, "--print", "--permission-mode", "default", "--model", model, "--system-prompt", prompt, message])
```

この変更により、Opus でも `--print` モードが動作する。ツールを使わずプロンプト→テキスト応答のみの用途では、permission mode の違いは実質的に影響しない。

## 調査の過程で試して失敗したこと

| 試行 | 結果 | 理由 |
|------|------|------|
| GitHub Secrets から `CLAUDE_CODE_OAUTH_TOKEN` を削除 | `Not logged in` | ランナーがキーチェーンにアクセスできない |
| ワークフローで `HOME: /Users/hdknr` を設定 | `Not logged in` | HOME が正しくてもキーチェーンセッションにアクセス不可 |
| `security find-generic-password` をワークフロー内で実行 | JSON パースエラー | ランナープロセスからキーチェーンが空を返す |
| 全エージェントを Sonnet に変更 | 動作するが Opus の品質が失われる | auto mode 制限の回避にはなるが根本対処ではない |

## 教訓

| ポイント | 詳細 |
|---------|------|
| **`--print` は暗黙的に auto mode** | `--permission-mode default` で明示的に変更可能 |
| **モデルごとに auto mode の制限が異なる** | Sonnet は OK、Opus は制限される場合がある |
| **self-hosted runner でもキーチェーンは使えない** | GitHub Actions プロセスはキーチェーンのログインセッション外で動く |
| **OAuth トークンは Secrets に静的保存しない** | ファイル + 定期更新（launchd）で鮮度を保つ |
| **エラーメッセージの解釈に注意** | 「unavailable for your plan」はプランの問題ではなく、モデル×モードの組み合わせ制限だった |

## 環境

- Claude Code v2.1.87
- macOS (Apple Silicon)
- GitHub Actions self-hosted runner
- Claude Max プラン

## 関連 PR

- [hdknr/trader#313](https://github.com/hdknr/trader/pull/313) — 期限切れ CLAUDE_CODE_OAUTH_TOKEN 削除
- [hdknr/trader#314](https://github.com/hdknr/trader/pull/314) — HOME 明示（効果なし）
- [hdknr/trader#315](https://github.com/hdknr/trader/pull/315) — keychain から動的取得（ランナーからアクセス不可）
- [hdknr/trader#316](https://github.com/hdknr/trader/pull/316) — ファイルベーストークン取得
- [hdknr/trader#317](https://github.com/hdknr/trader/pull/317) — 全エージェント Sonnet 化（暫定）
- [hdknr/trader#318](https://github.com/hdknr/trader/pull/318) — `--permission-mode default` で Opus 復活（最終解決）
