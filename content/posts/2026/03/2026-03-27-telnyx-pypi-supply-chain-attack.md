---
title: "PyPI公式パッケージ telnyx がサプライチェーン攻撃で汚染 — TeamPCPによるWAVステガノグラフィ攻撃の全容"
date: 2026-03-27
lastmod: 2026-03-27
draft: false
description: "PyPI公式パッケージ telnyx がTeamPCPのサプライチェーン攻撃で汚染。WAVステガノグラフィ手法の詳細と、Python開発者が今すぐ取るべき対策を解説。"
source_url: "https://github.com/hdknr/blogs/issues/1#issuecomment-4145706244"
categories: ["セキュリティ"]
tags: ["supply-chain", "PyPI", "マルウェア", "Python", "security"]
---

サプライチェーン攻撃とは、ソフトウェアの開発・配布の過程（サプライチェーン）に侵入し、正規のパッケージやツールに悪意あるコードを混入させる攻撃手法です。開発者が信頼して利用しているライブラリが攻撃の入口になるため、通常のセキュリティ対策では気づきにくいのが特徴です。

2026年3月27日、PyPIで月間74万ダウンロードを誇る通信プラットフォーム Telnyx の公式 Python SDK（`telnyx`）が、まさにこのサプライチェーン攻撃によって汚染されました。攻撃者グループ **TeamPCP** が悪意あるバージョン 4.87.1 および 4.87.2 を公開しました。これらは import するだけでマルウェアが実行される極めて危険なものです。

## 何が起きたのか

### タイムライン

- **2026年3月27日 03:51 UTC** — 悪意あるバージョン 4.87.1 と 4.87.2 が PyPI に公開
- **同日 10:13 UTC** — PyPI によって当該バージョンが隔離（quarantine）

約6時間にわたり、`pip install telnyx` を実行したユーザーは悪意あるバージョンをインストールする可能性がありました。

### 攻撃の仕組み

悪意あるコードは `telnyx/_client.py` に注入されていました。パッケージを import するだけで自動実行される仕組みです。攻撃は以下の手順で進行します:

1. **初期実行**: `import telnyx` だけでマルウェアコードが発動
2. **ペイロード取得**: リモートサーバーから WAV 音声ファイルをダウンロード
3. **ステガノグラフィ（データを別のファイルに隠す技術）**: WAV ファイルのオーディオフレーム内に実行ファイルが埋め込まれている
4. **環境別の挙動**:
   - **Windows**: 永続的な実行ファイルをドロップ
   - **Linux/macOS**: クレデンシャル（認証情報）を窃取

WAV ファイル内に実行ファイルを隠すステガノグラフィ手法は、通常のセキュリティスキャンやウイルス対策ソフトでは検出が困難です。音声ファイルという無害に見えるファイル形式を悪用している点が巧妙です。

## TeamPCP のサプライチェーン攻撃キャンペーン

今回の telnyx 攻撃は単独の事件ではありません。TeamPCP は2026年3月20日以降、以下のような連鎖的なサプライチェーン攻撃を展開しています:

| 対象 | 種別 | 影響 |
|------|------|------|
| **Trivy** | セキュリティスキャナー | CI/CD クレデンシャルの窃取 |
| **Checkmarx (KICS)** | セキュリティツール | 同上 |
| **LiteLLM** | AI/LLM プロキシ | 認証情報の窃取 |
| **telnyx** | 通信 API SDK | クレデンシャル窃取 + マルウェアドロップ |

攻撃パターンは一貫しています:

1. 信頼されたツールを侵害する
2. CI/CD クレデンシャルを窃取する
3. 窃取したクレデンシャルで次のターゲットを汚染する
4. 繰り返す

特に LiteLLM は AI/LLM 関連ツールであり、Claude Code や GPT を活用した開発環境で広く使われているため、AI 開発者にとっても直接的な脅威となります。

## 影響範囲

Telnyx 社は以下の点を明確にしています:

- **影響を受けたもの**: PyPI 上の Python SDK 配布チャネルのみ（バージョン 4.87.1 と 4.87.2）
- **影響を受けていないもの**: Telnyx のプラットフォーム、API、インフラストラクチャ本体

## telnyx 利用者への緊急対応

telnyx パッケージを利用している場合は、以下を**今すぐ**実行してください:

1. インストール済みバージョンを確認:
   ```bash
   pip show telnyx
   ```
2. バージョン 4.87.1 または 4.87.2 がインストールされている場合:
   ```bash
   pip install telnyx==4.87.0
   ```
3. システムのクレデンシャル（API キー、トークン等）をローテーションする
4. 不審なプロセスやファイルがないか確認する

## AI コーディングツール利用者への教訓

Claude Code をはじめとする AI コーディングツールは、ライブラリのインストールを提案してくれる便利な存在です。しかし、今回の事件は重要な教訓を示しています。「AI が提案したから安全」という思い込みは危険です。

### 防御策

1. **バージョンを明示的にピン留めする**
   ```bash
   # 危険: 最新版を自動インストール
   pip install telnyx

   # 安全: 検証済みバージョンを指定
   pip install telnyx==4.87.0
   ```

2. **インストール前に PyPI のリリース履歴を確認する**
   - 不自然なタイミングでの更新は要注意
   - GitHub のタグと PyPI のバージョンが一致しているか確認

3. **pip-audit で脆弱性チェックを行う**
   ```bash
   pip install pip-audit
   pip-audit
   ```

4. **仮想環境でテスト実行する**
   - 本番環境に直接インストールせず、venv や Docker コンテナ内で検証

5. **requirements.txt のバージョン範囲を制限する**
   ```txt
   # 危険: メジャーバージョン内で最新を許可
   telnyx>=4.0,<5.0

   # 安全: パッチバージョンまで固定
   telnyx==4.87.0
   ```

## まとめ

サプライチェーン攻撃は、信頼されたパッケージマネージャーの仕組みを悪用するため、従来のセキュリティ対策だけでは防ぎきれません。AI ツールが自動でライブラリを提案・インストールする時代です。だからこそ、開発者自身が「最後の防衛線」となる必要があります。バージョンの確認とピン留めを日常的な習慣にしましょう。

## 参考リンク

- [Telnyx 公式セキュリティ通知](https://telnyx.com/resources/telnyx-python-sdk-supply-chain-security-notice-march-2026)
- [Datadog Security Labs: LiteLLM and Telnyx compromised on PyPI](https://securitylabs.datadoghq.com/articles/litellm-compromised-pypi-teampcp-supply-chain-campaign/)
- [OX Security: Telnyx Malware — TeamPCP Strikes Again](https://www.ox.security/blog/telnyx-malware-teampcp-strikes-again-following-litellm-compromise/)
- [CybersecurityNews: Telnyx PyPI Package Compromised](https://cybersecuritynews.com/telnyx-pypi-package-compromised/)
- [Infosecurity Magazine: TeamPCP Targets Telnyx](https://www.infosecurity-magazine.com/news/teampcp-targets-telnyx-pypi-package/)
