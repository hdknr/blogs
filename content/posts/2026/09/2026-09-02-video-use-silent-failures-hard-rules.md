---
title: "Video Use の「沈黙する失敗」— ffmpeg が成功しても動画が壊れる 5 つの罠と 12 の Hard Rules"
date: 2026-09-02
lastmod: 2026-09-02
slug: "video-use-silent-failures-hard-rules"
description: "browser-use/video-use の 4 か月分の修正は、ほぼ全部が ffmpeg 正常終了・ファイル生成済み・ローカル再生 OK なのに中身が壊れている「沈黙する失敗」だった。音声トラックの取り違え、HDR メタデータの残留、フレームレート固定、回転メタデータ誤判定、字幕のセーフゾーン侵入と、12 の Hard Rules を整理する。"
draft: false
source_url: "https://github.com/hdknr/blogs/issues/297#issuecomment-5505621428"
categories: ["AI/LLM"]
tags: ["claude-code", "動画編集", "Video Use", "ffmpeg", "エージェント設計", "ElevenLabs"]
---

Claude Code で動画編集を自動化する [browser-use/video-use](https://github.com/browser-use/video-use) が、公開から 4 か月あまり経った 2026 年 9 月になって SNS で再び話題になっています。ツールそのものは [2026 年 4 月に紹介記事を書いた](/blogs/posts/2026/04/video-use-claude-code-video-editing/)ので、機能一覧をもう一度並べても意味がありません。

代わりに面白いのは、**この 4 か月に入った修正がほぼ全部同じ形をしていた**ことです。どれも ffmpeg が正常終了し、`final.mp4` が生成され、ローカルで再生すると問題なく見える。壊れているのは中身だけ。エージェントにパイプラインを任せるときに何が本当に危険なのかが、リポジトリの Git 履歴にそのまま残っています。

以下は 2026-09-02 時点の `main` を対象にした調査です。

## 前提: Video Use とは

素材フォルダに撮影データを置き、Claude Code に「これをローンチ動画にして」と伝えると、`edit/final.mp4` が返ってきます。Codex や OpenClaw でも動きます。

設計の核心は **LLM が動画を「見ない」** こと。主な入力は ElevenLabs Scribe の単語単位トランスクリプト（約 12KB の `takes_packed.md`）で、判断に迷う箇所だけフィルムストリップ + 波形の PNG を生成します。3 万フレームを画像として読ませる素朴なアプローチと比べて、桁違いに少ないトークンで編集判断を成立させる設計です。

仕組みの詳細は[前回の記事](/blogs/posts/2026/04/video-use-claude-code-video-editing/)にまとめてあります。以下はその続きです。

## 4 か月の修正はほぼ全部「沈黙する失敗」だった

2026 年 4 月 18 日以降にマージされた修正のうち、中心になったのは次の 5 種類です。

- **音声トラックの取り違え** — 画面収録の 2 トラック録音で、マイクではなくアプリ音声を書き起こす
- **HDR メタデータの残留** — アップロード先の再エンコードで色が潰れる
- **フレームレートの固定** — 30fps / 60fps のソースが黙って 24fps に間引かれる
- **回転メタデータの誤判定** — 縦動画が横に潰れる、あるいは縦に伸びる
- **字幕のセーフゾーン侵入** — TikTok / Reels / Shorts の UI が字幕を覆う

対象の失敗がパイプラインのどの段階で起きるかで並べたのが下図です。以下に出てくる `#N` は、すべて video-use リポジトリの Pull Request 番号です。

![Video Use のパイプラインを左列に縦に並べ、各段階から右側の赤いボックスへ点線で結んで「沈黙する失敗」を示した図。Transcribe 段階から音声トラックの取り違え、セグメント抽出段階から HDR メタデータの残留とフレームレートの固定、連結段階から回転メタデータの誤判定、字幕焼き込み段階からプラットフォーム UI への埋没が伸び、それぞれの右隣に緑色の修正内容が並んでいる。図の下部には自己評価ループの検査範囲が破線で示され、5 種類のうち字幕の 1 件だけがその範囲に入っている](/blogs/images/video-use-silent-failure-points.png)

この 5 種類に共通するのは、**どれもエラーを出さない**という点です。終了コードは 0、出力ファイルは存在する、再生もできる。検証を「コマンドが通ったか」「ファイルができたか」で済ませると、全部すり抜けます。

### 音声トラックの取り違え — OBS の 2 トラック録音でナレーションが消える（[#134](https://github.com/browser-use/video-use/pull/134)）

一番わかりやすい例です。`extract_audio` が `-map` を指定せずに ffmpeg を呼んでいたため、既定のストリーム選択が働いていました。

画面収録では音声トラックが 2 本あるのが普通です。OBS はトラック 0 にアプリケーション音声、トラック 1 にマイクを書きます。ffmpeg の既定選択は「チャンネル数が最も多い音声ストリーム」を拾うので、**アプリ音声をアップロードしてナレーションを黙って捨てる**ことが起こりました。

結果として返ってくるのは、エラーではなく「別物の書き起こし」です。修正では `--audio-track` で 0 から始まるストリーム番号を明示できるようになり（既定は 0）、あわせて無音トラックのアップロードを拒否するようになりました。

### HDR メタデータの残留 — アップロード後だけ色が潰れる（[#6](https://github.com/browser-use/video-use/pull/6)）

iPhone は HLG、他のミラーレス機は PQ で HDR 撮影するのが既定です。`extract_segment` は `-pix_fmt yuv420p` でビット深度を変換していましたが、転送特性のメタデータ（`arib-std-b67` / `smpte2084`）を出力に残していました。

メタデータを尊重するプレイヤーは、8bit の値を HDR として解釈します。画面録画ソフトや、TikTok・Instagram・YouTube・X のアップロード時再エンコード経路がほぼ全部これに該当します。色が潰れ、過度に彩度が上がります。

やっかいなのは、**macOS の QuickTime が再生時にトーンマップしてしまう**点です。ローカルで確認する限り正常に見え、アップロードして初めて崩れる。修正で HLG/PQ ソースを Rec.709 SDR へトーンマップするようになりました。

### フレームレートの固定 — 30fps / 60fps が黙って 24fps に間引かれる（[#55](https://github.com/browser-use/video-use/pull/55)）

`extract_segment` が全出力を 24fps で決め打ちしていました。30fps や 60fps のスマホ・Web カメラ・画面録画を黙って間引くうえ、SKILL.md 側の「ユーザーが指定しない限りソースに合わせる」という規定と矛盾していました。

修正では、まず `avg_frame_rate` を計測して出力レートを決めます（取れなければ `r_frame_rate`、それも失敗したら 24 にフォールバック）。レートはレンダリングごとに最初のソースから 1 つだけ決めます。ロスレス連結には全セグメントのレートが揃っている必要があるからです。`--fps` は整数・小数・有理数を受け付けるので、`30` でも `29.97` でも `30000/1001` でも指定できます。

### 回転メタデータと縦動画 — 縦動画が横に潰れる・縦に伸びる（[#29](https://github.com/browser-use/video-use/pull/29) / [#137](https://github.com/browser-use/video-use/pull/137)）

これは 2 段構えで面白いケースです。

まず #29 で、縦動画（height > width）が幅基準でスケールされて横に潰れる問題が直りました。`is_portrait_source()` を追加し、縦なら `scale=-2:1280`（ドラフト）／`scale=-2:1920`（最終）に切り替えるようにしたものです。

ところがこれでは足りませんでした。スマホやカメラのファイルは、**横向きで符号化されたフレーム + 90 度や 270 度の表示回転**という形で保存されるのが一般的です。ffmpeg はフィルタ適用前に自動回転します。ところが `render.py` は符号化寸法だけを比較していたため、横向きのスケール軸を選び、縦に伸びた過大な出力を作っていました。#137 では、display-matrix の回転（表示時の回転量を持つメタデータ。レガシーな `rotate` タグも含む）を ffprobe の 1 回のプローブで読み取ります。90/270 度なら実効寸法を入れ替えてから軸を選びます。

### 字幕がプラットフォーム UI に埋まる — TikTok / Reels / Shorts のセーフゾーン（[#5](https://github.com/browser-use/video-use/pull/5)）

`render.py` の `bold-overlay` キャプションスタイルが `MarginV=35` で出荷されていました。1080×1920 の縦出力では、これは TikTok / Instagram Reels / YouTube Shorts / Snap の UI が覆う帯の中に入ってしまいます。字幕、ユーザー名、音源のティッカー、右レールのアクションが下端から約 25〜30% を占めるため、アップロード後に字幕が隠れます。

実際に出荷された TikTok 書き出しで、2 ワード大文字の字幕が 1920px の高さに対して下端から約 240px の位置に座っているのが観測されています。`MarginV` を 90 に引き上げて解決しました。

これも**ローカル再生では完璧に見える**タイプの失敗です。

## だから Hard Rules は taste から切り離された

こうした修正の積み重ねを踏まえて、`SKILL.md` は自分の指示を 2 種類に明示的に分けています。

> **5. Artistic freedom is the default.** Every specific value, preset, font, color, duration, pitch structure, and technique in this document is a *worked example* from one proven video — not a mandate. (…) **The only things you MUST do are in the Hard Rules section below.** Everything else is yours.

（＝この文書に出てくる具体的な数値・プリセット・技法はすべて「実際に通った 1 本の動画での一例」であり、必須なのは Hard Rules だけ、という宣言です。）

そして Hard Rules 側にはこう書かれています。

> These are the things where deviation produces silent failures or broken output. They are not taste, they are correctness. Memorize them.

（＝ここから外れると「沈黙する失敗」か壊れた出力になる。これは趣味ではなく正しさの問題だ、と。）

12 項目のうち、ここまでの話と直結するものを挙げます（読みやすさのために並べ替えており、原文の番号順ではありません）。

- **字幕はフィルタチェーンの最後に適用する** — オーバーレイより先に焼くとオーバーレイが字幕を隠す。サイレント故障。
- **セグメント単位で抽出 → ロスレス `-c copy` で連結** — 単一パスのフィルタグラフにすると、オーバーレイ追加時に全セグメントを二重エンコードする。
- **全セグメント境界で 30ms のオーディオフェード** — `afade=t=in:st=0:d=0.03,afade=t=out:st={dur-0.03}:d=0.03`。入れないとカットごとにポップノイズが鳴る。
- **オーバーレイは `setpts=PTS-STARTPTS+T/TB` を使う** — さもないとオーバーレイ区間にアニメーションの途中が映る。
- **マスター SRT は出力タイムライン基準のオフセット** — `output_time = word.start - segment_start + segment_offset`。連結後に字幕がずれる。
- **単語の内側で切らない** — カット端は必ず Scribe のトランスクリプトの単語境界にスナップさせる。
- **カット端に必ずパディング** — 作業域は 30〜200ms。Scribe のタイムスタンプは 50〜100ms ドリフトするので、パディングで吸収する。

残る 5 項目は次のとおりです。

- 単語単位の verbatim ASR のみ使う（SRT / フレーズモードは秒未満のギャップ情報を失う）
- トランスクリプトはソース単位でキャッシュする
- 複数アニメーションはサブエージェントで並列生成する
- 戦略はユーザー承認前に実行しない
- 出力は必ず `<videos_dir>/edit/` に置く

エージェントに自由度を与えるツールの設計として、この線引きは示唆的です。非交渉の規則とそれ以外を分ける発想は、[Harness Engineering](/blogs/posts/2026/06/harness-engineering-ai-agents/) で言うランタイム側の設計そのものです。「12 hard rules, artistic freedom elsewhere」— **壊れ方が沈黙する箇所だけを非交渉の規則として抜き出し、それ以外は全部任せる**という構造になっています。

## 自己評価ループでも捕まらないものがある

Video Use にはレンダリング後の自己評価ループがあり、`timeline_view` を**出力側**に対して全カット境界で走らせて、映像の飛び、オーディオのポップ、隠れた字幕を検出します（問題があれば最大 3 回まで修正・再レンダリング）。

ただし、ここまで挙げた失敗のうち自己評価で捕まりそうなのは #5（字幕が隠れる）くらいです。フレームレートの間引き、HDR タグの残留、音声トラックの取り違えは、**カット境界のフィルムストリップと波形を見ても異常に見えません**。自己評価は「カットの継ぎ目」を検査する仕組みであって、コンテナ全体の属性やソース選択の妥当性を検査する仕組みではないからです。

エージェントに自己検証させる設計では、検証の視野がどこまでかを意識しておく必要がある、という話でもあります。ループの停止条件をどう置くかは [Claude Code チーム公式ガイド「ループ設計」](/blogs/posts/2026/07/claude-code-loop-design-guide/) でも中心的な論点です。

## 4 月以降の機能追加 — HyperFrames・MIT ライセンス・ワンペースト導入

沈黙する失敗の修正以外にも、次の変更が入りました。

- **HyperFrames をアニメーションエンジンに追加**（[#13](https://github.com/browser-use/video-use/pull/13)） — 従来は Web 系アニメーションの選択肢として Remotion しか名前が挙がっておらず、エージェントが既定で Remotion を選びがちでした。ブラウザネイティブな HTML/CSS/GSAP のコンポジションには [HyperFrames](https://github.com/heygen-com/hyperframes) のほうが合うため、Remotion / Manim / PIL と並ぶ第一級の選択肢になり、スキル指示も「スロットごとにエンジンを選ぶ」形に変わりました。HyperFrames 単体の実例は [Claude Code × HyperFrames でバズった Instagram リールを AI 完全再現](/blogs/posts/2026/04/claude-code-hyperframes-reel-recreation/) にまとめてあります。
- **MIT ライセンスの付与**（[#32](https://github.com/browser-use/video-use/pull/32)、2026-05-10） — 4 月時点では README が「100% open source」と書いていた一方でライセンスファイルがありませんでした。現在は MIT です。
- **`install.md` とワンペースト導入プロンプト**（[#9](https://github.com/browser-use/video-use/pull/9)） — README にそのまま貼れる導入プロンプトが用意され、クローン・依存インストール・スキル登録・API キー入力までエージェント自身が処理します。導入手順を自分で追う必要はほぼなくなりました。
- **依存管理が `uv` 前提に** — `uv sync` が第一候補で、`pip install -e .` はフォールバックです。
- **Codex など他エージェントへの対応が明文化** — スキルの登録先として `~/.claude/skills/`（Claude Code）と `~/.codex/skills/`（Codex）が併記されるようになりました。
- **常時稼働エージェントでの編集運用** — 自前の VPS や Telegram から指示を出す運用（Browser Use Box）が案内されるようになりました。

導入の必須要件は 4 月から変わっていません。リポジトリ、`ffmpeg`（および `ffprobe`）、そして ElevenLabs API キーの 3 つです。HyperFrames・Remotion・Manim といったアニメーションエンジンは、プロジェクトが実際に必要とした時点で遅延インストールされます。具体的な手順は[前回の記事](/blogs/posts/2026/04/video-use-claude-code-video-editing/)か `install.md` を参照してください。

## SNS で拡散された紹介の誤り — 「完全無料」ではない

今回この記事の発端になった SNS 投稿には、事実確認で 2 点の補正が必要でした。

| 主張 | 実際 |
|------|------|
| 「約 2.2 万⭐・無料」 | スター数は 23,169（2026-09-02 時点）。リポジトリは MIT で無料だが、**ElevenLabs API キーが必須**で、Scribe の従量課金は別途かかる |
| 「導入は ffmpeg を入れてリポジトリを渡すだけ」 | `ffmpeg` に加えて ElevenLabs API キーの設定が必要。`install.md` も「このマシンに必要なものは 3 つ」としてリポジトリ・ffmpeg・API キーを挙げている |

「完全無料でローカル完結」と読める紹介が多いですが、音声認識は外部 API に依存します。ここは導入前に押さえておくところです。

## まとめ

Video Use の 4 か月は、機能追加の歴史というより **「成功したように見える失敗」を 1 件ずつ特定していった歴史**でした。音声トラックの取り違え、HDR メタデータの残留、フレームレートの決め打ち、回転メタデータの誤判定、字幕のセーフゾーン侵入 — どれもコマンドは通り、ファイルはでき、手元では正しく見える。

エージェントにパイプラインを任せるとき、本当に効くのはこの種の失敗です。落ちてくれるバグはエージェントが自分で気づいて直しますが、沈黙するバグは成果物が世に出るまで残ります。`SKILL.md` が 12 項目を taste から切り離して「correctness」として明記しているのは、その非対称性への対処だと読めます。

自分のワークフローをエージェントに任せるときも、同じ問いが使えます。**この工程が黙って間違った出力を出すとしたら、どこで、何を見れば気づけるのか。** 「コマンドが通った＝完了」ではない、という同じ論点は [AI エージェントにリファクタさせるときの「完了の定義」の引き方](/blogs/posts/2026/07/ai-refactor-completion-boundary/) でも扱っています。

## 参考リンク

- [browser-use/video-use](https://github.com/browser-use/video-use) — 本体（MIT）
- [SKILL.md](https://github.com/browser-use/video-use/blob/main/SKILL.md) — Hard Rules と編集技法
- [install.md](https://github.com/browser-use/video-use/blob/main/install.md) — 導入手順
- [HyperFrames](https://github.com/heygen-com/hyperframes) — HTML を書いて動画をレンダリングするアニメーションエンジン
- [Video Use — Claude Code で動画編集を完全自動化するオープンソーススキル](/blogs/posts/2026/04/video-use-claude-code-video-editing/) — 前回の紹介記事
