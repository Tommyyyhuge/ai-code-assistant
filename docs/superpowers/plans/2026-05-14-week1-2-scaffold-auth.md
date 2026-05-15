# Week 1-2: 项目脚手架 + 数据库 + 认证模块 实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 搭建完整的开发环境（Docker + Anaconda），创建前后端项目脚手架，配置 PostgreSQL 数据库和 Alembic 迁移，实现用户注册/登录/JWT 认证/GitHub OAuth。

**Architecture:** 前后端分离架构。后端 FastAPI 提供 RESTful API，前端 React + Vite 单页应用，通过 Docker Compose 编排所有服务。数据库使用 PostgreSQL，迁移工具 Alembic，认证使用 JWT + bcrypt。

**Tech Stack:** FastAPI, SQLAlchemy, Alembic, PostgreSQL, Redis, React 18, TypeScript, Vite, Tailwind CSS, Zustand, Docker, Docker Compose, Anaconda

---

## 前置约束（必须遵守）

1. **Python 虚拟环境**: 必须使用 Anaconda 创建新环境 `ai_code_assistant_env`
2. **安装审批**: 任何软件/依赖安装前必须向项目经理汇报，获得同意后才能安装
3. **磁盘分区**: 优先安装到非 C 盘，项目代码放在 `D:\AI_code_assistant\`

---

## 文件结构规划

```
D:\AI_code_assistant\
├── docker-compose.yml              # Docker Compose 开发配置
├── docker-compose.prod.yml         # Docker Compose 生产配置
├── .env.example                    # 环境变量模板
├── backend\                       # FastAPI 后端
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── alembic.ini
│   ├── alembic\                   # 迁移脚本目录
│   │   ├── env.py
│   │   ├── script.py.mako
│   │   └── versions\
│   ├── app\                       # 应用代码
│   │   ├── __init__.py
│   │   ├── main.py                # FastAPI 入口
│   │   ├── config.py              # 配置管理
│   │   ├── database.py            # 数据库连接
│   │   ├── models\                # SQLAlchemy 模型
│   │   │   ├── __init__.py
│   │   │   └── user.py
│   │   ├── schemas\               # Pydantic 模型
│   │   │   ├── __init__.py
│   │   │   └── user.py
│   │   ├── routers\               # API 路由
│   │   │   ├── __init__.py
│   │   │   └── auth.py
│   │   ├── services\              # 业务逻辑
│   │   │   ├── __init__.py
│   │   │   └── auth_service.py
│   │   └── utils\                 # 工具函数
│   │       ├── __init__.py
│   │       └── security.py        # JWT + bcrypt
│   └── tests\                     # 测试
│       ├── __init__.py
│       ├── conftest.py
│       └── test_auth.py
├── frontend\                      # React 前端
│   ├── Dockerfile
│   ├── package.json
│   ├── vite.config.ts
│   ├── tailwind.config.js
│   ├── tsconfig.json
│   ├── index.html
│   └── src\
│       ├── main.tsx
│       ├── App.tsx
│       ├── index.css
│       ├── stores\                # Zustand stores
│       │   └── authStore.ts
│       ├── components\            # 组件
│       │   ├── LoginForm.tsx
│       │   └── RegisterForm.tsx
│       ├── pages\                 # 页面
│       │   ├── HomePage.tsx
│       │   └── LoginPage.tsx
│       └── services\              # API 服务
│           └── api.ts
└── docs\                          # 文档
    └── ...
```

---

## Task 1: 创建项目目录结构

**Files:**
- Create: `D:\AI_code_assistant\docker-compose.yml`
- Create: `D:\AI_code_assistant\.env.example`
- Create: 上述所有目录结构

- [ ] **Step 1: 创建后端目录结构**

```powershell
# 在 PowerShell 中执行
$basePath = "D:\AI_code_assistant"

# 创建目录
$dirs = @(
    "$basePath\backend\app\models",
    "$basePath\backend\app\schemas",
    "$basePath\backend\app\routers",
    "$basePath\backend\app\services",
    "$basePath\backend\app\utils",
    "$basePath\backend\alembic\versions",
    "$basePath\backend\tests",
    "$basePath\frontend\src\stores",
    "$basePath\frontend\src\components",
    "$basePath\frontend\src\pages",
    "$basePath\frontend\src\services",
    "$basePath\docs\superpowers\plans"
)

foreach ($dir in $dirs) {
    New-Item -ItemType Directory -Path $dir -Force
}

