---
title: "Pay2Key の Linux ランサムウェアが x64/ARM64 サーバーを標的に — 防御機構を無効化する高度な手口"
date: 2026-03-30
lastmod: 2026-03-30
draft: false
source_url: "https://github.com/hdknr/blogs/issues/1#issuecomment-4157822211"
categories: ["セキュリティ"]
tags: ["ランサムウェア", "Linux", "Pay2Key", "Morphisec", "I2P", "security"]
---

Linux を標的とするランサムウェアが新たな段階に入った。イラン系とされる攻撃グループ Pay2Key が Linux 向けに進化し、「Pay2Key.I2P」と呼ばれる新たな亜種を展開している。Morphisec の技術分析をもとに、攻撃の手口、防御機構の無効化手法、そして具体的な対策を整理する。

## Pay2Key とは

Pay2Key はイラン系の攻撃グループに帰属するランサムウェアで、Fox Kitten APT グループとの関連が指摘されている。従来は Windows を主な標的としていたが、企業のサーバー基盤を直撃する Linux 版が登場し、防御の前提が揺らぎ始めている。

2026年2月には、米国の医療機関で Pay2Key による侵害事例が Beazley Security Incident Response によって対応されている。

## Pay2Key.I2P の技術的特徴

### 設定駆動型の設計

Pay2Key.I2P は単なる Windows 版の移植ではない。JSON 設定ファイルによって動作を制御する設定駆動型の攻撃ツールとして設計されている。ターゲットとするファイルシステムの範囲や暗号化の挙動を柔軟に変更できる。

### デュアルアーキテクチャ対応

x64 と ARM64 の両方に対応し、従来の x86 サーバーだけでなく、ARM ベースのクラウドインスタンス（AWS Graviton など）や仮想化ホストも一括で狙うことができる。

### root 権限の必須化

侵入後は root 権限を必須とし、取得できない場合は即終了する設計となっている。これはノイズを最小限に抑え、検知を回避するための戦略と考えられる。

## 防御機構の無効化

Pay2Key.I2P の最も危険な特徴は、Linux の防御機構を体系的に無効化する点にある。

### SELinux / AppArmor の無効化

実行時に SELinux や AppArmor を無効化し、強制アクセス制御（MAC）による保護を解除する。これにより、通常であれば制限されるファイルアクセスやプロセス操作が可能になる。

### systemd サービスの停止

データベースやバックアップなどの重要なサービスを停止し、ファイルロックを解除して暗号化対象のファイルにアクセスできる状態を作り出す。

### cron による永続化

cron エントリを登録してリブート後も自動的に再実行されるようにし、単純な再起動では排除できない永続性を確保する。

## 暗号化の手法

### ChaCha20 による高速暗号化

暗号化アルゴリズムには ChaCha20 を採用している。AES と比較してソフトウェア実装での処理速度に優れる。AES-NI などの専用ハードウェアを持たない環境でも高速に動作する。

### 部分暗号化による検知回避

ファイルサイズに応じた部分暗号化を実装しており、大きなファイルの一部のみを暗号化することで処理速度を向上させつつ、従来のファイル整合性チェックによる検知を回避する。

## I2P ネットワークの利用

Pay2Key.I2P は、身代金ポータルや被害者との通信に Tor ではなく I2P（Invisible Internet Project）を使用する。I2P はパケットベースの匿名ネットワークで、Tor よりも追跡が困難とされており、ランサムウェアグループとしては先駆的な採用例である。

## 対策と推奨事項

Linux サーバーの管理者は以下の対策を検討すべきである。

- **SELinux / AppArmor を常時有効に保つ** — 無効化の試行を検知するアラートを設定する
- **root 権限の管理を強化する** — 不要な SUID ビットの除去、sudo の最小権限設定
- **cron エントリの監視** — 不審な cron ジョブの追加を検知する仕組みを導入する
- **systemd サービスの異常停止を監視する** — 重要サービスの予期しない停止をアラートする
- **ファイル整合性監視（FIM）を導入する** — 部分暗号化にも対応できるよう、ファイルの変更を即座に検知する
- **ネットワーク監視で I2P 通信を検知する** — I2P のトラフィックパターンをブロックまたはアラートする

## まとめ

Pay2Key.I2P は、Linux が安全圏ではない現実を浮き彫りにしている。設定駆動型の柔軟な設計、デュアルアーキテクチャ対応、防御機構の体系的な無効化、そして I2P による匿名通信と、マルウェアの「製品化」を思わせる完成度となっている。実行前に阻止する防御戦略の重要性がますます増している。

## 参考リンク

- [Inside Pay2Key: Technical Analysis of a Linux Ransomware Variant | Morphisec](https://www.morphisec.com/blog/inside-pay2key-technical-analysis-of-a-linux-ransomware-variant/)
- [Pay2Key's New Linux Ransomware Strips Server Defenses | SecurityOnline](https://securityonline.info/pay2key-linux-ransomware-x64-arm64-server-protection/)
- [Pay2Key's Resurgence: Iranian Cyber Warfare Targets the West | Morphisec](https://www.morphisec.com/blog/pay2key-resurgence-iranian-cyber-warfare/)
