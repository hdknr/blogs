---
title: "複数 API サーバーをまたぐ SPA の設計 — 分散トランザクションと重い処理をフロントに背負わせない実装パターン"
date: 2026-11-15
lastmod: 2026-11-15
slug: "distributed-api-spa-frontend-patterns"
draft: false
categories: ["Web開発"]
tags: ["API", "BFF", "Saga", "aws", "react"]
---

## はじめに

業務システムを機能ごとに分けた結果、**受注・在庫・請求といった業務ごとに API サーバーが別々に立ち、React の SPA がそれらを横断して呼び出す**という構成はよく見かけます。各 API は ECS（一部は EC2）で動き、それぞれ自分のデータベースを持っています。SPA は複数のオリジンへクロスオリジンでリクエストを送ります。

最初のうちはこれで回ります。ところが業務が増えるにつれて、次の 2 つの問題が目立ってきます。

1. **複数の API をまたぐ更新の作法が決まっていない。** 「受注を登録して、在庫を引き当てて、請求を作る」という一連の処理を、画面ごと・担当者ごとに違うやり方で書いている。途中で失敗したときの後始末も画面によって違う。
2. **帳票作成のような重い処理の置き場所が決まっていない。** HTTP リクエストの中で処理するとタイムアウトする。そこで一部の処理は、API から ECS タスクを直接起動して別サーバーで実行している。しかし、進み具合の確認・失敗時の再実行・同時実行数の制御は、それぞれの実装任せになっている。

この記事では、特定のシステムに依存しない一般的なアーキテクチャとして、**分散したサービスの前に立つ SPA をどう設計すればよいか**を整理します。結論を先に書くと、方針は次の 3 つです。

- **ブラウザにトランザクションを持たせない。** 複数サービスの更新はサーバー側の「操作」として 1 回で受け付け、フロントはその状態を見るだけにする
- **時間のかかる処理はすべて「ジョブ」として非同期にする。** `202 Accepted` と状態リソースという同じ形の API で統一する
- **入口を 1 つにまとめる。** 同一オリジン化と BFF で、CORS と認証の問題を構成で消す

## 用語とプロダクト

| 用語 / プロダクト | この記事での意味 |
|---|---|
| BFF（Backend for Frontend） | 特定のフロントエンド専用に置く薄いサーバー。認証・読み取りの集約・コマンド受付を担う |
| Saga | 複数サービスにまたがる処理を、ローカルなトランザクションの列と「失敗時に打ち消す補償処理」で組み立てるパターン |
| オーケストレーション / コレオグラフィ | Saga の 2 つの実装方式。司令塔が順に呼ぶか、各サービスがイベントに反応して動くか |
| 補償処理（Compensation） | 完了済みのステップを業務的に取り消す処理（引当解除、受注取消など） |
| 冪等キー（Idempotency Key） | 同じリクエストを何度送っても 1 回分しか効果が出ないようにするための、クライアントが付ける一意な値 |
| Transactional Outbox | DB の更新と「イベントを送る」記録を同じトランザクションで書き、別プロセスが確実に配信するパターン |
| Amazon CloudFront | AWS の CDN。パスのパターンごとに転送先（オリジン）を振り分ける「ビヘイビア」を設定できる |
| ALB（Application Load Balancer） | AWS の L7 ロードバランサー。ECS のサービスの前に置く |
| Amazon ECS / AWS Fargate | コンテナの実行基盤。常駐する「サービス」と、1 回だけ動かす「タスク」がある |
| AWS Step Functions | AWS のワークフローサービス。ステップの順序・リトライ・分岐・補償をステートマシンとして定義できる |
| Amazon SQS | AWS のメッセージキュー。失敗したメッセージを隔離するデッドレターキュー（DLQ）を持てる |
| TanStack Query | React などで使われるサーバー状態管理ライブラリ。キャッシュ・再取得・ポーリングを扱う |

## 目標アーキテクチャの全体像

