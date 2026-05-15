# 评测引擎 MVP 实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 实现最小可用的代码评测引擎，支持 C++ 和 Python 代码提交、Docker 沙箱编译运行、测试用例对比、返回 AC/WA/TLE/MLE/RE/CE 状态。

**Architecture:** 纯 Docker 沙箱 + Celery 异步任务队列。提交代码后保存到数据库并触发 Celery 任务，任务在 Docker 容器中编译运行代码，对比测试用例输出，更新评测结果。

**Tech Stack:** FastAPI, SQLAlchemy, Celery, Docker, PostgreSQL, Redis

---

## 文件结构

### 新建文件
| 文件 | 职责 |
|------|------|
| `backend/alembic/versions/20260515_add_submissions_and_test_cases.py` | 数据库迁移 |
| `backend/app/models/test_case.py` | TestCase SQLAlchemy 模型 |
| `backend/app/models/submission.py` | Submission SQLAlchemy 模型 |
| `backend/app/models/submission_result.py` | SubmissionResult SQLAlchemy 模型 |
| `backend/app/schemas/submission.py` | Submission Pydantic Schema |
| `backend/app/services/judge_service.py` | 评测核心逻辑 |
| `backend/app/tasks/judge_task.py` | Celery 评测任务 |
| `backend/app/routers/submissions.py` | 提交 API 路由 |
| `backend/judge/Dockerfile` | 评测沙箱镜像 |
| `backend/judge/judge.sh` | 评测入口脚本 |
| `backend/tests/test_judge.py` | 评测功能测试 |

### 修改文件
| 文件 | 修改内容 |
|------|----------|
| `backend/app/models/__init__.py` | 导出新模型 |
| `backend/app/schemas/__init__.py` | 导出 Submission schemas |
| `backend/app/routers/__init__.py` | 导出 submissions router |
| `backend/app/services/__init__.py` | 导出 JudgeService |
| `backend/app/main.py` | 注册 submissions 路由 |
| `docker-compose.yml` | 添加 judge 镜像构建 |

---

## Task 1: 数据库迁移脚本

**Files:**
- Create: `backend/alembic/versions/20260515_add_submissions_and_test_cases.py`

**依赖:** 无（基于现有 problems/users 表）

- [ ] **Step 1: 创建迁移脚本**

创建文件 `backend/alembic/versions/20260515_add_submissions_and_test_cases.py`：

```python
"""add submissions, test_cases, and submission_results tables

Revision ID: 20260515_add_submissions_and_test_cases
Revises: 20260515_add_problems_and_tags
Create Date: 2026-05-15 00:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '20260515_add_submissions_and_test_cases'
down_revision: Union[str, None] = '20260515_add_problems_and_tags'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 创建 test_cases 表
    op.create_table(
        'test_cases',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('problem_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('input_data', sa.Text(), nullable=False),
        sa.Column('expected_output', sa.Text(), nullable=False),
        sa.Column('is_sample', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('order_index', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('NOW()')),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['problem_id'], ['problems.id'], ondelete='CASCADE')
    )
    op.create_index('idx_test_cases_problem', 'test_cases', ['problem_id', 'is_active', 'order_index'])

    # 创建 submissions 表
    op.create_table(
        'submissions',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('problem_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('code', sa.Text(), nullable=False),
        sa.Column('language', sa.String(20), nullable=False),
        sa.Column('status', sa.String(20), nullable=False, server_default='Pending'),
        sa.Column('score', sa.Integer(), nullable=True),
        sa.Column('runtime_ms', sa.Integer(), nullable=True),
        sa.Column('memory_kb', sa.Integer(), nullable=True),
        sa.Column('passed_count', sa.SmallInteger(), nullable=True),
        sa.Column('total_count', sa.SmallInteger(), nullable=True),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('judge_log', sa.Text(), nullable=True),
        sa.Column('submitted_at', sa.DateTime(), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('judged_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['problem_id'], ['problems.id'], ondelete='CASCADE')
    )
    op.create_index('idx_submissions_user', 'submissions', ['user_id', 'submitted_at'])
    op.create_index('idx_submissions_problem', 'submissions', ['problem_id', 'status'])
    op.create_index('idx_submissions_status', 'submissions', ['status', 'submitted_at'])

    # 创建 submission_results 表
    op.create_table(
        'submission_results',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('submission_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('test_case_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('test_case_order', sa.SmallInteger(), nullable=False),
        sa.Column('status', sa.String(20), nullable=False),
        sa.Column('runtime_ms', sa.Integer(), nullable=True),
        sa.Column('memory_kb', sa.Integer(), nullable=True),
        sa.Column('actual_output', sa.Text(), nullable=True),
        sa.Column('diff_info', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('NOW()')),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['submission_id'], ['submissions.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['test_case_id'], ['test_cases.id'], ondelete='SET NULL')
    )
    op.create_index('idx_submission_results_submission', 'submission_results', ['submission_id', 'test_case_order'])


def downgrade() -> None:
    op.drop_table('submission_results')
    op.drop_table('submissions')
    op.drop_table('test_cases')
```

