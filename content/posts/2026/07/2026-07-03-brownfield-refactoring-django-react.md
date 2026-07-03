---
title: "brownfield を壊さず作り替える — Django × React/TS リファクタリング実践ガイド"
date: 2026-07-03
lastmod: 2026-07-03
slug: "brownfield-refactoring-django-react"
draft: false
description: "Django と React/TS の既存コード（brownfield）を壊さずリファクタリングする実践ガイド。特性テストで振る舞いを固定し、6 ステップのワークフロー・段階置換パターン・スタック別ツールで安全に作り替える。"
categories: ["Web開発"]
tags: ["django", "react", "typescript", "refactoring", "brownfield"]
---

新規開発（greenfield）と、改修を重ねてきた既存コード（brownfield）では、リファクタリングの難しさの質がまるで違う。前回の [Ponytail の記事](/blogs/posts/2026/06/ponytail-ai-agent-minimal-code/)では「greenfield で効き、成熟コードベースでは薄まる」という適用条件に触れたが、では **その成熟コードベース側を、どう安全に作り替えるのか**。この記事は Django（Python）と React（TypeScript）という具体的なスタックに落とし込んだ実践プレイブックだ。

## greenfield と brownfield

はじめに用語を整理しておく。

- **greenfield（グリーンフィールド）**: 既存のコードや制約に縛られず、更地から作る新規開発。
- **brownfield（ブラウンフィールド）**: すでに動いていて、改修を重ねてきた既存のコードベース。

工事現場で、更地（緑の草地）に新築するか、既存の建物（茶色く汚れた土地）を改修するか、という比喩から来ている。実運用中の業務システムのほとんどは brownfield であり、そこでの最大の敵は **過剰実装ではなく「正しさの後退」**——間違った項目名、間違った ID、データ不整合、意図しない挙動変化だ。

だからこそ brownfield のリファクタリングは、たった一つの鉄則に集約される。**振る舞いを固定してから、内部を動かす。**

## 大原則：安全網を先に張る

リファクタリングの定義は「外部から見た振る舞いを変えずに内部構造を改善する」こと。であれば、振る舞いを固定する手段を最初に用意しなければ、そもそも安全に始められない。

- **特性テスト（Characterization Test、現状記録テスト）**: 「正しい仕様」ではなく「今の実際の挙動」を記録するテスト。レガシーの仕様書は信用できない前提で、現状を凍結してから触る。Michael Feathers『レガシーコード改善ガイド』の中核テクニックだ。
- **Golden Master / スナップショット**: 個別アサーションを書きにくい複雑なロジックや UI は、出力・レンダリング結果を丸ごと比較して守る。
- **境界の契約**: API・DB スキーマ・イベントなど外部インターフェースに特性テストを置いてから、内部実装を動かす。境界が動かなければ利用側は無傷。
- **1 コミット 1 リファクタリング**: 振る舞い変更と構造変更を同じコミットに混ぜない。問題の切り分けが桁違いに楽になる。

## ワークフロー：6 ステップ

安全網を軸に、作業は次の 6 ステップで進める。順序に意味がある——安全網（②凍結）より前に大きく動かさない、削除（⑥）を最後に回す、が要点だ。

![Django と React/TS の brownfield リファクタリングを 6 ステップで示したワークフロー図。安全網を張るフェーズ（①計測・②凍結・③継ぎ目）と動かすフェーズ（④変換・⑤段階置換・⑥削除）に分かれ、各ステップに対応するツールが添えられている。⑥削除から①計測へ戻る反復の矢印も描かれている。](/blogs/images/brownfield-refactoring-django-react-workflow.png)

1. **計測** — 「変更頻度 × 複雑度」が高いホットスポットから着手する。感覚ではなく Git 履歴と静的解析で優先順位を出す。
2. **凍結** — 着手箇所の現状挙動を特性テストで記録する。ここが安全網の要。
3. **継ぎ目** — 依存を差し込めるテスト可能な接合点を作る。
4. **変換** — 振る舞い不変の小さな変更を、IDE と codemod で積む。
5. **段階置換** — 大物は一括でなく、新旧を並行稼働させながら機能単位で差し替える。
6. **削除** — 置換完了後に旧経路と未使用コードを消す。

## 段階置換のパターン

「直そうとすると芋づるで壊れる」brownfield 特有の依存に効く、言語非依存の定番手法を押さえておく。

