# AI_code_assisstant 技术决策确认书

> 版本: v1.0 (最终确认版)  
> 日期: 2026年5月14日  
> 确认方式: 头脑风暴逐项确认  

---

## 一、开发环境约束（新增）

> ⚠️ 以下约束由项目经理明确指定，所有开发和部署操作必须遵守。

### 1. Python 虚拟环境约束

- **必须使用 Anaconda 创建新虚拟环境**，不能直接使用 base 环境
- 虚拟环境命名建议：`ai_code_assistant_env`
- 所有 Python 依赖（FastAPI、SQLAlchemy、Celery、psycopg2 等）必须在虚拟环境中安装
- 创建命令示例：`conda create -n ai_code_assistant_env python=3.11`
- 激活命令：`conda activate ai_code_assistant_env`

### 2. 软件安装审批约束

- **任何软件或依赖的安装前，必须先向项目经理汇报**：
  - 软件/依赖名称和版本
  - 安装原因和必要性
  - 安装步骤和占用空间
  - 是否需要管理员权限
- **获得项目经理明确同意后才能执行安装**
- 紧急情况下（如阻塞开发）可以简要汇报，但仍需事后补充完整信息

### 3. 磁盘分区约束

- **所有软件和依赖优先安装到非 C 盘**（如 D 盘、E 盘）
- 只有在以下情况才允许安装到 C 盘：
  - 软件自身强制要求（如 Docker Desktop 默认安装路径）
  - 操作系统级别的依赖（如 Visual C++ Redistributable）
  - 获得项目经理明确授权
- 数据存储（数据库文件、测试数据、日志）必须放在非 C 盘
- 项目代码仓库建议放在 `D:\AI_code_assistant\` 目录下

---

## 二、基础技术栈（用户初始约束）

| 层次 | 技术选型 | 版本/说明 |
|------|---------|----------|
| 前端框架 | React + TypeScript | React 18, TypeScript 5.x |
| 前端样式 | Tailwind CSS | v3.x |
| 状态管理 | Zustand | 轻量状态管理 |
| 后端框架 | FastAPI (Python) | Python 3.10+ |
| 数据库 | PostgreSQL + SQLAlchemy | PostgreSQL 15+ |
| 迁移工具 | Alembic | SQLAlchemy 官方迁移工具 |
| 缓存/队列 | Redis | Redis 7+ |
| 评测沙箱 | Docker + Celery | 容器化隔离 + 异步任务队列 |
| AI 接入 | HTTP Client + 工厂模式 | 默认 DeepSeek, 支持 OpenAI 兼容 API |
| 部署 | Docker Compose | 一键启动，开发环境支持热重载 |

---

## 二、逐项确认的技术决策

### 1. 评测服务架构 ✅

**决策: Celery Worker 独立容器运行**

- FastAPI API 服务与 Celery Worker 分离为两个容器
- 通过 Redis 作为消息队列通信
- Worker 容器需要 Docker-in-Docker 权限执行用户代码
- 优势: 评测任务不随 API 重启而中断，符合 Docker 最佳实践

### 2. 前端代码编辑器 ✅

**决策: CodeMirror 6**

- 模块化设计，按需加载 C++/Python/Java 语法支持
- 基础体积约 500KB，远小于 Monaco (3MB+)
- 支持括号匹配、自动缩进、代码折叠
- MVP 阶段不需要完整的 IDE 体验

### 3. AI 模型接入 ✅

**决策: DeepSeek + 用户可配 OpenAI 兼容 API**

- 默认使用平台配置的 DeepSeek V3 API
- 用户在设置页可填入自己的 OpenAI 兼容 API Key
- 后端实现统一抽象层，支持多 Provider 切换
- 费用控制: 平台承担默认调用，用户自配 Key 走用户账户

### 4. 题目数据来源 ✅

**决策: 混合策略（手动导入 + 有限自动同步）**

- 手动导入 200 道精选题目（含 50 道蓝桥杯真题）
- 开发洛谷、Codeforces 同步脚本作为实验性功能
- 所有题目标注来源，避免版权争议
- 首次上线依赖手动导入，后续逐步增加自动同步

### 5. 数据库迁移工具 ✅

**决策: Alembic**

- SQLAlchemy 官方迁移工具，标准组合
- 支持自动生成迁移脚本、版本管理、回滚
- 开发阶段改表结构时非常有用
- 命令: `alembic revision --autogenerate`, `alembic upgrade head`

### 6. 前端路由权限控制 ✅

**决策: 前端路由守卫 + 后端鉴权双重验证**

- Zustand authStore 维护登录状态
- React Router 路由守卫读取 authStore 进行前端跳转
- App 初始化时调用 `GET /api/v1/auth/me` 验证 Token 有效性
- 后端每个受保护接口独立验证 JWT Token

### 7. Docker 开发环境 ✅

**决策: Docker Compose + 开发优化**

- 所有服务（前端、后端、DB、Redis、Worker）都在 Docker 中运行
- 后端 Uvicorn 启用 `--reload` 模式
- 前端启用 React Fast Refresh
- 开发配置与生产配置分离（`docker-compose.yml` vs `docker-compose.prod.yml`）
- Windows 下使用 Docker Desktop WSL2 后端优化文件监控

### 8. 评测沙箱安全 ✅

**决策: 严格限制（多层安全策略）**

```bash
# Docker 运行参数示例
docker run \
  --network none \                    # 网络隔离
  --read-only \                       # 只读文件系统
  --tmpfs /tmp:rw,noexec,nosuid,size=10m \  # 临时文件系统
  --security-opt seccomp=seccomp.json \     # seccomp 限制系统调用
  --user 1000:1000 \                  # 非 root 运行
  --memory 256m \                     # 内存限制
  --cpus 1.0 \                        # CPU 限制
  --timeout 60 \                      # 超时限制
  judge-runner
