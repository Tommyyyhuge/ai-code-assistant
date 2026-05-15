# AI_code_assisstant 技术规格说明书

> 版本: v1.0  
> 日期: 2026�?�?4�? 
> 基于 PRD v1.1  

---

## 技术约束（必须遵守�?
| 层次 | 技术选型 | 版本/说明 |
|------|---------|----------|
| 前端框架 | React + TypeScript | React 18, TypeScript 5.x |
| 前端样式 | Tailwind CSS | v3.x |
| 状态管�?| Zustand | 轻量状态管�?|
| 后端框架 | FastAPI (Python) | Python 3.10+ |
| 数据�?| PostgreSQL + SQLAlchemy | PostgreSQL 15+ |
| 缓存 | Redis | Redis 7+ |
| 评测沙箱 | Docker | 容器化隔�?|
| AI 接入 | HTTP Client + 工厂模式 | 默认 DeepSeek, 支持多模�?|
| 部署 | Docker Compose | 一键启�?|

---

## 一、数据库设计

### 1.1 数据库选型说明

- **PostgreSQL**: 存储所有持久化数据（用户、题目、提交记录、知识内容等�?- **Redis**: 缓存热点数据（题目列表、用户会话、评测队列状态）
- **文件存储**: 测试数据文件存储于本地文件系统，数据库仅存储路径。MVP 阶段使用本地存储，后续可迁移至对象存�?
### 1.2 实体关系概览

```
users ||--o{ submissions : submits
users ||--o{ ai_conversations : has
users ||--o{ user_progress : tracks
users ||--o{ learning_path_progress : follows

problems ||--o{ submissions : has
problems ||--o{ problem_tag_associations : tagged
problems ||--o{ test_cases : contains
problems ||--o{ knowledge_problem_associations : related_to

tags ||--o{ problem_tag_associations : tags

tags ||--o{ tag_parent_child : parent

tags ||--o{ tag_parent_child : child

knowledge_nodes ||--o{ knowledge_edges : from_node
knowledge_nodes ||--o{ knowledge_edges : to_node
knowledge_nodes ||--o{ knowledge_problem_associations : practices
knowledge_nodes ||--o{ user_progress : learned
knowledge_nodes ||--o{ learning_path_nodes : in_path

ai_conversations ||--o{ ai_messages : contains

learning_paths ||--o{ learning_path_nodes : contains
learning_paths ||--o{ learning_path_progress : tracked_by
```

### 1.3 数据库表结构

#### 1.3.1 用户系统

##### �? `users` (用户�?

| 字段�?| 类型 | 约束 | 默认�?| 说明 |
|--------|------|------|--------|------|
| id | UUID | PK, DEFAULT gen_random_uuid() | gen_random_uuid() | 用户唯一标识 |
| username | VARCHAR(50) | UNIQUE, NOT NULL | - | 用户�?|
| email | VARCHAR(255) | UNIQUE, NOT NULL | - | 邮箱地址 |
| password_hash | VARCHAR(255) | NOT NULL | - | 密码哈希（bcrypt�?|
| github_id | VARCHAR(100) | UNIQUE, NULL | NULL | GitHub OAuth ID |
| github_username | VARCHAR(100) | NULL | NULL | GitHub 用户�?|
| avatar_url | VARCHAR(500) | NULL | NULL | 头像URL |
| role | VARCHAR(20) | NOT NULL | 'user' | 角色: user/admin |
| elo_rating | INTEGER | NOT NULL | 1200 | Elo评分 |
| is_active | BOOLEAN | NOT NULL | TRUE | 账号是否激�?|
| last_login_at | TIMESTAMP | NULL | NULL | 最后登录时�?|
| created_at | TIMESTAMP | NOT NULL | NOW() | 创建时间 |
| updated_at | TIMESTAMP | NOT NULL | NOW() | 更新时间 |

**索引:**
- `idx_users_email`: email (用于登录查询)
- `idx_users_github_id`: github_id (用于OAuth登录)
- `idx_users_username`: username (用于搜索)

---

##### �? `user_profiles` (用户资料�?

| 字段�?| 类型 | 约束 | 默认�?| 说明 |
|--------|------|------|--------|------|
| user_id | UUID | PK, FK→users.id | - | 用户ID |
| display_name | VARCHAR(100) | NULL | NULL | 显示名称 |
| bio | TEXT | NULL | NULL | 个人简�?|
| school | VARCHAR(200) | NULL | NULL | 学校/机构 |
| grade | VARCHAR(50) | NULL | NULL | 年级/身份 |
| target_olympiad | VARCHAR(50) | NULL | NULL | 目标竞赛 |
| programming_level | VARCHAR(20) | NULL | NULL | 编程水平 |
| preferred_language | VARCHAR(20) | NOT NULL | 'cpp' | 偏好语言: cpp/py/java |
| ai_model_preference | VARCHAR(50) | NULL | NULL | 偏好的AI模型 |
| custom_api_key | VARCHAR(255) | NULL | NULL | 用户自定义API Key(加密存储) |
| updated_at | TIMESTAMP | NOT NULL | NOW() | 更新时间 |

---

#### 1.3.2 题库中心

##### �? `problems` (题目�?

| 字段�?| 类型 | 约束 | 默认�?| 说明 |
|--------|------|------|--------|------|
| id | UUID | PK, 自动递增 | gen_random_uuid() | 题目唯一标识 |
| title | VARCHAR(255) | NOT NULL | - | 题目标题 |
| title_slug | VARCHAR(255) | UNIQUE, NOT NULL | - | URL友好的标题标�?|
| description | TEXT | NOT NULL | - | 题目描述 (Markdown) |
| input_format | TEXT | NOT NULL | - | 输入格式说明 |
| output_format | TEXT | NOT NULL | - | 输出格式说明 |
| constraints | TEXT | NULL | NULL | 数据范围与约�?|
| difficulty | SMALLINT | NOT NULL, CHECK(1-10) | 1 | 难度�?1-10 |
| time_limit_ms | INTEGER | NOT NULL | 1000 | 时间限制（毫秒） |
| memory_limit_mb | INTEGER | NOT NULL | 256 | 内存限制（MB�?|
| source_oj | VARCHAR(50) | NULL | NULL | 来源OJ: luogu/codeforces/libreoj/custom |
| source_problem_id | VARCHAR(100) | NULL | NULL | 来源OJ的原始题�?|
| source_url | VARCHAR(500) | NULL | NULL | 来源URL |
| is_published | BOOLEAN | NOT NULL | FALSE | 是否已发�?|
| created_by | UUID | FK→users.id, NULL | NULL | 创建�?|
| created_at | TIMESTAMP | NOT NULL | NOW() | 创建时间 |
| updated_at | TIMESTAMP | NOT NULL | NOW() | 更新时间 |

