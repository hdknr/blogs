---
title: "Impeccable — AI コーディングツールのフロントエンド設計を底上げするスキルライブラリ"
date: 2026-03-09
lastmod: 2026-03-09
draft: false
source_url: "https://github.com/hdknr/blogs/issues/1#issuecomment-4020349617"
categories: ["AI/LLM"]
tags: ["claude-code", "agent", "ui", "ux"]
---

AI コーディングツール（Claude Code、Cursor、Gemini CLI など）で UI を生成すると、「動くけど見た目がイマイチ」になりがちだ。Impeccable は、AI に設計のボキャブラリーを教えることで、生成される UI の品質を引き上げるスキルライブラリだ。

## Impeccable とは

[Impeccable](https://impeccable.style/) は、Paul Bakaus 氏が開発した AI コーディングツール向けの設計スキル拡張だ。Anthropic の公式 `frontend-design` スキルをベースに、17個のコマンドと厳選されたアンチパターン集を提供する。

「派手なデザイン」ではなく「洗練された仕上がり」を目指すのが特徴で、中国のインディー開発者コミュニティでも注目を集めている。

## 対応ツール

- Cursor
- Claude Code
- Gemini CLI
- Codex CLI
- VS Code Copilot
- Google Antigravity
- Kiro

## インストール方法

### npx（推奨）

```bash
npx skills add pbakaus/impeccable
```

### Claude Code の場合

```bash
# プロジェクト単位
cp -r dist/claude-code/.claude your-project/

# グローバル
cp -r dist/claude-code/.claude/* ~/.claude/
```

### Cursor の場合

```bash
cp -r dist/cursor/.cursor your-project/
```

Nightly チャンネルの使用と Agent Skills の有効化が必要。

## 17個のコマンド一覧

Impeccable は用途別に整理された17個のコマンドを提供する：

### セットアップ

| コマンド | 機能 |
|---------|------|
| `/teach-impeccable` | 初期セットアップ。プロジェクトの設計コンテキストを収集 |

### 品質チェック系

| コマンド | 機能 |
|---------|------|
| `/audit` | 技術品質チェック（アクセシビリティ、パフォーマンス、レスポンシブ） |
| `/critique` | UX 設計レビュー |

### 調整・改善系

| コマンド | 機能 |
|---------|------|
| `/normalize` | デザインシステム標準への統一 |
| `/polish` | 最終調整（スペーシング、アニメーション等の微調整） |
| `/distill` | 本質の抽出。複雑性を削除 |
| `/clarify` | UX コピーの改善 |
| `/optimize` | パフォーマンス最適化 |
| `/harden` | エラー処理、多言語化対応 |

### デザイン強化系

| コマンド | 機能 |
|---------|------|
| `/animate` | 意図的なモーションの追加 |
| `/colorize` | 戦略的な色の導入 |
| `/bolder` | 地味な設計を強調 |
| `/quieter` | 大胆すぎる設計を調整 |
| `/delight` | 喜びの瞬間（マイクロインタラクション等）を追加 |

### 構造化系

| コマンド | 機能 |
|---------|------|
| `/extract` | 再利用可能なコンポーネントに分離 |
| `/adapt` | 異なるデバイスへの対応 |
| `/onboard` | オンボーディングフロー設計 |

## 実践的な使い方

基本的なワークフローは `/audit` で問題を検出し、他のコマンドで順番に修正していく流れだ：

```
/audit           # まず問題を検出
/normalize       # デザインの不一致を修正
/polish          # スペーシングやアニメーションを微調整
/distill         # 不要な複雑性を削除
```

特定の要素にフォーカスすることもできる：

```
/audit header
/polish checkout-form
```

## アンチパターン集

Impeccable には、LLM が陥りがちな設計のアンチパターンも含まれている：

- **使い古されたフォント**の回避（Arial、Inter など）
- **グレーテキスト on カラー背景**の禁止
- **純粋なブラック/グレー**の禁止（常にティント処理すべき）
- **カード内カードのネスト**の回避
- **バウンス/エラスティックイージング**の禁止

これらのルールが AI に適用されることで、「AI っぽい」デザインから脱却できる。

## 7つの設計参考資料

スキルには以下の分野のベストプラクティスが組み込まれている：

1. **Typography** — フォントペアリング、モジュラースケール
2. **Color & Contrast** — OKLCH、ダークモード、アクセシビリティ
3. **Spatial Design** — スペーシング、グリッド、視覚階層
4. **Motion Design** — イージング曲線、スタッガリング
5. **Interaction Design** — フォーム、フォーカス状態、ローディングパターン
6. **Responsive Design** — モバイルファースト、流体設計
7. **UX Writing** — ボタンラベル、エラーメッセージ

## 関連記事 — AI コーディングエージェントと UI/UX

Impeccable は「ツールで設計品質を自動改善する」アプローチだが、本ブログではコーディングエージェントと UI/UX の関係をさまざまな角度から取り上げてきた：

- **[バイブコーディングでデザインを劇的に改善する方法](/blogs/posts/2026-03-01-44d3e82b0c355de783233377c5f8fcff/)** — UI コンポーネント名で「構造」を指示するテクニック。Impeccable の `/normalize` や `/extract` が自動化する領域を、プロンプトの工夫で実現するアプローチ
- **[Claude-Native Designer — Figma MCP × Claude Code ワークフロー](/blogs/posts/2026-03-05-1f81385148befa3ee0e980408c174676/)** — デザイナーが Figma と Claude Code を組み合わせて「作る人」になるワークフロー。Impeccable はこのワークフローの仕上げ工程（`/polish`, `/audit`）を強化できる
- **[「Figmaは100%不要」宣言の真意](/blogs/posts/2026-03-04-4a6596b99ae8da9028f432e6c8d0b7f5/)** — Claude Code がデザインとコードの境界を溶かすという議論。Impeccable はまさにこの「コードの中でデザイン品質を担保する」ツール
- **[Claude Code 時代、UI デザイナーの仕事は軽くならない](/blogs/posts/2026-03-05-b03527dbe6ad00bfac9b4b431248b524/)** — 「整える仕事」の自動化と評価軸の変化。Impeccable のようなツールが「整える仕事」を自動化する一方、デザイナーに求められる判断力は変わらないという視点

## まとめ

Impeccable は「AI にデザインの語彙を教える」というアプローチで、生成される UI の品質を底上げする。派手さではなく洗練さを追求する設計思想は、実務で使えるプロダクト開発に適している。Claude Code や Cursor でフロントエンド開発をしているなら、導入を検討する価値がある。