Write-Host "目录结构创建完成"
```

Expected: 所有目录成功创建

- [ ] **Step 2: 创建空 init 文件**

```powershell
$initFiles = @(
    "$basePath\backend\app\__init__.py",
    "$basePath\backend\app\models\__init__.py",
    "$basePath\backend\app\schemas\__init__.py",
    "$basePath\backend\app\routers\__init__.py",
    "$basePath\backend\app\services\__init__.py",
    "$basePath\backend\app\utils\__init__.py",
    "$basePath\backend\tests\__init__.py"
)

foreach ($file in $initFiles) {
    New-Item -ItemType File -Path $file -Force
}

Write-Host "Init 文件创建完成"
```

Expected: 所有 __init__.py 文件成功创建

- [ ] **Step 3: Commit**

```bash
cd D:\AI_code_assistant
git init
git add .
git commit -m "chore: init project directory structure"
```

---

## Task 2: Docker Compose 配置

**Files:**
- Create: `D:\AI_code_assistant\docker-compose.yml`
- Create: `D:\AI_code_assistant\.env.example`

- [ ] **Step 1: 编写 docker-compose.yml**

```yaml
# D:\AI_code_assistant\docker-compose.yml
services:
  db:
    image: postgres:15-alpine
    container_name: ai_code_db
    volumes:
      - postgres_data:/var/lib/postgresql/data
    environment:
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=postgres
      - POSTGRES_DB=ai_code_assistant
    ports:
      - "5432:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 5s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7-alpine
    container_name: ai_code_redis
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 5s
      timeout: 5s
      retries: 5

  backend:
    build: ./backend
    container_name: ai_code_backend
    volumes:
      - ./backend:/app
      - /app/__pycache__
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql+asyncpg://postgres:postgres@db:5432/ai_code_assistant
      - REDIS_URL=redis://redis:6379/0
      - SECRET_KEY=dev-secret-key-change-in-production
      - ACCESS_TOKEN_EXPIRE_MINUTES=60
      - REFRESH_TOKEN_EXPIRE_DAYS=7
      - ALGORITHM=HS256
      - GITHUB_CLIENT_ID=
      - GITHUB_CLIENT_SECRET=
    depends_on:
      db:
        condition: service_healthy
      redis:
        condition: service_healthy
    command: uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

  frontend:
    build: ./frontend
    container_name: ai_code_frontend
    volumes:
      - ./frontend:/app
      - /app/node_modules
    ports:
      - "3000:3000"
    environment:
      - VITE_API_URL=http://localhost:8000
    command: npm run dev -- --host 0.0.0.0 --port 3000

volumes:
  postgres_data:
  redis_data:
```

- [ ] **Step 2: 编写 .env.example**

```bash
# D:\AI_code_assistant\.env.example
# 数据库
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/ai_code_assistant
REDIS_URL=redis://localhost:6379/0

# JWT
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
REFRESH_TOKEN_EXPIRE_DAYS=7

# GitHub OAuth
GITHUB_CLIENT_ID=your-github-client-id
GITHUB_CLIENT_SECRET=your-github-client-secret

# AI
DEEPSEEK_API_KEY=your-deepseek-api-key
DEEPSEEK_API_BASE=https://api.deepseek.com/v1
```

- [ ] **Step 3: Commit**

```bash
git add docker-compose.yml .env.example
git commit -m "chore: add docker-compose and env template"
```

---

## Task 3: Anaconda 虚拟环境 + 后端依赖

**Files:**
- Create: `D:\AI_code_assistant\backend\requirements.txt`

> ⚠️ **约束提醒**: 以下安装步骤涉及软件和依赖安装，请向项目经理汇报后执行。

- [ ] **Step 1: 向项目经理汇报安装需求**

汇报内容：
- 软件: Anaconda (如未安装)
- 依赖: Python 3.11 + 以下 Python 包
- 安装位置: D 盘 (Anaconda 安装到 D:\Anaconda，虚拟环境在 D:\Anaconda\envs\)
- 是否需要管理员权限: 是 (Anaconda 安装需要)

- [ ] **Step 2: 创建 Anaconda 虚拟环境**

```powershell
# 创建虚拟环境
conda create -n ai_code_assistant_env python=3.11 -y

# 激活环境
conda activate ai_code_assistant_env

# 验证 Python 版本
python --version
```

Expected: Python 3.11.x

- [ ] **Step 3: 编写 requirements.txt**

```txt
# D:\AI_code_assistant\backend\requirements.txt
# FastAPI
fastapi==0.109.0
uvicorn[standard]==0.27.0
python-multipart==0.0.6

# Database
sqlalchemy[asyncio]==2.0.25
asyncpg==0.29.0
alembic==1.13.1

# Authentication
passlib[bcrypt]==1.7.4
python-jose[cryptography]==3.3.0

# HTTP Client
httpx==0.26.0

# Validation
email-validator==2.1.0.post1

# Environment
python-dotenv==1.0.0