![ブラウザの React SPA が CloudFront を単一の入口としてアクセスし、静的ファイルは S3 から、/api 配下は BFF へ振り分けられる構成図。BFF は読み取りを各業務 API から集約し、業務をまたぐ書き込みは Step Functions の Saga オーケストレーターに渡し、帳票などの重い処理は SQS のジョブキュー経由で ECS の帳票ワーカーに渡す。ワーカーは PDF を S3 に保存し、操作とジョブの状態は DynamoDB などに記録され、SPA はポーリングや通知でその状態を受け取る](/blogs/images/distributed-spa-architecture.png)

役割ごとに見ると、次のように分かれます。

| 層 | 役割 | やらないこと |
|---|---|---|
| SPA | 画面、入力、操作 ID とジョブ ID の状態表示 | 複数 API の更新を順番に呼ぶこと、失敗時の後始末 |
| CloudFront | 単一オリジンの入口、パスで振り分け | 業務ロジック |
| BFF | 認証の終端、読み取りの集約、コマンドの受付 | 長時間の処理、業務ルール |
| オーケストレーター | 業務をまたぐ更新の順序・リトライ・補償 | 画面に依存した処理 |
| 業務 API | 自分の業務データの整合性 | 他業務の DB を直接触ること |
| ジョブワーカー | 帳票などの重い処理 | 同期レスポンスを返すこと |

以降、問題ごとに詳しく見ていきます。

## 方針 1: フロントで分散トランザクションを組まない

最もよくある、そして最も危ない実装は、SPA が複数の API を順番に呼ぶ書き方です。

```typescript
// アンチパターン: フロントが分散トランザクションの司令塔になっている
async function confirmOrder(input: OrderInput) {
  const order = await ordersApi.create(input);          // ① 成功
  const reservation = await stockApi.reserve(order.id); // ② 成功
  await billingApi.createInvoice(order.id);             // ③ ここで失敗したら？
  await ordersApi.confirm(order.id);
}
```

このコードには、ブラウザ特有の壊れ方がいくつもあります。

- **途中でタブを閉じられる。** ② まで終わって ③ を呼ぶ前に閉じられたら、在庫だけ引き当てられた受注が残る。後始末をするコードはもう動いていない
- **ネットワークが切れたとき、成功したのか失敗したのか分からない。** 再送すると二重に引き当てるかもしれないし、再送しないと処理が抜けるかもしれない
- **補償処理が画面ごとに散らばる。** 同じ業務を別の画面から実行すると、失敗時の振る舞いが画面によって違う
- **権限の境界がブラウザに露出する。** 各 API に「この順番で呼ばれる前提」の更新権限を個別に与える必要がある

ブラウザは「いつ消えてもおかしくない、信頼できない実行環境」です。複数のサービスにまたがる整合性は、**落ちても続きから再開できるサーバー側の仕組み**に持たせるべきです。フロントがやるのは「この操作をしたい」と 1 回伝えて、その結果を見ることだけにします。

```typescript
// 推奨: フロントは「操作」を 1 回送り、状態を見るだけ
// idempotencyKey はボタン押下時に crypto.randomUUID() で 1 回だけ作り、再送でも同じ値を使う
async function confirmOrder(input: OrderInput, idempotencyKey: string) {
  const res = await api.post("/api/operations/confirm-order", input, {
    headers: { "Idempotency-Key": idempotencyKey },
  });
  return res.data.operationId; // あとは GET /api/operations/{id} で状態を見る
}
```

## 複数サービスをまたぐ更新: Saga を標準にする

### 分散トランザクション（2PC）は選ばない

2 相コミット（2PC）は、複数の DB をまたいで「全部成功か全部失敗か」を保証する仕組みです。しかし HTTP の API 同士では現実的ではありません。全サービスがロックを持ち合ったまま待つことになり、1 つが遅いと全体が止まります。マイクロサービスの文脈では、代わりに **Saga** を使うのが定石です。

Saga は「ローカルなトランザクションを順に実行し、途中で失敗したら、完了済みのステップを補償処理で逆順に打ち消す」という考え方です。この打ち消す処理が、いわゆる**補償トランザクション（Compensating Transaction）**です。DB のロールバックとは違い、「引当解除」「受注取消」のような業務上の操作として記録が残ります。Saga は、ローカルなトランザクションの列と、それぞれに対応する補償トランザクションを組み合わせた全体のパターンだと捉えると分かりやすいでしょう。一時的に不整合な状態（在庫は引き当てたが請求はまだ、など）が見えることを受け入れる代わりに、ロックを長く持たずに済みます。