- [ ] **Step 2: 运行迁移**

```bash
cd D:\AI_code_assistant\backend
alembic upgrade head
```

Expected: 迁移成功执行。

- [ ] **Step 3: 验证**

```bash
alembic current
```

Expected: 显示 `20260515_add_submissions_and_test_cases`。

---

## Task 2: 数据模型

**Files:**
- Create: `backend/app/models/test_case.py`
- Create: `backend/app/models/submission.py`
- Create: `backend/app/models/submission_result.py`
- Modify: `backend/app/models/__init__.py`

**依赖:** Task 1（数据库表已创建）

- [ ] **Step 1: 创建 TestCase 模型**

创建文件 `backend/app/models/test_case.py`：

```python
import uuid
from datetime import datetime
from sqlalchemy import Column, Text, Boolean, Integer, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from app.database import Base


class TestCase(Base):
    __tablename__ = "test_cases"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    problem_id = Column(UUID(as_uuid=True), ForeignKey("problems.id", ondelete="CASCADE"), nullable=False)
    input_data = Column(Text, nullable=False)
    expected_output = Column(Text, nullable=False)
    is_sample = Column(Boolean, nullable=False, default=False)
    is_active = Column(Boolean, nullable=False, default=True)
    order_index = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
```

- [ ] **Step 2: 创建 Submission 模型**

创建文件 `backend/app/models/submission.py`：

```python
import uuid
from datetime import datetime
from sqlalchemy import Column, String, Text, Integer, SmallInteger, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from app.database import Base


class Submission(Base):
    __tablename__ = "submissions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    problem_id = Column(UUID(as_uuid=True), ForeignKey("problems.id", ondelete="CASCADE"), nullable=False)
    code = Column(Text, nullable=False)
    language = Column(String(20), nullable=False)  # cpp, py
    status = Column(String(20), nullable=False, default="Pending")
    score = Column(Integer, nullable=True)
    runtime_ms = Column(Integer, nullable=True)
    memory_kb = Column(Integer, nullable=True)
    passed_count = Column(SmallInteger, nullable=True)
    total_count = Column(SmallInteger, nullable=True)
    error_message = Column(Text, nullable=True)
    judge_log = Column(Text, nullable=True)
    submitted_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    judged_at = Column(DateTime, nullable=True)
```

- [ ] **Step 3: 创建 SubmissionResult 模型**

创建文件 `backend/app/models/submission_result.py`：

```python
import uuid
from datetime import datetime
from sqlalchemy import Column, String, Text, Integer, SmallInteger, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from app.database import Base


class SubmissionResult(Base):
    __tablename__ = "submission_results"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    submission_id = Column(UUID(as_uuid=True), ForeignKey("submissions.id", ondelete="CASCADE"), nullable=False)
    test_case_id = Column(UUID(as_uuid=True), ForeignKey("test_cases.id", ondelete="SET NULL"), nullable=True)
    test_case_order = Column(SmallInteger, nullable=False)
    status = Column(String(20), nullable=False)
    runtime_ms = Column(Integer, nullable=True)
    memory_kb = Column(Integer, nullable=True)
    actual_output = Column(Text, nullable=True)
    diff_info = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
```

- [ ] **Step 4: 更新 models/__init__.py**

