---
title: "現代的サーバー監視の王道スタック — Prometheus + Loki + Grafana + Alloy で始めるオブザーバビリティ基盤"
date: 2026-05-08
lastmod: 2026-05-08
draft: false
categories: ["クラウド/インフラ"]
tags: ["Prometheus", "Loki", "Grafana", "Alloy", "オブザーバビリティ", "サーバー監視", "PromQL", "LogQL", "監視", "SRE"]
---

サーバー監視は「死活監視 + リソース監視」の時代から、**「メトリクス + ログ + トレース」を 1 つの画面で相関分析する**オブザーバビリティの時代に移りました。クラウドネイティブ環境では、**Grafana Labs の OSS スタック**（Prometheus + Loki + Grafana + Alloy）が、コスト・自由度・運用ノウハウの蓄積において事実上の王道になっています。

この記事では、なぜこの組み合わせが現代の標準なのか、各コンポーネントがどう役割分担しているのか、そして最小構成から本番運用までの全体像を整理します。

![Prometheus・Loki・Tempo を Grafana Alloy が一括収集し、Grafana で可視化するサーバー監視スタックの全体構成図。各サーバー / コンテナで Alloy がメトリクス・ログ・トレースを収集し、Prometheus / Loki / Tempo に振り分け、Grafana が PromQL と LogQL でクエリしてダッシュボード化、Slack/メールにアラート通知する流れを示している](/blogs/images/loki-grafana-alloy-stack.png)

## なぜこの構成が「王道」なのか

サーバー監視の選択肢は大きく分けて 3 系統あります。

| カテゴリ | 代表例 | 特徴 |
|---|---|---|
| **OSS スタック（Grafana Labs）** | Prometheus + Loki + Grafana + Alloy | 無料、自由度高、運用責任は自分で |
| **OSS スタック（Elastic）** | Elasticsearch + Logstash + Kibana + Beats | 全文検索が強力、コストとリソース消費が大 |
| **SaaS** | Datadog、New Relic、Grafana Cloud | 楽だが高価、データ主権がない |

このうち **Prometheus + Loki + Grafana + Alloy** が王道とされる理由:

1. **Prometheus が事実上のメトリクス標準** — Kubernetes が同梱する `kube-state-metrics` や CNCF プロジェクトの大半が Prometheus 形式でメトリクスを公開
2. **Loki がコスト効率で ELK を凌駕** — ラベルのみインデックスで運用コストが数分の一
3. **Grafana が可視化のデファクト** — どのデータソース（CloudWatch / Prometheus / Loki / Datadog）でも同じ UI で扱える
4. **Alloy で収集エージェントが 1 種類に統合された** — メトリクス・ログ・トレース別々に Agent を入れていた時代から進化
5. **同じラベル思想でメトリクスとログが結合** — Loki は最初から「ログ版 Prometheus」として設計され、相関分析が標準動線

## 4 コンポーネントの役割分担

### ① Grafana Alloy（統合収集エージェント）

各サーバー / コンテナにインストールされる**唯一のエージェント**。メトリクス・ログ・トレースを 1 プロセスで収集して、それぞれの宛先に振り分けます。

- 旧 Grafana Agent + Promtail + OpenTelemetry Collector の機能を統合
- **Promtail は 2026-03-02 で EOL** — 新規構築・既存環境ともに Alloy が標準
- 設定ファイル形式は HCL ライクな Alloy syntax
- `alloy convert` コマンドで Promtail 設定を自動変換可能

```hcl
// alloy/config.alloy
// メトリクス: node_exporter からスクレイプ
prometheus.scrape "node" {
  targets    = [{__address__ = "localhost:9100"}]
  forward_to = [prometheus.remote_write.default.receiver]
}

prometheus.remote_write "default" {
  endpoint {
    url = "http://prometheus:9090/api/v1/write"
  }
}

// ログ: ファイルから収集
loki.source.file "syslog" {
  targets    = [{__path__ = "/var/log/syslog", job = "syslog", host = "web-01"}]
  forward_to = [loki.write.default.receiver]
}

loki.write "default" {
  endpoint {
    url = "http://loki:3100/loki/api/v1/push"
  }
}
```

