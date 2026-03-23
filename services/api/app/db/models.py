import uuid
from datetime import datetime, timezone
from typing import Dict, Any, List

from sqlalchemy import String, Boolean, DateTime, ForeignKey, Text, JSON, Integer, Float
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import JSONB

from app.db.base import Base

def utcnow() -> datetime:
    return datetime.now(timezone.utc)

class Tenant(Base):
    __tablename__ = "tenants"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    
    users: Mapped[List["User"]] = relationship(back_populates="tenant")
    documents: Mapped[List["Document"]] = relationship(back_populates="tenant")
    audit_events: Mapped[List["AuditEvent"]] = relationship(back_populates="tenant")
    cost_events: Mapped[List["CostEvent"]] = relationship(back_populates="tenant")
    leads: Mapped[List["Lead"]] = relationship(back_populates="tenant")

class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("tenants.id"))
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    tenant: Mapped["Tenant"] = relationship(back_populates="users")
    agent_runs: Mapped[List["AgentRun"]] = relationship(back_populates="user")
    audit_events: Mapped[List["AuditEvent"]] = relationship(back_populates="user")
    conversations: Mapped[List["Conversation"]] = relationship(back_populates="user")

class Document(Base):
    __tablename__ = "documents"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("tenants.id"))
    title: Mapped[str] = mapped_column(String(255))
    content_hash: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    status: Mapped[str] = mapped_column(String(50), default="pending") # pending, processing, completed, failed
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    tenant: Mapped["Tenant"] = relationship(back_populates="documents")
    chunks: Mapped[List["DocumentChunk"]] = relationship(back_populates="document")

class DocumentChunk(Base):
    __tablename__ = "document_chunks"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    document_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("documents.id"))
    chunk_index: Mapped[int] = mapped_column(Integer)
    text: Mapped[str] = mapped_column(Text)
    
    document: Mapped["Document"] = relationship(back_populates="chunks")

class AgentRun(Base):
    __tablename__ = "agent_runs"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"))
    query: Mapped[str] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(50), default="started")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    
    user: Mapped["User"] = relationship(back_populates="agent_runs")
    hitl_approvals: Mapped[List["HITLApproval"]] = relationship(back_populates="agent_run")

class HITLApproval(Base):
    __tablename__ = "hitl_approvals"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    agent_run_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("agent_runs.id"))
    action_type: Mapped[str] = mapped_column(String(100))
    status: Mapped[str] = mapped_column(String(50), default="pending") # pending, approved, rejected
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    agent_run: Mapped["AgentRun"] = relationship(back_populates="hitl_approvals")

class AuditEvent(Base):
    __tablename__ = "audit_events"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("tenants.id"))
    user_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    event_type: Mapped[str] = mapped_column(String(100), index=True)
    event_data: Mapped[Dict[str, Any]] = mapped_column(JSON().with_variant(JSONB, "postgresql"), default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    tenant: Mapped["Tenant"] = relationship(back_populates="audit_events")
    user: Mapped["User"] = relationship(back_populates="audit_events")

class CostEvent(Base):
    __tablename__ = "cost_events"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("tenants.id"))
    model_name: Mapped[str] = mapped_column(String(100), index=True)
    prompt_tokens: Mapped[int] = mapped_column(Integer, default=0)
    completion_tokens: Mapped[int] = mapped_column(Integer, default=0)
    cost: Mapped[float] = mapped_column(Float, default=0.0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    tenant: Mapped["Tenant"] = relationship(back_populates="cost_events")

class Conversation(Base):
    __tablename__ = "conversations"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("tenants.id"))
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"))
    title: Mapped[str] = mapped_column(String(255), default="New Conversation")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    
    user: Mapped["User"] = relationship(back_populates="conversations")
    messages: Mapped[List["Message"]] = relationship(back_populates="conversation")

class Message(Base):
    __tablename__ = "messages"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    conversation_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("conversations.id"))
    role: Mapped[str] = mapped_column(String(50)) # user, assistant, system
    content: Mapped[str] = mapped_column(Text)
    citations: Mapped[List[Dict[str, Any]]] = mapped_column(JSON().with_variant(JSONB, "postgresql"), default=list)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    
    conversation: Mapped["Conversation"] = relationship(back_populates="messages")


# ─── Stage 2 Models ────────────────────────────────────────────────

class Lead(Base):
    """Upwork/freelance job leads found by Lead Scout agent."""
    __tablename__ = "leads"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("tenants.id"))
    source: Mapped[str] = mapped_column(String(50), default="upwork")  # upwork, freelancer, etc.
    title: Mapped[str] = mapped_column(String(500))
    url: Mapped[str] = mapped_column(String(1000), default="")
    description: Mapped[str] = mapped_column(Text, default="")
    score: Mapped[float] = mapped_column(Float, default=0.0)  # 0-100 match score
    status: Mapped[str] = mapped_column(String(50), default="new")  # new, reviewed, applied, rejected
    found_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    tenant: Mapped["Tenant"] = relationship(back_populates="leads")


class SystemSetting(Base):
    """Key-value store for system settings (hardware tier, feature flags, etc.)."""
    __tablename__ = "system_settings"

    key: Mapped[str] = mapped_column(String(255), primary_key=True)
    value: Mapped[Dict[str, Any]] = mapped_column(JSON().with_variant(JSONB, "postgresql"), default=dict)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)