# Testing
pytest==7.4.4
pytest-asyncio==0.23.3
httpx==0.26.0
```

- [ ] **Step 4: 安装依赖**

```powershell
# 确保在虚拟环境中
conda activate ai_code_assistant_env

# 安装依赖
cd D:\AI_code_assistant\backend
pip install -r requirements.txt

# 验证安装
python -c "import fastapi; print(fastapi.__version__)"
python -c "import sqlalchemy; print(sqlalchemy.__version__)"
python -c "import passlib; print(passlib.__version__)"
```

Expected: 各包版本号正确输出，无报错

- [ ] **Step 5: Commit**

```bash
git add backend/requirements.txt
git commit -m "chore: add backend dependencies"
```

---

## Task 4: 后端配置管理

**Files:**
- Create: `D:\AI_code_assistant\backend\app\config.py`

- [ ] **Step 1: 编写配置模块**

```python
# D:\AI_code_assistant\backend\app\config.py
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # 数据库
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/ai_code_assistant"
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # JWT
    SECRET_KEY: str = "dev-secret-key"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # GitHub OAuth
    GITHUB_CLIENT_ID: str = ""
    GITHUB_CLIENT_SECRET: str = ""
    
    # AI
    DEEPSEEK_API_KEY: str = ""
    DEEPSEEK_API_BASE: str = "https://api.deepseek.com/v1"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
```

- [ ] **Step 2: Commit**

```bash
git add backend/app/config.py
git commit -m "feat: add configuration management"
```

---

## Task 5: 数据库连接 + SQLAlchemy 模型

**Files:**
- Create: `D:\AI_code_assistant\backend\app\database.py`
- Create: `D:\AI_code_assistant\backend\app\models\user.py`

- [ ] **Step 1: 编写数据库连接模块**

```python
# D:\AI_code_assistant\backend\app\database.py
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from app.config import settings

# 创建异步引擎
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=True,  # 开发环境打印 SQL
    future=True
)

# 创建会话工厂
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)

# 声明基类
Base = declarative_base()


async def get_db():
    """依赖注入用的数据库会话"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
```

- [ ] **Step 2: 编写 User 模型**

```python
# D:\AI_code_assistant\backend\app\models\user.py
import uuid
from datetime import datetime
from sqlalchemy import Column, String, Boolean, DateTime, Integer
from sqlalchemy.dialects.postgresql import UUID
from app.database import Base


class User(Base):
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    github_id = Column(String(100), unique=True, nullable=True)
    github_username = Column(String(100), nullable=True)
    avatar_url = Column(String(500), nullable=True)
    role = Column(String(20), default="user", nullable=False)
    elo_rating = Column(Integer, default=1200, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    last_login_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
```

- [ ] **Step 3: 更新 models/__init__.py**

```python
# D:\AI_code_assistant\backend\app\models\__init__.py
from app.models.user import User

__all__ = ["User"]
```

- [ ] **Step 4: Commit**

```bash
git add backend/app/database.py backend/app/models/
git commit -m "feat: add database connection and user model"
```

---

## Task 6: Pydantic Schemas

**Files:**
- Create: `D:\AI_code_assistant\backend\app\schemas\user.py`

- [ ] **Step 1: 编写 User Schemas**

```python
# D:\AI_code_assistant\backend\app\schemas\user.py
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field
from uuid import UUID


# ========== 基础模型 ==========
class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr


class UserProfile(BaseModel):
    display_name: Optional[str] = None
    bio: Optional[str] = None
    school: Optional[str] = None
    preferred_language: str = "cpp"


# ========== 请求模型 ==========
class UserRegister(UserBase):
    password: str = Field(..., min_length=8, max_length=128)


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserUpdate(BaseModel):
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    display_name: Optional[str] = None
    bio: Optional[str] = None
    school: Optional[str] = None
    preferred_language: Optional[str] = None


# ========== 响应模型 ==========
class UserResponse(UserBase):
    id: UUID
    avatar_url: Optional[str] = None
    role: str
    elo_rating: int
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


class UserProfileResponse(UserResponse):
    profile: Optional[UserProfile] = None


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


class TokenPayload(BaseModel):
    sub: Optional[str] = None
    exp: Optional[datetime] = None
```

- [ ] **Step 2: Commit**

```bash
git add backend/app/schemas/
git commit -m "feat: add user pydantic schemas"
```

---

## Task 7: 安全工具（JWT + Bcrypt）

**Files:**
- Create: `D:\AI_code_assistant\backend\app\utils\security.py`

- [ ] **Step 1: 编写安全工具模块**

```python
# D:\AI_code_assistant\backend\app\utils\security.py
from datetime import datetime, timedelta
from typing import Optional, Union
from jose import JWTError, jwt
from passlib.context import CryptContext
from app.config import settings

# 密码哈希上下文
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """验证密码"""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """生成密码哈希"""
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """创建 JWT Access Token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire, "type": "access"})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def create_refresh_token(data: dict) -> str:
    """创建 JWT Refresh Token"""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "type": "refresh"})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def decode_token(token: str) -> Optional[dict]:
    """解码 JWT Token"""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except JWTError:
        return None
