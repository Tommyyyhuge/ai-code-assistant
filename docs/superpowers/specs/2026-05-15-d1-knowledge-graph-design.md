# D1 知识图谱 — 设计规格说明书

> 版本: v1.0 | 日期: 2026-05-15 | 状态: 待审核
> 关联文档: `technical_spec.md`, `technical_decisions.md`

---

## 一、概述

为 AI_code_assisstant 构建算法知识图谱系统。核心功能：知识点树形浏览、节点详情（讲解+配套练习+关联导航）、用户学习进度追踪。

---

## 二、数据模型

### 2.1 存储引擎

PostgreSQL `ltree` 扩展（物化路径）。需在 Alembic 迁移中执行 `CREATE EXTENSION IF NOT EXISTS ltree`。

### 2.2 表结构

#### `knowledge_nodes` — 知识节点

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | UUID | PK, DEFAULT gen_random_uuid() | 节点唯一标识 |
| title | VARCHAR(255) | NOT NULL | 知识点标题（如"冒泡排序"） |
| title_slug | VARCHAR(255) | UNIQUE, NOT NULL | URL 友好标识 |
| path | LTREE | NOT NULL | 物化路径（如 `sorting.bubble`） |
| category | VARCHAR(50) | NOT NULL | 一级分类（排序/搜索/DP/图论/...） |
| level | SMALLINT | NOT NULL, CHECK(1-5) | 难度等级 |
| description | TEXT | NOT NULL | 概念定义（Markdown） |
| core_concept | TEXT | NOT NULL | 核心思想 |
| applicable_scenarios | TEXT | NULL | 适用场景 |
| algorithm_steps | TEXT | NULL | 算法步骤 |
| code_template_cpp | TEXT | NULL | C++ 代码模板 |
| code_template_py | TEXT | NULL | Python 代码模板 |
| code_template_java | TEXT | NULL | Java 代码模板 |
| time_complexity | VARCHAR(100) | NULL | 时间复杂度 |
| space_complexity | VARCHAR(100) | NULL | 空间复杂度 |
| common_mistakes | TEXT | NULL | 易错点提示 |
| order_index | INTEGER | NOT NULL, DEFAULT 0 | 同级排序 |
| is_published | BOOLEAN | NOT NULL, DEFAULT FALSE | 是否发布 |
| estimated_minutes | INTEGER | NULL | 预计学习时长（分钟） |
| created_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | 创建时间 |
| updated_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | 更新时间 |

**索引:**
- `UNIQUE (path)` — 路径唯一
- GIST `(path)` — 子树查询加速
- `(category, order_index)` — 分类列表
- `(is_published)` — 发布筛选

#### `knowledge_edges` — 知识关联边

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | UUID | PK | 关联 ID |
| from_node_id | UUID | FK→knowledge_nodes.id | 起始节点 |
| to_node_id | UUID | FK→knowledge_nodes.id | 目标节点 |
| edge_type | VARCHAR(20) | NOT NULL | prerequisite / next / related |
| created_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | 创建时间 |

**检查约束:** `from_node_id != to_node_id`
**索引:** `(from_node_id, edge_type)`, `(to_node_id, edge_type)`

#### `knowledge_problem_associations` — 知识点↔题目关联

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| knowledge_node_id | UUID | FK→knowledge_nodes ON DELETE CASCADE | 知识点 |
| problem_id | UUID | FK→problems ON DELETE CASCADE | 题目 |
| difficulty_level | SMALLINT | NOT NULL, CHECK(1-3) | 练习难度: 1 入门 / 2 进阶 / 3 挑战 |
| order_index | INTEGER | NOT NULL, DEFAULT 0 | 排序 |
| is_required | BOOLEAN | NOT NULL, DEFAULT TRUE | 是否必做 |
| created_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | 创建时间 |

**PK:** `(knowledge_node_id, problem_id)`

#### `user_progress` — 用户学习进度

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | UUID | PK | 进度 ID |
| user_id | UUID | FK→users NOT NULL | 用户 |
| knowledge_node_id | UUID | FK→knowledge_nodes NOT NULL | 知识点 |
| status | VARCHAR(20) | NOT NULL, DEFAULT 'not_started' | not_started / in_progress / completed |
| started_at | TIMESTAMP | NULL | 开始学习时间 |
| completed_at | TIMESTAMP | NULL | 完成时间 |
| practice_count | SMALLINT | NOT NULL, DEFAULT 0 | 练习次数 |
| last_practiced_at | TIMESTAMP | NULL | 最后练习时间 |
| created_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | 创建时间 |
| updated_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | 更新时间 |

