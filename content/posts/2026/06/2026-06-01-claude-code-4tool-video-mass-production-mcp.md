---
title: "Claude Code + 4ツールMCP連携で動画10本量産 — Algrow・Renoise・Higgsfield・Lovart・HyperFramesの全構成を解説"
date: 2026-06-01
lastmod: 2026-06-01
slug: "claude-code-4tool-video-mass-production-mcp"
draft: false
source_url: "https://github.com/hdknr/blogs/issues/1#issuecomment-4588948936"
description: "Claude CodeをオーケストレーターとしてAlgrow・Renoise・Higgsfield・LovartをMCP接続し、HyperFrames Skillでテロップ・カットを自動化。動画10本を量産する全構成を各ツールのMCP設定JSONと費用感とともに解説。"
categories: ["AI/LLM"]
tags: ["claude-code", "mcp", "AI動画", "動画生成", "Higgsfield", "Renoise", "Lovart", "HyperFrames", "コンテンツ自動化"]
---

「AIが寝ている間に自動販売機がチャリンチャリン鳴る時代」——株式会社MakeAI CEOのmana氏がXで公開したこの一文が多くの反響を呼んだ。Claude Codeに4つのツールをMCPで接続し、人間の手をほとんど介さずに動画10本を量産できる構成だという。本記事ではその全体像と各ツールの役割を詳しく解説する。

## 全体構成の概要

この動画量産システムは、Claude Codeをオーケストレーターとして、以下の4ツールをMCP経由で繋いだものだ。

| 役割 | ツール | 接続方法 |
|------|--------|---------|
| 競合分析 + 音声生成 | Algrow | MCP |
| AI動画生成 | Renoise | MCP |
| AI動画生成 | Higgsfield | MCP |
| AIデザイン・動画生成 | Lovart | API経由（MCP対応未確認） |
| テロップ・カット | HyperFrames | Claude Code Skill（無料） |

mana氏のツイートでは「4ツール組み合わせ」と表現されているが、これはAlgrow・Renoise・Higgsfield・Lovartの4サービスを指し、HyperFramesはClaude Code Skillとして別枠で機能する。Claude Codeが各ツールのMCPサーバーに自然言語で命令を出し、リサーチから動画の仕上げまでを自動でこなす。

## Algrow — YouTube競合分析 + 音声生成

### 概要