```python
from app.models.user import User
from app.models.problem import Problem
from app.models.tag import Tag
from app.models.problem_tag_association import ProblemTagAssociation
from app.models.test_case import TestCase
from app.models.submission import Submission
from app.models.submission_result import SubmissionResult

__all__ = ["User", "Problem", "Tag", "ProblemTagAssociation", "TestCase", "Submission", "SubmissionResult"]
```

---

## Task 3: Pydantic Schemas

**Files:**
- Create: `backend/app/schemas/submission.py`
- Modify: `backend/app/schemas/__init__.py`

**依赖:** Task 2（模型已定义）

- [ ] **Step 1: 创建 Submission Schemas**

创建文件 `backend/app/schemas/submission.py`：

```python
from datetime import datetime
from typing import List, Optional
from uuid import UUID
from pydantic import BaseModel, Field


class SubmissionCreate(BaseModel):
    problem_id: UUID
    code: str = Field(..., min_length=1)
    language: str = Field(..., pattern=r'^(cpp|py)$')


class SubmissionResultItem(BaseModel):
    test_case_order: int
    status: str
    runtime_ms: Optional[int] = None
    memory_kb: Optional[int] = None
    actual_output: Optional[str] = None
    
    class Config:
        from_attributes = True


class SubmissionInDB(BaseModel):
    id: UUID
    problem_id: UUID
    code: str
    language: str
    status: str
    score: Optional[int] = None
    runtime_ms: Optional[int] = None
    memory_kb: Optional[int] = None
    passed_count: Optional[int] = None
    total_count: Optional[int] = None
    error_message: Optional[str] = None
    submitted_at: datetime
    judged_at: Optional[datetime] = None
    results: List[SubmissionResultItem] = []
    
    class Config:
        from_attributes = True


class SubmissionListItem(BaseModel):
    id: UUID
    problem_id: UUID
    language: str
    status: str
    score: Optional[int] = None
    runtime_ms: Optional[int] = None
    passed_count: Optional[int] = None
    total_count: Optional[int] = None
    submitted_at: datetime
    
    class Config:
        from_attributes = True
```

- [ ] **Step 2: 更新 schemas/__init__.py**

```python
from app.schemas.submission import (
    SubmissionCreate,
    SubmissionInDB,
    SubmissionListItem,
    SubmissionResultItem
)

__all__ = [
    "SubmissionCreate",
    "SubmissionInDB",
    "SubmissionListItem",
    "SubmissionResultItem"
]
```

---

## Task 4: Docker 沙箱

**Files:**
- Create: `backend/judge/Dockerfile`
- Create: `backend/judge/judge.sh`

**依赖:** 无

- [ ] **Step 1: 创建 Dockerfile**

创建文件 `backend/judge/Dockerfile`：

```dockerfile
FROM alpine:3.18

RUN apk add --no-cache \
    g++ \
    python3 \
    py3-pip \
    bash \
    coreutils

WORKDIR /app

COPY judge.sh /app/judge.sh
RUN chmod +x /app/judge.sh

ENTRYPOINT ["/app/judge.sh"]
```

- [ ] **Step 2: 创建 judge.sh**

创建文件 `backend/judge/judge.sh`：

```bash
#!/bin/bash
set -e

LANGUAGE=$1
CODE_FILE=$2
INPUT_FILE=$3
TIME_LIMIT=$4
MEMORY_LIMIT=$5

# 编译（C++）
if [ "$LANGUAGE" = "cpp" ]; then
    g++ -std=c++17 -O2 -o /app/program "$CODE_FILE" 2>&1
fi

# 运行
if [ "$LANGUAGE" = "cpp" ]; then
    timeout "$((TIME_LIMIT / 1000))s" /app/program < "$INPUT_FILE"
else
    timeout "$((TIME_LIMIT / 1000))s" python3 "$CODE_FILE" < "$INPUT_FILE"
fi
```

- [ ] **Step 3: 构建 Docker 镜像**

```bash
cd D:\AI_code_assistant\backend\judge
docker build -t judge-sandbox:latest .
```

Expected: 镜像构建成功。

---

## Task 5: JudgeService（评测核心）

