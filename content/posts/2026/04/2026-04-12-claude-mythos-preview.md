---
title: "Claude Mythos Preview とは？数千件のゼロデイ脆弱性を発見した AI モデルの衝撃"
date: 2026-04-12
lastmod: 2026-04-12
draft: false
description: "Anthropic が発表した Claude Mythos Preview は、主要 OS の数千件のゼロデイ脆弱性を自律的に発見できる AI モデル。一般公開を見送り Project Glasswing で限定提供される理由と金融業界への影響を解説。"
source_url: "https://github.com/hdknr/blogs/issues/1#issuecomment-4232653095"
categories: ["AI/LLM"]
tags: ["claude", "anthropic", "security", "llm", "agent"]
---

Anthropic が 2026 年 4 月 7 日に発表した **Claude Mythos Preview** は、同社史上最も高性能な汎用言語モデルでありながら、一般公開が見送られた異例のモデルです。同モデルはサイバーセキュリティ分野で突出した能力を示し、主要 OS やブラウザに潜む数千件のゼロデイ脆弱性（開発者が認識する前に存在する未修正のセキュリティ上の欠陥）を自律的に発見・悪用できることが確認されました。

この発表はセキュリティ業界だけでなく金融業界にも波紋を広げ、米国の財務長官や FRB 議長、ウォール街の CEO たちが緊急招集される事態にまで発展しています。

## Claude Mythos Preview のベンチマーク性能

Mythos Preview は、従来の Claude Opus 4.6 を大幅に上回るベンチマーク結果を示しています。SWE-bench Verified では 13 ポイント以上、USAMO 2026 では 55 ポイント以上の向上を記録しました。

| 評価項目 | Mythos Preview | Opus 4.6 |
|---------|---------------|----------|
| SWE-bench Verified | 93.9% | 80.8% |
| USAMO 2026 | 97.6% | 42.3% |
| CyberGym（脆弱性再現） | 83.1% | 66.6% |
| SWE-bench Pro | 77.8% | 53.4% |
| Terminal-Bench 2.0 | 82.0% | 65.4% |

特にサイバーセキュリティの領域では、「ほぼすべての熟練した人間のセキュリティ研究者を上回る」と Anthropic 自身が述べています。

## Mythos Preview が発見したゼロデイ脆弱性

Mythos Preview が内部テストで発見した脆弱性は衝撃的です。

- **OpenBSD の 27 年間未検出の脆弱性**: 長年のセキュリティ監査をすり抜けていたバグを特定
- **FFmpeg の 16 年間のファジングを回避した欠陥**: 自動テストでは発見できなかった脆弱性を発見
- **FreeBSD のリモートコード実行脆弱性（CVE-2026-4747）**: RPCSEC_GSS 実装のスタックオーバーフロー。認証なしでシステムを完全に制御できる
- **Linux カーネルの複数脆弱性チェーン**: 個別の脆弱性を組み合わせて権限昇格を実現

これらは「主要 OS およびブラウザ全体で数千件」発見された深刻度の高い脆弱性の一部に過ぎません。

## Claude Mythos Preview が一般公開されない理由

脆弱性情報が悪意ある攻撃者に渡れば攻撃に悪用されるため、Anthropic は一般公開を見送りました。代わりに **Project Glasswing** という業界横断の取り組みを通じて、限定的にアクセスを提供しています。

### Project Glasswing の参加企業

約 40 の組織がアクセス権を持ち、以下の企業が中心メンバーです。

- **テクノロジー**: Amazon Web Services、Apple、Google、Microsoft、NVIDIA
- **セキュリティ**: CrowdStrike、Palo Alto Networks、Broadcom、Cisco
- **金融**: JPMorgan Chase
- **オープンソース**: Linux Foundation

### Anthropic の経済的コミットメント

- **1 億ドル**: 参加組織への利用クレジット
- **250 万ドル**: Linux Foundation の Alpha-Omega および OpenSSF への寄附
- **150 万ドル**: Apache Software Foundation への寄附

## 脆弱性の発見と修正のギャップ

Fortune の報道によると、業界のベテランは「真の問題は脆弱性を見つけることではなく、修正することだ」と指摘しています。数千件の脆弱性が一度に発見されても、修正のための人的リソースとプロセスが追いつかない恐れがあります。未修正の脆弱性が公知となれば、むしろリスクが増大します。

Mythos Preview は脆弱性の発見を劇的に加速させましたが、修正のパイプラインをどう構築するかが次の課題です。

## 金融業界への影響

Mythos Preview の発表は金融業界にも大きな衝撃を与えました。Bloomberg の報道によると、財務長官スコット・ベッセントと FRB 議長ジェローム・パウエルが、Goldman Sachs、Citigroup、Morgan Stanley、Bank of America、Wells Fargo の CEO たちを財務省に緊急招集しました。

金融システムはソフトウェアの上に構築されています。Mythos クラスの AI が脆弱性を大量に発見できるということは、金融インフラのセキュリティに対する根本的な再評価が必要であることを意味します。JPMorgan Chase が Project Glasswing の参加企業に含まれているのも、この危機感の表れでしょう。

## まとめ

Claude Mythos Preview は、AI の能力が「ほぼすべての熟練した人間を上回る」段階に達したことを示す象徴的なモデルです。

- **能力**: 主要 OS・ブラウザの数千件のゼロデイ脆弱性を自律的に発見
- **公開範囲**: 一般公開なし。Project Glasswing を通じて約 40 組織に限定提供
- **投資**: 1 億ドル超の経済的コミットメント
- **課題**: 発見した脆弱性の修正体制の構築

セキュリティ業界にとって、AI がもたらす「攻撃と防御の非対称性」をどう管理するかが、今後の最重要テーマとなるでしょう。

## 参考リンク

- [Claude Mythos Preview - red.anthropic.com](https://red.anthropic.com/2026/mythos-preview/)
- [Project Glasswing: Securing critical software for the AI era](https://www.anthropic.com/glasswing)
- [Anthropic Releases Claude Mythos Preview with Cybersecurity Capabilities - InfoQ](https://www.infoq.com/news/2026/04/anthropic-claude-mythos/)
- [Bessent, Powell Summon Bank CEOs to Urgent Meeting - Bloomberg](https://www.bloomberg.com/news/articles/2026-04-10/anthropic-model-scare-sparks-urgent-bessent-powell-warning-to-bank-ceos)
- [Anthropic caused panic that Mythos will expose cybersecurity weak spots - Fortune](https://fortune.com/2026/04/13/cybersecurity-anthropic-claude-mythos-dario-amodei-tech-ceo/)