**UNIQUE:** `(user_id, knowledge_node_id)`
**索引:** `(user_id, status)`, `(knowledge_node_id)`

---

## 三、后端架构

### 3.1 文件清单（6 个新文件）

```
backend/app/models/knowledge.py           # 4 个 SQLAlchemy 模型
backend/app/schemas/knowledge.py          # Pydantic 请求/响应
backend/app/services/knowledge_service.py # 业务逻辑
backend/app/routers/knowledge.py          # REST API
backend/app/data_seed.py                  # 种子数据（20 个知识点）
backend/alembic/versions/xxxx_ltree_knowledge_graph.py  # 迁移
```

### 3.2 API 端点

| 方法 | 路径 | 认证 | 限流 | 说明 |
|------|------|------|------|------|
| GET | `/api/v1/knowledge/tree` | 否 | 30/min | 完整知识树（嵌套 JSON） |
| GET | `/api/v1/knowledge/nodes/{slug}` | 否 | 30/min | 节点详情 + 关联题目 + 邻居 |
| GET | `/api/v1/knowledge/nodes/{id}/problems` | 否 | 30/min | 节点配套练习列表 |
| POST | `/api/v1/knowledge/progress` | 是 | 20/min | 更新用户进度 |
| GET | `/api/v1/knowledge/progress` | 是 | 20/min | 用户进度总览 |

#### 响应示例

**GET /tree** — 返回嵌套结构:
```json
{
  "children": [
    {
      "id": "uuid",
      "title": "排序算法",
      "slug": "sorting",
      "level": 1,
      "userStatus": "completed",
      "children": [
        {
          "id": "uuid",
          "title": "冒泡排序",
          "slug": "bubble-sort",
          "level": 1,
          "userStatus": "in_progress",
          "children": []
        }
      ]
    }
  ]
}
```

**GET /nodes/{slug}** — 返回完整节点 + 邻居:
```json
{
  "node": { /* 全部字段 */ },
  "prerequisites": [{ "id": "", "title": "", "slug": "" }],
  "nextNodes": [{ "id": "", "title": "", "slug": "" }],
  "relatedNodes": [{ "id": "", "title": "", "slug": "" }],
  "problems": [{ "id": "", "title": "", "difficulty": 1, "difficultyLevel": 1, "isRequired": true }],
  "userProgress": { "status": "not_started", "practiceCount": 0 }
}
```

### 3.3 核心业务逻辑

**树构建** (`knowledge_service.py`):
- `get_tree()`: `SELECT * FROM knowledge_nodes WHERE is_published ORDER BY path` → 用 `path` 父子关系构建嵌套 dict
- 如果用户已登录，合并 `user_progress` 到每个节点

**进度更新** (`knowledge_service.py`):
- `upsert_progress(user_id, node_id, status)`:
  - `not_started → in_progress`: 设置 `started_at = now()`
  - `→ completed`: 设置 `completed_at = now()`，同时触发「后续节点解锁」逻辑：查询 `knowledge_edges` 中 `edge_type = 'prerequisite'` → 如果所有前置知识都完成 → 通知前端

### 3.4 种子数据

20 个知识点覆盖算法竞赛核心领域：

| 分类 | 知识点 |
|------|--------|
| 基础 | 时间复杂度分析 |
| 排序 | 冒泡排序、选择排序、插入排序、快速排序、归并排序 |
| 搜索 | 二分查找、深度优先搜索(DFS)、广度优先搜索(BFS) |
| 数据结构 | 栈与队列、链表、二叉树、哈希表 |
| 动态规划 | DP 入门（斐波那契）、背包问题、最长公共子序列 |
| 贪心 | 贪心算法基础、区间调度 |
| 图论 | 最短路径(Dijkstra)、最小生成树 |

每个节点包含完整的 description、core_concept、algorithm_steps、code_template_cpp/py、time_complexity、common_mistakes。

---

## 四、前端架构

### 4.1 文件清单（4 个新文件，2 个修改）

```
frontend/src/pages/KnowledgeTreePage.tsx       # 主页面（左树 + 右详情）
frontend/src/pages/KnowledgeGraphPage.tsx      # 全图 D3.js 交互页
frontend/src/components/KnowledgeTree.tsx      # 递归目录树组件
frontend/src/components/KnowledgeNeighborGraph.tsx  # 迷你邻居图（D3）
App.tsx                                         # 添加 2 个路由
Navbar.tsx                                      # 导航栏添加"知识图谱"入口
```

