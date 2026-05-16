from typing import Optional
from uuid import UUID
from datetime import datetime
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.learning_path import LearningPath, LearningPathNode, LearningPathProgress
from app.models.knowledge import KnowledgeNode, UserProgress as KnowledgeUserProgress
from app.schemas.learning_path import LearningPathBrief, PathNodeItem, LearningPathDetail, EnrollResponse


class LearningPathService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def list_paths(self, user_id: Optional[UUID] = None) -> list[LearningPathBrief]:
        result = await self.db.execute(
            select(LearningPath).where(LearningPath.is_published == True).order_by(LearningPath.category)
        )
        paths = result.scalars().all()

        # 节点计数
        node_counts = {}
        if paths:
            path_ids = [p.id for p in paths]
            count_result = await self.db.execute(
                select(LearningPathNode.path_id)
                .where(LearningPathNode.path_id.in_(path_ids))
            )
            for row in count_result.all():
                pid = row[0]
                node_counts[pid] = node_counts.get(pid, 0) + 1

        # 用户进度
        user_progress_map = {}
        if user_id and paths:
            progress_result = await self.db.execute(
                select(LearningPathProgress).where(
                    LearningPathProgress.user_id == user_id,
                    LearningPathProgress.path_id.in_(path_ids),
                )
            )
            for p in progress_result.scalars().all():
                user_progress_map[p.path_id] = p

        briefs = []
        for path in paths:
            nc = node_counts.get(path.id, 0)
            up = user_progress_map.get(path.id)
            brief = LearningPathBrief(
                id=path.id,
                title=path.title,
                title_slug=path.title_slug,
                category=path.category,
                description=path.description,
                estimated_days=path.estimated_days,
                node_count=nc,
                user_status=up.status if up else "not_started",
                user_progress_pct=int(up.completed_nodes / up.total_nodes * 100) if up and up.total_nodes > 0 else 0,
            )
            briefs.append(brief)
        return briefs

    async def get_path_detail(self, slug: str, user_id: Optional[UUID] = None) -> Optional[LearningPathDetail]:
        result = await self.db.execute(
            select(LearningPath).where(LearningPath.title_slug == slug)
        )
        path = result.scalar_one_or_none()
        if not path:
            return None

        # 节点列表
        node_result = await self.db.execute(
            select(LearningPathNode, KnowledgeNode)
            .join(KnowledgeNode, LearningPathNode.knowledge_node_id == KnowledgeNode.id)
            .where(LearningPathNode.path_id == path.id)
            .order_by(LearningPathNode.order_index)
        )
        rows = node_result.all()

        # 用户各节点进度
        node_progress_map = {}
        if user_id:
            node_ids = [n.id for _, n in rows]
            if node_ids:
                p_result = await self.db.execute(
                    select(KnowledgeUserProgress).where(
                        KnowledgeUserProgress.user_id == user_id,
                        KnowledgeUserProgress.knowledge_node_id.in_(node_ids),
                    )
                )
                for p in p_result.scalars().all():
                    node_progress_map[p.knowledge_node_id] = p.status

        nodes = [
            PathNodeItem(
                id=pn.id,
                knowledge_node_id=kn.id,
                title=kn.title,
                title_slug=kn.title_slug,
                category=kn.category,
                level=kn.level,
                order_index=pn.order_index,
                is_required=pn.is_required,
                user_status=node_progress_map.get(kn.id, "not_started"),
            )
            for pn, kn in rows
        ]

        # 计算总进度
        completed = sum(1 for n in nodes if n.user_status == "completed")
        total = len(nodes)

        progress = None
        if user_id:
            p_result = await self.db.execute(
                select(LearningPathProgress).where(
                    LearningPathProgress.user_id == user_id,
                    LearningPathProgress.path_id == path.id,
                )
            )
            progress = p_result.scalar_one_or_none()

        brief = LearningPathBrief(
            id=path.id,
            title=path.title,
            title_slug=path.title_slug,
            category=path.category,
            description=path.description,
            estimated_days=path.estimated_days,
            node_count=total,
            user_status=progress.status if progress else "not_started",
            user_progress_pct=int(completed / total * 100) if total > 0 else 0,
        )

        return LearningPathDetail(path=brief, nodes=nodes)

    async def enroll(self, user_id: UUID, path_slug: str) -> EnrollResponse:
        path_result = await self.db.execute(
            select(LearningPath).where(LearningPath.title_slug == path_slug)
        )
        path = path_result.scalar_one_or_none()
        if not path:
            raise ValueError("Path not found")

        # 节点总数
        count_result = await self.db.execute(
            select(LearningPathNode).where(LearningPathNode.path_id == path.id)
        )
        total = len(count_result.scalars().all())

        # 幂等：已在则返回
        p_result = await self.db.execute(
            select(LearningPathProgress).where(
                LearningPathProgress.user_id == user_id,
                LearningPathProgress.path_id == path.id,
            )
        )
        progress = p_result.scalar_one_or_none()

        if not progress:
            progress = LearningPathProgress(
                user_id=user_id,
                path_id=path.id,
                status="in_progress",
                total_nodes=total,
                started_at=datetime.utcnow(),
            )
            self.db.add(progress)
            await self.db.commit()
            await self.db.refresh(progress)

        return EnrollResponse(path_id=path.id, status=progress.status, total_nodes=total)
