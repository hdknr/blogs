---
title: "Palo Alto Cortex XDR の振る舞い検知ルールが解読・バイパスされた脆弱性の全容"
date: 2026-03-18
lastmod: 2026-03-18
draft: false
description: "Cortex XDR エージェントの BIOC ルールが AES 暗号化キーのハードコードにより解読可能だった脆弱性の技術解説。ccmcache 許可リストによる検知バイパスの手口と修正内容を詳述。"
source_url: "https://github.com/hdknr/blogs/issues/1#issuecomment-4079193872"
categories: ["セキュリティ"]
tags: ["Palo Alto Networks", "Cortex XDR", "EDR", "脆弱性", "BIOC"]
---

Palo Alto Networks の EDR（Endpoint Detection and Response: エンドポイント検知・対応）製品「Cortex XDR」のエージェントに、重大な欠陥が発見された。振る舞い検知（BIOC: Behavioral Indicators of Compromise）ルールを解読し、検知を完全に回避できるというものだ。InfoGuard Labs の研究者 Manuel Feifel らが発見し、2025年7月に報告、2026年2月末に修正がリリースされた。Cortex XDR エージェント v8.7/8.8 を利用する組織は、修正済みの v9.1 へのアップデートが必要となる。

## 発見の経緯

InfoGuard Labs の研究チームは、Cortex XDR Windows エージェント（バージョン 8.7 および 8.8）の内部構造を調査した。カーネルデバッグツールを使用してエージェント内部の暗号化ルールの復号プロセスを追跡し、以下を特定した。

- 復号キーがエージェントのファイル内にハードコードされた文字列から導出されていた
- 平文の Lua 設定ファイルと組み合わせてキーが生成されていた
- 暗号化には AES-256-CBC が使用されていたが、全環境で同一の鍵が導出されるため、一度手法を解明すれば任意の環境で再現可能だった

## グローバル許可リストの問題

復号された BIOC ルールを解析した結果、検知ロジックにハードコードされた「グローバル許可リスト」の存在が明らかになった。

特に深刻だったのは `\Windows\ccmcache` という文字列の扱いだ。プロセスのコマンドラインにこの文字列が含まれるだけで、そのプロセスは監視対象から除外される仕組みになっていた。この条件により、**BIOC ルール全体の約半数の振る舞い検知ルールを無効化**できることが確認された。

`ccmcache` は Microsoft SCCM（System Center Configuration Manager）がソフトウェア配布時に使用するキャッシュディレクトリだ。正規のシステム管理ツールによるプロセスを誤検知しないための除外条件だったと考えられるが、その適用範囲が過度に広範だった。

## 実証された攻撃シナリオ

研究者は Sysinternals の ProcDump ツールに `\Windows\ccmcache` 文字列を引数として付加し、LSASS（Local Security Authority Subsystem Service）メモリのダンプ取得を無検知で実行できることを実証した。

LSASS メモリダンプは認証情報窃取の典型的な手法であり、Mimikatz などのツールによるクレデンシャルハーベスティング（認証情報の大量収集）に直結する。EDR がこの操作を検知できないことは、実運用環境において極めて深刻な影響をもたらす。

## 修正内容

Palo Alto Networks は 2026年2月末に Cortex XDR エージェント バージョン 9.1（コンテンツアップデート 2160）で修正をリリースした。主な修正内容は以下の通り。

- 過度に広範なグローバル許可リストの削除
- 暗号化キー生成プロセスの一部変更

ただし、暗号化方式自体の根本的な変更ではなく、主要な改善は広範な除外条件の排除にある。

## セキュリティ上の教訓

今回の事例が示す重要なポイントは以下の通りだ。

### 暗号化ルールへの過信は危険

検知ルールを暗号化して非公開にする「セキュリティ・バイ・オブスキュリティ」のアプローチには限界がある。攻撃者がエージェントのバイナリにアクセスできる以上、暗号化は時間稼ぎに過ぎない。

### 許可リストの設計は最小権限で

正規ソフトウェアとの共存のための除外条件は、可能な限り限定的に設計する必要がある。コマンドライン引数に特定文字列が含まれるだけで広範なルールが無効化される設計は、攻撃者にとって格好のバイパス手段となる。

### EDR は万能ではない

ブラックボックス型のセキュリティ製品であっても、内部ロジックの解析と回避は可能だ。多層防御の原則に立ち返り、EDR 単体への依存を避けることが重要である。

## 参考リンク

- [InfoGuard Labs 原文](https://labs.infoguard.ch/posts/decrypting-and-abusing_paloalto-cortex-xdr_behavioral-rules_biocs/)
- [Cyber Security News 記事](https://cybersecuritynews.com/decrypt-and-exploit-cortex-xdr/)
- [Cortex XDR BIOC Rule Details（公式ドキュメント）](https://docs-cortex.paloaltonetworks.com/r/Cortex-XDR/Cortex-XDR-Pro-Administrator-Guide/BIOC-Rule-Details)