```

- [ ] **Step 2: 测试安全工具**

```python
# D:\AI_code_assistant\backend\tests\test_security.py
import pytest
from app.utils.security import (
    get_password_hash, verify_password,
    create_access_token, decode_token
)


def test_password_hash():
    password = "testpassword123"
    hashed = get_password_hash(password)
    assert verify_password(password, hashed) is True
    assert verify_password("wrongpassword", hashed) is False


def test_access_token():
    data = {"sub": "user@example.com"}
    token = create_access_token(data)
    payload = decode_token(token)
    assert payload is not None
    assert payload["sub"] == "user@example.com"
    assert payload["type"] == "access"
```

Run:
```bash
cd D:\AI_code_assistant\backend
pytest tests/test_security.py -v
```

Expected: 2 tests passed

- [ ] **Step 3: Commit**

```bash
git add backend/app/utils/security.py backend/tests/test_security.py
git commit -m "feat: add JWT and bcrypt security utils with tests"
```

---

## Task 8: Alembic 配置 + 初始迁移

**Files:**
- Create: `D:\AI_code_assistant\backend\alembic.ini`
- Create: `D:\AI_code_assistant\backend\alembic\env.py`
- Create: `D:\AI_code_assistant\backend\alembic\script.py.mako`

- [ ] **Step 1: 初始化 Alembic**

```powershell
cd D:\AI_code_assistant\backend
conda activate ai_code_assistant_env

# 初始化 Alembic
alembic init alembic
```

Expected: alembic 目录和 alembic.ini 创建成功

- [ ] **Step 2: 配置 alembic.ini**

```ini
# D:\AI_code_assistant\backend\alembic.ini
[alembic]
script_location = alembic
prepend_sys_path = .
version_path_separator = os
sqlalchemy.url = postgresql+asyncpg://postgres:postgres@localhost:5432/ai_code_assistant

[post_write_hooks]

[loggers]
keys = root,sqlalchemy,alembic

[handlers]
keys = console

[formatters]
keys = generic

[logger_root]
level = WARN
handlers = console
qualname =

[logger_sqlalchemy]
level = WARN
handlers =
qualname = sqlalchemy.engine

[logger_alembic]
level = INFO
handlers =
qualname = alembic

[handler_console]
class = StreamHandler
args = (sys.stderr,)
level = NOTSET
formatter = generic

[formatter_generic]
format = %(levelname)-5.5s [%(name)s] %(message)s
datefmt = %H:%M:%S
```

- [ ] **Step 3: 配置 alembic/env.py**

```python
# D:\AI_code_assistant\backend\alembic\env.py
import asyncio
from logging.config import fileConfig
from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config
from alembic import context
from app.config import settings
from app.database import Base
from app.models import *  # 导入所有模型

# Alembic Config
config = context.config
config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)

# 配置日志
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# 目标元数据
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    context.configure(connection=connection, target_metadata=target_metadata)
    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)
    await connectable.dispose()


def run_migrations_online() -> None:
    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
```

- [ ] **Step 4: 启动数据库容器并创建初始迁移**

```powershell
cd D:\AI_code_assistant

# 启动数据库
docker-compose up -d db redis

# 等待数据库就绪（约 10 秒）
Start-Sleep -Seconds 10

# 创建初始迁移
cd backend
alembic revision --autogenerate -m "init: create users table"

# 执行迁移
alembic upgrade head
```

Expected: Migration 文件生成成功，users 表创建成功

- [ ] **Step 5: Commit**

```bash
git add backend/alembic.ini backend/alembic/
git commit -m "chore: setup alembic and create initial migration"
```

---

## Task 9: 认证服务层

**Files:**
- Create: `D:\AI_code_assistant\backend\app\services\auth_service.py`

- [ ] **Step 1: 编写认证服务**

```python
# D:\AI_code_assistant\backend\app\services\auth_service.py
from datetime import datetime
from typing import Optional
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import User
from app.schemas.user import UserRegister, UserLogin, TokenResponse
from app.utils.security import (
    get_password_hash, verify_password,
    create_access_token, create_refresh_token
)


