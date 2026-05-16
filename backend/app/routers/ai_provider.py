from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from uuid import UUID
from app.database import get_db
from app.rate_limit import limiter
from app.models.ai_provider import AIProvider
from app.utils.security import get_current_user

router = APIRouter(prefix="/api/v1/ai/providers", tags=["AI配置"])


def _mask_key(key: str) -> str:
    return key[:7] + "..." + key[-4:] if len(key) > 10 else "***"


@router.get("/")
@limiter.limit("20/minute")
async def list_providers(
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    result = await db.execute(
        select(AIProvider).where(AIProvider.user_id == current_user.id).order_by(AIProvider.created_at)
    )
    providers = result.scalars().all()
    return [
        {
            "id": str(p.id), "name": p.name, "base_url": p.base_url,
            "api_key": _mask_key(p.api_key), "model": p.model,
            "is_default": p.is_default,
        }
        for p in providers
    ]


@router.post("/")
@limiter.limit("10/minute")
async def create_provider(
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    body = await request.json()
    name = body.get("name", "").strip()
    if not name:
        raise HTTPException(400, "名称不能为空")

    # 设为默认时取消其他默认
    if body.get("is_default"):
        await db.execute(
            update(AIProvider).where(AIProvider.user_id == current_user.id).values(is_default=False)
        )

    provider = AIProvider(
        user_id=current_user.id,
        name=name,
        base_url=body.get("base_url", "").strip(),
        api_key=body.get("api_key", "").strip(),
        model=body.get("model", "").strip(),
        is_default=body.get("is_default", False),
    )
    db.add(provider)
    await db.commit()
    await db.refresh(provider)
    return {"id": str(provider.id), "name": provider.name}


@router.put("/{provider_id}")
@limiter.limit("10/minute")
async def update_provider(
    provider_id: str,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    result = await db.execute(
        select(AIProvider).where(AIProvider.id == UUID(provider_id), AIProvider.user_id == current_user.id)
    )
    provider = result.scalar_one_or_none()
    if not provider:
        raise HTTPException(404, "配置不存在")

    body = await request.json()

    if body.get("is_default"):
        await db.execute(
            update(AIProvider).where(AIProvider.user_id == current_user.id).values(is_default=False)
        )

    for field in ("name", "base_url", "api_key", "model"):
        if field in body and body[field]:
            setattr(provider, field, body[field])
    if "is_default" in body:
        provider.is_default = body["is_default"]

    await db.commit()
    return {"ok": True}


@router.delete("/{provider_id}")
@limiter.limit("10/minute")
async def delete_provider(
    provider_id: str,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    result = await db.execute(
        select(AIProvider).where(AIProvider.id == UUID(provider_id), AIProvider.user_id == current_user.id)
    )
    provider = result.scalar_one_or_none()
    if not provider:
        raise HTTPException(404, "配置不存在")

    await db.delete(provider)
    await db.commit()
    return {"ok": True}
