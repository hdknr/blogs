---
title: "Higgsfield"
description: "30 以上の AI 動画・画像生成モデルを 1 つのアカウントで使える動画生成プラットフォーム。公式 MCP サーバーで Claude Code などのエージェントから生成を実行できる"
date: 2026-10-30
lastmod: 2026-10-30
aliases: ["Higgsfield AI", "Higgsfield MCP", "Higgsfield Supercomputer", "mcp.higgsfield.ai"]
related_posts:
  - "/posts/2026/04/higgsfield-mcp-official-release/"
  - "/posts/2026/05/claude-code-higgsfield-mcp-cm-production/"
  - "/posts/2026/05/higgsfield-supercomputer-ai-cinematic-pipeline/"
  - "/posts/2026/06/claude-code-4tool-video-mass-production-mcp/"
  - "/posts/2026/10/higgsfield-claude-code-short-video/"
  - "/posts/2026/10/short-video-scenario-reverse-generation/"
tags: ["Higgsfield", "動画生成", "mcp", "claude-code"]
---

## 概要

Seedance・Kling・Veo・Sora などの動画生成モデルと、GPT Image・Flux などの画像生成モデルを 1 つのアカウントとクレジットで使える動画生成プラットフォーム。Web 版のほか、ホスト型の**公式 MCP サーバー**を提供しており、Claude Code などのエージェントからプロンプトを渡して生成まで実行できる。

実務で手間がかかるのは生成そのものより「カット割り」と「英文プロンプト」を毎回考える作業で、そこを Claude Code に任せてファイルで管理し、MCP で生成につなぐ使い方が定番になっている（[ショート動画のシナリオ設計と生成](/blogs/wiki/guides/short-video-scenario-generation/)）。

## 詳細

### Higgsfield MCP

```bash
claude mcp add --transport http --scope user higgsfield https://mcp.higgsfield.ai/mcp
claude mcp list   # 接続確認
```

- エンドポイントは末尾が `/mcp`。付けずに登録すると接続に失敗するという報告があり、その場合は `claude mcp remove higgsfield` してから登録し直す
- 認証は OAuth。API キーは不要で、初回利用時にブラウザでサインインする
- Claude（claude.ai）では Settings → Connectors から追加する。Cursor など他の MCP クライアントにも対応
- 動画は最大 15 秒、画像は最大 4K（リリース時点）
- API キーで認証する **Higgsfield API** は MCP とは別の開発者向け製品で、自前のスクリプトから直接呼ぶ場合に使う

### クレジット消費の注意

- MCP・CLI など自動化ツール経由の生成は**必ずクレジットを消費**する。Web 版の無制限プランや無料生成の枠は適用されない（公式ヘルプ）
- 無料クレジット量やプラン内容は情報源によって記述が異なり、変わりうるので公式で確認する
- 一括生成はクレジットが一気に減る。まず 1 カットだけ生成して品質を確かめてから広げる
- 人物や商品が出るシナリオは、生成前に人の目でレビューする工程を挟む。公開の責任は使う側にある

### Supercomputer

1 行の演出指示から、61 の制作スキルでシーンごとに最適なモデル（脚本は GPT-5.5 / Claude Opus 4.7、カメラワークは Seedance、実写質感は Veo、モーションは Kling など）へ自動ルーティングし、1 本のタイムラインに統合するマルチモデル制作ハブ。モデルを手で選んで出力をつなぐ従来の使い方を、オーケストレーション型に置き換える。

### 他ツールとの組み合わせ

Claude Code を司令塔にして、Higgsfield を映像・画像生成の担当に据え、他の MCP（音声・デザイン・動画編集）と組み合わせて量産する構成の例がある。参考動画からリバース生成した台本を、キャラクターや商品だけ差し替えて Higgsfield 用のプロンプトに書き直す使い方もできる。

## 関連ページ

- [ショート動画のシナリオ設計と生成](/blogs/wiki/guides/short-video-scenario-generation/) — Claude Code でのシナリオ量産とリバース生成の手順
- [MCP（Model Context Protocol）](/blogs/wiki/concepts/mcp/) — Higgsfield MCP の土台のプロトコル
- [Claude Code](/blogs/wiki/tools/claude-code/) — MCP 経由で生成を指示するエージェント
- [AI動画広告生成ツール](/blogs/wiki/concepts/ai-video-ads/) — UGC 広告に特化した周辺ツール群
- [Video Use](/blogs/wiki/tools/video-use/) — エージェントによる動画編集

## ソース記事

- [Higgsfield MCP 正式リリース — 1つのコネクタで30以上のAI動画・画像モデルをエージェントから使う](/blogs/posts/2026/04/higgsfield-mcp-official-release/) — 2026-04-29
- [Claude Code × Higgsfield MCP でCM制作が一撃完結](/blogs/posts/2026/05/claude-code-higgsfield-mcp-cm-production/) — 2026-05-20
- [Higgsfield「Supercomputer」— マルチモデル映像制作ハブ](/blogs/posts/2026/05/higgsfield-supercomputer-ai-cinematic-pipeline/) — 2026-05-21
- [Claude Code + 4ツールMCP連携で動画10本量産](/blogs/posts/2026/06/claude-code-4tool-video-mass-production-mcp/) — 2026-06-01
- [Claude Code で Higgsfield 用ショート動画シナリオを量産する — CLAUDE.md でプロンプト構文を固定し MCP で生成まで](/blogs/posts/2026/10/higgsfield-claude-code-short-video/) — 2026-10-14
- [ショート動画からシナリオと絵コンテをリバース生成する](/blogs/posts/2026/10/short-video-scenario-reverse-generation/) — 2026-10-16
