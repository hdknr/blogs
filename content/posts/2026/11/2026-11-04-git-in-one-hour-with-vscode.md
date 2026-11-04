---
title: "1 時間で Git の全体像をつかむ：VS Code で学ぶ「4 つの置き場所」とコミットまでの流れ"
date: 2026-11-04
lastmod: 2026-11-04
slug: "git-in-one-hour-with-vscode"
draft: false
source_url: "https://github.com/hdknr/blogs/issues/694#issuecomment-6624447339"
categories: ["ツール/開発環境"]
tags: ["Git", "vscode", "github", "バージョン管理"]
---

## はじめに

Git を初めて触る人に「何から教えるか」は、教える側にとっても悩ましい問題です。コマンドを片っ端から覚えても、Git が**どこに何を保存しているのか**を知らないままでは、`add` と `commit` と `push` の違いはいつまでも腑に落ちません。

X で紹介されていた Qiita の記事 [君には1時間でGitについて知ってもらう(with VSCode)](https://qiita.com/jesus_isao/items/63557eba36819faa4ad9)（jesus_isao 氏）は、プログラミングも業務も未経験の新入社員に、1 時間で Git を説明した内容をまとめたものです。2019 年に公開されて以来、定番記事として読まれ続けています。構成は次のとおりです。

1. Git と GitHub は別物だ、というところから始める
2. Subversion と比べて「ローカルにもリポジトリがある」構造を理解する
3. ステージングという「もう 1 工程」を知る
4. VS Code で `git init` からコミットまでを実際にやってみる
5. ブランチ・タグ・push などは全体像だけ紹介する

本記事ではこの記事の要点を整理し、2026 年時点の Git で補足しておきたい点（デフォルトブランチ名、`git switch` など）を加えます。

先に結論を書くと、押さえるべきは「変更は**作業ツリー → ステージングエリア → ローカルリポジトリ → リモートリポジトリ**の 4 か所を順に通る」という 1 点です。

## Git は GitHub ではない

元記事は「GitHub という言葉を聞いたことがあったら、ひとまず忘れてください」という一文から始まります。初学者がつまずく最初のポイントは、この 2 つの混同です。

- **Git**：手元の PC で動く**バージョン管理ソフトウェア**。ファイルの変更履歴を記録し、過去の状態に戻せるようにする
- **GitHub**：Git のリポジトリを置いておける**クラウドサービス**。GitLab や Bitbucket も同じ役割を持つ

Git の実体はコンソールで動く普通のアプリケーションです。インストールできているかは次のコマンドで確認できます（表示されるバージョン番号は環境によって異なります）。

```bash
git --version
```

```text
git version 2.56.0
```

## Subversion との違い：Git は分散型でローカルにもリポジトリがある

元記事は、あえて先に Subversion を説明しています。Subversion ではリポジトリ（履歴の貯蔵庫）は**サーバーにだけ**あり、`commit` するとサーバーに直接記録されます。

一方 Git は**分散型**で、サーバーだけでなく**ローカルにもリポジトリ**を持ちます。コミットはまずローカルリポジトリに対して行い、その内容を後からサーバー側の**リモートリポジトリ**へ送り込みます。

この構造の違いから、元記事では次のような使い分けにも触れています。

- Git はローカルに全履歴を持つため、大きなバイナリファイルを履歴に積み重ねると、`git clone` のたびに巨大なダウンロードが発生する
- そのため大きなバイナリファイルは Git で直接管理しないほうがよく、必要なら **Git LFS** などの拡張を使う
- 一度大きなファイルを履歴に入れてしまうと、あとから履歴ごと消すのはとても面倒

## git add とステージングエリア：コミット前の「もう 1 工程」

Git でつまずきやすいのが、**ファイルを保存してもすぐにはコミットできない**という点です。コミットの前に、変更を**ステージングエリア**（元記事の表現では「コミット予定エリア」）に追加する工程が入ります。

変更が通る場所を 4 つに分けて図にすると次のようになります。

![Git でファイルの変更が通る 4 つの場所と、その間を移動させるコマンドを示した図。自分の PC の中の作業ツリーから git add でステージングエリアへ、git commit でローカルリポジトリへ進み、サーバー上のリモートリポジトリとは git push と git pull でやり取りする](/blogs/images/git-one-hour-areas.png)

| 場所 | 中身 | 主な操作 |
|------|------|----------|
| 作業ツリー | エディタで編集して保存したファイル | `git add` でステージングエリアへ |
| ステージングエリア | 次のコミットに含める変更 | `git commit` でローカルリポジトリへ |
| ローカルリポジトリ | `.git` フォルダ。コミット履歴の全量 | `git push` でリモートリポジトリへ |
| リモートリポジトリ | GitHub などに置かれた共有用の履歴 | `git pull` / `git clone` でローカルへ取り込む |

ポイントは、**`git commit` まではネットワークを一切使わない**ことです。コミットした時点では手元に履歴が積まれただけで、他の人からは見えません。`git push` して初めてチームと共有されます。

## 始める前に：初期設定を 2 つ

ハンズオンに入る前に、Git を入れたばかりの環境で一度だけやっておく設定があります。元記事では「えっコミットできないんだけど」という追記で後から補われた内容ですが、先に済ませておくと途中で止まりません。

### コミットする人の名前とメールアドレス

Git はコミットごとに**誰がコミットしたか**を記録します。名前とメールアドレスが未設定だと、コミットの時点でエラーになります。何かのサービスへの登録や認証とは関係ないので、次の 2 行で設定します。

```bash
git config --global user.name "my_name"
git config --global user.email "my_name@example.com"
```

`--global` はその PC の Git 全体に効く設定です。特定のリポジトリだけで使い分けたい場合は、そのリポジトリ内で `--local` を指定します。

なお、GitHub に公開するリポジトリでは、このメールアドレスがコミット履歴を通じて誰でも見られる状態になります。私用のアドレスを出したくない場合は、GitHub が用意している `ID+ユーザー名@users.noreply.github.com` 形式の noreply アドレスを設定しておくとよいでしょう（[GitHub Docs: コミットメールアドレスを設定する](https://docs.github.com/ja/account-and-profile/setting-up-and-managing-your-personal-account-on-github/managing-email-preferences/setting-your-commit-email-address)）。

### 最初のブランチ名：master か main か

元記事では「リポジトリを作った時点で存在するブランチ」を `master` と説明し、注記で「現在のデフォルトは `main` に変わった」と補足しています。2026 年時点の状況を整理すると次のとおりです。

- **GitHub** で新しく作るリポジトリのデフォルトブランチは `main`
- **ローカルの `git init`** は、何も設定しなければ今も `master` で作られる

実際に Git 2.56 で設定なしに `git init` すると、次のヒントが表示されます（抜粋）。

```text
hint: Using 'master' as the name for the initial branch. This default branch name
hint: will change to "main" in Git 3.0. To configure the initial branch name
hint: to use in all of your new repositories, which will suppress this warning,
hint: call:
hint:
hint: 	git config --global init.defaultBranch <name>
```

GitHub と揃えたいなら、次のように一度だけ設定しておくと、以降の `git init` は `main` で始まり、このヒントも表示されなくなります。

```bash
git config --global init.defaultBranch main
```

## VS Code で git init からコミットまでやってみる

元記事のハンズオンは、ローカルリポジトリへのコミットまでに範囲を絞っています。同じ流れを、コマンドと VS Code の操作を対応づけながら見ていきます。

### 1. プロジェクトフォルダを作り、リポジトリを初期化する

日本語を含まないパスに `git-sandbox` フォルダを作り、その中で `git init` を実行します。

```bash
mkdir git-sandbox
cd git-sandbox
git init
```

```text
Initialized empty Git repository in /path/to/git-sandbox/.git/
```

これで隠しフォルダ `.git` が作られます。**この `.git` フォルダこそがローカルリポジトリの実体**です。隠しフォルダなので、通常は表示されません。確認したい場合は次の操作で表示を切り替えます。

- Windows：エクスプローラーの「表示」設定で、隠しファイルを表示する
- macOS：Finder で `Command` + `Shift` + `.`

### 2. VS Code でフォルダを開き、ファイルを作る

VS Code のメニュー［フォルダーを開く］で `git-sandbox` を開き、適当なファイル（例：`memo.md`）を作って保存します。すると、左側のアクティビティバーにある**ソース管理**アイコンに、変更されたファイル数を示すバッジが付きます。

コマンドで状態を見ると、まだ Git に追跡されていないファイル（`??`）として表示されます。

```bash
git status --short
```

```text
?? memo.md
```

### 3. ステージングする

ソース管理ビューを開き、ファイル名の右に出る **＋（変更をステージ）** ボタンを押します。ファイルが「変更」から「ステージされている変更」に移れば完了です。コマンドなら `git add` に相当します。

```bash
git add memo.md
git status --short
```

```text
A  memo.md
```

### 4. メッセージを書いてコミットする

上部のメッセージ欄にコミットメッセージ（例：`first commit`）を入力し、**コミット**ボタン（チェックマーク）を押します。メッセージは空のままではコミットできません。

```bash
git commit -m "first commit"
```

```text
[main (root-commit) 5d07d1e] first commit
 1 file changed, 1 insertion(+)
 create mode 100644 memo.md
```

（`5d07d1e` の部分はコミットごとに変わります。`init.defaultBranch` を設定していなければ `main` ではなく `master` と表示されます）

## ブランチ・タグ・push：ハンズオンの先にある基本概念

元記事は 1 時間の枠に収めるため、以下は全体像の紹介にとどめています。

### ブランチ

コミットを時系列に並べると 1 本の線になります。元記事はこれを「**ブランチの上にコミットがあるのではなく、コミットの連なりそのものがブランチ**」と説明しています。途中のコミットから分岐させれば別のブランチになり、分岐した変更を元のブランチに合流させる操作が**マージ**です。

ブランチを作って移動するコマンドは、昔は `git checkout` が定番でした。Git 2.23（2019 年）からは、役割を分けた `git switch` が用意されています。

```bash
git switch -c feature/hello
```

```text
Switched to a new branch 'feature/hello'
```

`git checkout` はブランチの切り替えとファイルの復元の両方を担っていて紛らわしかったため、ブランチ操作は `git switch`、ファイルの復元は `git restore` と使い分けられるようになりました。

### タグ

タグは、特定のコミットに「v1.7.0 をリリースした」といった名前を付ける機能です。ブランチと違って、基本的に後から動かしません。

```bash
git tag v1.0.0
```

### リモートリポジトリへの push

元記事ではハンズオンの範囲外ですが、流れは次のとおりです。

1. GitHub などのサービスでアカウントを作る
2. サービス上にリポジトリを作る
3. ローカルリポジトリにリモートの場所を登録する（`git remote add`）
4. `git push` でコミットを送る

逆に、サービス上のリポジトリを先に作り、`git clone` で手元にコピーしてから作業を始める方法もあります。リモートと紐づいたブランチでは、VS Code のステータスバー左下（ブランチ名の隣）に同期ボタンが表示され、pull と push をまとめて実行できます。

### .gitignore

ビルド成果物やログなど、Git で管理したくないファイルは `.gitignore` に書いて除外します。

```text
node_modules/
dist/
*.log
```

## まとめ

元記事が「1 時間」で伝えようとしているのは、コマンドの暗記ではなく**全体像**です。

- Git（ソフトウェア）と GitHub（サービス）は別物
- 変更は作業ツリー → ステージングエリア → ローカルリポジトリ → リモートリポジトリの 4 か所を順に通る
- コミットはまずローカルに積まれ、他の人と共有されるのは `git push` してから

この全体像が頭に入っていれば、VS Code のボタンが何をしているのかがわかります。エラーメッセージの意味も読み解けるようになるはずです。新人に Git を教える立場の人にも、教わる立場の人にも、最初の 1 本としておすすめできる記事です。

## 参考

- [君には1時間でGitについて知ってもらう(with VSCode) - Qiita](https://qiita.com/jesus_isao/items/63557eba36819faa4ad9)
- [図解！ Gitのブランチ・ツリーをちゃんと読む - Qiita](https://qiita.com/jesus_isao/items/2a0495c973a4c911c2cc)（同じ著者による続編）
- [Git - git-switch Documentation](https://git-scm.com/docs/git-switch)