| パターン | やること | Django / React での当てはめ |
|---|---|---|
| **Strangler Fig** | 新実装を旧の周りに這わせ、機能単位で差し替え、最後に旧を除去 | DRF の ViewSet を 1 本ずつ新サービスへ / ルート単位で新コンポーネントに切替 |
| **Branch by Abstraction** | 抽象層を挟み新旧を並行稼働、フラグで切替えながら main で継続 | Django のサービス interface + フラグ / React は Context・Hook を抽象境界にしフラグ分岐 |
| **Mikado Method** | 目標→前提依存をグラフ化し葉から潰す。行き詰まったら即 revert | 循環 import や密結合モデルの分解 / 相互依存した hook・store の解きほぐし |
| **Seam の導入** | テスト用に振る舞いを差し込める継ぎ目を作る | ORM 呼び出しをリポジトリ層へ / 副作用を `useXxx` フックに隔離し純粋化 |
| **Scientist（並行検証）** | 旧経路と新経路を本番で並行実行し、結果の差異だけ記録 | クリティカルな集計 API の無停止移行 / 表示ロジック差し替え時の出力比較 |

コツは、大物ほど段階置換で「いつでも戻せる」状態を保つこと。Mikado Method の「行き詰まったら即 revert」は、深い依存を相手にするときの精神的な安全弁でもある。

## スタック別ツールベルト

6 ステップの各役割に、Django と React/TS の具体的なツールを紐づける。

### Django（Python）

| ツール | 役割 | 用途 |
|---|---|---|
| `pytest-django` + `coverage.py` | 凍結・計測 | 特性テストの土台。`--cov` で薄い箇所を可視化してから着手する |
| `syrupy` / `inline-snapshot` | golden master | API レスポンスや複雑な戻り値をスナップショット比較。個別アサーションが辛い箇所を丸ごと固定 |
| `django-test-migrations` | 凍結 | マイグレーションの前後整合と後方互換を検証。データ移行の事故を止める |
| `import-linter` | 継ぎ目・契約 | app 間・パッケージ間の層依存をルール化し CI で強制。禁止依存の混入を防ぐ |
| `django-extensions` | 計測 | `show_urls` / `graph_models` で URL・モデル依存を可視化し、結合の実態を掴む |
| `ruff` + `mypy` / `pyright` | 変換 | Lint/format を一手に。型は段階導入し、触った箇所から厳格化する |
| `libcst` / `django-upgrade` / `pyupgrade` | 変換（codemod） | 構文木ベースの一括変換。API 移行や古い書式の機械置換を安全に |
| `django-waffle` | 段階置換 | フィーチャーフラグで新旧経路を切替え、Strangler / Branch by Abstraction を運用 |
| `nplusone` / `django-silk` | 計測 | N+1 とクエリのホットスポットを検出。ORM の遅延評価が絡む変更の副作用を見張る |
| `vulture` | 削除 | デッドコード候補を検出。旧経路除去の最終段で使う |

### React（TypeScript）

| ツール | 役割 | 用途 |
|---|---|---|
| `Vitest` / `Jest` + Testing Library | 凍結 | ユーザー視点の振る舞いを固定。実装詳細でなく「見える挙動」でテストするのが特性テストの肝 |
| `Playwright` | 凍結（E2E） | クリティカルなユーザーフローを端から端まで凍結。境界を跨ぐ改修の安全網 |
| `Storybook` + `Chromatic` | golden master | コンポーネントの見た目をビジュアルリグレッションで固定。UI の意図しない変化を検出 |
| `dependency-cruiser` / `madge` | 計測・契約 | 循環依存と層違反を検出しルール化。import の依存グラフを CI で強制 |
| `ts-morph` / `ast-grep` / `jscodeshift` | 変換（codemod） | AST ベースの一括変換。props リネーム、API 差し替え、パターン置換を機械的に |
| `typescript-eslint` / `Biome` | 変換 | Lint/format。Biome は大規模でも高速。ルールを段階的に厳格化 |
| `tsc --strict` + `type-coverage` | 変換 | strict を一括でなくファイル単位で導入し、型カバレッジを ratchet（後退禁止）で上げる |
| フィーチャーフラグ | 段階置換 | ルート・コンポーネント単位で新旧を切替え、Strangler を安全に進める |
| React DevTools Profiler / `react-scan` | 計測 | 再レンダリングのホットスポットを特定。Context 分割や memo 化の効果を before/after で確認 |
| `knip` | 削除 | 未使用の export・依存・ファイルを検出。旧経路撤去の最終段で安全に削る |