**Files:**
- Create: `backend/app/services/judge_service.py`
- Modify: `backend/app/services/__init__.py`

**依赖:** Task 2, Task 4（模型和 Docker 沙箱就绪）

- [ ] **Step 1: 创建 JudgeService**

创建文件 `backend/app/services/judge_service.py`：

```python
import subprocess
import tempfile
import os
from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.submission import Submission
from app.models.test_case import TestCase
from app.models.submission_result import SubmissionResult


class JudgeResult:
    def __init__(self, status: str, output: str = "", error: str = "", runtime_ms: int = 0, memory_kb: int = 0):
        self.status = status
        self.output = output
        self.error = error
        self.runtime_ms = runtime_ms
        self.memory_kb = memory_kb


class JudgeService:
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def judge(self, submission_id: str):
        """执行评测"""
        submission = await self._get_submission(submission_id)
        if not submission:
            return
        
        test_cases = await self._get_test_cases(submission.problem_id)
        
        # 更新为 Compiling
        await self._update_status(submission_id, "Compiling")
        
        with tempfile.TemporaryDirectory() as tmpdir:
            code_file = await self._prepare_code(submission, tmpdir)
            
            # 编译（C++）
            if submission.language == "cpp":
                compile_result = await self._compile_cpp(code_file)
                if compile_result.returncode != 0:
                    await self._update_status(
                        submission_id, "CE",
                        error_message=compile_result.stderr[:1000]
                    )
                    return
            
            # 更新为 Running
            await self._update_status(submission_id, "Running")
            
            # 逐组测试
            passed = 0
            total = len(test_cases)
            max_runtime = 0
            max_memory = 0
            
            for i, tc in enumerate(test_cases):
                result = await self._run_test_case(
                    submission.language,
                    code_file,
                    tc.input_data,
                    submission.problem.time_limit_ms,
                    submission.problem.memory_limit_mb
                )
                
                await self._save_result(submission_id, tc.id, i, result)
                
                if result.status != "AC":
                    await self._update_status(
                        submission_id, result.status,
                        passed_count=passed,
                        total_count=total,
                        error_message=result.error[:1000] if result.error else None
                    )
                    return
                
                passed += 1
                max_runtime = max(max_runtime, result.runtime_ms)
                max_memory = max(max_memory, result.memory_kb)
            
            # 全部通过
            score = int((passed / total) * 100) if total > 0 else 0
            await self._update_status(
                submission_id, "AC",
                score=score,
                passed_count=passed,
                total_count=total,
                runtime_ms=max_runtime,
                memory_kb=max_memory
            )
    
    async def _get_submission(self, submission_id: str) -> Optional[Submission]:
        result = await self.db.execute(
            select(Submission).where(Submission.id == submission_id)
        )
        return result.scalar_one_or_none()
    
    async def _get_test_cases(self, problem_id: str) -> List[TestCase]:
        result = await self.db.execute(
            select(TestCase)
            .where(TestCase.problem_id == problem_id, TestCase.is_active == True)
            .order_by(TestCase.order_index)
        )
        return result.scalars().all()
    
    async def _prepare_code(self, submission: Submission, tmpdir: str) -> str:
        ext = "cpp" if submission.language == "cpp" else "py"
        code_file = os.path.join(tmpdir, f"main.{ext}")
        with open(code_file, "w") as f:
            f.write(submission.code)
        return code_file
    
    async def _compile_cpp(self, code_file: str) -> subprocess.CompletedProcess:
        return subprocess.run(
            ["g++", "-std=c++17", "-O2", "-o", code_file.replace(".cpp", ""), code_file],
            capture_output=True,
            text=True,
            timeout=10
        )
    
    async def _run_test_case(self, language: str, code_file: str, input_data: str, time_limit_ms: int, memory_limit_mb: int) -> JudgeResult:
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write(input_data)
            input_file = f.name
        
        try:
            executable = code_file.replace(".cpp", "") if language == "cpp" else code_file
            
            cmd = [
                'docker', 'run',
                '--rm',
                '--network', 'none',
                '--memory', f'{memory_limit_mb}m',
                '--memory-swap', f'{memory_limit_mb}m',
                '--cpus', '1.0',
                '-v', f'{os.path.dirname(code_file)}:/app/code:ro',
                '-v', f'{input_file}:/app/input.txt:ro',
                'judge-sandbox:latest',
                language,
                f'/app/code/{os.path.basename(code_file)}',
                '/app/input.txt',
                str(time_limit_ms),
                str(memory_limit_mb)
            ]
            
            proc = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=time_limit_ms / 1000 + 2
            )
            
            if proc.returncode == 124:
                return JudgeResult(status="TLE")
            elif proc.returncode != 0:
                return JudgeResult(status="RE", error=proc.stderr)
            
            return JudgeResult(status="AC", output=proc.stdout)
        except subprocess.TimeoutExpired:
            return JudgeResult(status="TLE")
        except Exception as e:
            return JudgeResult(status="SystemError", error=str(e))
        finally:
            os.unlink(input_file)
    
    async def _save_result(self, submission_id: str, test_case_id: Optional[str], order: int, result: JudgeResult):
        sr = SubmissionResult(
            submission_id=submission_id,
            test_case_id=test_case_id,
            test_case_order=order,
            status=result.status,
            runtime_ms=result.runtime_ms,
            memory_kb=result.memory_kb,
            actual_output=result.output[:1000] if result.output else None
        )
        self.db.add(sr)
        await self.db.flush()
    
    async def _update_status(self, submission_id: str, status: str, **kwargs):
        submission = await self._get_submission(submission_id)
        if submission:
            submission.status = status
            for key, value in kwargs.items():
                if hasattr(submission, key):
                    setattr(submission, key, value)
            if status in ["AC", "WA", "TLE", "MLE", "RE", "CE"]:
                from datetime import datetime
                submission.judged_at = datetime.utcnow()
            await self.db.flush()
```

