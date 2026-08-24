---
title: "CLAUDE.md は「指示書」ではなく「憲法」——200行の壁とレベル別の育て方"
date: 2026-08-04
lastmod: 2026-08-24
slug: "claude-md-constitution-levels"
draft: false
source_url: "https://github.com/hdknr/blogs/issues/556#issuecomment-5174555217"
description: "CLAUDE.md は200行を超えると精度が落ちるという Anthropic 公式の指針を起点に、.claude/rules/ によるパス限定ロード、Hooks による強制ブロック、auto memory による学習蓄積まで、初心者・中級者・上級者向けの段階別運用を整理する。"
categories: ["AI/LLM"]
tags: ["claude-code", "claude", "CLAUDE.md", "hooks", "auto-memory"]
---

X で流れてきた投稿がきっかけで、CLAUDE.md の運用を改めて整理し直した。投稿自体は「CLAUDE.md をなんとなく書いてるなら、初心者・中級者・上級者のどこで詰まってるか一発でわかる」という煽り文句付きのスレッドで、リンク先には Claude Code の運用ノウハウを発信しているアカウントの解説記事がぶら下がっていた。

内容自体はよくできていて、CLAUDE.md を「毎回のやりとりで指示するだけのファイル」ではなく「プロジェクトの最高法規」として設計するという主張は的を射ている。ただ、記事中の具体的な数値（コスト削減率や個人の運用規模）は運営者の自己申告であり、外部から検証できるものではない。そこで本記事では、**Claude Code 公式ドキュメントで裏が取れる部分だけを技術的な骨格として採用**し、検証できない数値は「そう紹介されている」という扱いで参考情報にとどめる形で書き直した。

## 結論から

