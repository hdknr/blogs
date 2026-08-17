---
title: "Sandcastle — AI コーディングエージェントを夜間並列実行して朝にレビューするだけにする OSS"
date: 2026-05-01
lastmod: 2026-05-01
slug: "matt-pocock-sandcastle-afk-development"
draft: false
source_url: "https://github.com/hdknr/blogs/issues/1#issuecomment-4358352789"
description: "TypeScript の OSS ライブラリ Sandcastle を使い、AI コーディングエージェントを Docker/Vercel サンドボックスで並列実行するオーケストレーション手法を解説。夜間並列タスク・朝レビューの AFK 開発ワークフローを実現する。"
categories: ["AI/LLM"]
tags: ["typescript", "OSS", "AIエージェント", "docker", "自動化"]
---

元 Vercel エンジニアで TypeScript 専門家の Matt Pocock 氏が、AI エージェントを複数並列実行するためのオーケストレーションライブラリ **Sandcastle** を OSS として公開した。このツールは「夜間に 5 タスクを並列で走らせて、朝にマージレビューだけする」という **AFK（Away From Keyboard）開発** を現実のワークフローとして成立させる。

## Sandcastle とは

[Sandcastle](https://github.com/mattpocock/sandcastle) は TypeScript ライブラリで、AI コーディングエージェントを**隔離されたサンドボックス**の中で動かすためのオーケストレーション基盤を提供する。

主な機能は 3 ステップ：

1. `sandcastle.run()` の一行でエージェントを起動する
2. Sandcastle がサンドボックス化とブランチ戦略を管理する
3. エージェントが作ったコミットを自動的にマージ対象のブランチに集約する

## サンドボックスプロバイダー

Sandcastle はプロバイダーに依存しない設計で、以下をビルトインサポートする：

| プロバイダー | インポートパス | 種別 |
|---|---|---|
| Docker | `@ai-hero/sandcastle/sandboxes/docker` | バインドマウント |
| Podman | `@ai-hero/sandcastle/sandboxes/podman` | バインドマウント（rootless） |
| Vercel | `@ai-hero/sandcastle/sandboxes/vercel` | 隔離（Firecracker microVM） |
| No-sandbox | `@ai-hero/sandcastle/sandboxes/no-sandbox` | なし（インタラクティブ専用） |

ローカル開発では Docker Desktop が最も一般的だ。クラウド実行には Vercel の Firecracker microVM が選択肢になる。独自のコンテナ環境に接続する場合は `createBindMountSandboxProvider` や `createIsolatedSandboxProvider` でカスタムプロバイダーを作ることもできる。

## クイックスタート

パッケージ名は `@ai-hero/sandcastle`、npm で配布されている。

### インストール

```bash
npm install --save-dev @ai-hero/sandcastle
```

### 初期化

```bash
npx sandcastle init
```

`.sandcastle/` ディレクトリが作成され、設定ファイルとプロンプトテンプレートがセットアップされる。

### 環境変数の設定

```bash
cp .sandcastle/.env.example .sandcastle/.env
# .sandcastle/.env に ANTHROPIC_API_KEY を設定する
```

### エージェントの実行

```typescript
import { run, claudeCode } from "@ai-hero/sandcastle";
import { docker } from "@ai-hero/sandcastle/sandboxes/docker";

const result = await run({
  agent: claudeCode("claude-opus-4-6"),
  sandbox: docker(),
  promptFile: ".sandcastle/prompt.md",
});

console.log(result.commits);  // エージェントが作成したコミットの一覧
console.log(result.branch);   // ターゲットブランチ名
```

## 主要な設定オプション

### ブランチ戦略

`branchStrategy` でエージェントの変更をどのブランチに反映するかを制御できる：

```typescript
await run({
  agent: claudeCode("claude-opus-4-6"),
  sandbox: docker(),
  promptFile: ".sandcastle/prompt.md",
  branchStrategy: { type: "branch", branch: "agent/fix-42" },
});
```

### プロンプトへの変数埋め込み

`promptArgs` でプロンプトファイル内の `{{KEY}}` プレースホルダーに値を差し込める：

```typescript
await run({
  agent: claudeCode("claude-opus-4-6"),
  sandbox: docker(),
  promptFile: ".sandcastle/prompt.md",
  promptArgs: {
    ISSUE_NUMBER: "42",
    FEATURE_NAME: "user-auth",
  },
});
```

### Docker マウント設定

ホストのディレクトリをサンドボックス内にマウントしてキャッシュを共有できる：

```typescript
import { docker } from "@ai-hero/sandcastle/sandboxes/docker";

await run({
  agent: claudeCode("claude-opus-4-6"),
  sandbox: docker({
    mounts: [
      { hostPath: "~/.npm", sandboxPath: "/home/agent/.npm", readonly: true },
    ],
  }),
  prompt: "Fix the type errors in src/auth.ts",
});
```

## AFK 開発というコンセプト

Sandcastle が実現しようとしているのは、**エンジニアが離席中も、エージェントが並列でタスクをこなし続ける**開発スタイルだ。

典型的なユースケース：

- 夜間にバグ修正・機能追加・テスト作成を 5 つのエージェントに並列割り当て
- 各エージェントが独立したサンドボックスで作業し、別々のブランチにコミット
- 翌朝、エンジニアはマージレビューだけして取り込む

「コードを書く」から「エージェントのアウトプットをレビューする」へのシフトが、このツールで現実的になる。

## まとめ

Sandcastle は「AI エージェントを安全に・並列に・自動で動かす」というニーズに応える実用的な OSS だ。

- プロバイダー抽象（Docker / Podman / Vercel から選択可）
- `sandcastle.run()` のシンプルな API
- プロンプトファイルによるタスク管理

いずれも実際のプロジェクトへの組み込みを想定した設計になっている。AFK 開発というコンセプトが示す通り、エンジニアの作業時間の使い方が根本的に変わる可能性を秘めたツールだ。

- GitHub: [mattpocock/sandcastle](https://github.com/mattpocock/sandcastle)
- パッケージ: `@ai-hero/sandcastle`（npm）

## Matt Pocock について

Matt Pocock 氏は TypeScript 教育プラットフォーム **Total TypeScript** の創設者で、Vercel での勤務経験を持つ TypeScript エキスパートだ。TypeScript の複雑なパターンや型システムを丁寧に解説するコンテンツで知られており、Sandcastle はその知見を活かして TypeScript 開発者に向けて設計されている。