### 4.2 页面布局

**KnowledgeTreePage**（默认入口）:
```
┌─────────────┬──────────────────────────────┐
│  知识树     │  节点详情                      │
│  (w-80)    │                              │
│            │  [讲解] [题集] [关联知识]      │
│  ▼ 排序算法 │  ──────────────────────────── │
│    ▼ 冒泡  │  概念定义...                   │
│    ▼ 选择  │  核心思想...                   │
│    ▼ 插入  │  算法步骤...                   │
│    ▼ 快速  │  代码模板 (cpp/py/java 切换)    │
│    ▼ 归并  │                               │
│  ▼ 搜索    │                               │
│  ▼ DP      │                               │
│            │  ┌─────────────────────────┐  │
│            │  │ 关联知识点 (迷你图)      │  │
│            │  └─────────────────────────┘  │
└─────────────┴──────────────────────────────┘
```

**Tab 切换:**
- **讲解** — Markdown 渲染 description / core_concept / algorithm_steps / common_mistakes + 代码模板
- **题集** — 配套练习列表（链接至 ProblemDetailPage），标注入门/进阶/挑战 + 必做标记
- **关联知识** — 前置/后续/相关知识文字链 + 迷你 D3 关系图

### 4.3 状态管理

复用现有的 `knowledgeStore.ts`（A2 阶段骨架已创建），需补全以下 action：

| Action | 对应 API | 触发时机 |
|--------|---------|---------|
| `fetchTree()` | GET /tree | 页面加载 |
| `fetchNode(slug)` | GET /nodes/{slug} | 点击树节点 |
| `updateProgress(nodeId, status)` | POST /progress | 点击"标记完成"按钮 |
| `fetchProgress()` | GET /progress | 用户登录后初始化 |

### 4.4 KnowledgeGraphPage（全图）

D3.js 力导向布局：
- 节点 = `knowledge_nodes`（用 path 层级着色）
- 连线 = `knowledge_edges`（prerequisite = 实线, next = 虚线, related = 点线）
- 点击节点 → 侧边弹出 brief 摘要 + "查看详情"链接
- 顶部搜索框高亮匹配节点

---

## 五、数据流

```
用户点击树节点
  → fetchNode(slug)
    → GET /api/v1/knowledge/nodes/{slug}
      → knowledge_service.get_node_detail()
        → 查 knowledge_nodes（单条）
        → 查 knowledge_edges（from/to 邻居）
        → 查 knowledge_problem_associations（关联题目）
        → 查 user_progress（如果已登录）
      → 返回聚合 JSON
    → knowledgeStore.setCurrentNode()
  → 右侧详情面板渲染

用户点击"标记完成"
  → updateProgress(nodeId, 'completed')
    → POST /api/v1/knowledge/progress
    → knowledgeTree 状态刷新（节点图标从 ○ → ●）
```

---

## 六、错误处理

| 场景 | 处理 |
|------|------|
| 节点 slug 不存在 | HTTP 404 + "知识点未找到" |
| 未登录调用进度接口 | HTTP 401（P0 修复已涵盖） |
| 重复标记进度 | upsert，不报错 |
| 树为空（种子数据未导入） | 返回空数组，前端显示"暂无知识点"占位 |
| D3 渲染失败（JS 异常） | ErrorBoundary 捕获，显示降级文字链接 |
| ltree 查询性能问题 | GIST 索引保证，生产环境监控 query_time |

---

## 七、测试策略

| 层级 | 测试内容 | 工具 |
|------|---------|------|
| 模型 | ltree path 约束、UNIQUE 约束 | pytest |
| 服务 | 树构建逻辑、进度 upsert | pytest + async |
| 路由 | 5 个端点 200/401/404 响应 | pytest + httpx |
| 前端 | 组件渲染、Tab 切换 | 后续补充 |

---

## 八、依赖与风险

| 依赖 | 状态 | 风险 |
|------|------|------|
| PostgreSQL ltree 扩展 | 需迁移中启用 | 低，PG 15 内置 |
| D3.js | 需安装 npm 包 | 低 |
| knowledge_store 骨架 | A2 已创建 | 无 |
| 种子数据质量 | 需我生成 20 条 | 中，内容需准确 |
| 关联题目 | 依赖 problems 表已有数据 | 高——目前只有空表。**关联功能做完整但初始数据可能为空** |

---

> **审核检查点**: 请确认以上设计是否符合预期。重点关注：API 设计、前端布局、初始数据范围。
