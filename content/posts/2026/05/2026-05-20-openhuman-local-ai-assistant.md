---
title: "OpenHuman — 完全ローカルで動くパーソナルAIアシスタント：プライバシー最優先でChatGPT級の体験を自分のPCで"
date: 2026-05-20
lastmod: 2026-05-27
slug: "openhuman-local-ai-assistant"
draft: false
source_url: "https://github.com/hdknr/blogs/issues/1#issuecomment-4494575313"
description: "OpenHumanはRust製オープンソースのローカルAIアシスタント。Memory Tree・Ollama連携・118サービスAuto-fetchでChatGPT級の体験を実現する。ただしデフォルト構成ではTinyHumansへのサブスク課金が前提で、本当に「完全ローカル」にするには追加設定が必要——その構造を解説。"
categories: ["AI/LLM"]
tags: ["OpenHuman", "ローカルAI", "ollama", "AIエージェント", "プライバシー", "TinyHumans"]
---

> **2026-05-27 追記**: 実際にインストールしてみたところ、デフォルトのままでは TinyHumans へのサブスク課金（=有料アカウント）が必要なことが判明した。GPL-3 のオープンソースなのになぜ有料なのか、本記事に「[なぜ TinyHumans への課金が必要なのか](#なぜ-tinyhumans-への課金が必要なのか--オープンソースなのに有料な構造の正体)」セクションを追加した。「完全ローカル」を額面どおりに実現するための回避ルートも併記している。

「クラウドAIに自分の悩みを打ち明けるのが不安」という声をよく聞く。仕事の機密、家族の話、健康上の悩み——ChatGPTに投げてはみるものの、その会話がサーバーに残り続けることへの抵抗感は根強い。

そこに登場したのが **OpenHuman** だ。GitHubスター数2.7万を超え、週に1,000以上のペースで増え続けるこのプロジェクトは、「ChatGPT級のAIを完全にローカルで動かす」という問いへの実践的な回答を提供している。

## OpenHumanとは

[OpenHuman](https://github.com/tinyhumansai/openhuman) は、TinyHumans AIが開発するオープンソースのエージェント型AIアシスタントだ。Rustをコアに持ち、デスクトップアプリとして動作する。

公式の説明は簡潔にまとめられている。

> **Your Personal AI super intelligence. Private, Simple and extremely powerful.**

ポイントは3点だ。

- Memory Tree による長期記憶
- Obsidianスタイルのローカルナレッジベース
- 118以上のサービス連携

これらを組み合わせることで、「インストールから数分でユーザーを知り尽くしたエージェント」を目指している。

## なぜ「ローカルAI」が重要なのか

ChatGPTをはじめとするクラウドAIの課題は、会話が外部サーバーへ送信される点にある。個人情報保護の観点から問題となるだけでなく、企業での利用では情報漏洩リスクが伴う。

OpenHumanが解決しようとしているのはこの点だ。

- **会話を外に出さない構成が選べる** — ローカルLLM（Ollama / LM Studio経由）を選択すれば推論まで自機で完結する
- **データは自分のPCに保存される** — Memory Tree DB と Markdown Vault はローカルファイルとして残る
- **日本語README完備** — 日本語ユーザーへの配慮も行き届いている
- **Rust製で爆速** — コアがRustで書かれており、動作が軽快

ただし注意点がある。**デフォルト構成では「サインイン」「モデルルーティング」「Web検索プロキシ」「Composio経由のOAuth/ツール連携」がすべてOpenHuman（TinyHumans）社のマネージドバックエンドを経由する**。つまり初回起動時に TinyHumans アカウントを作って有料サブスクに入らないと、せっかくのMemory TreeもAuto-fetchも動かない。「完全オフライン」を額面どおりに実現するには、ローカルモデル＋Composio直接モード＋自前のWeb検索APIキー、といった追加設定が必要になる。詳細は後述する。

## 主な機能

### Memory Tree + Obsidian Vault

OpenHumanの中核機能は **Memory Tree** だ。接続した各種サービスから取得したデータを3,000トークン以内のMarkdownチャンクに圧縮し、SQLiteに階層的に保存する。同時に、Obsidianと互換性のある `.md` ファイルとしてローカルVaultへ書き出す。

Karpathy氏の [Obsidian Wikiワークフロー](https://x.com/karpathy/status/2039805659525644595) にインスパイアされており、AIが「あなたの文脈」をリアルタイムで持ち続けるための仕組みとなっている。Obsidianを使っているユーザーはそのままナレッジベースとして参照・編集できる。

### 118以上のサービス連携（Auto-fetch）

Gmail、Notion、GitHub、Slack、Stripe、Google Calendar、Google Drive、Linear、Jiraなど118以上のサービスにOAuth一発で接続できる。

**Auto-fetch** 機能が特徴的で、20分ごとに各連携サービスから新しいデータを自動取得してMemory Treeへ流し込む。ポーリングループを自分で書く必要はない。翌朝起動した時点で、昨晩のメールや今日のカレンダーがすでにエージェントのコンテキストに入っている。

### TokenJuice — トークン圧縮層

LLMにデータを渡す前に必ずTokenJuiceというトークン圧縮層を通す。HTMLをMarkdownへ変換し、長いURLを短縮し、冗長なツール出力を要約する。CJK（日本語・中国語・韓国語）や絵文字はグラフェム単位で保持されるため、日本語テキストが文字化けすることはない。

公式によれば、**コストと遅延を最大80%削減**できるとしている。

### デスクトップマスコット・ネイティブボイス

OpenHumanにはAIに「顔」がある。デスクトップ上に常駐するマスコットが発話・表情変化・リップシンクを行い、Google Meetへ実際の参加者として参加させることもできる。ネイティブボイス機能はデフォルトでElevenLabs TTSを使うが、v0.54.0以降はWhisper + Piper による完全ローカルの STT（音声認識）/ TTS（音声合成）も選択可能だ。

### モデルルーティング

OpenHumanの単一プランの中で、タスクに応じて推論・高速・ビジョンなど複数のLLMを自動選択する。Ollamaを使ったローカルAIも選択肢のひとつとして統合されている。

#### 「ローカルLLM」の中身

OpenHuman自身はモデルweightsを同梱せず、**OllamaまたはLM Studioにpullを委譲する**設計だ。公式ドキュメント（[Local AI](https://tinyhumans.gitbook.io/openhuman/features/model-routing/local-ai)）でデフォルト/推奨として挙げられているモデルは次のとおり。

| 用途 | デフォルト/推奨モデル | サイズ |
|------|---------------------|--------|
| Memory embeddings（記憶の埋め込み） | `all-minilm:latest` | 約23 MB |
| Summary-tree 構築（Memory Tree要約） | `gemma3:1b-it-qat` | 約700 MB |
| Chat / Reasoning | ユーザー設定（既定なし） | — |

チャット推論用のモデルは固定されておらず、ドキュメントの設定例では `ollama:llama3.1:8b` や `ollama:qwen2.5:14b` といった指定が示されている。つまり「ローカルLLM」の正体は、埋め込みに all-MiniLM、Memory Tree の階層要約に Google の Gemma 3 1B 量子化版が使われ、チャットは Llama 3.1 8B や Qwen2.5 14B などユーザーが pull した小〜中型モデルに委ねる構成だ。

「ChatGPT級のローカル体験」と謳われるが、実態は**フロンティアモデル級の推論性能を1台のPCで再現するのではなく、Memory Tree・Auto-fetch・TokenJuiceでコンテキストを最大化し、小型モデルでも実用ラインに引き上げる**というアプローチに近い。

## 他のAIアシスタントとの比較

以下は、公式READMEが競合として挙げているClaude Cowork（AnthropicのデスクトップAIエージェント製品。コーディングアシスタントのClaude Codeとは別製品）との比較だ。

| 項目 | Claude Cowork | OpenHuman |
|------|---------------|-----------|
| オープンソース | プロプライエタリ | GNU |
| 導入の手軽さ | デスクトップ + CLI | クリーンなUI、数分で完了 |
| メモリ | チャットスコープ | Memory Tree + Obsidianボールト |
| 連携数 | 少数 | 118以上（OAuth） |
| Auto-fetch | なし | 20分ごとのメモリ同期 |
| モデルルーティング | 単一モデル | 組み込み済み |

> 出典: OpenHuman公式READMEの比較表（Claude CoworkはAnthropicのデスクトップエージェント製品。Claude Codeとは別製品）

## インストール方法

macOS / Linux の場合はターミナルから1行で導入できる。

```bash
curl -fsSL https://raw.githubusercontent.com/tinyhumansai/openhuman/main/scripts/install.sh | bash
```

Windows の場合は PowerShell から次のコマンドを実行する。

```powershell
irm https://raw.githubusercontent.com/tinyhumansai/openhuman/main/scripts/install.ps1 | iex
```

または [tinyhumans.ai/openhuman](https://tinyhumans.ai/openhuman) からDMG・EXEをダウンロードすることもできる。

> **注意**: 現在アーリーベータ段階のため、荒削りな部分が残っている。LinuxのWayland環境でのAppImageクラッシュ問題（[#2463](https://github.com/tinyhumansai/openhuman/issues/2463)）はすでにクローズ済みだが、READMEには環境変数によるワークアラウンドへの参照が残っている。Arch Linux向けには `openhuman-bin` AURパッケージも用意されている。

### ビルドに必要なもの（ソースから開発する場合）

- Git、Node.js 24以上、pnpm 10.10.0
- Rust 1.93.0（`rustfmt` + `clippy`）
- CMake、Ninja、ripgrep、プラットフォームごとのデスクトップビルド前提条件

```bash
# サブモジュール初期化が必要
git submodule update --init --recursive
pnpm install

# UI開発のみ
pnpm dev

# デスクトップアプリ込み
pnpm --filter openhuman-app dev:app
```

## なぜ TinyHumans への課金が必要なのか — オープンソースなのに有料な構造の正体

実際にインストールしてみるとすぐに気付くのが、初回起動で「Sign in! Let's Cook」というサインイン画面が出てくることだ。READMEには **「One subscription includes all models」**（ひとつのサブスクで全モデル込み）とサラッと書いてあり、その「ひとつのサブスク」がTinyHumansへの月額課金を指している。

GitHubのREADME（[tinyhumansai/openhuman](https://github.com/tinyhumansai/openhuman)）と公式ドキュメントを読み込むと、課金が必要な理由は4つに整理できる。

### 1. 30以上のLLMプロバイダーをまとめて請求するため

OpenHumanのモデルルーティング機能は、タスクのヒント（`reasoning` / `fast` / `vision`）に応じて Claude・GPT-4o・Gemini・Llama などを自動で切り替える。これを自前で構築するには、Anthropic・OpenAI・Google・Cohere・Mistral……と**個別にAPIキーを発行して個別に課金カードを登録**する必要がある。

TinyHumansはこれを**「30+ providers needed to build your AI assistant」**として束ね、1枚のサブスクで全プロバイダーへ送るプロキシを担っている。実態は LLM 課金のアグリゲーター／プロキシだ。利用者から見れば「課金カード1枚で全モデル」、TinyHumans から見れば「ユーザーに代わって裏で各社へ支払い、その差額＋取扱手数料で食う」というビジネスモデルになっている。

### 2. Composio（118連携の本体）への支払いを巻き取るため

Gmail / Notion / GitHub / Slack ……といった118以上のOAuth連携は、OpenHumanが自前で書いているわけではなく、[Composio](https://composio.dev/) というSaaSにOAuth ハンドシェイクとツール呼び出しを委譲している。Composio自体が有料サービスであり、そのコストはTinyHumansのサブスクに含まれる。

「Composio直接モード」を選べば自分のComposio APIキーで動かせる代わりに、**今度はComposioに直接課金が発生する**。OpenHumanへの課金を回避してもComposio側の課金は残るので、無料化したいなら連携の数を絞るか、OAuth連携自体を諦めるしかない。

### 3. リアルタイムWebhookの受け口がクラウド前提だから

Auto-fetch を「20分ごとのポーリング」だけで使うなら自宅PCで完結する。しかし Gmail の新着メールや GitHub のPRイベントを**リアルタイムで拾う「triggers」**機能は、外部サービスからのwebhookを受け取る公開URLが必要になる。デスクトップアプリ単体ではNAT越えできないため、TinyHumans のクラウドが webhook 受信エンドポイントを代行する。

公式ドキュメントは Composio 直接モードでも明示している。

> If you want to run Composio directly instead, configure direct mode with your own Composio API key; **real-time trigger webhooks then need to be hosted and wired by you.**

「自分でWebhook受信サーバを立てて、Composioに登録して、ngrokなりCloudflare Tunnelなりで繋いでください」と。自前ホスティングできるユーザーは少ないので、現実的にはTinyHumansに課金して任せたほうが楽——というのが製品設計上の落とし所になっている。

### 4. ライセンスと商用モデルが分離されている（GPL-3 + Managed Service モデル）

OpenHumanのソースコードは **GPL-3.0** で公開されており、誰でも fork して自前ビルドできる。ただし「コードが自由」と「マネージドサービスが無料」はイコールではない。これは Mattermost / Cal.com / Plausible / Supabase など近年のOSS製品で一般化したパターンで、

- **コード（フロント＋ローカルランタイム）= GPL-3 で公開**
- **裏側のSaaS（モデル仲介・OAuth代行・Webhook 受信）= 商用サブスク**

という二層構造になっている。OSSとして検証可能・自前ホスト可能であることを担保しつつ、開発の財布はマネージドサービスで持つ、というハイブリッドだ。「Open source」「Local-first」「Private」というキーワードと、「Sign in to start」「Subscription required」のあいだのギャップはここから生まれる。

### 課金を回避して本当に「完全ローカル」で動かす設定

GPL-3 のおかげで、覚悟があれば課金ゼロ運用は可能だ。必要な設定をまとめると次のようになる。

| レイヤー | デフォルト（要課金） | 完全ローカル化の代替 |
|---------|---------------------|---------------------|
| 認証 | TinyHumans アカウントでサインイン | 自前ビルド＋サインインスキップ（ソース改変 or 設定で `local-only` モード） |
| Chat / Reasoning LLM | TinyHumans プロキシ経由（Claude / GPT 等） | Ollama / LM Studio のローカルモデル（Llama 3.1 8B、Qwen2.5 14B など） |
| Embeddings / Memory Tree要約 | プロキシ経由 | Ollama に `all-minilm` と `gemma3:1b-it-qat` を pull |
| Web検索 | TinyHumans 経由のプロキシ | 自前で Brave Search / SearXNG / Tavily の APIキーを設定 |
| OAuth連携 | Composio（TinyHumans経由） | Composio 直接モード（要自前APIキー）または OAuth連携を捨てる |
| リアルタイムtrigger | TinyHumans クラウドが受信 | 自前Webhookサーバ＋トンネリング、または triggers を諦める |

設定の手間と、Composio直接モードでのComposio側課金、Webhookホスティング費を考えると、**「完全に無料・完全にローカル」を選んだ瞬間、エンタープライズ向けセルフホスト製品を1人で運用するのと同じ複雑度**になる。これがTinyHumansが「一回課金してくれれば全部やる」と提示する価値の本体だ。

### 「Local-First」の正しい読み方

OpenHumanのマーケティング表現は「Local-first」であって「Local-only」ではない、と読むのが正確だ。

- **Local-first**: あなたのデータ（Memory Tree DB / Obsidian Vault / 会話履歴）は**あなたのマシン**に保存される。再起動・OS再インストール・サブスク解約後も手元に残る。
- **そのうえで** モデル推論・OAuth・Web検索といった**外部API呼び出しのプロキシは TinyHumans 経由**になっており、その費用がサブスクとして請求される。

「会話そのものが TinyHumans のサーバを通る（プロキシされる）」点は重要で、ローカルLLMを選ばない限り**プロンプト本文はTinyHumansを経由して各LLMプロバイダーに転送される**。Anthropic や OpenAI に直接送るのと、TinyHumans を一段挟むのとでは、リスクモデルが変わることに注意したい。

## まとめ

OpenHumanは「クラウドAIに頼らずに、自分専用のAIアシスタントを持ちたい」というニーズに対する現時点での最も完成度の高い回答のひとつだ。

Memory Tree・Auto-fetch・TokenJuiceという3つの機能が組み合わさることで、「インストールしたその日からコンテキストを持ったAI」が実現する。アーリーベータの荒削りさはあるものの、週1,000スター超のペースは本物の需要を反映している。

ただし**製品としてのデフォルト体験は TinyHumans への有料サブスクが前提**だ。「OSS だから無料で完全ローカル」とそのまま受け取ると期待外れになる。実態は、

- **コード**: GPL-3 で完全オープン、自前ビルド・自前ホスト可能
- **既定運用**: TinyHumans のマネージドSaaSに月額を払い、30+ LLMプロバイダーと118 OAuth連携をひとまとめにする「課金一本化サービス」
- **本気の完全ローカル**: 可能だが、Composio直接モード／自前Webhook／ローカルLLM／自前検索APIまで揃える必要があり、複雑度が一気に上がる

という三段階の選択肢があるOSS+SaaSハイブリッド製品、と理解するのが正しい。

プライバシーを重視するユーザーや、企業の機密情報をクラウドへ出したくないチームにとって、OpenHumanは試す価値のある選択肢だ。ただし試す前に、自分が払える「複雑度の予算」と「金額の予算」を見極めておくと、起動して即「サインインしてください」「Subscribeしてください」と出てきても落胆せずに済む。
