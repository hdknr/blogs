---
title: "Loki + Grafana で軽量ログ監視を構築する — Promtail EOL を機に Alloy へ移行する PLG → ALG スタック"
date: 2026-05-08
lastmod: 2026-05-08
draft: false
categories: ["クラウド/インフラ"]
tags: ["Loki", "Grafana", "Alloy", "Promtail", "ログ監視", "オブザーバビリティ", "Prometheus", "PLG スタック", "LogQL"]
---

サーバー監視において**ログを安く・軽く・横断的に検索できる**スタックとして、Grafana Labs の **Loki + Grafana** は既にデファクトの一つになっています。従来は **Promtail + Loki + Grafana = PLG スタック**と呼ばれてきましたが、**Promtail は 2026 年 3 月 2 日に EOL（End of Life）を迎え**、後継として **Grafana Alloy** への移行が公式推奨となりました。

この記事では、Loki + Grafana の本質的な設計思想と、Alloy 時代の現代的な構築・運用方法を整理します。

![Loki + Grafana + Alloy のログ監視スタック構成図。各サーバーの Alloy エージェントがログを収集してラベル付きで Loki に転送、Grafana がダッシュボードと LogQL クエリで可視化、Prometheus メトリクスとも統合される流れを示している](/blogs/images/loki-grafana-alloy-stack.png)

## なぜ Loki + Grafana なのか — 設計思想の核心

Loki の最大の特徴は、**ログ本文を全文インデックス化しない**点です。これは Elasticsearch（ELK スタック）との根本的な違いで、運用コストを劇的に下げます。

### ラベルのみインデックス、本文は圧縮保存

Loki が保存するのは:

- **ラベル**（`{job="nginx", env="prod", host="web-01"}` のようなメタデータ）→ インデックス化
- **ログ本文** → そのまま圧縮（gzip / snappy）してオブジェクトストレージ（S3 / GCS / ローカル）に保存

「全文検索」は LogQL の grep 的なフィルタで実行時に走らせる方式です。「事前にすべてをインデックスする」コストを払わない代わりに、**「クエリを発行したラベルの範囲だけスキャンする」**設計になっています。

### Prometheus と同じ思想

Loki は **「ログ版 Prometheus」**として設計されました。Prometheus がメトリクスを `{job="api", method="GET"}` のラベルで識別するのと同じ語彙でログを扱います。これにより、

- メトリクス（Prometheus）とログ（Loki）が**同じラベルセット**で結びつく
- Grafana 上でメトリクス異常 → 該当時間帯のログへ**画面遷移なしで掘り下げ**

という、トラブルシューティングの基本動作がシームレスになります。

## スタックを構成する 3 つのコンポーネント

### ① Grafana Alloy（収集・転送エージェント）

各サーバー / コンテナにインストールされ、ログを読み取って Loki へ送信します。**従来の Promtail の後継**で、以下の特徴があります。

- **ログ・メトリクス・トレースを 1 エージェントで扱える** — Promtail（ログ専用）、Grafana Agent（旧）、OpenTelemetry Collector の機能を統合
- **設定言語が River → Alloy syntax に進化** — HCL ライクで読み書きしやすい
- **Promtail からの移行ツールが提供済み** — `alloy convert` コマンドで既存設定を変換可能

```hcl
// alloy/config.alloy
loki.source.file "system_logs" {
  targets    = [{__path__ = "/var/log/syslog", job = "syslog", host = "web-01"}]
  forward_to = [loki.write.default.receiver]
}

loki.write "default" {
  endpoint {
    url = "http://loki:3100/loki/api/v1/push"
  }
}
```

> **Promtail EOL タイムライン**: 2025-02-13 に LTS 移行宣言、**2026-03-02 EOL**。新規構築は Alloy 一択。既存 Promtail 環境は移行スケジュールを立てるべき時期。

### ② Loki（ログ集約・蓄積）

Alloy から送られたログを受け取り、ラベルでインデックスして圧縮保存します。

- **シングルバイナリで動く** — 開発・小規模運用は単一プロセスで OK
- **マイクロサービスモード** — 大規模環境では distributor / ingester / querier に分離してスケール
- **ストレージは object store** — S3、GCS、Azure Blob、ローカルファイルシステム
- **保持期間（retention）はラベル単位で設定可能** — エラーログだけ長期保存、デバッグログは 7 日、など

### ③ Grafana（可視化・アラート）

