"""Tests for conversations router."""
import pytest
import uuid
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from tests.v1_test_utils import seed_test_user
from app.db.models import Conversation, Message


@pytest.mark.asyncio
async def test_list_conversations_empty(async_client: AsyncClient, db_session: AsyncSession):
    """GET /v1/chat/conversations should return empty list when no conversations exist."""
    user, token = await seed_test_user(db_session)
    
    response = await async_client.get(
        "/v1/chat/conversations",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data == []


@pytest.mark.asyncio
async def test_list_conversations_with_data(async_client: AsyncClient, db_session: AsyncSession):
    """GET /v1/chat/conversations returns list of conversations for the user."""
    user, token = await seed_test_user(db_session)
    
    # Create a conversation manually
    conv = Conversation(
        id=uuid.uuid4(),
        tenant_id=user.tenant_id,
        user_id=user.id,
        title="Test Conversation"
    )
    db_session.add(conv)
    await db_session.commit()
    
    response = await async_client.get(
        "/v1/chat/conversations",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["title"] == "Test Conversation"
    assert "id" in data[0]
    assert "message_count" in data[0]
    assert data[0]["message_count"] == 0


@pytest.mark.asyncio
async def test_get_conversation_messages(async_client: AsyncClient, db_session: AsyncSession):
    """GET /v1/chat/conversations/{conversation_id}/messages returns messages."""
    user, token = await seed_test_user(db_session)
    
    # Create conversation with messages
    conv = Conversation(
        id=uuid.uuid4(),
        tenant_id=user.tenant_id,
        user_id=user.id,
        title="Test Conversation"
    )
    db_session.add(conv)
    await db_session.flush()
    
    msg1 = Message(
        id=uuid.uuid4(),
        conversation_id=conv.id,
        role="user",
        content="Hello"
    )
    msg2 = Message(
        id=uuid.uuid4(),
        conversation_id=conv.id,
        role="assistant",
        content="Hi there!"
    )
    db_session.add(msg1)
    db_session.add(msg2)
    await db_session.commit()
    
    response = await async_client.get(
        f"/v1/chat/conversations/{conv.id}/messages",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]["content"] == "Hello"
    assert data[1]["content"] == "Hi there!"


@pytest.mark.asyncio
async def test_get_conversation_messages_not_found(async_client: AsyncClient, db_session: AsyncSession):
    """GET /v1/chat/conversations/{non_existent_id}/messages returns 404."""
    user, token = await seed_test_user(db_session)
    fake_id = uuid.uuid4()
    
    response = await async_client.get(
        f"/v1/chat/conversations/{fake_id}/messages",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_delete_conversation(async_client: AsyncClient, db_session: AsyncSession):
    """DELETE /v1/chat/conversations/{conversation_id} removes the conversation."""
    user, token = await seed_test_user(db_session)
    
    # Create conversation
    conv = Conversation(
        id=uuid.uuid4(),
        tenant_id=user.tenant_id,
        user_id=user.id,
        title="To Delete"
    )
    db_session.add(conv)
    await db_session.commit()
    
    delete_response = await async_client.delete(
        f"/v1/chat/conversations/{conv.id}",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert delete_response.status_code == 200
    assert delete_response.json()["status"] == "deleted"
    
    # Verify it's gone
    get_response = await async_client.get(
        f"/v1/chat/conversations/{conv.id}/messages",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert get_response.status_code == 404


@pytest.mark.asyncio
async def test_delete_conversation_not_found(async_client: AsyncClient, db_session: AsyncSession):
    """DELETE /v1/chat/conversations/{non_existent_id} returns 404."""
    user, token = await seed_test_user(db_session)
    fake_id = uuid.uuid4()
    
    response = await async_client.delete(
        f"/v1/chat/conversations/{fake_id}",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_list_conversations_with_message_count(async_client: AsyncClient, db_session: AsyncSession):
    """GET /v1/chat/conversations includes correct message count."""
    user, token = await seed_test_user(db_session)
    
    # Create conversation with messages
    conv = Conversation(
        id=uuid.uuid4(),
        tenant_id=user.tenant_id,
        user_id=user.id,
        title="Test Conversation"
    )
    db_session.add(conv)
    await db_session.flush()
    
    # Add 3 messages
    for i in range(3):
        msg = Message(
            id=uuid.uuid4(),
            conversation_id=conv.id,
            role="user" if i % 2 == 0 else "assistant",
            content=f"Message {i}"
        )
        db_session.add(msg)
    await db_session.commit()
    
    response = await async_client.get(
        "/v1/chat/conversations",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["message_count"] == 3
