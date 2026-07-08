## 概要

デッドリンクを CI で自動検出する GitHub Actions（lychee）を追加します。公開サイトを手動クロールしたところ内部リンクの構造バグが約 44 件見つかったため、再発防止として CI 化します（Phase 0）。本物の内部リンク修正は別 PR（Phase 1）で行います。

## 設計: 2 層構成

| ジョブ | トリガ | 対象 | 挙動 |
|---|---|---|---|
| `internal` | PR / push | 内部リンク・画像のみ | **失敗でブロック**。ビルド → `/blogs/` base path でローカルサーブ → lychee |
| `external` | 週次 cron / 手動 | 外部リンク | **非ブロッキング**。切れたら Issue 自動起票 |

### なぜローカルサーブなのか

baseURL が `/blogs/` のため、内部リンクを正しく検査するには本番同等のパス解決が要る。ビルド成果物を `_site/blogs/` にミラーしてローカルサーブし、lychee を通す。これにより:

- `/blogs/...` の正しいリンク → 200
- `/blogs` を欠いた `/posts/...` や、slug でなくファイル名（日付プレフィックス付き）を使った内部リンク → **404 として確実に検出**

これは直近 PR #535 で実際に踏みかけた内部リンク事故（`/blogs` 抜け）を機械的に止める仕組みです。

### 誤検知対策（`lychee.toml`）

手動クロールで「デッド」判定された外部 329 件のうち約 71 件は、bot に 403/429 を返すだけでブラウザでは開けるホスト（Bloomberg・axios・tabelog・Salesforce/MySQL docs・npmjs・sciencedirect・meti.go.jp 等）でした。これらを `lychee.toml` で `exclude` し、429/403 を `accept` することで、週次レポートを signal-rich に保ちます。内部ジョブは localhost のみ検査するため本設定を使いません。

## ローカル検証

lychee 0.24.2 をローカル取得し、ビルド済みサイトをミラー・サーブして内部検査コマンドを実地確認済み:

- favicon 系 5 件の欠落を検出
- `/posts/2026/03/harness-engineering/`（`/blogs` 抜け）を 404 として検出
- 外部リンクは `--include` により除外
- `lychee.toml` のパース・exclude 発火を確認

## 注意

- テーマは submodule のため CI は `submodules: recursive` でチェックアウトします（設定済み）。
- lychee / Hugo のバージョンはワークフロー内で pin しています（Hugo 0.157.0 / lychee 0.24.2）。

🤖 Generated with [Claude Code](https://claude.com/claude-code)
