---
title: "ChatGPTのコード実行環境にDNSトンネリングによるデータ漏洩の脆弱性が発覚"
date: 2026-03-31
lastmod: 2026-03-31
draft: false
source_url: "https://github.com/hdknr/blogs/issues/1#issuecomment-4165256986"
categories: ["セキュリティ"]
description: "ChatGPTのData Analysis環境にDNSトンネリングによるデータ漏洩の脆弱性をCheck Pointが発見。攻撃の仕組み、漏洩リスク、OpenAIの対応、ユーザーの対策を解説。"
tags: ["ChatGPT", "脆弱性", "DNSトンネリング", "OpenAI", "security"]
---

Check Point Research が、ChatGPT のコード実行ランタイム（Python Data Analysis 環境）に隠れた外部通信チャネルが存在することを発見しました。この脆弱性を悪用すると、ユーザーの会話内容やアップロードしたファイルが外部サーバーに漏洩する可能性がありました。OpenAI は 2026年2月20日に修正を完了しています。

## 脆弱性の概要

ChatGPT の Data Analysis 機能（旧 Code Interpreter）は、Python コードを実行するためのサンドボックス環境を提供しています。この環境は外部への直接的なネットワークアクセスを遮断するよう設計されていましたが、**DNS 名前解決の機能は通常のオペレーションとして残されていました**。

攻撃者はこの DNS 解決機能を悪用し、**DNS トンネリング**と呼ばれる手法でデータを外部に送信することが可能でした。

## DNS トンネリングの仕組み

DNS トンネリングとは、DNS クエリのサブドメイン部分にデータをエンコードして埋め込み、DNS の名前解決プロセスを通じてデータを送信する手法です。

```text
# 通常の DNS クエリ
example.com → IPアドレスを返す

# DNS トンネリング
<エンコードされたデータ>.attacker-controlled.com → 攻撃者のDNSサーバーがデータを受信
```

ChatGPT のコード実行環境では、DNS 解決が正常なオペレーションの一部として許可されていたため、この通信は外部へのデータ転送として認識されず、ユーザーへの警告も表示されませんでした。

## 攻撃シナリオ

### 悪意のあるプロンプトインジェクション

単一のプロンプトで隠れた漏洩チャネルを起動できます。「生産性向上ハック」や「プレミアム機能のアンロック」を謳う一見無害なプロンプトとして流通する可能性がありました。

### バックドア付きカスタム GPTs

悪意のある命令を埋め込んだカスタム GPT を通じて、ユーザーデータを無断で送信することが可能でした。通常、カスタム GPT が外部 API を呼び出す際にはユーザーの承認ダイアログが表示されますが、DNS 解決はこの承認対象外であったため、ユーザーの明示的な承認なしにデータが送信される仕組みでした。

## 漏洩する可能性があったデータ

- ユーザーのメッセージ（プロンプト）の生データ
- アップロードされたファイルの内容
- モデルが生成した要約や分析結果
- PDF や添付ファイルから抽出された個人情報（氏名、医療データ、財務情報など）

## OpenAI の対応

Check Point Research が OpenAI に報告したところ、OpenAI はすでに内部でこの問題を特定していたことを確認しました。修正は **2026年2月20日** に完全にデプロイされています。OpenAI によると、悪意ある攻撃に利用された証拠はないとのことです。

## 同時期に修正された Codex の脆弱性

同時期に、OpenAI の Codex にも別の脆弱性が報告されています。BeyondTrust の研究者が発見したこの脆弱性は、GitHub のブランチ名パラメータにおけるサニタイズ不備に起因するものでした。

攻撃者はブランチ名にコマンドを注入し、Codex コンテナ内で悪意のあるペイロードを実行して **GitHub ユーザーアクセストークン** を窃取できる可能性がありました。この脆弱性は **2026年2月5日** に修正されています。

## ユーザーが取るべき対策

1. **カスタム GPT の利用に注意する** — 信頼できないソースのカスタム GPT は使用を避ける
2. **機密データのアップロードを最小限にする** — 特に Data Analysis 機能利用時は注意
3. **不審なプロンプトを実行しない** — 「隠し機能」や「プレミアム機能」を謳うプロンプトに注意
4. **OpenAI のセキュリティ情報を定期的に確認する** — 今回の脆弱性は修正済みだが、今後も新たな脆弱性が発見される可能性がある

## まとめ

この脆弱性は、サンドボックス環境であっても DNS のような基本的なネットワーク機能がデータ漏洩のチャネルになり得ることを示しています。AI ツールのセキュリティは、従来の Web アプリケーションとは異なるリスクモデルを考慮する必要があり、特にコード実行環境の隔離設計には細心の注意が求められます。

## 参考リンク

- [ChatGPT Data Leakage via a Hidden Outbound Channel in the Code Execution Runtime - Check Point Research](https://research.checkpoint.com/2026/chatgpt-data-leakage-via-a-hidden-outbound-channel-in-the-code-execution-runtime/)
- [ChatGPT Data Leak (Fixed Feb 2026): Key Takeaways - Check Point Blog](https://blog.checkpoint.com/research/when-ai-trust-breaks-the-chatgpt-data-leakage-flaw-that-redefined-ai-vendor-security-trust)
