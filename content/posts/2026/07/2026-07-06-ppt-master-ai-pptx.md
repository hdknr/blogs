---
title: "ppt-master：AIが「画像貼り付けスライド」ではなく編集可能な本物のPowerPointを生成するツール"
date: 2026-07-06
lastmod: 2026-07-06
slug: "ppt-master-ai-pptx"
draft: false
source_url: "https://github.com/hdknr/blogs/issues/1#issuecomment-4888314063"
categories: ["AI/LLM"]
tags: ["claude-code", "agent", "python", "github", "pptx"]
---

## 概要

X（Twitter）で紹介されていた [hugohe3/ppt-master](https://github.com/hugohe3/ppt-master) が、GitHub でスター 39,000 超（2026年7月時点）まで伸びています。生成AIによる資料作成ツールは数多くありますが、ppt-master が支持されているポイントは「出力が画像ではなく、PowerPoint 上でネイティブに編集できる本物の PPTX である」ことです。

紹介元の投稿（2026年6月28日時点、当時のスター数は33,093）では次のように評されていました（原文ママ）。

> 神ツール到来。PowerPoint職人の手戻り、ここからかなり減ると思う。hugohe3/ppt-masterがGitHub 33,093★、今日+589。AI生成なのに「画像貼り付けスライド」ではなく、編集できるreal PowerPointをnative shapes & animationsで吐く。強い。
> 資料生成AIで一番つらいのは、出力後に直せないこと。ppt-masterは任意documentから.pptx化し、自前template追従、speaker notesのaudio narrationまで行ける。すでにWeb版のChatgptとCluadeはこれに対応なので、CLIも対応できるのが素晴らしらしい。現場では「初稿をAI、微修正を人間」の流れが現実解なので、これのワークフロー化が今後進むのでは。

## ppt-master とは何か

ppt-master は、Claude Code や Cursor、VS Code + Copilot といった「AI IDE」の中で動作するワークフロー（スキル）です。PDF・DOCX・Web ページなどの資料をエージェントに渡すと、ローカルマシン上で実際に PowerPoint として開いて編集できる `.pptx` ファイルを生成します。

作者の Hugo He 氏（財務系の専門家で、日常的にプレゼン資料をレビュー・編集している）は、README で次のように製品ポジションを説明しています。

> **PowerPoint で開いて要素ごとに編集できないファイルは、PPT と呼ぶべきではない。**

AI プレゼン生成ツールは大きく4種類に分類でき、ppt-master は最後の「ネイティブ編集可能」カテゴリのみを狙っています。

| カテゴリ | 出力 | PowerPoint で要素ごとに編集できるか |
|---|---|:---:|
| テンプレート穴埋め型 | 固定テンプレートから生成された PPTX | △（テンプレートの範囲内のみ） |
| 画像ベース型 | スライド1枚＝1枚の画像を PPTX に格納 | ❌ 各スライドが画像 |
| HTML プレゼン型 | Web ベースのデッキ | ❌ そもそも PPTX ではない |
| **ネイティブ編集型（ppt-master）** | **本物の DrawingML 図形・テキストボックス・チャート** | ✅ どの要素もクリックして編集可能 |

## 主な機能

- **任意のドキュメントから PPTX 化**：PDF・DOCX・HTML・EPUB・Jupyter Notebook などをそのまま資料化。`.doc` や `.rtf` など古い形式は Pandoc を使えば変換可能
- **ネイティブな図形・アニメーション**：画像貼り付けではなく、DrawingML ベースの図形・テキストボックスとして出力。スライド遷移や任意のエントランスアニメーションにも対応
- **編集可能なチャート・表**：デフォルトでは SVG 由来の編集可能な図形として出力されるが、`--native-charts-and-tables` オプションを付けると PowerPoint 純正の Chart/Table オブジェクト（データを **Edit Data** で書き換え可能）としてエクスポートできる
- **スピーカーノートの音声ナレーション化**：作成したノートを読み上げ音声に変換し、パワーポイント再生時にスライドが自ら読み上げる形にできる
- **既存テンプレートへの追従**：手持ちの `.pptx` テンプレートと資料を渡すと、デザインを保ったまま新しい内容で埋め込む「テンプレート差し替え」ワークフローも用意されている

## セットアップ

必要なのは Python 3.10 以降のみです。

```bash
git clone https://github.com/hugohe3/ppt-master.git
cd ppt-master
pip install -r requirements.txt
```

Git を使わずに試したい場合は GitHub の「Code → Download ZIP」からダウンロードして展開する方法もあります。また、Claude Code のプラグインマーケットプレイス経由でスキルとしてインストールすることも可能です。

```text
# Claude Code のチャットパネルに入力
/plugin marketplace add hugohe3/ppt-master
/plugin install ppt-master@ppt-master
```

この方法ではスキルファイルのみが取得されるため、後処理スクリプトを動かすにはインストール先で改めて `pip install -r requirements.txt` を実行する必要があります。

セットアップ後、Claude Code や Cursor などのチャットパネルで次のように依頼するだけで生成が始まります。

```
Please create a PPT from projects/q3-report/sources/report.pdf
```

AI がまずデザイン仕様（テンプレート、フォーマット、ページ数など）を確認してから、コンテンツ分析・ビジュアルデザイン・SVG 生成・PPTX エクスポートまで一気通貫で実行します。

## なぜこの設計が刺さっているのか

紹介ツイートが指摘していたとおり、資料生成AIの最大の弱点は「出力後に直せないこと」でした。画像として書き出されたスライドは、文言修正一つにも作り直しが必要になります。ppt-master は次の3点を同時に満たすことを狙って設計されています。

1. **コストの透明性**：ツール自体は無料・オープンソースで、費用はAIモデルの利用分のみ
2. **データのローカル保持**：モデルとの通信を除き、パイプライン全体がローカルマシン上で完結する
3. **プラットフォームロックインの回避**：Claude Code、Cursor、VS Code Copilot など複数のIDEに対応し、Claude・GPT・Gemini・Kimi など複数のモデルに対応

現場のワークフローとしては「初稿をAIに作らせ、微修正は人間が行う」という流れが現実的であり、ppt-master はまさにその「微修正できる初稿」を渡せる点が評価されている理由と言えそうです。

## まとめ

ppt-master は、AIによる資料生成を「見た目だけ整った画像スライド」から「実務でそのまま編集し続けられる本物のPowerPoint」へ引き上げるオープンソースツールです。Claude Code などの AI IDE をすでに使っているなら、Python 環境さえあれば試すハードルは低く、資料作成の初稿フェーズを大きく効率化できる可能性があります。

## 参考リンク

- [hugohe3/ppt-master (GitHub)](https://github.com/hugohe3/ppt-master)
- [紹介元ポスト（X / connect24h氏）](https://x.com/connect24h/status/2071164027930300556)
