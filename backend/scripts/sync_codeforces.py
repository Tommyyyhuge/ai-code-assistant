"""
Codeforces 题目同步脚本

从 Codeforces API 拉取题目数据并导入本地数据库。
运行方式: python -m scripts.sync_codeforces
"""

import asyncio
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import httpx
from sqlalchemy import select
from app.database import AsyncSessionLocal
from app.models.problem import Problem
from app.utils.security import slugify


CF_API_BASE = "https://codeforces.com/api"


def cf_rating_to_difficulty(rating: int) -> int:
    """将 Codeforces 难度分映射到 1-10"""
    if rating is None:
        return 3
    if rating <= 1000:
        return 1
    if rating <= 1300:
        return 2
    if rating <= 1600:
        return 3
    if rating <= 1900:
        return 4
    if rating <= 2200:
        return 5
    if rating <= 2500:
        return 6
    if rating <= 2800:
        return 7
    if rating <= 3100:
        return 8
    if rating <= 3400:
        return 9
    return 10


def cf_tags_to_string(tags: list[str]) -> str:
    if not tags:
        return ""
    return ", ".join(tags)


async def sync_problems():
    """同步 Codeforces 题目到数据库"""
    async with AsyncSessionLocal() as db:
        # 拉取题目列表
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.get(
                f"{CF_API_BASE}/problemset.problems",
                headers={"User-Agent": "AI-Code-Assistant/1.0"},
            )
            resp.raise_for_status()
            data = resp.json()

        if data["status"] != "OK":
            print(f"[ERROR] Codeforces API 返回异常: {data.get('comment')}")
            return

        problems = data["result"]["problems"]
        synced = 0

        for item in problems:
            contest_id = item.get("contestId")
            index = item.get("index", "")
            cf_id = f"{contest_id}{index}"
            title = f"{cf_id} - {item.get('name', cf_id)}"
            title_slug = slugify(f"cf-{cf_id}")

            # 检查是否已存在
            existing = await db.execute(
                select(Problem).where(Problem.source_oj == "codeforces").where(
                    Problem.source_problem_id == cf_id
                )
            )
            if existing.scalar_one_or_none():
                continue

            tags_str = cf_tags_to_string(item.get("tags", []))
            difficulty = cf_rating_to_difficulty(item.get("rating", 1200))

            problem = Problem(
                title=title,
                title_slug=title_slug,
                description=(
                    f"**来源**: [Codeforces {cf_id}](https://codeforces.com/problemset/problem/{contest_id}/{index})\n\n"
                    f"**标签**: {tags_str or '无'}\n\n"
                    f"（Codeforces 题目，请前往原站查看完整描述）"
                ),
                input_format="标准输入",
                output_format="标准输出",
                difficulty=difficulty,
                source_oj="codeforces",
                source_problem_id=cf_id,
                source_url=f"https://codeforces.com/problemset/problem/{contest_id}/{index}",
                is_published=True,
                # CF 默认: 1s / 256MB
                time_limit_ms=1000,
                memory_limit_mb=256,
            )
            db.add(problem)
            synced += 1

            # 每 100 道提交一次
            if synced % 100 == 0:
                await db.commit()
                print(f"[OK] 已处理 {synced} 道题目...")

        await db.commit()
        print(f"[DONE] Codeforces 同步完成，共导入 {synced} 道新题目")


if __name__ == "__main__":
    asyncio.run(sync_problems())
