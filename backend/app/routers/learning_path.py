from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.rate_limit import limiter
from app.schemas.learning_path import LearningPathDetail, EnrollResponse
from app.services.learning_path_service import LearningPathService
from app.utils.security import get_current_user, get_current_user_safe

router = APIRouter(prefix="/api/v1/paths", tags=["学习路径"])


@router.get("/", response_model=list)
@limiter.limit("30/minute")
async def list_paths(
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user_safe),
):
    """获取所有学习路线"""
    service = LearningPathService(db)
    user_id = current_user.id if current_user else None
    return await service.list_paths(user_id)


@router.get("/{slug}", response_model=LearningPathDetail)
@limiter.limit("30/minute")
async def get_path(
    slug: str,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user_safe),
):
    """获取路线详情"""
    service = LearningPathService(db)
    user_id = current_user.id if current_user else None
    detail = await service.get_path_detail(slug, user_id)
    if not detail:
        raise HTTPException(status_code=404, detail="路线未找到")
    return detail


@router.post("/{slug}/enroll", response_model=EnrollResponse)
@limiter.limit("10/minute")
async def enroll_path(
    slug: str,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """加入学习路线"""
    service = LearningPathService(db)
    try:
        return await service.enroll(current_user.id, slug)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