エージェント運用の観点では、**「マシンに 1 種類のバイナリだけインストールすればよい」**ことが Alloy 統合の最大の恩恵です。

### ② Prometheus（メトリクスの収集・保存・クエリ）

時系列データベース + クエリエンジン + アラートエンジンが一体化したコンポーネント。

- **Pull 型** — Prometheus 側がエクスポーター（`/metrics` エンドポイント）を定期スクレイプ
- **`node_exporter`、`cadvisor`、`kube-state-metrics` などのエクスポーターが豊富** — CPU・メモリ・ディスク・ネットワーク・コンテナ・K8s リソースを標準で収集可能
- **PromQL** という時系列に特化したクエリ言語
- **アラートルール** を YAML で定義 → Alertmanager 経由で Slack / メール / PagerDuty へ
- **長期保存は外部にオフロード** — Thanos / Mimir / Cortex で数ヶ月〜数年のデータを保持可能

```yaml
# prometheus/rules.yaml
groups:
  - name: server-health
    rules:
      - alert: HighCpuUsage
        expr: 100 - (avg by (instance) (rate(node_cpu_seconds_total{mode="idle"}[5m])) * 100) > 80
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "{{ $labels.instance }} の CPU 使用率が 80% を超過"
```

Prometheus が**システムの「異常検知エンジン」**を担うため、本番運用では事実上必須です。

### ③ Loki（ログの集約・保存・検索）

「ログ版 Prometheus」として設計された軽量ログアグリゲーション。

- **ラベルのみインデックス** — 全文インデックスを作らないので、ストレージとメモリが劇的に少ない
- **本文は圧縮して object store に保存** — S3 / GCS / Azure Blob / ローカル
- **LogQL** で検索 — Prometheus と同じラベルセレクタの語彙
- **マルチテナント対応** — 大規模運用ではテナント分離可能
- **retention をラベル単位で制御** — エラーログは長期、デバッグは短期、など

Prometheus と**全く同じラベル**（`{job, env, host, ...}`）でログが識別されるため、メトリクスから同じセレクタでログにジャンプできます。

### ④ Grafana（統合ダッシュボード・アラート UI）

すべてのデータソースを束ねる可視化レイヤー。

- **データソース不問** — Prometheus / Loki / Tempo / CloudWatch / Datadog / SQL DB すべて同じ UI
- **ダッシュボード** — JSON / YAML でコード化、Git 管理可能
- **アラート** — Prometheus 由来のアラートと Grafana ネイティブアラートを統合管理
- **Explore モード** — 即興で PromQL / LogQL を投げて相関分析
- **メトリクス → ログのドリルダウン**が 1 クリックで完結（Data link 機能）

## トレースを足すなら Tempo（オプション）

マイクロサービス環境では分散トレースが重要になります。Grafana Labs スタックでは **Tempo** が担当:

- OpenTelemetry / Jaeger / Zipkin プロトコル対応
- Object store ベースで Loki と同じ低コスト思想
- Trace ID で Loki ログと紐付け（ログに `trace_id=...` を仕込めば、ログから該当トレースへジャンプ）

ただし**最初の段階では Prometheus + Loki だけで十分**です。トレースは「マイクロサービス化が進んでから追加」で問題ありません。

## ELK / SaaS との比較

| 観点 | Prometheus + Loki + Grafana | ELK | Datadog |
|---|---|---|---|
| **メトリクス** | Prometheus（標準） | Metricbeat（やや弱い） | 標準 |
| **ログ** | Loki（軽量） | Elasticsearch（高機能・重） | 標準 |
| **トレース** | Tempo | APM | 標準 |
| **可視化 UI** | Grafana | Kibana | 専用 UI |
| **インデックス戦略** | ラベルのみ | ログ全文 | 全文 |
| **運用コスト** | 低（OSS、自前運用） | 中〜高 | 高（SaaS） |
| **学習コスト** | PromQL + LogQL | DSL + KQL | 専用 UI |
| **ベンダーロック** | なし（OSS） | なし（OSS） | あり |
| **SaaS 化の選択肢** | Grafana Cloud | Elastic Cloud | Datadog のみ |