Loki に蓄積されたログを LogQL で検索し、ダッシュボード化・アラート化します。Prometheus データソースと組み合わせれば、**メトリクスとログの相関分析**が標準でできます。

## ELK スタックとの比較

| 観点 | ELK（Elasticsearch + Logstash + Kibana） | Loki + Grafana + Alloy |
|---|---|---|
| **インデックス戦略** | ログ全文をインデックス | ラベルのみインデックス |
| **ストレージ消費** | 大（インデックスが本文の数倍） | 小（圧縮ログ + 軽量インデックス） |
| **メモリ消費** | 大（インデックスをキャッシュ） | 小 |
| **クエリ速度** | 全文検索は高速 | ラベル絞込前提なら高速、フリーテキストは遅い |
| **スケール運用** | クラスタ運用が複雑 | object store にオフロード可能で楽 |
| **コスト** | 高（特に大規模） | 低 |
| **メトリクス統合** | 別途設定が必要 | Prometheus と同じ思想で自然 |

**「とにかく全文検索したい」→ ELK**、**「ラベルで絞り込んだ範囲を見たい・コストを抑えたい」→ Loki** という棲み分けです。

## docker-compose で 5 分で起動する最小構成

ローカルで動作確認する最小構成:

```yaml
# docker-compose.yml
services:
  loki:
    image: grafana/loki:3.7
    ports:
      - "3100:3100"
    command: -config.file=/etc/loki/local-config.yaml
    volumes:
      - ./loki-config.yaml:/etc/loki/local-config.yaml

  alloy:
    image: grafana/alloy:latest
    ports:
      - "12345:12345"
    volumes:
      - ./alloy-config.alloy:/etc/alloy/config.alloy
      - /var/log:/var/log:ro
    command:
      - run
      - /etc/alloy/config.alloy
      - --server.http.listen-addr=0.0.0.0:12345
    depends_on:
      - loki

  grafana:
    image: grafana/grafana:latest
    ports:
      - "3000:3000"
    environment:
      - GF_AUTH_ANONYMOUS_ENABLED=true
      - GF_AUTH_ANONYMOUS_ORG_ROLE=Admin
    volumes:
      - ./grafana-datasources.yaml:/etc/grafana/provisioning/datasources/datasources.yaml
```

```yaml
# grafana-datasources.yaml
apiVersion: 1
datasources:
  - name: Loki
    type: loki
    access: proxy
    url: http://loki:3100
    isDefault: true
```

`docker compose up -d` で `http://localhost:3000` を開けば、即座に Loki データソースが繋がった Grafana が立ち上がります。

## LogQL の基本パターン

LogQL は「**ラベルセレクタ → ログパイプライン → 集計**」の 3 段構成です。

### 1. 基本のフィルタ

```logql
# nginx ログから 5xx エラーだけ抽出
{job="nginx"} |= "HTTP/1.1\" 5"

# 複数ラベル + 否定マッチ
{job="api", env="prod"} != "healthcheck"

# 正規表現
{job="app"} |~ "user_id=[0-9]+"
```

### 2. JSON / logfmt パース

```logql
# JSON ログをパースしてフィールド抽出
{job="api"} | json | level="error" | line_format "{{.timestamp}} {{.message}}"

# logfmt 形式
{job="caddy"} | logfmt | status >= 500
```

### 3. ログからメトリクスを生成

```logql
# 1 分あたりのエラー件数
sum by (host) (rate({job="api"} |= "ERROR" [1m]))

# パーセンタイル応答時間（response_time_ms フィールドを抽出）
quantile_over_time(0.95,
  {job="api"} | json | unwrap response_time_ms [5m]
) by (endpoint)
```

このメトリクス化機能のおかげで、**ログから直接アラートルールを作る**ことが可能です。

## Prometheus との統合 — 真価を発揮する組み合わせ

Loki 単体でも便利ですが、**Prometheus と組み合わせて初めて真価を発揮**します。Grafana ダッシュボード上で:

1. Prometheus パネルで CPU 使用率の異常スパイクを発見
2. クリックでその時間範囲・該当ホストを Loki クエリにドリルダウン
3. 同じ時間帯のエラーログを LogQL で表示
4. 必要ならログから抽出したメトリクスで根本原因を特定

という、**メトリクス → ログ → 原因分析**の流れが画面遷移なしに完結します。これが ELK 単体や CloudWatch Logs にない優位性です。

