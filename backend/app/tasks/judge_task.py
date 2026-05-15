import asyncio
import uuid
from app.celery_config import celery_app
from app.services.judge_service import JudgeService
from app.database import AsyncSessionLocal


async def _run_judge(submission_id: str, task_self) -> dict:
    """异步评测主逻辑 — 单事件循环内完成所有操作"""
    submission_uuid = uuid.UUID(submission_id)

    # 更新任务状态
    task_self.update_state(state="STARTED", meta={"submission_id": submission_id})

    # 单个异步会话覆盖整个评测生命周期
    async with AsyncSessionLocal() as db:
        judge_service = JudgeService()

        # 获取提交记录
        submission = await judge_service.get_submission(db, submission_uuid)
        if not submission:
            return {"status": "error", "message": "Submission not found"}

        # 更新状态为 judging
        submission.status = "judging"
        await db.commit()

        # 执行评测
        await judge_service.judge_submission(db, submission)

        # 返回结果
        return {
            "status": submission.status,
            "score": submission.score,
            "passed_count": submission.passed_count,
            "total_count": submission.total_count,
            "runtime_ms": submission.runtime_ms,
            "memory_kb": submission.memory_kb,
        }


@celery_app.task(bind=True)
def judge_submission_task(self, submission_id: str):
    """异步评测任务 — 使用单一 asyncio.run() 调用"""
    try:
        return asyncio.run(_run_judge(submission_id, self))
    except Exception as e:
        return {"status": "error", "message": str(e)}
