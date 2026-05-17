"""
题目种子数据：10 道经典算法题（含标签、测试用例、知识点关联）

运行: conda activate ai_code_assistant_env && python -m app.data_problem_seed
"""
import asyncio
from app.database import AsyncSessionLocal
from sqlalchemy import text as sa_text


# ── 标签 ────────────────────────────────────────────────────────
SEED_TAGS = [
    {"name": "入门", "name_slug": "intro", "category": "difficulty", "color": "#22c55e"},
    {"name": "基础", "name_slug": "basic", "category": "difficulty", "color": "#3b82f6"},
    {"name": "算法", "name_slug": "algorithm", "category": "difficulty", "color": "#f59e0b"},
    {"name": "动态规划", "name_slug": "dp", "category": "topic", "color": "#ef4444"},
    {"name": "数学", "name_slug": "math", "category": "topic", "color": "#8b5cf6"},
    {"name": "搜索", "name_slug": "search", "category": "topic", "color": "#06b6d4"},
    {"name": "字符串", "name_slug": "string", "category": "topic", "color": "#ec4899"},
    {"name": "排序", "name_slug": "sorting", "category": "topic", "color": "#f97316"},
    {"name": "递归", "name_slug": "recursion", "category": "topic", "color": "#14b8a6"},
    {"name": "蓝桥杯真题", "name_slug": "lanqiao", "category": "source", "color": "#6366f1", "is_lanqiao_special": True},
]