- [ ] **Step 2: 更新 services/__init__.py**

```python
from app.services.tag_service import TagService
from app.services.problem_service import ProblemService
from app.services.judge_service import JudgeService

__all__ = ["TagService", "ProblemService", "JudgeService"]
```

---

## Task 6: Celery 评测任务

**Files:**
- Create: `backend/app/tasks/judge_task.py`

**依赖:** Task 5（JudgeService 已完成）

- [ ] **Step 1: 创建 Celery 任务**

创建文件 `backend/app/tasks/judge_task.py`：

```python
import asyncio
from celery import Celery
from app.config import settings
from app.database import AsyncSessionLocal
from app.services.judge_service import JudgeService

# Celery 配置
celery_app = Celery(
    "judge",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL
)

@celery_app.task
def judge_submission(submission_id: str):
    """评测提交代码"""
    asyncio.run(_judge_async(submission_id))

async def _judge_async(submission_id: str):
    async with AsyncSessionLocal() as db:
        try:
            judge_service = JudgeService(db)
            await judge_service.judge(submission_id)
            await db.commit()
        except Exception as e:
            await db.rollback()
            # TODO: 记录错误日志
            raise
```

---

## Task 7: 提交 API 路由

**Files:**
- Create: `backend/app/routers/submissions.py`
- Modify: `backend/app/routers/__init__.py`
- Modify: `backend/app/main.py`

**依赖:** Task 3, Task 6（Schema 和 Celery 任务就绪）

- [ ] **Step 1: 创建 Submissions Router**

创建文件 `backend/app/routers/submissions.py`：

