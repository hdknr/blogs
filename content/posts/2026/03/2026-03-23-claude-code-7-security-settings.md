---
title: "Claude Codeを使うなら最低限やっておきたい「7つのセキュリティ設定」"
date: 2026-03-23
lastmod: 2026-03-23
draft: false
source_url: "https://github.com/hdknr/blogs/issues/1#issuecomment-4109770395"
categories: ["AI/LLM"]
description: "Claude Code のセキュリティ設定を7つ解説。サンドボックス、deny ルール、機密ファイル保護、ネットワーク制限、hooks、権限棚卸し、Managed Settings の設定方法を実践的にまとめます。"
tags: ["claude-code", "security", "claude", "sandbox", "anthropic"]
---

Claude Code が勝手に `git push --force` しかけた——そんな冷や汗体験から真剣にセキュリティ設定を見直したという実践的なまとめです。Anthropic の公式ドキュメントにも「セキュリティは自分で設定しろ」と明記されており、AIエージェントに人間と同じ権限を与えるリスクを理解した上で対策を講じる必要があります。

## 1. サンドボックスを有効にする（そして脱出口を塞ぐ）

サンドボックスは Claude Code が実行する Bash コマンドを OS レベルで隔離する機能です。macOS では Seatbelt（macOS 標準のサンドボックス機構）、Linux では Bubble Wrap（軽量コンテナ隔離ツール）が使われます。

現在の状態は `/sandbox` コマンドで確認できます。設定ファイルで明示的に有効化するには:

```json
{
  "sandbox": {
    "enabled": true,
    "allowUnsandboxedCommands": false
  }
}
```

ポイントは `allowUnsandboxedCommands: false` です。デフォルトでは `allowUnsandboxedCommands: true` になっており、サンドボックス制限でコマンドが失敗した場合、Claude がユーザーの許可を得た上で `dangerouslyDisableSandbox` パラメータ付きでリトライできる仕組みになっています。`allowUnsandboxedCommands: false` を設定して初めて、この脱出口が完全に塞がります。

## 2. deny ルールで危険なコマンドを止める

Claude Code のパーミッション評価は **deny → ask → allow** の順番で処理されます。deny は最優先で、後から allow で上書きされません。

セッション中に「Always allow」を連打しても、deny に入っているコマンドは絶対に実行されません。

```json
{
  "permissions": {
    "deny": [
      "Bash(rm -rf *)",
      "Bash(curl *)",
      "Bash(wget *)",
      "Bash(git push --force *)",
      "Bash(chmod 777 *)",
      "Bash(git reset --hard *)"
    ]
  }
}
```

公式ドキュメントでも curl と wget はデフォルトで確認が求められる（ask）設定になっていますが、明示的に deny に入れておけば確認なしで完全にブロックできます。`git push --force` と `git reset --hard` も deny に入れておくのがおすすめです。

## 3. 機密ファイルへのアクセスを塞ぐ

`.env` ファイル、SSH 鍵、AWS クレデンシャルなど、Claude Code に読まれたくないファイルは明示的にブロックします。

```json
{
  "permissions": {
    "deny": [
      "Read(./.env)",
      "Read(./.env.*)",
      "Read(**/*.pem)",
      "Read(**/*.key)"
    ]
  },
  "sandbox": {
    "filesystem": {
      "denyRead": ["~/.aws/credentials", "~/.ssh"]
    }
  }
}
```

パーミッションの deny は Claude Code の Read ツール経由のアクセスをブロックし、sandbox の `filesystem.denyRead` は Bash コマンド経由（`cat ~/.ssh/id_rsa` 等）もブロックします。**両方設定しておくのが確実です。**

プロンプトインジェクション攻撃では、Claude Code が意図せず機密ファイルを読もうとする可能性があるため、読み取り自体をブロックしておくことが重要です。

## 4. ネットワークのホワイトリストを設定する

サンドボックスのネットワーク設定で、アクセス可能なドメインをホワイトリスト方式で制限できます。GitHub、npm、PyPI など業務に必要なドメインだけを許可し、それ以外をブロックします。

Managed Settings を使う場合は `allowManagedDomainsOnly: true` で、管理者が指定したドメインのみに制限することも可能です。

悪意あるコードが Claude Code を操って外部サーバーにデータを送信しようとしても、ホワイトリスト外のドメインへの通信はブロックされます。

## 5. PreToolUse フックで独自の安全チェックを挟む

Claude Code には hooks という仕組みがあり、ツール実行の前後にカスタムスクリプトを挟めます。

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [{
          "type": "command",
          "command": ".claude/hooks/validate-command.sh"
        }]
      }
    ]
  }
}
```

フックスクリプトで `exit 2` を返すとコマンドがブロックされます。deny ルールでは対応しきれない複雑な条件分岐（「本番環境への接続を含むコマンドはブロック」等）に使えます。

フックの種類は4つ: コマンド実行、HTTP webhook、LLM プロンプト評価、エージェント型。セキュリティ要件に応じて選べます。

## 6. /permissions で定期的に棚卸しする

Claude Code を長く使っていると、セッション中に「Always allow」で許可したルールが蓄積されます。

- `/permissions` — 現在の権限設定を一覧表示
- `/status` — どの設定ファイルが読み込まれているか、エラーがないかを確認

月1回くらいの棚卸しがおすすめです。さらに自動化したい場合は、最近追加された `ConfigChange` フックで権限変更時に通知や監査ログを記録することもできます。

## 7. チーム開発: Managed Settings で組織ポリシーを強制する

チームで使う場合は、Managed Settings で組織全体にポリシーを強制できます。

- **Server-managed settings（Public Beta）**: Claude.ai の管理コンソールから設定を配信。MDM 不要
- **Endpoint-managed settings**: Jamf や Intune でデバイスに直接配置。セキュリティ重視の組織向け

```json
{
  "permissions": {
    "disableBypassPermissionsMode": "disable"
  },
  "allowManagedPermissionRulesOnly": true,
  "allowManagedHooksOnly": true,
  "allowManagedMcpServersOnly": true
}
```

`allowManagedPermissionRulesOnly: true` にすると、ユーザーが独自に設定した allow/deny ルールは全て無効化され、管理者が設定したルールだけが適用されます。MCP サーバーも管理者が許可したものだけに限定できます。

## さらに堅くしたい場合

### devcontainer で完全隔離

Anthropic 公式が devcontainer のリファレンス実装を公開しています。VS Code の「Reopen in Container」で起動でき、ホストマシンから完全に隔離された環境で Claude Code を動かせます。

### 外部サンドボックス（OpenShell）

NVIDIA の OpenShell を使うと、Claude Code のプロセス自体を外側からサンドボックスできます。エージェントが自分でガードレールを外すことができないため、インプロセスのガードレールより堅牢です。エンタープライズ向けの選択肢です。

### AgentShield

Cerebral Valley x Anthropic 共催の Claude Code Hackathon（2026年2月）から生まれたオープンソースツールで、1,282テスト・102ルールで Claude Code のワークフローをスキャンします。

## まとめ

AI エージェントが人間と同じ権限でコマンドを実行できるということは、設定を間違えたときのリスクも人間と同じです。全部を常時オンにする必要はなく、まずは 1〜4 の基本設定だけでも、センシティブな作業のときに切り替えられるようにしておくのがおすすめです。それだけで「何も設定していない状態」とは雲泥の差になります。
