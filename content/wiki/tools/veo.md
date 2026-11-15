---
title: "Veo（Google の動画生成モデル）"
description: "プロンプトから映像と音声（セリフを含む）を同時に生成する Google の動画生成モデル。Veo 3.1 / Fast / Lite の料金、モデル ID の提供状況、LLM エージェントと組み合わせたアバター動画の作り方"
date: 2026-11-15
lastmod: 2026-11-15
aliases: ["Veo", "Veo 3.1", "Veo 3.1 Lite", "Veo 3.1 Fast", "veo-3.1-lite-generate-001", "Gemini Enterprise Agent Platform"]
related_posts:
  - "/posts/2026/11/veo-lite-fable-avatar-video/"
tags: ["Veo", "動画生成", "gemini", "AIアバター", "claude"]
---

## 概要

Veo は Google の動画生成モデル。Veo 3.1 系はプロンプトから**映像と音声（セリフを含む）を同時に**生成できるため、口の動きと声を別々に合わせる手間がない。Veo 3.1 Lite は 2026 年 3 月 31 日に発表されたファミリー最安のモデルで、量産や試作に向く。

## 詳細

### 料金（Gemini API、2026 年 11 月時点）

生成した動画 1 秒あたりの価格。改定されることがあるので使う前に [料金表](https://ai.google.dev/gemini-api/docs/pricing) を確認する。

| モデル | 720p | 1080p |
| --- | --- | --- |
| Veo 3.1 | $0.40/秒 | $0.40/秒 |
| Veo 3.1 Fast | $0.10/秒 | $0.12/秒 |
| Veo 3.1 Lite | $0.05/秒 | $0.08/秒 |

Gemini API では Veo 3.1 系の無料枠は「Not available」。24 秒を Lite の 1080p で作ると $1.92（720p なら $1.20）で、撮り直しの分だけ増える。「0 円で作った」という報告は、無料クレジットや定額サブスクの範囲で「追加の現金支出が 0」だったと読むのが妥当。

### モデル ID の提供状況

- プレビュー版 `veo-3.1-lite-generate-preview` は **2026 年 10 月 22 日に Gemini API で提供終了**。移行先として Gemini Omni Flash か Agent Platform 上の Veo が案内されている
- Google Cloud の Gemini Enterprise Agent Platform（旧 Vertex AI）では `veo-3.1-lite-generate-001` が us-central1 で提供されている（位置づけはプレビュー）。料金は Gemini API とは別の料金表

### 呼び出し方

`google-genai` SDK で `genai.Client(vertexai=True, project=..., location="us-central1")` を作り、`client.models.generate_videos()` に `GenerateVideosConfig(aspect_ratio, resolution, duration_seconds=8, output_gcs_uri)` を渡す。長時間処理なので `operation.done` までポーリングし、結果は Cloud Storage に保存される。事前に Vertex AI API の有効化と `gcloud auth application-default login` が要る。

### LLM エージェントとの分担

「Claude が台本・3D・音楽・編集、Veo が映像と声」という分担で 24 秒のアバター動画を作った報告が話題になった（手順は非公開で、以下は推定）。Claude は映像や音声を直接は生成しないので、**コードを書いて実行する**ことで担う。

| 工程 | 担当と手段 |
| --- | --- |
| 台本・カット割り・Veo 用プロンプト | LLM。24 秒なら 8 秒 × 3 カット |
| 3D | LLM が Three.js や Blender の Python スクリプトを書き、ローカルでレンダリング |
| 音楽 | LLM が MIDI 生成や Web Audio API で合成するコードを書く |
| 映像と声 | Veo |
| 編集 | ffmpeg。同じ設定のクリップは `-f concat -c copy` で再エンコードなしに連結し、BGM は `volume=0.2` と `amix=duration=first` で声に重ねる |

HeyGen のようなアバター専用サービスはこの工程を GUI でまとめて提供している。汎用エージェントと安価な動画モデルの組み合わせは、品質の安定性や商用利用の条件まで含めて比べる必要があるが、短い動画なら数ドルで作れる水準になった。

## 関連ページ

- [AI 動画広告生成ツール](/blogs/wiki/concepts/ai-video-ads/) — HeyGen などアバター専用サービスとの比較
- [Higgsfield](/blogs/wiki/tools/higgsfield/) — 複数の動画モデルを MCP で使える生成プラットフォーム
- [ショート動画のシナリオ設計と生成](/blogs/wiki/guides/short-video-scenario-generation/) — LLM でカット割りとプロンプトを量産する手順
- [Claude Code](/blogs/wiki/tools/claude-code/) — コードを書いて実行するエージェント環境

## ソース記事

- [Veo 3.1 Lite の料金でアバター動画は 0 円で作れるか — Claude Fable 5.2 との分担を検証](/blogs/posts/2026/11/veo-lite-fable-avatar-video/) — 2026-11-15
