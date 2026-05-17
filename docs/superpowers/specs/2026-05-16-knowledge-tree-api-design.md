# 知识图谱树形 API 重构 — 设计规格

> 日期: 2026-05-16  
> 关联问题: M13 (前端知识图谱 store 扁平化)

---

## 一、问题

当前 `knowledgeStore.ts`（91 行）将后端返回的扁平知识节点数组，在前端用 `buildTree()` 函数手动重组为树。每次渲染时重新计算，且与数据库已有的 `ltree` 能力重复。

## 二、方案

让 PostgreSQL `ltree` 完成树的组织，后端新增一个树形 API，前端直接消费。

### 2.1 新增 API

```
GET /api/v1/knowledge/tree?category=
```

**响应**：

```json
[
  {
    "id": "uuid",
    "title": "基础",
    "title_slug": "basics",
    "level": 1,
    "category": "基础",
    "children": [
      {
        "id": "uuid",
        "title": "时间复杂度分析",
        "title_slug": "time-complexity",
        "level": 2,
        "order_index": 1,
        "estimated_minutes": 30,
        "children": []
      }
    ]
  },
  {
    "title": "排序",
    "children": [...]
  }
]
```

### 2.2 实现方式

利用 PostgreSQL `ltree` 的 `nlevel()` 和 `<@` 操作符，一条递归 CTE 完成：

```sql
WITH RECURSIVE tree AS (
  SELECT id, title, title_slug, path, category, level,
         order_index, estimated_minutes, NULL::uuid AS parent_id
  FROM knowledge_nodes
  WHERE is_published = true AND nlevel(path) = 1
    AND ($1::text IS NULL OR category = $1)
  UNION ALL
  SELECT kn.id, kn.title, kn.title_slug, kn.path, kn.category, kn.level,
         kn.order_index, kn.estimated_minutes, tree.id
  FROM knowledge_nodes kn
  JOIN tree ON kn.path <@ tree.path
    AND nlevel(kn.path) = nlevel(tree.path) + 1
  WHERE kn.is_published = true
)
SELECT * FROM tree ORDER BY category, path
```

然后在 `knowledge_service.py` 中将扁平结果组装为嵌套 JSON。

### 2.3 性能

- 知识点总 < 500，递归 CTE 毫秒级
- `path` 列已有 GIST 索引（Alembic 迁移 `7e9140efa2a3` 中创建）
- category 参数过滤可进一步缩小范围

## 三、前端变更

| 文件 | 变更 | 预计减行 |
|------|------|----------|
| `stores/knowledgeStore.ts` | 移除 `buildTree()`，加 `fetchTree(category?)`，存 `tree: TreeNode[]` | -30 行 |
| `pages/KnowledgeTreePage.tsx` | 去掉扁平→树的转换逻辑，直接递归渲染 | -60 行 |
| `pages/KnowledgeGraphPage.tsx` | 复用同一份树数据 | -20 行 |
| `components/KnowledgeTree.tsx` | `nodes` prop 改为 `tree` prop | ±0 |
| `services/api.ts` | 新增 `getKnowledgeTree(category?)` | +5 行 |

## 四、文件变更

| 文件 | 变更 |
|------|------|
| `app/routers/knowledge.py` | 新增 `GET /tree` 路由 |
| `app/services/knowledge_service.py` | 新增 `get_tree(category?)` 方法 |
| `app/schemas/knowledge.py` | 新增 `KnowledgeTreeNode` Pydantic schema |
| `stores/knowledgeStore.ts` | 精简 |
| `pages/KnowledgeTreePage.tsx` | 精简 |
| `services/api.ts` | 新增 API 调用 |

## 五、兼容性

- 现有 `GET /api/v1/knowledge` 扁平端点保留不变（知识图谱页仍需要）
- 树形端点纯新增，不破坏任何现有功能
- 前端其他消费 knowledgeStore 的组件不感知变化

## 六、不计入

- 不做知识图谱可视化重构（那是 M13 的延续，另开需求）
- 不做学习路径的树形展示（`learning_path` 已有自己的 API）
