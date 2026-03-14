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

[Opik](https://github.com/comet-ml/opik) は、Comet が開発する Apache 2.0 ライセンスのオープンソース LLM オブザーバビリティプラットフォームです（GitHub で 18,000 以上のスター）。LLM アプリケーション、RAG システム、エージェントワークフローのトレーシング、自動評価、モニタリングを提供します。

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

## まとめ

AI エージェントの運用が拡大するにつれ、「何が起きているか」を把握するオブザーバビリティの重要性は増しています。opik-openclaw は 3 コマンドで導入でき、エージェントのコードを一切変更せずにトレーシングを開始できるため、OpenClaw ユーザーにとって導入ハードルの低い実用的なツールです。

## リンク

- [opik-openclaw GitHub](https://github.com/comet-ml/opik-openclaw) — Apache 2.0 ライセンス
- [Opik GitHub](https://github.com/comet-ml/opik) — Apache 2.0 ライセンス
- [公式ドキュメント](https://www.comet.com/docs/opik/integrations/openclaw)