class AuthService:
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def register(self, user_data: UserRegister) -> User:
        """用户注册"""
        # 检查邮箱是否已存在
        result = await self.db.execute(
            select(User).where(User.email == user_data.email)
        )
        if result.scalar_one_or_none():
            raise ValueError("Email already registered")
        
        # 检查用户名是否已存在
        result = await self.db.execute(
            select(User).where(User.username == user_data.username)
        )
        if result.scalar_one_or_none():
            raise ValueError("Username already taken")
        
        # 创建用户
        user = User(
            username=user_data.username,
            email=user_data.email,
            password_hash=get_password_hash(user_data.password)
        )
        self.db.add(user)
        await self.db.flush()
        await self.db.refresh(user)
        return user
    
    async def login(self, login_data: UserLogin) -> TokenResponse:
        """用户登录"""
        result = await self.db.execute(
            select(User).where(User.email == login_data.email)
        )
        user = result.scalar_one_or_none()
        
        if not user or not verify_password(login_data.password, user.password_hash):
            raise ValueError("Invalid email or password")
        
        if not user.is_active:
            raise ValueError("User account is deactivated")
        
        # 更新最后登录时间
        user.last_login_at = datetime.utcnow()
        
        # 生成 Token
        token_data = {"sub": str(user.id), "email": user.email}
        access_token = create_access_token(token_data)
        refresh_token = create_refresh_token(token_data)
        
        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=60 * 60  # 60 minutes in seconds
        )
    
    async def get_user_by_id(self, user_id: UUID) -> Optional[User]:
        """通过 ID 获取用户"""
        result = await self.db.execute(
            select(User).where(User.id == user_id)
        )
        return result.scalar_one_or_none()
```

- [ ] **Step 2: Commit**

```bash
git add backend/app/services/auth_service.py
git commit -m "feat: add authentication service layer"
```

---

## Task 10: 认证路由（注册/登录/获取用户信息）

**Files:**
- Create: `D:\AI_code_assistant\backend\app\routers\auth.py`
- Modify: `D:\AI_code_assistant\backend\app\main.py`

- [ ] **Step 1: 编写认证路由**

```python
# D:\AI_code_assistant\backend\app\routers\auth.py
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.schemas.user import (
    UserRegister, UserLogin, UserResponse, TokenResponse
)
from app.services.auth_service import AuthService
from app.utils.security import decode_token

router = APIRouter(prefix="/auth", tags=["认证"])
security = HTTPBearer(auto_error=False)


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserRegister,
    db: AsyncSession = Depends(get_db)
):
    """用户注册"""
    auth_service = AuthService(db)
    try:
        user = await auth_service.register(user_data)
        return user
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/login", response_model=TokenResponse)
async def login(
    login_data: UserLogin,
    db: AsyncSession = Depends(get_db)
):
    """用户登录"""
    auth_service = AuthService(db)
    try:
        return await auth_service.login(login_data)
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))


@router.get("/me", response_model=UserResponse)
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
):
    """获取当前用户信息"""
    if not credentials:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    payload = decode_token(credentials.credentials)
    if not payload or payload.get("type") != "access":
        raise HTTPException(status_code=401, detail="Invalid token")
    
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token payload")
    
    auth_service = AuthService(db)
    user = await auth_service.get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return user
```

- [ ] **Step 2: 编写 FastAPI 主入口**

```python
# D:\AI_code_assistant\backend\app\main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import auth

app = FastAPI(
    title="AI_code_assisstant API",
    description="AI 编程学习平台后端 API",
    version="0.1.0"
)

# CORS 配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # 前端开发服务器
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(auth.router, prefix="/api/v1")


@app.get("/health")
async def health_check():
    """健康检查"""
    return {"status": "healthy"}


@app.get("/")
async def root():
    return {"message": "Welcome to AI_code_assisstant API", "version": "0.1.0"}
```

- [ ] **Step 3: 启动后端服务并测试**

```powershell
cd D:\AI_code_assistant\backend
conda activate ai_code_assistant_env

# 启动服务
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

在另一个终端测试：
```bash
# 测试健康检查
curl http://localhost:8000/health

# 测试注册
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username": "testuser", "email": "test@example.com", "password": "testpass123"}'

# 测试登录
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "testpass123"}'
```

Expected: 所有请求返回 200/201 状态码和正确 JSON

- [ ] **Step 4: Commit**

```bash
git add backend/app/routers/auth.py backend/app/main.py
git commit -m "feat: add authentication routes and FastAPI app entry"
```

---

## Task 11: 前端项目脚手架（Vite + React + TypeScript）

**Files:**
- Create: `D:\AI_code_assistant\frontend\package.json`
- Create: `D:\AI_code_assistant\frontend\vite.config.ts`
- Create: `D:\AI_code_assistant\frontend\tsconfig.json`
- Create: `D:\AI_code_assistant\frontend\tailwind.config.js`
- Create: `D:\AI_code_assistant\frontend\index.html`
- Create: `D:\AI_code_assistant\frontend\src\main.tsx`
- Create: `D:\AI_code_assistant\frontend\src\App.tsx`
- Create: `D:\AI_code_assistant\frontend\src\index.css`

