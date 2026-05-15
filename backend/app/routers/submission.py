from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from app.database import get_db
from app.rate_limit import limiter
from app.schemas.submission import SubmissionCreate, SubmissionInDB, SubmissionListItem
from app.services.judge_service import JudgeService
from app.tasks.judge_task import judge_submission_task
from app.utils.security import get_current_user

router = APIRouter(prefix="/api/v1/submissions", tags=["submissions"])


@router.post(
    "/",
    response_model=SubmissionInDB,
    status_code=status.HTTP_201_CREATED,
    summary="提交代码",
    description="提交代码进行评测"
)
@limiter.limit("30/minute")
async def submit_code(
    request: Request,
    submission_data: SubmissionCreate,
    db: AsyncSession = Depends(get_db),
    judge_service: JudgeService = Depends(),
    current_user=Depends(get_current_user)
):
    """提交代码进行评测"""
    # 创建提交记录（关联当前用户）
    submission = await judge_service.create_submission(
        db=db,
        user_id=current_user.id,
        problem_id=submission_data.problem_id,
        code=submission_data.code,
        language=submission_data.language
    )

    # 启动异步评测任务
    judge_submission_task.delay(str(submission.id))

    return submission


@router.get(
    "/{submission_id}",
    response_model=SubmissionInDB,
    summary="获取提交详情",
    description="获取提交的详细信息和评测结果"
)
async def get_submission(
    submission_id: UUID,
    db: AsyncSession = Depends(get_db),
    judge_service: JudgeService = Depends(),
    current_user=Depends(get_current_user)
):
    """获取提交详情"""
    submission = await judge_service.get_submission(db, submission_id)
    if not submission:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Submission not found"
        )
    # 仅允许查看自己的提交（管理员除外）
    if submission.user_id and submission.user_id != current_user.id and current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    return submission


@router.get(
    "/",
    response_model=list[SubmissionListItem],
    summary="获取提交列表",
    description="获取用户的提交历史列表"
)
async def list_submissions(
    problem_id: Optional[UUID] = None,
    status: Optional[str] = None,
    skip: int = 0,
    limit: int = 20,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user)
):
    """获取当前用户的提交历史列表"""
    from sqlalchemy import select
    from app.models.submission import Submission

    query = select(Submission).where(Submission.user_id == current_user.id)

    if problem_id:
        query = query.where(Submission.problem_id == problem_id)
    if status:
        query = query.where(Submission.status == status)

    query = query.offset(skip).limit(limit).order_by(Submission.submitted_at.desc())

    result = await db.execute(query)
    submissions = result.scalars().all()

    return submissions
