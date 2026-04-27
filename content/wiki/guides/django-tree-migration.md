---
title: "django-mptt から django-tree-queries への移行"
description: "django-mptt が unmaintained を宣言した背景と、Recursive CTE を使う django-tree-queries への移行手順・API 対応表・落とし穴"
date: 2026-04-27
lastmod: 2026-04-27
aliases: ["django-mptt", "django-tree-queries", "MPTT 移行"]
related_posts:
  - "/posts/2026/04/2026-04-20-django-mptt-unmaintained-tree-queries/"
tags: ["Django", "Python", "django-mptt", "django-tree-queries", "MPTT", "Recursive CTE", "ORM"]
---

## 概要

`django-mptt` は README で「This project is currently unmaintained」と宣言している。後継として推奨される `django-tree-queries` は同じメンテナ（Matthias Kestenholz）の手による Recursive CTE 実装で、書き込みコストが O(N) から O(1) に改善される。

## なぜ unmaintained になったのか

- MPTT（Modified Preorder Tree Traversal）はノード挿入・移動のたびに全ノードの `lft`/`rght` を更新する必要があり書き込みが O(N)
- 並行書き込みに弱く、`TreeManager.rebuild()` が「壊れることを前提とした API」であることを物語る
- PostgreSQL 8.4（2009）以降、すべての主要 DB が `WITH RECURSIVE` をサポートしており、MPTT の存在意義が薄れた
- メンテナは「放棄」ではなく「アルゴリズム的な世代交代を促している」

## django-tree-queries のアプローチ

`parent` 列 1 本だけを持ち、深さや祖先パスをクエリ時に Recursive CTE で動的に計算する。

- 書き込み: `parent_id` を更新するだけ → O(1)
- 読み取り: CTE 1 発で深さ・祖先・並び順を取得
- 並行性: ツリー操作で他行が壊れない
- リビルド不要: 冗長データが存在しない

## 移行手順

### 1. 整合性確保（移行前）

```bash
python manage.py shell -c "from myapp.models import Category; Category.objects.rebuild()"
```

### 2. モデル定義の差し替え

```python
# Before: django-mptt
from mptt.models import MPTTModel, TreeForeignKey
class Category(MPTTModel):
    parent = TreeForeignKey('self', null=True, blank=True, on_delete=models.CASCADE)

# After: django-tree-queries
from tree_queries.models import TreeNode
class Category(TreeNode):
    name = models.CharField(max_length=100)
    # parent は TreeNode が定義済みなので不要
```

### 3. マイグレーション生成

```bash
python manage.py makemigrations
# lft / rght / tree_id / level の DROP マイグレーションが自動生成される
```

### 4. API 対応表

| django-mptt | django-tree-queries |
|---|---|
| `node.get_descendants()` | `Category.objects.descendants(node)` |
| `node.get_ancestors()` | `Category.objects.ancestors(node)` |
| `node.get_children()` | `node.children.all()` |
| `node.is_leaf_node()` | `not node.children.exists()` |
| `node.level` | `node.tree_depth`（`with_tree_fields()` 必要） |
| `Model.objects.all()` | `Model.objects.with_tree_fields()` |
| `Model.objects.rebuild()` | 不要（存在しない） |

### 5. テンプレートタグの置換

```html
{# Before: django-mptt #}
{% load mptt_tags %}
{% recursetree categories %}
    <li>{{ node.name }}</li>
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

## 落とし穴

1. **Ordered insertion が無い** — `MPTTMeta.order_insertion_by` 相当は存在しない。必要なら `position` 列を自前で導入
2. **管理画面の UI** — `DraggableMPTTAdmin` は付属しない。必要なら別ライブラリか自作
3. **大規模 CTE のコスト** — 数十万ノードの `descendants` クエリは MPTT の `BETWEEN lft AND rght` より遅い場合がある。本番データで EXPLAIN を取ること
4. **MySQL 5.7 以下は非対応** — Recursive CTE は MySQL 8.0+ が必要
5. **DRF シリアライザの書き直し** — MPTT 専用 TreeSerializer を使っていると変更が必要

## 移行コストの目安

| 項目 | コスト |
|---|---|
| スキーマ移行 | 数分（makemigrations + migrate） |
| モデル定義変更 | 数分〜数十分 |
| API 呼び出しの全置換 | 数日〜数週間（規模次第） |
| テンプレート/Admin 改修 | 数日 |

## 判断基準

| ケース | 推奨 |
|---|---|
| 既存案件で安定稼働中、ツリー編集が稀 | django-mptt のまま |
| 新規プロジェクト、PostgreSQL/MySQL 8+ | 最初から django-tree-queries |
| MySQL 5.7 以下が必須 | django-mptt または django-treebeard |

## 関連ページ

- [FastAPI](/blogs/wiki/tools/fastapi/) — Django と同様の Python Web フレームワーク
- [DRF（Django REST Framework）](/blogs/wiki/tools/drf/) — API 移行時に関連するシリアライザ

## ソース記事

- [django-mptt はなぜ「unmaintained」と書かれているのか — そして django-tree-queries への移行](/blogs/posts/2026/04/2026-04-20-django-mptt-unmaintained-tree-queries/) — 2026-04-20