## AI エージェントは「テストで挟んで」使う

Claude Code や Cursor は brownfield でも強力だが、主要リスクが「正しさ」である以上、丸投げではなくテストで検証するループに乗せるのが前提だ。前回の Ponytail 記事で触れた「成熟コードベースでは『少なく書く』最適化がリスクと直交する」という論点と、ここは地続きである。

具体的には次の小刻みループを回す。

1. **現状を凍結させる** — まず AI に特性テスト（RTL / pytest / snapshot）を書かせ、今の挙動を固定する。
2. **小さく変換を依頼** — 抽出・リネーム・1 パターンの codemod など、範囲を絞った変更だけ頼む。
3. **テストで不変を確認** — 特性テストが緑のまま＝振る舞い不変。赤なら即 revert して粒度を下げる。

大きな一括変換を一発で頼まないこと。「凍結 → 小変換 → 検証」の小刻みループのほうが、成熟コードベースでは圧倒的に安全で速い。AST を理解する `ts-morph` / `libcst` のような codemod と組み合わせると役割分担が効く。AI は「変換の設計」に集中し、機械的な置換はツールが担う。

たとえば「凍結」ステップの特性テストは、正しい仕様を問わず、いま返っている出力をそのまま固定するだけでよい。

```python
# Django: 現状のレスポンスをスナップショットで固定する（syrupy）
def test_order_summary_characterization(client, snapshot):
    res = client.get("/api/orders/42/summary/")
    assert res.status_code == 200
    assert res.json() == snapshot  # 初回実行時の出力を「現状」として記録
```

```tsx
// React: 実装詳細でなく「見える挙動」を固定する（RTL）
test("送信ボタンを押すと確認ダイアログが出る", async () => {
  render(<OrderForm order={order} />);
  await userEvent.click(screen.getByRole("button", { name: "送信" }));
  expect(screen.getByRole("dialog")).toBeInTheDocument();
});
```

これらが緑のまま内部を作り替えられれば、振る舞いは不変だと機械的に保証できる。

## 危険地帯：この 2 スタックで壊れやすいところ

「振る舞い不変」の落とし穴。ここは特性テストを厚めに張ってから触る。

**Django**

- **マイグレーション / データ移行**: データマイグレーションは実質不可逆。`RunPython` は reverse を書き、staging の実データコピーで必ず検証してから本番へ。
- **signals と暗黙の副作用**: `post_save` 等の signal はコードを追うだけでは見えない。呼び出し経路をテストで固定してから移設・削除する。
- **ORM の遅延評価と N+1**: QuerySet の評価タイミングを変える改修はクエリ数を激変させる。`nplusone` と件数アサーションで見張る。

**React**

- **`useEffect` の依存配列**: 依存配列の変更は実行回数＝副作用の回数を変える。Testing Library で発火回数まで固定してからロジックを動かす。
- **Context / state の再レンダリング**: Context 分割や store 差し替えは再描画範囲を変え、パフォーマンスと表示順序に波及する。Profiler で before/after を比較する。
- **非同期・レース条件**: データ取得の並び替えや中断処理の改修はレースを生む。Playwright で実フローを凍結してから触る。

## まとめ

brownfield のリファクタリングは、greenfield のような「良い設計を最初から選ぶ」ゲームではなく、**「動いているものを壊さずに少しずつ良くする」ゲーム**だ。だからこそ、

1. まず安全網（特性テスト）を張り、
2. 計測でホットスポットを選び、
3. 継ぎ目を作って小さく変換し、
4. 大物は段階置換で可逆に進め、
5. 最後にデッドコードを削除する。

Django と React/TS には、この各ステップを支える成熟したツールが揃っている。AI エージェントも「テストで挟む小刻みループ」に乗せれば、正しさを損なわずに変換速度だけを上げられる。過剰実装を抑える Ponytail が greenfield の武器なら、こちらは brownfield の武器だ。

- 参考: Michael Feathers『レガシーコード改善ガイド』
- 参考: Martin Fowler『リファクタリング（第2版）』
- 参考: Maude Lemaire『Refactoring at Scale』