OSS で自前運用するなら **Prometheus + Loki + Grafana** がコスト最適。「運用したくない」なら **Grafana Cloud** で同じスタックを SaaS 化する道もあり、移行性が高いです。

## docker-compose で 5 分で起動する最小構成

ローカルで全体を動かす最小例:

```yaml
# docker-compose.yml
services:
  prometheus:
    image: prom/prometheus:latest
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml

  node-exporter:
    image: prom/node-exporter:latest
    ports:
      - "9100:9100"
    volumes:
      - /proc:/host/proc:ro
      - /sys:/host/sys:ro
      - /:/rootfs:ro
    command:
      - --path.procfs=/host/proc
      - --path.sysfs=/host/sys

  loki:
    image: grafana/loki:3.7
    ports:
      - "3100:3100"
    command: -config.file=/etc/loki/local-config.yaml

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
# prometheus.yml
scrape_configs:
  - job_name: node
    static_configs:
      - targets: ["node-exporter:9100"]
```

```yaml
# grafana-datasources.yaml
apiVersion: 1
datasources:
  - name: Prometheus
    type: prometheus
    url: http://prometheus:9090
  - name: Loki
    type: loki
    url: http://loki:3100
```

`docker compose up -d` で `http://localhost:3000` を開けば、両データソースが繋がった Grafana が起動します。

## 監視の 3 階層と各コンポーネントの守備範囲

実用的な監視は **「死活 → リソース → アプリケーション」**の 3 階層で考えると整理しやすいです。

| 階層 | 監視対象 | 主な担当 |
|---|---|---|
| **死活監視** | Ping、HTTP ヘルスチェック | Prometheus（`blackbox_exporter`） |
| **リソース監視** | CPU、メモリ、ディスク、ネットワーク | Prometheus（`node_exporter`、`cadvisor`） |
| **アプリ監視** | エラーログ、レスポンスタイム、ビジネスメトリクス | Prometheus（独自エクスポーター） + Loki |

「ログだけあればいい」というケースはほぼなく、**3 階層をカバーするにはメトリクスとログの両方が必須**です。

## メトリクスからログへドリルダウンする実践フロー

王道スタックの真価は「**異常検知 → ログでの原因分析**」が画面遷移なく繋がる点です。

### シナリオ: API のレスポンスタイムが急に悪化した

1. **Grafana ダッシュボード**で `histogram_quantile(0.95, ...)` の 95%ile レイテンシが 200ms → 2000ms に急上昇したと検知
2. グラフをクリック → **時間範囲・該当ホストを自動セット**して Loki Explore に遷移
3. `{job="api", host="api-01"}` のログを LogQL で表示
4. `|= "ERROR"` でエラー絞込、または `| json | response_time_ms > 1000` で遅いリクエストだけ抽出
5. スタックトレースから「DB 接続プール枯渇」が原因と特定
6. 必要なら `count_over_time({job="api"} |= "connection pool exhausted" [1m])` でメトリクス化してアラート追加

このフローが**同じ Grafana 画面内で完結**するのが、Prometheus + Loki セット運用の核心的な価値です。

## Kubernetes での標準構成

クラウドネイティブ環境では **kube-prometheus-stack（Helm chart）** が事実上の標準セットアップ:

```bash
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm install monitoring prometheus-community/kube-prometheus-stack \
  --set grafana.enabled=true \
  --set prometheusOperator.enabled=true
```

これで以下が一括導入されます:

- Prometheus Operator（Prometheus を K8s リソースとして管理）
- Prometheus 本体
- Alertmanager
- Grafana（kube-state-metrics ダッシュボード組み込み済み）
- node-exporter（DaemonSet）
- kube-state-metrics

ログ側は別途 Loki と Alloy を入れます:

```bash
helm install loki grafana/loki-stack
helm install alloy grafana/alloy
```

K8s 環境では Pod のラベルが Prometheus / Loki 両方のラベルにそのまま伝播するため、**ラベル設計を悩む必要がほぼなくなる**のが大きな利点です。

## 本番運用での注意点

