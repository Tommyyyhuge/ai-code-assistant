from fastapi import APIRouter, Depends, HTTPException, Request, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.rate_limit import limiter
from app.schemas.ai_chat import ConversationCreate, StreamRequest
from app.services.ai_service import AIService
from app.utils.security import get_current_user

router = APIRouter(prefix="/api/v1/ai", tags=["AI对话"])


@router.get("/conversations")
@limiter.limit("20/minute")
async def list_conversations(
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    service = AIService(db)
    return await service.list_conversations(current_user.id)


@router.post("/conversations")
@limiter.limit("10/minute")
async def create_conversation(
    data: ConversationCreate,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    service = AIService(db)
    conv = await service.create_conversation(current_user.id, data)
    return {"id": str(conv.id), "title": conv.title, "created_at": conv.created_at.isoformat()}


@router.get("/conversations/{conversation_id}/messages")
@limiter.limit("20/minute")
async def get_messages(
    conversation_id: str,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    from uuid import UUID
    service = AIService(db)
    return await service.get_messages(UUID(conversation_id))


@router.delete("/conversations/{conversation_id}")
@limiter.limit("20/minute")
async def delete_conversation(
    conversation_id: str,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    from uuid import UUID
    service = AIService(db)
    await service.delete_conversation(UUID(conversation_id), current_user.id)
    return {"ok": True}


@router.post("/conversations/{conversation_id}/stream")
async def stream_chat(
    conversation_id: str,
    data: StreamRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
    token: str = Query(None),
):
    """SSE 流式对话"""
    from uuid import UUID
    service = AIService(db)
    generator = service.stream_chat(UUID(conversation_id), data.content)
    return StreamingResponse(generator, media_type="text/event-stream")
