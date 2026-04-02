---
title: "OpenDataLoader PDF — CPUだけで毎秒100ページ、PDFをMarkdownに超高速変換するOSSツール"
date: 2026-03-18
lastmod: 2026-03-18
draft: false
source_url: "https://github.com/hdknr/blogs/issues/1#issuecomment-4082929222"
categories: ["AI/LLM"]
tags: ["python", "rag", "github", "llm", "pdf"]
---

GPUなしで毎秒100ページ以上のPDF→Markdown変換を実現するオープンソースツール「OpenDataLoader PDF」が話題になっている。Apache 2.0ライセンスで完全無料、CPUのみで動作するため、高価なGPUハードウェアは不要だ。

## OpenDataLoader PDF とは

[OpenDataLoader PDF](https://github.com/opendataloader-project/opendataloader-pdf) は、PDFドキュメントをAI活用に適した構造化データ（Markdown、JSON、HTML等）に変換するオープンソースのパーサーだ。Java で実装されており、Python・Node.js・Java から利用できる。

主な特徴:

- **超高速処理**: ローカルモードで 0.05秒/ページ（CPUのみ）、8コア以上のマシンでマルチプロセスバッチ処理すると毎秒100ページ以上
- **GPU不要**: CPUだけで高速に動作するため、導入コストが低い
- **高精度**: ベンチマークで総合精度0.90を達成し、読み順・テーブル・見出し抽出で1位
- **Apache 2.0ライセンス**: 商用利用可能な完全オープンソース

## インストール

Python パッケージは Java CLI のラッパーのため、**Java 11以上**と**Python 3.10以上**が必要だ。

```bash
# Python
pip install -U opendataloader-pdf

# Node.js
npm install @opendataloader/pdf
```

Java の場合は Maven で `opendataloader-pdf-core` を依存関係に追加する。

## 基本的な使い方

### Python でのシンプルな変換

```python
import opendataloader_pdf

opendataloader_pdf.convert(
    input_path=["file1.pdf", "file2.pdf", "folder/"],
    output_dir="output/",
    format="markdown,json"
)
```

フォルダを指定すれば一括変換も可能だ。出力形式は Markdown、JSON、HTML、プレーンテキスト、注釈付きPDFから選べる。

### Hybrid モード（複雑なPDF向け）

```python
opendataloader_pdf.convert(
    input_path=["complex-paper.pdf"],
    output_dir="output/",
    hybrid="docling-fast"
)
```

Hybrid モードでは、シンプルなページはローカルで高速処理（0.05秒/ページ）し、テーブル・スキャン画像・数式・チャートなどの複雑なページだけを Docling 等のAIベースエンジンに自動ルーティングして高精度に処理する。

## ベンチマーク比較

200件の実際のPDFを対象としたベンチマーク結果:

| エンジン | 総合精度 | 読み順 | テーブル | 見出し | 速度(秒/ページ) |
|---------|---------|--------|---------|--------|----------------|
| **OpenDataLoader [hybrid]** | **0.90** | **0.94** | **0.93** | **0.81** | 0.46 |
| OpenDataLoader (local) | 0.84 | 0.91 | 0.49 | 0.74 | **0.05** |
| Docling | 0.88 | 0.90 | 0.89 | 0.80 | 0.73 |
| Marker | 0.86 | 0.89 | 0.81 | 0.80 | 53.93 |
| MinerU | 0.83 | 0.86 | 0.87 | 0.74 | 5.96 |
| PyMuPDF4LLM | 0.73 | 0.89 | 0.40 | 0.41 | 0.09 |

ローカルモードでは Marker の約1,000倍、MinerU の約120倍の速度で処理できる。Hybrid モードにすると精度も最高水準になる。

## 主な機能

### 出力形式

- **Markdown**: LLMのコンテキストやRAGチャンキングに最適化
- **JSON**: バウンディングボックスとセマンティック型情報付きの構造化データ
- **HTML**: スタイリング付きのWeb出力
- **注釈付きPDF**: 検出された構造をビジュアルデバッグ

### 高度な機能

- **OCR対応**: `--force-ocr` フラグでスキャンPDFを処理、80以上の言語に対応
- **数式抽出**: 数式をLaTeX形式で出力（バウンディングボックス・ページ座標付き）
- **AIセーフティ**: 隠しテキスト、ページ外コンテンツ、プロンプトインジェクション攻撃を自動フィルタリング
- **Tagged PDF対応**: ネイティブPDF構造タグを保持し、著者の意図したレイアウトを維持

## LangChain との統合

RAGパイプラインで使う場合、公式の LangChain ドキュメントローダーが用意されている。

```python
from langchain_opendataloader_pdf import OpenDataLoaderPDFLoader

loader = OpenDataLoaderPDFLoader(
    file_path=["file1.pdf", "file2.pdf"],
    format="text"
)
documents = loader.load()
```

## どんな場面で使えるか

- **RAGパイプラインの前処理**: 大量のPDFドキュメントを高速にMarkdown化してベクトルDBに投入
- **社内ドキュメントのAI活用**: 既存のPDF資産をLLMが扱える形式に変換
- **論文・レポートの構造化**: 学術論文やビジネスレポートをテーブルや数式を含めて正確に変換
- **PDFアクセシビリティの自動化**: Tagged PDFの生成（Q2 2026予定）

## まとめ

OpenDataLoader PDF は「CPUだけで毎秒100ページ」という驚異的な速度と、Hybrid モードでの高精度を両立させた実用的なツールだ。Apache 2.0ライセンスで商用利用も可能なため、PDFを扱うAIプロジェクトでは有力な選択肢になるだろう。

- GitHub: [opendataloader-project/opendataloader-pdf](https://github.com/opendataloader-project/opendataloader-pdf)
- 公式サイト: [opendataloader.org](https://opendataloader.org/)
- PyPI: [opendataloader-pdf](https://pypi.org/project/opendataloader-pdf/)