# ── 题目 ─────────────────────────────────────────────────────────
SEED_PROBLEMS = [
    {
        "title": "A + B 问题",
        "title_slug": "a-plus-b",
        "difficulty": 1,
        "time_limit_ms": 1000,
        "memory_limit_mb": 128,
        "tag_slugs": ["intro", "math"],
        "knowledge_slugs": ["time-complexity"],
        "description": (
            "输入两个整数 A 和 B，输出它们的和。\n\n"
            "这是算法竞赛的入门题，帮助你熟悉输入输出格式。"
        ),
        "input_format": "一行，包含两个整数 A 和 B（-1000 ≤ A, B ≤ 1000），用空格分隔。",
        "output_format": "一个整数，表示 A + B 的结果。",
        "constraints": "-1000 ≤ A, B ≤ 1000",
        "test_cases": [
            {"input": "1 2", "output": "3", "is_sample": True},
            {"input": "100 200", "output": "300", "is_sample": False},
            {"input": "-5 10", "output": "5", "is_sample": False},
            {"input": "0 0", "output": "0", "is_sample": False},
            {"input": "-999 1000", "output": "1", "is_sample": False},
        ],
    },
    {
        "title": "斐波那契数列",
        "title_slug": "fibonacci",
        "difficulty": 2,
        "time_limit_ms": 1000,
        "memory_limit_mb": 128,
        "tag_slugs": ["basic", "math", "recursion"],
        "knowledge_slugs": ["recursion-divide-conquer"],
        "description": (
            "斐波那契数列的定义如下：\n"
            "- F(1) = F(2) = 1\n"
            "- F(n) = F(n-1) + F(n-2)，当 n > 2\n\n"
            "给定正整数 n，求 F(n) 的值。"
        ),
        "input_format": "一行，一个正整数 n（1 ≤ n ≤ 45）。",
        "output_format": "一个整数，表示 F(n) 的值。",
        "constraints": "1 ≤ n ≤ 45",
        "test_cases": [
            {"input": "1", "output": "1", "is_sample": True},
            {"input": "10", "output": "55", "is_sample": True},
            {"input": "20", "output": "6765", "is_sample": False},
            {"input": "30", "output": "832040", "is_sample": False},
            {"input": "45", "output": "1134903170", "is_sample": False},
        ],
    },
    {
        "title": "判断素数",
        "title_slug": "is-prime",
        "difficulty": 2,
        "time_limit_ms": 1000,
        "memory_limit_mb": 128,
        "tag_slugs": ["basic", "math"],
        "knowledge_slugs": ["time-complexity"],
        "description": (
            "素数是指大于 1 的自然数中，除了 1 和它本身以外不再有其他因数的数。\n\n"
            "给定一个整数 n，判断它是否为素数。"
        ),
        "input_format": "一行，一个整数 n（2 ≤ n ≤ 10⁹）。",
        "output_format": '如果是素数输出 "Yes"，否则输出 "No"。',
        "constraints": "2 ≤ n ≤ 10⁹",
        "test_cases": [
            {"input": "2", "output": "Yes", "is_sample": True},
            {"input": "17", "output": "Yes", "is_sample": True},
            {"input": "100", "output": "No", "is_sample": False},
            {"input": "999999937", "output": "Yes", "is_sample": False},
            {"input": "1", "output": "No", "is_sample": False},
        ],
    },
    {
        "title": "最大公约数",
        "title_slug": "gcd",
        "difficulty": 2,
        "time_limit_ms": 1000,
        "memory_limit_mb": 128,
        "tag_slugs": ["basic", "math", "recursion"],
        "knowledge_slugs": ["recursion-divide-conquer"],
        "description": (
            "给定两个正整数 a 和 b，求它们的最大公约数（GCD）。\n\n"
            "提示：可以使用欧几里得算法（辗转相除法）。"
        ),
        "input_format": "一行，两个正整数 a 和 b（1 ≤ a, b ≤ 10⁹），用空格分隔。",
        "output_format": "一个整数，表示 a 和 b 的最大公约数。",
        "constraints": "1 ≤ a, b ≤ 10⁹",
        "test_cases": [
            {"input": "12 18", "output": "6", "is_sample": True},
            {"input": "17 23", "output": "1", "is_sample": False},
            {"input": "100 100", "output": "100", "is_sample": False},
            {"input": "1071 462", "output": "21", "is_sample": False},
            {"input": "999999937 1000000000", "output": "1", "is_sample": False},
        ],
    },
    {
        "title": "回文串判断",
        "title_slug": "palindrome",
        "difficulty": 3,
        "time_limit_ms": 1000,
        "memory_limit_mb": 128,
        "tag_slugs": ["algorithm", "string"],
        "knowledge_slugs": ["time-complexity"],
        "description": (
            "回文串是指正着读和反着读都一样的字符串。\n\n"
            "给定一个由小写字母组成的字符串 s，判断它是否为回文串。"
        ),
        "input_format": "一行，一个由小写字母组成的字符串 s（1 ≤ |s| ≤ 1000）。",
        "output_format": '如果是回文串输出 "Yes"，否则输出 "No"。',
        "constraints": "1 ≤ |s| ≤ 1000，仅包含小写字母",
        "test_cases": [
            {"input": "aba", "output": "Yes", "is_sample": True},
            {"input": "abcba", "output": "Yes", "is_sample": True},
            {"input": "abcd", "output": "No", "is_sample": False},
            {"input": "a", "output": "Yes", "is_sample": False},
            {"input": "aaaaaa", "output": "Yes", "is_sample": False},
        ],
    },
    {
        "title": "二分查找",
        "title_slug": "binary-search-problem",
        "difficulty": 3,
        "time_limit_ms": 1000,
        "memory_limit_mb": 128,
        "tag_slugs": ["algorithm", "search"],
        "knowledge_slugs": ["binary-search"],
        "description": (
            "给定一个严格递增的正整数数列 a₁, a₂, ..., aₙ 和一个目标值 x。\n"
            "请判断 x 是否在数列中出现。如果出现，输出其下标（1-based）；否则输出 -1。\n\n"
            "要求使用 O(log n) 的二分查找算法。"
        ),
        "input_format": (
            "第一行一个整数 n（1 ≤ n ≤ 10⁵），表示数列长度。\n"
            "第二行 n 个严格递增的整数 a₁ a₂ ... aₙ（-10⁹ ≤ aᵢ ≤ 10⁹）。\n"
            "第三行一个整数 x（-10⁹ ≤ x ≤ 10⁹），表示目标值。"
        ),
        "output_format": "一个整数，表示 x 在数列中的位置（1-based），若未找到则输出 -1。",
        "constraints": "1 ≤ n ≤ 10⁵，数列严格递增",
        "test_cases": [
            {"input": "5\n1 3 5 7 9\n5", "output": "3", "is_sample": True},
            {"input": "5\n1 3 5 7 9\n6", "output": "-1", "is_sample": True},
            {"input": "3\n-5 0 100\n100", "output": "3", "is_sample": False},
            {"input": "3\n-5 0 100\n-10", "output": "-1", "is_sample": False},
            {"input": "1\n42\n42", "output": "1", "is_sample": False},
        ],
    },
    {
        "title": "快速幂",
        "title_slug": "fast-pow",
        "difficulty": 4,
        "time_limit_ms": 1000,
        "memory_limit_mb": 128,
        "tag_slugs": ["algorithm", "math", "recursion"],
        "knowledge_slugs": ["recursion-divide-conquer"],
        "description": (
            "计算 a 的 b 次方对 mod 取模的结果，即 (aᵇ) mod m。\n\n"
            "由于结果可能很大，要求使用快速幂算法（O(log b)）。\n"
            "注意：请使用 64 位整数（C++ 的 long long，Python 的 int）。"
        ),
        "input_format": "一行，三个整数 a、b、m（1 ≤ a ≤ 10⁹，0 ≤ b ≤ 10⁹，1 ≤ m ≤ 10⁹），用空格分隔。",
        "output_format": "一个整数，表示 (aᵇ) mod m 的结果。",
        "constraints": "1 ≤ a ≤ 10⁹，0 ≤ b ≤ 10⁹，1 ≤ m ≤ 10⁹",
        "test_cases": [
            {"input": "2 10 1000", "output": "24", "is_sample": True},
            {"input": "3 5 100", "output": "43", "is_sample": True},
            {"input": "5 0 7", "output": "1", "is_sample": False},
            {"input": "123456789 1 1000000007", "output": "123456789", "is_sample": False},
            {"input": "2 1000000000 1000000007", "output": "140625001", "is_sample": False},
        ],
    },
    {
        "title": "全排列",
        "title_slug": "permutations",
        "difficulty": 4,
        "time_limit_ms": 1000,
        "memory_limit_mb": 256,
        "tag_slugs": ["algorithm", "search", "recursion"],
        "knowledge_slugs": ["dfs", "recursion-divide-conquer"],
        "description": (
            "给定一个整数 n，按字典序输出 1 到 n 的所有全排列，每行一个排列（数字用空格分隔）。\n\n"
            "提示：可以使用 DFS（深度优先搜索）或递归回溯。"
        ),
        "input_format": "一行，一个整数 n（1 ≤ n ≤ 8）。",
        "output_format": "按字典序输出所有全排列，每个排列一行，数字用空格分隔。",
        "constraints": "1 ≤ n ≤ 8",
        "test_cases": [
            {"input": "3", "output": "1 2 3\n1 3 2\n2 1 3\n2 3 1\n3 1 2\n3 2 1", "is_sample": True},
            {"input": "2", "output": "1 2\n2 1", "is_sample": False},
            {"input": "1", "output": "1", "is_sample": False},
        ],
    },
    {
        "title": "0-1 背包问题",
        "title_slug": "knapsack-01",
        "difficulty": 5,
        "time_limit_ms": 1000,
        "memory_limit_mb": 256,
        "tag_slugs": ["algorithm", "dp"],
        "knowledge_slugs": ["knapsack", "dp-intro"],
        "description": (
            "有 N 件物品和一个容量为 W 的背包。第 i 件物品的重量是 wᵢ，价值是 vᵢ。\n"
            "每件物品只能选择拿或不拿。求在不超过背包容量的前提下，能获得的最大总价值。\n\n"
            "提示：使用动态规划，定义 dp[i][j] 为前 i 件物品在容量 j 下的最大价值。"
        ),
        "input_format": (
            "第一行两个整数 N 和 W（1 ≤ N ≤ 100，1 ≤ W ≤ 1000）。\n"
            "接下来 N 行，每行两个整数 wᵢ 和 vᵢ（1 ≤ wᵢ, vᵢ ≤ 1000）。"
        ),
        "output_format": "一个整数，表示能获得的最大总价值。",
        "constraints": "1 ≤ N ≤ 100，1 ≤ W ≤ 1000",
        "test_cases": [
            {"input": "4 10\n2 3\n3 4\n4 5\n5 8", "output": "12", "is_sample": True},
            {"input": "3 50\n10 60\n20 100\n30 120", "output": "220", "is_sample": True},
            {"input": "1 5\n10 100", "output": "0", "is_sample": False},
            {"input": "2 5\n2 3\n3 4", "output": "7", "is_sample": False},
        ],
    },
    {
        "title": "最长公共子序列",
        "title_slug": "lcs-problem",
        "difficulty": 5,
        "time_limit_ms": 1000,
        "memory_limit_mb": 256,
        "tag_slugs": ["algorithm", "dp", "string"],
        "knowledge_slugs": ["lcs", "dp-intro"],
        "description": (
            "给定两个由小写字母组成的字符串 s 和 t，求它们的最长公共子序列（LCS）的长度。\n\n"
            "子序列是指不要求连续，但保持原顺序的字符序列。\n"
            "提示：定义 dp[i][j] 为 s 的前 i 个字符和 t 的前 j 个字符的 LCS 长度。"
        ),
        "input_format": "两行，每行一个由小写字母组成的字符串。",
        "output_format": "一个整数，表示 LCS 的长度。",
        "constraints": "1 ≤ |s|, |t| ≤ 500",
        "test_cases": [
            {"input": "abcde\nace", "output": "3", "is_sample": True},
            {"input": "abc\nabc", "output": "3", "is_sample": True},
            {"input": "abc\ndef", "output": "0", "is_sample": False},
            {"input": "aaaaa\naa", "output": "2", "is_sample": False},
            {"input": "aggtab\ngxtxayb", "output": "4", "is_sample": False},
        ],
    },
]


