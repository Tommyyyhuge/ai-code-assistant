import json
import uuid
from datetime import datetime
from typing import AsyncGenerator, Optional
import httpx
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.ai_chat import AIConversation, AIMessage
from app.models.ai_provider import AIProvider
from app.models.knowledge import KnowledgeNode
from app.schemas.ai_chat import ConversationCreate, ConversationBrief, MessageItem
from app.utils.security import decrypt_api_key


class AIService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def list_conversations(self, user_id: uuid.UUID) -> list[ConversationBrief]:
        result = await self.db.execute(
            select(AIConversation)
            .where(AIConversation.user_id == user_id, AIConversation.is_active == True)
            .order_by(AIConversation.updated_at.desc())
        )
        return [ConversationBrief.model_validate(c) for c in result.scalars().all()]

    async def create_conversation(self, user_id: uuid.UUID, data: ConversationCreate) -> AIConversation:
        conv = AIConversation(
            user_id=user_id,
            knowledge_node_id=data.knowledge_node_id,
            provider_id=data.provider_id,
            title=data.title or "新对话",
        )
        self.db.add(conv)
        await self.db.commit()
        await self.db.refresh(conv)
        return conv

    async def get_messages(self, conversation_id: uuid.UUID) -> list[MessageItem]:
        result = await self.db.execute(
            select(AIMessage)
            .where(AIMessage.conversation_id == conversation_id)
            .order_by(AIMessage.created_at.asc())
        )
        return [MessageItem.model_validate(m) for m in result.scalars().all()]

    async def delete_conversation(self, conversation_id: uuid.UUID, user_id: uuid.UUID):
        result = await self.db.execute(
            select(AIConversation).where(
                AIConversation.id == conversation_id,
                AIConversation.user_id == user_id,
            )
        )
        conv = result.scalar_one_or_none()
        if conv:
            conv.is_active = False
            await self.db.commit()

    async def stream_chat(
        self, conversation_id: uuid.UUID, user_content: str
    ) -> AsyncGenerator[str, None]:
        # 查会话
        conv_result = await self.db.execute(
            select(AIConversation).where(AIConversation.id == conversation_id)
        )
        conv = conv_result.scalar_one_or_none()
        if not conv:
            yield f"data: {json.dumps({'error': '会话不存在'})}\n\n"
            yield "data: [DONE]\n\n"
            return

        # 查 AI Provider 配置
        provider = None
        if conv.provider_id:
            p_result = await self.db.execute(
                select(AIProvider).where(AIProvider.id == conv.provider_id)
            )
            provider = p_result.scalar_one_or_none()

        # 如果会话没有绑 provider，取用户默认
        if not provider:
            p_result = await self.db.execute(
                select(AIProvider).where(
                    AIProvider.user_id == conv.user_id, AIProvider.is_default == True
                )
            )
            provider = p_result.scalar_one_or_none()

        if not provider:
            yield f"data: {json.dumps({'error': '请先在设置中配置 AI 模型'})}\n\n"
            yield "data: [DONE]\n\n"
            return

        base_url = provider.base_url.rstrip("/")

        # 构建 System Prompt
        system_prompt = "你是算法竞赛教练助手，请用中文回答。"
        if conv.knowledge_node_id:
            node_result = await self.db.execute(
                select(KnowledgeNode).where(KnowledgeNode.id == conv.knowledge_node_id)
            )
            node = node_result.scalar_one_or_none()
            if node:
                system_prompt = (
                    f"你是算法竞赛教练助手，请用中文回答。\n"
                    f"用户正在学习知识点：{node.title}。\n"
                    f"核心概念：{node.core_concept}\n"
                    f"请用清晰的步骤讲解，引导学生独立思考，不要直接给完整代码答案。"
                )

        # 查历史消息（最近 20 条）
        hist_result = await self.db.execute(
            select(AIMessage)
            .where(AIMessage.conversation_id == conversation_id)
            .order_by(AIMessage.created_at.desc())
            .limit(20)
        )
        history = list(reversed(hist_result.scalars().all()))

        # 构建 messages
        messages = [{"role": "system", "content": system_prompt}]
        for msg in history:
            messages.append({"role": msg.role, "content": msg.content})
        messages.append({"role": "user", "content": user_content})

        # 保存用户消息
        user_msg = AIMessage(conversation_id=conversation_id, role="user", content=user_content)
        self.db.add(user_msg)
        await self.db.commit()

        # 更新会话时间
        conv.updated_at = datetime.utcnow()
        await self.db.commit()

        # 流式调用 AI
        assistant_content = ""
        try:
            async with httpx.AsyncClient(timeout=60) as client:
                async with client.stream(
                    "POST",
                    f"{base_url}/chat/completions",
                    headers={
                        "Authorization": f"Bearer {decrypt_api_key(provider.api_key)}",
                        "Content-Type": "application/json",
                    },
                    json={
                        "model": provider.model,
                        "messages": messages,
                        "stream": True,
                        "temperature": 0.7,
                        "max_tokens": 2048,
                    },
                ) as response:
                    async for line in response.aiter_lines():
                        if line.startswith("data: "):
                            data_str = line[6:]
                            if data_str == "[DONE]":
                                break
                            try:
                                chunk = json.loads(data_str)
                                delta = chunk["choices"][0]["delta"]
                                if "content" in delta:
                                    assistant_content += delta["content"]
                                    yield f"data: {json.dumps({'content': delta['content']})}\n\n"
                            except (json.JSONDecodeError, KeyError, IndexError):
                                continue
        except httpx.RequestError:
            yield f"data: {json.dumps({'error': 'AI 服务暂不可用，请稍后重试'})}\n\n"

        # 保存助手消息
        if assistant_content:
            assistant_msg = AIMessage(
                conversation_id=conversation_id,
                role="assistant",
                content=assistant_content,
                token_count=len(assistant_content) // 2,  # 粗略估算
            )
            self.db.add(assistant_msg)
            await self.db.commit()

        yield "data: [DONE]\n\n"
