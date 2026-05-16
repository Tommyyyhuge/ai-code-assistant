"""学习路径种子数据：5 条路线

运行: conda run -n ai_code_assistant_env python -m app.data_path_seed
"""
import asyncio
from app.database import AsyncSessionLocal
from sqlalchemy import text as sa_text

PATHS = [
    {
        "title_slug": "oi-junior",
        "title": "OI 入门路线 (CSP-J)",
        "category": "oi_junior",
        "description": "面向小学/初中竞赛入门，从零开始掌握基础算法和数据结构",
        "estimated_days": 30,
        "node_slugs": [
            "time-complexity", "recursion-divide-conquer", "stack-queue",
            "linked-list", "binary-tree", "bubble-sort", "selection-sort",
            "insertion-sort", "binary-search", "greedy-intro",
        ],
    },
    {
        "title_slug": "oi-senior",
        "title": "OI 提高路线 (CSP-S/NOIP)",
        "category": "oi_senior",
        "description": "面向高中竞赛进阶，覆盖核心算法和数据结构",
        "estimated_days": 45,
        "node_slugs": [
            "quick-sort", "merge-sort", "dfs", "bfs", "hash-table",
            "dp-intro", "knapsack", "lcs", "interval-scheduling", "dijkstra",
        ],
    },
    {
        "title_slug": "lanqiao",
        "title": "蓝桥杯备赛路线",
        "category": "lanqiao",
        "description": "蓝桥杯省赛核心考点全覆盖",
        "estimated_days": 35,
        "node_slugs": [
            "time-complexity", "recursion-divide-conquer", "bubble-sort",
            "selection-sort", "insertion-sort", "binary-search", "stack-queue",
            "linked-list", "dfs", "bfs", "dp-intro", "greedy-intro",
        ],
    },
    {
        "title_slug": "self-study",
        "title": "零基础自学路线",
        "category": "self_study",
        "description": "从零开始系统学习算法，适合没有任何算法基础的初学者",
        "estimated_days": 60,
        "node_slugs": [
            "time-complexity", "recursion-divide-conquer", "stack-queue",
            "linked-list", "binary-tree", "hash-table", "bubble-sort",
            "selection-sort", "insertion-sort", "quick-sort", "merge-sort",
            "binary-search", "dfs", "bfs", "dp-intro", "knapsack", "lcs",
            "greedy-intro", "interval-scheduling", "dijkstra",
        ],
    },
    {
        "title_slug": "acm-icpc",
        "title": "ACM-ICPC 训练路线",
        "category": "acm",
        "description": "高强度竞赛训练路线，适合有基础的学生冲击区域赛",
        "estimated_days": 60,
        "node_slugs": [
            "quick-sort", "merge-sort", "binary-search", "dfs", "bfs",
            "binary-tree", "hash-table", "dp-intro", "knapsack", "lcs",
            "greedy-intro", "interval-scheduling", "dijkstra",
        ],
    },
]


async def seed():
    from sqlalchemy import text as _text

    async with AsyncSessionLocal() as db:
        # 清空已有数据
        await db.execute(_text("DELETE FROM learning_path_progress"))
        await db.execute(_text("DELETE FROM learning_path_nodes"))
        await db.execute(_text("DELETE FROM learning_paths"))
        await db.commit()

        for path_data in PATHS:
            node_slugs = path_data.pop("node_slugs")

            # 插入路径
            result = await db.execute(
                _text(
                    "INSERT INTO learning_paths (id, title, title_slug, description, category, estimated_days, is_published) "
                    "VALUES (gen_random_uuid(), :title, :title_slug, :description, :category, :estimated_days, true) "
                    "RETURNING id"
                ),
                path_data,
            )
            path_id = result.scalar_one()

            # 查询知识点 ID
            slug_list = ", ".join(f"'{s}'" for s in node_slugs)
            node_result = await db.execute(
                _text(
                    f"SELECT id, title_slug FROM knowledge_nodes WHERE title_slug IN ({slug_list})"
                )
            )
            node_map = {row[1]: row[0] for row in node_result.all()}

            # 按顺序插入节点
            for idx, slug in enumerate(node_slugs):
                if slug in node_map:
                    await db.execute(
                        _text(
                            "INSERT INTO learning_path_nodes (id, path_id, knowledge_node_id, order_index, is_required) "
                            "VALUES (gen_random_uuid(), :path_id, :node_id, :order_index, true)"
                        ),
                        {"path_id": path_id, "node_id": node_map[slug], "order_index": idx + 1},
                    )

            print(f"  路线: {path_data['title_slug']} ({len(node_map)}/{len(node_slugs)} nodes)")

        await db.commit()
        print(f"[DONE] {len(PATHS)} 条学习路线导入完成")


if __name__ == "__main__":
    asyncio.run(seed())