### オーケストレーション型を標準にする

Saga には 2 つの実装方式があります。

| 方式 | 仕組み | 向いている場面 |
|---|---|---|
| オーケストレーション | 司令塔（オーケストレーター）が各サービスを順に呼び、失敗時に補償を指示する | 業務フローが明確で、全体の進み具合を 1 か所で見たい |
| コレオグラフィ | 各サービスがイベントを発行し、他のサービスがそれに反応して動く | サービス間の結合を最小にしたい、参加者が頻繁に増減する |

業務システムで「標準がない」ことが問題になっているなら、まずは**オーケストレーション型を標準に据える**のがおすすめです。フローが 1 つの定義に集まるので、「受注確定は今どこまで進んだか」「どこで失敗したか」を 1 か所で確認でき、業務担当者への説明もしやすくなります。

次の図は、受注確定をオーケストレーション型の Saga で組んだ例です。

![受注確定の Saga をオーケストレーション型で表した図。受注の仮登録、在庫の引当、請求の作成、受注の確定を順に実行し、すべて成功すれば状態が succeeded になる。請求の作成がリトライ上限を超えて失敗した場合は、在庫の引当解除、受注の取消という補償処理を逆順に実行し、状態が compensated になる。各ステップは Idempotency-Key 付きで呼ぶためリトライしても二重に引き当てない](/blogs/images/distributed-spa-saga.png)

AWS なら **Step Functions** がこの司令塔にそのまま使えます。リトライ（`Retry`）と失敗時の分岐（`Catch`）をステートマシンの定義に書けるので、補償の流れを宣言的に表現できます。図のうち、在庫引当と請求作成の部分だけを抜粋すると次のようになります（`"..."` は省略箇所です）。

```json
{
  "StartAt": "ReserveStock",
  "States": {
    "ReserveStock": {
      "Type": "Task",
      "Resource": "arn:aws:states:::http:invoke",
      "Parameters": {
        "ApiEndpoint": "https://stock.example.com/reservations",
        "Method": "POST",
        "InvocationConfig": { "ConnectionArn": "arn:aws:events:...:connection/..." },
        "Headers": { "Idempotency-Key.$": "$.operationId" },
        "RequestBody.$": "$.order"
      },
      "Retry": [{ "ErrorEquals": ["States.ALL"], "MaxAttempts": 3, "BackoffRate": 2 }],
      "Catch": [{ "ErrorEquals": ["States.ALL"], "Next": "CancelOrder" }],
      "Next": "CreateInvoice"
    },
    "CreateInvoice": {
      "Type": "Task",
      "Resource": "arn:aws:states:::http:invoke",
      "Parameters": { "...": "請求 API の呼び出し設定" },
      "Retry": [{ "ErrorEquals": ["States.ALL"], "MaxAttempts": 3, "BackoffRate": 2 }],
      "Catch": [{ "ErrorEquals": ["States.ALL"], "Next": "ReleaseStock" }],
      "End": true
    },
    "ReleaseStock": { "Type": "Task", "Resource": "...", "Next": "CancelOrder" },
    "CancelOrder":  { "Type": "Task", "Resource": "...", "Next": "Failed" },
    "Failed": { "Type": "Fail" }
  }
}
```

HTTP Task は EventBridge の接続（Connection）で認証情報を管理し、1 回の呼び出しは 60 秒でタイムアウトします。社内の API が VPC 内にしかない場合は、Lambda を挟んで呼ぶか、EventBridge の接続経由のプライベート API 呼び出しを使います。ただし後者は、公的に信頼された証明書を持つドメイン名の HTTPS エンドポイントが前提で、mTLS には対応していません。社内 CA の証明書しかない API なら Lambda を挟むほうが確実です。いずれにしても大事なのは「どの順で呼び、失敗したら何を打ち消すか」が**コードではなく定義として 1 か所にある**ことです。

### 業務 API 側の約束事

