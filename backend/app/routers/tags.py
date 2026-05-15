from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas.tag import TagCreate, TagInDB, TagUpdate
from app.services.tag_service import TagService
from app.utils.security import get_current_user, require_admin
from app.models.user import User

router = APIRouter(prefix="/tags", tags=["tags"])


@router.get("", response_model=List[TagInDB])
async def list_tags(
    category: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """获取标签列表"""
    return await TagService.get_tags(db, category=category)


@router.get("/{tag_id}", response_model=TagInDB)
async def get_tag(
    tag_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """获取标签详情"""
    tag = await TagService.get_tag(db, tag_id)
    if not tag:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tag not found"
        )
    return tag


@router.post("", response_model=TagInDB, status_code=status.HTTP_201_CREATED)
async def create_tag(
    data: TagCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """创建标签（仅管理员）"""
    return await TagService.create_tag(db, data)


@router.patch("/{tag_id}", response_model=TagInDB)
async def update_tag(
    tag_id: UUID,
    data: TagUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """更新标签（仅管理员）"""
    tag = await TagService.update_tag(db, tag_id, data)
    if not tag:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tag not found"
        )
    return tag


@router.delete("/{tag_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_tag(
    tag_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """删除标签（仅管理员）"""
    success = await TagService.delete_tag(db, tag_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tag not found"
        )