async def seed():
    async with AsyncSessionLocal() as db:
        # ── 检查是否已导入（按第一道题的 slug 判断）──
        first_slug = SEED_PROBLEMS[0]["title_slug"]
        result = await db.execute(
            sa_text("SELECT COUNT(*) FROM problems WHERE title_slug = :slug"),
            {"slug": first_slug},
        )
        if result.scalar() > 0:
            print("种子题目已存在，跳过导入")
            return

        # ── 插入标签（跳过已存在的）──
        tag_slug_to_id = {}
        for tag in SEED_TAGS:
            # 先查是否已存在（按 slug 或 name）
            exist = await db.execute(
                sa_text("SELECT id, name_slug FROM tags WHERE name_slug = :slug OR name = :name"),
                {"slug": tag["name_slug"], "name": tag["name"]},
            )
            row = exist.fetchone()
            if row:
                tag_slug_to_id[tag["name_slug"]] = row[0]
                # 如果 slug 不同，记录实际 slug
                print(f"  标签已存在: {tag['name']} (slug={row[1]})")
                continue

            is_lanqiao = tag.get("is_lanqiao_special", False)
            result = await db.execute(
                sa_text(
                    "INSERT INTO tags (id, name, name_slug, category, color, is_lanqiao_special) "
                    "VALUES (gen_random_uuid(), :name, :name_slug, :category, :color, :is_lanqiao) "
                    "RETURNING id"
                ),
                {**tag, "is_lanqiao": is_lanqiao},
            )
            tag_slug_to_id[tag["name_slug"]] = result.scalar_one()
        await db.commit()
        print(f"导入 {len(SEED_TAGS)} 个标签（{len(tag_slug_to_id)} 个有效）")

        # ── 查知识点 ID ──
        knowledge_result = await db.execute(
            sa_text("SELECT title_slug, id FROM knowledge_nodes")
        )
        knowledge_slug_to_id = {row[0]: row[1] for row in knowledge_result.all()}

        # ── 插入题目 + 测试用例 + 关联 ──
        for prob in SEED_PROBLEMS:
            # 插入题目
            prob_result = await db.execute(
                sa_text(
                    "INSERT INTO problems (id, title, title_slug, description, input_format, output_format, "
                    "constraints, difficulty, time_limit_ms, memory_limit_mb, is_published) "
                    "VALUES (gen_random_uuid(), :title, :title_slug, :description, :input_format, :output_format, "
                    ":constraints, :difficulty, :time_limit_ms, :memory_limit_mb, true) "
                    "ON CONFLICT (title_slug) DO NOTHING "
                    "RETURNING id"
                ),
                {k: v for k, v in prob.items() if k not in ("tag_slugs", "knowledge_slugs", "test_cases")},
            )
            row = prob_result.fetchone()
            if not row:
                print(f"  跳过已存在: {prob['title']}")
                continue
            problem_id = row[0]

            # 关联标签
            for slug in prob["tag_slugs"]:
                if slug in tag_slug_to_id:
                    await db.execute(
                        sa_text(
                            "INSERT INTO problem_tag_associations (problem_id, tag_id, is_primary) "
                            "VALUES (:pid, :tid, :is_primary) "
                            "ON CONFLICT DO NOTHING"
                        ),
                        {"pid": problem_id, "tid": tag_slug_to_id[slug], "is_primary": slug == prob["tag_slugs"][0]},
                    )

            # 插入测试用例
            for idx, tc in enumerate(prob["test_cases"]):
                await db.execute(
                    sa_text(
                        "INSERT INTO test_cases (id, problem_id, input_data, expected_output, is_sample, order_index) "
                        "VALUES (gen_random_uuid(), :pid, :input, :output, :is_sample, :order_index)"
                    ),
                    {
                        "pid": problem_id,
                        "input": tc["input"],
                        "output": tc["output"],
                        "is_sample": tc.get("is_sample", False),
                        "order_index": idx,
                    },
                )

            print(f"  [OK] {prob['title']} ({len(prob['test_cases'])} 组测试)")

        await db.commit()
        print(f"\n[DONE] {len(SEED_PROBLEMS)} 道题目导入完成")


if __name__ == "__main__":
    asyncio.run(seed())
