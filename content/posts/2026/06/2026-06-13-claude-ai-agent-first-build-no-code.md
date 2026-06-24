---
title: "コードゼロで最初のAIエージェントを作る完全ガイド — Claude Projects・Cowork・スケジュール実行の3ステップ"
date: 2026-06-13
lastmod: 2026-06-13
slug: "claude-ai-agent-first-build-no-code"
draft: false
source_url: "https://github.com/hdknr/blogs/issues/1#issuecomment-4714967798"
categories: ["AI/LLM"]
tags: ["Claude", "AIエージェント", "ノーコード", "Claude Projects", "Claude Cowork"]
---

AIエージェントの話はどこでも聞こえてくる。調査するエージェント、文章を書くエージェント、メールを管理し、スプレッドシートを更新し、レポートをまとめ、あなたが寝ている間にワークフロー全体を実行するエージェントまで登場している。

すごそうに聞こえる。テクニカルでなければ不可能にも聞こえる。

**不可能ではない。これから証明する。**

この記事を読み終えるころには、最初から最後まで一切手を触れることなくタスクを実行できる動作するAIエージェントが手元に存在する。コーディング不要。APIキー不要。ターミナルコマンド不要。Claude、明確な指示、そして30分の時間があれば十分だ。

---

## AIエージェントとは何か（難しい言葉を使わずに説明する）

技術的な定義はいったん忘れていい。

**AIエージェントとは、あなたが一度に一つずつやっていた複数のステップをClaudeが自動で実行してくれるものだ。**

普通にClaudeを使うと、こんなフローになる:

1. トピックを調査するよう指示する
2. 結果を読む
3. アウトラインを書くよう指示する
4. 確認する
5. 記事を書くよう指示する
6. 編集する
7. フォーマットするよう指示する
8. コピーする

これはすべて手動による往復作業の繰り返しだ。それぞれでユーザーが読んで、承認して、次の指示を手動で出さなければならない。

**エージェントはこれらのステップを自動で順番に実行する。** 「このトピックを調査して、アウトラインを作り、完全な記事を書いて、出版用にフォーマットして」と言うだけで、Claudeは4つのステップを次々と実行し、完成品を届けてくれる。

違いはそれだけだ。チャットボットは1つのことをして待つ。エージェントは一連のことをして完成したアウトプットを届ける。

---

## コードなしで構築できる3種類のエージェント

APIは不要。Agent SDKも不要。コードを1行も書く必要はない。

Claudeの既存ツールだけで3種類のエージェントを構築できる:

### タイプ1: チャットエージェント（Claude Projects）

マルチステップのワークフローを定義するシステムプロンプトを持つClaude Project。タスクを与えると、システムプロンプトに従うべき順序が明示されているため、フルワークフローを自動実行する。

### タイプ2: ファイルエージェント（Claude Cowork）

コンピュータ上のファイルを処理するCoworkタスク。フォルダを読み込み、各ファイルを処理し、出力を作成して、すべてを整理する。一つの指示から。

### タイプ3: スケジュール実行エージェント（Cowork + /schedule）

スケジュールに従って自動実行するCoworkタスク。朝7時にエージェントが起動し、メールを確認し、重要なものをまとめ、デスクトップにブリーフィングを保存する。あなたからの入力は一切不要。

**3つ全部構築する。最もシンプルなものから始める。**

---

## Build 1: リサーチ→記事エージェント（15分）

これはトピックを受け取り、完成した記事を生成するチャットエージェントだ。インプット1つ、アウトプット1つ。

### ステップ1: 新しいClaude Projectを作る

Claudeを開く。「Projects」をクリック。「Create Project」をクリック。名前を「Article Agent」にする。

### ステップ2: システムプロンプトを書く

プロジェクトのシステムプロンプトに以下を貼り付ける:

```
You are an autonomous article production agent. When the user gives you a topic,
you execute the following workflow automatically without stopping for approval between steps:

STEP 1 - RESEARCH
Search the web for the latest information on this topic. Find 5-7 relevant sources.
Extract the key insights, statistics, and expert perspectives.

STEP 2 - ANGLE
Based on your research, identify the most interesting angle. What does the reader already
believe about this topic? How can we challenge or expand that belief? Choose the angle
that would generate the most engagement.

STEP 3 - OUTLINE
Create a detailed article outline:
- Opening hook (contrast between common belief and reality)
- 5-7 main sections with bold subheadings
- Specific data points or examples for each section
- Closing CTA

STEP 4 - WRITE
Write the complete article. 2000-3000 words. Short paragraphs (3 sentences max).
Bold the key insight in every section. Specific numbers over vague claims.
Direct, conversational tone. Zero filler.

STEP 5 - REVIEW
Review the article against these quality criteria:
- Does every section add new information?
- Are all claims supported by specific numbers or examples?
- Would a busy person stop reading at any point? If yes, fix those sections.
- Is the opening hook genuinely compelling?

Output the final article. Include a recommended title at the top.

Execute all 5 steps in one response. Do not ask for approval between steps.
```

### ステップ3: テストする

「Article Agent」プロジェクトで新しい会話を開く。一文を入力する:

```
"AI agents for beginners"
```

Claudeは5つのステップを実行する。調査。アングル選択。アウトライン。完全な下書き。品質レビュー。3語の入力から完成した洗練された記事が手に入る。

**これがあなたの最初のエージェントだ。** 構築に15分かかり、使うたびに2〜3時間の手作業を代替する。

---

## Build 2: ファイル処理エージェント（15分）

これはフォルダ内のファイルを自動で処理するCoworkエージェントだ。

### ステップ1: Claude Desktopを開いてCoworkタブへ

処理したいフォルダへのCoworkアクセスを許可する。

### ステップ2: バッチ処理の指示を与える

