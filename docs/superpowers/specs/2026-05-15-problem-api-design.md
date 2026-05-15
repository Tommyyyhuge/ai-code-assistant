# 题目 API + 标签体系设计方案

> 日期: 2026-05-15  
> 版本: v1.0  
> 范围: 后端题目 CRUD + 标签体系（不含测试用例）  
> 方案: 传统分层扩展（方案 A）

---

## 1. 项目背景

AI_code_assistant 当前后端仅有用户认证模块，前端题目功能使用 Mock 数据。本设计旨在实现后端题目 API 和标签体系，使前端能够切换至真实数据源，为后续评测引擎和 AI 教练功能奠定基础。

## 2. 范围边界

### 2.1 包含（IN SCOPE）

- `problems` 表：题目基本信息 CRUD
- `tags` 表：标签体系 CRUD
- `problem_tag_associations` 表：题目标签多对多关联
- 题目列表 API（支持筛选 + 分页）
- 题目详情 API
- 标签列表 API
- 数据库迁移脚本

### 2.2 排除（OUT OF SCOPE）

- `test_cases` 表及测试数据管理（纳入评测引擎阶段）
- `submissions` 表及提交记录（纳入评测引擎阶段）
- 文件上传/存储（题目描述中的图片等）
- 题目导入/导出（如从洛谷 API 同步）
- 高级搜索（全文检索、Elasticsearch）
- 题目统计（通过次数、提交次数等）

## 3. 架构方案

采用**传统分层扩展**（方案 A），在现有代码结构下直接新增模块：

```
models/     -> 新增 Problem、Tag、ProblemTagAssociation
schemas/    -> 新增 Problem、Tag 的 Pydantic Schema
routers/    -> 新增 problems.py、tags.py
services/   -> 新增 problem_service.py、tag_service.py
```

**选择理由**：
- 与现有 auth 模块风格 100% 一致
- 当前项目规模小（2-3 个新模型），无需引入 Repository 或 CQRS 的额外抽象
- 开发速度快，便于调试

## 4. 数据模型设计

### 4.1 Problem（题目）

| 字段 | 类型 | 约束 | 默认值 | 说明 |
|------|------|------|--------|------|
| id | UUID | PK | gen_random_uuid() | 唯一标识 |
| title | VARCHAR(255) | NOT NULL | - | 题目标题 |
| title_slug | VARCHAR(255) | UNIQUE, NOT NULL | - | URL 友好标识 |
| description | TEXT | NOT NULL | - | 题目描述（Markdown） |
| input_format | TEXT | NOT NULL | - | 输入格式说明 |
| output_format | TEXT | NOT NULL | - | 输出格式说明 |
| constraints | TEXT | NULL | NULL | 数据范围与约束 |
| difficulty | SMALLINT | NOT NULL, CHECK(1-10) | 1 | 难度分 1-10 |
| time_limit_ms | INTEGER | NOT NULL | 1000 | 时间限制（毫秒） |
| memory_limit_mb | INTEGER | NOT NULL | 256 | 内存限制（MB） |
| source_oj | VARCHAR(50) | NULL | NULL | 来源 OJ |
| source_problem_id | VARCHAR(100) | NULL | NULL | 来源 OJ 原始题号 |
| source_url | VARCHAR(500) | NULL | NULL | 来源 URL |
| is_published | BOOLEAN | NOT NULL | FALSE | 是否已发布 |
| created_by | UUID | FK→users.id, NULL | NULL | 创建者 |
| created_at | TIMESTAMP | NOT NULL | NOW() | 创建时间 |
| updated_at | TIMESTAMP | NOT NULL | NOW() | 更新时间 |

**索引**：
- `idx_problems_difficulty`: difficulty
- `idx_problems_source_oj`: source_oj
- `idx_problems_published`: is_published, created_at
- `idx_problems_title`: title（GIN 全文搜索，后续优化）

### 4.2 Tag（标签）

| 字段 | 类型 | 约束 | 默认值 | 说明 |
|------|------|------|--------|------|
| id | UUID | PK | gen_random_uuid() | 唯一标识 |
| name | VARCHAR(100) | UNIQUE, NOT NULL | - | 标签名称 |
| name_slug | VARCHAR(100) | UNIQUE, NOT NULL | - | URL 友好名称 |
| category | VARCHAR(50) | NOT NULL | - | 分类：algorithm/datastructure/lanqiao |
| parent_id | UUID | FK→tags.id, NULL | NULL | 父标签 ID（树状结构） |
| description | TEXT | NULL | NULL | 标签描述 |
| color | VARCHAR(7) | NULL | NULL | 标签颜色（HEX） |
| is_lanqiao_special | BOOLEAN | NOT NULL | FALSE | 是否蓝桥杯特色标签 |
| created_at | TIMESTAMP | NOT NULL | NOW() | 创建时间 |

**索引**：
- `idx_tags_category`: category
- `idx_tags_parent`: parent_id

