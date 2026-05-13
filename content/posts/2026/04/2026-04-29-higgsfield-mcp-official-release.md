---
title: "Higgsfield MCP 正式リリース — 1つのコネクタで30以上のAI動画・画像モデルをエージェントから使う"
date: 2026-04-29
lastmod: 2026-04-29
slug: "higgsfield-mcp-official-release"
draft: false
description: "Higgsfield MCP は Claude・Cursor などの MCP クライアントから Seedance 2.0・Sora 2・Veo 3.1 など30以上の AI 動画・画像生成モデルを1つのコネクタで呼び出せるホスト型 MCP サーバー。"
source_url: "https://github.com/hdknr/blogs/issues/1#issuecomment-4340888308"
categories: ["AI/LLM"]
tags: ["MCP", "Higgsfield", "AI動画生成", "画像生成", "Claude"]
---

AI動画・画像生成の世界に大きな変化が来た。Higgsfield が MCP（Model Context Protocol）サーバーを正式リリースし、Seedance 2.0・Kling 3.0・Veo 3.1・Sora 2 など 30 以上のトップモデルを「1 つのコネクタ」で利用できる環境が整った。

## Higgsfield MCP とは

Higgsfield MCP は、複数の AI 画像・動画生成モデルをエージェントツールとして公開するホスト型 MCP サーバーだ。エンドポイントは `https://mcp.higgsfield.ai/mcp` で、Higgsfield アカウントで一度認証するだけで配下のモデルをすべて利用できる。

対応クライアント:

- **Claude**（Settings → Connectors から追加）
- OpenClaw
- Hermes Agent
- NemoClaw
- Cursor
- その他 MCP 対応クライアント全般

## 対応モデル一覧

### 動画生成モデル

| モデル | 特徴 |
|---|---|
| Seedance 2.0 | ByteDance製。口パク同期・SFX・音楽を1パスで生成 |
| Sora 2 | OpenAI製。長尺・高品質な動画生成 |
| Kling 3.0 | 高精細な映像クオリティ |
| Veo 3.1 | Google DeepMind製。映画的なビジュアル |
| WAN 2.6 | 多様なスタイル対応 |
| Hailuo 02 | MiniMax製。リアルな動作表現 |

全対応モデルは [Higgsfield 公式ページ](https://higgsfield.ai/ai-video) を参照。

### 画像生成モデル

| モデル | 特徴 |
|---|---|
| GPT Image 2 | OpenAI製。指示追従性が高い |
| Nano Banana Pro | 高速生成 |
| Soul 2.0 | キャラクター一貫性 |
| Flux 2 | 高解像度出力 |
| Seedream 5.0 Lite | ByteDance製。高速テキスト・画像生成 |

全対応モデルは [Higgsfield 公式ページ](https://higgsfield.ai/ai-image) を参照。

動画は最大 15 秒、画像は最大 4K 解像度に対応している。生成コストは Higgsfield クレジットから消費される。

## Claude から使う手順

### 1. MCP を追加する

Claude の Settings → Connectors を開き（`claude.ai/settings/connectors`）、以下の URL を登録する:

```
https://mcp.higgsfield.ai/mcp
```

### 2. Higgsfield アカウントで認証

初回接続時に Higgsfield アカウントへの OAuth 認証が求められる。認証後は以降のセッションで自動的に使える。

### 3. 会話から動画・画像を生成する

認証後は Claude との会話の中で直接リクエストできる:

```
「桜が散る夜の東京の映像を Seedance 2.0 で 10 秒生成して」
「Flux 2 で 4K のサイバーパンク風の街並みを生成して」
```

エージェントが生成・管理を担うため、ユーザーは指示を与えるだけでよい。

## エージェントによる自律ワークフロー

Higgsfield MCP の本質的な価値は **「人間が寝ている間にコンテンツが量産される」** 自律運用だ。

たとえば Claude Code で以下のようなルーティンを組むことができる:

1. マーケティング要件を受け取る
2. コンセプトを設計する
3. Higgsfield MCP でバリエーション動画を複数生成する
4. 結果を S3 等にアップロードする
5. 品質評価レポートを出力する

人間の介在なしに、エージェントが一連のビジュアルコンテンツ制作フローを完結させられるようになった。

## 従来との違い

従来は各モデルのサービスに個別にアクセスし、UI を操作して生成する必要があった。Higgsfield MCP によって以下が変わった。

- **認証の一元化**: 各モデルへのアカウント管理不要
- **ツール呼び出しの統一**: エージェントから同じインターフェースで全モデルを操作
- **会話内での反復**: 生成結果を会話の文脈で評価・修正・再生成できる
- **履歴の参照**: 過去の生成物をエージェントがそのまま参照できる

## 広告業界へのインパクト

Higgsfield MCP が示す変化の本質は、従来の制作フローの全面的な圧縮だ。

### 従来の広告制作フロー

ブリーフィング → 代理店会議 → プリプロダクション → 撮影 → 編集 → 数十ラウンドのレビュー → 数週間のタイムライン

商品動画の制作に数十万円以上のコストと数週間の期間が必要だったフローが、**Claude + Higgsfield の1つの会話セッション**に収まる。

### コスト削減の試算

一部の実践者による試算では、Higgsfield MCP を使った場合のコスト削減幅は **従来制作比 97〜99%** に達するとされている（公式数値ではなく個人試算）。

- レストランのメニュー写真：従来数万円 → Claude で数百バリエーションを生成
- スタートアップのプロモーション動画：制作会社なしで大手と同等のビジュアル品質

### 圧縮される職種

「ブランドがコンテンツを欲しがる」から「コンテンツが公開される」までの間に存在した職能チェーン全体が対象になっている。

- 商品フォトグラファー
- 動画プロダクション
- 動画エディター
- フリーランスのアートディレクター
- ポストプロダクションスタジオ

このチェーン全体が1つのテキストフィールドに圧縮された。

### プロトコルの開放性

Higgsfield MCP が MCP という**オープンプロトコル**で提供されていることも重要だ。Claude だけでなく、MCP に対応したあらゆるエージェントから利用できる。先行して統合したエージェントやサービスが市場のスプレッドを取る可能性がある。

## Marketing Studio プリセット

Higgsfield MCP には、広告・マーケティング用途に特化した 9 種類のプリセットが含まれている（以下は公式が明示している主要 5 種）:

| プリセット | 用途 |
|---|---|
| UGC（User Generated Content） | SNS向けのリアルなユーザー体験動画 |
| Unboxing | 商品開封動画 |
| TV Spot | テレビCM形式の短尺動画 |
| Product Review | 商品レビュー動画 |
| Hyper Motion | 高速・ダイナミックな映像 |

同一キャラクターのビジュアル一貫性（複数シーンにわたるキャラクター同一性）も維持できるため、ブランドイメージを保ちながら複数バリエーションのコンテンツを大量生成できる。

## まとめ

Higgsfield MCP の登場により、AI 動画・画像生成がエージェントワークフローに本格的に組み込めるようになった。Claude をはじめとする MCP 対応クライアントから 30 以上のモデルを統一インターフェースで呼び出せる環境は、コンテンツ制作の自動化を一気に加速させる。

技術的な敷居が低く、プロトコルが開放されているため、最初に動いた者がアドバンテージを得やすい状況にある。

- [Higgsfield MCP 公式ページ](https://higgsfield.ai/mcp)
- MCP エンドポイント: `https://mcp.higgsfield.ai/mcp`
