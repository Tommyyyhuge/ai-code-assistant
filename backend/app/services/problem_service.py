from typing import List, Optional, Tuple
from uuid import UUID

from sqlalchemy import select, func, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.problem import Problem
from app.models.tag import Tag
from app.schemas.problem import ProblemCreate, ProblemUpdate
from app.services.tag_service import TagService


class ProblemService:
    @staticmethod
    async def get_problem(db: AsyncSession, problem_id: UUID) -> Optional[Problem]:
        """获取题目详情（含标签）"""
        result = await db.execute(
            select(Problem)
            .where(Problem.id == problem_id)
            .options(selectinload(Problem.tags))
        )
        return result.scalar_one_or_none()
    
    @staticmethod
    async def create_problem(
        db: AsyncSession,
        data: ProblemCreate,
        user_id: UUID
    ) -> Problem:
        """创建题目"""
        from app.utils.security import slugify
        
        # 生成唯一 slug
        base_slug = slugify(data.title)
        slug = base_slug
        counter = 1
        while True:
            existing = await db.execute(
                select(Problem).where(Problem.title_slug == slug)
            )
            if not existing.scalar_one_or_none():
                break
            slug = f"{base_slug}-{counter}"
            counter += 1
        
        # 创建题目
        problem = Problem(
            title=data.title,
            title_slug=slug,
            description=data.description,
            input_format=data.input_format,
            output_format=data.output_format,
            constraints=data.constraints,
            difficulty=data.difficulty,
            time_limit_ms=data.time_limit_ms,
            memory_limit_mb=data.memory_limit_mb,
            source_oj=data.source_oj,
            source_problem_id=data.source_problem_id,
            source_url=data.source_url,
            created_by=user_id,
            is_published=False  # 默认未发布
        )
        db.add(problem)
        await db.flush()
        
        # 关联标签
        if data.tag_ids:
            tags = await TagService.get_tags_by_ids(db, data.tag_ids)
            problem.tags = tags
        
        await db.flush()
        await db.refresh(problem)
        return problem
    
    @staticmethod
    async def update_problem(
        db: AsyncSession,
        problem_id: UUID,
        data: ProblemUpdate
    ) -> Optional[Problem]:
        """更新题目"""
        problem = await ProblemService.get_problem(db, problem_id)
        if not problem:
            return None
        
        # 更新非 None 字段
        update_data = data.model_dump(exclude_unset=True)
        
        # 如果更新标题，重新生成 slug
        if "title" in update_data:
            from app.utils.security import slugify
            base_slug = slugify(update_data["title"])
            slug = base_slug
            counter = 1
            while True:
                existing = await db.execute(
                    select(Problem).where(
                        and_(Problem.title_slug == slug, Problem.id != problem_id)
                    )
                )
                if not existing.scalar_one_or_none():
                    break
                slug = f"{base_slug}-{counter}"
                counter += 1
            update_data["title_slug"] = slug
        
        # 如果更新标签
        if "tag_ids" in update_data:
            tag_ids = update_data.pop("tag_ids")
            if tag_ids is not None:
                tags = await TagService.get_tags_by_ids(db, tag_ids)
                problem.tags = tags
        
        for field, value in update_data.items():
            setattr(problem, field, value)
        
        await db.flush()
        await db.refresh(problem)
        return problem
    
    @staticmethod
    async def delete_problem(db: AsyncSession, problem_id: UUID) -> bool:
        """删除题目"""
        problem = await ProblemService.get_problem(db, problem_id)
        if not problem:
            return False
        await db.delete(problem)
        await db.flush()
        return True
    
    @staticmethod
    async def list_problems(
        db: AsyncSession,
        search: Optional[str] = None,
        difficulty_min: Optional[int] = None,
        difficulty_max: Optional[int] = None,
        source_oj: Optional[str] = None,
        tag_ids: Optional[List[UUID]] = None,
        page: int = 1,
        page_size: int = 20
    ) -> Tuple[List[Problem], int]:
        """获取题目列表（支持筛选和分页）"""
        # 基础查询：只返回已发布的题目
        query = select(Problem).where(Problem.is_published == True)
        
        # 关键词搜索
        if search:
            search_term = f"%{search}%"
            query = query.where(
                or_(
                    Problem.title.ilike(search_term),
                    Problem.description.ilike(search_term)
                )
            )
        
        # 难度范围
        if difficulty_min is not None:
            query = query.where(Problem.difficulty >= difficulty_min)
        if difficulty_max is not None:
            query = query.where(Problem.difficulty <= difficulty_max)
        
        # 来源筛选
        if source_oj:
            query = query.where(Problem.source_oj == source_oj)
        
        # 标签筛选（AND 关系）
        if tag_ids:
            for tag_id in tag_ids:
                query = query.where(
                    Problem.tags.any(Tag.id == tag_id)
                )
        
        # 计算总数
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await db.execute(count_query)
        total = total_result.scalar()
        
        # 分页
        query = (
            query
            .options(selectinload(Problem.tags))
            .order_by(Problem.created_at.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
        
        result = await db.execute(query)
        items = result.scalars().all()
        
        return items, total
