import uuid
from datetime import datetime
from typing import Optional
import docker
from docker.errors import ContainerError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.submission import Submission
from app.models.test_case import TestCase
from app.models.submission_result import SubmissionResult


class JudgeService:
    """评测服务：接收提交、调用Docker沙箱执行、返回结果"""
    
    DOCKER_IMAGE = "judge-sandbox:latest"
    TIME_LIMIT_MS = 1000  # 1秒
    MEMORY_LIMIT_MB = 256  # 256MB
    
    @staticmethod
    def _get_docker_client():
        """每次评测创建新的 Docker 客户端（Celery fork 后连接失效）"""
        try:
            client = docker.from_env()
            client.ping()
            return client
        except Exception:
            # 重试一次
            import time
            time.sleep(1)
            return docker.from_env()
    
    async def create_submission(
        self,
        db: AsyncSession,
        problem_id: uuid.UUID,
        code: str,
        language: str,
        user_id: uuid.UUID | None = None
    ) -> Submission:
        """创建提交记录，状态为 pending"""
        submission = Submission(
            id=uuid.uuid4(),
            user_id=user_id,
            problem_id=problem_id,
            code=code,
            language=language,
            status="pending",
            submitted_at=datetime.utcnow()
        )
        db.add(submission)
        await db.commit()
        await db.refresh(submission)
        return submission
    
    async def get_submission(
        self,
        db: AsyncSession,
        submission_id: uuid.UUID
    ) -> Optional[Submission]:
        """获取提交记录详情"""
        result = await db.execute(
            select(Submission).where(Submission.id == submission_id)
        )
        return result.scalar_one_or_none()
    
    async def judge_submission(
        self,
        db: AsyncSession,
        submission: Submission
    ) -> None:
        """执行评测"""
        import logging
        log = logging.getLogger("judge")
        try:
            # 获取测试用例
            result = await db.execute(
                select(TestCase).where(
                    TestCase.problem_id == submission.problem_id
                ).order_by(TestCase.order_index)
            )
            test_cases = result.scalars().all()
            log.info(f"Found {len(test_cases)} test cases")
            
            if not test_cases:
                submission.status = "error"
                submission.error_message = "No test cases found for this problem"
                await db.commit()
                return
            
            total_count = len(test_cases)
            passed_count = 0
            total_runtime = 0
            total_memory = 0
            
            for test_case in test_cases:
                result_item = await self._run_single_test(
                    db, submission, test_case
                )
                
                if result_item.status == "passed":
                    passed_count += 1
                    total_runtime += result_item.runtime_ms or 0
                    total_memory += result_item.memory_kb or 0
                else:
                    # 有测试用例失败，整体失败
                    submission.status = "failed"
                    break
            else:
                # 所有测试用例通过
                submission.status = "accepted"
                submission.score = int(passed_count / total_count * 100)
                submission.runtime_ms = total_runtime // total_count if total_count > 0 else 0
                submission.memory_kb = total_memory // total_count if total_count > 0 else 0
            
            submission.passed_count = passed_count
            submission.total_count = total_count
            submission.judged_at = datetime.utcnow()
            await db.commit()
            
        except Exception as e:
            submission.status = "error"
            submission.error_message = str(e)
            await db.commit()
    
    async def _run_single_test(
        self,
        db: AsyncSession,
        submission: Submission,
        test_case: TestCase
    ) -> SubmissionResult:
        """运行单个测试用例"""
        import tempfile
        import os
        import logging
        log = logging.getLogger("judge")
        
        # 创建临时文件
        with tempfile.TemporaryDirectory() as tmpdir:
            # 写入代码文件
            if submission.language == "cpp":
                code_file = os.path.join(tmpdir, "main.cpp")
            else:
                code_file = os.path.join(tmpdir, "main.py")
            
            with open(code_file, "w", encoding="utf-8") as f:
                f.write(submission.code)
            
            # 写入输入文件
            input_file = os.path.join(tmpdir, "input.txt")
            with open(input_file, "w", encoding="utf-8") as f:
                f.write(test_case.input_data)
            
            # 代码文件名
            code_ext = os.path.splitext(code_file)[1]
            container_code_path = f"/app/main{code_ext}"

            # 运行Docker容器
            try:
                docker_client = self._get_docker_client()
                log.info(f"Running container for test case, lang={submission.language}")
                container = docker_client.containers.run(
                    self.DOCKER_IMAGE,
                    command=[
                        submission.language,
                        container_code_path,
                        "/app/input.txt",
                        str(self.TIME_LIMIT_MS),
                        str(self.MEMORY_LIMIT_MB)
                    ],
                    volumes={
                        tmpdir: {"bind": "/app", "mode": "ro"}
                    },
                    mem_limit=f"{self.MEMORY_LIMIT_MB}m",
                    cpu_quota=100000,
                    network_mode="none",
                    # seccomp 由重新构建的 sandbox 镜像内置，不在运行时指定
                    detach=True
                )
                
                # 等待容器完成
                result = container.wait(timeout=self.TIME_LIMIT_MS / 1000 + 5)
                
                # 获取输出
                if result["StatusCode"] == 0:
                    stdout = container.logs(stdout=True, stderr=False).decode("utf-8").strip()
                    stderr = container.logs(stdout=False, stderr=True).decode("utf-8").strip()
                    
                    # 检查输出是否匹配
                    if stdout == test_case.expected_output.strip():
                        status = "passed"
                    else:
                        status = "wrong_answer"
                    
                    # 创建结果记录
                    submission_result = SubmissionResult(
                        id=uuid.uuid4(),
                        submission_id=submission.id,
                        test_case_order=test_case.order_index,
                        status=status,
                        actual_output=stdout
                    )
                else:
                    # 运行时错误
                    stderr = container.logs(stdout=False, stderr=True).decode("utf-8").strip()
                    submission_result = SubmissionResult(
                        id=uuid.uuid4(),
                        submission_id=submission.id,
                        test_case_order=test_case.order_index,
                        status="runtime_error",
                        actual_output=stderr
                    )
                
                container.remove(force=True)
                
            except ContainerError as e:
                log.error(f"ContainerError: {str(e)[:150]}")
                submission_result = SubmissionResult(
                    id=uuid.uuid4(),
                    submission_id=submission.id,
                    test_case_order=test_case.order_index,
                    status="runtime_error" if "timeout" in str(e).lower() else "error",
                    actual_output=str(e)[:500]
                )
            except Exception as e:
                log.error(f"Docker exception: {type(e).__name__}: {str(e)[:200]}")
                submission_result = SubmissionResult(
                    id=uuid.uuid4(),
                    submission_id=submission.id,
                    test_case_order=test_case.order_index,
                    status="error",
                    actual_output=f"{type(e).__name__}: {str(e)[:300]}"
                )
            except Exception as e:
                submission_result = SubmissionResult(
                    id=uuid.uuid4(),
                    submission_id=submission.id,
                    test_case_order=test_case.order_index,
                    status="error",
                    actual_output=str(e)
                )
            
            db.add(submission_result)
            await db.commit()
            return submission_result