> ⚠️ **约束提醒**: 以下安装步骤涉及 Node.js 和 npm 依赖安装，请向项目经理汇报后执行。

- [ ] **Step 1: 向项目经理汇报 Node.js 安装需求**

汇报内容：
- 软件: Node.js 18+ LTS
- 安装位置: D 盘 (如 D:\nodejs 或 D:\Program Files\nodejs)
- 依赖管理器: npm (随 Node.js 安装)
- 是否需要管理员权限: 是

- [ ] **Step 2: 使用 Vite 创建项目**

```powershell
cd D:\AI_code_assistant\frontend

# 使用 Vite 创建 React + TypeScript 项目
# 注意：这会创建一个新的目录结构，我们需要调整
npm create vite@latest . -- --template react-ts

# 安装依赖
npm install
```

Expected: 项目创建成功，node_modules 安装完成

- [ ] **Step 3: 安装额外依赖**

```powershell
cd D:\AI_code_assistant\frontend

# 安装 Tailwind CSS
npm install -D tailwindcss postcss autoprefixer
npx tailwindcss init -p

# 安装 Zustand
npm install zustand

# 安装 React Router
npm install react-router-dom

# 安装 Axios
npm install axios

# 安装图标库
npm install lucide-react
```

- [ ] **Step 4: 配置 Tailwind CSS**

```javascript
// D:\AI_code_assistant\frontend\tailwind.config.js
/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          50: '#eff6ff',
          100: '#dbeafe',
          500: '#3b82f6',
          600: '#2563eb',
          700: '#1d4ed8',
        }
      }
    },
  },
  plugins: [],
}
```

```css
/* D:\AI_code_assistant\frontend\src\index.css */
@tailwind base;
@tailwind components;
@tailwind utilities;

@layer base {
  body {
    @apply bg-gray-50 text-gray-900;
  }
}
```

- [ ] **Step 5: 配置 Vite**

```typescript
// D:\AI_code_assistant\frontend\vite.config.ts
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    port: 3000,
    host: '0.0.0.0',
  },
})
```

- [ ] **Step 6: 编写基础组件**

```typescript
// D:\AI_code_assistant\frontend\src\main.tsx
import React from 'react'
import ReactDOM from 'react-dom/client'
import { BrowserRouter } from 'react-router-dom'
import App from './App'
import './index.css'

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <BrowserRouter>
      <App />
    </BrowserRouter>
  </React.StrictMode>,
)
```

```typescript
// D:\AI_code_assistant\frontend\src\App.tsx
import { Routes, Route } from 'react-router-dom'
import HomePage from './pages/HomePage'
import LoginPage from './pages/LoginPage'

function App() {
  return (
    <div className="min-h-screen">
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/login" element={<LoginPage />} />
      </Routes>
    </div>
  )
}

export default App
```

```typescript
// D:\AI_code_assistant\frontend\src\pages\HomePage.tsx
export default function HomePage() {
  return (
    <div className="p-8">
      <h1 className="text-3xl font-bold text-primary-600">
        AI_code_assisstant
      </h1>
      <p className="mt-4 text-gray-600">
        面向竞赛选手与自学者的 AI 编程学习平台
      </p>
    </div>
  )
}
```

```typescript
// D:\AI_code_assistant\frontend\src\pages\LoginPage.tsx
export default function LoginPage() {
  return (
    <div className="flex min-h-screen items-center justify-center">
      <div className="w-full max-w-md p-8 bg-white rounded-lg shadow">
        <h2 className="text-2xl font-bold text-center">登录</h2>
        <p className="mt-4 text-center text-gray-500">功能开发中...</p>
      </div>
    </div>
  )
}
```

- [ ] **Step 7: 启动前端开发服务器**

```powershell
cd D:\AI_code_assistant\frontend
npm run dev
```

打开浏览器访问 http://localhost:3000

Expected: 页面显示 "AI_code_assisstant" 标题和介绍文字

- [ ] **Step 8: Commit**

```bash
git add frontend/
git commit -m "chore: setup frontend scaffold with Vite + React + TS + Tailwind"
```

---

## Task 12: 前端认证状态管理（Zustand）

**Files:**
- Create: `D:\AI_code_assistant\frontend\src\stores\authStore.ts`
- Create: `D:\AI_code_assistant\frontend\src\services\api.ts`

- [ ] **Step 1: 编写 API 服务**

