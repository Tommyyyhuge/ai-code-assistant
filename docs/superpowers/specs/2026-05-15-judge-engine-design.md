# 评测引擎 MVP 设计方案

> 日期: 2026-05-15  
> 版本: v1.0  
> 范围: 后端代码评测核心功能（C++ + Python）  
> 方案: 纯 Docker 沙箱 + Celery 任务队列  
> 状态: 已批准

---

## 1. 项目背景

前端题目 API 已对接完成，用户可以在前端查看题目列表和详情。但平台目前无法接收代码提交和进行评测。本设计旨在实现最小可用的评测引擎，支持用户提交代码、在 Docker 沙箱中编译运行、对比测试用例输出、返回评测结果。

## 2. 目标

- 实现代码提交 API（保存代码到数据库，触发评测）
- 实现 Docker 沙箱评测（编译 + 运行 + 判题）
- 支持 C++ 和 Python 两种语言
- 返回 AC/WA/TLE/MLE/RE/CE 评测状态
- 实现提交结果查询 API
- 数据库支持测试用例、提交记录、结果详情

## 3. 范围边界

### 3.1 包含（IN SCOPE）

- `test_cases` 表：存储题目测试数据
- `submissions` 表：存储用户提交记录
- `submission_results` 表：存储每组测试用例的评测结果
- 提交代码 API（POST /api/v1/submissions）
- 查询提交结果 API（GET /api/v1/submissions/{id}）
- Celery 评测任务（异步执行）
- Docker 沙箱（C++ + Python）
- 评测状态判定（AC/WA/TLE/MLE/RE/CE）
- 评测 Dockerfile 和入口脚本

### 3.2 排除（OUT OF SCOPE）

- Java 语言支持（后续迭代）
- 实时评测状态推送（WebSocket）
- 评测队列优先级调度
- 代码相似度检测（plagiarism）
- 提交记录排行榜
- 测试数据文件上传（MVP 阶段手动插入）
- 评测结果缓存
- 多评测节点负载均衡

## 4. 架构设计

### 4.1 整体流程

```
用户提交代码
    ↓
POST /api/v1/submissions
    ↓
submissions 表（状态 Pending）
    ↓
Celery Worker 触发评测任务
    ↓
Docker 沙箱（编译 + 运行 + 判题）
    ↓
更新 submissions 表（AC/WA/TLE/MLE/RE/CE）
    ↓
用户查询 GET /api/v1/submissions/{id}
```

### 4.2 组件架构

