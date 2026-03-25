import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models import Tenant, User
from app.core.security import get_password_hash, create_access_token

async def seed_test_user(db: AsyncSession, email: str | None = None, password: str = "testpass"):
    """Seed a test user with a unique email. Returns (user, jwt_token)."""
    if email is None:
        email = f"test_{uuid.uuid4().hex[:8]}@co-op.local"

    tenant = Tenant(name=f"Tenant_{uuid.uuid4().hex[:8]}")
    db.add(tenant)
    await db.flush()
    
    user = User(
        tenant_id=tenant.id,
        email=email,
        hashed_password=get_password_hash(password),
        is_active=True
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    
    token = create_access_token(subject=str(user.id))
    return user, token