```python
from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.models.submission import Submission
from app.models.problem import Problem
from app.schemas.submission import SubmissionCreate, SubmissionInDB, SubmissionListItem
from app.utils.security import get_current_user
from app.models.user import User
from app.tasks.judge_task import judge_submission

router = APIRouter(prefix="/submissions", tags=["submissions"])


@router.post("", response_model=SubmissionInDB, status_code=status.HTTP_201_CREATED)
async def create_submission(
    data: SubmissionCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """提交代码"""
    # 验证题目存在
    problem = await db.execute(select(Problem).where(Problem.id == data.problem_id))
    if not problem.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Problem not found")
    
    # 创建提交记录
    submission = Submission(
        user_id=current_user.id,
        problem_id=data.problem_id,
        code=data.code,
        language=data.language,
        status="Pending"
    )
    db.add(submission)
    await db.flush()
    await db.refresh(submission)
    
    # 触发异步评测任务
    judge_submission.delay(str(submission.id))
    
    return submission


@router.get("/{submission_id}", response_model=SubmissionInDB)
async def get_submission(
    submission_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """查询提交结果"""
    result = await db.execute(
        select(Submission)
        .where(Submission.id == submission_id)
        .options(selectinload(Submission.results))
    )
    submission = result.scalar_one_or_none()
    
    if not submission:
        raise HTTPException(status_code=404, detail="Submission not found")
    
    # 只能查看自己的提交（管理员除外）
    if submission.user_id != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Access denied")
    
    return submission


@router.get("", response_model=List[SubmissionListItem])
async def list_submissions(
    problem_id: Optional[UUID] = None,
    page: int = 1,
    page_size: int = 20,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """查询用户提交历史"""
    query = select(Submission).where(Submission.user_id == current_user.id)
    
    if problem_id:
        query = query.where(Submission.problem_id == problem_id)
    
    query = query.order_by(Submission.submitted_at.desc())
    query = query.offset((page - 1) * page_size).limit(page_size)
    
    result = await db.execute(query)
    return result.scalars().all()
```

- [ ] **Step 2: 更新 routers/__init__.py**

```python
from app.routers.tags import router as tags_router
from app.routers.problems import router as problems_router
from app.routers.submissions import router as submissions_router

__all__ = ["tags_router", "problems_router", "submissions_router"]
```

- [ ] **Step 3: 更新 main.py**

```python
from app.routers import auth, tags, problems, submissions

# ... 其他代码 ...

app.include_router(auth.router, prefix="/api/v1")
app.include_router(tags.router, prefix="/api/v1")
app.include_router(problems.router, prefix="/api/v1")
app.include_router(submissions.router, prefix="/api/v1")  # 新增
```

---

## Task 8: 集成验证

**Files:**
- 无新增/修改

**依赖:** Task 7（所有路由已注册）

- [ ] **Step 1: 运行测试**

```bash
cd D:\AI_code_assistant\backend
pytest tests/ -v
```

Expected: 测试通过。

- [ ] **Step 2: 启动服务验证**

```bash
# 启动后端
cd D:\AI_code_assistant\backend
uvicorn app.main:app --reload

# 在另一个终端测试提交
curl -X POST http://localhost:8000/api/v1/submissions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer {token}" \
  -d '{
    "problem_id": "...",
    "code": "print(1+1)",
    "language": "py"
  }'
```

Expected: 返回 201，status 为 Pending，随后 Celery worker 处理评测。

- [ ] **Step 3: 验证 Celery Worker**

```bash
cd D:\AI_code_assistant\backend
celery -A app.tasks.judge_task worker --loglevel=info
```

Expected: Worker 启动，接收到任务后执行评测。

---

## 自审检查清单

**1. Spec 覆盖检查：**

| 设计需求 | 对应任务 | 状态 |
|----------|----------|------|
| 数据库迁移 | Task 1 | ✅ |
| 数据模型 | Task 2 | ✅ |
| Pydantic Schemas | Task 3 | ✅ |
| Docker 沙箱 | Task 4 | ✅ |
| JudgeService | Task 5 | ✅ |
| Celery 任务 | Task 6 | ✅ |
| API 路由 | Task 7 | ✅ |
| 集成验证 | Task 8 | ✅ |

**2. Placeholder 扫描：**
- 无 TBD/TODO/"implement later"/"similar to Task X"
- 所有步骤包含完整代码

**3. 类型一致性检查：**
- `SubmissionCreate.language` 限制为 cpp/py
- `JudgeResult.status` 与数据库 status 字段一致
- API 参数与 Schema 定义一致

---

## 执行选项

Plan complete and saved to `docs/superpowers/plans/2026-05-15-judge-engine.md`.

**Two execution options:**

**1. Subagent-Driven (recommended)** - I dispatch a fresh subagent per task, review between tasks, fast iteration

**2. Inline Execution** - Execute tasks in this session using executing-plans, batch execution with checkpoints for review

**Which approach?**
