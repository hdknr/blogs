---
title: "ForceMemo: GitHub アカウントを乗っ取り Python リポジトリにバックドアを仕込む新型攻撃"
date: 2026-03-19
lastmod: 2026-03-19
draft: false
source_url: "https://github.com/hdknr/blogs/issues/1#issuecomment-4088498941"
categories: ["セキュリティ"]
tags: ["security", "github", "python", "supply-chain", "vscode"]
---

2026年3月上旬から、GitHub アカウントを侵害して Python リポジトリに悪意あるコードを注入する「ForceMemo」と呼ばれる大規模攻撃キャンペーンが確認されています。force-push によるコミット履歴の書き換えと、Solana ブロックチェーンを利用した C2（Command and Control: 攻撃者がマルウェアに指令を送る仕組み）通信という巧妙な手法が特徴です。

## 攻撃の概要

ForceMemo は、以下の流れで Python プロジェクトを侵害します:

1. **GitHub アカウントの侵害** — GlassWorm と呼ばれる情報窃取マルウェアが VS Code / Cursor 拡張機能から GitHub トークンを抽出
2. **コードの改ざん** — 侵害したアカウントで `setup.py`、`main.py`、`app.py`、`manage.py` 等に難読化されたマルウェアを注入
3. **痕跡の隠蔽** — force-push でコミット履歴を書き換え、タイムスタンプを維持することで改ざんを検知困難に
4. **C2 通信** — Solana ブロックチェーンのメモ機能を使ったコマンド＆コントロール通信

## GlassWorm による初期侵入

攻撃の起点となる GlassWorm は情報窃取型マルウェアで、VS Code および Cursor の拡張機能を経由して感染します。窃取対象となる GitHub トークンの格納先は多岐にわたります:

- VS Code / Cursor 拡張機能のストレージ
- `git credential fill` の出力
- `~/.git-credentials` ファイル
- `GITHUB_TOKEN` 環境変数

窃取されたトークンを使って正規のアカウントとしてリポジトリにアクセスし、コードを改ざんします。

## force-push による履歴改ざん

通常のコミットであれば `git log` で変更履歴を追跡できますが、ForceMemo は force-push を使ってコミット履歴自体を書き換えます。さらにタイムスタンプも維持するため、リポジトリのメンテナーやユーザーが改ざんに気づきにくい構造になっています。

## Solana ブロックチェーンを利用した C2

従来のマルウェアは HTTP/HTTPS ベースの C2 サーバーと通信しますが、ForceMemo は Solana ブロックチェーンのメモ（Memo）機能——トランザクションに任意のテキストデータを添付できる機能——を C2 通信に利用します。ブロックチェーン上のトランザクションデータを介して指令を受け取るため、従来のネットワーク監視では検知が困難です。

## 影響範囲

- **C2 インフラ活動開始**: 2025年11月27日から Solana 上での活動を確認
- **GitHub 上の感染確認**: 2026年3月8日に最初のリポジトリ侵害を確認
- **規模**: 数百の Python リポジトリが侵害（400以上との報告も）
- **対象**: Django アプリ、機械学習研究コード、Streamlit ダッシュボード、PyPI パッケージなど
- **状況**: 2026年3月時点で攻撃は継続中

## 対策

### リポジトリ管理者向け

- **ブランチ保護ルールの設定** — `main` / `master` ブランチへの force-push を禁止する
- **コミット履歴の監査** — 不審な force-push がないか定期的に確認する
- **署名付きコミットの強制** — GPG/SSH 署名付きコミットのみを受け入れる設定にする

### 開発者向け

- **VS Code / Cursor 拡張機能の見直し** — 不要な拡張機能を削除し、信頼できるもののみを使用する
- **GitHub トークンの管理** — トークンに最小限の権限のみ付与し、定期的にローテーションする
- **依存パッケージの検証** — `pip install` 前に `setup.py` の内容を確認する習慣をつける

### 組織向け

- **GitHub Audit Log の監視** — アカウントの異常なアクティビティを検知する仕組みを導入する
- **ネットワーク監視** — Solana ブロックチェーンへの異常な通信を監視対象に追加する

## まとめ

ForceMemo は、GlassWorm による GitHub トークン窃取を起点に、force-push での履歴改ざんと Solana ブロックチェーン C2 という検知困難な手法を組み合わせたサプライチェーン攻撃です。Python リポジトリの管理者・利用者は、ブランチ保護ルールの設定、署名付きコミットの強制、拡張機能の見直しなど、早急に防御策を講じることを推奨します。

## 参考リンク

- [Cybersecurity News: ForceMemo Hijacks GitHub Accounts](https://cybersecuritynews.com/forcememo-hijacks-github-accounts/)
- [StepSecurity: ForceMemo Campaign Report](https://www.stepsecurity.io/blog/forcememo-hundreds-of-github-python-repos-compromised-via-account-takeover-and-force-push)
- [The Hacker News: GlassWorm Attack](https://thehackernews.com/2026/03/glassworm-attack-uses-stolen-github.html)
