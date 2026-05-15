# D3 学习路径 — 设计规格说明书

> 版本: v1.0 | 日期: 2026-05-15 | 状态: 待审核
> 关联: `D1 知识图谱设计规格`

---

## 一、概述

将 D1 的 20 个知识点按 5 条学习路线组织，用户可加入路线、自由跳学、追踪完成进度。完成标志为该节点所有必做题目通过。

---

## 二、数据模型

### 2.1 表结构

#### `learning_paths` — 学习路径

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | UUID | PK | 路径 ID |
| title | VARCHAR(255) | NOT NULL | 如"蓝桥杯备赛路线" |
| title_slug | VARCHAR(255) | UNIQUE, NOT NULL | URL 标识 |
| description | TEXT | NULL | 路线说明 |
| category | VARCHAR(50) | NOT NULL | oi_junior/oi_senior/lanqiao/self_study/acm |
| estimated_days | INTEGER | NULL | 预计完成天数 |
| is_published | BOOLEAN | NOT NULL, DEFAULT FALSE | 是否发布 |
| created_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | |
| updated_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | |

#### `learning_path_nodes` — 路径节点

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | UUID | PK | |
| path_id | UUID | FK→learning_paths ON DELETE CASCADE | 所属路径 |
| knowledge_node_id | UUID | FK→knowledge_nodes | 知识点 |
| order_index | INTEGER | NOT NULL | 建议学习顺序 |
| is_required | BOOLEAN | NOT NULL, DEFAULT TRUE | 是否必学 |
| created_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | |

**UNIQUE:** (path_id, knowledge_node_id)

#### `learning_path_progress` — 用户路径进度

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | UUID | PK | |
| user_id | UUID | FK→users | 用户 |
| path_id | UUID | FK→learning_paths | 路径 |
| status | VARCHAR(20) | NOT NULL, DEFAULT 'not_started' | not_started/in_progress/completed |
| completed_nodes | SMALLINT | NOT NULL, DEFAULT 0 | |
| total_nodes | SMALLINT | NOT NULL, DEFAULT 0 | |
| started_at | TIMESTAMP | NULL | |
| completed_at | TIMESTAMP | NULL | |
| created_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | |
| updated_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | |

**UNIQUE:** (user_id, path_id)

---

## 三、后端

### 3.1 文件

| 操作 | 文件 |
|------|------|
| CREATE | `backend/app/models/learning_path.py` |
| CREATE | `backend/app/schemas/learning_path.py` |
| CREATE | `backend/app/services/learning_path_service.py` |
| CREATE | `backend/app/routers/learning_path.py` |
| CREATE | `backend/app/data_path_seed.py` |
| CREATE | `backend/alembic/versions/xxxx_learning_path.sql` |

### 3.2 API

| 方法 | 路径 | 认证 | 说明 |
|------|------|------|------|
| GET | `/api/v1/paths` | 否 | 路线列表（含节点数、总进度） |
| GET | `/api/v1/paths/{slug}` | 否 | 路线详情 + 节点列表 + 用户进度 |
| POST | `/api/v1/paths/{slug}/enroll` | 是 | 加入路线 |
| GET | `/api/v1/paths/{slug}/progress` | 是 | 用户在该路线的进度 |

### 3.3 种子数据（5 条路线）

| slug | title | 节点数 | 节点 slug 列表 |
|------|-------|--------|---------------|
| oi-junior | OI 入门路线 (CSP-J) | 10 | time-complexity, recursion-divide-conquer, stack-queue, linked-list, binary-tree, bubble-sort, selection-sort, insertion-sort, binary-search, greedy-intro |
| oi-senior | OI 提高路线 (CSP-S) | 10 | quick-sort, merge-sort, dfs, bfs, hash-table, dp-intro, knapsack, lcs, interval-scheduling, dijkstra |
| lanqiao | 蓝桥杯备赛路线 | 12 | time-complexity, recursion-divide-conquer, bubble-sort, selection-sort, insertion-sort, binary-search, stack-queue, linked-list, dfs, bfs, dp-intro, greedy-intro |
| self-study | 零基础自学路线 | 20 | 全部节点 |
| acm-icpc | ACM-ICPC 训练路线 | 13 | quick-sort, merge-sort, binary-search, dfs, bfs, binary-tree, hash-table, dp-intro, knapsack, lcs, greedy-intro, interval-scheduling, dijkstra |

---

## 四、前端

### 4.1 文件

| 操作 | 文件 |
|------|------|
| CREATE | `frontend/src/pages/LearningPathListPage.tsx` |
| CREATE | `frontend/src/pages/LearningPathDetailPage.tsx` |
| MODIFY | `frontend/src/App.tsx` |
| MODIFY | `frontend/src/components/Navbar.tsx` |

### 4.2 页面布局

**LearningPathListPage** — 5 张路线卡片网格：

```
┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│ OI 入门      │ │ OI 提高      │ │ 蓝桥杯       │
│ 10 节点      │ │ 10 节点      │ │ 12 节点      │
│ 难度: ★★☆☆☆  │ │ 难度: ★★★★☆  │ │ 难度: ★★★☆☆  │
│ [加入此路线]  │ │ [加入此路线]  │ │ [继续学习 60%]│
└──────────────┘ └──────────────┘ └──────────────┘
┌──────────────┐ ┌──────────────┐
│ 零基础自学    │ │ ACM-ICPC    │
│ 20 节点      │ │ 13 节点      │
│ 难度: ★★★☆☆  │ │ 难度: ★★★★★  │
│ [加入此路线]  │ │ [加入此路线] │
└──────────────┘ └──────────────┘
```

**LearningPathDetailPage** — 节点列表 + 进度条：

```
┌──────────────────────────────────────────┐
│ 蓝桥杯备赛路线                   进度 4/12 │
│ ████████░░░░░░░░░░░░ 33%                │
│                                          │
│ ✅ 1. 时间复杂度分析                      │
│ ✅ 2. 递归与分治                          │
│ ✅ 3. 冒泡排序                            │
│ ✅ 4. 选择排序                            │
│ ◐ 5. 插入排序          [去学习 →]         │
│ ○ 6. 二分查找                            │
│ ○ 7. 栈与队列                            │
│ ...                                      │
└──────────────────────────────────────────┘
```

每个节点的完成状态通过查询 `user_progress`（D1 已实现）判断。点击"去学习"跳转到知识图谱对应节点详情页。

---

## 五、错误处理

| 场景 | 处理 |
|------|------|
| 路径 slug 不存在 | 404 |
| 未登录调用 enroll/progress | 401 |
| 重复加入同一路径 | 幂等，不报错 |
| 种子数据未导入 | 列表返回空 |

> **审核检查点**: 确认 5 条路线 + 弱解锁机制 + 自由跳学 + 进度追踪。通过后进入实现计划。
