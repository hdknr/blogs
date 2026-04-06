---
title: "agent-skill-bus: AIエージェントのスキル劣化を自動検知・修復するOSSランタイム"
date: 2026-03-18
lastmod: 2026-03-18
draft: false
source_url: "https://github.com/hdknr/blogs/issues/1#issuecomment-4079182847"
categories: ["AI/LLM"]
tags: ["agent", "llm", "claude-code", "github"]
description: "42体のAIエージェント運用から生まれたOSS agent-skill-bus の紹介。スキルの劣化検知、DAGベースのタスクキュー、自己改善ループの3モジュール構成で、エージェントスキルの健全性を自動管理する。"
---

AIエージェントを本番運用していると、スキルが静かに壊れていく問題に直面する。[agent-skill-bus](https://github.com/ShunsukeHayashi/agent-skill-bus) は、エージェントスキルのヘルスモニタリング・自己改善・依存管理を担うフレームワーク非依存の運用基盤だ。

## 背景: 42体のAIエージェント運用で見えた課題

開発者のシュンスケ氏（[@The_AGI_WAY](https://x.com/The_AGI_WAY)）は、42体のAIエージェントを半年間運用する中で以下の課題に直面したという。

- **エージェントは壊れる** — APIの変更、モデルのアップデート、認証の期限切れなどで、スキルが静かに劣化する
- **タスクは衝突する** — 複数のエージェントが同時に同じファイルを編集し、データ破損が発生する
- **依存関係が管理できない** — 複雑なタスクはA→B→Cの順序が必要だが、多くのシステムは並列実行してしまう
- **学習ループがない** — フィードバック機構がないため、同じ失敗が繰り返される

42体を人間が目視で監視するのは現実的ではない。そこで作られたのが agent-skill-bus だ。

## 3つのモジュール構成

agent-skill-bus は、独立して動作する3つのモジュールで構成されている。

| モジュール | 役割 |
|-----------|------|
| **Prompt Request Bus** | DAG（有向非巡回グラフ）ベースのタスクキュー。依存関係の解決とファイルロックを提供 |
| **Self-Improving Skills** | スキル品質の自動モニタリングと修復ループ |
| **Knowledge Watcher** | 外部変更の検知から自動改善トリガーを発火 |

これらが連携することで、閉ループの自己改善エージェントシステムを形成する。

```text
外部変更 ──→ Knowledge Watcher ──→ Prompt Request Bus ──→ 実行
                                        ↑                    │
                                        │                    ↓
                                  Self-Improving ←── スキル実行ログ
                                     Skills
```

## セットアップと基本的な使い方

Node.js のみで動作し、外部依存はゼロ。

```bash
# 初期化（30秒で完了）
npx agent-skill-bus init

# スキル実行を記録
npx agent-skill-bus record-run \
  --agent my-agent \
  --skill api-caller \
  --task "fetch data" \
  --result success \
  --score 1.0

# 劣化が検知されたスキルを確認
npx agent-skill-bus flagged

# タスクをキューに追加
npx agent-skill-bus enqueue \
  --source human \
  --priority high \
  --agent dev \
  --task "Fix auth bug"

# ディスパッチ可能なタスクを確認
npx agent-skill-bus dispatch

# ダッシュボードで全体を俯瞰
npx agent-skill-bus dashboard
```

## Claude Code / Codex との連携

`AGENTS.md` に以下を追記するだけで、タスク完了時に自動でスキル実行を記録できる。

```markdown
After completing any task, log the result:
npx agent-skill-bus record-run --agent claude --skill <skill-name> --task "<task>" --result <success|fail|partial> --score <0.0-1.0>
```

自己改善ループが自動的に動作し、スキルの劣化を検知・修復してくれる。

## 既存フレームワークとの違い

LangGraph、CrewAI、AutoGen などの既存フレームワークはエージェントの「実行」を担当するが、「運用上の健全性」はカバーしていない。agent-skill-bus はその隙間を埋める位置づけだ。

- フレームワーク非依存で、既存のエージェントシステムに後付けできる
- JSONL（1行1JSONのログ形式）ベースのシンプルなログ
- ゼロ依存（Node.js のみ）
- MIT ライセンスで OSS 公開

## まとめ

AIエージェントの運用が長期化するほど、スキルの劣化やタスク衝突の問題は避けられない。agent-skill-bus は「エージェントの実行」ではなく「エージェントスキルの健全性」にフォーカスした、実運用から生まれたツールだ。

まずは `npx agent-skill-bus init` で試してみてほしい。

- **リポジトリ**: [ShunsukeHayashi/agent-skill-bus](https://github.com/ShunsukeHayashi/agent-skill-bus)
- **ライセンス**: MIT
