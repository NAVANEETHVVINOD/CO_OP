import uuid
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.db.repositories import DocumentRepository
from app.dependencies import verify_token
from app.db.models import User
from app.core.redis_client import publish_ingestion_event

from app.core.minio_client import upload_file, delete_file

router = APIRouter(prefix="/v1/documents", tags=["Documents"])

@router.post("")
async def upload_document(
    file: UploadFile = File(...),
    current_user: User = Depends(verify_token),
    db: AsyncSession = Depends(get_db)
):
    if not file.filename:
        raise HTTPException(status_code=400, detail="Filename missing")

    doc_id = uuid.uuid4()
    ext = file.filename.split(".")[-1].lower() if "." in file.filename else ""
    object_name = f"{current_user.tenant_id}/{doc_id}.{ext}"

    file_content = await file.read()
    
    # Upload to MinIO
    upload_success = upload_file("raw-documents", object_name, file_content, content_type=file.content_type)
    if not upload_success:
        raise HTTPException(status_code=500, detail="Failed to upload document to object storage")

    doc_repo = DocumentRepository(db)
    # Create document entry in PENDING status
    new_doc = await doc_repo.create({
        "id": doc_id,
        "tenant_id": current_user.tenant_id,
        "title": file.filename,
        "content_hash": object_name,
        "status": "PENDING",
    })
    # Commit so the Redis consumer (separate session) can see the document
    await db.commit()
    await db.refresh(new_doc)

    # Trigger async ingestion
    await publish_ingestion_event(
        document_id=str(new_doc.id),
        file_path=object_name,
        tenant_id=str(current_user.tenant_id),
        filename=file.filename
    )

    return {"document_id": str(new_doc.id), "status": "PENDING"}

@router.get("")
async def list_documents(
    current_user: User = Depends(verify_token),
    db: AsyncSession = Depends(get_db)
):
    doc_repo = DocumentRepository(db)
    docs = await doc_repo.get_by_tenant(current_user.tenant_id)
    return [
        {
            "id": str(doc.id),
            "title": doc.title,
            "status": doc.status,
            "created_at": doc.created_at.isoformat() if doc.created_at else None
        }
        for doc in docs
    ]

@router.get("/{document_id}/status")
async def get_document_status(
    document_id: uuid.UUID,
    current_user: User = Depends(verify_token),
    db: AsyncSession = Depends(get_db)
):
    doc_repo = DocumentRepository(db)
    doc = await doc_repo.get(document_id)
    if not doc or doc.tenant_id != current_user.tenant_id:
        raise HTTPException(status_code=404, detail="Document not found")
        
    return {"document_id": str(doc.id), "status": doc.status}

@router.delete("/{document_id}")
async def delete_document(
    document_id: uuid.UUID,
    current_user: User = Depends(verify_token),
    db: AsyncSession = Depends(get_db)
):
    doc_repo = DocumentRepository(db)
    doc = await doc_repo.get(document_id)
    if not doc or doc.tenant_id != current_user.tenant_id:
        raise HTTPException(status_code=404, detail="Document not found")
    
    # Delete from MinIO
    delete_file("raw-documents", doc.content_hash)
    
    # Delete from DB
    await db.delete(doc)
    await db.commit()
    
    return {"status": "deleted", "document_id": str(document_id)}