- CLAUDE.md は**200行を超えると文脈を圧迫し、指示への追従率が落ちる**——これは公式ドキュメントに明記されている指針であり、憶測ではない
- 「メインは薄く、詳細は分ける」の分離先は3つある：`.claude/rules/`（パス限定で条件付きロード）、[スキル](https://code.claude.com/docs/en/skills)（呼び出し時のみロード）、auto memory（Claude 自身が書く学習ログ）
- CLAUDE.md は「お願い」であり強制力を持たない。**強制したいルールは Hooks（PreToolUse 等）で物理的にブロックする**——この区別が上級者と中級者を分ける最大のポイント

## なぜ200行なのか——公式ドキュメントの根拠

Claude Code の公式メモリドキュメント（[How Claude remembers your project](https://code.claude.com/docs/en/memory)）には次のように明記されている。

> **Size**: target under 200 lines per CLAUDE.md file. Longer files consume more context and reduce adherence.

つまり「200行」という数字は都市伝説やX上のバズワードではなく、Anthropic 自身が推奨値として置いている閾値だ。理由もシンプルで、CLAUDE.md はセッション開始時に**丸ごとコンテキストウィンドウへ展開**される。会話の本題とは無関係な行が延々と並んでいれば、その分だけモデルが「今この瞬間に関係あるルール」を見分けるコストが上がる。

元ネタのスレッドでは「500行で崩壊する」「特定のルールだけが無視されるのではなく全ルールが均等に薄まる」といった、もう一段具体的な言い方をしていたが、この閾値の出典は運営者の実測ベースの経験則であり、Anthropic が公式に定量化しているものではない。方向性としては公式の指針と整合するが、「500行」という数字そのものは検証不能な参考情報として読んでおくのが安全だ。

## CLAUDE.md は1枚のファイルではなく「層」の集合

公式ドキュメントを読むと、CLAUDE.md 相当の仕組みは実質的に6つのレイヤーに分かれている。

| レイヤー | 場所 | 読み込まれるタイミング |
|---|---|---|
| Managed policy | `/etc/claude-code/CLAUDE.md` 等 | 常時（組織全体） |
| User instructions | `~/.claude/CLAUDE.md` | 常時（自分の全プロジェクト） |
| Project instructions | `./CLAUDE.md` | 常時（プロジェクトメンバー共有） |
| Local instructions | `./CLAUDE.local.md` | 常時（自分だけ、gitignore対象） |
| Rules（条件付き） | `.claude/rules/*.md` | `paths` に一致するファイルを開いたときだけ |
| Auto memory | `~/.claude/projects/<project>/memory/` | 常時（`MEMORY.md` の先頭200行 or 25KB） |

ここで注意したいのは「近い場所のルールほど優先される」という言い方だ。公式ドキュメントの説明はもう少し正確で、**全ての CLAUDE.md は上書きではなく連結（concatenate）される**。ディレクトリツリーを遡って見つかった順に、ルートから作業ディレクトリに向かって連結される。つまり「作業ディレクトリに近いファイルほど後に読まれる」ということだ。モデルは会話の後半で読んだ情報を重視する傾向があるため、結果として「近い場所のルールが効きやすい」という現象が起きる。これは厳密な優先順位制御ではなく、**連結順による事実上の効果**だと理解しておくと、期待値のズレを防げる。

## 初心者：まず `/init` を叩いて、削って、書き足す

Claude Code には `/init` コマンドがあり、コードベースを解析してビルドコマンドやテスト手順、プロジェクトの慣習を含む CLAUDE.md の初期版を自動生成してくれる。公式ドキュメントも「既存の CLAUDE.md があれば `/init` は上書きせず改善案を出す」仕組みを持つと説明している。

ここで一番多い失敗は、**自動生成された内容をそのまま使い続けること**だ。`/init` が出す内容には「ファイルを読めばわかること」（ディレクトリ構成やライブラリ一覧）が多く含まれる。これはモデル自身がコードから導出できる情報であり、CLAUDE.md に固定費として書いておく必要はない。

初心者がやるべきことは3つだけ。

1. `/init` を実行する
2. 出力を読んで、コードを見れば分かる説明を削る
3. 「見ただけではわからないこと」——独自ルール、環境の癖、過去の失敗から得た教訓、触ってはいけない場所——だけを書き足す

公式ドキュメントも同じ判断基準を「Specificity」として挙げている。

> "Use 2-space indentation" instead of "Format code properly"
> "Run `npm test` before committing" instead of "Test your changes"

抽象的な精神論ではなく、**検証可能な具体的な指示**にするほど追従率が上がる、という点は公式・実践知の両方で一致している。

## 中級者：`.claude/rules/` でパス限定ロードを設計する

CLAUDE.md が育ってくると、「このルールはフロントエンドの作業のときだけ関係する」「このルールはテストを書くときだけ関係する」という行が増えてくる。これを全部メインの CLAUDE.md に残すと、無関係な作業をしているときにも毎回コンテキストを消費する。

ここで使うのが `.claude/rules/` ディレクトリだ。ここに置いた Markdown ファイルは、YAML フロントマターの `paths` フィールドでファイルパターンを指定できる。

```markdown
---
paths:
  - "src/api/**/*.ts"
---

# API Development Rules

- All API endpoints must include input validation
- Use the standard error response format
```

`paths` を指定しないルールファイルは `.claude/CLAUDE.md` と同じ優先度で常時ロードされるが、`paths` を指定したルールは**該当パターンに一致するファイルを Claude が実際に開いたときだけ**コンテキストに入る。公式ドキュメントは次のように明言している。

> Rules load into context every session or when matching files are opened.

つまり「特定の作業をしたときだけ自動で読み込まれる」という元ツイートの説明は、この `paths` frontmatter の挙動として正確に裏が取れる。中級者が最初にやるべきことは、CLAUDE.md の各行に「これがなかったら次のセッションでミスするか」を問い、Noなら削除、Yesだが特定作業限定なら `.claude/rules/` に切り出す、という棚分けだ。

なお、頻繁に参照しない長い手順書（デプロイ手順やインシデント対応フローなど）は、ルールファイルよりも[スキル](https://code.claude.com/docs/en/skills)に置く方が適している。スキルは呼び出されたとき、あるいはモデルが関連性を判断したときにのみロードされ、ルールファイルよりもさらにオンデマンド性が高い。

## 上級者：CLAUDE.md は「お願い」、Hooks は「強制」

CLAUDE.md には構造的な弱点がある。公式ドキュメントもこれを隠さず書いている。

> Claude treats them as context, not enforced configuration. ... Settings rules are enforced by the client regardless of what Claude decides to do. CLAUDE.md instructions shape Claude's behavior but are not a hard enforcement layer.

どれだけ「必ず確認しろ」「テストを実行してから保存しろ」と書いても、それは指示であって強制ではない。文脈が長くなったり、他の指示と競合したりすれば、モデルはその行を無視する可能性がある。

「絶対に守らせたいルール」を物理的にブロックするための仕組みが Hooks だ。`PreToolUse` フックを使えば、特定のツール呼び出しが実行される**前**に介入し、許可・拒否を強制的に決定できる。

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "${CLAUDE_PROJECT_DIR}/.claude/hooks/block-rm.sh"
          }
        ]
      }
    ]
  }
}
```

CLAUDE.md と Hooks の使い分けは、公式ドキュメントの一文に凝縮されている。

> If the instruction is something that must run at a specific point, such as before every commit or after each file edit, write it as a hook instead. Hooks execute as shell commands at fixed lifecycle events and apply regardless of what Claude decides to do.

「〜してほしい」で済むものは CLAUDE.md、「〜しないと先に進めない」ものは Hooks——この線引きができるかどうかが、中級者と上級者を分ける実質的な境界線だと言える。

## Auto memory：セッションを越えて学習が蓄積される仕組み

元ツイートの記事では「354ファイルのメモリーが最大の武器」という表現があった。ファイル数は運営者個人の環境の話で検証はできないが、**仕組みそのものは公式機能として存在する**。

Claude Code には CLAUDE.md とは別に auto memory という仕組みがあり、ユーザーの訂正や好みから Claude 自身が学習内容を書き残す。保存先は `~/.claude/projects/<project>/memory/` で、`MEMORY.md` が索引として機能し、詳細は個別のトピックファイルに分割される。読み込み時は `MEMORY.md` の先頭200行または25KBまでが毎セッションでロードされ、トピックファイルは必要になったときだけ読み込まれる。

CLAUDE.md との役割分担は次のようになる。

| | CLAUDE.md | Auto memory |
|---|---|---|
| 誰が書くか | 人間 | Claude 自身 |
| 内容 | 指示・ルール | 学習・パターン |
| 用途 | コーディング規約、ワークフロー、アーキテクチャ | ビルドコマンド、デバッグの知見、Claude が発見した好み |

「ミスが起きたら CLAUDE.md にルールを追加する」という運用は、複利で効くというのは元記事の主張どおりだが、すべてを人間がメインの CLAUDE.md に手で書き込む必要はない。訂正や好みの共有は auto memory に任せ、CLAUDE.md には「プロジェクトの方針」「多くのセッションで再利用される具体的な手順」だけを残す、という分業が現実的だ。

## レベル別アクションプラン

- **初心者（CLAUDE.md がまだない）**：`/init` を実行し、コードから分かる説明を削り、独自ルールと環境の癖を書き足す
- **中級者（CLAUDE.md はあるが肥大化している）**：全行に「これがなかったらミスするか」を問い、特定作業限定のルールは `.claude/rules/` の `paths` frontmatter に切り出す。常時ロードされる行数を200行以下に近づける
- **上級者（さらに信頼性を上げたい）**：「絶対に守らせたいルール」を Hooks（`PreToolUse` 等）に移し、CLAUDE.md では表現しきれない強制力を確保する。合わせて auto memory の内容を定期的に `/memory` で見直す

どのレベルでも共通するのは、CLAUDE.md は「書いて終わり」のドキュメントではなく、セッションを重ねるたびに削り・足していく運用対象だという点だ。ただし、その運用判断は「Anthropic の公式ドキュメントが何を保証しているか」と「発信者個人の経験則」を分けて読むところから始めた方がいい——今回、元スレッドを掘って一番学びになったのはその区別自体だった。

## 参考リンク

- [元ツイート（Claude Code アカデミア, @ClaudeCode_aca）](https://x.com/ClaudeCode_aca/status/2084112017275879907)
- [How Claude remembers your project — Claude Code Docs](https://code.claude.com/docs/en/memory)
- [Hooks reference — Claude Code Docs](https://code.claude.com/docs/en/hooks)
- [Skills — Claude Code Docs](https://code.claude.com/docs/en/skills)