### 1. ラベルのカーディナリティ爆発（Loki / Prometheus 共通）

**最大のアンチパターン**。`user_id` や `request_id` のような高カーディナリティ値をラベルに入れると、両者ともインデックスが膨張して性能が劇的に劣化します。

- **NG**: `{job="api", user_id="12345"}`
- **OK**: ラベルは `{job, env, host, method}` 程度に抑え、可変値はログ本文 / メトリクス値として扱う

### 2. メトリクスの retention と長期保存

Prometheus 単体は数週間程度の保存が現実的。それ以上は Thanos / Mimir / Grafana Cloud で長期保存を別途構成。

### 3. アラート設計の規律

- **Symptom-based alert（症状ベース）**: 「ユーザー影響があるか」を起点にアラート設計
- **Cause-based alert（原因ベース）の濫用を避ける** — 「ディスク使用率 80%」より「書き込みエラー率上昇」の方が実用的
- アラート疲れを避けるため、`for: 5m` で短期スパイクを除外、`severity` で優先度分け

### 4. Promtail からの移行スケジュール

既存環境がある場合は **EOL（2026-03-02）が過ぎているので最優先で移行**:

```bash
alloy convert --source-format=promtail config.yaml -o config.alloy
```

設定の 9 割は自動変換されます。

### 5. 認証とアクセス制御

シングルバイナリ運用ではマルチテナント機能が無効化されているケースが多い。本番では:

- Grafana の前段に OAuth Proxy / Authelia
- Prometheus / Loki への直接アクセスはネットワーク分離 or Basic 認証
- マルチテナント運用なら `auth_enabled: true` + テナントヘッダ

## 適しているケース・向かないケース

### 王道スタックが向いているケース

- **Kubernetes / コンテナ環境** — エコシステムが完璧に揃う
- **オンプレ + クラウド混在** — どこでも同じ構成で動く
- **OSS で自前運用したい** — ベンダーロックを避けたい
- **コストを抑えたい** — 大規模ログを object store にオフロード可能
- **将来 SaaS 化の選択肢を残したい** — Grafana Cloud に同じスタックで移行可能

### 向かないケース

- **小規模・単一サーバーで運用負担を最小化したい** — Datadog などの SaaS の方が早い
- **複雑な全文検索が主用途** — ELK の方が向いている
- **すでに別の監視 SaaS が組織標準** — 移行コストに見合わない

## まとめ

サーバー監視の現代的な王道は:

- **Prometheus** がメトリクスの異常検知エンジン
- **Loki** がログの低コスト集約（Prometheus と同じラベル思想で結合）
- **Grafana** が両者を統合した可視化・アラート UI
- **Alloy** が 3 つのテレメトリ（メトリクス・ログ・トレース）を 1 エージェントで収集

「Prometheus 抜きで Loki だけ」「Loki 抜きで Prometheus だけ」のどちらも成立はするものの、本来は **2 つセットで使う前提の設計**で、片方だけでは現代の障害対応のスピードに追いつきません。

新規構築では **Prometheus + Loki + Grafana + Alloy** を最初から揃え、必要に応じて Tempo（トレース）、Mimir / Thanos（長期保存）を追加するのが、運用コストと将来の拡張性のバランスが最も取れた選択です。docker-compose で 5 分で起動できるので、まずはローカルで全体を触って感覚を掴むのが最良の入口です。

## 参考リンク

- [Prometheus 公式ドキュメント](https://prometheus.io/docs/)
- [Grafana Loki 公式ドキュメント](https://grafana.com/docs/loki/latest/)
- [Grafana Alloy 公式ドキュメント](https://grafana.com/docs/alloy/latest/)
- [kube-prometheus-stack（Helm chart）](https://github.com/prometheus-community/helm-charts/tree/main/charts/kube-prometheus-stack)
- [Promtail から Alloy への移行ガイド](https://grafana.com/docs/loki/latest/setup/migrate/migrate-to-alloy/)
- [PromQL リファレンス](https://prometheus.io/docs/prometheus/latest/querying/basics/)
- [LogQL リファレンス](https://grafana.com/docs/loki/latest/query/)