```
┌─────────────────────────────────────────────────────────────┐
│                        FastAPI 后端                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐  │
│  │ Submission   │  │ JudgeService │  │ Celery Worker    │  │
│  │ Router       │  │              │  │ (judge_task.py)  │  │
│  └──────────────┘  └──────────────┘  └──────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                            │
                            │ 调用 Docker API
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                    Docker 沙箱容器                            │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐  │
│  │ 编译代码     │  │ 运行测试     │  │ 对比输出         │  │
│  │ (g++/python3)│  │ (逐组执行)   │  │ (normalize)      │  │
│  └──────────────┘  └──────────────┘  └──────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

## 5. 数据模型设计

### 5.1 TestCase（测试用例）

| 字段 | 类型 | 约束 | 默认值 | 说明 |
|------|------|------|--------|------|
| id | UUID | PK | gen_random_uuid() | 测试数据ID |
| problem_id | UUID | FK→problems.id, NOT NULL, ON DELETE CASCADE | - | 所属题目 |
| input_data | TEXT | NOT NULL | - | 输入数据 |
| expected_output | TEXT | NOT NULL | - | 期望输出 |
| is_sample | BOOLEAN | NOT NULL | FALSE | 是否样例数据 |
| is_active | BOOLEAN | NOT NULL | TRUE | 是否启用 |
| order_index | INTEGER | NOT NULL | 0 | 排序顺序 |
| created_at | TIMESTAMP | NOT NULL | NOW() | 创建时间 |

**索引：**
- `idx_test_cases_problem`: problem_id, is_active, order_index

### 5.2 Submission（提交记录）

| 字段 | 类型 | 约束 | 默认值 | 说明 |
|------|------|------|--------|------|
| id | UUID | PK | gen_random_uuid() | 提交ID |
| user_id | UUID | FK→users.id, NOT NULL | - | 提交用户 |
| problem_id | UUID | FK→problems.id, NOT NULL | - | 题目ID |
| code | TEXT | NOT NULL | - | 提交的代码 |
| language | VARCHAR(20) | NOT NULL | - | 语言: cpp/py |
| status | VARCHAR(20) | NOT NULL | 'Pending' | 状态 |
| score | INTEGER | NULL | NULL | 得分（百分比） |
| runtime_ms | INTEGER | NULL | NULL | 运行时间（毫秒） |
| memory_kb | INTEGER | NULL | NULL | 内存使用（KB） |
| passed_count | SMALLINT | NULL | NULL | 通过测试点数 |
| total_count | SMALLINT | NULL | NULL | 总测试点数量 |
| error_message | TEXT | NULL | NULL | 错误信息 |
| judge_log | TEXT | NULL | NULL | 评测日志 |
| submitted_at | TIMESTAMP | NOT NULL | NOW() | 提交时间 |
| judged_at | TIMESTAMP | NULL | NULL | 评测完成时间 |

**状态枚举：** `Pending`, `Compiling`, `Running`, `AC` (Accepted), `WA` (Wrong Answer), `TLE` (Time Limit Exceeded), `MLE` (Memory Limit Exceeded), `RE` (Runtime Error), `CE` (Compile Error), `SystemError`

**索引：**
- `idx_submissions_user`: user_id, submitted_at DESC
- `idx_submissions_problem`: problem_id, status
- `idx_submissions_status`: status, submitted_at

### 5.3 SubmissionResult（提交结果详情）

| 字段 | 类型 | 约束 | 默认值 | 说明 |
|------|------|------|--------|------|
| id | UUID | PK | gen_random_uuid() | 结果ID |
| submission_id | UUID | FK→submissions.id, ON DELETE CASCADE | - | 提交ID |
| test_case_id | UUID | FK→test_cases.id, NULL | NULL | 测试点ID |
| test_case_order | SMALLINT | NOT NULL | - | 测试点序号 |
| status | VARCHAR(20) | NOT NULL | - | 该测试点状态 |
| runtime_ms | INTEGER | NULL | NULL | 运行时间 |
| memory_kb | INTEGER | NULL | NULL | 内存使用 |
| actual_output | TEXT | NULL | NULL | 实际输出（截断存储） |
| diff_info | TEXT | NULL | NULL | 差异信息 |
| created_at | TIMESTAMP | NOT NULL | NOW() | 创建时间 |

**索引：**
- `idx_submission_results_submission`: submission_id, test_case_order

## 6. API 接口设计

### 6.1 提交代码

```http
POST /api/v1/submissions
Content-Type: application/json
Authorization: Bearer {token}

Request Body:
{
  "problem_id": "550e8400-e29b-41d4-a716-446655440000",
  "code": "#include <iostream>\nusing namespace std;\nint main() {\n    int a, b;\n    cin >> a >> b;\n    cout << a + b << endl;\n    return 0;\n}",
  "language": "cpp"
}

Response: 201 Created
{
  "id": "550e8400-e29b-41d4-a716-446655440001",
  "problem_id": "550e8400-e29b-41d4-a716-446655440000",
  "language": "cpp",
  "status": "Pending",
  "submitted_at": "2026-05-15T10:00:00Z"
}
```

### 6.2 查询提交结果

```http
GET /api/v1/submissions/{submission_id}
Authorization: Bearer {token}