[Algrow](https://algrow.online/) はYouTubeに特化したリサーチ・コンテンツ生成プラットフォームだ。公式MCPサーバーを提供しており、Claude CodeからAlgrowの機能を自然言語で呼び出せる。

MCPツールは9カテゴリ・40以上が用意されている。

- **競合チャンネル分析**: バイラル動画の発見・トレンド追跡
- **TTS（テキスト音声変換）**: ElevenLabsおよびStealthプロバイダー対応、音声クローニング・多言語対応
- **サムネイル生成**: 競合分析結果をもとにした自動生成
- **動画分析**: 再生数・エンゲージメントの分析

### Claude CodeからのMCP接続

```json
{
  "mcpServers": {
    "algrow": {
      "url": "https://algrow.online/mcp"
    }
  }
}
```

Claude Codeに「このニッチで最近バイラルした動画のトップ10を調べて」と頼むだけで、Algrowが競合分析を実行し、その結果をもとに台本の方向性まで提案してくれる。TTSも同じMCP経由で呼び出せるため、台本さえ決まれば音声ナレーションを自動生成できる。

### 料金

| プラン | 月額 | TTS |
|--------|------|-----|
| Starter | $25 | 非対応 |
| Professional | $45 | 対応 |
| Ultimate | $80 | 対応 |

TTSを使うにはProfessional以上が必要。2日間$1のトライアルが用意されている。

## Renoise — AI動画生成（MCP対応）

### 概要

[Renoise](https://renoise.ai/) は商品写真1枚から大量の動画広告バリエーションを自動生成することに強みを持つAI動画プラットフォームだ。Seedance 2.0とKling 3.0 Omniを1つのキャンバス上で使い分けられる。

公式MCPマニフェストを提供しており、Claude Code・OpenClaw向けのプラグインもある。

### 主な機能

- **FacePass**: 本人確認済みの実顔を動画に使用できる機能
- **ネイティブリップシンク**: 音声と口の動きを自動同期
- **フォーリーオーディオ生成**: 映像に合った効果音を自動生成
- **REST API / Python SDK / CLI**: バッチ生成（GitHub Actions・Zapier連携）
- **出力解像度**: 720p〜1080p

Claude Codeから「この台本でリップシンク動画を5本生成して」と指示するだけで、Renoiseが複数バリエーションを並列で出力する。

### 料金

Starter $20/月（1,200クレジット相当）から。

## Higgsfield — 30以上のモデルを束ねるAI動画生成

### 概要

[Higgsfield](https://higgsfield.ai/) はSoul 2.0・Kling 3.0・Seedance 2.0・Veo 3.1・Sora 2・Flux・Minimax Hailuoなど30以上の動画モデルを1つのプラットフォームに統合している。

公式ホスト型MCPサーバー（`https://mcp.higgsfield.ai/mcp`）を正式リリース済みで、APIキー不要でHiggsfieldアカウントにより認証できる。

### 主な機能

- **Soul Character**: キャラクター一貫性のトレーニング機能（動画全体で同じキャラを維持）
- **バイラリティ予測**: Hook Score・Hold Rate・Brain Heatmapで拡散しやすさを事前評価
- **長尺→短編クリップ自動生成**: 長い動画からSNS用の切り抜きを自動作成
- **最大解像度**: 画像4K・動画15秒

### Claude CodeからのMCP接続

```json
{
  "mcpServers": {
    "higgsfield": {
      "url": "https://mcp.higgsfield.ai/mcp"
    }
  }
}
```

「この画像素材からKling 3.0でシネマティックな15秒動画を作って」といった指示が自然言語で通る。

## Lovart — AIデザインエージェント

### 概要

[Lovart](https://www.lovart.ai/) は中国のLiblib社が開発した「初のAIデザインエージェント」を標榜するサービスだ。ロゴ・SNS素材・マーケティングキャンペーン素材を一括生成できる。

動画モデルとしてはSora 2・Gemini Veo 3・Kling 2.6・Hailuo・Wan 2.6・Seedance 2.0など15以上を統合し、最大10分の動画生成に対応している。

### 主な特徴

- **マルチアセット出力**: 画像・動画・音声・3Dを同時並行で生成
- **ブランドキット統合**: ロゴや色彩ガイドラインを記憶して一貫性を保つ
- **キャンペーン一括生成**: 1つのブリーフから複数フォーマットの素材を自動生成

> **注意**: mana氏のツイートでは「全部MCPで繋がる」と述べているが、Lovartの公式MCPサーバーは現時点（2026年6月）で公式ドキュメントが確認できていない。Claude Codeとの連携はAPI経由またはカスタムツール経由の可能性がある。

## HyperFrames — 無料Skillでテロップ・カット

### 概要

[HyperFrames](https://github.com/heygen-com/hyperframes) はHeyGen社が開発したオープンソースの動画フレームワークだ。「HTMLを書いてMP4に変換する」というコードファーストな思想で設計されており、Claude Code Skillとして無料で利用できる。

- **GitHubスター**: 23,300以上
- **インストール数**: 80,700以上
- **ライセンス**: Apache 2.0（商用利用自由）

### インストール

```bash
npx -y skills add heygen-com/hyperframes --skill hyperframes --agent claude-code
```

### 主な機能

- **シンクドキャプション**: 音声に合わせたタイミングで字幕を自動表示
- **カイネティックテキスト**: 動くテキストアニメーション
- **ロウアーサード**: ニュース風のテキストオーバーレイ
- **シェーダートランジション**: GPUを使ったシーン切り替え効果
- **内蔵ツール**: Kokoro TTS・Whisper文字起こし・u2net背景除去

GSAP・CSS・Lottie・Three.jsなどのアニメーションライブラリにも対応している。

> **制限**: 生の映像フッテージのフレーム精度カットは非対応。テロップ・モーショングラフィックス・テキストオーバーレイに特化している。

## 全体ワークフロー

以下が、Claude Codeが指揮する動画量産の実際の流れだ。

```
1. [Algrow MCP] ニッチリサーチ → バイラル動画トップ10を分析
2. [Claude Code] 分析結果をもとに台本10本を生成
3. [Algrow MCP / TTS] 台本→音声ナレーション生成
4. [Higgsfield MCP or Renoise MCP] 音声+プロンプト→動画素材生成
5. [Lovart] ビジュアル素材・サムネイル生成（API経由）
6. [HyperFrames Skill] テロップ・カット・エフェクト追加 → MP4出力
```

これをClaude Codeが一元管理することで、ステップ間の受け渡しも含めてほぼ自動化される。1回のプロンプトで「ニッチのリサーチから完成動画まで」を通せる構成だ。

## 実現のポイントと課題

### メリット

- **統一コントロール**: すべてのツールをClaude Codeの自然言語インターフェースで操作できる
- **並列処理**: 複数の動画を同時生成することで量産速度が上がる
- **反復可能**: 同じ構成を繰り返すことで、量産ワークフローを標準化できる

### 現実的な課題

- **コスト**: 各ツールのサブスクリプション費用が重なる（Algrow $45 + Renoise $20 + Higgsfield（要問い合わせ）+ Lovart（要問い合わせ））
- **Lovartのモデル統合**: 執筆時点でLovartの公式MCP対応が未確認のため、完全自動化には追加の実装が必要になる可能性がある
- **動画品質のばらつき**: AIモデルの生成結果には品質のばらつきがあるため、最終チェックは人間が行うことが推奨される

## まとめ

Claude Code + MCPエコシステムの成熟により、「AIがコンテンツ制作パイプラインをオーケストレートする」という構成が現実的になってきた。Algrowで市場を読み、Renoise/Higgsfield/Lovartで映像を作り、HyperFramesで仕上げる——この4ツール連携は、1人のクリエイターが大量のコンテンツを継続的に出力するための一つのモデルケースとなるだろう。

ツールの組み合わせはまだ進化の途中だが、MCPという共通規格があることで、今後も新しいツールを差し替え・追加しながら構成をアップデートできる点が大きな強みだ。
