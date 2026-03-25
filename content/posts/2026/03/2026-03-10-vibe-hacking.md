---
title: "Vibe Hacking とは何か：AI が変えるサイバー攻撃の新潮流"
date: 2026-03-10
lastmod: 2026-03-18
draft: false
source_url: "https://github.com/hdknr/blogs/issues/1#issuecomment-4031826348"
categories: ["セキュリティ"]
tags: ["security", "AI/LLM", "マルウェア"]
---

「Vibe Coding」が開発者の間で広まる中、同じ発想をサイバー攻撃に応用する「Vibe Hacking」が新たな脅威として注目されている。AI を使って、専門知識がなくてもマルウェアや攻撃スクリプトを生成できる時代が到来した。

## Vibe Hacking とは

Vibe Hacking は、AI を活用してサイバー攻撃のハードルを劇的に下げる手法・思想を指す。開発者が自然言語で AI にコードを書かせる「Vibe Coding」のダークサイドとも言える概念だ。

従来のハッキングには、ネットワークプロトコルの理解、脆弱性の発見、エクスプロイトコードの記述といった高度な技術スキルが必要だった。しかし Vibe Hacking では「ターゲットを指定するだけ」「経験不要」「AI が処理する」といった形で、技術的な障壁がほぼ消失する。

## 具体的な脅威

### AI 生成マルウェア

HP Wolf Security の脅威インサイトレポート（2025年10月〜12月）によると、攻撃者は AI で生成した感染スクリプトを実際の攻撃キャンペーンに使用している。偽のインボイス PDF を通じて、正規のプラットフォーム（Booking.com など）へリダイレクトする前にマルウェアをダウンロードさせる手口が確認されている。

### Flat-Pack Malware

複数の無関係な脅威グループが、同一のモジュール化されたマルウェアコンポーネントを再利用する「Flat-Pack Malware」も増加している。市販のマルウェア部品を組み立てるだけで、最小限の労力でカスタマイズされた攻撃キャンペーンを展開できる。

### 国家レベルの活用

パキスタン系の脅威アクター「Transparent Tribe」が、AI コーディングツールを使ってマルウェアを「Vibe Coding」し、インド政府やその海外大使館を標的にした事例も報告されている。

## なぜ危険なのか

### 攻撃コストの劇的な低下

脆弱性の発見からエクスプロイト作成までのコストは、かつて数週間と数千ドルを要した。AI によりこれがほぼゼロになりつつある。「スプレー＆プレイ」型の大規模攻撃ではなく、特定のシステムや企業、さらには個々の開発者をピンポイントで狙うマイクロターゲット攻撃が現実的になった。

### 検出回避能力の向上

HP の調査では、メール脅威の 14% 以上がゲートウェイスキャナーを回避している。AI が生成するコードは毎回微妙に異なるため、シグネチャベースの検出が困難になっている。

### Vibe Coding で作られたアプリの脆弱性

攻撃だけでなく、Vibe Coding で開発されたアプリケーション側も問題を抱えている。Veracode の GenAI コードセキュリティレポートによると、AI 生成コードの 45% にセキュリティ脆弱性が含まれている。AI はほぼ半分の確率で安全でない実装を選択する。

## 対策のポイント

### AI によるコードレビューの自動化

Vibe Coding で生成された全コードを人間がレビューするのは現実的ではない。コード生成が AI なら、レビューも AI で自動化するのが自然な流れだ。

例えば Claude Code には、PR 作成時に自動でセキュリティレビューを実行する仕組みがある。GitHub Actions と連携させれば、CI/CD パイプラインに組み込める。

```yaml
# .github/workflows/claude-review.yml
name: Security Review
on:
  pull_request:
    types: [opened, synchronize]
jobs:
  review:
    runs-on: ubuntu-latest
    steps:
      - uses: anthropics/claude-code-action@v1
        with:
          anthropic_api_key: ${{ secrets.ANTHROPIC_API_KEY }}
          prompt: |
            このPRのセキュリティ脆弱性をチェックしてください:
            - SQLインジェクション、XSS、CSRF
            - 認証・認可の不備
            - 秘密情報のハードコード
            - 依存パッケージの既知の脆弱性
```

ローカルでも `claude` コマンドで PR レビューを実行したり、hooks 機能でコミット前にセキュリティチェックを自動実行できる。「AI が書いたコードを AI がレビューする」というワークフローは、Vibe Coding 時代のセキュリティ対策として最も現実的なアプローチだ。

### その他の対策

1. **ゼロトラストアーキテクチャ** — AI 生成の攻撃は従来の境界防御を突破するため、ゼロトラストの採用が重要
2. **行動ベースの検知** — シグネチャベースではなく、異常な振る舞いを検知するアプローチへの移行
3. **セキュリティ教育の更新** — AI 時代の新しい脅威モデルについて、開発者・運用チームの意識を更新する

## まとめ

Vibe Hacking は、AI が攻撃者側にもたらす変革を端的に表す言葉だ。Vibe Coding が開発の民主化を進めるのと同様に、Vibe Hacking はサイバー攻撃の民主化を進めてしまう。防御側もまた AI を活用した検知・対応の自動化を進め、この非対称性に対応していく必要がある。

## 参考リンク

- [HP Research: From Vibe Hacking to Flat-Pack Malware](https://www.hp.com/us-en/newsroom/press-releases/2026/hp-research-low-effort-ai-attacks-beating-defenses.html)
- [Vibe Hacking: The Next Frontier in AI Cybersecurity Threats](https://www.uscsinstitute.org/cybersecurity-insights/blog/vibe-hacking-the-next-frontier-in-ai-cybersecurity-threats)
- [Vibe Hacking: How AI Is Reshaping Cybercrime](https://www.lmgsecurity.com/vibe-hacking-how-ai-is-reshaping-cybercrime-and-what-your-organization-can-do/)