Response: 200 OK
{
  "id": "550e8400-e29b-41d4-a716-446655440001",
  "problem_id": "550e8400-e29b-41d4-a716-446655440000",
  "code": "...",
  "language": "cpp",
  "status": "AC",
  "score": 100,
  "runtime_ms": 12,
  "memory_kb": 4096,
  "passed_count": 10,
  "total_count": 10,
  "error_message": null,
  "submitted_at": "2026-05-15T10:00:00Z",
  "judged_at": "2026-05-15T10:00:05Z",
  "results": [
    {
      "test_case_order": 1,
      "status": "AC",
      "runtime_ms": 12,
      "memory_kb": 4096,
      "actual_output": "3"
    }
  ]
}
```

### 6.3 查询用户提交历史

```http
GET /api/v1/submissions?problem_id={problem_id}&page=1&page_size=20
Authorization: Bearer {token}

Response: 200 OK
{
  "items": [...],
  "total": 50,
  "page": 1,
  "page_size": 20,
  "total_pages": 3
}
```

## 7. 评测核心设计

### 7.1 Docker 沙箱镜像

**Dockerfile** (`backend/judge/Dockerfile`):

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

**入口脚本** (`backend/judge/judge.sh`):

```bash
#!/bin/bash
set -e

LANGUAGE=$1
CODE_FILE=$2
INPUT_FILE=$3
TIME_LIMIT=$4  # 毫秒
MEMORY_LIMIT=$5  # MB

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

### 7.2 Celery 评测任务

```python
# app/tasks/judge_task.py
import subprocess
import tempfile
import os
from celery import shared_task
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import AsyncSessionLocal
from app.models.submission import Submission
from app.models.test_case import TestCase
from app.services.judge_service import JudgeService

@shared_task
def judge_submission(submission_id: str):
    """评测提交代码"""
    asyncio.run(_judge_async(submission_id))

async def _judge_async(submission_id: str):
    async with AsyncSessionLocal() as db:
        judge_service = JudgeService(db)
        await judge_service.judge(submission_id)
```

### 7.3 JudgeService 核心逻辑

```python
# app/services/judge_service.py
class JudgeService:
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def judge(self, submission_id: str):
        # 1. 获取提交记录和测试用例
        submission = await self._get_submission(submission_id)
        test_cases = await self._get_test_cases(submission.problem_id)
        
        # 2. 更新状态为 Compiling
        await self._update_status(submission_id, "Compiling")
        
        # 3. 准备临时目录
        with tempfile.TemporaryDirectory() as tmpdir:
            code_file = self._prepare_code(submission, tmpdir)
            
            # 4. 编译（C++）
            if submission.language == "cpp":
                compile_result = await self._compile_cpp(code_file)
                if compile_result.returncode != 0:
                    await self._update_status(
                        submission_id, "CE",
                        error_message=compile_result.stderr[:1000]
                    )
                    return
            
            # 5. 更新状态为 Running
            await self._update_status(submission_id, "Running")
            
            # 6. 逐组运行测试用例
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
                
                # 记录结果
                await self._save_result(submission_id, tc, i, result)
                
                if result.status == "TLE":
                    await self._update_status(submission_id, "TLE", passed, total)
                    return
                elif result.status == "MLE":
                    await self._update_status(submission_id, "MLE", passed, total)
                    return
                elif result.status == "RE":
                    await self._update_status(submission_id, "RE", passed, total, error=result.error)
                    return
                elif result.status == "WA":
                    await self._update_status(submission_id, "WA", passed, total)
                    return
                
                # AC
                passed += 1
                max_runtime = max(max_runtime, result.runtime_ms)
                max_memory = max(max_memory, result.memory_kb)
            
            # 7. 全部通过
            score = int((passed / total) * 100) if total > 0 else 0
            await self._update_status(
                submission_id, "AC",
                passed_count=passed,
                total_count=total,
                score=score,
                runtime_ms=max_runtime,
                memory_kb=max_memory
            )
    
    async def _run_test_case(self, language: str, code_file: str, input_data: str, time_limit_ms: int, memory_limit_mb: int):
        """在 Docker 中运行单个测试用例"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write(input_data)
            input_file = f.name
        
        try:
            # Docker 运行命令
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
            
            # 使用 timeout 控制时间
            proc = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=time_limit_ms / 1000 + 2  # 额外 2 秒缓冲
            )
            
            if proc.returncode == 124:  # timeout 命令返回 124 表示超时
                return JudgeResult(status="TLE")
            elif proc.returncode != 0:
                return JudgeResult(status="RE", error=proc.stderr[:1000])
            
            return JudgeResult(
                status="AC",
                output=proc.stdout,
                runtime_ms=0,  # TODO: 实际测量
                memory_kb=0    # TODO: 实际测量
            )
        finally:
            os.unlink(input_file)
```

