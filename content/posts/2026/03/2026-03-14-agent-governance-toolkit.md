---
title: "Microsoft Agent Governance Toolkit：AIエージェントのセキュリティを4つの柱で守るOSSツールキット"
date: 2026-03-14
lastmod: 2026-03-14
draft: false
source_url: "https://github.com/hdknr/blogs/issues/1#issuecomment-4061220341"
categories: ["セキュリティ"]
tags: ["agent", "security", "llm", "github"]
---

Microsoft がオープンソースで公開した [Agent Governance Toolkit](https://github.com/microsoft/agent-governance-toolkit) は、自律型 AI エージェントに欠けていたセキュリティレイヤーを提供するツールキットだ。ポリシー強制、ゼロトラスト ID、実行サンドボックス、信頼性エンジニアリングの4つの柱で、OWASP Agentic Top 10 の全10項目のリスクをカバーする。

## 背景：なぜ AI エージェントにガバナンスが必要か

AI エージェントが自律的にツールを呼び出し、ファイルを操作し、外部 API と通信する時代になった。しかし、その自律性にはリスクが伴う。意図しないゴールの書き換え、過剰な権限の付与、エージェント間通信の改ざん、カスケード障害など、従来の Web アプリケーションとは異なるセキュリティ課題がある。

OWASP は「Agentic Top 10」として AI エージェント特有のリスクを定義しており、Agent Governance Toolkit はこの全10項目に対応している。

## 4つの柱

### 1. Policy Engine（ポリシーエンジン）

すべてのエージェントアクションを実行前に評価し、許可・拒否を判定する。サブミリ秒（0.1ms 未満）のレイテンシで動作するため、エージェントの応答速度に影響を与えない。

```python
from agent_governance_toolkit import CapabilityModel

capabilities = CapabilityModel(
    allowed_tools=["web_search", "file_read"],
    denied_tools=["file_write", "shell_exec"]
)
```

許可するツールと拒否するツールを明示的に定義し、エージェントが意図しない操作を行うことを防ぐ。

### 2. Agent Identity（ゼロトラスト ID）

Ed25519 暗号化認証情報と SPIFFE/SVID をベースにした、エージェントのゼロトラスト認証を実現する。各エージェントに 0〜1000 のスケールで信頼スコアを付与し、信頼度に応じてアクセス制御を行う。

### 3. Execution Sandboxing（実行サンドボックス）

4層の特権リングでエージェントの実行権限を制限する。サガオーケストレーションによるトランザクション管理や、緊急時のキルスイッチ（強制終了）機能も備えている。

### 4. Agent SRE（信頼性エンジニアリング）

SLO（Service Level Objective）とエラーバジェットの管理、リプレイデバッグ、カオスエンジニアリング、段階的ロールアウトを統合し、エージェントシステムの運用信頼性を確保する。

## OWASP Agentic Top 10 との対応

| リスク | 対応方法 |
|--------|---------|
| Agent Goal Hijack（ASI-01） | ポリシーエンジンがゴール変更をブロック |
| Tool Misuse（ASI-02） | 最小権限の能力モデル |
| Identity & Privilege Abuse（ASI-03） | Ed25519 ベースのゼロトラスト認証 |
| Supply Chain Vulnerabilities（ASI-04） | 特権リング＋サンドボックス |
| Unexpected Code Execution（ASI-05） | コンテンツ検証ポリシー |
| Memory & Context Poisoning（ASI-06） | 整合性チェック付きメモリ管理 |
| Insecure Inter-Agent Communication（ASI-07） | AgentMesh 暗号化チャネル |
| Cascading Failures（ASI-08） | サーキットブレーカー＋SLO |
| Human-Agent Trust Exploitation（ASI-09） | 完全な監査トレイル |
| Rogue Agents（ASI-10） | キルスイッチ＋異常検知 |

## インストール

Python、TypeScript、.NET の3言語に対応している。

```bash
# Python
pip install agent-governance-toolkit[full]

# TypeScript / Node.js
npm install @agentmesh/sdk

# .NET
dotnet add package Microsoft.AgentGovernance
```

## 対応フレームワーク

12以上のエージェントフレームワークと統合可能：

- Microsoft Agent Framework（ネイティブミドルウェア）
- Semantic Kernel（Python / .NET）
- LangChain / LangGraph
- Microsoft AutoGen
- CrewAI
- LlamaIndex
- Dify
- OpenAI Agents SDK
- Google ADK
- Haystack

## まとめ

AI エージェントの実運用が広がる中、セキュリティとガバナンスは避けて通れない課題だ。Agent Governance Toolkit は OWASP Agentic Top 10 という業界標準のリスクフレームワークに沿って設計されており、既存のエージェントフレームワークにミドルウェアとして組み込める実用的なアプローチを取っている。MIT ライセンスで公開されているため、商用プロジェクトでも自由に利用できる。