### 4.3 ProblemTagAssociation（题目标签关联）

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| problem_id | UUID | PK, FK→problems.id, ON DELETE CASCADE | 题目 ID |
| tag_id | UUID | PK, FK→tags.id, ON DELETE CASCADE | 标签 ID |
| is_primary | BOOLEAN | NOT NULL, DEFAULT FALSE | 是否主要标签 |
| created_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | 创建时间 |

## 5. Pydantic Schemas

### 5.1 Problem Schemas

```python
class ProblemBase(BaseModel):
    title: str
    description: str
    input_format: str
    output_format: str
    constraints: Optional[str] = None
    difficulty: int = Field(..., ge=1, le=10)
    time_limit_ms: int = 1000
    memory_limit_mb: int = 256
    source_oj: Optional[str] = None
    source_problem_id: Optional[str] = None
    source_url: Optional[str] = None

class ProblemCreate(ProblemBase):
    tag_ids: Optional[List[UUID]] = []

class ProblemUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    input_format: Optional[str] = None
    output_format: Optional[str] = None
    constraints: Optional[str] = None
    difficulty: Optional[int] = Field(None, ge=1, le=10)
    time_limit_ms: Optional[int] = None
    memory_limit_mb: Optional[int] = None
    source_oj: Optional[str] = None
    source_problem_id: Optional[str] = None
    source_url: Optional[str] = None
    tag_ids: Optional[List[UUID]] = None

class ProblemInDB(ProblemBase):
    id: UUID
    title_slug: str
    is_published: bool
    created_by: Optional[UUID] = None
    created_at: datetime
    updated_at: datetime
    tags: List[TagBrief] = []
    
    class Config:
        from_attributes = True

class ProblemListItem(BaseModel):
    id: UUID
    title: str
    title_slug: str
    difficulty: int
    source_oj: Optional[str] = None
    tags: List[TagBrief] = []
    
    class Config:
        from_attributes = True
```

### 5.2 Tag Schemas

```python
class TagBase(BaseModel):
    name: str
    category: str
    description: Optional[str] = None
    color: Optional[str] = None
    is_lanqiao_special: bool = False

class TagCreate(TagBase):
    parent_id: Optional[UUID] = None

class TagInDB(TagBase):
    id: UUID
    name_slug: str
    parent_id: Optional[UUID] = None
    created_at: datetime
    
    class Config:
        from_attributes = True

class TagBrief(BaseModel):
    id: UUID
    name: str
    color: Optional[str] = None
```

### 5.3 分页响应

```python
class PaginatedResponse(BaseModel, Generic[T]):
    items: List[T]
    total: int
    page: int
    page_size: int
    total_pages: int
```

## 6. API 接口设计

### 6.1 Problem Routes (`/api/problems`)

| 方法 | 路径 | 功能 | 认证 |
|------|------|------|------|
| GET | `/` | 题目列表（筛选+分页） | 可选 |
| GET | `/{problem_id}` | 题目详情 | 可选 |
| POST | `/` | 创建题目 | 需要 |
| PATCH | `/{problem_id}` | 更新题目 | 需要 |
| DELETE | `/{problem_id}` | 删除题目 | 管理员 |

**查询参数（GET /）**：
- `search`: 关键词搜索（title + description，ILIKE）
- `difficulty_min`: 最小难度（1-10）
- `difficulty_max`: 最大难度（1-10）
- `source_oj`: 来源平台（luogu/codeforces/libreoj/custom）
- `tag_ids`: 标签 ID 列表（Query 数组，AND 关系）
- `page`: 页码（默认 1）
- `page_size`: 每页数量（默认 20，最大 100）

### 6.2 Tag Routes (`/api/tags`)

| 方法 | 路径 | 功能 | 认证 |
|------|------|------|------|
| GET | `/` | 标签列表 | 可选 |
| GET | `/{tag_id}` | 标签详情 | 可选 |
| POST | `/` | 创建标签 | 管理员 |

**查询参数（GET /）**：
- `category`: 分类筛选（algorithm/datastructure/lanqiao）

## 7. Service 层设计

### 7.1 ProblemService

```python
class ProblemService:
    @staticmethod
    async def list_problems(
        db: AsyncSession,
        search: Optional[str] = None,
        difficulty_min: Optional[int] = None,
        difficulty_max: Optional[int] = None,
        source_oj: Optional[str] = None,
        tag_ids: Optional[List[UUID]] = None,
        page: int = 1,
        page_size: int = 20
    ) -> Tuple[List[Problem], int]:
        # 1. 构建基础查询
        # 2. 动态添加筛选条件
        # 3. 计算总数
        # 4. 分页获取数据
        # 5. 加载关联标签（selectinload）
        pass

    @staticmethod
    async def get_problem(db: AsyncSession, problem_id: UUID) -> Optional[Problem]:
        # 获取详情，404 如果不存在
        pass

    @staticmethod
    async def create_problem(
        db: AsyncSession, 
        data: ProblemCreate, 
        user_id: UUID
    ) -> Problem:
        # 1. 生成 title_slug（slugify）
        # 2. 创建 Problem 实例
        # 3. 关联标签（验证 tag_ids 有效性）
        # 4. 提交事务
        pass

    @staticmethod
    async def update_problem(
        db: AsyncSession,
        problem_id: UUID,
        data: ProblemUpdate
    ) -> Problem:
        # 1. 查找现有题目
        # 2. 更新非 None 字段
        # 3. 如提供 tag_ids，重新关联标签
        # 4. 提交事务
        pass

    @staticmethod
    async def delete_problem(db: AsyncSession, problem_id: UUID) -> None:
        # 级联删除由数据库 ON DELETE CASCADE 处理
        pass
```

