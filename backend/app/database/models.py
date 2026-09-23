import uuid
from datetime import datetime
from sqlalchemy import Column, String, Text, DateTime, Float, Integer, JSON, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from app.database.database import Base

def generate_uuid():
    return str(uuid.uuid4())

def generate_ticket_id():
    return f"TKT-{uuid.uuid4().hex[:6].upper()}"

class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, default=generate_uuid)
    name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    tickets = relationship("Ticket", back_populates="customer")


class Ticket(Base):
    __tablename__ = "tickets"

    id = Column(String, primary_key=True, default=generate_ticket_id)
    customer_id = Column(String, ForeignKey("users.id"), nullable=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    category = Column(String(50), nullable=True, default="Unclassified")
    priority = Column(String(20), nullable=True, default="Medium")
    status = Column(String(50), nullable=False, default="NEW")  # NEW, PROCESSING, PENDING_APPROVAL, RESOLVED, ESCALATED, FAILED
    assigned_team = Column(String(50), nullable=True, default="Unassigned")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    customer = relationship("User", back_populates="tickets")
    workflow_runs = relationship("WorkflowRun", back_populates="ticket", cascade="all, delete-orphan")


class WorkflowRun(Base):
    __tablename__ = "workflow_runs"

    id = Column(String, primary_key=True, default=generate_uuid)
    ticket_id = Column(String, ForeignKey("tickets.id"), nullable=False)
    status = Column(String(50), nullable=False, default="RUNNING")  # RUNNING, PENDING_APPROVAL, COMPLETED, FAILED, REJECTED
    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    duration_ms = Column(Float, nullable=True)
    state_data = Column(JSON, nullable=True)

    ticket = relationship("Ticket", back_populates="workflow_runs")
    agent_runs = relationship("AgentRun", back_populates="workflow_run", cascade="all, delete-orphan")
    approvals = relationship("Approval", back_populates="workflow_run", cascade="all, delete-orphan")


class AgentRun(Base):
    __tablename__ = "agent_runs"

    id = Column(String, primary_key=True, default=generate_uuid)
    workflow_run_id = Column(String, ForeignKey("workflow_runs.id"), nullable=False)
    agent_name = Column(String(50), nullable=False)
    status = Column(String(20), nullable=False, default="SUCCESS")  # SUCCESS, FAILED, RETRYING
    input_data = Column(JSON, nullable=True)
    output_data = Column(JSON, nullable=True)
    duration_ms = Column(Float, nullable=False, default=0.0)
    error = Column(Text, nullable=True)
    retry_count = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)

    workflow_run = relationship("WorkflowRun", back_populates="agent_runs")


class Approval(Base):
    __tablename__ = "approvals"

    id = Column(String, primary_key=True, default=generate_uuid)
    workflow_run_id = Column(String, ForeignKey("workflow_runs.id"), nullable=False)
    risk_level = Column(String(20), nullable=False, default="HIGH")
    reason = Column(Text, nullable=False)
    status = Column(String(20), nullable=False, default="PENDING")  # PENDING, APPROVED, REJECTED
    approved_by = Column(String(100), nullable=True)
    decision_notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    resolved_at = Column(DateTime, nullable=True)

    workflow_run = relationship("WorkflowRun", back_populates="approvals")


class Document(Base):
    __tablename__ = "documents"

    id = Column(String, primary_key=True, default=generate_uuid)
    filename = Column(String(255), nullable=False)
    source = Column(String(255), nullable=False)
    chunk_id = Column(String(100), nullable=False)
    metadata_info = Column(JSON, nullable=True)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
