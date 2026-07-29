---
title: "Claude Code の社内設計を読み解く：ループ・CLAUDE.md・Skills・Dreaming"
date: 2026-06-26
lastmod: 2026-06-26
slug: "claude-code-loop-skills-dreaming"
draft: false
description: "Anthropicのエンジニアが語ったClaude Code社内活用法——ループ設計、CLAUDE.mdとSkillsの使い分け、Dreaming機能を裏取りする。"
source_url: "https://github.com/hdknr/blogs/issues/1#issuecomment-4806753053"
categories: ["AI/LLM"]
tags: ["Claude Code", "Anthropic", "CLAUDE.md", "Skills", "Dreaming"]
---

「Claude Code の社内設計を、Anthropicのエンジニアが全部バラした」という投稿が X（旧Twitter）で拡散された。ループ × CLAUDE.md × Skills という構造で、Anthropic 社内では自己改善するエージェントを構築しているという内容だ。

元になっている動画は、Cat Wu と Boris Cherny が出演した対談だと見られる。二人は Claude Code の生みの親であり、Every 社のポッドキャスト「AI & I」（配信元: [every.to](https://every.to/podcast/how-to-use-claude-code-like-the-people-who-built-it)）で、社内でどう使っているかを語った。

この記事では、拡散されたポイントを一次情報（Anthropic公式ドキュメントや報道）で裏取りしながら整理する。

## ループ設計：プロンプトではなく「繰り返しの条件」を書く

Boris Cherny は別のインタビューでも「もう自分でプロンプトを打つことはない、書いているのはループだ」と語っている（[The New Stack](https://thenewstack.io/loop-engineering/)）。人間が一問一答でエージェントを操作するのではなく、「どんな条件を満たすまで何を繰り返すか」を設計し、あとはエージェントに任せるという考え方だ。

Claude Code の `/loop` コマンドはこの発想を体現した機能で、インターバルを指定して同じタスクを繰り返し実行できる。この仕組み自体の使い方は以前の記事「[AIコーディングエージェント時代の新常識](/blogs/posts/2026/06/claude-code-loop-design-agents/)」で詳しく解説しているので、そちらを参照してほしい。

## CLAUDE.md は肥大化する——Skills の段階的開示で解決する

拡散された投稿でもう一つ強調されていたのが、CLAUDE.md の肥大化問題だ。「CLAUDE.md は不合理なほど効果的だが、肥大化する。Skills の段階的開示がこれを解決する」という主張である。

これは Anthropic 公式のガイダンスとも整合する。Claude Code のベストプラクティスでは、常に有効にしておきたいルールは CLAUDE.md に、特定のワークフローでのみ必要な手順は Skills に切り出すことが推奨されている。

Skills は「段階的開示（progressive disclosure）」という仕組みを採用している。インストールされている Skill の一覧はフロントマター（名前と説明）だけが常にシステムプロンプトに読み込まれ、実際の詳細な手順（`SKILL.md` の本文や `references/` 以下のファイル）は、そのタスクが必要になったときに初めて読み込まれる（[Anthropic: Equipping agents for the real world with Agent Skills](https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills)）。

これにより、Skill をいくつインストールしてもコンテキストウィンドウを圧迫しない。CLAUDE.md に全部書き込んで肥大化させるのではなく、「常時必要なルールは CLAUDE.md」「たまにしか使わない手順は Skills」と役割分担することが、現時点でのベストプラクティスだ。

実際、このブログのリポジトリでも同じ設計を採用している。ブログ執筆や Wiki 更新のような個別ワークフローは `.claude/skills/` 以下の Skill として切り出し、CLAUDE.md には常時有効なルール（URLのアローリスト、ブランチ命名規則など）だけを残している。

## エージェント自身がメモリの読み書きを判断する

拡散された投稿では、「エージェント自身がメモリの読み書きタイミングを判断し、ファイルシステムをメモリ基盤とする設計が現時点の最良実践」とも語られていた。

これは、CLAUDE.md や Skills、あるいは Claude Code のメモリ機能（会話をまたいで参照される記録ファイル）を指していると考えられる。人間があらかじめ全てを instructions として書き切るのではなく、エージェント自身が「このタイミングでメモリに書いておくべきか」「このファイルを読みに行くべきか」を判断する設計だ。ファイルシステムという素朴な基盤の上に、エージェントの自律的な判断を乗せる考え方には利点がある。複雑な専用メモリDBを持ち込むより実装コストが低く、デバッグもしやすい。

## "Dreaming"：セッションの合間に自己改善するエージェント

投稿の中で最も目を引くのが「将来の方向は "Dreaming"。エージェントが経験から自律的に学習・改善するシステム」という部分だ。

これは誇張ではなく、実在する Anthropic の機能である。Anthropic は "Code with Claude 2026" イベントで Dreaming 機能を発表した。これは、エージェントがジョブとジョブの合間に自分の過去のセッションを振り返り、そこから学習・改善するスケジュールプロセスだ（[VentureBeat](https://venturebeat.com/technology/anthropic-introduces-dreaming-a-system-that-lets-ai-agents-learn-from-their-own-mistakes)、[Let's Data Science](https://letsdatascience.com/blog/anthropic-dreaming-claude-managed-agents-self-improving-may-6)）。

リーガルAIスタートアップの Harvey がこの機能のパイロットを実施し、タスク完了率が約6倍に向上したと報告されている。エージェントが自分の失敗パターンを振り返り、次回以降のプロンプトや手順を自律的に調整することで精度が上がる、という仕組みだ。

CLAUDE.md やメモリファイルへの書き込みが「エージェントが自分の判断で今のセッションの学びを記録する」仕組みだとすれば、Dreaming は「エージェントがオフラインで過去のセッション全体を振り返り、自己改善する」仕組みだと言える。両者は連続した発想の上にある。

## 「90%のエンジニアが使っている」という数字をどう見るか

拡散された投稿には「Anthropicでは90%のエンジニアがループと"Dreaming"を使って自己改善するエージェントを構築している」という具体的な数字が含まれていた。

この記事の執筆時点で、この数字を裏付ける一次情報（Anthropic公式のブログや発表）は確認できなかった。近い文脈で確認できたのは、「Anthropicでは社内コードの90%以上をClaudeが書いている」という別種の統計だ。これはコード生成比率についての発言であり、「ループとDreamingを使っているエンジニアの割合」とは異なる主張である。

そのため、この「90%」という数字については、動画内で語られた体感的な表現である可能性を考慮し、鵜呑みにせず参考情報として扱うのが妥当だろう。一方で、ループ設計・Skills の段階的開示・Dreaming という個々の要素技術については、いずれも公式情報や複数の報道で裏付けが取れる実在の取り組みだ。

## まとめ

Anthropic 社内での Claude Code 活用法として語られた「ループ × CLAUDE.md × Skills」という構造は、それぞれ独立して裏取りできる実践に基づいている。

- **ループ設計**：人間が逐次プロンプトを打つのではなく、繰り返しの終了条件を設計する
- **CLAUDE.md + Skills**：常時ルールは CLAUDE.md、個別ワークフローは Skills の段階的開示に任せてコンテキストを圧迫しない
- **ファイルシステム基盤のメモリ**：エージェント自身が読み書きのタイミングを判断する
- **Dreaming**：セッションの合間にエージェントが自己改善する、Anthropicが実際に発表した機能

これらは個人開発者のワークフローにも応用できる考え方だ。ただし派生的に付いた具体的な統計（「90%」）のような数字は、出典を辿って裏取りする姿勢を忘れないようにしたい。
