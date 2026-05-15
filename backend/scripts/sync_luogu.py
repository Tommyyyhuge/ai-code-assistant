"""
洛谷题目同步脚本

从洛谷开放 API 拉取题目数据并导入本地数据库。
运行方式: python -m scripts.sync_luogu
"""

import asyncio
import sys
import os

# 允许从项目根目录运行
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import httpx
from sqlalchemy import select
from app.database import AsyncSessionLocal
from app.models.problem import Problem
from app.utils.security import slugify


LUOGU_API_BASE = "https://www.luogu.com.cn/problem/list"
DIFFICULTY_MAP = {
    "入门": 1,
    "普及-": 2,
    "普及/提高-": 3,
    "普及+/提高": 4,
    "提高+/省选-": 5,
    "省选/NOI-": 6,
    "NOI/NOI+/CTSC": 7,
}


def luogu_difficulty_to_int(raw: str) -> int:
    for key, val in DIFFICULTY_MAP.items():
        if key in raw:
            return val
    return 3  # 默认中等


def fetch_problem_list(page: int = 1, keyword: str = "") -> list[dict]:
    """从洛谷 API 拉取题目列表"""
    # 使用洛谷的公开接口（非官方 API，可能随网站改版变化）
    url = f"{LUOGU_API_BASE}?page={page}&keyword={keyword}"
    with httpx.Client(timeout=30) as client:
        resp = client.get(url, headers={"User-Agent": "AI-Code-Assistant/1.0"})
        resp.raise_for_status()
        data = resp.json()
    return data.get("problems", {}).get("result", [])


async def sync_problems():
    """同步洛谷题目到数据库"""
    async with AsyncSessionLocal() as db:
        synced = 0
        for page in range(1, 6):  # 最多 5 页
            try:
                problems = fetch_problem_list(page)
            except Exception as e:
                print(f"[WARN] 第 {page} 页拉取失败: {e}")
                continue

            for item in problems:
                pid = item.get("pid", "")
                title = item.get("title", pid)
                title_slug = slugify(f"luogu-{pid}")

                # 检查是否已存在
                existing = await db.execute(
                    select(Problem).where(Problem.source_oj == "luogu").where(
                        Problem.source_problem_id == pid
                    )
                )
                if existing.scalar_one_or_none():
                    continue

                problem = Problem(
                    title=title,
                    title_slug=title_slug,
                    description=item.get("description", "（洛谷题目，请前往原站查看完整描述）"),
                    input_format="标准输入",
                    output_format="标准输出",
                    difficulty=luogu_difficulty_to_int(item.get("difficulty", "普及-")),
                    source_oj="luogu",
                    source_problem_id=pid,
                    source_url=f"https://www.luogu.com.cn/problem/{pid}",
                    is_published=True,
                    time_limit_ms=item.get("timeLimit", 1000),
                    memory_limit_mb=item.get("memoryLimit", 256),
                )
                db.add(problem)
                synced += 1

            await db.commit()
            print(f"[OK] 第 {page} 页同步完成，累计 {synced} 道题目")

    print(f"[DONE] 洛谷同步完成，共导入 {synced} 道新题目")


if __name__ == "__main__":
    asyncio.run(sync_problems())
