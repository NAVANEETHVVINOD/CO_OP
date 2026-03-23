import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, func, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.dependencies import verify_token
from app.db.models import User, Conversation, Message

router = APIRouter(prefix="/v1/chat", tags=["Conversations"])

@router.get("/conversations")
async def list_conversations(
    current_user: User = Depends(verify_token),
    db: AsyncSession = Depends(get_db)
):
    # Subquery for message count per conversation
    msg_count = (
        select(
            Message.conversation_id,
            func.count(Message.id).label("message_count")
        )
        .group_by(Message.conversation_id)
        .subquery()
    )

    result = await db.execute(
        select(
            Conversation,
            func.coalesce(msg_count.c.message_count, 0).label("message_count")
        )
        .outerjoin(msg_count, Conversation.id == msg_count.c.conversation_id)
        .where(Conversation.user_id == current_user.id)
        .order_by(Conversation.created_at.desc())
        .limit(50)
    )
    rows = result.all()
    return [
        {
            "id": str(row[0].id),
            "title": row[0].title,
            "message_count": row[1],
            "created_at": row[0].created_at.isoformat() if row[0].created_at else None
        }
        for row in rows
    ]

@router.get("/conversations/{conversation_id}/messages")
async def get_conversation_messages(
    conversation_id: uuid.UUID,
    current_user: User = Depends(verify_token),
    db: AsyncSession = Depends(get_db)
):
    # Verify ownership
    result = await db.execute(
        select(Conversation).where(
            Conversation.id == conversation_id,
            Conversation.user_id == current_user.id
        )
    )
    conv = result.scalars().first()
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")

    result = await db.execute(
        select(Message)
        .where(Message.conversation_id == conversation_id)
        .order_by(Message.created_at.asc())
    )
    messages = result.scalars().all()
    return [
        {
            "id": str(m.id),
            "role": m.role,
            "content": m.content,
            "citations": m.citations or [],
            "created_at": m.created_at.isoformat() if m.created_at else None
        }
        for m in messages
    ]

@router.delete("/conversations/{conversation_id}")
async def delete_conversation(
    conversation_id: uuid.UUID,
    current_user: User = Depends(verify_token),
    db: AsyncSession = Depends(get_db)
):
    # Verify ownership
    result = await db.execute(
        select(Conversation).where(
            Conversation.id == conversation_id,
            Conversation.user_id == current_user.id
        )
    )
    conv = result.scalars().first()
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")

    # Delete messages first, then conversation
    await db.execute(
        delete(Message).where(Message.conversation_id == conversation_id)
    )
    await db.delete(conv)
    await db.commit()

    return {"status": "deleted", "id": str(conversation_id)}
