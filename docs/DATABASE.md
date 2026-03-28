# Database Schema

Co-Op uses PostgreSQL 16 as its primary relational database. All data is accessed asynchronously via SQLAlchemy 2.0+ with async engine and sessions.

## Table of Contents

- [Entity-Relationship Diagram](#entity-relationship-diagram)
- [Tables Description](#tables-description)
- [Migrations](#migrations)
- [Environment Variables](#environment-variables)
- [Best Practices](#best-practices)

## Entity-Relationship Diagram

```mermaid
erDiagram
    users ||--o{ conversations : has
    users ||--o{ documents : uploads
    users ||--o{ leads : owns
    users ||--o{ proposals : writes
    users ||--o{ invoices : creates
    users ||--o{ approvals : requests
    conversations ||--o{ messages : contains
    documents ||--o{ chunks : "parsed into"
    leads ||--o{ proposals : "generates"
    proposals ||--o{ projects : "wins →"
    projects ||--o{ milestones : "has"
    milestones ||--o{ invoices : "triggers"
    
    users {
        uuid id PK
        string email UK
        string hashed_password
        string full_name
        string role
        timestamp created_at
        timestamp updated_at
        jsonb preferences
    }
    
    conversations {
        uuid id PK
        uuid user_id FK
        string title
        timestamp created_at
        timestamp updated_at
    }
    
    messages {
        uuid id PK
        uuid conversation_id FK
        string role
        text content
        jsonb metadata
        timestamp created_at
    }
    
    documents {
        uuid id PK
        uuid user_id FK
        string filename
        string content_type
        string storage_path
        string status
        jsonb metadata
        timestamp created_at
        timestamp processed_at
    }
    
    chunks {
        uuid id PK
        uuid document_id FK
        int chunk_index
        text content
        jsonb metadata
    }
    
    leads {
        uuid id PK
        uuid user_id FK
        string title
        text description
        string source
        float score
        string status
        timestamp found_at
    }
    
    proposals {
        uuid id PK
        uuid lead_id FK
        text content
        string status
        timestamp created_at
        timestamp approved_at
    }
    
    projects {
        uuid id PK
        uuid user_id FK
        string name
        text description
        string status
        date start_date
        date end_date
    }
    
    milestones {
        uuid id PK
        uuid project_id FK
        string title
        text description
        date due_date
        boolean completed
    }
    
    invoices {
        uuid id PK
        uuid milestone_id FK
        uuid user_id FK
        float amount
        string currency
        string status
        date due_date
        timestamp sent_at
        timestamp paid_at
    }
    
    approvals {
        uuid id PK
        uuid user_id FK
        string action_type
        jsonb data
        string status
        timestamp created_at
        timestamp resolved_at
    }
```

## Tables Description

### `users`

Stores user accounts with authentication credentials and preferences.

- **id**: UUID primary key
- **email**: Unique email address for login
- **hashed_password**: bcrypt-hashed password (SHA256 pre-hash enabled to avoid 72-byte limit)
- **full_name**: User's display name
- **role**: User role (`admin`, `user`)
- **created_at**: Account creation timestamp
- **updated_at**: Last update timestamp
- **preferences**: JSONB field for user settings (theme, notifications, etc.)

**Security**: Passwords are hashed with bcrypt using cost factor 12. SHA256 pre-hashing is applied to handle passwords longer than 72 bytes.

### `conversations` & `messages`

Chat history storage for RAG-augmented conversations.

**conversations**:
- Groups related messages together
- Tracks conversation metadata (title, timestamps)
- Belongs to a single user

**messages**:
- Individual chat messages within a conversation
- **role**: `user`, `assistant`, or `system`
- **content**: Message text
- **metadata**: JSONB field for citations, sources, token counts, etc.

### `documents` & `chunks`

Document storage and processing pipeline.

**documents**:
- Metadata for uploaded documents
- **storage_path**: MinIO object key
- **status**: `PENDING`, `INDEXING`, `READY`, `FAILED`
- **metadata**: File size, page count, processing info

**chunks**:
- Document fragments for RAG retrieval
- Created by `chunker.py` during document processing
- **chunk_index**: Sequential position in document
- **content**: Text content of chunk
- **metadata**: Page number, section, embeddings info
- Also indexed in Qdrant for vector search

### `leads`, `proposals`, `projects`, `milestones`, `invoices`

Lead-to-cash workflow tables.

**leads**:
- Potential business opportunities discovered by agents
- **score**: Relevance/quality score (0-1)
- **source**: Where the lead was found (GitHub, LinkedIn, etc.)

**proposals**:
- Generated proposals for leads
- Requires HITL approval before sending

**projects**:
- Won proposals become active projects
- Tracks deliverables and timeline

**milestones**:
- Project checkpoints
- Trigger invoice generation when completed

**invoices**:
- Financial records for completed work
- **status**: `DRAFT`, `SENT`, `PAID`, `OVERDUE`

### `approvals`

Human-in-the-loop (HITL) approval queue.

- **action_type**: Type of action requiring approval (`send_proposal`, `create_invoice`, etc.)
- **data**: JSONB field with action details
- **status**: `PENDING`, `APPROVED`, `REJECTED`

## Migrations

Database migrations are managed with Alembic.

### Running Migrations

```bash
# Navigate to API directory
cd services/api

# Run pending migrations
alembic upgrade head

# Check current migration version
alembic current

# View migration history
alembic history
```

### Creating New Migrations

```bash
# Auto-generate migration from model changes
alembic revision --autogenerate -m "Add new column to users table"

# Create empty migration for manual changes
alembic revision -m "Add custom index"

# Edit the generated file in alembic/versions/
# Then apply it
alembic upgrade head
```

### Migration Best Practices

1. **Always review auto-generated migrations** - Alembic may miss some changes
2. **Test migrations on a copy of production data** before deploying
3. **Write reversible migrations** - implement both `upgrade()` and `downgrade()`
4. **Use batch operations** for large tables to avoid locking
5. **Add indexes concurrently** in PostgreSQL to avoid downtime

### Migration Files Location

Migrations are stored in `services/api/alembic/versions/`. Each file contains:
- **Revision ID**: Unique identifier
- **Down revision**: Parent migration
- **upgrade()**: Forward migration
- **downgrade()**: Rollback migration

## Environment Variables

Configure database connection via environment variables:

| Variable | Description | Default |
|----------|-------------|---------|
| `POSTGRES_HOST` | PostgreSQL host | `localhost` |
| `POSTGRES_PORT` | PostgreSQL port | `5432` |
| `POSTGRES_USER` | Database user | `coop` |
| `POSTGRES_PASSWORD` | Database password | (required) |
| `POSTGRES_DB` | Database name | `coop_os` |
| `DATABASE_URL` | Full connection string (overrides above) | (optional) |

### Connection String Format

```
postgresql+asyncpg://user:password@host:port/database
```

Example:
```
postgresql+asyncpg://coop:secret@localhost:5432/coop_os
```

## Best Practices

### Async Operations

All database operations use async/await with SQLAlchemy 2.0:

```python
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

async def get_user(session: AsyncSession, user_id: str):
    result = await session.execute(
        select(User).where(User.id == user_id)
    )
    return result.scalar_one_or_none()
```

### Connection Pooling

The application uses connection pooling for efficiency:
- **Pool size**: 5 connections
- **Max overflow**: 10 additional connections
- **Pool recycle**: 3600 seconds (1 hour)

### Transactions

Use transactions for multi-step operations:

```python
async with session.begin():
    # All operations here are atomic
    user = User(email="test@example.com")
    session.add(user)
    # Automatically committed if no exception
```

### Indexes

Key indexes for performance:
- `users.email` (unique)
- `documents.user_id`
- `documents.status`
- `messages.conversation_id`
- `chunks.document_id`

### Backup and Restore

```bash
# Backup
docker exec -t docker-postgres-1 pg_dump -U coop coop_os > backup.sql

# Restore
cat backup.sql | docker exec -i docker-postgres-1 psql -U coop coop_os
```

For production, use automated backups with point-in-time recovery (PITR).

## Related Documentation

- [Backend API Documentation](../services/api/README.md)
- [Docker Infrastructure](../infrastructure/docker/README.md)
- [Security Practices](./SECURITY.md)
