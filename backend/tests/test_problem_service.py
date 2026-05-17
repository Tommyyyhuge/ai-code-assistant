"""ProblemService 单元测试 — 使用 AsyncMock 模拟数据库"""
import uuid
from unittest.mock import AsyncMock, MagicMock

import pytest
from app.models.problem import Problem
from app.services.problem_service import ProblemService


def _make_result(scalar_return=None, scalars_return=None):
    """创建模拟的 SQLAlchemy result proxy"""
    result = MagicMock()
    if scalar_return is not None:
        result.scalar.return_value = scalar_return
    if scalars_return is not None:
        result.scalars.return_value.all.return_value = scalars_return
    result.scalar_one_or_none.return_value = scalar_return
    return result


def _set_execute_return(mock_db, result):
    """让 mock_db.execute 在 await 后返回 result"""
    async def _side_effect(*args, **kwargs):
        return result
    mock_db.execute.side_effect = _side_effect


@pytest.fixture
def mock_db():
    """模拟异步数据库会话"""
    return AsyncMock()


@pytest.fixture
def sample_problem():
    """创建一个示例题目对象"""
    p = MagicMock(spec=Problem)
    p.id = uuid.uuid4()
    p.title = "两数之和"
    p.title_slug = "two-sum"
    p.description = "给定一个整数数组，返回两数之和为目标值的索引"
    p.input_format = "第一行 n，第二行 n 个整数"
    p.output_format = "两个索引"
    p.constraints = "2 <= n <= 10^4"
    p.difficulty = 2
    p.time_limit_ms = 1000
    p.memory_limit_mb = 256
    p.source_oj = None
    p.is_published = True
    p.tags = []
    return p


@pytest.mark.asyncio
async def test_get_problem_found(mock_db, sample_problem):
    """查询存在的题目"""
    _set_execute_return(mock_db, _make_result(scalar_return=sample_problem))

    result = await ProblemService.get_problem(mock_db, sample_problem.id)

    assert result is not None
    assert result.title == "两数之和"


@pytest.mark.asyncio
async def test_get_problem_not_found(mock_db):
    """查询不存在的题目"""
    _set_execute_return(mock_db, _make_result(scalar_return=None))

    result = await ProblemService.get_problem(mock_db, uuid.uuid4())

    assert result is None


@pytest.mark.asyncio
async def test_delete_problem_success(mock_db, sample_problem):
    """删除存在的题目"""
    _set_execute_return(mock_db, _make_result(scalar_return=sample_problem))

    result = await ProblemService.delete_problem(mock_db, sample_problem.id)

    assert result is True
    mock_db.delete.assert_called_once()


@pytest.mark.asyncio
async def test_delete_problem_not_found(mock_db):
    """删除不存在的题目"""
    _set_execute_return(mock_db, _make_result(scalar_return=None))

    result = await ProblemService.delete_problem(mock_db, uuid.uuid4())

    assert result is False


@pytest.mark.asyncio
async def test_list_problems_empty(mock_db):
    """空列表：无已发布题目"""
    call_count = 0

    async def _side_effect(*args, **kwargs):
        nonlocal call_count
        call_count += 1
        if call_count == 1:
            return _make_result(scalar_return=0)
        return _make_result(scalars_return=[])

    mock_db.execute.side_effect = _side_effect

    items, total = await ProblemService.list_problems(mock_db)

    assert items == []
    assert total == 0


@pytest.mark.asyncio
async def test_list_problems_with_search(mock_db, sample_problem):
    """关键词搜索"""
    call_count = 0

    async def _side_effect(*args, **kwargs):
        nonlocal call_count
        call_count += 1
        if call_count == 1:
            return _make_result(scalar_return=1)
        return _make_result(scalars_return=[sample_problem])

    mock_db.execute.side_effect = _side_effect

    items, total = await ProblemService.list_problems(mock_db, search="两数之和")

    assert total == 1
    assert len(items) == 1


@pytest.mark.asyncio
async def test_list_problems_pagination(mock_db, sample_problem):
    """分页：第 2 页，每页 5 条"""
    call_count = 0

    async def _side_effect(*args, **kwargs):
        nonlocal call_count
        call_count += 1
        if call_count == 1:
            return _make_result(scalar_return=12)
        return _make_result(scalars_return=[sample_problem])

    mock_db.execute.side_effect = _side_effect

    items, total = await ProblemService.list_problems(mock_db, page=2, page_size=5)

    assert total == 12
    assert len(items) == 1
