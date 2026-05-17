from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # 应用
    APP_VERSION: str = "0.1.0"

    # 数据库 — 无默认值，必须通过环境变量或 .env 文件配置
    DATABASE_URL: str = ""
    REDIS_URL: str = ""

    # JWT — SECRET_KEY 无默认值，强制配置
    SECRET_KEY: str = ""
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # GitHub OAuth
    GITHUB_CLIENT_ID: str = ""
    GITHUB_CLIENT_SECRET: str = ""

    # AI — 平台默认 AI 配置
    DEEPSEEK_API_KEY: str = ""
    DEEPSEEK_API_BASE: str = "https://api.deepseek.com/v1"

    # Sentry — 错误监控
    SENTRY_DSN: str = ""
    SENTRY_ENVIRONMENT: str = "development"

    # SMTP — 邮件发送（忘记密码）
    SMTP_HOST: str = "smtp.qq.com"
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"  # 忽略 .env 中的多余配置


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()