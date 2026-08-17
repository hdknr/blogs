---
title: "Claude Code × Higgsfield MCP でCM制作が一撃完結 — 絵コンテから動画まで6シーンを自動生成する新時代の広告制作フロー"
date: 2026-05-20
lastmod: 2026-05-20
slug: "claude-code-higgsfield-mcp-cm-production"
draft: false
source_url: "https://github.com/hdknr/blogs/issues/1#issuecomment-4504066228"
categories: ["AI/LLM"]
tags: ["claude-code", "mcp", "Higgsfield", "動画生成", "Seedance"]
---

## はじめに

「演出を言語化するだけで6シーンのCMがそのまま動画になる」——そんな未来がもう始まっている。

2026年5月18日、動画生成AIプラットフォーム **Higgsfield AI** が公式ツイートで発表した一本のデモ動画が静かに話題を呼んでいる。Claude Code と Higgsfield MCP を組み合わせた新しいモーションデザインのワークフローで、Higgsfield は「**Motion Design, solved.**」と宣言した。

Pinterest から参考映像を収集し、6シーン分の絵コンテを自動生成して、そのまま動画化まで完結する——しかも全部 Claude Code のチャットから操作できる。広告制作者にとって長年の「制作コスト」と「スピード」のトレードオフを、一気に解消するかもしれないフローだ。

## Higgsfield MCP とは

**Higgsfield AI** はサンフランシスコ発のクリエイター向けAIプラットフォームだ。2026年4月30日に公式MCPサーバーを公開し、30以上の画像・動画生成モデルを単一のエンドポイントから呼び出せる仕組みを提供している。

対応モデルの主なラインナップ：

- **Sora 2** (OpenAI) ※2026年9月にAPI廃止予定
- **Veo 3.1** (Google)
- **Kling 3.0** (快手)
- **Seedance 2.0** (ByteDance)
- **GPT Image 2** (OpenAI) — 絵コンテ生成に使用
- **Wan 2.6**、**MiniMax Hailuo**
- Higgsfield 独自モデル: Soul、Soul Cinema、Cinema Studio

Claude Code からこれら全モデルに直接アクセスでき、プロンプトからカメラ移動・レンズ選択・被写界深度・アスペクト比・フレームレートまで自然言語で指定できる。

## 3ステップで完結するモーションデザインフロー

