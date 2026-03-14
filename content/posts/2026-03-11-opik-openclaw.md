---
title: "opik-openclaw — OpenClaw の AIエージェント動作を可視化するオブザーバビリティツール"
date: 2026-03-11
lastmod: 2026-03-11
draft: false
source_url: "https://github.com/hdknr/blogs/issues/1#issuecomment-4041953408"
categories: ["AI/LLM"]
tags: ["openclaw", "agent", "llm"]
---

OpenClaw を使っていると「AI が裏で何をしているのか分からない」と感じることはありませんか？Comet が開発した **opik-openclaw** は、OpenClaw のエージェント動作をトレース・可視化するオープンソースプラグインです。AI を「ブラックボックス」から「ガラスボックス」に変えてくれます。

## opik-openclaw とは

[opik-openclaw](https://github.com/comet-ml/opik-openclaw) は、Comet が開発する LLM オブザーバビリティプラットフォーム [Opik](https://github.com/comet-ml/opik)（GitHub Star 18,000+）の OpenClaw 公式プラグインです。

OpenClaw のエージェントが実行するすべての操作を記録・可視化し、以下の情報をダッシュボードで確認できます。

- **LLM 呼び出し**: 入出力ペア、トークン数、レイテンシ、コスト
- **ツール実行**: どのツールが、いつ、どんな引数で呼ばれたか
- **エージェント委譲**: サブエージェントへのタスク委譲の流れ
- **推論プロセス**: 最初のメッセージから最終応答までの全会話フロー

## セットアップ（3 コマンド）

```bash
# 1. プラグインをインストール
openclaw plugins install @opik/opik-openclaw

# 2. 認証情報を設定
openclaw opik configure

# 3. ゲートウェイを再起動
openclaw gateway restart
```

動作確認は以下のコマンドで行えます。

```bash
openclaw opik status
```

### 環境変数による設定

手動設定が必要な場合は、以下の環境変数を使用できます。

| 環境変数 | 説明 |
|---|---|
| `OPIK_API_KEY` | Opik API キー |
| `OPIK_URL_OVERRIDE` | セルフホスト時の URL |
| `OPIK_PROJECT_NAME` | プロジェクト名 |
| `OPIK_WORKSPACE` | ワークスペース名 |

JSON 設定ファイルでも `apiUrl`、`apiKey`、`projectName`、`workspaceName`、`tags` を指定できます。

## 何が見えるようになるか

### 1. AI の思考プロセス

エージェントがリクエストを受けてから応答を返すまでの全ステップがトレースされます。マルチステップの推論、ツール呼び出し、サブエージェントへの委譲を含め、一連のフローを時系列で追えます。

### 2. コスト分析

リクエストごと・モデルごとのコスト内訳が表示されます。トークンがどこで消費されているかが一目瞭然になるため、プロンプトの最適化やモデル選択の判断材料になります。

### 3. 品質評価

Opik は LLM-as-a-Judge による自動評価メトリクスを提供します。

- **ハルシネーション検出**: AI が事実と異なる回答をしていないか
- **回答関連性**: 質問に対して適切な回答をしているか
- **コンテキスト精度**: 提供されたコンテキストを正しく使えているか

## セルフホストも可能

Opik は Apache 2.0 ライセンスのオープンソースプロジェクトです。セルフホストの Opik インスタンスにプラグインを向ければ、データが外部に一切出ないオンプレミス環境でもフルオブザーバビリティを実現できます。

企業のセキュリティ要件が厳しい環境でも導入しやすい設計です。

## 注意点

- OpenClaw **2026.3.2 以降** が必要
- 並行セッション時にツールスパンの紐付けがずれるケースがある（プラグイン側でフォールバック相関ロジックを使用して対処）

## まとめ

opik-openclaw は「AI エージェントが何をしているか分からない」という OpenClaw ユーザーの課題を解決するツールです。3 コマンドでセットアップでき、エージェントの推論・ツール使用・コストをすべて可視化できます。

AI エージェントの運用が本格化するにつれ、こうしたオブザーバビリティツールの重要性は増していくでしょう。

## 参考リンク

- [comet-ml/opik-openclaw](https://github.com/comet-ml/opik-openclaw) — OpenClaw 公式プラグイン
- [comet-ml/opik](https://github.com/comet-ml/opik) — Opik 本体（Apache 2.0）
- [OpenClaw Observability with Opik](https://www.comet.com/site/blog/openclaw-observability/) — Comet 公式ブログ
- [Opik × OpenClaw 公式ドキュメント](https://www.comet.com/docs/opik/integrations/openclaw)
