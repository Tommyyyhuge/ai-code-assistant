import re
from datetime import datetime
from typing import Optional
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import User
from app.schemas.user import UserRegister, UserLogin, TokenResponse
from app.utils.security import (
    get_password_hash, verify_password,
    create_access_token, create_refresh_token, decode_token
)

# 密码强度规则
_PASSWORD_MIN_LENGTH = 8
_PASSWORD_PATTERN = re.compile(
    r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[!@#$%^&*()_+\-=\[\]{};':\"\\|,.<>\/?]).{8,}$"
)

def _validate_password_strength(password: str) -> None:
    """验证密码强度：至少8位，含大小写字母、数字、特殊字符"""
    if len(password) < _PASSWORD_MIN_LENGTH:
        raise ValueError(f"密码长度至少为 {_PASSWORD_MIN_LENGTH} 位")
    if not _PASSWORD_PATTERN.match(password):
        raise ValueError("密码必须包含大写字母、小写字母、数字和特殊字符")


class AuthService:
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def register(self, user_data: UserRegister) -> User:
        """用户注册"""
        # 密码强度校验
        _validate_password_strength(user_data.password)

        # 检查邮箱是否已存在
        result = await self.db.execute(
            select(User).where(User.email == user_data.email)
        )
        if result.scalar_one_or_none():
            raise ValueError("Email already registered")
        
        # 检查用户名是否已存在
        result = await self.db.execute(
            select(User).where(User.username == user_data.username)
        )
        if result.scalar_one_or_none():
            raise ValueError("Username already taken")
        
        # 创建用户
        user = User(
            username=user_data.username,
            email=user_data.email,
            password_hash=get_password_hash(user_data.password)
        )
        self.db.add(user)
        await self.db.flush()
        await self.db.refresh(user)
        return user
    
    async def login(self, login_data: UserLogin) -> TokenResponse:
        """用户登录"""
        result = await self.db.execute(
            select(User).where(User.email == login_data.email)
        )
        user = result.scalar_one_or_none()
        
        if not user or not verify_password(login_data.password, user.password_hash):
            raise ValueError("Invalid email or password")
        
        if not user.is_active:
            raise ValueError("User account is deactivated")
        
        # 更新最后登录时间
        user.last_login_at = datetime.utcnow()
        
        # 生成 Token
        token_data = {"sub": str(user.id), "email": user.email}
        access_token = create_access_token(token_data)
        refresh_token = create_refresh_token(token_data)
        
        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=60 * 60  # 60 minutes in seconds
        )
    
    async def refresh_access_token(self, refresh_token: str) -> TokenResponse:
        """使用 refresh token 获取新的 access token"""
        payload = decode_token(refresh_token)
        if not payload or payload.get("type") != "refresh":
            raise ValueError("Invalid refresh token")

        user_id = payload.get("sub")
        if not user_id:
            raise ValueError("Invalid token payload")

        user = await self.get_user_by_id(UUID(user_id))
        if not user or not user.is_active:
            raise ValueError("User not found or deactivated")

        token_data = {"sub": str(user.id), "email": user.email}
        access_token = create_access_token(token_data)
        # 滚动刷新：同时发放新的 refresh token
        new_refresh_token = create_refresh_token(token_data)

        return TokenResponse(
            access_token=access_token,
            refresh_token=new_refresh_token,
            expires_in=60 * 60,
        )

    async def get_user_by_id(self, user_id: UUID) -> Optional[User]:
        """通过 ID 获取用户"""
        result = await self.db.execute(
            select(User).where(User.id == user_id)
        )
        return result.scalar_one_or_none()