Higgsfield の[公式ツイートのデモ](https://x.com/higgsfield/status/2056427804531773598)が示したワークフローは以下の3ステップだ：

1. **Pinterest API で参考映像を収集**  
   Claude Code が Pinterest の API を呼び出し、ブランドや演出の参考になる映像素材を自動収集する。

2. **GPT Image 2 で6シーン分の絵コンテを生成**  
   Higgsfield MCP 経由で GPT Image 2 を呼び出し、各シーンの構図・テキストを含む絵コンテを生成する。

3. **Seedance 2.0 で絵コンテを動画化**  
   生成した絵コンテをそのまま Higgsfield MCP 経由で Seedance 2.0 へ投入し、動画として出力する。

このフロー全体が **Claude Code の1つのチャットセッション**から完結する点が革新的だ。従来であれば「企画 → 参考収集 → 絵コンテ → 撮影/動画制作 → 編集」と複数のツールをまたいでいたプロセスが、MCPという統一インターフェースによって Claude に指揮させる形にまとまった。

## セットアップ方法

Claude Code への Higgsfield MCP の追加は1コマンドで完了する：

```bash
claude mcp add --transport http --scope user higgsfield https://mcp.higgsfield.ai/mcp
```

初回実行時にブラウザが開き、Higgsfield アカウントで OAuth 認証を行う。完了後は以下で接続を確認できる：

```bash
claude mcp list
# または Claude Code 内で /mcp コマンド
```

設定が完了すれば、あとは Claude Code のチャットで「Pinterest から〇〇のテイストの参考を集めて、6シーン分の絵コンテと動画を作って」と指示するだけだ。

## Seedance 2.0 について

このフローの動画生成エンジンとして使われている **Seedance 2.0** は、ByteDance が2026年2月にリリースしたマルチモーダル動画生成モデルだ。

主な仕様：

- 最大2K解像度での動画生成
- **ネイティブ同期オーディオ**（セリフ・効果音・環境音・BGMを1回の生成で同時出力）
- 4〜15秒の動画を生成
- 最大9枚の画像・3本の動画・3つの音声ファイルを入力として参照可能
- キャラクターの視覚的一貫性を保ったマルチシーン生成

Higgsfield のプラットフォーム上では `higgsfield.ai/seedance/2.0` からアクセスでき、MCP 経由でも呼び出せる。

## Higgsfield と Adobe Firefly — 対応AIの違い

「複数の生成AIを単一インターフェースから呼び出す」という発想自体は、Higgsfield の専売特許ではない。Adobe も **Firefly** を「全部入りのクリエイティブAIスタジオ」として再設計し、自社モデルに加えて多数のパートナーモデルを束ねている。両者は同じ「アグリゲーター型」でありながら、**取り込むモデルの系統がほぼ正反対**だ。

### 動画生成モデル

| モデル | Higgsfield | Adobe Firefly |
|------|:---:|:---:|
| Sora 2 / 2 Pro (OpenAI) | ✅ | ✅ |
| Google Veo 3.1 | ✅ | ✅ |
| Kling 3.0 (快手) | ✅ | ❌ |
| Seedance 2.0 (ByteDance) | ✅ | ❌ |
| Wan 2.7 (Alibaba) | ✅ | ❌ |
| MiniMax Hailuo 02 | ✅ | ❌ |
| Runway Gen-4 / Aleph | ❌ | ✅ |
| Luma Ray2 / Ray3 | ❌ | ✅ |
| Pika 2.2 | ❌ | ✅ |
| Moonvalley Marey | ❌ | ✅ |

### 画像生成モデル

| モデル | Higgsfield | Adobe Firefly |
|------|:---:|:---:|
| Nano Banana / Gemini Image (Google) | ✅ | ✅ |
| GPT Image (OpenAI) | ✅ | ✅ |
| FLUX (Black Forest Labs) | ✅ | ✅ |
| Seedream 4.0 / 5.0 (ByteDance) | ✅ | ❌ |
| Ideogram 3.0 | ❌ | ✅ |
| Adobe Firefly Image（自社） | ❌ | ✅ |

### 思想の違い

- **Higgsfield** は Kling・Seedance・Wan・MiniMax・Seedream といった**中国系の最先端モデルを積極的に取り込む**。さらに本記事のように MCP / CLI でエージェント（Claude Code）から叩ける点が決定的で、「絵コンテ→動画を一撃生成」のような**自動化・パイプライン志向**が強い。
- **Adobe Firefly** は Runway・Luma・Pika・Ideogram など**欧米系を網羅**し、中国系モデルは扱わない。最大の武器は**自社 Firefly モデルの商用利用安全性**（学習データがクリーン）と、Photoshop / Premiere Pro を含む Creative Cloud への統合、タイムライン編集との地続きさだ。

つまり「**中国系最新モデル × エージェント自動化**」を取りに行くなら Higgsfield、「**欧米系網羅 × 商用安全 × 既存CCワークフロー統合**」を重視するなら Adobe Firefly、という住み分けになる。今回のCM制作フローが Higgsfield で成立するのは、Seedance や Kling といったモデル群と MCP 自動化の両方が揃っているからだ。

## 「構想力」の時代へ

このワークフローが示唆することは、技術的なスキルよりも **演出・コンセプトを言語化する力** が制作の核になるという変化だ。

従来の広告制作では：
- **撮影スキル**（カメラ操作、ライティング）
- **編集スキル**（After Effects、Premiere Pro）
- **ツール習熟**（複数の専門ソフトウェア）

これらが参入障壁になっていた。しかし Claude Code × MCP のフレームワークでは、「外部APIで道具を揃えてClaudeが指揮する」（[@ClaudeCode_love の解説より](https://x.com/ClaudeCode_love/status/2056936711721308581)）標準型として、複数の専門ツールをMCPサーバーとして集め、Claude がオーケストレーターとして動く構造が定着しつつある。

個人クリエイターも、スタートアップも、「何を作るか・どう見せるか」を明確に言語化できれば、技術的な実装コストはMCPが吸収してくれる。

## まとめ

Claude Code × Higgsfield MCP のモーションデザインフローをまとめると：

| 項目 | 内容 |
|------|------|
| MCP追加コマンド | `claude mcp add --transport http --scope user higgsfield https://mcp.higgsfield.ai/mcp` |
| 対応モデル数 | 30以上（Sora 2、Veo 3.1、Kling 3.0、Seedance 2.0 など） |
| 動画解像度 | 最大4K（Kling 3.0 等）/ Seedance 2.0 は最大2K |
| ワークフロー | Pinterest参考収集 → GPT Image 2 絵コンテ → Seedance 2.0 動画化 |
| 操作方法 | Claude Code のチャットのみ |

Higgsfield の「Motion Design, solved.」という宣言は大げさに聞こえるかもしれないが、このフローが普及すれば広告制作の現場は確実に変わる。まずは `claude mcp add` の1コマンドから試してみてほしい。
