---
title: "「値は計算されていた。ただ届いていなかっただけ」— LLMエージェントプロンプトのハードコード問題"
date: 2026-03-27
lastmod: 2026-03-27
draft: false
description: "LLMエージェントのプロンプトにリスクパラメータがハードコードされていたため、動的調整が反映されなかったバグの原因と修正。テンプレート変数化、結合テスト、CLAUDE.mdルール追加による再発防止策を解説。"
categories: ["AI/LLM"]
tags: ["Claude Code", "LLM", "prompt", "agent", "Python"]
---

## TL;DR

自律型トレーディングシステムで、投資目標の進捗に応じてリスクパラメータを動的に調整する機能を実装した。計算ロジックは正しく動いていたが、**計算結果がエージェントのプロンプトに届いていなかった**。プロンプト内の数値がプレーンテキストでハードコードされていたため、エージェントは常に保守的な固定値に従い続けていた。

---

## 背景

trader は日本株・ビットコインの自律型トレーディングシステムで、Claude をマルチエージェントとして使い、日次の投資提案を生成する。

システムには安全規約があり、エクスポージャー上限（60%）や現金比率下限（30%）などのリスクパラメータが定義されている。投資目標（goal）システムを導入し、目標への進捗ペースに応じてこれらのパラメータを動的に調整する機能を実装した。

## 何が起きたか

### 期待していた動作

```text
goal 評価: behind（目標に遅れている）
  → AdjustmentProposal: exposure_limit=70%, cash_ratio_min=20%
    → エージェント: 「エクスポージャー70%以内、現金比率20%以上」で提案作成
```

### 実際の動作

```text
goal 評価: behind（目標に遅れている）
  → AdjustmentProposal: exposure_limit=70%, cash_ratio_min=20%
    → エージェント: 「エクスポージャー60%以内、現金比率30%以上」で提案作成 ← 固定値のまま！
```

goal の評価は正しく行われ、`propose_adjustment()` は適切な調整値を返していた。しかしエージェントが参照するプロンプトには、値がハードコードされていた：

```markdown
<!-- portfolio.md -->
- 総エクスポージャー60%以内
- 現金比率30%以上を維持
```

一方、同じプロンプト内の `max_position_pct`（1取引あたりポジション上限）は既にテンプレート変数化されていた：

```markdown
- 1取引あたり総資産の最大{{max_position_pct}}%
```

**同じファイル内に、テンプレート化された値とハードコードされた値が混在していた。**

## 原因分析

### 時系列

1. PR #255 で `{{max_position_pct}}` のテンプレート置換を `orchestrator.py` に導入
2. PR #257 で goal システムに `AdjustmentProposal`（`exposure_limit` / `cash_ratio_min`）を実装
3. しかし #257 でエージェントプロンプトへの注入パイプラインが未実装のままマージされた

### 構造的原因

| 原因 | 説明 |
|------|------|
| **接続の欠落** | goal システムは「評価→提案→レポート」として完結しており、「提案→プロンプト注入」が設計から漏れた |
| **テンプレート化の不統一** | `max_position_pct` だけテンプレート化済み。同じパターンの適用が漏れた |
| **テスト境界の問題** | `propose_adjustment()` の返り値テストはあったが、値がプロンプトに到達するかの結合テストがなかった |
| **自然言語ハードコード** | `.md` ファイル内の日本語テキストに埋め込まれた数値は、コードレビューで「値の出所」を問われにくい |

最後の点が特に興味深い。プログラムコードなら `EXPOSURE_LIMIT = 60` というハードコードはレビューで指摘されやすいが、自然言語プロンプト内の「エクスポージャー60%以内」は「説明文」として読み飛ばされやすい。

## 修正内容

### 1. プロンプトのテンプレート変数化

```markdown
<!-- Before -->
- 総エクスポージャー60%以内
- 現金比率30%以上を維持

<!-- After -->
- 総エクスポージャー{{exposure_limit}}%以内
- 現金比率{{cash_ratio_min}}%以上を維持
```

