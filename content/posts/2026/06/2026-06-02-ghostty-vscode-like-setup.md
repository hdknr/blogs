---
title: "Ghostty を VSCode みたいにする — FileTree・keifu・zellij で軽量なターミナル開発環境を組む"
date: 2026-06-02
lastmod: 2026-06-02
slug: "ghostty-vscode-like-setup"
draft: false
source_url: "https://github.com/hdknr/blogs/issues/1#issuecomment-4601461859"
categories: ["ツール/開発環境"]
tags: ["Ghostty", "ターミナル", "TUI", "zellij", "Claude Code"]
---

Claude Code でコーディングする時間が増えると、ふと気づくのが「VSCode って、けっこうメモリを食うな」という事実です。プロジェクトを 5 つも同時に開けば、エディタだけでメモリがカツカツになります。

[note の記事「GhosttyをVSCodeみたいにしよう！」](https://note.com/electrical_cat/n/n7a3b634a2b51)（Naoki | 電電猫猫 氏）では、まさにこの悩みを起点に、高速なターミナルエミュレータ **Ghostty** の上に VSCode 風の開発環境を再現する構成が紹介されていました。本記事ではその考え方を整理しつつ、使われている TUI ツール群を補足して紹介します。

## なぜターミナルで VSCode を再現するのか

VSCode の基本的な画面構成はだいたいこうなっています。

- 左サイドバー：ファイル一覧と Git のツリー表示
- 右側メイン：エディタ（または Claude Code）と、その下にターミナル

便利な一方で、Electron ベースの VSCode は 1 ウィンドウあたりのメモリ消費が大きく、プロジェクトを並行して開くほど重くなります。そこで「同じレイアウトを、軽量なターミナル上で組めないか？」という発想に至ります。

Ghostty は Mitchell Hashimoto 氏が開発する GPU アクセラレーション対応のターミナルエミュレータで、標準で画面分割（split）機能を持っています。この分割機能と、小さな TUI ツールを **LEGO のように組み合わせる**ことで、VSCode のレイアウトをそのまま再現するというのが今回のアプローチです。

> **前提**：以降の手順は Rust の `cargo` と Ghostty がインストール済みであることを前提にしています。FileTree・keifu・zellij はいずれも `cargo install` で導入できます。

![Ghostty の画面分割で VSCode 風レイアウトを再現する構成図。左の細いサイドバー列に上から FileTree（ファイルツリー）と keifu（Git 表示）を縦に並べ、右の広いメイン領域に Claude Code/エディタとターミナルを上下に配置している。メイン領域は zellij でセッション保存する。](/blogs/images/ghostty-vscode-like-setup-layout.png)

各パーツの役割は次のとおりです。

- **サイドバー（細い列）**：上に **FileTree**、下に **keifu**
- **メイン領域（広い列）**：上に **Claude Code / エディタ**、下に **ターミナル**
- 高頻度で触るプロジェクトは **zellij** のセッションとして保存しておく

## FileTree — VSCode 風のファイルツリー TUI

[FileTree](https://github.com/nyanko3141592/filetree) は、VSCode のファイル一覧をターミナル上で模倣した TUI ファイルエクスプローラです。記事の著者（電電猫猫 氏 = Naoki Takahashi 氏）自身が作ったツールで、Vim キーバインドに対応した高速・軽量なファイルブラウザになっています。

主な機能は以下のとおりです。

- VSCode 風のファイルツリー表示
- ファイル / フォルダの作成・リネーム・削除・コピー・移動
- ドラッグ＆ドロップ対応
- ファイルプレビュー（テキスト / 画像 / バイナリ）

Rust 製なので、`cargo` ですぐにインストールできます。

```bash
cargo install filetree
ft   # インストールされるバイナリ名は ft
```

著者が特に推しているのが**ドラッグ＆ドロップ対応**です。ターミナル上の FileTree にファイルをドロップすると、そのパスを取得してコピーします。直感的にファイルを追加できる仕組みです。

また、簡易的なクイックルック機能もあり、ファイルの中身をサッと確認できます。画像の場合はサムネイルレベルで表示されます。サイドバーのファイル一覧としては十分な機能です。

選択したファイル / ディレクトリのパスは他のペインへ渡せるので、エディタやターミナル側ですぐにそのパスへ移動できるのも実用的なポイントです。

> リッチなファイラーとしては `yazi` も人気ですが、著者いわく「リッチすぎる」。あくまでサイドバーの 1 パーツとして使いたい用途では、シンプルな FileTree のほうが好みだとのことです。

## keifu — シンプルで縦画面に強い Git ツリー表示

[keifu（系譜）](https://github.com/trasta298/keifu) は、Git のコミットグラフをターミナル上で可視化する TUI ツールです。記事の著者の会社の同僚（trasta298 氏）が作ったツールで、Rust + Ratatui で実装されています。

VSCode のサイドバーにある Git 表示のように使いたい、というのが採用理由です。サイドバーとして使う以上、横幅を取られると困ります。その点 keifu は **細い時は縦にスタックされ、広い時は横に展開される**という、サイドバー用途にぴったりな挙動をします。

keifu の特徴を整理するとこうなります。

- Unicode のコミットグラフをブランチごとに色分け表示
- ブランチラベル・日付・著者・短縮ハッシュ・メッセージの一覧
- コミット詳細パネル（フルメッセージと変更ファイルの +/- 統計）
- checkout / ブランチ作成・削除 / fetch などの基本的な Git 操作
- 画像プロトコル不要 — Unicode が使える端末ならどこでも動く

`lazygit` のような全部入り TUI が「やや過剰」に感じる場面でも、keifu は**コミット状態とブランチの確認・切り替え**という用途に絞っているのが心地よい、というのが著者の評価です。

```bash
cargo install keifu
keifu   # インストールされるバイナリ名は keifu
```

おもしろいのは、keifu が**あえて Diff を表示しない**点です。「Diff が見たいならメインの右上の画面で `git diff` を叩くし、大きい画面で見たいなら `lazygit` を使う。サイドバーにその機能は要らない」という割り切りです。小さなツールを組み合わせて環境を作る、という思想がよく表れています。

## zellij — セッションを保存して画面分割を自動化

「毎回手動で画面分割するの、面倒じゃない？」という疑問はもっともです。そこで terminal multiplexer の出番になります。

著者は `tmux` ではなく **zellij** を採用しています。tmux も優秀ですが、コマンドが覚えにくいのに対し、zellij はそのあたりが親切だからです。zellij も Rust 製で `cargo install zellij` で導入できます。よく使うプロジェクトのレイアウトを zellij のセッションとして保存しておけば、毎回ゼロから分割を組む手間がなくなります。

### zellij + Claude Code で日本語入力（IME）がずれる問題と対処

ひとつ実用上の注意があります。一部の IME では、**zellij + Claude Code の組み合わせで日本語入力が変な位置に出現する**という不具合が起きることがあります（zellij の issue トラッカーでも報告例があります）。

この症状が出る場合は、zellij ではなく **tmux** を使うのがおすすめです。コマンドは少し覚える必要がありますが、入力の不具合は回避できます。著者は tmux のコマンドを zellij 用に置き換えるコードを書いて対処したそうです。どうしても zellij を使いたい場合は、こうした工夫も選択肢になります。

## Ghostty の設定例（config の書き方）

記事で公開されていた Ghostty の設定（`~/.config/ghostty/config`）を紹介します。テーマ・フォント・背景の透過・分割移動のキーバインド・クイックターミナルなどがまとまっています（原文ママのため一部に重複行があります）。

```ini
theme = TokyoNight
maximize = true
font-family = PlemolJP35 Console NF
background-opacity = 0.8
macos-titlebar-style = tabs
background-blur = true
adjust-cell-height = 2
font-thicken = true
keybind = ctrl+h=goto_split:left
keybind = ctrl+l=goto_split:right
window-inherit-working-directory = true
shell-integration = detect

quick-terminal-position = "right"
quick-terminal-screen = "main"
quick-terminal-animation-duration = 0.3
keybind = "cmd+shift+t=toggle_quick_terminal"

clipboard-write = allow
clipboard-trim-trailing-spaces = true
macos-titlebar-style = tabs
window-new-tab-position = current
```

ポイントをいくつか挙げると、

- `keybind = ctrl+h=goto_split:left` / `ctrl+l=goto_split:right` で、Vim 風に分割ペイン間を移動できる
- `window-inherit-working-directory = true` で、新しいペインが現在の作業ディレクトリを引き継ぐ
- `quick-terminal-*` 系で、`cmd+shift+t` でサッと呼び出せるクイックターミナルを右側に配置
- `theme = TokyoNight` と `background-opacity = 0.8` + `background-blur` で見た目を整える

といった具合です。`font-family` の `PlemolJP35 Console NF` は日本語と Nerd Font に対応した等幅フォントで、TUI 中心の環境では効いてきます。

## まとめ — Ghostty + TUI で VSCode より軽い開発環境を

この構成のいちばんの魅力は、**重い統合 IDE を 1 つ抱えるのではなく、目的に絞った小さなツールを LEGO のように組み合わせる**という発想にあります。

- ファイル操作 → FileTree
- Git 確認 → keifu
- 画面分割とセッション → Ghostty + zellij
- 編集とエージェント → Claude Code

それぞれが軽量なので、5 プロジェクトを並行して開いてもメモリに余裕があります。そして著者が最後に書いているとおり、「自分で困ったらすぐにツールを作れる」のが今の時代の強みです。実際 FileTree は著者自身が、keifu は同僚が作ったものでした。

VSCode のメモリ消費に悩んでいる人や、ターミナル中心の開発スタイルに興味がある人は、Ghostty を入れたうえで `cargo install filetree keifu zellij` から試してみてはいかがでしょうか。

---

**出典**：[GhosttyをVSCodeみたいにしよう！](https://note.com/electrical_cat/n/n7a3b634a2b51)（Naoki | 電電猫猫）
