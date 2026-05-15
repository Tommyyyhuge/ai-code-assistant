from typing import List, Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.tag import Tag
from app.schemas.tag import TagCreate, TagUpdate


class TagService:
    @staticmethod
    async def get_tags(
        db: AsyncSession,
        category: Optional[str] = None
    ) -> List[Tag]:
        query = select(Tag)
        if category:
            query = query.where(Tag.category == category)
        query = query.order_by(Tag.name)
        result = await db.execute(query)
        return result.scalars().all()
    
    @staticmethod
    async def get_tag(db: AsyncSession, tag_id: UUID) -> Optional[Tag]:
        result = await db.execute(
            select(Tag).where(Tag.id == tag_id)
        )
        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_tags_by_ids(db: AsyncSession, tag_ids: List[UUID]) -> List[Tag]:
        if not tag_ids:
            return []
        result = await db.execute(
            select(Tag).where(Tag.id.in_(tag_ids))
        )
        return result.scalars().all()
    
    @staticmethod
    async def create_tag(db: AsyncSession, data: TagCreate) -> Tag:
        from app.utils.security import slugify
        
        tag = Tag(
            name=data.name,
            name_slug=slugify(data.name),
            category=data.category,
            description=data.description,
            color=data.color,
            is_lanqiao_special=data.is_lanqiao_special,
            parent_id=data.parent_id
        )
        db.add(tag)
        await db.flush()
        await db.refresh(tag)
        return tag
    
    @staticmethod
    async def update_tag(db: AsyncSession, tag_id: UUID, data: TagUpdate) -> Optional[Tag]:
        tag = await TagService.get_tag(db, tag_id)
        if not tag:
            return None
        
        update_data = data.model_dump(exclude_unset=True)
        if "name" in update_data:
            from app.utils.security import slugify
            update_data["name_slug"] = slugify(update_data["name"])
        
        for field, value in update_data.items():
            setattr(tag, field, value)
        
        await db.flush()
        await db.refresh(tag)
        return tag
    
    @staticmethod
    async def delete_tag(db: AsyncSession, tag_id: UUID) -> bool:
        tag = await TagService.get_tag(db, tag_id)
        if not tag:
            return False
        await db.delete(tag)
        await db.flush()
        return True
