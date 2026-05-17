import uuid
from datetime import datetime
from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.knowledge import KnowledgeNode, KnowledgeEdge, KnowledgeProblemAssociation, UserProgress
from app.models.problem import Problem
from app.schemas.knowledge import (
    KnowledgeNodeTreeItem, KnowledgeNodeDetailResponse, KnowledgeNodeDetail,
    KnowledgeNodeNeighbor, ProblemAssociationItem, UserProgressResponse,
    UserProgressSummary, UserProgressItem,
)


class KnowledgeService:
    def __init__(self, db: AsyncSession):
        self.db = db

    # ── 树构建 ──

    async def get_tree(self, user_id: Optional[uuid.UUID] = None, category: Optional[str] = None) -> list[KnowledgeNodeTreeItem]:
        import uuid as _uuid  # for uuid5
        query = select(KnowledgeNode).where(KnowledgeNode.is_published == True)
        if category:
            query = query.where(KnowledgeNode.category == category)
        query = query.order_by(KnowledgeNode.category, KnowledgeNode.path)

        result = await self.db.execute(query)
        nodes = result.scalars().all()

        user_progress_map: dict = {}
        if user_id:
            progress_result = await self.db.execute(
                select(UserProgress).where(UserProgress.user_id == user_id)
            )
            for p in progress_result.scalars().all():
                user_progress_map[p.knowledge_node_id] = p.status

        id_map = {
            str(n.id): KnowledgeNodeTreeItem(
                id=n.id, title=n.title, title_slug=n.title_slug,
                category=n.category, level=n.level, order_index=n.order_index,
                user_status=user_progress_map.get(n.id, "not_started"),
                children=[]
            )
            for n in nodes
        }

        roots: list[KnowledgeNodeTreeItem] = []
        path_to_node = {n.path: str(n.id) for n in nodes}

        # 虚拟根节点：当父级路径段没有对应节点时，按 category 分组
        virtual_roots: dict[str, KnowledgeNodeTreeItem] = {}

        for node in nodes:
            item = id_map[str(node.id)]
            path_parts = node.path.split(".")

            if len(path_parts) == 1:
                # 本身就是根节点
                roots.append(item)
                # 如果这个根节点之前是虚拟的，用真实节点替换
                if node.path in virtual_roots:
                    item.children = virtual_roots[node.path].children
                    virtual_roots.pop(node.path)
            else:
                # 有父节点，尝试找真实父节点
                parent_path = ".".join(path_parts[:-1])
                parent_id = path_to_node.get(parent_path)

                if parent_id and parent_id in id_map:
                    id_map[parent_id].children.append(item)
                else:
                    # 父节点不存在，创建虚拟分组节点
                    if parent_path not in virtual_roots:
                        cat_title = parent_path.replace("_", " ").title()
                        virtual_roots[parent_path] = KnowledgeNodeTreeItem(
                            id=_uuid.uuid5(_uuid.NAMESPACE_DNS, f"knowledge:{parent_path}"),
                            title=cat_title,
                            title_slug=parent_path,
                            category=node.category,
                            level=node.level,
                            order_index=0,
                            user_status="not_started",
                            children=[],
                        )
                    virtual_roots[parent_path].children.append(item)

        # 合并虚拟根节点
        for vr in virtual_roots.values():
            vr.children.sort(key=lambda c: c.order_index)
            roots.append(vr)

        roots.sort(key=lambda r: r.order_index)

        for item in id_map.values():
            item.children.sort(key=lambda c: c.order_index)

        return roots

    # ── 节点详情 ──

    async def get_node_detail(
        self, slug: str, user_id: Optional[uuid.UUID] = None
    ) -> Optional[KnowledgeNodeDetailResponse]:
        result = await self.db.execute(
            select(KnowledgeNode).where(KnowledgeNode.title_slug == slug)
        )
        node = result.scalar_one_or_none()
        if not node:
            return None

        prerequisites = await self._get_neighbors(node.id, "prerequisite")
        next_nodes = await self._get_neighbors(node.id, "next", reverse=True)
        related = await self._get_neighbors(node.id, "related")
        related += await self._get_neighbors(node.id, "related", reverse=True)

        problems = await self._get_problems(node.id)

        user_progress = None
        if user_id:
            p_result = await self.db.execute(
                select(UserProgress).where(
                    UserProgress.user_id == user_id,
                    UserProgress.knowledge_node_id == node.id,
                )
            )
            p = p_result.scalar_one_or_none()
            if p:
                user_progress = UserProgressResponse(
                    status=p.status,
                    practice_count=p.practice_count,
                    started_at=p.started_at,
                    completed_at=p.completed_at,
                )

        return KnowledgeNodeDetailResponse(
            node=KnowledgeNodeDetail.model_validate(node),
            prerequisites=prerequisites,
            next_nodes=next_nodes,
            related_nodes=related,
            problems=problems,
            user_progress=user_progress,
        )

    async def _get_neighbors(
        self, node_id: uuid.UUID, edge_type: str, reverse: bool = False
    ) -> list[KnowledgeNodeNeighbor]:
        if reverse:
            stmt = (
                select(KnowledgeEdge, KnowledgeNode)
                .join(KnowledgeNode, KnowledgeEdge.from_node_id == KnowledgeNode.id)
                .where(KnowledgeEdge.to_node_id == node_id, KnowledgeEdge.edge_type == edge_type)
            )
        else:
            stmt = (
                select(KnowledgeEdge, KnowledgeNode)
                .join(KnowledgeNode, KnowledgeEdge.to_node_id == KnowledgeNode.id)
                .where(KnowledgeEdge.from_node_id == node_id, KnowledgeEdge.edge_type == edge_type)
            )
        result = await self.db.execute(stmt)
        rows = result.all()
        return [
            KnowledgeNodeNeighbor(
                id=n.id, title=n.title, title_slug=n.title_slug, edge_type=edge.edge_type
            )
            for edge, n in rows
        ]

    async def _get_problems(self, node_id: uuid.UUID) -> list[ProblemAssociationItem]:
        result = await self.db.execute(
            select(KnowledgeProblemAssociation, Problem)
            .join(Problem, KnowledgeProblemAssociation.problem_id == Problem.id)
            .where(KnowledgeProblemAssociation.knowledge_node_id == node_id)
            .order_by(KnowledgeProblemAssociation.order_index)
        )
        rows = result.all()
        return [
            ProblemAssociationItem(
                problem_id=p.id,
                title=p.title,
                title_slug=p.title_slug,
                difficulty=p.difficulty,
                difficulty_level=assoc.difficulty_level,
                is_required=assoc.is_required,
            )
            for assoc, p in rows
        ]

    # ── 进度 ──

    async def upsert_progress(
        self, user_id: uuid.UUID, knowledge_node_id: uuid.UUID, status: str
    ) -> UserProgress:
        result = await self.db.execute(
            select(UserProgress).where(
                UserProgress.user_id == user_id,
                UserProgress.knowledge_node_id == knowledge_node_id,
            )
        )
        progress = result.scalar_one_or_none()

        now = datetime.utcnow()
        if progress:
            progress.status = status
            progress.updated_at = now
            if status == "in_progress" and not progress.started_at:
                progress.started_at = now
            if status == "completed":
                progress.completed_at = now
            progress.practice_count += 1
            progress.last_practiced_at = now
        else:
            progress = UserProgress(
                user_id=user_id,
                knowledge_node_id=knowledge_node_id,
                status=status,
                started_at=now if status == "in_progress" else None,
                completed_at=now if status == "completed" else None,
                practice_count=1,
                last_practiced_at=now,
            )
            self.db.add(progress)

        await self.db.commit()
        await self.db.refresh(progress)
        return progress

    async def get_user_progress_summary(self, user_id: uuid.UUID) -> UserProgressSummary:
        total_result = await self.db.execute(
            select(KnowledgeNode).where(KnowledgeNode.is_published == True)
        )
        total_nodes = len(total_result.scalars().all())

        result = await self.db.execute(
            select(UserProgress, KnowledgeNode)
            .join(KnowledgeNode, UserProgress.knowledge_node_id == KnowledgeNode.id)
            .where(UserProgress.user_id == user_id)
            .order_by(KnowledgeNode.category, KnowledgeNode.path)
        )
        rows = result.all()

        completed = sum(1 for p, _ in rows if p.status == "completed")
        in_progress = sum(1 for p, _ in rows if p.status == "in_progress")
        items = [
            UserProgressItem(
                node_id=p.knowledge_node_id,
                node_title=n.title,
                node_slug=n.title_slug,
                status=p.status,
                practice_count=p.practice_count,
            )
            for p, n in rows
        ]

        return UserProgressSummary(
            total_nodes=total_nodes,
            completed_nodes=completed,
            in_progress_nodes=in_progress,
            items=items,
        )