```
/Downloadsフォルダに移動して。その中のすべてのPDFファイルに対して:

1. ドキュメントを読む
2. 要約を抽出する（箇条書き5つまで）
3. 最も重要なアクションアイテムを3つ特定する
4. 同じファイル名だが.md拡張子の要約ファイルを/Summariesに保存する

すべてのファイルを処理したら、"all-summaries.md"というマスターサマリーファイルを作成して
日付順に並べてすべてをまとめる。

すべてのファイルを処理すること。ファイル間で止まらないこと。
```

Claudeはフォルダ内のすべてのPDFを処理する。それぞれを読み込む。要約を抽出する。個別ファイルを作成する。そしてマスタードキュメントを作成する。

**一つの指示。フォルダ全体が処理される。** PDFが20枚あれば、2〜3時間の手動読み取りとノート取りが節約できる。

---

## Build 3: 定期実行モーニングエージェント（15分）

これは毎朝自動で実行されるスケジュール実行エージェントだ。

### ステップ1: Coworkを開く

### ステップ2: `/schedule`を入力する

### ステップ3: 定期タスクを設定する

```
毎平日朝7:00:

1. 昨日の午後5時以降に受信したGmailを確認する
2. 各メールを分類する:
   - ACTION REQUIRED（返信や判断が必要）
   - FYI ONLY（情報のみ、返信不要）
   - CAN IGNORE（ニュースレター、プロモーション、自動通知）
3. ACTION REQUIREDの各メールに対して返信案を作成する
4. 今日の会議についてGoogleカレンダーを確認する
5. 各会議の参加者とトピックをメモする
6. すべてを"morning-brief-[今日の日付].md"というファイルに保存して
   /Dailyフォルダに入れる

フォーマット:
## 緊急メール
[返信案付きリスト]

## 今日のカレンダー
[参加者情報付き会議]

## FYI項目
[簡潔なリスト]
```

スケジュールを設定する。毎平日朝7時。

**これ以降、完全な毎日のブリーフィングで目が覚める。** メールが整理されている。返信案が用意されている。カレンダーがまとめられている。あなたからの努力は一切不要。エージェントが寝ている間に動く。

---

## エージェントを時間とともに改善する方法

エージェントの最初のバージョンはそこそこだ。完璧ではない。改善方法はこうだ:

**修正ルール**: エージェントのアウトプットに修正が必要なたびに、システムプロンプトまたはタスク説明を更新する。「要約が長すぎる」は新しいルールになる: 「各要約は100語以内にすること。」10回の修正後、エージェントは劇的に精度が上がる。

**例示ルール**: 優れたアウトプットの例をProjectのナレッジファイルにアップロードする。「これらの3つの記事は完璧なアウトプット品質を表している。このレベルに合わせること。」例があるエージェントは指示だけのエージェントを上回る。

**フィードバックループ**: 週に一度、過去7日間のエージェントのアウトプットをレビューする。何がうまくいったか？何を修正する必要があったか？それに応じて指示を更新する。週次改良を受けるエージェントは、一度も更新されないエージェントより1ヶ月後に3〜5倍高品質なアウトプットを生成する。

---

## 今日構築できる5つのエージェントアイデア

3種類を知ったところで、すぐに構築できる5つのエージェントを紹介する:

### 1. コンテンツ転用エージェント

**インプット**: 長文記事1本。**アウトプット**: X/Twitterスレッド、LinkedInの投稿、Instagramキャプション、ニュースレターティーザー、YouTubeスクリプトアウトライン。すべて一回の返答で。

### 2. 週次競合トラッカー

毎週スケジュール実行。上位3社の競合をウェブ検索する。新しい製品ローンチ、価格変更、公開コンテンツ、ニュース報道を見つける。競合インテリジェンスブリーフィングを保存する。

### 3. クライアントオンボーディングエージェント

**インプット**: クライアント名とプロジェクト説明。**アウトプット**: ウェルカムメール、プロジェクトタイムライン、インテークアンケート、ブランドアセットリクエスト。すべてクライアントの詳細でカスタマイズ済み。送信準備完了。

### 4. ミーティングデブリーフエージェント

**インプット**: 生の会議メモ（雑然としていてもOK）。**アウトプット**: 決定事項、担当者付きアクションアイテム、未解決の質問、次のステップのクリーンなサマリー。参加者と共有できる形にフォーマット済み。

### 5. 請求書処理エージェント

毎月/Receiptsフォルダをスキャンするコーワークエージェント。各領収書から日付、ベンダー、金額、カテゴリを抽出する。カテゴリ分けされたスプレッドシートを作成する。合計を計算する。/Financeに保存する。

---

## まとめ: 今日から始めるエージェント思考

ほとんどの人が気づいていないことがある。

あなたは3つのエージェントを構築しただけでなく、**エージェントを構築するスキルを身につけた**。そのスキルは複利で成長する。構築するエージェントが増えるにつれ、再利用できるパターンが学べる。システムプロンプトが鋭くなる。ワークフローが緻密になる。アウトプットの質が高くなる。

エージェントを構築して1ヶ月後には、人生のあらゆる繰り返し作業を見て「これはエージェント化できる」と考えるようになる。

そして実際にできる。なぜなら、パターンを一度理解すれば（ステップを定義し、品質基準を設定し、シーケンスを自動化する）、何でもエージェント化できるからだ。

ほとんどの人は、AIエージェントがどれほどクールに聞こえるかを話しながら、手作業で仕事を続ける。**今日最初のエージェントを構築した人たちは、月末までにエージェントチームを走らせているだろう。** そして二度と自分でその作業をすることはないだろう。

---

*元記事: [@eng_khairallah1](https://x.com/eng_khairallah1/status/2065721530546373016) (Khairallah AL-Awady)*
