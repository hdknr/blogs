---
title: "Claude Codeをメインのデザインツールに：Tailwind CSSデザイナーSteve Schogerの1時間解説動画"
date: 2026-03-23
lastmod: 2026-03-23
draft: false
source_url: "https://github.com/hdknr/blogs/issues/1#issuecomment-4113577162"
categories: ["AI/LLM"]
tags: ["claude-code", "react", "figma"]
---

Tailwind CSSチームのデザイナー Steve Schoger が、「Claude Codeをメインのデザインツールにした」という1時間の解説動画を公開した。Figmaを使わず、Claude Codeだけで金融アプリのランディングページをゼロから構築する過程を全公開している。

## Steve Schoger とは

Steve Schoger は Tailwind Labs のデザイナーで、Adam Wathan と共に「[Refactoring UI](https://refactoringui.com/)」の著者としても知られている。開発者向けにデザインスキルを体系的に教える活動で広く認知されており、X（Twitter）でのデザインTipsや YouTube でのUI改善動画でも人気が高い。

## 動画の内容

動画では、約50回の対話を通じて初期出力をプロ級の品質に仕上げていく過程が公開されている。

注目すべきは、Schoger 本人が「コマンドラインはディレクトリ移動と Claude 起動しかできない」と語っている点だ。プログラミングの深い知識がなくても、Claude Code との対話だけでプロ品質のLPを作り上げている。

### ワークフロー

- **左画面**: ブラウザ（localhost 表示）
- **右画面**: Claude Code のターミナル

これだけのシンプルな構成で、Figma は一切使っていない。

### 技術スタック

- **Vite** — ビルドツール
- **Tailwind CSS** — ユーティリティファーストCSS
- **React** — UIライブラリ

## デザイナーがCLIに移行する時代

「デザイナーがCLIに移行する」というのは、一見ありえない話に思える。しかし、この動画を見ると、AIコーディングツールがデザインワークフローを根本的に変えつつあることが実感できる。

従来のデザインワークフローでは、Figma などのビジュアルツールでモックアップを作成し、それをエンジニアが実装するという流れが一般的だった。しかし Claude Code を使えば、デザイナーが自然言語で指示を出すだけで、直接コードとして実装されたUIを確認・修正できる。

## ui.sh — デザインスキルをAIに組み込むツール

Schoger と Adam Wathan は [ui.sh](https://ui.sh) というツールも開発している。これは Claude Code や Cursor などのAIコーディングエージェントに、プロレベルのデザイン基準を適用させるスキルツールキットだ。ターミナルを「デザインエンジニア」に変えるというコンセプトで、AIが生成するUIの品質を大幅に向上させることを目指している。

## まとめ

Steve Schoger の動画は、AIツールがデザインの民主化をさらに推し進めている現状を示している。コマンドラインしか使えないと自称するデザイナーが、テンプレート感ゼロのプロ品質LPを作れるという事実は、Web制作のワークフローが大きな転換期にあることを物語っている。

### 参考リンク

- [Steve Schoger の動画ポスト（X）](https://x.com/steveschoger/status/2035077141050622173)
- [すぐる氏による解説スレッド（X）](https://x.com/SuguruKun_ai/status/2035771262216400954)
- [Refactoring UI](https://refactoringui.com/)
- [ui.sh](https://ui.sh)
