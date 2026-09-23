from datetime import datetime
from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, desc, func
from app.database.models import Ticket, WorkflowRun, AgentRun, Approval, Document, User

class TicketRepository:
    @staticmethod
    async def create(session: AsyncSession, title: str, description: str, customer_id: Optional[str] = None) -> Ticket:
        ticket = Ticket(
            title=title,
            description=description,
            customer_id=customer_id,
            status="NEW"
        )
        session.add(ticket)
        await session.commit()
        await session.refresh(ticket)
        return ticket

    @staticmethod
    async def get_by_id(session: AsyncSession, ticket_id: str) -> Optional[Ticket]:
        result = await session.execute(select(Ticket).where(Ticket.id == ticket_id))
        return result.scalars().first()

    @staticmethod
    async def list_all(session: AsyncSession, limit: int = 50, offset: int = 0) -> List[Ticket]:
        result = await session.execute(
            select(Ticket).order_by(desc(Ticket.created_at)).limit(limit).offset(offset)
        )
        return list(result.scalars().all())

    @staticmethod
    async def update_status(
        session: AsyncSession,
        ticket_id: str,
        status: str,
        category: Optional[str] = None,
        priority: Optional[str] = None,
        assigned_team: Optional[str] = None
    ) -> Optional[Ticket]:
        values: Dict[str, Any] = {"status": status, "updated_at": datetime.utcnow()}
        if category:
            values["category"] = category
        if priority:
            values["priority"] = priority
        if assigned_team:
            values["assigned_team"] = assigned_team

        await session.execute(update(Ticket).where(Ticket.id == ticket_id).values(**values))
        await session.commit()
        return await TicketRepository.get_by_id(session, ticket_id)


class WorkflowRepository:
    @staticmethod
    async def create_run(session: AsyncSession, ticket_id: str) -> WorkflowRun:
        run = WorkflowRun(ticket_id=ticket_id, status="RUNNING", started_at=datetime.utcnow())
        session.add(run)
        await session.commit()
        await session.refresh(run)
        return run

    @staticmethod
    async def get_run(session: AsyncSession, run_id: str) -> Optional[WorkflowRun]:
        result = await session.execute(select(WorkflowRun).where(WorkflowRun.id == run_id))
        return result.scalars().first()

    @staticmethod
    async def update_run(
        session: AsyncSession,
        run_id: str,
        status: str,
        state_data: Optional[Dict[str, Any]] = None,
        duration_ms: Optional[float] = None
    ) -> Optional[WorkflowRun]:
        values: Dict[str, Any] = {"status": status}
        if state_data is not None:
            values["state_data"] = state_data
        if duration_ms is not None:
            values["duration_ms"] = duration_ms
        if status in ["COMPLETED", "FAILED", "REJECTED"]:
            values["completed_at"] = datetime.utcnow()

        await session.execute(update(WorkflowRun).where(WorkflowRun.id == run_id).values(**values))
        await session.commit()
        return await WorkflowRepository.get_run(session, run_id)

    @staticmethod
    async def list_runs(session: AsyncSession, limit: int = 50) -> List[WorkflowRun]:
        result = await session.execute(
            select(WorkflowRun).order_by(desc(WorkflowRun.started_at)).limit(limit)
        )
        return list(result.scalars().all())


class AgentRunRepository:
    @staticmethod
    async def log_run(
        session: AsyncSession,
        workflow_run_id: str,
        agent_name: str,
        status: str,
        input_data: Optional[Dict[str, Any]] = None,
        output_data: Optional[Dict[str, Any]] = None,
        duration_ms: float = 0.0,
        error: Optional[str] = None,
        retry_count: int = 0
    ) -> AgentRun:
        run = AgentRun(
            workflow_run_id=workflow_run_id,
            agent_name=agent_name,
            status=status,
            input_data=input_data,
            output_data=output_data,
            duration_ms=duration_ms,
            error=error,
            retry_count=retry_count,
            created_at=datetime.utcnow()
        )
        session.add(run)
        await session.commit()
        await session.refresh(run)
        return run

    @staticmethod
    async def get_logs_for_workflow(session: AsyncSession, workflow_run_id: str) -> List[AgentRun]:
        result = await session.execute(
            select(AgentRun)
            .where(AgentRun.workflow_run_id == workflow_run_id)
            .order_by(AgentRun.created_at)
        )
        return list(result.scalars().all())

    @staticmethod
    async def list_all_logs(session: AsyncSession, limit: int = 100) -> List[AgentRun]:
        result = await session.execute(
            select(AgentRun).order_by(desc(AgentRun.created_at)).limit(limit)
        )
        return list(result.scalars().all())


class ApprovalRepository:
    @staticmethod
    async def create_approval(
        session: AsyncSession,
        workflow_run_id: str,
        risk_level: str,
        reason: str
    ) -> Approval:
        approval = Approval(
            workflow_run_id=workflow_run_id,
            risk_level=risk_level,
            reason=reason,
            status="PENDING",
            created_at=datetime.utcnow()
        )
        session.add(approval)
        await session.commit()
        await session.refresh(approval)
        return approval

    @staticmethod
    async def get_by_id(session: AsyncSession, approval_id: str) -> Optional[Approval]:
        result = await session.execute(select(Approval).where(Approval.id == approval_id))
        return result.scalars().first()

    @staticmethod
    async def list_pending(session: AsyncSession) -> List[Approval]:
        result = await session.execute(
            select(Approval).where(Approval.status == "PENDING").order_by(desc(Approval.created_at))
        )
        return list(result.scalars().all())

    @staticmethod
    async def resolve_approval(
        session: AsyncSession,
        approval_id: str,
        approved: bool,
        approved_by: str = "Admin",
        notes: Optional[str] = None
    ) -> Optional[Approval]:
        status = "APPROVED" if approved else "REJECTED"
        await session.execute(
            update(Approval)
            .where(Approval.id == approval_id)
            .values(
                status=status,
                approved_by=approved_by,
                decision_notes=notes,
                resolved_at=datetime.utcnow()
            )
        )
        await session.commit()
        return await ApprovalRepository.get_by_id(session, approval_id)