```typescript
// D:\AI_code_assistant\frontend\src\services\api.ts
import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1'

export const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// 请求拦截器 - 添加 Token
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// 响应拦截器 - 处理错误
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('access_token')
      localStorage.removeItem('refresh_token')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

// 认证相关 API
export const authApi = {
  register: (data: { username: string; email: string; password: string }) =>
    api.post('/auth/register', data),
  
  login: (data: { email: string; password: string }) =>
    api.post('/auth/login', data),
  
  getMe: () =>
    api.get('/auth/me'),
}
```

- [ ] **Step 2: 编写 Auth Store**

```typescript
// D:\AI_code_assistant\frontend\src\stores\authStore.ts
import { create } from 'zustand'
import { authApi } from '../services/api'

interface User {
  id: string
  username: string
  email: string
  avatar_url: string | null
  role: string
  elo_rating: number
}

interface AuthState {
  user: User | null
  isAuthenticated: boolean
  isLoading: boolean
  
  // Actions
  login: (email: string, password: string) => Promise<void>
  register: (username: string, email: string, password: string) => Promise<void>
  logout: () => void
  fetchUser: () => Promise<void>
}

export const useAuthStore = create<AuthState>((set) => ({
  user: null,
  isAuthenticated: false,
  isLoading: false,

  login: async (email: string, password: string) => {
    set({ isLoading: true })
    try {
      const response = await authApi.login({ email, password })
      const { access_token, refresh_token } = response.data.data
      
      localStorage.setItem('access_token', access_token)
      localStorage.setItem('refresh_token', refresh_token)
      
      // 获取用户信息
      const userResponse = await authApi.getMe()
      set({ 
        user: userResponse.data.data,
        isAuthenticated: true,
        isLoading: false 
      })
    } catch (error) {
      set({ isLoading: false })
      throw error
    }
  },

  register: async (username: string, email: string, password: string) => {
    set({ isLoading: true })
    try {
      await authApi.register({ username, email, password })
      // 注册成功后自动登录
      await useAuthStore.getState().login(email, password)
    } catch (error) {
      set({ isLoading: false })
      throw error
    }
  },

  logout: () => {
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
    set({ user: null, isAuthenticated: false })
  },

  fetchUser: async () => {
    const token = localStorage.getItem('access_token')
    if (!token) {
      set({ isAuthenticated: false })
      return
    }
    
    try {
      const response = await authApi.getMe()
      set({ 
        user: response.data.data,
        isAuthenticated: true 
      })
    } catch (error) {
      localStorage.removeItem('access_token')
      localStorage.removeItem('refresh_token')
      set({ user: null, isAuthenticated: false })
    }
  },
}))
```

- [ ] **Step 3: 编写登录表单组件**

```typescript
// D:\AI_code_assistant\frontend\src\components\LoginForm.tsx
import { useState } from 'react'
import { useAuthStore } from '../stores/authStore'
import { useNavigate } from 'react-router-dom'

export default function LoginForm() {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const { login, isLoading } = useAuthStore()
  const navigate = useNavigate()

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    
    try {
      await login(email, password)
      navigate('/')
    } catch (err: any) {
      setError(err.response?.data?.detail || '登录失败')
    }
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      {error && (
        <div className="p-3 text-sm text-red-600 bg-red-50 rounded">
          {error}
        </div>
      )}
      
      <div>
        <label className="block text-sm font-medium text-gray-700">
          邮箱
        </label>
        <input
          type="email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md"
          required
        />
      </div>
      
      <div>
        <label className="block text-sm font-medium text-gray-700">
          密码
        </label>
        <input
          type="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md"
          required
        />
      </div>
      
      <button
        type="submit"
        disabled={isLoading}
        className="w-full py-2 px-4 bg-primary-600 text-white rounded-md hover:bg-primary-700 disabled:opacity-50"
      >
        {isLoading ? '登录中...' : '登录'}
      </button>
    </form>
  )
}
```

- [ ] **Step 4: 更新 LoginPage**

```typescript
// D:\AI_code_assistant\frontend\src\pages\LoginPage.tsx
import LoginForm from '../components/LoginForm'

export default function LoginPage() {
  return (
    <div className="flex min-h-screen items-center justify-center bg-gray-50">
      <div className="w-full max-w-md p-8 bg-white rounded-lg shadow">
        <h2 className="text-2xl font-bold text-center text-gray-900">
          AI_code_assisstant
        </h2>
        <p className="mt-2 text-center text-gray-500">登录你的账户</p>
        <div className="mt-6">
          <LoginForm />
        </div>
      </div>
    </div>
  )
}
```

- [ ] **Step 5: Commit**

```bash
git add frontend/src/stores/ frontend/src/services/ frontend/src/components/ frontend/src/pages/
git commit -m "feat: add frontend auth store, api service, and login form"
```