Saga を成り立たせるには、各業務 API が次の約束を守る必要があります。これを「社内 API の標準」として明文化しておくと、新しい業務を追加するときの議論が減ります。

1. **更新系 API は冪等にする。** `Idempotency-Key` ヘッダーを受け付け、同じキーでの再送には前回と同じ結果を返す。オーケストレーターのリトライで二重処理が起きないようにするため
2. **補償用の API を用意する。** 「引当」に対する「引当解除」、「仮登録」に対する「取消」を公開する。補償も冪等にする（2 回取り消しても壊れない）
3. **「仮」の状態を持つ。** いきなり確定させず、仮登録 → 確定の 2 段階にすると、補償が「削除」ではなく「取消」という業務的に自然な操作になる
4. **エラー形式を揃える。** RFC 9457（Problem Details for HTTP APIs）の `application/problem+json` に揃えておくと、オーケストレーターも SPA も同じ方法でエラーを解釈できる
5. **相関 ID を引き回す。** W3C Trace Context の `traceparent` ヘッダーなどを全サービスで伝播させ、1 つの操作のログを横断して追えるようにする

冪等キーの実装は、キーとレスポンスを保存するテーブルを 1 つ持つだけで始められます。

```python
# 更新系 API での冪等キーの扱い（擬似コード）
def handle(request):
    key = request.headers.get("Idempotency-Key")
    if key is None:
        return problem(400, "Idempotency-Key is required")

    saved = idempotency_store.get(key)
    if saved:
        if saved.request_hash != hash(request.body):
            return problem(422, "Idempotency-Key reused with different payload")
        return saved.response  # 前回と同じ結果を返す

    with db.transaction():
        result = do_business_logic(request)
        idempotency_store.put(key, hash(request.body), result)  # 同じトランザクションで保存
    return result
```

### 補足: イベントを確実に送るなら Outbox

オーケストレーション型でも、「受注が確定したら分析基盤や通知に知らせる」といったイベント連携は残ります。このとき「DB を更新した直後にメッセージを送る」と、更新は成功したのに送信だけ失敗する、ということが起きます。そこで **Transactional Outbox** パターンを使います。更新と同じトランザクションで outbox テーブルに書き、別プロセスがそれを読んで配信します。こうすると取りこぼしを防げます。

## 方針 2: 帳票などの重い処理は非同期ジョブに統一する

### HTTP リクエストの中で待たない

帳票作成のような処理を同期 API で実装すると、経路上のどこかのタイムアウトに必ず引っかかります。代表的な既定値は次のとおりです。

| 経路 | 既定のタイムアウト |
|---|---|
| CloudFront のオリジン応答タイムアウト | 30 秒 |
| ALB のアイドルタイムアウト | 60 秒 |
| API Gateway（REST API）の統合タイムアウト | 29 秒（Regional / private は 2024 年 6 月から緩和申請が可能） |

設定や上限緩和の申請で延ばせるものもありますが、延ばしても「ユーザーがその間ずっと画面で待たされる」「途中で接続が切れると結果が失われる」という問題は残ります。**数秒を超える可能性がある処理は、最初から非同期ジョブとして設計する**のが安全です。

### 202 Accepted + 状態リソースの形に揃える

非同期 API の形は 1 つに決めてしまいます。HTTP の意味論に沿った定番の形は次のとおりです。

![帳票作成の非同期ジョブのシーケンス図。SPA が Idempotency-Key 付きで POST /reports を送ると、BFF はジョブを SQS に登録して 202 Accepted と Location ヘッダーでジョブの URL を返す。帳票ワーカーが SQS からジョブを受信して実行し、その間 SPA は間隔を広げながら GET /jobs/{id} をポーリングする。ワーカーが PDF を S3 に保存して状態を succeeded に更新すると、SPA は署名付き URL を受け取り、S3 から直接ダウンロードする](/blogs/images/distributed-spa-async-job.png)

```http
POST /api/reports HTTP/1.1
Idempotency-Key: 3f6c1e1a-...
Content-Type: application/json

{ "type": "monthly-invoice", "month": "2026-10" }
```