**索引:**
- `idx_problems_difficulty`: difficulty (筛�?
- `idx_problems_source_oj`: source_oj (筛�?
- `idx_problems_published`: is_published, created_at (列表查询)
- `idx_problems_title`: title (GIN全文搜索)

---

##### �? `test_cases` (测试数据�?

| 字段�?| 类型 | 约束 | 默认�?| 说明 |
|--------|------|------|--------|------|
| id | UUID | PK, 自动递增 | gen_random_uuid() | 测试数据ID |
| problem_id | UUID | FK→problems.id, NOT NULL, ON DELETE CASCADE | - | 所属题�?|
| input_data | TEXT | NOT NULL | - | 输入数据 |
| expected_output | TEXT | NOT NULL | - | 期望输出 |
| is_sample | BOOLEAN | NOT NULL | FALSE | 是否样例数据 |
| is_active | BOOLEAN | NOT NULL | TRUE | 是否启用 |
| order_index | INTEGER | NOT NULL | 0 | 排序顺序 |
| created_at | TIMESTAMP | NOT NULL | NOW() | 创建时间 |

**索引:**
- `idx_test_cases_problem`: problem_id, is_active, order_index

---

##### �? `tags` (标签�?

| 字段�?| 类型 | 约束 | 默认�?| 说明 |
|--------|------|------|--------|------|
| id | UUID | PK, 自动递增 | gen_random_uuid() | 标签ID |
| name | VARCHAR(100) | UNIQUE, NOT NULL | - | 标签名称 |
| name_slug | VARCHAR(100) | UNIQUE, NOT NULL | - | URL友好名称 |
| category | VARCHAR(50) | NOT NULL | - | 分类: algorithm/datastructure/lanqiao |
| parent_id | UUID | FK→tags.id, NULL | NULL | 父标签ID（树状结构） |
| description | TEXT | NULL | NULL | 标签描述 |
| color | VARCHAR(7) | NULL | NULL | 标签颜色 (HEX) |
| is_lanqiao_special | BOOLEAN | NOT NULL | FALSE | 是否蓝桥杯特色标�?|
| created_at | TIMESTAMP | NOT NULL | NOW() | 创建时间 |

**索引:**
- `idx_tags_category`: category (筛�?
- `idx_tags_parent`: parent_id (树查�?

---

##### �? `problem_tag_associations` (题目-标签关联�?

| 字段�?| 类型 | 约束 | 默认�?| 说明 |
|--------|------|------|--------|------|
| problem_id | UUID | FK→problems.id, ON DELETE CASCADE | - | 题目ID |
| tag_id | UUID | FK→tags.id, ON DELETE CASCADE | - | 标签ID |
| is_primary | BOOLEAN | NOT NULL | FALSE | 是否主要标签 |
| created_at | TIMESTAMP | NOT NULL | NOW() | 创建时间 |

**PK:** (problem_id, tag_id)

---

#### 1.3.3 评测系统

##### �? `submissions` (提交记录�?

| 字段�?| 类型 | 约束 | 默认�?| 说明 |
|--------|------|------|--------|------|
| id | UUID | PK, 自动递增 | gen_random_uuid() | 提交ID |
| user_id | UUID | FK→users.id, NOT NULL | - | 提交用户 |
| problem_id | UUID | FK→problems.id, NOT NULL | - | 题目ID |
| code | TEXT | NOT NULL | - | 提交的代�?|
| language | VARCHAR(20) | NOT NULL | - | 语言: cpp/py/java |
| status | VARCHAR(20) | NOT NULL | 'Pending' | 状�?|
| score | INTEGER | NULL | NULL | 得分（百分比�?|
| runtime_ms | INTEGER | NULL | NULL | 运行时间（毫秒） |
| memory_kb | INTEGER | NULL | NULL | 内存使用（KB�?|
| passed_count | SMALLINT | NULL | NULL | 通过测试点数�?|
| total_count | SMALLINT | NULL | NULL | 总测试点数量 |
| error_message | TEXT | NULL | NULL | 错误信息 |
| judge_log | TEXT | NULL | NULL | 评测日志 |
| submitted_at | TIMESTAMP | NOT NULL | NOW() | 提交时间 |
| judged_at | TIMESTAMP | NULL | NULL | 评测完成时间 |
| judge_worker_id | VARCHAR(100) | NULL | NULL | 评测工作节点 |

**状态枚�?** `Pending`, `Compiling`, `Running`, `AC` (Accepted), `WA` (Wrong Answer), `TLE` (Time Limit Exceeded), `MLE` (Memory Limit Exceeded), `RE` (Runtime Error), `CE` (Compile Error), `SystemError`

**索引:**
- `idx_submissions_user`: user_id, submitted_at DESC (用户提交历史)
- `idx_submissions_problem`: problem_id, status (题目统计)
- `idx_submissions_status`: status, submitted_at (评测队列)
- `idx_submissions_user_problem`: user_id, problem_id, status (去重查询)

---

##### �? `submission_results` (提交结果详情�?

| 字段�?| 类型 | 约束 | 默认�?| 说明 |
|--------|------|------|--------|------|
| id | UUID | PK, 自动递增 | gen_random_uuid() | 结果ID |
| submission_id | UUID | FK→submissions.id, ON DELETE CASCADE | - | 提交ID |
| test_case_id | UUID | FK→test_cases.id, NULL | NULL | 测试点ID |
| test_case_order | SMALLINT | NOT NULL | - | 测试点序�?|
| status | VARCHAR(20) | NOT NULL | - | 该测试点状�?|
| runtime_ms | INTEGER | NULL | NULL | 运行时间 |
| memory_kb | INTEGER | NULL | NULL | 内存使用 |
| actual_output | TEXT | NULL | NULL | 实际输出（截断存储） |
| diff_info | TEXT | NULL | NULL | 差异信息 |
| created_at | TIMESTAMP | NOT NULL | NOW() | 创建时间 |

**索引:**
- `idx_submission_results_submission`: submission_id, test_case_order

---

#### 1.3.4 知识图谱

##### �? `knowledge_nodes` (知识节点�?

| 字段�?| 类型 | 约束 | 默认�?| 说明 |
|--------|------|------|--------|------|
| id | UUID | PK, 自动递增 | gen_random_uuid() | 节点ID |
| title | VARCHAR(255) | NOT NULL | - | 知识点标�?|
| title_slug | VARCHAR(255) | UNIQUE, NOT NULL | - | URL友好标识 |
| category | VARCHAR(50) | NOT NULL | - | 分类 |
| subcategory | VARCHAR(50) | NULL | NULL | 子分�?|
| level | SMALLINT | NOT NULL, CHECK(1-5) | 1 | 难度等级 1-5 |
| description | TEXT | NOT NULL | - | 概念定义 |
| core_concept | TEXT | NOT NULL | - | 核心思想 |
| applicable_scenarios | TEXT | NULL | NULL | 适用场景 |
| algorithm_steps | TEXT | NULL | NULL | 算法步骤 |
| code_template_cpp | TEXT | NULL | NULL | C++代码模板 |
| code_template_py | TEXT | NULL | NULL | Python代码模板 |
| code_template_java | TEXT | NULL | NULL | Java代码模板 |
| time_complexity | VARCHAR(100) | NULL | NULL | 时间复杂�?|
| space_complexity | VARCHAR(100) | NULL | NULL | 空间复杂�?|
| common_mistakes | TEXT | NULL | NULL | 易错点提�?|
| parent_id | UUID | FK→knowledge_nodes.id, NULL | NULL | 父节点ID |
| order_index | INTEGER | NOT NULL | 0 | 同级排序 |
| is_published | BOOLEAN | NOT NULL | FALSE | 是否发布 |
| is_lanqiao_special | BOOLEAN | NOT NULL | FALSE | 是否蓝桥杯专�?|
| estimated_minutes | INTEGER | NULL | NULL | 预计学习时长 |
| created_at | TIMESTAMP | NOT NULL | NOW() | 创建时间 |
| updated_at | TIMESTAMP | NOT NULL | NOW() | 更新时间 |

**索引:**
- `idx_knowledge_nodes_category`: category, order_index (分类列表)
- `idx_knowledge_nodes_parent`: parent_id, order_index (树查�?
- `idx_knowledge_nodes_published`: is_published (筛�?

---

##### �? `knowledge_edges` (知识关联�?

| 字段�?| 类型 | 约束 | 默认�?| 说明 |
|--------|------|------|--------|------|
| id | UUID | PK, 自动递增 | gen_random_uuid() | 关联ID |
| from_node_id | UUID | FK→knowledge_nodes.id, NOT NULL | - | 起始节点 |
| to_node_id | UUID | FK→knowledge_nodes.id, NOT NULL | - | 目标节点 |
| edge_type | VARCHAR(20) | NOT NULL | 'prerequisite' | 关联类型 |
| created_at | TIMESTAMP | NOT NULL | NOW() | 创建时间 |

**关联类型枚举:**
- `prerequisite`: 前置知识 (必须先学)
- `next`: 后续知识 (学完后可�?
- `related`: 相关知识

**索引:**
- `idx_knowledge_edges_from`: from_node_id, edge_type
- `idx_knowledge_edges_to`: to_node_id, edge_type

---

##### �? `knowledge_problem_associations` (知识�?题目关联�?

| 字段�?| 类型 | 约束 | 默认�?| 说明 |
|--------|------|------|--------|------|
| knowledge_node_id | UUID | FK→knowledge_nodes.id, ON DELETE CASCADE | - | 知识点ID |
| problem_id | UUID | FK→problems.id, ON DELETE CASCADE | - | 题目ID |
| difficulty_level | SMALLINT | NOT NULL, CHECK(1-3) | 1 | 练习难度: 1入门/2进阶/3挑战 |
| order_index | INTEGER | NOT NULL | 0 | 排序顺序 |
| is_required | BOOLEAN | NOT NULL | TRUE | 是否必做 |
| created_at | TIMESTAMP | NOT NULL | NOW() | 创建时间 |

**PK:** (knowledge_node_id, problem_id)

---

#### 1.3.5 AI 教练

##### �? `ai_conversations` (AI 对话会话�?

| 字段�?| 类型 | 约束 | 默认�?| 说明 |
|--------|------|------|--------|------|
| id | UUID | PK, 自动递增 | gen_random_uuid() | 会话ID |
| user_id | UUID | FK→users.id, NOT NULL | - | 用户ID |
| problem_id | UUID | FK→problems.id, NULL | NULL | 关联题目 |
| knowledge_node_id | UUID | FK→knowledge_nodes.id, NULL | NULL | 关联知识�?|
| submission_id | UUID | FK→submissions.id, NULL | NULL | 关联提交 |
| title | VARCHAR(255) | NOT NULL | - | 会话标题 |
| conversation_type | VARCHAR(30) | NOT NULL | 'problem_help' | 会话类型 |
| ai_model | VARCHAR(50) | NOT NULL | - | 使用的AI模型 |
| system_prompt_version | VARCHAR(20) | NOT NULL | 'v1' | System Prompt版本 |
| is_active | BOOLEAN | NOT NULL | TRUE | 是否活跃 |
| created_at | TIMESTAMP | NOT NULL | NOW() | 创建时间 |
| updated_at | TIMESTAMP | NOT NULL | NOW() | 更新时间 |

**会话类型枚举:**
- `problem_help`: 题目求助
- `knowledge_explain`: 知识点讲�?- `error_diagnosis`: 错误诊断
- `code_review`: 代码审查
- `general_chat`: 一般咨�?
**索引:**
- `idx_ai_conversations_user`: user_id, updated_at DESC (用户会话列表)
- `idx_ai_conversations_problem`: problem_id, user_id (题目关联查询)
- `idx_ai_conversations_knowledge`: knowledge_node_id, user_id (知识点关�?

---

##### �? `ai_messages` (AI 消息�?

| 字段�?| 类型 | 约束 | 默认�?| 说明 |
|--------|------|------|--------|------|
| id | UUID | PK, 自动递增 | gen_random_uuid() | 消息ID |
| conversation_id | UUID | FK→ai_conversations.id, ON DELETE CASCADE | - | 所属会�?|
| role | VARCHAR(20) | NOT NULL | - | 角色: user/assistant/system |
| content | TEXT | NOT NULL | - | 消息内容 |
| prompt_level | SMALLINT | NULL | NULL | 提示级别 1-3 |
| is_error_diagnosis | BOOLEAN | NOT NULL | FALSE | 是否为错误诊�?|
| error_type | VARCHAR(20) | NULL | NULL | 错误类型: WA/TLE/MLE/RE/CE |
| token_count | INTEGER | NULL | NULL | Token消耗数 |
| metadata | JSONB | NULL | NULL | 额外元数�?|
| created_at | TIMESTAMP | NOT NULL | NOW() | 创建时间 |

**索引:**
- `idx_ai_messages_conversation`: conversation_id, created_at ASC (会话消息查询)

---

#### 1.3.6 学习路径

##### �? `learning_paths` (学习路径�?

| 字段�?| 类型 | 约束 | 默认�?| 说明 |
|--------|------|------|--------|------|
| id | UUID | PK, 自动递增 | gen_random_uuid() | 路径ID |
| title | VARCHAR(255) | NOT NULL | - | 路径标题 |
| title_slug | VARCHAR(255) | UNIQUE, NOT NULL | - | URL友好标识 |
| description | TEXT | NULL | NULL | 路径描述 |
| category | VARCHAR(50) | NOT NULL | - | 分类 |
| target_audience | VARCHAR(100) | NULL | NULL | 目标人群 |
| difficulty_range | VARCHAR(20) | NULL | NULL | 难度范围 |
| estimated_days | INTEGER | NULL | NULL | 预计完成天数 |
| is_official | BOOLEAN | NOT NULL | TRUE | 是否官方路径 |
| is_published | BOOLEAN | NOT NULL | FALSE | 是否发布 |
| created_by | UUID | FK→users.id, NULL | NULL | 创建�?|
| created_at | TIMESTAMP | NOT NULL | NOW() | 创建时间 |
| updated_at | TIMESTAMP | NOT NULL | NOW() | 更新时间 |

**路径分类枚举:**
- `oi_junior`: OI 入门路线 (CSP-J)
- `oi_senior`: OI 提高路线 (CSP-S/NOIP)
- `lanqiao`: 蓝桥杯备赛路�?- `self_study`: 零基础自学路线
- `acm`: ACM-ICPC 训练路线

**索引:**
- `idx_learning_paths_category`: category, is_published (分类查询)

---

##### �? `learning_path_nodes` (路径节点�?

| 字段�?| 类型 | 约束 | 默认�?| 说明 |
|--------|------|------|--------|------|
| id | UUID | PK, 自动递增 | gen_random_uuid() | 节点ID |
| path_id | UUID | FK→learning_paths.id, ON DELETE CASCADE | - | 所属路�?|
| knowledge_node_id | UUID | FK→knowledge_nodes.id, NOT NULL | - | 知识点ID |
| order_index | INTEGER | NOT NULL | - | 路径中的顺序 |
| is_required | BOOLEAN | NOT NULL | TRUE | 是否必学 |
| estimated_minutes | INTEGER | NULL | NULL | 预计学习时长 |
| created_at | TIMESTAMP | NOT NULL | NOW() | 创建时间 |

**索引:**
- `idx_path_nodes_path`: path_id, order_index (路径节点列表)

---

##### �? `user_progress` (用户学习进度�?

| 字段�?| 类型 | 约束 | 默认�?| 说明 |
|--------|------|------|--------|------|
| id | UUID | PK, 自动递增 | gen_random_uuid() | 进度ID |
| user_id | UUID | FK→users.id, NOT NULL | - | 用户ID |
| knowledge_node_id | UUID | FK→knowledge_nodes.id, NOT NULL | - | 知识点ID |
| status | VARCHAR(20) | NOT NULL | 'not_started' | 状�?|
| started_at | TIMESTAMP | NULL | NULL | 开始学习时�?|
| completed_at | TIMESTAMP | NULL | NULL | 完成时间 |
| practice_count | SMALLINT | NOT NULL | 0 | 练习次数 |
| last_practiced_at | TIMESTAMP | NULL | NULL | 最后练习时�?|
| created_at | TIMESTAMP | NOT NULL | NOW() | 创建时间 |
| updated_at | TIMESTAMP | NOT NULL | NOW() | 更新时间 |

**状态枚�?** `not_started`, `in_progress`, `completed`, `mastered`

**PK约束:** UNIQUE(user_id, knowledge_node_id)

**索引:**
- `idx_user_progress_user`: user_id, status (用户进度查询)
- `idx_user_progress_node`: knowledge_node_id (知识点统�?

---

##### �? `learning_path_progress` (路径进度追踪�?

| 字段�?| 类型 | 约束 | 默认�?| 说明 |
|--------|------|------|--------|------|
| id | UUID | PK, 自动递增 | gen_random_uuid() | 进度ID |
| user_id | UUID | FK→users.id, NOT NULL | - | 用户ID |
| path_id | UUID | FK→learning_paths.id, NOT NULL | - | 路径ID |
| status | VARCHAR(20) | NOT NULL | 'not_started' | 状�?|
| completed_nodes | SMALLINT | NOT NULL | 0 | 已完成节点数 |
| total_nodes | SMALLINT | NOT NULL | 0 | 总节点数 |
| completion_percent | SMALLINT | NOT NULL, CHECK(0-100) | 0 | 完成百分�?|
| started_at | TIMESTAMP | NULL | NULL | 开始时�?|
| completed_at | TIMESTAMP | NULL | NULL | 完成时间 |
| last_activity_at | TIMESTAMP | NOT NULL | NOW() | 最后活动时�?|
| created_at | TIMESTAMP | NOT NULL | NOW() | 创建时间 |
| updated_at | TIMESTAMP | NOT NULL | NOW() | 更新时间 |

**PK约束:** UNIQUE(user_id, path_id)

---

#### 1.3.7 系统配置

##### �? `system_configs` (系统配置�?

| 字段�?| 类型 | 约束 | 默认�?| 说明 |
|--------|------|------|--------|------|
| id | UUID | PK, 自动递增 | gen_random_uuid() | 配置ID |
| config_key | VARCHAR(100) | UNIQUE, NOT NULL | - | 配置�?|
| config_value | TEXT | NOT NULL | - | 配置�?|
| description | VARCHAR(255) | NULL | NULL | 描述 |
| updated_at | TIMESTAMP | NOT NULL | NOW() | 更新时间 |

---

### 1.4 数据库关系图 (文字描述)

```
┌─────────────────────────────────────────────────────────────────�?�?                        用户�?(User Layer)                      �?├─────────────────────────────────────────────────────────────────�?�? users ──1:1── user_profiles                                    �?�? users ──1:N── submissions                                      �?�? users ──1:N── ai_conversations                                 �?�? users ──1:N── user_progress                                    �?�? users ──1:N── learning_path_progress                           �?└─────────────────────────────────────────────────────────────────�?                              �?                              �?┌─────────────────────────────────────────────────────────────────�?�?                       题库�?(Problem Layer)                    �?├─────────────────────────────────────────────────────────────────�?�? problems ──1:N── test_cases                                    �?�? problems ──N:M── tags (via problem_tag_associations)           �?�? problems ──1:N── submissions                                   �?�? problems ──N:M── knowledge_nodes (via knowledge_problem_assoc) �?└─────────────────────────────────────────────────────────────────�?                              �?                              �?┌─────────────────────────────────────────────────────────────────�?�?                      评测�?(Judge Layer)                       �?├─────────────────────────────────────────────────────────────────�?�? submissions ──1:N── submission_results                         �?�? submission_results ──N:1── test_cases                          �?└─────────────────────────────────────────────────────────────────�?                              �?                              �?┌─────────────────────────────────────────────────────────────────�?�?                    知识图谱�?(Knowledge Layer)                  �?├─────────────────────────────────────────────────────────────────�?�? knowledge_nodes ──自关联── parent_id (树状结构)                 �?�? knowledge_nodes ──N:M── knowledge_edges (前置/后续关联)         �?�? knowledge_nodes ──N:M── problems (配套练习)                    �?�? knowledge_nodes ──1:N── user_progress                          �?└─────────────────────────────────────────────────────────────────�?                              �?                              �?┌─────────────────────────────────────────────────────────────────�?�?                     学习路径�?(Path Layer)                      �?├─────────────────────────────────────────────────────────────────�?�? learning_paths ──1:N── learning_path_nodes                     �?�? learning_path_nodes ──N:1── knowledge_nodes                    �?�? learning_paths ──1:N── learning_path_progress                  �?└─────────────────────────────────────────────────────────────────�?                              �?                              �?┌─────────────────────────────────────────────────────────────────�?�?                       AI�?(AI Layer)                           �?├─────────────────────────────────────────────────────────────────�?�? ai_conversations ──1:N── ai_messages                           �?�? ai_conversations ──N:1── users                                 �?�? ai_conversations ──N:1── problems (可�?                       �?�? ai_conversations ──N:1── knowledge_nodes (可�?                �?�? ai_conversations ──N:1── submissions (可�?                    �?└─────────────────────────────────────────────────────────────────�?```

---

### 1.5 数据初始化方案

MVP 阶段需要预置基础数据，通过 data/seeds/ 目录管理：

`
data/seeds/
├── knowledge_nodes.json          # 知识点初始数据（15-20个）
├── learning_paths.json           # 学习路径初始数据（4条）
├── tags.json                     # 标签体系初始数据
├── prompts/                      # System Prompt 配置
│   ├── v1.json                   # 竞赛教练 System Prompt v1
│   ├── v1_diagnosis.json         # 错误诊断 Prompt
│   └── v1_knowledge.json         # 知识点讲解 Prompt
├── problems/                     # 题目初始数据
│   ├── lanqiao_samples.json      # 蓝桥杯样题（50道）
│   └── custom_problems.json      # 原创题目
└── sync/
    ├── sync_luogu.py             # 洛谷题目同步脚本
    ├── sync_codeforces.py        # Codeforces 题目同步脚本
    └── sync_runner.py            # 定时同步调度器
`

**初始化流程：**
1. 数据库迁移完成后，运行 python scripts/init_db.py 导入种子数据
2. 题目同步脚本通过 OJ 开放 API 定期获取题目（首次全量，后续增量）
3. 测试数据存储于 data/test_cases/ 目录，按题目 ID 分文件夹

**System Prompt 管理：**
- 存储位置：data/seeds/prompts/
- 文件格式：每个版本/场景一个 JSON 文件
- 内容结构：包含 system_prompt、ersion、scenario 字段
- 加载方式：后端启动时读取，缓存于内存

## 二、API 接口清单

### 2.1 API 设计规范

- **基础路径**: `/api/v1`
- **认证方式**: JWT Token (Bearer Token)，通过 `Authorization: Bearer <token>` 头部传�?- **响应格式**: 统一 JSON 格式
- **分页规范**: `page` (页码, �?开�?, `per_page` (每页数量, 默认20, 最�?00)
- **错误格式**: `{ "error": { "code": "ERROR_CODE", "message": "错误描述", "details": {} } }`

### 2.2 认证模块

#### 2.2.1 邮箱注册

```
POST /api/v1/auth/register
```

**请求参数:**

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| username | string | �?| 用户名，3-50字符 |
| email | string | �?| 邮箱地址 |
| password | string | �?| 密码�?-128字符 |

**响应 (201 Created):**

```json
{
  "data": {
    "user": {
      "id": "uuid",
      "username": "string",
      "email": "string",
      "created_at": "2026-01-01T00:00:00Z"
    },
    "access_token": "jwt_token",
    "refresh_token": "jwt_token",
    "expires_in": 3600
  }
}
```

---

#### 2.2.2 邮箱登录

```
POST /api/v1/auth/login
```

**请求参数:**

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| email | string | �?| 邮箱地址 |
| password | string | �?| 密码 |

**响应 (200 OK):** 同注册响�?
---

#### 2.2.3 GitHub OAuth 登录

```
GET /api/v1/auth/github/authorize
```

**说明:** 重定向到 GitHub 授权页面

---

```
GET /api/v1/auth/github/callback
```

**查询参数:**

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| code | string | �?| GitHub 授权�?|

**响应 (200 OK):** 同注册响�?
---

#### 2.2.4 刷新 Token

```
POST /api/v1/auth/refresh
```

**请求参数:**

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| refresh_token | string | �?| 刷新令牌 |

**响应 (200 OK):**

```json
{
  "data": {
    "access_token": "jwt_token",
    "expires_in": 3600
  }
}
```

---

#### 2.2.5 获取当前用户信息

```
GET /api/v1/auth/me
```

**认证:** 需�?
**响应 (200 OK):**

```json
{
  "data": {
    "id": "uuid",
    "username": "string",
    "email": "string",
    "avatar_url": "string",
    "role": "user",
    "elo_rating": 1200,
    "profile": {
      "display_name": "string",
      "school": "string",
      "preferred_language": "cpp"
    }
  }
}
```

---

#### 2.2.6 更新用户信息

```
PUT /api/v1/auth/me
```

**认证:** 需�?
**请求参数:**

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| username | string | �?| 用户�?|
| display_name | string | �?| 显示名称 |
| bio | string | �?| 个人简�?|
| school | string | �?| 学校 |
| preferred_language | string | �?| 偏好语言 |

**响应 (200 OK):** 更新后的用户信息

---

### 2.3 题目模块

#### 2.3.1 获取题目列表

```
GET /api/v1/problems
```

**认证:** 可选（登录后可显示做题状态）

**查询参数:**

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| page | integer | �?| 页码，默�? |
| per_page | integer | �?| 每页数量，默�?0 |
| difficulty_min | integer | �?| 最小难�?1-10 |
| difficulty_max | integer | �?| 最大难�?1-10 |
| tags | string | �?| 标签筛选，逗号分隔 |
| source_oj | string | �?| 来源OJ筛�?|
| search | string | �?| 关键词搜�?|
| lanqiao_only | boolean | �?| 仅蓝桥杯题目 |
| status | string | �?| 做题状�? unsolved/attempted/solved |
| sort_by | string | �?| 排序: difficulty/created_at/submission_count |
| sort_order | string | �?| 排序方向: asc/desc |

**响应 (200 OK):**

```json
{
  "data": {
    "items": [
      {
        "id": "uuid",
        "title": "string",
        "title_slug": "string",
        "difficulty": 3,
        "tags": [{"id": "uuid", "name": "string", "color": "#hex"}],
        "source_oj": "luogu",
        "source_problem_id": "P1001",
        "status": "solved",
        "submission_count": 150,
        "acceptance_rate": 0.72
      }
    ],
    "pagination": {
      "page": 1,
      "per_page": 20,
      "total": 100,
      "total_pages": 5
    }
  }
}
```

---

#### 2.3.2 获取题目详情

```
GET /api/v1/problems/{problem_slug}
```

**认证:** 可�?
**路径参数:**

| 字段 | 类型 | 说明 |
|------|------|------|
| problem_slug | string | 题目URL标识 |

**响应 (200 OK):**

```json
{
  "data": {
    "id": "uuid",
    "title": "string",
    "title_slug": "string",
    "description": "markdown",
    "input_format": "markdown",
    "output_format": "markdown",
    "constraints": "markdown",
    "difficulty": 3,
    "time_limit_ms": 1000,
    "memory_limit_mb": 256,
    "source_oj": "luogu",
    "source_problem_id": "P1001",
    "source_url": "string",
    "tags": [...],
    "sample_test_cases": [
      {
        "id": "uuid",
        "input": "string",
        "expected_output": "string",
        "explanation": "string"
      }
    ],
    "user_status": "attempted",
    "user_last_submission": {...}
  }
}
```

---

#### 2.3.3 获取题目提交历史

```
GET /api/v1/problems/{problem_id}/submissions
```

**认证:** 需�?
**查询参数:**

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| page | integer | �?| 页码 |
| per_page | integer | �?| 每页数量 |

**响应 (200 OK):** 提交记录列表

---

#### 2.3.4 创建题目（管理员�?
```
POST /api/v1/problems
```

**认证:** 需�?(admin)

**请求参数:**

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| title | string | �?| 标题 |
| description | string | �?| 描述 |
| input_format | string | �?| 输入格式 |
| output_format | string | �?| 输出格式 |
| constraints | string | �?| 约束条件 |
| difficulty | integer | �?| 难度 1-10 |
| time_limit_ms | integer | �?| 时间限制 |
| memory_limit_mb | integer | �?| 内存限制 |
| tags | string[] | �?| 标签ID列表 |
| test_cases | object[] | �?| 测试数据 |

**响应 (201 Created):** 创建的题目详�?
---

#### 2.3.5 更新题目（管理员�?
```
PUT /api/v1/problems/{problem_id}
```

**认证:** 需�?(admin)

**请求参数:** 同创建题�?
**响应 (200 OK):** 更新后的题目详情

---

#### 2.3.6 删除题目（管理员�?
```
DELETE /api/v1/problems/{problem_id}
```

**认证:** 需�?(admin)

**响应 (204 No Content)**

---

### 2.4 评测模块

#### 2.4.1 提交代码

```
POST /api/v1/submissions
```

**认证:** 需�?
**请求参数:**

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| problem_id | string | �?| 题目ID |
| code | string | �?| 代码内容 |
| language | string | �?| 语言: cpp/py/java |

**响应 (201 Created):**

```json
{
  "data": {
    "id": "uuid",
    "problem_id": "uuid",
    "status": "Pending",
    "submitted_at": "2026-01-01T00:00:00Z",
    "queue_position": 5
  }
}
```

---

#### 2.4.2 获取提交详情

```
GET /api/v1/submissions/{submission_id}
```

**认证:** 需要（用户只能查看自己的提交，管理员可查看所有）

**响应 (200 OK):**

```json
{
  "data": {
    "id": "uuid",
    "problem": {"id": "uuid", "title": "string", "title_slug": "string"},
    "code": "string",
    "language": "cpp",
    "status": "AC",
    "score": 100,
    "runtime_ms": 125,
    "memory_kb": 16384,
    "passed_count": 10,
    "total_count": 10,
    "error_message": null,
    "submitted_at": "2026-01-01T00:00:00Z",
    "judged_at": "2026-01-01T00:00:05Z",
    "results": [
      {
        "test_case_order": 1,
        "status": "AC",
        "runtime_ms": 12,
        "memory_kb": 1024,
        "actual_output": "...",
        "diff_info": null
      }
    ]
  }
}
```

---

#### 2.4.3 获取评测状态（SSE 长轮询）

```
GET /api/v1/submissions/{submission_id}/status
```

**认证:** 需�?
**响应格式:** Server-Sent Events

```
event: status_update
data: {"status": "Compiling", "progress": 10}

event: status_update
data: {"status": "Running", "progress": 50, "current_case": 3, "total_cases": 10}

event: completed
data: {"status": "AC", "score": 100, "runtime_ms": 125, "memory_kb": 16384}
```

---

#### 2.4.4 获取用户提交历史

```
GET /api/v1/submissions
```

**认证:** 需�?
**查询参数:**

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| page | integer | �?| 页码 |
| per_page | integer | �?| 每页数量 |
| problem_id | string | �?| 筛选题�?|
| status | string | �?| 筛选状�?|
| language | string | �?| 筛选语言 |

**响应 (200 OK):** 提交记录列表

---

### 2.5 知识图谱模块

#### 2.5.1 获取知识图谱�?
```
GET /api/v1/knowledge/nodes
```

**认证:** 可�?
**查询参数:**

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| category | string | �?| 分类筛�?|
| parent_id | string | �?| 父节点ID（获取子节点�?|
| include_progress | boolean | �?| 是否包含当前用户进度 |

**响应 (200 OK):**

```json
{
  "data": {
    "nodes": [
      {
        "id": "uuid",
        "title": "动态规�?,
        "title_slug": "dynamic-programming",
        "category": "algorithm",
        "level": 2,
        "parent_id": null,
        "order_index": 5,
        "children_count": 8,
        "user_status": "in_progress",
        "children": [...]
      }
    ]
  }
}
```

---

#### 2.5.2 获取知识点详�?
```
GET /api/v1/knowledge/nodes/{node_slug}
```

**认证:** 可�?
**响应 (200 OK):**

```json
{
  "data": {
    "id": "uuid",
    "title": "背包问题",
    "title_slug": "knapsack",
    "category": "algorithm",
    "level": 3,
    "description": "markdown",
    "core_concept": "markdown",
    "applicable_scenarios": "markdown",
    "algorithm_steps": "markdown",
    "code_template_cpp": "code",
    "code_template_py": "code",
    "code_template_java": "code",
    "time_complexity": "O(nW)",
    "space_complexity": "O(nW) 可优化至 O(W)",
    "common_mistakes": "markdown",
    "prerequisites": [{"id": "uuid", "title": "线性DP"}],
    "next_nodes": [{"id": "uuid", "title": "完全背包"}],
    "related_problems": [...],
    "user_status": "not_started",
    "estimated_minutes": 45
  }
}
```

---

#### 2.5.3 获取知识点配套练�?
```
GET /api/v1/knowledge/nodes/{node_id}/problems
```

**认证:** 可�?
**响应 (200 OK):**

```json
{
  "data": {
    "problems": [
      {
        "id": "uuid",
        "title": "01背包问题",
        "difficulty": 3,
        "difficulty_level": 1,
        "status": "unsolved"
      }
    ]
  }
}
```

---

#### 2.5.4 更新学习进度

```
POST /api/v1/knowledge/progress
```

**认证:** 需�?
**请求参数:**

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| knowledge_node_id | string | �?| 知识点ID |
| status | string | �?| 状�? in_progress/completed/mastered |

**响应 (200 OK):** 更新后的进度

---

### 2.6 AI 教练模块

#### 2.6.1 创建 AI 对话会话

```
POST /api/v1/ai/conversations
```

**认证:** 需�?
**请求参数:**

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| title | string | �?| 会话标题（默认自动生成） |
| problem_id | string | �?| 关联题目ID |
| knowledge_node_id | string | �?| 关联知识点ID |
| submission_id | string | �?| 关联提交ID |
| conversation_type | string | �?| 类型 |
| initial_message | string | �?| 初始消息 |

**响应 (201 Created):**

```json
{
  "data": {
    "id": "uuid",
    "title": "P1001 求助",
    "conversation_type": "problem_help",
    "problem_id": "uuid",
    "created_at": "2026-01-01T00:00:00Z"
  }
}
```

---

#### 2.6.2 获取用户对话列表

```
GET /api/v1/ai/conversations
```

**认证:** 需�?
**查询参数:**

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| page | integer | �?| 页码 |
| per_page | integer | �?| 每页数量 |
| conversation_type | string | �?| 类型筛�?|
| problem_id | string | �?| 题目筛�?|

**响应 (200 OK):** 对话列表

---

#### 2.6.3 获取对话消息

```
GET /api/v1/ai/conversations/{conversation_id}/messages
```

**认证:** 需�?
**响应 (200 OK):**

```json
{
  "data": {
    "conversation": {...},
    "messages": [
      {
        "id": "uuid",
        "role": "user",
        "content": "string",
        "created_at": "2026-01-01T00:00:00Z"
      },
      {
        "id": "uuid",
        "role": "assistant",
        "content": "string",
        "prompt_level": 2,
        "is_error_diagnosis": false,
        "created_at": "2026-01-01T00:00:01Z"
      }
    ]
  }
}
```

---

#### 2.6.4 发送消息（流式响应�?
```
POST /api/v1/ai/conversations/{conversation_id}/messages
```

**认证:** 需�?
**请求参数:**

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| content | string | �?| 用户消息内容 |
| prompt_level | integer | �?| 请求的提示级�?1-3 |

**响应格式:** Server-Sent Events (流式)

```
event: message_start
data: {"message_id": "uuid"}

event: content_chunk
data: {"content": "�?}

event: content_chunk
data: {"content": "道题"}

event: message_end
data: {"message_id": "uuid", "prompt_level": 2, "token_count": 150}
```

---

#### 2.6.5 请求错误诊断

```
POST /api/v1/ai/diagnose
```

**认证:** 需�?
**请求参数:**

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| submission_id | string | �?| 提交ID |
| error_type | string | �?| 错误类型: WA/TLE/MLE/RE/CE |

**响应 (200 OK):** 同发送消息（流式响应�?
---

#### 2.6.6 删除对话会话

```
DELETE /api/v1/ai/conversations/{conversation_id}
```

**认证:** 需�?
**响应 (204 No Content)**

---

### 2.7 学习路径模块

#### 2.7.1 获取学习路径列表

```
GET /api/v1/learning-paths
```

**认证:** 可�?
**查询参数:**

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| category | string | �?| 分类筛�?|
| is_official | boolean | �?| 是否官方路径 |

**响应 (200 OK):**

```json
{
  "data": {
    "paths": [
      {
        "id": "uuid",
        "title": "蓝桥杯备赛路�?,
        "title_slug": "lanqiao-preparation",
        "category": "lanqiao",
        "target_audience": "大学�?,
        "estimated_days": 60,
        "total_nodes": 30,
        "user_progress": {
          "status": "in_progress",
          "completed_nodes": 10,
          "completion_percent": 33
        }
      }
    ]
  }
}
```

---

#### 2.7.2 获取学习路径详情

```
GET /api/v1/learning-paths/{path_slug}
```

**认证:** 可�?
**响应 (200 OK):**

```json
{
  "data": {
    "id": "uuid",
    "title": "蓝桥杯备赛路�?,
    "description": "markdown",
    "category": "lanqiao",
    "estimated_days": 60,
    "nodes": [
      {
        "id": "uuid",
        "knowledge_node": {"id": "uuid", "title": "基础语法", "title_slug": "..."},
        "order_index": 1,
        "is_required": true,
        "user_status": "completed"
      }
    ],
    "user_progress": {...}
  }
}
```

---

#### 2.7.3 开始学习路�?
```
POST /api/v1/learning-paths/{path_id}/start
```

**认证:** 需�?
**响应 (200 OK):** 路径进度

---

#### 2.7.4 获取用户进度概览

```
GET /api/v1/progress/overview
```

**认证:** 需�?
**响应 (200 OK):**

```json
{
  "data": {
    "total_solved": 45,
    "total_attempted": 78,
    "streak_days": 7,
    "elo_rating": 1350,
    "weak_areas": [
      {"tag": "动态规�?, "correct_rate": 0.45, "suggestion": "建议加强练习"}
    ],
    "active_paths": [...],
    "recent_submissions": [...]
  }
}
```

---

### 2.8 标签模块

#### 2.8.1 获取标签列表

```
GET /api/v1/tags
```

**查询参数:**

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| category | string | �?| 分类筛�?|
| include_problems_count | boolean | �?| 是否包含题目数量 |

**响应 (200 OK):** 标签树状列表

---

#### 2.8.2 获取标签详情

```
GET /api/v1/tags/{tag_slug}
```

**响应 (200 OK):** 标签详情及关联题�?
---

### 2.9 系统模块

#### 2.9.1 获取系统配置

```
GET /api/v1/system/config
```

**响应 (200 OK):**

```json
{
  "data": {
    "supported_languages": ["cpp", "py", "java"],
    "default_ai_model": "deepseek-v3",
    "available_ai_models": [
      {"id": "deepseek-v3", "name": "DeepSeek V3", "is_default": true},
      {"id": "gpt-4o", "name": "GPT-4o", "is_default": false}
    ],
    "site_name": "AI_code_assisstant",
    "version": "1.0.0"
  }
}
```

---

#### 2.9.2 健康检�?
```
GET /api/v1/health
```

**响应 (200 OK):**

```json
{
  "status": "healthy",
  "services": {
    "database": "ok",
    "redis": "ok",
    "judge_service": "ok"
  }
}
```

---

## 三、前端页面路�?
### 3.1 路由设计规范

- **路由模式:** Browser Router (History API)
- **布局结构:** 主布局(MainLayout) + 认证布局(AuthLayout) + 管理布局(AdminLayout)
- **权限控制:** 路由守卫(Route Guard) + 页面级权限检�?- **代码分割:** 按路由懒加载(Lazy Loading)

### 3.2 页面路由清单

#### 3.2.1 认证相关

| 路由路径 | 页面组件 | 布局 | 权限 | 核心功能 | 调用API |
|---------|---------|------|------|---------|---------|
| `/login` | LoginPage | AuthLayout | 公开 | 邮箱登录、跳转到GitHub OAuth | `POST /auth/login` |
| `/register` | RegisterPage | AuthLayout | 公开 | 邮箱注册 | `POST /auth/register` |
| `/auth/github/callback` | GitHubCallbackPage | AuthLayout | 公开 | 处理GitHub OAuth回调 | `GET /auth/github/callback` |
| `/forgot-password` | ForgotPasswordPage | AuthLayout | 公开 | 忘记密码（后续版本） | - |

---

#### 3.2.2 公共页面

| 路由路径 | 页面组件 | 布局 | 权限 | 核心功能 | 调用API |
|---------|---------|------|------|---------|---------|
| `/` | HomePage | MainLayout | 公开 | 首页、产品介绍、学习路径入�?| `GET /learning-paths` |
| `/problems` | ProblemListPage | MainLayout | 公开 | 题目列表、筛选、搜�?| `GET /problems` |
| `/problems/:problemSlug` | ProblemDetailPage | MainLayout | 公开 | 题目详情、代码编辑器、提�?| `GET /problems/:slug`, `POST /submissions` |
| `/knowledge` | KnowledgeHubPage | MainLayout | 公开 | 知识图谱总览、分类浏�?| `GET /knowledge/nodes` |
| `/knowledge/:nodeSlug` | KnowledgeNodePage | MainLayout | 公开 | 知识点详情、代码模板、配套练�?| `GET /knowledge/nodes/:slug` |
| `/learning-paths` | LearningPathsPage | MainLayout | 公开 | 学习路径列表 | `GET /learning-paths` |
| `/learning-paths/:pathSlug` | LearningPathDetailPage | MainLayout | 公开 | 路径详情、节点列表、进�?| `GET /learning-paths/:slug` |

---

#### 3.2.3 用户相关（需登录�?
| 路由路径 | 页面组件 | 布局 | 权限 | 核心功能 | 调用API |
|---------|---------|------|------|---------|---------|
| `/profile` | UserProfilePage | MainLayout | 需登录 | 个人资料、设置、API Key配置 | `GET /auth/me`, `PUT /auth/me` |
| `/submissions` | MySubmissionsPage | MainLayout | 需登录 | 提交历史、评测结�?| `GET /submissions` |
| `/submissions/:submissionId` | SubmissionDetailPage | MainLayout | 需登录 | 提交详情、测试点结果 | `GET /submissions/:id` |
| `/progress` | MyProgressPage | MainLayout | 需登录 | 学习进度、能力分析、薄弱诊�?| `GET /progress/overview` |
| `/settings` | SettingsPage | MainLayout | 需登录 | 偏好设置、AI模型选择、主�?| `PUT /auth/me` |

---

#### 3.2.4 AI 教练（需登录�?
| 路由路径 | 页面组件 | 布局 | 权限 | 核心功能 | 调用API |
|---------|---------|------|------|---------|---------|
| `/ai/chat` | AIChatPage | MainLayout | 需登录 | AI对话列表、新建对�?| `GET /ai/conversations`, `POST /ai/conversations` |
| `/ai/chat/:conversationId` | AIChatRoomPage | MainLayout | 需登录 | 对话详情、消息流、发送消�?| `GET /ai/conversations/:id/messages`, `POST /ai/conversations/:id/messages` |
| `/ai/diagnose/:submissionId` | AIDiagnosisPage | MainLayout | 需登录 | 错误诊断、AI分析 | `POST /ai/diagnose` |

---

#### 3.2.5 管理后台（需管理员权限）

| 路由路径 | 页面组件 | 布局 | 权限 | 核心功能 | 调用API |
|---------|---------|------|------|---------|---------|

---

### 3.3 页面与API调用关系�?
```
首页 (HomePage)
  └── GET /api/v1/learning-paths

题目列表 (ProblemListPage)
  └── GET /api/v1/problems?difficulty_min=&difficulty_max=&tags=&...
  └── GET /api/v1/tags

题目详情 (ProblemDetailPage)
  └── GET /api/v1/problems/:slug
  └── POST /api/v1/submissions
  └── GET /api/v1/submissions/:id/status (SSE)
  └── POST /api/v1/ai/conversations (新建AI求助会话)

知识图谱 (KnowledgeHubPage)
  └── GET /api/v1/knowledge/nodes

知识点详�?(KnowledgeNodePage)
  └── GET /api/v1/knowledge/nodes/:slug
  └── GET /api/v1/knowledge/nodes/:id/problems
  └── POST /api/v1/ai/conversations (新建知识点讲解会�?

学习路径 (LearningPathsPage)
  └── GET /api/v1/learning-paths

路径详情 (LearningPathDetailPage)
  └── GET /api/v1/learning-paths/:slug
  └── POST /api/v1/learning-paths/:id/start

提交记录 (MySubmissionsPage)
  └── GET /api/v1/submissions

提交详情 (SubmissionDetailPage)
  └── GET /api/v1/submissions/:id

AI对话 (AIChatPage)
  └── GET /api/v1/ai/conversations
  └── POST /api/v1/ai/conversations

AI对话详情 (AIChatRoomPage)
  └── GET /api/v1/ai/conversations/:id/messages
  └── POST /api/v1/ai/conversations/:id/messages (SSE)

个人进度 (MyProgressPage)
  └── GET /api/v1/progress/overview

个人设置 (SettingsPage)
  └── GET /api/v1/auth/me
  └── PUT /api/v1/auth/me
  └── GET /api/v1/system/config
```

---

## 四、补充说�?
### 4.1 安全考虑

1. **密码存储**: 使用 bcrypt 加密，cost factor 12
2. **JWT 策略**: Access Token 有效�?1 小时，Refresh Token 有效�?7 �?3. **API 限流**: 基于 Redis 的滑动窗口限流，认证接口 5�?分钟，评测提�?10�?分钟
4. **CORS 配置**: 仅允许前端域名访�?5. **SQL 注入防护**: 使用 SQLAlchemy ORM，禁止原�?SQL
6. **XSS 防护**: 前端 React 自动转义，Markdown 渲染使用 DOMPurify
7. **AI API Key 加密**: 用户自定�?API Key 使用 AES-256-GCM 加密存储

### 4.2 性能优化

1. **数据库索�?*: 所有外键和常用查询字段建立索引
2. **Redis 缓存策略**:
   - 题目列表: 缓存 5 分钟
   - 题目详情: 缓存 10 分钟
   - 知识图谱: 缓存 30 分钟
   - 用户会话: 缓存�?Token 过期
3. **评测队列**: Redis List 实现 FIFO 队列，支持优先级
4. **图片/文件**: 使用 CDN 或对象存储，数据库只�?URL
5. **分页**: 所有列表接口默�?20 �?页，最�?100 �?�?
### 4.3 Docker 部署说明

```yaml
# docker-compose.yml 核心服务
services:
  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
  
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://user:pass@db:5432/ai_code
      - REDIS_URL=redis://redis:6379
  
  db:
    image: postgres:15
    volumes:
      - postgres_data:/var/lib/postgresql/data
  
  redis:
    image: redis:7
    volumes:
      - redis_data:/data
  
  # 评测服务通过 Celery Worker 在 backend 服务中运行
  # 无需单独 judge 服务容器
```

### 4.4 开发环境端口分�?
| 服务 | 端口 | 说明 |
|------|------|------|
| 前端开发服务器 | 3000 | React Dev Server |
| 后端 API | 8000 | FastAPI + Uvicorn |
| PostgreSQL | 5432 | 数据�?|
| Redis | 6379 | 缓存 |
| 评测任务队列 | Redis | Celery + Redis Queue |

---

> 本文档为技术规格说明书 V1.0，基�?PRD V1.1 编制�? 
> 后续根据技术评审意见进行修订�?
### 3.3 ǰ��״̬������Zustand Store ��ƣ�

#### authStore �� �û���֤״̬

`	ypescript
interface AuthState {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  accessToken: string | null;
  refreshToken: string | null;
  
  // Actions
  login: (email: string, password: string) => Promise<void>;
  register: (username: string, email: string, password: string) => Promise<void>;
  logout: () => void;
  updateProfile: (data: Partial<UserProfile>) => Promise<void>;
  refreshAccessToken: () => Promise<void>;
}
`

#### problemStore �� ��Ŀ״̬

`	ypescript
interface ProblemState {
  problems: Problem[];
  currentProblem: Problem | null;
  filters: {
    difficultyMin: number;
    difficultyMax: number;
    tags: string[];
    sourceOJ: string | null;
    search: string;
  };
  pagination: PaginationState;
  isLoading: boolean;
  
  // Actions
  fetchProblems: (params?: FilterParams) => Promise<void>;
  fetchProblem: (slug: string) => Promise<void>;
  setFilters: (filters: Partial<FilterState>) => void;
  submitCode: (problemId: string, code: string, language: string) => Promise<Submission>;
}
`

#### aiChatStore �� AI �Ի�״̬

`	ypescript
interface AIChatState {
  conversations: Conversation[];
  currentConversation: Conversation | null;
  messages: Message[];
  isStreaming: boolean;
  currentStreamingContent: string;
  
  // Actions
  fetchConversations: () => Promise<void>;
  createConversation: (params: CreateConversationParams) => Promise<Conversation>;
  sendMessage: (conversationId: string, content: string, promptLevel?: number) => Promise<void>;
  fetchMessages: (conversationId: string) => Promise<void>;
  deleteConversation: (id: string) => Promise<void>;
}
`

#### submissionStore �� �ύ��¼״̬

`	ypescript
interface SubmissionState {
  submissions: Submission[];
  currentSubmission: Submission | null;
  isPolling: boolean;
  
  // Actions
  fetchSubmissions: (params?: SubmissionFilter) => Promise<void>;
  fetchSubmission: (id: string) => Promise<void>;
  pollSubmissionStatus: (id: string) => void;
}
`

#### knowledgeStore �� ֪ʶͼ��״̬

`	ypescript
interface KnowledgeState {
  nodes: KnowledgeNode[];
  currentNode: KnowledgeNode | null;
  tree: TreeNode[];
  userProgress: Record<string, ProgressStatus>;
  
  // Actions
  fetchKnowledgeTree: () => Promise<void>;
  fetchNode: (slug: string) => Promise<void>;
  updateProgress: (nodeId: string, status: ProgressStatus) => Promise<void>;
}
`
