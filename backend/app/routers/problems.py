from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.user import User
from app.schemas.problem import (
    ProblemCreate,
    ProblemInDB,
    ProblemListItem,
    ProblemUpdate,
    PaginatedResponse
)
from app.services.problem_service import ProblemService
from app.utils.security import get_current_user, require_admin

router = APIRouter(prefix="/problems", tags=["problems"])


@router.get("", response_model=PaginatedResponse[ProblemListItem])
async def list_problems(
    search: Optional[str] = None,
    difficulty_min: Optional[int] = Query(None, ge=1, le=10),
    difficulty_max: Optional[int] = Query(None, ge=1, le=10),
    source_oj: Optional[str] = None,
    tag_ids: Optional[List[UUID]] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db)
):
    """获取题目列表（支持筛选和分页）"""
    items, total = await ProblemService.list_problems(
        db,
        search=search,
        difficulty_min=difficulty_min,
        difficulty_max=difficulty_max,
        source_oj=source_oj,
        tag_ids=tag_ids,
        page=page,
        page_size=page_size
    )
    
    total_pages = (total + page_size - 1) // page_size
    
    return PaginatedResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages
    )


@router.get("/{problem_id}", response_model=ProblemInDB)
async def get_problem(
    problem_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """获取题目详情"""
    problem = await ProblemService.get_problem(db, problem_id)
    if not problem:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Problem not found"
        )
    return problem


@router.post("", response_model=ProblemInDB, status_code=status.HTTP_201_CREATED)
async def create_problem(
    data: ProblemCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """创建题目"""
    return await ProblemService.create_problem(db, data, current_user.id)


@router.patch("/{problem_id}", response_model=ProblemInDB)
async def update_problem(
    problem_id: UUID,
    data: ProblemUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """更新题目"""
    # TODO: 检查权限（创建者或管理员）
    problem = await ProblemService.update_problem(db, problem_id, data)
    if not problem:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Problem not found"
        )
    return problem


@router.delete("/{problem_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_problem(
    problem_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """删除题目（仅管理员）"""
    success = await ProblemService.delete_problem(db, problem_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Problem not found"
        )