```http
HTTP/1.1 202 Accepted
Location: /api/jobs/01J...
Content-Type: application/json

{ "jobId": "01J...", "status": "queued" }
```

`GET /api/jobs/{id}` の応答は次のとおりです。

```json
{
  "jobId": "01J...",
  "status": "succeeded",
  "progress": 100,
  "result": { "downloadUrl": "https://...署名付き URL...", "expiresAt": "2026-11-15T12:30:00Z" },
  "error": null
}
```

状態は `queued` → `running` → `succeeded` / `failed`（Saga なら `compensating` / `compensated` も）のように、**操作とジョブで同じ語彙を使う**とフロントの実装を共通化できます。前節の Saga の「操作」も、フロントから見れば同じ形のジョブとして扱えます。

### 「API から ECS タスクを直接起動」をキュー経由に置き換える

API の中から `RunTask` で ECS タスクを直接起動する方式は手軽ですが、規模が大きくなると次の問題が出ます。

- **同時実行数を制御できない。** 月末に帳票が集中すると、タスクが一気に起動してクォータや DB 接続数の上限に達する
- **失敗時の再実行が実装任せになる。** タスクが途中で落ちたら誰が再実行するのかが決まっていない
- **起動待ちが毎回かかる。** Fargate タスクの起動には数十秒程度かかることがあり、小さな帳票でもその分待たされる
- **進み具合を見る場所がない。** タスクの状態と業務的なジョブの状態が対応づいていない

これを **SQS + 常駐ワーカー（ECS サービス）** に置き換えると、多くが構成で解決します。

| 課題 | SQS + ワーカーでの解決 |
|---|---|
| 同時実行数 | ワーカーのタスク数（とその上限）で制御できる。キューの長さに応じたオートスケールも可能 |
| 再実行 | 処理中に落ちたメッセージは、可視性タイムアウト（受信中のメッセージを他のワーカーから見えなくしておく時間）が過ぎると再配信される。何度も失敗したものは DLQ に隔離される |
| 起動待ち | 常駐ワーカーならキューから取り出してすぐ処理できる。夜間は最小数まで縮める |
| 状態 | ワーカーがジョブ状態テーブルを更新し、BFF がそれを返す |

ワーカーはメッセージを複数回受け取りうる（SQS 標準キューは「少なくとも 1 回」の配信）ので、**ジョブ ID で冪等に処理する**ことを忘れないでください。

処理が「帳票を作って、承認者に通知して、外部に送信する」のように複数ステップになる場合は、Step Functions の ECS 統合（`arn:aws:states:::ecs:runTask.sync`）でタスクの完了まで待つ形にすると、リトライと状態管理をステートマシンに任せられます。単発の重い処理は SQS + ワーカー、複数ステップの業務フローは Step Functions、と使い分けるのが目安です。

### 結果は署名付き URL で直接渡す

生成した PDF を BFF 経由でストリーミングすると、BFF のメモリと帯域を消費し、再びタイムアウトの心配が出ます。**結果は S3 に置きます。そして有効期限の短い署名付き URL（presigned URL）を返し、ブラウザから直接ダウンロードさせる**のが定石です。

## フロントの実装パターン

ここまでで、フロントが扱うものは「操作 / ジョブを開始する」と「その状態を見る」の 2 つに絞られました。これを共通のフックにしておくと、画面ごとの実装がばらつきません。

### TanStack Query でジョブを監視する共通フック

TanStack Query（v5）なら、`refetchInterval` に関数を渡して「終わるまでポーリングし、終わったら止める」を書けます。