## 8. 资源限制策略

| 资源 | 限制方式 | 说明 |
|------|----------|------|
| **CPU** | `--cpus=1.0` | 限制使用 1 核 CPU |
| **内存** | `--memory=256m --memory-swap=256m` | 限制内存 + 禁止 swap |
| **时间** | `timeout` 命令 | 基于题目时间限制 |
| **网络** | `--network none` | 禁止网络访问 |
| **文件系统** | `-v` 只读挂载 | 代码和输入文件只读 |

## 9. 错误处理策略

| 场景 | 处理方式 |
|------|----------|
| 编译错误 | 返回 CE，记录 stderr |
| 运行超时 | 返回 TLE，终止容器 |
| 内存超限 | 返回 MLE，Docker OOM Killer |
| 运行时错误 | 返回 RE，记录 stderr |
| 输出不匹配 | 返回 WA，可选记录 diff |
| 系统错误 | 返回 SystemError，记录日志 |
| Docker 不可用 | 返回 SystemError，重试机制 |

## 10. 性能考虑

- **容器启动延迟**：1-2 秒（alpine 镜像小）
- **编译缓存**：MVP 不考虑，每次重新编译
- **并发限制**：单 worker 串行执行，后续可扩展多 worker
- **资源清理**：使用 `docker run --rm` 自动删除容器

## 11. 文件变更清单

### 新增文件
- `backend/app/models/submission.py` - 提交记录模型
- `backend/app/models/test_case.py` - 测试数据模型
- `backend/app/models/submission_result.py` - 结果详情模型
- `backend/app/schemas/submission.py` - Pydantic Schema
- `backend/app/services/judge_service.py` - 评测业务逻辑
- `backend/app/routers/submissions.py` - 提交 API 路由
- `backend/app/tasks/judge_task.py` - Celery 评测任务
- `backend/judge/Dockerfile` - 评测沙箱镜像
- `backend/judge/judge.sh` - 评测入口脚本
- `backend/alembic/versions/xxxx_add_submissions_and_test_cases.py` - 数据库迁移

### 修改文件
- `backend/app/models/__init__.py` - 导出新模型
- `backend/app/main.py` - 注册 submissions 路由
- `docker-compose.yml` - 构建 judge 镜像（可选）

## 12. 验收标准

- [ ] 可以提交 C++ 代码并返回 Pending 状态
- [ ] Celery Worker 能触发评测任务
- [ ] Docker 沙箱能编译 C++ 代码
- [ ] Docker 沙箱能运行 Python 代码
- [ ] AC/WA/TLE/MLE/RE/CE 状态判定正确
- [ ] 评测结果能正确保存到数据库
- [ ] 可以查询提交历史和结果详情
- [ ] 资源限制（时间/内存）生效

---

## 13. 后续扩展点

1. **Java 支持**：扩展 Dockerfile 安装 OpenJDK
2. **实时推送**：WebSocket 推送评测状态变更
3. **评测缓存**：相同代码跳过重复评测
4. **并发评测**：多 worker 并行处理
5. **特殊判题**：支持 SPJ（Special Judge）
6. **测试数据上传**：管理员上传测试数据文件
