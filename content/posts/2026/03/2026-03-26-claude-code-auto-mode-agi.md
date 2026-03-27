---
title: "Claude Code の Auto Mode から見える AGI への道筋"
date: 2026-03-26
lastmod: 2026-03-26
draft: false
description: "Claude Code の auto mode はパーミッションの自動判断に留まらず、Claude 実行自体の自動化、つまり AGI への一歩と捉えられる。開発ツールの自律性がどこまで進むかを考察する。"
source_url: "https://github.com/hdknr/blogs/issues/1#issuecomment-4136299255"
categories: ["AI/LLM"]
tags: ["claude-code", "claude", "agent", "anthropic", "llm"]
---

AGI（Artificial General Intelligence、汎用人工知能）とは、特定のタスクに限定されず、人間のように幅広い知的作業をこなせる AI を指す概念だ。現在の AI は特定領域で高い能力を発揮するが、未知の領域への汎用的な対応力では人間に及ばないとされている。

Claude Code に auto mode が導入された。パーミッションの承認を Claude 自身が判断するこの機能について、「次に来るのは Claude 実行自体の auto mode、つまり AGI だ」という指摘が注目を集めている。開発ツールの自律性の進化と、その先にある可能性を考える。

## Auto Mode の本質

2026年3月、Anthropic は Claude Code に auto mode を導入した。公式 X アカウントの発表によると:

> New in Claude Code: auto mode. Instead of approving every file write and bash command, or skipping permissions entirely, auto mode lets Claude make permission decisions on your behalf. Safeguards check each action before it runs.

従来の Claude Code では、ファイル書き込みやシェルコマンドの実行のたびにユーザーの承認が必要だった。auto mode はこの判断を Claude 自身に委ねるもので、セーフガードが各操作を実行前にチェックする仕組みだ。

## 「Claude 実行自体の Auto Mode」という視点

この発表に対して、Yutaka Kondo 氏（[@youtalk](https://x.com/youtalk)、自動運転ソフトウェア企業 TIER IV）は以下のようにコメントした:

> この開発スピード感だと、パーミッションの auto mode だけでなく、claude 実行自体の auto mode（つまり人は claude を自分で実行しなくなる）も今年中に来るだろう。それはもう AGI だ。

この指摘は、auto mode を単なる利便性向上ではなく、AI の自律性が段階的に拡大していく流れの一部として捉えている。

## 自律性の段階

開発ツールにおける AI の自律性は、段階的に進んできた:

### レベル 1: コード補完（2020年〜）

GitHub Copilot に代表される、カーソル位置のコードを補完する段階。人間がすべての操作を主導する。

### レベル 2: タスク実行（2024年〜）

Claude Code や Cursor のように、自然言語の指示からコードの読み書き、コマンド実行まで行う段階。ただし、各操作にユーザーの承認が必要。

### レベル 3: 自律的タスク実行 — auto mode（2026年〜）

パーミッション判断を AI に委ね、長時間の連続作業を人間の介入なしで実行する段階。現在の auto mode はここに位置する。

### レベル 4: 自律的な実行開始（未到達）

AI が自ら判断して開発タスクを開始・実行する段階。Kondo 氏が「Claude 実行自体の auto mode」と表現したのはこのレベルだ。CI/CD パイプラインや Issue のトリアージから自動的に開発を開始するような世界観になる。

## 既に見え始めている兆候

レベル 4 への兆候は既にいくつか現れている:

- **Claude Code のスケジュール実行**: cron ベースでリモートエージェントを定期実行する機能が実装されている
- **GitHub Actions との統合**: Issue や PR のイベントをトリガーに Claude Code を起動するワークフローが普及しつつある
- **Anthropic の Agent SDK**: プログラムから Claude をエージェントとして起動し、ツール実行を委任する SDK が公開されている

これらを組み合わせれば、「Issue が作成されたら自動で調査し、修正 PR を出す」というワークフローは技術的に実現可能な段階にある。

## AGI と呼べるのか

Kondo 氏は「それはもう AGI だ」と述べているが、これは厳密な AGI の定義（汎用的な知的能力）とは異なる用法だ。ここでの AGI は「開発者が介入しなくても開発が進む状態」を指している。

しかし、この感覚的な表現は的を射ている部分がある。開発という知的作業において、タスクの理解・計画・実行・検証のサイクルを AI が自律的に回せるようになれば、それは「この領域において汎用的に機能する知能」と言えるかもしれない。

## 現実的な課題

自律的な実行開始に向けては、技術的な課題よりも信頼性と安全性の課題が大きい:

- **判断の正確性**: 誤った判断でデプロイやデータ変更を行うリスク
- **スコープの制御**: AI がタスクの範囲を適切に判断できるか
- **責任の所在**: 自律的に行われた変更に対する責任の帰属
- **セキュリティ**: 外部からの操作（プロンプトインジェクション等）への耐性

auto mode でさえ、現時点ではリサーチプレビューとして慎重に導入されている。完全な自律実行に至るまでには、これらの課題に対する段階的な解決が必要だろう。

## まとめ

Claude Code の auto mode は、パーミッション承認の自動化という一見小さな機能に見える。しかし、開発ツールの自律性という軸で見ると、コード補完からタスク実行、そして自律的な実行開始へと向かう流れの中の重要な一歩だ。

「Claude 実行自体の auto mode」がいつ実現するかはわからない。だが、スケジュール実行や Agent SDK など要素技術は揃いつつある。開発者にとっては、AI に委ねる範囲を段階的に広げながら、その信頼性を見極めていく時期と言える。