### 7.2 TagService

```python
class TagService:
    @staticmethod
    async def list_tags(
        db: AsyncSession,
        category: Optional[str] = None
    ) -> List[Tag]:
        pass

    @staticmethod
    async def get_tags_by_ids(
        db: AsyncSession,
        tag_ids: List[UUID]
    ) -> List[Tag]:
        # 批量获取标签，用于创建/更新题目时验证
        pass
```

## 8. 筛选逻辑详解

**动态查询构建**（SQLAlchemy 2.0 风格）：

```python
query = select(Problem).where(Problem.is_published == True)

# 关键词搜索
if search:
    query = query.where(
        or_(
            Problem.title.ilike(f"%{search}%"),
            Problem.description.ilike(f"%{search}%")
        )
    )

# 难度范围
if difficulty_min is not None:
    query = query.where(Problem.difficulty >= difficulty_min)
if difficulty_max is not None:
    query = query.where(Problem.difficulty <= difficulty_max)

# 来源筛选
if source_oj:
    query = query.where(Problem.source_oj == source_oj)

# 标签筛选（AND 关系：题目必须包含所有指定标签）
if tag_ids:
    for tag_id in tag_ids:
        query = query.where(
            Problem.tags.any(Tag.id == tag_id)
        )

# 分页
total = await db.scalar(select(func.count()).select_from(query.subquery()))
query = query.offset((page - 1) * page_size).limit(page_size)
query = query.options(selectinload(Problem.tags))
```

## 9. 权限控制

| 操作 | 要求 |
|------|------|
| 查看题目列表/详情 | 无需认证 |
| 创建题目 | 需登录（后续可改为仅管理员） |
| 更新题目 | 需登录，且为创建者或管理员 |
| 删除题目 | 仅管理员 |
| 创建标签 | 仅管理员 |

## 10. 前端数据对齐

前端 Mock 数据与后端字段映射：

| 前端字段 | 后端字段 | 映射说明 |
|----------|----------|----------|
| `difficulty: 'Easy'` | `difficulty: 1-3` | Easy=1-3, Medium=4-7, Hard=8-10 |
| `category: '字符串'` | `tags: [{name: '字符串'}]` | category 映射为主要标签 |
| `source: '洛谷'` | `source_oj: 'luogu'` | 中文名转标识符 |

## 11. 文件结构

```
backend/app/
├── models/
│   ├── __init__.py
│   ├── user.py              # 现有
│   ├── problem.py           # 新增
│   ├── tag.py               # 新增
│   └── problem_tag_association.py  # 新增
├── schemas/
│   ├── __init__.py
│   ├── user.py              # 现有
│   ├── problem.py           # 新增
│   └── tag.py               # 新增
├── routers/
│   ├── __init__.py
│   ├── auth.py              # 现有
│   ├── problems.py          # 新增
│   └── tags.py              # 新增
├── services/
│   ├── __init__.py
│   ├── auth_service.py      # 现有
│   ├── problem_service.py   # 新增
│   └── tag_service.py       # 新增
└── main.py                  # 注册 problems, tags 路由
```

## 12. 数据库迁移

新增 Alembic 迁移脚本，创建以下表：
- `problems`
- `tags`
- `problem_tag_associations`

## 13. 错误处理

| 场景 | HTTP 状态码 | 错误信息 |
|------|------------|----------|
| 题目不存在 | 404 | "Problem not found" |
| 标签不存在 | 400 | "Invalid tag IDs: [...]" |
| 标题重复（slug 冲突）| 409 | "Problem with this title already exists" |
| 无权限 | 403 | "Insufficient permissions" |
| 参数验证失败 | 422 | Pydantic 自动处理 |

## 14. 测试策略

- **单元测试**：Service 层筛选逻辑、slug 生成
- **API 测试**：FastAPI TestClient 测试各端点
- **数据工厂**：使用 factory-boy 或手动 fixture 创建测试数据

---

## 15. 后续扩展点

1. **全文搜索**：将 title 搜索升级为 PostgreSQL 全文检索（GIN 索引）
2. **题目统计**：添加 `acceptance_rate`、`submission_count` 等字段（依赖评测引擎）
3. **题目导入**：从洛谷/Codeforces API 同步题目
4. **测试用例管理**：评测引擎阶段补充 test_cases 表和文件存储
