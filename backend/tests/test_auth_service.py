"""AuthService 单元测试 — 使用 AsyncMock 模拟数据库"""
import uuid
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from app.models.user import User
from app.schemas.user import UserRegister, UserLogin
from app.services.auth_service import AuthService
from app.utils.security import get_password_hash, verify_password


def _make_result(return_value):
    """创建模拟的 SQLAlchemy result proxy"""
    result = MagicMock()
    result.scalar_one_or_none.return_value = return_value
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
def sample_user():
    """创建一个示例用户对象（用于模拟数据库返回）"""
    user = MagicMock(spec=User)
    user.id = uuid.uuid4()
    user.username = "testuser"
    user.email = "test@example.com"
    user.password_hash = get_password_hash("StrongP@ss1")
    user.is_active = True
    return user


@pytest.mark.asyncio
async def test_register_success(mock_db):
    """正常注册：邮箱和用户名均不重复"""
    _set_execute_return(mock_db, _make_result(None))

    service = AuthService(mock_db)
    user_data = UserRegister(
        username="newuser",
        email="new@example.com",
        password="StrongP@ss1",
    )

    # mock db.add + flush + refresh
    async def mock_refresh(user):
        user.id = uuid.uuid4()

    mock_db.refresh = mock_refresh

    user = await service.register(user_data)

    assert user.username == "newuser"
    assert user.email == "new@example.com"
    assert mock_db.add.called


@pytest.mark.asyncio
async def test_register_duplicate_email(mock_db, sample_user):
    """邮箱已被注册"""
    _set_execute_return(mock_db, _make_result(sample_user))

    service = AuthService(mock_db)
    user_data = UserRegister(
        username="otheruser",
        email="test@example.com",
        password="StrongP@ss1",
    )

    with pytest.raises(ValueError, match="Email already registered"):
        await service.register(user_data)


@pytest.mark.asyncio
async def test_register_duplicate_username(mock_db, sample_user):
    """用户名已被占用"""
    # 第一次查询（邮箱）返回 None，第二次查询（用户名）返回已有用户
    call_count = 0

    async def _side_effect(*args, **kwargs):
        nonlocal call_count
        call_count += 1
        if call_count == 1:
            return _make_result(None)
        return _make_result(sample_user)

    mock_db.execute.side_effect = _side_effect

    service = AuthService(mock_db)
    user_data = UserRegister(
        username="testuser",
        email="new@example.com",
        password="StrongP@ss1",
    )

    with pytest.raises(ValueError, match="Username already taken"):
        await service.register(user_data)


@pytest.mark.asyncio
async def test_register_weak_password_short(mock_db):
    """密码长度够但缺少数字和特殊字符 — 被业务规则拦截"""
    _set_execute_return(mock_db, _make_result(None))

    service = AuthService(mock_db)
    user_data = UserRegister(
        username="newuser",
        email="new@example.com",
        password="Abcdefgh",  # 长度够但不含数字和特殊字符
    )

    with pytest.raises(ValueError, match="密码必须包含"):
        await service.register(user_data)


@pytest.mark.asyncio
async def test_register_weak_password_no_uppercase(mock_db):
    """密码缺少大写字母"""
    _set_execute_return(mock_db, _make_result(None))

    service = AuthService(mock_db)
    user_data = UserRegister(
        username="newuser",
        email="new@example.com",
        password="abcdef1!",
    )

    with pytest.raises(ValueError, match="密码必须包含"):
        await service.register(user_data)


@pytest.mark.asyncio
async def test_login_success(mock_db, sample_user):
    """正确邮箱+密码登录成功"""
    _set_execute_return(mock_db, _make_result(sample_user))

    service = AuthService(mock_db)
    login_data = UserLogin(email="test@example.com", password="StrongP@ss1")

    result = await service.login(login_data)

    assert result.access_token is not None
    assert result.refresh_token is not None
    assert result.token_type == "bearer"


@pytest.mark.asyncio
async def test_login_wrong_password(mock_db, sample_user):
    """密码错误"""
    _set_execute_return(mock_db, _make_result(sample_user))

    service = AuthService(mock_db)
    login_data = UserLogin(email="test@example.com", password="WrongP@ss1")

    with pytest.raises(ValueError, match="Invalid email or password"):
        await service.login(login_data)


@pytest.mark.asyncio
async def test_login_user_not_found(mock_db):
    """用户不存在"""
    _set_execute_return(mock_db, _make_result(None))

    service = AuthService(mock_db)
    login_data = UserLogin(email="ghost@example.com", password="Whatever1!")

    with pytest.raises(ValueError, match="Invalid email or password"):
        await service.login(login_data)


@pytest.mark.asyncio
async def test_login_deactivated_user(mock_db, sample_user):
    """已停用的用户"""
    sample_user.is_active = False
    _set_execute_return(mock_db, _make_result(sample_user))

    service = AuthService(mock_db)
    login_data = UserLogin(email="test@example.com", password="StrongP@ss1")

    with pytest.raises(ValueError, match="deactivated"):
        await service.login(login_data)