対象ファイル: `portfolio.md`, `risk.md`, `researcher.md`

### 2. orchestrator.py での動的注入

```python
def _get_safety_params() -> tuple[float, float]:
    """goal の AdjustmentProposal からエクスポージャー上限・現金比率下限を取得."""
    goal = get_active_goal()
    if goal is None:
        return 60.0, 30.0  # デフォルト値

    evaluation = evaluate_goal(...)
    proposal = propose_adjustment(evaluation.pace_status)
    return proposal.exposure_limit, proposal.cash_ratio_min


def _load_prompt(filename: str) -> str:
    text = path.read_text(encoding="utf-8")
    # ... 既存の max_position_pct 置換 ...

    if "{{exposure_limit}}" in text or "{{cash_ratio_min}}" in text:
        exposure_limit, cash_ratio_min = _get_safety_params()
        text = text.replace("{{exposure_limit}}", f"{exposure_limit:g}")
        text = text.replace("{{cash_ratio_min}}", f"{cash_ratio_min:g}")

    return text
```

### 3. 週次レビューレポートの動的化

`reporter.py` の「現在値」カラムもハードコードから動的取得に変更。

### 4. テスト追加（4件）

```python
class TestSafetyParamsInjection:
    def test_default_params_without_goal(self):
        """goal 未設定時はデフォルト値が返る"""

    def test_behind_pace_returns_aggressive_params(self):
        """behind ペースでは積極的なパラメータが返る"""

    def test_prompts_contain_injected_values(self):
        """テンプレート変数がプロンプトに正しく注入される"""

    def test_no_hardcoded_safety_values_in_prompts(self):
        """プロンプトに安全規約のハードコード値が残っていないことを検証"""
```

最後のテストは**回帰防止テスト**で、プロンプトファイル内にエクスポージャーや現金比率のハードコード値が存在しないことを正規表現で検証する。

### ペース別パラメータ

| ペース | エクスポージャー上限 | 現金比率下限 |
|--------|-------------------|------------|
| ahead | 50% | 40% |
| on_track | 60% | 30% |
| behind | 70% | 20% |
| critical | 変更なし | 変更なし |

## 再発防止策

### CLAUDE.md にルールを追加

```markdown
- **エージェントプロンプトに数値パラメータを追加・変更する場合**:
  - `agents/prompts/*.md` にハードコードせず、テンプレート変数（`{{変数名}}`）を使用
  - `orchestrator.py` の `_load_prompt()` でテンプレート変数を展開するコードを追加
  - 値の生成元（`goal/evaluation.py` 等）と消費先（プロンプト）の**両方**を変更したか確認
```

これは Claude Code の `CLAUDE.md` に追加したルールで、AI アシスタントが今後のコード変更時にこのパターンを自動的に適用する。

## 教訓

### 1. LLM プロンプトは「コード」として扱え

自然言語で書かれたプロンプトも、パラメータを含む以上はコードと同等に扱うべき。マジックナンバーの禁止、テンプレート変数の使用、テストによる検証 — ソフトウェアエンジニアリングの原則はプロンプトにも適用される。

### 2. 「生成元」と「消費先」の接続を検証せよ

値を生成するモジュールと消費するモジュールが分かれている場合、パイプラインの接続テストが必要。単体テストで各モジュールが正しく動いていても、接続が切れていれば意味がない。

### 3. 既存パターンの適用漏れに注意

`max_position_pct` でテンプレート変数のパターンが確立されていたのに、新しいパラメータに同じパターンを適用し忘れた。パターンを導入したら、同じカテゴリのすべての箇所に適用されているか確認するチェックリストが有効。

### 4. 回帰防止テストは「仕組み」で守る

「ハードコード禁止」をルールとして文書化するだけでなく、テストコードで機械的に検出する仕組みを入れた。人間（とAI）の注意力に頼らず、CI が自動的にキャッチする。
