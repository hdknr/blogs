---
title: "自動テスト修正パイプライン（監査ツール + 自律修正スキル）"
description: "大規模 Django で pytest の失敗を冪等な Issue キューに変換し、AI エージェントのループで1件ずつ自律修正する3フェーズ・パイプラインの設計。なぜ自動マージしないのかの安全境界も解説する"
date: 2026-07-15
lastmod: 2026-07-15
aliases: ["自動テスト修正", "test audit", "自律修正スキル", "pollution", "phantom failure"]
related_posts:
  - "/posts/2026/07/auto-test-fix-pipeline/"
tags: ["claude-code", "agent", "django", "pytest", "自律システム"]
---

## 概要

テスト失敗を「人が直す」から「AI エージェントがキューを自律消化する」へ変える保守パイプラインの設計。**Phase 1（監査ツール）→ Phase 2（Issue 起票）→ Phase 3（自律修正スキル）** の3段で、pytest 失敗という非構造のノイズを冪等な Issue キューに変換し、**マージは必ず人手**という安全境界を引いた上で AI に消化させる。

## 詳細

### 3フェーズ

| Phase | 成果物 | 役割 |
|---|---|---|
| 1 | 監査ツール（`test_audit`） | ランナー＋冪等 Issue レポーター |
| 2 | `--report` による per-file Issue 起票 | 失敗を1ファイル1 Issue に正規化 |
| 3 | 自律修正スキル | エージェントのループで Issue を1件ずつ修正 → PR |

### 監査ツールは triage → verify → report

- **triage**: サブパッケージ単位の bulk 実行で候補を高速に絞る（速いが pollution 込み）
- **verify**: 候補を per-file 単独実行で再検証し real（単独でも失敗）と **pollution（単独 green、まとめると失敗）** を切り分ける
- **report**: real 失敗ごとに安定マーカー（`<!-- test-audit:<path> -->`）で Issue を作成/更新し、green 復帰は自動クローズ（**冪等同期**）

> 最重要の教訓: **サブパッケージ全体を1プロセスでまとめて流すと本物でない失敗（pollution）が混ざる。だから失敗判定は必ずファイル単独で再実行して確かめる。**

### 自律修正スキル（1イテレーション = 1 Issue）

Issue を1件取得 → 単独再現 → トレースと `git log -S` で根本原因を特定し A/B/C/D に分類する。

| 分類 | 内容 | 対応 |
|---|---|---|
| A. 仕様ドリフト | テスト期待値/フィクスチャが後発仕様に未追従 | テスト側を現行仕様へ追従 |
| B. obsolete | 機能削除で import/対象が存在しない | テストを削除 |
| C. テスト基盤 | setUp のマスタ/前提データ欠落 | setUp を補完 |
| D. 実バグ疑い | プロダクト挙動が誤り／テスト修正が本番バグの隠蔽になる | **直さず** `needs-human` へエスカレーション |

**安全方針**: マージしない（PR 作成まで）／実バグ疑いは自動修正しない（迷ったら D に倒す）／プロダクトコードは原則変更しない／修正は隔離した作業ツリーで。

### なぜ test-only な diff でも自動マージしないか

「テストコードしか変わらない」＝「リスクもテスト内に閉じる」ではない。**リスクは本番の correctness 側に漏れ出る**。最大の失敗モードは D を A と誤判定してテストを直し「正しく失敗していた検知を消す」こと。AI は「正しく直す」より「green にする」に滑りやすく（assert 弱化・skip/xfail 追加・mock で対象を消す）、per-file green を根拠にした自動マージは pollution の教訓と矛盾する。ただし **B（obsolete の純粋削除）が CI 相当でも green かつ assert 弱化を検出しない** なら段階的に自動マージへ昇格させるのは妥当。

### 副次効果: ツール自身の幻の失敗（phantom failure）

自動 Issue 化で監査ツール自身の false-positive が2系統炙り出された。(a) 翻訳ファイル `.mo` が VCS 管理外でチェックアウト直後に存在せず gettext が原文にフォールバック（監査起動時に `msgfmt` で自前コンパイルして解消）。(b) pytest のログ出力行を結果行と誤認する正規表現の緩さ（`FAILED`/`ERROR` の後は単一スペースのみ・node を実テストパスに限定して解消）。**自動化は自分の欠陥を「誤った Issue」として可視化するぶん直しやすい。**

## 関連ページ

- [自律改善システムの設計](/blogs/wiki/concepts/autonomous-system-design/) — 安全ゲートと progressive autonomy の原則
- [AI エージェントにリファクタさせる時の完了の定義](/blogs/wiki/concepts/ai-refactor-completion-boundary/) — 横断スイープと敵対的レビュー
- [Django の on_commit と TestCase](/blogs/wiki/guides/django-on-commit-testcase/) — 監査が炙り出した非局所な副作用の具体例
- [エージェントループ設計](/blogs/wiki/concepts/agent-loop-design/) — ループでキューを消化する仕組み

## ソース記事

- [テスト失敗を「人が直す」から「キューを自律消化する」へ — 監査ツール + 自律修正スキルの設計](/blogs/posts/2026/07/auto-test-fix-pipeline/) — 2026-07-01
