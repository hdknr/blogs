---
title: "Google Gemini Embedding 2：テキスト・画像・動画・音声を統一ベクトル空間に埋め込むマルチモーダル埋め込みモデル"
date: 2026-03-11
lastmod: 2026-03-11
draft: false
source_url: "https://github.com/hdknr/blogs/issues/1#issuecomment-4042051334"
categories: ["AI/LLM"]
tags: ["gemini", "rag", "llm", "python"]
---

Google が 2026年3月に公開した **Gemini Embedding 2** は、テキスト・画像・動画・音声・ドキュメントを同一のベクトル空間に埋め込める、初のネイティブマルチモーダル埋め込みモデルだ。RAG パイプラインやマルチモーダル検索を構築する開発者にとって注目すべきモデルとなっている。

## 主な特徴

### ネイティブマルチモーダル対応

従来の埋め込みモデルはテキスト専用か、別モデルで画像を処理する必要があった。Gemini Embedding 2 は全モダリティを **3072次元の統一ベクトル空間** に直接埋め込む。これにより、テキストで検索して関連する画像や動画を取得するといったクロスモーダル検索が自然に実現できる。

対応モダリティと制限:

| モダリティ | 制限 |
|------------|------|
| テキスト | 最大 8,192 トークン |
| 画像 | 1リクエストあたり最大 6枚（PNG, JPEG） |
| 動画 | 最大 120秒（MP4, MOV） |
| 音声 | ネイティブ対応（テキスト変換不要） |

インターリーブ入力にも対応しており、1つのリクエストに画像とテキストを混在させて渡すことができる。

### Matryoshka 表現学習（MRL）

Matryoshka Representation Learning（マトリョーシカ表現学習）により、重要な意味情報がベクトルの先頭次元に集約される設計になっている。デフォルトの 3,072次元から 1,536 や 768次元に切り詰めても、検索品質の大部分を維持できる。

Google の推奨次元数:

- **3,072次元**：最高品質
- **1,536次元**：高品質（コスト削減向け）
- **768次元**：バランスの良い推奨値

768次元に切り詰めた場合でも、同サイズの固定次元モデルを上回る性能を発揮するとされている。

### 多言語対応と性能

- 100以上の言語をサポート
- MTEB 多言語リーダーボードで 69.9 を記録しトップランク
- MTEB コード検索でも 84.0 と高スコア

## 料金

| プラン | 料金 |
|--------|------|
| リアルタイム API | $0.20 / 100万トークン |
| バッチ API | $0.10 / 100万トークン（50% OFF） |

OpenAI の text-embedding-3-small（$0.02/100万トークン）と比較すると高価だが、マルチモーダル対応を単一モデルで実現している点が差別化要因となる。

## API の使い方

Gemini API と Vertex AI の両方で利用可能（パブリックプレビュー）。

```python
from google import genai

client = genai.Client()

result = client.models.embed_content(
    model="gemini-embedding-2-preview",
    contents="検索したいテキスト",
    config={
        "output_dimensionality": 768,
    },
)

print(result.embeddings[0].values[:5])
```

画像を含むマルチモーダル入力の場合:

```python
from google import genai
from google.genai import types

client = genai.Client()

image = types.Part.from_uri(
    file_uri="gs://your-bucket/image.jpg",
    mime_type="image/jpeg",
)

result = client.models.embed_content(
    model="gemini-embedding-2-preview",
    contents=[image, "この画像の説明"],
)
```

## ユースケース

- **マルチモーダル RAG**：テキストだけでなく画像や動画も含めたナレッジベースの構築と検索
- **クロスモーダル検索**：テキストクエリで関連する画像・動画を検索、またはその逆
- **多言語ドキュメント検索**：100以上の言語を跨いだセマンティック検索
- **音声コンテンツの検索**：ポッドキャストや会議録音を文字起こしなしで直接埋め込み・検索
- **コード検索**：自然言語の説明からコードスニペットを検索

## まとめ

Gemini Embedding 2 は、複数のモダリティを統一的に扱えるという点で、埋め込みモデルの新たなスタンダードとなる可能性がある。Matryoshka 表現学習による柔軟な次元調整も実用面で大きなメリットだ。RAG やセマンティック検索の設計において、マルチモーダル対応が選択肢に入るようになったことは大きな進展といえる。
