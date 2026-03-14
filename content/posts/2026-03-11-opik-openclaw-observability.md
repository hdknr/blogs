---
title: "Opik × OpenClaw — AI エージェントの動作を完全可視化するオブザーバビリティプラグイン"
date: 2026-03-11
lastmod: 2026-03-11
draft: false
source_url: "https://github.com/hdknr/blogs/issues/1#issuecomment-4041953408"
categories: ["AI/LLM"]
tags: ["agent", "llm"]
---

OpenClaw で AI エージェントを運用していると、「エージェントが内部で何をしているのか分からない」という課題に直面します。Comet チームが開発した **opik-openclaw** は、OpenClaw のエージェント動作をトレース・評価・監視できるオブザーバビリティプラグインです。AI の「ブラックボックス」を「ガラスボックス」に変えるツールとして注目されています。

## Opik とは

[Opik](https://github.com/comet-ml/opik) は、[Comet](https://www.comet.com/) が開発する Apache 2.0 ライセンスのオープンソース LLM オブザーバビリティプラットフォームです（GitHub で 18,000 以上のスター）。LLM アプリケーションのライフサイクル全体 — 開発・評価・本番監視 — をカバーする統合基盤として設計されています。

### Opik の 3 つの柱

**1. トレーシング（開発）**

すべての LLM 呼び出しについて、プロンプト・レスポンス・メタデータ・コスト・レイテンシを詳細に記録します。1 日あたり 4,000 万以上のトレースを処理できるスケーラビリティを持ち、Prompt Playground でプロンプトの実験・比較も可能です。

**2. 評価とテスト**

LLM-as-a-judge によるハルシネーション検出、コンテキスト精度、回答の関連性といった自動評価メトリクスを提供します。データセットを定義して「良い回答とは何か」を基準化し、新バージョンのアプリを自動スコアリングできます。Pytest との統合により CI/CD パイプラインに評価を組み込むことも可能です。

```python
from opik.evaluation.metrics import Hallucination

metric = Hallucination()
score = metric.score(
    input="フランスの首都は？",
    output="パリです。",
    context=["フランスの首都はパリである。"],
)
print(score)  # HallucinationResult(score=0.0, reason="...")
```

**3. 本番監視と最適化**

フィードバックスコア、トークン使用量のリアルタイム追跡に加え、オンライン評価ルールで本番環境の品質を継続監視できます。プロンプトの自動最適化アルゴリズム（Agent Optimizer）や Guardrails（安全性フィルタ）機能も備えています。

### 対応インテグレーション

60 以上のフレームワーク・プロバイダーと統合できます:

- **LLM プロバイダー**: OpenAI、Anthropic、Google Gemini、AWS Bedrock、Ollama
- **エージェントフレームワーク**: LangChain、LlamaIndex、CrewAI、OpenAI Agents SDK、Google ADK
- **その他**: Vercel AI SDK、Pydantic AI、n8n、Dify、Flowise AI

### デプロイ方式

| 項目 | クラウド版 | セルフホスト |
|------|----------|------------|
| セットアップ | comet.com でアカウント作成後すぐ利用可能 | Docker Compose or Kubernetes + Helm |
| データ管理 | Comet 側で管理 | 自社インフラ内で完結 |
| 推奨用途 | 個人・スタートアップ・クイックスタート | エンタープライズ・データ主権が必要な場合 |

セルフホストは以下のコマンドで起動でき、`localhost:5173` でダッシュボードにアクセスできます:

```bash
git clone https://github.com/comet-ml/opik.git
cd opik
./opik.sh
```

### Python / TypeScript SDK

Python SDK は `pip install opik` でインストールし、`@opik.track` デコレータを付けるだけでトレースが自動記録されます。TypeScript SDK（`npm install opik`）も提供されており、フロントエンド・バックエンド問わず利用可能です。

```bash
pip install opik
opik configure  # API キーまたはローカルインスタンスの URL を設定
```

## opik-openclaw の主要機能

### フルトレースキャプチャ

すべての LLM 呼び出し、ツール実行、メモリ参照、コンテキスト組み立て、エージェント間の委譲を記録します。各操作について、入出力ペア、トークン数、レイテンシ、コストが完全に記録されます。

### 会話スレッドの追跡

リクエストの開始から、マルチステップ推論、ツール呼び出し、最終レスポンスまでの全フローを追跡できます。サブエージェントへのチェーンやスケジュールされたハートビートからの処理再開も含めて可視化されます。

### コスト可視化

リクエスト単位・モデル単位のコスト内訳を表示し、トークンの使用先を正確に把握できます。どの処理にどれだけコストがかかっているかを分析し、最適化の判断材料にできます。

### 自動評価

LLM-as-a-judge による評価メトリクスを設定し、トレースに対して自動的に実行できます。ハルシネーション検出、回答の関連性、コンテキストの精度など、品質を継続的に監視できます。

## セットアップ手順

OpenClaw バージョン 2026.3.2 以降が必要です。

### 1. プラグインのインストール

```bash
openclaw plugins install @opik/opik-openclaw
```

### 2. 設定

```bash
openclaw opik configure
```

このコマンドで Opik の URL 検証と API キーアクセスの検証が行われます。

### 3. ステータス確認とゲートウェイ再起動

```bash
openclaw opik status
openclaw gateway restart
```

設定完了後にメッセージを送信すると、Opik ダッシュボードにトレースが表示されます。

### 手動設定（JSON）

OpenClaw の設定ファイルに直接記述することも可能です。

```json
{
  "apiUrl": "https://www.comet.com/opik/api",
  "apiKey": "YOUR_API_KEY",
  "projectName": "my-project",
  "workspaceName": "my-workspace"
}
```

環境変数による設定にも対応しています:

- `OPIK_API_KEY` — API キー
- `OPIK_URL_OVERRIDE` — カスタム URL
- `OPIK_PROJECT_NAME` — プロジェクト名
- `OPIK_WORKSPACE` — ワークスペース名

## セルフホスト対応

Opik はセルフホストにも対応しており、プラグインをローカルインスタンスに向けるだけで、完全なオブザーバビリティを自社インフラ上で実現できます。データが外部に送信されることはありません。

## ネイティブプラグインの優位性

opik-openclaw はネイティブプラグインとしてゲートウェイのライフサイクルにフックするため、ネットワークプロキシでは取得できない情報も記録できます:

- どのスキルがロードされたか
- どのメモリが参照されたか
- エージェントがサブエージェント間でどのようにルーティングしたか
- エージェントの推論の全深度

## 既知の制限事項

複数セッションを並行実行した場合、ツールスパンの相関が正しく行われないケースがあります。

## OpenClaw なしでも実現できる？ — 自前スクリプト + Opik という選択肢

opik-openclaw が提供するオブザーバビリティの仕組みを分解してみると、各要素は汎用的な技術の組み合わせであることが分かります。

| 機能 | opik-openclaw | 自前スクリプトでの代替 |
|------|--------------|----------------------|
| LLM 呼び出しログ | 自動キャプチャ | API ラッパーで `usage` フィールドを記録 |
| ツール実行追跡 | ゲートウェイフック | Python デコレータやシェルのトラップで記録 |
| コスト集計 | ダッシュボード表示 | API レスポンスのトークン数 × 単価で計算 |
| エージェント間委譲 | 自動追跡 | ワークフロー定義で明示的に制御 |
| 自動評価 | LLM-as-a-judge 連携 | Opik Python SDK で直接設定可能 |

**Opik 自体は OpenClaw に依存しない汎用プラットフォーム**です。Python SDK（`pip install opik`）を使えば、自前のスクリプトから直接トレースを送信できます。

```python
import opik

# デコレータを付けるだけでトレースが記録される
@opik.track
def call_llm(prompt: str) -> str:
    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        messages=[{"role": "user", "content": prompt}],
    )
    return response.content[0].text
```

つまり、**やりたいことが明確でワークフローが決まっている場合**、OpenClaw というエージェント実行環境を介さずに、シェルスクリプトや Python スクリプトで LLM API を直接呼び、Opik でトレースを記録する方が依存が少なく見通しも良くなります。OpenClaw の価値は「汎用エージェント実行環境」としての柔軟性にありますが、特定の業務フローを自動化するだけなら、薄いスクリプト + オブザーバビリティ基盤という構成の方がシンプルです。

## まとめ

AI エージェントの運用が拡大するにつれ、「何が起きているか」を把握するオブザーバビリティの重要性は増しています。opik-openclaw は OpenClaw ユーザーにとって 3 コマンドで導入できる手軽なソリューションですが、Opik 自体は汎用プラットフォームであるため、自前のスクリプトから直接利用することも可能です。目的に応じて、OpenClaw 経由か直接統合かを選択できる点が、オープンソースエコシステムの強みと言えます。

## リンク

- [opik-openclaw GitHub](https://github.com/comet-ml/opik-openclaw) — Apache 2.0 ライセンス
- [Opik GitHub](https://github.com/comet-ml/opik) — Apache 2.0 ライセンス
- [公式ドキュメント](https://www.comet.com/docs/opik/integrations/openclaw)
