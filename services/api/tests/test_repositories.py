import pytest
import pytest_asyncio
import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.repositories import UserRepository, DocumentRepository, AuditRepository
from app.db.models import Tenant

@pytest_asyncio.fixture
async def seeded_tenant(db_session: AsyncSession) -> Tenant:
    tenant = Tenant(name=f"test_tenant_{uuid.uuid4()}")
    db_session.add(tenant)
    await db_session.flush()
    return tenant

@pytest.mark.asyncio
async def test_user_repository_create_and_get(db_session: AsyncSession, seeded_tenant: Tenant):
    repo = UserRepository(db_session)
    email = f"test_{uuid.uuid4()}@example.com"
    user = await repo.create({
        "tenant_id": seeded_tenant.id,
        "email": email,
        "hashed_password": "fakehashedpassword",
    })
    
    assert user.id is not None
    assert user.email == email
    
    fetched = await repo.get(user.id)
    assert fetched is not None
    assert fetched.email == email

    fetched_by_email = await repo.get_by_email(email)
    assert fetched_by_email is not None
    assert fetched_by_email.id == user.id

@pytest.mark.asyncio
async def test_document_repository_create_and_get(db_session: AsyncSession, seeded_tenant: Tenant):
    repo = DocumentRepository(db_session)
    doc_hash = f"hash_{uuid.uuid4()}"
    doc = await repo.create({
        "tenant_id": seeded_tenant.id,
        "title": "Test Document",
        "content_hash": doc_hash,
    })
    
    assert doc.id is not None
    
    docs = await repo.get_by_tenant(seeded_tenant.id)
    assert len(docs) == 1
    assert docs[0].title == "Test Document"

    fetched = await repo.get_by_hash(seeded_tenant.id, doc_hash)
    assert fetched is not None
    assert fetched.id == doc.id

@pytest.mark.asyncio
async def test_audit_repository_append_event(db_session: AsyncSession, seeded_tenant: Tenant):
    repo = AuditRepository(db_session)
    event_type = "user_login"
    event_data = {"ip": "127.0.0.1"}
    
    event = await repo.append_event(
        tenant_id=seeded_tenant.id,
        event_type=event_type,
        event_data=event_data
    )
    
    assert event.id is not None
    assert event.event_type == event_type
    assert event.event_data == event_data
    assert event.tenant_id == seeded_tenant.id
