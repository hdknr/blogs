---
title: "NVIDIA Auto Ontology とは — オントロジー自動生成で AI エージェントの Text-to-SQL 精度を上げる"
date: 2026-11-15
lastmod: 2026-11-15
slug: "nvidia-auto-ontology"
draft: false
source_url: "https://github.com/hdknr/blogs/issues/694#issuecomment-6888081317"
categories: ["AI/LLM"]
tags: ["NVIDIA", "オントロジー", "Text-to-SQL", "mcp", "AIエージェント"]
---

AI エージェントにデータベースを問い合わせさせると、SQL 自体はそれらしく書けます。しかし「売上」をどの列で数えるか、どのテーブルをどう結合するかを取り違え、もっともらしい誤った数字を返すことがあります。速く答えても、数字が間違っていれば価値はありません。

[NVIDIA/auto-ontology](https://github.com/NVIDIA/auto-ontology) は、この Text-to-SQL（自然文の質問から SQL を生成すること）の問題に、「オントロジー（業務上の意味の層）」で取り組むオープンソースのライブラリです。企業のデータベースのメタデータからオントロジーを自動生成し、人が検証・認定したうえで、MCP（AI エージェントに外部ツールをつなぐ標準プロトコル）・CLI・REST API 経由で任意のエージェントに提供します。ライセンスは Apache-2.0 です。

この記事では、まず「オントロジーとは何か」「Text-to-SQL にどう効くのか」を押さえたうえで、README をもとに Auto Ontology の考え方・仕組み・使い方を整理します。

## そもそもオントロジーとは

オントロジー（ontology）は、もともと哲学で「存在論」を指す言葉です。情報科学では、**ある分野にどんな概念があり、それぞれが何を意味し、互いにどう関係するかを定義したもの**を指します。ポイントは、それを人だけでなく**機械が読める形**で書く点です。「用語辞典」と「概念どうしの関係図」を合わせたもの、と考えるとわかりやすいでしょう。

たとえば販売業務なら、次のような知識がオントロジーになります（データ分析の文脈では、最後の「計算の決まり」のような指標のルールまで含めて扱うことが多くあります）。

- **概念**：「顧客」「注文」「請求明細」「商品」「州」がある
- **意味と同義語**：「売上」は revenue・売上高とも呼ばれる
- **関係**：顧客は注文を出す。請求明細は商品を指す。顧客は配送先の都市に属し、都市は州に属する
- **計算の決まり**：「売上」は請求明細の金額を合計して求める

ここで大事なのは、**データベースのスキーマとオントロジーは別物**だという点です。スキーマが表すのは「データがどう保存されているか」（テーブル・列・型・制約）です。一方、オントロジーが表すのは「そのデータが業務上なにを意味するか」です。`sales.invoicelines.extendedprice` という列名を見ても、それが「売上として数えるべき金額」なのかはわかりません。その対応付けを担うのがオントロジーです。

スキーマにも外部キーという形で「テーブルの関係」は書かれています。ただし外部キーが示すのは「つなげられる」ことまでで、「この質問ならどの経路でつなぐべきか」までは示しません。

## Text-to-SQL にオントロジーを使うと何が良くなるか

Text-to-SQL では、LLM が自然文の質問をスキーマと照らし合わせて SQL を書きます。実際の誤りを見ると、SQL の文法ミスよりも意味の取り違えが目立ちます。間違いが起きやすいのは、**スキーマに書かれていない「意味」を推測で補う部分**です。典型的なのは次の 4 つです。

| LLM がつまずく点 | 具体例 | オントロジーが持つ情報 |
|---|---|---|
| 言葉と列の対応 | 「売上」「顧客」が社内用語で、列名は英語の略語。似た名前の列が複数ある | 用語と同義語、その用語を保持する列 |
| 指標の計算式 | 売上は単価×数量か、明細の金額か。返品を差し引くか。システムごとに定義が違う | レビューされた計算式（Auto Ontology では SQL 属性） |
| 結合の経路 | 顧客から州へたどる経路が複数ある（配送先の住所か、郵送先の住所か） | 使うべき結合キー（データで裏付けたもの） |
| 答えられない質問 | データにない「広告費」を、似た列で無理に計算する | 何が定義されているか（定義されていないものは何か） |

特にやっかいなのが、計算式と結合経路の取り違えです。どちらも **SQL はエラーにならず、それらしい数字が返ってくる**ため、誤りに気付けません。

![Text-to-SQL でオントロジーがない場合とある場合を比べた図。オントロジーがない場合、LLM はテーブル名と列名だけを見て SQL を書くため、売上をどの列で計算するか、州をどの住所経由でたどるかを推測することになり、SQL は動いても数字が正しいかわからない。オントロジーがある場合は、質問の用語を、人がレビュー・修正できる定義（売上の計算式、顧客から配送先の都市を経て州に至る経路、同義語）に解決してから LLM が SQL を組み立てるので、毎回同じ式と経路で答え、使った定義を添えて検証できる。定義が見つからない概念は「このデータでは答えられない」と返す。](/blogs/images/nvidia-auto-ontology-before-after.png)

オントロジーを使った Text-to-SQL の要点は、**LLM に任せる範囲を狭めること**です。LLM は質問の言葉を理解し、SQL を書くことに専念します。「売上とは何か」「どの経路で結合するか」といった意味の判断は、あらかじめ定義しておき、人がレビューできる知識から引きます。これにより、次の利益が得られます。

- **正確さ**：意味の推測による「動くけれど間違った SQL」が減る
- **一貫性**：同じ質問なら、誰が聞いても同じ式・同じ経路で計算される
- **説明可能性**：どの定義を使ったかを回答に添えられるので、人が検証できる
- **誠実さ**：定義がない概念を聞かれたら、無理に計算せず「答えられない」と返せる
- **統制**：定義は人がレビューして修正できる。たとえば売上の計算式を 1 か所直せば、以後その指標を使う回答すべてに反映される

ただし、オントロジーには「作るのが大変」という弱点があります。数百のテーブルについて、用語・計算式・結合経路を人が一から書き起こすのは現実的ではありません。Auto Ontology は、この**作る手間を自動化する**ことを狙ったツールです。

## Auto Ontology の全体像：5 つの機能

README の冒頭では、エージェントに必要な「コンテキスト層」を次のように説明しています。

- データがどこにあるか
- それが何を意味するか
- 使うべきかどうか、どう使うか
- どこから来たか（来歴：どのテーブルや処理から作られたか）
- 似たものは何か

オントロジーは、このうち主に「何を意味するか」「どう使うか」を担います。Auto Ontology はこの層を企業のメタデータから構築し、システムごとに食い違う定義（前述の「指標の計算式」の問題）を突き合わせます。機能は次の 5 つにまとめられています。

| 機能 | 内容 |
|---|---|
| Discover | メタデータからオントロジーを生成し、既存のオントロジーやセマンティックモデルとつなぐ |
| Ground | 指標・エンティティ・関係について、信頼できる業務上の意味をエージェントに与える |
| Validate | 生成されたクエリを認定済みの定義や来歴と照合し、回答に出典を付ける |
| Expose | MCP・CLI・API でエージェントに提供する |
| Learn | 認定された修正や利用状況をオントロジーに還元する |

既存のセマンティックモデル（BI ツールなどで指標やディメンションを定義する層）を置き換えるのではなく、「補完する」位置づけである点も明記されています。

## オントロジーの中身：用語・SQL 属性・関係

Auto Ontology のオントロジーは、3 種類の定義で構成されます。

- **用語（Terms）**：*Customer* や *Invoice Line* のような業務概念。説明と同義語を持ち、それを保持する列に対応付けられます。
- **SQL 属性（SQL attributes）**：用語の下に置く、レビュー済みの SQL 式（利益率や移動合計など）。エージェントがこれを再利用するので、同じ指標は毎回同じ方法で計算されます。
- **関係（Relationships）**：テーブルどうしの結合方法。中間テーブル（bridge table）も含み、キーとデータの両方から推定されます。

冒頭の販売業務の例でいえば、「顧客」「売上」とその同義語が用語に、「売上は請求明細の金額の合計」が SQL 属性に、「顧客 → 都市 → 州」が関係に当たります。前述の「LLM がつまずく点」でいえば、用語が「言葉と列の対応」に、SQL 属性が「指標の計算式」に、関係が「結合の経路」に対応します。

なお、一般的なオントロジーでいう「関係」（顧客は注文を出す、など）を、Auto Ontology では「どのテーブルをどのキーで結合するか」という具体的な形で持ちます。人による認定の対象は用語・説明・SQL 属性で、結合にどのキーを使うかはコンパイルのたびに選び直されます。

## 仕組み：生成と回答の 2 段階

Auto Ontology は、オントロジーを**生成**して人が認定する段階と、それを使って質問に**回答**する段階の 2 つで動きます。

![NVIDIA Auto Ontology の処理の流れを示す図。上段の生成段階では、ソース DB からカタログを取り込み、テーブルごとの分析とテーブル横断の分析を経て、用語・SQL 属性・関係からなるオントロジーを Postgres と pgvector に保存し、人が検証して認定する。下段の回答段階では、質問を分類し、埋め込み検索で候補を絞り、オントロジーを参照して経路の探索に LLM を使わずに結合経路を決め、推論モデルで SQL を生成し、静的チェックと LLM ジャッジで検査・修復したうえで、SQL と手順を添えて回答する。](/blogs/images/nvidia-auto-ontology-pipeline.png)

### 生成（セマンティックコンパイル）

Web UI の **Settings → Semantic Compilation** を有効にすると、取り込みサービスがソース DB から最初の草案を作ります。

1. **カタログ取り込み**：テーブル・列・キー・ビュー・クエリ履歴を読み込み、テーブルと列を pgvector に埋め込みます。PII 検出を有効にすれば個人情報のタグ付けも行います。
2. **テーブルごとの処理**：SQL で値をプロファイリングし、モデルが外部キー候補や中間テーブルを見つけ、列の説明を書き、用語に名前を付けます。
3. **テーブル横断の処理**：同じスキーマのコピーを「用語ファミリー」にまとめ、外部キーを参照先の用語に結び付けます。推定した結合は、**データで裏付けが取れたものだけを残します**。クエリ履歴や中間テーブルから SQL 属性の候補も提案します。
4. **出力**：オントロジーは Postgres に、埋め込みは pgvector に保存されます。Ossie YAML 形式でのインポート・エクスポートにも対応しています。
5. **認定（Certify）**：Chat や MCP の `check_answerable`・`ask_question` で実際の質問を試しながら、用語・説明・SQL 属性を UI や API で修正し、正しくなったものを認定します。修正内容は次回のコンパイルでも保持されます。ただし、各結合にどのセマンティック外部キー（DB に定義された制約ではなく、オントロジー側で推定・検証した結合キー）を使うかは、コンパイルのたびに選び直されます。

### 回答

質問が来るたびに、エージェントは同じ手順を踏みます。

1. **分類**：LLM が質問の意図をラベル付けし、質問に含まれる条件などを切り分けます。
2. **検索**：埋め込み検索で候補の用語・列・SQL 属性を探し、LLM が関連するものを残します。
3. **結合**：結合経路はオントロジーのセマンティック外部キーから決まり、**経路の探索に LLM は関与しません**（README の説明による。詳細設計ドキュメントでは、起点となる列やテーブルの選択には LLM を使うとされています）。
4. **SQL 生成**：推論モデルが SQL と平易な説明文を書きます。
5. **検査と修復**：静的チェックと LLM による判定で SQL をレビューし、却下・失敗したクエリは修復します。結果が空なら、フィルタ値が実在するかを確かめに行きます。
6. **回答**：SQL と実行した手順を添えて答えを返します（Chat ではグラフも表示されます）。

有効なクエリが作れなければ、「このデータからは答えられない」と報告します。LLM が誤りやすい結合経路の選択を決定的な処理に切り出し、残りの LLM 工程も検査で挟む構成になっているのがわかります。

## 回答の例：答えと根拠をセットで返す

README のクイックスタートでは、Microsoft のサンプル販売データベース Wide World Importers を使い、次のような質問をしています。

> What was revenue for the USB food flash drive - sushi roll in Pennsylvania in June 2015?

エージェントは *revenue*・*product*・*state* をオントロジーの用語に解決し、その関係をたどって必要な結合を組み立てます。返ってくるのは答えだけではありません。

```text
Answer:  Revenue for USB food flash drive - sushi roll in Pennsylvania in
         June 2015 was $588.80, from 3 invoice lines.

SQL:     SELECT SUM(il.extendedprice) AS revenue, COUNT(*) AS invoice_lines
         FROM sales.invoicelines il
         JOIN sales.invoices i             ON il.invoiceid = i.invoiceid
         -- （中略：customers・cities などの結合）
         JOIN application.stateprovinces sp ON ct.stateprovinceid = sp.stateprovinceid
         WHERE si.stockitemname = 'USB food flash drive - sushi roll'
           AND sp.stateprovincename = 'Pennsylvania'
           AND i.invoicedate >= '2015-06-01' AND i.invoicedate < '2015-07-01'

Steps:   Resolved terms: Invoice Line (revenue), Stock Item, State Province, Invoice
         Joined: invoice line -> invoice -> customer -> city -> state province
         Validated the filter values against the data, then executed
```

SQL と「どの用語に解決し、どう結合したか」が一緒に返るので、人がソースと突き合わせて検証できます。

データにない概念を聞かれた場合の振る舞いも示されています。Wide World Importers には広告データがありません。そこで「広告費用対効果（ROAS）」を聞くと、MCP 経由のエージェントはまず `check_answerable` で回答できるかを確かめます。そのうえで「売上なら出せるが、広告費のデータがないので ROAS は計算できない」と聞き返します。もっともらしい数字をでっち上げずに止まれる点は、業務利用では大きな違いです。

## 構成要素

Auto Ontology は複数のサービスで構成されます。

| コンポーネント | 技術 | 役割 | ポート |
|---|---|---|---|
| Frontend | Next.js、Better Auth、Prisma | Web UI、認証、公開 API ゲートウェイ | 3000 |
| Backend | FastAPI（Python 3.12+）、LangChain | Text-to-SQL エージェント、カタログ・オントロジー API | 3001 |
| Ingestion service | FastAPI（Python 3.12+） | 取り込みとセマンティックコンパイル | 3002 |
| MCP server | FastMCP | 公開 API 上の読み取り専用エージェントツール | 3003 |
| Postgres + pgvector | PostgreSQL 17 | カタログ、オントロジー、アプリデータ、ベクトルストア | 5432 |
| HashiCorp Vault | 任意 | 接続情報の保管 | — |

なお、MCP サーバーは Docker Compose や Helm チャートには含まれず、デプロイの横で別途起動します（後述）。

推論には NVIDIA NIM のエンドポイント（ホスト版の NVIDIA API カタログまたはセルフホスト）を使い、既定では Nemotron 系のモデルが設定されています。モデルは推論用（`REASONING`）・軽量処理用（`NON_REASONING`）・埋め込み（`EMBED`）・リランク（`RERANK`）の 4 役割に分かれ、それぞれ `<ROLE>_ENDPOINT` / `<ROLE>_API_KEY` / `<ROLE>_MODEL` の 3 変数で設定します。未設定の項目は `DEFAULT_MODELS_*` にフォールバックするので、OpenAI 互換のエンドポイントに差し替えることもできます。埋め込みモデルは取り込み時と問い合わせ時で同じものを使う必要があります。

接続できるデータソースは、PostgreSQL・MySQL・Databricks・Snowflake・ClickHouse・Trino・Apache Kyuubi・HeavyDB・DuckDB・SQLite の 10 種類です。

## 試してみる：Docker Compose でのクイックスタート

必要なものは、Docker（Compose v2）、[uv](https://docs.astral.sh/uv/)、[build.nvidia.com](https://build.nvidia.com) で取得する NVIDIA API キー（`nvapi-...`）です。

```bash
git clone https://github.com/NVIDIA/auto-ontology.git
cd auto-ontology
cp .env.example .env
```

`.env` に最低限次の値を設定します。

```dotenv
DEFAULT_MODELS_API_KEY=nvapi-...
AUTH_SECRET=<openssl rand -base64 32 などで作った長いランダム文字列>
APP_URL=http://localhost:3000
POSTGRES_PASSWORD=<新しいパスワード>
CONNECTION_STRINGS=postgresql://postgres:<同じパスワード>@postgres:5432/wideworldimporters
AUTO_ONTOLOGY_ADMIN_PASSWORD=<新しいパスワード>
PGADMIN_PASSWORD=<新しいパスワード>
```

管理者のメールアドレス（`AUTO_ONTOLOGY_ADMIN_EMAIL`）は `.env.example` に既定値が入っているので、必要に応じて変更します。Compose は Postgres・pgAdmin・Web アプリをホストに公開するので、既定のパスワードは必ず置き換えます。また `.env.example` にはモデルの役割ごとに `nvapi-your-api-key-here` が書かれているので、自分のキーに置き換えるか、行ごと削除して `DEFAULT_MODELS_API_KEY` にフォールバックさせます。

続いて Postgres を起動し、別リポジトリ [auto-ontology-eval](https://github.com/NVIDIA/auto-ontology-eval) のスクリプトでサンプル DB を投入します。

```bash
docker compose up -d --wait postgres
git clone https://github.com/NVIDIA/auto-ontology-eval.git ../auto-ontology-eval
cd ../auto-ontology-eval
uv sync
cp .env.example .env
POSTGRES_PASSWORD='<同じパスワード>' uv run python scripts/seed/seed_wwi.py --database-name wideworldimporters --drop
```

auto-ontology のディレクトリに戻り、残りのスタックを起動します。

```bash
cd ../auto-ontology
docker compose up -d --build
```

`http://localhost:3000` を開き、`.env` の `AUTO_ONTOLOGY_ADMIN_EMAIL` と `AUTO_ONTOLOGY_ADMIN_PASSWORD` でサインインします。**Settings → Semantic Compilation** を有効にし、「Semantic compilation is ready」と表示されたら Chat で質問できます。

## エージェントから使う

### MCP サーバー

MCP サーバーは、オントロジーに対する**読み取り専用**のツールを MCP クライアントに提供します。各ユーザーは Auto Ontology にサインインし、すべての呼び出しはそのユーザーの権限で実行されます。

| 用途 | ツール |
|---|---|
| 準備状態 | `check_readiness` |
| 用語 | `search_terms`、`get_term`、`get_term_columns`、`get_term_sql_attributes`、`get_sql_attribute`、`describe_table` |
| 回答可能性 | `check_answerable` |
| 質問 | `ask_question`（答え・SQL・行を返す） |

MCP サーバーはクイックスタートの Compose では起動しないので、デプロイ先の URL を指定して別途起動します（既定ポートは 3003）。

```bash
AUTO_ONTOLOGY_API_URL=http://localhost:3000 \
  uvx --from "git+https://github.com/NVIDIA/auto-ontology.git#subdirectory=mcp" auto-ontology-mcp
```

Claude Desktop からは [`mcp-remote`](https://www.npmjs.com/package/mcp-remote) で中継して接続します（`claude_desktop_config.json`）。

```json
{
  "mcpServers": {
    "auto-ontology": {
      "command": "npx",
      "args": ["mcp-remote", "http://localhost:3003/mcp"]
    }
  }
}
```

### エージェントスキルと REST API

コーディングエージェント向けに、セットアップ（`nvidia-ontology-setup`）・管理（`nvidia-ontology-management`）・問い合わせ（`nvidia-ontology-query`）の 3 つのスキルも同梱されています。入口は `AGENTS.md` です。

REST API では、Web UI のユーザーメニューで API トークンを発行し、`POST /api/chat/completions` に質問を送ります。応答は Server-Sent Events のストリームで、`result` イベントに答えが入り、`data: [DONE]` で終わります。

```bash
export AUTO_ONTOLOGY_API_TOKEN=<発行したトークン>
curl -N http://localhost:3000/api/chat/completions \
  -H "x-api-key: $AUTO_ONTOLOGY_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"question": "How many orders shipped last week?"}'
```

## 運用上の注意点

README には、導入前に押さえておきたい注意点がいくつか書かれています。

- **ポート 3001・3002 はプライベートネットワークに閉じる**：Backend は Frontend が転送する `x-auto-ontology-user-id` ヘッダーのユーザー ID をそのまま信頼します。また、取り込みサービスの ingest・delete・reset・compile エンドポイントには独自の認証がありません。外部からは 3000（Web）と 3003（MCP）だけを通す前提です。
- **データの外部送信**：既定ではモデル推論に NVIDIA API カタログ（`integrate.api.nvidia.com` など）を使います。また予測機能の KumoRFM を有効にすると、接続したテーブル（既定で最大 20 テーブル、行数は無制限）がホスト型サービスにアップロードされます。組織のデータレビューを済ませてから有効にするよう明記されています。
- **ウェアハウスへのクエリコスト**：セマンティックコンパイルは、推定した外部キーを確かめるためにウェアハウスへクエリを発行します。コストが高い環境では `PREVENT_SEMANTIC_FK_DB_QUERIES=true` で止められますが、その場合は名前と説明だけで外部キーを受け入れることになります。
- **外部コントリビューションは受け付けていない**：Issue（バグ報告・統合リクエスト）は歓迎されていますが、プルリクエストは受け付けていません。

## まとめ

Auto Ontology は、Text-to-SQL の精度をプロンプトやモデルの賢さだけに頼らず、「業務上の意味」と「結合の仕方」をオントロジーとしてデータ化し、人が認定したものをエージェントに使わせるアプローチです。

- 用語・SQL 属性・関係の 3 種類で業務の意味を表す
- 草案は DB のメタデータとクエリ履歴から自動生成し、推定した結合はデータで裏付ける
- 回答時の結合経路は LLM を使わずオントロジーから決め、SQL と手順を添えて返す
- データで答えられない質問は、答えられないと言える
- MCP・REST API・エージェントスキルで、既存のエージェント基盤から使える

クイックスタートでサンプル DB の投入に使った [auto-ontology-eval](https://github.com/NVIDIA/auto-ontology-eval) は、本来は BIRD などの Text-to-SQL ベンチマークで、オントロジーの有無による差を測る評価環境です。社内データに AI エージェントで問い合わせたいが、数字の正しさが不安でためらっている場合に、検討する価値のあるツールです。
