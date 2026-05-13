---
title: "ブラック・ショールズの IV：50年来の難問に閉形式の陽解法が登場"
date: 2026-04-30
lastmod: 2026-04-30
slug: "black-scholes-iv-closed-form-schadner"
draft: false
source_url: "https://github.com/hdknr/blogs/issues/1#issuecomment-4349360681"
categories: ["その他"]
tags: ["ブラック・ショールズ", "インプライド・ボラティリティ", "クオンツ", "オプション取引", "数理ファイナンス"]
---

リヒテンシュタイン大学のクオンツ研究者 Wolfgang Schadner 氏が、ブラック・ショールズ・モデルのインプライド・ボラティリティ（IV）を直接算出する閉形式の陽解法を発表した。オプション理論が確立されてから約50年間、IV の計算にはニュートン法などの反復数値解法が用いられてきたが、この研究によって初めて解析的な陽解が得られた。

## 背景：なぜ IV の計算が難しいのか

ブラック・ショールズ式はコールオプション価格 $C$ を以下の形で与える:

$$C = S \cdot N(d_1) - K e^{-rT} \cdot N(d_2)$$

ここで $d_1, d_2$ はボラティリティ $\sigma$（と他のパラメータ）の非線形関数である。市場で観測されるのはオプション価格 $C$ であり、そこから $\sigma$（＝インプライド・ボラティリティ）を逆算する必要がある。

この逆算問題は閉形式の解が存在しないとされてきたため、実務では:

- ニュートン・ラフソン法
- 二分探索
- Let-It-Be（LIB）近似など

の数値・近似手法が用いられてきた。これらは反復計算や初期値の設定を必要とし、精度を高めると計算コストが増加するトレードオフを抱えていた。

## Schadner の発見：逆ガウス分布との同一視

Schadner 氏は、ブラック・ショールズのコール価格を**逆ガウス分布の生存確率（Survival Probability）**として表現できることに着目した。

> ブラック・ショールズのコール価格は、逆ガウス分布の生存確率として書ける。
> 等価的に、これはバリアンス空間における確率として表現される。

この表現を逆転させると、インプライド・ボラティリティが**逆ガウス分布の分位関数（Quantile Function）**によって陽に表現される:

ここで $C$ は市場観測価格、$S$ は原資産価格、$K$ は行使価格、$r$ は無リスク金利、$T$ は満期を表す。

$$\sigma = f(\text{逆ガウス分位関数}, C, S, K, r, T)$$

式の左辺には $\sigma$ のみ、右辺には市場で直接観測可能なオプション入力値だけが並ぶ（$\sigma$ が**陽に**＝左辺に直接分離した形で求まる）。

## 手法の特徴

| 項目 | 従来の数値解法 | Schadner の陽解法 |
|------|--------------|-----------------|
| 反復計算 | 必要 | 不要 |
| 近似 | 必要（場合による） | 不要 |
| 初期値 | 必要 | 不要 |
| 境界条件 | 必要 | 不要 |
| 精度 | 実装依存 | 機械精度 |
| 速度 | 基準（1×） | **約 3.4 倍（≈3.4×）** |

数値テストでは、機械精度（machine precision）で IV を復元できることが確認されており、既存の最先端ベンチマークと比較して約3.4倍高速とされている。さらに計算は評価1回あたり約0.305マイクロ秒で完了する。

## 論文情報

- **タイトル**: An Explicit Solution to Black-Scholes Implied Volatility
- **著者**: Wolfgang Schadner（スイス）
- **arXiv**: [arXiv:2604.24480](https://arxiv.org/abs/2604.24480)（2026年4月27日投稿、5月1日改訂）
- **分類**: Mathematical Finance (q-fin.MF), Computational Finance (q-fin.CP)
- **SSRN**: [papers.ssrn.com/sol3/papers.cfm?abstract_id=6649499](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=6649499)

## デモ実装（Python）

Schadner 氏本人が Python によるデモコードを公開している:

- **GitHub**: [wol-fi/direct_vola](https://github.com/wol-fi/direct_vola)

リポジトリの説明:
> Demo code for direct Black-Scholes implied-volatility calculation from normalized call prices via the inverse-Gaussian quantile representation.

## オプション市場への影響

この発見はオプション取引・クオンツファイナンスの実務において、以下の分野への応用が期待される:

- **高頻度取引（HFT）**: IV の計算ボトルネックが解消され、レイテンシ削減に寄与
- **リスク管理**: 大規模ポートフォリオの IV グリッド計算が高速化
- **学術的意義**: 50年以上「存在しない」とされてきた陽解の発見は、ブラック・ショールズ理論の理解を根本から更新する

## まとめ

インプライド・ボラティリティの計算は「反復数値解法が必須」という50年来の常識が覆された。逆ガウス分布との関係を利用した Schadner の陽解法は、機械精度・既存手法比3.4倍の高速性を実現しており、オプション理論と実務の両面で大きな意義を持つ。

論文は arXiv（[arXiv:2604.24480](https://arxiv.org/abs/2604.24480)）で無料公開されており、Python デモも [GitHub](https://github.com/wol-fi/direct_vola) で利用可能だ。
