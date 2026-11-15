---
title: "Veo 3.1 Lite の料金でアバター動画は 0 円で作れるか — Claude Fable 5.2 との分担を検証"
date: 2026-11-15
lastmod: 2026-11-15
slug: "veo-lite-fable-avatar-video"
draft: false
source_url: "https://github.com/hdknr/blogs/issues/694#issuecomment-6888111846"
categories: ["AI/LLM"]
tags: ["Veo", "claude", "動画生成", "AIアバター", "gemini"]
---

## はじめに

2026 年 11 月、X で「HeyGen や Higgsfield はもう要らないかもしれない」という投稿が話題になりました。発端は、韓国のデータアナリスト UCHAL（[@tm_uchal](https://x.com/tm_uchal/status/2120573380768518390)）さんが 11 月 12 日（日本時間）に公開した投稿です。**Claude Fable 5.2** と **Veo 3.1 Lite** だけで 24 秒の AI アバター動画を作ったと報告しています。投稿のポイントは次の 2 点です。

- 自分がやったのは「1 行の依頼」だけ
- コストは 0 ウォン（以下、日本の読者に合わせて「0 円」と表記します）

11 月 14 日には、中国語圏のユーザー Andy L（[@AndyL5cc](https://x.com/AndyL5cc/status/2121553136615596139)）さんがこの動画を紹介しました。「プラットフォームの表示がなければ AI だと気づかない」と評し、さらに拡散しています。

動画の出来は確かに自然です。ただし元の投稿が明かしているのは、次の分担だけです。

| 担当 | 作業 |
|---|---|
| Claude Fable 5.2 | 台本、編集、3D、音楽 |
| Veo 3.1 Lite | 映像、声 |

この記事では、まずこの分担を実際の作業に分解し、「0 円」という主張が Veo 3.1 Lite の公開価格と整合するかを確かめます。さらに、2026 年 11 月時点で使えるモデル ID と、Python と ffmpeg で 24 秒の動画を組み立てる手順も紹介します。

**先に結論**: 公開価格どおりに API を使うと、1080p で 24 秒なら $1.92 かかります。Gemini API に Veo の無料枠はなく、プレビュー版のモデル ID はすでに提供を終えています。

## Claude Fable 5.2 と Veo 3.1 Lite の分担を作業に分解する

Claude は文章とコードを出力するモデルで、映像や音声のファイルを直接は生成しません。それでも「3D」「音楽」「編集」を担当できるのは、**コードを書き、エージェント環境でそれを実行する**からだと考えるのが自然です。元の投稿は手順を明かしていないので、以下は推定です。

![人間の 1 行の依頼を Claude Fable 5.2 が受け取り、台本・Veo 用プロンプト・3D と BGM を作るコード・ffmpeg による編集指示に分解する。プロンプトは Veo 3.1 Lite に渡って声つきの人物映像になり、コードはローカルで 3D レンダリングと BGM の書き出しを行う。最後に ffmpeg で連結・ミックスして 24 秒の 1080p 動画になる流れを示した図](/blogs/images/veo-lite-fable-avatar-pipeline.png)

- **台本・カット割り・プロンプト**: LLM が最も得意とする部分です。24 秒の動画なら、8 秒のカットを 3 本つなぐ構成が考えられます。
- **3D**: Three.js や Blender の Python スクリプトを Claude が書き、ローカルでレンダリングすれば、背景やロゴのアニメーションを作れます。
- **音楽**: 同じくコードで作れます。MIDI を生成して音源で書き出す方法や、ブラウザの Web Audio API で合成する方法があります。
- **映像と声**: ここが Veo 3.1 Lite の担当です。Veo 3.1 系はプロンプトから映像と音声（セリフを含む）を同時に生成できるため、口の動きと声を別々に合わせる手間がありません。
- **編集**: クリップの連結と BGM のミックスは ffmpeg で十分です。Claude がコマンドを組み立てて実行します。

HeyGen のようなアバター専用サービスは、この工程をまとめて GUI で提供しています。「要らないかもしれない」という主張は、**汎用のエージェントと汎用の動画モデルを組み合わせれば、専用サービスの代わりになり得る**という意味だと読めます。

## Veo 3.1 Lite とは

Veo 3.1 Lite は、Google が 2026 年 3 月 31 日に[発表](https://blog.google/innovation-and-ai/technology/ai/veo-3-1-lite/)した、Veo 3.1 ファミリーで最も安価な動画生成モデルです。[Gemini API の料金表](https://ai.google.dev/gemini-api/docs/pricing)では、生成した動画 1 秒あたりの価格が次のように設定されています（2026 年 11 月時点の値。価格は改定されることがあるので、使う前に料金表を確認してください）。

| モデル | 720p | 1080p |
|---|---|---|
| Veo 3.1 | $0.40/秒 | $0.40/秒 |
| Veo 3.1 Fast | $0.10/秒 | $0.12/秒 |
| Veo 3.1 Lite | $0.05/秒 | $0.08/秒 |

Lite は 720p で Fast の半額、1080p で約 3 分の 2 の価格です。量産や試作に向いた位置づけといえます。

## Veo 3.1 Lite の料金で「0 円」は成り立つか

結論から言うと、**公開価格どおりに API を使ったのなら 0 円にはなりません**。

- Gemini API の料金表では、Veo 3.1 系のモデルはいずれも無料枠が「Not available」です。
- 24 秒をすべて Veo 3.1 Lite で 1080p 生成すると、24 秒 × $0.08 = **$1.92**（720p なら $1.20）です。撮り直しをすれば、その分だけ増えます。
- Claude Fable 5.2 の利用料も別にかかります。

それでも本人が 0 円と感じた理由としては、次のような可能性が考えられます（投稿では説明されていません）。

- Google Cloud の新規利用者向け無料クレジットなど、**手元のクレジット**で支払った
- Claude も Google の AI も**定額サブスクリプションの範囲内**で使ったため、追加の支払いが発生しなかった

いずれにしても「追加の現金支出が 0」であって、「計算資源が無料」という意味ではない点に注意が必要です。とはいえ、24 秒で約 2 ドルという水準は、専用サービスの月額課金と比べても手頃だと言えます。

## Veo 3.1 Lite のモデル ID（プレビュー版は提供終了）

自分で試す場合は、モデル ID に注意してください。Gemini API の[モデルページ](https://ai.google.dev/gemini-api/docs/models/veo-3.1-lite-generate-preview)によると、プレビュー版の `veo-3.1-lite-generate-preview` は **2026 年 10 月 22 日に Gemini API で提供終了**しています。移行先としては、Gemini Omni Flash か、Agent Platform 上の Veo が案内されています。

Google Cloud の [Gemini Enterprise Agent Platform](https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/veo/3-1-generate)（旧 Vertex AI。以下 Agent Platform）では、`veo-3.1-lite-generate-001` が us-central1 で提供されています。ただし、こちらも位置づけはプレビュー（2026 年 4 月 2 日リリース）です。また、Agent Platform の料金は Gemini API とは別の料金表で定められているので、試す前に確認してください。

元の投稿は Gemini API での提供終了後の 11 月 12 日に公開されています。そのため、Agent Platform の経路か、Veo を組み込んだ別のサービスを使った可能性があります。

## 試してみる: Veo 3.1 Lite で 24 秒の動画を組み立てる

### 1. 準備

Python の SDK をインストールし、Google Cloud の認証を済ませます。Google Cloud のプロジェクトで Vertex AI API（Agent Platform の API）を有効にしておく必要があります。

```bash
pip install google-genai
gcloud auth application-default login
```

### 2. Python で 8 秒のクリップを生成する

`google-genai` SDK で Agent Platform 経由のクライアントを作り、`veo-3.1-lite-generate-001` を呼ぶ例です。プロジェクト ID と Cloud Storage のバケットは自分のものに置き換えてください。

```python
import time

from google import genai
from google.genai import types

client = genai.Client(vertexai=True, project="your-project-id", location="us-central1")

prompt = (
    "A friendly presenter in her 30s stands in a bright studio, "
    "looks into the camera and says in Japanese: "
    "'こんにちは。今日は新しいサービスを紹介します。' "
    "Natural gestures, soft key light, 35mm lens."
)

operation = client.models.generate_videos(
    model="veo-3.1-lite-generate-001",
    prompt=prompt,
    config=types.GenerateVideosConfig(
        aspect_ratio="16:9",
        resolution="1080p",
        duration_seconds=8,
        output_gcs_uri="gs://your-bucket/veo-output/",
    ),
)

# 動画生成は長時間処理なので、完了までポーリングする
while not operation.done:
    time.sleep(15)
    operation = client.operations.get(operation)

# 生成された動画の保存先（gs://your-bucket/veo-output/... の URI）が表示される
print(operation.result.generated_videos[0].video.uri)
```

台本を 8 秒ずつのセリフに分けてこれを 3 回呼べば、24 秒分の素材がそろいます。この「分割してプロンプトを書く」部分を Claude に任せるのが、元の投稿の使い方だと考えられます。

### 3. ダウンロードして連結する

生成した動画は Cloud Storage に保存されるので、手元にダウンロードし、`clip1.mp4` から `clip3.mp4` に名前を付け替えます。

```bash
gcloud storage cp "gs://your-bucket/veo-output/*" .
```

次の内容で `list.txt` を作成します。

```text
file 'clip1.mp4'
file 'clip2.mp4'
file 'clip3.mp4'
```

同じモデル・同じ設定で生成したクリップなら、再エンコードせずにつなげられます。

```bash
ffmpeg -f concat -safe 0 -i list.txt -c copy joined.mp4
```

### 4. BGM を重ねる

Claude に作らせた BGM を `bgm.wav` として書き出しておき、Veo が生成した声に重ねます。

```bash
ffmpeg -i joined.mp4 -i bgm.wav \
  -filter_complex "[1:a]volume=0.2[bgm];[0:a][bgm]amix=inputs=2:duration=first[a]" \
  -map 0:v -map "[a]" -c:v copy -c:a aac final.mp4
```

`volume=0.2` で BGM を小さくしておかないと、セリフが聞き取りにくくなります。`duration=first` を付けているので、BGM が長くても動画の長さで切れます。

## まとめ

- 話題の動画は「Claude Fable 5.2 が台本・コード・編集を担当し、Veo 3.1 Lite が声つきの映像を生成する」という分担で作られています。手順の詳細は公開されていません。
- Veo 3.1 Lite は 1080p で $0.08/秒、24 秒なら約 2 ドルです。Gemini API には無料枠がないため、「0 円」は手持ちのクレジットや定額プランの範囲で使ったという意味だと考えるのが妥当です。
- プレビュー版のモデル ID は Gemini API で 2026 年 10 月 22 日に提供終了しています。試すなら Agent Platform の `veo-3.1-lite-generate-001`（こちらもプレビュー）を確認してください。

専用のアバターサービスが不要になるかどうかは、品質の安定性や商用利用の条件まで含めて判断する必要があります。それでも、汎用 LLM と安価な動画モデルを組み合わせれば、1 行の依頼から短い動画まで現実的な価格で作れるようになりました。この変化は押さえておく価値があります。
