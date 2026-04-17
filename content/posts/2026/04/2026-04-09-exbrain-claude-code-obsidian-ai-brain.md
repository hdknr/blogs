---
title: "Exbrain — Claude Code × Obsidian で「外付けAI脳」を構築する"
date: 2026-04-09
lastmod: 2026-04-17
draft: false
source_url: "https://github.com/hdknr/blogs/issues/1#issuecomment-4217201303"
categories: ["AI/LLM"]
tags: ["Claude Code", "Obsidian", "PKM", "自動化", "エージェント"]
---

チャエン（@masahirochaen）さんが「外付けのAI脳」と名付けたシステム **Exbrain** を GitHub で公開した。Claude Code × Obsidian × 常駐エージェントを組み合わせて、記憶・日報・クリッピングを全自動化するという意欲的なプロジェクトだ。

- GitHub: [chaenmasahiro0425/exbrain](https://github.com/chaenmasahiro0425/exbrain)

## Exbrain とは

Exbrain は「自分の外側にある AI の脳」を目指したパーソナル PKM（Personal Knowledge Management）システムだ。Karpathy が提唱した「LLM Wiki」パターンの実装版として設計されており、AIが継続的に自分の経験・価値観・目標を学習し続ける仕組みを提供する。

主な特徴:

- **毎朝の日報自動作成**: AI がカレンダー・Slack・Gmail を読み込み、その日のブリーフィングを自動生成
- **毎夕の振り返り**: AI が1日の行動を分析し、繰り返しパターン（例:「月曜は会議10件が3週連続」）を検出・記録
- **自動クリッピング**: X でブックマークした記事やツイートを約4時間後に自動要約して Obsidian に蓄積
- **Slack 連携**: Slack の DM に URL を投げるだけで即座にクリップ
- **常時稼働**: PC を閉じた状態・就寝中でもエージェントが動き続ける
- **iPhone で全部読める**: Obsidian の同期により、モバイルからもアクセス可能

## SOUL / MEMORY / DREAMS の3ファイル設計

Exbrain の核心は、自分自身を表現する3つの Markdown ファイルだ。

| ファイル | 役割 |
|----------|------|
| `SOUL.md` | 自分は誰か（価値観・境界線） |
| `MEMORY.md` | 何を経験したか（決定・学び） |
| `DREAMS.md` | どこに向かうか（洞察・未解決の問い） |

AI はこの3ファイルを毎日読み込み、そのコンテキストをもとに振り返りや提案を行う。単なるメモ帳ではなく、AIが自分のことを「知っている」状態を維持する仕組みだ。

## 3ファイルの自動更新メカニズム

Exbrain の特徴的な点は、3ファイルが**手動メンテナンスではなく Dreaming プロセスによって自動更新**される設計にある。

### MEMORY.md — 毎夕 + セッション終了時

| トリガー | 内容 |
|----------|------|
| 毎夕 18:30（クラウドスケジュール） | 1日の行動を分析し、決定履歴・学びを「Recent」セクションに追記 |
| Claude Code セッション終了時（フック） | セッション中のフィードバック・参照資料・プロジェクト情報をサマリ化して記録 |

記録される内容の例:
- 決定履歴:「2026-04-07 Obsidian vault 構築を決定」
- 行動パターン:「メール返信は午後に集中」「金曜は会議が多い」

### DREAMS.md — 朝夕 + 週次

| トリガー | 内容 |
|----------|------|
| 毎朝 7:00 | Morning Dreaming — 外部サービスの情報を取り込み、新たな洞察を生成 |
| 毎夕 18:30 | Evening Dreaming — 7日間のパターン検出・成長軌跡の追跡 |
| 毎週日曜 | 週次 Dreaming — より長期的な深掘り分析、未解決の問いの更新 |

蓄積される内容の例:
- パターン検出:「ツール → スキル → 自動化のサイクルが10回以上」
- 未解決の問い（Open Questions）:今後掘り下げるべきテーマ

### SOUL.md — 初期同期のみ

SOUL.md は価値観・境界線を定義するファイルであり、初期セットアップ時に Claude Code の CLAUDE.md とユーザー情報を統合して生成される。以降は基本的に**人間が手動で管理**する設計だ。AI が勝手に価値観を書き換えないという意図的な制約になっている。

### クラウドスケジュール実行

Dreaming プロセスはクラウドスケジュールで実行されるため、**PC を閉じた状態や就寝中でも自動的に動作**する。更新結果は git push で同期され、Obsidian Mobile 経由で iPhone からも確認できる。

## アーキテクチャの概要

```
外部サービス（Google Calendar / Slack / Gmail / X）
        ↓（Claude Code エージェントが定期取得）
  SOUL / MEMORY / DREAMS（3ファイル）
        ↓（コンテキストとして注入）
  Obsidian Vault（振り返り・クリッピング・日報）
        ↓（同期）
  iPhone（Obsidian Mobile）
```

常駐エージェントが各サービスの情報を定期的に収集し、3ファイルのコンテキストを参照しながら Obsidian への書き込みを行う。

## セットアップ

公式 README には日本語のセットアップ手順・フロー図・相関図が含まれており、非エンジニアでも把握できるよう配慮されている。

基本的な流れ:

1. リポジトリをクローンして依存パッケージをインストール
2. `SOUL.md` / `MEMORY.md` / `DREAMS.md` を自分の情報で初期化
3. Google Calendar・Slack・Gmail の API 認証を設定
4. X（Twitter）の認証を設定
5. Claude Code のエージェント設定を構成して常駐起動

詳細は [README](https://github.com/chaenmasahiro0425/exbrain) を参照。

## Karpathy「LLM Wiki」パターンとの関係

Andrej Karpathy が提唱した「LLM Wiki」パターンは、LLM が自分自身の知識・経験を構造化されたドキュメントとして蓄積し続けるというコンセプトだ。Exbrain はその実装例として、個人の PKM に応用したケースと見ることができる。

このブログでも Claude Code の memory システム（`MEMORY.md` + 個別メモリファイル）という同様のパターンを採用しているが、Exbrain はそれをさらに外部サービス連携・常駐エージェントと組み合わせた本格的な実装だ。

## まとめ

Exbrain は「AIに自分のことを覚えさせる」という発想を、実用レベルで実現したシステムだ。特に:

- **SOUL/MEMORY/DREAMS の3ファイル設計**という人間の記憶構造を模したアーキテクチャ
- **常駐エージェント**による完全自動化
- **Obsidian との統合**による可読性とモバイルアクセス

この組み合わせが個人 PKM を一段上のレベルに引き上げている。Claude Code を使った自律エージェントの応用例として、非常に参考になるプロジェクトだ。
