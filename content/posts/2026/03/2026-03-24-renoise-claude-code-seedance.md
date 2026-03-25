---
title: "Renoise：Claude Code + Seedance 2.0 で動画広告制作を100倍スケールさせるAIツール"
date: 2026-03-24
lastmod: 2026-03-24
draft: false
source_url: "https://github.com/hdknr/blogs/issues/1#issuecomment-4121767768"
categories: ["AI/LLM"]
tags: ["claude-code", "ai-video", "seedance", "広告", "自動化"]
---

Claude Code と ByteDance の Seedance 2.0 を組み合わせた動画広告制作ツール「Renoise」が登場した。1枚の商品写真から数百パターンの動画クリエイティブを自動生成できるという。

## Renoise とは

[Renoise](https://renoise.ai/) は「動画をつくるな、プログラムしろ（Don't make videos — program them）」をコンセプトに掲げる AI 動画制作ツール。Claude Code のコード生成能力と、ByteDance が開発した動画生成 AI「Seedance 2.0」を組み合わせることで、動画広告の制作を従来の100倍にスケールさせることを目指している。

主な特徴：

- 1枚の商品写真から数百パターンの動画クリエイティブを生成
- 手動編集ではなく、コードベースで動画を「設計・展開」するアプローチ
- 広告やマーケティング向けのクリエイティブ量産に特化

## Seedance 2.0 について

[Seedance 2.0](https://seed.bytedance.com/en/seedance2_0) は ByteDance の Seed 研究チームが開発した次世代 AI 動画生成モデル。2026年2月にベータ版が公開され、SNS で大きな話題となった。

### 主な機能

- **マルチモーダル入力**: テキスト、画像（最大9枚）、動画（最大3本）、音声（最大3ファイル）を組み合わせて動画を生成
- **音声・動画の同時生成**: デュアルチャンネルステレオ技術で映像と完全同期した音声を生成
- **高解像度出力**: ネイティブ 2K 解像度（2048×1080）に対応
- **高速生成**: 前モデル Seedance 1.5 Pro と比べて30%の速度向上
- **物理演算の改善**: 人物の動きや物体の相互作用がよりリアルに

## Claude Code との連携

Claude Code は Anthropic が提供する CLI ベースの AI コーディングアシスタント。Renoise では、Claude Code の自然言語によるコード生成能力を活かして、動画制作のワークフローをプログラマブルに制御する。

この仕組みにより：

- 動画の構成やテンプレートをコードで定義
- 商品画像やテキストを差し替えてバリエーションを自動生成
- 編集・プレビュー・書き出しをワークスペース内で完結

従来の動画制作が「1本ずつ手作業で編集」だったのに対し、Renoise は「テンプレートを設計してプログラムで量産」するパラダイムシフトを提案している。

## AI 動画広告制作の潮流

Renoise の登場は、AI を活用した動画広告制作が新しいフェーズに入ったことを示している。類似のアプローチとして、Remotion（React ベースの動画生成フレームワーク）と Claude Code を組み合わせた動画自動生成なども注目されている。

広告クリエイティブの A/B テストやパーソナライゼーションの需要が高まる中、「コードで動画を量産する」というアプローチは今後さらに広がりそうだ。

## 参考リンク

- [Renoise 公式サイト](https://renoise.ai/)
- [Seedance 2.0（ByteDance 公式）](https://seed.bytedance.com/en/seedance2_0)
- [@renoiseai（X）](https://x.com/renoiseai)
