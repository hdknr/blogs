---
title: "Obsidianの創業者が「有料Syncを使わずに済む方法」を公式公開 — iCloud・Git・ヘッドレスCLIで完全無料運用する選択肢"
date: 2026-05-21
lastmod: 2026-05-21
slug: "obsidian-free-sync-without-paid-subscription"
draft: false
source_url: "https://github.com/hdknr/blogs/issues/1#issuecomment-4504098914"
categories: ["ツール/開発環境"]
tags: ["Obsidian", "ナレッジ管理", "セカンドブレイン", "Git", "iCloud"]
---

Obsidianの創業者が、自社の有料サービスである Obsidian Sync を **使わずに** Vault を同期・バックアップする方法を公式ドキュメントとして明文化したことが話題になっている。

## 何が起きているのか

Obsidian は「あなたのノートは永遠にあなたのもの」を掲げるローカルファースト型のナレッジ管理ツールだ。ノートはプレーンテキスト（Markdown）でローカルに保存され、クラウドへの依存を強制しない設計になっている。

そのObsidianの創業者が、有料の Obsidian Sync（$4〜/月・年払い、または $5/月・月払い）を契約しなくても Vault を複数デバイス間で同期できる方法を、公式ドキュメント上で余すところなく公開した。

## 公式が案内している無料同期の選択肢

公式ヘルプ（[Sync your notes across devices](https://obsidian.md/help/sync-notes)）によると、以下の方法が紹介されている。

### 1. iCloud（Apple デバイス間）

Mac・iPhone・iPad を使うユーザーにとって最もシンプルな選択肢。iCloud Drive の中に Vault フォルダを配置するだけで、Apple デバイス間でシームレスに同期される。

```
~/Library/Mobile Documents/iCloud~md~obsidian/Documents/MyVault
```

設定コストがほぼゼロで、iOS アプリとの相性も良い。

### 2. Google Drive / Dropbox / OneDrive

クラウドストレージのフォルダ配下に Vault を置くだけで同期が成立する。Windows や Android ユーザーにも対応できる汎用的な方法だ。

- Google Drive のデスクトップアプリで同期するフォルダを指定
- Vault を `~/Google Drive/MyVault` などのパスに配置
- モバイルでは公式の [Obsidian アプリ](https://obsidian.md) + ファイルマネージャアプリで Vault フォルダを指定

### 3. Git（バージョン履歴も残したい人向け）

[obsidian-git](https://github.com/Vinzent03/obsidian-git) プラグインを使えば、Vault の変更を GitHub などに自動プッシュできる。

```bash
# プラグイン設定後、Vault ルートで初期化
git init
git remote add origin https://github.com/yourname/my-vault.git
git push -u origin main
```

プラグイン設定で自動コミット・プッシュ間隔を指定できるため、**バージョン履歴**まで残せる点が他の方法と異なる。

### 4. ヘッドレス CLI で自動バックアップ

GUI に頼らず、CLI + cron や launchd で定期的にバックアップを組む方法も案内されている。Mac 環境なら以下のように launchctl でタスクを登録できる。

```bash
# rsync で外付けドライブや NAS にバックアップ
# --delete: コピー元にないファイルをコピー先からも削除（ミラーリング）
rsync -av --delete ~/Documents/MyVault/ /Volumes/Backup/MyVault/
```

サーバーに SSH でアクセスできる環境なら、Obsidian を起動せずにバックアップを完結させられる。

## なぜこれが珍しいのか

通常、SaaS 企業は有料プランへの誘導を優先するためドキュメントを設計する。無料で済む方法をわざわざ公式サイトで詳説するのは珍しい。

Obsidian はこの姿勢について次の立場を一貫して表明している。

> *"Obsidian はあなたのファイルを人質に取るつもりはない。あなたのノートは永遠にあなたのものだ。"*

この透明性は、Obsidian が「ユーザーの信頼によって成り立つビジネスモデル」を選んでいることの表れである。有料の Obsidian Sync を選ぶかどうかはユーザーに委ねられており、無料代替手段を公認することでむしろ長期的なロイヤリティを高めている。

## Obsidian Sync を使うメリットも残っている

もちろん、有料の Obsidian Sync には無料代替手段にないメリットもある。

| 機能 | Obsidian Sync | iCloud / Git |
|------|:---:|:---:|
| エンドツーエンド暗号化 | ✅ | ❌（クラウド側の暗号化のみ） |
| バージョン履歴（最大12ヶ月・Plusプラン） | ✅ | Git のみ ✅ |
| 設定・プラグインの同期 | ✅ | 手動 or Git |
| モバイル対応（即時） | ✅ | 要追加設定 |
| 選択的同期（フォルダ単位） | ✅ | ❌ |

セキュリティ要件が高い用途や、設定・プラグインを複数デバイスで統一したい場合には Obsidian Sync の価値は十分にある。

## まとめ

Obsidianの創業者が「有料プランを使わずに済む方法」を公式ドキュメントに明文化したことで、以下の事実が改めて確認された。

- **iCloud / Google Drive / Git / ヘッドレスCLI** のいずれかで完全無料運用が可能
- プロダクトを売る側がここまで透明なのは珍しく、Obsidian の「ユーザーファースト」哲学の表れである
- 有料 Sync には依然として独自の価値があるが、**選択肢はユーザーに完全に開かれている**

いずれの方法も設定コストは低く、まずは自分の環境と目的に合った手段を選んで試してみると良いだろう。
