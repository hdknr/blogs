---
title: "DeepSeek-V4 Preview — Claude Opus 4.6 匹敵・100万トークン対応のオープンソース LLM が無償公開"
date: 2026-04-25
lastmod: 2026-04-25
draft: false
source_url: "https://github.com/hdknr/blogs/issues/1#issuecomment-4320800640"
categories: ["AI/LLM"]
tags: ["DeepSeek", "LLM", "オープンソース", "MoE", "ローカルLLM", "HuggingFace"]
description: "DeepSeek-V4 Preview は 2026 年 4 月公開のオープンソース LLM。Pro（1.6 兆パラメータ）と Flash の 2 バリアントで 100 万トークンに対応。Codeforces で GPT-5.4 を超え、MIT ライセンスで Hugging Face から無償取得可能。MoE アーキテクチャで推論演算量を 73% 削減。"
---

DeepSeek-AI が 2026 年 4 月 24 日、100 万トークンのコンテキスト長に対応したオープンソース AI モデル「**DeepSeek-V4 Preview**」を公開した。コーディング競技プラットフォーム Codeforces では GPT-5.4 を上回るレーティングを記録。コーディングベンチマークでは Claude Opus 4.6 にほぼ匹敵する性能を持ちながら MIT ライセンスで無償公開されるという、衝撃的なリリースとなった。

## DeepSeek-V4 の概要

DeepSeek-V4 Preview は **Pro** と **Flash** の 2 バリアントで構成される。

| モデル | 総パラメータ数 | 推論時アクティブパラメータ数 |
|---|---|---|
| DeepSeek-V4-Pro | 1 兆 6,000 億 | 490 億 |
| DeepSeek-V4-Flash | 2,840 億 | 130 億 |

いずれも **Mixture-of-Experts（MoE）アーキテクチャ**を採用しており、推論時には全パラメータの一部のみを活性化することで高い効率を実現している。

## アーキテクチャの革新：ハイブリッドアテンション

DeepSeek-V4 の技術的な目玉は「**ハイブリッドアテンション機構**」だ。トークン単位の圧縮と **DSA（DeepSeek Sparse Attention）** を組み合わせることで、前世代と比較して：

- **推論演算量を約 73% 削減**
- **KV キャッシュサイズを約 90% 削減**

これにより、100 万トークンという非常に長いコンテキストをより少ないリソースで扱えるようになった。実用上は長い会話履歴・大きなコードベース・長文ドキュメントを一度のプロンプトに収められるため、エージェント系ユースケースとの相性が良い。

## ベンチマーク性能

### Codeforces で GPT-5.4 超え

コーディング競技プラットフォーム **Codeforces** でのレーティングは **3,206**（V4-Pro）を記録し、GPT-5.4 の 3,168 を上回るスコアを達成した。コーディング能力においてオープンソースモデルとして最先端の水準に到達した形だ。

### コーディングで Claude Opus 4.6 にほぼ匹敵

SWE-bench Verified のようなコーディングベンチマークでは DeepSeek-V4-Pro が Claude Opus 4.6 とほぼ同等のスコアを記録している。一方、知識・推論系タスクではまだ差があり、公式ドキュメントも「フロンティアモデルとの差を縮めた（closing the gap with frontier models）」と表現している。

## 提供方法とライセンス

- **Hugging Face** にてモデルの重みを **MIT ライセンス**で公開
- DeepSeek 公式 API サービスにてデフォルトで 100 万トークンのコンテキスト長を提供
- 商用利用可能な MIT ライセンスのため、ローカル実行・自社サービスへの組み込みが容易

MIT ライセンスによるオープンソース公開は、企業での採用ハードルを大きく下げる。

## なぜ無料でオープンソース公開できるのか

この公開はオープンソースコミュニティで話題を呼び、ビジネスモデルへの疑問も SNS で噴出した。X（旧 Twitter）では「これほどの性能のモデルがポンとオープンで出てくるのはマジでいったいどういう商売の仕組みなんや」という率直な疑問も話題になった。

DeepSeek は中国のクオンタティブヘッジファンド High-Flyer Quant の創業者・梁文鋒（Liang Wenfeng）氏が 2023 年に設立した独立 AI 研究企業だ。オープンソース公開によって研究コミュニティとの協力関係を構築しつつ、API サービス（deepseek.com）での商用利用で収益を上げるビジネスモデルを採用している。強力なベースモデルを無償公開して知名度と採用実績を高め、クラウド API 利用や企業向けサポート契約を取り込む戦略は、Meta の LLaMA 戦略と近い。

## まとめ

DeepSeek-V4 Preview のポイントを整理すると：

- GPT-5.4 超え・コーディング系ベンチマークで Claude Opus 4.6 にほぼ匹敵
- 100 万トークンのコンテキスト長
- MoE アーキテクチャで推論コストを大幅削減
- MIT ライセンスで商用利用可能
- Hugging Face で重みを無償公開

オープンソース LLM のレベルが商用フロンティアモデルに肩を並べるペースで進化しており、「AI は一部の大企業だけが持てるもの」という前提が急速に崩れつつある。高性能 LLM のローカル活用・プライベートクラウドへのデプロイを検討している開発者はもちろん、AI 調達の選択肢を広げたい企業担当者にとっても、注目すべきリリースといえる。

---

**参考リンク**

- [コーディングで GPT-5.4 超え「DeepSeek-V4」無償公開 - PC Watch](https://pc.watch.impress.co.jp/docs/news/2104454.html)
- [DeepSeek-V4 Preview Release Notes - DeepSeek API Docs](https://api-docs.deepseek.com/news/news260424)
- [DeepSeek-V4-Pro - Hugging Face](https://huggingface.co/deepseek-ai/DeepSeek-V4-Pro)
- [DeepSeek-V4-Flash - Hugging Face](https://huggingface.co/deepseek-ai/DeepSeek-V4-Flash)
