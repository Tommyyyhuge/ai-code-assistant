from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from app.database import get_db
from app.rate_limit import limiter
from app.schemas.knowledge import (
    KnowledgeTreeResponse, KnowledgeNodeDetailResponse,
    UserProgressCreate, UserProgressResponse, UserProgressSummary,
)
from app.services.knowledge_service import KnowledgeService
from app.utils.security import get_current_user, get_current_user_safe

router = APIRouter(prefix="/api/v1/knowledge", tags=["知识图谱"])


@router.get("/tree", response_model=KnowledgeTreeResponse)
@limiter.limit("30/minute")
async def get_tree(
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user_safe),
):
    """获取知识树，如已登录则合并用户进度"""
    service = KnowledgeService(db)
    user_id = current_user.id if current_user else None
    children = await service.get_tree(user_id)
    return KnowledgeTreeResponse(children=children)


@router.get("/nodes/{slug}", response_model=KnowledgeNodeDetailResponse)
@limiter.limit("30/minute")
async def get_node(
    slug: str,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user_safe),
):
    """获取节点详情（含邻居、关联题目、用户进度）"""
    service = KnowledgeService(db)
    user_id = current_user.id if current_user else None
    detail = await service.get_node_detail(slug, user_id)
    if not detail:
        raise HTTPException(status_code=404, detail="知识点未找到")
    return detail


@router.post("/progress", response_model=UserProgressResponse)
@limiter.limit("20/minute")
async def update_progress(
    data: UserProgressCreate,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """更新当前用户的学习进度"""
    service = KnowledgeService(db)
    progress = await service.upsert_progress(current_user.id, data.knowledge_node_id, data.status)
    return UserProgressResponse(
        status=progress.status,
        practice_count=progress.practice_count,
        started_at=progress.started_at,
        completed_at=progress.completed_at,
    )


@router.get("/progress", response_model=UserProgressSummary)
@limiter.limit("20/minute")
async def get_progress(
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """获取当前用户的学习进度总览"""
    service = KnowledgeService(db)
    return await service.get_user_progress_summary(current_user.id)
