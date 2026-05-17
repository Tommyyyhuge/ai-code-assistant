from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field
from uuid import UUID


# ========== 基础模型 ==========
class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr


class UserProfile(BaseModel):
    display_name: Optional[str] = None
    bio: Optional[str] = None
    school: Optional[str] = None
    preferred_language: str = "cpp"


# ========== 请求模型 ==========
class UserRegister(UserBase):
    password: str = Field(..., min_length=8, max_length=128)


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class RefreshTokenRequest(BaseModel):
    refresh_token: str


class UserUpdate(BaseModel):
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    display_name: Optional[str] = None
    bio: Optional[str] = None
    school: Optional[str] = None
    preferred_language: Optional[str] = None


# ========== 响应模型 ==========
class UserResponse(UserBase):
    id: UUID
    avatar_url: Optional[str] = None
    role: str
    elo_rating: int
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


class UserProfileResponse(UserResponse):
    profile: Optional[UserProfile] = None


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


class TokenPayload(BaseModel):
    sub: Optional[str] = None
    exp: Optional[datetime] = None


# ========== 忘记密码 ==========
class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    email: EmailStr
    code: str = Field(..., min_length=6, max_length=6)
    new_password: str = Field(..., min_length=8, max_length=128)