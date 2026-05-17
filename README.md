# AI Code Assistant - 算法学习平台

面向算法竞赛（蓝桥杯/CSP/NOIP）的编程学习平台，支持在线刷题、知识图谱浏览、学习路径追踪。

## 功能

- **题库系统** — 题目浏览、搜索、CodeMirror 在线编辑
- **在线评测** — 代码提交 + Docker 沙箱自动评测（C++/Python）
- **知识图谱** — 20 个算法知识点，ltree 树形结构，支持学习进度追踪
- **用户系统** — 注册/登录（JWT + 限流）、Token 刷新

## 技术栈

| 层 | 技术 |
|---|------|
| 前端 | React 18 + TypeScript + Zustand + Tailwind CSS + CodeMirror 6 |
| 后端 | FastAPI + SQLAlchemy async + PostgreSQL + Redis + Celery |
| 评测 | Docker 沙箱 + seccomp 安全策略 |
| 部署 | Docker Compose |

## 快速开始

### 环境要求

- Python 3.11+ (Conda)
- PostgreSQL 15+
- Redis 7+
- Docker Desktop

### 启动

```bash
# 1. 创建并激活虚拟环境
conda create -n ai_code_assistant_env python=3.11
conda activate ai_code_assistant_env

# 2. 安装依赖
cd backend
pip install -r requirements.txt
cp .env.example .env   # 编辑 .env 填入配置

# 3. 数据库迁移
alembic upgrade head

# 4. 导入种子数据
python -m app.data_seed
python -m app.data_path_seed
python -m app.data_problem_seed

# 5. 启动后端
uvicorn app.main:app --reload --port 8000

# 6. 新终端，启动前端
cd frontend
npm install
npm run dev
```

浏览器打开 http://localhost:3000

### Docker 一键启动

```bash
cp .env.example .env  # 编辑 .env
docker compose up -d
```

## 项目结构

```
├── backend/           # FastAPI 后端
│   ├── app/
│   │   ├── models/    # SQLAlchemy 模型
│   │   ├── schemas/   # Pydantic 校验
│   │   ├── services/  # 业务逻辑
│   │   └── routers/   # API 路由
│   ├── alembic/       # 数据库迁移
│   └── judge/         # Docker 评测沙箱
├── frontend/          # React 前端
│   └── src/
│       ├── pages/     # 页面组件
│       ├── components/# 通用组件
│       ├── stores/    # Zustand 状态管理
│       └── services/  # API 调用
└── docs/              # 设计文档
    └── superpowers/
        ├── specs/     # 功能规格
        └── plans/     # 实现计划
```

## 许可证

MIT