```

- seccomp 配置文件禁止 exec、fork、socket 等危险调用
- 用户代码在 tmpfs 中运行，退出后自动清理
- 资源限制: CPU 时间、内存、输出大小、进程数

### 9. 前端状态持久化 ✅

**决策: 仅关键状态持久化到 localStorage**

持久化内容:
- `access_token` / `refresh_token`（登录状态）
- `preferred_language`（偏好语言: cpp/py/java）
- `theme`（主题: light/dark）
- `editor_code:{problem_id}`（编辑器未提交代码，按题目分 key）

不持久化内容:
- 题目列表、知识图谱（刷新后重新获取）
- AI 对话记录（从服务端加载）
- 提交记录（从服务端加载）

### 10. 错误处理和日志 ✅

**决策: 基础方案**

- FastAPI 统一异常处理器返回标准错误 JSON
- 前端 Toast/Notification 组件提示用户
- 日志输出到容器 stdout，Docker 收集查看
- MVP 阶段不引入 Sentry 等外部错误追踪服务
- 后续用户量增长后再评估是否需要 Sentry

---

## 三、数据初始化方案

```
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
```

**初始化流程:**
1. `alembic upgrade head` 执行数据库迁移
2. `python scripts/init_db.py` 导入种子数据
3. 测试数据存储于 `data/test_cases/` 目录，按题目 ID 分文件夹

---

## 四、Zustand Store 设计

### authStore — 用户认证状态

```typescript
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
```

### problemStore — 题目状态

```typescript
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
```

### aiChatStore — AI 对话状态

```typescript
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
```

### submissionStore — 提交记录状态

```typescript
interface SubmissionState {
  submissions: Submission[];
  currentSubmission: Submission | null;
  isPolling: boolean;
  
  // Actions
  fetchSubmissions: (params?: SubmissionFilter) => Promise<void>;
  fetchSubmission: (id: string) => Promise<void>;
  pollSubmissionStatus: (id: string) => void;
}
```

### knowledgeStore — 知识图谱状态

```typescript
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
```

---

## 五、Docker 部署架构

```yaml
# docker-compose.yml (开发环境)
services:
  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    volumes:
      - ./frontend:/app
      - /app/node_modules
    environment:
      - VITE_API_URL=http://localhost:8000
  
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    volumes:
      - ./backend:/app
    environment:
      - DATABASE_URL=postgresql://user:pass@db:5432/ai_code
      - REDIS_URL=redis://redis:6379
      - DEBUG=true
    command: uvicorn main:app --reload --host 0.0.0.0 --port 8000
  
  worker:
    build: ./backend
    volumes:
      - ./backend:/app
      - /var/run/docker.sock:/var/run/docker.sock
    environment:
      - DATABASE_URL=postgresql://user:pass@db:5432/ai_code
      - REDIS_URL=redis://redis:6379
    command: celery -A tasks worker --loglevel=info
    privileged: true  # Docker in Docker
  
  db:
    image: postgres:15
    volumes:
      - postgres_data:/var/lib/postgresql/data
    environment:
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=pass
      - POSTGRES_DB=ai_code
  
  redis:
    image: redis:7
    volumes:
      - redis_data:/data

volumes:
  postgres_data:
  redis_data:
```

---

## 六、MVP 明确不做（后续版本）

根据 PRD 和技术评审意见，MVP 阶段明确不做：

1. **管理后台** — 题目/知识点管理通过数据库直接操作或命令行脚本
2. **用户社交功能** — 无关注、私信、讨论区
3. **竞赛模式** — 无模拟赛、排行榜、团队功能
4. **题解社区** — 无用户发布题解功能
5. **班级/教练管理系统** — 无学生进度管理、作业布置
6. **移动端适配** — 仅桌面端 Web 应用
7. **复杂可视化动画** — 无算法执行过程动画
8. **Elo 评分系统** — 无竞赛能力分计算
9. **薄弱分析和训练计划** — 无自动推荐算法
10. **成就系统** — 无连续打卡、里程碑
11. **Sentry 错误追踪** — 仅基础日志
12. **对象存储** — 测试数据存在本地文件系统

---

## 七、开发阶段里程碑

| 阶段 | 周期 | 核心交付 |
|------|------|----------|
| Week 1-2 | 2周 | 项目脚手架 + 数据库 + Docker 环境 + 认证模块 |
| Week 3-4 | 2周 | 题库同步 + 知识图谱数据结构 + 题目列表页 |
| Week 5-6 | 2周 | 在线评测完整流程 + 知识内容页（15 个知识点） |
| Week 7-8 | 2周 | AI 教练对话 + 三级提示 + 蓝桥杯路径 |
| Week 9-10 | 2周 | 配套练习关联 + 用户系统 + UI 打磨 |
| Week 11-12 | 2周 | Docker 部署 + 文档 + 开源准备 |

---

> 本文档汇总了头脑风暴阶段确认的所有技术决策。  
> 所有决策已与项目经理逐项确认，可作为开发依据。  
> 如需调整任何技术决策，请在此文档基础上修订。
