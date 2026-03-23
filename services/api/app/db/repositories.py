import uuid
from typing import Optional, List, TypeVar, Generic, Type

from sqlalchemy import select, String
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.db.models import User, Document, AuditEvent, Tenant
from app.db.base import Base

ModelType = TypeVar("ModelType", bound=Base)

class BaseRepository(Generic[ModelType]):
    def __init__(self, model: Type[ModelType], session: AsyncSession):
        self.model = model
        self.session = session

    async def get(self, id: uuid.UUID) -> Optional[ModelType]:
        result = await self.session.execute(select(self.model).where(self.model.id == id))
        return result.scalars().first()

    async def create(self, obj_in: dict) -> ModelType:
        db_obj = self.model(**obj_in)
        self.session.add(db_obj)
        await self.session.flush()
        return db_obj

class UserRepository(BaseRepository[User]):
    def __init__(self, session: AsyncSession):
        super().__init__(User, session)

    async def get_by_email(self, email: str) -> Optional[User]:
        result = await self.session.execute(select(self.model).where(self.model.email == email))
        return result.scalars().first()

    async def get_with_tenant(self, user_id: uuid.UUID) -> Optional[User]:
        result = await self.session.execute(
            select(self.model).where(self.model.id == user_id).options(selectinload(self.model.tenant))
        )
        return result.scalars().first()

class DocumentRepository(BaseRepository[Document]):
    def __init__(self, session: AsyncSession):
        super().__init__(Document, session)

    async def get_by_tenant(self, tenant_id: uuid.UUID, limit: int = 100, offset: int = 0) -> List[Document]:
        result = await self.session.execute(
            select(self.model).where(self.model.tenant_id == tenant_id).limit(limit).offset(offset)
        )
        return list(result.scalars().all())

    async def get_by_hash(self, tenant_id: uuid.UUID, content_hash: str) -> Optional[Document]:
        result = await self.session.execute(
            select(self.model).where(
                self.model.tenant_id == tenant_id,
                self.model.content_hash == content_hash
            )
        )
        return result.scalars().first()

class AuditRepository(BaseRepository[AuditEvent]):
    def __init__(self, session: AsyncSession):
        super().__init__(AuditEvent, session)

    async def append_event(self, tenant_id: uuid.UUID, event_type: str, event_data: dict, user_id: Optional[uuid.UUID] = None) -> AuditEvent:
        return await self.create({
            "tenant_id": tenant_id,
            "user_id": user_id,
            "event_type": event_type,
            "event_data": event_data
        })
