---
title: "OpenWiki を GitHub Actions で定期実行する — 設定と API キーをどこに置くか"
description: "LangChain の OpenWiki を GitHub Actions で定期実行する構成。エージェント本体は CLI に同梱され、自分で置くのは推論プロバイダと認証情報だけ。設定の 3 層、OIDC キーレス認証、fetch-depth: 0 の落とし穴まで。"
date: 2026-08-16
lastmod: 2026-08-16
slug: "openwiki-github-actions-ci"
draft: false
categories: ["AI/LLM"]
tags: ["OpenWiki", "LangChain", "GitHub Actions", "OIDC", "ドキュメント自動生成"]
---

コードベースのドキュメントを AI に書かせて維持させるツールには、大きく 2 つの形態がある。Google の Code Wiki や Cognition の DeepWiki のように、リポジトリを渡して向こうのサイトで読む**ホスト型サービス**。もう一つは、mkdocs のように自分の CI で回す**セルフホスト型 CLI** だ。

後者の代表が LangChain の [OpenWiki](https://github.com/langchain-ai/openwiki)（MIT、npm 配布）で、GitHub Actions・GitLab CI・Bitbucket Pipelines 向けのワークフロー例が同梱されている。自社のプライベートリポジトリを対象にできるのはこちらだけなので、実務ではこの型を選ぶ場面が多い。

この記事では、OpenWiki を GitHub Actions で定期実行する際に **LLM とエージェントをどう設定・配置するか**を整理する。結論から言うと、**エージェント本体を自分で用意する必要はない**。ドキュメント生成エージェントは [Deep Agents](https://github.com/langchain-ai/deepagentsjs) ベースで CLI に同梱されており、外から差し込むのは推論プロバイダの選択と認証情報だけだ。設計上の判断が要るのは、それらを**どの層に置くか**に集約される。

![OpenWiki を GitHub Actions で回す構成図。左に設定の 3 層（リポジトリにコミットする workflow・INSTRUCTIONS.md・.openwikiignore、GitHub Secrets、CI では読まれないローカルの ~/.openwiki/.env）、中央に cron から checkout・インストール・openwiki code --update・PR 作成へ続くジョブの流れ、右に API キー方式とキーレス方式に分かれた外部の推論プロバイダを示している](/blogs/images/openwiki-github-actions-pipeline.png)

先に要点だけ挙げておく。

- 置くのは**プロバイダの選択と認証情報**だけ。エージェント本体は CLI に同梱されている
- 振る舞いを決めるのは `openwiki/INSTRUCTIONS.md` と `.openwikiignore` の 2 ファイル
- CI の認証は **OIDC でキーレス**にできる Bedrock / Gemini Enterprise が有利
- `fetch-depth: 0` と `--print` を外すと、分かりにくい壊れ方をする

## OpenWiki の設定を置く 3 つの層 — リポジトリ / GitHub Secrets / ローカル

| 層 | 置くもの | 共有範囲 |
|---|---|---|
| ① リポジトリにコミット | `.github/workflows/openwiki-update.yml`（プロバイダ名・モデル ID）、`openwiki/INSTRUCTIONS.md`（生成方針）、`.openwikiignore`（読み取り境界） | チーム全員・CI で同一 |
| ② GitHub Secrets | プロバイダの API キー | CI のみ |
| ③ `~/.openwiki/.env` | 手元の provider 設定・キー | ローカルのみ。**CI では読まれない** |

つまずきやすいのは ③ で、ローカルで `openwiki code --init` を通したあと、その設定が CI にも効くと思い込むケースだ。`~/.openwiki/.env` はあくまで手元の認証情報ストアであり、CI では改めて env として与える必要がある。

なおコマンドは `code` を省いた `openwiki --init` / `--update` でも同じで、既定が `code` モードだからだ（個人ナレッジ側を回すときだけ `personal` を付ける）。この記事では公式ワークフローに合わせて明示形の `openwiki code --update` で統一する。

そして「エージェントの設定」に相当するのは、① に置く `openwiki/INSTRUCTIONS.md` と `.openwikiignore` の 2 ファイルである（詳細は後述）。モデルの選択がエージェントの**能力**を決めるのに対して、この 2 つが**振る舞い**を決める。

## 公式ワークフロー例 openwiki-update.yml を読む

同梱の `examples/openwiki-update.yml` はそのまま `.github/workflows/` に置いて使える。要点だけ抜き出すと次のようになる。

```yaml
name: OpenWiki Update

on:
  workflow_dispatch:
  schedule:
    - cron: "0 8 * * *"

permissions:
  contents: write
  pull-requests: write

jobs:
  update:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          persist-credentials: true
          fetch-depth: 0

      - uses: actions/setup-node@v4
        with:
          node-version: "22"

      - run: npm install --global openwiki mermaid@11.16.0 jsdom@29.1.1

      - run: openwiki code --update --print
        env:
          OPENWIKI_PROVIDER: openrouter
          OPENROUTER_API_KEY: ${{ secrets.OPENROUTER_API_KEY }}
          OPENWIKI_MODEL_ID: z-ai/glm-5.2

      - uses: peter-evans/create-pull-request@v7
        with:
          add-paths: |
            openwiki
            AGENTS.md
            CLAUDE.md
          branch: openwiki/update
          commit-message: "docs: update OpenWiki"
```

押さえるべき点が 4 つある。

### 毎日動いているのに更新されない — `fetch-depth: 0` は必須

`openwiki code --update` は「最後にドキュメント化したコミット」と HEAD を比較して差分を得る。浅いクローンではその基準コミットが履歴に無いため、変更サマリが空のまま更新が走る。公式ワークフローにもこの理由がコメントで明記されている。地味だが、これを外すと「毎日動いているのに内容が更新されない」という分かりにくい壊れ方をする。

### ジョブがタイムアウトする — `--print` が無いと対話モードで待機する

OpenWiki の CLI は既定で実行後もチャットを開いたまま待機する。`-p` / `--print` がワンショット実行の指定で、これが無いとジョブはタイムアウトまで待つことになる。なお `--update` は初回実行も兼ねるので、`--init` を別に呼ぶ必要はない。

### `mermaid` と `jsdom` を入れる理由

無くても動くが、その場合の図の検証は簡易チェックに留まる。OpenWiki は実行後に全ての `mermaid` フェンスを検証する。失敗した図は、壊れたブロックをそのまま出すのではなく、理由コメント付きの `text` フェンスに落とす。次の `--update` はそのコメントを見つけて図を修復するため、品質は回を重ねて回復する。GitHub と同じレンダリングで検証したいなら、この 2 つをワークフロー側にも入れる。

### 成果物は push ではなく PR で出る

`peter-evans/create-pull-request` で `openwiki/update` ブランチに PR が立つので、エージェントの誤記をマージ前に止められる。`permissions` に `pull-requests: write` が要るのはこのためだ。また変更が無い実行はスナップショット比較で no-op（差分なしで何も出力しない実行）になり、PR は出ない。毎日回しても無駄な差分で溢れることはない。

## プロバイダ別の認証情報の置き方 — Bedrock と Gemini Enterprise は OIDC でキーレス

OpenWiki は 12 のプロバイダに対応していて、CI での認証の置き方はそれぞれ異なる。

| プロバイダ | CI での配置 |
|---|---|
| OpenRouter / OpenAI / Anthropic / Gemini (AI Studio) | 各 API キーを Secrets に置き、env で渡す |
| **AWS Bedrock** | **キーレス可**。明示キーが無ければ AWS SDK の既定の認証情報チェーン（OIDC / web identity ロール）が使われる |
| **Gemini Enterprise (Vertex AI)** | **キーレス**。`google-github-actions/auth` で認証し、`OPENWIKI_PROVIDER=gemini-enterprise` と `GOOGLE_CLOUD_PROJECT` を渡す |
| GitHub Copilot | `COPILOT_API_KEY` には **OAuth トークン**が必要。Personal Access Token は Copilot API 側でサードパーティ統合として拒否される |
| OpenAI 互換（Ollama / LM Studio） | GitHub ホストランナーからローカルサーバには到達できないため、実質セルフホストランナー前提 |

CI に置くなら **Bedrock か Gemini Enterprise を勧めたい**。どちらも OIDC（実行のたびに短命トークンを発行して認証する仕組み）でキーレスにでき、長期の API キーを Secrets に寝かせずに済む。ドキュメント生成のためだけに有効期限のないキーをリポジトリに紐付けるのは、得られる利便性に対して割に合わない。

### `ValidationException: on-demand throughput isn't supported` が出たら

Bedrock を使う場合、新しめのモデルはクロスリージョン推論プロファイル経由でないとオンデマンド呼び出しを受け付けないことがある。`ValidationException: Invocation of model ID ... with on-demand throughput isn't supported` が出たら、モデル ID にリージョンコードを前置する（例: `us.anthropic.claude-sonnet-5`）。IAM 側も `foundation-model` と `inference-profile` の両方のリソースタイプに対して `bedrock:InvokeModel` が必要になる。

### コードの送信先を決めるのは統制の話

コードは選んだプロバイダに送信される。**送信先の選択がそのまま統制ポイント**になるので、ここは組織のポリシーに合わせて決めるべきところだ。外に出したくないなら、セルフホストランナー + Ollama という構成が唯一ローカル完結する選択肢になる。

## エージェントの振る舞いを決める 2 ファイル（INSTRUCTIONS.md と .openwikiignore）

モデルを選んだあと、生成物の質を左右するのは次の 2 ファイルだ。どちらもリポジトリにコミットするので、チーム全員と CI で同じ設定が効く。

### `openwiki/INSTRUCTIONS.md`

何を重点的に書かせるかの指示書で、ユーザーが書き、OpenWiki は通常の実行で**書き換えない**。OpenWiki 自身のリポジトリに置かれている実物が参考になる。

```markdown
---
type: Repository guide
title: Repository Wiki Instructions
description: Guidance for creating and maintaining a practical code wiki for the local repository.
tags: [documentation, repository, code-wiki]
---

A code wiki for this local repository. Prioritize a concise quickstart, architecture
overview, source map, key workflows, domain concepts, operations/runbook notes, testing
guidance, and integration points. Inspect git history to understand reasoning behind code
changes and the progression of the repository. Keep pages grounded in the repository
structure and recent code changes. Prefer practical navigation for engineers over generic
summaries.
```

「git 履歴を見て変更の理由を理解せよ」「汎用的な要約より実務的なナビゲーションを優先せよ」といった、出力の性格を決める指示が並んでいる。ここを書かないと汎用的なコード要約が出てくるので、**実質的にはこのファイルが記事の編集方針**になる。

### `.openwikiignore`

読み取り境界の定義で、`.gitignore` と同じ記法（コメント、`*` と `**` のグロブ、ディレクトリ指定、`!` の否定）が使える。

```gitignore
secrets/
*.log
!logs/keep.log
```

有効なルールがあると、ファイル探索とシェル実行の両方が制限され、対象パスは読まれも走査もされない。ただし公式ドキュメントは注意書きを添えている。これは**読み取りの境界であって、話題の禁止ではない**。テストや README、コミットメッセージなど許可された証拠から、除外した領域の存在をエージェントが推測して言及する可能性は残る。機密の実体が漏れないことは保証されるが、「その機能について一切触れさせない」ことは保証されない。

## 生成物の形 — OKF v0.1 準拠の Markdown と AGENTS.md / CLAUDE.md

`openwiki code --update` が書くのは、利用者側の手元に残る Markdown だ。OpenWiki 自身のリポジトリでは次のような構成になっている。

```text
openwiki/
├── index.md          # ルート索引（okf_version: "0.1" を宣言）
├── quickstart.md
├── INSTRUCTIONS.md   # 人間が書く。OpenWiki は触らない
├── .last-update.json # 最後にドキュメント化した地点の記録
├── agent/
├── architecture/
├── cli/
├── integrations/
└── operations/
```

出力は Google の [Open Knowledge Format (OKF) v0.1](https://github.com/GoogleCloudPlatform/knowledge-catalog/blob/main/okf/SPEC.md) 準拠で、各ページは `type` を持つ YAML フロントマターと、ページ間の標準的な Markdown リンクで関係を表現する。ホスト型サービスと違い、成果物がリポジトリの中にあってレビューでき、他の OKF 対応ツールに持ち出せる。

もう一つ特徴的なのは、`code` モードの実行ごとにリポジトリ直下の `AGENTS.md` と `CLAUDE.md` を維持し、コーディングエージェントを Wiki へ誘導する点だ。書き換えるのは自分の `<!-- OPENWIKI:START -->` 〜 `<!-- OPENWIKI:END -->` ブロックだけで、それ以外の記述には手を触れない。つまり**人間の読み物であると同時に、エージェントのメモリとして設計されている**。ワークフロー例の `add-paths` にこの 2 ファイルが入っているのはそのためだ。

## LangSmith の使い道は 2 つある

OpenWiki には LangSmith が 2 か所で登場する。環境変数名が似ていて紛らわしいので、分けて整理する。

### 生成エージェント自身のトレース

公式ワークフローの env には、プロバイダ設定に加えてトレース設定が入っている。

```yaml
# openwiki code --update ステップの env: に追加する
env:
  LANGSMITH_API_KEY: ${{ secrets.LANGSMITH_API_KEY }}
  LANGCHAIN_PROJECT: openwiki
  LANGCHAIN_TRACING_V2: "true"
```

これは**ドキュメント生成エージェント自身の実行**をトレースするための設定で、任意である。CI でエージェントを回すと「なぜこの記述になったのか」が後から追いにくくなるため、生成物が期待とずれる時の調査手段として効く。

### LangSmith コネクタ

`code` モードには **LangSmith コネクタ**がある。指定したプロジェクトの実行トレース（ツール呼び出し・結果・レイテンシ）を取り込み、「コードが実際にどう動いているか」をドキュメントに反映させる機能だ。こちらは `openwiki/.langsmith.json`（キーは含まない）をコミットし、キーは `OPENWIKI_LANGSMITH_API_KEY` として渡す。前節の `LANGSMITH_API_KEY` とは別の環境変数なので、混同しないようにしたい。

## テレメトリを無効化する（OPENWIKI_TELEMETRY_DISABLED / DO_NOT_TRACK）

OpenWiki は既定で匿名の集計テレメトリを送信する。収集されるのはコマンド種別（init / update）と結果（成功 / 失敗 / no-op）程度だ。ファイル内容・リポジトリ名・認証情報・プロンプト・モデル出力・ファイルパス・エラーメッセージは収集対象外と明記されている。CI 実行は共有 CI 識別子の下で匿名の信頼性データとして扱われる。

それでも組織のポリシー上オフにしたい場合は、env に次のどちらかを足す（両方書く必要はない）。

```yaml
# openwiki code --update ステップの env: に追加する
env:
  OPENWIKI_TELEMETRY_DISABLED: "1"
  # DO_NOT_TRACK: "1"   # 業界横断の標準。こちらでも同じ効果
```

## まとめ

- OpenWiki の CI 実行で自分が配置するのは、**エージェント本体ではなく推論プロバイダの選択と認証情報**。エージェントは CLI に同梱されている
- 設定は 3 層に分かれる。ローカルの `~/.openwiki/.env` は **CI では読まれない**
- エージェントの振る舞いを決めるのは `openwiki/INSTRUCTIONS.md`（何を書かせるか）と `.openwikiignore`（何を読ませないか）。どちらもリポジトリにコミットする
- 落とし穴は 2 つ。`fetch-depth: 0` を外すと差分が空のまま走り「動いているのに更新されない」壊れ方をし、`--print` が無いと対話モードのまま止まる
- CI の認証は OIDC でキーレスにできる **Bedrock / Gemini Enterprise** が有利。長期キーを Secrets に置かずに済む
- `.openwikiignore` は読み取り境界であって、話題の禁止ではない
- 成果物は自分のリポジトリの Markdown（OKF v0.1 準拠）として PR で提出され、レビューを通せる

## 参考リンク

- [langchain-ai/openwiki（GitHub）](https://github.com/langchain-ai/openwiki)
- [examples/openwiki-update.yml（公式ワークフロー例）](https://github.com/langchain-ai/openwiki/blob/main/examples/openwiki-update.yml)
- [Deep Agents（生成エージェントの基盤）](https://github.com/langchain-ai/deepagentsjs)
- [Open Knowledge Format (OKF) v0.1 仕様](https://github.com/GoogleCloudPlatform/knowledge-catalog/blob/main/okf/SPEC.md)
- [peter-evans/create-pull-request](https://github.com/peter-evans/create-pull-request)
- [LLM Wiki パターン（当ブログ Wiki）](/blogs/wiki/concepts/llm-wiki-pattern/)
- [GitHub Actions セキュリティ（当ブログ Wiki）](/blogs/wiki/guides/github-actions-security/)
- [AI エージェントのシークレット管理（当ブログ Wiki）](/blogs/wiki/guides/ai-agent-secret-management/)
