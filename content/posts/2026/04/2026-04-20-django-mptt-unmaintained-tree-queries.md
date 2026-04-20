---
title: "django-mptt はなぜ「unmaintained」と書かれているのか — そして django-tree-queries への移行"
date: 2026-04-20
lastmod: 2026-04-20
draft: false
source_url: "https://gist.github.com/hdknr/83ba1f9b683a871a176d9110036364ad"
categories: ["Web開発", "データベース"]
description: "django-mptt が unmaintained を表明した背景を CHANGELOG とソースから読み解き、後継として推奨される django-tree-queries (Recursive CTE) への移行手順・API 対応表・落とし穴までまとめる"
tags: ["Django", "Python", "django-mptt", "django-tree-queries", "ツリー構造", "MPTT", "Recursive CTE", "ORM"]
---

`django-mptt` の README を開くと、いきなり以下の文言が目に飛び込んでくる。

> **This project is currently unmaintained**
>
> You can find alternatives to django-mptt on Django Packages. Maybe you do not need MPTT, especially when using newer databases. See [django-tree-queries](https://github.com/matthiask/django-tree-queries) for an implementation using recursive Common Table Expressions (CTE).

「単に飽きて投げ出した」のか、それとも「技術的に役目を終えた」のか。本稿では `django-mptt` のリポジトリ、CHANGELOG、ソースコードを実際に読んで、その背景と後継への移行可否を整理する。

---

## 1. 経緯 — メンテナンス側の事情

CHANGELOG.rst を時系列で追うと、放棄宣言とその後の経緯が見て取れる。

### v0.13: 公式に「unmaintained」を宣言

```
0.13
====
- **MARKED THE PROJECT AS UNMAINTAINED, WHICH IT STILL IS**
- Reformatted everything using black, isort etc.
- Switched from Travis CI to GitHub actions.
...
```

この時点で「もうメンテしません」と公式宣言がなされた。

### v0.15: 不本意な復活

```
0.15
====
- **Since I unfortunately still depend on django-mptt in prehistoric projects I
  took it upon me to make it runnable again. This doesn't mean I want to
  maintain the package.**
- Added Django 4.2.
- Dropped Python < 3.9, Django < 3.2.
```

メンテナ自身が古い案件で依存しているため**仕方なく動くようにしただけ**で、積極的にメンテする意図は無いと明記している。

### v0.16〜0.18: 最低限の追従のみ

| バージョン | 内容 |
|-----------|------|
| 0.16 | Python 3.12, Django 5.0 対応 |
| 0.17 | Python 3.13, Django 5.1/5.2 対応 |
| 0.18 | Django 5 の `Meta.indexes` 対応 |

新機能はゼロ。Python/Django のバージョン追従と、壊れた箇所の修繕のみ。

### 後継は同じ作者の手による

README が推す `django-tree-queries` の作者は **Matthias Kestenholz (matthiask)** — `django-mptt` を引き継いだ後期メンテナ本人である。つまり「放棄」ではなく **「アルゴリズムの世代交代を促している」** と読むのが正しい。

---

## 2. 技術的背景 — MPTT の構造的問題

### MPTT とは何か

Modified Preorder Tree Traversal (MPTT) は、各ノードに **`lft` (left)** と **`rght` (right)** の整数値を割り当てて木構造を区間で表現するテクニック。

```
              root (1, 14)
             /            \
        A (2, 7)          B (8, 13)
        /     \            /     \
   A1(3,4)  A2(5,6)   B1(9,10) B2(11,12)
```

このとき「A の子孫を取得する」は `WHERE lft > 2 AND rght < 7` という単純な範囲検索になる。**SELECT が極めて高速** なのが MPTT 最大の利点。

`django-mptt` は次の 5 つの列をモデルに自動付与してこれを実現する。

| 列名 | 役割 |
|------|------|
| `parent` | 親ノードへの FK |
| `tree_id` | 同じテーブルに複数の独立した木がある場合の識別子 |
| `level` | 深さ（0 始まり） |
| `lft` | プレオーダー走査時の左番号 |
| `rght` | プレオーダー走査時の右番号 |

### 問題点

#### (a) 書き込みが O(N)

ノード 1 つを挿入・移動するたびに **その後ろにある全ノードの `lft`/`rght` を更新する必要がある**。木のサイズが大きくなるほど 1 件の操作で何千行もの UPDATE が走る。

#### (b) 並行書き込みに弱い

複数トランザクションが同時に同じ木を編集すると、`lft`/`rght` の整合性が容易に壊れる。`django-mptt` には `TreeManager.rebuild()` という **ツリー再構築 API** が用意されており、これが「壊れることを前提とした設計」であることを物語っている。

```python
# 公式 README からの引用
# rebuild the MPTT fields for the tree
# (useful when you do bulk updates outside of Django)
MyModel.objects.rebuild()
```

#### (c) スケーラビリティ

数千ノード程度なら問題ないが、数万を超えると挿入/並べ替えが体感できる遅延を伴うようになる。CMS のカテゴリツリーなど「読みは多いが更新はほぼ無い」ユースケースに最適化されたデータ構造である。

#### (d) モダン DB では不要に近い

MPTT が考案された 1990 年代当時、MySQL や PostgreSQL は再帰クエリをサポートしていなかった。階層を SQL で扱うには `lft`/`rght` のような工夫が必須だった。

しかし現在は事情が異なる。

| DB | Recursive CTE サポート開始 |
|----|---------------------------|
| PostgreSQL | 8.4 (2009) |
| SQLite | 3.8.3 (2014) |
| MySQL | 8.0 (2018) |
| Oracle | 11g R2 (2009) |
| SQL Server | 2005 |

すべての主要 DB で `WITH RECURSIVE` が使えるようになった以上、**`parent_id` だけ持って読み取り時に CTE で辿る**方が圧倒的に素直で、かつ書き込みが O(1) になる。

---

## 3. django-tree-queries のアプローチ

`django-tree-queries` は `parent` 列**ただ 1 本**だけを持つ。深さや祖先パスは、クエリ時に Recursive CTE で動的に計算する。

```python
from tree_queries.models import TreeNode

class Category(TreeNode):
    name = models.CharField(max_length=100)
```

実行時イメージ:

```sql
WITH RECURSIVE __tree (
    "tree_depth", "tree_path", "tree_ordering", "tree_pk"
) AS (
    SELECT
        0,
        array[T.id],
        array[T.position],
        T.id
    FROM category T
    WHERE T.parent_id IS NULL

    UNION ALL

    SELECT
        __tree.tree_depth + 1,
        __tree.tree_path || T.id,
        __tree.tree_ordering || T.position,
        T.id
    FROM category T
    JOIN __tree ON T.parent_id = __tree.tree_pk
)
SELECT ... FROM category JOIN __tree ON ...
```

- 書き込み: `parent_id` を更新するだけ → **O(1)**
- 読み取り: CTE 1 発で深さ・祖先・並び順を取得 → DB の最適化に乗る
- 並行性: ツリー操作で他行が壊れない
- リビルド不要: そもそも壊れる冗長データが無い

---

## 4. データ移行 — できるか？できる

結論から言えば、**スキーマレベルでは極めて簡単**。データ変換ロジックは原則不要。

### スキーマの差分

| 列 | django-mptt | django-tree-queries |
|----|-------------|--------------------|
| `parent` | ✅ | ✅ |
| `lft`    | ✅ | ❌ |
| `rght`   | ✅ | ❌ |
| `tree_id`| ✅ | ❌ |
| `level`  | ✅ | ❌ |

`parent` 列は両者共通でそのまま流用できる。**MPTT 固有の 4 列を DROP するだけ**で物理移行は完了する。

### 移行ステップ

#### Step 1. 移行前の整合性確保

```bash
python manage.py shell -c "from myapp.models import Category; Category.objects.rebuild()"
```

仮に MPTT 側のメタデータが壊れていても、`parent` さえ正しければ tree-queries では問題にならない。ただし保険としてリビルドしておく。

#### Step 2. モデル定義の差し替え

```python
# Before: django-mptt
from mptt.models import MPTTModel, TreeForeignKey

class Category(MPTTModel):
    name = models.CharField(max_length=100)
    parent = TreeForeignKey(
        'self', null=True, blank=True,
        on_delete=models.CASCADE, related_name='children'
    )

    class MPTTMeta:
        order_insertion_by = ['name']

# After: django-tree-queries
from tree_queries.models import TreeNode

class Category(TreeNode):
    name = models.CharField(max_length=100)
    # parent は TreeNode が定義済みなので削除
```

#### Step 3. マイグレーション生成

```bash
python manage.py makemigrations
```

`lft`, `rght`, `tree_id`, `level` の DROP マイグレーションが自動生成される。インデックスも一緒に消える。

```python
# 自動生成されるマイグレーション例
operations = [
    migrations.RemoveIndex(model_name='category', name='category_tree_id_lft_idx'),
    migrations.RemoveField(model_name='category', name='lft'),
    migrations.RemoveField(model_name='category', name='rght'),
    migrations.RemoveField(model_name='category', name='tree_id'),
    migrations.RemoveField(model_name='category', name='level'),
]
```

#### Step 4. API の書き換え（ここが本番）

| django-mptt | django-tree-queries |
|-------------|--------------------|
| `node.get_descendants()` | `Category.objects.descendants(node)` |
| `node.get_ancestors()` | `Category.objects.ancestors(node)` |
| `node.get_children()` | `node.children.all()` |
| `node.get_root()` | `Category.objects.ancestors(node).first()` |
| `node.is_leaf_node()` | `not node.children.exists()` |
| `node.level` | `node.tree_depth` (要 `with_tree_fields()`) |
| `Model.objects.all()` (順序付き) | `Model.objects.with_tree_fields()` |
| `Model.objects.rebuild()` | （存在しない・不要） |

クエリの基本形:

```python
# tree_depth, tree_path, tree_ordering を付与
qs = Category.objects.with_tree_fields()

for node in qs:
    print('  ' * node.tree_depth + node.name)
```

#### Step 5. テンプレートタグの置換

`django-mptt` の `recursetree` / `mptt_full_tree_for_model` などは `django-tree-queries` の `tree_info` 等に置き換える。

```html
{# Before: django-mptt #}
{% load mptt_tags %}
{% recursetree categories %}
    <li>{{ node.name }}
        {% if not node.is_leaf_node %}
            <ul>{{ children }}</ul>
        {% endif %}
    </li>
{% endrecursetree %}

{# After: django-tree-queries #}
{% load tree_queries %}
{% tree_info categories as tree %}
{% for node, structure in tree %}
    {% if structure.new_level %}<ul>{% endif %}
    <li>{{ node.name }}
    {% for level in structure.closed_levels %}</li></ul>{% endfor %}
{% endfor %}
```

### 注意点・落とし穴

1. **Ordered insertion が無い** — `MPTTMeta.order_insertion_by` 相当の自動兄弟ソートは存在しないので、必要なら明示的な `position` 列を自前で導入する。
2. **管理画面** — `DraggableMPTTAdmin` のようなドラッグ&ドロップ UI は付属しない。必要なら別ライブラリか自作。
3. **CTE のコスト** — 数十万ノードのツリーに対する `descendants` クエリは、MPTT の `BETWEEN lft AND rght` より遅くなる場合がある。実データで EXPLAIN を取ること。
4. **DB 制約** — Recursive CTE は前述の通り全主要 DB で動くが、**MySQL 5.7 以下は非対応**。
5. **シリアライザ等の差** — DRF などで MPTT 専用の TreeSerializer を使っていると書き直しが必要。

### 移行コストの見積もり

| 項目 | コスト |
|------|--------|
| スキーマ移行 | 数分（`makemigrations` + `migrate`） |
| モデル定義変更 | 数分〜数十分 |
| API 呼び出しの全置換 | **数日〜数週間**（規模次第） |
| テンプレート/Admin 改修 | 数日 |
| 性能ベンチ・回帰テスト | 数日 |

データ自体の変換は不要だが、**コードの呼び出し箇所の網羅的書き換えが本作業**となる。

---

## 5. どう判断するか

| ケース | 推奨 |
|--------|------|
| 既存案件で安定稼働中、ツリー編集が稀 | 現状維持 (`django-mptt` のまま) |
| 既存案件、ツリー操作で性能/破損問題が顕在化 | `django-tree-queries` 移行を検討 |
| 新規プロジェクト、PostgreSQL/MySQL 8+ | **最初から `django-tree-queries`** |
| 新規プロジェクト、MySQL 5.7 以下が必須 | やむなく `django-mptt`（または `django-treebeard`） |
| 「並び順固定で読み取りが極めて多い」CMS 等 | `django-mptt` の SELECT 性能が活きる場面も残る |

---

## 6. まとめ

- `django-mptt` の "unmaintained" 表明は、**怠惰ではなくアルゴリズム的な世代交代の宣言**である。
- 後継として推奨される `django-tree-queries` は同じメンテナの手によるもので、Recursive CTE を前提とした素直な実装。
- **データ移行は技術的に容易** (`parent` を残し他列を DROP) だが、**API/テンプレート/Admin の書き換えが本番の工数**。
- 新規採用は `django-tree-queries` 一択に近い。既存案件は「動いているなら触らない」も合理的選択。

> 「既存依存があるから保守を続けてはいるが、新規には勧めない」 — メンテナの態度はこれ以上なく明確である。

---

### 参考リンク

- [django-mptt (GitHub)](https://github.com/django-mptt/django-mptt)
- [django-tree-queries (GitHub)](https://github.com/matthiask/django-tree-queries)
- [django-tree-queries 紹介ブログ (matthiask)](https://406.ch/writing/django-tree-queries/)
- [Storing Hierarchical Data in a Database](https://www.sitepoint.com/hierarchical-data-database/)
- [Trees in SQL](https://www.ibase.ru/files/articles/programming/dbmstrees/sqltrees.html)
- [元の Gist](https://gist.github.com/hdknr/83ba1f9b683a871a176d9110036364ad)
