---
title: "SecSuite — OSINT収集からAI修復まで統合したオープンソースセキュリティプラットフォームが登場"
date: 2026-06-16
lastmod: 2026-06-16
slug: "secsuite-ai-security-platform"
draft: false
description: "OSINT収集・Web脆弱性診断・APIセキュリティ評価・AI修復支援を一元化したオープンソースツール「SecSuite」が登場。ローカルAI（Ollama）対応で完全オフライン環境でも動作する。"
source_url: "https://github.com/hdknr/blogs/issues/1#issuecomment-4714964281"
categories: ["セキュリティ"]
tags: ["SecSuite", "OSINT", "ペネトレーションテスト", "APIセキュリティ", "ollama", "security", "python"]
---

OSINT収集・Web脆弱性診断・APIセキュリティ評価・AI修復支援を一元化したオープンソースツール「**SecSuite**」がリリースされた。ローカルAIモデルに対応しており、完全オフラインの閉域環境でも動作する点が大きな特徴だ。

## SecSuiteとは

SecSuiteは「TheSecuredAnalyst」プロジェクトが開発したPython製のセキュリティスイートで、GitHub（`TheSecuredAnalyst/security-suite`）で公開されている。セキュリティ担当者・ペネトレーションテスター・レッドチーム向けに設計されており、モジュール式の拡張性と完全オフライン運用を両立させている。

v0.1.0の主なコンポーネントは次のとおりだ。

- **11種類のOSINTモジュール** — ドメイン情報・メールアドレス・IPレピュテーション・SNSデータなどを一括収集
- **6種類のWebセキュリティスキャナー** — XSS・SQLインジェクション・ディレクトリブルートフォース・Nucleiテンプレートスキャン・SSL/TLS解析などをカバー
- **4種類のAPIセキュリティテスト機能** — OpenAPI/Swagger仕様を読み込み、認証回避・JWTの不備・BOLA/IDORなどを検査

CLIとFastAPIベースのREST APIの両方から利用できる。

## インストール方法

セットアップスクリプトが用意されており、Python・依存ライブラリ・Ollamaとローカルモデルの導入まで一括で行われる。

```bash
# Linux / macOS
bash setup.sh

# Windows（管理者権限不要）
.\setup.ps1
```

インストール後は `secsuite` コマンドでCLIを、`secsuite serve` でFastAPIサーバーを起動できる。

## AI統合：Ollama・Claude・GPTに対応

AI分析機能は3つのプロバイダーをサポートする。

| プロバイダー | 特徴 |
|---|---|
| Ollama | 完全ローカル。APIキー不要。閉域環境で動作可能 |
| Anthropic Claude | クラウドAPI経由の高品質な分析 |
| OpenAI GPT | 同上 |

すべてのAPIキーはオプションであり、Ollamaを使えばAPIキーなしで主要機能をすべて利用できる。

## AI修復エンジン — secsuite ai remediate

SecSuiteの中でも特に実用的な機能が `secsuite ai remediate` だ。静的なレポートを出力するのではなく、スキャン後に発見された問題ごとに **確認・修正・検証用のコマンド** をインタラクティブに提示する。

```text
[CHECK]  redis-cli -h 192.168.1.10 ping
[FIX]    sed -i 's/^# requirepass/requirepass strongpassword/' /etc/redis/redis.conf
[VERIFY] redis-cli -h 192.168.1.10 -a strongpassword ping
```

オペレーターは各コマンドを実行・編集・スキップしながら対話的に問題を解消できる。このプロセス全体は **Qwen2.5 や LLaMA 3.2 などのローカルモデル**（Ollama）上で動作する。スキャンデータや認証情報が外部サーバーに送信されないため、セキュリティ用途において重要な特徴となる。

## APIセキュリティモジュール（`apisec`）

AI修復エンジンとは別に、`apisec` モジュールはREST APIを専門に担当するテストコンポーネントだ。OpenAPI/Swagger仕様を読み込み、発見されたエンドポイントを体系的にテストする。主な検査項目は次のとおりだ。

- 認証回避（Broken Authentication）
- JWT実装の不備（アルゴリズム混乱・署名検証スキップ）
- BOLA/IDOR（オブジェクトレベルの認可不備）

## スキャン結果の出力とSIEM連携

スキャン結果はJSON・CSV・HTML・Markdownの4形式で出力できる。さらに以下のSIEM連携機能も備えている。

- CEF/LEEFフォーマットでのログ出力（Splunk・Elasticsearch・Syslog）
- スケジューラーによるcronベースの定期スキャンと履歴管理

CI/CDパイプラインや既存のセキュリティオーケストレーション基盤への統合も `secsuite serve` のHTTPエンドポイント経由で可能だ。

## まとめ

SecSuiteはOSINT・Web診断・API評価・AI修復を一元化した意欲的なオープンソースプロジェクトだ。Ollamaによる完全オフライン動作は、インターネット非接続の環境でセキュリティ評価を行う必要がある場面で特に有用になる。ペネトレーションテストの各フェーズをシームレスにつなぐ統合ツールとして、今後の機能拡張が注目される。

- GitHub: [TheSecuredAnalyst/security-suite](https://github.com/TheSecuredAnalyst/security-suite)
- 参考記事: [SecSuite - AI-powered Tool for OSINT, Web and API Security Testing (Cyber Security News)](https://cybersecuritynews.com/secsuite-ai-powered-tool/)
