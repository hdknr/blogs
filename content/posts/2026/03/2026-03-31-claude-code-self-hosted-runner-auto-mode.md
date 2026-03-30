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

ワークフローで `CLAUDE_CODE_OAUTH_TOKEN` 環境変数に **期限切れの OAuth トークン** を渡していたことが原因。

```yaml
# daily-proposal.yml
- name: 日次投資提案を生成
  run: uv run trader daily-proposal
  env:
    CLAUDE_CODE_OAUTH_TOKEN: ${{ secrets.CLAUDE_CODE_OAUTH_TOKEN }}  # ← 2月に設定したまま
```

### なぜローカルでは動くのか

Claude Code の認証は以下の優先順位で解決される:

1. **環境変数** `CLAUDE_CODE_OAUTH_TOKEN`（設定されていれば最優先）
2. **macOS キーチェーン**（`Claude Code-credentials` エントリ）
3. **対話的 OAuth フロー**

ローカル実行時は環境変数を設定していないため、キーチェーンから有効なトークンが自動取得される。一方、GitHub Actions では期限切れのトークンが環境変数で渡され、キーチェーンの有効な認証を**上書き**してしまっていた。

### トークン期限切れのメカニズム

Claude Code の OAuth トークンには有効期限がある。通常の対話的利用では CLI がリフレッシュトークンを使って自動更新するが、GitHub Secrets に保存された静的なトークンは更新されない。2月に設定したトークンが3月末に期限切れとなり、エラーが発生した。

## 対処

ワークフローから `CLAUDE_CODE_OAUTH_TOKEN` 環境変数の行を削除した。

```diff
  env:
    GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
    DATABASE_URL: ${{ vars.DATABASE_URL }}
    BITFLYER_HOST: ${{ vars.BITFLYER_HOST }}
    BITFLYER_PORT: ${{ vars.BITFLYER_PORT }}
-   CLAUDE_CODE_OAUTH_TOKEN: ${{ secrets.CLAUDE_CODE_OAUTH_TOKEN }}
```

**PR**: [hdknr/trader#313](https://github.com/hdknr/trader/pull/313)

### なぜこれで動くのか

self-hosted runner は同一マシン・同一ユーザー（`hdknr`）で動作している。環境変数がなければ、`claude --print` は macOS キーチェーンから有効な OAuth トークンを自動取得する。さらに、CLI が定期的にリフレッシュトークンでアクセストークンを更新するため、今後の期限切れも自動的に回避される。

## 教訓

| ポイント | 詳細 |
|---------|------|
| **self-hosted runner ではキーチェーン認証を使う** | 同一マシンなら Secrets でトークンを管理する必要がない |
| **環境変数は最優先で解決される** | 期限切れのトークンを環境変数で渡すと、有効な認証を上書きしてしまう |
| **OAuth トークンは Secrets に保存しない** | 静的に保存されたトークンは自動更新されず、いずれ期限切れになる |
| **エラーメッセージに注意** | 「Auto mode is unavailable for your plan」はプランの問題ではなく、認証トークンの問題だった |

## 環境

- Claude Code v2.1.87
- macOS (Apple Silicon)
- GitHub Actions self-hosted runner
- Claude Max プラン
