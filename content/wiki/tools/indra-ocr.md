---
title: "Indra OCR"
description: "Datalab が公開した CPU だけで動く軽量 OCR。ONNX Runtime で推論し、PDF や画像を Markdown・テキスト・座標付き JSON に変換する。日本語・縦書きにも対応するが、モデルの重みは修正版 OpenRAIL-M で商用利用に条件がある"
date: 2026-10-30
lastmod: 2026-10-30
aliases: ["indra-ocr", "Indra", "Datalab OCR", "CPU OCR", "軽量 OCR"]
related_posts:
  - "/posts/2026/10/indra-ocr-cpu-ocr/"
tags: ["ocr", "pdf", "python", "RAG", "CPU推論"]
---

## 概要

Indra OCR は、Datalab（[datalab-to](https://github.com/datalab-to)）が 2026 年 10 月に 1.1 を公開した OCR ツール。推論は ONNX Runtime で行い、PyTorch にも GPU にも依存しない。主認識器は公称 100 万（実際は約 125 万）パラメータ、既定モデル全体でも約 730 万パラメータと、数十億パラメータ級の VLM 系 OCR より桁違いに小さい。

位置づけは「**きれいな印刷物を CPU で速く読む**」ことに特化した OCR。LLM に文書を読ませる前のテキスト化（前処理）に向く。

## 詳細

### 基本情報

| 項目 | 内容 |
|---|---|
| 実行環境 | Python 3.10 以上。Linux（x86_64 / aarch64）、macOS（Apple silicon） |
| 依存 | ONNX Runtime、OpenCV、pypdfium2 |
| モデル | 約 76 MB。初回実行時に Hugging Face から取得 |
| 出力 | Markdown / テキスト / JSON（行・ブロックの座標と信頼度つき） |

### 処理の流れ

既定の `--mode auto` は、デジタル PDF のテキスト層がチェックに合格すればそれを読み、合格しない部分だけ OCR する。OCR が本当に必要なのは主にスキャン画像。

OCR では向き・傾きを補正してレイアウトと行を検出し、**行分類器**が文字種ごとに 4 つの認識器へ振り分ける。

- `rec.onnx` — ラテン文字・キリル文字・ギリシャ文字・ラテン文字の手書き
- `rec_cjk.onnx` — 中国語・日本語・韓国語
- `rec_rtl.onnx` — アラビア語・ヘブライ語など右から左に書く文字
- `rec_world.onnx` — インド系文字・タイ語・クメール語など

分類に自信がない行は主認識器でも読み、信頼度の高い方を採る。

### 使い方

`pip install indra-ocr` で CLI が入る。主なオプションは `--format [md|text|json]`、`--mode [auto|ocr|text]`、`--cores N`、`--dpi N`（既定 200）、数式を LaTeX で出す `--math`。`indra-ocr-viewer` はローカルのブラウザで検出した行・ブロック・読み順を元ページに重ねて確認できるビューアで、ファイルは手元から出ない。

Python からは `indra_ocr.load()` でコンバーターを作り `convert()` でページごとに結果を得る。大量処理には全コアにワーカーを立てる `convert_many` があり、macOS と Windows では `if __name__ == "__main__":` ガードが要る。結果の `Page` には Markdown のほか、行の座標（`lines`）、レイアウトブロック（`blocks`）、縦書きかどうか（`vertical`）、工程ごとの処理時間が入る。

### 性能（開発元のベンチマーク）

Datalab 自身の OmniParseBench（2,937 ページ）での数字なので、自分の文書で試してから判断するのが前提。

- x86・4 vCPU で 1 ページの中央値は約 210 ms。PaddleOCR PP-StructureV3 は約 41 秒、Tesseract 5 は約 5.5 秒
- 総合スコアは Indra 66.7（`--math` で 71.4）に対し PP-StructureV3 58.4。ただし `--math` なしのテキスト単体のスコアは PP-StructureV3 が上
- 「毎秒 44 ページ」は AMD EPYC 32 コアでの値。4 コアでは毎秒約 6 ページ

### 日本語と苦手な文書

日本語は `rec_cjk.onnx` が受け持つ。縦書きページは 90 度回転させて縦の 1 列を 1 行として読むが、横書きより精度が落ち、新聞のように段をまたぐ紙面では記事の順序が崩れることがある。日本語のテストは 19 件しかなく、スコアは参考値にとどまる。相性がよいのは請求書や見積書のような横書きの帳票。

README が苦手と明記するのは、結合セルや罫線のない**複雑な表**、**手書き**（スコア 25.2）、**劣化したスキャン**（29.5）、対象外の文字種（チベット文字など）。こうした文書向けに、Datalab は高精度モデル Chandra のマネージドサービスを案内している。

### ライセンス：Apache 2.0 なのはコードだけ

**モデルの重みは修正版 OpenRAIL-M**。無償で使えるのは研究目的・個人利用・調達額または売上が 2,000 万ドル未満のスタートアップに限られ、Datalab の API と競合する用途には使えない。2,000 万ドルの判定は本人だけでなく**雇用主や関連組織も含む**ので、業務で導入する前に Hugging Face 上の LICENSE を必ず読む。

### LLM の前処理として

PDF や画像をそのままマルチモーダル LLM に渡すと画像トークンのコストがかかる。CPU の OCR で先に Markdown にしておけば、次の利点がある。

- 入力トークンが小さくなる
- [RAG](/blogs/wiki/concepts/rag/) や全文検索の取り込みにそのまま使える
- OCR の段階では文書を外部に送らずに済む
- JSON の `bbox` で、抽出した値が元ページのどこにあったかを示せる

一方、表崩れや手書きの弱さはそのまま LLM の入力品質に響く。少量で試し、ビューアで検出結果を目視してからパイプラインに組み込む。

## 関連ページ

- [RAG](/blogs/wiki/concepts/rag/) — OCR で得た Markdown の主な取り込み先
- [ローカルLLM比較（2026年春）](/blogs/wiki/concepts/local-llm-comparison/) — OCR を含むマルチモーダル対応の比較
- [AI-ready データ設計](/blogs/wiki/concepts/ai-ready-data/) — LLM に渡すデータを整える考え方

## ソース記事

- [Indra OCR：CPU だけで動く 100 万パラメータの OCR、日本語・縦書きにも対応](/blogs/posts/2026/10/indra-ocr-cpu-ocr/) — 2026-10-30