### 推奨される最小オブザーバビリティスタック

```text
Alloy（収集）─┬─ Loki         （ログ）
              ├─ Prometheus   （メトリクス、または Mimir）
              └─ Tempo        （トレース）
                  ↓
              Grafana（可視化・アラート）
```

Alloy が 1 つあれば 3 種類のテレメトリすべてを扱えるため、エージェント分散の運用負担も最小化できます。

## 本番運用での落とし穴と対策

### 1. ラベルの「カーディナリティ爆発」

**最大のアンチパターン**です。`user_id` や `request_id` のような**高カーディナリティ値をラベルに入れると、Loki のインデックスが膨れ上がり、性能が劇的に劣化**します。

- **NG**: `{job="api", user_id="12345"}`
- **OK**: ラベルは `{job="api", env="prod", method="GET"}` 程度に抑え、`user_id` はログ本文に入れて LogQL の `| json | user_id="12345"` で抽出

ラベルは「**カーディナリティが低く、検索の絞り込みに使う**」属性だけに限定するのが鉄則です。

### 2. retention とコスト

S3 にオフロードしても、**ストレージ + クエリ時のスキャンコスト**は積み上がります。対策:

- ログレベル別に retention を分ける（ERROR は 90 日、INFO は 7 日）
- `compactor` を有効化して chunk を統合
- 重要度の低いログは送らない（Alloy 側でフィルタ）

### 3. Alloy への移行スケジュール

既存 Promtail 環境がある場合:

```bash
# Alloy 公式の変換ツール
alloy convert --source-format=promtail config.yaml -o config.alloy
```

設定の 9 割は自動変換されるため、移行コストは想像より低いです。**EOL（2026-03-02）後はセキュリティパッチも止まる**ため、放置せず計画しましょう。

### 4. 認証・マルチテナント

シングルバイナリの Loki はデフォルトで `X-Scope-OrgID: fake` の単一テナント前提。本番では:

- Loki の前段にリバースプロキシ（nginx / Caddy）を立てて Basic 認証 or OAuth
- マルチテナント運用なら `auth_enabled: true` + テナント ID をヘッダで送信
- Grafana Cloud Loki を使えば認証は SaaS 側で管理される

## 適しているケース・向かないケース

### 向いているケース

- **コンテナ / Kubernetes 環境** — Pod のラベルがそのまま Loki ラベルになる、自然な設計
- **すでに Grafana / Prometheus を使っている** — エコシステムが揃う、設定が最小
- **大量ログを安価に長期保存したい** — S3 など object store にオフロードでコスト最適化
- **メトリクス + ログの相関分析が重要** — 障害対応の標準動線

### 向かないケース

- **複雑な全文検索が主な用途** — 「過去のログから特定キーワードを縦横無尽に検索」が要件なら ELK の方が速い
- **構造化されていないログを大量に投げ込みたい** — ラベル設計の規律が必須
- **既に ELK の運用ノウハウが社内にある** — 移行コストに見合わない可能性

## まとめ

Loki + Grafana + Alloy のスタックは、

- **ログ全文インデックスを捨てた割り切り**で、ELK の数分の一のコストで運用できる
- **Prometheus と同じラベル思想**でメトリクス・ログ・トレースを統合できる
- **Alloy 統合**でエージェントが 1 種類に集約され、運用が単純化された
- **2026-03-02 の Promtail EOL** を機に、新規構築・移行ともに Alloy が標準

Kubernetes / コンテナ時代のオブザーバビリティ基盤としては、現時点で最もコストパフォーマンスが高い構成の一つです。docker-compose で 5 分で起動できるので、まずはローカルで触ってラベル設計の感覚を掴むのが入り口として最適です。

## 参考リンク

- [Grafana Loki 公式ドキュメント](https://grafana.com/docs/loki/latest/)
- [Grafana Alloy 公式ドキュメント](https://grafana.com/docs/alloy/latest/)
- [Promtail から Alloy への移行ガイド](https://grafana.com/docs/loki/latest/setup/migrate/migrate-to-alloy/)
- [Promtail EOL 告知（Grafana Community）](https://community.grafana.com/t/promtail-end-of-life-eol-march-2026-how-to-migrate-to-grafana-alloy-for-existing-loki-server-deployments/159636)
- [LogQL リファレンス](https://grafana.com/docs/loki/latest/query/)
