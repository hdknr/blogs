---
title: "Claude Code vs OpenClaw — 「どっちを勉強すべき？」に対する責務ベースの選び方"
date: 2026-03-11
lastmod: 2026-03-11
draft: false
source_url: "https://github.com/hdknr/blogs/issues/1#issuecomment-4036921380"
categories: ["AI/LLM"]
tags: ["claude-code", "openclaw", "agent", "llm"]
---

AI コーディングエージェントの選択肢が増えるなか、「Claude Code と OpenClaw、どっちを勉強すべき？」という疑問を抱く人が増えている。AI駆動塾（[@L_go_mrk](https://x.com/L_go_mrk)）が両方を実際に触った上での[比較記事](https://note.com/l_mrk/n/n435e046b6a67)を公開した。本記事では、この比較を起点に両ツールの位置づけを整理する。

## そもそも何が違うのか

一言でまとめると、**Claude Code は「開発」、OpenClaw は「運用・自動化」**のためのツールだ。

| 観点 | Claude Code | OpenClaw |
|------|------------|----------|
| 開発元 | Anthropic（プロプライエタリ） | Peter Steinberger（オープンソース） |
| 主な用途 | コーディング、PR レビュー、リファクタリング | 日常タスク自動化、DevOps、定期ジョブ |
| インターフェース | ターミナル CLI | メッセージングアプリ（Telegram, Discord, Signal 等） |
| 記憶 | セッションごとにリセット（CLAUDE.md で補完） | 永続メモリ（日記、TODO リスト、アイデンティティファイル） |
| 料金 | サブスクリプション（月額 $20〜）または API 従量課金 | 無料（接続する LLM API の料金のみ） |
| LLM | Claude モデル固定 | Claude, DeepSeek, GPT 等を選択可能 |
| セキュリティ | Anthropic が管理、安全ガードレール付き | ユーザー管理、システム権限を継承 |

## Claude Code が強い領域

Claude Code は SWE-bench で約 80.8% のスコアを達成しており、**複雑なコード変更やリファクタリング**において高い精度を発揮する。Extended Thinking による段階的な推論が、大規模な変更を安全に実行する鍵になっている。

強みをまとめると:

- **コード品質**: Hooks による PostToolUse リンター自動実行、プリコミットチェック
- **PR ワークフロー**: ブランチ作成→コミット→PR→レビューの一気通貫
- **エンタープライズ対応**: Team / Enterprise プラン、Code Review 機能
- **安全性**: 破壊的操作に対するガードレール

## OpenClaw が強い領域

OpenClaw（愛称 "Molty"）は、**常駐型の AI エージェント**だ。ターミナルで起動して終了する Claude Code と異なり、バックグラウンドで動き続け、cron ジョブやウェブフックでタスクを実行する。

強みをまとめると:

- **永続メモリ**: 過去の作業を記憶し、文脈を維持する
- **24/7 稼働**: 夜間にコードを書き、朝には結果が出ている
- **メッセージング統合**: Telegram や Discord から指示を出せる（後述）
- **完全カスタマイズ**: オープンソースのため内部ロジックを自由に変更可能
- **ローカルファースト**: Raspberry Pi でも動作する

### なぜ Telegram なのか

OpenClaw の通知・対話チャネルとして Telegram がよく使われる理由がある。

- **Bot API が無料かつ高機能**: Telegram Bot API はレートリミットが緩く、メッセージ送信・ファイル添付・インラインボタンなどを無料で利用できる。Slack のように有料プランが必要になるケースがない
- **双方向対話が自然**: 通知を受け取るだけでなく、その場で「詳細を見せて」「修正して」と指示を返せる。OpenClaw にとってメッセージングアプリは単なる通知先ではなく、**ユーザーとの対話インターフェース**そのものだ
- **モバイルからの操作**: PC を開かなくてもスマートフォンから AI エージェントに指示を出せる。深夜にアラートを受けたとき、ベッドの中から「ロールバックして」と返信するだけで対処できる
- **プライバシー**: Telegram はエンドツーエンド暗号化（シークレットチャット）に対応しており、API キーやエラーログなどの機密情報を含む通知でも比較的安全に扱える

もちろん Discord、Signal、WhatsApp なども利用可能だが、Bot API の自由度とコストの面で Telegram が OpenClaw コミュニティのデファクトになっている。

## 「責務」で選ぶ

迷ったときの判断基準は**責務（responsibility）の分離**だ。

```
開発フェーズ → Claude Code
  コードを書く、テストする、レビューする、PR を出す

運用フェーズ → OpenClaw
  デプロイ後の監視、定期タスク、外部サービス連携、日常業務の自動化
```

この分け方は [CLAUDE.md 肥大化問題](https://zenn.dev/akasara/articles/b80fe3c8cc8569)とも関連する。Claude Code の CLAUDE.md に運用系の指示まで詰め込むと、開発時のコンテキストを圧迫する。開発と運用でツールを分けることで、それぞれの指示書をシンプルに保てる。

## 両方使うハイブリッド構成

実際には「どちらか一方」ではなく、**両方を組み合わせる**のが現実的な解だ。

1. **Claude Code** で機能開発・PR 作成
2. PR マージ後、**OpenClaw** がデプロイパイプラインを監視
3. 本番環境の異常を OpenClaw が検知し、Telegram で通知
4. 修正が必要なら Claude Code で対応

[ハーネスエンジニアリング](/posts/2026-03-09-harness-engineering/)の観点では、Claude Code は実行制御層（Hooks）が強く、OpenClaw は検証層（常駐監視）が強い。両者を組み合わせることで、ハーネスの全層をカバーできる。

### 実例: 遅い単体テストを高速化する

具体的なシナリオで責務分離を見てみよう。「単体テストの実行に 15 分かかるプロジェクト」を 3 分以内に短縮するケースを考える。

**Phase 1: 現状分析（Claude Code）**

まず Claude Code にテストスイートのボトルネックを特定させる。

```bash
# Claude Code に指示
> テストスイートが遅い。pytest --durations=50 の結果を分析して、
> 遅いテスト上位20件の原因を分類してください。
```

Claude Code はコードベースを横断的に読み、遅延原因を分類する:

- DB アクセスを伴うテスト（モック化されていない）
- 外部 API を呼んでいるテスト（タイムアウト待ちが発生）
- テストごとに重い fixture を再生成しているテスト
- sleep() がハードコードされたテスト

**Phase 2: リファクタリング（Claude Code）**

分析結果に基づき、Claude Code がコードを修正する。

```bash
# Claude Code に指示
> 以下の方針でテストをリファクタリングしてください:
> 1. DB アクセスは factory_boy + SQLite in-memory に置換
> 2. 外部 API 呼び出しは responses/respx でモック化
> 3. 重い fixture は session スコープに変更
> 4. sleep() は freezegun/time-machine に置換
> 各変更後にテストが通ることを確認してから次に進むこと。
```

Claude Code は変更 → テスト実行 → 確認のループを回しながら、PR を作成する。テスト時間が 15 分 → 3 分に短縮されたことをコミットメッセージに記録する。

**Phase 3: 継続監視（OpenClaw）**

ここから OpenClaw の出番だ。せっかく高速化しても、新しいテストが追加されるたびに再び遅くなるリスクがある。OpenClaw に「テスト実行時間の番人」を任せる。

```yaml
# OpenClaw の cron ジョブ設定
schedule: "0 2 * * *"  # 毎日深夜2時
task: |
  1. main ブランチの最新コードで pytest --durations=20 を実行
  2. 総実行時間が 3 分を超えたら警告
  3. 前回より 10% 以上遅くなったテストを特定
  4. 結果を Telegram に通知
```

OpenClaw は永続メモリを持つため、過去の実行結果との比較が可能だ。「先週は 2 分 48 秒だったが今日は 3 分 22 秒、原因は `test_payment_flow` が 30 秒増加」といったトレンド分析を自動で行える。

**Phase 4: 再改善ループ（Claude Code + OpenClaw）**

OpenClaw が劣化を検知したら、Claude Code に修正を依頼する流れになる。

```
OpenClaw（検知）→ Telegram 通知
  「テスト実行時間が 3:22 に劣化。test_payment_flow が +30s」

開発者 → Claude Code（修正）
  「test_payment_flow を分析して高速化して」

Claude Code（修正）→ PR 作成

OpenClaw（確認）→ 翌日の定期実行で改善を確認
  「テスト実行時間 2:51 に回復 ✓」
```

このように、**Claude Code が「改善する」、OpenClaw が「維持する」**という責務分離が、持続的なコード品質の改善サイクルを実現する。

## セキュリティ上の注意

OpenClaw はシステム権限を継承するため、設定を誤るとファイル削除や認証情報の漏洩につながるリスクがある。導入時は:

- 専用ユーザーで実行し、権限を最小化する
- API キーの保管場所を分離する
- 実行可能なコマンドをホワイトリストで制限する

Claude Code は Anthropic のガードレールが組み込まれている分、デフォルトでの安全性は高いが、そのぶん「意図した操作がブロックされる」ケースもある。

## まとめ

「どっちを勉強すべき？」への回答は「**まず Claude Code、次に OpenClaw**」が現実的だ。コーディングエージェントとしての完成度は Claude Code が一歩先を行っており、学習コストも低い。OpenClaw は Claude Code を使いこなした上で、運用自動化のニーズが出てきたときに導入すると効果が大きい。

重要なのは、どちらも「ハーネス」なしでは真価を発揮しないということだ。ツールの選定と同時に、[ハーネスの設計](/posts/2026-03-09-harness-engineering/)にも投資することが、AI エージェント時代の開発者に求められている。

## 参考

- [AI駆動塾 — マジで世界一やさしいClaude Codeの教科書](https://note.com/l_mrk/n/n435e046b6a67)
- [AI駆動塾 — マジで世界一やさしいOpenClawの教科書](https://note.com/l_mrk/n/n479da2092faf)
- [OpenClaw vs Claude Code — Analytics Vidhya](https://www.analyticsvidhya.com/blog/2026/03/openclaw-vs-claude-code/)
- [Claude Code × OpenClaw の責務分離 — Zenn](https://zenn.dev/akasara/articles/b80fe3c8cc8569)