---

## Task 13: 前端 Dockerfile

**Files:**
- Create: `D:\AI_code_assistant\frontend\Dockerfile`

- [ ] **Step 1: 编写前端 Dockerfile**

```dockerfile
# D:\AI_code_assistant\frontend\Dockerfile
FROM node:18-alpine

WORKDIR /app

# 复制 package 文件
COPY package*.json ./

# 安装依赖
RUN npm install

# 复制源代码
COPY . .

# 暴露端口
EXPOSE 3000

# 开发模式启动
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0", "--port", "3000"]
```

- [ ] **Step 2: Commit**

```bash
git add frontend/Dockerfile
git commit -m "chore: add frontend Dockerfile"
```

---

## Task 14: 后端 Dockerfile

**Files:**
- Create: `D:\AI_code_assistant\backend\Dockerfile`

- [ ] **Step 1: 编写后端 Dockerfile**

```dockerfile
# D:\AI_code_assistant\backend\Dockerfile
FROM python:3.11-slim

WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# 复制 requirements
COPY requirements.txt .

# 安装 Python 依赖
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用代码
COPY . .

# 暴露端口
EXPOSE 8000

# 默认命令（开发模式）
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
```

- [ ] **Step 2: Commit**

```bash
git add backend/Dockerfile
git commit -m "chore: add backend Dockerfile"
```

---

## Task 15: 端到端集成测试

- [ ] **Step 1: 使用 Docker Compose 启动完整环境**

```powershell
cd D:\AI_code_assistant

# 构建并启动所有服务
docker-compose up --build -d

# 等待服务就绪
Start-Sleep -Seconds 15

# 检查服务状态
docker-compose ps
```

Expected: 所有服务状态为 Up

- [ ] **Step 2: 测试后端 API**

```bash
# 测试根路径
curl http://localhost:8000/

# 测试注册
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username": "demo", "email": "demo@example.com", "password": "demopass123"}'

# 测试登录
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "demo@example.com", "password": "demopass123"}'

# 测试获取用户信息（使用登录返回的 token）
curl http://localhost:8000/api/v1/auth/me \
  -H "Authorization: Bearer <access_token>"
```

- [ ] **Step 3: 测试前端页面**

打开浏览器访问：
- http://localhost:3000/ — 首页
- http://localhost:3000/login — 登录页

Expected: 页面正常显示，无报错

- [ ] **Step 4: 验证数据库**

```bash
# 进入数据库容器
docker-compose exec db psql -U postgres -d ai_code_assistant -c "\dt"

# 查询用户表
docker-compose exec db psql -U postgres -d ai_code_assistant -c "SELECT id, username, email FROM users;"
```

Expected: users 表存在，demo 用户已创建

- [ ] **Step 5: Commit**

```bash
git add .
git commit -m "test: verify end-to-end integration"
```

---

## 验收标准 (Week 1-2 完成标志)

- [ ] Docker Compose 可以一键启动所有服务（db + redis + backend + frontend）
- [ ] 后端 API 文档可访问：http://localhost:8000/docs (Swagger UI)
- [ ] 用户可以注册新账户
- [ ] 用户可以使用邮箱+密码登录
- [ ] 登录后可获取当前用户信息
- [ ] JWT Token 正确生成和验证
- [ ] 前端页面正常显示（首页 + 登录页）
- [ ] 前端登录表单可以调用后端 API
- [ ] 数据库 users 表结构正确
- [ ] Alembic 迁移可以正常执行
- [ ] 所有代码已提交到 Git

---

## 已知风险与应对

| 风险 | 影响 | 应对策略 |
|------|------|----------|
| Docker 在 Windows 上文件监控性能差 | 热重载延迟 | 使用 WSL2 后端，或增大轮询间隔 |
| Anaconda 环境配置问题 | 依赖安装失败 | 使用 conda + pip 混合安装，记录精确版本 |
| PostgreSQL 容器数据持久化 | 容器重启数据丢失 | 使用 Docker Volume，不删除 volume |
| 端口冲突 | 服务无法启动 | 检查 3000, 8000, 5432, 6379 端口占用 |

---

> **Plan complete and saved to `D:\AI_code_assistant\docs\superpowers\plans\2026-05-14-week1-2-scaffold-auth.md`**

---

## 执行选项

**Plan complete. Two execution options:**

**1. Subagent-Driven (recommended)** - I dispatch a fresh subagent per task, review between tasks, fast iteration

**2. Inline Execution** - Execute tasks in this session using executing-plans, batch execution with checkpoints for review

**Which approach do you prefer?**

Or, if you want to review/modify the plan first, please let me know what changes you'd like to make.