```typescript
import { useMutation, useQuery } from "@tanstack/react-query";

type JobStatus = "queued" | "running" | "succeeded" | "failed" | "compensating" | "compensated";
type Job = { jobId: string; status: JobStatus; progress?: number; result?: unknown; error?: unknown };

const TERMINAL: JobStatus[] = ["succeeded", "failed", "compensated"];

// 開始: 冪等キーはボタン押下（= 操作の意図）ごとに 1 回だけ作る
export function useStartJob<T>(path: string) {
  return useMutation({
    mutationFn: async ({ input, idempotencyKey }: { input: T; idempotencyKey: string }) => {
      const res = await fetch(path, {
        method: "POST",
        credentials: "include",
        headers: { "Content-Type": "application/json", "Idempotency-Key": idempotencyKey },
        body: JSON.stringify(input),
      });
      if (res.status !== 202) throw await res.json(); // problem+json
      return (await res.json()) as Job;
    },
  });
}

// 監視: 終わるまで間隔を広げながらポーリング
export function useJob(jobId: string | undefined) {
  return useQuery({
    queryKey: ["job", jobId],
    enabled: !!jobId,
    queryFn: async () => {
      const res = await fetch(`/api/jobs/${jobId}`, { credentials: "include" });
      return (await res.json()) as Job;
    },
    refetchInterval: (query) => {
      const job = query.state.data;
      if (job && TERMINAL.includes(job.status)) return false; // 終わったら止める
      // dataUpdateCount は取得に成功するたびに増える: 2s, 4s, 8s ... 最大 15s
      return Math.min(1000 * 2 ** query.state.dataUpdateCount, 15_000);
    },
  });
}
```

いくつかの注意点があります。

- **冪等キーは「ユーザーの 1 回の意図」につき 1 つ。** ボタンを押したときに生成し、ネットワークエラーで再送するときは同じキーを使う。再送のたびに新しいキーを作ると冪等にならない
- **ジョブ ID を URL かストレージに残す。** `?job=01J...` のように URL に載せておけば、リロードや別タブでも状態を追い直せる。ブラウザを閉じても処理はサーバーで続いているので、「戻ってきたら結果が見られる」ようにしておく
- **Saga の操作に楽観的更新（サーバーの応答を待たずに画面を先に更新すること）を使わない。** 一覧に「確定済み」と先に表示してから補償で取り消されると、ユーザーには「消えた」ように見える。状態が `succeeded` になるまでは「処理中」と表示する
- **ジョブ一覧の画面を用意する。** 帳票のように何度も実行するものは「自分が依頼したジョブの一覧」があると、待たずに他の作業へ移れる

### ポーリングから通知へ

ポーリングは単純で壊れにくいので、**まずはポーリングで始める**のがおすすめです。ジョブ数やユーザー数が増えてサーバー負荷やレスポンスの遅れが気になってきたら、サーバーからのプッシュに切り替えます。

| 方式 | 特徴 |
|---|---|
| ポーリング | 実装が最も簡単。状態リソースがあればすぐ使える |
| SSE（Server-Sent Events） | サーバー → ブラウザの一方向の通知。BFF が ECS 上で常駐していれば実装しやすい |
| WebSocket（API Gateway WebSocket API など） | 双方向。接続管理の仕組みが必要 |
| AWS AppSync Events | WebSocket ベースの pub/sub をマネージドで提供。チャネルを購読するだけで通知を受け取れる |

どの方式でも、**通知は「状態が変わった」というきっかけに留め、正しい状態は状態リソース（`GET /jobs/{id}`）から取り直す**ようにしておくと、通知の取りこぼしや順序の入れ替わりに強くなります。

## 方針 3: CORS をなくす — CloudFront による同一オリジン化と BFF

### CORS とプリフライトが辛い理由

SPA が複数の API オリジンを直接呼ぶ構成では、次のような手間が API の数だけ発生します。

- 各 API で CORS の設定（許可オリジン、ヘッダー、プリフライトのキャッシュ）を揃える必要がある
- 独自ヘッダー（`Authorization`、`Idempotency-Key` など）を付けると、本番のリクエストの前にブラウザが「送ってよいか」を確かめる `OPTIONS` リクエスト（プリフライト）が飛び、往復が増える
- 認証トークンをブラウザの JavaScript から読める場所に置くことになり、XSS で盗まれたときの被害が大きい
- API のホスト名がフロントのコードや設定に散らばり、構成変更のたびにフロントのリリースが要る

### CloudFront でパスごとに振り分ける

最も効果が大きいのは、**SPA と API を同じオリジンに見せる**ことです。CloudFront のビヘイビアで、`/` は S3 の静的ファイル、`/api/*` は BFF（ALB）へ振り分けます。ブラウザから見ればすべて同じオリジンなので、CORS の設定もプリフライトも不要になります。

