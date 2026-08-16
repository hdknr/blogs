---
title: "Google Code Wiki を設計として読む — 「毎回読み直す」をやめた常設 Wiki 層"
description: "Google が 2025 年 11 月に公開した Code Wiki を、機能紹介ではなく設計として読む。チャットがコードではなく生成済み Wiki を読む構造、LLM Wiki パターンとの同型性、DeepWiki との差、プライベートリポジトリ非対応という制約までを整理する。"
date: 2026-08-16
lastmod: 2026-08-16
slug: "google-code-wiki-llm-wiki-pattern"
draft: false
source_url: "https://github.com/hdknr/blogs/issues/572#issuecomment-5306590695"
categories: ["AI/LLM"]
tags: ["Code Wiki", "DeepWiki", "Gemini", "Google", "RAG"]
---

X で「Google が開発者待望のツールを出した」という投稿が流れてきた。CodeWiki というらしい（正式名称は二語の Code Wiki）。リポジトリを貼るだけで対話的なドキュメントに変換され、図も自動生成され、コードを理解したチャットボットまで付いてくる、と。

調べてみると、ツール自体は実在する。[Code Wiki](https://codewiki.google/) は、公開リポジトリの URL を貼るだけで Gemini がそのコードベースの Wiki を生成し、以後コードの変更に追従して更新し続ける Google のサービスだ。生成された Wiki はそのままチャットの知識ベースになる。

ただし「今出た」わけではない。パブリックプレビューでの公開は **2025 年 11 月 13 日**で、本記事の執筆時点から見て 9 か月前になる。バズった投稿はその再発見にすぎない。

とはいえ、9 か月前のツールが今もタイムラインで数千リポストを集めるのには、それなりに理由がある。この記事では「新しいツールの紹介」ではなく、次の 3 点を見ていく。

- Code Wiki が採った設計上の選択（なぜ「常設 Wiki」なのか）
- LLM Wiki パターンとの同型性と、決定的な違い
- 9 か月経っても解けていない制約

## Code Wiki が実際に何をするか

[公式ブログ](https://developers.googleblog.com/introducing-code-wiki-accelerating-your-code-understanding/)（Google Cloud / Google Research の 4 名連名）は、解こうとしている問題を明確に書いている。

> Reading existing code is the one of the biggest, most expensive bottlenecks in software development.
> （既存コードを読むことは、ソフトウェア開発における最大かつ最もコストの高いボトルネックの一つだ）

「コードを書く」ではなく「コードを読む」をボトルネックと定義したところが出発点になっている。そのうえで、Code Wiki は三つの性質を掲げる。

| 性質 | 内容 |
|---|---|
| **Automated & always up-to-date**<br>（自動生成・常に最新） | コードベース全体をスキャンし、変更のたびにドキュメントを再生成する |
| **Intelligent & context-aware**<br>（文脈を持つ） | 常に最新の Wiki 全体が、統合チャットの知識ベースになる |
| **Integrated & actionable**<br>（コードに直結） | Wiki の各節とチャットの回答が、該当するコードファイル・定義に直接ハイパーリンクされる |

加えて、テキストで足りない箇所にはアーキテクチャ図・クラス図・シーケンス図が自動生成され、これもコードの現状に追従する。

### 使い方 — codewiki.google の後ろにリポジトリ URL を繋ぐ

使い方は単純で、`codewiki.google` の後ろにリポジトリの URL をそのまま繋ぐ。パブリックプレビュー中の現在、公開リポジトリの Wiki はログインも課金もなしに閲覧できる。

```text
https://codewiki.google/github.com/{owner}/{repo}

# 例: Gemini CLI 自身の Wiki
https://codewiki.google/github.com/google-gemini/gemini-cli
```

## Code Wiki の本質は図の自動生成ではなく「Wiki が常設であること」

冒頭の X 投稿は「図を生成する」「チュートリアルを作る」「チャットボットが付く」と機能を並べていた。しかし機能の列挙だと、既存のコード解説 AI との違いが見えない。設計として効いているのは、もっと地味な一点だと思う。

**チャットが参照するのは、コードそのものではなく、生成済みの Wiki である。**

コードへの質問応答を素直に実装すると、質問のたびに関連ファイルを検索して読み込む方式になる（これがコードに対する RAG だ）。この方式では、一度組み立てた「このモジュールは何をしているか」という理解が、回答を返した瞬間に捨てられる。次の質問はまたゼロから始まる。

Code Wiki は、その理解を Wiki という形で外に固定してしまう。チャットは毎回コードを読み直すのではなく、既に構造化された Wiki を文脈として読む。

![コード理解の二つの型の比較図。左は質問のたびに検索し直すコード RAG、右は Gemini が全体スキャンして常設 Wiki 層を作り、それをチャットの知識ベースにする Code Wiki 型](/blogs/images/google-code-wiki-architecture.png)

この違いは、コストと品質の両方に効く。

- **コスト**: 全体スキャンは重いが、リポジトリあたり一度（＋変更差分）で済む。質問回数に比例しない。
- **品質**: 検索で引っ張ってきたコード片の寄せ集めではなく、リポジトリ全体を俯瞰して書かれた構造の上から答えられる。

そして「常に最新」を担保する仕掛けが、変更検知による再生成だ。ドキュメントが腐る原因は、書く手間ではなく**更新されないこと**にある。生成コストがゼロに近づけば、腐る前に作り直すという解き方が成立する。これは「ドキュメントを速く書く」のではなく、「ドキュメントの寿命の問題を、再生成の頻度で潰す」というアプローチになっている。

## LLM Wiki パターンとの一致

この構造は、当ブログで扱ってきた [LLM Wiki パターン](/blogs/wiki/concepts/llm-wiki-pattern/) とほぼ同型だ。Andrej Karpathy が提案した、LLM に個人ナレッジベースを継続的に構築・保守させるやり方である。

| LLM Wiki パターン | Code Wiki |
|---|---|
| Raw Sources（原本資料） | リポジトリのソースコード |
| Wiki（AI が生成・保守） | 自動生成される構造化ドキュメント |
| Schema（人間が定義する管理指示） | Google 側が固定（ページ構成・図の種類・リンク規則） |
| Ingest / Query / Lint | スキャン再生成 / チャット / 変更検知 |

対象が「個人が読んだ資料」から「リポジトリのコード」に変わっただけで、**知識を都度検索するのではなく、AI が保守する中間層に固定して積み上げる**という骨格は同じである。

違いは Schema をどこに置くかだ。LLM Wiki パターンでは Wiki の構造・命名規則・ワークフローを人間が定義する。Code Wiki ではそこが製品側に固定されていて、ユーザーが触れる余地はない。手軽さと引き換えに、「自分たちのチームが必要とする切り口でまとめてほしい」という要求は通らない。

## DeepWiki との違い — 機能はほぼ同じ、差はモデルと運用主体

同じ発想の先行例として、Cognition の [DeepWiki](https://deepwiki.com/) がある（Devin Wiki / Devin Search の無料公開版として 2025 年 5 月に登場した）。URL の `github.com` を `deepwiki.com` に差し替えるだけで、そのリポジトリの Wiki が開く。

```text
https://github.com/google-gemini/gemini-cli    # 元の URL
https://deepwiki.com/google-gemini/gemini-cli  # github.com を deepwiki.com に差し替える
```

Code Wiki と DeepWiki は、機能セットとしてはかなり近い。自動生成された Wiki、図、ソースへのリンク、対話用のチャット、という構成はほぼ共通で、アクセス方法（URL を差し替える）まで似ている。

現時点で意味のある差分は、機能の有無というより**背後のモデルと運用主体**だろう。Code Wiki は Gemini、DeepWiki は Devin 側のモデルで動く。同じリポジトリを両方で開いて、どちらの説明が自分の読みたい粒度に合うかを比べるのが、いちばん早い評価方法になる。どちらも公開リポジトリならそのまま試せる。

## 9 か月経っても解けていない制約 — プライベートリポジトリと Gemini CLI 拡張の待機列

実務で使うかどうかの判断は、たいてい機能表ではなく制約側で決まる。

### Web 版が扱えるのは公開リポジトリだけ

Code Wiki の Web 版に自社のプライベートリポジトリを読ませることはできない。公式ブログもここを認識していて、内部リポジトリ向けにローカルで安全に実行できる Gemini CLI 拡張を用意すると書いている。

> While the open-source ecosystem hosts massive repositories, it's often our own private repos that are the hardest to document effectively.
> （オープンソースには巨大なリポジトリがあるが、実際に最も文書化が難しいのは自分たちのプライベートリポジトリであることが多い）

まさにその通りで、著者がもう社内にいないレガシーコードこそ、この手のツールが最も効く領域だ。ただしこの拡張は**発表から 9 か月が経った現在も待機列（waitlist）のまま**で、一般提供の時期は公表されていない。Code Wiki 自体もパブリックプレビューのままである。

### 現状の使いどころ

つまり現状の使いどころは、こう整理できる。

- **効く**: OSS ライブラリを導入前に評価する、依存しているライブラリの内部挙動を追う、初見のリポジトリにコントリビュートする前に全体像を掴む
- **効かない**: 自社のプロダクトコードを理解する、社内の秘伝のレガシーを引き継ぐ

X でバズっていた「読めないプロジェクトが数分で読めるようになる」は、対象が公開リポジトリである限り概ね正しい。ただし多くの開発者が本当に読めなくて困っているコードは、まだこのツールの外側にある。

## まとめ

- Google Code Wiki は実在するが、公開は 2025 年 11 月 13 日で、今回バズったのは再発見である
- 設計上の要点は機能の多さではなく、**チャットがコードではなく生成済み Wiki を読む**という構造にある
- 質問ごとに読み直す方式と違い、理解が中間層に蓄積される。ドキュメントが腐る問題は再生成の頻度で潰している
- これは [LLM Wiki パターン](/blogs/wiki/concepts/llm-wiki-pattern/) をコードベースに適用したものと見なせる。ただし Schema（構造の定義）は製品側に固定されている
- DeepWiki とは機能・アクセス方法ともに近く、実質的な差はモデルと運用主体。両方で同じリポジトリを開いて比べるのが早い
- プライベートリポジトリ対応（Gemini CLI 拡張）は 9 か月経っても待機列のままで、実務投入の最大の制約になっている

## 参考リンク

- [Introducing Code Wiki: Accelerating your code understanding — Google Developers Blog](https://developers.googleblog.com/introducing-code-wiki-accelerating-your-code-understanding/)
- [Code Wiki](https://codewiki.google/)
- [DeepWiki](https://deepwiki.com/)
- [DeepWiki: AI docs for any repo — Cognition](https://cognition.com/blog/deepwiki)
- [Google previews Code Wiki: Can you trust AI to document your repository? — The Register](https://www.theregister.com/software/2025/11/17/google-previews-code-wiki-ai-to-document-repositories/2804407)
- [LLM Wiki パターン（当ブログ Wiki）](/blogs/wiki/concepts/llm-wiki-pattern/)
