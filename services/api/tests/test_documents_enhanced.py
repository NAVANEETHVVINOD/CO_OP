"""Enhanced tests for documents router."""
import pytest
import uuid
from io import BytesIO
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from tests.v1_test_utils import seed_test_user
from app.db.models import Document


@pytest.mark.asyncio
async def test_document_upload_without_file(async_client: AsyncClient, db_session: AsyncSession):
    """POST /v1/documents without a file should return 422."""
    user, token = await seed_test_user(db_session)
    
    response = await async_client.post(
        "/v1/documents",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_document_upload_success(async_client: AsyncClient, db_session: AsyncSession):
    """POST /v1/documents with valid file should succeed."""
    user, token = await seed_test_user(db_session)
    
    content = b"This is a test document about Python programming."
    files = {"file": ("test.txt", BytesIO(content), "text/plain")}
    
    response = await async_client.post(
        "/v1/documents",
        files=files,
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "document_id" in data
    assert data["status"] == "PENDING"


@pytest.mark.asyncio
async def test_document_upload_without_filename(async_client: AsyncClient, db_session: AsyncSession):
    """POST /v1/documents with file but no filename should return 422."""
    user, token = await seed_test_user(db_session)
    
    content = b"Test content"
    files = {"file": ("", BytesIO(content), "text/plain")}
    
    response = await async_client.post(
        "/v1/documents",
        files=files,
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_list_documents_empty(async_client: AsyncClient, db_session: AsyncSession):
    """GET /v1/documents returns empty list when no documents."""
    user, token = await seed_test_user(db_session)
    
    response = await async_client.get(
        "/v1/documents",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data == []


@pytest.mark.asyncio
async def test_list_documents_with_data(async_client: AsyncClient, db_session: AsyncSession):
    """GET /v1/documents returns list of user's documents."""
    user, token = await seed_test_user(db_session)
    
    # Create a document manually
    doc = Document(
        id=uuid.uuid4(),
        tenant_id=user.tenant_id,
        title="Test Document",
        content_hash="test_hash",
        status="READY"
    )
    db_session.add(doc)
    await db_session.commit()
    
    response = await async_client.get(
        "/v1/documents",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["title"] == "Test Document"
    assert data[0]["status"] == "READY"


@pytest.mark.asyncio
async def test_get_document_status(async_client: AsyncClient, db_session: AsyncSession):
    """GET /v1/documents/{document_id}/status returns document status."""
    user, token = await seed_test_user(db_session)
    
    doc = Document(
        id=uuid.uuid4(),
        tenant_id=user.tenant_id,
        title="Test Document",
        content_hash="test_hash",
        status="INDEXING"
    )
    db_session.add(doc)
    await db_session.commit()
    
    response = await async_client.get(
        f"/v1/documents/{doc.id}/status",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "INDEXING"
    # Compare UUIDs as strings (may have different formats with/without hyphens)
    assert str(data["document_id"]).replace("-", "") == str(doc.id).replace("-", "")


@pytest.mark.asyncio
async def test_get_document_status_not_found(async_client: AsyncClient, db_session: AsyncSession):
    """GET /v1/documents/{non_existent_id}/status returns 404."""
    user, token = await seed_test_user(db_session)
    fake_id = uuid.uuid4()
    
    response = await async_client.get(
        f"/v1/documents/{fake_id}/status",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_delete_document(async_client: AsyncClient, db_session: AsyncSession):
    """DELETE /v1/documents/{document_id} removes the document."""
    user, token = await seed_test_user(db_session)
    
    doc = Document(
        id=uuid.uuid4(),
        tenant_id=user.tenant_id,
        title="To Delete",
        content_hash="test_hash",
        status="READY"
    )
    db_session.add(doc)
    await db_session.commit()
    
    delete_response = await async_client.delete(
        f"/v1/documents/{doc.id}",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert delete_response.status_code == 200
    assert delete_response.json()["status"] == "deleted"
    
    # Verify it's gone
    get_response = await async_client.get(
        f"/v1/documents/{doc.id}/status",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert get_response.status_code == 404


@pytest.mark.asyncio
async def test_delete_document_not_found(async_client: AsyncClient, db_session: AsyncSession):
    """DELETE /v1/documents/{non_existent_id} returns 404."""
    user, token = await seed_test_user(db_session)
    fake_id = uuid.uuid4()
    
    response = await async_client.delete(
        f"/v1/documents/{fake_id}",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_document_upload_pdf(async_client: AsyncClient, db_session: AsyncSession):
    """POST /v1/documents with PDF file should succeed."""
    user, token = await seed_test_user(db_session)
    
    content = b"%PDF-1.4 fake pdf content"
    files = {"file": ("document.pdf", BytesIO(content), "application/pdf")}
    
    response = await async_client.post(
        "/v1/documents",
        files=files,
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "document_id" in data



@pytest.mark.asyncio
async def test_document_list_pagination(async_client: AsyncClient, db_session: AsyncSession):
    """GET /v1/documents returns paginated results."""
    user, token = await seed_test_user(db_session)
    
    # Create multiple documents
    for i in range(5):
        doc = Document(
            id=uuid.uuid4(),
            tenant_id=user.tenant_id,
            title=f"Document {i}",
            content_hash=f"hash_{i}",
            status="READY"
        )
        db_session.add(doc)
    await db_session.commit()
    
    response = await async_client.get(
        "/v1/documents",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 5


@pytest.mark.asyncio
async def test_document_upload_with_metadata(async_client: AsyncClient, db_session: AsyncSession):
    """POST /v1/documents stores document metadata correctly."""
    user, token = await seed_test_user(db_session)
    
    content = b"Document with metadata for testing purposes."
    files = {"file": ("metadata_test.txt", BytesIO(content), "text/plain")}
    
    response = await async_client.post(
        "/v1/documents",
        files=files,
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    data = response.json()
    
    # Verify document was created in database
    doc_id = uuid.UUID(data["document_id"])
    result = await db_session.execute(
        select(Document).where(Document.id == doc_id)
    )
    doc = result.scalars().first()
    assert doc is not None
    assert doc.tenant_id == user.tenant_id
