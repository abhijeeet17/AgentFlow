import time
import logging
from typing import Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.repositories import (
    TicketRepository, WorkflowRepository, AgentRunRepository, ApprovalRepository
)
from app.graph.workflow import agentflow_graph
from app.monitoring.metrics import metrics_manager

logger = logging.getLogger(__name__)

class TicketWorkflowService:
    @staticmethod
    async def run_ticket_workflow(session: AsyncSession, ticket_id: str) -> Dict[str, Any]:
        ticket = await TicketRepository.get_by_id(session, ticket_id)
        if not ticket:
            raise ValueError(f"Ticket {ticket_id} not found.")

        # Create WorkflowRun DB entry
        wf_run = await WorkflowRepository.create_run(session, ticket.id)

        initial_state = {
            "ticket": {
                "ticket_id": ticket.id,
                "title": ticket.title,
                "customer_message": ticket.description,
                "customer_id": ticket.customer_id or "CUST-9901",
                "channel": "web",
                "timestamp": ticket.created_at.isoformat()
            },
            "classification": {},
            "retrieved_documents": {},
            "decision": {},
            "action_result": {},
            "verification": {},
            "errors": [],
            "retry_count": 0,
            "status": "STARTED",
            "workflow_run_id": wf_run.id,
            "human_approved": None,
            "approval_notes": None
        }

        config = {"configurable": {"thread_id": wf_run.id}}

        t0 = time.time()
        # Stream / Invoke graph
        final_state = dict(initial_state)
        async for output in agentflow_graph.astream(initial_state, config=config):
            for node_name, state_update in output.items():
                if isinstance(state_update, dict):
                    final_state.update(state_update)

        duration_ms = (time.time() - t0) * 1000

        # Check snapshot to see if graph is paused at an interrupt (e.g. human_approval)
        snapshot = agentflow_graph.get_state(config)
        decision_info = final_state.get("decision", {})
        
        is_pending = (
            bool(snapshot.next) or 
            decision_info.get("risk_level") == "HIGH" or 
            decision_info.get("decision") == "REQUEST_HUMAN_APPROVAL" or 
            decision_info.get("requires_approval") is True
        )

        if is_pending:
            final_state["status"] = "PENDING_APPROVAL"
            # Update Ticket status
            await TicketRepository.update_status(
                session,
                ticket_id=ticket.id,
                status="PENDING_APPROVAL",
                category=final_state.get("classification", {}).get("category"),
                priority=final_state.get("classification", {}).get("priority"),
                assigned_team=final_state.get("classification", {}).get("department")
            )
            # Create Approval record if not already created
            await ApprovalRepository.create_approval(
                session,
                workflow_run_id=wf_run.id,
                risk_level=decision_info.get("risk_level", "HIGH"),
                reason=decision_info.get("reason", "Action requires human authorization.")
            )
            # Update WorkflowRun status
            await WorkflowRepository.update_run(
                session,
                run_id=wf_run.id,
                status="PENDING_APPROVAL",
                state_data=final_state,
                duration_ms=duration_ms
            )
            metrics_manager.record_workflow_execution("PENDING_APPROVAL")
            return {"workflow_run_id": wf_run.id, "status": "PENDING_APPROVAL", "state": final_state}

        # Otherwise workflow completed, failed, or escalated
        new_status = final_state.get("status", "COMPLETED")
        if new_status in ["COMPLETED", "ACTION_EXECUTED"]:
            new_status = "RESOLVED"

        await TicketRepository.update_status(
            session,
            ticket_id=ticket.id,
            status=new_status,
            category=final_state.get("classification", {}).get("category"),
            priority=final_state.get("classification", {}).get("priority"),
            assigned_team=final_state.get("classification", {}).get("department")
        )

        await WorkflowRepository.update_run(
            session,
            run_id=wf_run.id,
            status=new_status,
            state_data=final_state,
            duration_ms=duration_ms
        )

        metrics_manager.record_workflow_execution(new_status)
        return {"workflow_run_id": wf_run.id, "status": new_status, "state": final_state}

    @staticmethod
    async def resume_after_approval(session: AsyncSession, approval_id: str, approved: bool, notes: Optional[str] = None) -> Dict[str, Any]:
        approval = await ApprovalRepository.resolve_approval(session, approval_id, approved, notes=notes)
        if not approval:
            raise ValueError(f"Approval {approval_id} not found.")

        wf_run = await WorkflowRepository.get_run(session, approval.workflow_run_id)
        if not wf_run:
            raise ValueError(f"WorkflowRun {approval.workflow_run_id} not found.")

        config = {"configurable": {"thread_id": wf_run.id}}

        # Update Graph state with human approval decision
        update_state = {
            "human_approved": approved,
            "approval_notes": notes
        }
        await agentflow_graph.aupdate_state(config, update_state, as_node="human_approval")

        t0 = time.time()
        snapshot = agentflow_graph.get_state(config)
        final_state = dict(snapshot.values) if snapshot.values else {}
        
        # Resume graph from interrupt node
        async for output in agentflow_graph.astream(None, config=config):
            for node_name, state_update in output.items():
                if isinstance(state_update, dict):
                    final_state.update(state_update)

        duration_ms = (wf_run.duration_ms or 0) + (time.time() - t0) * 1000
        new_status = "RESOLVED" if approved else "REJECTED"
        final_state["status"] = new_status

        await TicketRepository.update_status(
            session,
            ticket_id=wf_run.ticket_id,
            status=new_status
        )

        await WorkflowRepository.update_run(
            session,
            run_id=wf_run.id,
            status=new_status,
            state_data=final_state,
            duration_ms=duration_ms
        )

        return {"workflow_run_id": wf_run.id, "status": new_status, "state": final_state}

ticket_workflow_service = TicketWorkflowService()