業務 API ごとに `/api/orders/*` → 受注 API、`/api/stock/*` → 在庫 API のように直接振り分けることもできますが、その場合でも認証やエラー形式の統一のために、間に BFF か API Gateway を挟むことを検討してください。

### BFF でトークンをブラウザから隠す

BFF を置くと、認証を **Cookie セッション**で終端できます。ブラウザが持つのは `HttpOnly; Secure; SameSite=Lax`（または `Strict`）の Cookie だけです。アクセストークンは BFF がサーバー側で保持し、業務 API を呼ぶときに付け替えます。JavaScript からトークンが読めなくなるので、XSS でトークンを抜かれるリスクを下げられます。OAuth のブラウザアプリ向けのベストプラクティス（"OAuth 2.0 for Browser-Based Applications"、2026 年 8 月に RFC 10017 として発行）でも、この BFF パターンが選択肢として挙げられています。

Cookie 認証にすると CSRF 対策が必要になる点には注意してください。`SameSite` 属性に加えて、更新系リクエストでは独自ヘッダーの必須化や CSRF トークンの検証を組み合わせます。

BFF の責務は次の 3 つに絞り、**業務ロジックを持たせない**のがコツです。

1. **認証の終端**: Cookie セッション ↔ トークンの付け替え
2. **読み取りの集約**: 1 画面で必要な情報を複数 API から並列に取って 1 回で返す（API Composition と呼ばれるパターン）
3. **コマンドの受付**: 操作やジョブを開始し、`202` と ID を返す

BFF に業務ルールが入り始めると、BFF 自体が新しい「巨大な共通サーバー」になってしまいます。業務ルールは業務 API に、業務をまたぐ流れはオーケストレーターに置き、BFF は「フロントの都合」だけを吸収する層に留めます。

## 段階的な移行の進め方

すべてを一度に作り替える必要はありません。効果が大きく、既存の API に手を入れずに済むものから順に進めるのがおすすめです。

1. **同一オリジン化**: CloudFront のビヘイビアで `/api/*` を振り分ける。フロントの API ホスト名を相対パスに変えるだけで、CORS の問題が消える
2. **ジョブ API の形を決める**: `202 Accepted` + `Location` + 状態リソースの形と状態の語彙を決め、帳票作成を 1 つ SQS + ワーカーに移す。フロントは共通フックで受ける
3. **冪等キーとエラー形式を標準にする**: 更新系 API に `Idempotency-Key` と `application/problem+json` を順次入れる
4. **業務をまたぐ処理を 1 つ Saga にする**: 最も事故が多い（または最も業務的に重要な）フローを Step Functions に移し、フロントからの連続呼び出しをやめる
5. **BFF と Cookie セッション**: 認証を BFF で終端し、トークンをブラウザから取り除く
6. **通知への切り替え**: ポーリングの負荷が問題になってから、SSE や AppSync Events を検討する

## まとめ

- **ブラウザにトランザクションを持たせない。** 複数サービスの更新はサーバー側の「操作」として 1 回で受け付け、Saga（まずはオーケストレーション型）で順序・リトライ・補償を 1 か所に定義する
- **業務 API の標準を決める。** 冪等キー、補償 API、仮 → 確定の 2 段階、RFC 9457 のエラー形式、相関 ID の伝播
- **重い処理はジョブに統一する。** `202 Accepted` + 状態リソースの形に揃え、ECS タスクの直接起動は SQS + 常駐ワーカーに置き換える。結果は署名付き URL で渡す
- **フロントは「開始」と「状態の監視」だけ。** 共通フックでポーリングし、ジョブ ID を URL に残して、リロードしても追い直せるようにする
- **入口を 1 つにする。** CloudFront で同一オリジン化して CORS をなくし、BFF で認証を終端してトークンをブラウザから隠す

分散したサービスの前に立つ SPA の設計で大事なのは、「フロントで頑張る」ことではなく、**フロントが頑張らなくて済む形にサーバー側の約束事を揃える**ことです。約束事が揃えば、新しい業務の API を追加しても、フロントはいつもの共通フックで受けるだけで済むようになります。
